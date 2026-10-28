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

    var body: some View {
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
                ActionButton(title: "Software Update", primary: false) { nav.open(.update, on: .settings) }
            }
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

struct FlavorDetailView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(\.dynamicTypeSize) private var typeSize
    let channel: Int
    let width: CGFloat

    /// The ratio being chosen, until it is saved; nil follows the machine.
    @State private var draft: Int?
    @State private var saving = false
    @State private var selecting = false
    @State private var problem: String?

    private var confirmed: Int? { ble.appliance.ratio(channel) }
    private var ratio: Int { draft ?? confirmed ?? 20 }
    private var active: Bool { ble.appliance.selection?.value.channel == channel }
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
                        if saving {
                            ProgressView().tint(Theme.textSecondary)
                        } else if confirmed == ratio {
                            Label("Saved", systemImage: "checkmark").font(.caption).foregroundStyle(Theme.textSecondary)
                        } else {
                            Button("Save") { save() }.font(.subheadline.weight(.semibold)).disabled(!ble.canChange)
                        }
                    }
                    HStack(spacing: 18) {
                        Button { draft = max(6, ratio - 1) } label: {
                            Image(systemName: "minus").frame(width: 44, height: 44).background(Theme.ice.opacity(0.10), in: Circle())
                        }
                        .accessibilityLabel("Stronger mix")
                        Text("1:\(ratio)").font(.largeTitle.weight(.medium).monospacedDigit()).frame(maxWidth: .infinity)
                            .accessibilityLabel("1 to \(ratio)")
                        Button { draft = min(24, ratio + 1) } label: {
                            Image(systemName: "plus").frame(width: 44, height: 44).background(Theme.ice.opacity(0.10), in: Circle())
                        }
                        .accessibilityLabel("Lighter mix")
                    }
                    .disabled(!ble.canChange || saving)
                    Text("1 part concentrate · \(ratio) parts water").font(.subheadline).foregroundStyle(Theme.textSecondary)
                    HStack { Text("More flavor"); Spacer(); Text("Lighter") }.font(.caption).foregroundStyle(Theme.textSecondary)
                    Text("1:6–1:24 · Match your concentrate bottle.").font(.caption).foregroundStyle(Theme.textSecondary)
                }
                if let problem { Note(problem) }
                if active {
                    Label("On tap at the faucet", systemImage: "checkmark.circle.fill")
                        .font(.subheadline).foregroundStyle(Theme.accent).padding(.vertical, 4)
                } else {
                    ActionButton(title: "Use at faucet", working: selecting) { select() }
                        .disabled(!ble.canChange || selecting)
                }
            }
            .frame(maxWidth: .infinity)
        }
        .modifier(StatusPolling())
    }

    private func save() {
        let wanted = ratio
        saving = true
        problem = nil
        Task {
            let answer = await ble.saveRatio(channel, wanted)
            saving = false
            switch answer {
            case .success:
                if ble.appliance.ratio(channel) == wanted {
                    draft = nil
                } else {
                    problem = "The machine kept \(confirmed.map { "1:\($0)" } ?? "its ratio")."
                }
            case .failure(let e):
                problem = e.message
            }
        }
    }

    private func select() {
        selecting = true
        problem = nil
        Task {
            let answer = await ble.selectFlavor(channel)
            selecting = false
            switch answer {
            case .success: if ble.appliance.selection?.value.channel == channel { nav.back() }
            case .failure(let e): problem = e.message
            }
        }
    }
}
