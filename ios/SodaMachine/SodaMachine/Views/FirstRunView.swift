import SwiftUI

// ────────────────────────────────────────────────────────────
// A device that knows no machine: find one through the system's accessory
// sheet, or open the demo. Add a machine is the same page, over the page it
// was asked from.
// ────────────────────────────────────────────────────────────

struct FirstRunView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(MachineAccess.self) var access

    var body: some View {
        FindYourMachine(title: "Soda Machine",
                        subtitle: "Choose your flavor images, care for your machine, and keep it up to date.",
                        other: directory.demo == nil ? ("Try the demo", { ble.addDemo() }) : nil)
            .onAppear { access.clearOutcome() }
    }
}

/// Adding a machine, over the page it was asked for from. Cancel returns to
/// that page; a machine added opens.
struct AddMachineSheet: View {
    @Environment(MachineAccess.self) var access
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        FindYourMachine(title: "Add a machine", other: ("Cancel", { dismiss() }))
            .onAppear { access.clearOutcome() }
            .onChange(of: access.added) { dismiss() }
    }
}

/// Finding a machine: what the page is, the picture of where to hold the
/// device, and the button that opens Apple's sheet. In a column the button
/// stays on the screen under the words, which scroll when they need to, and
/// the picture takes the room they leave. A landscape page puts the picture
/// beside the words and the button.
struct FindYourMachine: View {
    @Environment(MachineAccess.self) var access
    let title: String
    var subtitle: String?
    /// The quieter way out, under the button.
    var other: (title: String, action: () -> Void)?

    var body: some View {
        GeometryReader { page in
            if page.size.width > page.size.height * 1.2 {
                HStack(spacing: 32) {
                    HoldAtFaucet().padding(.vertical, 24)
                    ScrollView {
                        VStack(spacing: 20) { heading; instruction; actions }
                            .padding(.vertical, 20)
                            .frame(minHeight: page.size.height)
                    }
                    .scrollBounceBehavior(.basedOnSize)
                    .frame(maxWidth: 400)
                }
                .padding(.horizontal, 24)
            } else {
                VStack(spacing: 0) {
                    GeometryReader { room in
                        ScrollView {
                            VStack(spacing: 28) {
                                heading.frame(maxWidth: 480)
                                HoldAtFaucet().frame(maxWidth: 640, maxHeight: min(max(room.size.height * 0.55, 140), 560))
                                instruction.frame(maxWidth: 480)
                            }
                            .padding(.vertical, 20)
                            .frame(maxWidth: .infinity, minHeight: room.size.height)
                        }
                        .scrollBounceBehavior(.basedOnSize)
                    }
                    actions.frame(maxWidth: 480).padding(.bottom, 8)
                }
                .padding(.horizontal, 24)
            }
        }
        .background(Theme.background.ignoresSafeArea())
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
    }

    private var heading: some View {
        VStack(spacing: 10) {
            Text(title).font(.largeTitle.weight(.semibold))
            if let subtitle {
                Text(subtitle).font(.body).foregroundStyle(Theme.textSecondary)
            }
        }
        .multilineTextAlignment(.center)
        .fixedSize(horizontal: false, vertical: true)
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isHeader)
    }

    private var instruction: some View {
        Text("Hold your \(UIDevice.current.model) up to the faucet display, the way you would at a card reader.")
            .font(.body)
            .multilineTextAlignment(.center)
            .fixedSize(horizontal: false, vertical: true)
    }

    private var actions: some View {
        VStack(spacing: 8) {
            AddOutcome()
            ActionButton(title: "Find your machine", working: access.opening) { access.add() }
                .disabled(access.opening)
            if let other {
                Button(other.title, action: other.action)
                    .font(.body.weight(.medium)).frame(minHeight: 44)
            }
        }
    }
}

/// What came of the last try: why Apple's sheet did not open, or what to try
/// when it came back empty.
struct AddOutcome: View {
    @Environment(MachineAccess.self) var access

    var body: some View {
        switch access.outcome {
        case .failed(let why)?:
            Text(why).font(.subheadline).foregroundStyle(Theme.textSecondary)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.bottom, 8)
                .accessibilityAddTraits(.updatesFrequently)
        case .nothingAdded?:
            VStack(alignment: .leading, spacing: 8) {
                Label("Hold your \(UIDevice.current.model) right next to the faucet display", systemImage: "figure.walk")
                Label("Make sure the machine is powered on", systemImage: "power")
                Label("Try turning it off and on", systemImage: "arrow.clockwise")
            }
            .font(.subheadline).foregroundStyle(Theme.textSecondary)
            .fixedSize(horizontal: false, vertical: true)
            .padding(.bottom, 8)
            .accessibilityElement(children: .combine)
        case nil:
            EmptyView()
        }
    }
}

/// A phone held to the faucet display the way people hold one at a card
/// reader, its top corner over the display and the rest toward the hand. It is
/// an outline drawing of the current faucet head, from
/// tools/install-guide/hold_scene.py, in the page's ice. The words beside it
/// say the same, so VoiceOver reads them instead.
struct HoldAtFaucet: View {
    var body: some View {
        Image("HoldAtFaucet").resizable().renderingMode(.template).scaledToFit()
            .foregroundStyle(Theme.ice)
            .frame(maxWidth: .infinity)
            .accessibilityHidden(true)
    }
}
