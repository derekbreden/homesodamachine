import SwiftUI

// ────────────────────────────────────────────────────────────
// History: what the machine did, from its own record.
//
// The machine keeps the record whether or not a phone is near. This page
// reads it while it is up, newest first, and keeps what it has read for as
// long as the app runs. Only a device the machine trusts may read it.
// ────────────────────────────────────────────────────────────

struct HistoryView: View {
    @Environment(BLEManager.self) var ble
    let entry: RouteEntry

    enum Showing: String, CaseIterable {
        case everything = "Everything"
        case pours = "Pours"
        case problems = "Needs attention"
    }

    /// How often the page asks the machine for anything new while it is up.
    private static let recheck: Duration = .seconds(15)

    @State private var showing = Showing.everything
    @State private var reading = false
    @State private var readingEarlier = false
    @State private var problem: BridgeError?

    private var history: MachineHistory { ble.current?.history ?? MachineHistory() }
    private var reachable: Bool { ble.demoMode || (ble.linked && ble.bridgeReady) }

    var body: some View {
        let history = history
        let shown = history.entries.filter(matches)
        VStack(alignment: .leading, spacing: 20) {
            notice
            if !history.entries.isEmpty {
                HistorySummary(history: history)
                Picker("Show", selection: $showing) {
                    ForEach(Showing.allCases, id: \.self) { Text($0.rawValue).tag($0) }
                }
                .pickerStyle(.segmented)
                if shown.isEmpty {
                    Note(showing == .problems ? "Nothing here has needed attention." : "No pours in what has been read.")
                } else {
                    ForEach(days(of: shown, anchor: history.anchor), id: \.title) { day in
                        VStack(alignment: .leading, spacing: 12) {
                            SectionTitle(day.title)
                            GroupedPanel {
                                ForEach(Array(day.entries.enumerated()), id: \.element.id) { index, item in
                                    if index > 0 { RowDivider() }
                                    HistoryRow(entry: item, time: item.date(in: .current, anchor: history.anchor))
                                }
                            }
                        }
                    }
                }
                footer(history)
            } else if reading {
                HStack(spacing: 12) { ProgressView(); Text("Reading the machine’s history…").font(.subheadline) }
                    .frame(maxWidth: .infinity, minHeight: 88)
            } else if problem == nil, history.readAt != nil {
                Note("The machine has not recorded anything yet.")
            }
        }
        .frame(maxWidth: 640).frame(maxWidth: .infinity, alignment: .leading)
        .task(id: reachable) {
            guard reachable else { return }
            while !Task.isCancelled {
                await refresh()
                try? await Task.sleep(for: Self.recheck)
            }
        }
    }

    private func matches(_ entry: HistoryEntry) -> Bool {
        switch showing {
        case .everything: true
        case .pours: entry.kind == .pour
        case .problems: entry.needsAttention
        }
    }

    private func refresh() async {
        reading = true
        problem = await ble.refreshHistory()
        reading = false
    }

    /// What stands between this device and the record, when something does.
    @ViewBuilder private var notice: some View {
        if !reachable {
            Notice(title: history.entries.isEmpty ? "History is read from the machine" : "Last read \(history.readAt.map(said) ?? "earlier")",
                   message: "Bring your device near the machine to read its history.",
                   icon: "antenna.radiowaves.left.and.right.slash")
        } else if let problem {
            switch problem {
            case .untrusted:
                VStack(spacing: 12) {
                    Notice(title: "History is for trusted devices",
                           message: "It shows when your household pours. Ask the machine to trust this \(BLEManager.deviceWord), then tap Trust on the machine.",
                           icon: "lock")
                    if let ask = ble.trustAsk, ask.quiet, ask.reason == .anything {
                        Panel { TrustStatusView(ask: ask) }
                    } else {
                        ActionButton(title: "Ask the machine to trust this \(BLEManager.deviceWord)", primary: false) {
                            Task {
                                guard await ble.requestTrust(.anything) == .trusted else { return }
                                await refresh()
                            }
                        }
                    }
                }
            case .refused, .needsUpdate:
                Notice(title: "Update your machine",
                       message: "Its software does not keep a history this app can read yet.",
                       icon: "arrow.down.circle")
            default:
                Notice(title: "Couldn’t read the history", message: problem.message, icon: "exclamationmark.triangle.fill")
            }
        }
    }

    @ViewBuilder private func footer(_ history: MachineHistory) -> some View {
        if history.reachedEnd {
            Note("That is everything the machine has kept.")
        } else {
            ActionButton(title: "Show earlier", primary: false, working: readingEarlier) {
                guard !readingEarlier else { return }
                readingEarlier = true
                Task {
                    problem = await ble.readEarlierHistory()
                    readingEarlier = false
                }
            }
            .disabled(!reachable)
        }
    }

    private struct Day {
        let title: String
        var entries: [HistoryEntry]
    }

    /// The entries by the day they happened, newest day first. An entry
    /// whose time neither the machine's clock nor its uptime gives goes last,
    /// under its own heading.
    private func days(of entries: [HistoryEntry], anchor: HistoryAnchor?) -> [Day] {
        let calendar = Calendar.current
        var days: [Day] = []
        var undated: [HistoryEntry] = []
        for item in entries {
            guard let when = item.date(in: calendar, anchor: anchor) else { undated.append(item); continue }
            let title: String
            if calendar.isDateInToday(when) { title = "Today" }
            else if calendar.isDateInYesterday(when) { title = "Yesterday" }
            else { title = when.formatted(.dateTime.weekday(.wide).month(.wide).day()) }
            if days.last?.title == title { days[days.count - 1].entries.append(item) }
            else { days.append(Day(title: title, entries: [item])) }
        }
        if !undated.isEmpty { days.append(Day(title: "Earlier · the machine’s clock was not set", entries: undated)) }
        return days
    }
}

/// How much the machine has poured lately.
struct HistorySummary: View {
    let history: MachineHistory

    private static let days = 7

    var body: some View {
        let pours = history.pours(days: Self.days, now: Date(), calendar: .current)
        let today = pours.last ?? 0
        let week = pours.reduce(0, +)
        Panel {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Today").font(.subheadline).foregroundStyle(Theme.textSecondary)
                    Text(Self.count(today)).font(.title2.weight(.medium).monospacedDigit())
                }
                Spacer(minLength: 16)
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Past \(Self.days) days").font(.subheadline).foregroundStyle(Theme.textSecondary)
                    Text(Self.count(week)).font(.title2.weight(.medium).monospacedDigit())
                }
            }
            .accessibilityElement(children: .combine)
            if !history.reachedEnd, week > 0 {
                Note("Counted from what has been read. Show earlier to count further back.")
            }
        }
    }

    static func count(_ pours: Int) -> String { pours == 1 ? "1 pour" : "\(pours) pours" }
}

struct HistoryRow: View {
    let entry: HistoryEntry
    let time: Date?

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: entry.symbol)
                .frame(width: 24)
                .foregroundStyle(entry.needsAttention ? Theme.error : Theme.textSecondary)
                .padding(.top, 2)
            VStack(alignment: .leading, spacing: 3) {
                Text(entry.title).font(.body).fixedSize(horizontal: false, vertical: true)
                if let note = entry.note(temperature: MachineStatusPanel.temperature) { Note(note) }
            }
            Spacer(minLength: 12)
            if let time {
                Text(time.formatted(date: .omitted, time: .shortened))
                    .font(.subheadline.monospacedDigit()).foregroundStyle(Theme.textSecondary)
            }
        }
        .padding(.vertical, 12)
        .frame(maxWidth: .infinity, minHeight: 52, alignment: .leading)
        .accessibilityElement(children: .combine)
    }
}
