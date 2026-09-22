package net.truce.sodamachine.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/** Big Blue palette, shared with the companion app and enclosure display. */
object Theme {
    val cobalt = Color(0xFF1749D1)
    val navy = Color(0xFF10319C)
    val ice = Color(0xFFDCE6FF)
    val orange = Color(0xFFFF9152)

    val background = cobalt
    val surface = navy
    val textPrimary = Color.White
    val textSecondary = ice
    val accent = orange
    val onAccent = navy
    val controlTint = ice

    val dotActive = orange
    val dotInactive = ice.copy(alpha = 0.6f)
    val placeholder = navy
    val activePhase = ice
    val chartFlavor1 = orange
    val chartFlavor2 = ice
}

@Composable
fun SodaMachineTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            background = Theme.background,
            onBackground = Theme.textPrimary,
            surface = Theme.surface,
            onSurface = Theme.textPrimary,
            surfaceVariant = Theme.cobalt,
            onSurfaceVariant = Theme.ice,
            primary = Theme.accent,
            onPrimary = Theme.onAccent,
            primaryContainer = Theme.navy,
            onPrimaryContainer = Theme.ice,
            secondary = Theme.ice,
            onSecondary = Theme.navy,
            secondaryContainer = Theme.navy,
            onSecondaryContainer = Theme.ice,
            tertiary = Theme.orange,
            onTertiary = Theme.navy,
            outline = Theme.ice.copy(alpha = 0.6f),
        ),
        content = content,
    )
}
