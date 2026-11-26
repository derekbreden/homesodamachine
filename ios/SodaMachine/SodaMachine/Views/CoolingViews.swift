import SwiftUI

/// The same controller report supplies the Machine shortcut and the explanation in Settings.
private struct CoolingReading {
    let status: MachineStatus?
    var state: CoolingState { status?.coolingState ?? .unavailable }
    var time: String? {
        guard state == .startupWait, let seconds = status?.startupCoolingSeconds else { return nil }
        return String(format: "%d:%02d", seconds / 60, seconds % 60)
    }
    var spokenTitle: String {
        guard state == .startupWait, let seconds = status?.startupCoolingSeconds else { return title }
        return "Cooling starts in " + Duration.seconds(seconds).formatted(.units(allowed: [.minutes, .seconds], width: .wide))
    }

    var symbol: String {
        switch state {
        case .startupWait, .restartHold: "hourglass"
        case .running: "snowflake"
        case .idle: "checkmark.circle"
        case .probeFault, .freezeProtection: "exclamationmark.triangle"
        case .paused: "pause.circle"
        case .unavailable: "minus.circle"
        }
    }

    var title: String {
        switch state {
        case .startupWait: return time.map { "Starts in " + $0 } ?? "Cooling soon"
        case .restartHold: return "Cooling soon"
        case .running: return "Compressor running"
        case .idle: return "Holding temperature"
        case .probeFault: return "Waiting for sensors"
        case .freezeProtection: return "Freeze protection"
        case .paused: return "Cooling paused"
        case .unavailable: return status == nil ? "Waiting for machine" : "Status unavailable"
        }
    }

    func detail(unit: MachineTemperatureUnit) -> String {
        switch state {
        case .startupWait: return "Compressor restart delay."
        case .restartHold: return "Waiting to restart the compressor."
        case .running, .idle: return "Cooling coil " + unit.format(tenthsC: status?.coilTenthsC)
        case .probeFault:
            switch (status?.tankTenthsC, status?.coilTenthsC) {
            case (nil, nil): return status?.probeCount == 0 ? "No temperature probes detected." : "Both temperature readings are missing."
            case (nil, _): return "No tank wall reading."
            case (_, nil): return "No cooling coil reading."
            default: return "The controller is waiting for fresh probe readings."
            }
        case .freezeProtection: return "Cooling resumes when the coil warms."
        case .paused: return status?.gasAlarm == true ? "The gas alarm is active." : "The compressor is off."
        case .unavailable: return status == nil ? "Waiting for a fresh reading." : "No cooling status from the controller."
        }
    }
}

/// The enclosure's gear, thermometer and activity mark form one accessible Settings button.
struct MachineCoolingButton: View {
    @Environment(BLEManager.self) private var ble
    @Environment(Navigator.self) private var nav

    var body: some View {
        TimelineView(.periodic(from: .now, by: 1)) { _ in
            let status = ble.liveCoolingStatus(at: .now)
            let cooling = CoolingReading(status: status)
            let tank = ble.temperatureUnit.format(tenthsC: status?.tankTenthsC, compact: true)
            Button {
                nav.setPath([], on: .settings)
                nav.select(.settings)
            } label: {
                ViewThatFits(in: .horizontal) {
                    HStack(spacing: 14) {
                        tankMark(tank, tenths: status?.tankTenthsC)
                        Spacer(minLength: 4)
                        activity(cooling)
                    }
                    VStack(alignment: .leading, spacing: 12) {
                        tankMark(tank, tenths: status?.tankTenthsC)
                        activity(cooling)
                    }
                }
                .padding(.horizontal, 16).padding(.vertical, 12)
                .frame(maxWidth: .infinity, minHeight: 54, alignment: .leading)
                .background(Theme.surface, in: RoundedRectangle(cornerRadius: 16))
                .overlay(RoundedRectangle(cornerRadius: 16).strokeBorder(Theme.ice.opacity(0.18), lineWidth: 1))
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Machine settings")
            .accessibilityValue((status?.tankTenthsC == nil ? "No tank wall reading" : "Tank wall " + tank) + ", " + cooling.spokenTitle)
        }
    }

    private func tankMark(_ temperature: String, tenths: Int?) -> some View {
        HStack(spacing: 12) {
            Image(systemName: "gearshape.fill").font(.title3).foregroundStyle(Theme.ice)
            Divider().overlay(Theme.ice.opacity(0.25)).frame(height: 25)
            HStack(spacing: 4) {
                let symbol = switch tenths ?? 0 {
                case ..<67: "thermometer.low"
                case ..<134: "thermometer.medium"
                default: "thermometer.high"
                }
                Image(systemName: symbol).font(.title3).foregroundStyle(Theme.ice)
                Text(temperature).font(.title2.weight(.semibold).monospacedDigit())
            }
        }.fixedSize()
    }

    @ViewBuilder private func activity(_ cooling: CoolingReading) -> some View {
        switch cooling.state {
        case .startupWait, .restartHold:
            HStack(spacing: 6) {
                Image(systemName: "hourglass")
                if let time = cooling.time { Text(time).monospacedDigit() }
            }.font(.title3.weight(.medium)).foregroundStyle(Theme.ice).fixedSize()
        case .running:
            Image(systemName: "snowflake").font(.title3.weight(.medium)).foregroundStyle(Theme.ice)
        case .probeFault, .freezeProtection, .paused:
            Image(systemName: "exclamationmark.triangle.fill").font(.title3).foregroundStyle(Theme.accent)
        case .idle, .unavailable:
            EmptyView()
        }
    }
}

private struct LastTankReading: View {
    @Environment(BLEManager.self) private var ble

    var body: some View {
        if let reading = ble.appliance.status {
            let when = said(reading.at)
            if let tank = reading.value.tankTenthsC {
                Note("Last tank reading \(ble.temperatureUnit.format(tenthsC: tank)) · \(when)")
            } else {
                Note("Last read \(when)")
            }
        }
    }
}

/// Readings always use the machine's confirmed unit, including while a new choice awaits Trust.
struct CoolingSettings: View {
    @Environment(BLEManager.self) private var ble
    @Environment(SettingWriter.self) private var writer
    @Environment(\.dynamicTypeSize) private var typeSize

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionTitle("Temperature & cooling")
            Panel {
                TimelineView(.periodic(from: .now, by: 1)) { _ in
                    let status = ble.liveCoolingStatus(at: .now)
                    let cooling = CoolingReading(status: status)
                    VStack(alignment: .leading, spacing: 13) {
                        LabeledContent("Tank wall") {
                            Text(status?.tankTenthsC == nil ? "No reading" : ble.temperatureUnit.format(tenthsC: status?.tankTenthsC, compact: true))
                                .font(.title2.weight(.semibold).monospacedDigit())
                        }
                        VStack(alignment: .leading, spacing: 5) {
                            Label(cooling.title, systemImage: cooling.symbol).font(.headline.monospacedDigit())
                            Note(cooling.detail(unit: ble.temperatureUnit))
                        }.accessibilityElement(children: .combine)
                        if status == nil { LastTankReading() }
                    }
                }
                Divider().overlay(Theme.ice.opacity(0.2))
                unitControl
            }
            FormSaveOutcome(setting: .temperatureUnit, discard: {}, submitted: { _ in })
        }
    }

    private var unitControl: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Temperature unit").font(.subheadline.weight(.medium))
            if ble.settingSnapshot(.temperatureUnit) != nil || ble.temperatureUnitUnavailable {
                if typeSize.isAccessibilitySize {
                    unitPicker.pickerStyle(.menu)
                } else {
                    unitPicker.pickerStyle(.segmented)
                }
            }
            if let pending = writer.commit(.temperatureUnit),
               let byte = pending.desired.first, let unit = MachineTemperatureUnit(rawValue: byte) {
                Note("Requested \(unit.label)")
            } else if ble.temperatureUnitUnavailable {
                Note("Update the machine’s software to change its temperature unit.")
            } else if ble.current?.settingStorageProblem == true {
                Note("The machine can’t save settings right now.")
            } else if !ble.temperatureUnitWritable {
                Note(ble.canChange ? "Waiting for the machine’s saved unit." : "Connect to the machine to change its temperature unit.")
                if ble.canChange {
                    Button("Read saved unit") { Task { _ = await ble.readSetting(.temperatureUnit) } }
                        .frame(minHeight: 44)
                }
            }
        }
    }

    private var unitPicker: some View {
        Picker("Temperature unit", selection: Binding(get: { ble.temperatureUnit }, set: { unit in
            guard unit != ble.temperatureUnit, ble.temperatureUnitWritable,
                  let base = ble.settingSnapshot(.temperatureUnit) else { return }
            writer.submit(.temperatureUnit, base: base, desired: unit.wire)
        })) {
            ForEach(MachineTemperatureUnit.allCases, id: \.self) { unit in
                Text(unit.label).tag(unit)
            }
        }
        .labelsHidden()
        .disabled(!ble.temperatureUnitWritable || writer.commit(.temperatureUnit) != nil)
    }
}

/// The two temperature probes and the ten physical level switches can each be read independently.
struct WaterSensorsView: View {
    @Environment(BLEManager.self) private var ble
    @Environment(Navigator.self) private var nav
    let entry: RouteEntry

    var body: some View {
        TimelineView(.periodic(from: .now, by: 1)) { _ in
            let live = ble.liveCoolingStatus(at: .now)
            let last = ble.appliance.status
            let status = live ?? last?.value
            VStack(alignment: .leading, spacing: 24) {
                if live == nil {
                    if let last { Note("Last known readings · \(said(last.at))") }
                    else { Note("Waiting for readings from the machine.") }
                }
                VStack(alignment: .leading, spacing: 12) {
                    SectionTitle("Temperature probes")
                    Panel {
                        probe("Tank wall", status?.tankTenthsC)
                        probe("Cooling coil", status?.coilTenthsC)
                        LabeledContent("Probes found", value: status?.probeCount.map(String.init) ?? "No reading")
                    }
                }
                VStack(alignment: .leading, spacing: 12) {
                    SectionTitle("Water")
                    Panel {
                        Text(status?.waterDescription ?? "Water level unknown")
                        LabeledContent("Refill", value: refill(status))
                    }
                }
                VStack(alignment: .leading, spacing: 12) {
                    SectionTitle("Level switches")
                    Panel {
                        switches("Flavor 1", mask: status?.reedMask(0), count: 4)
                        let tank = status.flatMap { s in s.levelsRead ? UInt8((s.carbonatorLowReed ? 1 : 0) | (s.carbonatorHighReed ? 2 : 0)) : nil }
                        switches("Tank", mask: tank, count: 2)
                        switches("Flavor 2", mask: status?.reedMask(1), count: 4)
                        Note("Switches are shown from low to high. A filled dot means closed.")
                    }
                }
            }
            .frame(maxWidth: 560).frame(maxWidth: .infinity, alignment: .leading)
        }
        .modifier(StatusPolling(visible: nav.top == entry))
    }

    private func probe(_ name: String, _ value: Int?) -> some View {
        LabeledContent(name, value: value.map { ble.temperatureUnit.format(tenthsC: $0) } ?? "No reading")
            .monospacedDigit()
    }

    private func refill(_ status: MachineStatus?) -> String {
        guard let status, status.probeCount != nil else { return "No reading" }
        switch RefillState(rawValue: status.refillState) {
        case .idle: return "Idle"
        case .queued: return "Waiting"
        case .filling: return "Refilling"
        case .timeout: return "Timed out"
        case .fault: return "Level fault"
        case nil: return "No reading"
        }
    }

    private func switches(_ name: String, mask: UInt8?, count: Int) -> some View {
        LabeledContent(name) {
            if let mask {
                HStack(spacing: 8) {
                    ForEach(0..<count, id: \.self) { bit in
                        Circle().strokeBorder(Theme.ice, lineWidth: 1.5)
                            .background(Circle().fill(mask & (1 << bit) == 0 ? .clear : Theme.ice))
                            .frame(width: 15, height: 15)
                    }
                }
                .accessibilityElement(children: .ignore)
                .accessibilityLabel((0..<count).map { mask & (1 << $0) == 0 ? "open" : "closed" }.joined(separator: ", "))
            } else { Text("No reading") }
        }
    }
}
