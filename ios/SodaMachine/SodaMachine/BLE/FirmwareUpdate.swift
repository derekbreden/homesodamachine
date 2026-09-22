import Foundation
import CryptoKit
import os

private let log = Logger(subsystem: "com.derekbreden.SodaMachine", category: "Firmware")

// ────────────────────────────────────────────────────────────
// The phone is the path a machine's firmware takes.
//
// A machine is never on WiFi and never on the internet. The phone is: it reads
// what homesodamachine.com published, holds the download to the sha256 the
// manifest names, and pushes the bytes over BLE to the board with the radio.
// That board updates itself or hands them to the main board, which hands them
// to the other display.
//
// The crc32 in the manifest is the one MSG_OTA_BEGIN promises. The board holds
// the whole image to it before its boot partition moves, so the phone passes it
// through rather than computing anything.
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

/// What went wrong on the way to a machine, in the words the screen shows.
/// A `URLError` here reaches the person as "NSURLErrorDomain error -1020".
enum FirmwareError: LocalizedError {
    case notWhatWasPublished

    var errorDescription: String? {
        "What downloaded was not the update your machine was offered. Try again."
    }
}

@Observable
final class FirmwareCatalog {
    /// Where a machine's next image comes from. Overridable so a laptop serving
    /// the site on the same network can be pointed at during development.
    static var origin: URL {
        if let raw = UserDefaults.standard.string(forKey: "firmwareOrigin"),
           let url = URL(string: raw) { return url }
        return URL(string: "https://homesodamachine.com")!
    }

    var manifest: FirmwareManifest?
    var error: String?
    var loading = false

    /// Image bytes, held only as long as the push that needs them.
    @ObservationIgnored private var payloads: [String: Data] = [:]

    func refresh() async {
        await MainActor.run { self.loading = true; self.error = nil }
        defer { Task { @MainActor in self.loading = false } }
        do {
            var request = URLRequest(url: Self.origin.appendingPathComponent("api/firmware"))
            request.cachePolicy = .reloadIgnoringLocalCacheData
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            let decoded = try JSONDecoder().decode(FirmwareManifest.self, from: data)
            await MainActor.run { self.manifest = decoded }
            log.info("Manifest: \(decoded.images.count) image(s) at \(decoded.commit ?? "?")")
        } catch {
            await MainActor.run { self.error = error.localizedDescription }
            log.error("Manifest: \(error.localizedDescription)")
        }
    }

    /// The bytes for one image, held to the sha256 the manifest named. A file
    /// that hashes differently is not the image and is not returned.
    func payload(for image: FirmwareImage) async throws -> Data {
        if let held = payloads[image.target] { return held }
        guard let url = URL(string: image.url) else { throw URLError(.badURL) }
        // NOTHING A MACHINE RUNS COMES OUT OF A CACHE. Two builds of one board
        // are usually the same number of bytes, so bytes a phone already holds
        // can carry a validator this release's bytes also carry.
        var request = URLRequest(url: url)
        request.cachePolicy = .reloadIgnoringLocalCacheData
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        guard digest == image.sha256, data.count == image.bytes else {
            log.error("\(image.target): sha256 \(digest) (\(data.count) B) is not \(image.sha256) (\(image.bytes) B)")
            throw FirmwareError.notWhatWasPublished
        }
        payloads[image.target] = data
        return data
    }

    func release(_ target: String) { payloads[target] = nil }
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

/// What the phone is doing to one board right now.
struct OTAProgress: Equatable {
    var target: String
    var what: String
    var sent: Int
    var total: Int
    var finished: Bool = false
    var failure: String? = nil

    var fraction: Double { total > 0 ? Double(sent) / Double(total) : 0 }
}

/// The failures the receiver reports, as proto_msg.h names them.
///
/// WHAT A PERSON IS TOLD IS WHAT THEY CAN DO. Which partition table a board was
/// flashed with, and whether a CRC matched, are answers to questions nobody
/// standing at a kitchen counter asked. Two things can be done about a failed
/// update: try it again, or get the machine looked at. Every one of these is
/// one of those, and the exact cause goes to the log for whoever reads logs.
enum OTAError: UInt8 {
    case none = 0, noSlot = 1, tooBig = 2, write = 3, crc = 4, verify = 5, sequence = 6

    /// True where trying again cannot help, because nothing about the machine
    /// will be different next time.
    var needsService: Bool { self == .noSlot || self == .tooBig }

    var message: String {
        needsService
            ? "This machine needs an update that can't be installed over Bluetooth."
            : "Something went wrong partway through. Your machine is unchanged."
    }

    /// For the log, not the screen.
    var detail: String {
        switch self {
        case .none:     return "stopped"
        case .noSlot:   return "single-slot partition table"
        case .tooBig:   return "image does not fit the slot"
        case .write:    return "flash write failed"
        case .crc:      return "whole-image CRC32 did not match"
        case .verify:   return "esp_ota_end / set_boot_partition refused"
        case .sequence: return "bytes arrived for the wrong offset"
        }
    }
}
