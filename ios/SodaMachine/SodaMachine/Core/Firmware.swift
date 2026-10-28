import Foundation

// ────────────────────────────────────────────────────────────
// What the catalog publishes for a machine, what each of its boards reports
// running, and whether the two agree. Nothing here reaches the radio or the
// network.
// ────────────────────────────────────────────────────────────

/// Which board an image is for, as the wire names it (proto_msg.h OTA_TGT_*).
enum OTATarget: UInt8 {
    case mainBoard = 1   // the relay's own spare slot
    case radioBoard = 2  // the display holding the radio, which needs no relay
    case farDisplay = 3  // the display on the relay's other link
}

enum OTAKind: UInt8 {
    case app = 0
    case art = 1
}

struct FirmwareImage: Codable, Identifiable, Equatable {
    let target: String
    let machine: String
    let what: String
    let kind: String
    let version: String?
    /// HEAD's commit time, and the only field two builds are ordered by. The
    /// version string above is what a person reads; a date is as fine as a
    /// screen has room for, and two builds made on one day are not ordered by
    /// one. Null from an image published before this field existed.
    let buildEpoch: UInt32?
    let bytes: Int
    let crc32: UInt32
    /// Art only: the crc32 over the pixels, which is what a board reports about
    /// the partition it holds. `crc32` is over the file, and is what the wire
    /// holds the transfer to.
    let artCrc32: UInt32?
    let sha256: String
    let url: String
    let available: Bool

    var id: String { target }

    var otaKind: OTAKind { kind == "art" ? .art : .app }

    /// Which board on the appliance this image goes to. The appliance is the
    /// machine the phone updates.
    func otaTarget(on model: MachineModel) -> OTATarget? {
        switch (model, target) {
        case (.appliance, "appliance"): return .mainBoard
        case (.appliance, "faucet"):    return .radioBoard
        case (.appliance, "enclosure"): return .farDisplay
        case (.appliance, "art"):       return .farDisplay
        default: return nil
        }
    }
}

struct FirmwareManifest: Codable {
    let commit: String?
    let deployed: String?
    let unproven: [String]
    let images: [FirmwareImage]

    /// What is published for the machine the phone is pointed at.
    func images(for model: MachineModel) -> [FirmwareImage] {
        guard model == .appliance else { return [] }
        return images.filter { $0.machine == "appliance" && $0.available }
    }
}


/// What every board on the machine reports running, as the main board assembled
/// it. A board that has not answered carries an empty string, which is not the
/// same as one running nothing.
struct MachineVersions: Codable, Equatable {
    /// Keyed by OTATarget.rawValue.
    var byBoard: [UInt8: String] = [:]
    /// The crc32 over the art partition's pixels, by the board that holds one.
    var artCrc: [UInt8: UInt32] = [:]
    /// HEAD's commit time for the build each board is running. Absent, or zero,
    /// from a board built before the field existed — "did not say", never the
    /// epoch — and the comparison falls back to the dates in the strings.
    var buildEpoch: [UInt8: UInt32] = [:]

    func version(for image: FirmwareImage, on model: MachineModel) -> String? {
        guard let t = image.otaTarget(on: model) else { return nil }
        let v = byBoard[t.rawValue] ?? ""
        return v.isEmpty ? nil : v
    }

    /// Whether this image is newer than what its board reports.
    ///
    /// Settled by the commit time both ends carry beside the version string,
    /// and by the dates inside those strings only where one end predates that
    /// field. Nothing downstream re-checks: the receiver holds the image to its
    /// crc32 and moves its boot partition.
    ///
    /// The art partition carries no version. It carries a crc32 over its
    /// pixels, the manifest carries the same one, and pixels have no order.
    ///
    /// A board that has said nothing is not called current, and not called
    /// stale either: there is nothing to compare it to.
    func needs(_ image: FirmwareImage, on model: MachineModel) -> Bool {
        guard let t = image.otaTarget(on: model) else { return false }
        if image.kind == "art" {
            guard let running = artCrc[t.rawValue], running != 0,
                  let published = image.artCrc32 else { return false }
            return running != published
        }
        guard let running = version(for: image, on: model),
              let published = image.version, published != running else { return false }

        // Both ends said when they were committed, so the question is settled
        // to the second and two builds made on one day order correctly.
        if let mine = buildEpoch[t.rawValue], mine != 0,
           let theirs = image.buildEpoch, theirs != 0 {
            return theirs > mine
        }

        // One of them did not say — a board or an image from before the field
        // existed. The dates in the strings are all that is left, and they do
        // not separate two builds made on one day, so neither is offered over
        // the other.
        guard let here = Self.buildDate(running),
              let there = Self.buildDate(published) else { return false }
        return there > here
    }

    /// The commit date a version string opens with, as one comparable number.
    ///
    /// FW_VERSION is `YYYY.MM.DD <short sha>`, with a trailing `+` where the
    /// build carried uncommitted edits. The date is that commit's own, so it
    /// can never drift from the sha beside it, and it is the only part of the
    /// string two builds can be ordered by.
    ///
    /// Two builds dated the same day are not ordered by anything the string
    /// carries.
    static func buildDate(_ version: String) -> Int? {
        let field = version.split(separator: " ").first.map(String.init) ?? version
        let parts = field.split(separator: ".")
        guard parts.count == 3,
              let y = Int(parts[0]), let m = Int(parts[1]), let d = Int(parts[2])
        else { return nil }
        return y * 10_000 + m * 100 + d
    }

    /// Every board that answered. Until one has, the machine has said nothing
    /// about itself and no claim either way is honest.
    var answered: Int { byBoard.values.filter { !$0.isEmpty }.count }
}

// ── Whether the machine runs what is published ──────────────────────────

/// One published part against what its board reports.
enum PartStanding: Equatable {
    /// The board reports this software or newer.
    case current
    /// The board reports older software.
    case behind
    /// The board has not said, or said nothing this can be compared with.
    case unknown
}

/// The machine against the catalog, part by part. Every part the catalog
/// publishes for the machine is one that has to be verified: a part that has
/// not answered is not current just because no part that has answered is
/// behind.
struct UpdateAssessment: Equatable {
    enum Verdict: Equatable {
        /// Every published part answered, and none is behind.
        case upToDate
        /// At least one part is behind.
        case updateAvailable
        /// None is known to be behind, and at least one has not answered.
        case unverified
        /// The catalog publishes nothing for this machine.
        case nothingPublished
    }

    let current: [FirmwareImage]
    let behind: [FirmwareImage]
    let unknown: [FirmwareImage]

    init(published: [FirmwareImage], versions: MachineVersions, model: MachineModel) {
        var current: [FirmwareImage] = [], behind: [FirmwareImage] = [], unknown: [FirmwareImage] = []
        for image in published {
            switch Self.standing(of: image, versions: versions, model: model) {
            case .current?: current.append(image)
            case .behind?: behind.append(image)
            case .unknown?: unknown.append(image)
            case nil: break
            }
        }
        self.current = current
        self.behind = behind
        self.unknown = unknown
    }

    var verdict: Verdict {
        if !behind.isEmpty { return .updateAvailable }
        if !unknown.isEmpty { return .unverified }
        return current.isEmpty ? .nothingPublished : .upToDate
    }

    /// Nil for an image that is not for this machine.
    static func standing(of image: FirmwareImage, versions: MachineVersions, model: MachineModel) -> PartStanding? {
        guard let target = image.otaTarget(on: model) else { return nil }
        if image.kind == "art" {
            guard let running = versions.artCrc[target.rawValue], running != 0,
                  let published = image.artCrc32 else { return .unknown }
            return running == published ? .current : .behind
        }
        guard let running = versions.version(for: image, on: model),
              let published = image.version else { return .unknown }
        if running == published { return .current }
        // Both ends said when they were committed: settled to the second.
        if let mine = versions.buildEpoch[target.rawValue], mine != 0,
           let theirs = image.buildEpoch, theirs != 0 {
            return theirs > mine ? .behind : .current
        }
        // Only the dates in the strings are left. Two builds of one day, or a
        // string that carries no date, are not ordered by anything here.
        guard let here = MachineVersions.buildDate(running),
              let there = MachineVersions.buildDate(published), here != there else { return .unknown }
        return there > here ? .behind : .current
    }
}
