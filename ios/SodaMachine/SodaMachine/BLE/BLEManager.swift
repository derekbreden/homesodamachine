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
    case choosing       // more than one machine in range, none of them remembered
    case connecting
    case connected
}

/// How long a scan collects before it decides. Long enough that the second
/// machine on the bench is in the list when the first one is.
private let settleWindow: TimeInterval = 2.5

// ────────────────────────────────────────────────────────────
// BLEManager — @Observable so SwiftUI only re-renders views
// that read the specific property that changed.
// ────────────────────────────────────────────────────────────

@Observable
class BLEManager {
    var connectionState: ConnectionState = .bluetoothOff

    // Config state (synced from ESP32 via S3 bridge)
    var configSynced = false
    var flavor1Image: Int = 0
    var flavor2Image: Int = 1
    var flavor1Ratio: Int = 20
    var flavor2Ratio: Int = 20
    var numImages: Int = 0

    // Image list and cached images
    var imageNames: [String] = []
    var cachedImages: [Int: UIImage] = [:]
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
    var s3Version: String = ""
    var espVersion: String = ""
    var rpVersion: String = ""

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

    // Demo mode (no hardware needed)
    var demoMode = false

    // ── The user's own pictures ───────────────────────────────────────────
    // What the machine says it holds, and how an upload to it is going. The
    // bundle itself is held only for the length of the push.
    var imageSlots = ImageSlots()
    var flavorArt = FlavorArt()
    var imageQueue: [QueuedImage] = []
    // A read-back in flight, and the crcs already asked for, so a face is
    // fetched once ever rather than once per state frame.
    /// Faces by the crc32 of the picture they belong to. Observable, so a face
    /// that lands redraws the tile that was waiting for it.
    var faces: [UInt32: UIImage] = [:]
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
    var discovered: [DiscoveredMachine] = []
    var connectedMachine: DiscoveredMachine? = nil

    /// What faces are filed under. The machine's own three bytes when it has
    /// said them, and this phone's id for it otherwise — a picture is still
    /// worth caching for a machine that has not introduced itself yet.
    var machineKey: String {
        if let m = connectedMachine {
            return m.unit.isEmpty ? m.id : m.unit
        }
        return ""
    }

    /// The one to reconnect to without asking. Set by picking, cleared by
    /// picking something else.
    var rememberedMachineID: String? {
        get { UserDefaults.standard.string(forKey: "rememberedMachineID") }
        set { UserDefaults.standard.set(newValue, forKey: "rememberedMachineID") }
    }

    @ObservationIgnored fileprivate var settleTimer: Timer?
    @ObservationIgnored fileprivate var chooserPending = false
    @ObservationIgnored fileprivate var scanStartedAt = Date.distantPast
    @ObservationIgnored fileprivate var lastRssiPush: [String: Date] = [:]

    // ── Pushing an image ─────────────────────────────────────────────────
    // The board pulls. It asks for an offset and a length, this sends exactly
    // that, and nothing moves until it asks again — so the phone never has to
    // guess a rate, and a frame that goes missing costs one re-ask.
    var otaProgress: OTAProgress? = nil
    /// What the board with the radio says it is running, from BLE_IDENTITY.
    var radioBoardVersion: String = ""
    /// What every board on the machine reports, assembled by its main board.
    var machineVersions = MachineVersions()

    @ObservationIgnored fileprivate var otaImage: FirmwareImage? = nil
    @ObservationIgnored fileprivate var otaData: Data = Data()

    /// What one tap of Update still owes. A board reboots into its new image and
    /// the link comes back before the next one starts, so these go one at a time.
    var otaQueue: [FirmwareImage] = []
    var otaQueueDone: Int = 0
    @ObservationIgnored fileprivate var otaModel: MachineModel = .unknown
    @ObservationIgnored fileprivate var otaFetch: ((FirmwareImage) async throws -> Data)? = nil

    /// Ready to transition from animated splash to main UI.
    ///
    /// The prototype is ready once its images are down, which is what the
    /// config screens are made of. The appliance answers none of that
    /// vocabulary, so being connected is the whole of it.
    var readyToShow: Bool {
        // The last board an update touches is the one carrying the connection,
        // so finishing one drops it. Being dumped back to a search screen is not
        // what "Update complete" should look like.
        if updateSettling { return true }
        guard connectionState == .connected else { return false }
        if demoMode || isAppliance { return true }
        return !cachedImages.isEmpty
    }

    /// An update finished and the machine is restarting into it.
    var updateSettling = false

    /// Which screens this machine gets. A machine whose advertisement carried
    /// no model byte is running firmware older than that, and every one of
    /// those is a prototype.
    var isAppliance: Bool { connectedMachine?.model == .appliance }

    // Chart data (populated by GET_CHART_DATA response)
    var chartData24H: [[Double]] = [Array(repeating: 0, count: 24), Array(repeating: 0, count: 24)]
    var chartData30D: [[Double]] = [Array(repeating: 0, count: 30), Array(repeating: 0, count: 30)]
    var chartDataHOD: [[Double]] = [Array(repeating: 0, count: 24), Array(repeating: 0, count: 24)]
    var chartDataHODDays: Int = 1
    var chartDataSynced: Bool = false

    @ObservationIgnored fileprivate var rawHourlyData: [[(seqHour: UInt32, flowSum: UInt32)]] = [[], []]
    @ObservationIgnored fileprivate var currentSeqHour: UInt32 = 0
    @ObservationIgnored fileprivate var chartCurReceived: Int = 0

    // Live chart baselines (for computing delta from CHART_LIVE pushes)
    @ObservationIgnored fileprivate var chartBaseFlowSum: [UInt32] = [0, 0]
    @ObservationIgnored fileprivate var chartBase24H_last: [Double] = [0, 0]
    @ObservationIgnored fileprivate var chartBase30D_last: [Double] = [0, 0]
    @ObservationIgnored fileprivate var chartBaseHOD_slot: [Double] = [0, 0]
    @ObservationIgnored fileprivate var chartBaseHOD_hour: Int = Calendar.current.component(.hour, from: Date())
    @ObservationIgnored fileprivate var lastLiveFS: [UInt32] = [0, 0]

    // Usage statistics (used by pie chart)
    struct FlavorStats {
        var monthFlowSum: UInt32 = 0
    }
    var flavor1Stats = FlavorStats()
    var flavor2Stats = FlavorStats()
    var statsSynced = false

    // ── Internal state (not observed by SwiftUI) ──

    @ObservationIgnored fileprivate var pendingImageList: [String] = []
    @ObservationIgnored fileprivate var pendingCRCs: [Int: UInt32] = [:]  // from LIST response
    @ObservationIgnored fileprivate var connectedPeripheralUUID: String = ""

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

    init() {
        cbAdapter = CBDelegateAdapter(self)
    }

    /// Create the CBCentralManager (triggers Bluetooth permission prompt).
    /// Idempotent — safe to call multiple times.
    /// Bring the radio up, or start looking again on a radio that is already up.
    ///
    /// The central manager outlives a disconnect — it is the app's, not the
    /// connection's — and creating it is what starts the first scan, by way of
    /// `centralManagerDidUpdateState`. A second call therefore has to start one
    /// itself, or "Scan for Hardware" after a disconnect does nothing at all.
    func activateBluetooth() {
        guard centralManager == nil else {
            startScan()
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
        } else if connectionState != .bluetoothOff {
            // iOS may have stopped our scan or stalled a connection attempt
            // while backgrounded. Cancel any pending connection and rescan.
            if let peripheral = connectedPeripheral {
                userInitiatedDisconnect = true
                centralManager.cancelPeripheralConnection(peripheral)
                connectedPeripheral = nil
                rxCharacteristic = nil
                nusReady = false
            }
            startScan()
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
        s3Version = ""
        espVersion = ""
        rpVersion = ""
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
        guard !isDownloading else { return }
        let persistedCRCs = loadPersistedCRCs()
        var queue: [Int] = []
        for slot in 0..<numImages {
            if cachedImages[slot] != nil { continue }
            // Check if we have a CRC match and disk cache hit
            if let advertised = advertisedCRCs[slot],
               let persisted = persistedCRCs[slot],
               advertised == persisted,
               let diskImage = loadImageFromDisk(slot: slot) {
                cachedImages[slot] = diskImage
                log.info("Image \(slot) loaded from disk cache (CRC match)")
                continue
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

    // MARK: - Demo mode

    func enterDemoMode() {
        centralManager?.stopScan()
        scanTimer?.invalidate()
        reconnectTimer?.invalidate()
        demoMode = true
        connectionState = .connected
        configSynced = true
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
        s3Version = "Demo"
        espVersion = "Demo"
        rpVersion = "Demo"
    }

    func exitDemoMode() {
        demoMode = false
        configSynced = false
        cachedImages = [:]
        imageNames = []
        numImages = 0
        s3Version = ""
        espVersion = ""
        rpVersion = ""
        connectionState = .searching
    }

    func disconnect() {
        centralManager?.stopScan()
        scanTimer?.invalidate()
        settleTimer?.invalidate()
        reconnectTimer?.invalidate()
        // Done with this machine: the next scan offers a choice rather than
        // going straight back to the one just left.
        rememberedMachineID = nil
        connectedMachine = nil
        if let peripheral = connectedPeripheral {
            userInitiatedDisconnect = true
            centralManager?.cancelPeripheralConnection(peripheral)
        }
        connectedPeripheral = nil
        rxCharacteristic = nil
        nusReady = false
        connectionState = .searching
        configSynced = false
        statsSynced = false
        chartDataSynced = false
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

    private func populateDemoStats() {
        flavor1Stats = FlavorStats(monthFlowSum: 60000)
        flavor2Stats = FlavorStats(monthFlowSum: 40000)
        statsSynced = true
    }

    private func populateDemoChartData() {
        var hod0 = [Double](repeating: 0, count: 24)
        var hod1 = [Double](repeating: 0, count: 24)
        for h in 0..<24 {
            let angle = Double(h - 12) / 12.0 * .pi
            let base = max(0, cos(angle)) * 8.0
            hod0[h] = base * 1.2
            hod1[h] = base * 0.8
        }
        chartDataHOD = [hod0, hod1]
        chartDataHODDays = 14

        let calendar = Calendar.current
        let currentHour = calendar.component(.hour, from: Date())
        var h24_0 = [Double](repeating: 0, count: 24)
        var h24_1 = [Double](repeating: 0, count: 24)
        for i in 0..<24 {
            let hour = (currentHour - 23 + i + 24) % 24
            let angle = Double(hour - 12) / 12.0 * .pi
            let base = max(0, cos(angle))
            h24_0[i] = base * 10.0 * (0.7 + Double.random(in: 0...0.6))
            h24_1[i] = base * 7.0 * (0.7 + Double.random(in: 0...0.6))
        }
        chartData24H = [h24_0, h24_1]

        var d30_0 = [Double](repeating: 0, count: 30)
        var d30_1 = [Double](repeating: 0, count: 30)
        for i in 0..<30 {
            let ramp = Double(i + 1) / 30.0
            d30_0[i] = ramp * 60.0 * (0.5 + Double.random(in: 0...1.0))
            d30_1[i] = ramp * 40.0 * (0.5 + Double.random(in: 0...1.0))
        }
        chartData30D = [d30_0, d30_1]

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
                    rawHourlyData[flavor].append((seqHour: seq, flowSum: fs))
                }
            }
            return
        }

        if prefix == "CHART_CUR" {
            if let fsStr = kvValues["FS"], let fs = UInt32(fsStr) {
                computeChartsFromRaw(flavor: flavor)
                chartBaseFlowSum[flavor] = fs
                chartBase24H_last[flavor] = chartData24H[flavor][23]
                chartBase30D_last[flavor] = chartData30D[flavor][29]
                let curHour = Calendar.current.component(.hour, from: Date())
                chartBaseHOD_hour = curHour
                chartBaseHOD_slot[flavor] = chartDataHOD[flavor][curHour]
                lastLiveFS[flavor] = fs
            }
            chartCurReceived += 1
            if chartCurReceived >= 2 {
                chartRetryTimer?.cancel()
                chartDataSynced = true
                statsSynced = true
                chartCurReceived = 0
            }
            return
        }

        if prefix == "CHART_LIVE" {
            if let fsStr = kvValues["FS"], let newFS = UInt32(fsStr) {
                let delta = Double(newFS - chartBaseFlowSum[flavor]) * 0.05

                var new24H = chartData24H
                new24H[flavor][23] = chartBase24H_last[flavor] + delta

                var new30D = chartData30D
                new30D[flavor][29] = chartBase30D_last[flavor] + delta

                var newHOD = chartDataHOD
                newHOD[flavor][chartBaseHOD_hour] = chartBaseHOD_slot[flavor] + delta

                let incr = newFS - lastLiveFS[flavor]
                lastLiveFS[flavor] = newFS

                withAnimation {
                    chartData24H = new24H
                    chartData30D = new30D
                    chartDataHOD = newHOD
                    if flavor == 0 {
                        flavor1Stats.monthFlowSum += incr
                    } else {
                        flavor2Stats.monthFlowSum += incr
                    }
                }
            }
            return
        }
    }

    private func computeChartsFromRaw(flavor: Int) {
        let now = Date()
        let calendar = Calendar.current
        let startOfToday = calendar.startOfDay(for: now)

        var arr24H = [Double](repeating: 0, count: 24)
        var arr30D = [Double](repeating: 0, count: 30)
        var arrHOD = [Double](repeating: 0, count: 24)
        var daysWithData = Set<Int>()
        var monthFlowSum: UInt32 = 0

        for entry in rawHourlyData[flavor] {
            let hoursAgo = Int(currentSeqHour) - Int(entry.seqHour)
            guard hoursAgo >= 0 else { continue }
            let bucketDate = now.addingTimeInterval(-Double(hoursAgo) * 3600)
            let flowValue = Double(entry.flowSum) * 0.05

            if hoursAgo < 24 {
                arr24H[23 - hoursAgo] += flowValue
            }

            let bucketDay = calendar.startOfDay(for: bucketDate)
            let daysAgo = calendar.dateComponents([.day], from: bucketDay, to: startOfToday).day ?? 999
            if daysAgo >= 0, daysAgo < 30 {
                arr30D[29 - daysAgo] += flowValue
                daysWithData.insert(daysAgo)
                monthFlowSum += entry.flowSum
            }

            if daysAgo >= 0, daysAgo < 30 {
                let hourOfDay = calendar.component(.hour, from: bucketDate)
                arrHOD[hourOfDay] += flowValue
            }
        }

        chartDataHODDays = max(daysWithData.count, 1)

        withAnimation {
            chartData24H[flavor] = arr24H
            chartData30D[flavor] = arr30D
            chartDataHOD[flavor] = arrHOD
            let stats = FlavorStats(monthFlowSum: monthFlowSum)
            if flavor == 0 {
                flavor1Stats = stats
            } else {
                flavor2Stats = stats
            }
        }

        rawHourlyData[flavor] = []
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

    private func imageCacheDir() -> URL? {
        guard !connectedPeripheralUUID.isEmpty else { return nil }
        let caches = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first!
        return caches.appendingPathComponent("images/\(connectedPeripheralUUID)")
    }

    private func saveImageToDisk(slot: Int, data: Data) {
        guard let dir = imageCacheDir() else { return }
        do {
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            try data.write(to: dir.appendingPathComponent("slot_\(slot).png"))
        } catch {
            log.error("Failed to cache image \(slot) to disk: \(error.localizedDescription)")
        }
    }

    private func loadImageFromDisk(slot: Int) -> UIImage? {
        guard let dir = imageCacheDir() else { return nil }
        let url = dir.appendingPathComponent("slot_\(slot).png")
        guard let data = try? Data(contentsOf: url) else { return nil }
        return UIImage(data: data)
    }

    fileprivate func clearDiskCache() {
        guard let dir = imageCacheDir() else { return }
        try? FileManager.default.removeItem(at: dir)
        clearPersistedCRCs()
    }

    private func crcDefaultsKey() -> String {
        return "imageCRCs_\(connectedPeripheralUUID)"
    }

    private func loadPersistedCRCs() -> [Int: UInt32] {
        guard !connectedPeripheralUUID.isEmpty else { return [:] }
        guard let dict = UserDefaults.standard.dictionary(forKey: crcDefaultsKey()) else { return [:] }
        var result: [Int: UInt32] = [:]
        for (key, val) in dict {
            if let slot = Int(key), let num = val as? NSNumber {
                result[slot] = num.uint32Value
            }
        }
        return result
    }

    private func savePersistedCRC(slot: Int, crc: UInt32) {
        guard !connectedPeripheralUUID.isEmpty else { return }
        var dict = UserDefaults.standard.dictionary(forKey: crcDefaultsKey()) ?? [:]
        dict["\(slot)"] = NSNumber(value: crc)
        UserDefaults.standard.set(dict, forKey: crcDefaultsKey())
    }

    private func clearPersistedCRCs() {
        guard !connectedPeripheralUUID.isEmpty else { return }
        UserDefaults.standard.removeObject(forKey: crcDefaultsKey())
    }

    // MARK: - Internal

    fileprivate func startScan() {
        guard let centralManager, centralManager.state == .poweredOn else { return }
        DispatchQueue.main.async {
            self.connectionState = .searching
            self.configSynced = false
            // Don't clear cachedImages here — disk cache + CRC comparison
            // in downloadAllImages() handles stale data on reconnect
        }
        // Duplicates on: RSSI is how a picker sorts, and a machine that moves
        // closer should climb the list rather than keep the reading it had when
        // it was first seen.
        centralManager.scanForPeripherals(withServices: [nusServiceUUID], options: [
            CBCentralManagerScanOptionAllowDuplicatesKey: true
        ])
        log.info("Scanning for machines...")

        DispatchQueue.main.async {
            self.discovered = []
            self.lastRssiPush = [:]
            self.chooserPending = true
            self.scanStartedAt = Date()
            // Repeating, because a machine that only starts advertising after
            // the window closes still has to be decided about. It stops when
            // the decision is made, or when the scan is torn down.
            self.settleTimer?.invalidate()
            self.settleTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) {
                [weak self] _ in self?.decideFromScan()
            }
        }

        DispatchQueue.main.async {
            self.scanTimer?.invalidate()
            self.scanTimer = Timer.scheduledTimer(withTimeInterval: scanTimeout, repeats: false) { [weak self] _ in
                guard let self, self.connectionState == .searching else { return }
                self.connectionState = .searchingLong
                log.info("Still scanning, showing hints")
            }
        }
    }

    /// What the scan has found. The machine picked last time wins outright and
    /// needs no window; anything else waits for one, so the second machine on
    /// the bench is in the list before the question is asked.
    fileprivate func decideFromScan() {
        guard chooserPending, connectionState == .searching || connectionState == .searchingLong
        else { return }

        if let remembered = rememberedMachineID,
           let match = discovered.first(where: { $0.id == remembered }) {
            connect(to: match)
            return
        }
        guard Date().timeIntervalSince(scanStartedAt) >= settleWindow else { return }
        if discovered.count == 1 {
            connect(to: discovered[0])
        } else if discovered.count > 1 {
            chooserPending = false
            settleTimer?.invalidate()
            connectionState = .choosing
        }
    }

    /// Point the app at one machine. Everything the previous one filled in is
    /// dropped, but its disk cache is not — the caches are per-peripheral, so
    /// coming back finds what was there.
    func connect(to machine: DiscoveredMachine) {
        guard let centralManager,
              let peripheral = centralManager.retrievePeripherals(withIdentifiers:
                  [UUID(uuidString: machine.id)].compactMap { $0 }).first
        else { return }

        chooserPending = false
        settleTimer?.invalidate()
        centralManager.stopScan()

        if !connectedPeripheralUUID.isEmpty && connectedPeripheralUUID != machine.id {
            forgetConnectedState()
        }
        rememberedMachineID = machine.id
        connectedMachine = machine
        connectedPeripheralUUID = machine.id
        connectedPeripheral = peripheral
        connectionState = .connecting
        centralManager.connect(peripheral, options: nil)
    }

    /// Go back to the list without forgetting what is on disk for either.
    func chooseAnother() {
        if let peripheral = connectedPeripheral {
            userInitiatedDisconnect = true
            centralManager?.cancelPeripheralConnection(peripheral)
        }
        connectedPeripheral = nil
        rxCharacteristic = nil
        nusReady = false
        connectedMachine = nil
        rememberedMachineID = nil
        forgetConnectedState()
        connectionState = .searching
        startScan()
    }

    /// The previous machine's answers, which do not describe this one.
    fileprivate func forgetConnectedState() {
        configSynced = false
        statsSynced = false
        chartDataSynced = false
        cachedImages = [:]
        imageNames = []
        numImages = 0
        s3Version = ""
        espVersion = ""
        rpVersion = ""
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
            // this connection runs on. Hold the screen until it is back.
            updateSettling = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 90) { [weak self] in
                self?.updateSettling = false
            }
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
            self.radioBoardVersion = version
            if var m = self.connectedMachine {
                if !name.isEmpty { m.name = name }
                if !unit.isEmpty, unit != "000000" { m.unit = unit }
                self.connectedMachine = m
            }
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
        DispatchQueue.main.async { self.machineVersions = found }
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
        // Persist to disk cache
        saveImageToDisk(slot: slot, data: imgData)
        savePersistedCRC(slot: slot, crc: expectedCRC)
        DispatchQueue.main.async {
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
            ble.startScan()
        } else {
            DispatchQueue.main.async {
                self.ble.connectionState = .bluetoothOff
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
            }
            return
        }

        DispatchQueue.main.async {
            self.ble.scanTimer?.invalidate()
            guard !self.ble.discovered.contains(where: { $0.id == seen.id }) else { return }
            log.info("Found \(seen.displayName) at \(seen.rssi) dBm")
            self.ble.discovered.append(seen)
            self.ble.lastRssiPush[seen.id] = Date()
            // The set changed, so this is where the order is settled.
            self.ble.discovered.sort { $0.rssi > $1.rssi }
            self.ble.decideFromScan()
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        DispatchQueue.main.async { self.ble.updateSettling = false }
        log.info("Connected to \(peripheral.name ?? "device")")
        peripheral.delegate = self
        peripheral.discoverServices([nusServiceUUID])
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        log.error("Connection failed: \(error?.localizedDescription ?? "unknown")")
        ble.connectedPeripheral = nil
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
            DispatchQueue.main.async { self.ble.connectionState = .connected }
            log.info("NUS ready")
            // GET_CONFIG and LIST are the rotary display's vocabulary, on the
            // machine under the counter. An appliance answers neither, so it
            // was being asked two questions it has no words for on every
            // connection. What an appliance is asked instead is what pictures
            // it holds, which is the screen someone opens the app for.
            if ble.connectedMachine?.model == .prototype {
                ble.send("GET_CONFIG")
                ble.send("LIST")
            } else {
                ble.queryImageSlots()
                let m = ble
                DispatchQueue.main.async { m.startFacePump() }
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
