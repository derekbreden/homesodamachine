import SwiftUI

// ────────────────────────────────────────────────────────────
// Which machine this phone is pointed at.
//
// Shown when more than one is in range and none of them is the one picked last
// time, and reachable from Settings at any point after that. Two machines a
// metre apart are told apart here by name, by unit, and by which is closer.
// ────────────────────────────────────────────────────────────

struct MachinePickerView: View {
    @Environment(BLEManager.self) var ble
    var onPick: (() -> Void)? = nil

    var body: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            VStack(spacing: 0) {
                VStack(spacing: 6) {
                    Text("Which machine?")
                        .font(.system(size: 22, weight: .semibold))
                        .foregroundStyle(Theme.textPrimary)
                    Text("Pick the one you're standing at.")
                        .font(.system(size: 14))
                        .foregroundStyle(Theme.textSecondary)
                }
                .padding(.top, 32)
                .padding(.bottom, 20)

                ScrollView {
                    VStack(spacing: 10) {
                        ForEach(ble.discovered) { machine in
                            Button {
                                ble.connect(to: machine)
                                onPick?()
                            } label: {
                                row(machine)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 20)
                }

                HStack(spacing: 6) {
                    ProgressView().scaleEffect(0.7).tint(Theme.textSecondary)
                    Text("Still looking")
                        .font(.system(size: 13))
                        .foregroundStyle(Theme.textSecondary)
                }
                .padding(.vertical, 20)
                .accessibilityHidden(true)
            }
        }
    }

    private func row(_ machine: DiscoveredMachine) -> some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 3) {
                Text(machine.displayName)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                Text(machine.subtitle)
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
            }
            Spacer()
            if machine.id == ble.rememberedMachineID {
                Text("last used")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(Theme.textSecondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.white.opacity(0.10))
                    .cornerRadius(6)
            }
            Image(systemName: "chevron.right")
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(Theme.textSecondary)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
        .frame(maxWidth: .infinity)
        .background(Color.white.opacity(0.08))
        .cornerRadius(12)
        .accessibilityElement(children: .combine)
        .accessibilityHint("Connects to this machine")
    }
}
