import Foundation

// ────────────────────────────────────────────────────────────
// Reading the machine's record through the bridge.
//
// The main board answers for one entry at a time, by its number, and says
// with each what number its next entry will be given (proto_msg.h,
// MSG_LOG_READ). The faucet carries the question only for a device the
// machine trusts, so asking is never what raises a Trust request: the page
// offers that itself.
// ────────────────────────────────────────────────────────────

extension BLEManager {
    /// Questions in the air at once. The faucet holds a few more than this.
    private static let historyAtOnce = 4

    /// One entry by its number, or the newest for zero, and the number the
    /// machine will give its next. A nil entry is one the machine does not
    /// hold.
    func readHistoryEntry(_ seq: UInt32) async -> Result<(entry: HistoryEntry?, next: UInt32), BridgeError> {
        switch await request(MachineMessage.historyRead, withUnsafeBytes(of: seq.littleEndian, Array.init)) {
        case .failure(let failure):
            return .failure(failure)
        case .success(let answer):
            let b = [UInt8](answer.body)
            guard answer.type == MachineMessage.historyEntry, b.count >= 8 + HistoryEntry.wireBytes else {
                return .failure(.refused)
            }
            func u32(_ o: Int) -> UInt32 { UInt32(b[o]) | UInt32(b[o + 1]) << 8 | UInt32(b[o + 2]) << 16 | UInt32(b[o + 3]) << 24 }
            let entry = u32(0) == 0 ? nil : HistoryEntry(wire: Array(b[8..<(8 + HistoryEntry.wireBytes)]))
            return .success((entry, u32(4)))
        }
    }

    /// The entries with these numbers, in the order asked, a few at a time.
    /// It stops at the first the machine does not hold, and at a failure.
    private func readHistory(_ seqs: [UInt32]) async -> (entries: [HistoryEntry], failure: BridgeError?) {
        var entries: [HistoryEntry] = []
        var start = 0
        while start < seqs.count {
            let group = Array(seqs[start..<min(start + Self.historyAtOnce, seqs.count)])
            let answers = await withTaskGroup(of: (Int, Result<(entry: HistoryEntry?, next: UInt32), BridgeError>).self) { tasks in
                for (index, seq) in group.enumerated() {
                    tasks.addTask { (index, await self.readHistoryEntry(seq)) }
                }
                var collected = Array<Result<(entry: HistoryEntry?, next: UInt32), BridgeError>?>(repeating: nil, count: group.count)
                for await (index, answer) in tasks { collected[index] = answer }
                return collected
            }
            for answer in answers {
                switch answer {
                case .success(let read):
                    guard let entry = read.entry else { return (entries, nil) }
                    entries.append(entry)
                case .failure(let failure):
                    return (entries, failure)
                case nil:
                    return (entries, .noAnswer)
                }
            }
            start += group.count
        }
        return (entries, nil)
    }

    /// Read whatever is newer than what this machine's history holds. The
    /// failure, when there is one.
    @discardableResult
    func refreshHistory() async -> BridgeError? {
        guard let m = current else { return .offline }
        let machine = m.id
        await readStatus()
        let newest: (entry: HistoryEntry?, next: UInt32)
        switch await readHistoryEntry(0) {
        case .failure(let failure): return failure
        case .success(let read): newest = read
        }
        guard current?.id == machine else { return .offline }

        let plan = m.history.newer(next: newest.next)
        var read: [HistoryEntry] = []
        var failure: BridgeError?
        if let first = newest.entry, plan.ask.first == first.seq {
            let rest = await readHistory(Array(plan.ask.dropFirst()))
            read = [first] + rest.entries
            failure = rest.failure
        } else if !plan.ask.isEmpty {
            (read, failure) = await readHistory(plan.ask)
        }
        guard current?.id == machine else { return .offline }

        var history = m.history
        // Entries that stopped short of what is kept leave a gap, so they
        // stand alone rather than ahead of it.
        let whole = read.count == plan.ask.count
        if failure == nil || !read.isEmpty {
            history.took(newer: read, next: newest.next, keep: plan.keep && whole, at: Date())
            if failure == nil, !whole { history.reachedEnd = true }
        }
        if let first = newest.entry, let status = m.appliance.status, let uptime = status.value.uptimeS {
            history.anchor = HistoryAnchor(boot: first.boot, uptime: uptime, at: status.at)
        }
        if history != m.history { m.history = history }
        return failure
    }

    /// The next older page.
    @discardableResult
    func readEarlierHistory() async -> BridgeError? {
        guard let m = current else { return .offline }
        let machine = m.id
        let ask = m.history.earlier
        guard !ask.isEmpty else { return nil }
        let (read, failure) = await readHistory(ask)
        guard current?.id == machine else { return .offline }
        var history = m.history
        // The kept entries may have grown at the front meanwhile, never at
        // the back, so an older page still joins where it was asked from.
        guard history.entries.last?.seq == ask.first.map({ $0 + 1 }) else { return failure }
        if failure == nil {
            history.took(earlier: read, asked: ask.count)
        } else if !read.isEmpty {
            history.entries += read
        }
        if history != m.history { m.history = history }
        return failure
    }

    /// The demo's record: a few days at a kitchen sink, ending now.
    func demoHistoryAnswer(_ body: [UInt8]) -> Result<BridgeAnswer, BridgeError> {
        guard body.count == 4 else { return .failure(.refused) }
        let asked = UInt32(body[0]) | UInt32(body[1]) << 8 | UInt32(body[2]) << 16 | UInt32(body[3]) << 24
        let entries = Self.demoHistory(now: Date())
        let next = UInt32(entries.count) + 1
        let seq = asked == 0 ? next - 1 : asked
        var answer: [UInt8] = []
        func put32(_ v: UInt32) { answer += [UInt8(v & 0xFF), UInt8(v >> 8 & 0xFF), UInt8(v >> 16 & 0xFF), UInt8(v >> 24)] }
        if seq >= 1, seq < next {
            put32(seq)
            put32(next)
            answer += entries[Int(seq) - 1].wire
        } else {
            put32(0)
            put32(next)
            answer += Array(repeating: 0, count: HistoryEntry.wireBytes)
        }
        return .success(BridgeAnswer(type: MachineMessage.historyEntry, body: Data(answer)))
    }

    /// Oldest first, numbered from one. The same days every time it is asked,
    /// counted back from the start of this hour so a second reading agrees
    /// with the first.
    static func demoHistory(now: Date) -> [HistoryEntry] {
        let calendar = Calendar.current
        let hour = calendar.dateInterval(of: .hour, for: now)?.start ?? now
        // Minutes before this hour, and what happened then.
        typealias Made = (minutesAgo: Int, kind: HistoryEntry.Kind, detail: UInt8, a: UInt32, b: UInt32, d: Int16, e: Int16)
        let plan: [Made] = [
            (4190, .start, 1, 0, 0, 0, 0),
            (4180, .cooling, 1, 1560, 0, 21, -62),
            (4050, .pour, 0x00, 6400, 512, 11, 20),
            (4049, .refill, 0, 38_000, 0, 24, 0),
            (3890, .cooling, 1, 780, 0, 20, -58),
            (3600, .pour, 0x01, 7100, 566, 12, 20),
            (3599, .refill, 0, 41_000, 0, 25, 0),
            (3420, .fill, 0x10, 52_000, 0, 0, 0),
            (3300, .cooling, 1, 810, 0, 20, -60),
            (2990, .pour, 0x00, 5200, 410, 9, 20),
            (2760, .pour, 0x00, 8300, 660, 14, 20),
            (2759, .refill, 0, 44_000, 0, 26, 0),
            (2650, .cooling, 1, 900, 0, 20, -61),
            (2310, .pour, 0x01, 6100, 487, 10, 20),
            (2130, .clean, 0x01, 6, 0, 0, 0),
            (2005, .prime, 0x21, 9000, 0, 0, 0),
            (1890, .cooling, 1, 760, 0, 20, -57),
            (1650, .pour, 0x00, 6900, 548, 12, 20),
            (1649, .refill, 0, 39_000, 0, 24, 0),
            (1480, .pour, 0x00, 5600, 447, 10, 20),
            (1200, .cooling, 1, 840, 0, 20, -60),
            (735, .pour, 0x01, 7400, 590, 13, 20),
            (734, .refill, 0, 43_000, 0, 25, 0),
            (560, .cooling, 1, 790, 0, 20, -59),
            (395, .pour, 0x00, 6200, 494, 11, 20),
            (250, .pour, 0x00, 5900, 470, 10, 20),
            (249, .refill, 0, 40_000, 0, 24, 0),
            (140, .cooling, 1, 820, 0, 20, -60),
            (35, .pour, 0x01, 6600, 526, 11, 20),
        ]
        var utc = Calendar(identifier: .gregorian)
        utc.timeZone = TimeZone(identifier: "UTC")!
        let started = hour.addingTimeInterval(-TimeInterval(plan[0].minutesAgo * 60))
        return plan.enumerated().map { index, made in
            let when = hour.addingTimeInterval(-TimeInterval(made.minutesAgo * 60))
            // The machine's clock counts wall time, so the demo's does too.
            let parts = calendar.dateComponents([.year, .month, .day, .hour, .minute, .second], from: when)
            let wall = utc.date(from: parts) ?? when
            let clock = UInt32(max(0, wall.timeIntervalSinceReferenceDate + 366 * 24 * 3600))
            return HistoryEntry(seq: UInt32(index + 1), uptime: UInt32(max(0, when.timeIntervalSince(started))),
                                clock: clock, boot: 1, kind: made.kind, detail: made.detail,
                                a: made.a, b: made.b, d: made.d, e: made.e)
        }
    }
}
