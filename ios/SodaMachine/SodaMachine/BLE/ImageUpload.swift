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
    let crop: UIImage
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

    /// Keep a read moving for as long as there is a link, rather than for as
    /// long as someone is looking at it. A burst ends in deliberate silence, so
    /// something has to ask for the next one — and that cannot be a timer on a
    /// screen, because the fetch starts when the machine connects and finishes
    /// long after anyone has stopped watching a particular view.
    func startFacePump() {
        stopFacePump()
        facePump = Timer.scheduledTimer(withTimeInterval: 0.2, repeats: true) { [weak self] _ in
            self?.resumeFaceIfStalled()
            self?.nudgeUploadIfStalled()
        }
    }

    func stopFacePump() {
        facePump?.invalidate()
        facePump = nil
    }

    /// Say something on the machine's console. This phone has no wire on it and
    /// its own log is not reachable from a bench, so a decision made here is
    /// otherwise invisible to anyone holding the machine.
    func say(_ text: String) {
        guard !demoMode, let data = text.data(using: .utf8) else { return }
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: 0x01, payload: data.prefix(72))
        }
    }

    /// The same, for a condition that persists rather than an event that
    /// happens. Said when it becomes true and not again while it stays true,
    /// because a standing fault repeated at the polling rate buries every other
    /// line on the console.
    func sayOnce(_ text: String) {
        guard saidStanding != text else { return }
        saidStanding = text
        say(text)
    }

    /// A picture whose last byte is on the air and whose "kept it" never came
    /// back. That answer is a single notification, and a notification is not
    /// acknowledged — so it can be lost, and when it is, every byte of the
    /// picture is already on the machine and nothing further was ever going to
    /// arrive. Waiting on it forever is what left a finished ring on screen
    /// with no way past it.
    ///
    /// Asking again is END, which the board answers from a finished transfer as
    /// readily as from a running one. And behind that, the machine's own list of
    /// what it holds settles it outright: a slot carrying the crc32 this phone
    /// computed for the bundle it sent IS that bundle, whatever was lost coming
    /// back.
    func nudgeUploadIfStalled() {
        guard case .sending(let sent, let total) = imageUploadState,
              total > 0, sent >= total else { return }
        guard Date().timeIntervalSince(uploadHeardAt) > 2.0 else { return }
        uploadHeardAt = Date()
        uploadAsks += 1

        // Long enough that a board still writing flash is not called a failure,
        // short enough that nobody is left holding a phone that will never move.
        guard uploadAsks <= 8 else {
            let slot = imageSlotSending
            say("upload: slot \(slot) gave up after \(uploadAsks) asks")
            forgetPreview(slot: slot)
            bleQueue.async { [weak self] in self?.imageBundle = Data() }
            finishActive(.failed("the machine never said it kept it"))
            return
        }
        say("upload: slot \(imageSlotSending) asking again, \(uploadAsks)")
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: ImageFrame.end, payload: Data(), withResponse: true)
        }
        queryImageSlots()
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
            // The machine listing this picture's own crc32 in the slot it was
            // sent to is the picture having arrived, and outranks any frame
            // that went missing on the way back.
            if case .sending = self.imageUploadState, let active = self.activeUpload,
               let want = self.pendingCrc[active.slot], want != 0,
               slots.crc(of: active.slot) == want {
                self.say("upload: slot \(active.slot) is on the machine")
                self.bleQueue.async { [weak self] in self?.imageBundle = Data() }
                self.finishActive(.done)
            }
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
    /// A RECONCILE IS SILENT WHEN THERE IS NOTHING TO RECONCILE. This runs off
    /// the pump as well as off a state frame, so a line at the top of it is a
    /// line five times a second on a console someone is reading and on the link
    /// it is reporting about — the same shape as the progress line that became
    /// the traffic it was measuring. It speaks when it acts, or when something
    /// is wrong, and neither of those repeats on a quiet machine.
    func fetchMissingFaces() {
        let unit = machineKey
        guard !unit.isEmpty else {
            log.error("no machine key yet; faces cannot be filed or fetched")
            sayOnce("faces: no machine key, cannot fetch")
            return
        }
        for slot in 0..<imageSlots.count where imageSlots.isHeld(slot) {
            let crc = imageSlots.crc(of: slot)
            guard crc != 0 else {
                log.error("slot \(slot) is held but reports no crc")
                sayOnce("faces: slot \(slot) held but crc is 0")
                continue
            }
            if faces[crc] != nil { continue }
            if let onDisk = PictureCache.load(unit: unit, crc: crc) {
                faces[crc] = onDisk
                say("faces: slot \(slot) came off disk")
                continue
            }
            // One read at a time. Whether one is in flight is decided where the
            // read state lives, not here — this runs on the main queue and
            // would be reading a copy of it.
            log.info("asking for slot \(slot) face, crc \(crc)")
            requestFace(slot: slot, crc: crc)
            return   // one at a time; the next goes when this one lands
        }
    }

    /// Always on the radio's queue, which is the only place face state lives.
    private func requestFace(slot: Int, from offset: Int = 0, crc: UInt32 = 0) {
        bleQueue.async { [weak self] in
            guard let self else { return }
            // A fresh ask while one is already running would reset the buffer
            // out from under the frames arriving into it.
            if offset == 0, self.faceSlot >= 0, self.faceSlot != slot { return }
            if offset == 0, self.faceSlot == slot, self.faceReceived > 0 { return }
            if crc != 0 {
                self.say("faces: asking slot \(slot) crc \(String(crc, radix: 16))")
            }
            self.faceSlot = slot
            if offset == 0 {
                self.facePixels = Data()
                self.faceHave.removeAll()
                self.faceReceived = 0
                self.faceResumes = 0
            }
            self.faceAskedAt = Date()
            var payload = Data([UInt8(slot), 0])
            payload.append(contentsOf: withUnsafeBytes(of: UInt32(offset).littleEndian, Array.init))
            self.sendBLEFrame(type: ImageFrame.read, payload: payload)
        }
    }

    /// A stream that stopped short. Notifications are not acknowledged, so a
    /// dropped one leaves every frame after it at an offset nothing is waiting
    /// for — silence that used to cost the whole picture. Asking again from
    /// where this actually got to costs the remainder and nothing else.
    func resumeFaceIfStalled() {
        // On the radio's queue, because that is where the buffer this decides
        // from is filled. Deciding on the main queue meant deciding from a copy
        // that never saw a single byte arrive.
        bleQueue.async { [weak self] in self?.resumeFaceOnBleQueue() }
    }

    private func resumeFaceOnBleQueue() {
        // Nothing in flight: something may still be missing, and a fetch that
        // died with a link would otherwise never be started again.
        guard faceSlot >= 0 else {
            // Nothing in flight is the normal state of a machine whose faces
            // are all in hand. Sweeping for a missing one is a catch-up for a
            // fetch that died with a link, not something to do five times a
            // second.
            guard Date().timeIntervalSince(faceSweptAt) > 3.0 else { return }
            faceSweptAt = Date()
            DispatchQueue.main.async { [weak self] in
                guard let self, !self.imageSlots.crc.isEmpty else { return }
                self.fetchMissingFaces()
            }
            return
        }
        // A burst ends in deliberate silence, so this is the normal way the
        // next one is asked for rather than an error path. Short, because it is
        // in the middle of a transfer someone is watching.
        guard Date().timeIntervalSince(faceAskedAt) > 0.35 else { return }
        let from = firstGap()
        // How far this phone has actually got is the number that settles
        // whether a read is working, and it is the one number that has never
        // left the phone. Every eighth pull, so it says enough to be read
        // without becoming the traffic.
        // Throttled by the clock, not by a count. The count is reset on every
        // ask from zero, so "every eighth" was every single one — which is how
        // a progress line became the traffic it was reporting on.
        faceResumes += 1
        if Date().timeIntervalSince(faceSaidAt) > 3.0 {
            faceSaidAt = Date()
            say("faces: \(faceReceived)/\(faceTotal) next \(from) after \(faceResumes)")
        }
        requestFace(slot: faceSlot, from: from)
    }

    /// Pixels coming back, a frame at a time, each carrying where it belongs.
    /// Called on the radio's delegate queue, and everything it touches stays
    /// there. The one thing that leaves is a finished picture.
    ///
    /// EVERY FRAME GOES WHERE ITS OFFSET SAYS, and none of them has to be first.
    /// Requiring the next contiguous byte meant one lost frame at the head of a
    /// burst threw away every frame behind it, forever — the phone asked from
    /// zero, the first frames were the ones dropped, and it asked from zero
    /// again. What is missing is asked for instead, so the order things arrive
    /// in stops being something this has to be lucky about.
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
        guard slot == faceSlot, total > 0, !bytes.isEmpty else { return }
        guard offset >= 0, offset + bytes.count <= total else { return }

        if facePixels.count != total {
            facePixels = Data(count: total)
            faceHave.removeAll()
            faceReceived = 0
            faceTotal = total
        }
        // What one frame carries, learned from a frame rather than agreed in
        // advance. The board sizes these from the MTU it negotiated, so a
        // constant here would be a second opinion about that — and a wrong one
        // makes the phone hunt for gaps at offsets nothing will ever send.
        if offset + bytes.count < total { facePixelStride = bytes.count }
        if faceHave.contains(offset) { return }   // a duplicate from a resume

        facePixels.replaceSubrange(offset..<(offset + bytes.count), with: bytes)
        faceHave.insert(offset)
        faceReceived += bytes.count
        faceAskedAt = Date()
        guard faceReceived >= total else { return }

        let crc = imageSlots.crc(of: slot)
        let whole = facePixels
        facePixels = Data()
        faceHave.removeAll()
        faceReceived = 0
        faceSlot = -1
        DispatchQueue.main.async {
            let unit = self.machineKey
            if !unit.isEmpty, let face = ImageBundle.decode(whole, ImageBundle.sizes[0]) {
                PictureCache.save(face, unit: unit, crc: crc)
                self.faces[crc] = face      // observable: this is what redraws the tile
                log.info("read back slot \(slot), \(total) bytes")
                self.say("faces: slot \(slot) decoded, \(total) B")
                self.saidStanding = ""      // the path works; a fault may be said again
            }
            self.fetchMissingFaces()   // whatever else is missing, now this is in hand
        }
    }

    /// The lowest byte this phone still needs, which is where the next pull
    /// starts. Nothing about it assumes frames arrived in order.
    private func firstGap() -> Int {
        guard faceTotal > 0, facePixelStride > 0 else { return 0 }
        var at = 0
        while at < faceTotal {
            if !faceHave.contains(at) { return at }
            at += facePixelStride
        }
        return faceTotal
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
    func enqueueImage(_ crop: UIImage, preview: UIImage?) -> Int? {
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

        // Resampling every rendition is real work; it does not belong on the
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
            self.uploadHeardAt = Date()
            self.uploadAsks = 0

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
        uploadHeardAt = Date()

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
