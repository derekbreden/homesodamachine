# Companion-app distribution and lifecycle gap — the iOS/Android app is built, but nothing in the repo says how it reaches a customer's phone, stays there, or survives 10 years of OS churn

*Recommendation for follow-up — written 2026-05-20, hourly-todo-filler agent (sixth of the day).*

**Audience:** future agents, Derek
**Status:** recommendation only — not for direct execution

## Distinct from siblings

This gap is the *App Store side* of the product. None of today's five other files touch it:

- [`appliance-gfci-protection-component-survey.md`](appliance-gfci-protection-component-survey.md) is the appliance's AC-mains protection path. This gap is the iPhone in the customer's pocket.
- [`first-pour-commissioning-gap.md`](first-pour-commissioning-gap.md) is the time-axis state machine between plug-in and first cold soda. This gap is the prerequisite to all of it: how does the customer's phone have the app installed when the install consult starts?
- [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md) audits production-side labor. This gap is post-production: every shipped unit creates a 10-year app-maintenance obligation that the labor model has never costed.
- [`install-envelope-spec-gap.md`](install-envelope-spec-gap.md) is the kitchen-cabinet contract. This gap is the App-Store contract.
- [`unit-000-founder-kitchen-gap.md`](unit-000-founder-kitchen-gap.md) is the founder's own kitchen as a rehearsal install. That rehearsal *cannot happen* until the app is installable on Derek's own phone via the path future customers will use — which is also unsorted.

It is also distinct from these prior-day gaps:

- [`2026-05-19/integrated-firmware-gap.md`](../2026-05-19/integrated-firmware-gap.md) covers the **factory** firmware that boots the appliance on the bench. The present gap covers the **customer** software that lives on a phone the founder will never see.
- [`2026-05-19/leak-detection-coverage-gap.md`](../2026-05-19/leak-detection-coverage-gap.md) lists "alarm UX + iOS critical-alert entitlement" as one of its open items but does not unpack what acquiring that entitlement actually requires from Apple. The present gap unpacks it.
- [`2026-05-18/per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md) covers the per-customer `homesodamachine.com/u/NNN` web portal. The present gap covers the native app, which is a separate surface with separate distribution constraints and separate failure modes.
- [`2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) is the conversational structure of the Zoom install consult. The present gap is the question that consult cannot start with: "open the Soda Machine app on your phone."

---

## What the repo already contains

The companion-app footprint in the repo is bigger than its absence from the gap docs suggests:

- [`ios/SodaMachine/SodaMachine/`](../../ios/SodaMachine/) — a finished SwiftUI app, ~3.5K LOC. Bundle ID `com.derekbreden.SodaMachine`, deployment target iOS 17.0, marketing version 1.0.0, build 1 ([`ios/SodaMachine/project.yml`](../../ios/SodaMachine/project.yml)). Surfaces: BLE scan/connect, flavor image upload, ratio config, prime gesture, stats charts (Swift Charts), maintenance ([`ios/SodaMachine/SodaMachine/Views/`](../../ios/SodaMachine/SodaMachine/Views/) — `ConfigView.swift`, `ScanView.swift`, `GlassAnimationView.swift`).
- [`android/`](../../android/) — Kotlin/Jetpack-Compose scaffold with the same module layout (`ui/scan`, `ui/glass`, `ui/theme`, `ble`). The actual port has not begun in earnest; [`docs/android-port-roadmap.md`](../../docs/android-port-roadmap.md) is the plan.
- BLE protocol: Nordic UART Service (NUS) UUIDs `6E400001-...`, `6E400002-...`, `6E400003-...` ([`ios/SodaMachine/SodaMachine/BLE/BLEManager.swift:7-10`](../../ios/SodaMachine/SodaMachine/BLE/BLEManager.swift)). S3 firmware in [`firmware/src_config/main.cpp`](../../firmware/src_config/main.cpp) hosts the GATT server.
- The OTA path is explicitly app-mediated: "updates flow phone -> BLE -> S3 -> UART -> ESP32 main. The unit is never on WiFi or the internet (air gap is intentional)" — [`firmware/partitions_esp32.csv`](../../firmware/partitions_esp32.csv) lines 7-9, mirrored in [`firmware/partitions_s3.csv`](../../firmware/partitions_s3.csv).

What is *not* in the repo, anywhere I could grep, is:

- Whether the **Apple Developer Program** ($99/yr) is enrolled for `com.derekbreden`, and under what name (individual vs. organization — the latter requires a D-U-N-S number; the former personally identifies Derek as the publisher on the App Store listing).
- Whether the **Google Play Console** ($25 one-time) is enrolled.
- A chosen **distribution method** (App Store vs. TestFlight vs. ad-hoc vs. enterprise vs. AltStore-style sideload).
- A **privacy policy URL** (mandatory for any App Store / Play submission).
- A **Privacy Manifest** (`PrivacyInfo.xcprivacy`, required by Apple for all new submissions since May 1, 2024 — the iOS app has none).
- A **Critical Alert entitlement** plan — explicitly cited as an open item in [`2026-05-19/leak-detection-coverage-gap.md`](../2026-05-19/leak-detection-coverage-gap.md) but never unpacked.
- A **trademark search** on the App Store name. The project.yml sets `CFBundleDisplayName: "Soda Machine"` — two generic English words. The App Store will not block on that alone, but Apple's App Store team has discretion to reject names too close to existing apps, and "Soda Maker" / "SodaStream" / "Soda Mixer" all exist on the store.
- A **10-year maintenance commitment** — Apple deprecates SDKs annually, raises minimum Xcode versions, and historically (iOS 12→13, iOS 16→17) has bumped deployment-target floors. Without yearly rebuilds, the app will eventually be pulled from the store.
- A **bus-factor** plan — if Derek stops maintaining the app, the BLE-only OTA mechanism stops being deliverable.

The gap is not "the app doesn't exist." It is "the app exists, it's load-bearing for several promises the appliance makes to the customer, and the distribution + lifecycle plan around it is entirely unwritten."

---

## Why the app is load-bearing despite [`hardware/requirements.md:31`](../../hardware/requirements.md)

Requirements.md asserts:

> The iOS app and BLE bridge are conveniences, not dependencies. All necessary operation — selection, dispense, fill, cleaning, ratio configuration — is reachable from the appliance's physical interfaces (faucet handle, air switch, S3 display)

That is true for *steady-state daily dispense* but false for at least four other obligations the rest of the repo accumulates:

1. **First-install firmware binding.** [`hardware/assembly/firmware-and-commissioning.md:5,24,157`](../../hardware/assembly/firmware-and-commissioning.md) repeatedly defers customer-side firmware binding (Wi-Fi credentials are NOT needed, but ratio tuning, image upload, and cloud pairing) "to the iOS/Android app at first install." Acceptance and burn-in [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) ends with the unit ready for the customer, not for use. If the app isn't installable, "first install" stops at the appliance's S3 display, which is workable for ratios (touchscreen UI exists) but not for the per-customer flavor images that the marketing video [`marketing/video/concepts.md:99-104`](../../marketing/video/concepts.md) leans on as a brand-consistency story.

2. **The over-the-air firmware-update path.** [`firmware/partitions_esp32.csv`](../../firmware/partitions_esp32.csv) commits unambiguously: "phone -> BLE -> S3 -> UART -> ESP32 main … The unit is never on WiFi or the internet." There is no other update path. If the customer cannot install the app, the customer cannot receive a firmware update, ever. Yesterday's commit decision to switch to dual-slot OTA before unit #001 ships only acquires the *device-side* OTA capability; the *delivery-side* depends on the app being on the customer's phone. If a customer's phone OS no longer runs the app five years in, that customer is on the firmware they shipped with, period.

3. **The backflow-vent leak alarm.** [`hardware/future.md:121`](../../hardware/future.md) commits the moisture-sensor-on-vent alarm to "an iOS app notification." [`2026-05-19/leak-detection-coverage-gap.md`](../2026-05-19/leak-detection-coverage-gap.md) escalates this to a Critical Alert — an alarm that bypasses Silent Mode and Do Not Disturb, because a slow backflow leak is the kind of event the customer should be woken up for. Apple gates Critical Alerts behind a hand-reviewed entitlement (`com.apple.developer.usernotifications.critical-alerts`); the entitlement request goes to a form at developer.apple.com/contact/request/notifications-critical-alerts-entitlement, requires written justification, and is regularly denied for consumer hardware companion apps. If the entitlement is denied, the alarm is a regular notification, which iOS will *silence* on a sleeping phone, which is the exact scenario the design intends to alarm.

4. **The MQ-6 hydrocarbon-leak alarm.** Yesterday's commit (76eb420) moved the MQ-6 R-600a sensor to the rear interior wall but left the alarm-UX half of [`2026-05-19/leak-detection-coverage-gap.md`](../2026-05-19/leak-detection-coverage-gap.md) unresolved. Same Critical Alert dependency as the vent leak. Refrigerant leaking and pooling at the cabinet floor is more alarming, not less, than a backflow weep.

The "app is convenience" framing is true at the dispense lever and false everywhere else the product makes a safety-, security-, or trust-affecting promise. The promises don't change because of the convenience framing; they change because of the channel.

---

## The eight load-bearing decisions that have never been written down

### 1. Apple Developer Program: individual vs. organization

The bundle ID `com.derekbreden.SodaMachine` ([`ios/SodaMachine/project.yml:11`](../../ios/SodaMachine/project.yml)) is an *individual* namespace. On the App Store, the publisher line under the app name will read **"Derek Bredensteiner"** — not the brand name the marketing strategy is built around. At Founder Edition pricing, that may even be a feature ("the brand is Derek" — [`marketing/target-market.md:260`](../../marketing/target-market.md)), and it neatly avoids the D-U-N-S Number requirement for organization accounts (a Dun & Bradstreet number, free but multi-week to acquire). It also tightly couples the app's distribution to a single person; transferring an individual account to an LLC later is possible but requires an Apple-mediated migration with downtime.

Recommendation: enroll as an individual for now, plan to migrate to an LLC organization account simultaneously with the LLC formation Derek already plans before first paid unit ships ([`business/incorporation.md`](../../business/incorporation.md)). The migration is one of the things to bundle into "before unit 001 ships."

Comparable decision on Android: Play Console enrollment as Personal account vs. Organization. Same trade. As of late 2023 Google also requires identity verification for personal-account developers, which adds friction but is one-time.

### 2. Distribution method choice for the first 50

There are five viable paths to get the iOS app onto a Founder Edition customer's iPhone. They are not equivalent.

| Path | Friction for customer | Friction for Derek | Long-term viability | Cost |
|---|---|---|---|---|
| Public App Store listing | Tap link, install | App Store Review on every release | Strong (multi-year) | $99/yr |
| TestFlight public link | Tap link, install TestFlight app, accept invite, re-accept every 90 days when build expires | Manage tester list (Apple cap of 10,000); rebuild every 90 days | Weak (TestFlight was never designed for production use) | $99/yr |
| Ad-hoc / UDID provisioning | Send Derek your phone's UDID, wait for a signed IPA, install via Apple Configurator or Xcode | 100 UDIDs per year cap; expires annually with the dev cert | Untenable past unit ~50 | $99/yr |
| Apple Developer Enterprise Program | Install via MDM or a profile + a "trust this developer" workflow | $299/yr; Apple has tightened enforcement (the program is for "in-house" employee apps only, third-party use risks revocation of *all* Derek's signing) | High legal risk | $299/yr |
| AltStore / sideload | Customer installs AltStore Pal (€1.50/yr in EU only) or jailbreaks | Customer rebuild every 7 days unless paid Apple ID; US/non-EU customers cannot do this legally | Untenable | $0 |

The Founder Edition population is 50 customers spread across the US over ~4 years. Public App Store is the only path that scales past the TestFlight 90-day re-accept treadmill *and* survives without a yearly attention pulse from Derek. But getting a hardware companion app *past* App Store Review for an unlisted appliance is the question item #5 below addresses.

Recommendation: target **App Store** as the primary distribution path, with **TestFlight** used only as the bridge for the first 3-5 customers while the App Store submission is in review. Internal TestFlight (100 testers, no review) is the path for Derek's own pre-ship validation. External TestFlight (10,000 testers, abbreviated review) is the path for unit-001-through-unit-005 customers if the App Store submission gets stuck.

### 3. Privacy policy URL + Privacy Manifest

Required for App Store and Play submission. The app's data behavior is genuinely minimal: BLE-only, no analytics, no off-device telemetry (the partition banner is loud about this), no account, no IAP. That's the easiest possible privacy policy to write — but it still has to be hosted somewhere on `homesodamachine.com`, and the Privacy Manifest (`PrivacyInfo.xcprivacy`) has to be in the iOS bundle. Apple now rejects new submissions and updates of existing apps that don't have one.

What the manifest has to declare:
- **NSPrivacyTracking**: `false` (no third-party tracking).
- **NSPrivacyTrackingDomains**: empty array.
- **NSPrivacyCollectedDataTypes**: empty array. (Genuinely.)
- **NSPrivacyAccessedAPITypes**: this is the surprising one. The Privacy Manifest now requires declaring use of "required-reason" APIs even for apps that don't collect data. The iOS app uses `UserDefaults` (reason category `CA92.1`) and probably `fileTimestamp` (`C617.1`) for image cache invalidation. Both must be enumerated. Skipping this is the single most common reason a no-data app gets a Privacy Manifest rejection.

Equivalent on Android: the Play Data Safety form, which requires similar disclosures and a hosted privacy policy URL.

Recommendation: add `PrivacyInfo.xcprivacy` to the iOS bundle now (well before submission) and a `/privacy` route to the [`web/`](../../web/) server. The privacy text is ~10 lines because the data behavior is honestly minimal.

### 4. Critical Alert entitlement application

The entitlement that the leak alarms depend on is *requested*, not configured. The application asks for:
- A description of why the app needs to bypass Silent Mode and DND.
- The category of users the entitlement is for.
- Evidence that the alerts are infrequent and genuinely critical.

Apple historically grants this for healthcare apps (CGMs, EpiPen-adjacent), public-safety apps (CodeRED, severe-weather), and some smart-home leak detectors (Phyn, Flo, StreamLabs). The justification is "low-frequency notification for safety event in the home." A hydrocarbon refrigerant leak alarm and a backflow-vent leak alarm both fit that profile, but the entitlement is not granted automatically — Derek will need to write the request.

Possible second-best fallback if the entitlement is denied: **Time Sensitive notifications** (a separate, lighter-weight category that does NOT bypass Silent Mode but DOES bypass scheduled Focus modes; available to all apps, no entitlement needed). This degrades the alarm experience but does not break it. The repo should commit to which alarm UX is the design target *before* the entitlement is filed, because that frames the request.

Recommendation: file the Critical Alert entitlement at least 60 days before unit-001's ship date. Document a Time-Sensitive fallback in [`2026-05-19/leak-detection-coverage-gap.md`](../2026-05-19/leak-detection-coverage-gap.md). Both alarms (vent and MQ-6) should go through the same notification category, configured at compile time.

### 5. App Store Review — Guideline 4.2 ("Minimum Functionality")

The most common rejection category for hardware companion apps. Apple's framing: the app must do something useful *even without the hardware connected*. The iOS app today opens to [`ios/SodaMachine/SodaMachine/Views/ScanView.swift`](../../ios/SodaMachine/SodaMachine/Views/ScanView.swift), and if no Home Soda Machine is in BLE range, the user sees a scan-spinner indefinitely. That is the literal pattern Guideline 4.2 calls out.

Mitigations that work in practice:
- A **demo mode** the user can enter without a connected appliance — shows the glass animation, lets the user explore the UI, possibly shows simulated stats. Cheap to add given the existing `GlassAnimationView` and `Chart` views already render from data — they would just need a fake-data source path.
- **Marketing material on the scan screen** — a few illustrative screenshots of the connected experience, with a "buy at homesodamachine.com" link. Apple discourages but does not reject this when paired with demo functionality.
- **Detailed App Review notes** explaining the hardware that the app pairs with, with a link to the product website. Reviewers do read these and Apple has a separate hardware-companion-app reviewer pool that is more lenient when the hardware is real and well-documented.

Recommendation: build a demo mode that shows the glass animation + a sample charts page from canned data. ~1 day of work. Pair with a thorough App Review note + a link to the product website. Plan for the first submission to be rejected; the second submission, after addressing reviewer feedback, is typically accepted.

### 6. Background BLE — the alarm path's quietest failure mode

The vent and MQ-6 leak alarms are described as iOS notifications. iOS notifications can be delivered three ways:
1. **Local notification** scheduled by the app while running, fired at a future time. Doesn't apply here — the alarm trigger is the appliance, not the app.
2. **Local notification fired immediately in response to a BLE event**. This works only if the app is in the foreground OR has the `bluetooth-central` background mode AND is running AND the user has granted background BLE permission AND the OS hasn't suspended it for memory pressure. Five conditions that all have to hold.
3. **Push notification via APNs**. Doesn't apply — the appliance is air-gapped per [`firmware/partitions_esp32.csv`](../../firmware/partitions_esp32.csv) "never on WiFi or the internet."

Path (2) is the only available channel today, and it's fragile. On a phone that has been idle for hours, with the app not recently opened, iOS will typically have suspended the app to free memory, and a BLE leak event from the appliance will not wake it. The alarm will arrive only when the user next picks up the phone and the app gets re-scheduled — which in a true overnight slow-leak scenario is too late.

Three options for fixing this:
- **Add WiFi to the appliance** for alarm purposes only. Violates the explicit air-gap commitment. Real cost in firmware complexity, attack surface, FCC Part 15 implications. Strongly out of scope.
- **Add a cellular fallback channel** via a tiny per-appliance modem (e.g., Notecard) that sends APNs/FCM pushes for *only* the alarm events, never for telemetry. ~$50/unit BOM, ~$3/mo per appliance for the data plan, but matches the spirit of the air gap (one-way, alarm-only, no telemetry).
- **Hardware-side alarm and only soft-notify the app**. Make the appliance itself an audible alarm — a piezo buzzer wired to the ESP32 that fires on either leak event, loud enough to be heard from the kitchen. The iOS notification becomes the optional, best-effort secondary channel. This matches what residential smoke and CO detectors actually do: the device is the alarm, the app is a convenience.

Recommendation: go with the hardware-side alarm (option 3). It's the cheapest, the most reliable, the most familiar to customers, and it converts the iOS app from "load-bearing for safety" back to "convenience." This is also the recommendation that closes the leak-detection-coverage gap from yesterday cleanly: the alarm becomes a piezo on the rear panel, the iOS notification becomes a nice-to-have, the Critical Alert entitlement becomes optional rather than mandatory, and the air-gap commitment stays intact.

Note: this recommendation is opinionated and may be the most consequential single item in this doc. If accepted, it amends [`hardware/future.md`](../../hardware/future.md), [`2026-05-19/leak-detection-coverage-gap.md`](../2026-05-19/leak-detection-coverage-gap.md), and the alarm-UX framing in [`hardware/requirements.md`](../../hardware/requirements.md).

### 7. The 10-year maintenance commitment

Marketing commits explicitly to a 10-year design life. The repo even commits to it in places ([`hardware/requirements.md:29`](../../hardware/requirements.md) — "The target is 10 years"). Over 10 years on Apple's roadmap, historically:
- iOS major versions advance one per year. Each typically deprecates several APIs.
- Xcode major versions advance one per year. Each typically raises the minimum Swift, macOS, and iOS-SDK versions for new submissions.
- Apple typically deprecates support for the oldest 2-3 device generations per release.
- App Store requires apps to be built against an SDK no more than ~1 year old to remain submittable. Apps not updated for ~3 years get the dreaded "App Improvements: This developer needs to update this app to work with the latest version of iOS" email and are eventually delisted.

Translation: the iOS app needs a yearly rebuild-and-resubmit at minimum, even with zero feature changes, just to remain in the store and installable on new phones. The same is true for Google Play, with slightly less aggressive deprecation cadence.

The yearly labor cost of "rebuild against latest Xcode, fix the 1-3 deprecation warnings, re-test on a current iPhone, resubmit" is realistically 1-2 days of Derek's time per year per platform. That's ~4 days/year across iOS + Android. Not nothing, not catastrophic, but real.

The labor model in [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md) does not include this 4 days/year, because the labor model is built around per-unit assembly. App maintenance is a fixed per-year cost regardless of unit count. At 50 units lifetime, that's a multi-week obligation against revenue that was bounded by physical build capacity.

Recommendation: add an "annual maintenance" line to [`business/incorporation.md`](../../business/incorporation.md)'s eventual P&L thinking — 4 days/yr labor + $99/yr Apple Developer + $0/yr Google (one-time) + ~$10/yr domain for privacy policy hosting = a small but persistent recurring cost.

### 8. The bus-factor question

The companion app is the only OTA path. If Derek is unavailable for an extended period (illness, life change, etc.):
- The yearly rebuilds stop.
- The app drifts out of App Store compatibility within ~1-3 years.
- New customers cannot install the app onto new phones running newer iOS.
- Existing customers retain their already-installed copy until their iOS upgrade renders it non-launchable.
- The OTA firmware-update path stops working for all units.

This isn't unique to the app — the entire 50-unit Founder Edition has a single-person dependency by design. But the *fastest-decaying* dependency is the app, because Apple's platform churns faster than the appliance's mechanical wear-out curve. The compressor will outlast Apple's deprecation of the SDK the app currently builds against.

Recommendation: the bus-factor case for the appliance is its own gap (and might be worth a future hourly-todo file in its own right). For the app specifically, the meaningful mitigation is keeping the source open and dependency-free enough that someone else could rebuild and resubmit if needed. The current iOS app is in good shape on this — pure SwiftUI, no third-party SDKs, no Swift Package Manager dependencies, Nordic UART is RFC-style protocol over CoreBluetooth. A capable iOS developer could pick it up and rebuild it cold from the repo. That's worth preserving as a deliberate constraint, not an accident.

---

## What I would want to read next

In rough order of urgency:

1. A **decision** on hardware-side leak alarm (option 3 above) vs. relying on iOS Critical Alerts. This is the highest-leverage item because it cascades into the entitlement decision, the air-gap-vs-cellular decision, and the alarm UX in [`2026-05-19/leak-detection-coverage-gap.md`](../2026-05-19/leak-detection-coverage-gap.md).
2. A **distribution path decision** (App Store + TestFlight bridge, per recommendation in §2).
3. A **Privacy Manifest + privacy policy** stub committed to the repo at `ios/SodaMachine/SodaMachine/PrivacyInfo.xcprivacy` and `web/lib/privacy.js` (a route, ~10 lines of HTML).
4. A **demo mode** added to the iOS app so it can survive Guideline 4.2 review.
5. The **Apple Developer Program enrollment** opened as an individual; bundle ID transferred to organization account later, alongside LLC formation.
6. A **Critical Alert entitlement application** filed 60+ days before unit-001 ships, *conditional on* the alarm-UX decision in §1 above. If we go with hardware-side alarms, this becomes optional.
7. The **App Store name** locked in. "Soda Machine" as a CFBundleDisplayName works; the App Store listing name should be considered separately (e.g. "Home Soda Machine" — which matches `homesodamachine.com`).
8. An **annual maintenance calendar** added to [`business/incorporation.md`](../../business/incorporation.md): every August (after each year's WWDC, before each year's iOS GA), Derek rebuilds against the latest Xcode and resubmits. Anchor to a fixed week on the calendar.
9. A **first-install card** added to the unboxing brief at [`marketing/unboxing-and-quickstart.md`](../../marketing/unboxing-and-quickstart.md) that includes the App Store / Play Store QR codes. Today the unboxing brief does not name the app or tell the customer where to get it.

The first five items collectively unblock unit-001's ship date in a way the repo currently does not.

---

## What I am explicitly *not* recommending

- A complete rewrite of the iOS app. It's in good shape. ~3.5K LOC, clean SwiftUI patterns, accessibility done (per [`docs/android-port-roadmap.md`](../../docs/android-port-roadmap.md) Milestone 0a), no third-party dependencies. The gap is around the app, not in it.
- A PWA replacement for the native app. The product depends on BLE, and BLE-over-Web (Web Bluetooth) is not available on iOS Safari and unlikely ever to be. The PWA path is foreclosed by the platform decision.
- A "subscription" or IAP. The product is sold once; the app should not introduce App Store revenue mechanics. Side benefit: this also dodges the App Store's 30% take entirely.
- Adding WiFi to the appliance. The air-gap commitment is a genuine product property, not just a firmware-complexity dodge — it's a privacy story we'd be giving up.
- Filing for the Critical Alert entitlement *first*, then designing the alarm UX. The entitlement request asks why the app needs the entitlement, which means the UX has to be designed first, then defended.

---

## A note on cost of inaction

The cheapest version of this gap to close is the version where Derek decides on the hardware-side alarm (§6, option 3) and concludes that the iOS app remains a convenience. In that world, App Store distribution still matters for firmware-OTA and for the brand surface, but it's not load-bearing for safety, and the Critical Alert entitlement work disappears.

The most expensive version is the one where the leak alarms stay app-mediated, the Critical Alert entitlement gets denied, and a customer experiences a slow vent leak overnight with their phone silenced. That story has both a customer-harm cost and a brand cost that the Founder Edition reputation cannot easily absorb.

The work to convert the cheapest version into reality is small and concentrated in 2-3 firmware-side changes (add a piezo, wire it to ESP32, add a software gate that drives it from either of the two leak-sensor inputs) — none of which require any iOS work. That's the recommendation this doc is built around.
