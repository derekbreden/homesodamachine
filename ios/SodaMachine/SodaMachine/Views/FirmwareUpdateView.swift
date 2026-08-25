import SwiftUI

// ────────────────────────────────────────────────────────────
// Whether this machine is current, and the one button that makes it so.
//
// A machine is several boards, and being current is all of them being current.
// Each reports the version string `pre_build.py` wrote into its own tree, and
// the manifest carries the same strings — so the comparison is a value against
// itself, not two readings of a date. The animation partition carries a crc32
// instead of a version, and the manifest carries that too.
//
// A board that has said nothing is not counted as behind. Until the machine has
// answered at all, neither claim is made.
// ────────────────────────────────────────────────────────────

struct FirmwareUpdateView: View {
    @Environment(BLEManager.self) var ble
    @State private var catalog = FirmwareCatalog()
    @State private var checking = false

    private var model: MachineModel { ble.connectedMachine?.model ?? .unknown }
    private var published: [FirmwareImage] { catalog.manifest?.images(for: model) ?? [] }
    private var behind: [FirmwareImage] {
        published.filter { ble.machineVersions.needs($0, on: model) }
    }
    private var heardFrom: Bool { ble.machineVersions.answered > 0 }

    var body: some View {
        VStack(spacing: 18) {
            Text("Firmware")
                .font(.system(size: 20, weight: .medium))
                .foregroundStyle(Theme.textPrimary)
                .padding(.top, 24)

            Spacer()

            if let push = ble.otaProgress {
                pushing(push)
            } else if catalog.loading || checking {
                ProgressView().tint(Theme.textPrimary)
                Text("Checking for updates")
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
            } else if let error = catalog.error {
                state("Could not reach homesodamachine.com", error)
                checkButton()
            } else if !heardFrom {
                state("Asking the machine what it is running",
                      "It has not answered yet.")
                checkButton()
            } else if behind.isEmpty {
                state("Your machine is up to date",
                      running)
                checkButton()
            } else {
                available
            }

            Spacer()
        }
        .task { await check() }
    }

    // MARK: - The one button

    private var available: some View {
        VStack(spacing: 14) {
            Text("An update is available")
                .font(.system(size: 17, weight: .medium))
                .foregroundStyle(Theme.textPrimary)

            Text(behind.count == 1
                 ? "One part of your machine has a newer version."
                 : "\(behind.count) parts of your machine have newer versions.")
                .font(.system(size: 14))
                .foregroundStyle(Theme.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)

            Button {
                ble.startUpdateAll(behind, on: model) { try await catalog.payload(for: $0) }
            } label: {
                Text("Update Now")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Theme.accent)
                    .cornerRadius(14)
            }
            .padding(.horizontal, 28)
            .padding(.top, 8)

            Text("Keep your phone near the machine. Do not unplug it.")
                .font(.system(size: 12))
                .foregroundStyle(Theme.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }

    // MARK: - While it runs

    private func pushing(_ push: OTAProgress) -> some View {
        VStack(spacing: 14) {
            if push.finished && ble.otaQueue.isEmpty {
                Text("Update complete")
                    .font(.system(size: 17, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                Text("Your machine is restarting into it.")
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
                Button("Done") { ble.otaProgress = nil }
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.top, 6)
            } else if let why = push.failure {
                Text("The update stopped")
                    .font(.system(size: 17, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                Text(why)
                    .font(.system(size: 13))
                    .foregroundStyle(.orange)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
                Text("Your machine is still running what it was.")
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
                Button("Done") { ble.otaProgress = nil }
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.top, 6)
            } else {
                Text("Updating your machine")
                    .font(.system(size: 17, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)

                ProgressView(value: overall)
                    .tint(Theme.accent)
                    .scaleEffect(x: 1, y: 1.6, anchor: .center)
                    .padding(.horizontal, 32)

                Text(step)
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)

                Text("Keep your phone near the machine. Do not unplug it.")
                    .font(.system(size: 12))
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
                    .padding(.top, 4)

                Button("Cancel") { ble.cancelUpdate() }
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
            }
        }
    }

    /// One bar for the whole tap, not one per board.
    private var overall: Double {
        let total = ble.otaQueueDone + ble.otaQueue.count
        guard total > 0, let push = ble.otaProgress else { return 0 }
        return (Double(ble.otaQueueDone) + push.fraction) / Double(total)
    }

    private var step: String {
        let total = ble.otaQueueDone + ble.otaQueue.count
        guard let push = ble.otaProgress else { return "" }
        return total > 1
            ? "\(push.what) — part \(ble.otaQueueDone + 1) of \(total)"
            : push.what
    }

    // MARK: - Pieces

    private var running: String {
        let v = ble.machineVersions.byBoard.values.filter { !$0.isEmpty }
        return v.first.map { "Running \($0)" } ?? ""
    }

    private func state(_ title: String, _ body: String) -> some View {
        VStack(spacing: 8) {
            Text(title)
                .font(.system(size: 17, weight: .medium))
                .foregroundStyle(Theme.textPrimary)
                .multilineTextAlignment(.center)
            if !body.isEmpty {
                Text(body)
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
            }
        }
        .padding(.horizontal, 32)
    }

    private func checkButton() -> some View {
        Button("Check for Updates") { Task { await check() } }
            .font(.system(size: 16, weight: .medium))
            .foregroundStyle(Theme.textPrimary)
            .padding(.horizontal, 22)
            .padding(.vertical, 12)
            .background(Color.white.opacity(0.12))
            .cornerRadius(12)
            .padding(.top, 14)
    }

    private func check() async {
        checking = true
        ble.send("IDENTITY")          // ask the machine to say what it is running
        await catalog.refresh()
        // Give the machine's answer the same beat the manifest took.
        try? await Task.sleep(nanoseconds: 900_000_000)
        checking = false
    }
}
