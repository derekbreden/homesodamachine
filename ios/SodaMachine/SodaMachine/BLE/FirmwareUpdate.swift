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

    /// Where this image goes, given which machine the phone is pointed at. The
    /// board with the radio differs between the two, and the byte follows it.
    func otaTarget(on model: MachineModel) -> OTATarget? {
        switch (model, target) {
        case (.appliance, "appliance"): return .mainBoard
        case (.appliance, "faucet"):    return .radioBoard
        case (.appliance, "enclosure"): return .farDisplay
        case (.appliance, "art"):       return .farDisplay
        case (.prototype, "prototype"): return .mainBoard
        case (.prototype, "rotary"):    return .radioBoard
        default: return nil
        }
    }
}

struct FirmwareManifest: Codable {
    let commit: String?
    let deployed: String?
    let unproven: [String]
    let images: [FirmwareImage]

    func images(for model: MachineModel) -> [FirmwareImage] {
        let want = model == .prototype ? "prototype" : "appliance"
        return images.filter { $0.machine == want && $0.available }
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
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        guard digest == image.sha256 else {
            log.error("\(image.target): sha256 \(digest) is not \(image.sha256)")
            throw URLError(.dataNotAllowed)
        }
        guard data.count == image.bytes else { throw URLError(.dataLengthExceedsMaximum) }
        payloads[image.target] = data
        return data
    }

    func release(_ target: String) { payloads[target] = nil }
}

/// What every board on the machine reports running, as the main board assembled
/// it. A board that has not answered carries an empty string, which is not the
/// same as one running nothing.
struct MachineVersions: Equatable {
    /// Keyed by OTATarget.rawValue.
    var byBoard: [UInt8: String] = [:]
    /// The crc32 over the art partition's pixels, by the board that holds one.
    var artCrc: [UInt8: UInt32] = [:]

    func version(for image: FirmwareImage, on model: MachineModel) -> String? {
        guard let t = image.otaTarget(on: model) else { return nil }
        let v = byBoard[t.rawValue] ?? ""
        return v.isEmpty ? nil : v
    }

    /// Whether this image differs from what its board reports.
    ///
    /// Firmware is a version string against a version string. The art partition
    /// carries no version — it carries a crc32 over its pixels, and the manifest
    /// carries the same one. A board that has said nothing is not called
    /// current: there is nothing to compare it to.
    func needs(_ image: FirmwareImage, on model: MachineModel) -> Bool {
        guard let t = image.otaTarget(on: model) else { return false }
        if image.kind == "art" {
            guard let running = artCrc[t.rawValue], running != 0,
                  let published = image.artCrc32 else { return false }
            return running != published
        }
        guard let running = version(for: image, on: model) else { return false }
        return running != (image.version ?? running)
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
