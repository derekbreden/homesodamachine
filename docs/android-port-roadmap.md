# Android Port Roadmap

The plan for porting the iOS companion app (SwiftUI, ~3.5K LOC) to Android with identical UX. Native Kotlin + Jetpack Compose. Two iOS polish milestones precede the Android work so the labels and haptics get designed once and ported across.

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

The line-for-line ports: `Theme.swift`, `GlassAnimationView.swift`, `ImageProcessor.swift`, the binary frame parser inside `BLEManager.swift`. The piece needing real translation: `StatsSheet`'s charts (Compose has no first-party Swift Charts equivalent — Vico or hand-rolled `Canvas` bars).

Alternatives rejected:

- **Flutter** — would render the glass animation fine, but draws system UI through Skia rather than using Android's actual widgets. Ambient feel (system fonts, ripple touch feedback, modal physics) deviates in ways the polish bar will catch.
- **React Native** — animation polish is harder; BLE bridges add latency.
- **KMP** — valid but doubles build complexity for a 3.5K-LOC codebase that already exists in Swift. KMP wins for parallel new development of two apps from scratch, not this situation.
- **Native Java** — outdated; Kotlin is the standard.

## Milestone 0a — iOS Accessibility

Half a day. Seven specific additions, not "labels everywhere."

1. **Glass animation is decorative** — wrap every use of `GlassAnimationView` with `.accessibilityHidden(true)`. The loading state is conveyed by the status text below; making VoiceOver announce "image" twice (onboarding + scanning) is noise. See `ios/SodaMachine/SodaMachine/Views/ScanView.swift:51` and `:108`.
2. **Status text is a live region** — the `Text(...)` in `ScanView` showing "Searching for hardware…" / "Connecting…" (`ScanView.swift:140-168`) gets `.accessibilityAddTraits(.updatesFrequently)`. Without this, VoiceOver users hear scan-start once and never the connection landing.
3. **Hold-to-Prime hint** — VoiceOver users can't easily long-press. The button at `ConfigView.swift:486` gets:
   ```swift
   .accessibilityLabel("Prime flavor \(flavor)")
   .accessibilityHint("Touch and hold to dispense priming fluid; release to stop.")
   ```
   The hint is the only place to communicate the unusual interaction model.
4. **Image carousel cells use the actual flavor name** — `.accessibilityLabel(imageNames[slot])` instead of generic "image, button". The data is already in `ble.imageNames`.
5. **Carousel pages are named** — the 5-page `TabView` (`ConfigView.swift:1313`) gets `.accessibilityLabel("Page \(currentPage + 1) of 5: \(pageName)")` per page, names: "Flavor 1 image", "Flavor 1 ratio", "Flavor 2 image", "Flavor 2 ratio", "Settings".
6. **Ratio wheel reads as ratio, not number** — `.accessibilityValue("1 to \(ratio)")` on the picker (`ConfigView.swift:254-295`). Reading "20" without context is wrong.
7. **Chart bars get a value description** — Swift Charts in `StatsSheet` get per-bar `.accessibilityValue("\(flavor1Oz) ounces flavor 1, \(flavor2Oz) ounces flavor 2")`. Default chart accessibility reads raw numbers without units.

Explicitly **not** doing: localizing strings, custom rotor actions, custom VoiceOver layouts, per-bubble labels, dynamic-type sizing of the glass canvas. Overshoot.

## Milestone 0b — iOS Haptics

One hour. Earned moments only — two definite, one rejected.

1. **Hold-to-Prime activation** — at `ConfigView.swift:495-506`, in the `DragGesture.onChanged` handler, fire heavy impact exactly once when `primeActive` first becomes true:
   ```swift
   UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
   ```
   Heavy because the user is initiating a physical machine action. **Don't** haptic on release — the absence of dispensing *is* the feedback.
2. **Connection lands** — when `connectionState` transitions to `.connected`, fire success once. This is the "found it" moment. Best site: `BLEManager.swift:1443-1446` so it fires regardless of which view is mounted:
   ```swift
   UINotificationFeedbackGenerator().notificationOccurred(.success)
   ```
3. **Factory reset** — considered, rejected. The visual confirmation already feels weighty; haptic-celebrating a destructive action is style noise.

Explicitly **not** doing: tap haptics on regular buttons, swipe haptics on the carousel, increment haptics on the ratio wheel. iOS pickers already self-haptic; everything else would be noise on a small surface.

## Milestone 1 — Android phase 1: splash + glass-animation handoff

3–4 days. Cold-launch on a real Android device feels right. Static splash → animated glass with no perceptible gap. No BLE, no other UI yet — just the launch sequence, perfected.

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

Line-for-line port of `ios/SodaMachine/SodaMachine/Views/GlassAnimationView.swift`. The skeleton showing the structure (the inner `drawGlassBody` / `drawLiquid` / `drawBubbles` are where the polish time goes):

```kotlin
package net.truce.sodamachine.ui.glass

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
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
    val t = (elapsedMs % CYCLE_MS).toFloat() / CYCLE_MS  // 0..1, matches GlassAnimationView line 24

    Canvas(modifier = modifier.size(200.dp)) {
        drawGlassBody()                  // strokes, opacity 0.25 / 0.35 / 0.10
        drawLiquid(t)                    // sin wave, amplitude 9, period 1.6 s
        drawBubbles(t)                   // 4 bubbles, rise [0..0.75] easeOut, pop [0.75..0.85]
        drawGlassHighlights()            // rim + edge
    }
}

// Bubble model — 4 instances matching GlassAnimationView:50-55
private data class Bubble(val xCenter: Float, val phase: Float, val radius: Float)
private val bubbles = listOf(
    Bubble(xCenter = 0.50f, phase = 0.00f, radius = 6f),
    Bubble(xCenter = 0.42f, phase = 0.30f, radius = 5f),
    Bubble(xCenter = 0.58f, phase = 0.55f, radius = 7f),
    Bubble(xCenter = 0.48f, phase = 0.80f, radius = 4f),
)

// Drawing functions ported from GlassAnimationView.swift:60-188 line-for-line.
// Liquid wave:    y = baseline + 9 * sin(t * 2 * PI)                                 (line 78)
// Bubble rise:    riseT = bt / 0.75; y = bottom - (top-bottom) * (1 - (1-riseT).pow(1.5))   (line 201)
// Bubble pop:     popT = (bt - 0.75) / 0.10; alpha = 0.8 * (1 - popT)                (line 211)
// Lateral wobble: x += 8 * sin(riseT * PI * 3 + bubble.phase * 10)                   (line 203)
private fun androidx.compose.ui.graphics.drawscope.DrawScope.drawGlassBody() { /* ... */ }
private fun androidx.compose.ui.graphics.drawscope.DrawScope.drawLiquid(t: Float) { /* ... */ }
private fun androidx.compose.ui.graphics.drawscope.DrawScope.drawBubbles(t: Float) { /* ... */ }
private fun androidx.compose.ui.graphics.drawscope.DrawScope.drawGlassHighlights() { /* ... */ }
```

The `withFrameMillis` loop is the direct analog of SwiftUI's `TimelineView(.animation)` — both driven by the platform's display link / vsync. This is what gets the same 60–120 fps motion.

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

| # | Milestone | Where | Time |
|---|---|---|---|
| **M0a** | iOS accessibility (7 specific items) | iOS app | half a day |
| **M0b** | iOS haptics (2 earned moments) | iOS app | one hour |
| **M1** | Android: splash + glass handoff | Android phase 1 | 3–4 days |
| M2 | Android: theme polish + ScanView wired (no BLE yet) | Android phase 2 | 2–3 days |
| M3 | Android: BLE layer + binary protocol + demo mode | Android phase 3 | 1–2 weeks |
| M4 | Android: image processing (median-cut, RGB565, CRC32) | Android phase 4 | 2–3 days |
| M5 | Android: ConfigView carousel + 7 sheets | Android phase 5 | 1–2 weeks |
| M6 | Android: charts (Vico or hand-rolled Canvas) | Android phase 6 | 3–5 days |
| M7 | Side-by-side polish QA against iPhone | both platforms | 1 week |
| M8 | Android: accessibility + haptics (mirror M0a/M0b) | Android | half a day |

M0a and M0b are pre-Android because doing them first lets the fully-considered iOS labels and haptics carry across to Android in M8 — designed once, ported, not designed twice.
