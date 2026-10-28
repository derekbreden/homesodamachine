import Foundation
import Observation

struct FormSettingID: Hashable, Codable {
    let machine: String
    let setting: SettingKey
}

struct FormCommit: Equatable, Codable {
    enum Phase: String, Codable { case queued, sending, trust, conflict, uncertain, failed }
    let id: UUID
    let base: SettingSnapshot
    let desired: Data
    var phase = Phase.queued
    var current: SettingSnapshot?
    var problem: String?
    var unconfirmed: Bool?
    var trustEnd: UInt8?
    var trustRetryAt: Date?
}

/// Explicit form submissions remain owned by their setting through page and
/// connection changes. Permission is requested only with that form in front.
@Observable
final class SettingWriter {
    let ble: BLEManager
    private(set) var commits: [FormSettingID: FormCommit] = [:]
    private(set) var accepted: [FormSettingID: UUID] = [:]
    private(set) var acceptedCommits: [FormSettingID: FormCommit] = [:]
    private var visible: SettingKey?
    private var foreground = true
    @ObservationIgnored private var work: Task<Void, Never>?
    @ObservationIgnored private let storeURL: URL

    init(ble: BLEManager) {
        self.ble = ble
        let folder = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("SodaMachine", isDirectory: true)
        storeURL = folder.appendingPathComponent("form-commits.json")
        if let data = try? Data(contentsOf: storeURL),
           let saved = try? JSONDecoder().decode([FormSettingID: FormCommit].self, from: data) {
            commits = saved.mapValues { pending in
                var next = pending
                if next.phase == .sending { next.phase = .uncertain; next.unconfirmed = true }
                return next
            }
        }
    }

    func commit(_ setting: SettingKey) -> FormCommit? {
        guard let machine = ble.current?.id else { return nil }
        return commits[FormSettingID(machine: machine, setting: setting)]
    }

    @discardableResult
    func submit(_ key: SettingKey, base: SettingSnapshot, desired: Data) -> UUID? {
        guard let machine = ble.current?.id, base.key == key, key.validValue(desired) else { return nil }
        let id = FormSettingID(machine: machine, setting: key)
        let pending = FormCommit(id: UUID(), base: base, desired: desired)
        commits[id] = pending
        persist()
        poke()
        return pending.id
    }

    func contextChanged(setting: SettingKey?, foreground: Bool) {
        visible = setting
        self.foreground = foreground
        poke()
    }

    func discard(_ setting: SettingKey) {
        guard let machine = ble.current?.id else { return }
        commits[FormSettingID(machine: machine, setting: setting)] = nil
        ble.withdrawTrustAsk()
        persist()
    }

    func forget(machine: String) {
        commits = commits.filter { $0.key.machine != machine }
        accepted = accepted.filter { $0.key.machine != machine }
        acceptedCommits = acceptedCommits.filter { $0.key.machine != machine }
        persist()
    }

    func useMine(_ setting: SettingKey) {
        guard let machine = ble.current?.id, let snapshot = ble.settingSnapshot(setting),
              let old = commit(setting) else { return }
        commits[FormSettingID(machine: machine, setting: setting)] = FormCommit(id: UUID(), base: snapshot, desired: old.desired)
        persist()
        poke()
    }

    func retry(_ setting: SettingKey) {
        guard let machine = ble.current?.id else { return }
        let id = FormSettingID(machine: machine, setting: setting)
        guard var pending = commits[id], pending.phase != .conflict else { return }
        pending.phase = .queued
        pending.problem = nil
        pending.trustEnd = nil
        pending.trustRetryAt = nil
        commits[id] = pending
        persist()
        poke()
    }

    func poke() {
        guard work == nil, foreground else { return }
        work = Task { [weak self] in
            guard let self else { return }
            await self.sendNext()
            self.work = nil
        }
    }

    private func sendNext() async {
        guard foreground, let machine = ble.current?.id, ble.canChange,
              let pair = commits.first(where: {
                  $0.key.machine == machine && [.queued, .uncertain, .trust].contains($0.value.phase)
                      && (ble.demoMode || ble.trust == .trusted || visible == $0.key.setting)
              }) else { return }
        let (id, original) = pair
        func stillOwned() -> Bool { commits[id]?.id == original.id && ble.current?.id == machine && foreground }
        guard ble.stampedSettingsSupported else {
            finish(id, original.id, phase: .failed, problem: SettingFailure.needsUpdate.message); return
        }
        if ble.trust != .trusted && !ble.demoMode {
            guard visible == id.setting else { return }
            commits[id]?.phase = .trust
            let reason: TrustReason = id.setting.kind == .name ? .name : .sound
            let outcome = await ble.requestTrust(reason, quiet: true)
            guard commits[id]?.id == original.id else { return }
            guard outcome == .trusted else {
                commits[id]?.phase = outcome == .lostLink || outcome == .canceled ? .queued : .failed
                if outcome != .canceled && outcome != .lostLink {
                    commits[id]?.trustEnd = outcome.rawValue
                    commits[id]?.trustRetryAt = ble.trustAsk?.retryAt
                }
                commits[id]?.problem = ble.trustAsk?.message ?? "Trust is needed before this change can be sent."
                persist(); return
            }
        }
        guard stillOwned(), let pending = commits[id] else { return }
        if let current = ble.settingSnapshot(id.setting), current.revision != pending.base.revision {
            commits[id]?.current = current
            finish(id, original.id, phase: .conflict, problem: "Changed from another device"); return
        }
        commits[id]?.phase = .sending
        persist()
        let result = await ble.writeSetting(id.setting, expected: pending.base.revision, value: pending.desired)
        guard commits[id]?.id == original.id else { return }
        switch result {
        case .accepted:
            acceptedCommits[id] = pending
            accepted[id] = original.id
            commits[id] = nil
        case .conflict(let current):
            commits[id]?.phase = .conflict
            commits[id]?.current = current
            commits[id]?.problem = "Changed from another device"
        case .failure(let failure):
            commits[id]?.phase = failure == .unanswered || failure == .offline ? .uncertain : .failed
            if commits[id]?.phase == .uncertain { commits[id]?.unconfirmed = true }
            commits[id]?.problem = failure.message
        }
        persist()
    }

    private func finish(_ key: FormSettingID, _ token: UUID, phase: FormCommit.Phase, problem: String) {
        guard commits[key]?.id == token else { return }
        commits[key]?.phase = phase
        commits[key]?.problem = problem
        persist()
    }

    private func persist() {
        do {
            try FileManager.default.createDirectory(at: storeURL.deletingLastPathComponent(), withIntermediateDirectories: true)
            try JSONEncoder().encode(commits).write(to: storeURL, options: .atomic)
        } catch {
            // The desired value remains in memory; show that its local copy
            // cannot survive closing the app instead of claiming it was kept.
            for key in commits.keys {
                commits[key]?.problem = "This device couldn’t keep a copy. Keep the app open until the machine accepts it."
            }
        }
    }
}
