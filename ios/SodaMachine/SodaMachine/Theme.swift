import SwiftUI

/// Big Blue palette. The faucet mark lives in Assets.xcassets/LaunchIcon.
nonisolated enum Theme {
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

    static let placeholder = navy
}

// ────────────────────────────────────────────────────────────
// The mark at the head of the first-run page.
// ────────────────────────────────────────────────────────────

extension Theme {
    static let markSize: CGFloat = 160
    /// From the top of the safe area to the top of the mark.
    static let markTop: CGFloat = 72
}

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
