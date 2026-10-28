import SwiftUI

// ────────────────────────────────────────────────────────────
// A change waiting on the machine to trust this device: the machine asks on
// both of its displays, and this says so until one of them is tapped. How an
// ask ended other than Trust stays up until it is read.
// ────────────────────────────────────────────────────────────

struct TrustAskOverlay: View {
    @Environment(BLEManager.self) var ble
    let ask: TrustAsk

    var body: some View {
        ZStack {
            Color.black.opacity(0.45).ignoresSafeArea()
                .accessibilityHidden(true)
            VStack(spacing: 18) {
                Image(systemName: ask.ended == nil ? "hand.tap" : "hand.raised")
                    .font(.system(size: 40, weight: .light))
                    .foregroundStyle(Theme.accent)
                    .accessibilityHidden(true)
                Text(title).font(.title3.weight(.semibold))
                Note(message)
                if ask.ended == nil {
                    ProgressView().tint(Theme.accent)
                    ActionButton(title: "Cancel", primary: false) { ble.withdrawTrustAsk() }
                } else {
                    ActionButton(title: "OK") { ble.dismissTrustAsk() }
                }
            }
            .multilineTextAlignment(.center)
            .padding(24)
            .frame(maxWidth: 420)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
            .padding(24)
            .accessibilityElement(children: .contain)
            .accessibilityAddTraits(.isModal)
        }
    }

    private var device: String { BLEManager.deviceWord }

    private var title: String {
        switch ask.ended {
        case nil: "Tap Trust on the machine"
        case .unpaired?: "Tap Pair on this \(device)"
        case .declined?: "Not trusted"
        case .timedOut?: "No answer"
        case .busy?: "The machine is asking about another device"
        default: "Nothing changed"
        }
    }

    private var message: String {
        switch ask.ended {
        case nil: "The faucet and the main display are asking whether to trust this \(device) \(ask.purpose)."
        case .unpaired?: "This \(device) hasn’t paired with the machine. When it asks, tap Pair, and the machine asks for Trust next."
        case .declined?: "Someone tapped Don’t Trust on the machine. Nothing changed."
        case .timedOut?: "No one tapped Trust on the machine. Nothing changed."
        case .busy?: "Try again in a moment. Nothing changed."
        default: ""
        }
    }
}
