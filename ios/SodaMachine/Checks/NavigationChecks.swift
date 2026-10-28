import Foundation

private struct NavigationReviewSound: Hashable {
    var volume: Int
    var quiet: Bool
}

/// Manual experience review against the production pure core.
/// The caller supplies reporting and owns the executable entry point.
@MainActor
func runNavigationChecks(_ check: (Bool, String) -> Void) {
    // A draft is a task's work, not a property of the view currently mounted.
    do {
        let nav = Navigator()
        let edits = EditSessions()
        let ratioKey = EditKey(machine: "A", field: .ratio(channel: 0))
        let soundKey = EditKey(machine: "A", field: .sound)
        let flavor = nav.push(.flavor(0)) ?? RouteEntry(.flavor(0))
        edits.setDraft(18, for: ratioKey)
        let images = nav.push(.images(0)) ?? RouteEntry(.images(0))
        check(nav.top == images, "Opening Images creates a child of the flavor task")
        nav.back()
        check(nav.top == flavor, "Back from Images returns to the exact Flavor entry")
        check(edits.draft(ratioKey, as: Int.self) == 18, "A child journey preserves the ratio draft")

        nav.select(.settings)
        let sound = nav.push(.sound) ?? RouteEntry(.sound)
        let wantedSound = NavigationReviewSound(volume: 40, quiet: true)
        edits.setDraft(wantedSound, for: soundKey)
        nav.select(.machine)
        check(nav.top == flavor, "Returning to Machine retains its nested route")
        check(nav.path(on: .settings).last == sound, "A background tab retains its nested route")
        check(edits.draft(soundKey, as: NavigationReviewSound.self) == wantedSound, "A background tab retains its Sound draft")

        nav.back()
        let reopened = nav.push(.flavor(0)) ?? RouteEntry(.flavor(0))
        check(reopened.id != flavor.id, "Reopening the same route creates a new page identity")
        check(edits.draft(ratioKey, as: Int.self) == 18, "Back and reopening preserve the machine's ratio draft")
    }

    // An old completion is not authority to close a later opening of a page.
    do {
        let nav = Navigator()
        nav.select(.settings)
        let old = nav.push(.sound) ?? RouteEntry(.sound)
        nav.back()
        let new = nav.push(.sound) ?? RouteEntry(.sound)
        nav.finish(old)
        check(nav.top == new, "Route ABA: an old Sound completion cannot close a reopened Sound editor")
        check(!nav.isOpen(old) && nav.isOpen(new), "Route ABA: membership uses page identity rather than route equality")
        nav.finish(new)
        check(nav.top == nil, "The live originating entry can finish normally")

        let firstMachineEntry = nav.push(.rename) ?? RouteEntry(.rename)
        nav.reset()
        let returnedMachineEntry = nav.push(.rename) ?? RouteEntry(.rename)
        nav.finish(firstMachineEntry)
        check(nav.top == returnedMachineEntry, "Machine ABA: an entry from before a machine reset cannot close a later entry")
    }

    // Equal route names on separate tabs must not compete for completion.
    do {
        let nav = Navigator()
        let machineUpdate = nav.push(.update) ?? RouteEntry(.update)
        nav.select(.settings)
        let settingsUpdate = nav.push(.update) ?? RouteEntry(.update)
        nav.select(.care)
        let careTask = nav.push(.fill(0)) ?? RouteEntry(.fill(0))

        nav.finish(machineUpdate)
        check(nav.tab == .care && nav.top == careTask, "Background completion never redirects the foreground tab or task")
        check(nav.path(on: .machine).isEmpty, "Background completion can finish its own still-live origin")
        check(nav.path(on: .settings).last == settingsUpdate, "Same route on two tabs: completing one leaves the other intact")
        nav.finish(settingsUpdate)
        check(nav.tab == .care && nav.top == careTask, "Finishing a second background origin still leaves foreground navigation intact")
        check(nav.path(on: .settings).isEmpty, "The exact Settings Update entry finishes independently")
    }

    // Completion is not Back when another page now covers the origin.
    do {
        let nav = Navigator()
        let flavor = nav.push(.flavor(1)) ?? RouteEntry(.flavor(1))
        let child = nav.push(.images(1)) ?? RouteEntry(.images(1))
        nav.finish(flavor)
        check(nav.top == child && nav.isOpen(flavor), "A delayed parent completion cannot pop or remove a child journey")
        nav.back()
        check(nav.top == flavor, "The child still has its original parent after delayed completion")
        nav.finish(flavor)
        nav.finish(flavor)
        check(nav.top == nil, "Repeating a completion cannot perform an extra Back")
    }

    // One operation policy must govern buttons and native path bindings.
    do {
        let nav = Navigator()
        let flavor = nav.push(.flavor(0)) ?? RouteEntry(.flavor(0))
        _ = nav.push(.images(0))
        let before = nav.path(on: .machine)
        nav.locked = true
        check(nav.push(.update) == nil, "An attended operation blocks a new pushed page")
        nav.back()
        check(nav.path(on: .machine) == before, "An attended operation blocks Back")
        nav.select(.settings)
        check(nav.tab == .machine && nav.path(on: .machine) == before, "An attended operation blocks a tab switch")
        nav.select(.machine)
        check(nav.path(on: .machine) == before, "Retapping the current tab cannot bypass an operation lock")

        nav.setPath([], on: .machine)
        check(nav.path(on: .machine) == before, "Native full-pop path binding obeys the same operation lock as Back")

        // Restore independently so a failing full-pop check does not mask this case.
        nav.locked = false
        nav.setPath(before, on: .machine)
        nav.locked = true
        nav.setPath([flavor], on: .machine)
        check(nav.path(on: .machine) == before, "Native one-page edge-pop binding obeys the operation lock")

        nav.locked = false
        nav.setPath([flavor], on: .machine)
        check(nav.top == flavor, "After the operation unlocks, native pop returns to the correct parent")
    }

    // A write token protects the latest intent; equality protects newer edits.
    do {
        let edits = EditSessions()
        let key = EditKey(machine: "A", field: .ratio(channel: 0))
        edits.setDraft(18, for: key)
        let older = edits.begin(key)
        edits.setDraft(16, for: key)
        edits.settle(key, saved: 18)
        check(edits.draft(key, as: Int.self) == 16, "Accepted old ratio does not clear a different newer draft")
        edits.end(older, for: key, note: "Saved 1:18")
        check(!edits.working(key), "An accepted write can finish without clearing newer work")
        check(edits.draft(key, as: Int.self) == 16, "Finishing an older choice preserves the newer ratio draft")

        let first = edits.begin(key)
        let newest = edits.begin(key)
        check(!edits.isNewest(first, for: key) && edits.isNewest(newest, for: key), "A newer write supersedes the old write token")
        edits.end(first, for: key, problem: "Old failure", note: "Old success")
        check(edits.write(key)?.token == newest && edits.working(key), "An old write result cannot stop the newer request")
        check(edits.write(key)?.problem == nil && edits.write(key)?.note == nil, "An old write cannot overwrite the newer request's result")
        edits.end(newest, for: key, problem: "Try again")
        check(edits.write(key)?.problem == "Try again", "The newest write's useful failure remains available")
        check(edits.draft(key, as: Int.self) == 16, "A failed save preserves the intended ratio")

        edits.setDraft(15, for: key)
        check(edits.write(key) == nil, "A new edit clears an obsolete finished write's message")
        edits.settle(key, saved: 15)
        check(edits.draft(key, as: Int.self) == nil, "A matching accepted ratio resolves that draft")
    }

    // Discard invalidates a waiting task's local result as well as its draft.
    do {
        let edits = EditSessions()
        let key = EditKey(machine: "A", field: .sound)
        edits.setDraft(NavigationReviewSound(volume: 30, quiet: true), for: key)
        let waiting = edits.begin(key)
        edits.discard(key)
        edits.end(waiting, for: key, problem: "Late failure")
        check(edits.draft(key, as: NavigationReviewSound.self) == nil, "Discard explicitly removes the Sound draft")
        check(edits.write(key) == nil && !edits.isNewest(waiting, for: key), "Discard prevents a late local write result from resurrecting the task")
    }

    // Machine identity, setting, and channel are independent draft dimensions.
    do {
        let edits = EditSessions()
        let a0 = EditKey(machine: "record-A", field: .ratio(channel: 0))
        let a1 = EditKey(machine: "record-A", field: .ratio(channel: 1))
        let b0 = EditKey(machine: "record-B", field: .ratio(channel: 0))
        let aName = EditKey(machine: "record-A", field: .name)
        edits.setDraft(18, for: a0)
        edits.setDraft(22, for: a1)
        edits.setDraft(16, for: b0)
        edits.setDraft("Kitchen", for: aName)
        let aWrite = edits.begin(a0)
        let bWrite = edits.begin(b0)
        check(edits.draft(a0, as: Int.self) == 18 && edits.draft(a1, as: Int.self) == 22, "Two channels retain independent ratio choices")
        check(edits.draft(b0, as: Int.self) == 16 && edits.draft(aName, as: String.self) == "Kitchen", "Machines and settings cannot share each other's draft")

        edits.forget(machine: "record-A")
        check(edits.draft(a0, as: Int.self) == nil && edits.draft(a1, as: Int.self) == nil && edits.draft(aName, as: String.self) == nil, "Forgetting a machine removes every field and channel draft for it")
        check(edits.write(a0) == nil && !edits.isNewest(aWrite, for: a0), "Forgetting a machine invalidates its pending write token")
        edits.end(aWrite, for: a0, note: "Late completion")
        check(edits.write(a0) == nil, "A removed machine's late result cannot recreate its edit task")
        check(edits.draft(b0, as: Int.self) == 16 && edits.isNewest(bWrite, for: b0) && edits.working(b0), "Forgetting A leaves B's draft and pending request intact")

        let readded = EditKey(machine: "fresh-record-A", field: .ratio(channel: 0))
        check(edits.draft(readded, as: Int.self) == nil && edits.write(readded) == nil, "A re-added record cannot inherit an obsolete record's task")
    }

    // Directory decisions must not quietly pick another appliance.
    do {
        check(afterRemoving("B", current: "A", remaining: ["A", "B", "C"]) == .keep("A"), "Removing a noncurrent record preserves the current appliance")
        check(afterRemoving("A", current: "A", remaining: ["A", "B", "C"]) == .choose(["B", "C"]), "Removing the current record offers remaining records without selecting one")
        check(afterRemoving("A", current: "A", remaining: ["A"]) == .firstRun, "Removing the final record offers first-run setup")
        check(afterRemoving("B", current: nil, remaining: ["A", "B"]) == .choose(["A"]), "An existing unselected directory still requires an explicit choice")
        check(afterRemoving("B", current: "missing", remaining: ["A", "B"]) == .choose(["A"]), "A stale selection cannot be retained as a phantom current appliance")
        check(afterRemoving("B", current: nil, remaining: []) == .firstRun, "An empty unselected directory offers first-run setup")
    }

    // Device-level management outlives appliance navigation resets.
    do {
        let nav = Navigator()
        let edits = EditSessions()
        let key = EditKey(machine: "A", field: .ratio(channel: 1))
        edits.setDraft(17, for: key)
        _ = nav.push(.flavor(1))
        nav.select(.settings)
        _ = nav.push(.sound)
        nav.managing = true
        nav.reset()
        check(nav.managing, "A machine reset cannot dismiss root-owned Your machines")
        check(nav.tab == .machine && AppTab.allCases.allSatisfy { nav.path(on: $0).isEmpty }, "Explicitly opening a machine returns all appliance navigation to the overview")
        check(edits.draft(key, as: Int.self) == 17, "A machine navigation reset does not discard machine-keyed edits")
    }
}
