import Foundation

enum TrustStanding: UInt8 { case unpaired = 0, viewer, trusted }
enum TrustOutcome: UInt8 {
    case none = 0, trusted, declined, timedOut, busy, unpaired, canceled
    case lostLink = 0xF0
}
enum TrustReason: UInt8 {
    case anything = 0, flavor, ratio, image, fill, clean, prime, sound, name, update
}

/// A request belongs to the machine, connection and page that made it.
/// `asking` is an acknowledgement from the faucet, never an inference from a send.
struct TrustAsk: Equatable {
    let reason: TrustReason
    let channel: Int?
    let quiet: Bool
    let machine: String
    let link: Int
    let context: String?
    var tag: UInt8
    var sentAt: Date
    var asking = false
    var expiresAt: Date?
    var retryAt: Date?
    var ended: TrustOutcome?

    func retrySeconds(at now: Date) -> Int {
        max(0, Int(ceil((retryAt ?? now).timeIntervalSince(now))))
    }

    func remainingSeconds(at now: Date) -> Int {
        max(0, Int(ceil((expiresAt ?? now).timeIntervalSince(now))))
    }

    func shouldContinuePairing(from previous: TrustStanding?, to current: TrustStanding) -> Bool {
        previous == .unpaired && current == .viewer && ended == .unpaired
    }

    var purpose: String {
        let flavor = channel.map { "Flavor \($0 + 1)" }
        switch reason {
        case .flavor: return flavor.map { "to put \($0) on tap" } ?? "to change the flavor on tap"
        case .ratio: return flavor.map { "to save \($0)'s mix" } ?? "to save a mix"
        case .image: return flavor.map { "to change \($0)'s image" } ?? "to change flavor images"
        case .fill: return flavor.map { "to fill \($0)" } ?? "to fill a flavor"
        case .clean: return flavor.map { "to clean \($0)" } ?? "to clean a flavor"
        case .prime: return flavor.map { "to prime \($0)" } ?? "to prime a flavor"
        case .sound: return "to change the sound"
        case .name: return "to rename the machine"
        case .update: return "to update the machine"
        case .anything: return "to change settings and run cycles"
        }
    }
}

struct TrustReport: Equatable {
    let standing: TrustStanding
    let asking: Bool
    let outcome: TrustOutcome
    let retrySeconds: Int
    let remainingSeconds: Int?
    let tag: UInt8?

    init?(_ payload: Data) {
        let b = [UInt8](payload)
        guard b.count >= 3, let standing = TrustStanding(rawValue: b[0]) else { return nil }
        self.standing = standing
        asking = b[1] != 0
        outcome = TrustOutcome(rawValue: b[2]) ?? .none
        retrySeconds = b.count >= 5 ? Int(b[3]) | Int(b[4]) << 8 : 0
        remainingSeconds = b.count >= 7 ? Int(b[5]) | Int(b[6]) << 8 : nil
        tag = b.count >= 8 ? b[7] : nil
    }
}
