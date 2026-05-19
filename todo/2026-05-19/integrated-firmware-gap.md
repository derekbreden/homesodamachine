# The integrated-build firmware does not exist yet

**Author:** hourly agent, 2026-05-19 (fourth of the day)
**Status:** prototype-blocker — recommendation only, not for direct execution
**Audience:** Derek, future agents
**Distinct from siblings:**
- Morning sibling [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) — brand-name legal exposure (post-sale operations).
- Midday sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) — per-SKU stockout policy (post-sale operations).
- Earlier today [`routine-is-optimizing-the-wrong-thing-gap.md`](routine-is-optimizing-the-wrong-thing-gap.md) — meta doc telling this routine to **bias toward the appliance**. This doc is the first one to take that bias seriously.

Following the third sibling's R1: this recommendation, if executed, **changes files in `firmware/` and in `hardware/wiring/`**, and unblocks the next physical bring-up of the integrated build.

---

## TL;DR

The on-counter prototype firmware (`firmware/src/main.cpp`, 3,781 lines) drives the bench: 2 dispense valves + 2 clean solenoids over an L298N, two Kamoer peristaltics, the DIGITEN flow meter, the KRAUS air switch, the RP2040 round display, the ESP32-S3 config display, the RTC. It is the working firmware of record.

The integrated-build wiring and assembly docs ([`hardware/wiring/esp32-pinout.mmd`](../../hardware/wiring/esp32-pinout.mmd), [`hardware/wiring/valve-control.mmd`](../../hardware/wiring/valve-control.mmd), [`hardware/assembly/firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md), [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md)) describe a different ESP32 program: 12 solenoids over 2× MCP23017 + 2× ULN2803A, two DS18B20 temperature probes on a 1-wire bus, 2 carbonator reed switches on direct GPIO + 8 reservoir reed switches via the MCP23017s, the SeaFlo diaphragm pump on relay #2, the hermetic compressor on relay #1 with hysteresis + freeze cutout + 3-minute min-off, the MQ-6 hydrocarbon sensor in the compressor shroud, the backflow drip-pan moisture sensor, and a DIYables passive buzzer for the audible alarm output. None of that integrated-build behavior is in the firmware on `main`.

This is not a per-feature gap. It is the *firmware target itself* — there is no PlatformIO env for the integrated controller, no `firmware/src_integrated/`, no architecture doc in `firmware/`, and no enumerated set of factory defaults committed anywhere code can read them. The integrated build's first power-on has nothing to flash that does anything useful past sensor I/O.

Acceptance and commissioning procedures already exist and are good. They simply cannot run.

---

## Evidence

### 1. The firmware on `main` is prototype-only

[`firmware/src/main.cpp`](../../firmware/src/main.cpp), top-of-file (lines 16-34):

```cpp
// Prototype valve topology (2 dispense valves + 2 clean solenoids on
// L298N boards #2 and #3) …
#define A_ENB  12    // dispensing solenoid valve
#define B_ENB   4    // dispensing solenoid valve
// ── L298N Board C (clean solenoids) ──
#define CLEAN_SOL1_PIN 27   // clean solenoid flavor 1, L298N #3 Channel A ENA
#define CLEAN_SOL2_PIN 17   // clean solenoid flavor 2, L298N #3 Channel B ENB
```

GPIO 4, 12, 17, 27 are reused by the prototype for dispense + clean solenoids. Those same four pins are reassigned in [`hardware/wiring/esp32-pinout.mmd`](../../hardware/wiring/esp32-pinout.mmd) to the integrated build's refrigeration + carbonator subsystem (GPIO 4 = relay #2 to diaphragm pump, GPIO 17 = carbonator low reed, GPIO 27 = carbonator high reed, and GPIO 12 stays free as bootstrap-sensitive). On the integrated build, the prototype's pin macros will short-circuit the refill path and the carbonator level-reed inputs the moment the firmware boots. The same firmware cannot drive both topologies.

Includes (lines 1-10): `Arduino.h`, `Wire.h`, `RTClib.h`, `LittleFS.h`, `ArduinoJson.h`, `PersistentLog.h`, `proto_link.h`, `proto_msg.h`, `fw_version.h`. No `OneWire`, no `DallasTemperature`, no `Adafruit_MCP23X17`. The integrated build's two MCP23017s and two DS18B20s have no code path.

`grep` confirms:

| Integrated-build feature | In `firmware/src/main.cpp`? |
|---|---|
| DS18B20 read / 1-wire bus | no |
| MCP23017 / I²C expander | no |
| 12-valve topology-table sequencer | no |
| Compressor relay (GPIO 14) + 3-min min-off + freeze cutout | no |
| SeaFlo diaphragm-pump relay (GPIO 4) | no — pin is the prototype B_ENB |
| MQ-6 hydrocarbon-sensor read | no |
| Backflow drip-pan moisture-sensor read | no |
| Passive buzzer (LEDC PWM) | no |
| Reservoir reed-switch chain (8 × MCP23017 inputs) | no |
| Carbonator level reeds (GPIO 17, 27) | no — pins are the prototype clean-solenoids |

### 2. The pinout doc has known holes for already-purchased sensors

[`hardware/wiring/esp32-pinout.mmd`](../../hardware/wiring/esp32-pinout.mmd) shows the integrated-build pin assignments for compressor relay (GPIO 14), refill relay (GPIO 4), DS18B20 bus (GPIO 16), and two carbonator reeds (GPIO 17, 27). It does **not** show:

- **MQ-6 hydrocarbon-sensor analog input.** Module has analog + digital outputs. Sensor needs ESP32 ADC1 (ADC2 conflicts with WiFi). Free ADC1 GPIOs after current assignments: 36, 39 (both input-only — fine for an analog sensor). Not in the diagram.
- **Backflow drip-pan moisture sensor.** [`hardware/wiring/ac-wiring-schedule.md`](../../hardware/wiring/ac-wiring-schedule.md) SIG-9 explicitly says: *"ESP32 GPIO (TBD) … pin not yet assigned in `esp32-pinout.mmd`."* Same doc Open items: *"Backflow moisture sensor pin assignment — needs to land in `esp32-pinout.mmd`."* Outstanding since this part was committed.
- **DIYables passive piezo buzzer.** [`hardware/purchases.md`](../../hardware/purchases.md) §10 (2026-05-11 entry) commits a passive buzzer driven by ESP32 PWM (LEDC) so firmware can vary pitch + cadence for "cycle-complete chime" vs "leak alarm." Buzzer needs one GPIO with LEDC. Not in the pinout.
- **Condenser-fan low-side switching.** [`assembly/firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) step 7 says the fan is *"driven by MCP23017 0x21 PA4 through ULN2803A U2 channel 5"* but the pinout's `VALVE_CHAIN` block doesn't enumerate this bit. The doc names the bit; the diagram doesn't.
- **L298N pump direction pins.** [`hardware/future.md`](../../hardware/future.md) "Flavor subsystem" says *"Pump direction is forward-only. Filling, dispensing, and clean-cycle operations are selected by the valve manifold, not by reversing the pump."* The pinout shows IN1/IN2 for each L298N channel — which is fine if both pump directions are wired statically, but the firmware then doesn't need to drive IN2 at all. Worth normalizing the pinout to match the design intent (forward-only).

These are the sensors and actuators the integrated firmware has to know about on day one. None of them have a pin to land on.

### 3. Commissioning + acceptance describe firmware that does not exist

[`hardware/assembly/firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) steps 6–9 enumerate everything the integrated firmware must do on first boot:

- Print a periodic sensor-health frame: I²C ACKs at 0x20 / 0x21 / 0x68, two DS18B20 addresses with first-read temperatures, all 10 reed baselines, flow-meter pulse count, air-switch debounced press count, MQ-6 baseline (after ~60 s warm-up), drip-pan baseline.
- Accept a serial-console command that walks the 12 solenoids one at a time and confirms each click.
- Accept a serial-console command that briefly spins each peristaltic pump.
- Accept a serial-console command that briefly spins the condenser fan.
- Accept a firmware-override compressor-on / compressor-off command, with the 3-minute min-off guard dropped for the override and re-armed after.
- Accept a setpoint-query command that returns: tank target 2 °C, hysteresis ±2 °C, freeze-protect cutoff −8 °C, compressor minimum off-time 3 min, carbonator refill threshold = low-level reed, backflow alarm armed.

Acceptance ([`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md)) extends from there: an interactive "bench-acceptance mode," commanded fill / dispense / metered-ratio / clean / air-purge cycles per the topology-table operations in [`hardware/topology/fluid-topology.md`](../../hardware/topology/fluid-topology.md), 8-hour burn-in with a 75-minute dispense timer, per-serial JSON log archived to disk.

None of those serial commands exist in `firmware/src/main.cpp`. No code path produces the sensor-health frame. No factory defaults are stored as named constants the way `step 9` describes them. The firmware passes a `fw_version.h` build ID over its existing proto-link, but that is the prototype's version, not the integrated firmware's.

### 4. The hardware-only-vs-firmware-read story for the MQ-6 is inconsistent across docs

A doc bug worth flagging while the spec is open. The MQ-6 is described two different ways:

- [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) "Safety" (line 25): *"Thermal fuse + gas sensor backstop the soft (firmware) cutoffs so a controller failure can't keep the compressor energized through a thermal or leak event."* Reads as **hardware-only backstop** (not firmware-dependent).
- [`hardware/purchases.md`](../../hardware/purchases.md) 2026-05-11 fire-safety entry: *"polled by the ESP32 alongside the existing tank-wall and evap-coil DS18B20 probes; triggers a shut-down + user-visible alarm well below the LFL."* Reads as **firmware-polled** with firmware-driven shutdown.
- [`hardware/assembly/firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) step 6: *"expect a clean-air baseline reading on its analog input."* Reads as **firmware analog read**.
- [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) burn-in watch: *"any MQ-6 trip is hard-fail … visible on the config display and audible at the buzzer."* Reads as **firmware-routed alarm output** through the buzzer.

Three of four docs say firmware-polled with firmware-driven shutdown + alarm; one (refrigerant-loop.md) implies the gas sensor is independent of firmware. The MQ-6 module has a digital comparator output as well as analog, so it *could* be wired purely as a hardware interlock (digital-out into the SF76E circuit or a dedicated relay coil) — but that isn't what's on the BOM or in the pinout intent. The integrated firmware spec needs to settle this: **MQ-6 is firmware-polled, drives the buzzer + display alarm, and triggers a firmware-controlled compressor cutoff**, with the SF76E thermal fuse as the genuinely hardware-only backstop. If that lands, refrigerant-loop.md "Safety" needs one sentence updated to match.

### 5. There is no firmware-side spec doc

`firmware/` contains no README, no `SPEC.md`, no `ARCHITECTURE.md`. The integrated build's required behavior lives in `hardware/assembly/*.md` and `hardware/wiring/*.mmd` — appropriate for the *hardware* design, but it means firmware development has no in-tree source of truth to gate against. A new firmware author (or a future agent doing the work) has to reconstruct the behavior by reading six hardware docs and one mermaid diagram and inferring the pin assignments the diagram doesn't yet contain.

`fw_version.h` is auto-generated by [`firmware/pre_build.py`](../../firmware/pre_build.py) and is the only `firmware/`-side document of any kind, which is appropriate for a build-stamp file but not a substitute for a spec.

### 6. PlatformIO env layout doesn't have an integrated-build target

[`platformio.ini`](../../platformio.ini) defines three envs:

- `[env:esp32dev]` — builds `firmware/src/` (prototype controller). This is the env [`assembly/firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) step 3 invokes (`./tools/flash.sh esp32dev`).
- `[env:rp2040_display]` — builds `firmware/src_display/` (above-counter round display, unchanged between prototype and integrated build).
- `[env:esp32s3_config]` — builds `firmware/src_config/` (config display, also unchanged).

`esp32dev` points at the prototype source. The integrated controller needs a different source tree (or a build-time flag), a different pin map, and a different set of library dependencies (`OneWire`, `DallasTemperature`, `Adafruit_MCP23X17` at minimum). [`assembly/firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) Open items §2 already flags the same question — *"whether the firmware has a dedicated 'factory test' mode separate from production mode"* — but frames it as a factory-vs-production split. The actually-pressing split is prototype-vs-integrated, and that one is not flagged anywhere.

---

## What changes in the repo if this is executed

Per the third sibling's "what would this change" test, the honest answer is:

- **`firmware/src/main.cpp`** stays as the prototype. **New `firmware/src_integrated/main.cpp`** holds the integrated controller. Two source trees, two PlatformIO envs (`esp32dev_prototype` + `esp32dev_integrated`), both targeting the ESP32-DevKitC-32E.
- **New `firmware/SPEC.md`** documents the integrated controller's required behavior: pin map (linking back to `hardware/wiring/esp32-pinout.mmd` as the diagram-of-record), valve topology-table (linking to `hardware/topology/fluid-topology.md`), sensor-health frame schema, serial test-command interface, factory defaults (2 °C target, ±2 °C hysteresis, −8 °C freeze cutoff, 3-min min-off, low-reed refill threshold, MQ-6 LFL fraction trip-point, drip-pan-wet trip), and the alarm-output cadences for the buzzer.
- **`hardware/wiring/esp32-pinout.mmd`** gains pins for MQ-6 analog, drip-pan moisture digital, buzzer PWM, and the condenser-fan bit on MCP23017 0x21 PA4 (currently named in commissioning but not in the diagram).
- **`hardware/assembly/refrigerant-loop.md`** "Safety" section gets one sentence updated to call the MQ-6 firmware-polled (with the SF76E as the hardware-only backstop), resolving the inconsistency in §4 above.
- **`hardware/assembly/firmware-and-commissioning.md`** Open items §2 gets replaced with a more honest item: *"the integrated firmware does not yet exist; this procedure is the spec the firmware must satisfy, not a description of working firmware."* Or — if the firmware is built first — that item is closed entirely and the procedure is verified against actual flashable artifacts.
- **`platformio.ini`** gains an `esp32dev_integrated` env (or whatever name fits) with the `OneWire` + `DallasTemperature` + `Adafruit_MCP23X17` lib deps.

Six files change minimum: one new source tree, one new spec doc, one mermaid update, two prose-doc clarifications, one build-config addition. That moves the next physical bring-up forward by orders of magnitude — the cold core + refrigerant loop + plumbed manifold can power up and have something to actually run on the ESP32.

---

## Recommendation

Three actions, in this order. All three are firmware-side or wiring-doc-side; none touch the existing prototype, the cold core, the refrigerant loop, or the customer-facing surfaces.

### R1 — Land the missing pin assignments in `esp32-pinout.mmd` first

This is the cheapest action and unblocks both the firmware spec and the wiring schedule. Concretely:

- **MQ-6 analog** → GPIO 36 (input-only, ADC1 channel 0). Free per the current diagram; closest to the existing GPIO 34 RX from S3 so the analog header on the electronics shelf is geographically nearby.
- **Drip-pan moisture** → GPIO 39 (input-only, ADC1 channel 3). Reads as digital (high-impedance dry, low when wet), but parking it on an ADC pin allows firmware to threshold against an analog reading if a binary switch turns out to be flaky.
- **Buzzer** → GPIO 2 (general-purpose, LEDC-capable). Bootstrap-sensitive but only as a *strapping* pin at boot — driving it after boot is fine, and a passive buzzer module with its own transistor stage is high-impedance during boot so the strap reads normally.
- **Condenser fan** → leave on MCP23017 0x21 PA4 / ULN2803A U2 channel 5 as already named in commissioning; add the connection to `valve-control.mmd` so the diagram is consistent with the prose.
- **L298N IN3/IN4** (forward-only pump direction) → either wire IN3/IN4 to fixed levels at the L298N board (no GPIO required) or drop them from the pinout. Both are fine; pick one.

This is one file's worth of edits to [`esp32-pinout.mmd`](../../hardware/wiring/esp32-pinout.mmd) plus a paired update to [`valve-control.mmd`](../../hardware/wiring/valve-control.mmd) and the matching SIG-9 entry in [`ac-wiring-schedule.md`](../../hardware/wiring/ac-wiring-schedule.md). Half an hour of work; clears 100 % of the "pin-not-assigned" Open items in those docs.

### R2 — Write `firmware/SPEC.md` *before* writing the integrated firmware

Single-document source of truth for the integrated controller's required behavior. Sections:

1. **Build target.** Board, PlatformIO env name, lib deps.
2. **Pin map.** Direct copy of `esp32-pinout.mmd` after R1 lands, plus the MCP23017 0x20 / 0x21 input/output bit-by-bit assignment from `valve-control.mmd`. Source-of-truth pointer back to the diagrams, not a duplicate; this doc reads the diagrams.
3. **Subsystems, one section each:**
   - Carbonator control: refill state machine (level-reed-driven, faucet-closed interlock, SeaFlo via relay #2).
   - Refrigeration control: hysteresis loop on tank-wall DS18B20 (off at 2 °C, on at 4 °C); freeze cutout on suction-line DS18B20 (hard stop at −8 °C, requires manual re-arm or a long cooldown); 3-min min-off guard on Teyleten relay #1; condenser fan gated alongside the compressor.
   - Flavor dispense: valve-table sequencer keyed off the operations in [`fluid-topology.md`](../../hardware/topology/fluid-topology.md); peristaltic pump A/B forward-only via L298N.
   - Reservoir level: 4 reeds per reservoir → effective fill level (13 steps), surfaced over the proto link to the config display.
   - Safety: MQ-6 polled at ~1 Hz, threshold trip cuts compressor relay and chimes alarm cadence A on the buzzer; drip-pan moisture polled at ~1 Hz, wet trip chimes alarm cadence B; SF76E thermal fuse is hardware-only and out of scope here.
   - User interface: KRAUS air switch debounce + flavor-select broadcast to the RP2040; faucet-handle flow-sensor reads from DIGITEN.
4. **Serial test-command interface.** Enumerate every command [`firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) and [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) name, with the expected request format and response payload.
5. **Factory defaults.** Named constants with the exact numbers from `firmware-and-commissioning.md` step 9.
6. **Sensor-health frame schema.** JSON or framed-binary, structured so the per-serial commissioning log in step 10 can just snapshot the latest frame.
7. **Alarm-cadence catalog.** Buzzer patterns for ready-chime, cycle-complete, MQ-6 trip, drip-pan trip, freeze-cutout, refill-pump-overrun.

This is the doc that turns commissioning + acceptance from aspirational procedures into executable ones. It also makes the inconsistency in §4 above unambiguous, because the spec has to either contain "firmware polls MQ-6" or not.

### R3 — Set up the second PlatformIO env before writing a line of code

Add `[env:esp32dev_integrated]` to [`platformio.ini`](../../platformio.ini), pointing `build_src_filter` at a new `firmware/src_integrated/` directory. Lib deps add `paulstoffregen/OneWire`, `milesburton/DallasTemperature`, `adafruit/Adafruit MCP23017 Arduino Library`. The new src tree starts with a near-empty `main.cpp` that boots, initializes the I²C bus, scans for the two MCP23017s + DS3231, reads the two DS18B20 addresses, and prints one sensor-health frame per second over Serial. That alone is enough to dry-run [`firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) step 6, which is the single highest-value step to unblock first — every later step depends on knowing the chassis isn't a wiring disaster.

Order of build-out after the boot-and-scan skeleton lands:

1. DS18B20 + reed reads → sensor-health frame complete. Unblocks commissioning step 6.
2. Compressor relay #1 with hysteresis + freeze cutout + min-off. Unblocks commissioning step 8 and the entire refrigeration side of acceptance.
3. SeaFlo relay #2 + level-reed-gated refill. Unblocks acceptance step 3.
4. 12-solenoid topology-table sequencer + peristaltic pumps. Unblocks acceptance steps 6, 7, 8, 9.
5. MQ-6 + drip-pan polling + buzzer alarms. Closes the safety subsystem; required for burn-in step 11.
6. Serial test-command interface (the override commands `firmware-and-commissioning.md` and `acceptance-and-burn-in.md` invoke).
7. Per-serial commissioning + acceptance log emission.

Each of the seven steps above is hours-to-a-day of work, not weeks. The reason to do them in this order is that every later step needs the sensor reads (step 1) and the safety interlocks (step 5) to be live before it can be exercised against real hardware. Done in any other order, the integrated firmware lives in a state where flashing it onto the integrated build is genuinely unsafe (the compressor could energize without the freeze cutout).

---

## What this doc is *not* asking for

- Not asking to delete `firmware/src/main.cpp` or stop using it. It is the working prototype controller and stays in service on the bench unit until the integrated build is ready to take over.
- Not asking to re-pin the existing prototype to match the integrated pinout. The reuse of GPIO 4 / 17 / 27 between the two builds is fine *because they are two builds*. The integrated env is a clean source tree with its own pin map.
- Not asking the firmware to handle customer-side firmware binding, OTA updates, cloud pairing, or the iOS/Android app. All of those are post-first-sale per [`firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) step 5 ("customer-side firmware binding … is **not** done here").
- Not asking to write firmware in this doc. The recommendation is for someone (Derek, or a future agent invoked with that intent) to write it; this doc is a gap report and a sequencing argument.

---

## The single thing

If the recommendation collapses to one sentence:

> The integrated build's pressure vessel, cold core, refrigerant loop, and flavor manifold are months ahead of the firmware that will control them — write `firmware/SPEC.md` and `firmware/src_integrated/main.cpp` before the cold-core assembly procedure is ever run on a real unit, so that the unit has something to boot into when first power lands.

Everything else is implementation detail.
