import Foundation

@MainActor
func runSettingsSyncChecks(_ check: (Bool, String) -> Void) {
    let ratio = SettingKey.ratio(channel: 1)
    check(SettingsWire.get(ratio) == Data([0, 1]), "Stamped ratio GET identifies kind and channel")
    let stamp: UInt64 = 0x8877665544332211
    let set = SettingsWire.set(ratio, expected: stamp, value: Data([14]))
    check(set == Data([0, 1, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 1, 14]),
          "CAS carries the full captured 64-bit stamp in little-endian order")
    let snapshot = SettingSnapshot(key: ratio, revision: stamp, value: Data([14]))
    let encoded = SettingsWire.encode(SettingsWire.State(snapshot: snapshot, result: .conflict))
    check(encoded == Data([0, 1, 1, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 1, 14]),
          "STATE layout exactly matches firmware kind/channel/result/stamp/length/value")
    check(SettingsWire.decode(encoded)?.reply == .conflict(snapshot), "A conflict preserves the current authoritative snapshot")
    check(SettingsWire.decode(SettingsWire.encode(.init(snapshot: snapshot, result: .accepted)))?.reply == .accepted(snapshot),
          "Accepted snapshots round-trip without narrowing the stamp")
    check(SettingsWire.decode(encoded.dropLast()) == nil, "A truncated setting response cannot establish a saved value")
    check(SettingsWire.decode(encoded + Data([0])) == nil, "Trailing or mismatched setting bytes are rejected")
    check(SettingsWire.get(.ratio(channel: 2)) == nil && SettingsWire.get(SettingKey(.sound, channel: 0)) == nil,
          "Channel settings and global settings use their distinct valid keys")
    check(SettingsWire.set(ratio, expected: 0, value: Data([14])) == nil,
          "A missing base stamp cannot become a blind conditional write")
    check(SettingsWire.set(ratio, expected: stamp, value: Data([5])) == nil
          && SettingsWire.set(ratio, expected: stamp, value: Data([25])) == nil,
          "Mix values stay within the appliance's 1:6 through 1:24 range")
    check(SettingsWire.set(.selection, expected: stamp, value: Data([1])) != nil
          && SettingsWire.set(.selection, expected: stamp, value: Data([2])) == nil,
          "Selection is a global one-byte channel")
    check(SettingsWire.set(.art(channel: 0), expected: stamp, value: Data([7])) != nil
          && SettingsWire.set(.art(channel: 0), expected: stamp, value: Data([8])) == nil,
          "Artwork uses the machine's eight faces")
    check(SettingsWire.set(.sound, expected: stamp, value: Data([60, 1, 22, 7, 20, 0])) != nil
          && SettingsWire.set(.sound, expected: stamp, value: Data([60, 1, 22, 7, 20, 1])) == nil,
          "Sound's setting bytes are canonical; runtime clock flags are not settings")
    check(SettingsWire.set(.name, expected: stamp, value: Data("Kitchen".utf8)) != nil
          && SettingsWire.set(.name, expected: stamp, value: Data(repeating: 65, count: 21)) == nil,
          "Machine names respect their UTF-8 byte capacity")
    check(SettingsWire.set(.name, expected: stamp, value: Data([0xFF])) == nil,
          "A name with invalid UTF-8 cannot be committed")
    let unavailable = SettingSnapshot(key: ratio, revision: 0, value: Data())
    check(SettingsWire.decode(SettingsWire.encode(.init(snapshot: unavailable, result: .storageFailure)))?.reply == .failure(.storageFailure),
          "An unavailable durable epoch reports storage failure, never a usable zero stamp")
    check(SettingsWire.decode(SettingsWire.encode(.init(snapshot: unavailable, result: .accepted))) == nil,
          "Zero-stamp success is rejected")
    let unavailableValue = SettingSnapshot(key: ratio, revision: 0, value: Data([14]))
    let unavailableWire = SettingsWire.encode(SettingsWire.State(snapshot: unavailableValue, result: .storageFailure))
    check(SettingsWire.decode(unavailableWire)?.reply == .failure(.storageFailure),
          "An unavailable boot stamp reports storage failure instead of preserving an old stamp")

}
