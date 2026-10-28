import Foundation
import Observation

/// The app's mix synchronizer. Taps coalesce, each channel has one write in
/// flight, and the main board compares the captured base stamp atomically.
/// Navigation presents this state; it does not own its lifetime.
@MainActor
@Observable
final class MixController {
    let changes: MixChanges
    @ObservationIgnored private let ble: BLEManager
    private var context: String?
    private var foreground = false
    @ObservationIgnored private var workers: [MixChanges.Key: Task<Void, Never>] = [:]
    @ObservationIgnored private var trustBlocked: Set<MixChanges.Key> = []
    @ObservationIgnored private var editContexts: [MixChanges.Key: String] = [:]
    @ObservationIgnored private var forced: Set<MixChanges.Key> = []

    init(ble: BLEManager, changes: MixChanges = MixChanges()) {
        self.ble = ble
        self.changes = changes
    }

    var signal: [MixChanges.Pending] {
        changes.intents.values.sorted {
            $0.key.machine == $1.key.machine ? $0.key.channel < $1.key.channel : $0.key.machine < $1.key.machine
        }
    }

    func pending(channel: Int) -> MixChanges.Pending? { key(channel).flatMap(changes.pending) }
    func value(channel: Int) -> Int? {
        pending(channel: channel)?.desired ?? ble.settingSnapshot(.ratio(channel: channel))?.byte
    }

    func canEdit(channel: Int) -> Bool {
        guard (0..<2).contains(channel), ble.current != nil,
              ble.settingSnapshot(.ratio(channel: channel))?.valid == true else { return false }
        if ble.linked && ble.bridgeVersion != nil && !ble.stampedSettingsSupported { return false }
        return true
    }

    func status(channel: Int) -> String {
        guard let item = pending(channel: channel) else {
            if ble.linked && !ble.stampedSettingsSupported && !ble.demoMode { return SettingFailure.needsUpdate.message }
            return value(channel: channel) == nil ? "Waiting for the machine’s saved mix." : "Saved"
        }
        switch item.phase {
        case .queued: return "Saving your mix…"
        case .saving: return "Saving your mix…"
        case .waitingForTrust: return "Not saved · waiting for Trust on the machine."
        case .held: return "Not saved · kept here until the machine is reachable."
        case .conflict: return item.conflictFromUncertainty == true ? "Save not confirmed" : "Changed elsewhere"
        case .uncertain: return "The saved mix needs checking before this change can continue."
        case .unsupported: return SettingFailure.needsUpdate.message
        case .failed: return item.problem ?? "The mix wasn’t saved. Your choice is kept here."
        }
    }

    /// A nonnil context identifies the visible mix editor. Other destinations
    /// pass nil: trusted queued changes can sync there, but cannot summon a
    /// permission request belonging to an editor the person already left.
    func contextChanged(context: String?, foreground: Bool) {
        self.context = context
        self.foreground = foreground
        pump()
    }

    func connectionChanged() {
        if let machine = ble.current?.id {
            for item in changes.intents.values where item.key.machine == machine {
                guard item.phase != .saving && item.phase != .uncertain,
                      let current = ble.settingSnapshot(item.key.setting),
                      current.revision != item.base.revision else { continue }
                changes.conflicted(item.key, attempt: nil, snapshot: current)
                if ble.trustAsk?.reason == .ratio, ble.trustAsk?.channel == item.key.channel {
                    ble.withdrawTrustAsk()
                }
            }
        }
        if ble.trust == .trusted || ble.demoMode {
            trustBlocked = trustBlocked.filter { $0.machine != ble.current?.id }
        }
        pump()
    }

    func changed(channel: Int, to value: Int) {
        guard let key = key(channel), canEdit(channel: channel) else { return }
        if let context { editContexts[key] = context }
        guard changes.change(key, to: value, basedOn: ble.settingSnapshot(key.setting)) else { return }
        if !ble.linked && !ble.demoMode { changes.hold(key, phase: .held) }
        pump()
    }

    func retry(channel: Int) {
        guard let key = key(channel) else { return }
        trustBlocked.remove(key)
        if let context { editContexts[key] = context }
        changes.retry(key)
        Task {
            if let ask = ble.trustAsk, ask.quiet, ask.ended != nil,
               ask.reason == .ratio, ask.channel == channel {
                let outcome = await ble.retryTrustAsk()
                guard outcome == .trusted else {
                    trustBlocked.insert(key)
                    if outcome != .canceled && outcome != .lostLink {
                        changes.requireTrustRetry(key, outcome: outcome.rawValue, retryAt: ble.trustAsk?.retryAt)
                    }
                    changes.hold(key, phase: .waitingForTrust, problem: "Trust is needed before this mix can be saved.")
                    return
                }
            }
            pump()
        }
    }

    func useMine(channel: Int) {
        guard let key = key(channel), let item = changes.pending(key),
              let snapshot = ble.settingSnapshot(key.setting) ?? item.elsewhere else { return }
        changes.useMine(key, against: snapshot)
        retry(channel: channel)
    }

    func keepTheirs(channel: Int) { discard(channel: channel) }
    func discard(channel: Int) {
        guard let key = key(channel) else { return }
        changes.discard(key)
        trustBlocked.remove(key)
        editContexts[key] = nil
    }

    /// A deliberate Use-at-faucet waits for the newest mix to be accepted.
    /// It cannot select a flavor whose pending mix is offline or conflicted.
    func flush(channel: Int) async -> Bool {
        guard let key = key(channel), foreground else { return false }
        if changes.pending(key) == nil { return ble.settingSnapshot(key.setting)?.valid == true }
        forced.insert(key)
        pump()
        guard let worker = workers[key] else { forced.remove(key); return false }
        await worker.value
        forced.remove(key)
        return ble.current?.id == key.machine && changes.pending(key) == nil
    }

    private func key(_ channel: Int) -> MixChanges.Key? {
        ble.current.map { MixChanges.Key(machine: $0.id, channel: channel) }
    }

    private func pump() {
        guard foreground, let machine = ble.current?.id else { return }
        for key in changes.intents.keys.filter({ $0.machine == machine }) {
            if ble.demoMode || ble.trust == .trusted { changes.permissionGranted(key) }
            guard workers[key] == nil, let item = changes.pending(key), item.phase != .conflict && item.phase != .failed else { continue }
            guard ble.linked || ble.demoMode else { changes.hold(key, phase: .held); continue }
            // A newly connected faucet reports its bridge after the link is
            // up. Absence during discovery is not unsupported firmware.
            guard ble.demoMode || ble.bridgeVersion != nil else { continue }
            guard ble.stampedSettingsSupported else { changes.hold(key, phase: .unsupported, problem: SettingFailure.needsUpdate.message); continue }
            changes.resumeCapability(key)
            workers[key] = Task { [weak self] in
                guard let self else { return }
                await self.process(key)
                self.workers[key] = nil
            }
        }
    }

    private func process(_ key: MixChanges.Key) async {
        while foreground, ble.current?.id == key.machine, ble.linked || ble.demoMode,
              let item = changes.pending(key) {
            guard item.phase != .conflict && item.phase != .failed && ble.stampedSettingsSupported else { return }
            if item.phase == .uncertain {
                switch await ble.readSetting(key.setting) {
                case .accepted(let snapshot): changes.reconcileUncertain(key, snapshot: snapshot)
                default: return
                }
                continue
            }
            if !ble.demoMode && ble.trust != .trusted {
                changes.hold(key, phase: .waitingForTrust)
                guard !trustBlocked.contains(key), changes.pending(key)?.requiresTrustRetry != true,
                      let context, editContexts[key] == context else { return }
                let outcome = await ble.requestTrust(.ratio, channel: key.channel, quiet: true)
                guard outcome == .trusted else {
                    trustBlocked.insert(key)
                    if outcome == .declined || outcome == .timedOut || outcome == .busy || outcome == .unpaired {
                        changes.requireTrustRetry(key, outcome: outcome.rawValue, retryAt: ble.trustAsk?.retryAt)
                    }
                    return
                }
                guard foreground, ble.current?.id == key.machine else { return }
            }
            guard let latest = changes.pending(key), latest.phase != .conflict else { return }
            let delay = forced.contains(key) ? 0 : max(0, 0.4 - Date().timeIntervalSince(latest.changedAt))
            if delay > 0 {
                try? await Task.sleep(for: .milliseconds(Int(delay * 1000) + 1))
                continue // a tap during the delay starts its own coalescing interval
            }
            guard foreground, ble.current?.id == key.machine, ble.linked || ble.demoMode,
                  let attempt = changes.begin(key) else { return }
            let reply = await ble.writeSetting(key.setting, expected: attempt.expected,
                                               value: Data([UInt8(attempt.desired)]))
            switch reply {
            case .accepted(let snapshot): changes.accepted(key, attempt: attempt, snapshot: snapshot)
            case .conflict(let snapshot): changes.conflicted(key, attempt: attempt, snapshot: snapshot); return
            case .failure(let failure):
                let uncertain = failure == .unanswered || failure == .offline || failure == .malformed
                changes.failed(key, attempt: attempt, failure: failure, uncertain: uncertain)
                if failure == .notTrusted {
                    changes.hold(key, phase: .waitingForTrust, problem: failure.message)
                }
                return
            }
        }
        if let item = changes.pending(key), item.phase == .queued || item.phase == .waitingForTrust {
            changes.hold(key, phase: .held)
        }
    }
}
