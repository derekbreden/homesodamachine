import SwiftUI

struct ScanView: View {
    @Environment(BLEManager.self) var ble
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
    @AppStorage("prefersDemoMode") private var prefersDemoMode = false

    var body: some View {
        Group {
            if ble.readyToShow {
                ConfigView()
            } else if !hasCompletedOnboarding {
                onboardingView
            } else if ble.demoMode {
                // Demo mode chosen from onboarding — wait for enterDemoMode to set readyToShow
                Color.clear
            } else {
                animatedSearchView
            }
        }
        .onAppear {
            if hasCompletedOnboarding {
                if prefersDemoMode {
                    ble.enterDemoMode()
                } else {
                    ble.activateBluetooth()
                }
            }
        }
    }

    // MARK: - First-run onboarding

    private var onboardingView: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            GeometryReader { geo in
                let animSize: CGFloat = 200
                let animCenter = geo.size.height / 2
                let animBottom = animCenter + animSize / 2
                let belowSpace = geo.size.height - animBottom

                GlassAnimationView()
                    .frame(width: animSize, height: animSize)
                    .position(x: geo.size.width / 2, y: animCenter)
                    .accessibilityHidden(true)

                VStack(spacing: 0) {
                    VStack(spacing: 8) {
                        Text("Home Soda Machine")
                            .font(.system(size: 20, weight: .medium))
                            .foregroundStyle(Theme.textPrimary)

                        Text("Manage your machine's display images, run maintenance cycles, and view usage statistics.")
                            .font(.system(size: 14))
                            .foregroundStyle(Theme.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.bottom, 24)

                    Button {
                        prefersDemoMode = false
                        hasCompletedOnboarding = true
                        ble.activateBluetooth()
                    } label: {
                        Text("Scan for Hardware")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(Color.white.opacity(0.15))
                            .cornerRadius(10)
                    }
                    .padding(.bottom, 12)

                    Button("Enter Demo Mode") {
                        prefersDemoMode = true
                        hasCompletedOnboarding = true
                        ble.enterDemoMode()
                    }
                    .font(.system(size: 14))
                    .foregroundStyle(Theme.textSecondary)
                }
                .padding(.horizontal, 32)
                .frame(width: geo.size.width, height: belowSpace)
                .position(x: geo.size.width / 2, y: animBottom + belowSpace / 2)
            }
            .ignoresSafeArea()
        }
    }

    // MARK: - Scanning (shown on subsequent launches)

    private var animatedSearchView: some View {
        ZStack {
            Theme.background.ignoresSafeArea()

            GeometryReader { geo in
                GlassAnimationView()
                    .frame(width: 200, height: 200)
                    .position(x: geo.size.width / 2, y: geo.size.height / 2)
                    .accessibilityHidden(true)
            }
            .ignoresSafeArea()

            VStack {
                Spacer()

                statusContent
                    .frame(height: 100)
                    .padding(.bottom, 16)

                Button("Cancel") {
                    ble.disconnect()
                    hasCompletedOnboarding = false
                }
                .font(.system(size: 14))
                .foregroundStyle(Theme.textSecondary)

                Spacer().frame(height: 20)
            }
            .padding(.horizontal, 32)
        }
    }

    @ViewBuilder
    private var statusContent: some View {
        if ble.connectionState == .bluetoothOff {
            VStack(spacing: 8) {
                Text("Turn on Bluetooth")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textSecondary)
                Text("Bluetooth is required to connect to your Soda Machine.")
                    .font(.system(size: 16))
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
            }
            .accessibilityElement(children: .combine)
            .accessibilityAddTraits(.updatesFrequently)
        } else if ble.connectionState == .searchingLong {
            VStack(spacing: 8) {
                Text("Searching for Soda Machine...")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(Theme.textSecondary)
                    .padding(.bottom, 4)
                VStack(alignment: .leading, spacing: 8) {
                    Label("Get closer to the Soda Machine", systemImage: "figure.walk")
                    Label("Make sure it is powered on", systemImage: "power")
                    Label("Try rebooting the Soda Machine", systemImage: "arrow.clockwise")
                }
                .font(.system(size: 16))
                .foregroundStyle(Theme.textSecondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityAddTraits(.updatesFrequently)
        } else if ble.connectionState == .connecting {
            Text("Connecting...")
                .font(.system(size: 16, weight: .medium))
                .foregroundStyle(Theme.textSecondary)
                .accessibilityAddTraits(.updatesFrequently)
        } else {
            Text("Searching for Soda Machine...")
                .font(.system(size: 16, weight: .medium))
                .foregroundStyle(Theme.textSecondary)
                .accessibilityAddTraits(.updatesFrequently)
        }
    }
}
