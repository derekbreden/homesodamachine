import AccessorySetupKit
import CoreBluetooth
import UIKit
import os

private let log = Logger(subsystem: "com.derekbreden.SodaMachine", category: "Access")

// ────────────────────────────────────────────────────────────
// Which machines this app may reach, as the system keeps them.
//
// THE SYSTEM HANDS THE APP ONE MACHINE AT A TIME. Adding a machine is the
// system's own sheet: the machine's picture, only the machines right next to
// the phone, and a tap on the one in hand. The app is handed that machine and
// can reach no other, and nothing asks about Bluetooth — the tap is the
// permission. Settings lists every machine handed over, under Accessories,
// where a person can rename one or remove it.
//
// THE SHEET LOOKS FOR THE SERVICE, NOT FOR THE BLOCK THAT NAMES A MACHINE.
// The Nordic UART service is in the primary advertisement of every machine
// there is; the manufacturer block is not — older firmware writes it in the
// scan response, and the prototype under the counter does not write it at
// all. Which of two machines is the one being added is settled by distance:
// the sheet lists only the machines right next to the phone.
//
// THE SYSTEM'S LIST IS WHICH MACHINES ARE ON THE PHONE. A machine removed in
// Settings leaves the phone, pictures and all, as Forget leaves it, and
// Forget on a machine the system lists is the system's removal. A name given
// in Settings is sent to the machine, whose main board keeps the name every
// phone shows. The sheet that adds a machine asks for no name: it cannot know
// the one the machine already has, and the machine keeps it.
//
// AN EARLIER BUILD'S MACHINES ARE CARRIED OVER ONCE, BEFORE THE RADIO COMES
// UP. That build reached them on Bluetooth access of its own, and carrying
// them over is the system's sheet too, which will not open while this app
// holds a central manager on that access. So at launch the radio waits until
// the system has said which machines it lists, and, the one time it is
// needed, until it has taken those.
// ────────────────────────────────────────────────────────────

@MainActor
@Observable
final class MachineAccess {
    /// What came of the last tap on Find, for the screen it was tapped on.
    enum Outcome: Equatable {
        /// The sheet came down with no machine in it.
        case nothingAdded
        /// The sheet did not open, said the way a person can act on.
        case failed(String)
    }

    /// The system's sheet has been asked for, and is on its way up or up.
    private(set) var opening = false
    private(set) var outcome: Outcome?
    /// Machines the sheet has handed over since launch. A screen that opened
    /// the sheet closes when this moves.
    private(set) var added = 0

    private let directory: MachineDirectory
    private let ble: BLEManager

    private enum Job {
        /// The machine at hand, being added.
        case adding
        /// An earlier build's machines, by peripheral id, being carried over.
        case carrying(Set<String>)
    }

    @ObservationIgnored private var session: ASAccessorySession?
    /// The session has said which machines the system lists.
    @ObservationIgnored private var ready = false
    @ObservationIgnored private var job: Job?
    /// A tap on Find that came while the session was not ready, or while
    /// machines were being carried over. It opens the sheet when that is done.
    @ObservationIgnored private var addWanted = false
    /// The machine the sheet handed over, held until the sheet is down.
    @ObservationIgnored private var handed: ASAccessory?
    /// The sheet said setting the machine up failed.
    @ObservationIgnored private var setupFailed = false
    /// The sheet is up. A sheet that is up ends only with its dismissal.
    @ObservationIgnored private var presented = false
    /// Counts each ask for the sheet, so an answer that belongs to an earlier
    /// one lands nowhere.
    @ObservationIgnored private var request = 0
    /// Counts the waits on a quiet sheet; only the newest may end it.
    @ObservationIgnored private var wait = 0

    /// What a machine nobody has named is called, which is also what the
    /// sheet calls the machine it shows.
    private static let unnamed = "Soda machine"
    private static let didNotOpen = "The setup sheet did not open. Try again."
    /// How many times the sheet is asked for again after the system turns it
    /// down for this app's radio, a second apart.
    private static let restrictedTries = 8

    init(directory: MachineDirectory, ble: BLEManager) {
        self.directory = directory
        self.ble = ble
        start()
    }

    // ── What the sheet shows ──────────────────────────────────────────────

    /// THE PICTURE IN THE SHEET. The system fits it into a box 180 by 120
    /// points, on its own light or dark background, so it is transparent and
    /// carries at least three times that in pixels.
    private static var picture: UIImage { UIImage(named: "SetupPicture") ?? UIImage() }

    /// What the sheet looks for. A machine being added has to be right next to
    /// the phone; one being carried over is not looked for at all.
    private static func descriptor(range: ASDiscoveryDescriptor.Range) -> ASDiscoveryDescriptor {
        let descriptor = ASDiscoveryDescriptor()
        descriptor.bluetoothServiceUUID = CBUUID(string: "6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
        descriptor.bluetoothRange = range
        descriptor.supportedOptions = [.bluetoothPairingLE]
        return descriptor
    }

    // ── The session ───────────────────────────────────────────────────────

    /// Ask the system which machines it lists for this app. The radio waits
    /// for the answer, though not for a system that never gives one: that
    /// leaves the app on whatever Bluetooth access it already has.
    private func start() {
        guard session == nil else { return }
        let session = ASAccessorySession()
        self.session = session
        ready = false
        session.activate(on: .main) { [weak self] event in
            MainActor.assumeIsolated { self?.handle(event) }
        }
        Task { [weak self] in
            try? await Task.sleep(for: .seconds(5))
            guard let self, self.session === session, !self.ready else { return }
            log.error("the accessory session did not activate")
            self.unavailable()
        }
    }

    /// The system's list cannot be had. The radio comes up on whatever access
    /// the app has, and a tap that was waiting on the list is told.
    private func unavailable() {
        ble.allowRadio()
        if addWanted {
            addWanted = false
            opening = false
            outcome = .failed("Adding a machine did not start. Close the app, open it, and try again.")
        }
    }

    /// The app is in front: a session that ended starts again, and an earlier
    /// build's machines are carried over if that was waiting on it.
    func becameActive() {
        guard session != nil else { start(); return }
        if ready, job == nil, !carryOver(inFront: true) { ble.allowRadio() }
    }

    private func handle(_ event: ASAccessoryEvent) {
        switch event.eventType {
        case .activated:
            if let error = event.error {
                log.error("the accessory session did not activate: \(error.localizedDescription)")
                unavailable()
                return
            }
            ready = true
            reconcile()
            if !carryOver(inFront: UIApplication.shared.applicationState == .active) {
                ble.allowRadio()
            }
            if addWanted, job == nil {
                addWanted = false
                add()
            }
        case .accessoryAdded:
            if case .adding = job { handed = event.accessory } else { reconcile() }
        case .accessoryChanged:
            // A name given in the sheet can follow the machine it names.
            if case .adding = job, let changed = event.accessory,
               changed.bluetoothIdentifier == handed?.bluetoothIdentifier {
                handed = changed
            } else {
                reconcile()
            }
        case .accessoryRemoved:
            removed(event.accessory)
        case .migrationComplete:
            carried()
        case .pickerDidPresent:
            presented = true
        case .pickerSetupFailed:
            log.error("the sheet could not set the machine up: \(event.error?.localizedDescription ?? "no reason")")
            setupFailed = true
        case .pickerDidDismiss:
            if job != nil { end(failure: nil) } else { reconcile() }
        case .invalidated:
            log.error("the accessory session ended")
            session = nil
            ready = false
            end(failure: "The setup sheet closed. Try again.")
            ble.allowRadio()
        default:
            break
        }
    }

    // ── Adding ────────────────────────────────────────────────────────────

    /// Open the system's sheet for the machine at hand.
    func add() {
        if case .adding = job { return }
        outcome = nil
        if ble.transferInFlight {
            outcome = .failed("Finish the update first, then add the machine.")
            return
        }
        guard ready, session != nil, job == nil else {
            addWanted = true
            opening = true
            if session == nil { start() }
            return
        }
        job = .adding
        opening = true
        handed = nil
        setupFailed = false
        show([ASPickerDisplayItem(name: Self.unnamed, productImage: Self.picture,
                                  descriptor: Self.descriptor(range: .immediate))])
    }

    /// An outcome shown once is not shown to the next screen that opens.
    func clearOutcome() {
        outcome = nil
    }

    // ── Carrying an earlier build's machines over ─────────────────────────

    /// The machines an earlier build added that the system does not list,
    /// carried over once, with the app in front — the system shows its sheet
    /// only then. Says whether the radio is to keep waiting.
    @discardableResult
    private func carryOver(inFront: Bool) -> Bool {
        guard ready, !directory.carriedOver, job == nil, !ble.transferInFlight,
              let session else { return false }
        let listed = Set(session.accessories.compactMap { $0.bluetoothIdentifier?.uuidString })
        var ids = Set<String>()
        var items: [ASPickerDisplayItem] = []
        for m in directory.known where !m.isDemo && m.accessoryID == nil {
            guard let id = m.peripheralID, !listed.contains(id),
                  let uuid = UUID(uuidString: id) else { continue }
            let item = ASMigrationDisplayItem(name: m.displayName, productImage: Self.picture,
                                              descriptor: Self.descriptor(range: .default))
            item.peripheralIdentifier = uuid
            items.append(item)
            ids.insert(id)
        }
        guard !items.isEmpty else { return false }
        guard inFront else { return true }
        log.info("carrying over \(items.count) machine(s)")
        job = .carrying(ids)
        show(items)
        return true
    }

    /// One machine carried over. The sheet is done when every one asked about
    /// is listed, unless it is up: a sheet that is up ends with its dismissal.
    private func carried() {
        reconcile()
        guard case .carrying(let ids) = job else { return }
        let listed = Set(session?.accessories.compactMap { $0.bluetoothIdentifier?.uuidString } ?? [])
        if ids.isSubset(of: listed), !presented {
            end(failure: nil)
        } else {
            waitOut(seconds: 10)
        }
    }

    // ── The sheet ─────────────────────────────────────────────────────────

    private func show(_ items: [ASPickerDisplayItem], attempt: Int = 0) {
        guard let session else { end(failure: Self.didNotOpen); return }
        request += 1
        let asked = request
        presented = false
        Task { [weak self] in
            var refused: Error?
            do { try await session.showPicker(for: items) } catch { refused = error }
            self?.answered(refused, to: asked, items: items, attempt: attempt)
        }
        if case .adding = job { waitOut(seconds: 30) } else { waitOut(seconds: 10) }
    }

    /// The system's answer to an ask for the sheet. Up, the rest arrives as
    /// events; turned down, the sheet is asked for again or given up on.
    /// Carrying over answers yes with nothing on screen, so only adding takes
    /// a yes as a sheet that is up.
    private func answered(_ error: Error?, to asked: Int, items: [ASPickerDisplayItem], attempt: Int) {
        guard asked == request, let job else { return }
        guard let error else {
            if case .adding = job { presented = true }
            return
        }
        switch (error as? ASError)?.code {
        case .pickerRestricted? where attempt < Self.restrictedTries:
            // THE SHEET WILL NOT COME UP OVER THIS APP'S RADIO on a phone that
            // gave an earlier build Bluetooth access of its own. The radio is
            // let go, and the sheet asked for again once the system has seen
            // it go — never over an update, which letting go would end.
            if ble.transferInFlight {
                end(failure: "Finish the update first, then add the machine.")
                return
            }
            ble.holdRadio()
            Task { [weak self] in
                try? await Task.sleep(for: .seconds(1))
                guard let self, asked == self.request, self.job != nil else { return }
                self.show(items, attempt: attempt + 1)
            }
        case .userCancelled?:
            end(failure: nil)
        case .pickerAlreadyActive?:
            end(failure: "The setup sheet is stuck. Close the app, open it, and try again.")
        default:
            log.error("the setup sheet did not open: \(error.localizedDescription)")
            end(failure: Self.didNotOpen)
        }
    }

    /// A SHEET THAT NEVER COMES UP, AND NEVER SAYS SO, STILL ENDS. The system
    /// can do both — a carry-over with nothing to show, a sheet asked for
    /// while another is still held — and the radio waits while the sheet is
    /// asked for. A sign of the system still working starts the wait again; a
    /// sheet that is up is waited for until it is dismissed.
    private func waitOut(seconds: Double) {
        wait += 1
        let waiting = wait
        Task { [weak self] in
            try? await Task.sleep(for: .seconds(seconds))
            guard let self, waiting == self.wait, self.job != nil, !self.presented else { return }
            log.info("the setup sheet went quiet")
            self.end(failure: Self.didNotOpen)
        }
    }

    /// The sheet is done with, however it went. A machine it handed over is
    /// added and pointed at; machines it carried over are marked; and the
    /// radio comes back.
    private func end(failure: String?) {
        guard let was = job else { return }
        job = nil
        request += 1
        wait += 1
        presented = false
        opening = false
        let picked = handed.map { held in
            session?.accessories.first { $0.bluetoothIdentifier == held.bluetoothIdentifier } ?? held
        }
        handed = nil
        switch was {
        case .adding:
            if let picked, let id = picked.bluetoothIdentifier?.uuidString {
                // Met by a central manager made after the system listed it.
                ble.holdRadio()
                let m = ble.add(peripheralID: id)
                adopt(picked, as: m, named: false)
                ble.askTrustOnLink()
                added += 1
                outcome = nil
            } else if let failure {
                outcome = .failed(failure)
            } else if setupFailed {
                outcome = .failed("The machine did not finish setting up. Try again.")
            } else {
                outcome = .nothingAdded
            }
        case .carrying:
            directory.carriedOver = true
            reconcile()
            directory.save()
        }
        setupFailed = false
        ble.allowRadio()
        if addWanted {
            addWanted = false
            add()
        }
    }

    // ── The system's list and the records ─────────────────────────────────

    /// A machine the system lists, written onto its record: the peripheral id
    /// it is listed under, and the name it is listed as. A name someone gave
    /// there goes to the machine.
    private func adopt(_ accessory: ASAccessory, as m: KnownMachine, named: Bool) {
        m.accessoryID = accessory.bluetoothIdentifier?.uuidString
        m.accessoryName = accessory.displayName
        if named { ble.rename(m, to: accessory.displayName) }
        directory.save()
    }

    /// Every record held to the system's list. A record whose listing is gone
    /// was removed in Settings, and leaves the phone. A listed name that
    /// changed was given in Settings, and goes to the machine. A record from
    /// an earlier build that the system now lists takes its listing. And a
    /// machine handed over with no record — handed over as the app went away
    /// — is given one.
    private func reconcile() {
        guard ready, let session else { return }
        var listed: [String: ASAccessory] = [:]
        for accessory in session.accessories {
            if let id = accessory.bluetoothIdentifier?.uuidString { listed[id] = accessory }
        }
        // The machine the sheet is handing over is added when the sheet is down.
        if case .adding = job, let id = handed?.bluetoothIdentifier?.uuidString { listed[id] = nil }

        for m in directory.known where !m.isDemo {
            if let id = m.accessoryID {
                if let accessory = listed.removeValue(forKey: id) {
                    if accessory.displayName != m.accessoryName { adopt(accessory, as: m, named: true) }
                } else {
                    log.info("\(m.displayName) was removed in Settings")
                    ble.forget(m)
                }
            } else if let id = m.peripheralID, let accessory = listed.removeValue(forKey: id) {
                adopt(accessory, as: m, named: false)
            }
        }
        for (id, accessory) in listed where accessory.state == .authorized {
            // What the system calls it is no new name: the machine says its own.
            log.info("the system lists \(id) with no record; adding it")
            let m = directory.add(peripheralID: id)
            adopt(accessory, as: m, named: false)
            if directory.current == nil { ble.select(m) }
        }
    }

    /// A machine the system no longer lists: gone from the phone.
    private func removed(_ accessory: ASAccessory?) {
        guard let id = accessory?.bluetoothIdentifier?.uuidString,
              let m = directory.machine(accessoryID: id) else { return }
        log.info("\(m.displayName) was removed")
        ble.forget(m)
    }

    // ── Forgetting ────────────────────────────────────────────────────────

    /// Whether the system lists this machine, so that forgetting it is the
    /// system's removal, which asks first.
    func lists(_ m: KnownMachine) -> Bool {
        listing(of: m) != nil
    }

    private func listing(of m: KnownMachine) -> ASAccessory? {
        guard ready, let session, let id = m.accessoryID else { return nil }
        return session.accessories.first { $0.bluetoothIdentifier?.uuidString == id }
    }

    /// Why the last removal did not happen, for Your machines to say.
    private(set) var removalProblem: String?

    /// Gone from the phone, pictures and all. A machine the system handed
    /// over is removed from the system, which asks first, and its record goes
    /// only once the system has removed it — a record dropped while the
    /// system still lists the machine would come straight back. Any other
    /// goes at once.
    func forget(_ m: KnownMachine) {
        removalProblem = nil
        guard m.accessoryID != nil else {
            ble.forget(m)
            return
        }
        guard ready, let session else {
            removalProblem = "\(m.displayName) wasn’t removed: the system’s list of accessories isn’t available yet. Try again in a moment."
            if session == nil { start() }
            return
        }
        guard let accessory = listing(of: m) else {
            // The system no longer lists it: removed in Settings already.
            ble.forget(m)
            return
        }
        Task { [weak self] in
            do {
                try await session.removeAccessory(accessory)
            } catch {
                log.info("\(accessory.displayName) stays: \(error.localizedDescription)")
                if (error as? ASError)?.code != .userCancelled {
                    self?.removalProblem = "\(m.displayName) wasn’t removed. Try again."
                }
                return
            }
            self?.removed(accessory)
        }
    }
}
