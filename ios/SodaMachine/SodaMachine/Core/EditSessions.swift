import Foundation
import Observation

// ────────────────────────────────────────────────────────────
// What a person is changing, kept above the pages that show it.
//
// A draft belongs to one machine and one setting: a flavor's mix, the sound,
// the name, the image a flavor is to wear. It outlives the page that made it —
// Back, a child page, another destination, a window that changes shape — and
// ends only with Discard changes or a save the machine accepted. Each
// machine's drafts are its own, and none outlives the running app.
//
// A save is a write with a token. Its answer lands only while it is still the
// newest write for that setting, so a late answer never clears a newer draft
// or speaks over a newer write.
// ────────────────────────────────────────────────────────────

enum EditField: Hashable {
    case ratio(channel: Int)
    case sound
    case name
    case image(channel: Int)
}

struct EditKey: Hashable {
    let machine: String
    let field: EditField
}

@Observable
final class EditSessions {
    /// How the newest write for a setting stands.
    struct Write: Equatable {
        let token: UUID
        var running = true
        /// What went wrong, said beside the draft it leaves standing.
        var problem: String?
        /// What went right, where that needs saying.
        var note: String?
    }

    private var drafts: [EditKey: AnyHashable] = [:]
    private var writes: [EditKey: Write] = [:]
    private var bases: [EditKey: SettingSnapshot] = [:]

    func draft<Value: Hashable>(_ key: EditKey, as type: Value.Type = Value.self) -> Value? {
        drafts[key]?.base as? Value
    }

    /// A choice made on the page. Whatever the last finished write said about
    /// the choice before it no longer applies.
    func setDraft<Value: Hashable>(_ value: Value?, for key: EditKey) {
        drafts[key] = value.map { AnyHashable($0) }
        if writes[key]?.running == false { writes[key] = nil }
    }

    func capture(_ snapshot: SettingSnapshot?, for key: EditKey) {
        if bases[key] == nil { bases[key] = snapshot }
    }

    func base(_ key: EditKey) -> SettingSnapshot? { bases[key] }

    /// Discard changes: the confirmed value stands again.
    func discard(_ key: EditKey) {
        drafts[key] = nil
        writes[key] = nil
        bases[key] = nil
    }

    /// A write starts, superseding any earlier one for the same setting.
    func begin(_ key: EditKey) -> UUID {
        let token = UUID()
        writes[key] = Write(token: token)
        return token
    }

    func isNewest(_ token: UUID, for key: EditKey) -> Bool { writes[key]?.token == token }

    /// How a write ended. Nothing, for one a newer write has superseded.
    func end(_ token: UUID, for key: EditKey, problem: String? = nil, note: String? = nil) {
        guard isNewest(token, for: key) else { return }
        writes[key]?.running = false
        writes[key]?.problem = problem
        writes[key]?.note = note
    }

    /// The machine accepted `saved`. A draft still holding it is done; one
    /// changed since stays.
    func settle<Value: Hashable>(_ key: EditKey, saved: Value) {
        if draft(key, as: Value.self) == saved { drafts[key] = nil; bases[key] = nil }
    }

    func write(_ key: EditKey) -> Write? { writes[key] }
    func working(_ key: EditKey) -> Bool { writes[key]?.running == true }

    /// A machine removed from this device takes its drafts with it.
    func forget(machine: String) {
        drafts = drafts.filter { $0.key.machine != machine }
        writes = writes.filter { $0.key.machine != machine }
        bases = bases.filter { $0.key.machine != machine }
    }
}
