# Android Port Roadmap

The plan for porting the iOS companion app (SwiftUI, ~3.5K LOC) to Android with identical UX. Native Kotlin + Jetpack Compose. Three iOS polish milestones precede the Android work so the theme, accessibility labels, and haptic moments are settled in one place before being mirrored on Android.

## Why Compose

Compose is a near-1:1 mental model of SwiftUI. The mappings that matter for this app:

| iOS / SwiftUI | Compose equivalent |
|---|---|
| `Canvas { ctx, size in ... Path() ... }` | `Canvas { drawPath(...) }` — same semantics, same Path API |
| `TimelineView(.animation)` (the 1.6 s glass loop) | `withFrameMillis` inside `LaunchedEffect` — also frame-driven |
| `withAnimation(.easeInOut(duration: 0.2))` | `animateFloatAsState(animationSpec = tween(200, easing = FastOutSlowInEasing))` |
| `@Observable class` + `@Environment` | `class` exposing `StateFlow`s + `CompositionLocal` |
| `TabView(...).tabViewStyle(.page)` | `HorizontalPager` |
| `.sheet { }` | `ModalBottomSheet` |
| `LaunchScreen.storyboard` | `androidx.core:core-splashscreen` |
| `UserDefaults` | `DataStore` |
| CoreBluetooth | Nordic's `Android-BLE-Library` |

The line-for-line ports: `Theme.swift`, `GlassAnimationView.swift`, `ImageProcessor.swift`, the binary frame parser inside `BLEManager.swift`. The piece needing real translation: `StatsSheet`. Compose has no first-party Swift Charts equivalent — three bar charts can use Vico or hand-rolled `Canvas` bars, but the pie chart (`SectorMark` with inner radius for the 30-day flavor split) and the serving-size selector (three glass icons drawn with the SVG glass path at 12oz / 16oz / 20oz heights) are hand-rolled regardless.

Alternatives rejected:

- **Flutter** — would render the glass animation fine, but draws system UI through Skia rather than using Android's actual widgets. Ambient feel (system fonts, ripple touch feedback, modal physics) deviates in ways the polish bar will catch.
- **React Native** — animation polish is harder; BLE bridges add latency.
- **KMP** — valid but doubles build complexity for a 3.5K-LOC codebase that already exists in Swift. KMP wins for parallel new development of two apps from scratch, not this situation.
- **Native Java** — outdated; Kotlin is the standard.

## Milestone -1 — iOS Theme consolidation *(landed)*

Pull `primeBlue`, `chartPink`, `chartPurple` (file-scoped private constants in `ConfigView.swift`) and the three liquid-gradient stops (RGB literals inline in `GlassAnimationView`'s draw code) into `Theme.swift`. One source of truth on iOS, mirrors the structure the Android port will use. Pure refactor, no behavior change.

## Milestone 0a — iOS Accessibility *(landed)*

Six additions. No accessibility-only branches — the same UI works for sighted and VoiceOver users.

1. **Glass animation is decorative** — `.accessibilityHidden(true)` on every use of `GlassAnimationView`. Loading state is conveyed by the status text below; announcing "image" twice (onboarding + scanning) is noise. Sites: `ScanView.swift` onboarding + animatedSearchView.
2. **Status text is a live region** — `.accessibilityAddTraits(.updatesFrequently)` on each branch of `statusContent` so VoiceOver re-polls when connection state changes. Drop the 3-second `searchTextIndex` rotation between two near-identical messages — the animation already conveys the "still working" signal that the rotation was added to provide, and rotating text adds noise without information for everyone.
3. **Hold-to-Prime label + hint + button trait** — the Text-with-DragGesture at `ConfigView.swift` PrimeSheet gets:
   ```swift
   .accessibilityLabel(ble.primeActive ? "Priming flavor \(flavor)" : "Prime flavor \(flavor)")
   .accessibilityHint("Touch and hold to dispense priming fluid; release to stop.")
   .accessibilityAddTraits(.isButton)
   ```
   The hint communicates the unusual interaction model. VoiceOver double-tap won't trigger priming (hold-only is a safety mechanism for a real machine pumping fluid); a custom `accessibilityAction` for VO-friendly priming is a deliberate non-goal here.
4. **Carousel pages 0–3 are a single VO button each** — outer container gets `.accessibilityElement(children: .combine)` + `"Page \(i + 1) of \(pageCount): \(pageLabels[i])"` label + `.isButton` trait + a hint to double-tap to change image/ratio. The existing `.onTapGesture` fires on VO double-tap. Page 4 (Settings) keeps its inner buttons individually navigable. Refactored the inline `ForEach` into a private `carouselPage(for:)` to hold the per-page conditional accessibility shape cleanly.
5. **Ratio wheel reads as ratio, not number** — `.accessibilityLabel("1 to \(value)")` on each row in the picker `ForEach`, plus `.accessibilityLabel(flavorLabel)` on the picker so the wheel announces "Flavor 1 Ratio" as context.
6. **Chart bars get a per-position value description** — each `BarMark` pair in `Chart24HView` / `Chart30DView` / `ChartHODView` is wrapped in a `Plot { ... }` with combined accessibility:
   ```swift
   .accessibilityLabel(hourLabel(...))
   .accessibilityValue("0.5 servings of Flavor 1, 0.25 of Flavor 2")
   ```
   Units are *servings* (output of `toServings()` driven by the 12/16/20oz selector), not ounces. Pie chart is `.accessibilityHidden(true)` since the data is in the legend; legend images get `"Flavor N: P percent"` labels via `.accessibilityElement(children: .ignore)`.

Explicitly **not** doing: localizing strings, custom rotor actions, custom VoiceOver layouts, per-bubble labels, dynamic-type sizing of the glass canvas. Overshoot.

Explicitly **dropped**: per-image accessibility labels in the picker. The existing `imageNames` are storage IDs (`diet_wild_cherry_pepsi`, `image_3`), not display names; users aren't required to label their uploads, so no real source exists. The page-level naming above is enough orientation.

## Milestone 0b — iOS Haptics *(landed)*

One earned moment.

**Hold-to-Prime activation** — in the `DragGesture.onChanged` handler, fire medium impact exactly once at the start of priming:
```swift
UIImpactFeedbackGenerator(style: .medium).impactOccurred()
```

The HIG documents Impact-Medium for "medium-sized or medium-weight UI objects" — a conservative read for "real machine engages." Heavy is a stretch as a metaphor for this control; medium is the honest choice. Don't haptic on release — the absence of dispensing *is* the feedback.

**Explicitly rejected:**

- **Connection lands** — the user opens the app and may set the phone down; the BLE connect happens automatically without their direct involvement. The HIG's Notification-Success documents "task or action that has completed" (Apple's examples: depositing a check, unlocking a vehicle — both user-initiated and user-awaited). Firing a success haptic for a background-completed connect is exactly the "using a pattern to mean something else" the HIG warns against, and contributes to the "overuse" pattern the HIG also warns against. So no haptic on connect.
- **Factory reset** — visual confirmation already feels weighty; haptic-celebrating a destructive action is style noise.
- **Tap haptics on regular buttons, swipe haptics on the carousel, increment haptics on the ratio wheel.** iOS pickers self-haptic; everything else would be noise on a small surface.

User opt-out is free — `UIImpactFeedbackGenerator` respects the iOS system-level toggle (Settings → Sounds & Haptics → System Haptics).

## Milestone 1 — Android phase 1: splash + glass-animation handoff

Cold-launch on a real Android device feels right. Static splash → animated glass with no perceptible gap. No BLE, no other UI yet — just the launch sequence, perfected.

### Project skeleton

```
android/
├── settings.gradle.kts
├── build.gradle.kts
├── gradle/libs.versions.toml
└── app/
    ├── build.gradle.kts
    └── src/main/
        ├── AndroidManifest.xml
        ├── kotlin/net/truce/sodamachine/
        │   ├── MainActivity.kt
        │   ├── App.kt
        │   └── ui/
        │       ├── theme/Theme.kt
        │       ├── glass/GlassAnimation.kt
        │       └── scan/ScanView.kt
        └── res/
            ├── values/{colors,strings,themes}.xml
            └── drawable/launch_icon.xml
```

### Versions (`gradle/libs.versions.toml`)

```toml
[versions]
agp                  = "8.7.3"
kotlin               = "2.1.0"
compose-bom          = "2025.01.00"
core-splashscreen    = "1.0.1"
activity-compose     = "1.10.0"
nordic-ble           = "2.7.5"     # phase 3
datastore            = "1.1.1"     # phase 3

[libraries]
androidx-core-splashscreen = { module = "androidx.core:core-splashscreen", version.ref = "core-splashscreen" }
androidx-activity-compose  = { module = "androidx.activity:activity-compose", version.ref = "activity-compose" }
compose-bom                = { module = "androidx.compose:compose-bom",       version.ref = "compose-bom" }
compose-ui                 = { module = "androidx.compose.ui:ui" }
compose-ui-graphics        = { module = "androidx.compose.ui:ui-graphics" }
compose-foundation         = { module = "androidx.compose.foundation:foundation" }
compose-material3          = { module = "androidx.compose.material3:material3" }
```

Build settings: Min SDK 26 (Android 8, ~99 % device coverage in 2026, simplifies Bluetooth permission paths since only the API 31+ split for runtime perms is needed), Target SDK 35, Kotlin 2.1, Compose Compiler via the Kotlin Compose Compiler Gradle plugin (no separate compiler version).

### The splash → Compose handoff

iOS `LaunchScreen.storyboard` → first Compose frame analog. The OS holds the splash icon until Compose's first frame is drawn. Zero gap.

`res/values/colors.xml`:
```xml
<color name="splash_bg">#FF1A1A2E</color>
```

`res/values/themes.xml`:
```xml
<style name="Theme.App.Splash" parent="Theme.SplashScreen">
    <item name="windowSplashScreenBackground">@color/splash_bg</item>
    <item name="windowSplashScreenAnimatedIcon">@drawable/launch_icon</item>
    <item name="postSplashScreenTheme">@style/Theme.App</item>
</style>
<style name="Theme.App" parent="android:Theme.Material.NoActionBar">
    <item name="android:windowBackground">@color/splash_bg</item>
    <item name="android:statusBarColor">@color/splash_bg</item>
    <item name="android:navigationBarColor">@color/splash_bg</item>
</style>
```

`AndroidManifest.xml` (relevant bits):
```xml
<application android:theme="@style/Theme.App.Splash" ...>
    <activity android:name=".MainActivity" android:exported="true"
              android:theme="@style/Theme.App.Splash">
        <intent-filter>
            <action android:name="android.intent.action.MAIN"/>
            <category android:name="android.intent.category.LAUNCHER"/>
        </intent-filter>
    </activity>
</application>
```

`MainActivity.kt`:
```kotlin
package net.truce.sodamachine

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}
```

The OS holds the static icon until Compose's first frame paints — and Compose's first frame *is* `GlassAnimation`'s first drawn frame. No intermediate state, no flash, no `setKeepOnScreenCondition` needed.

### Theme port

Direct port of `ios/SodaMachine/SodaMachine/Theme.swift`:

```kotlin
package net.truce.sodamachine.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

object Theme {
    val background      = Color(0xFF1A1A2E)
    val textPrimary     = Color.White
    val textSecondary   = Color(0xFF999999)
    val dotActive       = Color.White
    val dotInactive     = Color(0xFF595959)
    val placeholder     = Color(0xFF333333)
    val primeBlue       = Color(0xFF4485FF)
    val chartPink       = Color(0xFFE64D80)
    val chartPurple     = Color(0xFF994DE5)

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
```

### `GlassAnimation.kt` — the phase-1 deliverable

Line-for-line port of `ios/SodaMachine/SodaMachine/Views/GlassAnimationView.swift`. The actual file is more involved than a "draw a glass with a sine wave" sketch — six distinct draw passes, one of which is a clipped layer, plus a wave generated by shifting Bezier control points (not by Y-offsetting a sampled curve) and bubbles with grow/shrink phases. The Kotlin port preserves all of that.

**Coordinate system.** All coordinates are in the source SVG's 1024×1024 space, scaled at render time by `s = min(width, height) / 1024f`. Don't normalize to 0..1 fractions — the constants below (bubble cx, liquid baseline, glass path nodes) are read directly off the SVG, and inheriting that space lets the Android and iOS sides cite the same numbers when iterating on shape.

**Six draw passes**, in order. Each maps to a contiguous block in `GlassAnimationView.draw`:

1. Glass body fill — `Color.White.copy(alpha = 0.06f)` over the closed glass path.
2. **Clipped layer** containing the liquid + surface highlight wave + bubbles, clipped to the glass path. In Compose: `clipPath(glassPath) { ... }` inside the `DrawScope`. Skipping this clip lets the bubbles and liquid spill outside the glass walls.
3. Glass body stroke — opacity 0.25, width `4*s`.
4. Glass rim highlight — opacity 0.35, width `5*s`, round caps, top edge only.
5. Glass left-edge highlight — opacity 0.10, width `8*s`, round caps.
6. Glass surface gradient overlay — top-down white linear gradient (alpha 0.15 → 0) over the closed glass path.

**Liquid wave.** A two-`addQuadCurve` Bezier path traces the wavy top edge. The wave is achieved by shifting the path's *control points* by `waveShift = sin(t * 2π) * 9` (in 1024-space units). Don't sample a sine into Y-offsets — the curve is a Bezier whose control point Y values move. The "surface highlight wave" in pass 2 is a separate 4-curve closed shape (the meniscus highlight) drawn on top of the liquid with `Color.White.copy(alpha = 0.12f)`.

**Bubble model.** Four bubbles, in 1024-space coords:

```kotlin
private data class Bubble(
    val cx: Float,            // 1024-space x
    val r: Float,             // 1024-space radius
    val phase: Float,         // 0..1 — offset into the cycle
    val strokeOpacity: Float,
    val strokeWidth: Float,   // 1024-space; multiply by s at render
)
private val bubbles = listOf(
    Bubble(cx = 440f, r = 42f, phase = 0.00f, strokeOpacity = 0.20f, strokeWidth = 2.5f),
    Bubble(cx = 580f, r = 35f, phase = 0.20f, strokeOpacity = 0.20f, strokeWidth = 2.5f),
    Bubble(cx = 500f, r = 30f, phase = 0.42f, strokeOpacity = 0.18f, strokeWidth = 2.0f),
    Bubble(cx = 620f, r = 26f, phase = 0.62f, strokeOpacity = 0.18f, strokeWidth = 2.0f),
)
```

Constants used throughout: `liquidTopBase = 347f`, `waveAmplitude = 9f`, `bubbleBottom = 740f`. Bubble top (in 1024-space) is `liquidTopBase + r + waveAmplitude`.

**Bubble physics.** Each bubble's local time is `bt = (t * speed + phase) mod 1`. Three regions:

```
RISING  (bt < 0.75):
    riseT = bt / 0.75
    easeT = 1 - (1 - riseT).pow(1.5)
    cy    = bubbleBottom - easeT * (bubbleBottom - bubbleTop)   // bubble rises
    cx    = bubble.cx + 8 * sin(riseT * PI * 3 + bubble.phase * 10)
    radius = r * (1 + 0.15 * riseT)                              // grows on the way up
    opacity = 0.8

POPPING (0.75 ≤ bt < 0.85):
    popT  = (bt - 0.75) / 0.10
    cy    = bubbleTop                                            // pinned at surface
    cx    = bubble.cx
    radius = r * (1.15 - 0.5 * popT)                             // shrinks while popping
    opacity = 0.8 * (1 - popT)

INVISIBLE (bt ≥ 0.85): skip the bubble for this frame
```

Each visible bubble draws as: a radial-gradient fill (white 0.5 → 0.1 inner-to-edge, scaled by the per-frame `opacity`) plus a stroke at the bubble's `strokeOpacity` and `strokeWidth * s`. Render only when `cy` is between 250 and 780 in 1024-space (inside the glass).

**Skeleton.**

```kotlin
package net.truce.sodamachine.ui.glass

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.clipPath
import androidx.compose.ui.unit.dp
import kotlin.math.*

private const val CYCLE_MS = 1600L

@Composable
fun GlassAnimation(modifier: Modifier = Modifier) {
    var elapsedMs by remember { mutableLongStateOf(0L) }
    LaunchedEffect(Unit) {
        val start = withFrameMillis { it }
        while (true) {
            withFrameMillis { now -> elapsedMs = now - start }
        }
    }
    val t = (elapsedMs % CYCLE_MS).toFloat() / CYCLE_MS

    Canvas(modifier = modifier.size(200.dp)) {
        val s = min(size.width, size.height) / 1024f
        val glassPath = buildGlassPath(s)

        drawGlassBodyFill(glassPath)                       // pass 1
        clipPath(glassPath) {                              // pass 2
            drawLiquid(t, s)
            drawSurfaceHighlightWave(t, s)
            drawBubbles(t, s)
        }
        drawGlassBodyStroke(glassPath, s)                  // pass 3
        drawGlassRimHighlight(s)                           // pass 4
        drawGlassLeftEdgeHighlight(s)                      // pass 5
        drawGlassSurfaceGradient(glassPath, s)             // pass 6
    }
}
```

The `withFrameMillis` loop is the direct analog of SwiftUI's `TimelineView(.animation)` — both driven by the platform's display link / vsync.

### `ScanView.kt` phase-1 stub

Renders the glass + onboarding layout, no BLE wired (that's phase 3):

```kotlin
@Composable
fun ScanView() {
    Surface(color = Theme.background, modifier = Modifier.fillMaxSize()) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
            modifier = Modifier.fillMaxSize().padding(24.dp),
        ) {
            GlassAnimation()
            Spacer(Modifier.height(48.dp))
            Text(
                text = "Soda Machine",
                color = Theme.textPrimary,
                fontSize = 28.sp,
                fontWeight = FontWeight.Medium,
            )
            Spacer(Modifier.height(16.dp))
            Button(onClick = { /* phase 3: BLE init */ }) {
                Text("Scan for Hardware")
            }
        }
    }
}
```

### `App.kt`

```kotlin
@Composable
fun App() {
    SodaMachineTheme { ScanView() }
}
```

### Phase-1 acceptance criteria

The phase is done when:

1. **Cold launch on a real device feels right.** Tested on at least one Android 14+ device (Pixel) and one older Android 9–11 device to verify the splash transition. Side-by-side with iPhone, the static-→-animated handoff timing is indistinguishable to the eye.
2. **Frame rate is locked to display refresh.** Verified via Android Studio Profiler — no dropped frames during the 1.6 s loop at 60 Hz on the lowest-end target device, 120 Hz on Pixel 8/9.
3. **Glass animation is pixel-equivalent to iOS.** 30-second screen recordings of both, frame-stepped, compared. Bubble timing, liquid amplitude, gradient stops, glass strokes all match.
4. **No work done off-spec.** No BLE code, no settings UI, no permissions — those are phase 3+. Phase 1 ships when launch feels right and nothing else.

## Full milestone list

| # | Milestone | Where | Status |
|---|---|---|---|
| **M-1** | iOS: pull scattered colors into Theme.swift | iOS app | landed |
| **M0a** | iOS accessibility (6 additions, no per-image labels) | iOS app | landed |
| **M0b** | iOS haptic — medium impact at Hold-to-Prime engage | iOS app | landed |
| **M1** | Android: splash + glass handoff | Android phase 1 | landed |
| M2 | Android: theme polish + ScanView wired (no BLE yet) | Android phase 2 | next |
| M3 | Android: BLE layer + binary protocol + demo mode | Android phase 3 | |
| M4 | Android: image processing (median-cut, RGB565, CRC32) | Android phase 4 | |
| M5 | Android: ConfigView carousel + 7 sheets | Android phase 5 | |
| M6 | Android: stats sheet — pie + 3 bar charts + serving-size selector | Android phase 6 | |
| M7 | Side-by-side polish QA against iPhone | both platforms | |
| M8 | Android: accessibility + haptics (mirror M0a/M0b) | Android | |

M-1, M0a, M0b were pre-Android so the fully-considered iOS labels, haptics, and theme structure carry across to Android in M8 — designed once, ported, not designed twice. M6 is heavier than billed in earlier drafts: in addition to three bar charts (24h, 30d, hour-of-day), `StatsSheet` also includes a pie chart for the 30-day flavor split (no first-party `SectorMark` equivalent in Compose — hand-rolled regardless of Vico) and a custom serving-size selector that draws three glass icons at 12oz / 16oz / 20oz heights with the SVG glass path.
