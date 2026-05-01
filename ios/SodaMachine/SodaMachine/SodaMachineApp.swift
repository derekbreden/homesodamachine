import SwiftUI
import UIKit

@main
struct SodaMachineApp: App {
    @State private var bleManager = BLEManager()
    @Environment(\.scenePhase) private var scenePhase

    init() {
        // Color-match the system UIPageControl (used by TabView's .page style)
        // to the dark theme. The control supplies tap-to-jump, scrub-to-step,
        // and the adjustable trait that VoiceOver and Voice Control bridge to
        // — none of which a custom decorative dot row provides.
        UIPageControl.appearance().currentPageIndicatorTintColor = UIColor(Theme.dotActive)
        UIPageControl.appearance().pageIndicatorTintColor = UIColor(Theme.dotInactive)
    }

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
