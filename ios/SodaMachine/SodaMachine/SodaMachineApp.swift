import SwiftUI

@main
struct SodaMachineApp: App {
    @State private var directory: MachineDirectory
    @State private var bleManager: BLEManager
    @State private var writer: SettingWriter
    @State private var mix: MixController
    @State private var access: MachineAccess
    @Environment(\.scenePhase) private var scenePhase

    init() {
        let directory = MachineDirectory()
        let bleManager = BLEManager(directory: directory)
        _directory = State(initialValue: directory)
        _bleManager = State(initialValue: bleManager)
        _writer = State(initialValue: SettingWriter(ble: bleManager))
        _mix = State(initialValue: MixController(ble: bleManager, changes: MixChanges()))
        _access = State(initialValue: MachineAccess(directory: directory, ble: bleManager))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .tint(Theme.controlTint)
                .preferredColorScheme(.dark)
                .environment(bleManager)
                .environment(directory)
                .environment(access)
                .environment(mix)
                .environment(writer)
                .onChange(of: scenePhase) { _, phase in
                    if phase == .active {
                        bleManager.handleReturnToForeground()
                        access.becameActive()
                    } else if phase == .background {
                        bleManager.handleEnterBackground()
                    }
                }
        }
    }
}
