import Foundation
import CoreBluetooth

// ────────────────────────────────────────────────────────────
// What is in range, and which one the app is pointed at.
//
// Two machines standing a metre apart both answer the Nordic UART service, so
// the advertisement has to say which is which before either is connected to.
// Each carries a manufacturer block — 0xFFFF, then the model byte and the low
// three bytes of that machine's main board MAC — and a local name built from
// the same unit, or whatever someone named the machine.
//
// A machine's identity therefore belongs to its main board, not to the display
// holding the radio. A display moved between machines advertises the machine it
// is now wired to.
// ────────────────────────────────────────────────────────────

enum MachineModel: UInt8 {
    case unknown = 0
    case appliance = 1
    case prototype = 2

    var label: String {
        switch self {
        case .appliance: return "Appliance"
        case .prototype: return "Prototype"
        case .unknown: return "Soda Machine"
        }
    }
}

struct DiscoveredMachine: Identifiable, Equatable {
    /// CoreBluetooth's per-install peripheral id. Stable on this phone, which is
    /// what "connect to the one I picked last time" needs.
    let id: String
    var name: String
    var model: MachineModel
    /// The main board's own three bytes, e.g. "7AFC20". Empty from a machine
    /// whose firmware predates the manufacturer block.
    var unit: String
    var rssi: Int
    var lastSeen: Date

    var displayName: String {
        name.isEmpty ? (unit.isEmpty ? "Soda Machine" : "SodaMachine \(unit.suffix(4))") : name
    }

    /// Distinct even when two machines share a name: the unit is the machine.
    var subtitle: String {
        let bars = signal
        return unit.isEmpty ? "\(model.label) · \(bars)" : "\(model.label) · \(unit) · \(bars)"
    }

    var signal: String {
        switch rssi {
        case (-55)...:    return "right here"
        case (-70)..<(-55): return "nearby"
        case (-85)..<(-70): return "far"
        default:          return "very far"
        }
    }
}

enum MachineAdvert {
    static let manufacturerID: UInt16 = 0xFFFF

    /// What a scan result says about the machine behind it, or nil when the
    /// peripheral is not one of ours.
    static func read(peripheral: CBPeripheral,
                     advertisementData: [String: Any],
                     rssi: NSNumber) -> DiscoveredMachine? {
        let advertised = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        let name = advertised ?? peripheral.name ?? ""

        var model = MachineModel.unknown
        var unit = ""
        if let mfg = advertisementData[CBAdvertisementDataManufacturerDataKey] as? Data,
           mfg.count >= 6 {
            let base = mfg.startIndex
            let company = UInt16(mfg[base]) | (UInt16(mfg[base + 1]) << 8)
            if company == manufacturerID {
                model = MachineModel(rawValue: mfg[base + 2]) ?? .unknown
                unit = mfg[(base + 3)..<(base + 6)].map { String(format: "%02X", $0) }.joined()
            }
        }

        // A machine that predates the manufacturer block still answers to the
        // name every unit used to carry.
        if unit.isEmpty && !name.hasPrefix("SodaMachine") && model == .unknown { return nil }

        return DiscoveredMachine(id: peripheral.identifier.uuidString,
                                 name: name.hasPrefix("SodaMachine") ? "" : name,
                                 model: model,
                                 unit: unit,
                                 rssi: rssi.intValue,
                                 lastSeen: Date())
    }
}
