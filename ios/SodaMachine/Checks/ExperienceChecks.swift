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

        for failure in failures { print("FAIL: \(failure)") }
        print("\(count - failures.count)/\(count) experience checks passed")
        if !failures.isEmpty { exit(1) }
    }
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
