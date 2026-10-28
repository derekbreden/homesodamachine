import SwiftUI

// ────────────────────────────────────────────────────────────
// Whether this machine is current, and the one button that makes it so.
//
// One page for the whole machine. Each board reports the version string
// `pre_build.py` wrote into its tree, and the manifest carries the same
// strings, so being current is every board matching. A board that has said
// nothing is not counted as behind, and a run is done when the boards answer
// again on the new software, not when its bytes are sent.
// ────────────────────────────────────────────────────────────

struct SoftwareUpdateView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @State private var catalog = FirmwareCatalog()
    @State private var checking = false

    private var model: MachineModel { ble.current?.model ?? .unknown }
    private var published: [FirmwareImage] { catalog.manifest?.images(for: model) ?? [] }
    private var behind: [FirmwareImage] { published.filter { ble.machineVersions.needs($0, on: model) } }
    private var heardFrom: Bool { ble.machineVersions.answered > 0 }
    private var settling: Bool { ble.otaSettlingSince != nil }

    var body: some View {
        VStack(alignment: .center, spacing: 24) {
            Image(systemName: icon)
                .font(.system(size: 56, weight: .light)).foregroundStyle(Theme.accent).padding(.top, 24)
                .accessibilityHidden(true)
            content
        }
        .multilineTextAlignment(.center)
        .frame(maxWidth: 460).frame(maxWidth: .infinity).padding(.vertical, 20)
        .task { await check() }
        .onChange(of: running, initial: true) { _, now in nav.locked = now }
        .onDisappear { nav.locked = false }
    }

    /// Bytes on their way, or the machine restarting into them.
    private var running: Bool {
        if let p = ble.otaProgress, !p.finished, p.failure == nil { return true }
        return !ble.otaQueue.isEmpty || settling
    }

    private var icon: String {
        if ble.demoMode { return "checkmark.circle" }
        if let p = ble.otaProgress, p.finished, ble.otaQueue.isEmpty, !settling, heardFrom, behind.isEmpty { return "checkmark.circle" }
        if ble.otaProgress == nil, heardFrom, catalog.manifest != nil, behind.isEmpty { return "checkmark.circle" }
        return "arrow.down.circle"
    }

    @ViewBuilder private var content: some View {
        if ble.demoMode {
            title("The demo is up to date")
            Note("Software Update installs on a real machine.")
        } else if let push = ble.otaProgress {
            pushing(push)
        } else if catalog.loading || checking {
            title("Checking for updates")
            ProgressView().tint(Theme.accent)
        } else if catalog.error != nil {
            title("Check for an update")
            Notice(title: "Couldn’t check for updates", message: "Connect this device to the internet and try again.",
                   icon: "exclamationmark.circle")
            ActionButton(title: "Try again") { Task { await check() } }
        } else if !heardFrom {
            title(ble.linked ? "Checking your machine" : "Waiting for your machine")
            if !ble.linked { Note("Bring your device near the machine.") }
        } else if behind.isEmpty {
            title("Your machine is up to date")
            Note(["All parts of the machine report the published software.", installed].filter { !$0.isEmpty }.joined(separator: " "))
            if ble.linked { ActionButton(title: "Check again", primary: false) { Task { await check() } } }
        } else {
            title("An update is ready")
            Note("This usually takes a few minutes. Keep your device near the machine and leave the machine plugged in.")
            ActionButton(title: "Update now") {
                Task {
                    guard await ble.ensureTrusted(.update) else { return }
                    ble.startUpdateAll(behind, on: model) { try await catalog.payload(for: $0) }
                }
            }
            .disabled(!ble.linked)
            if !ble.linked { Note("Bring your device near the machine to install it.") }
        }
    }

    @ViewBuilder private func pushing(_ push: OTAProgress) -> some View {
        if push.finished && ble.otaQueue.isEmpty && !settling {
            if !heardFrom {
                title("Your machine hasn’t come back yet")
                Note("It may still be restarting. Check again in a moment.")
            } else if behind.isEmpty {
                title("Your machine is up to date")
                Note(installed)
            } else {
                title("The update didn’t finish")
                Note("Your machine is still running the software it was. You can try again.")
            }
            ActionButton(title: "Done") { ble.otaProgress = nil }
        } else if let why = push.failure {
            title("The update didn’t finish")
            Note(why)
            ActionButton(title: "Done") { ble.otaProgress = nil }
        } else if settling {
            title(ble.linked ? "Checking your machine" : "Restarting your machine")
            ProgressView().tint(Theme.accent)
            Note(ble.linked ? "Checking the software the machine is running. Waiting for every part to answer."
                            : "Restarting the machine. Keep it plugged in.")
        } else {
            title("Updating your machine")
            ProgressView(value: overall).tint(Theme.accent)
            Text("\(Int(overall * 100))%").font(.title3.monospacedDigit())
            Note("Sending software")
            Note("Keep your device near the machine. Do not unplug it.")
            ActionButton(title: "Cancel update", primary: false) { ble.cancelUpdate() }
        }
    }

    private func title(_ text: String) -> some View {
        Text(text).font(.title2.weight(.semibold)).fixedSize(horizontal: false, vertical: true)
    }

    /// One bar for the whole run, across every board's image.
    private var overall: Double {
        let total = ble.otaQueueDone + ble.otaQueue.count
        guard total > 0, let push = ble.otaProgress else { return 0 }
        let inFlight = ble.otaQueue.isEmpty ? 0 : push.fraction
        return min(1, (Double(ble.otaQueueDone) + inFlight) / Double(total))
    }

    /// The date the running software was built, and how old that reading is.
    /// The main board's build speaks for the machine; a display's stands in
    /// only when the main board has not said.
    private var installed: String {
        let v = [OTATarget.mainBoard, .radioBoard, .farDisplay].lazy
            .compactMap { ble.machineVersions.byBoard[$0.rawValue] }
            .first { !$0.isEmpty } ?? ""
        let date = v.split(separator: " ").first.map(String.init) ?? ""
        var line = date.isEmpty ? "" : "Installed \(date)."
        if !ble.linked, let t = ble.current?.versionsReadAt {
            line += (line.isEmpty ? "" : " ") + "As of \(said(t))."
        }
        return line
    }

    private func check() async {
        guard !ble.demoMode else { return }
        checking = true
        if ble.linked { ble.send("IDENTITY") }   // the faucet answers with what every board runs
        await catalog.refresh()
        try? await Task.sleep(for: .milliseconds(900))
        checking = false
    }
}
