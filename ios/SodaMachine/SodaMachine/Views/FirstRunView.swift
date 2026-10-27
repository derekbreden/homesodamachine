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
                        ActionButton(title: "Find your machine", working: access.opening) { access.add() }
                            .disabled(access.opening)
                        Note("Hold your device right next to the faucet. Choose your machine in Apple’s nearby accessory sheet.")
                        outcome
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

    @ViewBuilder private var outcome: some View {
        switch access.outcome {
        case .failed(let why)?:
            Note(why)
                .accessibilityAddTraits(.updatesFrequently)
        case .nothingAdded?:
            VStack(alignment: .leading, spacing: 8) {
                Label("Hold your device closer to the faucet", systemImage: "figure.walk")
                Label("Make sure the machine is powered on", systemImage: "power")
                Label("Try turning it off and on", systemImage: "arrow.clockwise")
            }
            .font(.subheadline).foregroundStyle(Theme.textSecondary)
            .accessibilityElement(children: .combine)
        case nil:
            EmptyView()
        }
    }
}
