import SwiftUI

enum Theme {
    // Background
    static let background = Color(red: 0.102, green: 0.102, blue: 0.180)  // #1a1a2e

    // Text
    static let textPrimary = Color.white
    static let textSecondary = Color(white: 0.6)

    // UI elements
    static let dotActive = Color.white
    static let dotInactive = Color(white: 0.35)
    static let placeholder = Color(white: 0.2)

    // Accent (used by Hold-to-Prime button and Clean cycle phase)
    static let primeBlue = Color(red: 0.27, green: 0.53, blue: 1.0)

    // Chart colors (per-flavor, also used as pie + bar foregrounds in StatsSheet)
    static let chartPink = Color(red: 0.9, green: 0.3, blue: 0.5)
    static let chartPurple = Color(red: 0.6, green: 0.3, blue: 0.9)

    // Liquid gradient stops — used by GlassAnimationView. Order is top → bottom-right.
    static let liquidStop0 = Color(red: 0.914, green: 0.271, blue: 0.376)
    static let liquidStop1 = Color(red: 0.761, green: 0.200, blue: 0.451)
    static let liquidStop2 = Color(red: 0.482, green: 0.184, blue: 0.969)
}
