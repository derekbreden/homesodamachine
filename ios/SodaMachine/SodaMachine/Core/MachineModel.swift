import Foundation

/// What kind of machine a record is, as its advertisement or main board says.
enum MachineModel: UInt8, Codable {
    case unknown = 0
    case appliance = 1
    case prototype = 2

    var label: String {
        switch self {
        case .appliance: return "Soda machine"
        case .prototype: return "Prototype"
        case .unknown: return "Soda machine"
        }
    }
}

/// Why the machine is not making soda, as its status names it (NOTICE_* in
/// firmware/lib/proto_link/proto_msg.h), in the words its own glasses use.
enum MachineNotice: UInt8, Codable {
    case none = 0
    case noWater = 1
    case sweep = 2       // a first start: the tank's air goes out at the faucet before its first fill
    case sweepDone = 3   // that sweep has met its target, and the lever is to be let go
    case moving = 4      // drained for a move; the next start is a first start

    var title: String? {
        switch self {
        case .none: return nil
        case .noWater: return "No water"
        case .sweep: return "Welcome"
        case .sweepDone: return "Done"
        case .moving: return "Moving the machine"
        }
    }

    var message: String? {
        switch self {
        case .none: return nil
        case .noWater:
            return "The machine pumped and its tank did not fill. Check that the water is turned on and that nothing around the machine is wet, then tap Try again on the machine’s display."
        case .sweep:
            return "With the cylinder open, hold the faucet’s lever down until its display says Done. Gas hisses while the tank clears its air."
        case .sweepDone:
            return "Let go of the faucet’s lever. The machine fills itself now."
        case .moving:
            return "It stops pouring and filling while it is drained. Follow the steps on its display. When it is plugged in again, it welcomes you."
        }
    }

    var icon: String {
        switch self {
        case .none: return "info.circle"
        case .noWater: return "drop.triangle"
        case .sweep: return "hand.wave"
        case .sweepDone: return "checkmark.circle"
        case .moving: return "shippingbox"
        }
    }

    var urgent: Bool { self == .noWater }

    /// The carbonator's water as the notice leaves it, where its reeds alone would mislead:
    /// a dry tank reads between its marks.
    var water: String? {
        switch self {
        case .sweep: return "Empty until its air is cleared"
        case .sweepDone: return "Fills once the lever is let go"
        case .moving: return "Draining for a move"
        case .none, .noWater: return nil
        }
    }
}

/// StatusPayload: what the main board reads about itself.
struct MachineStatus: Codable, Equatable {
    var flags: UInt8 = 0
    var operationChannel: UInt8 = 0
    var reservoirReeds: [UInt8]?
    var levels: [UInt8] = [0xFF, 0xFF]
    var levelFlags: UInt8 = 0
    var ratios: [Int] = [20, 20]
    /// The carbonator wall, in tenths of a degree Celsius; nil when unread.
    var tankTenthsC: Int?
    var coilTenthsC: Int?
    var coldState: UInt8 = .max
    var refillState: UInt8 = .max
    /// A missing count identifies status from before the thermal fields were sent.
    var probeCount: Int?
    var startupCoolingSeconds: Int?
    /// Seconds since the machine last started; nil in a reading kept from
    /// before the app read it.
    var uptimeS: UInt32?
    /// NOTICE_*: what stops the machine making soda; nil in a reading kept
    /// from before the app read it.
    var notice: UInt8?

    static let levelUnknown: UInt8 = 0xFF
    static let segments = 4

    init() {}

    init?(_ d: Data) {
        let b = [UInt8](d)
        guard b.count >= 32 else { return nil }
        uptimeS = UInt32(b[0]) | UInt32(b[1]) << 8 | UInt32(b[2]) << 16 | UInt32(b[3]) << 24
        flags = b[18]
        operationChannel = b[19]
        reservoirReeds = [b[25], b[26]]
        levels = [b[27], b[28]]
        levelFlags = b[29]
        ratios = [Int(b[30]), Int(b[31])]
        if b.count >= 39 {
            func probe(at index: Int) -> Int? {
                let value = Int16(bitPattern: UInt16(b[index]) | UInt16(b[index + 1]) << 8)
                return value == .min ? nil : Int(value)
            }
            tankTenthsC = probe(at: 32)
            coilTenthsC = probe(at: 34)
            coldState = b[36]
            refillState = b[37]
            probeCount = Int(b[38])
        }
        if b.count >= 40 { notice = b[39] }
        if b.count >= 42 {
            let seconds = UInt16(b[40]) | UInt16(b[41]) << 8
            if seconds != 0 && seconds != .max { startupCoolingSeconds = Int(seconds) }
        }
    }

    var machineNotice: MachineNotice { notice.flatMap(MachineNotice.init(rawValue:)) ?? .none }

    var gasAlarm: Bool { flags & 0x01 != 0 }
    var priming:  Bool { flags & 0x02 != 0 }
    var filling:  Bool { flags & 0x04 != 0 }
    var cleaning: Bool { flags & 0x08 != 0 }
    var airing:   Bool { flags & 0x10 != 0 }
    var busy: Bool { priming || filling || cleaning || airing }
    var compressorRunning: Bool { flags & 0x40 != 0 }

    /// The reeds were read within the last few seconds.
    var levelsRead: Bool { levelFlags & 0x01 != 0 }
    var carbonatorLowReed: Bool { levelFlags & 0x02 != 0 }
    var carbonatorHighReed: Bool { levelFlags & 0x04 != 0 }
    /// A reading put in from the main board's console, not off a probe.
    var simulated: Bool { levelFlags & 0x08 != 0 }

    func reedMask(_ channel: Int) -> UInt8? {
        guard levelsRead, let reservoirReeds, reservoirReeds.indices.contains(channel) else { return nil }
        return reservoirReeds[channel] & 0x0F
    }

    /// A reservoir's gauge, 0 through 4, or nil while it is not known.
    func level(_ channel: Int) -> Int? {
        guard levelsRead, levels.indices.contains(channel), levels[channel] != Self.levelUnknown else { return nil }
        return min(Int(levels[channel]), Self.segments)
    }

    var tankCelsius: Double? { tankTenthsC.map { Double($0) / 10 } }

    /// Matches front_cooling.h so both screens describe the actual relay and its interlocks.
    var coolingState: CoolingState {
        guard probeCount != nil else { return .unavailable }
        if gasAlarm { return .paused }
        guard let cold = ColdState(rawValue: coldState) else { return .unavailable }
        if cold == .fault { return .probeFault }
        if cold == .freeze { return .freezeProtection }
        guard tankTenthsC != nil, coilTenthsC != nil else { return .probeFault }
        if compressorRunning { return .running }
        if cold == .holding { return startupCoolingSeconds == nil ? .restartHold : .startupWait }
        return cold == .off ? .idle : .paused
    }
}

/// machine_policy::ColdState and RefillState, as StatusPayload carries them.
enum ColdState: UInt8 { case fault = 0, off, holding, on, freeze }
enum RefillState: UInt8 { case idle = 0, queued, filling, timeout, fault }

enum CoolingState {
    case unavailable, probeFault, freezeProtection, running, startupWait, restartHold, idle, paused
}

/// One reading, and when the machine supplied it.
struct Reading<Value: Codable & Equatable>: Codable, Equatable {
    var value: Value
    var at: Date
}

extension Reading where Value == MachineStatus {
    func liveStatus(at now: Date, connected: Bool) -> MachineStatus? {
        let age = now.timeIntervalSince(at)
        return connected && age >= 0 && age < 10 ? value : nil
    }
}
