import Foundation
import os

private let log = Logger(subsystem: "com.derekbreden.SodaMachine", category: "Bridge")

// ────────────────────────────────────────────────────────────
// What this phone asks of the machine, and what the machine says back.
//
// The faucet's radio carries a request to the main board and brings the main
// board's answer — the state the request produced — to the phone that asked
// (firmware/src_faucet/phone_bridge.h). State that moved, by anyone's hand,
// arrives unasked under request id 0. Both land on the machine's record.
//
// A request that goes unanswered is reported as unanswered, and a screen reads
// the truth with a query.
// ────────────────────────────────────────────────────────────

enum BridgeFrame {
    static let request: UInt8 = 0x23
    static let answer:  UInt8 = 0x24
    static let version: UInt8 = 0x25
}

/// proto_msg.h's numbers for what a phone may ask, and what answers it.
enum MachineMessage {
    static let statusRequest: UInt8 = 0x0E
    static let status:        UInt8 = 0x18
    static let flavorSelect:  UInt8 = 0x27
    static let flavorState:   UInt8 = 0x28
    static let flavorQuery:   UInt8 = 0x29
    static let ratioQuery:    UInt8 = 0x64
    static let ratio:         UInt8 = 0x65
    static let ratioSetOne:   UInt8 = 0x69
    static let fillStart:     UInt8 = 0x30
    static let fillQuery:     UInt8 = 0x57
    static let fill:          UInt8 = 0x58
    static let fillStop:      UInt8 = 0x59
    static let cleanStart:    UInt8 = 0x0F
    static let cleanQuery:    UInt8 = 0x5C
    static let clean:         UInt8 = 0x5D
    static let cleanStop:     UInt8 = 0x5E
    static let soundGet:      UInt8 = 0x21
    static let soundSet:      UInt8 = 0x22
    static let sound:         UInt8 = 0x23
    static let primeSet:      UInt8 = 0x2A
    static let primeQuery:    UInt8 = 0x2B
    static let prime:         UInt8 = 0x2C
    static let primeOpen:     UInt8 = 0x6A
    static let primeOpened:   UInt8 = 0x6B
}

enum BridgeError: Error, Equatable {
    /// Not something a phone may ask, or not well formed.
    case refused
    /// The faucet's link to the main board is down: it never heard the request.
    case linkDown
    /// The faucet was holding as many requests as it can.
    case busy
    /// Asked, and no answer came. Whether the machine acted is unknown.
    case noAnswer
    /// The machine's software predates the bridge.
    case needsUpdate
    /// The phone is not on the machine.
    case offline
    /// The main board turned it down for a reason of its own (MSG_ERR_*).
    case rejected(UInt8)
    /// The machine does not trust this device, and asking ended this way.
    case untrusted(TrustOutcome)
}

// ── What the machine says, as the app keeps it ───────────────────────────

/// StatusPayload: what the main board reads about itself.
struct MachineStatus: Codable, Equatable {
    var flags: UInt8 = 0
    var operationChannel: UInt8 = 0
    var levels: [UInt8] = [0xFF, 0xFF]
    var levelFlags: UInt8 = 0
    var ratios: [Int] = [20, 20]
    /// The carbonator wall, in tenths of a degree Celsius; nil when unread.
    var tankTenthsC: Int?
    var coldState: UInt8 = 0
    var refillState: UInt8 = 0

    static let levelUnknown: UInt8 = 0xFF
    static let segments = 4

    init() {}

    init?(_ d: Data) {
        let b = [UInt8](d)
        guard b.count >= 40 else { return nil }
        flags = b[18]
        operationChannel = b[19]
        levels = [b[27], b[28]]
        levelFlags = b[29]
        ratios = [Int(b[30]), Int(b[31])]
        let tank = Int16(bitPattern: UInt16(b[32]) | UInt16(b[33]) << 8)
        tankTenthsC = tank == Int16.min ? nil : Int(tank)
        coldState = b[36]
        refillState = b[37]
    }

    var gasAlarm: Bool { flags & 0x01 != 0 }
    var priming:  Bool { flags & 0x02 != 0 }
    var filling:  Bool { flags & 0x04 != 0 }
    var cleaning: Bool { flags & 0x08 != 0 }
    var airing:   Bool { flags & 0x10 != 0 }
    var busy: Bool { priming || filling || cleaning || airing }

    /// The reeds were read within the last few seconds.
    var levelsRead: Bool { levelFlags & 0x01 != 0 }
    var carbonatorLowReed: Bool { levelFlags & 0x02 != 0 }
    var carbonatorHighReed: Bool { levelFlags & 0x04 != 0 }
    /// A reading put in from the main board's console, not off a probe.
    var simulated: Bool { levelFlags & 0x08 != 0 }

    /// A reservoir's gauge, 0 through 4, or nil while it is not known.
    func level(_ channel: Int) -> Int? {
        guard levelsRead, levels.indices.contains(channel), levels[channel] != Self.levelUnknown else { return nil }
        return min(Int(levels[channel]), Self.segments)
    }

    var tankCelsius: Double? { tankTenthsC.map { Double($0) / 10 } }
}

/// machine_policy::ColdState and RefillState, as StatusPayload carries them.
enum ColdState: UInt8 { case fault = 0, off, holding, on, freeze }
enum RefillState: UInt8 { case idle = 0, queued, filling, timeout, fault }

struct FlavorSelection: Codable, Equatable {
    var channel: Int
    var persisted: Bool

    init(channel: Int, persisted: Bool) {
        self.channel = channel
        self.persisted = persisted
    }

    init?(_ d: Data) {
        let b = [UInt8](d)
        guard b.count >= 6, b[0] <= 1 else { return nil }
        channel = Int(b[0])
        persisted = b[1] & 0x02 != 0
    }
}

struct SoundSettings: Codable, Hashable {
    var volume = 60
    var quietOn = false
    var quietStart = 22
    var quietEnd = 7
    var quietVolume = 20
    /// The machine's clock is set; quiet hours can take effect.
    var clockSet = true
    var quietNow = false

    init() {}

    init?(_ d: Data) {
        let b = [UInt8](d)
        guard b.count >= 6 else { return nil }
        volume = Int(b[0])
        quietOn = b[1] != 0
        quietStart = Int(b[2])
        quietEnd = Int(b[3])
        quietVolume = Int(b[4])
        clockSet = b[5] & 0x01 != 0
        quietNow = b[5] & 0x02 != 0
    }

    var wire: [UInt8] {
        [UInt8(clamping: volume), quietOn ? 1 : 0, UInt8(clamping: quietStart),
         UInt8(clamping: quietEnd), UInt8(clamping: quietVolume), 0]
    }

    /// The settings a person chooses, without the machine's flags.
    func sameChoices(as other: SoundSettings) -> Bool {
        volume == other.volume && quietOn == other.quietOn && quietStart == other.quietStart
            && quietEnd == other.quietEnd && quietVolume == other.quietVolume
    }
}

enum FillOutcome: UInt8, Codable {
    case none = 0, done, full, stopped, busy, noIO, fault, gas
}

struct FillState: Codable, Equatable {
    var running = false
    var channel = 0
    var outcome = FillOutcome.none
    var elapsedMs: UInt32 = 0
    var plannedMs: UInt32 = 80_000

    init() {}

    init?(_ d: Data) {
        let b = [UInt8](d)
        guard b.count >= 12 else { return nil }
        running = b[0] == 1
        channel = Int(b[1])
        outcome = FillOutcome(rawValue: b[2]) ?? .fault
        elapsedMs = UInt32(b[3]) | UInt32(b[4]) << 8 | UInt32(b[5]) << 16 | UInt32(b[6]) << 24
        plannedMs = UInt32(b[7]) | UInt32(b[8]) << 8 | UInt32(b[9]) << 16 | UInt32(b[10]) << 24
    }
}

enum CleanOutcome: UInt8, Codable {
    case none = 0, done, stopped, busy, noIO, fault, gas
}

enum CleanStep: UInt8, Codable {
    case waterFill = 0, flush, funnel
}

struct CleanState: Codable, Equatable {
    var running = false
    var channel = 0
    var outcome = CleanOutcome.none
    var step = CleanStep.funnel
    var round = 0
    var rounds = 3
    var stepElapsedMs: UInt32 = 0
    var stepPlannedMs: UInt32 = 0
    var cycleLeftMs: UInt32 = 0

    init() {}

    init?(_ d: Data) {
        let b = [UInt8](d)
        guard b.count >= 19 else { return nil }
        func u32(_ o: Int) -> UInt32 { UInt32(b[o]) | UInt32(b[o + 1]) << 8 | UInt32(b[o + 2]) << 16 | UInt32(b[o + 3]) << 24 }
        running = b[0] == 1
        channel = Int(b[1])
        outcome = CleanOutcome(rawValue: b[2]) ?? .fault
        step = CleanStep(rawValue: b[3]) ?? .flush
        round = Int(b[4])
        rounds = Int(b[5])
        stepElapsedMs = u32(6)
        stepPlannedMs = u32(10)
        cycleLeftMs = u32(14)
    }
}

enum PrimePhase: UInt8, Codable { case off = 0, ready, running }
enum PrimeOwner: UInt8, Codable { case none = 0, enclosure, faucet }
enum PrimeOutcome: UInt8, Codable {
    case none = 0, stopped, timeout, limit, refused, canceled, leaseExpired
}

struct PrimeSession: Codable, Equatable {
    var phase = PrimePhase.off
    var channel = 0
    var owner = PrimeOwner.none
    var outcome = PrimeOutcome.none
    var elapsedMs: UInt32 = 0
    var revision: UInt32 = 0
    var sessionToken: UInt32 = 0

    init() {}

    init?(_ d: Data) {
        let b = [UInt8](d)
        guard b.count >= 20 else { return nil }
        func u32(_ o: Int) -> UInt32 { UInt32(b[o]) | UInt32(b[o + 1]) << 8 | UInt32(b[o + 2]) << 16 | UInt32(b[o + 3]) << 24 }
        phase = PrimePhase(rawValue: b[0]) ?? .off
        channel = Int(b[1])
        owner = PrimeOwner(rawValue: b[2]) ?? .none
        outcome = PrimeOutcome(rawValue: b[3]) ?? .none
        elapsedMs = u32(4)
        revision = u32(8)
        sessionToken = u32(12)
    }
}

enum PrimeOpenResult: UInt8 { case shown = 0, refused, noAnswer }

/// One reading, and when it was taken.
struct Reading<Value: Codable & Equatable>: Codable, Equatable {
    var value: Value
    var at: Date
}

/// Everything an appliance has said, as this phone last heard it, on the
/// machine's record.
struct ApplianceState: Codable, Equatable {
    var status: Reading<MachineStatus>?
    var selection: Reading<FlavorSelection>?
    var sound: Reading<SoundSettings>?
    var fill: Reading<FillState>?
    var clean: Reading<CleanState>?
    var prime: Reading<PrimeSession>?

    func ratio(_ channel: Int) -> Int? {
        status.flatMap { $0.value.ratios.indices.contains(channel) ? $0.value.ratios[channel] : nil }
    }
}

// ── The requests ─────────────────────────────────────────────────────────

struct BridgeAnswer {
    let type: UInt8
    let body: Data
}

extension BLEManager {
    /// The faucet answers for a silent main board at two seconds; a Prime
    /// waits on the enclosure's next poll.
    private static let answerWait: TimeInterval = 3.5
    private static let primeOpenWait: TimeInterval = 8.5

    /// Whether this link carries the bridge: nil until the faucet has said who
    /// the machine is, then what it said.
    var bridgeReady: Bool { bridgeVersion != nil }

    /// The faucet carries the bridge. The first time a link says so, every
    /// page's readings are read.
    func handleBridgeVersion(_ payload: Data) {
        let first = bridgeVersion == nil
        bridgeVersion = Int(payload.first ?? 0)
        bridgeMissing = false
        log.info("bridge version \(self.bridgeVersion ?? 0)")
        if first, linked { Task { await readAppliance() } }
    }

    /// The faucet answered IDENTITY without saying it carries the bridge.
    func noteIdentityAnswered() {
        let gen = linkGeneration
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            guard let self, gen == self.linkGeneration, self.linked, self.bridgeVersion == nil else { return }
            self.bridgeMissing = true
        }
    }

    /// One request, and the machine's answer to it. A change the machine
    /// turns down for want of trust is asked for on its displays and, once
    /// this device is trusted, sent again.
    func ask(_ type: UInt8, _ body: [UInt8] = []) async -> Result<BridgeAnswer, BridgeError> {
        let machine = current?.id
        let first = await request(type, body)
        guard case .failure(.untrusted) = first else { return first }
        let (reason, channel) = Self.trustReason(type, body)
        let outcome = await requestTrust(reason, channel: channel)
        guard outcome == .trusted else { return .failure(.untrusted(outcome)) }
        // Trusted, and still the same machine on the same link: only then is
        // the change sent again, once.
        guard current?.id == machine, linked else { return .failure(.offline) }
        return await request(type, body)
    }

    /// What a change is for, as the displays ask about it.
    private static func trustReason(_ type: UInt8, _ body: [UInt8]) -> (TrustReason, Int?) {
        let channel = body.first.map(Int.init)
        switch type {
        case MachineMessage.flavorSelect: return (.flavor, channel)
        case MachineMessage.ratioSetOne: return (.ratio, channel)
        case MachineMessage.fillStart: return (.fill, channel)
        case MachineMessage.fillStop: return (.fill, nil)
        case MachineMessage.cleanStart: return (.clean, channel)
        case MachineMessage.cleanStop: return (.clean, nil)
        case MachineMessage.soundSet: return (.sound, nil)
        case MachineMessage.primeOpen: return (.prime, channel)
        case MachineMessage.primeSet: return (.prime, body.count > 1 ? Int(body[1]) : nil)
        default: return (.anything, nil)
        }
    }

    private func request(_ type: UInt8, _ body: [UInt8]) async -> Result<BridgeAnswer, BridgeError> {
        if demoMode { return demoAnswer(type, body) }
        guard linked, connectedPeripheral != nil else { return .failure(.offline) }
        guard bridgeReady else { return .failure(bridgeMissing ? .needsUpdate : .offline) }
        bridgeNextID = bridgeNextID == 255 ? 1 : bridgeNextID + 1
        let id = bridgeNextID
        let gen = linkGeneration
        sendBLEFrame(type: BridgeFrame.request, payload: Data([id, type] + body))
        let wait = type == MachineMessage.primeOpen ? Self.primeOpenWait : Self.answerWait
        return await withCheckedContinuation { continuation in
            bridgeWaiting[id] = continuation
            DispatchQueue.main.asyncAfter(deadline: .now() + wait) { [weak self] in
                guard let self, let waiting = self.bridgeWaiting.removeValue(forKey: id) else { return }
                log.info("no answer to 0x\(String(type, radix: 16)) id \(id)")
                waiting.resume(returning: .failure(gen == self.linkGeneration ? .noAnswer : .offline))
            }
        }
    }

    /// BLE_FRAME_MACHINE: [reqId][type][the answer's own payload].
    func handleBridgeAnswer(_ payload: Data) {
        let b = [UInt8](payload)
        guard b.count >= 2 else { return }
        let id = b[0]
        let type = b[1]
        let body = Data(b.dropFirst(2))
        take(type, body)
        guard id != 0, let waiting = bridgeWaiting.removeValue(forKey: id) else { return }
        switch type {
        case 0xD0: waiting.resume(returning: .failure(.refused))
        case 0xD1: waiting.resume(returning: .failure(.linkDown))
        case 0xD2: waiting.resume(returning: .failure(.busy))
        case 0xD3: waiting.resume(returning: .failure(.noAnswer))
        case 0xD4: waiting.resume(returning: .failure(.needsUpdate))
        case 0xD5: waiting.resume(returning: .failure(.untrusted(.none)))
        case 0xE1...0xE9: waiting.resume(returning: .failure(.rejected(type)))
        default: waiting.resume(returning: .success(BridgeAnswer(type: type, body: body)))
        }
    }

    /// The link went: whatever was waiting will not be answered on it.
    func abandonBridgeRequests() {
        let waiting = bridgeWaiting
        bridgeWaiting = [:]
        for (_, w) in waiting { w.resume(returning: .failure(.offline)) }
        bridgeVersion = nil
        bridgeMissing = false
    }

    /// File what the machine said on its record, whoever asked.
    func take(_ type: UInt8, _ body: Data) {
        guard let m = current else { return }
        let now = Date()
        var state = m.appliance
        switch type {
        case MachineMessage.status:
            guard let s = MachineStatus(body) else { return }
            state.status = Reading(value: s, at: now)
        case MachineMessage.flavorState:
            guard let s = FlavorSelection(body) else { return }
            state.selection = Reading(value: s, at: now)
        case MachineMessage.ratio:
            let b = [UInt8](body)
            guard b.count >= 2 else { return }
            var s = state.status?.value ?? MachineStatus()
            s.ratios = [Int(b[0]), Int(b[1])]
            state.status = Reading(value: s, at: state.status?.at ?? now)
        case MachineMessage.sound:
            guard let s = SoundSettings(body) else { return }
            state.sound = Reading(value: s, at: now)
        case MachineMessage.fill:
            guard let s = FillState(body) else { return }
            state.fill = Reading(value: s, at: now)
        case MachineMessage.clean:
            guard let s = CleanState(body) else { return }
            state.clean = Reading(value: s, at: now)
        case MachineMessage.prime:
            guard let s = PrimeSession(body) else { return }
            state.prime = Reading(value: s, at: now)
        default:
            return
        }
        if state != m.appliance { m.appliance = state }
    }

    // ── What the screens ask ─────────────────────────────────────────────

    @discardableResult
    func readStatus() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.statusRequest) }

    @discardableResult
    func readSelection() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.flavorQuery) }

    /// Absolute and tokenized: a selection that crosses twice selects once.
    func selectFlavor(_ channel: Int) async -> Result<BridgeAnswer, BridgeError> {
        let token = UInt32.random(in: 1...UInt32.max)
        return await ask(MachineMessage.flavorSelect,
                         [UInt8(channel), 0] + withUnsafeBytes(of: token.littleEndian, Array.init))
    }

    /// One flavor's ratio; the machine keeps the other one at what it holds.
    func saveRatio(_ channel: Int, _ ratio: Int) async -> Result<BridgeAnswer, BridgeError> {
        await ask(MachineMessage.ratioSetOne, [UInt8(channel), UInt8(clamping: ratio)])
    }

    @discardableResult
    func readSound() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.soundGet) }

    func saveSound(_ s: SoundSettings) async -> Result<BridgeAnswer, BridgeError> {
        await ask(MachineMessage.soundSet, s.wire)
    }

    @discardableResult
    func readFill() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.fillQuery) }
    func startFill(_ channel: Int) async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.fillStart, [UInt8(channel)]) }
    func stopFill() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.fillStop) }

    @discardableResult
    func readClean() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.cleanQuery) }
    func startClean(_ channel: Int) async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.cleanStart, [UInt8(channel)]) }
    func stopClean() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.cleanStop) }

    @discardableResult
    func readPrime() async -> Result<BridgeAnswer, BridgeError> { await ask(MachineMessage.primeQuery) }

    func openPrime(_ channel: Int) async -> Result<PrimeOpenResult, BridgeError> {
        switch await ask(MachineMessage.primeOpen, [UInt8(channel)]) {
        case .success(let a):
            let b = [UInt8](a.body)
            guard a.type == MachineMessage.primeOpened, b.count >= 2 else { return .failure(.noAnswer) }
            return .success(PrimeOpenResult(rawValue: b[1]) ?? .noAnswer)
        case .failure(let e):
            return .failure(e)
        }
    }

    /// Ends the session this screen is showing, and no newer one.
    func exitPrime(_ session: PrimeSession) async -> Result<BridgeAnswer, BridgeError> {
        await ask(MachineMessage.primeSet,
                  [1, UInt8(session.channel)] + withUnsafeBytes(of: session.sessionToken.littleEndian, Array.init))
    }

    /// Everything a machine's pages show, read once when the link comes up.
    func readAppliance() async {
        await readSelection()
        await readStatus()
        await readFill()
        await readClean()
        await readPrime()
    }
}
