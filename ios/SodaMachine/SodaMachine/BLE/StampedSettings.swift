import Foundation

extension BLEManager {
    var stampedSettingsSupported: Bool {
        demoMode || ((bridgeVersion ?? 0) >= SettingsWire.minimumBridgeVersion && current?.stampedSettingsUnavailable != true)
    }

    func settingSnapshot(_ key: SettingKey) -> SettingSnapshot? { current?.settingSnapshots[key] }

    /// A read never changes the base of an existing pending edit. Its result
    /// is available for a new edit or explicit conflict resolution.
    func readSetting(_ key: SettingKey) async -> SettingReply {
        guard let body = SettingsWire.get(key) else { return .failure(.invalid) }
        return await settingRequest(SettingsWire.get, body: body, key: key)
    }

    /// Trust is obtained by the context that owns the change. This does not
    /// retry through a global permission prompt or fall back to a blind write.
    func writeSetting(_ key: SettingKey, expected: SettingRevision, value: Data) async -> SettingReply {
        guard let body = SettingsWire.set(key, expected: expected, value: value) else { return .failure(.invalid) }
        let reply = await settingRequest(SettingsWire.setIf, body: body, key: key)
        if case .accepted(let snapshot) = reply, snapshot.revision == expected { return .failure(.malformed) }
        return reply
    }

    private func settingRequest(_ type: UInt8, body: Data, key: SettingKey) async -> SettingReply {
        guard let machine = current?.id, linked || demoMode else { return .failure(.offline) }
        guard stampedSettingsSupported else { return .failure(.needsUpdate) }
        let answer = await request(type, Array(body))
        guard current?.id == machine else { return .failure(.offline) }
        switch answer {
        case .success(let answer):
            guard answer.type == SettingsWire.state, let state = SettingsWire.decode(answer.body),
                  state.snapshot.key == key else { return .failure(.malformed) }
            return state.reply
        case .failure(let error):
            let failure: SettingFailure
            switch error {
            case .offline: failure = .offline
            case .needsUpdate, .refused:
                current?.stampedSettingsUnavailable = true
                failure = .needsUpdate
            case .noAnswer: failure = .unanswered
            case .untrusted: failure = .notTrusted
            case .busy: failure = .busy
            case .linkDown: failure = .linkDown
            case .rejected: failure = .refused
            }
            return .failure(failure)
        }
    }

    /// Both a request reply and an unsolicited push carry the main board's
    /// snapshot. Values used by the existing screens follow this same truth.
    func takeSettingState(_ body: Data) {
        guard let state = SettingsWire.decode(body), let machine = current else { return }
        guard state.snapshot.valid else {
            if state.result == .storageFailure, state.snapshot.key.valid, state.snapshot.revision == 0 {
                // An unusable boot epoch invalidates every cached stamp. Fresh
                // telemetry must never be overwritten with a previous boot's values.
                machine.settingSnapshots = [:]
                machine.settingStorageProblem = true
                directory.touch()
            }
            return
        }
        machine.settingStorageProblem = state.result == .storageFailure
        let snapshot = state.snapshot
        machine.settingSnapshots[snapshot.key] = snapshot
        var appliance = machine.appliance
        let now = Date()
        switch snapshot.key.kind {
        case .ratio:
            var status = appliance.status?.value ?? MachineStatus()
            status.ratios[Int(snapshot.key.channel)] = snapshot.byte!
            appliance.status = Reading(value: status, at: appliance.status?.at ?? now)
        case .sound:
            if var sound = SoundSettings(snapshot.value) {
                sound.clockSet = appliance.sound?.value.clockSet ?? false
                sound.quietNow = appliance.sound?.value.quietNow ?? false
                appliance.sound = Reading(value: sound, at: now)
            }
        case .name:
            machine.name = String(data: snapshot.value, encoding: .utf8) ?? ""
            if machine.pendingName == machine.name { machine.pendingName = nil }
        case .selection:
            appliance.selection = Reading(value: FlavorSelection(channel: snapshot.byte!, persisted: true), at: now)
        case .art:
            machine.flavorArt.art[Int(snapshot.key.channel)] = snapshot.byte!
        }
        machine.appliance = appliance
        directory.touch()
    }
}
