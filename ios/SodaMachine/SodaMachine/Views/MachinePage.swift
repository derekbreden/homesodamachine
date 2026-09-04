import SwiftUI

// ────────────────────────────────────────────────────────────
// One machine's page.
//
// THE PAGE IS THE SAME PAGE WHETHER OR NOT THE RADIO CAN HEAR THE MACHINE.
// What is on it is what the machine last said, and one line says whether it
// is saying anything right now. A machine in the next room is not a search
// screen; it is its page with "out of range" on it, and the radio trying
// underneath.
//
// Which page depends on the machine. The prototype under the counter is a
// rotary knob's worth of settings; the appliance is what it is, what it runs,
// and the faces its flavors wear.
// ────────────────────────────────────────────────────────────

struct MachinePage: View {
    @Environment(BLEManager.self) var ble
    let machine: KnownMachine

    var body: some View {
        ZStack(alignment: .top) {
            if machine.model == .appliance {
                ApplianceView(machine: machine)
            } else {
                ConfigView(machine: machine)
            }
            if ble.radioOff && !machine.isDemo {
                BluetoothBanner()
            }
        }
    }
}

/// Whether the phone can hear the machine, and if not, when it last could.
struct LinkStatusView: View {
    @Environment(BLEManager.self) var ble
    let machine: KnownMachine
    /// Lead with the machine's name, on a page that does not carry it.
    var named = false

    var body: some View {
        Text(!named ? status : machine.isDemo ? machine.displayName : "\(machine.displayName) · \(status)")
            .font(.system(size: 13))
            .foregroundStyle(Theme.textSecondary)
            .multilineTextAlignment(.center)
            .accessibilityAddTraits(.updatesFrequently)
    }

    private var status: String {
        if machine.isDemo { return "Demo" }
        switch ble.connectionState {
        case .connected:    return "Connected"
        case .connecting:   return "Connecting…"
        case .bluetoothOff: return "Bluetooth is off"
        case .searching:    return "Looking for it…"
        case .searchingLong:
            if let t = machine.lastConnected { return "Out of range · last connected \(said(t))" }
            return "Out of range · never connected"
        }
    }
}

/// A condition of the phone, over whatever page is open.
struct BluetoothBanner: View {
    var body: some View {
        VStack(spacing: 2) {
            Text("Turn on Bluetooth")
                .font(.system(size: 14, weight: .medium))
                .foregroundStyle(Theme.textPrimary)
            Text("Bluetooth is how this phone reaches your machine.")
                .font(.system(size: 12))
                .foregroundStyle(Theme.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.10))
        .cornerRadius(12)
        .padding(.horizontal, 20)
        .padding(.top, 8)
        .accessibilityElement(children: .combine)
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
