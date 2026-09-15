package net.truce.sodamachine

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen

/**
 * The OS holds the static `launch_icon` over `splash_bg` until Compose's first
 * frame paints. Compose uses the same faucet mark and cobalt background.
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
