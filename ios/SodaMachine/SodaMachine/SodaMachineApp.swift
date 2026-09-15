import SwiftUI

@main
struct SodaMachineApp: App {
    @State private var directory: MachineDirectory
    @State private var bleManager: BLEManager
    @Environment(\.scenePhase) private var scenePhase

    init() {
        let directory = MachineDirectory()
        _directory = State(initialValue: directory)
        _bleManager = State(initialValue: BLEManager(directory: directory))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .tint(Theme.controlTint)
                .preferredColorScheme(.dark)
                .environment(bleManager)
                .environment(directory)
                .onChange(of: scenePhase) { _, phase in
                    if phase == .active {
                        bleManager.handleReturnToForeground()
                    }
                }
        }
    }
}
