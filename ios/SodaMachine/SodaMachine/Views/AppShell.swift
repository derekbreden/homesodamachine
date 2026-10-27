import SwiftUI

// ────────────────────────────────────────────────────────────
// What the app opens on, at every size.
//
// Three destinations — Machine, Care and Settings — in a bar along the bottom
// of a narrow window, and in a sidebar beside the pages once the window is a
// thousand points wide. The tab and each tab's stack of pages live in
// Navigator, above the layout. The machine and whether the phone can hear it
// sit in the header of a narrow window and in the sidebar of a wide one.
// ────────────────────────────────────────────────────────────

enum AppTab: String, CaseIterable {
    case machine, care, settings

    var title: String {
        switch self {
        case .machine: "Machine"
        case .care: "Care"
        case .settings: "Settings"
        }
    }

    var icon: String {
        switch self {
        case .machine: "drop"
        case .care: "sparkles"
        case .settings: "slider.horizontal.3"
        }
    }
}

enum AppRoute: Hashable {
    case flavor(Int)
    case images(Int)
    case fill(Int)
    case clean(Int)
    case prime(Int)
    case sound
    case update
    case machines
    case rename
}

/// Where someone is: a tab, and a stack of pages on each.
@Observable
final class Navigator {
    var tab = AppTab.machine
    private var stacks: [AppTab: [AppRoute]] = [:]
    /// A run on the machine that this screen is minding: the tabs, the back
    /// button and the machine switcher wait for it.
    var locked = false

    var path: [AppRoute] { stacks[tab] ?? [] }
    var top: AppRoute? { path.last }

    func push(_ route: AppRoute) {
        guard !locked else { return }
        stacks[tab, default: []].append(route)
    }

    func back() {
        guard !locked else { return }
        _ = stacks[tab]?.popLast()
    }

    /// A tab chosen again goes back to its top.
    func select(_ next: AppTab) {
        guard !locked else { return }
        if next == tab { stacks[next] = [] } else { tab = next }
    }

    /// One page on a tab, from anywhere.
    func open(_ route: AppRoute, on tab: AppTab) {
        self.tab = tab
        stacks[tab] = [route]
    }

    /// The Machine tab, every tab back to its top, unlocked.
    func reset() {
        tab = .machine
        stacks = [:]
        locked = false
    }
}

struct RootView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @State private var nav = Navigator()

    var body: some View {
        Group {
            if let machine = directory.current {
                if !machine.supported {
                    UnsupportedMachineView(machine: machine)
                } else {
                    AppShell()
                }
            } else {
                FirstRunView()
            }
        }
        .environment(nav)
        .onChange(of: directory.current?.id) { nav.reset() }
        .onAppear {
            // A phone pointed at a machine turns toward it as soon as the
            // system has said which machines it may reach. The radio comes up
            // only for a machine that needs it: a phone with none, or with only
            // the demo, leaves the looking to the system's sheet.
            ble.activateBluetooth()
        }
    }
}

struct AppShell: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    @Environment(\.dynamicTypeSize) private var typeSize

    var body: some View {
        GeometryReader { geo in
            let sidebar = geo.size.width >= 1000 && !typeSize.isAccessibilitySize
            let pageWidth = min(840, geo.size.width - (sidebar ? 216 : 0) - 48)
            HStack(spacing: 0) {
                if sidebar { SideNavigation() }
                VStack(spacing: 0) {
                    PageHeader(sidebar: sidebar, width: pageWidth)
                    ScrollView {
                        page(width: pageWidth, height: geo.size.height)
                            .frame(maxWidth: pageWidth)
                            .frame(maxWidth: .infinity, alignment: .top)
                            .padding(.horizontal, 24)
                            .padding(.top, 20)
                            .padding(.bottom, 24)
                    }
                    .scrollIndicators(.automatic)
                    if !sidebar { BottomNavigation() }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .background(Theme.background.ignoresSafeArea())
        .foregroundStyle(Theme.textPrimary)
        .tint(Theme.accent)
        .font(.body)
    }

    @ViewBuilder private func page(width: CGFloat, height: CGFloat) -> some View {
        switch nav.top {
        case nil:
            switch nav.tab {
            case .machine: MachineHomeView(width: width, height: height)
            case .care: CareHomeView(width: width)
            case .settings: SettingsHomeView()
            }
        case .flavor(let ch): FlavorDetailView(channel: ch, width: width)
        case .images(let ch): ImageLibraryView(channel: ch, width: width)
        case .fill(let ch): FillView(channel: ch, width: width)
        case .clean(let ch): CleanView(channel: ch, width: width)
        case .prime(let ch): PrimeView(channel: ch, width: width)
        case .sound: SoundView()
        case .update: SoftwareUpdateView()
        case .machines: MachinesView()
        case .rename: RenameView()
        }
    }
}

// ── The header, the bar, the sidebar ─────────────────────────────────────

/// What the page is, and which machine. A top page leads with its title, and
/// the Machine page with the machine itself; a page further in leads with a
/// way back.
struct PageHeader: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    let sidebar: Bool
    let width: CGFloat

    private var isTop: Bool { nav.top == nil }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                if !isTop && !nav.locked {
                    Button { nav.back() } label: {
                        Image(systemName: "chevron.left").font(.body.weight(.medium))
                            .frame(width: 32, height: 44, alignment: .leading)
                    }
                    .accessibilityLabel("Back")
                }
                if isTop && nav.tab == .machine && !sidebar {
                    Button { nav.open(.machines, on: .settings) } label: {
                        HStack(spacing: 9) {
                            Text(ble.current?.displayName ?? "").font(.largeTitle.weight(.semibold))
                            Image(systemName: "chevron.down").font(.caption.weight(.semibold))
                                .foregroundStyle(Theme.textSecondary)
                        }
                    }
                    .buttonStyle(.plain)
                    .disabled(nav.locked)
                    .accessibilityHint("Your machines")
                } else {
                    Text(title)
                        .font(isTop ? .largeTitle.weight(.semibold) : .headline)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 8)
                if isTop && nav.tab != .machine && !sidebar {
                    Button { nav.open(.machines, on: .settings) } label: {
                        HStack(spacing: 6) {
                            Text(ble.current?.displayName ?? "")
                            Image(systemName: "chevron.down").font(.caption2)
                        }
                        .font(.subheadline.weight(.medium)).foregroundStyle(Theme.textSecondary)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.ice.opacity(0.08), in: Capsule())
                    }
                    .buttonStyle(.plain)
                    .disabled(nav.locked)
                }
            }
            if !sidebar {
                HStack(spacing: 6) {
                    Circle().fill(ble.linked ? Theme.ice : Theme.textSecondary.opacity(0.5)).frame(width: 5, height: 5)
                    Text(isTop ? linkText : "\(ble.current?.displayName ?? "") · \(linkText)")
                }
                .font(.caption)
                .foregroundStyle(Theme.textSecondary)
                .accessibilityElement(children: .combine)
                .accessibilityAddTraits(.updatesFrequently)
            }
        }
        .frame(maxWidth: width).frame(maxWidth: .infinity)
        .padding(.horizontal, 24)
        .padding(.top, isTop ? 24 : 10)
        .padding(.bottom, isTop ? 8 : 6)
        .background(Theme.background)
    }

    private var title: String {
        switch nav.top {
        case nil: nav.tab.title
        case .flavor(let ch): "Flavor \(ch + 1)"
        case .images(let ch): "Flavor \(ch + 1) image"
        case .fill(let ch): "Fill Flavor \(ch + 1)"
        case .clean(let ch): "Clean Flavor \(ch + 1)"
        case .prime(let ch): "Prime Flavor \(ch + 1)"
        case .sound: "Sound"
        case .update: "Software Update"
        case .machines: "Your machines"
        case .rename: "Machine name"
        }
    }

    private var linkText: String { ble.linkText }
}

struct BottomNavigation: View {
    @Environment(Navigator.self) var nav

    var body: some View {
        HStack(spacing: 4) {
            ForEach(AppTab.allCases, id: \.self) { tab in
                let selected = nav.tab == tab
                Button { nav.select(tab) } label: {
                    VStack(spacing: 5) {
                        Image(systemName: tab == .machine && selected ? "drop.fill" : tab.icon)
                            .font(.system(size: 20, weight: .regular))
                        Text(tab.title).font(.caption2.weight(selected ? .semibold : .regular))
                    }
                    .foregroundStyle(selected ? Theme.accent : Theme.textSecondary)
                    .frame(maxWidth: .infinity, minHeight: 48)
                }
                .disabled(nav.locked)
                .accessibilityAddTraits(selected ? .isSelected : [])
            }
        }
        .frame(maxWidth: 480).frame(maxWidth: .infinity)
        .padding(.horizontal, 16).padding(.top, 8).padding(.bottom, 8)
        .background(Theme.surface.ignoresSafeArea(edges: .bottom))
        .overlay(alignment: .top) { Theme.ice.opacity(0.10).frame(height: 0.5) }
    }
}

struct SideNavigation: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 10) {
                Image("LaunchIcon").resizable().scaledToFit().frame(width: 32, height: 32).accessibilityHidden(true)
                Text("Soda Machine").font(.subheadline.weight(.semibold))
            }
            .padding(.bottom, 24)
            Button { nav.open(.machines, on: .settings) } label: {
                HStack {
                    VStack(alignment: .leading, spacing: 5) {
                        Text(ble.current?.displayName ?? "").font(.headline)
                        Text(ble.linkText).font(.caption).foregroundStyle(Theme.textSecondary)
                    }
                    Spacer(minLength: 6)
                    Image(systemName: "chevron.down").font(.caption2)
                }
                .padding(12)
                .background(Theme.background, in: RoundedRectangle(cornerRadius: 12))
            }
            .buttonStyle(.plain)
            .disabled(nav.locked)
            .padding(.bottom, 20)
            ForEach(AppTab.allCases, id: \.self) { tab in
                let selected = nav.tab == tab
                Button { nav.select(tab) } label: {
                    Label(tab.title, systemImage: tab.icon)
                        .font(.subheadline.weight(.medium)).frame(maxWidth: .infinity, alignment: .leading)
                        .padding(12)
                        .foregroundStyle(selected ? Theme.accent : Theme.textSecondary)
                        .background(selected ? Theme.ice.opacity(0.08) : Color.clear, in: RoundedRectangle(cornerRadius: 10))
                }
                .disabled(nav.locked)
                .accessibilityAddTraits(selected ? .isSelected : [])
            }
            Spacer(minLength: 32)
            Button { nav.open(.machines, on: .settings) } label: {
                Label("Your machines", systemImage: "square.stack").frame(minHeight: 44)
            }
            .foregroundStyle(Theme.textSecondary)
            .disabled(nav.locked)
        }
        .padding(20)
        .frame(width: 216)
        .frame(maxHeight: .infinity, alignment: .top)
        .background(Theme.surface.ignoresSafeArea())
    }
}

extension BLEManager {
    /// Whether the phone can hear the machine, and if not, since when.
    var linkText: String {
        guard let m = current else { return "" }
        if m.isDemo { return "Demo" }
        switch connectionState {
        case .connected: return "Connected"
        case .connecting: return "Connecting…"
        case .bluetoothOff: return "Bluetooth is off"
        case .searching: return "Looking for it…"
        case .searchingLong:
            if let t = m.lastConnected { return "Out of range · last connected \(said(t))" }
            return "Out of range"
        }
    }
}

/// When something was read, the way a person says it: relative within the
/// day, dated past it.
func said(_ date: Date) -> String {
    if Date().timeIntervalSince(date) < 24 * 3600 {
        return date.formatted(.relative(presentation: .named))
    }
    return date.formatted(date: .abbreviated, time: .shortened)
}

// ── What every page is built from ────────────────────────────────────────

struct SectionTitle: View {
    let text: String
    init(_ text: String) { self.text = text }
    var body: some View {
        Text(text).font(.subheadline.weight(.medium)).foregroundStyle(Theme.textSecondary)
            .frame(maxWidth: .infinity, alignment: .leading)
            .accessibilityAddTraits(.isHeader)
    }
}

struct Note: View {
    let text: String
    init(_ text: String) { self.text = text }
    var body: some View {
        Text(text).font(.subheadline).foregroundStyle(Theme.textSecondary)
            .fixedSize(horizontal: false, vertical: true)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct Panel<Content: View>: View {
    @ViewBuilder let content: () -> Content
    var body: some View {
        VStack(alignment: .leading, spacing: 16, content: content).padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }
}

/// The page's one commitment, or a quieter way out of it.
struct ActionButton: View {
    let title: String
    var primary = true
    var working = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            ZStack {
                Text(title).opacity(working ? 0 : 1)
                if working { ProgressView().tint(primary ? Theme.onAccent : Theme.textPrimary) }
            }
            .font(.body.weight(.semibold)).multilineTextAlignment(.center)
            .frame(maxWidth: .infinity, minHeight: 48)
            .foregroundStyle(primary ? Theme.onAccent : Theme.textPrimary)
            .background(primary ? Theme.accent : Theme.ice.opacity(0.12), in: RoundedRectangle(cornerRadius: 12))
        }
        .buttonStyle(.plain)
        .accessibilityLabel(title)
    }
}

struct SettingsRow: View {
    let title: String
    var detail: String?
    var icon: String?
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                if let icon { Image(systemName: icon).frame(width: 24).foregroundStyle(Theme.textSecondary) }
                Text(title).font(.body)
                Spacer(minLength: 12)
                if let detail { Text(detail).font(.subheadline).foregroundStyle(Theme.textSecondary) }
                Image(systemName: "chevron.right").font(.caption.weight(.semibold)).foregroundStyle(Theme.textSecondary)
            }
            .frame(minHeight: 52)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}

struct GroupedPanel<Content: View>: View {
    @ViewBuilder let content: () -> Content
    var body: some View {
        VStack(spacing: 0, content: content).padding(.horizontal, 16).padding(.vertical, 4)
            .frame(maxWidth: .infinity)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
    }
}

struct RowDivider: View {
    var inset: CGFloat = 36
    var body: some View { Theme.ice.opacity(0.12).frame(height: 0.5).padding(.leading, inset) }
}

/// A condition worth stopping for: what it is, and what to do about it.
struct Notice: View {
    let title: String
    let message: String
    var icon = "info.circle"
    var urgent = false

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon).foregroundStyle(urgent ? Theme.error : Theme.accent)
            VStack(alignment: .leading, spacing: 5) {
                Text(title).font(.body.weight(.semibold))
                Note(message)
            }
        }
        .padding(16).frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
        .accessibilityElement(children: .combine)
    }
}

/// A reservoir's four segments, from the machine's reed column.
struct LevelGauge: View {
    let level: Int?

    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<MachineStatus.segments, id: \.self) { i in
                Capsule().fill(level.map { i < $0 } == true ? Theme.ice : Theme.ice.opacity(0.18)).frame(height: 5)
            }
        }
        .accessibilityElement()
        .accessibilityLabel(level.map { "Reservoir \(Self.word($0).lowercased()), \($0) of 4" } ?? "Reservoir level unknown")
    }

    static func word(_ level: Int) -> String {
        switch level {
        case ...0: "Empty"
        case 1: "Low"
        case 2: "Half"
        case 3: "High"
        default: "Full"
        }
    }
}

/// A flavor's face, in the 43:80 shape both machine displays wear it in.
struct FlavorArtView: View {
    @Environment(BLEManager.self) var ble
    let art: Int
    let height: CGFloat

    var body: some View {
        Group {
            if let image = ble.picture(art: art) {
                Image(uiImage: image).resizable().scaledToFill()
            } else {
                ZStack {
                    Theme.placeholder
                    Image(systemName: "photo").foregroundStyle(Theme.textSecondary)
                }
            }
        }
        .frame(width: height * 43 / 80, height: height)
        .clipped()
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .accessibilityLabel(art < ble.flavorArt.factory ? "Image \(art + 1)" : "Your picture")
    }
}

extension BLEManager {
    /// A face by its art index: one of the four this app ships with, or one of
    /// the machine's own pictures as this phone holds it.
    func picture(art: Int) -> UIImage? {
        if art < flavorArt.factory { return UIImage(named: "flavor_\(art + 1)") }
        guard let slot = flavorArt.customSlot(art: art) else { return nil }
        return faces[imageSlots.crc(of: slot)]
    }
}

struct FlexibleColumns<Left: View, Right: View>: View {
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
