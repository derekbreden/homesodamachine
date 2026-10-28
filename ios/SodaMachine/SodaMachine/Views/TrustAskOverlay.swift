import SwiftUI

/// Used in an editor's fixed outcome area and by commands awaiting permission.
struct TrustStatusView: View {
    @Environment(BLEManager.self) var ble
    let ask: TrustAsk
    var offersClose = true
    var retry: (() -> Void)?

    var body: some View {
        TimelineView(.periodic(from: .now, by: 1)) { tick in
            VStack(alignment: .leading, spacing: 12) {
                Label(ask.title, systemImage: ask.symbol)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(ask.ended == .declined ? Theme.accent : Theme.textPrimary)
                Text(ask.message).font(.subheadline).foregroundStyle(Theme.textSecondary)
                if ask.asking, ask.ended == nil {
                    Text("Request ends in \(ask.remainingSeconds(at: tick.date)) seconds")
                        .font(.caption.monospacedDigit()).foregroundStyle(Theme.textSecondary)
                }
                HStack(spacing: 20) {
                    if ask.ended != nil {
                        let seconds = ask.retrySeconds(at: tick.date)
                        Button(seconds > 0 ? "Ask again in \(seconds)s" : "Ask again") {
                            if let retry { retry() }
                            else { Task { _ = await ble.retryTrustAsk() } }
                        }
                        .disabled(seconds > 0 || !ble.linked)
                    }
                    if ask.ended == nil || offersClose {
                        Button(ask.ended == nil ? "Cancel request" : "Close") { ble.withdrawTrustAsk() }
                    }
                }
                .font(.subheadline.weight(.semibold)).frame(minHeight: 44)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .accessibilityElement(children: .contain)
        }
    }
}

struct TrustAskOverlay: View {
    let ask: TrustAsk

    var body: some View {
        ZStack {
            Color.black.opacity(0.45).ignoresSafeArea().accessibilityHidden(true)
            TrustStatusView(ask: ask)
                .padding(24)
                .frame(maxWidth: 420)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 20))
                .padding(24)
                .accessibilityAddTraits(.isModal)
        }
    }
}

extension TrustAsk {
    var title: String {
        switch ended {
        case nil: asking ? "Tap Trust on the machine" : "Requesting Trust…"
        case .unpaired?: "Pair this \(BLEManager.deviceWord) first"
        case .declined?: "Trust was declined"
        case .timedOut?: "Trust request expired"
        case .busy?: "Trust request is waiting"
        case .lostLink?: "Connection lost"
        case .canceled?: "Trust request canceled"
        default: "Trust needed"
        }
    }

    var symbol: String {
        switch ended {
        case .declined?: "exclamationmark.octagon.fill"
        case .lostLink?: "antenna.radiowaves.left.and.right.slash"
        case .timedOut?: "clock.badge.exclamationmark"
        case .busy?: "hourglass"
        case nil: asking ? "exclamationmark.triangle.fill" : "arrow.triangle.2.circlepath"
        default: "hand.raised"
        }
    }

    var message: String {
        switch ended {
        case nil:
            asking
                ? "Tap Trust on a machine display \(purpose). On the enclosure, open Phone request first."
                : "Waiting for the machine to confirm that it is asking \(purpose)."
        case .unpaired?: "Accept the Bluetooth pairing request on this \(BLEManager.deviceWord), then ask again."
        case .declined?: "Someone tapped Don’t Trust on the machine. Your changes are kept on this \(BLEManager.deviceWord). The app will ask again only when you choose."
        case .timedOut?: "The machine is no longer asking. Your changes are kept here. Ask again when you are at the machine."
        case .busy?: "Another request or the machine’s retry delay is in progress. Your changes are kept here."
        case .lostLink?: "Your changes are kept here. Bring this \(BLEManager.deviceWord) near the machine to reconnect."
        default: "Your changes are kept here."
        }
    }
}

/// The physical decision remains visible after leaving and returning to an
/// editor, even though its live request was withdrawn with that page.
struct KeptTrustOutcome: View {
    @Environment(BLEManager.self) var ble
    let outcome: UInt8
    let retryAt: Date?
    var retry: () -> Void

    var body: some View {
        TimelineView(.periodic(from: .now, by: 1)) { tick in
            let seconds = max(0, Int(ceil((retryAt ?? tick.date).timeIntervalSince(tick.date))))
            VStack(alignment: .leading, spacing: 10) {
                Label(outcome == TrustOutcome.declined.rawValue ? "Trust was declined" : "Trust request ended",
                      systemImage: "exclamationmark.triangle.fill").font(.headline)
                Note(outcome == TrustOutcome.declined.rawValue
                     ? "Someone tapped Don’t Trust on the machine. Your change is kept on this device."
                     : "Your change is kept here. Ask again when you are at the machine.")
                Button(seconds > 0 ? "Ask again in \(seconds)s" : "Ask again", action: retry)
                    .frame(minHeight: 44).disabled(seconds > 0 || !ble.linked)
            }
        }
    }
}
