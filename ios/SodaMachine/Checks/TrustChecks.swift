import Foundation

@MainActor
func runTrustChecks(_ check: (Bool, String) -> Void) {
    check(TrustReport(Data([1, 1])) == nil, "A truncated Trust report cannot admit a request")
    check(TrustReport(Data([9, 1, 0])) == nil, "Unknown standing is not silently trusted")
    let legacy = TrustReport(Data([1, 1, 0]))
    check(legacy?.asking == true && legacy?.tag == nil && legacy?.remainingSeconds == nil,
          "Legacy asking is an explicit admission with unknown remaining time")
    let active = TrustReport(Data([1, 1, 0, 0, 0, 57, 0, 12]))
    check(active?.standing == .viewer && active?.asking == true && active?.remainingSeconds == 57 && active?.tag == 12,
          "Tagged admission carries the hardware's remaining lifetime")
    let declined = TrustReport(Data([1, 0, 2, 0x08, 0x07, 0, 0, 22]))
    check(declined?.outcome == .declined && declined?.retrySeconds == 1800 && declined?.asking == false,
          "A physical decline's cooldown is read from the machine, including the long backoff")
    let busy = TrustReport(Data([1, 0, 4, 15, 0, 0, 0, 23]))
    check(busy?.outcome == .busy && busy?.retrySeconds == 15,
          "Global quiet time is distinct from a physical decline")
    let now = Date(timeIntervalSince1970: 1000)
    var ask = TrustAsk(reason: .ratio, channel: 0, quiet: true, machine: "A", link: 3,
                       context: "flavor-A", tag: 12, sentAt: now)
    check(!ask.asking && ask.expiresAt == nil, "Sending a request alone never claims the machine displays are asking")
    ask.asking = true
    ask.expiresAt = now.addingTimeInterval(57)
    ask.retryAt = now.addingTimeInterval(30)
    check(ask.remainingSeconds(at: now) == 57 && ask.retrySeconds(at: now) == 30,
          "The status row reports the admitted request lifetime and retry deadline independently")
    check(ask.remainingSeconds(at: now.addingTimeInterval(58)) == 0,
          "An expired hardware lifetime never displays negative time")
    check(ask.retrySeconds(at: now.addingTimeInterval(29.2)) == 1,
          "Retry countdown rounds up until the actual deadline")
    check(ask.retrySeconds(at: now.addingTimeInterval(31)) == 0,
          "A completed cooldown offers a deliberate retry")
    ask.ended = .unpaired
    check(ask.shouldContinuePairing(from: .unpaired, to: .viewer),
          "Finishing Bluetooth pairing can continue its own pending Trust request")
    ask.ended = .declined
    check(!ask.shouldContinuePairing(from: .unpaired, to: .viewer) && !ask.shouldContinuePairing(from: .viewer, to: .viewer),
          "Pairing continuation never automatically retries a physical decline")
}
