package net.truce.sodamachine

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen

/**
 * The OS holds the static `launch_icon` over `splash_bg` until Compose's first
 * frame paints. Compose's first frame is `GlassAnimation` at t=0 — same shape
 * as the static icon — so the static→animated handoff has no visual seam.
 *
 * No `setKeepOnScreenCondition` and no intermediate state. Mirrors the
 * `LaunchScreen.storyboard` → first SwiftUI frame model on iOS.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent { App() }
    }
}
