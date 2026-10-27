import SwiftUI

// A native, local-data proposal. This target has no radio, persistence or network.
// The layout and controls are executable SwiftUI; the fixture is deliberately
// separate from the production BLE model.
enum StudyRoute: String, CaseIterable {
    case home, flavor, images, crop, uploading, care, fill, filling, clean, cleaning
    case prime, priming, settings, sound, update, updating, current, machines, rename, add
    case offline, bluetooth, unread, alarm, busy, stopped, complete, lost, clock, imageError
    case fillStopped, fillFull, cleanFunnel, stopping, updateError, restarting, verifying

    var tab: String {
        switch self {
        case .care, .fill, .filling, .clean, .cleaning, .prime, .priming, .busy, .stopped, .complete, .lost, .fillStopped, .fillFull, .cleanFunnel, .stopping: "Care"
        case .settings, .sound, .update, .updating, .current, .machines, .rename, .clock, .updateError, .restarting, .verifying: "Settings"
        default: "Machine"
        }
    }
    var title: String {
        switch self {
        case .home, .offline, .bluetooth, .unread, .alarm: "Kitchen"
        case .flavor: "Flavor 1"
        case .images, .uploading, .imageError: "Flavor 1 image"
        case .crop: "Position your picture"
        case .care: "Care"
        case .fill, .filling, .fillStopped, .fillFull: "Fill Flavor 1"
        case .clean, .cleaning, .stopped, .complete, .lost, .cleanFunnel, .stopping: "Clean Flavor 1"
        case .prime, .priming: "Prime Flavor 1"
        case .settings: "Settings"
        case .sound, .clock: "Sound"
        case .update, .updating, .current, .updateError, .restarting, .verifying: "Software Update"
        case .machines: "Your machines"
        case .rename: "Machine name"
        case .add: "Soda Machine"
        case .busy: "Machine in use"
        }
    }
    var isTop: Bool { [.home, .offline, .bluetooth, .unread, .alarm, .care, .settings].contains(self) }
    var parent: StudyRoute {
        switch self {
        case .images: .flavor
        case .crop, .uploading, .imageError: .images
        case .sound, .clock, .update, .updateError, .current, .machines, .rename: .settings
        case .fill, .clean, .prime, .busy, .stopped, .complete, .fillStopped, .fillFull, .lost: .care
        default: .home
        }
    }
}

struct StudyRoot: View {
    @State private var route: StudyRoute
    @State private var fixture: StudyFixture
    @Environment(\.dynamicTypeSize) private var typeSize

    init(initialRoute: StudyRoute = .home) {
        _route = State(initialValue: initialRoute)
        _fixture = State(initialValue: StudyFixture(route: initialRoute))
    }

    private var disconnected: Bool { !fixture.isConnected }
    private var blocksNavigation: Bool { [.filling, .cleaning, .cleanFunnel, .stopping, .updating, .restarting, .verifying].contains(route) }
    private var ratio: Int { get { fixture.draftRatio } nonmutating set { fixture.draftRatio = newValue } }
    private var art: Int { fixture.arts[fixture.selectedChannel] }
    private var flavorLabel: String { "Flavor \(fixture.selectedChannel + 1)" }
    private var linkText: String {
        switch fixture.connection {
        case .connected: "Connected"
        case .outOfRange: route == .lost ? "Connection lost" : "Out of range · last read 10 min ago"
        case .bluetoothOff: "Bluetooth is off"
        }
    }
    private func go(_ next: StudyRoute) {
        if next == .rename { fixture.beginRename() }
        route = next
    }

    var body: some View {
        GeometryReader { geo in
            let sidebar = geo.size.width >= 1000 && !typeSize.isAccessibilitySize
            let pageWidth = min(840, geo.size.width - (sidebar ? 216 : 0) - 48)
            HStack(spacing: 0) {
                if sidebar && route != .add { sideNavigation }
                VStack(spacing: 0) {
                    if route != .add { header(sidebar: sidebar, width: pageWidth) }
                    if route == .crop {
                        cropEditor(size: CGSize(width: geo.size.width - (sidebar ? 216 : 0), height: geo.size.height - 164))
                    } else {
                        ScrollView {
                            content(width: pageWidth, height: geo.size.height)
                                .frame(maxWidth: pageWidth)
                                .frame(maxWidth: .infinity, alignment: .top)
                                .padding(.horizontal, 24)
                                .padding(.top, route == .add ? 32 : 20)
                                .padding(.bottom, 24)
                        }
                        .scrollIndicators(.automatic)
                    }
                    if !sidebar && route != .add && route != .crop { bottomNavigation }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            .background(Theme.background)
        }
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
        .preferredColorScheme(.dark)
        .font(.body)
    }

    private func header(sidebar: Bool, width: CGFloat) -> some View {
        let home = [.home, .offline, .bluetooth, .unread, .alarm].contains(route)
        return VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                if !route.isTop && !blocksNavigation {
                    Button { go(route.parent) } label: {
                        Image(systemName: "chevron.left").font(.body.weight(.medium)).frame(width: 32, height: 44, alignment: .leading)
                    }
                    .accessibilityLabel("Back")
                }
                if home && !sidebar {
                    Button { go(.machines) } label: {
                        HStack(spacing: 9) {
                            Text(fixture.machineName).font(.largeTitle.weight(.semibold))
                            Image(systemName: "chevron.down").font(.caption.weight(.semibold)).foregroundStyle(Theme.textSecondary)
                        }
                    }.buttonStyle(.plain).disabled(blocksNavigation)
                } else {
                    Text(home ? "Machine" : route.title.replacingOccurrences(of: "Flavor 1", with: flavorLabel))
                        .font(route.isTop ? .largeTitle.weight(.semibold) : .headline)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 8)
                if route.isTop && !home && !sidebar {
                    Button { go(.machines) } label: {
                        HStack(spacing: 6) { Text(fixture.machineName); Image(systemName: "chevron.down").font(.caption2) }
                            .font(.subheadline.weight(.medium)).foregroundStyle(Theme.textSecondary)
                            .padding(.horizontal, 12).padding(.vertical, 10)
                            .background(Theme.ice.opacity(0.08), in: Capsule())
                    }.buttonStyle(.plain).disabled(blocksNavigation)
                }
                if route == .crop {
                    Button("Cancel") { go(.images) }.frame(minHeight: 44)
                }
            }
            if !sidebar {
                HStack(spacing: 6) {
                    Circle().fill(disconnected ? Theme.textSecondary.opacity(0.5) : Theme.ice).frame(width: 5, height: 5)
                    Text(route.isTop ? linkText : "\(fixture.machineName) · \(linkText)")
                }
                .font(.caption)
                .foregroundStyle(Theme.textSecondary)
            }
        }
        .frame(maxWidth: width).frame(maxWidth: .infinity)
        .padding(.horizontal, 24)
        .padding(.top, route.isTop ? 24 : 10)
        .padding(.bottom, route.isTop ? 8 : 6)
        .background(Theme.background)
    }

    private let navigation: [(String, String, StudyRoute)] = [
        ("Machine", "drop", .home), ("Care", "sparkles", .care), ("Settings", "slider.horizontal.3", .settings)
    ]
    private var bottomNavigation: some View {
        HStack(spacing: 4) {
            ForEach(navigation, id: \.0) { item in
                Button { go(item.2) } label: {
                    VStack(spacing: 5) {
                        Image(systemName: item.0 == "Machine" && route.tab == item.0 ? "drop.fill" : item.1).font(.system(size: 20, weight: .regular))
                        Text(item.0).font(.caption2.weight(route.tab == item.0 ? .semibold : .regular))
                    }
                    .foregroundStyle(route.tab == item.0 ? Theme.accent : Theme.textSecondary)
                    .frame(maxWidth: .infinity, minHeight: 48)
                }.disabled(blocksNavigation)
            }
        }
        .frame(maxWidth: 480).frame(maxWidth: .infinity)
        .padding(.horizontal, 16).padding(.top, 8).padding(.bottom, 8)
        .background(Theme.surface)
        .overlay(alignment: .top) { Theme.ice.opacity(0.10).frame(height: 0.5) }
    }
    private var sideNavigation: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 10) {
                Image("LaunchIcon").resizable().scaledToFit().frame(width: 32, height: 32).accessibilityHidden(true)
                Text("Soda Machine").font(.subheadline.weight(.semibold))
            }.padding(.bottom, 24)
            Button { go(.machines) } label: {
                HStack {
                    VStack(alignment: .leading, spacing: 5) {
                        Text(fixture.machineName).font(.headline)
                        Text(linkText).font(.caption).foregroundStyle(Theme.textSecondary)
                    }
                    Spacer(minLength: 6)
                    Image(systemName: "chevron.down").font(.caption2)
                }.padding(12).background(Theme.background, in: RoundedRectangle(cornerRadius: 12))
            }.buttonStyle(.plain).disabled(blocksNavigation).padding(.bottom, 20)
            ForEach(navigation, id: \.0) { item in
                Button { go(item.2) } label: {
                    Label(item.0, systemImage: item.1)
                        .font(.subheadline.weight(.medium)).frame(maxWidth: .infinity, alignment: .leading)
                        .padding(12)
                        .foregroundStyle(route.tab == item.0 ? Theme.accent : Theme.textSecondary)
                        .background(route.tab == item.0 ? Theme.ice.opacity(0.08) : Color.clear, in: RoundedRectangle(cornerRadius: 10))
                }.disabled(blocksNavigation)
            }
            Spacer(minLength: 32)
            Button { go(.machines) } label: { Label("Your machines", systemImage: "square.stack").frame(minHeight: 44) }
                .foregroundStyle(Theme.textSecondary)
                .disabled(blocksNavigation)
        }
        .padding(20).frame(width: 216).background(Theme.surface)
    }

    @ViewBuilder private func content(width: CGFloat, height: CGFloat) -> some View {
        switch route {
        case .home, .offline, .bluetooth, .unread, .alarm: home(width: width, height: height)
        case .flavor: flavor(width: width)
        case .images, .uploading, .imageError: imagePicker(width: width)
        case .care: care(width: width)
        case .fill, .clean, .prime: preparation(width: width)
        case .filling, .cleaning, .priming, .busy, .stopped, .complete, .lost, .fillStopped, .fillFull, .cleanFunnel, .stopping: operation(width: width)
        case .settings: settings(width: width)
        case .sound, .clock: sound(width: width)
        case .update, .updating, .current, .updateError, .restarting, .verifying: software(width: width)
        case .machines: machines
        case .rename: rename
        case .add: onboarding(width: width)
        case .crop: EmptyView()
        }
    }

    private func section(_ title: String) -> some View {
        Text(title).font(.subheadline.weight(.medium)).foregroundStyle(Theme.textSecondary)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
    private func note(_ text: String) -> some View {
        Text(text).font(.subheadline).foregroundStyle(Theme.textSecondary)
            .fixedSize(horizontal: false, vertical: true).frame(maxWidth: .infinity, alignment: .leading)
    }
    private func panel<V: View>(@ViewBuilder _ content: () -> V) -> some View {
        VStack(alignment: .leading, spacing: 16, content: content).padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }
    private func action(_ text: String, primary: Bool = true, next: StudyRoute, forChannel: Int? = nil, perform: (() -> Void)? = nil) -> some View {
        Button { if let forChannel { fixture.beginFlavor(channel: forChannel) }; perform?(); go(next) } label: {
            Text(text).font(.body.weight(.semibold)).multilineTextAlignment(.center)
                .frame(maxWidth: .infinity, minHeight: 48)
                .foregroundStyle(primary ? Theme.onAccent : Theme.textPrimary)
                .background(primary ? Theme.accent : Theme.ice.opacity(0.12), in: RoundedRectangle(cornerRadius: 12))
        }.buttonStyle(.plain)
    }
    private func row(_ title: String, detail: String? = nil, icon: String? = nil, next: StudyRoute) -> some View {
        Button { go(next) } label: {
            HStack(spacing: 12) {
                if let icon { Image(systemName: icon).frame(width: 24).foregroundStyle(Theme.textSecondary) }
                Text(title).font(.body)
                Spacer(minLength: 12)
                if let detail { Text(detail).font(.subheadline).foregroundStyle(Theme.textSecondary) }
                Image(systemName: "chevron.right").font(.caption.weight(.semibold)).foregroundStyle(Theme.textSecondary)
            }.frame(minHeight: 52)
        }.buttonStyle(.plain)
    }
    private func groupedPanel<V: View>(@ViewBuilder _ content: () -> V) -> some View {
        VStack(spacing: 0, content: content).padding(.horizontal, 16).padding(.vertical, 4)
            .frame(maxWidth: .infinity)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }
    private var rowDivider: some View { Theme.ice.opacity(0.12).frame(height: 0.5).padding(.leading, 36) }
    private func artView(_ index: Int, height: CGFloat) -> some View {
        let picture = Bundle.main.path(forResource: "flavor_\(index + 1)", ofType: "png").flatMap(UIImage.init(contentsOfFile:)) ?? UIImage()
        return Image(uiImage: picture).resizable().scaledToFill()
            .frame(width: height * 43 / 80, height: height).clipped()
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .accessibilityLabel("Flavor artwork \(index + 1)")
    }
    private func gauge(_ n: Int, unknown: Bool = false) -> some View {
        HStack(spacing: 4) {
            ForEach(0..<4) { i in
                Capsule().fill(unknown ? Theme.ice.opacity(0.18) : i < n ? Theme.ice : Theme.ice.opacity(0.18)).frame(height: 5)
            }
        }.accessibilityLabel(unknown ? "Reservoir level unknown" : "Reservoir level \(n) of 4")
    }
    private func notice(_ title: String, _ message: String, icon: String = "info.circle", urgent: Bool = false) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon).foregroundStyle(urgent ? Theme.error : Theme.accent)
            VStack(alignment: .leading, spacing: 5) {
                Text(title).font(.body.weight(.semibold))
                note(message)
            }
        }.padding(16).frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
    }

    private func home(width: CGFloat, height: CGFloat) -> some View {
        let compact = !typeSize.isAccessibilitySize && (height < 520 || (width >= 360 && width < 552 && height < 740))
        return VStack(alignment: .leading, spacing: 20) {
            if fixture.connection == .outOfRange { notice("Last known readings", "Bring your device near the machine to make changes.") }
            if fixture.connection == .bluetoothOff { notice("Turn on Bluetooth", "Bluetooth connects this device to your machine.", icon: "antenna.radiowaves.left.and.right.slash") }
            if route == .alarm { notice("Gas alarm", "Check the machine now. Filling, cleaning and flavor injection are unavailable.", icon: "exclamationmark.triangle.fill", urgent: true) }
            if width >= 760 && !typeSize.isAccessibilitySize {
                HStack(alignment: .top, spacing: 24) {
                    flavorPair(compact: compact, artHeight: 200).frame(maxWidth: .infinity)
                    machineStatus.frame(width: min(260, width * 0.31))
                }
            } else {
                flavorPair(compact: compact, artHeight: 152)
                machineStatus
            }
        }
    }
    private func flavorPair(compact: Bool, artHeight: CGFloat) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            section("Flavors")
            LazyVGrid(columns: typeSize.isAccessibilitySize ? [GridItem(.flexible())] : [GridItem(.flexible(), spacing: 12), GridItem(.flexible())], spacing: 12) {
                flavorCard(0, level: 3, compact: compact, artHeight: artHeight)
                flavorCard(1, level: 1, compact: compact, artHeight: artHeight)
            }
        }
    }
    private func flavorCard(_ channel: Int, level: Int, compact: Bool, artHeight: CGFloat) -> some View {
        let active = fixture.activeFlavor == channel && route != .unread
        return Button { fixture.beginFlavor(channel: channel); go(.flavor) } label: {
            Group {
                if compact {
                    HStack(spacing: 12) {
                        if route == .unread {
                            Image(systemName: "photo").foregroundStyle(Theme.textSecondary).frame(width: 59, height: 110)
                        } else {
                            artView(fixture.arts[channel], height: 110)
                        }
                        VStack(alignment: .leading, spacing: 10) {
                            HStack(spacing: 4) {
                                Text("Flavor \(channel + 1)").font(.headline)
                                Spacer(minLength: 0)
                                Image(systemName: "chevron.right").font(.caption.weight(.semibold))
                            }
                            Text(route == .unread ? "—" : "1:\(fixture.ratios[channel])").font(.title3.weight(.medium).monospacedDigit())
                            gauge(level, unknown: route == .unread)
                            Text(route == .unread ? "Unknown" : "\(level == 3 ? "High" : "Low")\(active ? " · On tap" : "")")
                                .font(.caption).foregroundStyle(active ? Theme.accent : Theme.textSecondary)
                        }
                    }
                } else {
                    VStack(alignment: .leading, spacing: 14) {
                        HStack {
                            Text("Flavor \(channel + 1)").font(.subheadline.weight(.semibold))
                            Spacer(minLength: 2)
                            Image(systemName: "chevron.right").font(.caption.weight(.semibold))
                        }
                        Group {
                            if route == .unread {
                                Image(systemName: "photo").font(.title).foregroundStyle(Theme.textSecondary)
                                    .frame(height: artHeight).frame(maxWidth: .infinity)
                            } else {
                                artView(fixture.arts[channel], height: artHeight).frame(maxWidth: .infinity)
                            }
                        }.padding(.vertical, 4)
                        HStack {
                            if active {
                                Label("On tap", systemImage: "checkmark.circle.fill").font(.caption2.weight(.medium)).foregroundStyle(Theme.accent)
                            }
                            Spacer(minLength: 0)
                            Text(route == .unread ? "—" : "1:\(fixture.ratios[channel])").font(.subheadline.weight(.medium).monospacedDigit())
                        }
                        gauge(level, unknown: route == .unread)
                        HStack {
                            Text("Reservoir").font(.caption).foregroundStyle(Theme.textSecondary)
                            Spacer(minLength: 2)
                            Text(route == .unread ? "—" : level == 3 ? "High" : "Low").font(.caption.weight(.medium))
                        }
                    }
                }
            }.padding(16).frame(maxWidth: .infinity, alignment: .leading)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 18))
                .overlay(RoundedRectangle(cornerRadius: 18).strokeBorder(active ? Theme.accent.opacity(0.7) : Theme.ice.opacity(0.08), lineWidth: active ? 1.25 : 0.5))
        }.buttonStyle(.plain)
    }
    private var machineStatus: some View {
        VStack(alignment: .leading, spacing: 12) {
            section("Status")
            panel {
                HStack {
                    Image(systemName: "thermometer.low").foregroundStyle(Theme.textSecondary)
                    Text("Tank wall").font(.subheadline)
                    Spacer()
                    Text(route == .unread ? "—" : "36°F").font(.title3.weight(.medium).monospacedDigit())
                }
                Divider().overlay(Theme.ice.opacity(0.2))
                Label(route == .unread ? "Waiting for a reading" : "Cooling", systemImage: "snowflake").font(.subheadline)
                Label(route == .unread ? "Water level unknown" : "Water level high", systemImage: "drop").font(.subheadline)
                if disconnected { note("As of 10 min ago") }
            }
        }
    }

    private func flavor(width: CGFloat) -> some View {
        let wide = width >= 600 && !typeSize.isAccessibilitySize
        return FlexibleColumns(wide: wide, spacing: 24) {
            VStack(spacing: 12) {
                if wide {
                    artView(art, height: 240)
                    Button("Change image") { go(.images) }.font(.subheadline.weight(.medium)).frame(minHeight: 44)
                } else {
                    HStack(spacing: 20) {
                        artView(art, height: 132)
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Display image").font(.headline)
                            note("Shown on both machine displays.")
                            Button("Change image") { go(.images) }.font(.subheadline.weight(.medium)).frame(minHeight: 44)
                        }
                    }.frame(maxWidth: .infinity, alignment: .leading)
                }
            }.frame(maxWidth: .infinity)
        } right: {
            VStack(alignment: .leading, spacing: 16) {
                panel {
                    HStack {
                        Text("Mix ratio").font(.headline)
                        Spacer()
                        if fixture.draftRatio == fixture.ratios[fixture.selectedChannel] {
                            Label("Saved", systemImage: "checkmark").font(.caption).foregroundStyle(Theme.textSecondary)
                        } else {
                            Button("Save") { fixture.saveRatio() }.font(.subheadline.weight(.semibold)).disabled(disconnected)
                        }
                    }
                    HStack(spacing: 18) {
                        Button { ratio = max(6, ratio - 1) } label: { Image(systemName: "minus").frame(width: 44, height: 44).background(Theme.ice.opacity(0.10), in: Circle()) }
                            .accessibilityLabel("Stronger mix")
                        Text("1:\(ratio)").font(.largeTitle.weight(.medium).monospacedDigit()).frame(maxWidth: .infinity)
                        Button { ratio = min(24, ratio + 1) } label: { Image(systemName: "plus").frame(width: 44, height: 44).background(Theme.ice.opacity(0.10), in: Circle()) }
                            .accessibilityLabel("Lighter mix")
                    }.disabled(disconnected)
                    Text("1 part concentrate · \(ratio) parts water").font(.subheadline).foregroundStyle(Theme.textSecondary)
                    HStack { Text("More flavor"); Spacer(); Text("Lighter") }.font(.caption).foregroundStyle(Theme.textSecondary)
                    Text("1:6–1:24 · Match your concentrate bottle.").font(.caption).foregroundStyle(Theme.textSecondary)
                }
                if fixture.activeFlavor == fixture.selectedChannel {
                    Label("On tap at the faucet", systemImage: "checkmark.circle.fill")
                        .font(.subheadline).foregroundStyle(Theme.accent).padding(.vertical, 4)
                } else {
                    action("Use at faucet", next: .home, perform: { fixture.selectFlavorAtFaucet() }).disabled(disconnected)
                }
            }.frame(maxWidth: .infinity)
        }
    }

    private func imagePicker(width: CGFloat) -> some View {
        let room = min(560, width)
        let columns = max(1, Int((room + 12) / 84))
        let tileWidth = min(112, (room - CGFloat(columns - 1) * 12) / CGFloat(columns))
        let tileHeight = tileWidth * 80 / 43
        return VStack(alignment: .leading, spacing: 20) {
            if route == .imageError { notice("Picture wasn’t sent", "Check your connection and try sending it again.", icon: "exclamationmark.circle") }
            section("Choose an image")
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 12), count: columns), alignment: .leading, spacing: 16) {
                ForEach(0..<4) { index in
                    Button { fixture.selectArt(index); go(.flavor) } label: {
                        VStack(spacing: 8) {
                            artView(index, height: tileHeight)
                                .overlay(alignment: .bottomTrailing) {
                                    if index == art { Image(systemName: "checkmark.circle.fill").symbolRenderingMode(.palette).foregroundStyle(Theme.onAccent, Theme.accent).padding(5) }
                                }
                            Text("Image \(index + 1)").font(.caption)
                        }
                    }.buttonStyle(.plain).disabled(disconnected)
                }
                if route == .uploading {
                    VStack(spacing: 8) {
                        ZStack {
                            artView(2, height: tileHeight).opacity(0.35)
                            VStack(spacing: 10) { ProgressView(value: 0.46).tint(Theme.accent); Text("46%").font(.caption.monospacedDigit()) }.padding(10)
                        }
                        Button("Cancel") { go(.images) }.font(.caption).frame(minHeight: 44)
                    }
                }
                Button { go(.crop) } label: {
                    VStack(spacing: 8) {
                        Image(systemName: "plus").font(.title2).frame(width: tileWidth, height: tileHeight)
                            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 8))
                        Text("Add photo").font(.caption)
                    }
                }.disabled(disconnected)
            }
            note(route == .uploading ? "Sending picture to the machine. You can add another while it sends." : "Four included images. Add up to four of your own.")
            if route == .imageError { action("Try again", next: .uploading).frame(maxWidth: 360) }
        }.frame(maxWidth: room).frame(maxWidth: .infinity, alignment: .leading)
    }
    private func cropEditor(size: CGSize) -> some View {
        let wide = size.width >= 600 || size.height < 350
        let height = max(100, min(wide ? size.height - 48 : size.height - 150, 460))
        return FlexibleColumns(wide: wide, spacing: 28) {
            artView(2, height: height)
                .overlay(Rectangle().strokeBorder(Theme.ice.opacity(0.7), lineWidth: 2))
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } right: {
            VStack(alignment: .leading, spacing: 20) {
                Text("Frame the faucet display").font(.title3.weight(.medium))
                note("Drag to move. Pinch to zoom.")
                note("This same framing is used on both machine displays.")
                action("Use this picture", next: .uploading)
            }.frame(maxWidth: wide ? 320 : 440).frame(maxWidth: .infinity)
        }.padding(24).frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func care(width: CGFloat) -> some View {
        let count = typeSize.isAccessibilitySize ? 1 : width >= 760 ? 3 : width >= 600 ? 2 : 1
        return VStack(alignment: .leading, spacing: 20) {
            note("One flavor at a time.")
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 16, alignment: .top), count: count), alignment: .leading, spacing: 16) {
                careCard("Fill", icon: "arrow.down.to.line", detail: "Add concentrate through the top funnel.", next: .fill)
                careCard("Clean", icon: "sparkles", detail: "Rinse the funnel, reservoir and flavor line.", next: .clean)
                careCard("Prime", icon: "drop", detail: "Bring concentrate to the faucet.", next: .prime)
            }
        }
    }
    private func careCard(_ title: String, icon: String, detail: String, next: StudyRoute) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: icon).font(.title3.weight(.medium))
            note(detail).frame(minHeight: 34, alignment: .topLeading)
            HStack(spacing: 12) {
                action("Flavor 1", primary: false, next: next, forChannel: 0)
                action("Flavor 2", primary: false, next: next, forChannel: 1)
            }.disabled(disconnected)
        }.padding(16).frame(maxWidth: .infinity, alignment: .topLeading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }
    private func preparation(width: CGFloat) -> some View {
        let fill = route == .fill
        let prime = route == .prime
        return FlexibleColumns(wide: width >= 650 && !typeSize.isAccessibilitySize, spacing: 28) {
            VStack(spacing: 14) {
                artView(art, height: 200)
                Text(flavorLabel).font(.headline)
                gauge(3).frame(maxWidth: 140)
            }.frame(maxWidth: .infinity)
        } right: {
            VStack(alignment: .leading, spacing: 20) {
                Text(fill ? "Add concentrate" : prime ? "Continue at the machine" : "Three rinse cycles").font(.title2.weight(.semibold))
                note(fill ? "Pour concentrate into the top funnel." : prime ? "Place a glass under the faucet. Open Prime on the machine, then hold its pad to run the pump. Release to stop." : "Place a pitcher under the faucet. The machine rinses the funnel path, then fills and flushes the reservoir three times.")
                panel {
                    Label(fill ? "Stops when full" : prime ? "Hold on either machine display" : "Water exits at the faucet", systemImage: fill ? "drop.fill" : prime ? "hand.tap" : "arrow.down")
                        .font(.body.weight(.medium))
                    note(fill ? "Filling also ends when the planned run finishes. Concentrate may remain in the funnel if the reservoir fills first." : prime ? "The app follows the same Prime session as both displays." : "Keep the pitcher in place until the cycle ends.")
                }
                action(fill ? "Start filling" : prime ? "Open Prime on machine" : "Start cleaning", next: fill ? .filling : prime ? .priming : .cleanFunnel)
                    .disabled(disconnected)
            }.frame(maxWidth: .infinity)
        }
    }

    private func operation(width: CGFloat) -> some View {
        let fill = route == .filling
        let prime = route == .priming
        return VStack(alignment: .leading, spacing: 24) {
            if route == .lost {
                notice("The cycle may still be running", "The phone cannot confirm its state. Check the machine display. Reconnecting will read its current progress.", icon: "antenna.radiowaves.left.and.right.slash")
            } else if route == .fillStopped {
                notice("Filling stopped", "Concentrate may remain in the funnel. Check the funnel before adding more.", icon: "stop.circle")
                action("Back to Care", next: .care)
            } else if route == .fillFull {
                notice("Reservoir full", "Filling ended because the reservoir is full. Concentrate may remain in the funnel.", icon: "checkmark.circle")
                action("Done", next: .care)
            } else if route == .stopping {
                notice("Stopping cleaning…", "Waiting for the machine to confirm that the pump and valves are stopped.", icon: "hourglass")
            } else if route == .busy {
                notice("Flavor 2 is being filled", "Finish or stop that operation at the machine before starting another.", icon: "hourglass")
                action("Back to Care", next: .care)
            } else if route == .stopped {
                notice("Cleaning stopped", "Water may remain in the reservoir. Keep the pitcher under the faucet and run a complete clean cycle before adding concentrate.", icon: "stop.circle")
                action("Back to Care", next: .care)
            } else if route == .complete {
                notice("\(flavorLabel) is clean", "The funnel path and three rinse cycles are complete.", icon: "checkmark.circle")
                action("Done", next: .care)
            } else {
                FlexibleColumns(wide: width >= 650 && !typeSize.isAccessibilitySize, spacing: 28) {
                    VStack(spacing: 18) {
                        Image(systemName: fill ? "arrow.down.to.line" : prime ? "hand.tap" : "sparkles")
                            .font(.system(size: 52, weight: .light)).foregroundStyle(Theme.accent)
                        Text(fill ? "Filling" : prime ? "Ready to prime" : "Cleaning").font(.title2.weight(.semibold))
                        Text(flavorLabel).foregroundStyle(Theme.textSecondary)
                    }.frame(maxWidth: .infinity).padding(.vertical, 28)
                } right: {
                    VStack(alignment: .leading, spacing: 20) {
                        panel {
                            Text(fill ? "Drawing from the funnel" : prime ? "Hold the pad on the machine" : route == .cleanFunnel ? "Rinsing the funnel path" : "Round 2 of 3 · Flushing").font(.headline)
                            if !prime {
                                ProgressView(value: fill ? 0.4 : 0.6).tint(Theme.accent)
                                note(fill ? "32 s elapsed · up to 80 s" : route == .cleanFunnel ? "Before rinse round 1" : "About 4 min left")
                            }
                            note(prime ? "Either display can run the selected pump. Release the pad to stop. Both displays and this app follow the same session." : "Keep a container under the faucet.")
                        }
                        action(prime ? "Exit Prime" : fill ? "Stop filling" : "Stop cleaning", primary: false, next: prime ? .care : fill ? .fillStopped : .stopping)
                        if !prime { note("The machine reports progress and confirms when it has stopped.") }
                    }.frame(maxWidth: .infinity)
                }
            }
        }.frame(maxWidth: 820).frame(maxWidth: .infinity)
    }

    private func settings(width: CGFloat) -> some View {
        VStack(alignment: .leading, spacing: 28) {
            VStack(alignment: .leading, spacing: 12) {
                section("Your machine")
                groupedPanel {
                    row("Name", detail: fixture.machineName, icon: "pencil", next: .rename)
                    rowDivider
                    row("Sound", icon: "speaker.wave.2", next: .sound)
                    rowDivider
                    row("Software Update", icon: "arrow.down.circle", next: .update)
                }
            }
            VStack(alignment: .leading, spacing: 12) {
                section("This device")
                groupedPanel {
                    row("Your machines", icon: "square.stack", next: .machines)
                }
                Text("Unit \(fixture.unit)").font(.caption).foregroundStyle(Theme.textSecondary).padding(.leading, 4)
            }
        }.frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
    }
    private func sound(width: CGFloat) -> some View {
        VStack(alignment: .leading, spacing: 22) {
            if route == .clock { notice("Quiet hours need the machine clock", "The clock is unavailable. Your schedule is saved, but quiet hours cannot take effect.", icon: "clock.badge.exclamationmark") }
            VStack(alignment: .leading, spacing: 20) {
                panel {
                    HStack { Text("Volume").font(.headline); Spacer(); Text("\(Int(fixture.volume))%").monospacedDigit() }
                    Slider(value: $fixture.volume, in: 0...100, step: 1).accessibilityLabel("Volume")
                    note("Touch sounds and completion chimes.")
                }
                panel {
                    Toggle("Quiet hours", isOn: $fixture.quiet).tint(Theme.accent)
                    HStack {
                        Text("From"); Spacer()
                        Picker("From", selection: $fixture.startHour) { ForEach(0..<24) { h in Text(hour(h)).tag(h) } }.tint(Theme.ice)
                    }.frame(minHeight: 44)
                    HStack {
                        Text("Until"); Spacer()
                        Picker("Until", selection: $fixture.endHour) { ForEach(0..<24) { h in Text(hour(h)).tag(h) } }.tint(Theme.ice)
                    }.frame(minHeight: 44)
                    HStack { Text("Quiet volume"); Spacer(); Text("\(Int(fixture.quietVolume))%").monospacedDigit() }
                    Slider(value: $fixture.quietVolume, in: 0...100, step: 1).accessibilityLabel("Quiet volume")
                }
            }.disabled(disconnected)
            note("The gas alarm always sounds at full volume.")
            action("Save sound settings", next: .settings).frame(maxWidth: 440)
                .disabled(disconnected)
        }.frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
    }
    private func hour(_ h: Int) -> String { "\(h % 12 == 0 ? 12 : h % 12) \(h < 12 ? "AM" : "PM")" }
    private func software(width: CGFloat) -> some View {
        VStack(alignment: .center, spacing: 24) {
            Image(systemName: route == .current ? "checkmark.circle" : "arrow.down.circle")
                .font(.system(size: 56, weight: .light)).foregroundStyle(Theme.accent).padding(.top, 24)
            Text(softwareTitle)
                .font(.title2.weight(.semibold)).multilineTextAlignment(.center)
            if route == .updateError {
                notice("Couldn’t check for updates", "Connect this device to the internet and try again.", icon: "exclamationmark.circle")
                action("Try again", next: .update)
            } else if route == .restarting || route == .verifying {
                ProgressView().tint(Theme.accent)
                note(route == .restarting ? "Restarting the machine. Keep it plugged in." : "Checking the software the machine is running. Waiting for every part to answer.")
            } else if route == .updating {
                ProgressView(value: 0.64).tint(Theme.accent)
                Text("64%").font(.title3.monospacedDigit())
                note("Sending software").multilineTextAlignment(.center)
                note("Keep your device near the machine. Do not unplug it.")
                action("Cancel update", primary: false, next: .update)
            } else if route == .current {
                note("All parts of the machine report the published software.")
                action("Check again", primary: false, next: .current)
            } else {
                note("This usually takes a few minutes. Keep your device near the machine and leave the machine plugged in.")
                action("Update now", next: .updating).disabled(disconnected)
            }
        }.frame(maxWidth: 460).frame(maxWidth: .infinity).padding(.vertical, 20)
    }
    private var softwareTitle: String {
        switch route {
        case .updating: "Updating your machine"
        case .current: "Your machine is up to date"
        case .updateError: "Check for an update"
        case .restarting: "Restarting your machine"
        case .verifying: "Checking your machine"
        default: "An update is ready"
        }
    }
    private var machines: some View {
        VStack(alignment: .leading, spacing: 20) {
            groupedPanel {
                ForEach(0..<fixture.names.count, id: \.self) { index in
                    Button {
                        fixture.selectMachine(index)
                        go(fixture.isConnected ? .home : .offline)
                    } label: {
                        HStack(spacing: 12) {
                            VStack(alignment: .leading, spacing: 6) {
                                Text(fixture.names[index]).font(.body.weight(.medium))
                                Text(index == fixture.selectedMachine ? "Unit \(fixture.unit) · \(linkText)" : index == 0 ? "Unit A1B2C3 · In range" : "Unit D4E5F6 · Last connected yesterday")
                                    .font(.caption).foregroundStyle(Theme.textSecondary)
                            }
                            Spacer()
                            if index == fixture.selectedMachine {
                                Image(systemName: "checkmark").font(.body.weight(.semibold)).foregroundStyle(Theme.accent)
                            }
                        }.padding(.vertical, 16)
                    }.buttonStyle(.plain)
                    if index == 0 { Theme.ice.opacity(0.12).frame(height: 0.5) }
                }
            }
            action("Add a machine", primary: false, next: .add)
            note("A machine’s name is shared by every device that connects to it.")
            Button("Remove \(fixture.machineName) from this device") { go(.add) }.font(.subheadline).foregroundStyle(Theme.error).frame(minHeight: 44)
        }.frame(maxWidth: 560).frame(maxWidth: .infinity)
    }
    private var rename: some View {
        VStack(alignment: .leading, spacing: 20) {
            TextField("Name", text: $fixture.draftName).textInputAutocapitalization(.words).autocorrectionDisabled()
                .padding(16).background(Theme.surface, in: RoundedRectangle(cornerRadius: 12))
            note("Up to twenty letters. The machine keeps its name so every device sees the same one.")
            action("Save name", next: .settings, perform: { fixture.saveName() }).disabled(disconnected)
        }.frame(maxWidth: 460).frame(maxWidth: .infinity)
    }
    private func onboarding(width: CGFloat) -> some View {
        FlexibleColumns(wide: width >= 650 && !typeSize.isAccessibilitySize, spacing: 36) {
            VStack(spacing: 20) {
                Image("LaunchIcon").resizable().scaledToFit().frame(width: 160, height: 160).accessibilityHidden(true)
                Text("Soda Machine").font(.largeTitle.weight(.semibold))
            }.frame(maxWidth: .infinity).padding(.vertical, 32)
        } right: {
            VStack(alignment: .leading, spacing: 24) {
                Text("Make it yours").font(.title2.weight(.semibold))
                note("Choose your flavor images, care for your machine, and keep it up to date.")
                action("Find your machine", next: .home)
                note("Hold your device right next to the faucet. Choose your machine in Apple’s nearby accessory sheet.")
                Button("Try the demo") { go(.home) }.font(.body.weight(.medium)).frame(minHeight: 44)
            }.frame(maxWidth: 420).frame(maxWidth: .infinity)
        }.padding(.vertical, 20)
    }
}

private struct FlexibleColumns<Left: View, Right: View>: View {
    let wide: Bool
    let spacing: CGFloat
    @ViewBuilder let left: () -> Left
    @ViewBuilder let right: () -> Right
    var body: some View {
        if wide {
            HStack(alignment: .top, spacing: spacing) { left(); right() }
        } else {
            VStack(alignment: .leading, spacing: spacing) { left(); right() }
        }
    }
}
