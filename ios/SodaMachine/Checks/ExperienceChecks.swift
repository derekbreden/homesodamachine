import Foundation

@main
@MainActor
enum ExperienceChecks {
    static func main() {
        var count = 0
        var failures: [String] = []
        let check: (Bool, String) -> Void = { passed, description in
            count += 1
            if !passed { failures.append(description) }
        }

        runNavigationChecks(check)
        runFirmwareChecks(check)
        runSettingsSyncChecks(check)
        runMixChecks(check)
        runTrustChecks(check)
        runHistoryChecks(check)
        runNoticeChecks(check)
        runCoolingChecks(check)

        for failure in failures { print("FAIL: \(failure)") }
        print("\(count - failures.count)/\(count) experience checks passed")
        if !failures.isEmpty { exit(1) }
    }
}

/// The app and the enclosure read the same status frame at every supported length.
@MainActor
private func runCoolingChecks(_ check: (Bool, String) -> Void) {
    var bytes = [UInt8](repeating: 0, count: 42)
    bytes[18] = 0x20     // pouring, with the compressor off
    bytes[25...31] = [0xF4, 0x82, 3, 1, 7, 15, 20]
    bytes[32...41] = [167, 0, 0xDD, 0xFF, 2, 1, 2, 1, 125, 0]
    func status(_ length: Int = 42) -> MachineStatus { MachineStatus(Data(bytes.prefix(length)))! }
    check(MachineStatus(Data(bytes.prefix(31))) == nil, "Status requires the complete 32-byte core")
    let core = status(32)
    check(core.level(0) == 3 && core.level(1) == 1 && core.reedMask(0) == 4 && core.reedMask(1) == 2
          && core.ratios == [15, 20] && core.carbonatorLowReed && core.carbonatorHighReed,
          "Older boards still supply their reed masks, levels and mix")
    check(core.coolingState == .unavailable && core.tankTenthsC == nil && status(38).probeCount == nil,
          "A missing or partial thermal extension leaves cooling unavailable")
    let thermal = status(39)
    check(thermal.tankTenthsC == 167 && thermal.coilTenthsC == -35 && thermal.probeCount == 2
          && thermal.refillState == RefillState.queued.rawValue && thermal.notice == nil,
          "The 39-byte extension carries two independent signed probes and the controller state")
    check(thermal.coolingState == .restartHold && status(40).machineNotice == .noWater
          && status(41).startupCoolingSeconds == nil,
          "An older status can carry a hold or a notice without a complete timer")
    check(status().coolingState == .startupWait && status().startupCoolingSeconds == 125,
          "A warm restart shows the controller’s remaining seconds")
    bytes[40...41] = [0x02, 0x01]
    check(status().startupCoolingSeconds == 258, "The countdown uses both bytes in little-endian order")
    for sentinel: UInt8 in [0, 0xFF] {
        bytes[40...41] = [sentinel, sentinel]
        check(status().startupCoolingSeconds == nil && status().coolingState == .restartHold,
              "A hidden or already-running countdown never displays as seconds")
    }
    bytes[18] = 0x80
    bytes[36] = 1
    check(status().coolingState == .idle, "The refill relay is independent of the compressor")
    bytes[36] = 3
    check(status().coolingState == .paused, "A cooling demand with an open compressor relay is paused")
    bytes[18] = 0x40
    check(status().coolingState == .running, "The compressor relay confirms running")
    bytes[32...33] = [0, 0x80]
    check(status().coolingState == .probeFault && status().tankTenthsC == nil && status().coilTenthsC == -35,
          "A failed tank probe leaves the valid coil reading intact")
    bytes[32...35] = [0, 0, 0, 0x80]
    check(status().coolingState == .probeFault && status().tankTenthsC == 0 && status().coilTenthsC == nil,
          "Zero degrees is a real reading when only the coil is unread")
    bytes[36] = 4
    check(status().coolingState == .freezeProtection, "Freeze protection takes precedence over the relay and probes")
    bytes[18] = 0x41
    check(status().coolingState == .paused, "A gas trip takes precedence over freeze protection and the relay")
    bytes[18] = 0x40
    bytes[36] = 0xA5
    check(status().coolingState == .unavailable, "An unknown controller state cannot report running")
    bytes[29] = 0
    check(status().reedMask(0) == nil && status().level(1) == nil, "Unread switches do not imply open switches")

    let sampled = Date()
    let reading = Reading(value: thermal, at: sampled)
    check(reading.liveStatus(at: sampled, connected: true) == thermal
          && reading.liveStatus(at: sampled.addingTimeInterval(10), connected: true) == nil
          && reading.liveStatus(at: sampled, connected: false) == nil,
          "Only a fresh sample from this connection supplies a live temperature or countdown")
    let f = MachineTemperatureUnit.fahrenheit, c = MachineTemperatureUnit.celsius
    check(f.format(tenthsC: 167, compact: true) == "62°F" && c.format(tenthsC: 167, compact: true) == "17°C"
          && f.format(tenthsC: 167) == "62.1°F" && c.format(tenthsC: 167) == "16.7°C"
          && f.format(tenthsC: -175, compact: true) == "1°F" && f.format(tenthsC: -225, compact: true) == "-9°F"
          && c.format(tenthsC: -4, compact: true) == "0°C" && c.format(tenthsC: -5, compact: true) == "-1°C"
          && c.format(tenthsC: -2) == "-0.2°C",
          "Both units match the enclosure’s precision and signed rounding")
    check(f.format(tenthsC: nil) == "--" && c.format(tenthsC: Int(Int16.min)) == "--",
          "A missing probe never formats as zero or an extreme temperature")
}

/// What the machine's notice byte says on the phone: the kinds its firmware sends
/// (NOTICE_* in firmware/lib/proto_link/proto_msg.h), and nothing for a kind it does not know.
@MainActor
func runNoticeChecks(_ check: (Bool, String) -> Void) {
    check(MachineNotice(rawValue: 0) == MachineNotice.none && MachineNotice.none.title == nil,
          "No notice puts nothing on the machine page")
    check(MachineNotice(rawValue: 1) == .noWater && MachineNotice.noWater.urgent
          && MachineNotice.noWater.message?.contains("Try again on the machine’s display") == true,
          "No water points at Try again on the machine's display")
    check(MachineNotice(rawValue: 2) == .sweep && MachineNotice.sweep.title == "Welcome"
          && MachineNotice.sweep.message?.contains("until its display says Done") == true
          && MachineNotice.sweep.water != nil,
          "A first start welcomes the person and sends them to the faucet's lever")
    check(MachineNotice(rawValue: 3) == .sweepDone && MachineNotice.sweepDone.title == "Done"
          && MachineNotice.sweepDone.message?.hasPrefix("Let go") == true,
          "The sweep's end asks for the lever to be let go")
    check(MachineNotice(rawValue: 4) == .moving && MachineNotice.moving.message?.contains("welcomes you") == true
          && MachineNotice.moving.water == "Draining for a move",
          "A move says the next start welcomes the person again")
    check(MachineNotice(rawValue: 5) == nil && MachineNotice.none.water == nil && MachineNotice.noWater.water == nil,
          "A notice this app does not know says nothing, and the reeds say where the water is")
}
