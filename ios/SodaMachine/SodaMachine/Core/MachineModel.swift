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
