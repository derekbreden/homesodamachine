import SwiftUI

/// Big Blue palette. The faucet mark lives in Assets.xcassets/LaunchIcon.
enum Theme {
    static let cobalt = Color(red: 23 / 255, green: 73 / 255, blue: 209 / 255) // #1749D1
    static let navy = Color(red: 16 / 255, green: 49 / 255, blue: 156 / 255) // #10319C
    static let ice = Color(red: 220 / 255, green: 230 / 255, blue: 255 / 255) // #DCE6FF
    static let orange = Color(red: 255 / 255, green: 145 / 255, blue: 82 / 255) // #FF9152

    static let background = cobalt
    static let surface = navy
    static let textPrimary = Color.white
    static let textSecondary = ice
    static let accent = orange
    static let onAccent = navy
    static let controlTint = ice
    static let error = Color(red: 1, green: 181 / 255, blue: 181 / 255)

    static let dotActive = orange
    static let dotInactive = ice.opacity(0.6)
    static let placeholder = navy
    static let activePhase = ice

    // Per-flavor chart series, paired with labels and flavor pictures.
    static let chartFlavor1 = orange
    static let chartFlavor2 = ice

    // Liquid gradient stops used by GlassAnimationView.
    static let liquidStop0 = ice
    static let liquidStop1 = cobalt
    static let liquidStop2 = navy
}

// ────────────────────────────────────────────────────────────
// The mark, and the one place a screen that opens with it puts it.
//
// THE LAUNCH SCREEN AND THE SCREEN BEHIND IT HOLD THE SAME TWO NUMBERS.
// LaunchScreen.storyboard draws this size at this distance below the safe
// area, against Assets.xcassets/LaunchBackground, which is Theme.background.
// The app's first frame lands with the mark where the launch screen has it.
// Change one of the three and change all three.
// ────────────────────────────────────────────────────────────

extension Theme {
    /// The mark's frame, where it is the first thing on a screen.
    static let markSize: CGFloat = 160
    /// From the top of the safe area to the top of that frame.
    static let markTop: CGFloat = 72
}

/// The mark at the head of a screen, in the place the launch screen leaves it.
struct MarkHeader: View {
    var body: some View {
        Image("LaunchIcon")
            .resizable()
            .scaledToFit()
            .frame(width: Theme.markSize, height: Theme.markSize)
            .padding(.top, Theme.markTop)
            .accessibilityHidden(true)
    }
}
