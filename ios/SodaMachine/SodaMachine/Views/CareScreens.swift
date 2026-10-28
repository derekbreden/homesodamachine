import SwiftUI

// ────────────────────────────────────────────────────────────
// Care: Fill, Clean and Prime, one operation at a time on the whole machine.
//
// Each run is the machine's. A page shows the state the machine reports —
// starting, running, stopping, how it ended — and a run this phone started
// holds the app's navigation until it ends, while the phone can hear the
// machine. A run started at the machine shows the same progress here, with
// nothing held. What a page has seen of a run is kept above it (RunLog), so
// leaving and coming back finds it as it was, and a run seen running keeps
// its ending until someone taps Done.
//
// A command that got no answer may have been carried out. Nothing starts
// again until a reading taken after it says what the machine is doing, and
// nothing is ever sent again on the phone's own say.
// ────────────────────────────────────────────────────────────

/// What a run page is doing on this phone's side of it.
enum RunPhase: Equatable {
    case prepare
    case starting
    case running     // this phone started it, and the machine said so
    case stopping
    case ended
}

/// Something that went wrong on a run page, said the way a Notice says it.
struct RunProblem: Equatable {
    let title: String
    let message: String
    var icon = "exclamationmark.circle"
    var urgent = false

    var notice: Notice { Notice(title: title, message: message, icon: icon, urgent: urgent) }
}

/// What this device has seen of each operation, per machine and flavor. A
/// page opens a record; from then on the root applies every reading of that
/// machine to it, whether or not the page is still up, so an ending that comes
/// while someone is elsewhere is kept for them.
@Observable
final class RunLog {
    enum Kind: Hashable { case fill, clean, prime }

    struct Key: Hashable {
        let machine: String
        let kind: Kind
        let channel: Int
    }

    struct Record: Equatable {
        var phase = RunPhase.prepare
        /// This phone started the run, and the machine said so.
        var startedHere = false
        /// This flavor's run has been seen in progress, whoever started it.
        var sawRun = false
        var problem: RunProblem?
        /// A command whose answer never came. Nothing starts again until a
        /// reading newer than this says what the machine did.
        var unsureSince: Date?
        /// How the run ended, as the machine said when it did: kept until Done,
        /// or until a newer run of the flavor takes its place.
        var fillEnded: FillState?
        var cleanEnded: CleanState?
        /// The run ended while this device wasn't hearing it, so how is unknown.
        var endedUnheard = false
        /// The Prime session this page opened or followed.
        var primeToken: UInt32?
    }

    private var records: [Key: Record] = [:]

    subscript(key: Key) -> Record {
        get { records[key] ?? Record() }
        set { records[key] = newValue }
    }

    /// A page shows this operation: its record follows the machine from now on.
    func attend(_ key: Key) {
        if records[key] == nil { records[key] = Record() }
    }

    /// Done: the next visit starts clean.
    func acknowledge(_ key: Key) { records[key] = nil }

    /// A machine removed from this device takes its records with it.
    func forget(machine: String) { records = records.filter { $0.key.machine != machine } }

    /// A run this phone started, or is stopping, on its own page: the app's
    /// navigation waits for it while that page is up and the phone can hear
    /// the machine.
    func minding(_ key: RunLog.Key) -> Bool {
        [.starting, .running, .stopping].contains(self[key].phase)
    }

    /// Operations a page opened on this machine that haven't ended, or whose
    /// start went unanswered. Their state moves only when the machine is
    /// asked, so the root asks, whichever page is up.
    func outstanding(machine: String?) -> Set<Kind> {
        Set(records.filter { key, r in
            key.machine == machine && r.phase != .ended
                && (r.sawRun || r.unsureSince != nil || [.starting, .running, .stopping].contains(r.phase))
        }.map(\.key.kind))
    }

    /// The link went: a stop that was waiting on the machine's word is not
    /// confirmed, and says so rather than spinning.
    func lostLink(machine: String) {
        for (key, r) in records where key.machine == machine && r.phase == .stopping {
            var next = r
            next.phase = r.startedHere ? .running : .prepare
            next.problem = RunProblem(title: "Stop not confirmed",
                                      message: "The phone lost the machine before it said it had stopped. Check the machine display; reconnecting reads what it is doing.")
            records[key] = next
        }
    }

    /// What one reading says about a record following one flavor's run.
    private enum Seen { case runningHere, endedHere, endedUnheard, nothing }

    private static func seen(_ r: Record, channel: Int, running: Bool, runChannel: Int) -> Seen {
        if running && runChannel == channel { return .runningHere }
        guard r.sawRun || r.phase == .running || r.phase == .stopping else { return .nothing }
        // Idle, last run on this flavor: this run's own ending. Anything else —
        // another flavor running, or last run — means this one ended unheard.
        return !running && runChannel == channel ? .endedHere : .endedUnheard
    }

    /// Every reading of a machine, applied to each of its records.
    func observe(machine: String, appliance a: ApplianceState) {
        for (key, old) in records where key.machine == machine {
            var r = old
            switch key.kind {
            case .fill:
                guard let reading = a.fill else { continue }
                if let since = r.unsureSince, reading.at > since { r.unsureSince = nil }
                if r.phase == .ended {
                    // A newer run of this flavor replaces the ending kept for the last one.
                    if reading.value.running && reading.value.channel == key.channel { r = Record(sawRun: true) }
                    break
                }
                switch Self.seen(r, channel: key.channel, running: reading.value.running, runChannel: reading.value.channel) {
                case .runningHere: r.sawRun = true
                case .endedHere: r.phase = .ended; r.fillEnded = reading.value
                case .endedUnheard: r.phase = .ended; r.endedUnheard = true
                case .nothing: break
                }
            case .clean:
                guard let reading = a.clean else { continue }
                if let since = r.unsureSince, reading.at > since { r.unsureSince = nil }
                if r.phase == .ended {
                    if reading.value.running && reading.value.channel == key.channel { r = Record(sawRun: true) }
                    break
                }
                switch Self.seen(r, channel: key.channel, running: reading.value.running, runChannel: reading.value.channel) {
                case .runningHere: r.sawRun = true
                case .endedHere: r.phase = .ended; r.cleanEnded = reading.value
                case .endedUnheard: r.phase = .ended; r.endedUnheard = true
                case .nothing: break
                }
            case .prime:
                guard let reading = a.prime else { continue }
                if let since = r.unsureSince, reading.at > since { r.unsureSince = nil }
                if reading.value.phase != .off, reading.value.channel == key.channel {
                    r.primeToken = reading.value.sessionToken
                }
            }
            if r != old { records[key] = r }
        }
    }
}

extension BridgeError {
    /// Sent, and the machine may have acted on it: nothing came back.
    var mayHaveActed: Bool { self == .noAnswer || self == .offline }
}

// ── Care ────────────────────────────────────────────────────────────────

struct CareHomeView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(\.dynamicTypeSize) private var typeSize
    let width: CGFloat

    var body: some View {
        let count = typeSize.isAccessibilitySize ? 1 : width >= 760 ? 3 : width >= 600 ? 2 : 1
        VStack(alignment: .leading, spacing: 20) {
            MachineNotices()
            RunningCard()
            Note("One operation at a time, on either flavor.")
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 16, alignment: .top), count: count),
                      alignment: .leading, spacing: 16) {
                card("Fill", icon: "arrow.down.to.line", detail: "Add concentrate through the top funnel.") { .fill($0) }
                card("Clean", icon: "sparkles", detail: "Rinse the funnel, reservoir and flavor line.") { .clean($0) }
                card("Prime", icon: "drop", detail: "Bring concentrate to the faucet.") { .prime($0) }
            }
        }
        .task(id: ble.canChange) {
            guard ble.canChange else { return }
            await ble.readFill()
            await ble.readClean()
            await ble.readPrime()
        }
    }

    private func card(_ title: String, icon: String, detail: String, route: @escaping (Int) -> AppRoute) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: icon).font(.title3.weight(.medium))
            Note(detail).frame(minHeight: 34, alignment: .topLeading)
            HStack(spacing: 12) {
                ActionButton(title: "Flavor 1", primary: false) { nav.push(route(0)) }
                    .accessibilityLabel("\(title), Flavor 1")
                ActionButton(title: "Flavor 2", primary: false) { nav.push(route(1)) }
                    .accessibilityLabel("\(title), Flavor 2")
            }
        }
        .padding(16).frame(maxWidth: .infinity, alignment: .topLeading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }
}

/// The operation the machine is running, whoever started it: the first thing
/// on Care, and the way to its page.
struct RunningCard: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav

    var body: some View {
        if let blocker = Blocker.active(ble.appliance) {
            Button { nav.push(blocker.route) } label: {
                HStack(spacing: 12) {
                    Image(systemName: blocker.icon).foregroundStyle(Theme.accent)
                    VStack(alignment: .leading, spacing: 4) {
                        Text(blocker.title).font(.body.weight(.semibold))
                        Text(blocker.action).font(.subheadline).foregroundStyle(Theme.accent)
                    }
                    Spacer()
                    Image(systemName: "chevron.right").font(.caption.weight(.semibold)).foregroundStyle(Theme.textSecondary)
                }
                .padding(16).frame(maxWidth: .infinity, alignment: .leading)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
                .overlay(RoundedRectangle(cornerRadius: 14).strokeBorder(Theme.accent.opacity(0.6), lineWidth: 1))
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityElement(children: .combine)
        }
    }
}

/// An operation holding the machine, and the page that follows it.
struct Blocker: Equatable {
    let kind: RunLog.Kind
    let channel: Int
    let title: String
    let action: String
    let icon: String

    var route: AppRoute {
        switch kind {
        case .fill: .fill(channel)
        case .clean: .clean(channel)
        case .prime: .prime(channel)
        }
    }

    /// Whatever the machine is running, on either flavor.
    static func active(_ a: ApplianceState) -> Blocker? {
        if let f = a.fill?.value, f.running {
            return Blocker(kind: .fill, channel: f.channel, title: "Filling Flavor \(f.channel + 1)",
                           action: "View filling", icon: "arrow.down.to.line")
        }
        if let c = a.clean?.value, c.running {
            return Blocker(kind: .clean, channel: c.channel, title: "Cleaning Flavor \(c.channel + 1)",
                           action: "View cleaning", icon: "sparkles")
        }
        if let p = a.prime?.value, p.phase != .off {
            return Blocker(kind: .prime, channel: p.channel, title: "Prime is open for Flavor \(p.channel + 1)",
                           action: "View Prime", icon: "hand.tap")
        }
        return nil
    }

    /// What stops `kind` starting on `channel`: any other operation, on
    /// either flavor.
    static func against(_ kind: RunLog.Kind, channel: Int, in a: ApplianceState) -> Blocker? {
        guard let b = active(a), b.kind != kind || b.channel != channel else { return nil }
        return b
    }
}

/// Another operation holds the machine: what it is, and the way to it.
struct BlockerNotice: View {
    @Environment(Navigator.self) var nav
    let blocker: Blocker

    var body: some View {
        VStack(spacing: 12) {
            Notice(title: blocker.title,
                   message: "One operation runs at a time. Open it to follow it or stop it.", icon: "hourglass")
            ActionButton(title: blocker.action, primary: false) { nav.push(blocker.route) }
        }
    }
}

/// The flavor a run is for: its face, its name, its reservoir.
struct CareFlavorColumn: View {
    @Environment(BLEManager.self) var ble
    let channel: Int

    var body: some View {
        let art = ble.flavorArt.art.indices.contains(channel) ? ble.flavorArt.art[channel] : channel
        VStack(spacing: 14) {
            FlavorArtView(art: art, height: 200)
            Text("Flavor \(channel + 1)").font(.headline)
            LevelGauge(level: ble.appliance.status?.value.level(channel)).frame(maxWidth: 140)
        }
        .frame(maxWidth: .infinity)
    }
}

/// The big mark at the head of a run.
struct RunHeading: View {
    let icon: String
    let title: String
    let channel: Int

    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: icon).font(.system(size: 52, weight: .light)).foregroundStyle(Theme.accent)
                .accessibilityHidden(true)
            Text(title).font(.title2.weight(.semibold))
            Text("Flavor \(channel + 1)").foregroundStyle(Theme.textSecondary)
        }
        .frame(maxWidth: .infinity).padding(.vertical, 28)
    }
}

private let lostContact = Notice(
    title: "The cycle may still be running",
    message: "The phone cannot confirm its state. Check the machine display. Reconnecting will read its current progress.",
    icon: "antenna.radiowaves.left.and.right.slash")

private func unsure(_ what: String) -> Notice {
    Notice(title: "Checking what the machine did",
           message: "The machine didn’t answer, so \(what) may have started. This page reads the machine before anything starts again.",
           icon: "questionmark.circle")
}

// ── Fill ────────────────────────────────────────────────────────────────

struct FillView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(RunLog.self) var runs
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat
    let entry: RouteEntry

    private var key: RunLog.Key? { ble.current.map { RunLog.Key(machine: $0.id, kind: .fill, channel: channel) } }
    private var record: RunLog.Record { key.map { runs[$0] } ?? RunLog.Record() }
    private var reading: Reading<FillState>? { ble.appliance.fill }
    private var fill: FillState? { reading?.value }
    private var runningHere: Bool { fill?.running == true && fill?.channel == channel }
    private var blocker: Blocker? { Blocker.against(.fill, channel: channel, in: ble.appliance) }

    var body: some View {
        let wide = width >= 650 && !typeSize.isAccessibilitySize
        VStack(alignment: .leading, spacing: 24) {
            if runningHere || record.phase == .stopping {
                if !ble.linked && !ble.demoMode { lostContact }
                FlexibleColumns(wide: wide, spacing: 28) {
                    RunHeading(icon: "arrow.down.to.line", title: "Filling", channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        if record.phase == .stopping {
                            Notice(title: "Stopping filling…",
                                   message: "Waiting for the machine to confirm that the pump and valves are stopped.",
                                   icon: "hourglass")
                        }
                        if let problem = record.problem { problem.notice }
                        Panel {
                            Text("Drawing from the funnel").font(.headline)
                            TimelineView(.periodic(from: .now, by: 1)) { context in
                                let elapsed = elapsedMs(at: context.date)
                                let planned = max(fill?.plannedMs ?? 80_000, 1)
                                VStack(alignment: .leading, spacing: 16) {
                                    ProgressView(value: min(Double(elapsed) / Double(planned), 1)).tint(Theme.accent)
                                    Note("\(elapsed / 1000) s elapsed · up to \(planned / 1000) s")
                                }
                            }
                        }
                        ActionButton(title: "Stop filling", primary: false, working: record.phase == .stopping) { stop() }
                            .disabled(record.phase == .stopping || !ble.canChange)
                        Note("The machine reports progress and confirms when it has stopped.")
                    }
                    .frame(maxWidth: .infinity)
                }
            } else if record.phase == .ended {
                result(record.endedUnheard ? nil : record.fillEnded)
            } else {
                if let blocker { BlockerNotice(blocker: blocker) }
                if record.unsureSince != nil { unsure("filling") }
                if let problem = record.problem { problem.notice }
                FlexibleColumns(wide: wide, spacing: 28) {
                    CareFlavorColumn(channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        Text("Add concentrate").font(.title2.weight(.semibold))
                        Note("Pour concentrate into the top funnel.")
                        Panel {
                            Label("Stops when full", systemImage: "drop.fill").font(.body.weight(.medium))
                            Note("Filling also ends when the planned run finishes. Concentrate may remain in the funnel if the reservoir fills first.")
                        }
                        ActionButton(title: "Start filling", working: record.phase == .starting) { start() }
                            .disabled(!ble.canChange || record.phase == .starting || blocker != nil || record.unsureSince != nil)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .frame(maxWidth: 820).frame(maxWidth: .infinity)
        .task(id: ble.canChange) { if ble.canChange { await ble.readFill() } }
        .onAppear { if let key { runs.attend(key) } }
    }

    private func update(_ key: RunLog.Key, _ change: (inout RunLog.Record) -> Void) {
        var r = runs[key]
        change(&r)
        runs[key] = r
    }

    private func elapsedMs(at date: Date) -> UInt32 {
        guard let reading, reading.value.running else { return reading?.value.elapsedMs ?? 0 }
        let since = UInt32(max(0, date.timeIntervalSince(reading.at)) * 1000)
        return min(reading.value.elapsedMs &+ since, reading.value.plannedMs)
    }

    private func start() {
        guard let key else { return }
        update(key) { $0.phase = .starting; $0.problem = nil }
        Task {
            let answer = await ble.startFill(channel)
            switch answer {
            case .success:
                if let f = fill, f.running, f.channel == channel, ble.current?.id == key.machine {
                    update(key) { $0.phase = .running; $0.startedHere = true; $0.sawRun = true }
                } else {
                    update(key) { $0.phase = .prepare; $0.problem = fill.map { refusal($0.outcome) } }
                }
            case .failure(let e):
                update(key) { r in
                    r.phase = .prepare
                    if e.mayHaveActed {
                        r.unsureSince = Date()
                    } else {
                        r.problem = RunProblem(title: "Filling didn’t start", message: e.message)
                    }
                }
                await ble.readFill()
            }
        }
    }

    /// Stopping lasts until the machine says it has stopped. A stop that
    /// didn't reach it says so beside the run: still running, by a reading
    /// taken after it; not confirmed, without one.
    private func stop() {
        guard let key, runningHere else { return }
        let sent = Date()
        update(key) { $0.phase = .stopping; $0.problem = nil }
        Task {
            guard case .failure(let e) = await ble.stopFill() else { return }
            await ble.readFill()
            guard runs[key].phase == .stopping else { return }
            let fresh = ble.current?.id == key.machine ? reading.flatMap { $0.at > sent ? $0.value : nil } : nil
            update(key) { r in
                r.phase = r.startedHere ? .running : .prepare
                if let fresh, fresh.running, fresh.channel == channel {
                    r.problem = RunProblem(title: "Filling didn’t stop", message: "\(e.message) It’s still running. Stop it at the machine if this keeps happening.")
                } else if fresh == nil {
                    r.problem = RunProblem(title: "Stop not confirmed", message: "\(e.message) Check the machine display; reconnecting reads whether it stopped.")
                }
            }
        }
    }

    private func refusal(_ outcome: FillOutcome) -> RunProblem {
        switch outcome {
        case .gas:
            return RunProblem(title: "Gas alarm", message: "Filling is unavailable during the gas alarm. Check the machine now.",
                              icon: "exclamationmark.triangle.fill", urgent: true)
        case .noIO:
            return RunProblem(title: "The machine can’t fill right now",
                              message: "Its valve controls didn’t check out. Check the machine display.")
        default:
            return RunProblem(title: "The machine is busy",
                              message: "Something else is running on the machine. Finish or stop it, then start filling.",
                              icon: "hourglass")
        }
    }

    private func done() {
        if let key { runs.acknowledge(key) }
        nav.finish(entry)
    }

    @ViewBuilder private func result(_ fill: FillState?) -> some View {
        switch fill?.outcome {
        case nil:
            Notice(title: "Filling ended",
                   message: "It ended while this device wasn’t connected, so how isn’t known. Check the funnel and the machine display.",
                   icon: "info.circle")
        case .full?:
            Notice(title: "Reservoir full",
                   message: "Filling ended because the reservoir is full. Concentrate may remain in the funnel.", icon: "checkmark.circle")
        case .stopped?:
            Notice(title: "Filling stopped",
                   message: "Concentrate may remain in the funnel. Check the funnel before adding more.", icon: "stop.circle")
        case .gas?:
            Notice(title: "Gas alarm", message: "Filling stopped for the gas alarm. Check the machine now.",
                   icon: "exclamationmark.triangle.fill", urgent: true)
        case .fault?, .noIO?, .busy?:
            Notice(title: "Filling stopped by a fault",
                   message: "The machine stopped and closed its valves. Check the machine display.", icon: "exclamationmark.circle", urgent: true)
        case .done?:
            Notice(title: "Filling finished", message: "The machine finished its planned run. Check the funnel for anything left.",
                   icon: "checkmark.circle")
        case .none?:
            Notice(title: "Filling ended", message: "The machine didn’t say how it ended. Check the funnel and the machine display.",
                   icon: "info.circle")
        }
        ActionButton(title: "Done") { done() }
    }
}

// ── Clean ───────────────────────────────────────────────────────────────

struct CleanView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(RunLog.self) var runs
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat
    let entry: RouteEntry

    private var key: RunLog.Key? { ble.current.map { RunLog.Key(machine: $0.id, kind: .clean, channel: channel) } }
    private var record: RunLog.Record { key.map { runs[$0] } ?? RunLog.Record() }
    private var reading: Reading<CleanState>? { ble.appliance.clean }
    private var clean: CleanState? { reading?.value }
    private var runningHere: Bool { clean?.running == true && clean?.channel == channel }
    private var rounds: Int { max(clean?.rounds ?? 3, 1) }
    private var blocker: Blocker? { Blocker.against(.clean, channel: channel, in: ble.appliance) }

    var body: some View {
        let wide = width >= 650 && !typeSize.isAccessibilitySize
        VStack(alignment: .leading, spacing: 24) {
            if runningHere || record.phase == .stopping {
                if !ble.linked && !ble.demoMode { lostContact }
                FlexibleColumns(wide: wide, spacing: 28) {
                    RunHeading(icon: "sparkles", title: "Cleaning", channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        if record.phase == .stopping {
                            Notice(title: "Stopping cleaning…",
                                   message: "Waiting for the machine to confirm that the pump and valves are stopped.", icon: "hourglass")
                        }
                        if let problem = record.problem { problem.notice }
                        Panel {
                            Text(stepTitle).font(.headline)
                            TimelineView(.periodic(from: .now, by: 1)) { context in
                                VStack(alignment: .leading, spacing: 16) {
                                    ProgressView(value: stepFraction(at: context.date)).tint(Theme.accent)
                                    Note(clean?.step == .funnel ? "Before rinse round 1" : timeLeft(at: context.date))
                                }
                            }
                            Note("Keep a container under the faucet.")
                        }
                        ActionButton(title: "Stop cleaning", primary: false, working: record.phase == .stopping) { stop() }
                            .disabled(record.phase == .stopping || !ble.canChange)
                        Note("The machine reports progress and confirms when it has stopped.")
                    }
                    .frame(maxWidth: .infinity)
                }
            } else if record.phase == .ended {
                result(record.endedUnheard ? nil : record.cleanEnded)
            } else {
                if let blocker { BlockerNotice(blocker: blocker) }
                if record.unsureSince != nil { unsure("cleaning") }
                if let problem = record.problem { problem.notice }
                FlexibleColumns(wide: wide, spacing: 28) {
                    CareFlavorColumn(channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        Text(rounds == 3 ? "Three rinse cycles" : "\(rounds) rinse cycles").font(.title2.weight(.semibold))
                        Note("Place a pitcher under the faucet. The machine rinses the funnel path, then fills and flushes the reservoir \(rounds == 3 ? "three times" : "\(rounds) times").")
                        Panel {
                            Label("Water exits at the faucet", systemImage: "arrow.down").font(.body.weight(.medium))
                            Note("Keep the pitcher in place until the cycle ends.")
                        }
                        ActionButton(title: "Start cleaning", working: record.phase == .starting) { start() }
                            .disabled(!ble.canChange || record.phase == .starting || blocker != nil || record.unsureSince != nil)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .frame(maxWidth: 820).frame(maxWidth: .infinity)
        .task(id: ble.canChange) { if ble.canChange { await ble.readClean() } }
        .onAppear { if let key { runs.attend(key) } }
    }

    private func update(_ key: RunLog.Key, _ change: (inout RunLog.Record) -> Void) {
        var r = runs[key]
        change(&r)
        runs[key] = r
    }

    private var stepTitle: String {
        guard let clean else { return "Cleaning" }
        switch clean.step {
        case .funnel: return "Rinsing the funnel path"
        case .waterFill: return "Round \(clean.round) of \(clean.rounds) · Filling"
        case .flush: return "Round \(clean.round) of \(clean.rounds) · Flushing"
        }
    }

    private func since(_ date: Date) -> UInt32 {
        guard let reading, reading.value.running else { return 0 }
        return UInt32(max(0, date.timeIntervalSince(reading.at)) * 1000)
    }

    private func stepFraction(at date: Date) -> Double {
        guard let clean, clean.stepPlannedMs > 0 else { return 0 }
        return min(Double(clean.stepElapsedMs &+ since(date)) / Double(clean.stepPlannedMs), 1)
    }

    private func timeLeft(at date: Date) -> String {
        guard let clean else { return "" }
        let left = Int(clean.cycleLeftMs) - Int(since(date))
        let minutes = Int((Double(max(left, 0)) / 60_000).rounded(.up))
        return minutes <= 1 ? "About a minute left" : "About \(minutes) min left"
    }

    private func start() {
        guard let key else { return }
        update(key) { $0.phase = .starting; $0.problem = nil }
        Task {
            let answer = await ble.startClean(channel)
            switch answer {
            case .success:
                if let c = clean, c.running, c.channel == channel, ble.current?.id == key.machine {
                    update(key) { $0.phase = .running; $0.startedHere = true; $0.sawRun = true }
                } else {
                    update(key) { $0.phase = .prepare; $0.problem = clean.map { refusal($0.outcome) } }
                }
            case .failure(let e):
                update(key) { r in
                    r.phase = .prepare
                    if e.mayHaveActed {
                        r.unsureSince = Date()
                    } else {
                        r.problem = RunProblem(title: "Cleaning didn’t start", message: e.message)
                    }
                }
                await ble.readClean()
            }
        }
    }

    private func stop() {
        guard let key, runningHere else { return }
        let sent = Date()
        update(key) { $0.phase = .stopping; $0.problem = nil }
        Task {
            guard case .failure(let e) = await ble.stopClean() else { return }
            await ble.readClean()
            guard runs[key].phase == .stopping else { return }
            let fresh = ble.current?.id == key.machine ? reading.flatMap { $0.at > sent ? $0.value : nil } : nil
            update(key) { r in
                r.phase = r.startedHere ? .running : .prepare
                if let fresh, fresh.running, fresh.channel == channel {
                    r.problem = RunProblem(title: "Cleaning didn’t stop", message: "\(e.message) It’s still running. Stop it at the machine if this keeps happening.")
                } else if fresh == nil {
                    r.problem = RunProblem(title: "Stop not confirmed", message: "\(e.message) Check the machine display; reconnecting reads whether it stopped.")
                }
            }
        }
    }

    private func refusal(_ outcome: CleanOutcome) -> RunProblem {
        switch outcome {
        case .gas:
            return RunProblem(title: "Gas alarm", message: "Cleaning is unavailable during the gas alarm. Check the machine now.",
                              icon: "exclamationmark.triangle.fill", urgent: true)
        case .noIO:
            return RunProblem(title: "The machine can’t clean right now",
                              message: "Its valve controls didn’t check out. Check the machine display.")
        default:
            return RunProblem(title: "The machine is busy",
                              message: "Something else is running on the machine. Finish or stop it, then start cleaning.",
                              icon: "hourglass")
        }
    }

    private func done() {
        if let key { runs.acknowledge(key) }
        nav.finish(entry)
    }

    @ViewBuilder private func result(_ clean: CleanState?) -> some View {
        switch clean?.outcome {
        case nil:
            Notice(title: "Cleaning ended",
                   message: "It ended while this device wasn’t connected, so how isn’t known. Run a complete clean cycle before adding concentrate if you aren’t sure it finished.",
                   icon: "info.circle")
        case .done?:
            Notice(title: "Flavor \(channel + 1) is clean",
                   message: "The funnel path and \(clean.map { $0.rounds == 3 ? "three" : "\($0.rounds)" } ?? "the") rinse cycles are complete.",
                   icon: "checkmark.circle")
        case .none?:
            Notice(title: "Cleaning ended",
                   message: "The machine didn’t say how it ended. Run a complete clean cycle before adding concentrate if you aren’t sure it finished.",
                   icon: "info.circle")
        case .stopped?:
            Notice(title: "Cleaning stopped",
                   message: "Water may remain in the reservoir. Keep the pitcher under the faucet and run a complete clean cycle before adding concentrate.",
                   icon: "stop.circle")
        case .gas?:
            Notice(title: "Gas alarm", message: "Cleaning stopped for the gas alarm. Check the machine now.",
                   icon: "exclamationmark.triangle.fill", urgent: true)
        case .fault?, .noIO?, .busy?:
            Notice(title: "Cleaning stopped by a fault",
                   message: "The machine stopped and closed its valves. Water may remain in the reservoir. Check the machine display.",
                   icon: "exclamationmark.circle", urgent: true)
        }
        ActionButton(title: "Done") { done() }
    }
}

// ── Prime ───────────────────────────────────────────────────────────────

/// Prime is held on the machine's displays. This page opens the shared
/// session, follows it by its token, and exits it.
struct PrimeView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(RunLog.self) var runs
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat
    let entry: RouteEntry

    @State private var opening = false
    @State private var exiting = false

    private var key: RunLog.Key? { ble.current.map { RunLog.Key(machine: $0.id, kind: .prime, channel: channel) } }
    private var record: RunLog.Record { key.map { runs[$0] } ?? RunLog.Record() }
    private var session: PrimeSession? { ble.appliance.prime?.value }
    private var ours: Bool { session.map { $0.phase != .off && $0.channel == channel } ?? false }
    private var blocker: Blocker? { Blocker.against(.prime, channel: channel, in: ble.appliance) }

    var body: some View {
        let wide = width >= 650 && !typeSize.isAccessibilitySize
        VStack(alignment: .leading, spacing: 24) {
            if ours, let session {
                FlexibleColumns(wide: wide, spacing: 28) {
                    RunHeading(icon: "hand.tap", title: session.phase == .running ? "Priming" : "Ready to prime", channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        if let problem = record.problem { problem.notice }
                        Panel {
                            if session.phase == .running {
                                Text(session.owner == .faucet ? "Held at the faucet" : "Held on the machine display").font(.headline)
                                Note("Release the pad to stop.")
                            } else {
                                Text("Hold the pad on the machine").font(.headline)
                                Note("Either display can run the selected pump. Release the pad to stop. Both displays and this app follow the same session.")
                            }
                        }
                        ActionButton(title: "Exit Prime", primary: false, working: exiting) { exit(session) }
                            .disabled(exiting || !ble.canChange)
                        if !ble.linked && !ble.demoMode {
                            Note("This phone can’t reach the machine. Exit Prime on the machine display.")
                        }
                    }
                    .frame(maxWidth: .infinity)
                }
            } else if let ended = endedNotice {
                ended
                ActionButton(title: "Done") { done() }
            } else {
                if let blocker { BlockerNotice(blocker: blocker) }
                if record.unsureSince != nil { unsure("Prime") }
                if let problem = record.problem { problem.notice }
                FlexibleColumns(wide: wide, spacing: 28) {
                    CareFlavorColumn(channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        Text("Continue at the machine").font(.title2.weight(.semibold))
                        Note("Place a glass under the faucet. Open Prime on the machine, then hold its pad to run the pump. Release to stop.")
                        Panel {
                            Label("Hold on either machine display", systemImage: "hand.tap").font(.body.weight(.medium))
                            Note("The app follows the same Prime session as both displays.")
                        }
                        ActionButton(title: "Open Prime on machine", working: opening) { open() }
                            .disabled(!ble.canChange || opening || blocker != nil || record.unsureSince != nil)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .frame(maxWidth: 820).frame(maxWidth: .infinity)
        .task(id: ble.canChange) {
            guard ble.canChange else { return }
            while !Task.isCancelled {
                await ble.readPrime()
                try? await Task.sleep(for: .seconds(ours ? 2 : 5))
            }
        }
        .onAppear {
            guard let key else { return }
            runs.attend(key)
            if let id = ble.current?.id { runs.observe(machine: id, appliance: ble.appliance) }
        }
    }

    private func update(_ key: RunLog.Key, _ change: (inout RunLog.Record) -> Void) {
        var r = runs[key]
        change(&r)
        runs[key] = r
    }

    /// The session this page was following has ended, by its own token.
    private var endedNotice: Notice? {
        guard let token = record.primeToken, let session, session.phase == .off, session.sessionToken == token else { return nil }
        switch session.outcome {
        case .canceled:
            return Notice(title: "Prime closed", message: "The machine left Prime.", icon: "checkmark.circle")
        case .leaseExpired:
            return Notice(title: "Prime closed on the machine", message: "The machine display left Prime.", icon: "info.circle")
        case .refused:
            return Notice(title: "Prime stopped", message: "The machine refused the pump. Check the machine display.",
                          icon: "exclamationmark.circle", urgent: true)
        default:
            return Notice(title: "Prime closed", message: "The machine left Prime.", icon: "checkmark.circle")
        }
    }

    private func done() {
        if let key { runs.acknowledge(key) }
        nav.finish(entry)
    }

    private func open() {
        guard let key else { return }
        opening = true
        update(key) { $0.problem = nil; $0.primeToken = nil }
        Task {
            switch await ble.openPrime(channel) {
            case .success(.shown):
                // The session follows as its own state; it is read until it does.
                for _ in 0..<10 where !ours {
                    await ble.readPrime()
                    if ours { break }
                    try? await Task.sleep(for: .milliseconds(400))
                }
                if !ours {
                    update(key) {
                        $0.problem = RunProblem(title: "Prime didn’t open",
                                                message: "The machine display didn’t start a Prime session. Check it, then try again.")
                    }
                }
            case .success(.refused):
                update(key) {
                    $0.problem = RunProblem(title: "The machine display didn’t open Prime",
                                            message: "Finish what’s on the machine display, then try again.")
                }
            case .success(.noAnswer):
                update(key) {
                    $0.problem = RunProblem(title: "The machine display didn’t answer",
                                            message: "Check the machine display, then try again.")
                }
            case .failure(let e):
                if e.mayHaveActed {
                    update(key) { $0.unsureSince = Date() }
                    await ble.readPrime()
                } else {
                    update(key) { $0.problem = RunProblem(title: "Prime didn’t open", message: e.message) }
                }
            }
            opening = false
        }
    }

    /// An exit that didn't take stays said beside the open session.
    private func exit(_ session: PrimeSession) {
        guard let key else { return }
        exiting = true
        update(key) { $0.problem = nil }
        Task {
            if case .failure(let e) = await ble.exitPrime(session) {
                update(key) { $0.problem = RunProblem(title: "Prime is still open", message: e.message) }
            }
            exiting = false
        }
    }
}
