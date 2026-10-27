import SwiftUI

// ────────────────────────────────────────────────────────────
// Care: Fill, Clean and Prime, one flavor at a time.
//
// Each run is the machine's. A page shows the state the machine reports —
// starting, running, stopping, how it ended — and a run this phone started
// holds the app's navigation until it ends. A run started at the machine
// shows the same progress here, with nothing held.
// ────────────────────────────────────────────────────────────

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
            Note("One flavor at a time.")
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
                ActionButton(title: "Flavor 2", primary: false) { nav.push(route(1)) }
            }
            .disabled(!ble.canChange)
        }
        .padding(16).frame(maxWidth: .infinity, alignment: .topLeading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }
}

/// A fill or a clean cycle the machine is running, whoever started it.
struct RunningCard: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav

    var body: some View {
        if let fill = ble.appliance.fill?.value, fill.running {
            button("Filling Flavor \(fill.channel + 1)", icon: "arrow.down.to.line") { nav.push(.fill(fill.channel)) }
        } else if let clean = ble.appliance.clean?.value, clean.running {
            button("Cleaning Flavor \(clean.channel + 1)", icon: "sparkles") { nav.push(.clean(clean.channel)) }
        }
    }

    private func button(_ title: String, icon: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon).foregroundStyle(Theme.accent)
                VStack(alignment: .leading, spacing: 4) {
                    Text(title).font(.body.weight(.semibold))
                    Text("In progress on the machine").font(.subheadline).foregroundStyle(Theme.textSecondary)
                }
                Spacer()
                Image(systemName: "chevron.right").font(.caption.weight(.semibold)).foregroundStyle(Theme.textSecondary)
            }
            .padding(16).frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
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

/// What a run page is doing on this phone's side of it.
enum RunPhase: Equatable {
    case prepare
    case starting
    case running     // this phone started it, and the machine said so
    case stopping
    case ended
}

/// Another flavor's run, or Prime, is holding the machine.
private func busyNotice(_ ble: BLEManager, channel: Int) -> Notice? {
    let a = ble.appliance
    if let f = a.fill?.value, f.running, f.channel != channel {
        return Notice(title: "Flavor \(f.channel + 1) is being filled",
                      message: "Finish or stop that operation at the machine before starting another.", icon: "hourglass")
    }
    if let c = a.clean?.value, c.running, c.channel != channel {
        return Notice(title: "Flavor \(c.channel + 1) is being cleaned",
                      message: "Finish or stop that operation at the machine before starting another.", icon: "hourglass")
    }
    if let p = a.prime?.value, p.phase != .off {
        return Notice(title: "Prime is open on the machine",
                      message: "Exit Prime on the machine display before starting another operation.", icon: "hourglass")
    }
    return nil
}

private let lostContact = Notice(
    title: "The cycle may still be running",
    message: "The phone cannot confirm its state. Check the machine display. Reconnecting will read its current progress.",
    icon: "antenna.radiowaves.left.and.right.slash")

// ── Fill ────────────────────────────────────────────────────────────────

struct FillView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat

    @State private var phase = RunPhase.prepare
    @State private var problem: Notice?
    /// This page has seen the run in progress, whoever started it.
    @State private var sawRun = false

    private var reading: Reading<FillState>? { ble.appliance.fill }
    private var fill: FillState? { reading?.value }
    private var runningHere: Bool { fill?.running == true && fill?.channel == channel }

    var body: some View {
        let wide = width >= 650 && !typeSize.isAccessibilitySize
        VStack(alignment: .leading, spacing: 24) {
            if phase == .ended, let fill {
                result(fill)
            } else if runningHere || phase == .stopping {
                if !ble.linked && !ble.demoMode { lostContact }
                FlexibleColumns(wide: wide, spacing: 28) {
                    RunHeading(icon: "arrow.down.to.line", title: "Filling", channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        if phase == .stopping {
                            Notice(title: "Stopping filling…",
                                   message: "Waiting for the machine to confirm that the pump and valves are stopped.",
                                   icon: "hourglass")
                        }
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
                        ActionButton(title: "Stop filling", primary: false, working: phase == .stopping) { stop() }
                            .disabled(phase == .stopping || !ble.canChange)
                        Note("The machine reports progress and confirms when it has stopped.")
                    }
                    .frame(maxWidth: .infinity)
                }
            } else {
                if let busy = busyNotice(ble, channel: channel) { busy }
                if let problem { problem }
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
                        ActionButton(title: "Start filling", working: phase == .starting) { start() }
                            .disabled(!ble.canChange || phase == .starting || busyNotice(ble, channel: channel) != nil)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .frame(maxWidth: 820).frame(maxWidth: .infinity)
        .task(id: runningHere && ble.canChange) {
            guard runningHere, ble.canChange else { return }
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(2))
                await ble.readFill()
            }
        }
        .task { if ble.canChange { await ble.readFill() } }
        .onChange(of: fill, initial: true) { _, now in
            guard let now else { return }
            if now.running && now.channel == channel { sawRun = true }
            if (sawRun || phase == .stopping) && !now.running { phase = .ended }
        }
        .onChange(of: phase) { lock() }
        .onChange(of: ble.linked) { lock() }
        .onDisappear { nav.locked = false }
    }

    private func lock() {
        nav.locked = (phase == .starting || phase == .running || phase == .stopping) && (ble.linked || ble.demoMode)
    }

    private func elapsedMs(at date: Date) -> UInt32 {
        guard let reading, reading.value.running else { return reading?.value.elapsedMs ?? 0 }
        let since = UInt32(max(0, date.timeIntervalSince(reading.at)) * 1000)
        return min(reading.value.elapsedMs &+ since, reading.value.plannedMs)
    }

    private func start() {
        phase = .starting
        problem = nil
        Task {
            switch await ble.startFill(channel) {
            case .success:
                if let f = fill, f.running, f.channel == channel {
                    phase = .running
                } else {
                    phase = .prepare
                    problem = fill.map { refusal($0.outcome) }
                }
            case .failure(let e):
                phase = .prepare
                problem = Notice(title: "Filling didn’t start", message: e.message, icon: "exclamationmark.circle")
                await ble.readFill()
            }
        }
    }

    private func stop() {
        phase = .stopping
        Task {
            if case .failure = await ble.stopFill() { await ble.readFill() }
            if fill?.running == false { phase = .ended }
        }
    }

    private func refusal(_ outcome: FillOutcome) -> Notice {
        switch outcome {
        case .gas:
            return Notice(title: "Gas alarm", message: "Filling is unavailable during the gas alarm. Check the machine now.",
                          icon: "exclamationmark.triangle.fill", urgent: true)
        case .noIO:
            return Notice(title: "The machine can’t fill right now",
                          message: "Its valve controls didn’t check out. Check the machine display.", icon: "exclamationmark.circle")
        default:
            return Notice(title: "The machine is busy",
                          message: "Finish or stop what’s running at the machine before starting another.", icon: "hourglass")
        }
    }

    @ViewBuilder private func result(_ fill: FillState) -> some View {
        switch fill.outcome {
        case .full:
            Notice(title: "Reservoir full",
                   message: "Filling ended because the reservoir is full. Concentrate may remain in the funnel.", icon: "checkmark.circle")
            ActionButton(title: "Done") { nav.back() }
        case .stopped:
            Notice(title: "Filling stopped",
                   message: "Concentrate may remain in the funnel. Check the funnel before adding more.", icon: "stop.circle")
            ActionButton(title: "Back to Care") { nav.back() }
        case .gas:
            Notice(title: "Gas alarm", message: "Filling stopped for the gas alarm. Check the machine now.",
                   icon: "exclamationmark.triangle.fill", urgent: true)
            ActionButton(title: "Back to Care") { nav.back() }
        case .fault, .noIO, .busy:
            Notice(title: "Filling stopped by a fault",
                   message: "The machine stopped and closed its valves. Check the machine display.", icon: "exclamationmark.circle", urgent: true)
            ActionButton(title: "Back to Care") { nav.back() }
        case .done, .none:
            Notice(title: "Filling finished", message: "The machine finished its planned run. Check the funnel for anything left.",
                   icon: "checkmark.circle")
            ActionButton(title: "Done") { nav.back() }
        }
    }
}

// ── Clean ───────────────────────────────────────────────────────────────

struct CleanView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat

    @State private var phase = RunPhase.prepare
    @State private var problem: Notice?
    /// This page has seen the run in progress, whoever started it.
    @State private var sawRun = false

    private var reading: Reading<CleanState>? { ble.appliance.clean }
    private var clean: CleanState? { reading?.value }
    private var runningHere: Bool { clean?.running == true && clean?.channel == channel }
    private var rounds: Int { max(clean?.rounds ?? 3, 1) }

    var body: some View {
        let wide = width >= 650 && !typeSize.isAccessibilitySize
        VStack(alignment: .leading, spacing: 24) {
            if phase == .ended, let clean {
                result(clean)
            } else if phase == .stopping {
                Notice(title: "Stopping cleaning…",
                       message: "Waiting for the machine to confirm that the pump and valves are stopped.", icon: "hourglass")
            } else if runningHere {
                if !ble.linked && !ble.demoMode { lostContact }
                FlexibleColumns(wide: wide, spacing: 28) {
                    RunHeading(icon: "sparkles", title: "Cleaning", channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
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
                        ActionButton(title: "Stop cleaning", primary: false) { stop() }
                            .disabled(!ble.canChange)
                        Note("The machine reports progress and confirms when it has stopped.")
                    }
                    .frame(maxWidth: .infinity)
                }
            } else {
                if let busy = busyNotice(ble, channel: channel) { busy }
                if let problem { problem }
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
                        ActionButton(title: "Start cleaning", working: phase == .starting) { start() }
                            .disabled(!ble.canChange || phase == .starting || busyNotice(ble, channel: channel) != nil)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .frame(maxWidth: 820).frame(maxWidth: .infinity)
        .task(id: runningHere && ble.canChange) {
            guard runningHere, ble.canChange else { return }
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(2))
                await ble.readClean()
            }
        }
        .task { if ble.canChange { await ble.readClean() } }
        .onChange(of: clean, initial: true) { _, now in
            guard let now else { return }
            if now.running && now.channel == channel { sawRun = true }
            if (sawRun || phase == .stopping) && !now.running { phase = .ended }
        }
        .onChange(of: phase) { lock() }
        .onChange(of: ble.linked) { lock() }
        .onDisappear { nav.locked = false }
    }

    private func lock() {
        nav.locked = (phase == .starting || phase == .running || phase == .stopping) && (ble.linked || ble.demoMode)
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
        phase = .starting
        problem = nil
        Task {
            switch await ble.startClean(channel) {
            case .success:
                if let c = clean, c.running, c.channel == channel {
                    phase = .running
                } else {
                    phase = .prepare
                    problem = clean.map { refusal($0.outcome) }
                }
            case .failure(let e):
                phase = .prepare
                problem = Notice(title: "Cleaning didn’t start", message: e.message, icon: "exclamationmark.circle")
                await ble.readClean()
            }
        }
    }

    private func stop() {
        phase = .stopping
        Task {
            if case .failure = await ble.stopClean() { await ble.readClean() }
            if clean?.running == false { phase = .ended }
        }
    }

    private func refusal(_ outcome: CleanOutcome) -> Notice {
        switch outcome {
        case .gas:
            return Notice(title: "Gas alarm", message: "Cleaning is unavailable during the gas alarm. Check the machine now.",
                          icon: "exclamationmark.triangle.fill", urgent: true)
        case .noIO:
            return Notice(title: "The machine can’t clean right now",
                          message: "Its valve controls didn’t check out. Check the machine display.", icon: "exclamationmark.circle")
        default:
            return Notice(title: "The machine is busy",
                          message: "Finish or stop what’s running at the machine before starting another.", icon: "hourglass")
        }
    }

    @ViewBuilder private func result(_ clean: CleanState) -> some View {
        switch clean.outcome {
        case .done, .none:
            Notice(title: "Flavor \(channel + 1) is clean",
                   message: "The funnel path and \(clean.rounds == 3 ? "three" : "\(clean.rounds)") rinse cycles are complete.",
                   icon: "checkmark.circle")
            ActionButton(title: "Done") { nav.back() }
        case .stopped:
            Notice(title: "Cleaning stopped",
                   message: "Water may remain in the reservoir. Keep the pitcher under the faucet and run a complete clean cycle before adding concentrate.",
                   icon: "stop.circle")
            ActionButton(title: "Back to Care") { nav.back() }
        case .gas:
            Notice(title: "Gas alarm", message: "Cleaning stopped for the gas alarm. Check the machine now.",
                   icon: "exclamationmark.triangle.fill", urgent: true)
            ActionButton(title: "Back to Care") { nav.back() }
        case .fault, .noIO, .busy:
            Notice(title: "Cleaning stopped by a fault",
                   message: "The machine stopped and closed its valves. Water may remain in the reservoir. Check the machine display.",
                   icon: "exclamationmark.circle", urgent: true)
            ActionButton(title: "Back to Care") { nav.back() }
        }
    }
}

// ── Prime ───────────────────────────────────────────────────────────────

struct PrimeView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat

    @State private var opening = false
    @State private var exiting = false
    /// The session this page opened or is showing, by its token.
    @State private var token: UInt32?
    @State private var problem: Notice?

    private var session: PrimeSession? { ble.appliance.prime?.value }
    private var ours: Bool { session.map { $0.phase != .off && $0.channel == channel } ?? false }

    var body: some View {
        let wide = width >= 650 && !typeSize.isAccessibilitySize
        VStack(alignment: .leading, spacing: 24) {
            if ours, let session {
                FlexibleColumns(wide: wide, spacing: 28) {
                    RunHeading(icon: "hand.tap", title: session.phase == .running ? "Priming" : "Ready to prime", channel: channel)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
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
                ActionButton(title: "Back to Care") { nav.back() }
            } else {
                if let busy = busyNotice(ble, channel: channel), session?.phase == .off || session == nil { busy }
                if let other = session, other.phase != .off, other.channel != channel {
                    Notice(title: "Prime is open for Flavor \(other.channel + 1)",
                           message: "Exit Prime on the machine display to prime this flavor.", icon: "hourglass")
                }
                if let problem { problem }
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
                            .disabled(!ble.canChange || opening || session.map { $0.phase != .off } == true
                                      || ble.appliance.fill?.value.running == true || ble.appliance.clean?.value.running == true)
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
        .onChange(of: session) { _, now in
            if let now, now.phase != .off, now.channel == channel { token = now.sessionToken }
        }
    }

    /// The session this page was showing has ended.
    private var endedNotice: Notice? {
        guard let token, let session, session.phase == .off, session.sessionToken == token else { return nil }
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

    private func open() {
        opening = true
        problem = nil
        token = nil
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
                    problem = Notice(title: "Prime didn’t open",
                                     message: "The machine display didn’t start a Prime session. Check it, then try again.",
                                     icon: "exclamationmark.circle")
                }
            case .success(.refused):
                problem = Notice(title: "The machine display didn’t open Prime",
                                 message: "Finish what’s on the machine display, then try again.", icon: "exclamationmark.circle")
            case .success(.noAnswer):
                problem = Notice(title: "The machine display didn’t answer",
                                 message: "Check the machine display, then try again.", icon: "exclamationmark.circle")
            case .failure(let e):
                problem = Notice(title: "Prime didn’t open", message: e.message, icon: "exclamationmark.circle")
            }
            opening = false
        }
    }

    private func exit(_ session: PrimeSession) {
        exiting = true
        Task {
            if case .failure(let e) = await ble.exitPrime(session) {
                problem = Notice(title: "Prime is still open", message: e.message, icon: "exclamationmark.circle")
            }
            exiting = false
        }
    }
}
