# Android Port Roadmap

The plan for porting the iOS companion app (SwiftUI, ~3.5K LOC) to Android with identical UX. Native Kotlin + Jetpack Compose. Three iOS polish milestones precede the Android work so the theme, accessibility labels, and haptic moments are settled in one place before being mirrored on Android.

## Why Compose

Compose is a near-1:1 mental model of SwiftUI. The mappings that matter for this app:

| iOS / SwiftUI | Compose equivalent |
|---|---|
| `Canvas { ctx, size in ... Path() ... }` | `Canvas { drawPath(...) }` — same semantics, same Path API |
| `TimelineView(.periodic(from:by:))` (Your machines re-reads its sightings every 5 s) | a `LaunchedEffect` loop around `delay` — the same clock |
| `withAnimation(.easeInOut(duration: 0.2))` | `animateFloatAsState(animationSpec = tween(200, easing = FastOutSlowInEasing))` |
| `@Observable class` + `@Environment` | `class` exposing `StateFlow`s + `CompositionLocal` |
| `TabView(...).tabViewStyle(.page)` | `HorizontalPager` |
| `.sheet { }` | `ModalBottomSheet` |
| `LaunchScreen.storyboard` | `androidx.core:core-splashscreen` |
| `UserDefaults` | `DataStore` |
| CoreBluetooth | Nordic's `Android-BLE-Library` |

The line-for-line ports: `Theme.swift`, `ImageProcessor.swift`, the binary frame parser inside `BLEManager.swift`. The piece needing real translation: `StatsSheet`. Compose has no first-party Swift Charts equivalent — three bar charts can use Vico or hand-rolled `Canvas` bars, but the pie chart (`SectorMark` with inner radius for the 30-day flavor split) and the serving-size selector (three glass icons drawn with the SVG glass path at 12oz / 16oz / 20oz heights) are hand-rolled regardless.

Alternatives rejected:

- **Flutter** — would render the custom drawing fine, but draws system UI through Skia rather than using Android's actual widgets. Ambient feel (system fonts, ripple touch feedback, modal physics) deviates in ways the polish bar will catch.
- **React Native** — animation polish is harder; BLE bridges add latency.
- **KMP** — valid but doubles build complexity for a 3.5K-LOC codebase that already exists in Swift. KMP wins for parallel new development of two apps from scratch, not this situation.
- **Native Java** — outdated; Kotlin is the standard.

## Milestone -1 — iOS Theme consolidation *(landed)*

`Theme.swift` holds the Big Blue palette — cobalt, navy, ice, orange — and the roles the views draw with: background, surface, text, accent, the two flavor chart series. One source of truth on iOS, mirrored by `ui/theme/Theme.kt` on Android.

## Milestone 0a — iOS Accessibility *(landed)*

Six additions. No accessibility-only branches — the same UI works for sighted and VoiceOver users.

1. **The mark is decorative** — `.accessibilityHidden(true)` on `MarkHeader` in `Theme.swift` and on the smaller mark `AddMachineView.swift` draws as a sheet. The text beside it names the screen; announcing "image" on every screen that opens with the mark is noise.
2. **Status text is a live region** — `.accessibilityAddTraits(.updatesFrequently)` on the Bluetooth-off message in `AddMachineView.swift` and on the link line in `MachinePage.swift`, so VoiceOver re-reads them when connection state changes. Each state shows one message; nothing rotates between near-identical messages, which would add noise without information for everyone.
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

Explicitly **not** doing: localizing strings, custom rotor actions, custom VoiceOver layouts. Overshoot.

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

## Milestone 1 — Android phase 1: splash + first-frame handoff

Cold-launch on a real Android device feels right. The OS splash shows the static faucet mark over cobalt, and the first Compose frame draws the same mark in the same place, so the handoff cannot be seen. No BLE, no other UI yet — just the launch sequence, perfected.

### Project skeleton

```
android/
├── settings.gradle.kts
├── build.gradle.kts
├── gradle.properties
├── gradle/libs.versions.toml
└── app/
    ├── build.gradle.kts
    └── src/main/
        ├── AndroidManifest.xml
        ├── kotlin/net/truce/sodamachine/
        │   ├── MainActivity.kt
        │   ├── App.kt
        │   ├── ble/BleManager.kt
        │   └── ui/
        │       ├── theme/Theme.kt
        │       └── scan/ScanView.kt
        └── res/
            ├── values/{colors,strings,themes}.xml
            ├── drawable/{launch_icon,ic_launcher_foreground}.xml
            └── mipmap-anydpi-v26/{ic_launcher,ic_launcher_round}.xml
```

[`tools/build_brand_assets.py`](/tools/build_brand_assets.py) writes `colors.xml`, both drawables and both adaptive-icon files from [`brand/mark.svg`](/brand/mark.svg) and `brand/palette.json`.

### Versions

`gradle/libs.versions.toml` pins AGP, Kotlin, the Compose BOM, `core-splashscreen` and `activity-compose`, with Nordic's BLE library and DataStore staged for phase 3.

Build settings: Min SDK 26 (Android 8, ~99 % device coverage in 2026, simplifies Bluetooth permission paths since only the API 31+ split for runtime perms is needed), compile and target SDK 36. AGP drives the Kotlin compiler itself; the Compose Compiler comes from the Kotlin Compose Compiler Gradle plugin (no separate compiler version).

### The splash → Compose handoff

iOS `LaunchScreen.storyboard` → first Compose frame analog. The OS holds the splash icon until Compose's first frame is drawn. Zero gap.

`res/values/colors.xml`:
```xml
<!-- Generated from brand/palette.json by tools/build_brand_assets.py. -->
<color name="splash_bg">#1749D1</color>
```

`res/drawable/launch_icon.xml` is a 288 dp vector of the faucet path in ice and the drop in orange, scaled 0.7 about its centre so the whole mark sits inside the splash's 192 dp icon circle.

`res/values/themes.xml` puts `launch_icon` over `splash_bg`, pins the status and navigation bars to `splash_bg` so the splash is cobalt edge to edge, and hands over to `Theme.App`, whose window background is `splash_bg` too:
```xml
<style name="Theme.App.Splash" parent="Theme.SplashScreen">
    <item name="windowSplashScreenBackground">@color/splash_bg</item>
    <item name="windowSplashScreenAnimatedIcon">@drawable/launch_icon</item>
    <item name="postSplashScreenTheme">@style/Theme.App</item>
    <item name="android:statusBarColor">@color/splash_bg</item>
    <item name="android:navigationBarColor">@color/splash_bg</item>
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
import android.graphics.Color
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.dark(Color.TRANSPARENT),
            navigationBarStyle = SystemBarStyle.dark(Color.TRANSPARENT),
        )
        setContent { App() }
    }
}
```

The OS holds `launch_icon` over `splash_bg` until Compose's first frame paints, and that frame is `ScanView` drawing the same `launch_icon` at the same 288 dp, centred, over the same cobalt. Nothing on screen moves at the handoff: no intermediate state, no flash, no `setKeepOnScreenCondition` needed.

### Theme port

Direct port of `ios/SodaMachine/SodaMachine/Theme.swift`: the Big Blue palette and the same roles, which `SodaMachineTheme` maps into Material 3's `darkColorScheme`.

```kotlin
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
    // …dots, placeholder, active phase, the two flavor chart series
}
```

### `ScanView.kt`

The first screen, and the other half of the handoff. It branches on `BleManager`'s state — onboarding, searching, demo, a connected placeholder — and the onboarding and searching screens open with the splash's own mark:

```kotlin
Box(modifier = Modifier.fillMaxSize()) {
    // The same mark and size as the system splash.
    Image(
        painter = painterResource(R.drawable.launch_icon),
        contentDescription = null,
        modifier = Modifier
            .align(Alignment.Center)
            .size(288.dp)
            .clearAndSetSemantics { },
    )
    // Title, subtitle and actions, anchored to the bottom.
}
```

`BleManager` is a stub until M3.

### `App.kt`

```kotlin
@Composable
fun App() {
    val ble = remember { BleManager() }
    SodaMachineTheme {
        ScanView(ble = ble)
    }
}
```

### Phase-1 acceptance criteria

The phase is done when:

1. **Cold launch on a real device feels right.** Tested on at least one Android 14+ device (Pixel) and one older Android 9–11 device to verify the splash transition. Side-by-side with iPhone, nothing on screen moves when the splash hands over to the first frame.
2. **The mark matches iOS.** Both apps draw it from `brand/mark.svg` through `tools/build_brand_assets.py` — `launch_icon.xml` here, `LaunchIcon.png` on iOS — over the same cobalt.
3. **No work done off-spec.** No BLE code, no settings UI, no permissions — those are phase 3+. Phase 1 ships when launch feels right and nothing else.

## Full milestone list

| # | Milestone | Where | Status |
|---|---|---|---|
| **M-1** | iOS: pull scattered colors into Theme.swift | iOS app | landed |
| **M0a** | iOS accessibility (6 additions, no per-image labels) | iOS app | landed |
| **M0b** | iOS haptic — medium impact at Hold-to-Prime engage | iOS app | landed |
| **M1** | Android: splash + first-frame handoff | Android phase 1 | landed |
| M2 | Android: theme polish + the root wired — Add a machine, and a machine's page (no BLE yet) | Android phase 2 | next |
| M3 | Android: BLE layer + binary protocol + the machine record — Your machines, the demo as a machine in it | Android phase 3 | |
| M4 | Android: image processing (median-cut, RGB565, CRC32) | Android phase 4 | |
| M5 | Android: ConfigView carousel + 7 sheets | Android phase 5 | |
| M6 | Android: stats sheet — pie + 3 bar charts + serving-size selector | Android phase 6 | |
| M7 | Side-by-side polish QA against iPhone | both platforms | |
| M8 | Android: accessibility + haptics (mirror M0a/M0b) | Android | |

The iOS root M2 mirrors is `Views/RootView.swift`: a machine's page (`MachinePage.swift`, with its link line and Bluetooth banner) when the phone has one, and `AddMachineView.swift` when it has none. The phone's record of every machine it knows, and which one it is pointed at, is `BLE/MachineDirectory.swift`; `YourMachinesView.swift` lists it. `ScanView.kt` above is the M1 stub of the screen that preceded that root.

M-1, M0a, M0b were pre-Android so the fully-considered iOS labels, haptics, and theme structure carry across to Android in M8 — designed once, ported, not designed twice. M6 is heavier than billed in earlier drafts: in addition to three bar charts (24h, 30d, hour-of-day), `StatsSheet` also includes a pie chart for the 30-day flavor split (no first-party `SectorMark` equivalent in Compose — hand-rolled regardless of Vico) and a custom serving-size selector that draws three glass icons at 12oz / 16oz / 20oz heights with the SVG glass path.
