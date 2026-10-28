import Foundation
import Observation

// ────────────────────────────────────────────────────────────
// Where someone is: a destination, and on each a stack of pages.
//
// Each opening of a page is its own entry. A task that finishes late closes
// only the entry that started it, and only while that entry is still on top of
// its own stack: never a later opening of the same page, never a page on
// another destination, and never a page of another machine, whose stacks are
// gone once the machine changes.
// ────────────────────────────────────────────────────────────

enum AppTab: String, CaseIterable {
    case machine, care, settings

    var title: String {
        switch self {
        case .machine: "Machine"
        case .care: "Care"
        case .settings: "Settings"
        }
    }

    var icon: String {
        switch self {
        case .machine: "drop"
        case .care: "sparkles"
        case .settings: "slider.horizontal.3"
        }
    }
}

enum AppRoute: Hashable {
    case flavor(Int)
    case images(Int)
    case fill(Int)
    case clean(Int)
    case prime(Int)
    case sound
    case update
    case rename
}

/// One opening of a page.
struct RouteEntry: Hashable, Identifiable {
    let id: UUID
    let route: AppRoute

    init(_ route: AppRoute) {
        id = UUID()
        self.route = route
    }
}

@Observable
final class Navigator {
    private(set) var tab = AppTab.machine
    private var stacks: [AppTab: [RouteEntry]] = [:]
    /// A run on the machine that a page is minding: the destinations, Back,
    /// the edge swipe and the machine menu wait for it.
    var locked = false
    /// Your machines, open over whatever is showing. It belongs to the device
    /// rather than to a machine, so choosing or removing one leaves it open.
    var managing = false

    func path(on tab: AppTab) -> [RouteEntry] { stacks[tab] ?? [] }

    /// The stack's own Back and edge swipe, which only ever shorten it, and
    /// which wait like every other way out while a page minds a run.
    func setPath(_ path: [RouteEntry], on tab: AppTab) {
        guard !locked else { return }
        stacks[tab] = path
    }

    /// The page in front, on the destination in front; nil on its top page.
    var top: RouteEntry? { stacks[tab]?.last }

    /// A page over the one in front. What opened it is what Back returns to.
    @discardableResult
    func push(_ route: AppRoute) -> RouteEntry? {
        guard !locked else { return nil }
        let entry = RouteEntry(route)
        stacks[tab, default: []].append(entry)
        return entry
    }

    func back() {
        guard !locked else { return }
        _ = stacks[tab]?.popLast()
    }

    /// A task that is done closes its own page, if that page is still on top
    /// of its stack. Anything opened over it since keeps it open.
    func finish(_ entry: RouteEntry) {
        for t in AppTab.allCases where stacks[t]?.last == entry {
            stacks[t]?.removeLast()
            return
        }
    }

    /// Whether this opening of a page is still on a stack.
    func isOpen(_ entry: RouteEntry) -> Bool {
        stacks.values.contains { $0.contains(entry) }
    }

    /// A destination chosen again goes back to its top.
    func select(_ next: AppTab) {
        guard !locked else { return }
        if next == tab { stacks[next] = [] } else { tab = next }
    }

    /// A machine opened deliberately, or none in use: the Machine overview,
    /// every stack at its top. Your machines stays as it is.
    func reset() {
        tab = .machine
        stacks = [:]
        locked = false
    }
}
