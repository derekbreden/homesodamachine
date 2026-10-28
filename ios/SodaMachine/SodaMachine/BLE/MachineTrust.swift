import Foundation
import UIKit
import os

private let log = Logger(subsystem: "com.derekbreden.SodaMachine", category: "Trust")

// ────────────────────────────────────────────────────────────
// Whether the machine trusts this device to change it.
//
// Every device reads the machine. Changing it takes a device the machine
// trusts, and the machine trusts one by a tap on either of its displays
// (firmware/src_faucet/phone_trust.h). The faucet says where this device
// stands each time it is asked who the machine is, and whenever that moves.
// A change it turns down for want of trust is asked for on the displays and,
// once this device is trusted, made.
// ────────────────────────────────────────────────────────────

enum TrustFrame {
    static let state: UInt8 = 0x26   // [standing][asking][outcome]
    static let ask:   UInt8 = 0x27   // [reason][channel][kind]; reason 0xFF withdraws
}

enum TrustStanding: UInt8 {
    case unpaired = 0, viewer = 1, trusted = 2
}

enum TrustOutcome: UInt8 {
    case none = 0, trusted, declined, timedOut, busy, unpaired, canceled
}

/// proto_msg.h's TRUST_FOR_*: what this device wants, so the displays can say so.
enum TrustReason: UInt8 {
    case anything = 0, flavor, ratio, image, fill, clean, prime, sound, name, update
}

/// An ask on the machine's displays from this device.
struct TrustAsk: Equatable {
    let reason: TrustReason
    let channel: Int?
    /// The ask made as the machine is set up: the Machine page mentions it,
    /// and nothing waits on it.
    let quiet: Bool
    /// How it ended, while that is shown.
    var ended: TrustOutcome?
}

extension BLEManager {
    /// What the displays call this device.
    static var deviceWord: String { UIDevice.current.userInterfaceIdiom == .pad ? "iPad" : "iPhone" }
    private var deviceKind: UInt8 { UIDevice.current.userInterfaceIdiom == .pad ? 1 : 0 }

    /// BLE_FRAME_TRUST.
    func handleTrust(_ payload: Data) {
        let b = [UInt8](payload)
        guard b.count >= 3 else { return }
        let standing = TrustStanding(rawValue: b[0]) ?? .viewer
        let outcome = TrustOutcome(rawValue: b[2]) ?? .none
        let was = trust
        trust = standing
        log.info("standing \(standing.rawValue), outcome \(outcome.rawValue)")
        if outcome != .none { finishTrustAsk(outcome) }
        if standing == .trusted, was != .trusted { pushPendingName() }
        if standing == .trusted {
            trustAskOnLink = false
        } else if trustAskOnLink, standing == .viewer {
            trustAskOnLink = false
            Task { _ = await requestTrust(.anything, quiet: true) }
        }
    }

    /// A machine just set up asks for trust as soon as it can say where this
    /// device stands.
    func askTrustOnLink() { trustAskOnLink = true }

    /// True when this device may make the change, asking first if it must.
    func ensureTrusted(_ reason: TrustReason, channel: Int? = nil) async -> Bool {
        if demoMode || trust == nil || trust == .trusted { return true }
        return await requestTrust(reason, channel: channel) == .trusted
    }

    /// Ask the machine to trust this device, and wait for how it ends. A device
    /// with no bond is asked by iOS to pair, and asks again once it has.
    func requestTrust(_ reason: TrustReason, channel: Int? = nil, quiet: Bool = false) async -> TrustOutcome {
        if demoMode || trust == .trusted { return .trusted }
        guard linked, connectedPeripheral != nil else { return .canceled }
        var (outcome, seq) = await askOnce(reason, channel: channel, quiet: quiet)
        if outcome == .unpaired, seq == trustAskSeq {
            if !quiet { trustAsk?.ended = .unpaired }
            if await pairedWithin(30), seq == trustAskSeq {
                (outcome, seq) = await askOnce(reason, channel: channel, quiet: quiet)
            }
        }
        guard seq == trustAskSeq else { return outcome }   // a later ask took its place
        switch outcome {
        case .trusted:
            trustAsk = nil
            if quiet {
                let at = Date()
                trustGrantedAt = at
                DispatchQueue.main.asyncAfter(deadline: .now() + 6) { [weak self] in
                    if self?.trustGrantedAt == at { self?.trustGrantedAt = nil }
                }
            }
        case .canceled, .none:
            trustAsk = nil
        default:
            if quiet { trustAsk = nil } else { trustAsk?.ended = outcome }
        }
        return outcome
    }

    /// Cancel on the phone: the displays let go of the ask too.
    func withdrawTrustAsk() {
        if trustAsk?.ended == nil {
            sendBLEFrame(type: TrustFrame.ask, payload: Data([0xFF, 0xFF, deviceKind]))
        }
        finishTrustAsk(.canceled)
        trustAsk = nil
    }

    /// OK on how an ask ended.
    func dismissTrustAsk() { trustAsk = nil }

    /// The link went, and the ask with it.
    func abandonTrust() {
        finishTrustAsk(.canceled)
        if trustAsk?.ended == nil { trustAsk = nil }
        trust = nil
    }

    private func askOnce(_ reason: TrustReason, channel: Int?, quiet: Bool) async -> (TrustOutcome, Int) {
        finishTrustAsk(.canceled)   // one ask at a time; this one takes its place
        trustAskSeq += 1
        let seq = trustAskSeq
        trustAsk = TrustAsk(reason: reason, channel: channel, quiet: quiet, ended: nil)
        sendBLEFrame(type: TrustFrame.ask,
                     payload: Data([reason.rawValue, channel.map { UInt8(clamping: $0) } ?? 0xFF, deviceKind]))
        let outcome = await withCheckedContinuation { (c: CheckedContinuation<TrustOutcome, Never>) in
            trustWaiting = c
            // The faucet ends every ask within a minute. This is for a link
            // that went before it could say how.
            DispatchQueue.main.asyncAfter(deadline: .now() + 75) { [weak self] in
                guard let self, self.trustAskSeq == seq else { return }
                self.finishTrustAsk(.timedOut)
            }
        }
        return (outcome, seq)
    }

    private func finishTrustAsk(_ outcome: TrustOutcome) {
        guard let waiting = trustWaiting else { return }
        trustWaiting = nil
        waiting.resume(returning: outcome)
    }

    private func pairedWithin(_ seconds: Double) async -> Bool {
        let until = Date().addingTimeInterval(seconds)
        while Date() < until {
            if trust == .viewer || trust == .trusted { return true }
            guard linked, trustAsk != nil else { return false }
            try? await Task.sleep(for: .milliseconds(500))
        }
        return false
    }
}

extension TrustAsk {
    /// What this device wants, as the overlay says it.
    var purpose: String {
        let flavor = channel.map { "Flavor \($0 + 1)" }
        switch reason {
        case .flavor: return flavor.map { "to put \($0) on tap" } ?? "to change the flavor on tap"
        case .ratio: return flavor.map { "to save \($0)'s mix" } ?? "to save a mix"
        case .image: return flavor.map { "to change \($0)'s image" } ?? "to change the flavor images"
        case .fill: return flavor.map { "to fill \($0)" } ?? "to fill a flavor"
        case .clean: return flavor.map { "to clean \($0)" } ?? "to clean a flavor"
        case .prime: return flavor.map { "to prime \($0)" } ?? "to prime a flavor"
        case .sound: return "to change the sound"
        case .name: return "to rename the machine"
        case .update: return "to update the machine"
        case .anything: return "to change settings and run cycles"
        }
    }
}
