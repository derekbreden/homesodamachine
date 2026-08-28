import SwiftUI
import PhotosUI

// ────────────────────────────────────────────────────────────
// Choosing the face a flavor wears.
//
// ONE SURFACE. Browsing, choosing, adding and removing all happen here, in one
// grid, because they are one thought — "I want this flavor to look like that."
// A separate screen for managing pictures asks someone to hold an inventory in
// their head before they can answer a question about a drink.
//
// THE "+" IS A CELL, NOT A BUTTON. It is the last thing in the same grid, the
// same size and shape as everything it makes, so the row reads as "these are
// the faces, and there is room for another." There is exactly one of them, and
// it is gone once the machine is full — a cap is expressed by an affordance
// that is not there, never by an error after the fact.
//
// NOBODY PICKS A SLOT. The machine keeps four of its own alongside the four it
// shipped with; which one a new picture lands in is arithmetic, and arithmetic
// is not a question to ask someone holding a photograph.
// ────────────────────────────────────────────────────────────

struct FlavorImagePicker: View {
    let channel: Int
    @Environment(BLEManager.self) var ble
    @Environment(\.dismiss) private var dismiss

    @State private var cropping: UIImage?
    @State private var confirmRemove: Int?     // art index

    private let tileAspect: CGFloat = 172.0 / 320.0
    private let columns = [GridItem(.adaptive(minimum: 130), spacing: 16)]

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                ScrollView {
                    LazyVGrid(columns: columns, spacing: 16) {
                        ForEach(0..<ble.flavorArt.factory, id: \.self) { art in
                            tile(art: art, image: factoryImage(art), custom: false)
                        }
                        ForEach(heldCustomArt, id: \.self) { art in
                            tile(art: art, image: customImage(art), custom: true)
                        }
                        if case .sending(let sent, let total) = ble.imageUploadState {
                            pendingTile(progress: Double(sent) / Double(max(total, 1)))
                        } else if ble.imageUploadState == .preparing {
                            pendingTile(progress: 0)
                        }
                        if hasRoom { addCell }
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 20)

                    if case .failed(let why) = ble.imageUploadState {
                        Text(why)
                            .font(.system(size: 13))
                            .foregroundStyle(Color.red.opacity(0.85))
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 32)
                            .padding(.bottom, 20)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("Flavor \(channel + 1) Image")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundStyle(Theme.textSecondary)
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                        .foregroundStyle(Theme.textSecondary)
                }
            }
            .toolbarColorScheme(.dark, for: .navigationBar)
            .toolbarBackground(Theme.background, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
        }
        .onAppear {
            ble.queryImageSlots()
            ble.queryFlavorArt()
        }
        .fullScreenCover(isPresented: Binding(get: { cropping != nil },
                                              set: { if !$0 { cropping = nil } })) {
            if let image = cropping {
                ImageCropView(image: image,
                              onUse: { crop in cropping = nil; add(crop) },
                              onCancel: { cropping = nil })
            }
        }
        .alert("Remove this picture?", isPresented: Binding(
            get: { confirmRemove != nil },
            set: { if !$0 { confirmRemove = nil } })) {
            Button("Remove", role: .destructive) {
                if let art = confirmRemove, let slot = ble.flavorArt.customSlot(art: art) {
                    ble.removeImage(slot: slot)
                }
                confirmRemove = nil
            }
            Button("Cancel", role: .cancel) { confirmRemove = nil }
        } message: {
            Text("A flavor wearing it goes back to its original face.")
        }
    }

    // ── The cells ─────────────────────────────────────────────────────────

    private func tile(art: Int, image: UIImage?, custom: Bool) -> some View {
        Group {
            if let image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
                    .aspectRatio(tileAspect, contentMode: .fit)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
            } else {
                ZStack {
                    RoundedRectangle(cornerRadius: 14)
                        .fill(Theme.placeholder)
                        .aspectRatio(tileAspect, contentMode: .fit)
                    Image(systemName: "photo")
                        .font(.system(size: 24))
                        .foregroundStyle(Theme.textSecondary)
                }
            }
        }
        .padding(5)
        .overlay(
            RoundedRectangle(cornerRadius: 19)
                .stroke(art == ble.flavorArt.art[channel] ? Theme.textPrimary : .clear, lineWidth: 1)
        )
        .contentShape(Rectangle())
        .onTapGesture { ble.setFlavorArt(channel: channel, art: art) }
        .contextMenu {
            // Only a picture someone added can be taken away, and only while
            // nothing else is in flight.
            if custom && !isBusy {
                Button("Remove", role: .destructive) { confirmRemove = art }
            }
        }
    }

    /// The photograph in the place it will occupy, dimmed under a ring — so the
    /// tile becomes the picture rather than being replaced by it.
    private func pendingTile(progress: Double) -> some View {
        ZStack {
            RoundedRectangle(cornerRadius: 14)
                .fill(Theme.placeholder)
                .aspectRatio(tileAspect, contentMode: .fit)
            Circle()
                .trim(from: 0, to: progress)
                .stroke(Color.white, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                .frame(width: 56, height: 56)
                .rotationEffect(.degrees(-90))
        }
        .padding(5)
    }

    private var addCell: some View {
        PhotosPicker(selection: picked, matching: .images, photoLibrary: .shared()) {
            ZStack {
                RoundedRectangle(cornerRadius: 14)
                    .fill(Theme.placeholder)
                    .aspectRatio(tileAspect, contentMode: .fit)
                Image(systemName: "plus")
                    .font(.system(size: 28))
                    .foregroundStyle(Theme.textSecondary)
            }
            .padding(5)
        }
        .disabled(isBusy)
    }

    // ── State ─────────────────────────────────────────────────────────────

    private var heldCustomArt: [Int] {
        (0..<ble.imageSlots.count)
            .filter { ble.imageSlots.isHeld($0) }
            .map { ble.flavorArt.artIndex(customSlot: $0) }
    }

    private var hasRoom: Bool { ble.imageSlots.firstFree != nil && !isBusy }

    private var isBusy: Bool {
        if case .sending = ble.imageUploadState { return true }
        return ble.imageUploadState == .preparing
    }

    private func factoryImage(_ art: Int) -> UIImage? {
        UIImage(named: "flavor_\(art + 1)")
    }

    private func customImage(_ art: Int) -> UIImage? {
        guard let slot = ble.flavorArt.customSlot(art: art) else { return nil }
        return SlotPreviews.load(unit: ble.connectedMachine?.unit ?? "", slot: slot)
    }

    /// The picker is the control, and it holds nothing in view state that a
    /// dismissal could clear before the selection is read.
    private var picked: Binding<PhotosPickerItem?> {
        Binding(get: { nil },
                set: { item in
                    guard let item else { return }
                    Task {
                        guard let data = try? await item.loadTransferable(type: Data.self),
                              let image = UIImage(data: data) else { return }
                        await MainActor.run { cropping = image }
                    }
                })
    }

    /// A new picture takes whichever slot is free, and wears itself at once —
    /// choosing it was the point of adding it.
    private func add(_ crop: ImageCrop) {
        guard let slot = ble.imageSlots.firstFree else { return }
        if let preview = ImageBundle.preview(from: crop) {
            SlotPreviews.save(preview, unit: ble.connectedMachine?.unit ?? "", slot: slot)
        }
        ble.uploadImage(crop, to: slot)
        ble.setFlavorArt(channel: channel, art: ble.flavorArt.artIndex(customSlot: slot))
    }
}

// What this phone happens to have sent, so a filled slot shows as itself.
// Not authority over anything: the machine says what it holds.
enum SlotPreviews {
    private static func url(_ unit: String, _ slot: Int) -> URL? {
        guard !unit.isEmpty else { return nil }
        let dir = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("images/\(unit)")
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir.appendingPathComponent("slot_\(slot).png")
    }

    static func save(_ image: UIImage, unit: String, slot: Int) {
        guard let u = url(unit, slot), let png = image.pngData() else { return }
        try? png.write(to: u)
    }

    static func load(unit: String, slot: Int) -> UIImage? {
        guard let u = url(unit, slot), let d = try? Data(contentsOf: u) else { return nil }
        return UIImage(data: d)
    }
}
