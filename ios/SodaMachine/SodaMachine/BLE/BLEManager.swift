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

    /// Ready to transition from animated splash to main UI
    var readyToShow: Bool {
        connectionState == .connected && (demoMode || !cachedImages.isEmpty)
    }

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

    // GATT/NUS state
    @ObservationIgnored fileprivate var nusReady = false
    @ObservationIgnored fileprivate var frameBuffer = Data()
    @ObservationIgnored fileprivate var rxCharacteristic: CBCharacteristic?

    // BLE runs on a dedicated background queue so binary data accumulation
    // and BLE writes don't block the main thread during image downloads.
    @ObservationIgnored let bleQueue = DispatchQueue(label: "com.derekbreden.SodaMachine.BLE", qos: .userInitiated)
    @ObservationIgnored fileprivate var cbAdapter: CBDelegateAdapter!
    @ObservationIgnored fileprivate var centralManager: CBCentralManager!
    @ObservationIgnored fileprivate var connectedPeripheral: CBPeripheral?
    @ObservationIgnored fileprivate var scanTimer: Timer?
    @ObservationIgnored fileprivate var reconnectTimer: Timer?
    @ObservationIgnored fileprivate var userInitiatedDisconnect = false

    init() {
        cbAdapter = CBDelegateAdapter(self)
    }

    /// Create the CBCentralManager (triggers Bluetooth permission prompt).
    /// Idempotent — safe to call multiple times.
    func activateBluetooth() {
        guard centralManager == nil else { return }
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
                self.frameBuffer = Data()
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
                frameBuffer = Data()
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
    fileprivate func sendBLEFrame(type: UInt8, payload: Data) {
        guard let rx = rxCharacteristic, let p = connectedPeripheral else { return }
        var frame = Data([type, UInt8(payload.count & 0xFF), UInt8((payload.count >> 8) & 0xFF)])
        frame.append(payload)
        p.writeValue(frame, for: rx, type: .withResponse)
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
    }

    func subscribeStats() {
        if demoMode { return }
        send("STATS_SUBSCRIBE")
    }

    func unsubscribeStats() {
        if demoMode { return }
        send("STATS_UNSUBSCRIBE")
    }

    func factoryReset() {
        if demoMode {
            flavor1Image = 0
            flavor2Image = 1
            flavor1Ratio = 20
            flavor2Ratio = 20
            numImages = 3
            imageNames = ["diet_wild_cherry_pepsi", "diet_mtn_dew", "diet_coke"]
            cachedImages = [
                0: generateDemoImage(label: "Cherry Pepsi", color: UIColor(red: 0.7, green: 0.1, blue: 0.15, alpha: 1)),
                1: generateDemoImage(label: "Mtn Dew", color: UIColor(red: 0.2, green: 0.6, blue: 0.2, alpha: 1)),
                2: generateDemoImage(label: "Diet Coke", color: UIColor(red: 0.4, green: 0.4, blue: 0.45, alpha: 1))
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
            cachedImages = [:]
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
        imageNames = ["diet_wild_cherry_pepsi", "diet_mtn_dew", "diet_coke"]
        cachedImages = [
            0: generateDemoImage(label: "Cherry Pepsi", color: UIColor(red: 0.7, green: 0.1, blue: 0.15, alpha: 1)),
            1: generateDemoImage(label: "Mtn Dew", color: UIColor(red: 0.2, green: 0.6, blue: 0.2, alpha: 1)),
            2: generateDemoImage(label: "Diet Coke", color: UIColor(red: 0.4, green: 0.4, blue: 0.45, alpha: 1))
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
        reconnectTimer?.invalidate()
        if let peripheral = connectedPeripheral {
            userInitiatedDisconnect = true
            centralManager?.cancelPeripheralConnection(peripheral)
        }
        connectedPeripheral = nil
        rxCharacteristic = nil
        nusReady = false
        frameBuffer = Data()
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
                self?.cachedImages = [:]
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
        centralManager.scanForPeripherals(withServices: [nusServiceUUID], options: [
            CBCentralManagerScanOptionAllowDuplicatesKey: false
        ])
        log.info("Auto-scanning for Soda Machine...")

        DispatchQueue.main.async {
            self.scanTimer?.invalidate()
            self.scanTimer = Timer.scheduledTimer(withTimeInterval: scanTimeout, repeats: false) { [weak self] _ in
                guard let self, self.connectionState == .searching else { return }
                self.connectionState = .searchingLong
                log.info("Still scanning, showing hints")
            }
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
        let name = peripheral.name ?? advertisementData[CBAdvertisementDataLocalNameKey] as? String ?? ""
        guard name == "SodaMachine" else { return }
        log.info("Found: \(name) (RSSI: \(RSSI.intValue))")

        DispatchQueue.main.async { self.ble.scanTimer?.invalidate() }
        central.stopScan()
        DispatchQueue.main.async { self.ble.connectionState = .connecting }
        let uuid = peripheral.identifier.uuidString
        // If connecting to a different device, clear disk cache from previous
        if !ble.connectedPeripheralUUID.isEmpty && ble.connectedPeripheralUUID != uuid {
            ble.clearDiskCache()
        }
        ble.connectedPeripheralUUID = uuid
        ble.connectedPeripheral = peripheral
        central.connect(peripheral, options: nil)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
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
        ble.frameBuffer = Data()
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
            ble.send("GET_CONFIG")
            ble.send("LIST")
        }
    }

    // MARK: - CBPeripheralDelegate (NUS notifications)

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard error == nil, let value = characteristic.value, characteristic.uuid == nusTxUUID else { return }
        ble.frameBuffer.append(value)

        // Parse all complete frames: [type(1B)][len(2B LE)][payload...]
        while ble.frameBuffer.count >= 3 {
            let type = ble.frameBuffer[ble.frameBuffer.startIndex]
            let lenLo = ble.frameBuffer[ble.frameBuffer.startIndex + 1]
            let lenHi = ble.frameBuffer[ble.frameBuffer.startIndex + 2]
            let payloadLen = Int(lenLo) | (Int(lenHi) << 8)
            let frameLen = 3 + payloadLen

            guard ble.frameBuffer.count >= frameLen else { break }

            let payload = ble.frameBuffer.subdata(in: (ble.frameBuffer.startIndex + 3)..<(ble.frameBuffer.startIndex + frameLen))
            ble.frameBuffer = ble.frameBuffer.subdata(in: (ble.frameBuffer.startIndex + frameLen)..<ble.frameBuffer.endIndex)

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
            default:
                break
            }
        }
    }
}
