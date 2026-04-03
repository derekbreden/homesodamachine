import SwiftUI

@main
struct SodaMachineApp: App {
    @State private var bleManager = BLEManager()

    var body: some Scene {
        WindowGroup {
            ScanView()
                .environment(bleManager)
        }
    }
}
