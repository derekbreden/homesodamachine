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
            // A phone with a machine on it turns the radio toward it at once.
            // A phone with none waits for the tap that says why.
            if directory.current != nil { ble.activateBluetooth() }
        }
    }
}
