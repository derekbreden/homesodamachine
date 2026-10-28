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

        for failure in failures { print("FAIL: \(failure)") }
        print("\(count - failures.count)/\(count) experience checks passed")
        if !failures.isEmpty { exit(1) }
    }
}
