import SwiftUI

@main
struct SodaMachineApp: App {
    @State private var bleManager = BLEManager()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            ScanView()
                .environment(bleManager)
                .onChange(of: scenePhase) { _, phase in
                    if phase == .active {
                        bleManager.handleReturnToForeground()
                    }
                }
        }
    }
}
