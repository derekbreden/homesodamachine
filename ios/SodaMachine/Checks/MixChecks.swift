import Foundation

@MainActor
func runMixChecks(_ check: (Bool, String) -> Void) {
    let a = MixChanges.Key(machine: "A", channel: 0)
    let b = MixChanges.Key(machine: "B", channel: 0)
    func saved(_ revision: UInt64, _ value: Int, key: MixChanges.Key = a) -> SettingSnapshot {
        SettingSnapshot(key: key.setting, revision: revision, value: Data([UInt8(value)]))
    }
    let model = MixChanges(storageURL: nil)
    check(!model.change(a, to: 12, basedOn: nil), "An unstamped legacy reading cannot be used as an offline edit base")
    check(model.change(a, to: 12, basedOn: saved(100, 10)), "The first edit captures a previously read stamp")
    check(model.pending(a)?.base.revision == 100 && model.pending(a)?.desired == 12,
          "Pending mix stores both desired choice and its exact base")
    _ = model.change(a, to: 13, basedOn: saved(200, 10))
    check(model.pending(a)?.base.revision == 100 && model.pending(a)?.desired == 13,
          "Later taps never silently rebase on a newer reading")
    model.hold(a, phase: .held)
    check(model.pending(a)?.base.revision == 100 && model.pending(a)?.phase == .held,
          "Going out of range retains the original CAS base")
    let first = model.begin(a)!
    _ = model.change(a, to: 16, basedOn: saved(200, 10))
    check(model.begin(a) == nil, "Only one mix write may be in flight per intent")
    model.accepted(a, attempt: first, snapshot: saved(101, 13))
    check(model.pending(a)?.desired == 16 && model.pending(a)?.base.revision == 101 && model.pending(a)?.phase == .queued,
          "Known own acceptance advances the next write's base while preserving newer taps")
    let second = model.begin(a)!
    model.accepted(a, attempt: first, snapshot: saved(102, 13))
    check(model.pending(a)?.attempt?.id == second.id, "A late old answer cannot clear the current write")
    model.accepted(a, attempt: second, snapshot: saved(102, 16))
    check(model.pending(a) == nil, "The newest desired mix clears only on its own accepted answer")

    _ = model.change(a, to: 18, basedOn: saved(300, 10))
    let aba = model.begin(a)!
    model.conflicted(a, attempt: aba, snapshot: saved(302, 10))
    check(model.pending(a)?.phase == .conflict && model.pending(a)?.desired == 18,
          "ABA is detected even when the machine returned to its original value")
    _ = model.change(a, to: 19, basedOn: saved(302, 10))
    check(model.pending(a)?.phase == .conflict && model.pending(a)?.base.revision == 300,
          "Tapping again does not implicitly choose Use mine")
    model.useMine(a, against: saved(302, 10))
    let rebased = model.begin(a)!
    check(rebased.expected == 302 && rebased.desired == 19, "Use mine explicitly rebases and still performs CAS")
    model.conflicted(a, attempt: rebased, snapshot: saved(303, 11))
    check(model.pending(a)?.phase == .conflict && model.pending(a)?.desired == 19,
          "A change after Use mine produces another conflict rather than an unconditional overwrite")
    model.discard(a)
    check(model.pending(a) == nil, "Keep theirs discards the local choice without writing")

    _ = model.change(a, to: 20, basedOn: saved(400, 10))
    let unknown = model.begin(a)!
    model.failed(a, attempt: unknown, failure: .unanswered, uncertain: true)
    model.reconcileUncertain(a, snapshot: saved(401, 20))
    check(model.pending(a)?.phase == .conflict && model.pending(a)?.desired == 20,
          "An equal desired value after a lost answer is not invented own success")
    check(model.pending(a)?.conflictFromUncertainty == true
          && model.pending(a)?.problem?.contains("before confirmation") == true,
          "A possible own unconfirmed write is not falsely attributed to another device")
    model.discard(a)
    _ = model.change(a, to: 20, basedOn: saved(500, 10))
    let unchanged = model.begin(a)!
    model.failed(a, attempt: unchanged, failure: .offline, uncertain: true)
    model.reconcileUncertain(a, snapshot: saved(500, 10))
    check(model.pending(a)?.phase == .queued && model.pending(a)?.base.revision == 500,
          "An unchanged authoritative stamp permits a safe retry of the original conditional write")
    let retried = model.begin(a)!
    model.accepted(a, attempt: retried, snapshot: saved(500, 20))
    check(model.pending(a)?.phase == .uncertain,
          "A purported accepted write that did not advance its stamp cannot count as Saved")
    model.discard(a)
    _ = model.change(a, to: 12, basedOn: saved(600, 10))
    let storage = model.begin(a)!
    model.failed(a, attempt: storage, failure: .storageFailure, uncertain: false)
    check(model.pending(a)?.desired == 12 && model.pending(a)?.phase == .failed,
          "A definite storage failure retains the local choice for explicit retry")
    model.retry(a)
    check(model.pending(a)?.phase == .queued && model.pending(a)?.base.revision == 600,
          "Retry preserves the original expected stamp")
    _ = model.change(b, to: 14, basedOn: saved(900, 20, key: b))
    model.forget(machine: "A")
    check(model.pending(a) == nil && model.pending(b)?.desired == 14,
          "Removing one appliance does not erase another appliance's pending mix")

    let location = FileManager.default.temporaryDirectory.appendingPathComponent("soda-mix-check-\(UUID().uuidString)")
        .appendingPathComponent("mix.json")
    defer { try? FileManager.default.removeItem(at: location.deletingLastPathComponent()) }
    let durable = MixChanges(storageURL: location)
    _ = durable.change(a, to: 15, basedOn: saved(700, 10))
    let inFlight = durable.begin(a)!
    _ = durable.change(a, to: 17, basedOn: saved(999, 24))
    let restored = MixChanges(storageURL: location)
    check(restored.pending(a)?.desired == 17 && restored.pending(a)?.base.revision == 700,
          "App restart preserves the newest desired value and its original base stamp")
    check(restored.pending(a)?.phase == .uncertain && restored.pending(a)?.attempt?.id == inFlight.id,
          "A persisted dispatched attempt restarts as unknown rather than replaying as if unsent")
    check(!restored.change(.init(machine: "A", channel: 2), to: 15, basedOn: saved(700, 10)),
          "An invalid channel never becomes a pending machine command")
    restored.forget(machine: "A")
    check(MixChanges(storageURL: location).pending(a) == nil, "Removed-machine intents do not return on the next launch")

    _ = restored.change(a, to: 15, basedOn: saved(800, 10))
    restored.requireTrustRetry(a, outcome: 2, retryAt: Date(timeIntervalSince1970: 9000))
    let denied = MixChanges(storageURL: location)
    check(denied.pending(a)?.requiresTrustRetry == true,
          "A physical Trust denial remains explicit-retry-only after app restart")
    check(denied.pending(a)?.trustEnd == 2 && denied.pending(a)?.trustRetryAt == Date(timeIntervalSince1970: 9000),
          "A restored editor retains the physical decline and machine-supplied retry deadline")
    _ = denied.change(a, to: 16, basedOn: saved(800, 10))
    check(denied.pending(a)?.requiresTrustRetry == true,
          "Another mix tap does not silently reset the persisted permission decision")
    denied.hold(a, phase: .held)
    denied.hold(a, phase: .unsupported)
    denied.resumeCapability(a)
    check(denied.pending(a)?.phase == .queued && denied.pending(a)?.requiresTrustRetry == true,
          "Automatic capability recovery requeues transport without resetting a physical Trust decision")
    check(denied.pending(a)?.trustEnd == 2 && denied.pending(a)?.trustRetryAt == Date(timeIntervalSince1970: 9000),
          "A declined request and retry deadline survive disconnect, discovery, and supported reconnect")
    let reconnected = MixChanges(storageURL: location)
    check(reconnected.pending(a)?.requiresTrustRetry == true && reconnected.pending(a)?.trustEnd == 2,
          "The reconnect transition keeps the physical decline on disk as well as in memory")
    let deniedAttempt = denied.begin(a)!
    denied.failed(a, attempt: deniedAttempt, failure: .notTrusted, uncertain: false)
    denied.resumeCapability(a)
    check(denied.pending(a)?.phase == .failed && denied.pending(a)?.requiresTrustRetry == true,
          "A persisted permission failure is not an automatic capability retry")
    denied.permissionGranted(a)
    check(denied.pending(a)?.phase == .queued && denied.pending(a)?.requiresTrustRetry != true
          && denied.pending(a)?.trustEnd == nil && denied.pending(a)?.desired == 16,
          "Authoritative Trust can resume the same desired mix without a new edit or permission prompt")
    denied.requireTrustRetry(a, outcome: 2, retryAt: Date(timeIntervalSince1970: 9000))
    denied.retry(a)
    check(denied.pending(a)?.requiresTrustRetry != true,
          "An explicit Try again permits one new bounded permission request")
}
