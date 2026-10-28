import Foundation
import Observation

/// Pending mixes are appliance-owned editing intents. A value alone never
/// identifies the setting it was based on: the captured stamp detects even a
/// change away and back to the same mix while this phone was out of range.
@Observable
final class MixChanges {
    struct Key: Hashable, Codable {
        let machine: String
        let channel: Int
        var setting: SettingKey { .ratio(channel: channel) }
    }

    enum Phase: String, Codable {
        case queued, waitingForTrust, held, saving, conflict, uncertain, failed, unsupported
    }

    struct Attempt: Codable, Equatable {
        let id: UUID
        let expected: SettingRevision
        let desired: Int
    }

    struct Pending: Codable, Equatable {
        let key: Key
        var desired: Int
        var base: SettingSnapshot
        var phase = Phase.queued
        var changedAt: Date
        var attempt: Attempt?
        var elsewhere: SettingSnapshot?
        var problem: String?
        var trustEnd: UInt8?
        var trustRetryAt: Date?
        /// Optional for pending files created before this field existed.
        /// An explicit refusal must not turn into a fresh request after launch.
        var requiresTrustRetry: Bool?
        /// A moved stamp after an unanswered write might be this phone's own
        /// write. The UI must not attribute it to another person or device.
        var conflictFromUncertainty: Bool?
    }

    private(set) var intents: [Key: Pending] = [:]
    private(set) var persistenceProblem: String?
    @ObservationIgnored private let storageURL: URL?

    static var defaultStorageURL: URL {
        FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("PendingMix", isDirectory: true).appendingPathComponent("mixes.json")
    }

    init(storageURL: URL? = MixChanges.defaultStorageURL) {
        self.storageURL = storageURL
        guard let storageURL, let data = try? Data(contentsOf: storageURL),
              let saved = try? JSONDecoder().decode([Pending].self, from: data) else { return }
        for var item in saved where item.key.channel >= 0 && item.key.channel < 2
            && (6...24).contains(item.desired) && item.base.valid && item.base.key == item.key.setting {
            // A terminated app cannot know whether its last dispatched write
            // took. A read and the original stamp must settle what can follow.
            if item.phase == .saving { item.phase = .uncertain }
            intents[item.key] = item
        }
    }

    func pending(_ key: Key) -> Pending? { intents[key] }

    /// The first edit requires a stamped base already read or cached before
    /// the tap. A later read must not silently become the base of an old edit.
    @discardableResult
    func change(_ key: Key, to desired: Int, basedOn snapshot: SettingSnapshot?, at now: Date = Date()) -> Bool {
        guard (0..<2).contains(key.channel), (6...24).contains(desired) else { return false }
        if var item = intents[key] {
            guard item.desired != desired else { return true }
            item.desired = desired
            item.changedAt = now
            // A new tap cannot erase a conflict or make an unanswered attempt
            // cease to exist. The in-flight write remains serialized.
            if item.phase != .saving && item.phase != .conflict && item.phase != .uncertain {
                item.phase = .queued
                item.problem = nil
            }
            intents[key] = item
        } else {
            guard let snapshot, snapshot.valid, snapshot.key == key.setting else { return false }
            if snapshot.byte == desired { return true }
            intents[key] = Pending(key: key, desired: desired, base: snapshot, changedAt: now)
        }
        persist()
        return true
    }

    func hold(_ key: Key, phase: Phase, problem: String? = nil) {
        guard var item = intents[key], item.phase != .conflict, item.phase != .uncertain, item.phase != .saving else { return }
        item.phase = phase
        item.problem = problem
        intents[key] = item
        persist()
    }

    func begin(_ key: Key) -> Attempt? {
        guard var item = intents[key], item.attempt == nil,
              item.phase != .conflict && item.phase != .uncertain else { return nil }
        let attempt = Attempt(id: UUID(), expected: item.base.revision, desired: item.desired)
        item.attempt = attempt
        item.phase = .saving
        item.problem = nil
        intents[key] = item
        persist() // the attempt exists on disk before its bytes leave the app
        return attempt
    }

    /// Only the accepted answer to this exact attempt can advance the base
    /// automatically. A push or a later equal-value read cannot do so.
    func accepted(_ key: Key, attempt: Attempt, snapshot: SettingSnapshot) {
        guard var item = intents[key], item.attempt?.id == attempt.id else { return }
        guard snapshot.valid, snapshot.key == key.setting, snapshot.byte == attempt.desired,
              snapshot.revision != attempt.expected else {
            failed(key, attempt: attempt, failure: .malformed, uncertain: true)
            return
        }
        if item.desired == attempt.desired {
            intents[key] = nil
        } else {
            item.base = snapshot
            item.attempt = nil
            item.phase = .queued
            item.elsewhere = nil
            item.problem = nil
            item.conflictFromUncertainty = nil
            intents[key] = item
        }
        persist()
    }

    func conflicted(_ key: Key, attempt: Attempt?, snapshot: SettingSnapshot, fromUncertainty: Bool = false) {
        guard var item = intents[key], snapshot.valid, snapshot.key == key.setting else { return }
        if let attempt, item.attempt?.id != attempt.id { return }
        item.phase = .conflict
        item.attempt = nil
        item.elsewhere = snapshot
        item.conflictFromUncertainty = fromUncertainty ? true : nil
        item.problem = fromUncertainty
            ? "Save not confirmed. The machine’s mix changed before confirmation. Choose which mix to keep."
            : "Changed elsewhere. Choose which mix to keep."
        intents[key] = item
        persist()
    }

    func failed(_ key: Key, attempt: Attempt, failure: SettingFailure, uncertain: Bool) {
        guard var item = intents[key], item.attempt?.id == attempt.id else { return }
        item.phase = uncertain ? .uncertain : failure == .needsUpdate ? .unsupported : .failed
        if !uncertain { item.attempt = nil }
        item.problem = failure.message
        intents[key] = item
        persist()
    }

    /// An unanswered write is never inferred successful from matching bytes.
    /// If the original stamp still stands, another CAS is safe. If it moved,
    /// including to the desired bytes, the person must resolve the conflict.
    func reconcileUncertain(_ key: Key, snapshot: SettingSnapshot) {
        guard var item = intents[key], item.phase == .uncertain,
              snapshot.valid, snapshot.key == key.setting else { return }
        if snapshot.revision == (item.attempt?.expected ?? item.base.revision) {
            item.base = snapshot
            item.attempt = nil
            item.phase = .queued
            item.problem = nil
            intents[key] = item
            persist()
        } else {
            conflicted(key, attempt: nil, snapshot: snapshot, fromUncertainty: true)
        }
    }

    /// Use mine is the explicit rebase. The next SET is still conditional:
    /// another change after this choice will produce another conflict.
    func useMine(_ key: Key, against snapshot: SettingSnapshot) {
        guard var item = intents[key], item.phase != .saving,
              snapshot.valid, snapshot.key == key.setting else { return }
        item.base = snapshot
        item.attempt = nil
        item.phase = .queued
        item.elsewhere = nil
        item.problem = nil
        item.conflictFromUncertainty = nil
        intents[key] = item
        persist()
    }

    func retry(_ key: Key) {
        guard var item = intents[key], item.phase != .saving && item.phase != .conflict else { return }
        if item.phase != .uncertain { item.phase = .queued }
        item.problem = nil
        item.requiresTrustRetry = nil
        item.trustEnd = nil
        item.trustRetryAt = nil
        intents[key] = item
        persist()
    }

    /// A supported connection can resume transport work, but cannot turn a
    /// declined permission request into an explicit Ask again.
    func resumeCapability(_ key: Key) {
        guard var item = intents[key], item.phase == .unsupported else { return }
        item.phase = .queued
        item.problem = nil
        intents[key] = item
        persist()
    }

    /// Authoritative Trust is a different event from transport recovery.
    /// Permission failures kept by an earlier app session may continue only
    /// after this event or an explicit retry by the person.
    func permissionGranted(_ key: Key) {
        guard var item = intents[key], item.requiresTrustRetry == true || item.trustEnd != nil else { return }
        if item.phase == .failed || item.phase == .waitingForTrust {
            item.phase = .queued
            item.problem = nil
        }
        item.requiresTrustRetry = nil
        item.trustEnd = nil
        item.trustRetryAt = nil
        intents[key] = item
        persist()
    }

    func requireTrustRetry(_ key: Key, outcome: UInt8? = nil, retryAt: Date? = nil) {
        guard var item = intents[key] else { return }
        item.requiresTrustRetry = true
        item.trustEnd = outcome
        item.trustRetryAt = retryAt
        if item.phase != .conflict && item.phase != .uncertain { item.phase = .waitingForTrust }
        intents[key] = item
        persist()
    }

    func discard(_ key: Key) {
        intents[key] = nil
        persist()
    }

    func forget(machine: String) {
        intents = intents.filter { $0.key.machine != machine }
        persist()
    }

    private func persist() {
        guard let storageURL else { return }
        do {
            let ordered = intents.values.sorted {
                $0.key.machine == $1.key.machine ? $0.key.channel < $1.key.channel : $0.key.machine < $1.key.machine
            }
            let data = try JSONEncoder().encode(ordered)
            try FileManager.default.createDirectory(at: storageURL.deletingLastPathComponent(), withIntermediateDirectories: true)
            try data.write(to: storageURL, options: .atomic)
            persistenceProblem = nil
        } catch {
            persistenceProblem = "This device couldn’t keep the pending mix for a later app session."
        }
    }
}
