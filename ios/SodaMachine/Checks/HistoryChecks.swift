import Foundation

/// Manual checks against the app's actual history model. The entries are bytes
/// the firmware's own encoder wrote (firmware/lib/machine_log), so the two
/// ends are held to one layout.
@MainActor
func runHistoryChecks(_ check: (Bool, String) -> Void) {
    func bytes(_ hex: String) -> [UInt8] {
        var out: [UInt8] = []
        var rest = Substring(hex)
        while rest.count >= 2 {
            out.append(UInt8(rest.prefix(2), radix: 16) ?? 0)
            rest = rest.dropFirst(2)
        }
        return out
    }
    let plain: (Double) -> String = { String(format: "%.1f", $0) }

    // 41 3 312 2026-11-12T19:04:11 pour ch=B end=flow-stopped ms=5230 pulses=412 bursts=9 ratio=20
    let pourWire = bytes("29000000380100002bca8832030002016e1400009c010000090014007392e2e3")
    // 42 3 4000 - compressor into=off ran_s=840 tank=1.2 coil_min=-7.5
    let coolingWire = bytes("2a000000a00f0000000000000300040148030000000000000c00b5ffa8597dc1")
    // 43 3 5000 - refill end=timeout pumped_ms=180000 tank=--
    let refillWire = bytes("2b00000088130000000000000300030320bf02000000000000800000c42a7c88")

    let pour = HistoryEntry(wire: pourWire)
    check(pour?.seq == 41 && pour?.uptime == 312 && pour?.boot == 3 && pour?.kind == .pour
          && pour?.low == 1 && pour?.ending == 0 && pour?.a == 5230 && pour?.b == 412
          && pour?.d == 9 && pour?.e == 20,
          "A pour the firmware encoded reads back field for field")
    check(pour?.wire == pourWire, "An entry encodes to the bytes the firmware wrote")
    check(pour?.title == "Poured Flavor 2" && pour?.note(temperature: plain) == "5 s" && pour?.isPour == true
          && pour?.needsAttention == false,
          "A pour says which flavor and for how long")

    var damaged = pourWire
    damaged[17] ^= 0x04
    check(HistoryEntry(wire: damaged) == nil, "A damaged entry is not an entry")
    check(HistoryEntry(wire: Array(pourWire.dropLast())) == nil, "A short entry is not an entry")
    var unknown = HistoryEntry(seq: 9, kind: .update).wire
    unknown[14] = 0x7F
    check(HistoryEntry(wire: unknown) == nil, "A kind this app does not know is not shown as something else")

    let cooling = HistoryEntry(wire: coolingWire)
    check(cooling?.kind == .cooling && cooling?.title == "Cooled for 14 min"
          && cooling?.note(temperature: plain) == "Tank 1.2 · coldest coil -7.5",
          "A compressor run says how long it ran and how cold it got")

    let refill = HistoryEntry(wire: refillWire)
    check(refill?.kind == .refill && refill?.title == "Refill stopped" && refill?.needsAttention == true
          && refill?.note(temperature: plain)?.contains("Check the water supply") == true,
          "A refill that gave up says so and points at the water supply")

    check(HistoryEntry(seq: 1, kind: .gas, detail: 1).needsAttention
          && !HistoryEntry(seq: 2, kind: .gas, detail: 0).needsAttention
          && HistoryEntry(seq: 3, kind: .start, detail: 4).needsAttention
          && !HistoryEntry(seq: 4, kind: .start, detail: 1).needsAttention
          && HistoryEntry(seq: 5, kind: .update, detail: 0).needsAttention
          && !HistoryEntry(seq: 6, kind: .cooling, detail: 1, a: 600).needsAttention,
          "Only what a person should act on asks for attention")

    check(HistoryEntry.spoken(seconds: 8) == "8 s" && HistoryEntry.spoken(seconds: 80) == "1 min 20 s"
          && HistoryEntry.spoken(seconds: 120) == "2 min" && HistoryEntry.spoken(seconds: 840) == "14 min"
          && HistoryEntry.spoken(seconds: 7500) == "2 h 5 min" && HistoryEntry.spoken(seconds: 7200) == "2 h",
          "A length reads the way a person says it")

    // ── When it happened ─────────────────────────────────────────────────
    var chicago = Calendar(identifier: .gregorian)
    chicago.timeZone = TimeZone(identifier: "America/Chicago")!
    let when = pour?.date(in: chicago, anchor: nil)
    let parts = when.map { chicago.dateComponents([.year, .month, .day, .hour, .minute, .second], from: $0) }
    check(parts?.year == 2026 && parts?.month == 11 && parts?.day == 12 && parts?.hour == 19
          && parts?.minute == 4 && parts?.second == 11,
          "The machine's clock is read as the wall time it was set to")

    let read = Date(timeIntervalSinceReferenceDate: 800_000_000)
    let anchor = HistoryAnchor(boot: 3, uptime: 4600, at: read)
    check(cooling?.date(in: chicago, anchor: anchor) == read.addingTimeInterval(-600),
          "Without a clock, an entry of the running start is dated back from the machine's uptime")
    check(cooling?.date(in: chicago, anchor: HistoryAnchor(boot: 4, uptime: 4600, at: read)) == nil
          && cooling?.date(in: chicago, anchor: nil) == nil
          && cooling?.date(in: chicago, anchor: HistoryAnchor(boot: 3, uptime: 100, at: read)) == nil,
          "An entry of another start, or one nothing dates, has no time rather than a guessed one")

    // ── What to ask for ──────────────────────────────────────────────────
    func entries(_ seqs: [UInt32]) -> [HistoryEntry] { seqs.map { HistoryEntry(seq: $0, kind: .pour) } }
    let page = UInt32(MachineHistory.page)

    var history = MachineHistory()
    check(history.newer(next: 1).ask.isEmpty && history.newer(next: 0).ask.isEmpty,
          "An empty record asks for nothing")
    var plan = history.newer(next: 100)
    check(plan.ask == Array(((100 - page)...99).reversed()) && !plan.keep,
          "A first reading asks for the newest page, newest first")
    plan = history.newer(next: 4)
    check(plan.ask == [3, 2, 1] && !plan.keep, "A short record is asked for whole")

    history.took(newer: entries(plan.ask), next: 4, keep: plan.keep, at: read)
    check(history.entries.map(\.seq) == [3, 2, 1] && history.nextSeq == 4 && history.reachedEnd
          && history.earlier.isEmpty,
          "Reading down to the first entry is the end of the record")

    history = MachineHistory()
    history.took(newer: entries(Array((60...99).reversed())), next: 100, keep: false, at: read)
    check(!history.reachedEnd && history.earlier == Array(((60 - page)...59).reversed()),
          "An older page continues below what is kept")
    plan = history.newer(next: 100)
    check(plan.ask.isEmpty && plan.keep, "Nothing new asks for nothing")
    plan = history.newer(next: 104)
    check(plan.ask == [103, 102, 101, 100] && plan.keep, "A few new entries are asked for alone")
    history.took(newer: entries(plan.ask), next: 104, keep: plan.keep, at: read)
    check(history.entries.first?.seq == 103 && history.entries.count == 44 && history.entries.last?.seq == 60,
          "New entries go ahead of what is kept")
    plan = history.newer(next: 104 + page + 5)
    check(!plan.keep && plan.ask.count == Int(page) && plan.ask.first == 104 + page + 4,
          "A gap wider than a page starts over from the newest page")
    plan = history.newer(next: 50)
    check(!plan.keep && plan.ask.first == 49,
          "A machine whose record starts again is read from its newest entry")

    history = MachineHistory()
    history.took(newer: entries([12, 11, 10]), next: 13, keep: false, at: read)
    history.took(earlier: entries([9, 8]), asked: 9)
    check(history.entries.map(\.seq) == [12, 11, 10, 9, 8] && history.reachedEnd,
          "Fewer entries than asked for is everything the machine has kept")

    // ── How much it poured ───────────────────────────────────────────────
    func clock(_ year: Int, _ month: Int, _ day: Int, _ hour: Int) -> UInt32 {
        var utc = Calendar(identifier: .gregorian)
        utc.timeZone = TimeZone(identifier: "UTC")!
        let date = utc.date(from: DateComponents(year: year, month: month, day: day, hour: hour))!
        return UInt32(date.timeIntervalSinceReferenceDate + 366 * 24 * 3600)
    }
    history = MachineHistory()
    history.entries = [
        HistoryEntry(seq: 9, clock: clock(2026, 11, 12, 18), kind: .pour, detail: 0x00),
        HistoryEntry(seq: 8, clock: clock(2026, 11, 12, 9), kind: .pour, detail: 0x31),
        HistoryEntry(seq: 7, clock: clock(2026, 11, 12, 8), kind: .pour, detail: 0x10),
        HistoryEntry(seq: 6, clock: clock(2026, 11, 12, 7), kind: .refill),
        HistoryEntry(seq: 5, clock: clock(2026, 11, 11, 23), kind: .pour),
        HistoryEntry(seq: 4, clock: clock(2026, 11, 6, 12), kind: .pour),
        HistoryEntry(seq: 3, clock: clock(2026, 11, 5, 12), kind: .pour),
        HistoryEntry(seq: 2, clock: 0, kind: .pour),
    ]
    let now = chicago.date(from: DateComponents(year: 2026, month: 11, day: 12, hour: 20))!
    check(history.pours(days: 7, now: now, calendar: chicago) == [1, 0, 0, 0, 0, 1, 2],
          "Pours are counted on the day they happened; a cut-off pour and an undated one are not counted")
}
