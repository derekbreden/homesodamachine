import SwiftUI
import Combine
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
    // Four to a row on a phone. The face the machine holds is 172 pixels
    // wide, and a tile this size shows it near that rather than blown up —
    // and the eight faces a channel can wear fit on one screen.
    private let columns = [GridItem(.adaptive(minimum: 72, maximum: 100), spacing: 12)]

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                ScrollView {
                    LazyVGrid(columns: columns, spacing: 12) {
                        ForEach(0..<ble.flavorArt.factory, id: \.self) { art in
                            tile(art: art, image: factoryImage(art), custom: false)
                        }
                        ForEach(heldCustomArt, id: \.self) { art in
                            tile(art: art, image: customImage(art), custom: true)
                        }
                        if let active = ble.activeUpload {
                            pendingTile(active.preview, progress: sendingProgress,
                                        cancel: { ble.cancelImageUpload() })
                        }
                        ForEach(ble.imageQueue) { item in
                            pendingTile(item.preview, progress: nil,
                                        cancel: { ble.cancelQueuedImage(id: item.id) })
                        }
                        if hasRoom && ble.linked { addCell }
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 20)

                    // A disagreement about what a picture is stands the moment
                    // the machine has said, so it is said here rather than
                    // waiting to be discovered by a photograph someone framed.
                    if let why = ble.imageSizeMismatch {
                        note(why)
                    } else if case .failed(let why) = ble.imageUploadState {
                        note(why)
                    } else if !ble.linked {
                        // What the machine last showed, and nothing to change
                        // it with until it can hear.
                        Text(ble.current?.picturesReadAt.map { "As of \(said($0))" } ?? "Nothing read yet")
                            .font(.system(size: 13))
                            .foregroundStyle(Theme.textSecondary)
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

    /// Every cell is the same shape, whatever is in it. An image asked to size
    /// itself lays out to its own aspect and the row stops being a row — which
    /// is why the cell is an empty box of the right shape and the picture is
    /// laid over it, never the other way round.
    private func cell<Content: View>(@ViewBuilder _ content: () -> Content) -> some View {
        Color.clear
            .aspectRatio(tileAspect, contentMode: .fit)
            .overlay(content())
            .clipShape(RoundedRectangle(cornerRadius: 14))
            .padding(5)
    }

    private func tile(art: Int, image: UIImage?, custom: Bool) -> some View {
        cell {
            if let image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
            } else {
                // A face the machine holds and this phone has not read back
                // yet is on its way while the machine can hear. One it cannot
                // be asked for is not here.
                ZStack {
                    Theme.placeholder
                    if custom && ble.linked {
                        ProgressView().tint(Theme.textSecondary)
                    } else {
                        Image(systemName: "photo")
                            .font(.system(size: 20))
                            .foregroundStyle(Theme.textSecondary)
                    }
                }
            }
        }
        .overlay(
            RoundedRectangle(cornerRadius: 19)
                .stroke(art == ble.flavorArt.art[channel] ? Theme.textPrimary : .clear, lineWidth: 1)
        )
        .contentShape(Rectangle())
        .onTapGesture { if ble.linked { ble.setFlavorArt(channel: channel, art: art) } }
        .contextMenu {
            // Only a picture someone added can be taken away, and only while
            // nothing else is in flight and the machine can hear.
            if custom && !isBusy && ble.linked {
                Button("Remove", role: .destructive) { confirmRemove = art }
            }
        }
    }

    /// The photograph in the place it will occupy, dimmed under a ring — so the
    /// tile becomes the picture rather than being replaced by one.
    private func pendingTile(_ image: UIImage?, progress: Double?, cancel: @escaping () -> Void) -> some View {
        cell {
            ZStack {
                if let image {
                    Image(uiImage: image).resizable().scaledToFill()
                } else {
                    Theme.placeholder
                }
                Color.black.opacity(0.5)
                if let progress {
                    Circle()
                        .trim(from: 0, to: progress)
                        .stroke(Color.white, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                        .frame(width: 56, height: 56)
                        .rotationEffect(.degrees(-90))
                } else {
                    Image(systemName: "clock")
                        .font(.system(size: 24))
                        .foregroundStyle(.white.opacity(0.7))
                }
                // A way out that is visible. A picture in flight is the one tile
                // that can hold the screen, and a long press is not somewhere to
                // put the only escape from it.
                VStack {
                    HStack {
                        Spacer()
                        Button(action: cancel) {
                            Image(systemName: "xmark.circle.fill")
                                .font(.system(size: 22))
                                .symbolRenderingMode(.palette)
                                .foregroundStyle(.white, .black.opacity(0.45))
                        }
                        .buttonStyle(.plain)
                    }
                    Spacer()
                }
                .padding(8)
            }
        }
    }

    /// Available while a picture is still going up, so the next one can be
    /// chosen and queued rather than waited for.
    private var addCell: some View {
        PhotosPicker(selection: picked, matching: .images, photoLibrary: .shared()) {
            cell {
                ZStack {
                    Theme.placeholder
                    Image(systemName: "plus")
                        .font(.system(size: 28))
                        .foregroundStyle(Theme.textSecondary)
                }
            }
        }
    }

    // ── State ─────────────────────────────────────────────────────────────

    /// Slots the machine says it holds, minus any this phone is still sending
    /// into — those are already on screen as the picture going up.
    private var heldCustomArt: [Int] {
        let inFlight = Set(ble.imageQueue.map(\.slot) + (ble.activeUpload.map { [$0.slot] } ?? []))
        return (0..<ble.imageSlots.count)
            .filter { ble.imageSlots.isHeld($0) && !inFlight.contains($0) }
            .map { ble.flavorArt.artIndex(customSlot: $0) }
    }

    /// Room for another, counting the ones already waiting on this phone —
    /// the machine cannot know about those. The "+" stays live during a send;
    /// choosing the next picture is not something to be made to wait for.
    private var hasRoom: Bool { ble.nextFreeSlot() != nil }

    /// How far the one in flight has got, or nil while its renditions are still
    /// being made — which is a wait with nothing to measure yet.
    private var sendingProgress: Double? {
        if case .sending(let sent, let total) = ble.imageUploadState {
            return Double(sent) / Double(max(total, 1))
        }
        return nil
    }

    private var isBusy: Bool { ble.activeUpload != nil }

    private func factoryImage(_ art: Int) -> UIImage? {
        UIImage(named: "flavor_\(art + 1)")
    }

    /// A face this phone holds for the picture that slot is carrying — whether
    /// it sent that picture or read it back off the machine.
    private func customImage(_ art: Int) -> UIImage? {
        guard let slot = ble.flavorArt.customSlot(art: art) else { return nil }
        return ble.faces[ble.imageSlots.crc(of: slot)]
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

    private func note(_ why: String) -> some View {
        Text(why)
            .font(.system(size: 13))
            .foregroundStyle(Color.red.opacity(0.85))
            .multilineTextAlignment(.center)
            .padding(.horizontal, 32)
            .padding(.bottom, 20)
    }

    /// A new picture takes whichever slot is free, and wears itself at once —
    /// choosing it was the point of adding it.
    private func add(_ crop: UIImage) {
        // The tile shown while it goes up. The durable one is filed under the
        // bundle's crc32 once that exists, which is the same face by a name the
        // machine also knows.
        let preview = ImageBundle.preview(from: crop)
        guard let slot = ble.enqueueImage(crop, preview: preview) else { return }
        ble.setFlavorArt(channel: channel, art: ble.flavorArt.artIndex(customSlot: slot))
    }
}

