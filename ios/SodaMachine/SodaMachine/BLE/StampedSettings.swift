import Foundation

extension BLEManager {
    var stampedSettingsSupported: Bool {
        demoMode || ((bridgeVersion ?? 0) >= SettingsWire.minimumBridgeVersion && current?.stampedSettingsUnavailable != true)
    }

    func settingSnapshot(_ key: SettingKey) -> SettingSnapshot? { current?.settingSnapshots[key] }

    var temperatureUnit: MachineTemperatureUnit {
        if temperatureUnitUnavailable { return .fahrenheit }
        return settingSnapshot(.temperatureUnit)?.value.first.flatMap(MachineTemperatureUnit.init(rawValue:)) ?? .fahrenheit
    }

    var temperatureUnitUnavailable: Bool {
        guard linked, !demoMode else { return false }
        return bridgeMissing || bridgeVersion.map { $0 < SettingsWire.minimumBridgeVersion } == true
            || current?.stampedSettingsUnavailable == true || temperatureUnitSupportedOnLink == false
    }

    var temperatureUnitWritable: Bool {
        guard linked, stampedSettingsSupported, current?.settingStorageProblem == false,
              settingSnapshot(.temperatureUnit)?.valid == true else { return false }
        return demoMode || temperatureUnitSupportedOnLink == true
    }

    func markTemperatureUnitUnavailable() {
        temperatureUnitSupportedOnLink = false
        if current?.settingSnapshots.removeValue(forKey: .temperatureUnit) != nil { directory.touch() }
    }

    /// A status heartbeat also repairs missed unit notifications and detects a controller upgraded behind the same faucet.
    func readTemperatureUnitIfNeeded() async {
        guard demoMode || (bridgeVersion ?? 0) >= SettingsWire.minimumBridgeVersion,
              temperatureUnitQuery == nil else { return }
        let now = ProcessInfo.processInfo.systemUptime
        let interval: TimeInterval = temperatureUnitSupportedOnLink == false ? 30 : 5
        if let last = temperatureUnitLastQuery, now - last < interval { return }
        temperatureUnitLastQuery = now
        let token = UUID()
        temperatureUnitQuery = token
        _ = await readSetting(.temperatureUnit)
        if temperatureUnitQuery == token { temperatureUnitQuery = nil }
    }

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
        if case .accepted(let snapshot) = reply, snapshot.revision == expected || snapshot.value != value {
            return .failure(.malformed)
        }
        return reply
    }

    private func settingRequest(_ type: UInt8, body: Data, key: SettingKey) async -> SettingReply {
        guard let machine = current?.id, linked || demoMode else { return .failure(.offline) }
        let unitProbe = key == .temperatureUnit && type == SettingsWire.get
                          && (bridgeVersion ?? 0) >= SettingsWire.minimumBridgeVersion
        guard stampedSettingsSupported || unitProbe else { return .failure(.needsUpdate) }
        let generation = linkGeneration
        let answer = await request(type, Array(body))
        guard current?.id == machine, generation == linkGeneration else { return .failure(.offline) }
        switch answer {
        case .success(let answer):
            guard answer.type == SettingsWire.state, let state = SettingsWire.decode(answer.body),
                  state.snapshot.key == key else { return .failure(.malformed) }
            if key == .temperatureUnit, temperatureUnitSupportedOnLink == false { return .failure(.needsUpdate) }
            return state.reply
        case .failure(let error):
            let failure: SettingFailure
            switch error {
            case .offline: failure = .offline
            case .needsUpdate, .refused:
                if key == .temperatureUnit {
                    markTemperatureUnitUnavailable()
                } else {
                    current?.stampedSettingsUnavailable = true
                }
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
            if state.snapshot.key == .temperatureUnit, state.result == .invalid,
               state.snapshot.revision == 0, state.snapshot.value.isEmpty {
                markTemperatureUnitUnavailable()
                machine.stampedSettingsUnavailable = false
            } else if state.result == .storageFailure, state.snapshot.key.valid, state.snapshot.revision == 0 {
                // An unusable boot epoch invalidates every cached stamp. Fresh
                // telemetry must never be overwritten with a previous boot's values.
                machine.settingSnapshots = [:]
                machine.settingStorageProblem = true
                if state.snapshot.key == .temperatureUnit { temperatureUnitSupportedOnLink = true }
                directory.touch()
            }
            return
        }
        machine.settingStorageProblem = state.result == .storageFailure
        let snapshot = state.snapshot
        let unitChanged = snapshot.key == .temperatureUnit && machine.settingSnapshots[.temperatureUnit] != snapshot
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
        case .temperatureUnit:
            machine.stampedSettingsUnavailable = false
            temperatureUnitSupportedOnLink = true
        }
        machine.appliance = appliance
        if unitChanged { directory.save() } else { directory.touch() }
    }
}
