import SwiftUI

// ────────────────────────────────────────────────────────────
// Your machines: every machine this device knows, managed from a place that
// belongs to the device rather than to any one machine.
//
// Open opens a machine's overview and closes Your machines, the machine in use
// included. Remove takes a machine off this device without opening it first.
// Removing the machine in use leaves none in use: Your machines stays open,
// and the person opens one of the rest, or, with none left, sets one up.
// ────────────────────────────────────────────────────────────

struct MachinesSheet: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(MachineAccess.self) var access
    @Environment(Navigator.self) var nav
    @State private var removing: KnownMachine?
    @State private var adding = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    Text("Your machines").font(.title2.weight(.semibold))
                    Spacer(minLength: 12)
                    Button("Done") { nav.managing = false }.font(.body.weight(.semibold)).frame(minHeight: 44)
                }
                if directory.known.isEmpty {
                    Note("No machines are on this device. Add one here, or close this to set one up.")
                } else {
                    if directory.current == nil { Note("No machine is open. Open the one you want to use.") }
                    TimelineView(.periodic(from: .now, by: 5)) { context in
                        GroupedPanel {
                            ForEach(Array(directory.known.enumerated()), id: \.element.id) { index, machine in
                                row(machine, at: context.date)
                                if index < directory.known.count - 1 { RowDivider(inset: 0) }
                            }
                        }
                    }
                }
                if let why = access.removalProblem { Note(why) }
                ActionButton(title: "Add a machine", primary: false) { adding = true }
                    .disabled(ble.transferInFlight || nav.locked)
                if ble.transferInFlight {
                    Note("Finish sending to \(ble.current?.displayName ?? "this machine") before opening or adding another.")
                }
                Note("A machine’s name is shared by every device that connects to it.")
            }
            .frame(maxWidth: 560).frame(maxWidth: .infinity)
            .padding(24)
        }
        .background(Theme.background.ignoresSafeArea())
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
        .onAppear { ble.beginBrowsing() }
        .onDisappear { ble.endBrowsing() }
        .sheet(isPresented: $adding) { AddMachineSheet() }
        .confirmationDialog("Remove \(removing.map(directory.label) ?? "this machine") from this device?",
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
        let inUse = machine.id == directory.current?.id
        return HStack(spacing: 12) {
            Button { open(machine) } label: {
                HStack(spacing: 12) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(directory.label(for: machine)).font(.body.weight(.medium))
                        Text(subtitle(machine, at: now)).font(.caption).foregroundStyle(Theme.textSecondary)
                    }
                    Spacer(minLength: 8)
                    if inUse {
                        Image(systemName: "checkmark").font(.body.weight(.semibold)).foregroundStyle(Theme.accent)
                    }
                    Text("Open").font(.subheadline.weight(.semibold)).foregroundStyle(Theme.accent)
                }
                .padding(.vertical, 16)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .disabled(nav.locked || ble.transferInFlight)
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Open \(directory.label(for: machine))\(inUse ? ", in use" : "")")
            Button { ask(remove: machine) } label: {
                Image(systemName: "trash").frame(width: 44, height: 44)
            }
            .buttonStyle(.plain)
            .foregroundStyle(Theme.error)
            .disabled(inUse && (nav.locked || ble.transferInFlight))
            .accessibilityLabel("Remove \(directory.label(for: machine))")
        }
    }

    /// Deliberate, even for the machine in use: its overview, and this closes.
    private func open(_ machine: KnownMachine) {
        nav.managing = false
        if directory.current?.id == machine.id { nav.reset() } else { ble.select(machine) }
    }

    /// A machine the system handed over is removed by the system, which asks
    /// first; this asks about any other.
    private func ask(remove machine: KnownMachine) {
        if machine.accessoryID != nil { access.forget(machine) } else { removing = machine }
    }

    /// The unit tells two machines nobody has named apart; one with no unit
    /// says what kind it is.
    private func subtitle(_ machine: KnownMachine, at now: Date) -> String {
        if machine.isDemo { return "Demo · Always here" }
        if !machine.supported { return "Prototype · \(status(machine, at: now))" }
        let who = machine.unit.isEmpty ? machine.kind : "Unit \(machine.unit)"
        return "\(who) · \(status(machine, at: now))"
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
}

/// Machines on this device, and none in use: the person opens one.
struct ChooseMachineView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(Navigator.self) var nav
    @State private var adding = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Choose a machine").font(.largeTitle.weight(.semibold))
                Note("Open the machine you want to use.")
                GroupedPanel {
                    ForEach(Array(directory.known.enumerated()), id: \.element.id) { index, machine in
                        SettingsRow(title: directory.label(for: machine),
                                    detail: machine.isDemo ? "Demo" : machine.supported ? nil : "Prototype") {
                            ble.select(machine)
                        }
                        if index < directory.known.count - 1 { RowDivider() }
                    }
                }
                ActionButton(title: "Add a machine", primary: false) { adding = true }
                Button("Your machines") { nav.managing = true }
                    .font(.body.weight(.medium)).frame(minHeight: 44)
            }
            .frame(maxWidth: 560).frame(maxWidth: .infinity)
            .padding(24)
        }
        .background(Theme.background.ignoresSafeArea())
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
        .sheet(isPresented: $adding) { AddMachineSheet() }
    }
}
