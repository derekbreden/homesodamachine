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
    @State private var pickingFor: Int?

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
                    // The two things only this app can do to a machine someone
                    // owns: change what it runs, and change what it looks like.
                    // Picking a face is asked per flavor, because that is the
                    // question — not "manage your pictures".
                    button("Flavor 1 Image") { pickingFor = 0 }
                    button("Flavor 2 Image") { pickingFor = 1 }
                    button("Software Update") { inFirmware = true }
                }
                .padding(.horizontal, 24)

                // Most people own one machine and never need this, so it is a
                // line of text rather than a second button competing with the
                // one thing this screen does.
                Button("Not this machine?") {
                    ble.chooseAnother()
                    inMachines = true
                }
                .font(.system(size: 14))
                .foregroundStyle(Theme.textSecondary)
                .padding(.top, 18)
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
        .sheet(isPresented: Binding(get: { pickingFor != nil },
                                    set: { if !$0 { pickingFor = nil } })) {
            if let ch = pickingFor {
                FlavorImagePicker(channel: ch)
                    .presentationBackground(Theme.background)
            }
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
