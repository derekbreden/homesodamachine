import Foundation
import UIKit

/// Optional fields preserve the original three-byte prefix for older clients.
enum TrustFrame {
    static let state: UInt8 = 0x26
    static let ask: UInt8 = 0x27
}

extension BLEManager {
    static var deviceWord: String { UIDevice.current.userInterfaceIdiom == .pad ? "iPad" : "iPhone" }
    private var deviceKind: UInt8 { UIDevice.current.userInterfaceIdiom == .pad ? 1 : 0 }

    func handleTrust(_ payload: Data) {
        guard let report = TrustReport(payload) else { return }
        let previous = trust
        trust = report.standing
        // Trust itself is authoritative even if an acknowledgement was lost.
        if report.standing == .trusted {
            if trustAsk != nil { completeTrust(.trusted) }
            if trustAskOnLink { sayTrusted() }
            trustAskOnLink = false
            return
        }
        if var ask = trustAsk, ask.machine == current?.id, ask.link == linkGeneration,
           report.tag == nil || report.tag == ask.tag {
            let now = Date()
            ask.retryAt = now.addingTimeInterval(Double(report.retrySeconds))
            if report.asking {
                ask.asking = true
                // The firmware owns the absolute deadline. Heartbeats only renew presence.
                let reported = now.addingTimeInterval(Double(report.remainingSeconds ?? 60))
                ask.expiresAt = min(ask.expiresAt ?? reported, reported)
            }
            trustAsk = ask
            if report.outcome != .none {
                completeTrust(report.outcome)
            } else if !report.asking && ask.asking {
                completeTrust(.timedOut)
            }
        }
        if let ask = trustAsk, ask.shouldContinuePairing(from: previous, to: report.standing),
           ask.machine == current?.id, ask.context == trustContext, trustForeground {
            trustAskOnLink = false
            Task { _ = await retryTrustAsk() }
        }
        if trustAskOnLink, report.standing == .viewer, trustContext != nil, trustForeground {
            trustAskOnLink = false
            Task { _ = await requestTrust(.anything, quiet: true) }
        }
    }

    func askTrustOnLink() { trustAskOnLink = true }

    func ensureTrusted(_ reason: TrustReason, channel: Int? = nil) async -> Bool {
        if demoMode || trust == .trusted { return true }
        return await requestTrust(reason, channel: channel) == .trusted
    }

    /// Matching callers share one request; repeated edits never restart its timer.
    func requestTrust(_ reason: TrustReason, channel: Int? = nil, quiet: Bool = false) async -> TrustOutcome {
        if demoMode || trust == .trusted { return .trusted }
        guard linked, connectedPeripheral != nil else { return .lostLink }
        guard trustForeground, trustContext != nil else { return .canceled }
        if let ask = trustAsk,
           ask.machine == current?.id, ask.link == linkGeneration, ask.context == trustContext {
            if let ended = ask.ended {
                // A decline or expired request requires a deliberate retry.
                if quiet { return ended }
                if ask.quiet { return ended }
            } else {
                return await withCheckedContinuation { trustWaiters.append($0) }
            }
        } else if trustAsk != nil {
            withdrawTrustAsk()
        }
        startTrustAttempt(reason, channel: channel, quiet: quiet)
        return await withCheckedContinuation { continuation in
            trustWaiters.append(continuation)
            sendTrustPresence()
        }
    }

    /// Explicit retry retains the original action for an overlay, or starts a
    /// fresh quiet waiter for a setting whose desired value is still held.
    func retryTrustAsk() async -> TrustOutcome {
        guard let previous = trustAsk else { return .canceled }
        guard previous.retrySeconds(at: Date()) == 0, linked, trustForeground,
              previous.machine == current?.id, previous.context == trustContext else {
            return previous.ended ?? .busy
        }
        startTrustAttempt(previous.reason, channel: previous.channel, quiet: previous.quiet)
        return await withCheckedContinuation { continuation in
            trustWaiters.append(continuation)
            sendTrustPresence()
        }
    }

    /// Stable page identity; inactive is intentionally excluded (Pair is a
    /// system sheet). Only background or leaving the owning page withdraws.
    func setTrustContext(_ context: String?, foreground: Bool) {
        let left = trustContext != context || !foreground
        trustContext = context
        trustForeground = foreground
        if left, trustAsk != nil { withdrawTrustAsk() }
        if trustAskOnLink, foreground, context != nil, trust == .viewer {
            trustAskOnLink = false
            Task { _ = await requestTrust(.anything, quiet: true) }
        }
    }

    func withdrawTrustAsk() {
        if let ask = trustAsk, ask.ended == nil, linked {
            sendBLEFrame(type: TrustFrame.ask, payload: Data([0xFF, 0xFF, deviceKind, 1, ask.tag]))
        }
        trustPulse?.cancel()
        trustPulse = nil
        resumeTrustWaiters(.canceled)
        trustAsk = nil
    }

    func dismissTrustAsk() { withdrawTrustAsk() }

    func clearTrustContext() {
        withdrawTrustAsk()
        trustAskSeq += 1
        trustAskOnLink = false
        trustGrantedAt = nil
    }

    func abandonTrust() {
        completeTrust(.lostLink)
        trust = nil
    }

    private func startTrustAttempt(_ reason: TrustReason, channel: Int?, quiet: Bool) {
        trustPulse?.cancel()
        trustAskSeq += 1
        let seq = trustAskSeq
        trustAsk = TrustAsk(reason: reason, channel: channel, quiet: quiet,
                            machine: current?.id ?? "", link: linkGeneration,
                            context: trustContext, tag: UInt8(seq % 255 + 1), sentAt: Date())
        trustPulse = Task { [weak self] in
            var ticks = 0
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(1))
                guard !Task.isCancelled, let self, self.trustAskSeq == seq,
                      let ask = self.trustAsk, ask.ended == nil else { return }
                guard self.linked, ask.link == self.linkGeneration else {
                    self.completeTrust(.lostLink); return
                }
                guard self.trustForeground, ask.context == self.trustContext else {
                    self.withdrawTrustAsk(); return
                }
                let now = Date()
                if let deadline = ask.expiresAt, now >= deadline.addingTimeInterval(2) {
                    self.completeTrust(.timedOut); return
                }
                if now.timeIntervalSince(ask.sentAt) >= 65 {
                    self.completeTrust(.timedOut); return
                }
                ticks += 1
                if ticks % 5 == 0 { self.sendTrustPresence() }
            }
        }
    }

    private func sendTrustPresence() {
        guard let ask = trustAsk, ask.ended == nil, linked else { return }
        sendBLEFrame(type: TrustFrame.ask,
                     payload: Data([ask.reason.rawValue, ask.channel.map { UInt8(clamping: $0) } ?? 0xFF,
                                    deviceKind, 1, ask.tag]))
    }

    private func completeTrust(_ outcome: TrustOutcome) {
        guard var ask = trustAsk else { return }
        if outcome == .timedOut, ask.ended == nil, linked {
            sendBLEFrame(type: TrustFrame.ask, payload: Data([0xFF, 0xFF, deviceKind, 1, ask.tag]))
        }
        trustPulse?.cancel()
        trustPulse = nil
        ask.asking = false
        ask.ended = outcome
        trustAsk = ask
        if outcome == .trusted {
            resumeTrustWaiters(.trusted)
            trustAsk = nil
            sayTrusted()
        } else if ask.quiet || outcome == .lostLink || outcome == .canceled {
            resumeTrustWaiters(outcome)
        }
        // The overlay retains its action while a decline/expiry is explained.
        // Ask again resumes that same action once; Cancel ends it.
    }

    private func resumeTrustWaiters(_ outcome: TrustOutcome) {
        let waiters = trustWaiters
        trustWaiters.removeAll()
        for waiter in waiters { waiter.resume(returning: outcome) }
    }

    private func sayTrusted() {
        let at = Date()
        trustGrantedAt = at
        DispatchQueue.main.asyncAfter(deadline: .now() + 6) { [weak self] in
            if self?.trustGrantedAt == at { self?.trustGrantedAt = nil }
        }
    }
}
