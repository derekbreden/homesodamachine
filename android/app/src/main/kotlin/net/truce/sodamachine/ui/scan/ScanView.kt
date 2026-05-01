package net.truce.sodamachine.ui.scan

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
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import net.truce.sodamachine.ui.glass.GlassAnimation
import net.truce.sodamachine.ui.theme.Theme

/**
 * Phase-1 stub. Background + glass animation + onboarding text + scan button.
 *
 * No BLE, no scanning state machine, no Cancel — that's phase 3. Visually and
 * animatically this should look the same as the iOS onboarding screen on a
 * freshly-installed app.
 *
 * Layout mirrors ScanView.swift's `onboardingView`: glass centered vertically,
 * title + subtitle + button block at the bottom of the screen with horizontal
 * padding 32dp.
 */
@Composable
fun ScanView() {
    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Theme.background,
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            // Glass animation centered vertically and horizontally.
            // clearAndSetSemantics() is the Compose equivalent of iOS's
            // .accessibilityHidden(true) — TalkBack will skip it entirely.
            GlassAnimation(
                modifier = Modifier
                    .align(Alignment.Center)
                    .size(200.dp)
                    .clearAndSetSemantics { },
            )

            // Title + button block at the bottom.
            Column(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(horizontal = 32.dp, vertical = 48.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Bottom,
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
                Button(
                    onClick = { /* phase 3: BLE init */ },
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
            }
        }
    }
}
