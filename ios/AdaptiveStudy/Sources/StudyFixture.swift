import Foundation
import Observation

/// Local presentation state for the native app proposal.
/// Confirmed sample values are separate from edits awaiting Save.
@Observable
@MainActor
final class StudyFixture {
    enum Connection {
        case connected
        case outOfRange
        case bluetoothOff
    }

    private(set) var selectedMachine = 0
    private(set) var names = ["Kitchen", "Workshop"]
    var connection: Connection
    var selectedChannel = 0
    private(set) var activeFlavor = 0
    private(set) var ratios = [20, 20]
    private(set) var arts = [0, 1]
    var draftRatio = 20
    var draftName = "Kitchen"
    var volume = 60.0
    var quietVolume = 20.0
    var quiet = true
    var startHour = 22
    var endHour = 7

    private var machineConnections: [Connection] = [.connected, .outOfRange]
    private let units = ["A1B2C3", "D4E5F6"]

    var machineName: String { names[selectedMachine] }
    var unit: String { units[selectedMachine] }
    var isConnected: Bool { connection == .connected }

    init(route: StudyRoute) {
        switch route {
        case .offline, .lost:
            connection = .outOfRange
            machineConnections[0] = .outOfRange
        case .bluetooth:
            connection = .bluetoothOff
        default:
            connection = .connected
        }
    }

    func selectMachine(_ index: Int) {
        guard names.indices.contains(index) else { return }
        if connection != .bluetoothOff {
            machineConnections[selectedMachine] = connection
            connection = machineConnections[index]
        }
        selectedMachine = index
        selectedChannel = 0
        draftRatio = ratios[selectedChannel]
        draftName = machineName
    }

    func beginFlavor(channel: Int) {
        guard ratios.indices.contains(channel) else { return }
        selectedChannel = channel
        draftRatio = ratios[channel]
    }

    func saveRatio() {
        guard isConnected, ratios.indices.contains(selectedChannel) else { return }
        ratios[selectedChannel] = min(24, max(6, draftRatio))
        draftRatio = ratios[selectedChannel]
    }

    func beginRename() {
        draftName = machineName
    }

    func saveName() {
        let candidate = draftName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard isConnected, !candidate.isEmpty else { return }
        names[selectedMachine] = String(candidate.prefix(20))
        draftName = machineName
    }

    func selectFlavorAtFaucet() {
        guard isConnected, ratios.indices.contains(selectedChannel) else { return }
        activeFlavor = selectedChannel
    }

    func selectArt(_ art: Int) {
        guard isConnected, arts.indices.contains(selectedChannel), (0..<8).contains(art) else { return }
        arts[selectedChannel] = art
    }
}
