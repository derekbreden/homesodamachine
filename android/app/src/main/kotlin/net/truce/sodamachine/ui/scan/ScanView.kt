package net.truce.sodamachine.ui.scan

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import net.truce.sodamachine.ble.BleManager
import net.truce.sodamachine.ble.ConnectionState
import net.truce.sodamachine.ui.glass.GlassAnimation
import net.truce.sodamachine.ui.theme.Theme

/**
 * Top-level scan / onboarding screen. Mirrors the SwiftUI `ScanView` on iOS:
 * branches into onboarding, animated-search, demo-waiting, or the connected
 * state based on `BleManager`'s observable properties.
 *
 * The actual BLE work is stubbed in `BleManager` — this file is purely UI +
 * state-driven branching. M3 will swap in the real BLE implementation
 * underneath without changes here.
 */
@Composable
fun ScanView(ble: BleManager) {
    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Theme.background,
    ) {
        when {
            ble.readyToShow -> ConfigPlaceholder()
            !ble.hasCompletedOnboarding -> OnboardingContent(ble)
            ble.demoMode -> Box(modifier = Modifier.fillMaxSize())  // brief waiting frame
            else -> AnimatedSearchContent(ble)
        }
    }
}

// ────────────────────────────────────────────────────────────
// Onboarding (first-run): glass + title + subtitle + scan / demo buttons
// ────────────────────────────────────────────────────────────

@Composable
private fun OnboardingContent(ble: BleManager) {
    Box(modifier = Modifier.fillMaxSize()) {
        // Glass animation centered. clearAndSetSemantics() is the Compose
        // equivalent of iOS .accessibilityHidden(true) — TalkBack skips it.
        // 288dp matches the launch_icon size so the splash → animation
        // handoff is size-stable.
        GlassAnimation(
            modifier = Modifier
                .align(Alignment.Center)
                .size(288.dp)
                .clearAndSetSemantics { },
        )

        // Title + buttons block at the bottom of the screen.
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(horizontal = 32.dp, vertical = 48.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = "Home Soda Machine",
                color = Theme.textPrimary,
                fontSize = 20.sp,
                fontWeight = FontWeight.Medium,
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = "Manage your machine's display images, run maintenance cycles, and view usage statistics.",
                color = Theme.textSecondary,
                fontSize = 14.sp,
                textAlign = TextAlign.Center,
            )
            Spacer(Modifier.height(24.dp))

            // Scan button. Sets the onboarding flag and prefers-not-demo;
            // recomposition flips the screen to AnimatedSearchContent, whose
            // LaunchedEffect kicks off the actual scan flow. We don't launch
            // the suspend call from here because rememberCoroutineScope() in
            // OnboardingContent would cancel it the moment we navigate away.
            Button(
                onClick = {
                    ble.prefersDemoMode = false
                    ble.hasCompletedOnboarding = true
                },
                shape = RoundedCornerShape(10.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.White.copy(alpha = 0.15f),
                    contentColor = Theme.textPrimary,
                ),
                contentPadding = PaddingValues(vertical = 12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
            ) {
                Text(
                    text = "Scan for Hardware",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                )
            }
            Spacer(Modifier.height(12.dp))

            // Demo mode link. Smaller, secondary text — same visual weight
            // as iOS's text button below the primary action.
            TextButton(
                onClick = {
                    ble.prefersDemoMode = true
                    ble.hasCompletedOnboarding = true
                    ble.enterDemoMode()
                },
            ) {
                Text(
                    text = "Enter Demo Mode",
                    color = Theme.textSecondary,
                    fontSize = 14.sp,
                )
            }
        }
    }
}

// ────────────────────────────────────────────────────────────
// Animated search (post-onboarding): glass + status text + cancel
// ────────────────────────────────────────────────────────────

@Composable
private fun AnimatedSearchContent(ble: BleManager) {
    // Auto-start the scan when this screen becomes the active branch and the
    // BLE state machine is at rest. If the user cancels mid-scan, we go back
    // to onboarding and reset to BluetoothOff; coming back here later
    // re-fires the LaunchedEffect since the composable left and re-entered
    // composition.
    LaunchedEffect(Unit) {
        if (ble.connectionState == ConnectionState.BluetoothOff) {
            ble.activateBluetooth()
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        GlassAnimation(
            modifier = Modifier
                .align(Alignment.Center)
                .size(288.dp)
                .clearAndSetSemantics { },
        )

        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(horizontal = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Bottom,
        ) {
            // Fixed-height status block. Matches the iOS .frame(height: 100)
            // so layout doesn't jump as state strings change length.
            Box(
                modifier = Modifier
                    .height(100.dp)
                    .padding(bottom = 16.dp),
                contentAlignment = Alignment.Center,
            ) {
                StatusContent(ble.connectionState)
            }

            TextButton(
                onClick = {
                    ble.disconnect()
                    ble.hasCompletedOnboarding = false
                },
            ) {
                Text(
                    text = "Cancel",
                    color = Theme.textSecondary,
                    fontSize = 14.sp,
                )
            }
            Spacer(Modifier.height(20.dp))
        }
    }
}

// ────────────────────────────────────────────────────────────
// Status content — connection-state driven
// ────────────────────────────────────────────────────────────

@Composable
private fun StatusContent(state: ConnectionState) {
    // Live region tells TalkBack to re-announce when the contents change —
    // the Android equivalent of iOS's
    // .accessibilityElement(children: .combine).accessibilityAddTraits(.updatesFrequently).
    // mergeDescendants combines the leaf texts into one accessibility element.
    val statusRegion = Modifier.semantics(mergeDescendants = true) {
        liveRegion = LiveRegionMode.Polite
    }

    when (state) {
        ConnectionState.BluetoothOff -> {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = statusRegion,
            ) {
                Text(
                    text = "Turn on Bluetooth",
                    color = Theme.textSecondary,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Bluetooth is required to connect to your Soda Machine.",
                    color = Theme.textSecondary,
                    fontSize = 16.sp,
                    textAlign = TextAlign.Center,
                )
            }
        }

        ConnectionState.SearchingLong -> {
            Column(modifier = statusRegion) {
                Text(
                    text = "Searching for Soda Machine...",
                    color = Theme.textSecondary,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(bottom = 12.dp),
                )
                HintLine("Get closer to the Soda Machine")
                HintLine("Make sure it is powered on")
                HintLine("Try rebooting the Soda Machine")
            }
        }

        ConnectionState.Connecting -> {
            Text(
                text = "Connecting...",
                color = Theme.textSecondary,
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium,
                modifier = statusRegion,
            )
        }

        ConnectionState.Searching, ConnectionState.Connected -> {
            // Connected briefly shows the same text before readyToShow flips
            // the parent branch — mirrors iOS's behavior in the same window.
            Text(
                text = "Searching for Soda Machine...",
                color = Theme.textSecondary,
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium,
                modifier = statusRegion,
            )
        }
    }
}

@Composable
private fun HintLine(text: String) {
    // iOS uses SF Symbol icons (figure.walk, power, arrow.clockwise) inline
    // with each label. Skipping the icons for M2 keeps Material Icons out of
    // the dependency set; we'll add them in M8 when we mirror M0a/M0b
    // accessibility polish. For now bullet text reads clearly with TalkBack.
    Text(
        text = "• $text",
        color = Theme.textSecondary,
        fontSize = 16.sp,
        modifier = Modifier.padding(vertical = 2.dp),
    )
}

// ────────────────────────────────────────────────────────────
// Connected placeholder — until the ConfigView port lands in M5
// ────────────────────────────────────────────────────────────

@Composable
private fun ConfigPlaceholder() {
    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.align(Alignment.Center),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = "Connected",
                color = Theme.textPrimary,
                fontSize = 24.sp,
                fontWeight = FontWeight.Medium,
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = "ConfigView lands in M5",
                color = Theme.textSecondary,
                fontSize = 14.sp,
            )
        }
    }
}
