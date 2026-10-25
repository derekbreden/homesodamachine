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
            // A phone pointed at a machine turns toward it as soon as the
            // system has said which machines it may reach. The radio comes up
            // only for a machine that needs it: a phone with none, or with only
            // the demo, leaves the looking to the system's sheet.
            ble.activateBluetooth()
        }
    }
}
