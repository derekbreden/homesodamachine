package net.truce.sodamachine.ui.glass

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipPath
import net.truce.sodamachine.ui.theme.Theme
import kotlin.math.PI
import kotlin.math.min
import kotlin.math.pow
import kotlin.math.sin

// ────────────────────────────────────────────────────────────
// GlassAnimation — direct port of GlassAnimationView.swift.
//
// All coordinates live in the source SVG's 1024×1024 space and are scaled at
// render time by `s = min(width, height) / 1024`. Constants like 347, 740,
// and the bubble cx/r values can be cited interchangeably between iOS and
// Android because they refer to the same coordinate space.
//
// Six draw passes, in order:
//   1. Glass body fill            (white @ 0.06)
//   2. Clipped layer              — liquid + meniscus + bubbles
//   3. Glass body stroke          (white @ 0.25, width 4)
//   4. Glass rim highlight        (white @ 0.35, width 5, round caps)
//   5. Glass left-edge highlight  (white @ 0.10, width 8, round caps)
//   6. Glass surface gradient     (white 0.15 → 0 horizontally)
//
// The wave shape is achieved by shifting Bezier control points by
// `sin(t·2π)·9`, not by Y-offsetting a sampled curve.
// ────────────────────────────────────────────────────────────

private const val CYCLE_MS: Long = 1600L

// 1024-space constants, ported from GlassAnimationView.swift:40-43.
private const val LIQUID_TOP_BASE = 347f
private const val WAVE_AMPLITUDE = 9f
private const val BUBBLE_BOTTOM = 740f

/**
 * 4 bubbles matching the original SVG's cx positions and radii, with phases
 * spaced to avoid clustering at any frame. The S3 firmware has 8 bubbles but
 * the extra 4 small ones create an ugly row at frame 0.
 *
 * Mirrors GlassAnimationView.swift:50-55.
 */
private data class BubbleDef(
    val cx: Float,             // 1024-space x
    val r: Float,              // 1024-space radius
    val phase: Float,          // 0..1 — offset into the cycle
    val strokeOpacity: Float,
    val strokeWidth: Float,    // 1024-space; multiply by s at render time
)

private val bubbles = listOf(
    BubbleDef(cx = 440f, r = 42f, phase = 0.00f, strokeOpacity = 0.20f, strokeWidth = 2.5f),
    BubbleDef(cx = 580f, r = 35f, phase = 0.20f, strokeOpacity = 0.20f, strokeWidth = 2.5f),
    BubbleDef(cx = 500f, r = 30f, phase = 0.42f, strokeOpacity = 0.18f, strokeWidth = 2.0f),
    BubbleDef(cx = 620f, r = 26f, phase = 0.62f, strokeOpacity = 0.18f, strokeWidth = 2.0f),
)

@Composable
fun GlassAnimation(modifier: Modifier = Modifier) {
    // `withFrameMillis` is the direct analog of SwiftUI's `TimelineView(.animation)`
    // — both driven by the platform's display link / vsync.
    var elapsedMs by remember { mutableLongStateOf(0L) }
    LaunchedEffect(Unit) {
        val start = withFrameMillis { it }
        while (true) {
            withFrameMillis { now -> elapsedMs = now - start }
        }
    }
    val t = (elapsedMs % CYCLE_MS).toFloat() / CYCLE_MS  // 0..1

    Canvas(modifier = modifier.aspectRatio(1f)) {
        val s = min(size.width, size.height) / 1024f
        val glassPath = buildGlassPath(s)

        // 1. Glass body fill
        drawPath(path = glassPath, color = Color.White.copy(alpha = 0.06f))

        // 2. Clipped layer: liquid, surface highlight, bubbles
        clipPath(glassPath) {
            drawLiquid(t = t, s = s)
            drawSurfaceHighlightWave(t = t, s = s)
            drawBubbles(t = t, s = s)
        }

        // 3. Glass body stroke
        drawPath(
            path = glassPath,
            color = Color.White.copy(alpha = 0.25f),
            style = Stroke(width = 4f * s),
        )

        // 4. Glass rim highlight
        drawLine(
            color = Color.White.copy(alpha = 0.35f),
            start = Offset(310f * s, 247f * s),
            end = Offset(714f * s, 247f * s),
            strokeWidth = 5f * s,
            cap = StrokeCap.Round,
        )

        // 5. Glass left-edge highlight
        drawLine(
            color = Color.White.copy(alpha = 0.10f),
            start = Offset(314f * s, 257f * s),
            end = Offset(342f * s, 737f * s),
            strokeWidth = 8f * s,
            cap = StrokeCap.Round,
        )

        // 6. Glass surface gradient overlay (left-side highlight, fades to 0 by 40%)
        drawPath(
            path = glassPath,
            brush = Brush.linearGradient(
                colorStops = arrayOf(
                    0.0f to Color.White.copy(alpha = 0.15f),
                    0.4f to Color.White.copy(alpha = 0.0f),
                ),
                start = Offset(310f * s, 0f),
                end = Offset(714f * s, 0f),
            ),
        )
    }
}

// MARK: - Path builders

/**
 * Glass body path. Identical to the SVG `<path>` at AppIcon.svg:30.
 * Mirrors GlassAnimationView.swift:60-68.
 */
private fun buildGlassPath(s: Float): Path = Path().apply {
    moveTo(310f * s, 247f * s)
    lineTo(340f * s, 747f * s)
    quadraticTo(345f * s, 777f * s, 380f * s, 777f * s)
    lineTo(644f * s, 777f * s)
    quadraticTo(679f * s, 777f * s, 684f * s, 747f * s)
    lineTo(714f * s, 247f * s)
    close()
}

// MARK: - Liquid + surface highlight

/**
 * Liquid fill with the wavy top edge. The wave is achieved by shifting the
 * Bezier control points by `sin(t·2π)·9` — not by Y-offsetting a sampled
 * sine. Mirrors GlassAnimationView.swift:78-94.
 */
private fun DrawScope.drawLiquid(t: Float, s: Float) {
    val waveShift = sin(t * 2f * PI.toFloat()) * WAVE_AMPLITUDE
    val path = Path().apply {
        moveTo(300f * s, (347f + waveShift) * s)
        quadraticTo(
            400f * s, (327f + waveShift) * s,
            512f * s, (352f - waveShift) * s,
        )
        quadraticTo(
            624f * s, (377f - waveShift) * s,
            724f * s, (342f + waveShift) * s,
        )
        lineTo(724f * s, 800f * s)
        lineTo(300f * s, 800f * s)
        close()
    }

    drawPath(
        path = path,
        brush = Brush.linearGradient(
            colorStops = arrayOf(
                0.0f to Theme.liquidStop0,
                0.5f to Theme.liquidStop1,
                1.0f to Theme.liquidStop2,
            ),
            start = Offset(300f * s, 327f * s),
            end = Offset(724f * s, 800f * s),
        ),
    )
}

/**
 * The meniscus highlight — a 4-curve closed band that follows the liquid's
 * wavy top edge and the same wave shape ~20 units lower. Drawn on top of
 * the liquid with white @ 0.12 alpha. Mirrors GlassAnimationView.swift:110-131.
 */
private fun DrawScope.drawSurfaceHighlightWave(t: Float, s: Float) {
    val waveShift = sin(t * 2f * PI.toFloat()) * WAVE_AMPLITUDE
    val path = Path().apply {
        moveTo(300f * s, (347f + waveShift) * s)
        quadraticTo(
            400f * s, (327f + waveShift) * s,
            512f * s, (352f - waveShift) * s,
        )
        quadraticTo(
            624f * s, (377f - waveShift) * s,
            724f * s, (342f + waveShift) * s,
        )
        lineTo(724f * s, (367f + waveShift) * s)
        quadraticTo(
            624f * s, (397f - waveShift) * s,
            512f * s, (372f - waveShift) * s,
        )
        quadraticTo(
            400f * s, (347f + waveShift) * s,
            300f * s, (367f + waveShift) * s,
        )
        close()
    }
    drawPath(path = path, color = Color.White.copy(alpha = 0.12f))
}

// MARK: - Bubble physics + drawing

private data class BubbleState(
    val cx: Float,
    val cy: Float,
    val r: Float,
    val opacity: Float,
)

/**
 * Bubble physics. Three regions per cycle:
 *   - bt < 0.75 — rising with ease-out, growing 0..15%, lateral wobble.
 *   - bt < 0.85 — popping at the surface, shrinking from 1.15× to 0.65×, fading.
 *   - else      — invisible (respawn delay).
 *
 * Mirrors GlassAnimationView.swift:192-217.
 */
private fun computeBubble(b: BubbleDef, t: Float): BubbleState? {
    val bt = ((t + b.phase) % 1f + 1f) % 1f  // wrap to [0, 1)
    val bubbleTop = LIQUID_TOP_BASE + b.r + WAVE_AMPLITUDE

    return when {
        bt < 0.75f -> {
            val riseT = bt / 0.75f
            val easeT = 1f - (1f - riseT).pow(1.5f)
            val cy = BUBBLE_BOTTOM - easeT * (BUBBLE_BOTTOM - bubbleTop)
            val cx = b.cx + 8f * sin(riseT * PI.toFloat() * 3f + b.phase * 10f)
            val r = b.r * (1.0f + 0.15f * riseT)
            BubbleState(cx = cx, cy = cy, r = r, opacity = 0.8f)
        }
        bt < 0.85f -> {
            val popT = (bt - 0.75f) / 0.10f
            val r = b.r * (1.15f - 0.5f * popT)
            BubbleState(cx = b.cx, cy = bubbleTop, r = r, opacity = 0.8f * (1f - popT))
        }
        else -> null
    }
}

private fun DrawScope.drawBubbles(t: Float, s: Float) {
    for (b in bubbles) {
        val state = computeBubble(b, t) ?: continue

        // iOS clips the bubble draw to "cy in (250, 780)" — anything outside
        // the glass interior (rim and floor) is skipped. The clipPath above
        // already contains the rendering, but this preserves the iOS guard
        // in case the glass path ever changes.
        if (state.cy <= 250f || state.cy >= 780f) continue

        val center = Offset(state.cx * s, state.cy * s)
        val radius = state.r * s

        // Radial gradient fill (white @ 0.5 → 0.1 inner-to-edge), with the
        // bubble's per-frame `opacity` folded in. iOS achieves this with a
        // drawLayer + ctx.opacity; Compose folds it into each color's alpha.
        drawCircle(
            brush = Brush.radialGradient(
                colorStops = arrayOf(
                    0.0f to Color.White.copy(alpha = 0.5f * state.opacity),
                    1.0f to Color.White.copy(alpha = 0.1f * state.opacity),
                ),
                center = center,
                radius = radius,
            ),
            radius = radius,
            center = center,
        )

        drawCircle(
            color = Color.White.copy(alpha = b.strokeOpacity * state.opacity),
            radius = radius,
            center = center,
            style = Stroke(width = b.strokeWidth * s),
        )
    }
}
