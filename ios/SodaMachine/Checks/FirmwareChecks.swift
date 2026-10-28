import Foundation

/// Manual experience checks against the app's actual Foundation firmware models.
/// The caller collects failures and supplies the executable entry point.
@MainActor
func runFirmwareChecks(_ check: (Bool, String) -> Void) {
    let release = "2026.10.27 abc1234"
    let releaseEpoch: UInt32 = 1_793_059_200
    let artCRC: UInt32 = 0x1234ABCD

    func image(_ target: String, kind: String = "app", version: String? = "2026.10.27 abc1234",
               epoch: UInt32? = 1_793_059_200, art: UInt32? = nil,
               machine: String = "appliance", available: Bool = true) -> FirmwareImage {
        FirmwareImage(target: target, machine: machine, what: target, kind: kind,
                      version: version, buildEpoch: epoch, bytes: 1024, crc32: 0x42,
                      artCrc32: art, sha256: "fixture", url: "https://example.invalid/firmware.bin",
                      available: available)
    }

    let main = image("appliance")
    let faucet = image("faucet")
    let enclosure = image("enclosure")
    let artwork = image("art", kind: "art", version: nil, epoch: nil, art: artCRC)
    let published = [main, faucet, enclosure, artwork]

    var versions = MachineVersions()
    for board in [OTATarget.mainBoard, .radioBoard, .farDisplay] {
        versions.byBoard[board.rawValue] = release
        versions.buildEpoch[board.rawValue] = releaseEpoch
    }
    versions.artCrc[OTATarget.farDisplay.rawValue] = artCRC

    func assess(_ offered: [FirmwareImage], _ actual: MachineVersions,
                model: MachineModel = .appliance) -> UpdateAssessment {
        UpdateAssessment(published: offered, versions: actual, model: model)
    }

    let allCurrent = assess(published, versions)
    check(allCurrent.verdict == .upToDate && allCurrent.current.count == 4
          && allCurrent.behind.isEmpty && allCurrent.unknown.isEmpty,
          "All three reported app versions and matching art CRC verify the whole machine")

    var older = versions
    older.byBoard[OTATarget.mainBoard.rawValue] = "2026.10.26 old0001"
    older.buildEpoch[OTATarget.mainBoard.rawValue] = releaseEpoch - 86_400
    let update = assess(published, older)
    check(update.verdict == .updateAvailable && update.behind.map(\.target) == ["appliance"],
          "One older app is offered without republishing the already-current components")

    var partial = MachineVersions()
    partial.byBoard[OTATarget.mainBoard.rawValue] = release
    partial.buildEpoch[OTATarget.mainBoard.rawValue] = releaseEpoch
    let partialResult = assess(published, partial)
    check(partialResult.verdict == .unverified && partialResult.current.map(\.target) == ["appliance"]
          && Set(partialResult.unknown.map(\.target)) == Set(["faucet", "enclosure", "art"]),
          "A current main board cannot establish success for unanswered displays and art")

    let nothingAnswered = assess(published, MachineVersions())
    check(nothingAnswered.verdict == .unverified && nothingAnswered.unknown.count == 4,
          "An appliance that has not answered remains unverified")

    var emptyVersion = versions
    emptyVersion.byBoard[OTATarget.farDisplay.rawValue] = ""
    let emptyResult = assess(published, emptyVersion)
    check(emptyResult.verdict == .unverified && emptyResult.unknown.map(\.target) == ["enclosure"],
          "An empty board-version string is unknown even if its epoch exists")

    var whitespaceVersion = versions
    whitespaceVersion.byBoard[OTATarget.mainBoard.rawValue] = "   "
    whitespaceVersion.buildEpoch[OTATarget.mainBoard.rawValue] = nil
    check(assess([main], whitespaceVersion).verdict == .unverified,
          "Whitespace in place of an app version cannot verify the component")

    let missingVersion = image("appliance", version: nil)
    check(assess([missingVersion], versions).verdict == .unverified,
          "An app catalog entry without its version cannot establish current software")

    let emptyPublishedVersion = image("appliance", version: "", epoch: nil)
    check(assess([emptyPublishedVersion], versions).verdict == .unverified,
          "An empty published app version remains unknown rather than no-update-needed")

    var noArt = versions
    noArt.artCrc[OTATarget.farDisplay.rawValue] = nil
    check(assess(published, noArt).verdict == .unverified,
          "A missing running art CRC prevents whole-machine verification")
    noArt.artCrc[OTATarget.farDisplay.rawValue] = 0
    check(assess([artwork], noArt).verdict == .unverified,
          "The protocol's zero art CRC means the board did not report its artwork")

    let missingPublishedArt = image("art", kind: "art", version: nil, epoch: nil, art: nil)
    check(assess([missingPublishedArt], versions).verdict == .unverified,
          "Missing published art metadata is unknown rather than a verified match")

    var otherArt = versions
    otherArt.artCrc[OTATarget.farDisplay.rawValue] = artCRC ^ 0xFFFF
    let artUpdate = assess(published, otherArt)
    check(artUpdate.verdict == .updateAvailable && artUpdate.behind.map(\.target) == ["art"],
          "A different known artwork CRC offers only the art update")

    var mixed = older
    mixed.byBoard[OTATarget.radioBoard.rawValue] = nil
    let mixedResult = assess(published, mixed)
    check(mixedResult.verdict == .updateAvailable && mixedResult.behind.map(\.target) == ["appliance"]
          && mixedResult.unknown.map(\.target) == ["faucet"],
          "A known update stays available without erasing the separate unanswered-component state")

    let unknownModel = assess(published, versions, model: .unknown)
    check(unknownModel.verdict == .nothingPublished && unknownModel.current.isEmpty,
          "An unknown machine model never reports verified current from an appliance catalog")
    check(assess([], versions).verdict == .nothingPublished,
          "An empty applicable catalog is not evidence that a machine is current")
    check(assess([image("legacy-prototype", machine: "prototype")], versions).verdict == .nothingPublished,
          "An irrelevant target does not count as a verified component")

    let catalog = FirmwareManifest(commit: "fixture", deployed: nil, unproven: [],
                                   images: [main, image("prototype", machine: "prototype"),
                                            image("enclosure", available: false)])
    check(catalog.images(for: .appliance).map(\.target) == ["appliance"],
          "The applicable catalog excludes other machine models and unavailable images")
    check(catalog.images(for: .unknown).isEmpty && catalog.images(for: .prototype).isEmpty,
          "Unsupported models have no applicable appliance release")

    var newer = versions
    newer.byBoard[OTATarget.mainBoard.rawValue] = "2026.10.28 new0001"
    newer.buildEpoch[OTATarget.mainBoard.rawValue] = releaseEpoch + 86_400
    check(assess(published, newer).verdict == .upToDate,
          "A known newer installed app does not offer a downgrade")

    var legacyNewer = newer
    legacyNewer.buildEpoch = [:]
    check(assess([image("appliance", epoch: nil)], legacyNewer).verdict == .upToDate,
          "A parseable later date verifies a legacy build when epochs are absent")
    var legacyOlder = older
    legacyOlder.buildEpoch = [:]
    check(assess([image("appliance", epoch: nil)], legacyOlder).verdict == .updateAvailable,
          "A parseable earlier date still offers a legacy app update")

    var sameDay = versions
    sameDay.byBoard[OTATarget.mainBoard.rawValue] = "2026.10.27 other99"
    sameDay.buildEpoch = [:]
    check(assess([image("appliance", epoch: nil)], sameDay).verdict == .unverified,
          "Different commits on the same date without epochs cannot be ordered or called current")
    check(assess([main], sameDay).verdict == .unverified,
          "A published epoch alone cannot order a mismatched same-day installed build")

    var malformedRunning = versions
    malformedRunning.byBoard[OTATarget.mainBoard.rawValue] = "unidentified build"
    malformedRunning.buildEpoch = [:]
    check(assess([image("appliance", epoch: nil)], malformedRunning).verdict == .unverified,
          "An unparseable installed version without an epoch remains unknown")
    check(assess([image("appliance", version: "unidentified release", epoch: nil)], versions).verdict == .unverified,
          "An unparseable published version without an epoch remains unknown")

    check(UpdateAssessment.standing(of: image("legacy-prototype", machine: "prototype"),
                                    versions: versions, model: .appliance) == nil,
          "Standing ignores an image with no target on the selected appliance")
}
