import Foundation

// ────────────────────────────────────────────────────────────
// What removing a machine from this device leaves selected.
//
// Removing another machine leaves the one in use, and the page under Your
// machines, as they were. Removing the one in use selects nothing in its
// place: the person chooses among the machines left, or, with none left, sets
// one up.
// ────────────────────────────────────────────────────────────

enum AfterRemoval: Equatable {
    /// Another machine went; this one is still in use.
    case keep(String)
    /// The machine in use went; these remain to choose from.
    case choose([String])
    /// No machine remains.
    case firstRun
}

func afterRemoving(_ removed: String, current: String?, remaining: [String]) -> AfterRemoval {
    let left = remaining.filter { $0 != removed }
    if let current, current != removed, left.contains(current) { return .keep(current) }
    return left.isEmpty ? .firstRun : .choose(left)
}
