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

    // Config state (synced from ESP32 via S3 bridge). Read once per session;
    // the values themselves are the record's.
    var configSynced = false
    var flavor1Image: Int {
        get { current?.config.flavor1Image ?? 0 }
        set { current?.config.flavor1Image = newValue; directory.touch() }
    }
    var flavor2Image: Int {
        get { current?.config.flavor2Image ?? 1 }
        set { current?.config.flavor2Image = newValue; directory.touch() }
    }
    var flavor1Ratio: Int {
        get { current?.config.flavor1Ratio ?? 20 }
        set { current?.config.flavor1Ratio = newValue; directory.touch() }
    }
    var flavor2Ratio: Int {
        get { current?.config.flavor2Ratio ?? 20 }
        set { current?.config.flavor2Ratio = newValue; directory.touch() }
    }
    var numImages: Int {
        get { current?.config.numImages ?? 0 }
        set { current?.config.numImages = newValue; directory.touch() }
    }

    // Image list and cached images
    var imageNames: [String] {
        get { current?.config.imageNames ?? [] }
        set { current?.config.imageNames = newValue; directory.touch() }
    }
    var cachedImages: [Int: UIImage] {
        get { current?.cachedImages ?? [:] }
        set { current?.cachedImages = newValue }
    }
    var imageDownloadProgress: Double? = nil  // nil = not downloading

    // Upload state
    var uploadProgress: Double? = nil  // nil = not uploading
    var uploadStatus: String = ""
    var uploadQueue: [UploadQueueItem] = []
    var activeUploadImage: UIImage? = nil
    var activeUploadSlot: Int = -1

    struct UploadQueueItem: Identifiable {
        let id = UUID()
        let image: UIImage
    }

    // Firmware versions (populated by GET_VERSION response)
    var s3Version: String {
        get { current?.prototypeVersions.s3 ?? "" }
        set { current?.prototypeVersions.s3 = newValue; directory.touch() }
    }
    var espVersion: String {
        get { current?.prototypeVersions.esp ?? "" }
        set { current?.prototypeVersions.esp = newValue; directory.touch() }
    }
    var rpVersion: String {
        get { current?.prototypeVersions.rp ?? "" }
        set { current?.prototypeVersions.rp = newValue; directory.touch() }
    }

    // Factory reset completion signal (toggled on OK:FACTORY_RESET)
    var factoryResetCompleted = false

    // Delete error (shown as alert in UI, nil = no error)
    var deleteError: String? = nil

    // Clean cycle state
    var cleanCycleActive = false
    var cleanCyclePhase: String? = nil   // "Filling... (1/3)", "Flushing... (2/3)", nil
    var cleanCycleCompleted = false

    // Prime state
    var primeActive = false
    var primeFlavor: Int = 0  // 1 or 2

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
    // The one this phone is pointed at is connected to as soon as it is heard;
    // a known machine among the rest has its sighting noted; and the rest are
    // what Add a machine lists.
    var discovered: [DiscoveredMachine] = []

    /// Scanning while connected, for a list that wants to say what is in range
    /// right now. Off, the radio scans only while it has nothing to talk to.
    var browsing = false

    /// The phone's radio is off, or this app may not use it. Said once the
    /// system has said so, which is after the first ask for permission.
    var radioOff = false

    /// What faces are filed under: the record's key.
    var machineKey: String { current?.key ?? "" }

    @ObservationIgnored fileprivate var lastRssiPush: [String: Date] = [:]

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
    @ObservationIgnored fileprivate var otaModel: MachineModel = .unknown
    @ObservationIgnored fileprivate var otaFetch: ((FirmwareImage) async throws -> Data)? = nil

    /// Which screens this machine gets. A machine whose advertisement carried
    /// no model byte is running firmware older than that, and every one of
    /// those is a prototype.
    var isAppliance: Bool { current?.model == .appliance }

    // Chart data: laid out on the record from its usage reading. Read once
    // per session; `chartDataSynced` says this session has.
    var chartData24H: [[Double]] {
        current?.chartData24H ?? [Array(repeating: 0, count: 24), Array(repeating: 0, count: 24)]
    }
    var chartData30D: [[Double]] {
        current?.chartData30D ?? [Array(repeating: 0, count: 30), Array(repeating: 0, count: 30)]
    }
    var chartDataHOD: [[Double]] {
        current?.chartDataHOD ?? [Array(repeating: 0, count: 24), Array(repeating: 0, count: 24)]
    }
    var chartDataHODDays: Int { current?.chartDataHODDays ?? 1 }
    var chartDataSynced: Bool = false

    /// A reading being assembled, hour by hour, until CHART_CUR closes it.
    @ObservationIgnored fileprivate var rawHourlyData: [[HourBucket]] = [[], []]
    @ObservationIgnored fileprivate var currentSeqHour: UInt32 = 0
    @ObservationIgnored fileprivate var chartCurReceived: Int = 0

    // Usage statistics (used by pie chart)
    struct FlavorStats {
        var monthFlowSum: UInt32 = 0
    }
    var flavor1Stats: FlavorStats { FlavorStats(monthFlowSum: current?.monthFlowSum[0] ?? 0) }
    var flavor2Stats: FlavorStats { FlavorStats(monthFlowSum: current?.monthFlowSum[1] ?? 0) }
    var statsSynced = false

    // ── Internal state (not observed by SwiftUI) ──

    @ObservationIgnored fileprivate var pendingImageList: [String] = []
    @ObservationIgnored fileprivate var pendingCRCs: [Int: UInt32] = [:]  // from LIST response

    // Pending delete state (for optimistic UI rollback)
    @ObservationIgnored fileprivate var pendingDeleteSlot: Int = -1
    @ObservationIgnored fileprivate var preDeleteNumImages: Int = 0
    @ObservationIgnored fileprivate var preDeleteCachedImages: [Int: UIImage] = [:]
    @ObservationIgnored fileprivate var preDeleteImageNames: [String] = []

    // Image upload state
    @ObservationIgnored fileprivate var isUploading = false
    @ObservationIgnored fileprivate var uploadSlot: Int = -1
    @ObservationIgnored fileprivate var uploadLabel: String = ""
    @ObservationIgnored fileprivate var uploadSteps: [(type: String, data: Data)] = []
    @ObservationIgnored fileprivate var currentUploadStep = 0
    @ObservationIgnored fileprivate var uploadBytesSent = 0
    @ObservationIgnored fileprivate var uploadQueueTotal = 0
    @ObservationIgnored fileprivate var uploadImageRef: UIImage?

    // Image download state — accessed from bleQueue during downloads
    @ObservationIgnored fileprivate var imgDownloadSlot: Int = -1
    @ObservationIgnored fileprivate var imgDownloadData = Data()
    @ObservationIgnored fileprivate var imgDownloadExpected: Int = 0
    @ObservationIgnored fileprivate var imgDownloadCRC: UInt32 = 0
    @ObservationIgnored fileprivate var imgDownloadRetries: Int = 0
    @ObservationIgnored fileprivate var imgDownloadQueue: [Int] = []
    @ObservationIgnored fileprivate var isDownloading = false
    @ObservationIgnored fileprivate var binStartReceived = false
    @ObservationIgnored fileprivate var pendingStatsRequest = false
    @ObservationIgnored fileprivate var chartRetryTimer: DispatchWorkItem?

    // GATT/NUS state
    @ObservationIgnored fileprivate var nusReady = false
    @ObservationIgnored var rxCharacteristic: CBCharacteristic?

    // BLE runs on a dedicated background queue so binary data accumulation
    // and BLE writes don't block the main thread during image downloads.
    @ObservationIgnored let bleQueue = DispatchQueue(label: "com.derekbreden.SodaMachine.BLE", qos: .userInitiated)
    @ObservationIgnored fileprivate var cbAdapter: CBDelegateAdapter!
    @ObservationIgnored fileprivate var centralManager: CBCentralManager!
    @ObservationIgnored var connectedPeripheral: CBPeripheral?
    @ObservationIgnored fileprivate var scanTimer: Timer?
    @ObservationIgnored fileprivate var reconnectTimer: Timer?
    @ObservationIgnored fileprivate var userInitiatedDisconnect = false

    init(directory: MachineDirectory) {
        self.directory = directory
        cbAdapter = CBDelegateAdapter(self)
    }

    /// Bring the radio up, or turn a radio that is already up toward the
    /// machine this phone is pointed at.
    ///
    /// The central manager outlives a disconnect — it is the app's, not the
    /// connection's — and creating it is what first turns the radio, by way of
    /// `centralManagerDidUpdateState`. Creating it is also what asks for
    /// Bluetooth permission, so it waits for a screen that has said why.
    func activateBluetooth() {
        // The demo needs no radio, and stands up before the radio has said
        // anything about itself.
        if demoMode { point() }
        guard centralManager == nil else {
            point()
            return
        }
        centralManager = CBCentralManager(delegate: cbAdapter, queue: bleQueue)
    }

    /// Called when the app returns to foreground after being backgrounded.
    /// Restarts scanning if not connected (iOS silently stops scans while
    /// backgrounded), and resets stale transfer state if connected (downloads
    /// interrupted by backgrounding leave isDownloading stuck true, blocking
    /// subsequent stats requests).
    func handleReturnToForeground() {
        guard !demoMode, centralManager != nil else { return }

        if connectionState == .connected {
            bleQueue.async { [weak self] in
                guard let self, self.isDownloading else { return }
                // Download was interrupted by backgrounding — the S3 stopped
                // sending while we were suspended. Clear the dead transfer so
                // requestStatsAndCharts() isn't blocked by isDownloading.
                self.imgDownloadQueue = []
                self.imgDownloadData = Data()
                self.imgDownloadSlot = -1
                self.binStartReceived = false
                DispatchQueue.main.async {
                    self.isDownloading = false
                    self.imageDownloadProgress = nil
                    self.pendingStatsRequest = false
                }
            }
        } else if connectionState != .bluetoothOff, current != nil {
            // iOS may have stopped our scan or stalled a connection attempt
            // while backgrounded. Cancel any pending connection and look again.
            if let peripheral = connectedPeripheral {
                userInitiatedDisconnect = true
                centralManager.cancelPeripheralConnection(peripheral)
                connectedPeripheral = nil
                rxCharacteristic = nil
                nusReady = false
            }
            point()
        }
    }

    // MARK: - Public API

    /// Send a text command to the S3 via BLE GATT/NUS.
    /// Wire format: [type(1B)][len(2B LE)][payload...]
    func send(_ text: String) {
        bleQueue.async { [weak self] in
            guard let self, let payload = text.data(using: .utf8) else { return }
            self.sendBLEFrame(type: 0x01, payload: payload)
            log.debug("TX: \(text)")
        }
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

    func requestConfig() {
        if demoMode { return }
        send("GET_CONFIG")
    }

    func requestImageList() {
        if demoMode { return }
        pendingImageList = []
        send("LIST")
    }

    func requestVersions() {
        if demoMode { return }
        send("GET_VERSION")
    }

    func requestStatsAndCharts() {
        if demoMode {
            populateDemoStats()
            populateDemoChartData()
            return
        }
        chartRetryTimer?.cancel()
        chartRetryTimer = nil
        statsSynced = false
        chartDataSynced = false
        rawHourlyData = [[], []]
        chartCurReceived = 0
        if isDownloading {
            pendingStatsRequest = true
            return
        }
        pendingStatsRequest = false
        send("GET_CHART_DATA")
        scheduleChartRetry()
    }

    private func scheduleChartRetry(attempt: Int = 1) {
        chartRetryTimer?.cancel()
        guard attempt <= 3 else { return }
        let work = DispatchWorkItem { [weak self] in
            guard let self, !self.chartDataSynced else { return }
            self.rawHourlyData = [[], []]
            self.chartCurReceived = 0
            self.send("GET_CHART_DATA")
            self.scheduleChartRetry(attempt: attempt + 1)
        }
        chartRetryTimer = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 3, execute: work)
    }

    func subscribeStats() {
        if demoMode { return }
        send("STATS_SUBSCRIBE")
    }

    func unsubscribeStats() {
        if demoMode { return }
        chartRetryTimer?.cancel()
        chartRetryTimer = nil
        send("STATS_UNSUBSCRIBE")
    }

    func factoryReset() {
        if demoMode {
            flavor1Image = 0
            flavor2Image = 1
            flavor1Ratio = 20
            flavor2Ratio = 20
            numImages = 3
            imageNames = ["flavor_1", "flavor_2", "flavor_3"]
            cachedImages = [
                0: flavorImage("flavor_1"),
                1: flavorImage("flavor_2"),
                2: flavorImage("flavor_3")
            ]
            factoryResetCompleted = true
            return
        }
        send("FACTORY_RESET")
    }

    func startCleanCycle(flavor: Int) {
        if demoMode {
            cleanCycleActive = true
            cleanCyclePhase = "Filling... (1/3)"
            let phases = [
                (0.5, "Flushing... (1/3)"),
                (1.0, "Filling... (2/3)"),
                (1.5, "Flushing... (2/3)"),
                (2.0, "Filling... (3/3)"),
                (2.5, "Flushing... (3/3)")
            ]
            for (delay, phase) in phases {
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
                    guard let self, self.cleanCycleActive else { return }
                    self.cleanCyclePhase = phase
                }
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) { [weak self] in
                guard let self, self.cleanCycleActive else { return }
                self.cleanCycleActive = false
                self.cleanCyclePhase = nil
                self.cleanCycleCompleted = true
            }
            return
        }
        cleanCycleActive = true
        cleanCyclePhase = "Starting..."
        send("CLEAN:\(flavor)")
    }

    func abortCleanCycle() {
        if demoMode {
            cleanCycleActive = false
            cleanCyclePhase = nil
            return
        }
        send("CLEAN_ABORT")
    }

    func startPrime(flavor: Int) {
        if demoMode {
            primeActive = true
            primeFlavor = flavor
            return
        }
        primeActive = true
        primeFlavor = flavor
        send("PRIME_START:\(flavor)")
    }

    func sendPrimeTick() {
        if demoMode { return }
        send("PRIME_TICK")
    }

    func stopPrime() {
        if demoMode {
            primeActive = false
            return
        }
        primeActive = false
        send("PRIME_STOP")
    }

    func sendSet(_ key: String, value: Int) {
        send("SET:\(key)=\(value)")
        bleQueue.asyncAfter(deadline: .now() + 0.05) { [weak self] in
            self?.send("SAVE")
        }
    }

    func displayName(for index: Int) -> String {
        guard index >= 0, index < imageNames.count else {
            return "Image \(index)"
        }
        let name = imageNames[index]
        if name.isEmpty { return "Image \(index)" }
        return name.replacingOccurrences(of: "_", with: " ").capitalized
    }

    func imageFor(slot: Int) -> UIImage? {
        return cachedImages[slot]
    }

    func queueUploads(_ items: [UploadQueueItem]) {
        uploadQueue.append(contentsOf: items)
        uploadQueueTotal = uploadQueue.count + (isUploading ? 1 : 0)
        if !isUploading {
            startNextUpload()
        }
    }

    private func startNextUpload() {
        guard !uploadQueue.isEmpty else {
            uploadQueueTotal = 0
            activeUploadImage = nil
            activeUploadSlot = -1
            requestImageList()
            return
        }
        let item = uploadQueue.removeFirst()
        let slot = numImages
        uploadImageRef = item.image
        activeUploadImage = item.image
        activeUploadSlot = slot
        let position = uploadQueueTotal - uploadQueue.count
        uploadStatus = "Uploading \(position) of \(uploadQueueTotal)..."
        uploadImage(item.image, toSlot: slot)
    }

    private func uploadImage(_ image: UIImage, toSlot slot: Int) {
        if demoMode {
            uploadDemoImage(image, toSlot: slot)
            return
        }
        guard let pngData = ImageProcessor.generatePNG(from: image),
              let s3Data = ImageProcessor.generateRGB565(from: image, width: 240, height: 240),
              let rpData = ImageProcessor.generateRGB565(from: image, width: 128, height: 115) else {
            uploadStatus = "Image processing failed"
            return
        }

        let label = "image_\(slot)"
        log.info("Upload: slot \(slot), png=\(pngData.count)B, s3=\(s3Data.count)B, rp=\(rpData.count)B")

        isUploading = true
        uploadSlot = slot
        uploadLabel = label
        uploadSteps = [
            (type: "png", data: pngData),
            (type: "s3",  data: s3Data),
            (type: "rp",  data: rpData)
        ]
        currentUploadStep = 0
        uploadBytesSent = 0
        uploadProgress = 0
        uploadStatus = "Uploading image..."

        sendNextUploadStep()
    }

    func deleteImage(slot: Int) {
        if demoMode {
            deleteDemoImage(slot: slot)
            return
        }

        pendingDeleteSlot = slot
        preDeleteNumImages = numImages
        preDeleteCachedImages = cachedImages
        preDeleteImageNames = imageNames

        numImages -= 1
        var newCache: [Int: UIImage] = [:]
        for (key, img) in cachedImages {
            if key < slot {
                newCache[key] = img
            } else if key > slot {
                newCache[key - 1] = img
            }
        }
        cachedImages = newCache
        if slot < imageNames.count {
            imageNames.remove(at: slot)
        }

        send("DELETE_STORE_IMG:\(slot)")
    }

    func downloadAllImages(advertisedCRCs: [Int: UInt32] = [:]) {
        guard let m = current, !isDownloading else { return }
        var queue: [Int] = []
        for slot in 0..<numImages {
            // A picture on the phone that the machine still lists under the
            // same crc is the picture. One listed under another has changed
            // under it and comes down again; firmware that lists no crc is
            // taken at its word.
            if let held = m.cachedImages[slot], held.size != .zero {
                if let advertised = advertisedCRCs[slot] {
                    if m.config.imageCRCs[slot] == advertised { continue }
                } else {
                    continue
                }
            }
            queue.append(slot)
        }
        if queue.isEmpty { return }
        isDownloading = true
        imageDownloadProgress = 0
        bleQueue.async {
            self.imgDownloadQueue = queue
            self.startNextDownload()
        }
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

    /// A machine picked out of a scan: added, pointed at, and connected to
    /// while its peripheral is still in hand.
    func add(_ seen: DiscoveredMachine) {
        dropLink()
        let m = directory.add(seen)
        directory.select(m)
        point()
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
        if linked, current?.id == machine.id { send("IDENTITY \(name)") }
        directory.save()
    }

    /// Turn the radio toward the machine this phone is pointed at: the demo is
    /// simply up, anything else is listened for, and nothing means the radio
    /// rests until a machine is added.
    fileprivate func point() {
        let radioOn = centralManager?.state == .poweredOn
        guard let m = current else {
            centralManager?.stopScan()
            scanTimer?.invalidate()
            connectionState = radioOn ? .searching : .bluetoothOff
            return
        }
        if m.isDemo {
            centralManager?.stopScan()
            scanTimer?.invalidate()
            reconnectTimer?.invalidate()
            seedDemo(m)
            connectionState = .connected
            configSynced = true
            return
        }
        connectionState = radioOn ? .searching : .bluetoothOff
        startScan()
    }

    /// The link, and everything in flight on it, let go. What the machine said
    /// stays on its record.
    fileprivate func dropLink() {
        centralManager?.stopScan()
        scanTimer?.invalidate()
        reconnectTimer?.invalidate()
        chartRetryTimer?.cancel()
        chartRetryTimer = nil
        stopFacePump()
        if let peripheral = connectedPeripheral {
            userInitiatedDisconnect = true
            centralManager?.cancelPeripheralConnection(peripheral)
        }
        connectedPeripheral = nil
        rxCharacteristic = nil
        nusReady = false
        if connectionState != .bluetoothOff { connectionState = .searching }
        configSynced = false
        statsSynced = false
        chartDataSynced = false
        rawHourlyData = [[], []]
        chartCurReceived = 0
        imgDownloadQueue = []
        isDownloading = false
        imageDownloadProgress = nil
        isUploading = false
        uploadProgress = nil
        uploadSteps = []
        uploadQueue = []
        uploadQueueTotal = 0
        uploadImageRef = nil
        activeUploadImage = nil
        activeUploadSlot = -1
        primeActive = false
        cleanCycleActive = false
        cleanCyclePhase = nil
        imgDownloadSlot = -1
        binStartReceived = false
        imageQueue = []
        activeUpload = nil
        imageUploadState = .idle
        otaQueue = []
        otaProgress = nil
        otaImage = nil
        otaData = Data()
        otaFetch = nil
        faceSlot = -1
        facePixels = Data()
        faceHave.removeAll()
        faceReceived = 0
    }

    // MARK: - Demo mode

    /// The demo's machine: settings filled in the first time it is pointed
    /// at, pictures whenever they are not in hand. They are the placeholders
    /// every prototype ships with, drawn from this app's bundle rather than
    /// kept in the record's folder.
    private func seedDemo(_ m: KnownMachine) {
        if m.cachedImages.isEmpty {
            m.cachedImages = [
                0: flavorImage("flavor_1"),
                1: flavorImage("flavor_2"),
                2: flavorImage("flavor_3")
            ]
        }
        guard m.configReadAt == nil else { return }
        m.config.flavor1Image = 0
        m.config.flavor2Image = 1
        m.config.flavor1Ratio = 20
        m.config.flavor2Ratio = 20
        m.config.numImages = 3
        m.config.imageNames = ["flavor_1", "flavor_2", "flavor_3"]
        m.prototypeVersions = PrototypeVersions(s3: "Demo", esp: "Demo", rp: "Demo")
        m.configReadAt = Date()
        directory.save()
    }

    // Demo-mode flavor art: the bundled placeholder PNG (images/flavor_N.png,
    // copied in by tools/build_flavor_assets.sh), falling back to a flat swatch.
    private func flavorImage(_ name: String) -> UIImage {
        if let url = Bundle.main.url(forResource: name, withExtension: "png"),
           let img = UIImage(contentsOfFile: url.path) {
            return img
        }
        let pretty = name.replacingOccurrences(of: "_", with: " ").capitalized
        return generateDemoImage(label: pretty, color: UIColor(white: 0.25, alpha: 1))
    }

    private func generateDemoImage(label: String, color: UIColor) -> UIImage {
        let size = CGSize(width: 240, height: 240)
        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { ctx in
            color.setFill()
            ctx.cgContext.fillEllipse(in: CGRect(origin: .zero, size: size))
            let attrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.systemFont(ofSize: 24, weight: .bold),
                .foregroundColor: UIColor.white
            ]
            let text = label as NSString
            let textSize = text.size(withAttributes: attrs)
            let textRect = CGRect(
                x: (size.width - textSize.width) / 2,
                y: (size.height - textSize.height) / 2,
                width: textSize.width,
                height: textSize.height
            )
            text.draw(in: textRect, withAttributes: attrs)
        }
    }

    private func uploadDemoImage(_ image: UIImage, toSlot slot: Int) {
        isUploading = true
        uploadSlot = slot
        uploadImageRef = image
        uploadProgress = 0
        var step = 0
        let totalSteps = 20
        Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] timer in
            guard let self, self.demoMode, self.isUploading else { timer.invalidate(); return }
            step += 1
            self.uploadProgress = Double(step) / Double(totalSteps)
            if step >= totalSteps {
                timer.invalidate()
                self.imageNames.append("image_\(slot)")
                self.completeUpload()
            }
        }
    }

    /// The demo's fortnight, as a usage reading: pours shaped like a day, so
    /// every chart is laid out the way a machine's is.
    private func populateDemoStats() {
        guard let m = current else { return }
        if m.usage.readAt == nil {
            let seqHour: UInt32 = 24 * 60
            let nowHour = Calendar.current.component(.hour, from: Date())
            var hourly: [[HourBucket]] = [[], []]
            for hoursAgo in 0..<(24 * 14) {
                let hour = (nowHour - hoursAgo % 24 + 24) % 24
                let angle = Double(hour - 12) / 12.0 * .pi
                let base = max(0, cos(angle)) * 8.0 * 20
                let seq = seqHour - UInt32(hoursAgo)
                hourly[0].append(HourBucket(seq: seq, flow: UInt32(base * 1.2 * (0.7 + Double.random(in: 0...0.6)))))
                hourly[1].append(HourBucket(seq: seq, flow: UInt32(base * 0.8 * (0.7 + Double.random(in: 0...0.6)))))
            }
            m.usage = UsageReading(hourly: hourly, seqHour: seqHour, readAt: Date())
            m.recomputeCharts()
            directory.save()
        }
        statsSynced = true
    }

    private func populateDemoChartData() {
        chartDataSynced = true
    }

    private func deleteDemoImage(slot: Int) {
        guard numImages > 1 else { return }

        var newNames: [String] = []
        var newCache: [Int: UIImage] = [:]
        var j = 0
        for i in 0..<numImages where i != slot {
            if i < imageNames.count { newNames.append(imageNames[i]) }
            if let img = cachedImages[i] { newCache[j] = img }
            j += 1
        }

        numImages -= 1
        imageNames = newNames
        cachedImages = newCache

        if flavor1Image > slot { flavor1Image -= 1 }
        else if flavor1Image == slot { flavor1Image = max(0, slot - 1) }
        if flavor2Image > slot { flavor2Image -= 1 }
        else if flavor2Image == slot { flavor2Image = max(0, slot - 1) }
    }

    // MARK: - Image upload

    private func sendNextUploadStep() {
        guard currentUploadStep < uploadSteps.count else {
            uploadStatus = "Finalizing..."
            send("FINALIZE_UPLOAD:\(uploadSlot):\(uploadLabel)")
            return
        }

        let step = uploadSteps[currentUploadStep]
        let crc = ImageProcessor.crc32(step.data)

        log.info("Upload step \(self.currentUploadStep)/\(self.uploadSteps.count): type=\(step.type) size=\(step.data.count) crc=0x\(String(crc, radix: 16, uppercase: true))")

        let fileType: UInt8 = step.type == "png" ? 0 : (step.type == "s3" ? 1 : 2)

        // Build BIN_START payload: [slot(1B), fileType(1B), size(4B LE), crc32(4B LE), label...]
        var startPayload = Data(capacity: 10 + 32)
        startPayload.append(UInt8(uploadSlot))
        startPayload.append(fileType)
        var sizeLE = UInt32(step.data.count).littleEndian
        withUnsafeBytes(of: &sizeLE) { startPayload.append(contentsOf: $0) }
        var crcLE = crc.littleEndian
        withUnsafeBytes(of: &crcLE) { startPayload.append(contentsOf: $0) }
        if currentUploadStep == 0, let labelData = uploadLabel.data(using: .utf8) {
            startPayload.append(labelData)
        }

        uploadBytesSent = 0

        bleQueue.async { [weak self] in
            guard let self else { return }
            self.sendBLEFrame(type: 0x02, payload: startPayload)
            self.bleQueue.asyncAfter(deadline: .now() + 0.05) {
                self.sendUploadChunks()
            }
        }
    }

    private func sendUploadChunks() {
        guard currentUploadStep < uploadSteps.count else { return }
        let data = uploadSteps[currentUploadStep].data
        let mtu = connectedPeripheral?.maximumWriteValueLength(for: .withResponse) ?? 182
        let chunkSize = min(mtu - 3, 240)

        func sendChunk() {
            self.bleQueue.asyncAfter(deadline: .now() + 0.02) {
                guard self.uploadBytesSent < data.count, self.isUploading else { return }
                let end = min(self.uploadBytesSent + chunkSize, data.count)
                let chunk = data[self.uploadBytesSent..<end]

                self.sendBLEFrame(type: 0x03, payload: Data(chunk))
                self.uploadBytesSent = end

                DispatchQueue.main.async {
                    let stepBase = Double(self.currentUploadStep) / 3.0
                    let stepProgress = Double(self.uploadBytesSent) / Double(data.count) / 3.0
                    self.uploadProgress = stepBase + stepProgress
                }

                if self.uploadBytesSent < data.count {
                    sendChunk()
                } else {
                    log.info("Upload step \(self.currentUploadStep): all \(self.uploadBytesSent) bytes sent, sending BIN_END")
                    self.sendBLEFrame(type: 0x04, payload: Data())
                }
            }
        }
        sendChunk()
    }

    private func completeUpload() {
        isUploading = false
        uploadSteps = []
        numImages = max(numImages, uploadSlot + 1)
        if let img = uploadImageRef { cachedImages[uploadSlot] = img }
        uploadImageRef = nil

        if !uploadQueue.isEmpty {
            let position = uploadQueueTotal - uploadQueue.count + 1
            uploadStatus = "Uploading \(position) of \(uploadQueueTotal)..."
            uploadProgress = 0
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [weak self] in
                self?.startNextUpload()
            }
        } else {
            uploadProgress = 1.0
            uploadStatus = "Upload complete!"
            uploadQueueTotal = 0
            activeUploadImage = nil
            activeUploadSlot = -1
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                self?.uploadProgress = nil
                self?.requestImageList()
            }
        }
    }

    private func failUpload(_ reason: String) {
        log.error("Upload failed (slot \(self.uploadSlot)): \(reason)")
        isUploading = false
        uploadSteps = []
        uploadImageRef = nil

        if !uploadQueue.isEmpty {
            uploadStatus = "Slot \(self.uploadSlot) failed, continuing..."
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                self?.startNextUpload()
            }
        } else {
            uploadStatus = "Upload failed: \(reason)"
            uploadProgress = nil
            uploadQueueTotal = 0
            activeUploadImage = nil
            activeUploadSlot = -1
        }
    }

    func cancelActiveUpload() {
        guard isUploading else { return }
        isUploading = false
        uploadSteps = []
        uploadImageRef = nil
        if !demoMode { send("ABORT_UPLOAD") }

        if !uploadQueue.isEmpty {
            uploadStatus = "Cancelled, continuing..."
            uploadProgress = 0
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                self?.startNextUpload()
            }
        } else {
            uploadProgress = nil
            uploadStatus = ""
            uploadQueueTotal = 0
            activeUploadImage = nil
            activeUploadSlot = -1
        }
    }

    func cancelQueuedUpload(id: UUID) {
        uploadQueue.removeAll { $0.id == id }
        uploadQueueTotal = uploadQueue.count + (isUploading ? 1 : 0)
    }

    // MARK: - Image download (runs entirely on bleQueue)

    fileprivate func startNextDownload() {
        guard !imgDownloadQueue.isEmpty else {
            DispatchQueue.main.async {
                self.imageDownloadProgress = nil
                self.isDownloading = false
                if self.pendingStatsRequest {
                    self.pendingStatsRequest = false
                    self.send("GET_CHART_DATA")
                }
            }
            return
        }
        let slot = imgDownloadQueue.removeFirst()
        imgDownloadData = Data()
        imgDownloadExpected = 0
        imgDownloadRetries = 0
        send("GETPNG:\(slot)")
    }

    // MARK: - Response parsing (main thread only)

    fileprivate func handleTextResponse(_ text: String) {
        if text.hasPrefix("CONFIG:") {
            parseConfig(text)
        } else if text.hasPrefix("IMG:") {
            parseImageLine(text)
        } else if text == "END" {
            imageNames = pendingImageList
            pendingImageList = []
            downloadAllImages(advertisedCRCs: pendingCRCs)
            pendingCRCs = [:]
        } else if text.hasPrefix("IMG_OK:") {
            guard isUploading else {
                log.debug("Ignoring IMG_OK (not uploading): \(text)")
                return
            }
            currentUploadStep += 1
            let stepNames = ["PNG", "S3 RGB565", "RP2040 RGB565"]
            if currentUploadStep < uploadSteps.count {
                uploadStatus = "Uploading \(stepNames[currentUploadStep])..."
            }
            sendNextUploadStep()
        } else if text.hasPrefix("IMG_ERR:") {
            guard isUploading else {
                log.debug("Ignoring IMG_ERR (not uploading): \(text)")
                return
            }
            failUpload(text)
        } else if text == "OK:UPLOAD_ABORTED" {
            log.info("Upload abort acknowledged by S3")
        } else if text.hasPrefix("OK:UPLOAD_DONE:") {
            guard isUploading else {
                log.debug("Ignoring OK:UPLOAD_DONE (not uploading): \(text)")
                return
            }
            completeUpload()
        } else if text.hasPrefix("OK:STORE_DELETED=") {
            pendingDeleteSlot = -1
            let body = String(text.dropFirst(3))
            for pair in body.split(separator: ",") {
                let parts = pair.split(separator: "=", maxSplits: 1)
                if parts.count == 2, let val = Int(parts[1]), String(parts[0]) == "NUM_IMAGES" {
                    numImages = max(val, 1)
                }
            }
            clearDiskCache()
            cachedImages = [:]
            requestImageList()
            log.info("Image deleted, refreshing list")
        } else if text.hasPrefix("VERSION:S3=") {
            s3Version = String(text.dropFirst(11))
        } else if text.hasPrefix("VERSION:ESP32=") {
            espVersion = String(text.dropFirst(14))
        } else if text.hasPrefix("VERSION:RP2040=") {
            rpVersion = String(text.dropFirst(15))
        } else if text.hasPrefix("CHART_") {
            parseChartLine(text)
        } else if text.hasPrefix("CLEAN:FILLING:") {
            let parts = text.dropFirst(14)
            if let slashIdx = parts.firstIndex(of: "/"),
               let colonIdx = parts.firstIndex(of: ":") {
                let c = parts[parts.index(after: colonIdx)..<slashIdx]
                let t = parts[parts.index(after: slashIdx)...]
                cleanCyclePhase = "Filling... (\(c)/\(t))"
            } else {
                cleanCyclePhase = "Filling..."
            }
        } else if text.hasPrefix("CLEAN:FLUSHING:") {
            let parts = text.dropFirst(15)
            if let slashIdx = parts.firstIndex(of: "/"),
               let colonIdx = parts.firstIndex(of: ":") {
                let c = parts[parts.index(after: colonIdx)..<slashIdx]
                let t = parts[parts.index(after: slashIdx)...]
                cleanCyclePhase = "Flushing... (\(c)/\(t))"
            } else {
                cleanCyclePhase = "Flushing..."
            }
        } else if text.hasPrefix("OK:CLEAN:") {
            cleanCycleActive = false
            cleanCyclePhase = nil
            cleanCycleCompleted = true
        } else if text == "OK:CLEAN_ABORT" {
            cleanCycleActive = false
            cleanCyclePhase = nil
        } else if text.hasPrefix("ERR:CLEAN") {
            cleanCycleActive = false
            cleanCyclePhase = nil
        } else if text.hasPrefix("PRIME:ACTIVE:") {
            primeActive = true
        } else if text == "OK:PRIME_STOP" || text == "OK:PRIME_TIMEOUT" {
            primeActive = false
        } else if text.hasPrefix("ERR:PRIME") {
            primeActive = false
        } else if text == "OK:FACTORY_RESET" {
            log.info("Factory reset confirmed, re-syncing")
            clearDiskCache()
            cachedImages = [:]
            imageNames = []
            statsSynced = false
            chartDataSynced = false
            factoryResetCompleted = true
            requestConfig()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self] in
                self?.requestImageList()
            }
        } else if text.hasPrefix("ERR:") {
            log.error("Error response: \(text)")
            if isUploading {
                failUpload(text)
            } else if isDownloading {
                log.error("Skipping failed image download, continuing queue")
                bleQueue.async { self.startNextDownload() }
            } else if pendingDeleteSlot >= 0 {
                numImages = preDeleteNumImages
                cachedImages = preDeleteCachedImages
                imageNames = preDeleteImageNames
                pendingDeleteSlot = -1
                deleteError = String(text.dropFirst(4))
            }
        }
    }

    private func parseConfig(_ text: String) {
        let body = String(text.dropFirst(7))
        var values: [String: Int] = [:]
        for pair in body.split(separator: ",") {
            let parts = pair.split(separator: "=", maxSplits: 1)
            if parts.count == 2, let val = Int(parts[1]) {
                values[String(parts[0])] = val
            }
        }

        if let v = values["F1_RATIO"] { flavor1Ratio = v }
        if let v = values["F2_RATIO"] { flavor2Ratio = v }
        if let v = values["F1_IMAGE"] { flavor1Image = v }
        if let v = values["F2_IMAGE"] { flavor2Image = v }
        if let v = values["numImages"] { numImages = max(v, 1) }
        current?.configReadAt = Date()
        directory.touch()
        configSynced = true
        log.info("Config synced: F1=\(self.flavor1Image)/\(self.flavor1Ratio) F2=\(self.flavor2Image)/\(self.flavor2Ratio) numImages=\(self.numImages)")
    }

    private func parseChartLine(_ text: String) {
        guard let firstColon = text.firstIndex(of: ":") else { return }
        let prefix = String(text[text.startIndex..<firstColon])
        let body = String(text[text.index(after: firstColon)...])
        let parts = body.split(separator: ",")
        guard parts.count >= 2 else { return }

        var flavor = 0
        var kvValues: [String: String] = [:]
        var dataStart = 0
        for (i, part) in parts.enumerated() {
            let kv = part.split(separator: "=", maxSplits: 1)
            if kv.count == 2 {
                kvValues[String(kv[0])] = String(kv[1])
                if kv[0] == "F" { flavor = Int(kv[1]) ?? 0 }
                dataStart = i + 1
            } else {
                break
            }
        }
        guard flavor >= 0, flavor <= 1 else { return }

        if prefix == "CHART_HOURLY" {
            if let seqStr = kvValues["SEQ"], let seq = UInt32(seqStr) {
                currentSeqHour = seq
            }
            for part in parts[dataStart...] {
                let pair = part.split(separator: ":", maxSplits: 1)
                if pair.count == 2, let seq = UInt32(pair[0]), let fs = UInt32(pair[1]) {
                    rawHourlyData[flavor].append(HourBucket(seq: seq, flow: fs))
                }
            }
            return
        }

        // The hour under way is not in the hourly list — the machine's live
        // count is authoritative for it — so CHART_CUR closes one flavor's
        // reading with it, and the reading lands on the record once both have.
        if prefix == "CHART_CUR" {
            if let fsStr = kvValues["FS"], let fs = UInt32(fsStr) {
                rawHourlyData[flavor].removeAll { $0.seq == currentSeqHour }
                rawHourlyData[flavor].append(HourBucket(seq: currentSeqHour, flow: fs))
            }
            chartCurReceived += 1
            if chartCurReceived >= 2 {
                chartRetryTimer?.cancel()
                if let m = current {
                    m.usage = UsageReading(hourly: rawHourlyData, seqHour: currentSeqHour, readAt: Date())
                    withAnimation { m.recomputeCharts() }
                    directory.touch()
                }
                rawHourlyData = [[], []]
                chartDataSynced = true
                statsSynced = true
                chartCurReceived = 0
            }
            return
        }

        // A pour as it happens: the hour under way, re-counted. A count lower
        // than the one held is the next hour having begun.
        if prefix == "CHART_LIVE" {
            guard let fsStr = kvValues["FS"], let fs = UInt32(fsStr),
                  let m = current, m.usage.readAt != nil else { return }
            var u = m.usage
            if let i = u.hourly[flavor].firstIndex(where: { $0.seq == u.seqHour }) {
                if fs < u.hourly[flavor][i].flow {
                    u.seqHour += 1
                    u.hourly[flavor].append(HourBucket(seq: u.seqHour, flow: fs))
                } else {
                    u.hourly[flavor][i].flow = fs
                }
            } else {
                u.hourly[flavor].append(HourBucket(seq: u.seqHour, flow: fs))
            }
            u.readAt = Date()
            m.usage = u
            withAnimation { m.recomputeCharts() }
            directory.touch()
            return
        }
    }


    private func parseImageLine(_ text: String) {
        // Format: IMG:slot:label or IMG:slot:label:hexcrc
        let parts = text.split(separator: ":", maxSplits: 3)
        if parts.count >= 3 {
            let name = String(parts[2])
            let slot = Int(parts[1]) ?? pendingImageList.count
            while pendingImageList.count <= slot {
                pendingImageList.append("")
            }
            pendingImageList[slot] = name
            // Parse optional CRC field (Phase 3)
            if parts.count >= 4, let crc = UInt32(parts[3], radix: 16) {
                pendingCRCs[slot] = crc
            }
        }
    }

    // MARK: - Image disk cache
    // The prototype's store, kept on the record by slot with the crc the
    // machine listed beside each one.

    private func saveImageToDisk(slot: Int, data: Data) {
        current?.saveSlot(slot, data: data)
    }

    fileprivate func clearDiskCache() {
        current?.clearSlots()
        directory.touch()
    }

    private func savePersistedCRC(slot: Int, crc: UInt32) {
        current?.config.imageCRCs[slot] = crc
        directory.touch()
    }

    // MARK: - Internal

    /// Listen for machines. While the phone has one to talk to and is not yet
    /// talking to it, this is how it finds it; while a list is open, this is
    /// how the list says what is in range.
    fileprivate func startScan() {
        guard let centralManager, centralManager.state == .poweredOn else { return }
        let idle = connectionState != .connected && connectionState != .connecting
        DispatchQueue.main.async {
            if idle {
                self.connectionState = .searching
                self.configSynced = false
            }
            self.discovered = []
            self.lastRssiPush = [:]
        }
        // Duplicates on: RSSI is how a picker sorts, and a machine that moves
        // closer should climb the list rather than keep the reading it had when
        // it was first seen.
        centralManager.scanForPeripherals(withServices: [nusServiceUUID], options: [
            CBCentralManagerScanOptionAllowDuplicatesKey: true
        ])
        log.info("Scanning for machines...")

        guard idle else { return }
        DispatchQueue.main.async {
            self.scanTimer?.invalidate()
            self.scanTimer = Timer.scheduledTimer(withTimeInterval: scanTimeout, repeats: false) { [weak self] _ in
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
        guard var known = directory.machine(matching: seen) else { return }
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
        if let m = current, m.id == known.id,
           connectionState == .searching || connectionState == .searchingLong {
            connect(m, peripheralID: seen.id)
        }
    }

    /// Open the link to the machine this phone is pointed at, whose peripheral
    /// the radio has just heard.
    fileprivate func connect(_ machine: KnownMachine, peripheralID: String) {
        guard let centralManager,
              let peripheral = centralManager.retrievePeripherals(withIdentifiers:
                  [UUID(uuidString: peripheralID)].compactMap { $0 }).first
        else { return }

        scanTimer?.invalidate()
        if !browsing { centralManager.stopScan() }
        machine.peripheralID = peripheralID
        connectedPeripheral = peripheral
        connectionState = .connecting
        centralManager.connect(peripheral, options: nil)
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
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: BLEManager.bleOtaBegin, payload: payload)
        }
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
                await MainActor.run { self.startUpdate(image: next, data: data, on: self.otaModel) }
            } catch {
                await MainActor.run {
                    self.otaProgress = OTAProgress(target: next.target, what: next.what,
                                                   sent: 0, total: next.bytes,
                                                   failure: error.localizedDescription)
                    self.otaQueue = []
                    self.otaFetch = nil
                }
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
            // this connection runs on. The page stays; the link comes back.
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
        bleQueue.async { [weak self] in
            self?.sendBLEFrame(type: BLEManager.bleOtaData, payload: frame)
        }

        DispatchQueue.main.async {
            if var p = self.otaProgress, end > p.sent {
                p.sent = end
                self.otaProgress = p
            }
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

        DispatchQueue.main.async {
            guard let m = self.current else { return }
            m.radioBoardVersion = version
            // A name given while the machine was out of earshot stands until
            // the machine says it back; what it says otherwise is what it is.
            let pending = m.pendingName
            let heard = pending == nil || pending == name ? name : ""
            let said = self.directory.introduce(m, unit: unit == "000000" ? "" : unit, name: heard)
            if pending != nil, pending == name { said.pendingName = nil }
            self.directory.save()
        }
    }

    /// VersionsPayload: [count:1] then count × [board:1][version:24][artCrc:4].
    fileprivate func handleVersions(_ payload: Data) {
        guard payload.count >= 1 else { return }
        let b = payload.startIndex
        let count = min(Int(payload[b]), 3)
        var found = MachineVersions()
        for i in 0..<count {
            let o = b + 1 + i * 29
            guard payload.count >= (o - b) + 29 else { break }
            let board = payload[o]
            let raw = payload[(o + 1)..<(o + 25)].prefix { $0 != 0 }
            found.byBoard[board] = String(data: Data(raw), encoding: .utf8) ?? ""
            found.artCrc[board] = UInt32(payload[o + 25]) | (UInt32(payload[o + 26]) << 8)
                                | (UInt32(payload[o + 27]) << 16) | (UInt32(payload[o + 28]) << 24)
        }
        DispatchQueue.main.async {
            guard let m = self.current else { return }
            m.versions = found
            m.versionsReadAt = Date()
            self.directory.touch()
        }
    }

    fileprivate func scheduleReconnect() {
        DispatchQueue.main.async {
            self.reconnectTimer?.invalidate()
            self.reconnectTimer = Timer.scheduledTimer(withTimeInterval: 2, repeats: false) { [weak self] _ in
                self?.startScan()
            }
        }
    }

    fileprivate func handleBinStart(_ payload: Data) {
        guard isDownloading else {
            log.debug("Ignoring unsolicited BIN_START")
            return
        }
        guard payload.count >= 10 else { return }
        let psi = payload.startIndex
        let slot = Int(payload[psi])
        let size = UInt32(payload[psi + 2]) | (UInt32(payload[psi + 3]) << 8) |
                   (UInt32(payload[psi + 4]) << 16) | (UInt32(payload[psi + 5]) << 24)
        let crc = UInt32(payload[psi + 6]) | (UInt32(payload[psi + 7]) << 8) |
                  (UInt32(payload[psi + 8]) << 16) | (UInt32(payload[psi + 9]) << 24)
        imgDownloadSlot = slot
        imgDownloadExpected = Int(size)
        imgDownloadCRC = crc
        imgDownloadData = Data()
        binStartReceived = true
        log.info("BIN_START: slot \(slot), \(size) bytes, CRC=0x\(String(crc, radix: 16))")
    }

    fileprivate func handleBinData(_ payload: Data) {
        guard binStartReceived else { return }
        imgDownloadData.append(payload)
    }

    fileprivate func handleBinEnd() {
        guard binStartReceived else { return }
        binStartReceived = false
        let imgData = imgDownloadData
        let slot = imgDownloadSlot
        let expectedSize = imgDownloadExpected
        let expectedCRC = imgDownloadCRC
        imgDownloadSlot = -1
        imgDownloadData = Data()

        if imgData.count != expectedSize {
            log.error("Image \(slot) size mismatch: got \(imgData.count) expected \(expectedSize)")
            retryDownload(slot: slot)
            return
        }

        let actualCRC = ImageProcessor.crc32(imgData)
        if actualCRC != expectedCRC {
            log.error("Image \(slot) CRC mismatch: got 0x\(String(actualCRC, radix: 16)) expected 0x\(String(expectedCRC, radix: 16))")
            retryDownload(slot: slot)
            return
        }

        imgDownloadRetries = 0
        let image = UIImage(data: imgData)
        DispatchQueue.main.async {
            // Kept on the record, beside the crc the machine listed for it.
            self.saveImageToDisk(slot: slot, data: imgData)
            self.savePersistedCRC(slot: slot, crc: expectedCRC)
            if let image {
                self.cachedImages[slot] = image
                log.info("Image \(slot) cached (\(imgData.count) bytes, CRC verified)")
            } else {
                log.error("Image \(slot) decode failed: \(imgData.count) bytes")
            }
        }
        startNextDownload()
    }

    private func retryDownload(slot: Int) {
        imgDownloadRetries += 1
        if imgDownloadRetries <= 3 {
            log.info("Retrying image \(slot) download (attempt \(self.imgDownloadRetries))")
            send("GETPNG:\(slot)")
        } else {
            log.error("Image \(slot) download failed after 3 retries")
            imgDownloadRetries = 0
            startNextDownload()
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
            DispatchQueue.main.async {
                // The radio is up: turned toward whatever the phone is pointed
                // at, and a list already open keeps looking too.
                self.ble.radioOff = false
                self.ble.point()
                if self.ble.browsing { self.ble.startScan() }
            }
        } else {
            DispatchQueue.main.async {
                // The radio is down. The page says so; the demo does not care.
                self.ble.radioOff = true
                self.ble.point()
            }
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral,
                         advertisementData: [String: Any], rssi RSSI: NSNumber) {
        guard let seen = MachineAdvert.read(peripheral: peripheral,
                                            advertisementData: advertisementData,
                                            rssi: RSSI) else { return }

        // Duplicates are on, so this runs many times a second per machine. Only
        // a sighting that changes what a row says reaches the main thread.
        if let i = ble.discovered.firstIndex(where: { $0.id == seen.id }) {
            let due = Date().timeIntervalSince(ble.lastRssiPush[seen.id] ?? .distantPast) >= 0.5
            let fills = (!seen.name.isEmpty && ble.discovered[i].name != seen.name)
                     || (!seen.unit.isEmpty && ble.discovered[i].unit != seen.unit)
                     || (seen.model != .unknown && ble.discovered[i].model != seen.model)
            guard due || fills else { return }
            DispatchQueue.main.async {
                guard let i = self.ble.discovered.firstIndex(where: { $0.id == seen.id }) else { return }
                self.ble.lastRssiPush[seen.id] = Date()
                var entry = self.ble.discovered[i]
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
                self.ble.discovered[i] = entry
                self.ble.noteSighting(entry)
            }
            return
        }

        DispatchQueue.main.async {
            guard !self.ble.discovered.contains(where: { $0.id == seen.id }) else { return }
            log.info("Found \(seen.displayName) at \(seen.rssi) dBm")
            self.ble.discovered.append(seen)
            self.ble.lastRssiPush[seen.id] = Date()
            // The set changed, so this is where the order is settled.
            self.ble.discovered.sort { $0.rssi > $1.rssi }
            self.ble.noteSighting(seen)
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        log.info("Connected to \(peripheral.name ?? "device")")
        peripheral.delegate = self
        peripheral.discoverServices([nusServiceUUID])
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        log.error("Connection failed: \(error?.localizedDescription ?? "unknown")")
        ble.connectedPeripheral = nil
        ble.userInitiatedDisconnect = false
        ble.scheduleReconnect()
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        if ble.demoMode || ble.userInitiatedDisconnect {
            ble.userInitiatedDisconnect = false
            return
        }
        log.info("Disconnected")
        ble.imgDownloadSlot = -1
        ble.binStartReceived = false
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
        let m = ble
        DispatchQueue.main.async { m.stopFacePump() }
        DispatchQueue.main.async {
            self.ble.connectionState = .searching
            self.ble.configSynced = false
            self.ble.statsSynced = false
            self.ble.chartDataSynced = false
            self.ble.imgDownloadQueue = []
            self.ble.isDownloading = false
            self.ble.imageDownloadProgress = nil
            self.ble.isUploading = false
            self.ble.uploadProgress = nil
            self.ble.uploadSteps = []
            self.ble.uploadQueue = []
            self.ble.uploadQueueTotal = 0
            self.ble.uploadImageRef = nil
            self.ble.activeUploadImage = nil
            self.ble.activeUploadSlot = -1
            self.ble.primeActive = false
            self.ble.cleanCycleActive = false
            self.ble.cleanCyclePhase = nil
            if self.ble.pendingDeleteSlot >= 0 {
                self.ble.numImages = self.ble.preDeleteNumImages
                self.ble.cachedImages = self.ble.preDeleteCachedImages
                self.ble.imageNames = self.ble.preDeleteImageNames
                self.ble.pendingDeleteSlot = -1
            }
            self.ble.scheduleReconnect()
        }
    }

    // MARK: - CBPeripheralDelegate (GATT service/characteristic discovery)

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard error == nil, let services = peripheral.services else { return }
        for service in services where service.uuid == nusServiceUUID {
            peripheral.discoverCharacteristics([nusRxUUID, nusTxUUID], for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard error == nil, let chars = service.characteristics else { return }
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
            let m = ble
            DispatchQueue.main.async {
                m.connectionState = .connected
                if let machine = m.current {
                    machine.lastConnected = Date()
                    // A name given while the machine was out of earshot, now
                    // that it is in it.
                    if let name = machine.pendingName { m.send("IDENTITY \(name)") }
                    m.directory.save()
                }
                // GET_CONFIG and LIST are the rotary display's vocabulary, on
                // the machine under the counter. An appliance answers neither.
                // What an appliance is asked instead is what pictures it
                // holds, which is the screen someone opens the app for.
                if m.current?.model == .prototype {
                    m.send("GET_CONFIG")
                    m.send("LIST")
                } else {
                    m.saidStanding = ""   // a new session reports its own conditions
                    m.queryImageSlots()
                    m.startFacePump()
                }
            }
        }
    }

    // iOS says when its outgoing queue has drained. A picture is streamed
    // rather than pulled, so this is what paces it: fill the link, stop when it
    // says stop, and carry on from here.
    func peripheralIsReady(toSendWriteWithoutResponse peripheral: CBPeripheral) {
        ble.bleQueue.async { [weak self] in self?.ble.pumpImageFrames() }
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
        var frameBuffer = value

        // Parse all complete frames: [type(1B)][len(2B LE)][payload...]
        while frameBuffer.count >= 3 {
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
            case 0x01: // TEXT
                if let text = String(data: payload, encoding: .utf8) {
                    if text.hasPrefix("DBG:") { continue }
                    DispatchQueue.main.async {
                        self.ble.handleTextResponse(text)
                    }
                }
            case 0x02: // BIN_START
                ble.handleBinStart(payload)
            case 0x03: // BIN_DATA
                ble.handleBinData(payload)
            case 0x04: // BIN_END
                ble.handleBinEnd()
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
            default:
                break
            }
        }
    }
}
