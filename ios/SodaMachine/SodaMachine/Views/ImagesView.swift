import SwiftUI
import PhotosUI

// ────────────────────────────────────────────────────────────
// The four slots that are the owner's rather than ours.
//
// The machine ships with four faces that cannot be removed, and keeps room for
// four more that only ever arrive from here. So this screen is two verbs: add
// a picture into a slot that is free, and give a slot back.
//
// THE MACHINE IS THE TRUTH ABOUT WHAT IT HOLDS. Occupancy comes from the board
// on every state frame, never from what this app thinks it uploaded — a phone
// that was reinstalled, or a second phone, still sees the machine correctly.
// What the app keeps is only the picture it happened to send, so a slot it
// filled can be shown as itself instead of as a filled rectangle.
// ────────────────────────────────────────────────────────────

struct ImagesView: View {
    @Environment(BLEManager.self) var ble
    @State private var picking: Int?
    @State private var pickedItem: PhotosPickerItem?
    @State private var confirmRemove: Int?

    var body: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            VStack(spacing: 0) {
                Text("Your Pictures")
                    .font(.system(size: 22, weight: .medium))
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.top, 28)

                Text("Four of the eight faces on this machine are yours. "
                     + "Choose which one a flavor wears on the machine itself.")
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
                    .padding(.top, 8)

                if ble.imageSlots.count == 0 {
                    Spacer()
                    ProgressView().tint(Theme.textSecondary)
                    Text("asking the machine what it holds")
                        .font(.system(size: 13))
                        .foregroundStyle(Theme.textSecondary)
                        .padding(.top, 12)
                    Spacer()
                } else {
                    slots
                    Spacer()
                    status
                }
            }
        }
        .onAppear { ble.queryImageSlots() }
        .photosPicker(isPresented: Binding(get: { picking != nil },
                                           set: { if !$0 { picking = nil } }),
                      selection: $pickedItem, matching: .images)
        .onChange(of: pickedItem) { _, item in
            guard let item, let slot = picking else { return }
            picking = nil
            pickedItem = nil
            Task { await load(item, into: slot) }
        }
        .confirmationDialog("Remove this picture?",
                            isPresented: Binding(get: { confirmRemove != nil },
                                                 set: { if !$0 { confirmRemove = nil } }),
                            titleVisibility: .visible) {
            Button("Remove", role: .destructive) {
                if let slot = confirmRemove { ble.removeImage(slot: slot) }
                confirmRemove = nil
            }
            Button("Keep it", role: .cancel) { confirmRemove = nil }
        } message: {
            Text("The slot becomes free. A flavor wearing it goes back to its original face.")
        }
    }

    private var slots: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 130), spacing: 16)], spacing: 16) {
            ForEach(0..<ble.imageSlots.count, id: \.self) { slot in
                slotTile(slot)
            }
        }
        .padding(.horizontal, 24)
        .padding(.top, 28)
    }

    @ViewBuilder
    private func slotTile(_ slot: Int) -> some View {
        let held = ble.imageSlots.isHeld(slot)
        VStack(spacing: 10) {
            ZStack {
                RoundedRectangle(cornerRadius: 14)
                    .fill(Color.white.opacity(held ? 0.10 : 0.04))
                    .aspectRatio(172.0 / 320.0, contentMode: .fit)
                if held, let cached = SlotPreviews.load(unit: ble.connectedMachine?.unit ?? "", slot: slot) {
                    Image(uiImage: cached)
                        .resizable()
                        .aspectRatio(172.0 / 320.0, contentMode: .fit)
                        .clipShape(RoundedRectangle(cornerRadius: 14))
                } else if held {
                    Image(systemName: "photo.fill")
                        .font(.system(size: 26))
                        .foregroundStyle(Theme.textSecondary)
                } else {
                    RoundedRectangle(cornerRadius: 14)
                        .strokeBorder(style: StrokeStyle(lineWidth: 1.5, dash: [5, 4]))
                        .foregroundStyle(Theme.textSecondary.opacity(0.4))
                        .aspectRatio(172.0 / 320.0, contentMode: .fit)
                    Image(systemName: "plus")
                        .font(.system(size: 22, weight: .light))
                        .foregroundStyle(Theme.textSecondary)
                }
            }

            Button(held ? "Remove" : "Add") {
                if held { confirmRemove = slot } else { picking = slot }
            }
            .font(.system(size: 14, weight: .medium))
            .foregroundStyle(held ? Color.red.opacity(0.85) : Theme.textPrimary)
            .disabled(isBusy)
        }
        .opacity(isBusy ? 0.5 : 1)
    }

    private var isBusy: Bool {
        if case .sending = ble.imageUploadState { return true }
        return ble.imageUploadState == .preparing
    }

    @ViewBuilder
    private var status: some View {
        Group {
            switch ble.imageUploadState {
            case .preparing:
                label("preparing the picture…")
            case .sending(let sent, let total):
                VStack(spacing: 8) {
                    ProgressView(value: Double(sent), total: Double(total))
                        .tint(Theme.textPrimary)
                    label("sending — \(sent * 100 / max(total, 1))%")
                }
            case .done:
                label("on the machine")
            case .failed(let why):
                label(why).foregroundStyle(Color.red.opacity(0.85))
            case .idle:
                label("\(ble.imageSlots.held) of \(ble.imageSlots.count) slots in use")
            }
        }
        .padding(.horizontal, 32)
        .padding(.bottom, 36)
    }

    private func label(_ s: String) -> some View {
        Text(s)
            .font(.system(size: 13))
            .foregroundStyle(Theme.textSecondary)
            .frame(maxWidth: .infinity)
    }

    private func load(_ item: PhotosPickerItem, into slot: Int) async {
        guard let data = try? await item.loadTransferable(type: Data.self),
              let image = UIImage(data: data) else { return }
        // Kept before the push rather than after: what is shown for a filled
        // slot should be what was sent, even if the send is what fails.
        if let preview = ImageBundle.preview(from: image) {
            SlotPreviews.save(preview, unit: ble.connectedMachine?.unit ?? "", slot: slot)
        }
        ble.uploadImage(image, to: slot)
    }
}

// What this phone happens to have sent, so a filled slot can be shown as
// itself. Not authority over anything: the machine says what it holds.
enum SlotPreviews {
    private static func url(_ unit: String, _ slot: Int) -> URL? {
        guard !unit.isEmpty else { return nil }
        let dir = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
        return dir.appendingPathComponent("slot-\(unit)-\(slot).png")
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
