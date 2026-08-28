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

enum ImageFrame {
    static let query: UInt8 = 0x16
    static let state: UInt8 = 0x17
    static let begin: UInt8 = 0x18
    static let data:  UInt8 = 0x19
    static let ack:   UInt8 = 0x1A
    static let end:   UInt8 = 0x1B
    static let erase: UInt8 = 0x1C
}

/// What the machine says it is holding.
struct ImageSlots: Equatable {
    var count: Int = 0            // custom slots this machine has
    var occupancy: UInt8 = 0      // bit per slot, low slot first
    var bundleBytes: Int = 0
    var artFirst: Int = 4         // art index the low custom slot answers to

    func isHeld(_ slot: Int) -> Bool { occupancy & (1 << UInt8(slot)) != 0 }
    var held: Int { (0..<count).filter { isHeld($0) }.count }
    var firstFree: Int? { (0..<count).first { !isHeld($0) } }
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
        var slots = ImageSlots()
        slots.count = Int(payload[b])
        slots.occupancy = payload[b + 2]
        slots.bundleBytes = Int(UInt32(payload[b + 4]) | (UInt32(payload[b + 5]) << 8) |
                                (UInt32(payload[b + 6]) << 16) | (UInt32(payload[b + 7]) << 24))
        slots.artFirst = Int(payload[b + 8])
        DispatchQueue.main.async {
            self.imageSlots = slots
            log.info("slots \(slots.count) held \(slots.held) bundle \(slots.bundleBytes)")
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

    // ── Adding ────────────────────────────────────────────────────────────
    func uploadImage(_ crop: ImageCrop, to slot: Int) {
        guard !demoMode else { return }
        guard imageUploadState == .idle || isTerminal(imageUploadState) else { return }

        DispatchQueue.main.async { self.imageUploadState = .preparing }

        // Resampling five renditions is real work; it does not belong on the
        // main thread and it does not belong on the BLE queue either, which has
        // a transfer to run the moment this finishes.
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self else { return }
            guard let bundle = ImageBundle.make(from: crop) else {
                DispatchQueue.main.async { self.imageUploadState = .failed("that picture would not convert") }
                return
            }
            self.startImagePush(bundle, slot: slot)
        }
    }

    private func isTerminal(_ s: ImageUploadState) -> Bool {
        if case .sending = s { return false }
        if s == .preparing { return false }
        return true
    }

    private func startImagePush(_ bundle: Data, slot: Int) {
        bleQueue.async { [weak self] in
            guard let self else { return }
            self.imageBundle = bundle
            self.imageSlotSending = slot
            self.imageSentOffset = 0
            self.imageStartedAt = Date()

            var payload = Data([UInt8(slot)])
            payload.append(contentsOf: withUnsafeBytes(of: UInt32(bundle.count).littleEndian, Array.init))
            payload.append(contentsOf: withUnsafeBytes(of: crc32(bundle).littleEndian, Array.init))
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
            bleQueue.async { [weak self] in self?.imageBundle = Data() }
            DispatchQueue.main.async { self.imageUploadState = .failed(why) }
            log.error("slot upload failed: \(why)")
        case 2:   // DONE
            let took = Date().timeIntervalSince(imageStartedAt)
            let kbs = Double(imageBundle.count) / took / 1024
            log.info("done in \(took, format: .fixed(precision: 1))s — \(kbs, format: .fixed(precision: 1)) KB/s")
            bleQueue.async { [weak self] in self?.imageBundle = Data() }
            DispatchQueue.main.async { self.imageUploadState = .done }
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
