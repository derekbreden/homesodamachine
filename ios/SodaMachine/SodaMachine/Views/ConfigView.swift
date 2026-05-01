import SwiftUI
import UIKit
import Charts
import PhotosUI

// ────────────────────────────────────────────────────────────
// PagedDots — a SwiftUI wrapper around UIKit's UIPageControl.
//
// Why not use SwiftUI's built-in .tabViewStyle(.page) indicator? It draws
// the same dots and forwards taps/scrubs visually, but doesn't surface the
// underlying UIPageControl's *adjustable* accessibility trait — VoiceOver
// can't focus it, Voice Control's "Show Numbers" doesn't number it, Switch
// Control can't reach it. Bringing the actual UIPageControl in via
// UIViewRepresentable is the only reliable way to get the native:
//
//   - tap-on-either-side          (prev / next page)
//   - scrub                       (continuous step — rotary-knob analog)
//   - VoiceOver adjustable trait  (focus once, swipe up/down to step)
//   - Voice Control numbered      (increment / decrement commands)
//   - Switch Control navigable
//
// Mirrors the design intent of the S3 rotary knob: one control, discrete
// steps, multiple input methods all converging on the same model.
// ────────────────────────────────────────────────────────────

/// `UIPageControl` that wraps from the last page back to the first when
/// activated by an assistive technology. Default `accessibilityActivate`
/// (invoked by VoiceOver double-tap and Voice Control "Tap [N]") sends a
/// touch which UIPageControl reads as "advance to next page" — but on the
/// last page there is no next, so the activation does nothing and the user
/// gets stuck. Wrapping lets the activation keep flowing through the cycle.
///
/// Sighted users tapping the dots directly bypass `accessibilityActivate`
/// and hit UIControl's regular hit-testing (tap left/right half = prev/next),
/// so this override only changes the assistive-activation behavior.
private final class AccessiblePageControl: UIPageControl {
    override func accessibilityActivate() -> Bool {
        guard numberOfPages > 0 else { return false }
        currentPage = (currentPage + 1) % numberOfPages
        sendActions(for: .valueChanged)
        return true
    }
}

private struct PagedDots: UIViewRepresentable {
    @Binding var currentPage: Int
    let pageCount: Int

    func makeUIView(context: Context) -> UIPageControl {
        let pc = AccessiblePageControl()
        pc.numberOfPages = pageCount
        pc.currentPage = currentPage
        pc.currentPageIndicatorTintColor = UIColor(Theme.dotActive)
        pc.pageIndicatorTintColor = UIColor(Theme.dotInactive)
        pc.allowsContinuousInteraction = true        // enables scrub
        pc.backgroundStyle = .automatic              // pill on interaction
        pc.addTarget(
            context.coordinator,
            action: #selector(Coordinator.pageChanged(_:)),
            for: .valueChanged
        )
        return pc
    }

    func updateUIView(_ uiView: UIPageControl, context: Context) {
        if uiView.numberOfPages != pageCount { uiView.numberOfPages = pageCount }
        if uiView.currentPage != currentPage { uiView.currentPage = currentPage }
    }

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    final class Coordinator: NSObject {
        var parent: PagedDots
        init(_ parent: PagedDots) { self.parent = parent }
        @objc func pageChanged(_ sender: UIPageControl) {
            parent.currentPage = sender.currentPage
        }
    }
}

// ────────────────────────────────────────────────────────────
// Separate View structs create their own @Observable observation
// scopes. Changes to cachedImages / imageDownloadProgress only
// re-render these leaf views — NOT the parent ConfigView / TabView.
// This prevents image downloads from interrupting swipe gestures.
// ────────────────────────────────────────────────────────────

private struct ImageSlotView: View {
    @Environment(BLEManager.self) var ble
    let slot: Int

    var body: some View {
        Group {
            if let uiImage = ble.imageFor(slot: slot) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFill()
                    .frame(width: 120, height: 120)
                    .clipShape(Circle())
            } else {
                ZStack {
                    Circle()
                        .fill(Theme.placeholder)
                        .frame(width: 120, height: 120)
                    if ble.imageDownloadProgress != nil {
                        ProgressView()
                            .tint(Theme.textPrimary)
                    } else {
                        Image(systemName: "photo")
                            .font(.system(size: 24))
                            .foregroundStyle(Theme.textSecondary)
                    }
                }
            }
        }
        .padding(6)
        .overlay(
            Circle()
                .stroke(Theme.textPrimary, lineWidth: 1)
        )
    }
}

// ────────────────────────────────────────────────────────────
// Image picker sheet — grid of images with selection border
// ────────────────────────────────────────────────────────────

private struct ImagePickerSheet: View {
    @Environment(BLEManager.self) var ble
    @Environment(\.dismiss) var dismiss
    let flavorLabel: String
    @State var selectedSlot: Int
    let onSelect: (Int) -> Void

    @State private var selectedPhotos: [PhotosPickerItem] = []
    @State private var deleteSlot: Int?
    @State private var showDeleteConfirm = false

    private let columns = [GridItem(.adaptive(minimum: 120), spacing: 20)]
    private let maxImages = 10

    private var totalPendingSlots: Int {
        ble.numImages + ble.uploadQueue.count + (ble.uploadProgress != nil ? 1 : 0)
    }

    private var canDelete: Bool {
        ble.numImages > 1 && ble.imageDownloadProgress == nil && ble.uploadQueue.isEmpty && ble.uploadProgress == nil
    }

    var body: some View {
        NavigationView {
            ScrollView {
                LazyVGrid(columns: columns, spacing: 20) {
                    // Existing images
                    ForEach(0..<ble.numImages, id: \.self) { slot in
                        imageCircle(slot: slot)
                    }

                    // Active upload
                    if let activeImage = ble.activeUploadImage, ble.uploadProgress != nil {
                        RadialProgressCircle(image: activeImage, progress: ble.uploadProgress ?? 0)
                            .contextMenu {
                                Button("Cancel Upload", role: .destructive) {
                                    ble.cancelActiveUpload()
                                }
                            }
                    }

                    // Queued uploads
                    ForEach(ble.uploadQueue) { item in
                        RadialProgressCircle(image: item.image, progress: nil)
                            .contextMenu {
                                Button("Cancel Upload", role: .destructive) {
                                    ble.cancelQueuedUpload(id: item.id)
                                }
                            }
                    }

                    // Add button
                    if totalPendingSlots < maxImages && ble.imageDownloadProgress == nil {
                        let remaining = maxImages - totalPendingSlots
                        PhotosPicker(
                            selection: $selectedPhotos,
                            maxSelectionCount: remaining,
                            selectionBehavior: .ordered,
                            matching: .images
                        ) {
                            ZStack {
                                Circle()
                                    .fill(Theme.placeholder)
                                    .frame(width: 120, height: 120)
                                Image(systemName: "plus")
                                    .font(.system(size: 28))
                                    .foregroundStyle(Theme.textSecondary)
                            }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 20)
            }
            .background(Theme.background)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(flavorLabel)
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
            .alert("Delete Image?", isPresented: $showDeleteConfirm) {
                Button("Delete", role: .destructive) {
                    if let slot = deleteSlot {
                        ble.deleteImage(slot: slot)
                    }
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("This cannot be undone.")
            }
            .alert("Delete Failed", isPresented: Binding(
                get: { ble.deleteError != nil },
                set: { if !$0 { ble.deleteError = nil } }
            )) {
                Button("OK") { ble.deleteError = nil }
            } message: {
                Text(ble.deleteError ?? "")
            }
            .onChange(of: selectedPhotos) { _, newItems in
                guard !newItems.isEmpty else { return }
                Task {
                    var images: [UIImage] = []
                    for item in newItems {
                        if let data = try? await item.loadTransferable(type: Data.self),
                           let image = UIImage(data: data) {
                            images.append(image)
                        }
                    }
                    selectedPhotos = []
                    if !images.isEmpty {
                        let items = images.map { BLEManager.UploadQueueItem(image: $0) }
                        ble.queueUploads(items)
                    }
                }
            }
        }
    }

    private func imageCircle(slot: Int) -> some View {
        Group {
            if let uiImage = ble.imageFor(slot: slot) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFill()
                    .frame(width: 120, height: 120)
                    .clipShape(Circle())
            } else {
                ZStack {
                    Circle()
                        .fill(Theme.placeholder)
                        .frame(width: 120, height: 120)
                    Image(systemName: "photo")
                        .font(.system(size: 24))
                        .foregroundStyle(Theme.textSecondary)
                }
            }
        }
        .padding(5)
        .overlay(
            Circle()
                .stroke(slot == selectedSlot ? Theme.textPrimary : .clear, lineWidth: 1)
        )
        .onTapGesture {
            selectedSlot = slot
            onSelect(slot)
        }
        .contextMenu {
            if canDelete {
                Button("Delete", role: .destructive) {
                    deleteSlot = slot
                    showDeleteConfirm = true
                }
            }
        }
    }
}

private struct RadialProgressCircle: View {
    let image: UIImage
    let progress: Double?  // nil = queued, 0-1 = uploading

    var body: some View {
        ZStack {
            Image(uiImage: image)
                .resizable()
                .scaledToFill()
                .frame(width: 120, height: 120)
                .clipShape(Circle())

            Circle()
                .fill(Color.black.opacity(0.5))
                .frame(width: 120, height: 120)

            if let progress {
                Circle()
                    .trim(from: 0, to: progress)
                    .stroke(Color.white, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                    .frame(width: 100, height: 100)
                    .rotationEffect(.degrees(-90))
            } else {
                Image(systemName: "clock")
                    .font(.system(size: 24))
                    .foregroundStyle(.white.opacity(0.7))
            }
        }
    }
}

// ────────────────────────────────────────────────────────────
// Ratio picker sheet — wheel picker for 1:6 through 1:24
// ────────────────────────────────────────────────────────────

private struct RatioPickerSheet: View {
    @Environment(\.dismiss) var dismiss
    let flavorLabel: String
    @State var ratio: Int
    let onDismiss: (Int) -> Void

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                Picker("Ratio", selection: $ratio) {
                    ForEach(6...24, id: \.self) { value in
                        Text("1:\(value)")
                            .foregroundStyle(Theme.textPrimary)
                            .accessibilityLabel("1 to \(value)")
                            .tag(value)
                    }
                }
                .pickerStyle(.wheel)
                .labelsHidden()
                .accessibilityLabel(flavorLabel)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(flavorLabel)
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
        .onDisappear {
            onDismiss(ratio)
        }
    }
}

// ────────────────────────────────────────────────────────────
// Settings page — shown inline on page 4 of the carousel.
// Tappable items with press-to-highlight feedback.
// ────────────────────────────────────────────────────────────

private struct SettingsItemButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundStyle(configuration.isPressed ? Theme.textPrimary : Theme.textSecondary)
    }
}

private struct SettingsPageView: View {
    @Environment(BLEManager.self) var ble
    @Binding var inAbout: Bool
    @Binding var inStats: Bool
    @Binding var inPrime: Bool
    @Binding var inClean: Bool
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
    @State private var showResetAlert = false
    @State private var showDisconnectAlert = false
    @State private var resetting = false

    var body: some View {
        VStack(spacing: 12) {
            if resetting {
                ProgressView()
                    .tint(Theme.textPrimary)
                    .padding(.top, 8)
                Text("Resetting...")
                    .font(.system(size: 16))
                    .foregroundStyle(Theme.textSecondary)
            } else {
                VStack(spacing: 0) {
                    settingsButton("Usage Stats") {
                        inStats = true
                    }
                    settingsButton("Prime") {
                        inPrime = true
                    }
                    settingsButton("Clean") {
                        inClean = true
                    }
                    settingsButton("Factory Reset") {
                        showResetAlert = true
                    }
                    settingsButton("About") {
                        ble.requestVersions()
                        inAbout = true
                    }
                    if ble.demoMode {
                        settingsButton("Exit Demo Mode") {
                            UserDefaults.standard.set(false, forKey: "prefersDemoMode")
                            ble.exitDemoMode()
                            hasCompletedOnboarding = false
                        }
                    } else {
                        settingsButton("Disconnect") {
                            showDisconnectAlert = true
                        }
                    }
                }
            }
        }
        .alert("Disconnect?", isPresented: $showDisconnectAlert) {
            Button("Disconnect", role: .destructive) {
                ble.disconnect()
                hasCompletedOnboarding = false
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Are you sure you want to disconnect from this home soda machine?")
        }
        .alert("Factory Reset?", isPresented: $showResetAlert) {
            Button("Reset", role: .destructive) {
                resetting = true
                ble.factoryReset()
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This will reset all settings to factory defaults.")
        }
        .onChange(of: ble.factoryResetCompleted) { _, completed in
            if completed {
                resetting = false
                ble.factoryResetCompleted = false
            }
        }
    }

    private func settingsButton(_ title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 16, weight: .medium))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
        }
        .buttonStyle(SettingsItemButtonStyle())
    }
}

// ────────────────────────────────────────────────────────────
// About screen (version display)
// ────────────────────────────────────────────────────────────

private struct AboutSheet: View {
    @Environment(BLEManager.self) var ble
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 0) {
                    Spacer()

                    let labels = ["S3", "ESP32", "RP2040"]
                    let versions = [ble.s3Version, ble.espVersion, ble.rpVersion]

                    ForEach(0..<3, id: \.self) { i in
                        VStack(spacing: 4) {
                            Text(labels[i])
                                .font(.system(size: 16))
                                .foregroundStyle(Theme.textSecondary)
                            Text(versions[i].isEmpty ? "..." : versions[i])
                                .font(.system(size: 16))
                                .foregroundStyle(Theme.textPrimary)
                        }
                        if i < 2 { Spacer().frame(height: 16) }
                    }

                    Spacer()
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("About")
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
    }
}

// ────────────────────────────────────────────────────────────
// Prime sheet — hold-to-run priming for selected flavor
// ────────────────────────────────────────────────────────────

private struct PrimeSheet: View {
    @Environment(BLEManager.self) var ble
    @Environment(\.dismiss) var dismiss
    @State private var selectedFlavor: Int? = nil
    @State private var tickTimer: Timer?

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 12) {
                    Spacer()

                    if let flavor = selectedFlavor {
                        Text("Prime Flavor \(flavor)")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundStyle(Theme.textSecondary)

                        Spacer().frame(height: 12)

                        Button("Back") {
                            selectedFlavor = nil
                        }
                        .buttonStyle(SettingsItemButtonStyle())
                        .disabled(ble.primeActive)

                        Text(ble.primeActive ? "Priming..." : "Hold to Prime")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(ble.primeActive ? Theme.primeBlue : Theme.textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(Color.white.opacity(ble.primeActive ? 0.08 : 0.04))
                            )
                            .contentShape(Rectangle())
                            .gesture(
                                DragGesture(minimumDistance: 0)
                                    .onChanged { _ in
                                        guard !ble.primeActive else { return }
                                        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
                                        ble.startPrime(flavor: flavor)
                                        startTickTimer()
                                    }
                                    .onEnded { _ in
                                        guard ble.primeActive else { return }
                                        ble.stopPrime()
                                        stopTickTimer()
                                    }
                            )
                            .accessibilityElement()
                            .accessibilityLabel(ble.primeActive ? "Priming flavor \(flavor)" : "Prime flavor \(flavor)")
                            .accessibilityHint("Touch and hold to dispense priming fluid; release to stop.")
                            .accessibilityAddTraits(.isButton)
                    } else {
                        VStack(spacing: 0) {
                            Button(action: { selectedFlavor = 1 }) {
                                Text("Flavor 1")
                                    .font(.system(size: 16, weight: .medium))
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                            }
                            .buttonStyle(SettingsItemButtonStyle())
                            Button(action: { selectedFlavor = 2 }) {
                                Text("Flavor 2")
                                    .font(.system(size: 16, weight: .medium))
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                            }
                            .buttonStyle(SettingsItemButtonStyle())
                        }
                    }

                    Spacer()
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("Prime")
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
        .interactiveDismissDisabled(ble.primeActive)
        .onDisappear {
            if ble.primeActive {
                ble.stopPrime()
            }
            stopTickTimer()
        }
    }

    private func startTickTimer() {
        tickTimer?.invalidate()
        tickTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
            ble.sendPrimeTick()
        }
    }

    private func stopTickTimer() {
        tickTimer?.invalidate()
        tickTimer = nil
    }
}

// ────────────────────────────────────────────────────────────
// Clean sheet — clean cycle with confirmation
// ────────────────────────────────────────────────────────────

private struct CleanSheet: View {
    @Environment(BLEManager.self) var ble
    @Environment(\.dismiss) var dismiss
    @State private var showConfirm = false
    @State private var selectedFlavor = 1

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 12) {
                    Spacer()

                    if ble.cleanCycleActive {
                        Text(ble.cleanCyclePhase ?? "Starting...")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(Theme.primeBlue)

                        Spacer().frame(height: 24)

                        Button("Abort") {
                            ble.abortCleanCycle()
                        }
                        .buttonStyle(SettingsItemButtonStyle())
                    } else {
                        VStack(spacing: 0) {
                            cleanButton("Flavor 1") {
                                selectedFlavor = 1
                                showConfirm = true
                            }
                            cleanButton("Flavor 2") {
                                selectedFlavor = 2
                                showConfirm = true
                            }
                        }
                    }

                    Spacer()
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("Clean")
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
            .alert("Clean Flavor \(selectedFlavor)?", isPresented: $showConfirm) {
                Button("Start") {
                    ble.startCleanCycle(flavor: selectedFlavor)
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("This will flush the line with water. Make sure the water supply is connected.")
            }
            .onChange(of: ble.cleanCycleCompleted) { _, completed in
                if completed {
                    ble.cleanCycleCompleted = false
                    dismiss()
                }
            }
        }
        .interactiveDismissDisabled(ble.cleanCycleActive)
    }

    private func cleanButton(_ title: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 16, weight: .medium))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
        }
        .buttonStyle(SettingsItemButtonStyle())
    }
}

// ────────────────────────────────────────────────────────────
// Stats screen (usage statistics display with charts)
// ────────────────────────────────────────────────────────────

private struct StatsSheet: View {
    @Environment(BLEManager.self) var ble
    @Environment(\.horizontalSizeClass) var sizeClass
    @Environment(\.dismiss) var dismiss
    @AppStorage("servingSizeOz") private var servingSizeOz = 20

    private var isDisconnected: Bool {
        ble.connectionState != .connected && !ble.demoMode
    }

    private var isWide: Bool { sizeClass == .regular }

    var body: some View {
        NavigationView {
            ZStack {
                Theme.background.ignoresSafeArea()

                VStack(spacing: 0) {
                    if !ble.chartDataSynced {
                        Spacer()
                        ProgressView()
                            .tint(Theme.textPrimary)
                        Text("Loading stats...")
                            .font(.system(size: 16))
                            .foregroundStyle(Theme.textSecondary)
                            .padding(.top, 8)
                        Spacer()
                    } else if isWide {
                        VStack(spacing: 0) {
                            Spacer()
                            wideRow1
                            Spacer()
                            wideRow2
                            Spacer()
                        }
                        .padding(.horizontal, 20)
                    } else {
                        ScrollView {
                            VStack(spacing: 24) {
                                compactLayout
                            }
                            .padding(.horizontal, 20)
                            .padding(.bottom, 20)
                            .padding(.top, 8)
                        }
                    }
                }
                .opacity(isDisconnected ? 0.3 : 1.0)

                if isDisconnected {
                    VStack(spacing: 12) {
                        ProgressView()
                            .tint(Theme.textPrimary)
                        Text("Reconnecting...")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(Theme.textPrimary)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("Usage Stats")
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
    }

    // MARK: - Compact layout (iPhone)

    @ViewBuilder
    private var compactLayout: some View {
        if ble.statsSynced { pieChartSection }
        if ble.chartDataSynced {
            let size = servingSizeForOz(servingSizeOz)
            Chart24HView(servingSize: size)
            Chart30DView(servingSize: size)
            ChartHODView(servingSize: size)
            ServingSizeSelector(selectedOz: $servingSizeOz)
        } else {
            ProgressView().tint(Theme.textPrimary).padding(.vertical, 20)
        }
    }

    // MARK: - Wide layout (iPad) — two rows with even spacing

    @ViewBuilder
    private var wideRow1: some View {
        if ble.chartDataSynced {
            HStack(spacing: 24) {
                Group {
                    if ble.statsSynced {
                        pieChartSection
                    } else {
                        Color.clear.frame(height: 160)
                    }
                }
                .frame(maxWidth: .infinity)

                Chart24HView(servingSize: servingSizeForOz(servingSizeOz))
                    .frame(maxWidth: .infinity)
            }
        } else {
            ProgressView().tint(Theme.textPrimary).padding(.vertical, 20)
        }
    }

    @ViewBuilder
    private var wideRow2: some View {
        if ble.chartDataSynced {
            let size = servingSizeForOz(servingSizeOz)
            HStack(spacing: 24) {
                Chart30DView(servingSize: size)
                    .frame(maxWidth: .infinity)
                ChartHODView(servingSize: size)
                    .frame(maxWidth: .infinity)
            }
            ServingSizeSelector(selectedOz: $servingSizeOz)
        }
    }

    // MARK: - Pie Chart (30-day flavor split)

    private var pieChartSection: some View {
        let f1 = Double(ble.flavor1Stats.monthFlowSum) * 0.05
        let f2 = Double(ble.flavor2Stats.monthFlowSum) * 0.05
        let total = f1 + f2

        return VStack(spacing: 8) {
            Text("30-Day Flavor Split")
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(Theme.textSecondary)

            if total > 0 {
                HStack(spacing: 20) {
                    flavorLegendImage(flavor: 1, slot: ble.flavor1Image, color: Theme.chartPink, pct: Int(f1 / total * 100))
                    Chart {
                        SectorMark(angle: .value("Flavor 1", f1), innerRadius: .ratio(0.5))
                            .foregroundStyle(Theme.chartPink)
                        SectorMark(angle: .value("Flavor 2", f2), innerRadius: .ratio(0.5))
                            .foregroundStyle(Theme.chartPurple)
                    }
                    .frame(width: 120, height: 120)
                    .accessibilityHidden(true)
                    flavorLegendImage(flavor: 2, slot: ble.flavor2Image, color: Theme.chartPurple, pct: Int(f2 / total * 100))
                }
            } else {
                Text("No activity")
                    .font(.system(size: 13))
                    .foregroundStyle(Theme.textSecondary.opacity(0.6))
            }
        }
    }

    private func flavorLegendImage(flavor: Int, slot: Int, color: Color, pct: Int) -> some View {
        VStack(spacing: 6) {
            if let uiImage = ble.imageFor(slot: slot) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFill()
                    .frame(width: 56, height: 56)
                    .clipShape(Circle())
                    .overlay(Circle().stroke(color, lineWidth: 3))
            } else {
                Circle()
                    .fill(Theme.placeholder)
                    .frame(width: 56, height: 56)
                    .overlay(Circle().stroke(color, lineWidth: 3))
            }
            Text("\(pct)%")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(color)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Flavor \(flavor): \(pct) percent")
    }

}

// Separate View structs create distinct @Observable tracking boundaries,
// ensuring Chart recreation when BLEManager properties change.

private func servingSizeForOz(_ oz: Int) -> Double {
    switch oz {
    case 12: return 20.0
    case 16: return 25.0
    default: return 30.0
    }
}

private func toServings(_ raw: Double, size: Double) -> Double {
    (raw / size * 4).rounded() / 4
}

private func formatBarPair(f1: Double, f2: Double, averagePrefix: Bool = false) -> String {
    let prefix = averagePrefix ? "Average " : ""
    return "\(prefix)\(String(format: "%g", f1)) servings of Flavor 1, \(String(format: "%g", f2)) of Flavor 2"
}

private func dayAccessibilityLabel(daysAgo: Int, today: Date, calendar: Calendar) -> String {
    let date = calendar.date(byAdding: .day, value: -daysAgo, to: today) ?? today
    return date.formatted(.dateTime.month(.wide).day())
}

// MARK: - Glass Icon

private struct GlassIcon: View {
    let height: CGFloat
    let color: Color

    // SVG glass: x 310-714 (w=404), y 247-777 (h=530), aspect 404/530 = 0.7623
    private let aspect: CGFloat = 404.0 / 530.0

    var body: some View {
        let w = height * aspect
        Canvas { ctx, sz in
            // Scale factors from SVG glass bounding box (310,247)-(714,777)
            let sx = sz.width / 404.0
            let sy = sz.height / 530.0

            // Glass body path: M310,247 L340,747 Q345,777,380,777 L644,777 Q679,777,684,747 L714,247 Z
            // Normalized to glass origin (310, 247)
            var glass = Path()
            glass.move(to: CGPoint(x: 0 * sx, y: 0 * sy))           // M310,247
            glass.addLine(to: CGPoint(x: 30 * sx, y: 500 * sy))     // L340,747
            glass.addQuadCurve(                                       // Q345,777 380,777
                to: CGPoint(x: 70 * sx, y: 530 * sy),
                control: CGPoint(x: 35 * sx, y: 530 * sy))
            glass.addLine(to: CGPoint(x: 334 * sx, y: 530 * sy))    // L644,777
            glass.addQuadCurve(                                       // Q679,777 684,747
                to: CGPoint(x: 374 * sx, y: 500 * sy),
                control: CGPoint(x: 369 * sx, y: 530 * sy))
            glass.addLine(to: CGPoint(x: 404 * sx, y: 0 * sy))      // L714,247
            glass.closeSubpath()

            ctx.stroke(glass, with: .color(color), lineWidth: max(1.5, height / 40))

            // Rim highlight (thicker top edge)
            var rim = Path()
            rim.move(to: CGPoint(x: 0, y: 0))
            rim.addLine(to: CGPoint(x: 404 * sx, y: 0))
            ctx.stroke(rim, with: .color(color), lineWidth: max(2, height / 28))

            // Liquid surface wave — matches AppIcon.svg / GlassAnimationView t=0
            // SVG: M300,347 Q400,327 512,352 Q624,377 724,342
            // Glass-relative (subtract 310,247): (-10,100) Q(90,80 202,105) Q(314,130 414,95)
            var liquid = Path()
            liquid.move(to: CGPoint(x: -10 * sx, y: 100 * sy))
            liquid.addQuadCurve(
                to: CGPoint(x: 202 * sx, y: 105 * sy),
                control: CGPoint(x: 90 * sx, y: 80 * sy))
            liquid.addQuadCurve(
                to: CGPoint(x: 414 * sx, y: 95 * sy),
                control: CGPoint(x: 314 * sx, y: 130 * sy))
            ctx.stroke(liquid, with: .color(color), lineWidth: max(1, height / 50))

            // 4 bubbles matching AppIcon.svg t=0 positions (glass-relative: subtract 310,247)
            let bubbles: [(x: CGFloat, y: CGFloat, r: CGFloat)] = [
                (130, 493, 42),   // cx=440,cy=740
                (262, 363, 36),   // cx=572,cy=610
                (190, 242, 33),   // cx=500,cy=489
                (318, 161, 29),   // cx=628,cy=408
            ]
            let bw = max(1, height / 50)
            for b in bubbles {
                let circle = Path(ellipseIn: CGRect(
                    x: (b.x - b.r) * sx,
                    y: (b.y - b.r) * sy,
                    width: b.r * 2 * sx,
                    height: b.r * 2 * sy
                ))
                ctx.stroke(circle, with: .color(color), lineWidth: bw)
            }
        }
        .frame(width: w, height: height)
    }
}

// MARK: - Serving Size Selector

private struct ServingSizeSelector: View {
    @Binding var selectedOz: Int

    private let options: [(oz: Int, label: String, iconHeight: CGFloat)] = [
        (12, "12oz", 48),
        (16, "16oz", 56),
        (20, "20oz", 64),
    ]

    var body: some View {
        VStack(spacing: 8) {
            Text("Serving Size")
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(Theme.textSecondary)

            HStack(alignment: .bottom, spacing: 32) {
                ForEach(options, id: \.oz) { opt in
                    let isSelected = selectedOz == opt.oz
                    let color = isSelected ? Theme.textPrimary : Theme.textSecondary.opacity(0.4)

                    Button {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedOz = opt.oz
                        }
                    } label: {
                        VStack(spacing: 4) {
                            GlassIcon(height: opt.iconHeight, color: color)
                            Text(opt.label)
                                .font(.system(size: 11, weight: isSelected ? .semibold : .regular))
                                .foregroundStyle(color)
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
}

private struct Chart24HView: View {
    @Environment(BLEManager.self) var ble
    let servingSize: Double
    var body: some View {
        let calendar = Calendar.current
        let currentHour = calendar.component(.hour, from: Date())
        let data0 = ble.chartData24H[0].map { toServings($0, size: servingSize) }
        let data1 = ble.chartData24H[1].map { toServings($0, size: servingSize) }

        VStack(spacing: 8) {
            Text("Last 24 Hours")
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(Theme.textSecondary)

            Chart {
                ForEach(0..<24, id: \.self) { i in
                    Plot {
                        BarMark(
                            x: .value("Hour", i),
                            y: .value("Servings", data0[i])
                        )
                        .foregroundStyle(by: .value("Flavor", "Flavor 1"))

                        BarMark(
                            x: .value("Hour", i),
                            y: .value("Servings", data1[i])
                        )
                        .foregroundStyle(by: .value("Flavor", "Flavor 2"))
                    }
                    .accessibilityLabel(hourLabel((currentHour - 23 + i + 24) % 24))
                    .accessibilityValue(formatBarPair(f1: data0[i], f2: data1[i]))
                }
            }

            .chartForegroundStyleScale(["Flavor 1": Theme.chartPink, "Flavor 2": Theme.chartPurple])
            .chartLegend(.hidden)
            .chartXScale(domain: -0.5...23.5)
            .chartXAxis {
                AxisMarks(values: [0, 6, 12, 18]) { value in
                    AxisValueLabel {
                        if let idx = value.as(Int.self) {
                            let hour = (currentHour - 23 + idx + 24) % 24
                            Text(hourLabel(hour))
                                .font(.system(size: 10))
                                .foregroundStyle(Theme.textSecondary)
                        }
                    }
                    AxisGridLine().foregroundStyle(Theme.textSecondary.opacity(0.2))
                }
            }
            .chartYAxis {
                AxisMarks { value in
                    AxisValueLabel {
                        if let v = value.as(Double.self) {
                            Text(String(format: "%g", v))
                                .font(.system(size: 10))
                                .foregroundStyle(Theme.textSecondary)
                        }
                    }
                    AxisGridLine().foregroundStyle(Theme.textSecondary.opacity(0.2))
                }
            }
            .frame(height: 160)
        }
    }

    private func hourLabel(_ hour: Int) -> String {
        let h = hour % 12
        let ampm = hour < 12 ? "AM" : "PM"
        return "\(h == 0 ? 12 : h) \(ampm)"
    }
}

private struct Chart30DView: View {
    @Environment(BLEManager.self) var ble
    let servingSize: Double

    var body: some View {
        let calendar = Calendar.current
        let today = Date()
        let data0 = ble.chartData30D[0].map { toServings($0, size: servingSize) }
        let data1 = ble.chartData30D[1].map { toServings($0, size: servingSize) }

        VStack(spacing: 8) {
            Text("Last 30 Days")
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(Theme.textSecondary)

            Chart {
                ForEach(0..<30, id: \.self) { i in
                    Plot {
                        BarMark(
                            x: .value("Day", i),
                            y: .value("Servings", data0[i])
                        )
                        .foregroundStyle(by: .value("Flavor", "Flavor 1"))

                        BarMark(
                            x: .value("Day", i),
                            y: .value("Servings", data1[i])
                        )
                        .foregroundStyle(by: .value("Flavor", "Flavor 2"))
                    }
                    .accessibilityLabel(dayAccessibilityLabel(daysAgo: 29 - i, today: today, calendar: calendar))
                    .accessibilityValue(formatBarPair(f1: data0[i], f2: data1[i]))
                }
            }

            .chartForegroundStyleScale(["Flavor 1": Theme.chartPink, "Flavor 2": Theme.chartPurple])
            .chartLegend(.hidden)
            .chartXScale(domain: -0.5...29.5)
            .chartXAxis {
                AxisMarks(values: [0, 7, 14, 21]) { value in
                    AxisValueLabel {
                        if let idx = value.as(Int.self) {
                            let date = calendar.date(byAdding: .day, value: idx - 29, to: today) ?? today
                            Text(date.formatted(.dateTime.month(.abbreviated).day()))
                                .font(.system(size: 10))
                                .foregroundStyle(Theme.textSecondary)
                        }
                    }
                    AxisGridLine().foregroundStyle(Theme.textSecondary.opacity(0.2))
                }
            }
            .chartYAxis {
                AxisMarks { value in
                    AxisValueLabel {
                        if let v = value.as(Double.self) {
                            Text(String(format: "%g", v))
                                .font(.system(size: 10))
                                .foregroundStyle(Theme.textSecondary)
                        }
                    }
                    AxisGridLine().foregroundStyle(Theme.textSecondary.opacity(0.2))
                }
            }
            .frame(height: 160)
        }
    }
}

private struct ChartHODView: View {
    @Environment(BLEManager.self) var ble
    let servingSize: Double

    var body: some View {
        let days = max(ble.chartDataHODDays, 1)
        let data0 = ble.chartDataHOD[0].map { toServings($0 / Double(days), size: servingSize) }
        let data1 = ble.chartDataHOD[1].map { toServings($0 / Double(days), size: servingSize) }

        VStack(spacing: 8) {
            Text("Average by Hour of Day")
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(Theme.textSecondary)

            Chart {
                ForEach(0..<24, id: \.self) { h in
                    Plot {
                        BarMark(
                            x: .value("Hour", h),
                            y: .value("Avg Servings", data0[h])
                        )
                        .foregroundStyle(by: .value("Flavor", "Flavor 1"))

                        BarMark(
                            x: .value("Hour", h),
                            y: .value("Avg Servings", data1[h])
                        )
                        .foregroundStyle(by: .value("Flavor", "Flavor 2"))
                    }
                    .accessibilityLabel(hourLabel(h))
                    .accessibilityValue(formatBarPair(f1: data0[h], f2: data1[h], averagePrefix: true))
                }
            }

            .chartForegroundStyleScale(["Flavor 1": Theme.chartPink, "Flavor 2": Theme.chartPurple])
            .chartLegend(.hidden)
            .chartXScale(domain: -0.5...23.5)
            .chartXAxis {
                AxisMarks(values: [0, 6, 12, 18]) { value in
                    AxisValueLabel {
                        if let idx = value.as(Int.self) {
                            Text(hourLabel(idx))
                                .font(.system(size: 10))
                                .foregroundStyle(Theme.textSecondary)
                        }
                    }
                    AxisGridLine().foregroundStyle(Theme.textSecondary.opacity(0.2))
                }
            }
            .chartYAxis {
                AxisMarks { value in
                    AxisValueLabel {
                        if let v = value.as(Double.self) {
                            Text(String(format: "%g", v))
                                .font(.system(size: 10))
                                .foregroundStyle(Theme.textSecondary)
                        }
                    }
                    AxisGridLine().foregroundStyle(Theme.textSecondary.opacity(0.2))
                }
            }
            .frame(height: 160)

            Text("\(days) day\(days == 1 ? "" : "s") of data")
                .font(.system(size: 11))
                .foregroundStyle(Theme.textSecondary.opacity(0.6))
        }
    }

    private func hourLabel(_ hour: Int) -> String {
        let h = hour % 12
        let ampm = hour < 12 ? "AM" : "PM"
        return "\(h == 0 ? 12 : h) \(ampm)"
    }
}

// ────────────────────────────────────────────────────────────

struct ConfigView: View {
    @Environment(BLEManager.self) var ble
    @Environment(\.scenePhase) private var scenePhase
    @State private var currentPage = 0
    @State private var showFlavor1Picker = false
    @State private var showFlavor2Picker = false
    @State private var showFlavor1Ratio = false
    @State private var showFlavor2Ratio = false
    @State private var inAbout = false
    @State private var inStats = false
    @State private var inPrime = false
    @State private var inClean = false

    private let pageCount = 5
    private let pageLabels = ["Flavor 1 Image", "Flavor 1 Ratio", "Flavor 2 Image", "Flavor 2 Ratio", "Settings"]

    var body: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            if !ble.configSynced {
                VStack(spacing: 16) {
                    ProgressView()
                        .scaleEffect(1.5)
                        .tint(Theme.textPrimary)
                    Text("Loading configuration...")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundStyle(Theme.textPrimary)
                }
            } else {
                carouselContent
            }
        }
        .sheet(isPresented: $showFlavor1Picker) {
            ImagePickerSheet(flavorLabel: "Flavor 1 Image", selectedSlot: ble.flavor1Image) { slot in
                ble.flavor1Image = slot
                ble.sendSet("F1_IMAGE", value: slot)
            }
            .environment(ble)
        }
        .sheet(isPresented: $showFlavor2Picker) {
            ImagePickerSheet(flavorLabel: "Flavor 2 Image", selectedSlot: ble.flavor2Image) { slot in
                ble.flavor2Image = slot
                ble.sendSet("F2_IMAGE", value: slot)
            }
            .environment(ble)
        }
        .sheet(isPresented: $showFlavor1Ratio) {
            RatioPickerSheet(flavorLabel: "Flavor 1 Ratio", ratio: ble.flavor1Ratio) { value in
                ble.flavor1Ratio = value
                ble.sendSet("F1_RATIO", value: value)
            }
        }
        .sheet(isPresented: $showFlavor2Ratio) {
            RatioPickerSheet(flavorLabel: "Flavor 2 Ratio", ratio: ble.flavor2Ratio) { value in
                ble.flavor2Ratio = value
                ble.sendSet("F2_RATIO", value: value)
            }
        }
        .sheet(isPresented: $inPrime) {
            PrimeSheet()
                .environment(ble)
        }
        .sheet(isPresented: $inClean) {
            CleanSheet()
                .environment(ble)
        }
        .sheet(isPresented: $inStats) {
            StatsSheet()
                .environment(ble)
                .onAppear {
                    ble.requestStatsAndCharts()
                    ble.subscribeStats()
                }
                .onDisappear { ble.unsubscribeStats() }
        }
        .sheet(isPresented: $inAbout) {
            AboutSheet()
                .environment(ble)
        }
        .onChange(of: ble.connectionState) { old, state in
            if state == .connected && old != .connected && inStats {
                ble.requestStatsAndCharts()
                ble.subscribeStats()
            }
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .active && inStats && ble.connectionState == .connected {
                ble.requestStatsAndCharts()
                ble.subscribeStats()
            } else if phase == .background && inStats {
                ble.unsubscribeStats()
            }
        }
    }

    // MARK: - Carousel (main menu)

    // SwiftUI's .tabViewStyle(.page) draws its own dots, but they don't
    // expose UIPageControl's accessibility traits. We hide that indicator
    // (.never) and overlay our own PagedDots, which is a real UIPageControl
    // wrapped via UIViewRepresentable — same look, plus the adjustable trait
    // for VoiceOver, numbered element for Voice Control, and Switch Control
    // navigability. See PagedDots above for the full rationale.
    private var carouselContent: some View {
        ZStack(alignment: .bottom) {
            TabView(selection: $currentPage) {
                ForEach(0..<pageCount, id: \.self) { i in
                    carouselPage(for: i)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .never))

            PagedDots(currentPage: $currentPage, pageCount: pageCount)
                .frame(height: 30)
                .padding(.bottom, 40)
        }
    }

    // MARK: - Page Views

    // Pages 0–3 are tap-to-edit (open the corresponding picker); page 4 is the
    // settings list. The first four are exposed to VoiceOver as a single
    // button per page so the swipe-and-double-tap interaction works; page 4
    // keeps its inner buttons individually navigable.
    @ViewBuilder
    private func carouselPage(for i: Int) -> some View {
        let page = VStack {
            Text(pageLabels[i])
                .font(.system(size: 16, weight: .medium))
                .foregroundStyle(Theme.textSecondary)
                .padding(.top, 60)

            Spacer()

            pageView(for: i)

            Spacer()
        }
        .padding(.bottom, 80)
        .contentShape(Rectangle())
        .onTapGesture {
            switch i {
            case 0: showFlavor1Picker = true
            case 1: showFlavor1Ratio = true
            case 2: showFlavor2Picker = true
            case 3: showFlavor2Ratio = true
            default: break
            }
        }
        .tag(i)

        if i < 4 {
            page
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Page \(i + 1) of \(pageCount): \(pageLabels[i])")
                .accessibilityAddTraits(.isButton)
                .accessibilityHint(i.isMultiple(of: 2) ? "Double tap to change image" : "Double tap to change ratio")
        } else {
            page
        }
    }

    @ViewBuilder
    private func pageView(for index: Int) -> some View {
        switch index {
        case 0:
            ImageSlotView(slot: ble.flavor1Image)
        case 1:
            ratioDisplay(ratio: ble.flavor1Ratio)
        case 2:
            ImageSlotView(slot: ble.flavor2Image)
        case 3:
            ratioDisplay(ratio: ble.flavor2Ratio)
        case 4:
            SettingsPageView(inAbout: $inAbout, inStats: $inStats, inPrime: $inPrime, inClean: $inClean)
        default:
            EmptyView()
        }
    }

    private func ratioDisplay(ratio: Int) -> some View {
        Text("1:\(ratio)")
            .font(.system(size: 36, weight: .regular, design: .rounded))
            .foregroundStyle(Theme.textSecondary)
    }
}
