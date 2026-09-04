import SwiftUI

// ────────────────────────────────────────────────────────────
// Your machines.
//
// EVERY MACHINE THIS PHONE KNOWS, WHETHER OR NOT THE RADIO CAN HEAR IT, and
// the one the phone is pointed at. Picking one points the phone at it: the
// page behind this sheet becomes that machine's, with whatever it last said,
// and the radio goes looking for it. Most people own one machine and open
// this once, to add it. A house with the old unit boxed for return and the
// new one under the sink has two rows here, and both still say what they
// said.
// ────────────────────────────────────────────────────────────

struct YourMachinesView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(\.dismiss) private var dismiss

    @State private var adding = false
    @State private var renaming: KnownMachine?
    @State private var forgetting: KnownMachine?

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                // Re-read on a clock, because "in range" is a sighting that
                // ages and nothing else moves when a machine falls silent.
                TimelineView(.periodic(from: .now, by: 5)) { context in
                    ScrollView {
                        VStack(spacing: 10) {
                            ForEach(directory.known) { machine in
                                row(machine, at: context.date)
                            }
                            addRow
                        }
                        .padding(.horizontal, 20)
                        .padding(.vertical, 20)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("Your machines")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundStyle(Theme.textSecondary)
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                        .foregroundStyle(Theme.textSecondary)
                }
            }
            .toolbarColorScheme(.dark, for: .navigationBar)
            .toolbarBackground(Theme.background, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
        }
        .onAppear { ble.beginBrowsing() }
        .onDisappear { ble.endBrowsing() }
        .sheet(isPresented: $adding) {
            AddMachineView()
                .presentationBackground(Theme.background)
        }
        .sheet(item: $renaming) { machine in
            RenameSheet(machine: machine)
                .presentationBackground(Theme.background)
        }
        .alert("Forget \(forgetting?.displayName ?? "this machine")?",
               isPresented: Binding(get: { forgetting != nil },
                                    set: { if !$0 { forgetting = nil } })) {
            Button("Forget", role: .destructive) {
                if let m = forgetting { ble.forget(m) }
                forgetting = nil
            }
            Button("Cancel", role: .cancel) { forgetting = nil }
        } message: {
            Text("Its pictures and readings leave this phone. The machine itself is not changed.")
        }
    }

    private func row(_ machine: KnownMachine, at now: Date) -> some View {
        HStack(spacing: 0) {
            Button {
                ble.select(machine)
                dismiss()
            } label: {
                HStack(spacing: 12) {
                    VStack(alignment: .leading, spacing: 3) {
                        Text(machine.displayName)
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(Theme.textPrimary)
                        Text("\(machine.kind) · \(status(machine, at: now))")
                            .font(.system(size: 13))
                            .foregroundStyle(Theme.textSecondary)
                    }
                    Spacer()
                    if machine.id == directory.current?.id {
                        Image(systemName: "checkmark")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundStyle(Theme.textPrimary)
                    }
                }
                .padding(.leading, 16)
                .padding(.vertical, 14)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityElement(children: .combine)
            .accessibilityHint("Shows this machine")

            Menu {
                Button("Rename") { renaming = machine }
                Button("Forget", role: .destructive) { forgetting = machine }
            } label: {
                Image(systemName: "ellipsis")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(Theme.textSecondary)
                    .frame(width: 44, height: 44)
                    .contentShape(Rectangle())
            }
            .accessibilityLabel("More for \(machine.displayName)")
            .padding(.trailing, 6)
        }
        .frame(maxWidth: .infinity)
        .background(Color.white.opacity(0.08))
        .cornerRadius(12)
    }

    private var addRow: some View {
        Button { adding = true } label: {
            HStack(spacing: 12) {
                Text("Add a machine")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                Spacer()
                Image(systemName: "plus")
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundStyle(Theme.textSecondary)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .frame(maxWidth: .infinity)
            .background(Color.white.opacity(0.08))
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }

    /// What one row says about the link: the machine the phone is pointed at
    /// says what the radio is doing, any other says when it was last heard.
    private func status(_ machine: KnownMachine, at now: Date) -> String {
        if machine.isDemo { return "Always here" }
        if machine.id == directory.current?.id {
            switch ble.connectionState {
            case .connected:  return "Connected"
            case .connecting: return "Connecting…"
            default: break
            }
        }
        if let seen = machine.lastSeen, now.timeIntervalSince(seen) < 10 { return "In range" }
        if let t = machine.lastConnected { return "Last connected \(said(t))" }
        return "Never connected"
    }
}
