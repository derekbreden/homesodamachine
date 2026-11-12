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
