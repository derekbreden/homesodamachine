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
                    SettingsRow(title: "Name", detail: nameDetail, icon: "pencil") { nav.push(.rename) }
                    RowDivider()
                    SettingsRow(title: "Sound", icon: "speaker.wave.2") { nav.push(.sound) }
                    RowDivider()
                    SettingsRow(title: "Software Update", icon: "arrow.down.circle") { nav.push(.update) }
                }
            }
            VStack(alignment: .leading, spacing: 12) {
                SectionTitle("This device")
                GroupedPanel {
                    SettingsRow(title: "Your machines", icon: "square.stack") { nav.managing = true }
                }
                if let unit = ble.current?.unit, !unit.isEmpty {
                    Text("Unit \(unit)").font(.caption).foregroundStyle(Theme.textSecondary).padding(.leading, 4)
                }
                if ble.linked, ble.trust == .viewer || ble.trust == .unpaired {
                    Note("This \(BLEManager.deviceWord) can view the machine. A change asks for Trust on the machine first.")
                    ActionButton(title: "Ask the machine to trust this \(BLEManager.deviceWord)", primary: false) {
                        Task { _ = await ble.requestTrust(.anything) }
                    }
                }
            }
        }
        .frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
    }

    /// A name the machine has not acknowledged yet says so.
    private var nameDetail: String? {
        guard let m = ble.current else { return nil }
        return m.pendingName.map { "\($0) · Pending" } ?? m.displayName
    }
}

// ── Sound ───────────────────────────────────────────────────────────────

/// The machine's sound. The choices are a draft until the machine accepts
/// them; Back keeps the draft, and Discard changes puts back what the machine
/// holds.
struct SoundView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(EditSessions.self) var edits
    let entry: RouteEntry

    private var key: EditKey? { ble.current.map { EditKey(machine: $0.id, field: .sound) } }
    private var held: SoundSettings? { ble.appliance.sound?.value }
    private var draft: SoundSettings? { key.flatMap { edits.draft($0) } }
    private var changed: Bool { draft.map { d in held.map { !d.sameChoices(as: $0) } ?? true } ?? false }

    var body: some View {
        let s = draft ?? held ?? SoundSettings()
        let write = key.flatMap(edits.write)
        VStack(alignment: .leading, spacing: 22) {
            if let held, !held.clockSet, s.quietOn {
                Notice(title: "Quiet hours need the machine clock",
                       message: "The clock is unavailable. Your schedule is saved, but quiet hours cannot take effect.",
                       icon: "clock.badge.exclamationmark")
            }
            if held == nil && !ble.canChange {
                Notice(title: "Sound settings unavailable", message: "Bring your device near the machine to read them.")
            } else if !ble.canChange {
                Notice(title: "Changes wait for the machine",
                       message: "Bring your device near the machine to save these settings.")
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
            .disabled(held == nil || write?.running == true)
            Note("The gas alarm always sounds at full volume.")
            if let problem = write?.problem { Note(problem) }
            if changed { Note("Not saved yet.") }
            ActionButton(title: "Save sound settings", working: write?.running == true) { save(s) }
                .frame(maxWidth: 440)
                .disabled(!ble.canChange || held == nil || !changed || write?.running == true)
            if draft != nil && write?.running != true {
                Button("Discard changes") { if let key { edits.discard(key) } }
                    .font(.body.weight(.medium)).frame(minHeight: 44)
            }
        }
        .frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
        .task(id: ble.canChange) { if ble.canChange { await ble.readSound() } }
    }

    private func field<T>(_ path: WritableKeyPath<SoundSettings, T>) -> Binding<T> {
        Binding(get: { (draft ?? held ?? SoundSettings())[keyPath: path] },
                set: { value in
                    guard let key else { return }
                    var next = draft ?? held ?? SoundSettings()
                    next[keyPath: path] = value
                    edits.setDraft(next, for: key)
                })
    }

    private func binding(_ path: WritableKeyPath<SoundSettings, Int>) -> Binding<Double> {
        let f = field(path)
        return Binding(get: { Double(f.wrappedValue) }, set: { f.wrappedValue = Int($0.rounded()) })
    }

    static func hour(_ h: Int) -> String {
        var c = DateComponents()
        c.hour = h
        let date = Calendar.current.date(from: c) ?? Date()
        return date.formatted(.dateTime.hour())
    }

    /// Done once the machine holds these choices: the editor closes. Anything
    /// else leaves the draft where it is, with what happened.
    private func save(_ wanted: SoundSettings) {
        guard let key, let machine = ble.current?.id else { return }
        let token = edits.begin(key)
        Task {
            let answer = await ble.saveSound(wanted)
            guard edits.isNewest(token, for: key) else { return }
            switch answer {
            case .success:
                if ble.current?.id == machine, let held = ble.appliance.sound?.value, held.sameChoices(as: wanted) {
                    edits.end(token, for: key)
                    edits.settle(key, saved: wanted)
                    nav.finish(entry)
                } else {
                    edits.end(token, for: key, problem: "The machine kept different settings. Yours are still here to save again or discard.")
                }
            case .failure(let e):
                edits.end(token, for: key, problem: e.message)
            }
        }
    }
}

// ── The machine's name ──────────────────────────────────────────────────

/// The machine's name, which the machine keeps for every device. Saved away
/// from the machine, it waits on this device and says so until the machine
/// acknowledges it.
struct RenameView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(EditSessions.self) var edits
    let entry: RouteEntry
    @FocusState private var focused: Bool

    private var key: EditKey? { ble.current.map { EditKey(machine: $0.id, field: .name) } }
    private var standing: String { ble.current?.pendingName ?? ble.current?.name ?? "" }
    private var text: Binding<String> {
        Binding(get: { key.flatMap { edits.draft($0) } ?? standing },
                set: { value in if let key { edits.setDraft(value, for: key) } })
    }
    private var trimmed: String { text.wrappedValue.trimmingCharacters(in: .whitespacesAndNewlines) }

    var body: some View {
        let write = key.flatMap(edits.write)
        VStack(alignment: .leading, spacing: 20) {
            TextField("Name", text: text, prompt: Text(ble.current?.displayName ?? "Name"))
                .textInputAutocapitalization(.words)
                .autocorrectionDisabled()
                .submitLabel(.done)
                .focused($focused)
                .onSubmit(save)
                .padding(16)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
                .disabled(write?.running == true)
            Note("Up to twenty letters. The machine keeps its name so every device sees the same one.")
            if let m = ble.current, let pending = m.pendingName {
                Note(ble.linked ? "Sending “\(pending)” to the machine."
                                : "“\(pending)” is saved on this device. It goes to the machine when this device is next near it.")
            }
            if let problem = write?.problem { Note(problem) }
            ActionButton(title: "Save name", working: write?.running == true) { save() }
                .disabled(trimmed.isEmpty || trimmed == standing || write?.running == true)
            if key.flatMap({ edits.draft($0, as: String.self) }) != nil && write?.running != true {
                Button("Discard changes") { if let key { edits.discard(key) } }
                    .font(.body.weight(.medium)).frame(minHeight: 44)
            }
        }
        .frame(maxWidth: 460).frame(maxWidth: .infinity)
        .onAppear { focused = true }
    }

    /// Done once the machine acknowledges the name, or once it is waiting on
    /// this device for the machine, which Settings then says.
    private func save() {
        guard let key, let m = ble.current, !trimmed.isEmpty, trimmed != standing else { return }
        let name = trimmed
        let typed = text.wrappedValue
        let token = edits.begin(key)
        Task {
            guard await ble.ensureTrusted(.name) else {
                edits.end(token, for: key, problem: "Nothing changed. Tap Trust on the machine to rename it from this device.")
                return
            }
            guard edits.isNewest(token, for: key) else { return }
            guard ble.current?.id == m.id else {
                edits.end(token, for: key, problem: "Nothing changed: another machine is in use.")
                return
            }
            ble.rename(m, to: name)
            for _ in 0..<12 where m.pendingName != nil && ble.linked {
                try? await Task.sleep(for: .milliseconds(500))
            }
            guard edits.isNewest(token, for: key) else { return }
            edits.end(token, for: key)
            edits.settle(key, saved: typed)
            nav.finish(entry)
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
    @State private var adding = false

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
                    if machine.accessoryID != nil { access.forget(machine) } else { removing = true }
                }
                if let why = access.removalProblem { Note(why) }
                ActionButton(title: "Add a machine") { adding = true }
            }
            .frame(maxWidth: 560).frame(maxWidth: .infinity)
            .padding(24)
        }
        .background(Theme.background.ignoresSafeArea())
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
        .sheet(isPresented: $adding) { AddMachineSheet() }
        .confirmationDialog("Remove \(machine.displayName) from this device?", isPresented: $removing, titleVisibility: .visible) {
            Button("Remove", role: .destructive) { access.forget(machine) }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Its pictures and readings leave this device. The machine itself is not changed.")
        }
    }
}
