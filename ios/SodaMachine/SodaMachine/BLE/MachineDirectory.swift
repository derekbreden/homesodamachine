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
//
// WHICH MACHINES ARE ON THE PHONE IS THE SYSTEM'S TO SAY. The system hands
// this app one machine at a time and lists each in Settings (MachineAccess),
// by the peripheral id the radio had when it was handed over. A record keeps
// that id beside its key, and keeps it when the machine is later found on a
// radio of another id: it is how the system's list and this one line up.
// ────────────────────────────────────────────────────────────

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
    var displayName: String { name.isEmpty ? "Soda machine" : name }
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

    /// The peripheral id the system lists this machine under, once it has
    /// handed the machine to this app: added through its sheet, or carried
    /// over from an earlier build. Nil for the demo, and for a machine an
    /// earlier build added that has not been carried over.
    var accessoryID: String?
    /// What the system calls the machine — the name Settings shows — as this
    /// phone last saw it. A change there is a name someone gave there.
    var accessoryName: String?

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

    // What the appliance last said through the bridge, each reading with the
    // moment it was read (MachineBridge.swift).
    var appliance = ApplianceState()

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
        return isDemo ? "Demo" : "Soda machine"
    }

    /// What kind of machine, for a list with more than one kind on it.
    var kind: String { isDemo ? "Demo" : model.label }

    /// A machine this app opens: the demo, or one that says it is an
    /// appliance. A machine whose advertisement carries no model byte runs
    /// the prototype's firmware.
    var supported: Bool { isDemo || model == .appliance }

    /// Where this record's pictures live.
    var folder: URL { MachineDirectory.root.appendingPathComponent(id, isDirectory: true) }

    /// Whether a sighting is this machine: the unit settles it when both sides
    /// have one, and the peripheral id stands in until the machine has said.
    func matches(_ seen: DiscoveredMachine) -> Bool {
        if !unit.isEmpty && !seen.unit.isEmpty { return unit == seen.unit }
        return peripheralID == seen.id
    }

    // ── Pictures on disk ──────────────────────────────────────────────────
    // A face is filed under the crc32 of the picture it belongs to, so a
    // picture that moves slots keeps its face and a slot that changes hands
    // does not inherit the old one.

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
    var accessoryID: String?
    var accessoryName: String?
    var versions: MachineVersions
    var radioBoardVersion: String
    var versionsReadAt: Date?
    var imageSlots: ImageSlots
    var flavorArt: FlavorArt
    var picturesReadAt: Date?
    var appliance: ApplianceState?

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
        accessoryID = m.accessoryID
        accessoryName = m.accessoryName
        versions = m.versions
        radioBoardVersion = m.radioBoardVersion
        versionsReadAt = m.versionsReadAt
        imageSlots = m.imageSlots
        flavorArt = m.flavorArt
        picturesReadAt = m.picturesReadAt
        appliance = m.appliance
    }

    func restore() -> KnownMachine {
        let m = KnownMachine(id: id, key: key, unit: unit, peripheralID: peripheralID,
                             name: name, model: model, isDemo: isDemo, addedAt: addedAt)
        m.lastSeen = lastSeen
        m.lastConnected = lastConnected
        m.pendingName = pendingName
        m.accessoryID = accessoryID
        m.accessoryName = accessoryName
        m.versions = versions
        m.radioBoardVersion = radioBoardVersion
        m.versionsReadAt = versionsReadAt
        m.imageSlots = imageSlots
        m.flavorArt = flavorArt
        m.picturesReadAt = picturesReadAt
        m.appliance = appliance ?? ApplianceState()
        m.loadPictures()
        return m
    }
}

private struct DirectoryFile: Encodable {
    var schema = MachineDirectory.schema
    var current: String?
    var machines: [MachineRecord]
    var carriedOver: Bool
}

/// One record, or nothing. A record that no longer decodes is skipped rather
/// than taking every other machine on the phone with it.
private struct Skippable<T: Decodable>: Decodable {
    let value: T?
    init(from decoder: Decoder) throws { value = try? T(from: decoder) }
}

private struct DirectoryFileRead: Decodable {
    var schema: Int?
    var current: String?
    var machines: [Skippable<MachineRecord>]
    var carriedOver: Bool?
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

    /// The machines an earlier build added have been offered to the system,
    /// which happens once. One the system did not take stays reachable on
    /// whatever Bluetooth access that build was given, and is added through
    /// the system's sheet like any other.
    @ObservationIgnored var carriedOver = false

    @ObservationIgnored private var saveSoon: DispatchWorkItem?

    /// What the file on disk is written as. A file without the field is 1,
    /// whose demo is a prototype.
    static let schema = 2

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

    func machine(peripheralID: String) -> KnownMachine? {
        known.first { $0.peripheralID == peripheralID }
    }

    /// The machine the system lists under this peripheral id.
    func machine(accessoryID: String) -> KnownMachine? {
        known.first { $0.accessoryID == accessoryID }
    }

    // ── Adding, choosing, forgetting ──────────────────────────────────────

    /// A machine the system handed over, by the peripheral id it came with.
    /// One this phone already reaches by that id is handed back rather than
    /// doubled. A new one is keyed by the id until it says its unit, when
    /// `introduce` folds it into any record that unit already has.
    ///
    /// IT IS AN APPLIANCE UNTIL IT SAYS OTHERWISE. The sheet hands over a
    /// peripheral id and no advertisement, and the page a machine gets depends
    /// on its kind. Every main board built from this repository says
    /// appliance, and a sighting whose advertisement names another kind
    /// corrects it.
    @discardableResult
    func add(peripheralID: String) -> KnownMachine {
        if let have = machine(peripheralID: peripheralID) { return have }
        let m = KnownMachine(key: peripheralID, unit: "", peripheralID: peripheralID,
                             name: "", model: .appliance)
        known.append(m)
        log.info("added \(m.displayName) as \(m.key)")
        save()
        return m
    }

    @discardableResult
    func addDemo() -> KnownMachine {
        if let have = demo { return have }
        let m = KnownMachine(key: "demo", unit: "", peripheralID: nil,
                             name: "", model: .appliance, isDemo: true)
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
    /// at nothing until a person chooses (Management.swift).
    func forget(_ m: KnownMachine) {
        let after = afterRemoving(m.id, current: current?.id, remaining: known.map(\.id))
        known.removeAll { $0.id == m.id }
        try? FileManager.default.removeItem(at: m.folder)
        if case .keep = after {} else { current = nil }
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
            // The system's listing goes with the record that is kept: a
            // machine handed over again is the newer listing.
            if let listed = m.accessoryID {
                twin.accessoryID = listed
                twin.accessoryName = m.accessoryName
            }
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
        carriedOver = file.carriedOver ?? false
        log.info("\(self.known.count) machine(s) known")
        if (file.schema ?? 1) < Self.schema { migrate(from: file.schema ?? 1) }
    }

    /// 1 to 2: the demo becomes an appliance, keeping its place in the list
    /// and its name, and is seeded with sample state when it next opens. Every
    /// other record keeps its model.
    private func migrate(from schema: Int) {
        if schema < 2 {
            for m in known where m.isDemo { m.model = .appliance }
        }
        log.info("machines.json migrated from schema \(schema)")
        save()
    }

    /// Written now. Cheap: a few records and no pictures.
    func save() {
        saveSoon?.cancel()
        saveSoon = nil
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let file = DirectoryFile(current: current?.id, machines: known.map(MachineRecord.init),
                                 carriedOver: carriedOver)
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
