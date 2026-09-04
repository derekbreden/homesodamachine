import SwiftUI

// ────────────────────────────────────────────────────────────
// Adding a machine.
//
// THE ONLY TIME THE PHONE LOOKS FOR STRANGERS. Every other scan is for a
// machine the phone already knows. Here the radio lists what is in range and
// not yet on the phone, and one tap adds it. A machine nobody tapped is never
// added, which is what keeps a neighbour's off the list.
//
// First run is this screen with nothing behind it. The radio comes up on the
// tap that says why, which is where iOS asks about Bluetooth.
// ────────────────────────────────────────────────────────────

struct AddMachineView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(\.dismiss) private var dismiss
    var firstRun = false

    @State private var looking = false
    @State private var lookedAWhile = false

    /// In range and not on the phone.
    private var strangers: [DiscoveredMachine] {
        ble.discovered.filter { !directory.knows($0) }
    }

    var body: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            VStack(spacing: 0) {
                GlassAnimationView()
                    .frame(width: firstRun ? 200 : 120, height: firstRun ? 200 : 120)
                    .padding(.top, firstRun ? 80 : 28)
                    .accessibilityHidden(true)

                VStack(spacing: 8) {
                    Text(firstRun ? "Home Soda Machine" : "Add a machine")
                        .font(.system(size: 20, weight: .medium))
                        .foregroundStyle(Theme.textPrimary)
                    Text(looking ? "Stand near it. It will show up here."
                                 : "Choose its pictures, keep it up to date, and see how it is used.")
                        .font(.system(size: 14))
                        .foregroundStyle(Theme.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.top, 20)
                .padding(.horizontal, 32)

                if looking {
                    found
                } else {
                    Button {
                        look()
                    } label: {
                        Text("Find your machine")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(Color.white.opacity(0.15))
                            .cornerRadius(10)
                    }
                    .padding(.horizontal, 32)
                    .padding(.top, 24)
                }

                Spacer()

                if directory.demo == nil {
                    Button("Try the demo") {
                        ble.addDemo()
                        if !firstRun { dismiss() }
                    }
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
                    .padding(.bottom, 32)
                }
            }
        }
        .onAppear { if !firstRun { look() } }
        .onDisappear { ble.endBrowsing() }
        .task {
            try? await Task.sleep(nanoseconds: 12_000_000_000)
            lookedAWhile = true
        }
    }

    private func look() {
        looking = true
        ble.beginBrowsing()
    }

    @ViewBuilder
    private var found: some View {
        ScrollView {
            VStack(spacing: 10) {
                ForEach(strangers) { seen in
                    Button {
                        ble.add(seen)
                        if !firstRun { dismiss() }
                    } label: {
                        row(seen)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
        }

        if ble.radioOff {
            VStack(spacing: 8) {
                Text("Turn on Bluetooth")
                    .font(.system(size: 16, weight: .medium))
                Text("Bluetooth is how this phone reaches your machine.")
                    .font(.system(size: 14))
                    .multilineTextAlignment(.center)
            }
            .foregroundStyle(Theme.textSecondary)
            .padding(.horizontal, 32)
            .padding(.vertical, 20)
            .accessibilityElement(children: .combine)
            .accessibilityAddTraits(.updatesFrequently)
        } else if strangers.isEmpty && lookedAWhile {
            VStack(alignment: .leading, spacing: 8) {
                Label("Get closer to the machine", systemImage: "figure.walk")
                Label("Make sure it is powered on", systemImage: "power")
                Label("Try turning it off and on", systemImage: "arrow.clockwise")
            }
            .font(.system(size: 14))
            .foregroundStyle(Theme.textSecondary)
            .padding(.vertical, 20)
            .accessibilityElement(children: .combine)
        } else {
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

    private func row(_ seen: DiscoveredMachine) -> some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 3) {
                Text(seen.displayName)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                Text("\(seen.model.label) · \(seen.signal)")
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
            }
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
        .accessibilityElement(children: .combine)
        .accessibilityHint("Adds this machine")
    }
}
