import SwiftUI

// ────────────────────────────────────────────────────────────
// Settings: the machine's name, its sound, its software, and the machines
// this device knows.
// ────────────────────────────────────────────────────────────

struct SettingsHomeView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav

    var body: some View {
        VStack(alignment: .leading, spacing: 28) {
            VStack(alignment: .leading, spacing: 12) {
                SectionTitle("Your machine")
                GroupedPanel {
                    SettingsRow(title: "Name", detail: ble.current?.displayName, icon: "pencil") { nav.push(.rename) }
                    RowDivider()
                    SettingsRow(title: "Sound", icon: "speaker.wave.2") { nav.push(.sound) }
                    RowDivider()
                    SettingsRow(title: "Software Update", icon: "arrow.down.circle") { nav.push(.update) }
                }
            }
            VStack(alignment: .leading, spacing: 12) {
                SectionTitle("This device")
                GroupedPanel {
                    SettingsRow(title: "Your machines", icon: "square.stack") { nav.push(.machines) }
                }
                if let unit = ble.current?.unit, !unit.isEmpty {
                    Text("Unit \(unit)").font(.caption).foregroundStyle(Theme.textSecondary).padding(.leading, 4)
                }
            }
        }
        .frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
    }
}

// ── Sound ───────────────────────────────────────────────────────────────

struct SoundView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav

    /// The settings being chosen, until they are saved; nil follows the machine.
    @State private var draft: SoundSettings?
    @State private var saving = false
    @State private var problem: String?

    private var held: SoundSettings? { ble.appliance.sound?.value }

    var body: some View {
        let s = draft ?? held ?? SoundSettings()
        VStack(alignment: .leading, spacing: 22) {
            if let held, !held.clockSet, s.quietOn {
                Notice(title: "Quiet hours need the machine clock",
                       message: "The clock is unavailable. Your schedule is saved, but quiet hours cannot take effect.",
                       icon: "clock.badge.exclamationmark")
            }
            if held == nil && !ble.canChange {
                Notice(title: "Sound settings unavailable", message: "Bring your device near the machine to read them.")
            }
            VStack(alignment: .leading, spacing: 20) {
                Panel {
                    HStack { Text("Volume").font(.headline); Spacer(); Text("\(s.volume)%").monospacedDigit() }
                    Slider(value: binding(\.volume), in: 0...100, step: 1).accessibilityLabel("Volume")
                    Note("Touch sounds and completion chimes.")
                }
                Panel {
                    Toggle("Quiet hours", isOn: field(\.quietOn)).tint(Theme.accent)
                    HStack {
                        Text("From"); Spacer()
                        Picker("From", selection: field(\.quietStart)) {
                            ForEach(0..<24, id: \.self) { h in Text(Self.hour(h)).tag(h) }
                        }
                        .tint(Theme.ice)
                    }
                    .frame(minHeight: 44)
                    HStack {
                        Text("Until"); Spacer()
                        Picker("Until", selection: field(\.quietEnd)) {
                            ForEach(0..<24, id: \.self) { h in Text(Self.hour(h)).tag(h) }
                        }
                        .tint(Theme.ice)
                    }
                    .frame(minHeight: 44)
                    HStack { Text("Quiet volume"); Spacer(); Text("\(s.quietVolume)%").monospacedDigit() }
                    Slider(value: binding(\.quietVolume), in: 0...100, step: 1).accessibilityLabel("Quiet volume")
                }
            }
            .disabled(!ble.canChange || held == nil)
            Note("The gas alarm always sounds at full volume.")
            if let problem { Note(problem) }
            ActionButton(title: "Save sound settings", working: saving) { save(s) }
                .frame(maxWidth: 440)
                .disabled(!ble.canChange || held == nil || saving)
        }
        .frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
        .task(id: ble.canChange) { if ble.canChange { await ble.readSound() } }
    }

    private func field<T>(_ key: WritableKeyPath<SoundSettings, T>) -> Binding<T> {
        Binding(get: { (draft ?? held ?? SoundSettings())[keyPath: key] },
                set: { value in
                    var next = draft ?? held ?? SoundSettings()
                    next[keyPath: key] = value
                    draft = next
                })
    }

    private func binding(_ key: WritableKeyPath<SoundSettings, Int>) -> Binding<Double> {
        let f = field(key)
        return Binding(get: { Double(f.wrappedValue) }, set: { f.wrappedValue = Int($0.rounded()) })
    }

    static func hour(_ h: Int) -> String {
        var c = DateComponents()
        c.hour = h
        let date = Calendar.current.date(from: c) ?? Date()
        return date.formatted(.dateTime.hour())
    }

    private func save(_ wanted: SoundSettings) {
        saving = true
        problem = nil
        Task {
            let answer = await ble.saveSound(wanted)
            saving = false
            switch answer {
            case .success:
                if let held = ble.appliance.sound?.value, held.sameChoices(as: wanted) {
                    draft = nil
                    nav.back()
                } else {
                    draft = nil
                    problem = "The machine kept different settings. They’re shown above."
                }
            case .failure(let e):
                problem = e.message
            }
        }
    }
}

// ── The machine's name ──────────────────────────────────────────────────

struct RenameView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @State private var name = ""
    @FocusState private var focused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            TextField("Name", text: $name)
                .textInputAutocapitalization(.words)
                .autocorrectionDisabled()
                .submitLabel(.done)
                .focused($focused)
                .onSubmit(save)
                .padding(16)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
            Note("Up to twenty letters. The machine keeps its name so every device sees the same one.")
            if let m = ble.current, m.pendingName != nil, !ble.linked {
                Note("Sent to the machine when this device is next near it.")
            }
            ActionButton(title: "Save name") { save() }
                .disabled(trimmed.isEmpty)
        }
        .frame(maxWidth: 460).frame(maxWidth: .infinity)
        .onAppear {
            name = ble.current?.pendingName ?? ble.current?.name ?? ""
            focused = true
        }
    }

    private var trimmed: String { name.trimmingCharacters(in: .whitespacesAndNewlines) }

    private func save() {
        guard let m = ble.current, !trimmed.isEmpty else { return }
        ble.rename(m, to: trimmed)
        nav.back()
    }
}

// ── Your machines ───────────────────────────────────────────────────────

struct MachinesView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(MachineAccess.self) var access
    @Environment(Navigator.self) var nav
    @State private var removing: KnownMachine?

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            TimelineView(.periodic(from: .now, by: 5)) { context in
                GroupedPanel {
                    ForEach(Array(directory.known.enumerated()), id: \.element.id) { index, machine in
                        row(machine, at: context.date)
                        if index < directory.known.count - 1 { RowDivider(inset: 0) }
                    }
                }
            }
            ActionButton(title: "Add a machine", primary: false, working: access.opening) { access.add() }
                .disabled(access.opening)
            outcome
            Note("A machine’s name is shared by every device that connects to it.")
            if let current = directory.current {
                Button("Remove \(current.displayName) from this device") {
                    // The system asks before removing a machine it lists.
                    if access.lists(current) { access.forget(current) } else { removing = current }
                }
                .font(.subheadline).foregroundStyle(Theme.error).frame(minHeight: 44)
            }
        }
        .frame(maxWidth: 560).frame(maxWidth: .infinity)
        .onAppear {
            access.clearOutcome()
            ble.beginBrowsing()
        }
        .onDisappear { ble.endBrowsing() }
        .confirmationDialog("Remove \(removing?.displayName ?? "this machine") from this device?",
                            isPresented: Binding(get: { removing != nil }, set: { if !$0 { removing = nil } }),
                            titleVisibility: .visible) {
            Button("Remove", role: .destructive) {
                if let m = removing { access.forget(m) }
                removing = nil
            }
            Button("Cancel", role: .cancel) { removing = nil }
        } message: {
            Text("Its pictures and readings leave this device. The machine itself is not changed.")
        }
    }

    private func row(_ machine: KnownMachine, at now: Date) -> some View {
        Button { ble.select(machine) } label: {
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(machine.displayName).font(.body.weight(.medium))
                    Text(subtitle(machine, at: now)).font(.caption).foregroundStyle(Theme.textSecondary)
                }
                Spacer()
                if machine.id == directory.current?.id {
                    Image(systemName: "checkmark").font(.body.weight(.semibold)).foregroundStyle(Theme.accent)
                }
            }
            .padding(.vertical, 16)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(machine.id == directory.current?.id ? .isSelected : [])
    }

    /// The unit tells two machines nobody has named apart; one with no unit
    /// says what kind it is.
    private func subtitle(_ machine: KnownMachine, at now: Date) -> String {
        if machine.isDemo { return "Demo · Always here" }
        let who = machine.unit.isEmpty ? machine.kind : "Unit \(machine.unit)"
        let kind = machine.supported ? "" : " · Prototype"
        return "\(who)\(kind) · \(status(machine, at: now))"
    }

    private func status(_ machine: KnownMachine, at now: Date) -> String {
        if machine.id == directory.current?.id {
            switch ble.connectionState {
            case .connected: return "Connected"
            case .connecting: return "Connecting…"
            default: break
            }
        }
        if let seen = machine.lastSeen, now.timeIntervalSince(seen) < 10 { return "In range" }
        if let t = machine.lastConnected { return "Last connected \(said(t))" }
        return "Never connected"
    }

    @ViewBuilder private var outcome: some View {
        switch access.outcome {
        case .failed(let why)?:
            Note(why)
        case .nothingAdded?:
            VStack(alignment: .leading, spacing: 8) {
                Label("Hold your device right next to the faucet", systemImage: "figure.walk")
                Label("Make sure the machine is powered on", systemImage: "power")
            }
            .font(.subheadline).foregroundStyle(Theme.textSecondary)
            .accessibilityElement(children: .combine)
        case nil:
            EmptyView()
        }
    }
}

// ── A prototype ─────────────────────────────────────────────────────────

/// A saved prototype: listed, and removable from this device.
struct UnsupportedMachineView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(MachineAccess.self) var access
    let machine: KnownMachine
    @State private var removing = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Text(machine.displayName).font(.largeTitle.weight(.semibold))
                Notice(title: "This app works with the soda machine appliance",
                       message: "This machine runs the prototype’s software. Remove it from this device, or choose another machine.",
                       icon: "exclamationmark.circle")
                if directory.known.count > 1 {
                    GroupedPanel {
                        ForEach(directory.known.filter { $0.id != machine.id }) { other in
                            SettingsRow(title: other.displayName, detail: other.isDemo ? "Demo" : nil) { ble.select(other) }
                        }
                    }
                }
                ActionButton(title: "Remove from this device", primary: false) {
                    if access.lists(machine) { access.forget(machine) } else { removing = true }
                }
                ActionButton(title: "Add a machine", working: access.opening) { access.add() }
                    .disabled(access.opening)
            }
            .frame(maxWidth: 560).frame(maxWidth: .infinity)
            .padding(24)
        }
        .background(Theme.background.ignoresSafeArea())
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
        .confirmationDialog("Remove \(machine.displayName) from this device?", isPresented: $removing, titleVisibility: .visible) {
            Button("Remove", role: .destructive) { access.forget(machine) }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Its pictures and readings leave this device. The machine itself is not changed.")
        }
    }
}
