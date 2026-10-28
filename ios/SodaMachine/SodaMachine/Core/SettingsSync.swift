import Foundation

/// A setting's stamp belongs to the main board. It is opaque: compare it for
/// equality, never infer ownership or success from its value or ordering.
typealias SettingRevision = UInt64

enum SettingKind: UInt8, Codable, CaseIterable {
    case ratio = 0, sound = 1, name = 2, selection = 3, art = 4
}

struct SettingKey: Hashable, Codable {
    let kind: SettingKind
    let channel: UInt8

    init(_ kind: SettingKind, channel: UInt8 = 0xFF) {
        self.kind = kind
        self.channel = channel
    }

    static func ratio(channel: Int) -> SettingKey { SettingKey(.ratio, channel: UInt8(clamping: channel)) }
    static func art(channel: Int) -> SettingKey { SettingKey(.art, channel: UInt8(clamping: channel)) }
    static let sound = SettingKey(.sound)
    static let name = SettingKey(.name)
    static let selection = SettingKey(.selection)

    var valid: Bool {
        switch kind {
        case .ratio, .art: channel < 2
        case .sound, .name, .selection: channel == 0xFF
        }
    }

    var wire: Data { Data([kind.rawValue, channel]) }

    func validValue(_ value: Data) -> Bool {
        let bytes = [UInt8](value)
        switch kind {
        case .ratio: return bytes.count == 1 && (6...24).contains(Int(bytes[0]))
        case .selection: return bytes.count == 1 && bytes[0] < 2
        case .art: return bytes.count == 1 && bytes[0] < 8
        case .sound:
            return bytes.count == 6 && bytes[0] <= 100 && bytes[1] <= 1
                && bytes[2] < 24 && bytes[3] < 24 && bytes[4] <= 100 && bytes[5] == 0
        case .name: return bytes.count <= 20 && String(data: value, encoding: .utf8) != nil
        }
    }
}

struct SettingSnapshot: Hashable, Codable {
    let key: SettingKey
    let revision: SettingRevision
    let value: Data

    var valid: Bool { key.valid && revision != 0 && key.validValue(value) }
    var byte: Int? { value.count == 1 ? value.first.map(Int.init) : nil }
}

enum SettingFailure: String, Error, Codable, Equatable {
    case offline, needsUpdate, notTrusted, unanswered, invalid, storageFailure, malformed, busy, refused, linkDown

    var message: String {
        switch self {
        case .offline: "Waiting for the machine. Your choice is kept here."
        case .needsUpdate: "Update the machine’s software to save settings from this app."
        case .notTrusted: "This device needs Trust on the machine before it can save changes."
        case .unanswered: "The machine didn’t confirm the change. Its saved setting must be checked before trying again."
        case .invalid: "The machine did not accept that setting."
        case .storageFailure: "The machine couldn’t keep that setting. Your choice is still here."
        case .malformed: "The machine did not return a usable saved setting."
        case .busy: "The machine is busy. Your choice is kept here to try again."
        case .refused: "The machine did not accept this request."
        case .linkDown: "The faucet can’t reach the rest of the machine. Your choice is kept here."
        }
    }
}

enum SettingReply: Equatable {
    case accepted(SettingSnapshot)
    case conflict(SettingSnapshot)
    case failure(SettingFailure)

    var snapshot: SettingSnapshot? {
        switch self {
        case .accepted(let snapshot), .conflict(let snapshot): snapshot
        case .failure: nil
        }
    }
}

enum SettingsWire {
    static let get: UInt8 = 0x72
    static let setIf: UInt8 = 0x73
    static let state: UInt8 = 0x74
    static let minimumBridgeVersion = 2

    enum Result: UInt8 { case accepted = 0, conflict = 1, invalid = 2, storageFailure = 3 }

    struct State: Equatable {
        let snapshot: SettingSnapshot
        let result: Result

        var reply: SettingReply {
            switch result {
            case .accepted: snapshot.valid ? .accepted(snapshot) : .failure(.malformed)
            case .conflict: snapshot.valid ? .conflict(snapshot) : .failure(.malformed)
            case .invalid: .failure(.invalid)
            case .storageFailure: .failure(.storageFailure)
            }
        }
    }

    static func get(_ key: SettingKey) -> Data? { key.valid ? key.wire : nil }

    static func set(_ key: SettingKey, expected: SettingRevision, value: Data) -> Data? {
        guard key.valid, expected != 0, key.validValue(value), value.count <= UInt8.max else { return nil }
        var data = key.wire
        data.append(contentsOf: (0..<8).map { UInt8(truncatingIfNeeded: expected >> ($0 * 8)) })
        data.append(UInt8(value.count))
        data.append(value)
        return data
    }

    static func decode(_ data: Data) -> State? {
        let bytes = [UInt8](data)
        guard bytes.count >= 12, let kind = SettingKind(rawValue: bytes[0]),
              let result = Result(rawValue: bytes[2]), bytes.count == 12 + Int(bytes[11]) else { return nil }
        let key = SettingKey(kind, channel: bytes[1])
        let revision = (0..<8).reduce(UInt64(0)) { $0 | (UInt64(bytes[3 + $1]) << ($1 * 8)) }
        let snapshot = SettingSnapshot(key: key, revision: revision, value: Data(bytes.dropFirst(12)))
        // An invalid-key response is allowed to carry no snapshot. It is a
        // refusal, not a revision that can become the base of an edit.
        guard result == .invalid || result == .storageFailure || snapshot.valid else { return nil }
        return State(snapshot: snapshot, result: result)
    }

    static func encode(_ state: State) -> Data {
        var data = state.snapshot.key.wire
        data.append(state.result.rawValue)
        data.append(contentsOf: (0..<8).map { UInt8(truncatingIfNeeded: state.snapshot.revision >> ($0 * 8)) })
        data.append(UInt8(clamping: state.snapshot.value.count))
        data.append(state.snapshot.value)
        return data
    }
}
