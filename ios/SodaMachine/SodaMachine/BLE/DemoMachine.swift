import Foundation

// ────────────────────────────────────────────────────────────
// The demo: an appliance with sample readings, answering every request on
// this device. Its runs play out here, on a short clock, and nothing reaches
// a radio.
// ────────────────────────────────────────────────────────────

extension BLEManager {
    /// Sample state for a demo that has none yet.
    func seedDemo(_ m: KnownMachine) {
        guard m.isDemo, m.appliance.status == nil else { return }
        let now = Date()
        var status = MachineStatus()
        status.levels = [3, 1]
        status.levelFlags = 0x01 | 0x02 | 0x04   // read, both carbonator reeds closed
        status.ratios = [20, 20]
        status.tankTenthsC = 22
        status.coldState = ColdState.on.rawValue
        status.refillState = RefillState.idle.rawValue
        var sound = SoundSettings()
        sound.volume = 60
        sound.quietOn = true
        sound.quietVolume = 20
        var state = ApplianceState()
        state.status = Reading(value: status, at: now)
        state.selection = Reading(value: FlavorSelection(channel: 0, persisted: true), at: now)
        state.sound = Reading(value: sound, at: now)
        state.fill = Reading(value: FillState(), at: now)
        state.clean = Reading(value: CleanState(), at: now)
        state.prime = Reading(value: PrimeSession(), at: now)
        m.appliance = state
        m.flavorArt = FlavorArt()
        directory.save()
    }

    /// The demo's answer to one request, as the machine would give it.
    func demoAnswer(_ type: UInt8, _ body: [UInt8]) -> Result<BridgeAnswer, BridgeError> {
        guard let m = current else { return .failure(.offline) }
        let now = Date()
        var a = m.appliance
        var answer = BridgeAnswer(type: type, body: Data())
        let channel = body.first.map { Int($0) & 1 } ?? 0
        let busy = a.fill?.value.running == true || a.clean?.value.running == true || a.prime?.value.phase != .off

        switch type {
        case MachineMessage.statusRequest:
            a.status?.at = now
        case MachineMessage.flavorQuery:
            a.selection?.at = now
        case MachineMessage.flavorSelect:
            a.selection = Reading(value: FlavorSelection(channel: channel, persisted: true), at: now)
        case MachineMessage.ratioSetOne where body.count >= 2:
            if (6...24).contains(Int(body[1])) { a.status?.value.ratios[channel] = Int(body[1]) }
            a.status?.at = now
        case MachineMessage.soundGet:
            a.sound?.at = now
        case MachineMessage.soundSet where body.count >= 5:
            var s = a.sound?.value ?? SoundSettings()
            s.volume = min(Int(body[0]), 100)
            s.quietOn = body[1] != 0
            s.quietStart = Int(body[2]) % 24
            s.quietEnd = Int(body[3]) % 24
            s.quietVolume = min(Int(body[4]), 100)
            a.sound = Reading(value: s, at: now)
        case MachineMessage.fillQuery, MachineMessage.cleanQuery, MachineMessage.primeQuery:
            break
        case MachineMessage.fillStart:
            var f = FillState()
            f.channel = channel
            if busy { f.outcome = .busy } else { f.running = true; demoRun(fill: channel, from: now) }
            a.fill = Reading(value: f, at: now)
        case MachineMessage.fillStop:
            demoEnd(after: 0.6) { a in
                a.fill?.value.running = false
                a.fill?.value.outcome = .stopped
            }
        case MachineMessage.cleanStart:
            if busy {
                var c = CleanState()
                c.channel = channel
                c.outcome = .busy
                a.clean = Reading(value: c, at: now)
            } else {
                a.clean = Reading(value: Self.demoClean(channel: channel, elapsed: 0), at: now)
                demoRun(clean: channel, from: now)
            }
        case MachineMessage.cleanStop:
            demoEnd(after: 0.6) { a in
                a.clean?.value.running = false
                a.clean?.value.outcome = .stopped
                a.clean?.value.cycleLeftMs = 0
            }
        case MachineMessage.primeOpen:
            let shown = !busy
            answer = BridgeAnswer(type: MachineMessage.primeOpened,
                                  body: Data([UInt8(channel), shown ? PrimeOpenResult.shown.rawValue : PrimeOpenResult.refused.rawValue]))
            if shown {
                demoEnd(after: 0.5) { a in
                    var p = PrimeSession()
                    p.phase = .ready
                    p.channel = channel
                    p.revision = (a.prime?.value.revision ?? 0) + 1
                    p.sessionToken = UInt32.random(in: 1...UInt32.max)
                    a.prime = Reading(value: p, at: Date())
                }
            }
        case MachineMessage.primeSet:
            if var p = a.prime?.value, p.phase != .off {
                p.phase = .off
                p.outcome = .canceled
                p.revision += 1
                a.prime = Reading(value: p, at: now)
            }
        default:
            return .failure(.refused)
        }
        m.appliance = a
        return .success(answer)
    }

    /// A change the demo machine makes on its own, a moment from now.
    private func demoEnd(after seconds: Double, _ change: @escaping (inout ApplianceState) -> Void) {
        DispatchQueue.main.asyncAfter(deadline: .now() + seconds) { [weak self] in
            guard let self, let m = self.current, m.isDemo else { return }
            var a = m.appliance
            change(&a)
            m.appliance = a
        }
    }

    // ── The demo's runs, on a short clock ────────────────────────────────

    private static let demoFillMs: UInt32 = 20_000
    private static let demoFunnelMs: UInt32 = 12_000
    private static let demoStepMs: UInt32 = 8_000
    private static let demoRounds = 3

    private func demoRun(fill channel: Int, from start: Date) {
        demoTick(from: start) { a, elapsed in
            guard a.fill?.value.running == true else { return true }
            a.fill?.value.elapsedMs = min(elapsed, Self.demoFillMs)
            a.fill?.value.plannedMs = Self.demoFillMs
            guard elapsed >= Self.demoFillMs else { return false }
            a.fill?.value.running = false
            a.fill?.value.outcome = .done
            a.status?.value.levels[channel] = 4
            return true
        }
    }

    private func demoRun(clean channel: Int, from start: Date) {
        let total = Self.demoFunnelMs + UInt32(Self.demoRounds) * 2 * Self.demoStepMs
        demoTick(from: start) { a, elapsed in
            guard a.clean?.value.running == true else { return true }
            guard elapsed < total else {
                a.clean?.value.running = false
                a.clean?.value.outcome = .done
                a.clean?.value.cycleLeftMs = 0
                a.status?.value.levels[channel] = 0
                return true
            }
            a.clean?.value = Self.demoClean(channel: channel, elapsed: elapsed)
            return false
        }
    }

    private static func demoClean(channel: Int, elapsed: UInt32) -> CleanState {
        let total = demoFunnelMs + UInt32(demoRounds) * 2 * demoStepMs
        var c = CleanState()
        c.running = true
        c.channel = channel
        c.rounds = demoRounds
        c.cycleLeftMs = total - min(elapsed, total)
        if elapsed < demoFunnelMs {
            c.step = .funnel
            c.round = 0
            c.stepElapsedMs = elapsed
            c.stepPlannedMs = demoFunnelMs
        } else {
            let into = elapsed - demoFunnelMs
            let step = Int(into / demoStepMs)
            c.round = min(step / 2 + 1, demoRounds)
            c.step = step % 2 == 0 ? .waterFill : .flush
            c.stepElapsedMs = into % demoStepMs
            c.stepPlannedMs = demoStepMs
        }
        return c
    }

    /// Once a second until `step` says the run is over.
    private func demoTick(from start: Date, _ step: @escaping (inout ApplianceState, UInt32) -> Bool) {
        demoRunTask?.cancel()
        demoRunTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(1))
                guard let self, let m = self.current, m.isDemo, !Task.isCancelled else { return }
                var a = m.appliance
                let done = step(&a, UInt32(Date().timeIntervalSince(start) * 1000))
                let now = Date()
                a.fill?.at = now
                a.clean?.at = now
                m.appliance = a
                if done { return }
            }
        }
    }
}
