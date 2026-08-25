import SwiftUI

// ────────────────────────────────────────────────────────────
// What this machine is running, and what homesodamachine.com has published.
//
// A board's version string is written into its own tree by pre_build.py and
// reported back over the wire, and the manifest carries the same string. So
// "current" is a comparison of one value against itself rather than two
// independent readings of a date.
//
// While a display is taking an image it goes dark and reboots either way. The
// phone is what says so — the screen being written cannot.
// ────────────────────────────────────────────────────────────

struct FirmwareUpdateView: View {
    @Environment(BLEManager.self) var ble
    @State private var catalog = FirmwareCatalog()
    @State private var failure: String?

    private var model: MachineModel { ble.connectedMachine?.model ?? .unknown }
    private var images: [FirmwareImage] { catalog.manifest?.images(for: model) ?? [] }

    var body: some View {
        VStack(spacing: 14) {
            header

            if let push = ble.otaProgress {
                pushing(push)
            } else if catalog.loading {
                ProgressView().tint(Theme.textPrimary).padding(.vertical, 24)
            } else if let error = catalog.error {
                message("Could not reach homesodamachine.com", error)
            } else if images.isEmpty {
                message("Nothing published for this machine", "The manifest carries no image for a \(model.label.lowercased()).")
            } else {
                ScrollView {
                    VStack(spacing: 10) { ForEach(images) { row($0) } }
                }
            }

            if let failure {
                Text(failure)
                    .font(.system(size: 13))
                    .foregroundStyle(.orange)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 20)
            }
        }
        .task { await catalog.refresh() }
    }

    private var header: some View {
        VStack(spacing: 4) {
            Text("Firmware")
                .font(.system(size: 20, weight: .medium))
                .foregroundStyle(Theme.textPrimary)
            if !ble.radioBoardVersion.isEmpty {
                Text("this machine reports \(ble.radioBoardVersion)")
                    .font(.system(size: 12))
                    .foregroundStyle(Theme.textSecondary)
            }
        }
        .padding(.top, 20)
    }

    private func pushing(_ push: OTAProgress) -> some View {
        VStack(spacing: 12) {
            Text(push.what)
                .font(.system(size: 15, weight: .medium))
                .foregroundStyle(Theme.textPrimary)

            ProgressView(value: push.fraction)
                .tint(Theme.textPrimary)
                .padding(.horizontal, 24)

            Text("\(push.sent.formatted()) of \(push.total.formatted()) bytes")
                .font(.system(size: 12).monospacedDigit())
                .foregroundStyle(Theme.textSecondary)

            if push.finished {
                Text("Verified. The board is restarting into it.")
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
            } else if let why = push.failure {
                Text(why)
                    .font(.system(size: 13))
                    .foregroundStyle(.orange)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 20)
            } else {
                // The display being written goes dark for the whole write and
                // reboots either way; a half-finished transfer costs a reboot
                // into what it was already running, and a pulled plug costs more.
                Text("Keep the phone near the machine. Do not unplug it.")
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 20)

                Button("Cancel") { ble.cancelUpdate() }
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
            }

            if push.finished || push.failure != nil {
                Button("Done") { ble.otaProgress = nil }
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.top, 4)
            }
        }
        .padding(.vertical, 20)
    }

    private func row(_ image: FirmwareImage) -> some View {
        let current = image.version != nil && image.version == ble.radioBoardVersion
        return HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 3) {
                Text(image.what)
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                Text("\(image.version ?? "no version") · \(image.bytes.formatted()) bytes")
                    .font(.system(size: 12))
                    .foregroundStyle(Theme.textSecondary)
            }
            Spacer()
            Button(current ? "Reinstall" : "Install") { push(image) }
                .font(.system(size: 14, weight: .medium))
                .foregroundStyle(Theme.textPrimary)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(Color.white.opacity(0.15))
                .cornerRadius(8)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color.white.opacity(0.08))
        .cornerRadius(12)
        .padding(.horizontal, 20)
    }

    private func message(_ title: String, _ body: String) -> some View {
        VStack(spacing: 6) {
            Text(title)
                .font(.system(size: 15, weight: .medium))
                .foregroundStyle(Theme.textPrimary)
            Text(body)
                .font(.system(size: 13))
                .foregroundStyle(Theme.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 24)
    }

    private func push(_ image: FirmwareImage) {
        failure = nil
        Task {
            do {
                let data = try await catalog.payload(for: image)
                await MainActor.run { ble.startUpdate(image: image, data: data, on: model) }
            } catch {
                await MainActor.run {
                    failure = "Could not fetch \(image.target): \(error.localizedDescription)"
                }
            }
        }
    }
}
