import SwiftUI

// ────────────────────────────────────────────────────────────
// Whether this machine is current, and the one button that makes it so.
//
// NOTHING HERE NAMES A BOARD. A machine is several of them and an update is
// several images, and neither is a thing a person owns — they own a soda
// machine. So there is one bar for the whole run, one button, and one sentence
// about what to do while it happens.
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
            Text("Software Update")
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
            } else if catalog.error != nil {
                state("Couldn't check for updates",
                      "Make sure your phone is online, then try again.")
                checkButton()
            } else if !heardFrom {
                state("Checking your machine", "")
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
            Text("An update is ready")
                .font(.system(size: 20, weight: .semibold))
                .foregroundStyle(Theme.textPrimary)

            Text("This usually takes a few minutes.")
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
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundStyle(Theme.textPrimary)
                Text("Your machine is restarting.")
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
                Button("Done") { ble.otaProgress = nil }
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.top, 6)
            } else if let why = push.failure {
                Text("The update didn't finish")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundStyle(Theme.textPrimary)
                Text(why)
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
                Button("Done") { ble.otaProgress = nil }
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.top, 6)
            } else {
                Text("Updating your machine")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundStyle(Theme.textPrimary)

                ProgressView(value: overall)
                    .tint(Theme.accent)
                    .scaleEffect(x: 1, y: 1.6, anchor: .center)
                    .padding(.horizontal, 32)

                Text("\(Int(overall * 100))%")
                    .font(.system(size: 14).monospacedDigit())
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

    // MARK: - Pieces

    /// The date the running firmware was built. The rest of the version string
    /// is a commit and a dirty marker, which answer a question nobody standing
    /// at their kitchen counter is asking.
    private var running: String {
        let v = ble.machineVersions.byBoard.values.first { !$0.isEmpty } ?? ""
        let date = v.split(separator: " ").first.map(String.init) ?? ""
        return date.isEmpty ? "" : "Installed \(date)"
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
