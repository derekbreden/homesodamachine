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

// ── Explicit forms ────────────────────────────────────────────────────

struct FormSaveOutcome: View {
    @Environment(BLEManager.self) var ble
    @Environment(SettingWriter.self) var writer
    let setting: SettingKey
    var discard: () -> Void
    var submitted: (UUID) -> Void

    var body: some View {
        if let pending = writer.commit(setting) {
            VStack(alignment: .leading, spacing: 12) {
                if let ask = ble.trustAsk, ask.quiet {
                    TrustStatusView(ask: ask, offersClose: false) {
                        Task {
                            guard await ble.retryTrustAsk() == .trusted else { return }
                            if let id = writer.commit(setting)?.id { submitted(id) }
                            writer.retry(setting)
                        }
                    }
                } else if let outcome = pending.trustEnd {
                    KeptTrustOutcome(outcome: outcome, retryAt: pending.trustRetryAt) {
                        submitted(pending.id)
                        writer.retry(setting)
                    }
                } else if pending.phase == .conflict {
                    Label(pending.unconfirmed == true ? "Save not confirmed" : "Changed from another device", systemImage: "exclamationmark.triangle.fill")
                        .font(.headline)
                    Text("The machine now has \(describe(ble.settingSnapshot(setting)?.value ?? pending.current?.value)). Your change is kept here.")
                        .font(.subheadline).foregroundStyle(Theme.textSecondary)
                    HStack(spacing: 24) {
                        Button("Use mine") {
                            writer.useMine(setting)
                            if let id = writer.commit(setting)?.id { submitted(id) }
                        }
                        Button("Keep machine’s setting") { writer.discard(setting); discard() }
                    }.frame(minHeight: 44)
                } else if !ble.canChange {
                    Label(ble.connectionState == .bluetoothOff ? "Not sent · Bluetooth is off" : "Not sent · out of range", systemImage: "antenna.radiowaves.left.and.right.slash")
                        .font(.headline)
                    Note("Your change is kept on this device. It sends automatically when the machine reconnects.")
                } else if pending.phase == .failed || pending.phase == .uncertain {
                    Label(pending.phase == .uncertain ? "Save not confirmed" : "Couldn’t save", systemImage: "exclamationmark.triangle.fill")
                        .font(.headline)
                    Note(pending.problem ?? "Your change is kept here.")
                    Button("Try again") {
                        submitted(pending.id)
                        writer.retry(setting)
                    }.frame(minHeight: 44)
                } else {
                    HStack { ProgressView(); Text(pending.phase == .trust ? "Trust needed to save" : "Saving…") }
                }
                if pending.phase != .conflict {
                    Button(pending.phase == .uncertain ? "Stop retrying" : "Discard changes") { writer.discard(setting); discard() }.frame(minHeight: 44)
                        .disabled(pending.phase == .sending)
                }
            }
            .padding(16).frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
            .accessibilityElement(children: .contain)
        }
    }

    private func describe(_ data: Data?) -> String {
        guard let data else { return "a newer setting" }
        if setting == .name { return "the name “\(String(data: data, encoding: .utf8) ?? "")”" }
        if let sound = SoundSettings(data) { return "volume \(sound.volume)% and its current quiet-hours schedule" }
        return "a newer setting"
    }
}

struct DraftSettingConflict: View {
    @Environment(BLEManager.self) var ble
    @Environment(SettingWriter.self) var writer
    let setting: SettingKey
    let base: SettingSnapshot
    let desired: Data
    var keepMachine: () -> Void
    var submitted: (UUID) -> Void

    var body: some View {
        if let current = ble.settingSnapshot(setting), current.revision != base.revision {
            VStack(alignment: .leading, spacing: 12) {
                Label("Changed from another device", systemImage: "exclamationmark.triangle.fill").font(.headline)
                Note(setting == .name
                     ? "The machine is now named “\(String(data: current.value, encoding: .utf8) ?? "")”. Your name is kept here."
                     : "The machine’s sound settings changed while you were editing. Your choices are kept here.")
                HStack(spacing: 24) {
                    Button("Use mine") {
                        if let token = writer.submit(setting, base: current, desired: desired) { submitted(token) }
                    }
                    Button("Keep machine’s setting", action: keepMachine)
                }.frame(minHeight: 44)
            }
            .padding(16).frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
        }
    }
}

struct SoundView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(EditSessions.self) var edits
    @Environment(SettingWriter.self) var writer
    let entry: RouteEntry
    @State private var submittedToken: UUID?
    @State private var submittedValue: SoundSettings?

    private var key: EditKey? { ble.current.map { EditKey(machine: $0.id, field: .sound) } }
    private var snapshot: SettingSnapshot? { ble.settingSnapshot(.sound) }
    private var held: SoundSettings? { snapshot.flatMap { SoundSettings($0.value) } }
    private var draft: SoundSettings? { key.flatMap { edits.draft($0) } }
    private var displayedSound: SoundSettings { writer.commit(.sound).flatMap { SoundSettings($0.desired) } ?? draft ?? held ?? SoundSettings() }
    private var changed: Bool { draft != nil }
    private var waiting: Bool { writer.commit(.sound) != nil }
    private var conflict: Bool { key.flatMap(edits.base).map { base in snapshot.map { base.revision != $0.revision } ?? false } ?? false }
    private var accepted: UUID? { ble.current.flatMap { writer.accepted[FormSettingID(machine: $0.id, setting: .sound)] } }

    var body: some View {
        let s = displayedSound
        VStack(alignment: .leading, spacing: 22) {
            if snapshot == nil {
                Notice(title: "Sound settings unavailable", message: ble.canChange ? "Waiting for the machine’s saved settings." : "Bring your device near the machine to read them.")
            }
            if ble.appliance.sound?.value.clockSet == false, s.quietOn {
                Notice(title: "Quiet hours need the machine clock", message: "The clock is unavailable. Your schedule can be saved, but quiet hours cannot take effect.", icon: "clock.badge.exclamationmark")
            }
            VStack(alignment: .leading, spacing: 20) {
                Panel {
                    HStack { Text("Volume").font(.headline); Spacer(); Text(held == nil ? "—" : "\(s.volume)%").monospacedDigit() }
                    Slider(value: binding(\.volume), in: 0...100, step: 1).accessibilityLabel("Volume")
                    Note("Touch sounds and completion chimes.")
                }
                Panel {
                    Toggle("Quiet hours", isOn: field(\.quietOn)).tint(Theme.accent)
                    HStack {
                        Text("From"); Spacer()
                        Picker("From", selection: field(\.quietStart)) {
                            ForEach(0..<24, id: \.self) { h in Text(Self.hour(h)).tag(h) }
                        }.tint(Theme.ice)
                    }.frame(minHeight: 44)
                    HStack {
                        Text("Until"); Spacer()
                        Picker("Until", selection: field(\.quietEnd)) {
                            ForEach(0..<24, id: \.self) { h in Text(Self.hour(h)).tag(h) }
                        }.tint(Theme.ice)
                    }.frame(minHeight: 44)
                    HStack { Text("Quiet volume"); Spacer(); Text("\(s.quietVolume)%").monospacedDigit() }
                    Slider(value: binding(\.quietVolume), in: 0...100, step: 1).accessibilityLabel("Quiet volume")
                }
            }.disabled(snapshot == nil || waiting)
            Note("The gas alarm always sounds at full volume.")
            FormSaveOutcome(setting: .sound, discard: { if let key { edits.discard(key) } }, submitted: { token in
                submittedToken = token
                submittedValue = s
            })
            if !waiting {
                if let key, let base = edits.base(key), let current = snapshot, current.revision != base.revision {
                    DraftSettingConflict(setting: .sound, base: base, desired: soundBytes(s), keepMachine: { edits.discard(key) }, submitted: { token in
                        submittedToken = token; submittedValue = s
                    })
                }
                if changed && !conflict { Note("Your sound changes are ready to save.") }
                if !conflict {
                    ActionButton(title: "Save sound settings") { save(s) }
                        .frame(maxWidth: 440).disabled(snapshot == nil || !changed)
                }
                if changed && !conflict {
                    Button("Discard changes") { if let key { edits.discard(key) } }.frame(minHeight: 44)
                }
            }
        }
        .frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
        .task(id: ble.canChange) {
            if ble.canChange { _ = await ble.readSetting(.sound); await ble.readSound() }
        }
        .onChange(of: accepted) { _, token in
            guard let token, token == submittedToken, nav.isOpen(entry), let key, let value = submittedValue else { return }
            edits.settle(key, saved: value)
            nav.finish(entry)
        }
    }

    private func field<T>(_ path: WritableKeyPath<SoundSettings, T>) -> Binding<T> {
        Binding(get: { displayedSound[keyPath: path] }, set: { value in
            guard let key else { return }
            edits.capture(snapshot, for: key)
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
        var c = DateComponents(); c.hour = h
        return (Calendar.current.date(from: c) ?? Date()).formatted(.dateTime.hour())
    }

    private func soundBytes(_ wanted: SoundSettings) -> Data {
        Data([UInt8(wanted.volume), wanted.quietOn ? 1 : 0, UInt8(wanted.quietStart), UInt8(wanted.quietEnd), UInt8(wanted.quietVolume), 0])
    }

    private func save(_ wanted: SoundSettings) {
        guard let key, let base = edits.base(key) ?? snapshot else { return }
        submittedValue = wanted
        submittedToken = writer.submit(.sound, base: base, desired: soundBytes(wanted))
    }
}

struct RenameView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(EditSessions.self) var edits
    @Environment(SettingWriter.self) var writer
    let entry: RouteEntry
    @FocusState private var focused: Bool
    @State private var submittedToken: UUID?
    @State private var submittedValue: String?

    private var key: EditKey? { ble.current.map { EditKey(machine: $0.id, field: .name) } }
    private var snapshot: SettingSnapshot? { ble.settingSnapshot(.name) }
    private var standing: String { snapshot.flatMap { String(data: $0.value, encoding: .utf8) } ?? ble.current?.name ?? "" }
    private var text: Binding<String> {
        Binding(get: { writer.commit(.name).flatMap { String(data: $0.desired, encoding: .utf8) } ?? key.flatMap { edits.draft($0) } ?? ble.current?.pendingName ?? standing }, set: { value in
            if let key { edits.capture(snapshot, for: key); edits.setDraft(value, for: key) }
        })
    }
    private var trimmed: String { text.wrappedValue.trimmingCharacters(in: .whitespacesAndNewlines) }
    private var waiting: Bool { writer.commit(.name) != nil }
    private var conflict: Bool { key.flatMap(edits.base).map { base in snapshot.map { base.revision != $0.revision } ?? false } ?? false }
    private var accepted: UUID? { ble.current.flatMap { writer.accepted[FormSettingID(machine: $0.id, setting: .name)] } }

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            TextField("Name", text: text, prompt: Text(ble.current?.displayName ?? "Name"))
                .textInputAutocapitalization(.words).autocorrectionDisabled()
                .submitLabel(.done).focused($focused).onSubmit(save)
                .padding(16).background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
                .disabled(waiting || snapshot == nil)
            Note("The machine keeps its name so every device sees the same one.")
            if trimmed.utf8.count > 20 { Note("This name is too long. Try a shorter name.") }
            if snapshot == nil { Note("Connect to the machine to read its saved name.") }
            FormSaveOutcome(setting: .name, discard: { if let key { edits.discard(key) } }, submitted: { token in
                submittedToken = token
                submittedValue = text.wrappedValue
            })
            if !waiting {
                if let key, let base = edits.base(key), let current = snapshot, current.revision != base.revision {
                    DraftSettingConflict(setting: .name, base: base, desired: Data(trimmed.utf8), keepMachine: { edits.discard(key) }, submitted: { token in
                        submittedToken = token; submittedValue = text.wrappedValue
                    })
                }
                if !conflict {
                    ActionButton(title: "Save name") { save() }
                        .disabled(snapshot == nil || trimmed.isEmpty || trimmed.utf8.count > 20 || trimmed == standing)
                }
                if !conflict && key.flatMap({ edits.draft($0, as: String.self) }) != nil {
                    Button("Discard changes") { if let key { edits.discard(key) } }.frame(minHeight: 44)
                }
            }
        }
        .frame(maxWidth: 460).frame(maxWidth: .infinity)
        .onAppear { focused = true }
        .task(id: ble.canChange) { if ble.canChange { _ = await ble.readSetting(.name) } }
        .onChange(of: accepted) { _, token in
            guard let token, token == submittedToken, nav.isOpen(entry), let key, let value = submittedValue else { return }
            edits.settle(key, saved: value)
            nav.finish(entry)
        }
    }

    private func save() {
        guard let key, let base = edits.base(key) ?? snapshot, !trimmed.isEmpty, trimmed.utf8.count <= 20 else { return }
        focused = false
        submittedValue = text.wrappedValue
        submittedToken = writer.submit(.name, base: base, desired: Data(trimmed.utf8))
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
