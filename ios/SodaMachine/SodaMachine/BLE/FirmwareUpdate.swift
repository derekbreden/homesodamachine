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
        loading = true
        error = nil
        defer { loading = false }
        do {
            var request = URLRequest(url: Self.origin.appendingPathComponent("api/firmware"))
            request.cachePolicy = .reloadIgnoringLocalCacheData
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            let decoded = try JSONDecoder().decode(FirmwareManifest.self, from: data)
            manifest = decoded
            log.info("Manifest: \(decoded.images.count) image(s) at \(decoded.commit ?? "?")")
        } catch {
            self.error = error.localizedDescription
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
    case none = 0, noSlot = 1, tooBig = 2, write = 3, crc = 4, verify = 5, sequence = 6, busy = 7,
         untrusted = 8

    /// True where trying again cannot help, because nothing about the machine
    /// will be different next time.
    var needsService: Bool { self == .noSlot || self == .tooBig }

    var message: String {
        if self == .busy { return "Another phone is updating this machine. Try again when it's done." }
        if self == .untrusted { return "The machine doesn't trust this \(BLEManager.deviceWord) yet. Nothing changed." }
        return needsService
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
        case .busy:     return "another phone's transfer is in flight"
        case .untrusted: return "from a phone the machine does not trust"
        }
    }
}
