# Above-counter UX gap — the visible product has no owning UX doc

**Author:** hourly agent, 2026-05-19 (afternoon)
**Status:** recommendation only — not for direct execution
**Audience:** Derek, future agents

**Distinct from siblings today and yesterday:**
- [`integrated-firmware-gap.md`](integrated-firmware-gap.md) covers the *firmware target itself* (no integrated-build env, no DS18B20/MCP23017/relay code paths). That gap is about what the firmware controls. This gap is about what the **customer sees on the visible product** — display content design, air-switch interaction model, audible feedback. Sibling fixes the engine; this one fixes the dashboard.
- [`co2-runtime-and-depletion-ux-gap.md`](co2-runtime-and-depletion-ux-gap.md) covers the **CO2-specific** signal chain (mass sensor, app screen, lockout) — one fault domain. This doc covers the **whole display surface** across boot, cooldown, idle, dispense, every fault, and sleep — and how CO2-low (and microbio-clean, freeze-cutout, fill-locked-during-dispense, etc.) all share that single 128×115 round display without colliding.
- [`reservoir-microbio-and-clean-policy-gap.md`](reservoir-microbio-and-clean-policy-gap.md) names a clean-cycle that the customer launches and watches; the *what does the cycle look like on the display* question lands here, not there.
- [`tap-water-quality-spec-gap.md`](tap-water-quality-spec-gap.md) and [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md) are upstream of any UX — quality + safety inputs. Not in scope.
- Yesterday's [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) explicitly carved this gap out in its "Out of scope" section:
  > **The above-counter visual install (the visible part of the appliance — faucet, display, switch).** The install guide names this but the visual / UX of the above-counter fixture is its own design problem, separate from the install procedure.
- Yesterday's [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md) covers the `/u/NNN` web surface; this doc is about the **on-device** surface. Different screens, different design constraints (web has effectively infinite real estate; this is 128×115 pixels round inside a printed shell).

---

## TL;DR

The product has three above-counter user-facing surfaces ([`hardware/future.md:125`](../../hardware/future.md)):

1. The **Westbrass faucet lever** (mechanical, no firmware).
2. The **KRAUS air switch** (matte black, [`hardware/bom.md §10`](../../hardware/bom.md)) for flavor select.
3. The **Waveshare RP2040 round LCD 0.99"** (128×115, [`hardware/bom.md §1`](../../hardware/bom.md)) inside the printed touch-flo-shell.

The mechanical assembly is fully documented: the shell is in PET-CF ([`touch-flo-shell/MATERIAL.md`](../../hardware/printed-parts/faucet/touch-flo-shell/MATERIAL.md)), the umbilical procedure is in [`faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md), the Cat6 wiring carries SIG-5 (KRAUS contacts) + SIG-6 (RP2040 UART + 5 V) per [`ac-wiring-schedule.md`](../../hardware/wiring/ac-wiring-schedule.md).

What it does on the customer's counter is documented in **one sentence**:

> *"RP2040 round display showing the active flavor's logo."* — [`hardware/future.md:125`](../../hardware/future.md)

The firmware on `main` matches the one-sentence spec: [`firmware/src_display/main.cpp`](../../firmware/src_display/main.cpp) renders one of N seeded flavor bitmaps from LittleFS based on the GP29 analog read of the KRAUS air switch, and that is the whole behavior. No boot screen, no cold-cooldown indication, no fault state, no CO2-low warning surface, no clean-cycle UI, no dispense-active visual, no sleep behavior, no brightness control, no error display, no day/night mode. The display's surface area is being used for ~0.5% of what it could communicate, and the other 99.5% of states are silently invisible to the user.

This is the **legitimacy hinge at Founder Edition pricing.** From [`marketing/target-market.md` Open Question 2](../../marketing/target-market.md):

> **The visible product.** What does the faucet and visible hardware look like now? **The legitimacy question at $7,500 lives or dies on surfaces.**

The faucet body is harvested chrome Westbrass — the customer's eye sees that as a real fixture. The PET-CF shell is a real-engineering object per MATERIAL.md's reasoning. The third element — the display — is the *only* piece in the visible stack with software, and right now its software is one screen.

This todo is the playbook for what the display, air switch, and audible feedback do *as an integrated UX*, in every state the appliance can be in, with one canonical doc that the firmware ([`integrated-firmware-gap.md`](integrated-firmware-gap.md)) implements against and that the install consult ([`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md)) can point a Ring 1 customer at when they ask "what do all the screens mean?"

The 30-second pour video that anchors the marketing plan ([`target-market.md` "Video is the discovery mechanism"](../../marketing/target-market.md)) **films this surface**. Whatever the display shows is on camera. A blank screen, or one that shows last-flavor when the appliance is idle, is the marketing-asset surface. This is not a cosmetic concern.

---

## Why this is not the firmware gap

The integrated-firmware gap is "we don't have code for the integrated controller." That is upstream: until that exists, none of the *signals* feeding the display surface exist either (no compressor-state, no level-reed reads, no CO2 mass, no clean-cycle state). So why write this doc now?

Because the firmware-architecture work is about to ramp, and **without a target on the display side, the firmware will define the display protocol implicitly** — by which signals happen to be available when each subsystem comes online, in whatever shape `proto_link.h` already happens to take. The display will end up showing whatever was easiest to wire up. That is what happened on the prototype: the seeded bitmap behavior was the easiest thing to wire up.

The right order is: (1) name the display states + transitions + visual treatment first as a doc, (2) build the firmware around that protocol second. That makes the protocol between the ESP32 and the RP2040 narrow and deliberate instead of accreted. It also gives the RP2040 firmware (which is structurally simpler than the ESP32 firmware — see [`firmware/src_display/`](../../firmware/src_display/)) a clean spec to implement against, separately and in parallel with the ESP32 work.

The opposite ordering — firmware-first, UX-after — produces the same artifact the prototype is producing: a display showing what's easy to show, not what's useful to show.

---

## What exists today

### The RP2040 firmware ([`firmware/src_display/main.cpp`](../../firmware/src_display/main.cpp))

128×115 GC9107 IPS display behind a Pico SPI bus, driven by `Arduino_GFX_Library`. The renderer pulls images from LittleFS (`img00.bin` … `img09.bin`), with the active slot selected by an analog read on GP29 from the KRAUS air switch. Seeded with three flavor bitmaps compiled in for first-boot only (`flavor1_bitmap.h`, `flavor2_bitmap.h`, `flavor3_bitmap.h`), then served from LittleFS. A `ProtoLink` UART channel on GP26/GP27 talks to the ESP32 for image upload/CRC verification — *the channel exists, but nothing on the ESP32 side currently sends anything except image-management commands.*

That's the entire user-facing behavior on this MCU today. No state machine beyond "render the bitmap at slot `activeFlavor`."

### The ESP32 side

The prototype firmware [`firmware/src/main.cpp`](../../firmware/src/main.cpp) reads the KRAUS air switch on a different GPIO (the prototype topology) and produces a `proto_link` message that the RP2040 currently treats as "show this slot." No message exists yet for any other display state.

The integrated-build firmware (per sibling [`integrated-firmware-gap.md`](integrated-firmware-gap.md)) doesn't exist. So all of the *new* state the display would surface — compressor running, carbonator filling, CO2 cylinder mass, refrigeration cooldown progress, drip-pan alarm, clean cycle running — has no source yet.

### The audible side

[`integrated-firmware-gap.md`](integrated-firmware-gap.md) notes the DIYables passive buzzer is wired to the ESP32 (LEDC PWM, GPIO TBD) per the wiring docs but has no firmware. The buzzer is inside the appliance under the sink, not on the counter — so this is an *audible-from-the-cabinet* signal, not an above-counter signal. (Per [`marketing/target-market.md:121`](../../marketing/target-market.md), the moisture-sensor drip-pan alarm is the canonical use case: "firmware fires an audible alarm at the device and an iOS app notification.") We have no documented audible-feedback model for above-counter actions — the air switch click is the only acoustic feedback the user gets from a flavor change today, and there is no documented intent for the display side to ever beep.

### The visible-stack finish

The KRAUS air switch is matte black ([`hardware/bom.md §10`](../../hardware/bom.md)). The Westbrass body is harvested chrome. The PET-CF shell is black (per [`touch-flo-shell/MATERIAL.md`](../../hardware/printed-parts/faucet/touch-flo-shell/MATERIAL.md): PET-CF is dark by default). The display bezel area is whatever the printed shell makes it — see [`generate_step_cadquery.py`](../../hardware/printed-parts/faucet/touch-flo-shell/generate_step_cadquery.py) for the recess geometry. There is **no documented decision** about whether the customer can pick a finish, whether the shell can ship in other colors, whether the chrome faucet body is a freedom or a constraint. The visible stack today is three different materials (chrome metal + matte-black plastic + matte-black PET-CF print) that just happen to be procured in compatible-looking finishes. No designer has signed off on the system.

---

## Specific gaps

The gaps below are sized for individual follow-up tickets (similar to the I-numbered gaps in the install-consult-playbook). Each one is doc-first; the firmware work follows.

### U1 — Write the canonical display-state catalog

A single doc — call it `firmware/display-states.md` — that enumerates every state the display can be in, in order of customer-facing priority. This is the spec the RP2040 firmware implements against and the protocol the ESP32 sends commands against. Recommended state list with current evidence:

| State | When | Visual treatment (proposal) | Source data |
|---|---|---|---|
| **Boot** | Power-on, before WiFi connect | A still "homesodamachine" mark, 1–2 seconds. Quiet. No animated brand reveal. | Local to RP2040 |
| **Commissioning / first-cooldown** | First boot after install consult — refrigeration is pulling carbonator from ambient to 2 °C, can take 20–40 min (sibling [`install-consult-playbook-gap.md` I1 Phase B step 8](../2026-05-18/install-consult-playbook-gap.md), **needs measurement**) | A progress arc around the round display perimeter, current temperature in the center. Number ticks down: "12 °C" → "6 °C" → "3 °C" → "Ready." | DS18B20 wall probe, via ESP32 |
| **Idle ready** | Carbonator at temp, no dispense in progress, CO2 nominal, no faults | Active flavor's logo, full color. **Default state.** This is what a guest sees walking into the kitchen — the *showpiece state*. See U7 below for the question of whether this should auto-dim. | Active flavor slot |
| **Dispense active** | Faucet lever open, flow meter showing dispense | Active flavor's logo, plus a subtle animated overlay (waveform? droplets? brief flash?) — *intent: confirm the appliance saw the pour, without changing the brand-forward visual*. Animation should last only while flow is detected; reverts to idle when faucet closes. | Flow meter via ESP32 |
| **Flavor switching** | User just pressed the KRAUS air switch | Cross-fade between flavor logos, ~200 ms. Inhibits during dispense (don't let a mid-pour press change the served flavor; see U2). | Air-switch via GP29 (RP2040 local) |
| **Refill in progress** | Faucet closed, low-level reed reading empty, SeaFlo pump filling the carbonator (per [`future.md:39`](../../hardware/future.md)) | Subtle indicator (top edge of round display: a thin animated line, or icon overlay). Customer can pour from a glass they already have during refill — but if they go back for a second pour during refill, the faucet is interlocked open, so they need to see *why nothing came out.* | Carbonator reed + pump state via ESP32 |
| **CO2 low — soft warning** | Cylinder mass below the "you have a week" threshold (sibling [`co2-runtime-and-depletion-ux-gap.md`](co2-runtime-and-depletion-ux-gap.md) defines the threshold and the math) | Small CO2 icon in a corner of the active-flavor screen. Not interrupting. iOS app gets the push; on-device is a passive flag. | CO2 mass sensor via ESP32 |
| **CO2 critical — hard warning** | Cylinder essentially empty | Full-screen replacement: large "Replace CO2" with the cylinder icon, brand color drops to gray. Customer cannot ignore. Faucet still operates but next pour will be flat (see sibling for the dispense-lockout question — there's a real product decision there). | CO2 mass sensor via ESP32 |
| **Refrigeration fault** | Wall probe doesn't drop within an expected envelope after compressor cycles, OR evaporator probe trips the −8 °C freeze cutout (per [`future.md:56`](../../hardware/future.md)) | Full-screen "Service needed — refrigeration" with the per-unit serial and a QR to `/u/NNN/diag`. Customer-loud signal that something is genuinely wrong, paired with iOS push + email to Derek. | DS18B20 wall + evap probes via ESP32 |
| **Drip-pan alarm** | Backflow vent moisture sensor wet (per [`future.md:121`](../../hardware/future.md)) | Full-screen "Backflow vent — check under sink" with QR to the explainer. Internal buzzer + iOS app per existing spec, plus this on-counter visual that the household sees within seconds even if the buzzer is muffled. | Moisture sensor via ESP32 |
| **Hydrocarbon-sensor pre-alarm** | MQ-6 reading rising but under hard cutout (per [`integrated-firmware-gap.md`](integrated-firmware-gap.md)) | Full-screen "R-600a sensor — service" + QR. Bias to false-positive; if the customer sees this and there's nothing wrong, they tell us; if we hide it and there's a leak, that is the worst-case failure mode. | MQ-6 via ESP32 |
| **Clean-cycle running** | Reservoir clean cycle in progress (sibling [`reservoir-microbio-and-clean-policy-gap.md`](reservoir-microbio-and-clean-policy-gap.md)) | Progress arc + "Cleaning Flavor 1 (3 of 5 minutes)". Faucet inhibited; the lever still moves but does nothing during a clean. Display owns explaining why. | Clean-cycle state machine via ESP32 |
| **Power-cycle / brown-out recovery** | Comm with ESP32 lost or stale | Quiet "Reconnecting…" overlay, 5-second timeout before escalating to "Service needed — communication." Don't panic the customer for a 200 ms blip. | Local timer on RP2040 |
| **Sleep / dim** | No interaction for N minutes, no dispense for M minutes, no warning state active | See U6 below for the brightness model. | Local timer + ESP32 occupancy hints if any |

The protocol implied by this table — what the ESP32 sends to the RP2040 over the UART — needs to be defined as part of this doc. Today `ProtoLink` exists ([`firmware/include/proto_link.h`](../../firmware/include/proto_link.h)) but the message set is the image-management one, not a state-update one. Defining the new message set (e.g. a single `display_state` message with `state_id`, `optional payload`) is part of U1.

**Estimated effort:** ~1 day for the state catalog as a doc, ~0.5 day for the protocol message-set definition. Both before firmware work starts.

### U2 — Define the KRAUS air-switch interaction model

Today: GP29 ADC read maps to one of N slots, immediate switch. That's it. Open questions worth pinning down before the integrated-build firmware solidifies:

- **Single press = next flavor, or single press = the specific flavor for that air-switch position?** The KRAUS is a passive air bulb; the appliance maps its position-or-press to a flavor. With only two flavors, "single press toggles" is the simpler model than "tap counts." The math: one tap → swap; idempotent if the user double-taps to undo.
- **Tap vs hold.** Does a *hold* mean anything? Today, no. Worth deciding now whether hold is reserved for future use (a clean cycle launch? a brightness change? a setup-mode reveal?) or formally has no meaning. Best answer is probably "reserved for future, currently does nothing" so it doesn't accidentally land on an action.
- **Debounce.** A pneumatic air switch behaves differently from a microswitch. The current GP29 ADC read is sampled — what's the debounce window? Per [`firmware/src_display/main.cpp`](../../firmware/src_display/main.cpp) it appears to be implicit in the sample rate. Spec a debounce window in the firmware doc (~50 ms is the typical answer for a bulb-actuated bellows microswitch).
- **Inhibit-during-dispense.** If the user mashes the flavor switch mid-pour, the appliance can't change the served flavor (the pumps are already running on the previously-selected flavor). Two options: ignore the press, or queue it for "next pour." Queue + visual confirmation ("Diet Pepsi — next pour") is the better UX; ignore is the simpler firmware.
- **Inhibit-during-clean.** Same logic — a flavor switch press during a clean cycle is ignored (or queued, same decision as above).
- **First-power-on default.** Which flavor logo shows when the appliance is brand new and has never been pressed? The first flavor in the LittleFS order today. With Ring 1, the customer has poured concentrate into both reservoirs during the install consult — they have no "default flavor" preference. Worth being explicit: default is `flavor 1`, defined per-unit at commissioning.

**Estimated effort:** ~0.5 day for the interaction-model doc, alongside U1.

### U3 — Define the audible-feedback model

The buzzer (DIYables passive, inside the cabinet, [`integrated-firmware-gap.md`](integrated-firmware-gap.md)) is unspec'd today. Worth deciding before firmware lands on a one-off pattern:

- **What sounds (if anything) does the appliance make for normal events?** Recommended: **none.** A premium under-counter appliance should be acoustically invisible during normal use. The compressor cycle and condenser fan are the appliance's natural noise floor (sibling [`compressor-acoustic-budget-gap.md`](compressor-acoustic-budget-gap.md) owns that). Adding a chirp on flavor-switch or first-pour is the wrong instinct — it ages badly and reads as "kitchen gadget" rather than "real fixture."
- **What sounds does it make for warnings?** Recommended: **only critical and hard-alarm states.** Drip-pan moisture, MQ-6 hydrocarbon, refrigeration freeze cutout. Each gets a distinct sub-1-second pattern (e.g. drip-pan = two-tone 800-1200 Hz repeating; MQ-6 = single long 2 kHz, this is the hydrocarbon-safety alarm and needs to be the loudest, most distinct sound the appliance can make).
- **Snooze/mute behavior.** A 3 AM drip-pan alarm needs to be silenceable from the iOS app without losing the visual + portal record. Snooze for 8 hours = "let me sleep, but page me in the morning"; mute permanently is not a thing; resolve = sensor read returns to normal for >5 min.
- **No audible "you have CO2 low."** That's an iOS app push, not an in-kitchen klaxon. The on-counter display owns the visual; the buzzer is reserved for *bad now, not bad soon*.

**Estimated effort:** ~0.5 day for the audio-pattern doc + a per-pattern test routine in the RP2040 firmware (the RP2040 doesn't drive the buzzer, but it's useful for the spec to live with the rest of the UX doc).

### U4 — Design the cold-start commissioning UX (the 20-40 minute first-cooldown)

A real and currently-unspec'd user experience: the customer just finished the install consult, the carbonator just filled, and the refrigeration loop has 20-40 minutes of work to do before the first pour will be cold. The install consult ([`install-consult-playbook-gap.md` I1 Phase B step 8](../2026-05-18/install-consult-playbook-gap.md)) flags this as "founder coaches the customer through the expected cycle time" — but what does the *display* do during those 20-40 minutes?

Proposal: this is the **commissioning state** in U1's catalog, with three sub-stages:

1. **Filling** (~30-60 seconds): "Filling carbonator" + the level-reed indicator.
2. **Pre-cooling** (~5-10 minutes): the wall probe is dropping from ambient (~22 °C) through ~12 °C. Show "Pre-cooling — 18 °C." Number ticks down.
3. **Cooling to service** (~15-30 minutes): the wall probe is dropping through 12 → 2 °C. Show a progress arc around the round perimeter, with the temperature in the center. The arc fills clockwise as °C drops.
4. **Ready** (terminal): the display animates from "2 °C" to the active-flavor logo (the first pour the customer ever does). This is the **Welcome moment**, and it is the cleanest place in the entire appliance lifecycle to put a small piece of brand storytelling — a one-frame "your first pour" text overlay that fades to the flavor logo as the user reaches for the lever.

The commissioning UX runs again — *abbreviated* — every time the appliance returns from a power cycle and the wall temperature is above some threshold (say, 6 °C). On a recovered power cycle from a brief outage with the carbonator still cold, the appliance shouldn't act like it's commissioning from scratch.

This state matters for marketing too: the install-consult video and the per-customer install footage *catch this UX on camera*. A blank screen for 30 minutes is a wasted opportunity. A progress arc with a temperature countdown is the kind of detail that lands as "real engineering" in the 30-second discovery video.

**Estimated effort:** ~0.5 day for the commissioning-UX storyboard + the RP2040 progress-arc rendering routine (one new image type beyond the existing bitmap renderer).

### U5 — Lock the visible-stack finish (and the question of whether the customer can choose)

Today the visible stack is chrome (Westbrass) + matte black (KRAUS + PET-CF shell). That's a defensible aesthetic — it reads as "real fixture meets understated electronics" — but it's an *accidental* aesthetic, not a chosen one. A few decisions worth committing in a single doc, `marketing/visible-stack-finish.md`:

- **Is the chrome Westbrass body a constraint or a choice?** Westbrass R2031-NL ships in other finishes; we picked chrome because that's what the prototype harvested and what fits the budget. If the Founder Edition customer's kitchen has matte-black or brushed-nickel fixtures, the chrome is jarring. Worth pricing the matching-finish variants and deciding whether Founder Edition offers customer choice, or whether the chrome is the single SKU and the customer accepts it.
- **Is the shell color a constraint or a choice?** PET-CF is dark by default but Polymaker and others offer engineered filaments in other colors. The matte-black-PET-CF aesthetic is intentional-looking but the constraint is what was on the shelf. If a Ring 1 customer with a white kitchen asks for a white shell, what do we say?
- **The KRAUS button is matte black already.** Limited variation available — KRAUS sells the same body in several finishes. Matching the shell is the right default. Document it.
- **The display bezel is "whatever the printed shell makes it."** The CAD recess geometry is in [`generate_step_cadquery.py`](../../hardware/printed-parts/faucet/touch-flo-shell/generate_step_cadquery.py). Today the bezel is the print itself — it could be a separate printed insert in a contrasting color, or a tiny aluminum bezel. Cheap decision but a visible one.
- **The Founder Edition story benefits from "we picked this finish, and here's why."** The Standard Edition story can offer choice. This is the kind of decision that ages well only if it's documented now.

**Estimated effort:** ~0.5 day for the doc + a side-by-side render of the variants the founder is willing to offer (Ring 1: probably one finish, then expand). Some of this is photography-driven, not text-driven.

### U6 — Design the display brightness / day-night model

A 128×115 IPS panel in a kitchen sees a wide range of ambient light: bright midday sun through a kitchen window, dim morning, the only-light-on at 11 PM. The current firmware drives the backlight at a fixed level (LCD_BL pin, [`firmware/src_display/main.cpp:28`](../../firmware/src_display/main.cpp), no PWM).

Proposal:

- **Time-of-day brightness.** The ESP32 has an RTC ([`firmware/src/main.cpp`](../../firmware/src/main.cpp) uses RTClib). The ESP32 can send the RP2040 a brightness hint based on local time: 80% during daytime hours, 30% from 8 PM to 7 AM, 10% from 11 PM to 6 AM. This is the cheap, no-extra-sensor version.
- **Ambient light sensor.** The Waveshare RP2040 board doesn't have one. Adding one is a board mod or an I²C peripheral. Probably not worth it for Ring 1.
- **Sleep state.** After N minutes of no flow + no air-switch press, the display drops to a very low brightness and shows only a small idle icon (or goes fully dark). The first faucet-handle motion (caught indirectly via the flow meter momentarily seeing flow) or the first air-switch press wakes it back to full brightness. **This is the showpiece-vs-utility tension** — see U7.
- **Warning states override sleep.** A drip-pan alarm or refrigeration fault forces the display to full brightness regardless of sleep state. The customer should not have to wave at the appliance to see why the buzzer is going off.
- **Burn-in.** The display will be on most of the day for years. The active-flavor logo will be in the same pixel position 23 hours a day. Worth confirming GC9107 IPS panels' burn-in characteristics (IPS is generally robust against burn-in, OLED would not be) and adding a 1-pixel position drift to the rendered logo over hours/days as cheap insurance.

**Estimated effort:** ~0.5 day for the brightness model + ~0.5 day for the RP2040 PWM backlight code (LCD_BL is currently driven as a digital HIGH; switching to LEDC PWM is small).

### U7 — Decide what the "idle showpiece" looks like, and whether that's the same as "ready"

The unresolved tension: when the kitchen is empty and no one is using the appliance, the display can either be:

- **A vivid full-color flavor logo, always on** (showpiece — what a guest sees), or
- **A subdued state or fully off** (utility — saving the panel and not visually nagging the homeowner).

Both are defensible. The marketing analysis biases toward showpiece — every visitor to the kitchen is a potential discovery moment per [`target-market.md`](../../marketing/target-market.md) "The coworker model" — and an always-on logo at moderate brightness is the strongest version of that. The kitchen-as-home analysis biases toward subdued — a flavor brand-mark glowing in the corner of a quiet kitchen at 11 PM is *gauche* in the way a never-dimming microwave display is gauche.

Proposal (worth disagreement):

- **Default: showpiece during daytime hours** (logo full-color, 80% brightness, 7 AM to 8 PM).
- **Subdued in evening** (logo at 30% brightness, 8 PM to 11 PM).
- **Minimal at night** (small monochrome icon at the bottom of the display, 10% brightness, 11 PM to 7 AM, or fully off — toggle in iOS app).
- **Per-customer override in iOS app** ("always showpiece" / "always subdued" / "schedule").

This is the kind of decision where Ring 1 customer feedback will write the doc. Worth picking a reasonable default for unit #1 and asking the customer explicitly in the day-7 touchpoint ([`install-consult-playbook-gap.md` I6](../2026-05-18/install-consult-playbook-gap.md)) what they think of it.

**Estimated effort:** trivial — most of the cost is debate and Ring 1 feedback, not engineering.

### U8 — Photography / video pass on the visible stack

Once U1–U7 are spec'd and the firmware renders the new states, the visible stack needs a photography pass for marketing assets. This is **not** another instance of the [`marketing/video/`](../../marketing/video/) workflow — that exists and is for the long-form/Bushing-style narrative video. This is a small targeted pass:

- The boot screen, on the appliance, in a real kitchen. One frame.
- The commissioning-cooldown progress arc, time-lapsed.
- The idle showpiece state, in daylight and at night.
- The CO2-low warning, the drip-pan alarm, and the refrigeration fault — *staged*, all three, on the appliance. These are the "the appliance can talk to you" demonstrations that anchor the legitimacy story.
- The 30-second pour video re-takes against the new active-dispense animation.

This pass also produces the images that go on the per-unit portal owner page ([`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md)), the install consult slide deck (the founder can show the customer what the display will look like during cooldown *before* they sit there watching it for 30 minutes), and the future marketing video's B-roll.

**Estimated effort:** ~1 day of shooting once the firmware can render the new states. Out of scope until U1–U6 are written.

---

## Migration plan / order of operations

1. **U1 first.** Without the state catalog, nothing else has a target. Producing the catalog forces the rest of the U-numbered decisions; many of them resolve themselves once the catalog exists. ~1 day.
2. **U2 + U3 alongside U1.** Interaction model and audible model are small but should be locked before firmware writes them implicitly. ~0.5 day each, can be done in parallel.
3. **U5 (finish) and U6 (brightness) before any photography pass.** The finish doc settles whether Ring 1 ships chrome+matte-black or offers choice. The brightness model settles whether evening photos show a glowing logo or a subdued one. Both upstream of any visual marketing asset that's supposed to be representative.
4. **U4 (commissioning UX) before unit #1 commissioning.** A Ring 1 customer's first 30 minutes with the appliance, watching the display, is a one-time event per customer. Whatever the display does during that 30 minutes is what they tell their friends about ("you should have seen the screen — it counts down the temperature"). Not commissioning unit #1 with the polished version is a missed Ring 1 marketing-yield moment.
5. **U7 (idle showpiece) is a Ring 1 feedback loop, not a pre-launch decision.** Pick a default, ship, ask in the day-7 touchpoint, revise.
6. **U8 (photography) only after the firmware renders all the new states.** This is downstream of every U above. Order it last.

The work above is roughly 4–5 days of writing + ~1 week of RP2040 firmware updates + ~1 day of photography. None of it is hardware. None of it blocks the integrated-firmware-architecture work in the sibling todo; in fact it gives that work a cleaner target than "show whatever bitmap is selected."

---

## Out of scope for this todo

- **The iOS app screens** — different surface, different real estate, different design constraints. Documented elsewhere (specifically: doesn't yet exist; see the [`ios/SodaMachine/`](../../ios/SodaMachine/) skeleton). The on-device display and the iOS app should **share an information model** — what the appliance knows is what the app shows — but the rendering layers are independent. This todo defines the on-device model; the app render comes later.
- **The Android app** — same as iOS, not in scope. (Note: [`android/`](../../android/) exists as a skeleton; per [`docs/android-port-roadmap.md`](../../docs/android-port-roadmap.md), it follows iOS.)
- **The per-unit portal `/u/NNN`** — web surface, owned by yesterday's [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md).
- **The flavor-bitmap pipeline itself.** [`firmware/src_display/main.cpp`](../../firmware/src_display/main.cpp) already supports up to 10 image slots over LittleFS with CRC verification — the asset pipeline (Photoshop → 128×115 RGB565 binary) is solved. New display states above are renderer changes (text, arcs, animations), not bitmap-uploads.
- **Brand-name usage on the bitmaps themselves.** Sibling [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) owns whether "Diet Pepsi" is a permitted logo on the round display.
- **The Westbrass body's mechanical UX** — the feel of the lever, the throw, the click. Mechanical, harvested, already-known.
- **The hopper, the BiB adapter, the front-panel CO2 inlet, the cabinet-side condenser grilles.** All sub-counter or under-cabinet user touchpoints, not above-counter. Different surface with different design constraints — worth a separate todo (the [`enclosure-exterior-doc-gap.md`](enclosure-exterior-doc-gap.md) sibling is the closest existing).

---

## Suggested next concrete step

Write **U1** as the canonical doc at `firmware/display-states.md`, with the state table fully populated and the ESP32 ↔ RP2040 protocol message-set defined. This is the document the integrated-firmware sibling work implements against. Without it, the firmware will choose its own display semantics by accident.

The most leveraged single passage is the **commissioning / cold-start visual** (U4 above) — that frame is what every Ring 1 customer sees in their first 30 minutes with the product, and what every install-consult video catches on camera. A blank screen during cooldown is a self-inflicted wound on the legitimacy story; a temperature countdown is the kind of detail that converts a "kitchen gadget" frame into a "real engineering" frame. One careful pass on that one screen is the highest-yield design work in this todo.
