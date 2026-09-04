import SwiftUI

// ────────────────────────────────────────────────────────────
// What a person calls a machine.
//
// The name lives on the main board and the radio advertises it, so every
// phone and both glasses agree on it. Given here, it goes to the machine the
// moment it can hear; until then the page wears it and the record holds it.
// ────────────────────────────────────────────────────────────

struct RenameSheet: View {
    @Environment(BLEManager.self) var ble
    @Environment(\.dismiss) private var dismiss
    let machine: KnownMachine
    @State private var name: String
    @FocusState private var editing: Bool

    init(machine: KnownMachine) {
        self.machine = machine
        _name = State(initialValue: machine.name)
    }

    private var trimmed: String { name.trimmingCharacters(in: .whitespacesAndNewlines) }

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 12) {
                    TextField("Name", text: $name, prompt: Text("Kitchen"))
                        .font(.system(size: 18))
                        .foregroundStyle(Theme.textPrimary)
                        .padding(14)
                        .background(Color.white.opacity(0.10))
                        .cornerRadius(12)
                        .focused($editing)
                        .submitLabel(.done)
                        .onSubmit(save)
                        .autocorrectionDisabled()
                    if !machine.isDemo {
                        Text("Up to twenty letters. The machine keeps it, so every phone sees the same name.")
                            .font(.system(size: 13))
                            .foregroundStyle(Theme.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    Spacer()
                }
                .padding(.horizontal, 24)
                .padding(.top, 24)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("Name")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundStyle(Theme.textSecondary)
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .foregroundStyle(Theme.textSecondary)
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save", action: save)
                        .foregroundStyle(trimmed.isEmpty ? Theme.textSecondary : Theme.textPrimary)
                        .disabled(trimmed.isEmpty)
                }
            }
            .toolbarColorScheme(.dark, for: .navigationBar)
            .toolbarBackground(Theme.background, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
        }
        .onAppear { editing = true }
    }

    private func save() {
        guard !trimmed.isEmpty else { return }
        ble.rename(machine, to: trimmed)
        dismiss()
    }
}
