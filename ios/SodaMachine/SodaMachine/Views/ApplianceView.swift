import SwiftUI

// ────────────────────────────────────────────────────────────
// The appliance, as much of it as the phone speaks to today.
//
// ConfigView is built around the prototype's vocabulary — image slots, ratios,
// a rotary knob's worth of settings — and the appliance answers none of it. So
// a machine that reports itself as an appliance gets this instead: what it is,
// what it is running, and the one thing the phone can do to it.
// ────────────────────────────────────────────────────────────

struct ApplianceView: View {
    @Environment(BLEManager.self) var ble
    @State private var inFirmware = false
    @State private var inMachines = false

    var body: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            VStack(spacing: 0) {
                Spacer()

                GlassAnimationView()
                    .frame(width: 160, height: 160)
                    .accessibilityHidden(true)

                Text(ble.connectedMachine?.displayName ?? "Home Soda Machine")
                    .font(.system(size: 22, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.top, 20)
                    .padding(.horizontal, 32)

                Spacer()

                VStack(spacing: 0) {
                    button("Firmware") { inFirmware = true }
                    button("Machines") {
                        ble.chooseAnother()
                        inMachines = true
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 32)
            }
        }
        .sheet(isPresented: $inFirmware) {
            ZStack {
                Theme.background.ignoresSafeArea()
                FirmwareUpdateView()
            }
            .presentationBackground(Theme.background)
        }
        .sheet(isPresented: $inMachines) {
            MachinePickerView(onPick: { inMachines = false })
                .presentationBackground(Theme.background)
        }
    }

    private func button(_ title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 16, weight: .medium))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .foregroundStyle(Theme.textPrimary)
                .background(Color.white.opacity(0.10))
                .cornerRadius(12)
        }
        .padding(.bottom, 10)
    }
}
