import Foundation
import UIKit
import os

private let log = Logger(subsystem: "com.derekbreden.SodaMachine", category: "Images")

// ════════════════════════════════════════════════════════════
//  Putting a picture on the machine
// ════════════════════════════════════════════════════════════
//
// THIS PUSHES; THE FIRMWARE PATH PULLS. A pull costs a round trip per frame and
// the connection interval then is the transfer rate, which is what makes the
// firmware path slow — the radio is not the limit. A picture is not firmware:
// it lands in a data partition rather than the slot the board is about to boot
// from, and a wrong byte costs a wrong pixel. So this streams without waiting.
//
// EVERY FRAME CARRIES ITS OWN OFFSET, WHICH IS THE WHOLE RECOVERY STORY. The
// board takes a frame only at the offset it is expecting and answers anything
// else with the offset it actually reached; this winds back to there. No
// sequence numbers, no window, and a frame the board was too busy to take costs
// the distance between them rather than the transfer.

/// Which face each channel wears, as the main board holds it.
struct FlavorArt: Equatable {
    var art: [Int] = [0, 1]
    var factory: Int = 4
    var custom: Int = 4
    var total: Int { factory + custom }
    /// Art index for a custom slot, and back again.
    func artIndex(customSlot: Int) -> Int { factory + customSlot }
    func customSlot(art: Int) -> Int? { art >= factory ? art - factory : nil }
}

enum ImageFrame {
    static let query: UInt8 = 0x16
    static let state: UInt8 = 0x17
    static let begin: UInt8 = 0x18
    static let data:  UInt8 = 0x19
    static let ack:   UInt8 = 0x1A
    static let end:   UInt8 = 0x1B
    static let erase: UInt8 = 0x1C
    static let artQuery: UInt8 = 0x1D
    static let artState: UInt8 = 0x1E
    static let artSet:   UInt8 = 0x1F
    static let abort:    UInt8 = 0x20
    static let read:     UInt8 = 0x21
    static let pix:      UInt8 = 0x22
}

/// What the machine says it is holding.
struct ImageSlots: Equatable {
    var count: Int = 0            // custom slots this machine has
    var occupancy: UInt8 = 0      // bit per slot, low slot first
    var bundleBytes: Int = 0
    var artFirst: Int = 4         // art index the low custom slot answers to
    /// What each slot holds, as a picture's identity rather than its address —
    /// so a cached face survives the picture moving, and a slot that changed
    /// hands is noticed rather than shown stale.
    var crc: [UInt32] = []

    func crc(of slot: Int) -> UInt32 { slot < crc.count ? crc[slot] : 0 }

    func isHeld(_ slot: Int) -> Bool { occupancy & (1 << UInt8(slot)) != 0 }
    var held: Int { (0..<count).filter { isHeld($0) }.count }
    var firstFree: Int? { (0..<count).first { !isHeld($0) } }
}

/// One picture waiting its turn. The preview travels with it so a queued tile
/// can be the photograph rather than a placeholder standing in for one.
struct QueuedImage: Identifiable, Equatable {
    let id = UUID()
    let crop: ImageCrop
    let slot: Int
    let preview: UIImage?
    static func == (a: QueuedImage, b: QueuedImage) -> Bool { a.id == b.id }
}

enum ImageUploadState: Equatable {
    case idle
    case preparing
    case sending(sent: Int, total: Int)
    case done
    case failed(String)
}

/// Board-side outcomes, as ble_image.h names them.
private let uploadErrors = [
    "", "no such slot", "not a picture this machine's size",
    "the board could not write it", "it did not arrive intact", "the board is busy",
]

extension BLEManager {

    // ── Which face a channel wears ────────────────────────────────────────
    // The main board owns this. The app asks and sets; it never keeps an idea
    // of its own, so a change made on either glass shows here immediately.
    func queryFlavorArt() {
        guard !demoMode else { return }
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: ImageFrame.artQuery, payload: Data())
        }
    }

    func setFlavorArt(channel: Int, art: Int) {
        guard !demoMode, channel >= 0, channel < 2 else { return }
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: ImageFrame.artSet, payload: Data([UInt8(channel), UInt8(art)]))
        }
    }

    func handleFlavorArt(_ payload: Data) {
        guard payload.count >= 4 else { return }
        let b = payload.startIndex
        var a = FlavorArt()
        a.art = [Int(payload[b]), Int(payload[b + 1])]
        a.factory = Int(payload[b + 2])
        a.custom = Int(payload[b + 3])
        DispatchQueue.main.async { self.flavorArt = a }
    }

    // ── Asking ────────────────────────────────────────────────────────────
    func queryImageSlots() {
        guard !demoMode else { return }
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: ImageFrame.query, payload: Data())
        }
    }

    func handleImageState(_ payload: Data) {
        guard payload.count >= 9 else { return }
        let b = payload.startIndex
        func u32(_ at: Int) -> UInt32 {
            UInt32(payload[b + at]) | (UInt32(payload[b + at + 1]) << 8) |
            (UInt32(payload[b + at + 2]) << 16) | (UInt32(payload[b + at + 3]) << 24)
        }
        var slots = ImageSlots()
        slots.count = Int(payload[b])
        slots.occupancy = payload[b + 2]
        slots.bundleBytes = Int(u32(4))
        slots.artFirst = Int(payload[b + 8])
        var crcs: [UInt32] = []
        var at = 9
        while at + 4 <= payload.count { crcs.append(u32(at)); at += 4 }
        slots.crc = crcs

        DispatchQueue.main.async {
            self.imageSlots = slots
            log.info("slots \(slots.count) held \(slots.held) bundle \(slots.bundleBytes)")
            self.fetchMissingFaces()
        }
    }

    // ── Reading one back ──────────────────────────────────────────────────
    // A picture this phone did not send has no cached face, so it is asked for
    // — once per picture, ever, because what comes back is filed under the
    // picture's own crc32 rather than under the slot it happens to occupy.
    /// Faces are held in memory, not read off disk in a draw. A view that had
    /// to open a file to know what to show would both do it on every frame and
    /// have nothing to notice when the answer changed — which is how a picture
    /// that arrived correctly still never appeared.
    func fetchMissingFaces() {
        let unit = machineKey
        guard !unit.isEmpty else {
            log.error("no machine key yet; faces cannot be filed or fetched")
            return
        }
        for slot in 0..<imageSlots.count where imageSlots.isHeld(slot) {
            let crc = imageSlots.crc(of: slot)
            guard crc != 0 else {
                log.error("slot \(slot) is held but reports no crc")
                continue
            }
            if faces[crc] != nil { continue }
            if let onDisk = PictureCache.load(unit: unit, crc: crc) {
                faces[crc] = onDisk
                continue
            }
            guard !faceWanted.contains(crc) else { continue }
            faceWanted.insert(crc)
            log.info("asking for slot \(slot) face, crc \(crc)")
            requestFace(slot: slot)
            return   // one at a time; the next goes when this one lands
        }
    }

    private func requestFace(slot: Int) {
        faceSlot = slot
        faceBuffer = Data()
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: ImageFrame.read, payload: Data([UInt8(slot), 0]))
        }
    }

    /// Pixels coming back, a frame at a time, each carrying where it belongs.
    func handleImagePix(_ payload: Data) {
        guard payload.count >= 10 else { return }
        let b = payload.startIndex
        let slot = Int(payload[b])
        func u32(_ at: Int) -> UInt32 {
            UInt32(payload[b + at]) | (UInt32(payload[b + at + 1]) << 8) |
            (UInt32(payload[b + at + 2]) << 16) | (UInt32(payload[b + at + 3]) << 24)
        }
        let offset = Int(u32(2)), total = Int(u32(6))
        let bytes = payload.subdata(in: (b + 10)..<payload.endIndex)
        guard slot == faceSlot, offset == faceBuffer.count else { return }
        faceBuffer.append(bytes)
        guard faceBuffer.count >= total else { return }

        let crc = imageSlots.crc(of: slot)
        let whole = faceBuffer
        faceBuffer = Data()
        faceSlot = -1
        DispatchQueue.main.async {
            let unit = self.machineKey
            if !unit.isEmpty, let face = ImageBundle.decode(whole, ImageBundle.sizes[0]) {
                PictureCache.save(face, unit: unit, crc: crc)
                self.faces[crc] = face      // observable: this is what redraws the tile
                log.info("read back slot \(slot), \(total) bytes")
            }
            self.fetchMissingFaces()   // whatever else is missing, now this is in hand
        }
    }

    // ── Removing ──────────────────────────────────────────────────────────
    // The slot goes back to being somewhere a picture can go. A channel still
    // wearing it falls back to that channel's factory logo, which the board
    // does on its own — nothing here has to reassign anything.
    func removeImage(slot: Int) {
        guard !demoMode, slot >= 0 else { return }
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: ImageFrame.erase, payload: Data([UInt8(slot)]))
        }
    }

    /// Stop one partway. The board's slot was erased when the transfer opened
    /// and never got its header, so there is nothing to undo on either side.
    func cancelImageUpload() {
        guard case .sending = imageUploadState else { return }
        let slot = imageSlotSending
        bleQueue.async { [weak self] in
            guard let self else { return }
            self.imageBundle = Data()
            self.sendBLEFrame(type: ImageFrame.abort, payload: Data())
        }
        forgetPreview(slot: slot)
        DispatchQueue.main.async { self.finishActive(.idle) }
    }

    /// Drop one that has not started yet.
    func cancelQueuedImage(id: UUID) {
        guard let item = imageQueue.first(where: { $0.id == id }) else { return }
        forgetPreview(slot: item.slot)
        imageQueue.removeAll { $0.id == id }
    }

    /// A picture that did not arrive must not go on being shown.
    func forgetPreview(slot: Int) {
        guard let crc = pendingCrc[slot] else { return }
        PictureCache.forget(unit: machineKey, crc: crc)
        faces[crc] = nil
        pendingCrc[slot] = nil
    }

    // ── Adding ────────────────────────────────────────────────────────────
    /// Take a picture for the machine. Choosing the next one never waits on the
    /// last: a queued picture is a real tile in the place it will occupy, and
    /// the "+" stays live the whole time.
    func enqueueImage(_ crop: ImageCrop, preview: UIImage?) -> Int? {
        guard !demoMode, let slot = nextFreeSlot() else { return nil }
        let item = QueuedImage(crop: crop, slot: slot, preview: preview)
        DispatchQueue.main.async {
            self.imageQueue.append(item)
            if self.activeUpload == nil { self.startNextImage() }
        }
        return slot
    }

    /// The lowest slot the machine has free that nothing already in this queue
    /// has claimed. The board cannot know about the ones still on the phone.
    func nextFreeSlot() -> Int? {
        let claimed = Set(imageQueue.map(\.slot) + (activeUpload.map { [$0.slot] } ?? []))
        return (0..<imageSlots.count).first { !imageSlots.isHeld($0) && !claimed.contains($0) }
    }

    func startNextImage() {
        guard activeUpload == nil, !imageQueue.isEmpty else { return }
        let item = imageQueue.removeFirst()
        activeUpload = item
        imageUploadState = .preparing

        // Resampling five renditions is real work; it does not belong on the
        // main thread and it does not belong on the BLE queue either, which has
        // a transfer to run the moment this finishes.
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self else { return }
            guard let bundle = ImageBundle.make(from: item.crop) else {
                DispatchQueue.main.async {
                    self.forgetPreview(slot: item.slot)
                    self.activeUpload = nil
                    self.imageUploadState = .failed("that picture would not convert")
                    self.startNextImage()
                }
                return
            }
            self.startImagePush(bundle, slot: item.slot)
        }
    }

    /// One finished, one way or another. The next starts after a beat so a run
    /// of pictures does not strobe.
    private func finishActive(_ outcome: ImageUploadState) {
        activeUpload = nil
        imageUploadState = outcome
        if !imageQueue.isEmpty {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [weak self] in
                self?.startNextImage()
            }
        } else if outcome == .done {
            // Let the ring finish visibly, then clear so the grid is just the
            // pictures again.
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                if self?.activeUpload == nil, self?.imageQueue.isEmpty == true {
                    self?.imageUploadState = .idle
                }
            }
        }
    }

    private func startImagePush(_ bundle: Data, slot: Int) {
        bleQueue.async { [weak self] in
            guard let self else { return }
            self.imageBundle = bundle
            self.imageSlotSending = slot
            self.imageSentOffset = 0
            self.imageStartedAt = Date()

            // The face is decoded out of the bundle just built and filed under
            // its crc32 — byte for byte what the board would send back if
            // asked, so an upload and a read-back agree without meeting.
            let crc = crc32(bundle)
            self.pendingCrc[slot] = crc
            let unit = self.machineKey
            if !unit.isEmpty, let face = ImageBundle.face(of: bundle) {
                PictureCache.save(face, unit: unit, crc: crc)
                DispatchQueue.main.async { self.faces[crc] = face }
            }

            var payload = Data([UInt8(slot)])
            payload.append(contentsOf: withUnsafeBytes(of: UInt32(bundle.count).littleEndian, Array.init))
            payload.append(contentsOf: withUnsafeBytes(of: crc.littleEndian, Array.init))
            self.sendBLEFrame(type: ImageFrame.begin, payload: payload)
            log.info("slot \(slot): \(bundle.count) bytes")
            // Nothing is sent until the board answers BEGIN with the offset it
            // wants, which is also how it says the slot was erased and is ready.
        }
    }

    /// The board's only steering signal: send from `have`.
    func handleImageAck(_ payload: Data) {
        guard payload.count >= 7 else { return }
        let b = payload.startIndex
        let state = payload[b + 1]
        let err = payload[b + 2]
        let have = Int(UInt32(payload[b + 3]) | (UInt32(payload[b + 4]) << 8) |
                       (UInt32(payload[b + 5]) << 16) | (UInt32(payload[b + 6]) << 24))

        switch state {
        case 3:   // FAILED
            let why = Int(err) < uploadErrors.count ? uploadErrors[Int(err)] : "unknown"
            // The preview was kept before the push so a slow send still had a
            // face. A send that failed has none, and must not pretend to.
            forgetPreview(slot: imageSlotSending)
            bleQueue.async { [weak self] in self?.imageBundle = Data() }
            DispatchQueue.main.async { self.finishActive(.failed(why)) }
            log.error("slot upload failed: \(why)")
        case 2:   // DONE
            let took = Date().timeIntervalSince(imageStartedAt)
            let kbs = Double(imageBundle.count) / took / 1024
            log.info("done in \(took, format: .fixed(precision: 1))s — \(kbs, format: .fixed(precision: 1)) KB/s")
            bleQueue.async { [weak self] in self?.imageBundle = Data() }
            DispatchQueue.main.async { self.finishActive(.done) }
            queryImageSlots()
        default:  // TAKING — either the opening ack, or a rewind
            bleQueue.async { [weak self] in
                guard let self, !self.imageBundle.isEmpty else { return }
                if have != self.imageSentOffset {
                    log.info("rewind \(self.imageSentOffset) -> \(have)")
                    self.imageSentOffset = have
                }
                self.pumpImageFrames()
            }
        }
    }

    /// Fill the link as far as it will take, then stop. iOS calls
    /// `peripheralIsReady` when it drains, which comes back here.
    func pumpImageFrames() {
        guard let p = connectedPeripheral, let rx = rxCharacteristic, !imageBundle.isEmpty else { return }
        let mtu = p.maximumWriteValueLength(for: .withoutResponse)
        let body = max(64, mtu - 3 - 4)          // our header, then the offset

        while imageSentOffset < imageBundle.count {
            guard p.canSendWriteWithoutResponse else { return }
            let end = min(imageSentOffset + body, imageBundle.count)
            var payload = Data()
            payload.append(contentsOf: withUnsafeBytes(of: UInt32(imageSentOffset).littleEndian, Array.init))
            payload.append(imageBundle[imageSentOffset..<end])
            sendBLEFrame(type: ImageFrame.data, payload: payload, withResponse: false)
            imageSentOffset = end

            let sent = imageSentOffset, total = imageBundle.count
            DispatchQueue.main.async { self.imageUploadState = .sending(sent: sent, total: total) }
        }

        // Everything is on the air. END is the one frame worth an acknowledged
        // write: it is what makes the board check the whole picture and keep it.
        sendBLEFrame(type: ImageFrame.end, payload: Data(), withResponse: true)
    }
}

/// The crc32 the board holds a picture to before it writes its header.
func crc32(_ data: Data) -> UInt32 {
    var table = [UInt32](repeating: 0, count: 256)
    for i in 0..<256 {
        var c = UInt32(i)
        for _ in 0..<8 { c = (c & 1) != 0 ? 0xEDB88320 ^ (c >> 1) : c >> 1 }
        table[i] = c
    }
    var crc: UInt32 = 0xFFFFFFFF
    for byte in data { crc = table[Int((crc ^ UInt32(byte)) & 0xFF)] ^ (crc >> 8) }
    return crc ^ 0xFFFFFFFF
}
