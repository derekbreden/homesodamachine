import SwiftUI

// ────────────────────────────────────────────────────────────
// A device that knows no machine: find one through the system's accessory
// sheet, or open the demo.
// ────────────────────────────────────────────────────────────

struct FirstRunView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(MachineAccess.self) var access
    @Environment(\.dynamicTypeSize) private var typeSize

    var body: some View {
        GeometryReader { geo in
            let wide = geo.size.width >= 650 && !typeSize.isAccessibilitySize
            ScrollView {
                FlexibleColumns(wide: wide, spacing: 36) {
                    VStack(spacing: 20) {
                        if wide {
                            Image("LaunchIcon").resizable().scaledToFit().frame(width: 160, height: 160)
                                .accessibilityHidden(true)
                        } else {
                            MarkHeader()
                        }
                        Text("Soda Machine").font(.largeTitle.weight(.semibold))
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, wide ? 32 : 0)
                } right: {
                    VStack(alignment: .leading, spacing: 24) {
                        Text("Make it yours").font(.title2.weight(.semibold))
                        Note("Choose your flavor images, care for your machine, and keep it up to date.")
                        HoldAtFaucet(height: wide ? 240 : 150)
                        Note("Hold your device up to the faucet display, the way you would at a card reader. Then choose your machine in Apple’s nearby accessory sheet.")
                        ActionButton(title: "Find your machine", working: access.opening) { access.add() }
                            .disabled(access.opening)
                        AddOutcome()
                        if directory.demo == nil {
                            Button("Try the demo") { ble.addDemo() }
                                .font(.body.weight(.medium)).frame(minHeight: 44)
                        }
                    }
                    .frame(maxWidth: 420).frame(maxWidth: .infinity)
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 20)
                .frame(minHeight: wide ? geo.size.height - 40 : nil)
            }
        }
        .background(Theme.background.ignoresSafeArea())
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
        .onAppear { access.clearOutcome() }
    }
}

/// A phone held to the faucet display the way people hold one at a card
/// reader: its top half over the display, its bottom half where the hand is.
/// The faucet is the install guide's render of the current model, on the
/// guide's white paper. On a phone it is short enough that Find your machine
/// stays on the first screen.
struct HoldAtFaucet: View {
    let height: CGFloat

    var body: some View {
        Image("HoldAtFaucet").resizable().scaledToFit()
            .frame(maxHeight: height)
            .padding(18)
            .frame(maxWidth: .infinity)
            .background(Color.white, in: RoundedRectangle(cornerRadius: 16))
            .accessibilityElement()
            .accessibilityLabel("A phone held up to the faucet display, its top half over the display")
    }
}
