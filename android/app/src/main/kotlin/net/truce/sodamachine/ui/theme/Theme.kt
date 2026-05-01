package net.truce.sodamachine.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/**
 * Direct port of `ios/SodaMachine/SodaMachine/Theme.swift`. Two platforms,
 * one source of truth per platform, identical values.
 */
object Theme {
    // Background
    val background    = Color(0xFF1A1A2E)

    // Text
    val textPrimary   = Color.White
    val textSecondary = Color(red = 0.6f, green = 0.6f, blue = 0.6f)

    // UI elements
    val dotActive   = Color.White
    val dotInactive = Color(red = 0.35f, green = 0.35f, blue = 0.35f)
    val placeholder = Color(red = 0.20f, green = 0.20f, blue = 0.20f)

    // Accent (Hold-to-Prime button, Clean cycle phase)
    val primeBlue = Color(red = 0.27f, green = 0.53f, blue = 1.0f)

    // Chart colors (per-flavor — also pie + bar foregrounds in StatsSheet)
    val chartPink   = Color(red = 0.9f, green = 0.3f, blue = 0.5f)
    val chartPurple = Color(red = 0.6f, green = 0.3f, blue = 0.9f)

    // Liquid gradient stops — used by GlassAnimation. Top → bottom-right.
    val liquidStop0 = Color(red = 0.914f, green = 0.271f, blue = 0.376f)
    val liquidStop1 = Color(red = 0.761f, green = 0.200f, blue = 0.451f)
    val liquidStop2 = Color(red = 0.482f, green = 0.184f, blue = 0.969f)
}

@Composable
fun SodaMachineTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            background = Theme.background,
            surface    = Theme.background,
            primary    = Theme.textPrimary,
        ),
        content = content,
    )
}
