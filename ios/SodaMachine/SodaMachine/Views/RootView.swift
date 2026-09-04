import SwiftUI

// ────────────────────────────────────────────────────────────
// What the app opens on.
//
// The machine this phone is pointed at, on its own page, with whatever it
// last said — or, with no machine on the phone yet, the screen that adds
// one. The link is a line on the page, not a screen of its own.
// ────────────────────────────────────────────────────────────

struct RootView: View {
    @Environment(BLEManager.self) var ble
    @Environment(MachineDirectory.self) var directory

    var body: some View {
        Group {
            if let machine = directory.current {
                MachinePage(machine: machine)
                    .id(machine.id)
            } else {
                AddMachineView(firstRun: true)
            }
        }
        .onAppear {
            // A phone pointed at a machine turns toward it at once. The radio
            // comes up only for a machine that needs it: a phone with none, or
            // with only the demo, waits for the tap that says why.
            ble.activateBluetooth()
        }
    }
}
