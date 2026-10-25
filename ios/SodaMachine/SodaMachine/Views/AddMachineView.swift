import SwiftUI

// ────────────────────────────────────────────────────────────
// Adding a machine.
//
// THE ONLY TIME THE PHONE LOOKS FOR STRANGERS, AND THE SYSTEM DOES THE
// LOOKING. Find opens the system's own sheet: the machine's picture, only the
// machines right next to this phone, and a tap on the one in hand, which hands
// the app that machine and no other. A machine nobody tapped is never added,
// which is what keeps a neighbour's off the list.
//
// First run is this screen with nothing behind it. Nothing asks about
// Bluetooth: the tap in the sheet is the permission, and it comes after the
// screen that says why.
// ────────────────────────────────────────────────────────────

struct AddMachineView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(MachineAccess.self) var access
    @Environment(\.dismiss) private var dismiss
    var firstRun = false

    var body: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            VStack(spacing: 0) {
                // A SHEET SAYS HOW TO LEAVE IT — except the one with nothing
                // behind it. On first run this screen is the app, and leaving
                // it would be leaving a phone that knows no machines.
                if !firstRun {
                    HStack {
                        Spacer()
                        Button("Done") { dismiss() }
                            .font(.system(size: 16))
                            .foregroundStyle(Theme.textSecondary)
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 20)
                }

                // First run is what the launch screen hands over to, and the
                // mark stays where it left it. As a sheet over a page already
                // carrying the mark it is smaller: two the same size one tap
                // apart read as one picture that moved.
                if firstRun {
                    MarkHeader()
                } else {
                    Image("LaunchIcon")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 88, height: 88)
                        .padding(.top, 28)
                        .accessibilityHidden(true)
                }

                VStack(spacing: 8) {
                    Text(firstRun ? "Soda Machine" : "Add a machine")
                        .font(.system(size: 20, weight: .medium))
                        .foregroundStyle(Theme.textPrimary)
                    Text("Choose its pictures, keep it up to date, and see how it is used.")
                        .font(.system(size: 14))
                        .foregroundStyle(Theme.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.top, 20)
                .padding(.horizontal, 32)

                Button {
                    access.add()
                } label: {
                    ZStack {
                        // The label keeps its size while the sheet is on its
                        // way, so the button does not jump under a finger.
                        Text("Find your machine")
                            .opacity(access.opening ? 0 : 1)
                        if access.opening {
                            ProgressView().tint(Theme.onAccent)
                        }
                    }
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.onAccent)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(Theme.accent)
                    .cornerRadius(10)
                }
                .disabled(access.opening)
                .accessibilityLabel("Find your machine")
                .padding(.horizontal, 32)
                .padding(.top, 24)

                // The machine's radio is in the faucet, and the sheet shows
                // only what is right next to the phone.
                Text("Hold this phone right next to the faucet.")
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
                    .padding(.top, 10)

                outcome

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
        .onAppear { access.clearOutcome() }
        // The sheet handed a machine over, and the page behind is now its.
        .onChange(of: access.added) {
            if !firstRun { dismiss() }
        }
    }

    /// What came of the last tap: why the sheet did not open, or what to try
    /// when it came back empty.
    @ViewBuilder
    private var outcome: some View {
        switch access.outcome {
        case .failed(let why)?:
            Text(why)
                .font(.system(size: 14))
                .foregroundStyle(Theme.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
                .padding(.vertical, 20)
                .accessibilityAddTraits(.updatesFrequently)
        case .nothingAdded?:
            VStack(alignment: .leading, spacing: 8) {
                Label("Hold the phone closer to the faucet", systemImage: "figure.walk")
                Label("Make sure the machine is powered on", systemImage: "power")
                Label("Try turning it off and on", systemImage: "arrow.clockwise")
            }
            .font(.system(size: 14))
            .foregroundStyle(Theme.textSecondary)
            .padding(.vertical, 20)
            .accessibilityElement(children: .combine)
        case nil:
            EmptyView()
        }
    }
}
