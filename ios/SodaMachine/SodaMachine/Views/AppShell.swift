import SwiftUI

// ────────────────────────────────────────────────────────────
// What the app opens on, at every size.
//
// Three destinations — Machine, Care and Settings — each its own stack of
// pages, in the system's tab bar: along the bottom of an iPhone, and on an
// iPad at the top or as a sidebar, as the person chooses. The stacks and the
// drafts live above the layout, so a window that changes shape keeps where
// someone is and what they were changing. A top page leads with the app's own
// header; a page opened from it has the system's Back and edge swipe.
//
// Your machines belongs to the device, not to a machine: it opens over
// whatever is showing, whether or not a machine is in use.
// ────────────────────────────────────────────────────────────

struct RootView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(MachineAccess.self) var access
    @State private var nav = Navigator()
    @State private var edits = EditSessions()
    @State private var runs = RunLog()

    var body: some View {
        Group {
            if let machine = directory.current {
                if !machine.supported {
                    UnsupportedMachineView(machine: machine)
                } else {
                    AppShell()
                }
            } else if directory.known.isEmpty {
                FirstRunView()
            } else {
                ChooseMachineView()
            }
        }
        .sheet(isPresented: Binding(get: { nav.managing }, set: { nav.managing = $0 })) { MachinesSheet() }
        .onChange(of: directory.current?.id) { nav.reset() }
        // A machine added from anywhere opens, even one already in use; Your
        // machines closes over it.
        .onChange(of: access.added) {
            nav.managing = false
            nav.reset()
        }
        // Every reading reaches the runs a page has opened, whether or not
        // that page is still up.
        .onChange(of: ble.appliance) { _, now in
            if let id = ble.current?.id { runs.observe(machine: id, appliance: now) }
        }
        .onChange(of: ble.linked) { _, up in
            if !up, let id = ble.current?.id { runs.lostLink(machine: id) }
        }
        // One rule holds navigation, wherever the run is shown from.
        .onChange(of: holding, initial: true) { _, now in nav.locked = now }
        // The one place an operation that hasn't ended is asked about, every
        // two seconds, whichever page is up: its progress, its ending, or what
        // an unanswered start did, all reach the runs through `observe`.
        .task(id: outstanding) {
            let kinds = outstanding
            guard !kinds.isEmpty else { return }
            while !Task.isCancelled {
                if kinds.contains(.fill) { await ble.readFill() }
                if kinds.contains(.clean) { await ble.readClean() }
                if kinds.contains(.prime) { await ble.readPrime() }
                try? await Task.sleep(for: .seconds(2))
            }
        }
        // A machine gone from this device, by any path, takes its drafts and
        // runs with it, so no late answer can bring them back.
        .onChange(of: directory.known.map(\.id)) { before, after in
            for id in Set(before).subtracting(after) {
                edits.forget(machine: id)
                runs.forget(machine: id)
                ble.forgetUploads(machine: id)
            }
        }
        .onAppear {
            // A phone pointed at a machine turns toward it as soon as the
            // system has said which machines it may reach. The radio comes up
            // only for a machine that needs it: a phone with none, or with only
            // the demo, leaves the looking to the system's sheet.
            ble.activateBluetooth()
        }
        .environment(nav)
        .environment(edits)
        .environment(runs)
    }
}

extension RootView {
    /// The page in front is minding what it shows: a run this phone started
    /// and can hear, or an update under way. Elsewhere nothing is held, so the
    /// way back to that page is always open.
    fileprivate var holding: Bool {
        guard let id = ble.current?.id, let route = nav.top?.route else { return false }
        let hearing = ble.linked || ble.demoMode
        switch route {
        case .fill(let ch): return hearing && runs.minding(RunLog.Key(machine: id, kind: .fill, channel: ch))
        case .clean(let ch): return hearing && runs.minding(RunLog.Key(machine: id, kind: .clean, channel: ch))
        case .update: return ble.updateRunning
        default: return false
        }
    }

    /// Operations that haven't ended, or whose start went unanswered, that the
    /// machine can be asked about now.
    fileprivate var outstanding: Set<RunLog.Kind> {
        ble.canChange ? runs.outstanding(machine: ble.current?.id) : []
    }
}

extension EnvironmentValues {
    /// The window's height, which decides how much of a page fits on one screen.
    @Entry var windowHeight: CGFloat = 800
}

struct AppShell: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav

    var body: some View {
        GeometryReader { geo in
            tabs
            .tabViewStyle(.sidebarAdaptable)
            .tabViewSidebarBottomBar {
                Button { nav.managing = true } label: {
                    Label("Your machines", systemImage: "square.stack").frame(minHeight: 44)
                }
                .disabled(nav.locked)
            }
            .environment(\.windowHeight, geo.size.height)
        }
        .tint(Theme.accent)
        .overlay {
            if let ask = ble.trustAsk, !ask.quiet { TrustAskOverlay(ask: ask) }
        }
    }
}

extension AppShell {
    /// The three destinations. While a page minds a run, the others can't be
    /// chosen; a system without disabled tabs refuses the choice instead.
    @ViewBuilder fileprivate var tabs: some View {
        let selection = Binding(get: { nav.tab }, set: { nav.select($0) })
        if #available(iOS 18.4, *) {
            TabView(selection: selection) {
                Tab(AppTab.machine.title, systemImage: AppTab.machine.icon, value: AppTab.machine) {
                    TabStack(tab: .machine)
                }
                .disabled(nav.locked && nav.tab != .machine)
                Tab(AppTab.care.title, systemImage: AppTab.care.icon, value: AppTab.care) {
                    TabStack(tab: .care)
                }
                .disabled(nav.locked && nav.tab != .care)
                Tab(AppTab.settings.title, systemImage: AppTab.settings.icon, value: AppTab.settings) {
                    TabStack(tab: .settings)
                }
                .disabled(nav.locked && nav.tab != .settings)
            }
        } else {
            TabView(selection: selection) {
                Tab(AppTab.machine.title, systemImage: AppTab.machine.icon, value: AppTab.machine) {
                    TabStack(tab: .machine)
                }
                Tab(AppTab.care.title, systemImage: AppTab.care.icon, value: AppTab.care) {
                    TabStack(tab: .care)
                }
                Tab(AppTab.settings.title, systemImage: AppTab.settings.icon, value: AppTab.settings) {
                    TabStack(tab: .settings)
                }
            }
        }
    }
}

// ── A destination's pages ────────────────────────────────────────────────

/// One destination: its top page under the app's header, and the pages opened
/// from it, each with the system's Back and edge swipe — both of which wait,
/// like everything else, while a page minds a run.
struct TabStack: View {
    @Environment(Navigator.self) var nav
    let tab: AppTab

    var body: some View {
        NavigationStack(path: Binding(get: { nav.path(on: tab) }, set: { nav.setPath($0, on: tab) })) {
            TopPage(tab: tab)
                .toolbar(.hidden, for: .navigationBar)
                .navigationDestination(for: RouteEntry.self) { entry in RoutePage(entry: entry) }
        }
        .foregroundStyle(Theme.textPrimary)
        .font(.body)
    }
}

/// A page's own scrolling region: a column at most 840 wide, centered.
struct PageScroll<Content: View>: View {
    @Environment(\.windowHeight) private var windowHeight
    @ViewBuilder let content: (_ width: CGFloat, _ windowHeight: CGFloat) -> Content

    var body: some View {
        GeometryReader { geo in
            let width = min(840, geo.size.width - 48)
            ScrollView {
                content(width, windowHeight)
                    .frame(maxWidth: width)
                    .frame(maxWidth: .infinity, alignment: .top)
                    .padding(.horizontal, 24)
                    .padding(.top, 20)
                    .padding(.bottom, 24)
            }
            .scrollIndicators(.automatic)
        }
        .background(Theme.background.ignoresSafeArea())
    }
}

struct TopPage: View {
    let tab: AppTab

    var body: some View {
        GeometryReader { geo in
            VStack(spacing: 0) {
                TopHeader(tab: tab, width: min(840, geo.size.width - 48))
                PageScroll { width, windowHeight in
                    switch tab {
                    case .machine: MachineHomeView(width: width, height: windowHeight)
                    case .care: CareHomeView(width: width)
                    case .settings: SettingsHomeView()
                    }
                }
            }
        }
        .background(Theme.background.ignoresSafeArea())
    }
}

struct RoutePage: View {
    @Environment(BLEManager.self) var ble
    @Environment(Navigator.self) var nav
    let entry: RouteEntry

    var body: some View {
        PageScroll { width, _ in
            switch entry.route {
            case .flavor(let ch): FlavorDetailView(channel: ch, width: width, entry: entry)
            case .images(let ch): ImageLibraryView(channel: ch, width: width, entry: entry)
            case .fill(let ch): FillView(channel: ch, width: width, entry: entry)
            case .clean(let ch): CleanView(channel: ch, width: width, entry: entry)
            case .prime(let ch): PrimeView(channel: ch, width: width, entry: entry)
            case .sound: SoundView(entry: entry)
            case .update: SoftwareUpdateView(entry: entry)
            case .rename: RenameView(entry: entry)
            }
        }
        .modifier(PageTitle(title: entry.route.title, subtitle: ble.machineLine))
        .navigationBarBackButtonHidden(nav.locked)
    }
}

/// A page's title in the navigation bar, with the machine and its link under
/// it.
private struct PageTitle: ViewModifier {
    let title: String
    let subtitle: String

    func body(content: Content) -> some View {
        if #available(iOS 26.0, *) {
            content
                .navigationTitle(title)
                .navigationSubtitle(subtitle)
                .navigationBarTitleDisplayMode(.inline)
        } else {
            content
                .navigationTitle(title)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .principal) {
                        VStack(spacing: 1) {
                            Text(title).font(.headline)
                            Text(subtitle).font(.caption).foregroundStyle(Theme.textSecondary)
                        }
                        .accessibilityElement(children: .combine)
                    }
                }
        }
    }
}

extension AppRoute {
    var title: String {
        switch self {
        case .flavor(let ch): "Flavor \(ch + 1)"
        case .images(let ch): "Flavor \(ch + 1) image"
        case .fill(let ch): "Fill Flavor \(ch + 1)"
        case .clean(let ch): "Clean Flavor \(ch + 1)"
        case .prime(let ch): "Prime Flavor \(ch + 1)"
        case .sound: "Sound"
        case .update: "Software Update"
        case .rename: "Machine name"
        }
    }
}

// ── The header ───────────────────────────────────────────────────────────

/// A top page's title, and which machine. The Machine page leads with the
/// machine itself; the others name it beside their title when there is more
/// than one to choose from, and in the line under it when there is not.
struct TopHeader: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    let tab: AppTab
    let width: CGFloat

    var body: some View {
        let several = directory.known.count > 1
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                if tab == .machine {
                    MachineSwitcher { menu in
                        HStack(spacing: 9) {
                            Text(ble.current?.displayName ?? "").font(.largeTitle.weight(.semibold))
                                .foregroundStyle(Theme.textPrimary)
                            if menu {
                                Image(systemName: "chevron.down").font(.caption.weight(.semibold))
                                    .foregroundStyle(Theme.textSecondary)
                            }
                        }
                    }
                } else {
                    Text(tab.title)
                        .font(.largeTitle.weight(.semibold))
                        .fixedSize(horizontal: false, vertical: true)
                        .accessibilityAddTraits(.isHeader)
                }
                Spacer(minLength: 8)
                if tab != .machine && several {
                    MachineSwitcher { _ in
                        HStack(spacing: 6) {
                            Text(ble.current?.displayName ?? "")
                            Image(systemName: "chevron.down").font(.caption2)
                        }
                        .font(.subheadline.weight(.medium)).foregroundStyle(Theme.textSecondary)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.ice.opacity(0.08), in: Capsule())
                    }
                }
            }
            HStack(spacing: 6) {
                Circle().fill(ble.linked ? Theme.ice : Theme.textSecondary.opacity(0.5)).frame(width: 5, height: 5)
                Text(tab == .machine || several ? ble.linkText : ble.machineLine)
            }
            .font(.caption)
            .foregroundStyle(Theme.textSecondary)
            .accessibilityElement(children: .combine)
            .accessibilityAddTraits(.updatesFrequently)
        }
        .frame(maxWidth: width).frame(maxWidth: .infinity)
        .padding(.horizontal, 24)
        .padding(.top, 24)
        .padding(.bottom, 8)
        .background(Theme.background)
    }
}

/// Which machine every destination is about. With more than one on this
/// device it is a menu of them, the one in use checked, and a way to add
/// another; Your machines is where they are managed. With one, it is the
/// name. Choosing another opens its overview; choosing the one in use leaves
/// everything where it is. It waits while a run or a transfer needs the link.
struct MachineSwitcher<Face: View>: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory
    @Environment(Navigator.self) var nav
    /// What it looks like, told whether it is a menu.
    @ViewBuilder let face: (_ menu: Bool) -> Face
    @State private var adding = false

    var body: some View {
        if directory.known.count > 1 {
            Menu {
                Picker("Machine", selection: chosen) {
                    ForEach(directory.known) { m in Text(directory.label(for: m)).tag(Optional(m.id)) }
                }
                .pickerStyle(.inline)
                Button { adding = true } label: {
                    Label("Add a machine", systemImage: "plus")
                }
            } label: {
                face(true)
            }
            .disabled(nav.locked || ble.transferInFlight)
            .sheet(isPresented: $adding) { AddMachineSheet() }
        } else {
            face(false)
        }
    }

    private var chosen: Binding<String?> {
        Binding(get: { directory.current?.id },
                set: { id in
                    if let m = directory.known.first(where: { $0.id == id }) { ble.select(m) }
                })
    }
}

extension MachineDirectory {
    /// A machine's name where two on this device share it: with its unit.
    func label(for m: KnownMachine) -> String {
        let twins = known.filter { $0.displayName == m.displayName }.count > 1
        return twins && !m.unit.isEmpty ? "\(m.displayName) · Unit \(m.unit)" : m.displayName
    }
}

extension BLEManager {
    /// Which machine, and whether the phone can hear it. The demo is just
    /// the demo.
    var machineLine: String {
        guard let m = current else { return "" }
        return m.isDemo ? linkText : "\(m.displayName) · \(linkText)"
    }

    /// Whether the phone can hear the machine, and if not, since when; and,
    /// once it can, whether the machine lets it change anything.
    var linkText: String {
        guard let m = current else { return "" }
        if m.isDemo { return "Demo" }
        switch connectionState {
        case .connected:
            return trust == .viewer || trust == .unpaired ? "Connected · View only" : "Connected"
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
