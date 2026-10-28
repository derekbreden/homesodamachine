import SwiftUI
import PhotosUI

// ────────────────────────────────────────────────────────────
// The face a flavor wears: the four this app ships with, the machine's own
// pictures, and a "+" that adds one more while the machine has room.
//
// Choosing is a task that ends back on the flavor once the machine says the
// flavor wears the choice. A new photo goes up first, in the place it will
// occupy, and is put on the flavor only once the machine holds it. The newest
// choice for a flavor is the only one that can still be put on it: an older
// picture may finish arriving, but it never takes the newer one's place, and
// a canceled one is never put on at all.
// ────────────────────────────────────────────────────────────

/// What a flavor is to wear: a face the machine has, or one on its way.
struct ImageChoice: Hashable {
    let art: Int
    let upload: UUID?
    let base: SettingSnapshot
}

struct ImageLibraryView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(EditSessions.self) var edits
    let channel: Int
    let width: CGFloat
    let entry: RouteEntry

    @State private var cropping: UIImage?
    @State private var removing: Int?   // art index
    @State private var conflict: SettingSnapshot?

    private var key: EditKey? { ble.current.map { EditKey(machine: $0.id, field: .image(channel: channel)) } }
    private var choice: ImageChoice? { key.flatMap { edits.draft($0) } }
    private var write: EditSessions.Write? { key.flatMap(edits.write) }
    private var worn: Int? { ble.flavorArt.art.indices.contains(channel) ? ble.flavorArt.art[channel] : nil }

    private var currentConflict: SettingSnapshot? {
        if let conflict { return ble.settingSnapshot(.art(channel: channel)) ?? conflict }
        guard write?.running != true, let choice, let current = ble.settingSnapshot(.art(channel: channel)),
              current.revision != choice.base.revision else { return nil }
        return current
    }

    var body: some View {
        let room = min(560, width)
        let columns = max(1, Int((room + 12) / 84))
        let tileWidth = min(112, (room - CGFloat(columns - 1) * 12) / CGFloat(columns))
        let tileHeight = tileWidth * 80 / 43
        VStack(alignment: .leading, spacing: 20) {
            if let why = ble.imageSizeMismatch {
                Notice(title: "Pictures can’t be sent", message: "\(why.prefix(1).uppercased())\(why.dropFirst()).",
                       icon: "exclamationmark.circle")
            }
            if let problem = write?.problem, currentConflict == nil {
                Notice(title: "Flavor \(channel + 1) didn’t change", message: problem, icon: "exclamationmark.circle")
                if let id = choice?.upload, ble.canRetryUpload(id), ble.linked {
                    ActionButton(title: "Try again") { retry(id) }.frame(maxWidth: 360)
                }
            } else if write?.running == true, let choice {
                Note(choice.upload == nil || !uploading(choice.upload)
                     ? "Putting it on Flavor \(channel + 1)…"
                     : "Sending your picture. It goes on Flavor \(channel + 1) once the machine has it.")
            }
            if let conflict = currentConflict, let chosen = choice?.art {
                Notice(title: "Machine’s image changed", message: "The machine now uses Image \((ble.settingSnapshot(.art(channel: channel))?.byte ?? conflict.byte ?? 0) + 1). Your choice is Image \(chosen + 1).", icon: "exclamationmark.triangle.fill")
                HStack(spacing: 24) {
                    Button("Use mine") { choose(chosen, basedOn: ble.settingSnapshot(.art(channel: channel))) }
                    Button("Keep machine’s image") {
                        if let key { release(); edits.discard(key) }
                        self.conflict = nil
                        nav.finish(entry)
                    }
                }.frame(minHeight: 44)
            }
            SectionTitle("Choose an image")
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 12), count: columns),
                      alignment: .leading, spacing: 16) {
                ForEach(0..<ble.flavorArt.factory, id: \.self) { art in
                    tile(art: art, label: "Image \(art + 1)", height: tileHeight, custom: false)
                }
                ForEach(heldCustomArt, id: \.self) { art in
                    tile(art: art, label: "Your picture", height: tileHeight, custom: true)
                }
                if let active = ble.activeUpload {
                    pendingTile(active.preview, progress: sendingProgress, height: tileHeight) { ble.cancelImageUpload() }
                }
                ForEach(ble.imageQueue) { item in
                    pendingTile(item.preview, progress: nil, height: tileHeight) { ble.cancelQueuedImage(id: item.id) }
                }
                if ble.nextFreeSlot() != nil && ble.linked && !ble.demoMode {
                    addTile(width: tileWidth, height: tileHeight)
                }
            }
            Note(footnote)
        }
        .frame(maxWidth: room).frame(maxWidth: .infinity, alignment: .leading)
        .onAppear {
            guard ble.linked, !ble.demoMode else { return }
            ble.queryImageSlots()
            ble.queryFlavorArt()
        }
        .fullScreenCover(isPresented: Binding(get: { cropping != nil }, set: { if !$0 { cropping = nil } })) {
            if let image = cropping {
                ImageCropView(image: image,
                              onUse: { crop in cropping = nil; add(crop) },
                              onCancel: { cropping = nil })
            }
        }
        .confirmationDialog("Remove this picture?",
                            isPresented: Binding(get: { removing != nil }, set: { if !$0 { removing = nil } }),
                            titleVisibility: .visible) {
            Button("Remove", role: .destructive) {
                if let art = removing, let slot = ble.flavorArt.customSlot(art: art), let machine = ble.current?.id {
                    Task {
                        guard await ble.ensureTrusted(.image), ble.current?.id == machine else { return }
                        ble.removeImage(slot: slot)
                    }
                }
                removing = nil
            }
            Button("Cancel", role: .cancel) { removing = nil }
        } message: {
            Text("A flavor wearing it goes back to its original image.")
        }
    }

    private var footnote: String {
        if ble.activeUpload != nil { return "Sending picture to the machine. You can add another while it sends." }
        if !ble.linked && !ble.demoMode {
            return ble.current?.picturesReadAt.map { "As of \(said($0)). Bring your device near the machine to change images." }
                ?? "Bring your device near the machine to change images."
        }
        if ble.demoMode { return "Four included images. A real machine also holds four of your own." }
        if ble.nextFreeSlot() == nil && ble.imageSlots.count > 0 { return "Four included images and four of your own. Remove one of yours to add another." }
        return "Four included images. Add up to four of your own."
    }

    private func uploading(_ id: UUID?) -> Bool {
        guard let id else { return false }
        return ble.activeUpload?.id == id || ble.imageQueue.contains { $0.id == id }
    }

    private func tile(art: Int, label: String, height: CGFloat, custom: Bool) -> some View {
        let chosen = worn == art
        let pending = write?.running == true && choice?.art == art && choice?.upload == nil
        return Button { choose(art) } label: {
            VStack(spacing: 8) {
                FlavorArtView(art: art, height: height)
                    .overlay {
                        if pending || custom && ble.picture(art: art) == nil && ble.linked {
                            ProgressView().tint(Theme.textSecondary)
                        }
                    }
                    .overlay(alignment: .bottomTrailing) {
                        if chosen {
                            Image(systemName: "checkmark.circle.fill").symbolRenderingMode(.palette)
                                .foregroundStyle(Theme.onAccent, Theme.accent).padding(5)
                        }
                    }
                Text(label).font(.caption).lineLimit(1)
            }
        }
        .buttonStyle(.plain)
        .disabled(!(ble.linked || ble.demoMode) || ble.settingSnapshot(.art(channel: channel)) == nil)
        .accessibilityAddTraits(chosen ? .isSelected : [])
        .contextMenu {
            if custom && ble.activeUpload == nil && ble.linked {
                Button("Remove", role: .destructive) { removing = art }
            }
        }
    }

    private func pendingTile(_ image: UIImage?, progress: Double?, height: CGFloat, cancel: @escaping () -> Void) -> some View {
        VStack(spacing: 8) {
            ZStack {
                Group {
                    if let image { Image(uiImage: image).resizable().scaledToFill() } else { Theme.placeholder }
                }
                .frame(width: height * 43 / 80, height: height).clipped()
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .opacity(0.35)
                VStack(spacing: 10) {
                    if let progress {
                        ProgressView(value: progress).tint(Theme.accent)
                        Text("\(Int(progress * 100))%").font(.caption.monospacedDigit())
                    } else {
                        ProgressView().tint(Theme.accent)
                    }
                }
                .padding(10)
            }
            .frame(width: height * 43 / 80, height: height)
            Button("Cancel", action: cancel).font(.caption).frame(minHeight: 44)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Picture being sent")
    }

    private func addTile(width: CGFloat, height: CGFloat) -> some View {
        PhotosPicker(selection: picked, matching: .images, photoLibrary: .shared()) {
            VStack(spacing: 8) {
                Image(systemName: "plus").font(.title2).frame(width: height * 43 / 80, height: height)
                    .background(Theme.surface, in: RoundedRectangle(cornerRadius: 8))
                Text("Add photo").font(.caption)
            }
        }
        .accessibilityLabel("Add photo")
    }

    /// Custom slots the machine holds, minus any this phone is still sending into.
    private var heldCustomArt: [Int] {
        let inFlight = Set(ble.imageQueue.map(\.slot) + (ble.activeUpload.map { [$0.slot] } ?? []))
        return (0..<ble.imageSlots.count)
            .filter { ble.imageSlots.isHeld($0) && !inFlight.contains($0) }
            .map { ble.flavorArt.artIndex(customSlot: $0) }
    }

    private var sendingProgress: Double? {
        if case .sending(let sent, let total) = ble.imageUploadState { return Double(sent) / Double(max(total, 1)) }
        return nil
    }

    private var picked: Binding<PhotosPickerItem?> {
        Binding(get: { nil },
                set: { item in
                    guard let item else { return }
                    Task {
                        guard let data = try? await item.loadTransferable(type: Data.self),
                              let image = UIImage(data: data) else { return }
                        cropping = image
                    }
                })
    }

    // ── The task ──────────────────────────────────────────────────────────

    /// A face the machine has. The one the flavor already wears, with no
    /// other face on its way to the machine, ends the task, and with it any
    /// earlier choice still being sent.
    private func choose(_ art: Int, basedOn supplied: SettingSnapshot? = nil) {
        guard let key, let machine = ble.current?.id,
              let base = supplied ?? choice?.base ?? ble.settingSnapshot(.art(channel: channel)) else { return }
        conflict = nil
        if worn == art && !ble.assigningArt(channel) {
            release()
            edits.discard(key)
            nav.finish(entry)
            return
        }
        release()
        edits.setDraft(ImageChoice(art: art, upload: nil, base: base), for: key)
        let token = edits.begin(key)
        Task {
            guard await ble.ensureTrusted(.image, channel: channel) else {
                edits.end(token, for: key, problem: "Nothing changed. Tap Trust on the machine to change images from this device.")
                return
            }
            guard edits.isNewest(token, for: key) else { return }
            guard ble.current?.id == machine else {
                edits.end(token, for: key, problem: "Nothing changed: another machine is in use.")
                return
            }
            await assign(art, base: base, token: token, key: key, machine: machine)
        }
    }

    /// A new photo: sent, then put on the flavor once the machine holds it.
    private func add(_ crop: UIImage) {
        guard let key, let machine = ble.current?.id, let base = ble.settingSnapshot(.art(channel: channel)) else { return }
        conflict = nil
        release()
        let token = edits.begin(key)
        Task {
            guard await ble.ensureTrusted(.image, channel: channel) else {
                edits.end(token, for: key, problem: "Nothing changed. Tap Trust on the machine to change images from this device.")
                return
            }
            guard edits.isNewest(token, for: key) else { return }
            guard ble.current?.id == machine else {
                edits.end(token, for: key, problem: "Nothing changed: another machine is in use.")
                return
            }
            guard let item = ble.enqueueImage(crop, preview: ImageBundle.preview(from: crop)) else {
                edits.end(token, for: key, problem: ble.imageSizeMismatch.map { "\($0)." } ?? "The machine has no room for another picture.")
                return
            }
            await follow(item, base: base, token: token, key: key, machine: machine)
        }
    }

    /// The same photograph, for the same flavor, as a new trip, under the
    /// same checks as the first: Trust, this machine, and still the newest
    /// choice.
    private func retry(_ id: UUID) {
        guard let key, let machine = ble.current?.id, let base = choice?.base else { return }
        let token = edits.begin(key)
        Task {
            guard await ble.ensureTrusted(.image, channel: channel) else {
                edits.end(token, for: key, problem: "Nothing changed. Tap Trust on the machine to change images from this device.")
                return
            }
            guard edits.isNewest(token, for: key) else { return }
            guard ble.current?.id == machine, let item = ble.retryUpload(id) else {
                edits.end(token, for: key, problem: "The picture couldn’t be sent again here. Bring your device near the machine and try again.")
                return
            }
            await follow(item, base: base, token: token, key: key, machine: machine)
        }
    }

    /// The choice being replaced keeps no picture for a retry.
    private func release() {
        if let id = choice?.upload { ble.dropFailedUpload(id) }
    }

    /// A picture on its way, followed to the end of its trip. Only the newest
    /// choice for the flavor is put on it.
    private func follow(_ item: QueuedImage, base: SettingSnapshot, token: UUID, key: EditKey, machine: String) async {
        let art = ble.flavorArt.artIndex(customSlot: item.slot)
        if edits.isNewest(token, for: key) { edits.setDraft(ImageChoice(art: art, upload: item.id, base: base), for: key) }
        switch await ble.awaitUpload(item.id) {
        case .stored:
            guard edits.isNewest(token, for: key) else { return }
            await assign(art, base: base, token: token, key: key, machine: machine)
        case .failed(let why):
            edits.end(token, for: key, problem: "The picture wasn’t sent: \(why).")
        case .interrupted:
            edits.end(token, for: key, problem: "The connection dropped before the picture arrived.")
        case .canceled:
            guard edits.isNewest(token, for: key) else { return }
            edits.discard(key)
        }
    }

    /// The machine wears it, or says why not. Done, the task closes its own
    /// page — only this opening of it, and only while it is on top.
    private func assign(_ art: Int, base: SettingSnapshot, token: UUID, key: EditKey, machine: String) async {
        let answer = await ble.assignArt(channel: channel, art: art, expected: base, on: machine,
                                        while: { edits.isNewest(token, for: key) })
        guard edits.isNewest(token, for: key) else { return }
        switch answer {
        case .accepted:
            edits.discard(key)
            nav.finish(entry)
        case .conflict(let current):
            conflict = current
            edits.end(token, for: key, problem: "Another device changed this flavor’s image. Choose which image to keep.")
        case .failure(let failure):
            edits.end(token, for: key, problem: failure.message)
        }
    }
}
