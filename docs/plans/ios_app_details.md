---
name: iOS App Details
description: iOS app architecture, gotchas, and physical system details that were trimmed from MEMORY.md
type: reference
---

## iOS App Architecture (detailed)
- **@Observable** (iOS 17 Observation framework), NOT ObservableObject
  - ObservableObject fires `objectWillChange` for ALL views on ANY @Published change — caused full TabView re-render on every image download chunk, freezing UI
  - @Observable provides per-property observation — only views reading the specific changed property re-render
  - Migrated from `@StateObject`/`@EnvironmentObject` to `@State`/`@Environment(BLEManager.self)`
- **CBDelegateAdapter pattern**: @Observable classes cannot inherit NSObject; CoreBluetooth delegates require NSObject. Solution: thin private NSObject class that forwards delegate methods to the @Observable BLEManager
- **bleQueue**: dedicated background DispatchQueue for all CoreBluetooth operations. Binary image data accumulation, BLE writes, download loop chaining all run on bleQueue. Only observable property updates dispatch to main.
- **@ObservationIgnored fileprivate**: internal BLE state (download buffers, upload steps, CoreBluetooth references) that the CBDelegateAdapter needs access to but SwiftUI should not observe
- **Separate View structs** (ImageSlotView, SettingsPageView, AboutView) create isolated observation scopes — image cache changes only re-render leaf views, not the parent TabView
- **BLE Framed Protocol** (replaces raw text/binary NUS): every message is `[1B type][2B payload length LE][payload...]`. Frame types: TEXT (0x01), BIN_START (0x02), BIN_DATA (0x03), BIN_END (0x04). Both S3 and iOS send/receive framed.
- **Image download flow**: GETPNG:slot (TEXT frame) → BIN_START (slot, file_type, size, CRC-32) → BIN_DATA chunks → BIN_END. iOS verifies size + CRC-32, auto-retries up to 3x on mismatch. All on bleQueue; UIImage decoded on bleQueue; only `cachedImages[slot] = image` dispatches to main.
- **Image upload flow**: phone generates PNG + S3 RGB565 + RP RGB565 → BIN_START frame (slot, type, size, CRC-32, label) → BIN_DATA frames → BIN_END frame → S3 validates CRC, saves locally → S3 forwards to ESP32 via SerialTransfer. No UPLOAD_READY handshake — BIN_START is processed directly in NimBLE callback.
- **NUS (Nordic UART Service)**: framed protocol over 6E400001 service UUID. Phone writes to RX char (write-with-response), subscribes to TX char notifications. Upload chunks: `min(mtu-3, 240)` with 20ms inter-chunk delay. Download chunks: 180 bytes + 20ms delay from S3.

## iPad Layout
- Stats view uses `horizontalSizeClass == .regular` to detect iPad
- iPhone: vertical ScrollView with all 4 charts stacked (160pt each)
- iPad: 2x2 grid — two HStack rows (donut+24H top, 30D+HOD bottom) with 3-way equal Spacer distribution (title→row1, row1→row2, row2→bottom). Charts keep 160pt fixed height for good aspect ratio.

## Theme / Visual Design
- Dark navy background `#1a1a2e` across app icon, launch screen, iOS app, and S3 display
- iOS: `Theme.swift` enum centralizes all colors (background, textPrimary, textSecondary, dotActive, dotInactive, placeholder)
- S3: `THEME_*` defines at top of `src_config/main.cpp` (THEME_BG, THEME_BG_RGB565=0x18C5, THEME_TEXT_PRIMARY, etc.)
- App icon source: `ios/AppIcon.svg` — regenerate PNGs with `rsvg-convert -w 1024 -h 1024`
- S3 logo: `src_config/images/logo_240.h` — regenerate from SVG via `rsvg-convert -w 240 -h 240` then Python RGB565 conversion
- Launch screen uses storyboard (not Info.plist approach) — hand-writing storyboard XML is fragile, reference Xcode's own templates for correct `toolsVersion`

## iOS Gotchas & Lessons Learned
- **Storyboard XML**: use Xcode's own template as reference (`find /Applications/Xcode.app -name "LaunchScreen.storyboard"`) for correct `toolsVersion` and `targetRuntime`
- **Xcode debugger kills BLE performance**: os.Logger is synchronous when debugger is attached; Main Thread Checker adds overhead. App that runs smoothly from home screen can appear frozen when launched from Xcode. Fix: uncheck Main Thread Checker in scheme diagnostics, reduce hot-path logging to .debug level.
- **EXIF orientation**: UIImage from PhotosPicker may have non-up orientation. Must normalize before generating RGB565.
- **PhotosPicker XPC warnings**: yellow console warnings about `usermanagerd.xpc` and `LaunchServices` are harmless Apple framework noise.
- **iOS 17 onChange**: `onChange(of:perform:)` deprecated; use `onChange(of:) { oldValue, newValue in }` two-parameter form.
- **SwiftUI gesture resolution**: child Button gestures take precedence over parent `.onTapGesture`.
- **iOS optimistic delete pattern**: `deleteImage()` saves pre-delete state, removes image immediately from UI, sends BLE command. On `ERR:` response, rolls back all state and shows alert.
- **Swift `Data.removeFirst()` doesn't rebase indices**: after `removeFirst(n)`, `startIndex` shifts to `n`, NOT 0. Subscripting with `data[0]` crashes. Always use `data[data.startIndex]` or `data[si + offset]` when parsing a Data buffer that has been mutated with `removeFirst`.

## Xcode Project
- Uses xcodegen (`project.yml` → `.xcodeproj`), run `xcodegen generate` after changes
- Deployment target: iOS 17.0
- Bundle ID: `com.derekbreden.SodaMachine`
- Display name: "Soda Machine"

## Plumbing / Physical System
- Flavoring bags: Platypus soft bags, connector at bottom
- Flavoring lines: 1/8" ID silicone tubing from platypus bags → solenoid valves → peristaltic pumps → dispensing point
- Water lines: 1/4" RO harder casing lines for filtered tap water and carbonated water
- Peristaltic pumps: duty-cycle based on flow meter readings, burst-driven (not continuous)
- Solenoid valves: normally closed, prevent backflow
- Air switch: toggles between 2 flavors
- Flow meter: reads 0-6 every 50ms, detects soda water flow

## Hardware / Flashing Notes (additional)
- ESP32 can be reset via RTS toggle (python serial) when reset button is hard to reach
