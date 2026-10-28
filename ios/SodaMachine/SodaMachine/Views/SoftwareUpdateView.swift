import SwiftUI

// ────────────────────────────────────────────────────────────
// Whether this machine runs what is published, and the one button that makes
// it so.
//
// One page for the whole machine: check, offer, send, restart, verify, and
// say how it went. Every part the catalog publishes for the machine is a part
// to verify (UpdateAssessment), so a part that has not answered is never
// called current because no part that answered is behind. Sending every byte
// is not an install: a run is done when each board it sent to answers again,
// on the new software or not. Done returns to the page this was opened from.
// ────────────────────────────────────────────────────────────

struct SoftwareUpdateView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    let entry: RouteEntry
    @State private var catalog = FirmwareCatalog()
    @State private var checking = false

    private var model: MachineModel { ble.current?.model ?? .unknown }
    private var published: [FirmwareImage] { catalog.manifest?.images(for: model) ?? [] }
    private var assessment: UpdateAssessment {
        UpdateAssessment(published: published, versions: ble.machineVersions, model: model)
    }
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
    }

    /// Bytes on their way, or the machine restarting into them.
    private var running: Bool {
        if let p = ble.otaProgress, !p.finished, p.failure == nil { return true }
        return !ble.otaQueue.isEmpty || settling
    }

    private var icon: String {
        if ble.demoMode { return "checkmark.circle" }
        if catalog.manifest != nil, !running, !checking, assessment.verdict == .upToDate { return "checkmark.circle" }
        return "arrow.down.circle"
    }

    @ViewBuilder private var content: some View {
        if ble.demoMode {
            title("The demo is up to date")
            Note("Software Update installs on a real machine.")
            ActionButton(title: "Done") { done() }
        } else if let push = ble.otaProgress {
            pushing(push)
        } else if catalog.loading || checking {
            title("Checking for updates")
            ProgressView().tint(Theme.accent)
        } else if catalog.error != nil || catalog.manifest == nil {
            title("Couldn’t check for updates")
            Note("Connect this device to the internet and try again.")
            ActionButton(title: "Check again") { Task { await check() } }
        } else {
            verdict
        }
    }

    @ViewBuilder private var verdict: some View {
        let a = assessment
        switch a.verdict {
        case .upToDate:
            title("Your machine is up to date")
            Note(["Every part of the machine reports the published software.", installed].filter { !$0.isEmpty }.joined(separator: " "))
            ActionButton(title: "Done") { done() }
            if ble.linked { ActionButton(title: "Check again", primary: false) { Task { await check() } } }
        case .updateAvailable:
            title("An update is ready")
            Note("This usually takes a few minutes. Keep your device near the machine and leave the machine plugged in.")
            if !a.unknown.isEmpty { Note(unheard(a.unknown)) }
            ActionButton(title: "Update now") { install(a.behind) }
                .disabled(!ble.linked)
            if !ble.linked { Note("Bring your device near the machine to install it.") }
        case .unverified:
            title(ble.linked || ble.current?.versionsReadAt != nil ? "Couldn’t check every part" : "Waiting for your machine")
            Note(ble.linked ? unheard(a.unknown) : "Bring your device near the machine to check it.")
            if ble.linked { ActionButton(title: "Check again") { Task { await check() } } }
        case .nothingPublished:
            title("No updates for this machine")
            Note("Nothing is published for this machine’s software.")
            ActionButton(title: "Done") { done() }
        }
    }

    @ViewBuilder private func pushing(_ push: OTAProgress) -> some View {
        if let why = push.failure {
            title("The update didn’t finish")
            Note(why)
            ActionButton(title: "Try again") { retry() }
                .disabled(!ble.linked)
            ActionButton(title: "Done", primary: false) { done() }
        } else if push.finished && ble.otaQueue.isEmpty && !settling {
            let a = assessment
            switch a.verdict {
            case .upToDate:
                title("Your machine is up to date")
                Note(installed)
                ActionButton(title: "Done") { done() }
            case .nothingPublished:
                title("Couldn’t verify the update")
                Note("The published software for this machine couldn’t be read, so this device can’t tell what the machine runs now.")
                ActionButton(title: "Check again") { Task { await check() } }
                    .disabled(!ble.linked)
                ActionButton(title: "Done", primary: false) { done() }
            case .updateAvailable:
                title("The update didn’t finish")
                Note("Part of your machine is still running the software it was. You can try again.")
                ActionButton(title: "Try again") { retry() }
                    .disabled(!ble.linked)
                ActionButton(title: "Done", primary: false) { done() }
            case .unverified:
                title("Couldn’t verify the update")
                Note(unheard(a.unknown))
                ActionButton(title: "Check again") { Task { await check() } }
                    .disabled(!ble.linked)
                ActionButton(title: "Done", primary: false) { done() }
            }
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

    /// The parts that haven't said what they run.
    private func unheard(_ parts: [FirmwareImage]) -> String {
        let names = parts.map(\.what).joined(separator: ", ")
        return "\(names.isEmpty ? "Part of the machine" : names) didn’t report what \(parts.count == 1 ? "it runs" : "they run"), so this device can’t tell whether \(parts.count == 1 ? "it needs" : "they need") an update."
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

    /// For the machine this was asked on, over the link it was asked on.
    private func install(_ images: [FirmwareImage]) {
        guard let machine = ble.current?.id, ble.linked else { return }
        let model = self.model
        Task {
            guard await ble.ensureTrusted(.update) else { return }
            guard ble.current?.id == machine, ble.linked, ble.current?.model == model else { return }
            ble.startUpdateAll(images, on: model) { try await catalog.payload(for: $0) }
        }
    }

    /// The same run again, for whatever is still behind.
    private func retry() {
        ble.otaProgress = nil
        let behind = assessment.behind
        guard !behind.isEmpty else { Task { await check() }; return }
        install(behind)
    }

    /// The result is read: back to the page this was opened from.
    private func done() {
        ble.otaProgress = nil
        nav.finish(entry)
    }

    private func check() async {
        guard !ble.demoMode else { return }
        checking = true
        if ble.otaProgress?.finished == true || ble.otaProgress?.failure != nil { ble.otaProgress = nil }
        if ble.linked { ble.send("IDENTITY") }   // the faucet answers with what every board runs
        await catalog.refresh()
        try? await Task.sleep(for: .milliseconds(900))
        checking = false
    }
}
