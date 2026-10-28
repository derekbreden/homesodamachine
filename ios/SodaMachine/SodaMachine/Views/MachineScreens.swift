import SwiftUI

// ────────────────────────────────────────────────────────────
// The machine: its two flavors, and how it is doing.
//
// Everything here is what the machine last said. A reading carries the moment
// it was read, and one the phone is no longer hearing shows that moment. A
// reading the machine has not given shows as unknown.
// ────────────────────────────────────────────────────────────

extension BLEManager {
    /// Changes can reach the machine: it is in range and its faucet carries
    /// the bridge. The demo is always reachable.
    var canChange: Bool { demoMode || (linked && bridgeReady) }

    var appliance: ApplianceState { current?.appliance ?? ApplianceState() }

    /// A status read in the last ten seconds, from a machine the phone hears.
    var statusIsLive: Bool {
        guard let at = appliance.status?.at else { return false }
        return (demoMode || linked) && Date().timeIntervalSince(at) < 10
    }
}

extension BridgeError {
    var message: String {
        switch self {
        case .refused: "The machine turned that down."
        case .linkDown: "The faucet can’t reach the rest of the machine right now."
        case .busy: "The machine is busy. Try again in a moment."
        case .noAnswer: "The machine didn’t answer. Check it, then try again."
        case .needsUpdate: "Update the machine’s software to do this from the app."
        case .offline: "Bring your device near the machine."
        case .rejected: "The machine turned that down."
        case .untrusted: "Nothing changed."
        }
    }
}

/// The machine's readings while this page is up, and nothing while it is not.
struct StatusPolling: ViewModifier {
    @Environment(BLEManager.self) var ble

    func body(content: Content) -> some View {
        content.task(id: ble.linked && ble.bridgeReady) {
            guard ble.linked, ble.bridgeReady else { return }
            while !Task.isCancelled {
                await ble.readStatus()
                try? await Task.sleep(for: .seconds(3))
            }
        }
    }
}

struct MachineHomeView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(\.dynamicTypeSize) private var typeSize
    let width: CGFloat
    let height: CGFloat

    var body: some View {
        let compact = !typeSize.isAccessibilitySize && (height < 520 || (width >= 360 && width < 552 && height < 740))
        VStack(alignment: .leading, spacing: 20) {
            MachineNotices()
            if width >= 760 && !typeSize.isAccessibilitySize {
                HStack(alignment: .top, spacing: 24) {
                    flavorPair(compact: compact, artHeight: 200).frame(maxWidth: .infinity)
                    MachineStatusPanel().frame(width: min(260, width * 0.31))
                }
            } else {
                flavorPair(compact: compact, artHeight: 152)
                MachineStatusPanel()
            }
        }
        .modifier(StatusPolling())
    }

    private func flavorPair(compact: Bool, artHeight: CGFloat) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionTitle("Flavors")
            LazyVGrid(columns: typeSize.isAccessibilitySize ? [GridItem(.flexible())]
                                                            : [GridItem(.flexible(), spacing: 12), GridItem(.flexible())],
                      spacing: 12) {
                FlavorCard(channel: 0, compact: compact, artHeight: artHeight)
                FlavorCard(channel: 1, compact: compact, artHeight: artHeight)
            }
        }
    }
}

/// What stands between someone and the machine right now, above everything else.
struct MachineNotices: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @State private var adding = false

    var body: some View {
        if ble.demoMode {
            VStack(spacing: 12) {
                Notice(title: "This is the demo",
                       message: "Its readings and runs are simulated. Nothing here reaches a machine.",
                       icon: "play.rectangle")
                ActionButton(title: "Add your machine", primary: false) { adding = true }
                    .disabled(nav.locked)
            }
            .sheet(isPresented: $adding) { AddMachineSheet() }
        }
        if ble.connectionState == .bluetoothOff && !ble.demoMode {
            Notice(title: "Turn on Bluetooth", message: "Bluetooth connects this device to your machine.",
                   icon: "antenna.radiowaves.left.and.right.slash")
        } else if !ble.linked && !ble.demoMode && ble.appliance.status != nil {
            Notice(title: "Last known readings", message: "Bring your device near the machine to make changes.")
        }
        if ble.linked && ble.bridgeMissing {
            VStack(spacing: 12) {
                Notice(title: "Update your machine",
                       message: "Its software can’t share readings or take changes from this app yet.",
                       icon: "arrow.down.circle")
                ActionButton(title: "Software Update", primary: false) { nav.push(.update) }
            }
        }
        if let ask = ble.trustAsk, ask.quiet, ask.ended == nil {
            Notice(title: "Tap Trust on the machine",
                   message: "So this \(BLEManager.deviceWord) can change settings and run cycles. The faucet and the main display both ask.",
                   icon: "hand.tap")
        } else if let ask = ble.trustAsk, ask.quiet, let ended = ask.ended {
            VStack(spacing: 12) {
                Notice(title: ask.title,
                       message: ended == .unpaired ? ask.message
                           : "This \(BLEManager.deviceWord) can view the machine. Ask again to change settings and run cycles.",
                       icon: "hand.raised")
                HStack(spacing: 12) {
                    ActionButton(title: "Ask again", primary: false) {
                        Task { _ = await ble.requestTrust(.anything, quiet: true) }
                    }
                    .disabled(!ble.linked)
                    ActionButton(title: "OK", primary: false) { ble.dismissTrustAsk() }
                }
            }
        } else if ble.trustGrantedAt != nil {
            Notice(title: "Trusted",
                   message: "This \(BLEManager.deviceWord) can change settings and run cycles.",
                   icon: "checkmark.circle")
        }
        if let s = ble.appliance.status?.value {
            if s.gasAlarm {
                Notice(title: "Gas alarm",
                       message: "Check the machine now. Filling, cleaning and flavor injection are unavailable.",
                       icon: "exclamationmark.triangle.fill", urgent: true)
            }
            if s.simulated {
                Notice(title: "Simulated readings",
                       message: "The machine’s console is supplying these readings, not its sensors.",
                       icon: "wrench.and.screwdriver")
            }
        }
    }
}

struct FlavorCard: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    let channel: Int
    let compact: Bool
    let artHeight: CGFloat

    private var state: ApplianceState { ble.appliance }
    private var active: Bool { state.selection?.value.channel == channel }
    private var level: Int? { state.status?.value.level(channel) }
    private var ratioText: String { state.ratio(channel).map { "1:\($0)" } ?? "—" }
    private var levelText: String { level.map(LevelGauge.word) ?? "—" }
    private var art: Int { ble.flavorArt.art.indices.contains(channel) ? ble.flavorArt.art[channel] : channel }

    var body: some View {
        Button { nav.push(.flavor(channel)) } label: {
            Group {
                if compact {
                    HStack(spacing: 12) {
                        FlavorArtView(art: art, height: 110)
                        VStack(alignment: .leading, spacing: 10) {
                            HStack(spacing: 4) {
                                Text("Flavor \(channel + 1)").font(.headline)
                                Spacer(minLength: 0)
                                Image(systemName: "chevron.right").font(.caption.weight(.semibold))
                            }
                            Text(ratioText).font(.title3.weight(.medium).monospacedDigit())
                            LevelGauge(level: level)
                            Text(level == nil ? (active ? "On tap" : "Unknown") : "\(levelText)\(active ? " · On tap" : "")")
                                .font(.caption).foregroundStyle(active ? Theme.accent : Theme.textSecondary)
                        }
                    }
                } else {
                    VStack(alignment: .leading, spacing: 14) {
                        HStack {
                            Text("Flavor \(channel + 1)").font(.subheadline.weight(.semibold))
                            Spacer(minLength: 2)
                            Image(systemName: "chevron.right").font(.caption.weight(.semibold))
                        }
                        FlavorArtView(art: art, height: artHeight).frame(maxWidth: .infinity).padding(.vertical, 4)
                        HStack {
                            if active {
                                Label("On tap", systemImage: "checkmark.circle.fill")
                                    .font(.caption2.weight(.medium)).foregroundStyle(Theme.accent)
                            }
                            Spacer(minLength: 0)
                            Text(ratioText).font(.subheadline.weight(.medium).monospacedDigit())
                        }
                        LevelGauge(level: level)
                        HStack {
                            Text("Reservoir").font(.caption).foregroundStyle(Theme.textSecondary)
                            Spacer(minLength: 2)
                            Text(levelText).font(.caption.weight(.medium))
                        }
                    }
                }
            }
            .padding(16).frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
            .overlay(RoundedRectangle(cornerRadius: 18)
                .strokeBorder(active ? Theme.accent.opacity(0.7) : Theme.ice.opacity(0.08), lineWidth: active ? 1.25 : 0.5))
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Flavor \(channel + 1)\(active ? ", on tap" : ""), ratio \(ratioText), reservoir \(levelText)")
    }
}

struct MachineStatusPanel: View {
    @Environment(BLEManager.self) var ble

    var body: some View {
        let reading = ble.appliance.status
        let s = reading?.value
        VStack(alignment: .leading, spacing: 12) {
            SectionTitle("Status")
            Panel {
                HStack {
                    Image(systemName: "thermometer.low").foregroundStyle(Theme.textSecondary)
                    Text("Tank wall").font(.subheadline)
                    Spacer()
                    Text(s?.tankCelsius.map(Self.temperature) ?? "—").font(.title3.weight(.medium).monospacedDigit())
                }
                .accessibilityElement(children: .combine)
                Divider().overlay(Theme.ice.opacity(0.2))
                Label(s.map(Self.cooling) ?? "Waiting for a reading", systemImage: "snowflake").font(.subheadline)
                Label(s.map(Self.water) ?? "Water level unknown", systemImage: "drop").font(.subheadline)
                if let reading, !ble.statusIsLive { Note("As of \(said(reading.at))") }
            }
        }
    }

    /// The device's own unit, whatever the machine reads in.
    static func temperature(_ celsius: Double) -> String {
        Measurement(value: celsius, unit: UnitTemperature.celsius)
            .formatted(.measurement(width: .abbreviated, usage: .weather, numberFormatStyle: .number.precision(.fractionLength(0))))
    }

    static func cooling(_ s: MachineStatus) -> String {
        switch ColdState(rawValue: s.coldState) {
        case .on: return "Cooling"
        case .holding: return "Cooling soon"
        case .off: return "Holding temperature"
        case .freeze: return "Paused to prevent freezing"
        case .fault, nil: return "Cooling unavailable"
        }
    }

    /// Where the carbonator's water is, by its two reeds, and its refill.
    static func water(_ s: MachineStatus) -> String {
        switch RefillState(rawValue: s.refillState) {
        case .filling: return "Refilling with water"
        case .queued: return "Refill waiting"
        case .timeout: return "Refill stopped · check the water supply"
        case .fault: return "Water level fault"
        case .idle, nil: break
        }
        guard s.levelsRead else { return "Water level unknown" }
        if s.carbonatorHighReed { return "Water level high" }
        if s.carbonatorLowReed { return "Water level low" }
        return "Water level normal"
    }
}

// ── One flavor ──────────────────────────────────────────────────────────

/// One flavor: its image, its mix, whether it is on tap, and its care. The
/// mix is a draft until the machine accepts it, and stays one through Back,
/// a child page or another destination. Putting the flavor on tap stays on
/// this page.
struct FlavorDetailView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(EditSessions.self) var edits
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat
    let entry: RouteEntry

    /// Which of this page's buttons the running write belongs to.
    @State private var selecting = false

    private var key: EditKey? { ble.current.map { EditKey(machine: $0.id, field: .ratio(channel: channel)) } }
    private var confirmed: Int? { ble.appliance.ratio(channel) }
    private var draft: Int? { key.flatMap { edits.draft($0) } }
    private var ratio: Int { draft ?? confirmed ?? 20 }
    private var unsaved: Bool { draft.map { $0 != confirmed } ?? false }
    private var active: Bool { ble.appliance.selection?.value.channel == channel }
    private var write: EditSessions.Write? { key.flatMap(edits.write) }
    private var working: Bool { write?.running == true }
    private var art: Int { ble.flavorArt.art.indices.contains(channel) ? ble.flavorArt.art[channel] : channel }

    var body: some View {
        let wide = width >= 600 && !typeSize.isAccessibilitySize
        FlexibleColumns(wide: wide, spacing: 24) {
            VStack(spacing: 12) {
                if wide {
                    FlavorArtView(art: art, height: 240)
                    Button("Change image") { nav.push(.images(channel)) }.font(.subheadline.weight(.medium)).frame(minHeight: 44)
                } else {
                    HStack(spacing: 20) {
                        FlavorArtView(art: art, height: 132)
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Display image").font(.headline)
                            Note("Shown on both machine displays.")
                            Button("Change image") { nav.push(.images(channel)) }.font(.subheadline.weight(.medium)).frame(minHeight: 44)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .frame(maxWidth: .infinity)
        } right: {
            VStack(alignment: .leading, spacing: 16) {
                Panel {
                    HStack {
                        Text("Mix ratio").font(.headline)
                        Spacer()
                        if working && !selecting {
                            ProgressView().tint(Theme.textSecondary)
                        } else if unsaved {
                            Button("Save mix") { save() }.font(.subheadline.weight(.semibold))
                                .frame(minWidth: 44, minHeight: 44).contentShape(Rectangle())
                                .disabled(!ble.canChange || working)
                        } else if confirmed != nil {
                            Label("Saved", systemImage: "checkmark").font(.caption).foregroundStyle(Theme.textSecondary)
                        }
                    }
                    HStack(spacing: 18) {
                        Button { change(to: max(6, ratio - 1)) } label: {
                            Image(systemName: "minus").frame(width: 44, height: 44).background(Theme.ice.opacity(0.10), in: Circle())
                        }
                        .accessibilityLabel("Stronger mix")
                        Text("1:\(ratio)").font(.largeTitle.weight(.medium).monospacedDigit()).frame(maxWidth: .infinity)
                            .accessibilityLabel("1 to \(ratio)\(unsaved ? ", not saved" : "")")
                        Button { change(to: min(24, ratio + 1)) } label: {
                            Image(systemName: "plus").frame(width: 44, height: 44).background(Theme.ice.opacity(0.10), in: Circle())
                        }
                        .accessibilityLabel("Lighter mix")
                    }
                    .disabled(working || confirmed == nil && !ble.canChange)
                    Text(unsaved ? "Not saved · the machine pours 1:\(confirmed.map(String.init) ?? "—")"
                                 : "1 part concentrate · \(ratio) parts water")
                        .font(.subheadline).foregroundStyle(unsaved ? Theme.accent : Theme.textSecondary)
                    HStack { Text("More flavor"); Spacer(); Text("Lighter") }.font(.caption).foregroundStyle(Theme.textSecondary)
                    Text("1:6–1:24 · Match your concentrate bottle.").font(.caption).foregroundStyle(Theme.textSecondary)
                }
                if unsaved && !working {
                    Button("Discard changes") { if let key { edits.discard(key) } }
                        .font(.subheadline.weight(.medium)).frame(minHeight: 44)
                }
                if !ble.canChange && !ble.demoMode {
                    Note(unsaved ? "Your mix is kept here. Bring your device near the machine to save it."
                                 : "Bring your device near the machine to make changes.")
                }
                if let problem = write?.problem { Note(problem) }
                if active {
                    Label("On tap at the faucet", systemImage: "checkmark.circle.fill")
                        .font(.subheadline).foregroundStyle(Theme.accent).padding(.vertical, 4)
                } else {
                    ActionButton(title: unsaved ? "Save and use at faucet" : "Use at faucet", working: working && selecting) { use() }
                        .disabled(!ble.canChange || working)
                }
                VStack(alignment: .leading, spacing: 12) {
                    SectionTitle("Care")
                    HStack(spacing: 12) {
                        ActionButton(title: "Fill", primary: false) { nav.push(.fill(channel)) }
                        ActionButton(title: "Clean", primary: false) { nav.push(.clean(channel)) }
                        ActionButton(title: "Prime", primary: false) { nav.push(.prime(channel)) }
                    }
                }
                .padding(.top, 8)
            }
            .frame(maxWidth: .infinity)
        }
        .modifier(StatusPolling())
    }

    private func change(to value: Int) {
        guard let key else { return }
        edits.setDraft(value == confirmed ? nil : value, for: key)
    }

    /// Saved in place. Anything but the machine taking this mix leaves the
    /// draft standing, with what happened.
    private func save() {
        guard let key, let machine = ble.current?.id else { return }
        let wanted = ratio
        selecting = false
        let token = edits.begin(key)
        Task {
            let answer = await ble.saveRatio(channel, wanted)
            guard edits.isNewest(token, for: key) else { return }
            switch answer {
            case .success where ble.current?.id == machine && ble.appliance.ratio(channel) == wanted:
                edits.end(token, for: key)
                edits.settle(key, saved: wanted)
            case .success:
                edits.end(token, for: key, problem: "The machine kept its mix. Yours is still here to save again or discard.")
            case .failure(let e):
                edits.end(token, for: key, problem: e.message)
            }
        }
    }

    /// On tap, saving the mix first when it has changed: the mix is confirmed
    /// before the flavor is put on tap, and a mix saved before the second
    /// step failed says so.
    private func use() {
        guard let key, let machine = ble.current?.id else { return }
        let wanted = unsaved ? ratio : nil
        selecting = true
        let token = edits.begin(key)
        Task {
            if let wanted {
                let saved = await ble.saveRatio(channel, wanted)
                guard edits.isNewest(token, for: key) else { return }
                switch saved {
                case .success where ble.current?.id == machine && ble.appliance.ratio(channel) == wanted:
                    edits.settle(key, saved: wanted)
                case .success:
                    edits.end(token, for: key, problem: "The machine kept its mix, so this flavor wasn’t put on tap. Your mix is still here.")
                    return
                case .failure(let e):
                    edits.end(token, for: key, problem: "\(e.message) This flavor wasn’t put on tap.")
                    return
                }
            }
            let answer = await ble.selectFlavor(channel)
            guard edits.isNewest(token, for: key) else { return }
            let saidMix = wanted == nil ? "" : "The mix was saved. "
            switch answer {
            case .success where ble.current?.id == machine && ble.appliance.selection?.value.channel == channel:
                edits.end(token, for: key)
            case .success:
                edits.end(token, for: key, problem: "\(saidMix)The machine kept the other flavor on tap.")
            case .failure(let e):
                edits.end(token, for: key, problem: "\(saidMix)\(e.message)")
            }
        }
    }
}
