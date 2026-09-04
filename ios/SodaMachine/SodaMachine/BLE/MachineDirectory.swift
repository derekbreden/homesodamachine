import Foundation
import CoreBluetooth
import UIKit
import os

private let log = Logger(subsystem: "com.derekbreden.SodaMachine", category: "Machines")

// ────────────────────────────────────────────────────────────
// The machines this phone knows, and which one it is pointed at.
//
// A MACHINE IS THE ROOT AND THE LINK IS A PROPERTY OF IT. Every machine this
// phone has added has a record here: who it is, what the phone last read off
// it and when, and how to find it again. The record outlives the connection.
// A machine in the next room, or one on its way back in a box, is still on
// the phone with everything it said — and its page is the same page whether
// or not the radio can hear it right now.
//
// IDENTITY BELONGS TO THE MAIN BOARD, NOT TO THE DISPLAY HOLDING THE RADIO.
// Two machines standing a metre apart both answer the Nordic UART service, so
// the advertisement has to say which is which before either is connected to.
// Each carries a manufacturer block — 0xFFFF, then the model byte and the low
// three bytes of that machine's main board MAC — and a local name built from
// the same unit, or whatever someone named the machine. A record is keyed by
// that unit once the machine has said it, and by this phone's own id for the
// peripheral until then. A display moved between machines advertises the
// machine it is now wired to; a replaced machine is a new record.
// ────────────────────────────────────────────────────────────

enum MachineModel: UInt8, Codable {
    case unknown = 0
    case appliance = 1
    case prototype = 2

    var label: String {
        switch self {
        case .appliance: return "Appliance"
        case .prototype: return "Prototype"
        case .unknown: return "Soda Machine"
        }
    }
}

/// One scan result: a machine in range right now, as its advertisement says.
struct DiscoveredMachine: Identifiable, Equatable {
    /// CoreBluetooth's per-install peripheral id. Stable on this phone, which is
    /// how a known machine is found again without a window.
    let id: String
    var name: String
    var model: MachineModel
    /// The main board's own three bytes, e.g. "7AFC20". Empty from a machine
    /// whose firmware predates the manufacturer block.
    var unit: String
    var rssi: Int
    var lastSeen: Date

    /// What a person calls this machine. Whoever owns it can set one — the main
    /// board holds it and the radio advertises it — and a machine nobody has
    /// named is just what it is.
    var displayName: String { name.isEmpty ? "Home Soda Machine" : name }

    /// Only what tells one machine from another in a room with two of them.
    var subtitle: String { signal }

    var signal: String {
        switch rssi {
        case (-55)...:    return "right here"
        case (-70)..<(-55): return "nearby"
        case (-85)..<(-70): return "far"
        default:          return "very far"
        }
    }
}

enum MachineAdvert {
    static let manufacturerID: UInt16 = 0xFFFF

    /// What a scan result says about the machine behind it, or nil when the
    /// peripheral is not one of ours.
    static func read(peripheral: CBPeripheral,
                     advertisementData: [String: Any],
                     rssi: NSNumber) -> DiscoveredMachine? {
        let advertised = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        let name = advertised ?? peripheral.name ?? ""

        var model = MachineModel.unknown
        var unit = ""
        if let mfg = advertisementData[CBAdvertisementDataManufacturerDataKey] as? Data,
           mfg.count >= 6 {
            let base = mfg.startIndex
            let company = UInt16(mfg[base]) | (UInt16(mfg[base + 1]) << 8)
            if company == manufacturerID {
                model = MachineModel(rawValue: mfg[base + 2]) ?? .unknown
                unit = mfg[(base + 3)..<(base + 6)].map { String(format: "%02X", $0) }.joined()
                // A display whose main board has not yet answered advertises
                // no unit at all, as three zero bytes.
                if unit == "000000" { unit = "" }
            }
        }

        // A machine that predates the manufacturer block still answers to the
        // name every unit used to carry.
        if unit.isEmpty && !name.hasPrefix("SodaMachine") && model == .unknown { return nil }

        return DiscoveredMachine(id: peripheral.identifier.uuidString,
                                 name: name.hasPrefix("SodaMachine") ? "" : name,
                                 model: model,
                                 unit: unit,
                                 rssi: rssi.intValue,
                                 lastSeen: Date())
    }
}

// ── What the phone reads off a machine ──────────────────────────────────

/// The rotary display's settings, as the prototype under the counter holds
/// them: which slot each flavor wears, what it pours at, and what is in the
/// image store.
struct PrototypeConfig: Codable, Equatable {
    var flavor1Image = 0
    var flavor2Image = 1
    var flavor1Ratio = 20
    var flavor2Ratio = 20
    var numImages = 0
    var imageNames: [String] = []
    /// The crc32 the machine listed for each slot when its picture was cached,
    /// so a reconnect can tell a picture on disk from one that changed.
    var imageCRCs: [Int: UInt32] = [:]
}

/// What each of the prototype's three boards says it runs.
struct PrototypeVersions: Codable, Equatable {
    var s3 = ""
    var esp = ""
    var rp = ""
}

/// One hour of one flavor, as the prototype counts it: the hour's sequence
/// number and the flow-meter sum inside it.
struct HourBucket: Codable, Equatable {
    var seq: UInt32
    var flow: UInt32
}

/// The prototype's usage log as it stood at one reading. `seqHour` is the
/// machine's current hour at that reading, and every bucket is placed against
/// `readAt` — so a chart laid out from this a week later still says what the
/// machine said then, rather than sliding the week's pours into today.
struct UsageReading: Codable, Equatable {
    var hourly: [[HourBucket]] = [[], []]
    var seqHour: UInt32 = 0
    var readAt: Date?
}

// ── One machine ─────────────────────────────────────────────────────────

/// One machine this phone knows. Observable field by field, so a face that
/// lands redraws the tile waiting for it and nothing else.
@Observable
final class KnownMachine: Identifiable {
    /// This record's own name on disk. Stable for the life of the record,
    /// which the key is not: a machine met before it said its unit is re-keyed
    /// when it does, and its pictures stay where they were.
    let id: String
    /// The unit, once the machine has said it; this phone's id for the
    /// peripheral until then.
    var key: String
    var unit: String
    var peripheralID: String?
    var name: String
    var model: MachineModel
    /// The machine that is always in range and never existed.
    let isDemo: Bool
    let addedAt: Date
    var lastSeen: Date?
    var lastConnected: Date?
    /// A name given while the machine was out of earshot, sent when it is next
    /// in it.
    var pendingName: String?

    // What every board reports running, as the main board assembled it.
    var versions = MachineVersions()
    var radioBoardVersion = ""
    var versionsReadAt: Date?

    // The appliance's pictures: what it holds, which face each flavor wears,
    // and the faces themselves, filed under each picture's own crc32.
    var imageSlots = ImageSlots()
    var flavorArt = FlavorArt()
    var picturesReadAt: Date?
    var faces: [UInt32: UIImage] = [:]

    // The prototype's settings, its image store, and what its boards run.
    var config = PrototypeConfig()
    var configReadAt: Date?
    var cachedImages: [Int: UIImage] = [:]
    var prototypeVersions = PrototypeVersions()

    // The prototype's usage, and the charts laid out from it.
    var usage = UsageReading()
    var chartData24H: [[Double]] = [Array(repeating: 0, count: 24), Array(repeating: 0, count: 24)]
    var chartData30D: [[Double]] = [Array(repeating: 0, count: 30), Array(repeating: 0, count: 30)]
    var chartDataHOD: [[Double]] = [Array(repeating: 0, count: 24), Array(repeating: 0, count: 24)]
    var chartDataHODDays: Int = 1
    var monthFlowSum: [UInt32] = [0, 0]

    init(id: String = UUID().uuidString, key: String, unit: String, peripheralID: String?,
         name: String, model: MachineModel, isDemo: Bool = false, addedAt: Date = Date()) {
        self.id = id
        self.key = key
        self.unit = unit
        self.peripheralID = peripheralID
        self.name = name
        self.model = model
        self.isDemo = isDemo
        self.addedAt = addedAt
    }

    var displayName: String {
        if !name.isEmpty { return name }
        return isDemo ? "Demo" : "Home Soda Machine"
    }

    /// What kind of machine, for a list with more than one kind on it.
    var kind: String { isDemo ? "Demo" : model.label }

    /// Where this record's pictures live.
    var folder: URL { MachineDirectory.root.appendingPathComponent(id, isDirectory: true) }

    /// Whether a sighting is this machine: the unit settles it when both sides
    /// have one, and the peripheral id stands in until the machine has said.
    func matches(_ seen: DiscoveredMachine) -> Bool {
        if !unit.isEmpty && !seen.unit.isEmpty { return unit == seen.unit }
        return peripheralID == seen.id
    }

    /// Lay the charts out from the usage reading, against the moment it was
    /// read. Days of data is the union of both flavors' days.
    func recomputeCharts() {
        while usage.hourly.count < 2 { usage.hourly.append([]) }
        let asOf = usage.readAt ?? Date()
        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: asOf)
        var new24 = [[Double]](repeating: Array(repeating: 0, count: 24), count: 2)
        var new30 = [[Double]](repeating: Array(repeating: 0, count: 30), count: 2)
        var newHOD = [[Double]](repeating: Array(repeating: 0, count: 24), count: 2)
        var sums: [UInt32] = [0, 0]
        var days = Set<Int>()

        for flavor in 0..<2 {
            for entry in usage.hourly[flavor] {
                let hoursAgo = Int(usage.seqHour) - Int(entry.seq)
                guard hoursAgo >= 0 else { continue }
                let bucketDate = asOf.addingTimeInterval(-Double(hoursAgo) * 3600)
                let flow = Double(entry.flow) * 0.05
                if hoursAgo < 24 { new24[flavor][23 - hoursAgo] += flow }
                let bucketDay = calendar.startOfDay(for: bucketDate)
                let daysAgo = calendar.dateComponents([.day], from: bucketDay, to: startOfDay).day ?? 999
                if daysAgo >= 0, daysAgo < 30 {
                    new30[flavor][29 - daysAgo] += flow
                    days.insert(daysAgo)
                    sums[flavor] &+= entry.flow
                    newHOD[flavor][calendar.component(.hour, from: bucketDate)] += flow
                }
            }
        }

        chartDataHODDays = max(days.count, 1)
        chartData24H = new24
        chartData30D = new30
        chartDataHOD = newHOD
        monthFlowSum = sums
    }

    // ── Pictures on disk ──────────────────────────────────────────────────
    // A face is filed under the crc32 of the picture it belongs to, so a
    // picture that moves slots keeps its face and a slot that changes hands
    // does not inherit the old one. The prototype's store is by slot, with the
    // crc the machine listed beside it in `config.imageCRCs`.

    func faceURL(crc: UInt32) -> URL {
        folder.appendingPathComponent("face-\(String(crc, radix: 16)).png")
    }

    func saveFace(_ image: UIImage, crc: UInt32) {
        guard crc != 0, let png = image.pngData() else { return }
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        try? png.write(to: faceURL(crc: crc))
    }

    func loadFace(crc: UInt32) -> UIImage? {
        guard crc != 0, let data = try? Data(contentsOf: faceURL(crc: crc)) else { return nil }
        return UIImage(data: data)
    }

    func forgetFace(crc: UInt32) {
        try? FileManager.default.removeItem(at: faceURL(crc: crc))
    }

    func slotURL(_ slot: Int) -> URL {
        folder.appendingPathComponent("slot-\(slot).png")
    }

    func saveSlot(_ slot: Int, data: Data) {
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        try? data.write(to: slotURL(slot))
    }

    func loadSlot(_ slot: Int) -> UIImage? {
        guard let data = try? Data(contentsOf: slotURL(slot)) else { return nil }
        return UIImage(data: data)
    }

    /// The prototype's whole store, gone from the phone as it has from the
    /// machine.
    func clearSlots() {
        let fm = FileManager.default
        if let names = try? fm.contentsOfDirectory(atPath: folder.path) {
            for n in names where n.hasPrefix("slot-") {
                try? fm.removeItem(at: folder.appendingPathComponent(n))
            }
        }
        config.imageCRCs = [:]
        cachedImages = [:]
    }

    /// Every picture kept for this machine, back into memory. Run once when the
    /// record is loaded; a page is drawn from memory, never from a file.
    func loadPictures() {
        let fm = FileManager.default
        guard let names = try? fm.contentsOfDirectory(atPath: folder.path) else { return }
        for n in names {
            if n.hasPrefix("face-"), n.hasSuffix(".png"),
               let crc = UInt32(n.dropFirst(5).dropLast(4), radix: 16),
               let img = loadFace(crc: crc) {
                faces[crc] = img
            } else if n.hasPrefix("slot-"), n.hasSuffix(".png"),
                      let slot = Int(n.dropFirst(5).dropLast(4)),
                      let img = loadSlot(slot) {
                cachedImages[slot] = img
            }
        }
    }
}

// ── The record on disk ──────────────────────────────────────────────────

/// A machine as it is written down. Everything but the pictures, which are
/// files beside it.
struct MachineRecord: Codable {
    var id: String
    var key: String
    var unit: String
    var peripheralID: String?
    var name: String
    var model: MachineModel
    var isDemo: Bool
    var addedAt: Date
    var lastSeen: Date?
    var lastConnected: Date?
    var pendingName: String?
    var versions: MachineVersions
    var radioBoardVersion: String
    var versionsReadAt: Date?
    var imageSlots: ImageSlots
    var flavorArt: FlavorArt
    var picturesReadAt: Date?
    var config: PrototypeConfig
    var configReadAt: Date?
    var prototypeVersions: PrototypeVersions
    var usage: UsageReading

    init(_ m: KnownMachine) {
        id = m.id
        key = m.key
        unit = m.unit
        peripheralID = m.peripheralID
        name = m.name
        model = m.model
        isDemo = m.isDemo
        addedAt = m.addedAt
        lastSeen = m.lastSeen
        lastConnected = m.lastConnected
        pendingName = m.pendingName
        versions = m.versions
        radioBoardVersion = m.radioBoardVersion
        versionsReadAt = m.versionsReadAt
        imageSlots = m.imageSlots
        flavorArt = m.flavorArt
        picturesReadAt = m.picturesReadAt
        config = m.config
        configReadAt = m.configReadAt
        prototypeVersions = m.prototypeVersions
        usage = m.usage
    }

    func restore() -> KnownMachine {
        let m = KnownMachine(id: id, key: key, unit: unit, peripheralID: peripheralID,
                             name: name, model: model, isDemo: isDemo, addedAt: addedAt)
        m.lastSeen = lastSeen
        m.lastConnected = lastConnected
        m.pendingName = pendingName
        m.versions = versions
        m.radioBoardVersion = radioBoardVersion
        m.versionsReadAt = versionsReadAt
        m.imageSlots = imageSlots
        m.flavorArt = flavorArt
        m.picturesReadAt = picturesReadAt
        m.config = config
        m.configReadAt = configReadAt
        m.prototypeVersions = prototypeVersions
        m.usage = usage
        m.recomputeCharts()
        m.loadPictures()
        return m
    }
}

private struct DirectoryFile: Encodable {
    var current: String?
    var machines: [MachineRecord]
}

/// One record, or nothing. A record that no longer decodes is skipped rather
/// than taking every other machine on the phone with it.
private struct Skippable<T: Decodable>: Decodable {
    let value: T?
    init(from decoder: Decoder) throws { value = try? T(from: decoder) }
}

private struct DirectoryFileRead: Decodable {
    var current: String?
    var machines: [Skippable<MachineRecord>]
}

/// The later of two moments, either of which may not have come.
private func later(_ a: Date?, _ b: Date?) -> Date? {
    switch (a, b) {
    case (nil, nil): return nil
    case (let x?, nil): return x
    case (nil, let y?): return y
    case (let x?, let y?): return max(x, y)
    }
}

// ── Your machines ───────────────────────────────────────────────────────

/// Every machine this phone knows, and the one it is pointed at. Kept on
/// disk, read at launch, written whenever something about a machine changes.
@Observable
final class MachineDirectory {
    private(set) var known: [KnownMachine] = []
    private(set) var current: KnownMachine?

    @ObservationIgnored private var saveSoon: DispatchWorkItem?

    static var root: URL {
        let support = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        return support.appendingPathComponent("Machines", isDirectory: true)
    }

    private static var file: URL { root.appendingPathComponent("machines.json") }

    init() {
        load()
        sweepOldCaches()
    }

    // ── Finding one ───────────────────────────────────────────────────────

    func machine(matching seen: DiscoveredMachine) -> KnownMachine? {
        known.first { $0.matches(seen) }
    }

    func machine(unit: String) -> KnownMachine? {
        guard !unit.isEmpty else { return nil }
        return known.first { $0.unit == unit }
    }

    var demo: KnownMachine? { known.first { $0.isDemo } }

    /// Whether a sighting is a machine this phone already has.
    func knows(_ seen: DiscoveredMachine) -> Bool { machine(matching: seen) != nil }

    // ── Adding, choosing, forgetting ──────────────────────────────────────

    /// A machine picked out of a scan. One that is already known is handed
    /// back rather than doubled.
    @discardableResult
    func add(_ seen: DiscoveredMachine) -> KnownMachine {
        if let have = machine(matching: seen) {
            have.peripheralID = seen.id
            have.lastSeen = seen.lastSeen
            if !seen.name.isEmpty { have.name = seen.name }
            if seen.model != .unknown { have.model = seen.model }
            save()
            return have
        }
        let m = KnownMachine(key: seen.unit.isEmpty ? seen.id : seen.unit,
                             unit: seen.unit, peripheralID: seen.id,
                             name: seen.name, model: seen.model)
        m.lastSeen = seen.lastSeen
        known.append(m)
        log.info("added \(m.displayName) as \(m.key)")
        save()
        return m
    }

    @discardableResult
    func addDemo() -> KnownMachine {
        if let have = demo { return have }
        let m = KnownMachine(key: "demo", unit: "", peripheralID: nil,
                             name: "", model: .prototype, isDemo: true)
        known.append(m)
        save()
        return m
    }

    func select(_ m: KnownMachine?) {
        current = m
        save()
    }

    /// Gone from the phone, pictures and all. The machine it points at is not
    /// touched. If it was the one the phone was pointed at, the phone points
    /// at whichever known machine it talked to most recently, or at nothing.
    func forget(_ m: KnownMachine) {
        known.removeAll { $0.id == m.id }
        try? FileManager.default.removeItem(at: m.folder)
        if current?.id == m.id {
            current = known.max { ($0.lastConnected ?? .distantPast) < ($1.lastConnected ?? .distantPast) }
        }
        log.info("forgot \(m.displayName)")
        save()
    }

    /// The machine has said who it is. A record keyed by a peripheral id
    /// takes the unit as its key; if another record already carries that
    /// unit — the same machine met through a display that had not yet asked
    /// its main board — the two become one, the older keeping its pictures.
    @discardableResult
    func introduce(_ m: KnownMachine, unit: String, name: String) -> KnownMachine {
        if !name.isEmpty { m.name = name }
        guard !unit.isEmpty, m.unit != unit else { save(); return m }
        if let twin = machine(unit: unit), twin.id != m.id {
            twin.peripheralID = m.peripheralID ?? twin.peripheralID
            if !name.isEmpty { twin.name = name }
            twin.lastSeen = later(m.lastSeen, twin.lastSeen)
            twin.lastConnected = later(m.lastConnected, twin.lastConnected)
            twin.pendingName = m.pendingName ?? twin.pendingName
            known.removeAll { $0.id == m.id }
            try? FileManager.default.removeItem(at: m.folder)
            if current?.id == m.id { current = twin }
            log.info("\(m.key) is \(twin.displayName), unit \(unit)")
            save()
            return twin
        }
        m.unit = unit
        m.key = unit
        log.info("\(m.displayName) is unit \(unit)")
        save()
        return m
    }

    // ── On disk ───────────────────────────────────────────────────────────

    func load() {
        guard let data = try? Data(contentsOf: Self.file) else { return }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        guard let file = try? decoder.decode(DirectoryFileRead.self, from: data) else {
            log.error("machines.json did not decode")
            return
        }
        known = file.machines.compactMap { $0.value?.restore() }
        current = known.first { $0.id == file.current }
        log.info("\(self.known.count) machine(s) known")
    }

    /// Written now. Cheap: a few records and no pictures.
    func save() {
        saveSoon?.cancel()
        saveSoon = nil
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let file = DirectoryFile(current: current?.id, machines: known.map(MachineRecord.init))
        do {
            try FileManager.default.createDirectory(at: Self.root, withIntermediateDirectories: true)
            try encoder.encode(file).write(to: Self.file, options: .atomic)
        } catch {
            log.error("machines.json did not write: \(error.localizedDescription)")
        }
    }

    /// Written soon. For readings that arrive many times a second.
    func touch() {
        guard saveSoon == nil else { return }
        let work = DispatchWorkItem { [weak self] in self?.save() }
        saveSoon = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 1, execute: work)
    }

    /// Pictures an earlier build of this app kept under Caches, where the
    /// system could drop them. They live beside their record now.
    private func sweepOldCaches() {
        let fm = FileManager.default
        let caches = fm.urls(for: .cachesDirectory, in: .userDomainMask)[0]
        try? fm.removeItem(at: caches.appendingPathComponent("images"))
        if let names = try? fm.contentsOfDirectory(atPath: caches.path) {
            for n in names where n.hasPrefix("face-") && n.hasSuffix(".png") {
                try? fm.removeItem(at: caches.appendingPathComponent(n))
            }
        }
    }
}
