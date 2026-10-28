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
struct FlavorArt: Codable, Equatable {
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
struct ImageSlots: Codable, Equatable {
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

/// How one picture's trip to the machine ended, for whoever is waiting on it.
enum UploadEnd: Equatable {
    /// The machine holds it.
    case stored
    case failed(String)
    /// Someone canceled it.
    case canceled
    /// The link went before it arrived.
    case interrupted
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
    "", "no such slot", "a picture is a different size on that machine",
    "the board could not write it", "it did not arrive intact", "the board is busy",
    "the machine does not trust this device yet",
]

extension BLEManager {

    // ── Which face a channel wears ────────────────────────────────────────
    // The main board owns this. The app asks and sets; it never keeps an idea
    // of its own, so a change made on either glass shows here immediately.
    func queryFlavorArt() {
        sendBLEFrame(type: ImageFrame.artQuery, payload: Data())
    }

    func setFlavorArt(channel: Int, art: Int) {
        guard channel >= 0, channel < 2 else { return }
        if demoMode {
            flavorArt.art[channel] = art
            return
        }
        sendBLEFrame(type: ImageFrame.artSet, payload: Data([UInt8(channel), UInt8(art)]))
    }

    /// Put `art` on `channel` and wait, up to a deadline, for the machine to
    /// say it wears it. The faucet answers from its own copy of the pair
    /// until the main board publishes the new one, so an answer still naming
    /// the old face is a wait, not a refusal. False for a deadline passed, a
    /// link gone, another machine in use, or a choice that `still` says has
    /// been superseded.
    ///
    /// THE MACHINE'S ASSIGNMENTS RUN ONE AFTER ANOTHER, in the order asked,
    /// both flavors together: the faucet sets a pair, filling the other half
    /// from its own copy, so two in flight at once can undo each other. A
    /// choice is sent only once every earlier one is done or given up, so the
    /// newest choice is the last the machine is sent, and the face the flavor
    /// ends up wearing. Only an answer heard after the send counts: what this
    /// device last heard can show a face, never confirm a change.
    func assignArt(channel: Int, art: Int, on machine: String,
                   while still: @escaping @MainActor () -> Bool) async -> Bool {
        let before = artChain
        artAssigning[channel, default: 0] += 1
        let mine = Task { () -> Bool in
            _ = await before?.value
            let worn = await self.assignNow(channel: channel, art: art, on: machine, while: still)
            self.artAssigning[channel, default: 1] -= 1
            return worn
        }
        artChain = mine
        return await mine.value
    }

    /// Whether a face assignment for this flavor is still under way.
    func assigningArt(_ channel: Int) -> Bool { (artAssigning[channel] ?? 0) > 0 }

    private func assignNow(channel: Int, art: Int, on machine: String,
                           while still: @MainActor () -> Bool) async -> Bool {
        func wearing() -> Bool { flavorArt.art.indices.contains(channel) && flavorArt.art[channel] == art }
        guard still(), current?.id == machine, linked || demoMode else { return false }
        let sent = Date()
        setFlavorArt(channel: channel, art: art)
        if demoMode { return true }
        let until = sent.addingTimeInterval(6)
        while Date() < until {
            try? await Task.sleep(for: .milliseconds(500))
            guard current?.id == machine, linked else { return false }
            if let heard = artHeardAt, heard > sent, wearing() { return true }
            // A newer choice waits behind this one and is sent next.
            guard still() else { return false }
            queryFlavorArt()
        }
        return false
    }

    func handleFlavorArt(_ payload: Data) {
        guard payload.count >= 4 else { return }
        let b = payload.startIndex
        var a = FlavorArt()
        a.art = [Int(payload[b]), Int(payload[b + 1])]
        a.factory = Int(payload[b + 2])
        a.custom = Int(payload[b + 3])
        flavorArt = a
        artHeardAt = Date()
    }

    /// Keep a read moving for as long as there is a link, rather than for as
    /// long as someone is looking at it. A burst ends in deliberate silence, so
    /// something has to ask for the next one — and that cannot be a timer on a
    /// screen, because the fetch starts when the machine connects and finishes
    /// long after anyone has stopped watching a particular view.
    func startFacePump() {
        stopFacePump()
        // A timer scheduled here fires on the main run loop.
        facePump = Timer.scheduledTimer(withTimeInterval: 0.2, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated {
                self?.resumeFaceIfStalled()
                self?.nudgeUploadIfStalled()
            }
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
        guard let data = text.data(using: .utf8) else { return }
        sendBLEFrame(type: 0x01, payload: data.prefix(72))
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
            imageBundle = Data()
            finishActive(.failed("the machine never said it kept it"))
            return
        }
        say("upload: slot \(imageSlotSending) asking again, \(uploadAsks)")
        sendBLEFrame(type: ImageFrame.end, payload: Data(), withResponse: true)
        queryImageSlots()
    }

    // ── Asking ────────────────────────────────────────────────────────────
    func queryImageSlots() {
        sendBLEFrame(type: ImageFrame.query, payload: Data())
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

        // A PICTURE ERASED OR REPLACED WHILE IT WAS BEING READ IS NOT COMING
        // BACK. The board stops sending it; a read left waiting on it asks again
        // forever, and every other missing face waits behind it. So the read is
        // let go before the reconcile below asks for whatever is missing now.
        if faceSlot >= 0 {
            let s = faceSlot
            if !slots.isHeld(s) || (faceCrc != 0 && slots.crc(of: s) != faceCrc) {
                say("faces: slot \(s) changed while it was read; letting it go")
                faceSlot = -1
                faceCrc = 0
                facePixels = Data()
                faceHave.removeAll()
                faceReceived = 0
            }
        }

        imageSlots = slots
        current?.picturesReadAt = Date()
        log.info("slots \(slots.count) held \(slots.held) bundle \(slots.bundleBytes)")
        // The machine listing this picture's own crc32 in the slot it was
        // sent to is the picture having arrived, and outranks any frame
        // that went missing on the way back.
        if case .sending = imageUploadState, let active = activeUpload, imageBegun == active.id,
           let want = pendingCrc[active.slot], want != 0,
           slots.crc(of: active.slot) == want {
            say("upload: slot \(active.slot) is on the machine")
            imageBundle = Data()
            finishActive(.done)
        }
        fetchMissingFaces()
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
        guard let m = current, linked else { return }
        for slot in 0..<imageSlots.count where imageSlots.isHeld(slot) {
            let crc = imageSlots.crc(of: slot)
            guard crc != 0 else {
                log.error("slot \(slot) is held but reports no crc")
                sayOnce("faces: slot \(slot) held but crc is 0")
                continue
            }
            if m.faces[crc] != nil { continue }
            if let onDisk = m.loadFace(crc: crc) {
                m.faces[crc] = onDisk
                say("faces: slot \(slot) came off disk")
                continue
            }
            // One read at a time: requestFace turns a fresh ask away while
            // another picture is still being read.
            log.info("asking for slot \(slot) face, crc \(crc)")
            requestFace(slot: slot, crc: crc)
            return   // one at a time; the next goes when this one lands
        }
    }

    private func requestFace(slot: Int, from offset: Int = 0, crc: UInt32 = 0) {
        // A fresh ask while one is already running would reset the buffer
        // out from under the frames arriving into it.
        if offset == 0, faceSlot >= 0, faceSlot != slot { return }
        if offset == 0, faceSlot == slot, faceReceived > 0 { return }
        if crc != 0 {
            say("faces: asking slot \(slot) crc \(String(crc, radix: 16))")
        }
        faceSlot = slot
        if offset == 0 { faceCrc = crc }
        if offset == 0 {
            facePixels = Data()
            faceHave.removeAll()
            faceReceived = 0
            faceResumes = 0
        }
        faceAskedAt = Date()
        var payload = Data([UInt8(slot), 0])
        payload.append(contentsOf: withUnsafeBytes(of: UInt32(offset).littleEndian, Array.init))
        sendBLEFrame(type: ImageFrame.read, payload: payload)
    }

    /// A stream that stopped short. Notifications are not acknowledged, so a
    /// dropped one leaves every frame after it at an offset nothing is waiting
    /// for. Asking again from where this actually got to costs the remainder
    /// and nothing else.
    func resumeFaceIfStalled() {
        // Nothing in flight is the normal state of a machine whose faces are
        // all in hand. A fetch that died with a link is caught up by a sweep
        // for whatever is still missing, every three seconds.
        guard faceSlot >= 0 else {
            guard Date().timeIntervalSince(faceSweptAt) > 3.0 else { return }
            faceSweptAt = Date()
            if !imageSlots.crc.isEmpty { fetchMissingFaces() }
            return
        }
        // A burst ends in deliberate silence, and this is how the next one is
        // asked for, a moment after the last frame landed.
        guard Date().timeIntervalSince(faceAskedAt) > 0.35 else { return }
        let from = firstGap()
        // How far this phone has actually got is the number that settles
        // whether a read is working. The machine's console hears it every
        // three seconds at most.
        faceResumes += 1
        if Date().timeIntervalSince(faceSaidAt) > 3.0 {
            faceSaidAt = Date()
            say("faces: \(faceReceived)/\(faceTotal) next \(from) after \(faceResumes)")
        }
        requestFace(slot: faceSlot, from: from)
    }

    /// Pixels coming back, a frame at a time, each carrying where it belongs.
    ///
    /// EVERY FRAME GOES WHERE ITS OFFSET SAYS, and none of them has to be first.
    /// What is missing is asked for again by its offset, whatever order the
    /// frames arrived in.
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

        let whole = facePixels
        let asked = faceCrc
        facePixels = Data()
        faceHave.removeAll()
        faceReceived = 0
        faceSlot = -1
        faceCrc = 0
        if let m = current, let face = ImageBundle.decode(whole, ImageBundle.sizes[0]) {
            // Filed under the picture that was asked for, not whatever the
            // slot holds by the time the last frame lands.
            let crc = asked != 0 ? asked : m.imageSlots.crc(of: slot)
            m.saveFace(face, crc: crc)
            m.faces[crc] = face         // observable: this is what redraws the tile
            log.info("read back slot \(slot), \(total) bytes")
            say("faces: slot \(slot) decoded, \(total) B")
            saidStanding = ""           // the path works; a fault may be said again
        }
        fetchMissingFaces()   // whatever else is missing, now this is in hand
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
        sendBLEFrame(type: ImageFrame.erase, payload: Data([UInt8(slot)]))
    }

    /// Stop one partway, or before it starts. The board's slot was erased
    /// when the transfer opened and never got its header, so there is nothing
    /// to undo on either side; one still being made is let go before its
    /// BEGIN goes out.
    func cancelImageUpload() {
        guard let active = activeUpload else { return }
        if imageBegun == active.id { sendBLEFrame(type: ImageFrame.abort, payload: Data()) }
        imageBundle = Data()
        forgetPreview(slot: active.slot)
        finishActive(.idle)
    }

    /// Drop one that has not started yet.
    func cancelQueuedImage(id: UUID) {
        guard let item = imageQueue.first(where: { $0.id == id }) else { return }
        forgetPreview(slot: item.slot)
        imageQueue.removeAll { $0.id == id }
        resolveUpload(id, .canceled)
    }

    // ── Who is waiting on which picture ───────────────────────────────────

    /// How this picture's trip ends: stored, failed, canceled, or cut off by
    /// the link. A picture no longer queued or on its way has already ended.
    func awaitUpload(_ id: UUID) async -> UploadEnd {
        if let end = uploadEnds.removeValue(forKey: id) { return end }
        guard activeUpload?.id == id || imageQueue.contains(where: { $0.id == id }) else { return .interrupted }
        return await withCheckedContinuation { uploadWaiters[id] = $0 }
    }

    private func resolveUpload(_ id: UUID, _ end: UploadEnd) {
        if let waiter = uploadWaiters.removeValue(forKey: id) {
            waiter.resume(returning: end)
        } else {
            uploadEnds[id] = end
        }
    }

    /// The link went. The board abandons a transfer it was taking, so the one
    /// on its way failed and can be tried again; the ones waiting behind it
    /// never started.
    func interruptUploads() {
        if let active = activeUpload {
            forgetPreview(slot: active.slot)
            keepFailed(active)
            imageUploadState = .failed("the connection dropped before it arrived")
            resolveUpload(active.id, .interrupted)
        }
        for item in imageQueue {
            forgetPreview(slot: item.slot)
            keepFailed(item)
            resolveUpload(item.id, .interrupted)
        }
        activeUpload = nil
        imageBegun = nil
        imageQueue = []
        imageBundle = Data()
        uploadEnds = [:]
    }

    /// A picture that did not arrive must not go on being shown.
    func forgetPreview(slot: Int) {
        guard let crc = pendingCrc[slot] else { return }
        current?.forgetFace(crc: crc)
        faces[crc] = nil
        pendingCrc[slot] = nil
    }

    // ── Adding ────────────────────────────────────────────────────────────
    /// WHAT A PICTURE IS, IF THE TWO SIDES DISAGREE ABOUT IT. The machine says
    /// how many bytes a bundle is; this app makes a fixed number of them. When
    /// those differ, every picture this app can produce will be refused, and it
    /// is refused after the resampling and after the whole bundle has crossed
    /// BLE — so the answer is known here, before any of that is spent, and
    /// nothing about it is the photograph's fault.
    ///
    /// Nil while the machine has not said yet, which is not a disagreement.
    var imageSizeMismatch: String? {
        let theirs = imageSlots.bundleBytes
        guard theirs > 0, theirs != ImageBundle.byteCount else { return nil }
        return "this app and the machine disagree about what a picture is "
             + "(\(ImageBundle.byteCount) bytes against \(theirs)) — one of them is a version behind"
    }

    /// Take a picture for the machine. Choosing the next one never waits on the
    /// last: a queued picture is a real tile in the place it will occupy, and
    /// the "+" stays live the whole time.
    func enqueueImage(_ crop: UIImage, preview: UIImage?) -> QueuedImage? {
        if let why = imageSizeMismatch {
            imageUploadState = .failed(why)
            return nil
        }
        guard !demoMode, linked, let slot = nextFreeSlot() else { return nil }
        let item = QueuedImage(crop: crop, slot: slot, preview: preview)
        imageQueue.append(item)
        if activeUpload == nil { startNextImage() }
        return item
    }

    /// A picture that didn't arrive goes up again, into whichever slot is
    /// free now, as a new trip. It is kept until the new trip has started.
    func retryUpload(_ id: UUID) -> QueuedImage? {
        guard let failed = failedUploads[id], failed.machine == current?.id else { return nil }
        guard let item = enqueueImage(failed.image.crop, preview: failed.image.preview) else { return nil }
        failedUploads[id] = nil
        if case .failed = imageUploadState { imageUploadState = .idle }
        return item
    }

    /// Whether this picture can be tried again here.
    func canRetryUpload(_ id: UUID) -> Bool { failedUploads[id]?.machine == current?.id }

    /// A choice gone, or its machine: its picture is no longer kept.
    func dropFailedUpload(_ id: UUID) { failedUploads[id] = nil }

    func forgetUploads(machine: String) {
        failedUploads = failedUploads.filter { $0.value.machine != machine }
    }

    private func keepFailed(_ item: QueuedImage) {
        if let machine = current?.id { failedUploads[item.id] = (machine, item) }
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

        Task {
            let prepared = await PreparedImage.make(from: item.crop)
            // A link let go while this was being made took the picture with it.
            guard activeUpload?.id == item.id else { return }
            guard let prepared else {
                forgetPreview(slot: item.slot)
                keepFailed(item)
                activeUpload = nil
                imageUploadState = .failed("that picture would not convert")
                resolveUpload(item.id, .failed("that picture would not convert"))
                startNextImage()
                return
            }
            startImagePush(prepared, slot: item.slot)
        }
    }

    /// One finished, one way or another. The next starts after a beat so a run
    /// of pictures does not strobe.
    private func finishActive(_ outcome: ImageUploadState) {
        if case .failed = outcome, let active = activeUpload { keepFailed(active) }
        imageBegun = nil
        if let id = activeUpload?.id {
            switch outcome {
            case .done: resolveUpload(id, .stored)
            case .failed(let why): resolveUpload(id, .failed(why))
            default: resolveUpload(id, .canceled)
            }
        }
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

    private func startImagePush(_ prepared: PreparedImage, slot: Int) {
        let bundle = prepared.bundle
        imageBundle = bundle
        imageSlotSending = slot
        imageSentOffset = 0
        imageStartedAt = Date()
        uploadHeardAt = Date()
        uploadAsks = 0

        // The face is decoded out of the bundle just built and filed under
        // its crc32 — byte for byte what the board would send back if
        // asked, so an upload and a read-back agree without meeting.
        pendingCrc[slot] = prepared.crc
        if let face = prepared.face {
            current?.saveFace(face, crc: prepared.crc)
            faces[prepared.crc] = face
        }

        var payload = Data([UInt8(slot)])
        payload.append(contentsOf: withUnsafeBytes(of: UInt32(bundle.count).littleEndian, Array.init))
        payload.append(contentsOf: withUnsafeBytes(of: prepared.crc.littleEndian, Array.init))
        imageBegun = activeUpload?.id
        sendBLEFrame(type: ImageFrame.begin, payload: payload)
        log.info("slot \(slot): \(bundle.count) bytes")
        // Nothing is sent until the board answers BEGIN with the offset it
        // wants, which is also how it says the slot was erased and is ready.
    }

    /// The board's only steering signal: send from `have`.
    func handleImageAck(_ payload: Data) {
        guard payload.count >= 7 else { return }
        let b = payload.startIndex
        // Only the picture whose BEGIN went out is answered here: an answer
        // about another slot, or before BEGIN, is about one already finished.
        guard let active = activeUpload, imageBegun == active.id, Int(payload[b]) == active.slot else { return }
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
            let slot = imageSlotSending
            imageBundle = Data()
            forgetPreview(slot: slot)
            finishActive(.failed(why))
            log.error("slot upload failed: \(why)")
        case 2:   // DONE
            let took = Date().timeIntervalSince(imageStartedAt)
            let kbs = Double(imageBundle.count) / took / 1024
            log.info("done in \(took, format: .fixed(precision: 1))s — \(kbs, format: .fixed(precision: 1)) KB/s")
            imageBundle = Data()
            finishActive(.done)
            queryImageSlots()
        default:  // TAKING — either the opening ack, or a rewind
            guard !imageBundle.isEmpty else { return }
            guard err == 0 else {
                // The board said no while taking it: nothing more goes out.
                let why = Int(err) < uploadErrors.count ? uploadErrors[Int(err)] : "unknown"
                imageBundle = Data()
                forgetPreview(slot: active.slot)
                finishActive(.failed(why))
                return
            }
            if have != imageSentOffset {
                log.info("rewind \(self.imageSentOffset) -> \(have)")
                imageSentOffset = have
            }
            pumpImageFrames()
        }
    }

    /// Fill the link as far as it will take, then stop. iOS calls
    /// `peripheralIsReady` when it drains, which comes back here.
    func pumpImageFrames() {
        guard let p = connectedPeripheral, rxCharacteristic != nil, !imageBundle.isEmpty else { return }
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
            imageUploadState = .sending(sent: imageSentOffset, total: imageBundle.count)
        }

        // Everything is on the air. END is the one frame worth an acknowledged
        // write: it is what makes the board check the whole picture and keep it.
        sendBLEFrame(type: ImageFrame.end, payload: Data(), withResponse: true)
    }
}

/// A picture made ready to push: the bundle the board takes, the crc32 it
/// holds that bundle to, and the face decoded back out of it.
nonisolated struct PreparedImage: Sendable {
    let bundle: Data
    let crc: UInt32
    let face: UIImage?

    /// Every rendition resampled, off the main actor.
    @concurrent
    static func make(from crop: UIImage) async -> PreparedImage? {
        guard let bundle = ImageBundle.make(from: crop) else { return nil }
        return PreparedImage(bundle: bundle, crc: crc32(bundle), face: ImageBundle.face(of: bundle))
    }
}

/// The crc32 the board holds a picture to before it writes its header.
nonisolated func crc32(_ data: Data) -> UInt32 {
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
