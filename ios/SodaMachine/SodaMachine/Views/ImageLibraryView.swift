import SwiftUI
import PhotosUI

// ────────────────────────────────────────────────────────────
// The face a flavor wears: the four this app ships with, the machine's own
// pictures, and a "+" that adds one more while the machine has room.
//
// A new picture takes whichever custom slot is free and wears itself at once.
// One on its way shows in the place it will occupy, with its progress and a
// way to cancel it.
// ────────────────────────────────────────────────────────────

struct ImageLibraryView: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    let channel: Int
    let width: CGFloat

    @State private var cropping: UIImage?
    @State private var removing: Int?   // art index

    var body: some View {
        let room = min(560, width)
        let columns = max(1, Int((room + 12) / 84))
        let tileWidth = min(112, (room - CGFloat(columns - 1) * 12) / CGFloat(columns))
        let tileHeight = tileWidth * 80 / 43
        VStack(alignment: .leading, spacing: 20) {
            if case .failed(let why) = ble.imageUploadState {
                Notice(title: "Picture wasn’t sent", message: "\(why.prefix(1).uppercased())\(why.dropFirst()).",
                       icon: "exclamationmark.circle")
            } else if let why = ble.imageSizeMismatch {
                Notice(title: "Pictures can’t be sent", message: "\(why.prefix(1).uppercased())\(why.dropFirst()).",
                       icon: "exclamationmark.circle")
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
            if ble.failedImage != nil, ble.linked {
                ActionButton(title: "Try again") { retry() }.frame(maxWidth: 360)
            }
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
                if let art = removing, let slot = ble.flavorArt.customSlot(art: art) {
                    Task {
                        guard await ble.ensureTrusted(.image) else { return }
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

    private func tile(art: Int, label: String, height: CGFloat, custom: Bool) -> some View {
        let chosen = ble.flavorArt.art.indices.contains(channel) && ble.flavorArt.art[channel] == art
        return Button {
            Task {
                guard await ble.ensureTrusted(.image, channel: channel) else { return }
                ble.setFlavorArt(channel: channel, art: art)
                nav.back()
            }
        } label: {
            VStack(spacing: 8) {
                FlavorArtView(art: art, height: height)
                    .overlay {
                        if custom && ble.picture(art: art) == nil && ble.linked { ProgressView().tint(Theme.textSecondary) }
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
        .disabled(!(ble.linked || ble.demoMode))
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

    private func add(_ crop: UIImage) {
        Task {
            guard await ble.ensureTrusted(.image, channel: channel) else { return }
            let preview = ImageBundle.preview(from: crop)
            guard let slot = ble.enqueueImage(crop, preview: preview) else { return }
            ble.setFlavorArt(channel: channel, art: ble.flavorArt.artIndex(customSlot: slot))
        }
    }

    private func retry() {
        Task {
            guard await ble.ensureTrusted(.image, channel: channel) else { return }
            guard let slot = ble.retryFailedImage() else { return }
            ble.setFlavorArt(channel: channel, art: ble.flavorArt.artIndex(customSlot: slot))
        }
    }
}
