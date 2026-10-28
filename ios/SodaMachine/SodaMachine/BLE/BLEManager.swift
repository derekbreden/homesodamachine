import Foundation
import CoreBluetooth
import UIKit
import SwiftUI
import os

/// Nordic UART Service UUIDs (must match S3 firmware)
private let nusServiceUUID = CBUUID(string: "6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
private let nusRxUUID = CBUUID(string: "6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
private let nusTxUUID = CBUUID(string: "6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

private let log = Logger(subsystem: "com.derekbreden.SodaMachine", category: "BLE")

private let scanTimeout: TimeInterval = 10

enum ConnectionState: Equatable {
    case bluetoothOff
    case searching
    case searchingLong  // been searching a while, show hints
    case connecting
    case connected
}

// ────────────────────────────────────────────────────────────
// BLEManager — @Observable so SwiftUI only re-renders views
// that read the specific property that changed.
// ────────────────────────────────────────────────────────────

@Observable
class BLEManager {
    var connectionState: ConnectionState = .bluetoothOff

    // ── The machine this phone is pointed at ──────────────────────────────
    // Everything a machine has said lives on its record, which outlives the
    // link. What is here is the link: whether it is up, what is crossing it,
    // and which machines the radio can hear. The fields below that read like
    // the machine's own are the record's, reached through the link so that
    // every screen and every frame handler has one name for each.
    let directory: MachineDirectory
    var current: KnownMachine? { directory.current }

    /// Up, to the machine this phone is pointed at. The demo counts: it is
    /// always in range.
    var linked: Bool { connectionState == .connected }

    // ── The bridge to the main board (MachineBridge.swift) ───────────────
    /// What the faucet said it carries, answering IDENTITY on this link; nil
    /// until it has.
    var bridgeVersion: Int?
    /// The faucet answered IDENTITY and said nothing about a bridge: its
    /// software predates it.
    var bridgeMissing = false
    @ObservationIgnored var bridgeNextID: UInt8 = 0
    @ObservationIgnored var bridgeWaiting: [UInt8: CheckedContinuation<Result<BridgeAnswer, BridgeError>, Never>] = [:]
    /// The demo's run in progress (DemoMachine.swift).
    @ObservationIgnored var demoRunTask: Task<Void, Never>?

    // ── Trust (MachineTrust.swift) ───────────────────────────────────────
    /// Where this device stands with the machine on this link; nil until the
    /// faucet says, and from a faucet that does not ask for trust.
    var trust: TrustStanding?
    /// The ask on the machine's displays from this device, while there is one.
    var trustAsk: TrustAsk?
    /// When the setup ask was answered Trust, for the Machine page to say so.
    var trustGrantedAt: Date?
    @ObservationIgnored var trustWaiting: CheckedContinuation<TrustOutcome, Never>?
    @ObservationIgnored var trustAskSeq = 0
    @ObservationIgnored var trustAskOnLink = false

    // The demo: a machine that is always in range and never existed.
    var demoMode: Bool { current?.isDemo ?? false }

    // ── The user's own pictures ───────────────────────────────────────────
    // What the machine says it holds, and how an upload to it is going. The
    // bundle itself is held only for the length of the push.
    var imageSlots: ImageSlots {
        get { current?.imageSlots ?? ImageSlots() }
        set { current?.imageSlots = newValue; directory.touch() }
    }
    var flavorArt: FlavorArt {
        get { current?.flavorArt ?? FlavorArt() }
        set { current?.flavorArt = newValue; directory.touch() }
    }
    var imageQueue: [QueuedImage] = []
    /// The last picture that did not reach the machine, kept for Try again.
    var failedImage: QueuedImage?
    // A read-back in flight, and the crcs already asked for, so a face is
    // fetched once ever rather than once per state frame.
    /// Faces by the crc32 of the picture they belong to, on the record.
    /// Observable, so a face that lands redraws the tile that was waiting for it.
    var faces: [UInt32: UIImage] {
        get { current?.faces ?? [:] }
        set { current?.faces = newValue }
    }
    // A picture being read back, placed by offset rather than accumulated in
    // order — see handleImagePix. `faceHave` is the offsets that have landed;
    // the stride is what one frame carries, which the board fixes.
    @ObservationIgnored var facePixels = Data()
    @ObservationIgnored var faceHave = Set<Int>()
    @ObservationIgnored var faceReceived = 0
    @ObservationIgnored var facePixelStride = 0
    @ObservationIgnored var faceSlot = -1
    /// The picture the read in flight is for, by its own crc32.
    @ObservationIgnored var faceCrc: UInt32 = 0
    @ObservationIgnored var faceAskedAt = Date.distantPast
    @ObservationIgnored var faceResumes = 0
    @ObservationIgnored var faceTotal = 0
    @ObservationIgnored var facePump: Timer?
    @ObservationIgnored var faceSaidAt = Date.distantPast
    @ObservationIgnored var faceSweptAt = Date.distantPast
    // The last standing condition reported to the machine's console, so one
    // that persists is said when it starts rather than at the polling rate.
    @ObservationIgnored var saidStanding = ""
    @ObservationIgnored var pendingCrc: [Int: UInt32] = [:]
    var activeUpload: QueuedImage?
    var imageUploadState: ImageUploadState = .idle
    @ObservationIgnored var imageBundle = Data()
    @ObservationIgnored var imageSlotSending = 0
    @ObservationIgnored var imageSentOffset = 0
    @ObservationIgnored var imageStartedAt = Date()
    // When the machine last said anything about the picture going up, and how
    // many times it has been asked again since. A notification is not
    // acknowledged, so the one frame that says "kept it" can simply be lost —
    // and with every byte already sent, nothing else was ever going to arrive.
    @ObservationIgnored var uploadHeardAt = Date.distantPast
    @ObservationIgnored var uploadAsks = 0

    // ── Which machines are in range ──────────────────────────────────────
    // Every scan result lands here rather than the first one winning. A phone
    // standing between the bench and the machine under the sink sees both.
    // The one this phone is pointed at is connected to as soon as it is heard,
    // and a known machine among the rest has its sighting noted. A scan hears
    // only the machines the system has handed this app — every machine in
    // range, on a phone that gave an earlier build Bluetooth access of its
    // own — and adding one is the system's sheet, not this list.
    var discovered: [DiscoveredMachine] = []

    /// Scanning while connected, for a list that wants to say what is in range
    /// right now. Off, the radio scans only while it has nothing to talk to.
    var browsing = false

    /// The phone's radio is off, or this app may not use it. Said once the
    /// system has said so.
    var radioOff = false

    @ObservationIgnored fileprivate var lastRssiPush: [String: Date] = [:]

    /// Counts the links this phone has opened and let go. A notification's
    /// frames are read under the generation it arrived in, and stop at the
    /// first one that lets that link go.
    @ObservationIgnored var linkGeneration = 0

    /// The pending name has gone to the machine on this link, and the next
    /// identity it answers is its word on it.
    @ObservationIgnored fileprivate var namePushed = false

    // ── Pushing an image ─────────────────────────────────────────────────
    // The board pulls. It asks for an offset and a length, this sends exactly
    // that, and nothing moves until it asks again — so the phone never has to
    // guess a rate, and a frame that goes missing costs one re-ask.
    var otaProgress: OTAProgress? = nil
    /// What the board with the radio says it is running, from BLE_IDENTITY.
    var radioBoardVersion: String {
        get { current?.radioBoardVersion ?? "" }
        set { current?.radioBoardVersion = newValue; directory.touch() }
    }
    /// What every board on the machine reports, assembled by its main board.
    var machineVersions: MachineVersions {
        get { current?.versions ?? MachineVersions() }
        set { current?.versions = newValue; directory.touch() }
    }

    @ObservationIgnored fileprivate var otaImage: FirmwareImage? = nil
    @ObservationIgnored fileprivate var otaData: Data = Data()

    /// What one tap of Update still owes. A board reboots into its new image and
    /// the link comes back before the next one starts, so these go one at a time.
    var otaQueue: [FirmwareImage] = []
    var otaQueueDone: Int = 0

    /// A run has sent its last image and the machine is going down into it.
    ///
    /// WHAT WAS SENT IS NOT WHAT IS RUNNING. A board answers DONE when the image
    /// is written and its boot partition moved, which is a sentence about flash
    /// — the machine still has to come back on that image before anyone can say
    /// the update took. So a run is not over when the last byte lands: the
    /// readings this phone holds describe the machine as it was, they are
    /// dropped here, and what is said next is decided by what the boards report
    /// when they answer again.
    var otaSettlingSince: Date? = nil

    /// How long to keep asking. A machine that has not answered by here is not
    /// going to inside a screen anyone is still watching, and saying so is
    /// better than a bar that never ends.
    static let otaSettleGiveUp: TimeInterval = 120
    /// An answer sooner than this is the machine on its way down, not back up:
    /// a board can answer in the moment between DONE and its own reboot, and
    /// that answer describes the image it is leaving.
    static let otaSettleFloor: TimeInterval = 15
    @ObservationIgnored fileprivate var otaModel: MachineModel = .unknown
    @ObservationIgnored fileprivate var otaFetch: ((FirmwareImage) async throws -> Data)? = nil

    /// Which screens this machine gets. A machine whose advertisement carried
    /// no model byte is running firmware older than that, and every one of
    /// those is a prototype.
    var isAppliance: Bool { current?.model == .appliance }

    // ── Internal state (not observed by SwiftUI) ──

    // GATT/NUS state
    @ObservationIgnored fileprivate var nusReady = false
    @ObservationIgnored var rxCharacteristic: CBCharacteristic?

    // ONE THREAD HOLDS THE LINK. CoreBluetooth calls back on the main queue,
    // and the link, the record and a picture half-read all live on the main
    // actor with it. A photograph is resampled into a bundle off it: see
    // PreparedImage.
    @ObservationIgnored fileprivate var cbAdapter: CBDelegateAdapter!
    @ObservationIgnored fileprivate var centralManager: CBCentralManager!
    @ObservationIgnored var connectedPeripheral: CBPeripheral?
    @ObservationIgnored fileprivate var scanTimer: Timer?
    /// The link was reached by peripheral id, and the board has not yet said
    /// which machine it is in.
    @ObservationIgnored fileprivate var unverified = false
    /// Which link's identity is being waited on.
    @ObservationIgnored fileprivate var identityAsk = 0
    /// Which connection attempt watchConnecting is timing.
    @ObservationIgnored fileprivate var connectingWatch = 0
    @ObservationIgnored fileprivate var reconnectTimer: Timer?

    init(directory: MachineDirectory) {
        self.directory = directory
        cbAdapter = CBDelegateAdapter(self)
    }

    /// Turn the radio toward the machine this phone is pointed at, bringing
    /// it up if it is not yet. The central manager outlives a disconnect — it
    /// is the app's, not the connection's — and creating it is what first
    /// turns the radio, by way of `centralManagerDidUpdateState`. A link
    /// already up, or on its way, is left alone.
    func activateBluetooth() {
        guard connectionState != .connected, connectionState != .connecting else { return }
        point()
    }

    /// Called when the app returns to foreground after being backgrounded.
    /// Restarts scanning if not connected: iOS silently stops scans while
    /// backgrounded.
    func handleReturnToForeground() {
        guard !demoMode, centralManager != nil else { return }

        if connectionState == .searching || connectionState == .searchingLong, current != nil {
            // Looking: iOS may have stopped the scan while the app was away, so
            // it looks again. A connection on its way is left to land — it was
            // asked for by peripheral id or by a sighting, and either one waits
            // for the radio on its own. Cancelling it here aborted a link a
            // second from up on every pull of Control Center or a notification.
            // One that never lands is let go by watchConnecting.
            point()
        }
    }

    /// A PHONE IN A POCKET HOLDS NONE OF THE MACHINE'S LINKS. The faucet takes
    /// three at once, and an app that kept its link in the background — and
    /// asked for the machine again whenever it lost one — would hold a link for
    /// as long as the phone was in the house. So the link is let go when the
    /// app leaves the screen, unless something is crossing it, and taken up
    /// again when the app returns.
    func handleEnterBackground() {
        guard !demoMode, centralManager != nil, current != nil, !transferInFlight else { return }
        dropLink()
    }

    /// An update or a picture on its way across the link.
    var transferInFlight: Bool {
        // A finished or failed update stays on screen until it is dismissed,
        // and is not crossing the link.
        if let p = otaProgress, !p.finished, p.failure == nil { return true }
        if !otaQueue.isEmpty || otaSettlingSince != nil { return true }
        switch imageUploadState {
        case .preparing, .sending: return true
        default: return false
        }
    }

    fileprivate var inBackground: Bool { UIApplication.shared.applicationState == .background }

    // MARK: - Public API

    /// Send a text command to the S3 via BLE GATT/NUS.
    /// Wire format: [type(1B)][len(2B LE)][payload...]
    func send(_ text: String) {
        guard let payload = text.data(using: .utf8) else { return }
        sendBLEFrame(type: 0x01, payload: payload)
        log.debug("TX: \(text)")
    }

    /// Send a framed BLE message: [type(1B)][len(2B LE)][payload...]
    // withResponse costs a round trip per frame, which is the right price for a
    // command and the wrong one for a stream: it is what holds the firmware
    // path to one frame per connection interval. A picture's data frames go
    // without it and are steered by the offsets the board reports instead.
    func sendBLEFrame(type: UInt8, payload: Data, withResponse: Bool = true) {
        guard let rx = rxCharacteristic, let p = connectedPeripheral else { return }
        var frame = Data([type, UInt8(payload.count & 0xFF), UInt8((payload.count >> 8) & 0xFF)])
        frame.append(payload)
        p.writeValue(frame, for: rx, type: withResponse ? .withResponse : .withoutResponse)
    }

    // MARK: - Your machines

    /// Point the phone at one machine. The link to the last one is dropped;
    /// nothing it said is, because that lives on its record.
    func select(_ machine: KnownMachine) {
        guard current?.id != machine.id else { return }
        dropLink()
        directory.select(machine)
        point()
    }

    /// A machine the system's sheet has just handed over: added, pointed at,
    /// and reached by the peripheral id the system gave it.
    @discardableResult
    func add(peripheralID: String) -> KnownMachine {
        dropLink()
        let m = directory.add(peripheralID: peripheralID)
        directory.select(m)
        point()
        return m
    }

    func addDemo() {
        dropLink()
        directory.select(directory.addDemo())
        point()
    }

    /// Gone from the phone. If it was the one the phone was pointed at, the
    /// phone points at whichever it talked to most recently, or at nothing.
    func forget(_ machine: KnownMachine) {
        let wasCurrent = current?.id == machine.id
        if wasCurrent { dropLink() }
        directory.forget(machine)
        if wasCurrent { point() }
    }

    /// What a person calls this machine. The name lives on the main board and
    /// the radio advertises it, so it is sent there when the machine can hear;
    /// until then the record carries it and the page shows it. Twenty bytes,
    /// which is what the board keeps, cut on a character.
    func rename(_ machine: KnownMachine, to raw: String) {
        var bytes = Array(raw.trimmingCharacters(in: .whitespacesAndNewlines).utf8.prefix(20))
        while !bytes.isEmpty, String(bytes: bytes, encoding: .utf8) == nil { bytes.removeLast() }
        let name = String(bytes: bytes, encoding: .utf8) ?? ""
        guard !name.isEmpty else { return }
        machine.name = name
        if machine.isDemo { directory.save(); return }
        machine.pendingName = name
        if linked, current?.id == machine.id, trust == nil || trust == .trusted {
            send("IDENTITY \(name)")
            namePushed = true
        }
        directory.save()
    }

    /// A name given while the machine could not take it — out of earshot, or
    /// not yet trusting this device — sent now that it can.
    func pushPendingName() {
        guard linked, let name = current?.pendingName else { return }
        send("IDENTITY \(name)")
        namePushed = true
    }

    /// Turn the radio toward the machine this phone is pointed at: the demo is
    /// simply up, anything else is listened for, and nothing means the radio
    /// rests until a machine is added.
    fileprivate func point() {
        guard let m = current else {
            centralManager?.stopScan()
            scanTimer?.invalidate()
            connectionState = radioDown ? .bluetoothOff : .searching
            return
        }
        if m.isDemo {
            centralManager?.stopScan()
            scanTimer?.invalidate()
            reconnectTimer?.invalidate()
            seedDemo(m)
            connectionState = .connected
            return
        }
        // A prototype is listed, and never connected to.
        guard m.supported else {
            centralManager?.stopScan()
            scanTimer?.invalidate()
            reconnectTimer?.invalidate()
            connectionState = radioDown ? .bluetoothOff : .searching
            return
        }
        // A real machine is the first thing that needs the radio, which comes
        // up once the system has said which machines this app may reach.
        ensureRadio()
        connectionState = radioDown ? .bluetoothOff : .searching
        startScan()
    }

    // ── The radio, and the system's say over it ──────────────────────────
    // THE CENTRAL MANAGER WAITS FOR THE SYSTEM. Which machines this app may
    // reach is the system's to say (MachineAccess), and on a phone that gave
    // an earlier build Bluetooth access of its own, the system will not open
    // its sheet — to add a machine, or to carry that build's machines over —
    // while this app holds a central manager. So none is made until the
    // system's list is settled at launch, and the one there is goes whenever
    // the sheet has to come up over it.

    /// The radio may come up.
    @ObservationIgnored fileprivate var radioAllowed = false

    fileprivate func ensureRadio() {
        guard centralManager == nil, radioAllowed else { return }
        // No queue is the main queue: see ONE THREAD HOLDS THE LINK.
        centralManager = CBCentralManager(delegate: cbAdapter, queue: nil)
    }

    /// Let the radio go — the link, the scan, and the central manager itself —
    /// until `allowRadio`.
    func holdRadio() {
        radioAllowed = false
        dropLink()
        centralManager = nil
    }

    /// Bring the radio up, turned toward the machine this phone is pointed at.
    func allowRadio() {
        guard !radioAllowed else { return }
        radioAllowed = true
        point()
    }

    /// The radio has said it cannot be used. A radio still making up its mind
    /// is not that.
    private var radioDown: Bool {
        switch centralManager?.state {
        case .poweredOff, .unauthorized, .unsupported: return true
        default: return false
        }
    }

    /// The link, and everything in flight on it, let go. What the machine said
    /// stays on its record.
    fileprivate func dropLink() {
        linkGeneration += 1
        unverified = false
        centralManager?.stopScan()
        scanTimer?.invalidate()
        reconnectTimer?.invalidate()
        stopFacePump()
        // The peripheral is let go before it is cancelled, so what the cancel
        // says back is not this link's any more.
        let peripheral = connectedPeripheral
        connectedPeripheral = nil
        rxCharacteristic = nil
        nusReady = false
        if let peripheral { centralManager?.cancelPeripheralConnection(peripheral) }
        if connectionState != .bluetoothOff { connectionState = .searching }
        namePushed = false
        abandonBridgeRequests()
        abandonTrust()
        imageQueue = []
        activeUpload = nil
        imageUploadState = .idle
        otaQueue = []
        otaProgress = nil
        otaImage = nil
        otaData = Data()
        otaFetch = nil
        imageBundle = Data()
        pendingCrc = [:]
        faceSlot = -1
        facePixels = Data()
        faceHave.removeAll()
        faceReceived = 0
    }

    // MARK: - Internal

    /// Listen for machines. While the phone has one to talk to and is not yet
    /// talking to it, this is how it finds it; while a list is open, this is
    /// how the list says what is in range.
    fileprivate func startScan() {
        guard let centralManager, centralManager.state == .poweredOn else { return }
        let idle = connectionState != .connected && connectionState != .connecting
        if idle { connectionState = .searching }
        discovered = []
        lastRssiPush = [:]
        // Duplicates on: RSSI is how a picker sorts, and a machine that moves
        // closer should climb the list rather than keep the reading it had when
        // it was first seen.
        centralManager.scanForPeripherals(withServices: [nusServiceUUID], options: [
            CBCentralManagerScanOptionAllowDuplicatesKey: true
        ])
        log.info("Scanning for machines...")

        guard idle else { return }
        reachKnown()
        scanTimer?.invalidate()
        // A timer scheduled here fires on the main run loop.
        scanTimer = Timer.scheduledTimer(withTimeInterval: scanTimeout, repeats: false) { [weak self] _ in
            MainActor.assumeIsolated {
                guard let self, self.connectionState == .searching else { return }
                self.connectionState = .searchingLong
                log.info("Still scanning, showing hints")
            }
        }
    }

    /// A list that wants to know what is in range right now, whether or not
    /// the radio is busy. Ends with the list.
    func beginBrowsing() {
        browsing = true
        ensureRadio()
        startScan()
    }

    func endBrowsing() {
        browsing = false
        if connectionState == .connected || connectionState == .connecting || current == nil {
            centralManager?.stopScan()
        }
    }

    /// One sighting. The machine this phone is pointed at is connected to on
    /// the spot; a known machine is noted as in range and takes whatever the
    /// advertisement says that its record did not yet have.
    fileprivate func noteSighting(_ seen: DiscoveredMachine) {
        guard var known = directory.machine(matching: seen) else {
            log.info("\(seen.id) is none of this phone's machines")
            return
        }
        known.lastSeen = seen.lastSeen
        if known.peripheralID != seen.id {
            known.peripheralID = seen.id
            directory.touch()
        }
        if known.unit.isEmpty, !seen.unit.isEmpty {
            known = directory.introduce(known, unit: seen.unit, name: "")
        }
        if !seen.name.isEmpty, known.pendingName == nil, known.name != seen.name {
            known.name = seen.name
            directory.touch()
        }
        // Which kind of machine, in its own advertisement: one the system's
        // sheet handed over came with no advertisement at all.
        if seen.model != .unknown, known.model != seen.model {
            known.model = seen.model
            directory.touch()
        }
        if let m = current, m.id == known.id, m.supported,
           connectionState == .searching || connectionState == .searchingLong {
            connect(m, peripheralID: seen.id, unit: seen.unit)
        }
    }

    /// Open the link to the machine this phone is pointed at, whose peripheral
    /// the radio has just heard.
    fileprivate func connect(_ machine: KnownMachine, peripheralID: String, unit: String) {
        guard let centralManager,
              let peripheral = centralManager.retrievePeripherals(withIdentifiers:
                  [UUID(uuidString: peripheralID)].compactMap { $0 }).first
        else { return }

        scanTimer?.invalidate()
        if !browsing { centralManager.stopScan() }
        machine.peripheralID = peripheralID
        // A connection still waiting on the radio this machine had before —
        // a board since replaced — is let go before it is cancelled, so what
        // the cancel says back is not this link's.
        let waiting = connectedPeripheral
        connectedPeripheral = peripheral
        if let waiting, waiting !== peripheral { centralManager.cancelPeripheralConnection(waiting) }
        // A sighting that carried a unit was matched on it; one that did not
        // was matched on peripheral id, and is asked like any other.
        unverified = unit.isEmpty
        connectionState = .connecting
        centralManager.connect(peripheral, options: nil)
        watchConnecting()
    }

    /// A CONNECTION THAT HAS NOT FINISHED IN FIFTEEN SECONDS IS NOT GOING TO.
    /// A machine that walked away mid-connect, or a link that came up and then
    /// never offered its service, would otherwise hold the page on
    /// "Connecting…" for good. Let go, the phone looks again — by sighting and
    /// by peripheral id — and the page says what it is doing.
    fileprivate func watchConnecting() {
        connectingWatch += 1
        let watch = connectingWatch
        DispatchQueue.main.asyncAfter(deadline: .now() + 15) { [weak self] in
            guard let self, watch == self.connectingWatch, self.connectionState == .connecting else { return }
            log.info("Connection did not finish in 15 s; looking again")
            self.dropLink()
            self.point()
        }
    }

    /// The NUS link is open. A link a sighting opened carries the unit the scan
    /// matched. One reached by peripheral id was reached by the board, and a
    /// board can be moved into another machine — so it says which machine it
    /// is in before anything is read off it or written to it.
    fileprivate func nusOpened() {
        if unverified, let machine = current, !machine.unit.isEmpty {
            identityAsk += 1
            send("IDENTITY")
            askWhoItIs(tries: 3, on: connectedPeripheral, ask: identityAsk)
            return
        }
        unverified = false
        linkReady()
    }

    /// A board that has not answered is asked again; one that never answers is
    /// taken at its peripheral id, which is all this phone ever had for it.
    /// Each chain belongs to the link that opened it, and ends with that link.
    private func askWhoItIs(tries: Int, on peripheral: CBPeripheral?, ask: Int) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) { [weak self] in
            guard let self, self.unverified, ask == self.identityAsk,
                  let peripheral, peripheral === self.connectedPeripheral,
                  peripheral.state == .connected, self.nusReady else { return }
            if tries > 0 {
                self.send("IDENTITY")
                self.askWhoItIs(tries: tries - 1, on: peripheral, ask: ask)
            } else {
                log.info("No identity from \(self.current?.displayName ?? "?"); taking it at its id")
                self.unverified = false
                self.linkReady()
            }
        }
    }

    /// The machine this phone is pointed at is on the other end: say so, and
    /// ask it for what its page shows.
    fileprivate func linkReady() {
        connectionState = .connected
        if let machine = current {
            machine.lastConnected = Date()
            // ASK A MACHINE WHO IT IS RATHER THAN WAIT TO BE TOLD.
            // A record with no unit matches only on peripheral id, and
            // those are per app install — one reinstall and it is orphaned
            // against the machine it belongs to. The board answers this
            // with its identity, its bridge and where this device stands,
            // and `introduce` folds the record into the unit's own. A name
            // given while the machine was out of earshot follows once the
            // machine trusts this device (pushPendingName).
            send("IDENTITY")
            directory.save()
        }
        // A prototype is listed and can be removed. An appliance is asked
        // what pictures it holds and which one each channel wears; the rest
        // of what its pages show is read once the faucet says it carries the
        // bridge.
        guard current?.supported == true else { return }
        saidStanding = ""   // a new session reports its own conditions
        queryImageSlots()
        queryFlavorArt()
        startFacePump()
    }

    /// THE MACHINE THIS PHONE KNOWS IS ASKED FOR, NOT ONLY LISTENED FOR. A
    /// connection to a peripheral iOS already knows needs no scan: it waits,
    /// and completes the moment that radio is heard advertising connectably —
    /// whatever its advertisement carries, and in the background too. A
    /// machine whose advertisement has lost the service is a machine a
    /// filtered scan never hears, and this one still reaches it. The scan runs
    /// beside it: it is how a replaced board is found again by its unit, and
    /// how a list says what is in range. The page keeps saying "looking" until
    /// the radio answers.
    fileprivate func reachKnown() {
        guard !inBackground, let centralManager, centralManager.state == .poweredOn,
              let machine = current, !machine.isDemo, machine.supported,
              let id = machine.peripheralID.flatMap(UUID.init(uuidString:)),
              let peripheral = centralManager.retrievePeripherals(withIdentifiers: [id]).first
        else { return }
        if let held = connectedPeripheral, held.state == .connecting || held.state == .connected { return }
        connectedPeripheral = peripheral
        unverified = true
        centralManager.connect(peripheral, options: nil)
        log.info("Waiting on \(machine.displayName) by its peripheral id")
    }

    // ── The image push ───────────────────────────────────────────────────
    fileprivate static let bleOtaBegin: UInt8 = 0x10
    fileprivate static let bleOtaNeed:  UInt8 = 0x11
    fileprivate static let bleOtaData:  UInt8 = 0x12
    fileprivate static let bleOtaEnd:   UInt8 = 0x13
    fileprivate static let bleIdentity: UInt8 = 0x14
    fileprivate static let bleVersions: UInt8 = 0x15

    /// Start pushing one image. `data` has already been held to the manifest's
    /// sha256; the crc32 goes onto the wire for the board to hold it to.
    func startUpdate(image: FirmwareImage, data: Data, on model: MachineModel) {
        guard otaProgress == nil else { return }
        guard let target = image.otaTarget(on: model) else { return }

        otaImage = image
        otaData = data
        otaProgress = OTAProgress(target: image.target, what: image.what,
                                  sent: 0, total: data.count)

        var payload = Data([target.rawValue, image.otaKind.rawValue])
        payload.append(contentsOf: withUnsafeBytes(of: UInt32(data.count).littleEndian, Array.init))
        payload.append(contentsOf: withUnsafeBytes(of: image.crc32.littleEndian, Array.init))
        sendBLEFrame(type: BLEManager.bleOtaBegin, payload: payload)
        log.info("OTA \(image.target): \(data.count) bytes, crc \(image.crc32)")
    }

    /// One tap: every image this machine is behind on, in order.
    ///
    /// THE RADIO BOARD GOES LAST. Each board reboots into what it took, and the
    /// board holding the radio is the one the session runs on — rebooting it
    /// drops the connection carrying everything still queued behind it. So the
    /// far display goes first, the main board next, and the radio last, where
    /// the only thing its reboot ends is a queue that is already empty.
    func startUpdateAll(_ images: [FirmwareImage], on model: MachineModel,
                        fetch: @escaping (FirmwareImage) async throws -> Data) {
        guard otaQueue.isEmpty, otaProgress == nil, !images.isEmpty else { return }
        otaModel = model
        otaFetch = fetch
        otaQueueDone = 0
        func order(_ i: FirmwareImage) -> Int {
            switch i.otaTarget(on: model) {
            case .farDisplay: return 0
            case .mainBoard:  return 1
            case .radioBoard: return 2
            case nil:         return 3
            }
        }
        // Art before the firmware of the display that renders it: the app checks
        // the partition at boot, so the reboot that ends this run finds it there.
        otaQueue = images.sorted { (order($0), $0.kind == "art" ? 0 : 1)
                                 < (order($1), $1.kind == "art" ? 0 : 1) }
        pumpQueue()
    }

    fileprivate func pumpQueue() {
        guard let next = otaQueue.first, let fetch = otaFetch else {
            otaFetch = nil
            return
        }
        Task {
            do {
                let data = try await fetch(next)
                startUpdate(image: next, data: data, on: otaModel)
            } catch {
                otaProgress = OTAProgress(target: next.target, what: next.what,
                                          sent: 0, total: next.bytes,
                                          failure: error.localizedDescription)
                otaQueue = []
                otaFetch = nil
            }
        }
    }

    func cancelUpdate() {
        guard let image = otaImage else { return }
        log.info("OTA \(image.target): cancelled")
        otaQueue = []
        otaFetch = nil
        finishUpdate(failure: "cancelled")
    }

    fileprivate func finishUpdate(failure: String?) {
        if var p = otaProgress {
            p.failure = failure
            p.finished = failure == nil
            otaProgress = p
        }
        otaImage = nil
        otaData = Data()

        guard failure == nil else { otaQueue = []; otaFetch = nil; return }
        if !otaQueue.isEmpty { otaQueue.removeFirst(); otaQueueDone += 1 }
        guard !otaQueue.isEmpty else {
            otaFetch = nil
            // The board that took the last image is rebooting, and it is the one
            // this connection runs on. The page stays; the link comes back, and
            // the run stays open until it does — nothing here knows yet whether
            // the machine is running what it was just sent.
            otaSettlingSince = Date()
            machineVersions = MachineVersions()
            settleTick()
            return
        }
        // The board that just took an image is rebooting into it, and on the far
        // side of a relay the link has to come back up before the next one can
        // start. J9 and J3 both take seconds to re-establish after a reset.
        let delay: TimeInterval = 12
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            guard let self, !self.otaQueue.isEmpty else { return }
            self.otaProgress = nil
            self.pumpQueue()
        }
    }

    /// While a run settles: ask again as the machine comes back. An answer is
    /// the only thing that ends this, so the asking is what it costs — and a
    /// machine that never answers stops being waited for rather than leaving a
    /// bar running against nothing.
    fileprivate func settleTick() {
        guard let began = otaSettlingSince else { return }
        guard Date().timeIntervalSince(began) < Self.otaSettleGiveUp else {
            otaSettlingSince = nil
            return
        }
        // The faucet answers IDENTITY with what every board runs.
        if linked { send("IDENTITY") }
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) { [weak self] in
            self?.settleTick()
        }
    }

    /// The board asking for the next piece. Answering is the whole of the
    /// phone's side: no timer, no pacing, no guess at a rate.
    fileprivate func handleOtaNeed(_ payload: Data) {
        guard payload.count >= 6, !otaData.isEmpty else { return }
        let b = payload.startIndex
        let offset = Int(UInt32(payload[b]) | (UInt32(payload[b + 1]) << 8) |
                         (UInt32(payload[b + 2]) << 16) | (UInt32(payload[b + 3]) << 24))
        let want = Int(UInt16(payload[b + 4]) | (UInt16(payload[b + 5]) << 8))
        guard offset >= 0, offset < otaData.count, want > 0 else { return }
        let end = min(offset + want, otaData.count)

        var frame = Data()
        frame.append(contentsOf: withUnsafeBytes(of: UInt32(offset).littleEndian, Array.init))
        frame.append(otaData[offset..<end])
        sendBLEFrame(type: BLEManager.bleOtaData, payload: frame)

        if var p = otaProgress, end > p.sent {
            p.sent = end
            otaProgress = p
        }
    }

    fileprivate func handleOtaEnd(_ payload: Data) {
        guard payload.count >= 6 else { return }
        let b = payload.startIndex
        let state = payload[b]
        let err = OTAError(rawValue: payload[b + 1]) ?? .none
        // OTA_STATE_DONE is 3 (proto_msg.h).
        if state == 3 {
            log.info("OTA \(self.otaImage?.target ?? "?"): verified and set to boot")
            finishUpdate(failure: nil)
        } else {
            log.error("OTA failed: state \(state), \(err.detail)")
            finishUpdate(failure: err.message)
        }
    }

    fileprivate func handleIdentity(_ payload: Data) {
        // [model:1][unit:3][name:21][version…NUL]
        guard payload.count > 25 else { return }
        let b = payload.startIndex
        let versionBytes = payload[(b + 25)...].prefix { $0 != 0 }
        let version = String(data: Data(versionBytes), encoding: .utf8) ?? ""
        let name = String(data: Data(payload[(b + 4)..<(b + 25)].prefix { $0 != 0 }),
                          encoding: .utf8) ?? ""
        // The three bytes that say which machine this is. They were being
        // parsed and dropped, leaving the app to depend on a scan record having
        // seen the manufacturer block — and a machine whose unit is unknown can
        // neither file a face nor ask for one. A machine connected to has just
        // told us who it is; that beats what a scan happened to catch.
        let unit = payload[(b + 1)..<(b + 4)].map { String(format: "%02X", $0) }.joined()

        guard let m = current else { return }
        // THIS RADIO IS ANOTHER MACHINE'S NOW. A link reached by peripheral
        // id is reached by the board, and a board can be moved into another
        // machine. The unit is the machine, so a board that names a
        // different one is let go and its id with it; the machine is looked
        // for again by its unit.
        let reported = unit == "000000" ? "" : unit
        if !m.unit.isEmpty, !reported.isEmpty, reported != m.unit {
            log.info("Peripheral \(m.peripheralID ?? "?") is unit \(reported), not \(m.unit)")
            m.peripheralID = nil
            directory.save()
            dropLink()
            point()
            return
        }
        // 000000 is a board whose main board has not answered it yet, which
        // says nothing about which machine it is in. The board says again
        // the moment its main board does.
        if unverified, reported.isEmpty { return }
        // Filed first, then the session opens: what it pushes — a pending
        // name — is answered by a reply of its own.
        defer {
            if unverified {
                unverified = false
                linkReady()
            }
        }
        // A name given while the machine was out of earshot stands until
        // the machine has answered the send — with that name, or with
        // whatever it made of it, which is then what the machine is called.
        let pending = m.pendingName
        let settled = pending == nil || pending == name || namePushed
        let said = directory.introduce(m, unit: unit == "000000" ? "" : unit,
                                       name: settled ? name : "")
        said.radioBoardVersion = version
        if settled { said.pendingName = nil }
        namePushed = false
        directory.save()
        noteIdentityAnswered()
    }

    /// VersionsPayload: [count:1] then count × [board:1][version:24][artCrc:4][buildEpoch:4].
    ///
    /// A main board built before `buildEpoch` sends 29-byte entries and this
    /// reads them, because the frame says how long an entry is: the length it
    /// arrived at, over the count it declares. The epoch is taken only when the
    /// entry is long enough to hold one, and stays absent otherwise — which
    /// `needs()` reads as "did not say" and answers with the dates instead.
    private static let versionCoreBytes = 29
    private static let versionEpochBytes = 33

    fileprivate func handleVersions(_ payload: Data) {
        guard payload.count >= 1 else { return }
        let b = payload.startIndex
        let count = min(Int(payload[b]), 3)
        guard count > 0 else { return }
        let stride = (payload.count - 1) / count
        guard stride >= Self.versionCoreBytes else { return }
        var found = MachineVersions()
        for i in 0..<count {
            let o = b + 1 + i * stride
            guard payload.count >= (o - b) + Self.versionCoreBytes else { break }
            let board = payload[o]
            let raw = payload[(o + 1)..<(o + 25)].prefix { $0 != 0 }
            found.byBoard[board] = String(data: Data(raw), encoding: .utf8) ?? ""
            found.artCrc[board] = UInt32(payload[o + 25]) | (UInt32(payload[o + 26]) << 8)
                                | (UInt32(payload[o + 27]) << 16) | (UInt32(payload[o + 28]) << 24)
            guard stride >= Self.versionEpochBytes,
                  payload.count >= (o - b) + Self.versionEpochBytes else { continue }
            found.buildEpoch[board] = UInt32(payload[o + 29]) | (UInt32(payload[o + 30]) << 8)
                                    | (UInt32(payload[o + 31]) << 16) | (UInt32(payload[o + 32]) << 24)
        }
        guard let m = current else { return }
        m.versions = found
        m.versionsReadAt = Date()
        // The machine has answered since it went down, so there is a fact
        // to report and the run is over. What that fact is — took, or did
        // not — is read off these versions like any other.
        if let began = otaSettlingSince,
           Date().timeIntervalSince(began) >= Self.otaSettleFloor {
            otaSettlingSince = nil
        }
        directory.touch()
    }

    fileprivate func scheduleReconnect() {
        reconnectTimer?.invalidate()
        reconnectTimer = Timer.scheduledTimer(withTimeInterval: 2, repeats: false) { [weak self] _ in
            MainActor.assumeIsolated {
                // From the background the link waits for the app to return:
                // see handleEnterBackground.
                guard let self, !self.inBackground else { return }
                self.startScan()
            }
        }
    }

}

// ────────────────────────────────────────────────────────────
// CBDelegateAdapter — thin NSObject that implements CoreBluetooth
// delegates and forwards to BLEManager. Required because @Observable
// classes cannot inherit from NSObject.
// ────────────────────────────────────────────────────────────

private class CBDelegateAdapter: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    unowned let ble: BLEManager

    init(_ ble: BLEManager) {
        self.ble = ble
        super.init()
    }

    // MARK: - CBCentralManagerDelegate

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        log.debug("Central state: \(central.state.rawValue)")
        if central.state == .poweredOn {
            // The radio is up: turned toward whatever the phone is pointed
            // at, and a list already open keeps looking too.
            ble.radioOff = false
            ble.point()
            if ble.browsing { ble.startScan() }
        } else {
            // The radio is down. The page says so; the demo does not care.
            ble.radioOff = true
            ble.point()
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral,
                         advertisementData: [String: Any], rssi RSSI: NSNumber) {
        guard let seen = MachineAdvert.read(peripheral: peripheral,
                                            advertisementData: advertisementData,
                                            rssi: RSSI) else { return }

        // Duplicates are on, so this runs many times a second per machine. Only
        // a sighting that changes what a row says reaches the list.
        if let i = ble.discovered.firstIndex(where: { $0.id == seen.id }) {
            let due = Date().timeIntervalSince(ble.lastRssiPush[seen.id] ?? .distantPast) >= 0.5
            let fills = (!seen.name.isEmpty && ble.discovered[i].name != seen.name)
                     || (!seen.unit.isEmpty && ble.discovered[i].unit != seen.unit)
                     || (seen.model != .unknown && ble.discovered[i].model != seen.model)
            guard due || fills else { return }
            ble.lastRssiPush[seen.id] = Date()
            var entry = ble.discovered[i]
            // Smoothed, because a raw reading swings ten dBm packet to
            // packet and the row would say "far" and "nearby" by turns.
            entry.rssi = (entry.rssi * 3 + seen.rssi) / 4
            entry.lastSeen = seen.lastSeen
            // A name or a unit that arrived in a later scan response fills
            // in what the first sighting did not carry.
            if !seen.name.isEmpty { entry.name = seen.name }
            if !seen.unit.isEmpty { entry.unit = seen.unit }
            if seen.model != .unknown { entry.model = seen.model }
            // ORDER IS NOT RE-DERIVED HERE. Sorting on every reading makes
            // rows trade places under a finger already on its way down.
            ble.discovered[i] = entry
            ble.noteSighting(entry)
            return
        }

        log.info("Found \(seen.displayName) at \(seen.rssi) dBm: unit \(seen.unit.isEmpty ? "none" : seen.unit), model \(seen.model.rawValue), peripheral \(seen.id)")
        ble.discovered.append(seen)
        ble.lastRssiPush[seen.id] = Date()
        // The set changed, so this is where the order is settled.
        ble.discovered.sort { $0.rssi > $1.rssi }
        ble.noteSighting(seen)
    }

    // EVERY CALLBACK IS HELD TO THE PERIPHERAL THIS LINK IS ON. A machine the
    // phone turned away from answers later, on its own time — its cancel, its
    // drop, its services — and none of that is the link the phone holds now.
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        guard peripheral === ble.connectedPeripheral else { return }
        log.info("Connected to \(peripheral.name ?? "device")")
        peripheral.delegate = self
        peripheral.discoverServices([nusServiceUUID])
        // A connection that was waiting by peripheral id lands without a
        // sighting ever having said so: the page moves on from "looking", and
        // the scan that was looking stops unless a list wants it.
        ble.scanTimer?.invalidate()
        if !ble.browsing { ble.centralManager?.stopScan() }
        if ble.connectionState == .searching || ble.connectionState == .searchingLong {
            ble.connectionState = .connecting
        }
        ble.watchConnecting()   // up at the radio; the clock starts again for the rest
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        guard peripheral === ble.connectedPeripheral else { return }
        log.error("Connection failed: \(error?.localizedDescription ?? "unknown")")
        ble.connectedPeripheral = nil
        ble.connectionState = ble.radioOff ? .bluetoothOff : .searching
        ble.scheduleReconnect()
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        guard peripheral === ble.connectedPeripheral else { return }
        log.info("Disconnected")
        ble.connectedPeripheral = nil
        ble.rxCharacteristic = nil
        ble.nusReady = false
        // A read in flight cannot survive the link it was on, and the record of
        // having asked must not either: `faceWanted` is what stops a picture
        // being asked for twice, so leaving it set across a disconnect means a
        // face that never arrived is never asked for again.
        ble.faceSlot = -1
        ble.facePixels = Data()
        ble.faceHave.removeAll()
        ble.faceReceived = 0
        ble.stopFacePump()
        ble.namePushed = false
        ble.abandonBridgeRequests()
        ble.abandonTrust()
        ble.connectionState = ble.radioOff ? .bluetoothOff : .searching
        ble.scheduleReconnect()
    }

    // MARK: - CBPeripheralDelegate (GATT service/characteristic discovery)

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard peripheral === ble.connectedPeripheral, error == nil, let services = peripheral.services else { return }
        for service in services where service.uuid == nusServiceUUID {
            peripheral.discoverCharacteristics([nusRxUUID, nusTxUUID], for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard peripheral === ble.connectedPeripheral, error == nil, let chars = service.characteristics else { return }
        for char in chars {
            if char.uuid == nusTxUUID {
                peripheral.setNotifyValue(true, for: char)
            } else if char.uuid == nusRxUUID {
                ble.rxCharacteristic = char
            }
        }
        if ble.rxCharacteristic != nil {
            ble.nusReady = true
            log.info("NUS ready")
            ble.nusOpened()
        }
    }

    // iOS says when its outgoing queue has drained. A picture is streamed
    // rather than pulled, so this is what paces it: fill the link, stop when it
    // says stop, and carry on from here.
    func peripheralIsReady(toSendWriteWithoutResponse peripheral: CBPeripheral) {
        ble.pumpImageFrames()
    }

    // MARK: - CBPeripheralDelegate (NUS notifications)

    // ONE NOTIFICATION IS ONE FRAME, AND A BAD ONE COSTS ONLY ITSELF. The board
    // builds [type][len][payload] and sends it in a single notification, so
    // there is nothing to reassemble — and treating the notifications as a
    // stream meant one short delivery desynchronised the parser for good. A
    // notification larger than the negotiated MTU is truncated rather than
    // split; the header then promises bytes that never arrive, the buffer waits
    // for them, and everything the machine says afterwards is swallowed
    // building a frame that will never complete. That is a phone that can still
    // send and can no longer hear, which is exactly what an upload with no
    // "kept it" looks like from the outside.
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard error == nil, let value = characteristic.value, characteristic.uuid == nusTxUUID else { return }
        // A frame from a machine this phone has turned away from would land on
        // the record of the one it turned toward.
        guard peripheral === ble.connectedPeripheral else { return }
        let gen = ble.linkGeneration
        var frameBuffer = value

        // Parse all complete frames: [type(1B)][len(2B LE)][payload...]
        // A frame that lets the link go — a board naming another machine —
        // leaves the rest of this notification to the link that is gone.
        while frameBuffer.count >= 3, gen == ble.linkGeneration {
            let type = frameBuffer[frameBuffer.startIndex]
            let lenLo = frameBuffer[frameBuffer.startIndex + 1]
            let lenHi = frameBuffer[frameBuffer.startIndex + 2]
            let payloadLen = Int(lenLo) | (Int(lenHi) << 8)
            let frameLen = 3 + payloadLen

            // Short of what its own header claims: cut off in the radio, and
            // nothing later can complete it. Dropped here, where it costs one
            // frame instead of every frame after it.
            guard frameBuffer.count >= frameLen else {
                log.error("dropped a frame claiming \(payloadLen) bytes with \(frameBuffer.count - 3) delivered")
                break
            }

            let payload = frameBuffer.subdata(in: (frameBuffer.startIndex + 3)..<(frameBuffer.startIndex + frameLen))
            frameBuffer = frameBuffer.subdata(in: (frameBuffer.startIndex + frameLen)..<frameBuffer.endIndex)

            switch type {
            case 0x01: // TEXT — why a name did not reach the main board
                if let text = String(data: payload, encoding: .utf8), text.hasPrefix("ERR:") {
                    log.error("Error response: \(text)")
                    // Not taken, so the name stands until the machine trusts this device.
                    if text == "ERR:IDENTITY:UNTRUSTED" { ble.namePushed = false }
                }
            case 0x11: // OTA_NEED — the board asking for its next piece
                ble.handleOtaNeed(payload)
            case 0x13: // OTA_END
                ble.handleOtaEnd(payload)
            case 0x14: // IDENTITY
                ble.handleIdentity(payload)
            case 0x15: // VERSIONS
                ble.handleVersions(payload)
            case 0x17: // IMG_STATE — which custom slots hold a picture
                ble.handleImageState(payload)
            case 0x1A: // IMG_ACK — where the board has got to, and how it ended
                ble.handleImageAck(payload)
            case 0x22: // IMG_PIX — a picture coming back off the machine
                ble.handleImagePix(payload)
            case 0x1E: // ART_STATE — which face each channel wears
                ble.handleFlavorArt(payload)
            case BridgeFrame.answer: // what the main board said, asked or not
                ble.handleBridgeAnswer(payload)
            case BridgeFrame.version: // the faucet carries the bridge
                ble.handleBridgeVersion(payload)
            case TrustFrame.state: // where this device stands with the machine
                ble.handleTrust(payload)
            default:
                break
            }
        }
    }
}
