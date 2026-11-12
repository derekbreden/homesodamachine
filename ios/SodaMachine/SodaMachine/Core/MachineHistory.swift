import Foundation

// ────────────────────────────────────────────────────────────
// What the machine did, read from its own record.
//
// The main board notes every pour, refill, compressor run, cycle, fault and
// start as it ends (firmware/lib/machine_log). A device the machine trusts
// reads those entries one at a time, newest first, and keeps what it has
// read for as long as the app runs.
// ────────────────────────────────────────────────────────────

/// One entry, as machine_log::encode() lays it out on the wire.
struct HistoryEntry: Codable, Equatable, Identifiable {
    /// machine_log::Kind.
    enum Kind: UInt8, Codable {
        case start = 1, pour, refill, cooling, coldTrouble, gas, fill, clean, air, prime, update, valves
    }

    static let wireBytes = 32

    var seq: UInt32
    /// Seconds since the start the entry was made in.
    var uptime: UInt32
    /// The machine's own clock, in seconds since its epoch; zero when it had none.
    var clock: UInt32
    /// Which start of the record it belongs to.
    var boot: UInt16
    var kind: Kind
    var detail: UInt8
    var a: UInt32
    var b: UInt32
    var d: Int16
    var e: Int16

    var id: UInt32 { seq }

    init(seq: UInt32, uptime: UInt32 = 0, clock: UInt32 = 0, boot: UInt16 = 1, kind: Kind,
         detail: UInt8 = 0, a: UInt32 = 0, b: UInt32 = 0, d: Int16 = 0, e: Int16 = 0) {
        self.seq = seq
        self.uptime = uptime
        self.clock = clock
        self.boot = boot
        self.kind = kind
        self.detail = detail
        self.a = a
        self.b = b
        self.d = d
        self.e = e
    }

    /// Nil for anything that is not a whole entry: the wrong length, a check
    /// that does not match, or a kind this app does not know.
    init?(wire: [UInt8]) {
        guard wire.count == Self.wireBytes else { return nil }
        let body = Array(wire[0..<28])
        guard Self.u32(wire, 28) == Self.crc32(body), let kind = Kind(rawValue: wire[14]) else { return nil }
        seq = Self.u32(wire, 0)
        uptime = Self.u32(wire, 4)
        clock = Self.u32(wire, 8)
        boot = UInt16(wire[12]) | UInt16(wire[13]) << 8
        self.kind = kind
        detail = wire[15]
        a = Self.u32(wire, 16)
        b = Self.u32(wire, 20)
        d = Int16(bitPattern: UInt16(wire[24]) | UInt16(wire[25]) << 8)
        e = Int16(bitPattern: UInt16(wire[26]) | UInt16(wire[27]) << 8)
    }

    var wire: [UInt8] {
        var out: [UInt8] = []
        func put32(_ v: UInt32) { out += [UInt8(v & 0xFF), UInt8(v >> 8 & 0xFF), UInt8(v >> 16 & 0xFF), UInt8(v >> 24)] }
        func put16(_ v: UInt16) { out += [UInt8(v & 0xFF), UInt8(v >> 8)] }
        put32(seq)
        put32(uptime)
        put32(clock)
        put16(boot)
        out += [kind.rawValue, detail]
        put32(a)
        put32(b)
        put16(UInt16(bitPattern: d))
        put16(UInt16(bitPattern: e))
        put32(Self.crc32(out))
        return out
    }

    private static func u32(_ b: [UInt8], _ o: Int) -> UInt32 {
        UInt32(b[o]) | UInt32(b[o + 1]) << 8 | UInt32(b[o + 2]) << 16 | UInt32(b[o + 3]) << 24
    }

    static func crc32(_ bytes: [UInt8]) -> UInt32 {
        var crc: UInt32 = 0xFFFF_FFFF
        for byte in bytes {
            crc ^= UInt32(byte)
            for _ in 0..<8 { crc = (crc >> 1) ^ (0xEDB8_8320 & (0 &- (crc & 1))) }
        }
        return ~crc
    }
}

// ── What an entry says ───────────────────────────────────────────────────

extension HistoryEntry {
    /// A reading the entry does not have (machine_log::kNoTemp).
    static let noTemperature = Int16.min

    /// The low half of `detail`: a channel, or a mode.
    var low: Int { Int(detail & 0x0F) }
    /// The high half: how it ended.
    var ending: Int { Int(detail >> 4) }
    var flavor: String { "Flavor \(low + 1)" }

    var isPour: Bool { kind == .pour && (ending == 0 || ending == 3) }

    /// What happened, the way a person would say it.
    var title: String {
        switch kind {
        case .start:
            return "Machine started"
        case .pour:
            switch ending {
            case 0, 3: return "Poured \(flavor)"
            case 1: return "Pour cut off"
            case 2: return "Pour stopped by the gas alarm"
            default: return "\(flavor) could not pour"
            }
        case .refill:
            switch Int(detail) {
            case 0: return "Refilled with water"
            case 1, 2: return "Refill paused"
            case 3: return "Refill stopped"
            case 4: return "Refill stopped at the machine"
            default: return "Refill could not start"
            }
        case .cooling:
            return "Cooled for \(Self.spoken(seconds: Int(a)))"
        case .coldTrouble:
            switch Int(detail) {
            case 0: return "Cooling lost its temperature readings"
            case 4: return "Cooling paused to prevent freezing"
            default: return "Cooling is back to normal"
            }
        case .gas:
            return detail != 0 ? "Gas alarm" : "Gas alarm cleared"
        case .fill:
            switch ending {
            case 0, 1: return "Filled \(flavor)"
            case 2: return "Fill stopped"
            default: return "Fill ended early"
            }
        case .clean:
            switch ending {
            case 0: return "Cleaned \(flavor)"
            case 2: return "Clean stopped"
            default: return "Clean ended early"
            }
        case .air:
            let what = low == 0 ? "Dried the flavor lines" : "Emptied a reservoir with air"
            switch ending {
            case 0: return what
            case 2: return low == 0 ? "Drying stopped" : "Emptying stopped"
            default: return low == 0 ? "Drying ended early" : "Emptying ended early"
            }
        case .prime:
            return ending == 7 ? "Prime refused for \(flavor)" : "Primed \(flavor)"
        case .update:
            return detail != 0 ? "Software update kept" : "Software update not confirmed"
        case .valves:
            return detail != 0 ? "Valves stopped answering" : "Valves answering again"
        }
    }

    /// What else is worth saying; nil when the title is the whole of it.
    /// Temperatures are worded by the caller, in the device's own unit.
    func note(temperature: (Double) -> String) -> String? {
        switch kind {
        case .start:
            switch Int(detail) {
            case 1: return "Power came on"
            case 3: return "Restarted itself"
            case 9: return "Restarted after a dip in power"
            case 4, 5, 6, 7: return "Restarted after a fault"
            default: return nil
            }
        case .pour:
            let length = Self.spoken(seconds: Int((a + 500) / 1000))
            switch ending {
            case 0: return length
            case 1: return "The flow meter never stopped, after \(length)"
            case 2: return "After \(length)"
            case 3: return "\(length), stopped at the machine"
            case 4: return "The flavor pump would not start"
            default: return "Its valves could not be opened"
            }
        case .refill:
            let length = Self.spoken(seconds: Int((a + 500) / 1000))
            switch Int(detail) {
            case 0: return "\(length) of pumping"
            case 1: return "Something else needed the valves"
            case 2: return "A pour came first"
            case 3: return "No water reached the tank in \(length). Check the water supply, then touch either display to try again."
            case 4: return nil
            default: return "Its valve could not be opened"
            }
        case .cooling:
            var parts: [String] = []
            if d != Self.noTemperature { parts.append("Tank \(temperature(Double(d) / 10))") }
            if e != Self.noTemperature { parts.append("coldest coil \(temperature(Double(e) / 10))") }
            if Int(detail) == 4 { parts.append("stopped to prevent freezing") }
            return parts.isEmpty ? nil : parts.joined(separator: " · ")
        case .coldTrouble:
            return a > 1 ? "Changed \(a) times" : nil
        case .gas:
            return a > 1 ? "Changed \(a) times" : (detail != 0 ? "Check the machine" : nil)
        case .fill:
            let length = Self.spoken(seconds: Int((a + 500) / 1000))
            switch ending {
            case 0: return length
            case 1: return "\(length), until the reservoir was full"
            case 2: return "After \(length)"
            case 3: return "A valve or a level sensor did not answer"
            case 4: return "The gas alarm"
            default: return nil
            }
        case .clean, .air:
            switch ending {
            case 0, 2: return nil
            case 3: return "A valve or a level sensor did not answer"
            case 4: return "The gas alarm"
            default: return nil
            }
        case .prime:
            let length = Self.spoken(seconds: Int((a + 500) / 1000))
            switch ending {
            case 5: return "\(length), until the hold stopped arriving"
            case 6: return "\(length), to its limit"
            case 7: return nil
            default: return length
            }
        case .update:
            return nil
        case .valves:
            return detail != 0 ? "Flavor, refills and cooling wait until they answer" : nil
        }
    }

    /// Something a person should act on.
    var needsAttention: Bool {
        switch kind {
        case .gas: return detail != 0
        case .refill: return Int(detail) == 3 || Int(detail) == 5
        case .coldTrouble: return Int(detail) == 0 || Int(detail) == 4
        case .pour: return ending == 1 || ending >= 4
        case .fill, .clean, .air: return ending == 3
        case .update: return detail == 0
        case .start: return [4, 5, 6, 7].contains(Int(detail))
        case .valves: return detail != 0
        case .cooling, .prime: return false
        }
    }

    /// An SF Symbol for the row.
    var symbol: String {
        switch kind {
        case .start: "power"
        case .pour: "drop.fill"
        case .refill: "drop"
        case .cooling, .coldTrouble: "snowflake"
        case .gas: "exclamationmark.triangle.fill"
        case .fill: "arrow.down.to.line"
        case .clean: "sparkles"
        case .air: "wind"
        case .prime: "hand.tap"
        case .update: "arrow.down.circle"
        case .valves: "cable.connector"
        }
    }

    /// "8 s", "1 min 20 s", "14 min", "2 h 5 min".
    static func spoken(seconds: Int) -> String {
        let s = max(0, seconds)
        if s < 60 { return "\(s) s" }
        if s < 600 { return s % 60 == 0 ? "\(s / 60) min" : "\(s / 60) min \(s % 60) s" }
        if s < 3600 { return "\((s + 30) / 60) min" }
        let minutes = (s + 30) / 60
        return minutes % 60 == 0 ? "\(minutes / 60) h" : "\(minutes / 60) h \(minutes % 60) min"
    }
}

// ── When it happened ─────────────────────────────────────────────────────

/// How long this start of the machine had been running when a status was
/// read, which dates the entries of that start when the machine has no clock.
struct HistoryAnchor: Codable, Equatable {
    var boot: UInt16
    var uptime: UInt32
    var at: Date
}

extension HistoryEntry {
    /// The machine's epoch (machine_log::kClockYear) against Foundation's
    /// reference date: one leap year earlier.
    private static let epochBeforeReference: TimeInterval = 366 * 24 * 3600

    /// When it happened: by the machine's own clock when it had one, read as
    /// the wall time it is; otherwise worked back from the anchor, for an
    /// entry of the same start. Nil when neither says.
    func date(in calendar: Calendar, anchor: HistoryAnchor?) -> Date? {
        if clock != 0 {
            var utc = Calendar(identifier: .gregorian)
            utc.timeZone = TimeZone(identifier: "UTC")!
            let wall = Date(timeIntervalSinceReferenceDate: TimeInterval(clock) - Self.epochBeforeReference)
            let parts = utc.dateComponents([.year, .month, .day, .hour, .minute, .second], from: wall)
            return calendar.date(from: parts)
        }
        guard let anchor, anchor.boot == boot, anchor.uptime >= uptime else { return nil }
        return anchor.at.addingTimeInterval(-TimeInterval(anchor.uptime - uptime))
    }
}

// ── What has been read ───────────────────────────────────────────────────

struct MachineHistory: Equatable {
    /// Newest first, their numbers falling by one.
    var entries: [HistoryEntry] = []
    /// The number the machine will give its next entry, as last read.
    var nextSeq: UInt32 = 0
    var readAt: Date?
    /// The machine holds nothing older than the last entry here.
    var reachedEnd = false
    var anchor: HistoryAnchor?
    /// The oldest number asked for so far. An entry this app cannot read is
    /// stepped over, so the oldest entry kept is not always the oldest asked.
    var askedDownTo: UInt32?

    /// How many entries one reading asks for.
    static let page = 40

    /// The entry numbers to ask for after the machine says its next entry is
    /// `next`: whatever is newer than what is kept, newest first. A gap wider
    /// than a page starts the kept entries over from the newest page.
    func newer(next: UInt32) -> (ask: [UInt32], keep: Bool) {
        guard next > 1 else { return ([], false) }
        let newest = next - 1
        if let kept = entries.first?.seq, kept <= newest, newest - kept <= UInt32(Self.page) {
            return (kept == newest ? [] : Array(((kept + 1)...newest).reversed()), true)
        }
        let oldest = newest >= UInt32(Self.page) ? newest - UInt32(Self.page) + 1 : 1
        return (Array((oldest...newest).reversed()), false)
    }

    /// The numbers of the next older page, newest first, below `below` — the
    /// oldest number already asked for. Empty at the start of the record.
    func earlier(below: UInt32? = nil) -> [UInt32] {
        guard !reachedEnd, let oldest = below ?? entries.last?.seq, oldest > 1 else { return [] }
        let first = oldest - 1
        let last = first >= UInt32(Self.page) ? first - UInt32(Self.page) + 1 : 1
        return Array((last...first).reversed())
    }

    /// Entries just read, newest first, put ahead of what is kept or in its
    /// place.
    mutating func took(newer: [HistoryEntry], next: UInt32, keep: Bool, at: Date) {
        if keep { entries = newer + entries } else { entries = newer; reachedEnd = false; askedDownTo = nil }
        nextSeq = next
        readAt = at
        if next <= 1 || entries.last?.seq == 1 { reachedEnd = true }
    }

    /// An older page just read, and whether the reading ran into an entry
    /// the machine no longer holds.
    mutating func took(earlier: [HistoryEntry], ranOut: Bool) {
        entries += earlier
        if ranOut || entries.last?.seq == 1 { reachedEnd = true }
    }

    /// Pours on each of the last `days` days, today last, for entries whose
    /// time is known.
    func pours(days: Int, now: Date, calendar: Calendar) -> [Int] {
        var counts = Array(repeating: 0, count: days)
        let today = calendar.startOfDay(for: now)
        for entry in entries where entry.isPour {
            guard let when = entry.date(in: calendar, anchor: anchor) else { continue }
            let back = calendar.dateComponents([.day], from: calendar.startOfDay(for: when), to: today).day ?? -1
            if back >= 0, back < days { counts[days - 1 - back] += 1 }
        }
        return counts
    }
}
