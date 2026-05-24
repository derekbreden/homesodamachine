# Firmware and Commissioning

The production procedure for first-time firmware flash and DC-side commissioning of a fully wired chassis. Takes the never-powered output of [`wiring.md`](wiring.md) — AC and DC continuity checks already passed — through three MCU flashes, a controlled first power-on under PSU, a sensor-health walkthrough, a valve self-test, and a brief firmware-driven compressor cycle confirming relay #1 switches the AC leg. Stops short of any test that requires water or CO2 — those live in [`acceptance-and-burn-in.md`](acceptance-and-burn-in.md).

Customer-side firmware binding (Wi-Fi credentials, cloud pairing, app association, per-customer ratio tuning) is **not** done here. Firmware ships with factory defaults; the iOS/Android app handles binding at first install. This procedure ends with a unit that boots clean, self-tests clean, and is ready to take water + CO2 in the next station.

Design intent and runtime behavior live in [`../future.md`](../future.md) "Refrigeration subsystem" + "Level sensing". Pin assignments and wiring topology live in [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd) and [`../wiring/valve-control.mmd`](../wiring/valve-control.mmd). The flash wrapper script and PlatformIO environment names live at the repo root.

## Scope

In: a fully wired chassis fresh out of [`wiring.md`](wiring.md) — AC and DC continuity checks passed, never powered. The flash tooling — three USB cables (one micro-USB for the ESP32-DevKitC, one USB-C for the ESP32-S3, one micro-USB for the RP2040), the `./tools/flash.sh` wrapper (see project root `CLAUDE.md`), and the firmware source tree at `/firmware/` configured per [`/platformio.ini`](../../platformio.ini). A multimeter for runtime DC-rail spot checks. A serial console (`pio device monitor`) for log capture.

Out:

- All three MCUs (ESP32-DevKitC for main control, ESP32-S3 for the front-face fixed config display, RP2040 for the front-face detachable round flavor display) flashed with the current firmware on `main`.
- First DC power-on under PSU control succeeds with no smoke, no breaker trip, no thermal-fuse open.
- Sensor health passes: both DS18B20 probes addressed on the 1-wire bus and reporting within ±2 °C of room ambient; all 10 reed switches (2 carbonator + 4 per flavor reservoir × 2 reservoirs) settled to their no-magnet "empty" baseline; the DIGITEN flow meter ticks pulses when its impeller is rotated by hand; the KRAUS air switch reads pressed/unpressed; the MQ-6 hydrocarbon sensor on the rear interior enclosure wall has reached operating temperature and reads its clean-air baseline; the backflow drip-pan moisture sensor reads dry.
- Both MCP23017 GPIO expanders ACK on the I²C bus at 0x20 and 0x21, with the DS3231 RTC at 0x68 also responsive.
- Valve self-test pass: each of the 12 Beduan solenoids clicks once with audible / visual confirmation, and both Kamoer peristaltic pumps spin briefly under L298N Board A drive.
- Relay #1 verified switching the compressor's AC leg under a deliberate firmware override: the suction-line DS18B20 reads a few degrees lower within a couple of minutes of the override starting (running dry, no water in the carbonator), confirming the relay is making AND that DS18B20 #2 is on the correct probe.
- Firmware setpoints loaded with factory defaults: **tank target 2 °C, hysteresis ±2 °C** (compressor off at 2 °C, on at 4 °C), **freeze-protect cutoff −8 °C** on the suction-line probe, **3-minute minimum off-time** for the compressor start capacitor, refill threshold on the carbonator's low-level reed.
- Per-serial commissioning log archived (sensor readings, I²C ACK list, valve click confirmation, compressor-cycle suction-line ΔT).

Not in scope: any acceptance test that requires water or CO2 (that's [`acceptance-and-burn-in.md`](acceptance-and-burn-in.md)); customer-side firmware binding via the iOS/Android app at install (post-shipping); the over-the-air firmware-update flow (not in scope for first-unit shipping).

## Inputs per appliance

| Item | Source / spec | Notes |
|---|---|---|
| Wired chassis | Output of [`wiring.md`](wiring.md) | Never powered. AC + DC continuity checks passed. Compressor shroud closed and grounded. |
| Firmware source tree | [`../../firmware/`](../../firmware/) on the build host, current `main` | PlatformIO project; envs `esp32dev`, `rp2040_display`, `esp32s3_config` (see [`/platformio.ini`](../../platformio.ini)). |
| Flash wrapper | [`/tools/flash.sh`](../../tools/flash.sh) | Pauses the serial logger during upload; pre-flights the sibling `PersistentLog` dependency. Invocation: `./tools/flash.sh <env>`. |
| USB cables | 1× micro-USB (ESP32-DevKitC), 1× USB-C (ESP32-S3), 1× micro-USB (RP2040) | Build-bench stock; not per-unit consumable. |
| Multimeter | Build-bench stock | DC-rail spot checks at 12 V, 5 V, 3.3 V test pads. |
| Serial monitor | `pio device monitor -e esp32dev` (115200 baud) | Captures the ESP32 boot log + structured commissioning output for the per-serial archive. |
| Commissioning-log template | TBD — see Open items | Per-unit serial + sensor readings + I²C ACK list + valve confirmation + suction-line ΔT during the relay #1 verification. |

Tooling (per-unit-amortized): one build-bench station with a PSU-controlled outlet feeding the C14 input, a current meter inline with the PSU output for the 12 V rail, USB hub on the bench host, the serial-logger background process from `tools/serial_logger.py`.

## Procedure

### 1. Verify wiring-out inputs

Before any power, walk the chassis once against [`wiring.md`](wiring.md) output condition: compressor shroud closed and grounded, electronics shelf populated and fastened, ground bus continuous from C14 earth pin to every exposed-metal bond point, all JST XH housings seated, the I²C bus terminated only at its end devices (no stray stubs), 4.7 kΩ pull-up present on the DS18B20 data line.

This is a *re-look*, not a re-test — the AC and DC continuity sign-offs from `wiring.md` are not repeated here. If anything on the shelf has moved since `wiring.md` signed off, return the unit there before continuing.

### 2. First DC power-on under PSU control

Power the C14 inlet through a bench PSU-controlled outlet, not direct wall power. The Teyleten relay #1 must remain de-energized for this step — the firmware boots into "all off" by default, but the PSU-controlled outlet is the hardware backstop.

Bring up in this order, verifying each rail with the multimeter before the next:

1. PSU output enabled — verify **12 V** at the distribution-block test point (PSU is the Mean Well IRM-90-12ST, see [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) run DC-1). Expected ~12.0 V ± 0.2 V at no load.
2. **5 V regulator output** at the regulator pin header — expected 5.0 V ± 0.1 V. This feeds the MCUs and the relay-module VCC.
3. **3.3 V regulator output** — expected 3.3 V ± 0.05 V. This feeds the I²C-bus pull-ups, the MCP23017 logic side, and the DS18B20 data-line pull-up.

If any rail is out of tolerance, kill the PSU and return the unit to `wiring.md`. Do **not** energize the AC side (compressor + fan) at this step — relay #1 stays de-energized until step 7.

Spot-check current draw at the PSU: cold idle with all MCUs off should sit near 0 — the relay coils are de-energized, no valves are driven, no pumps. A few mA from the LV pull-ups and the relay-module opto-coupler quiescent draw is expected.

### 3. Flash the ESP32-DevKitC main controller

Plug the micro-USB cable into the ESP32-DevKitC on the electronics shelf. The DevKitC's onboard CP2102 enumerates as a USB CDC port on the build host.

From the repo root:

```
./tools/flash.sh esp32dev
```

The wrapper pauses the background serial logger, runs `pio run -e esp32dev -t upload` per [`/platformio.ini`](../../platformio.ini) `[env:esp32dev]`, then resumes the logger. Expected outcome: build succeeds, upload reaches 100 %, ESP32 resets, the serial monitor at 115200 baud shows the firmware boot banner with the `fw_version.h` build ID.

If the build fails on the `symlink://${PROJECT_DIR}/../PersistentLog` dependency, fix the sibling-repo placement before continuing — the wrapper pre-flights this and prints the exact remediation path.

### 4. Flash the ESP32-S3 config display

Plug the USB-C cable into the ESP32-S3-DevKitC-1 (the front-face fixed config display, mounted in its recess per [`../printed-parts/enclosure/front-panel/README.md`](../printed-parts/enclosure/front-panel/README.md) — see [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd) UART subgraph). It enumerates as a native USB-CDC device — the build flag `ARDUINO_USB_CDC_ON_BOOT=1` in `[env:esp32s3_config]` brings the CDC port up immediately on boot.

```
./tools/flash.sh esp32s3_config
```

Confirm the LVGL splash renders on the GC9A01 display panel after reset. The S3 also pulls in `PersistentLog` and `NimBLE-Arduino` per `[env:esp32s3_config]` — same sibling-repo pre-flight applies.

### 5. Flash the RP2040 round display

**Important:** the RP2040's USB does not enumerate while its UART is connected to the ESP32 (the UART line steals the USB pins on the round-display module variant used here). The flash wrapper warns about this on the `rp2040_display` env. Disconnect the UART line at the JST XH connector on the electronics shelf before plugging the micro-USB into the RP2040, then reconnect after the flash completes.

```
./tools/flash.sh rp2040_display
```

The RP2040 enters BOOTSEL automatically through the Earle Philhower core's USB reset. Expected outcome: the round display shows the default flavor logo (flavor 1) within ~2 seconds of reset.

Reconnect the UART JST and re-verify by toggling the KRAUS air switch by hand: the active flavor logo should change on each press once the ESP32 begins broadcasting flavor-select frames over Serial2.

### 6. Sensor health walkthrough

With all three MCUs running their default firmware, open the serial monitor on the ESP32:

```
pio device monitor -e esp32dev
```

The default firmware periodically prints a sensor-health frame. Step through each line:

- **I²C scan** — expect ACKs at `0x20` (MCP23017 valves + Reservoir A reeds), `0x21` (Reservoir B reeds + condenser-fan driver bit), `0x68` (DS3231 RTC). Any missing ACK is a wiring or solder defect at that device.
- **DS18B20 bus** — expect exactly two devices addressed on the 1-wire bus on GPIO 16 (tank-wall probe + suction-line probe). Both should report within ±2 °C of room ambient with the compressor de-energized. If only one address enumerates, suspect a parasitic-power miswire or the 4.7 kΩ pull-up.
- **Carbonator reeds** (GPIO 17 low, GPIO 27 high) — both INPUT_PULLUP, both reading high (no magnet present, no float installed yet). Bring a small bench magnet near each reed in turn and confirm it pulls low.
- **Reservoir reeds** — all 8 (Reservoir A on MCP23017 0x20 PB[4:7], Reservoir B on 0x21 PA[0:3]) reading their no-magnet baseline. Architecture and calibration in [`../printed-parts/cold-core/reservoir/level-sensing.md`](../printed-parts/cold-core/reservoir/level-sensing.md). Same bench-magnet check per reed.
- **DIGITEN flow meter** (GPIO 23) — manually rotate the impeller with a clean implement; expect a pulse count increment per rotation in the serial output.
- **KRAUS air switch** (GPIO 13) — press and release by hand; expect the firmware's edge-detected count to increment on each press.
- **MQ-6 hydrocarbon sensor** — needs ~60 s warm-up to reach operating temperature. After warm-up, expect a clean-air baseline reading on its analog input (verify the bench air is free of solvents or LPG nearby — wave clean air across the sensor or move the chassis briefly to a clean-air environment if needed). Architecture: the MQ-6 sits low on the rear interior enclosure wall, mesh facing horizontally inward (the bare sensor's orientation is unconstrained per the Winsen datasheet; this position catches dense R-600a as it pools at the cabinet floor from any of the dominant brazed-joint leak sites) — the hardware-only backstop to the firmware-controlled cutoffs ([`refrigerant-loop.md`](refrigerant-loop.md) "Safety").
- **Backflow drip-pan moisture sensor** — reads dry (high impedance). Confirm by briefly bridging the sensor pads with a damp probe and watching the firmware reading swing.

Record each reading in the per-serial commissioning log. Any out-of-bounds reading at this step blocks the unit from proceeding to step 7.

### 7. Valve and peristaltic-pump self-test

The firmware exposes a self-test command over the serial console that walks each of the 12 Beduan solenoids individually and then spins each peristaltic pump briefly. Trigger it from the monitor prompt.

- **Solenoid sequence** — the firmware drives each MCP23017 0x20 output through ULN2803A U1 or U2 in turn (V-A through V-K-B; see [`../wiring/valve-control.mmd`](../wiring/valve-control.mmd)). Each coil energizes for ~250 ms then releases. Expected: 12 distinct clicks, each accompanied by the orange ULN-channel-on indicator if the module has one. Listen for stuck-on coils (no audible release click).
- **Condenser fan** — driven by MCP23017 0x21 PA4 through ULN2803A U2 channel 5. The self-test gives the fan a brief 1-second run. Expected: audible spin-up of the 12 V DC brushless axial mounted to the enclosure side wall, then coast-down.
- **Peristaltic pumps** — driven by the L298N Board A on the electronics shelf. The self-test spins Pump A forward for ~1 s, then Pump B. Expected: each silicone tube head rotates visibly. No flavor is loaded yet; the head turns dry.

Any failure here is wiring or driver-module (resolder, swap module, or trace defect). Resolve and re-run before continuing.

### 8. Relay #1 compressor-cycle smoke test

This is the only step that energizes the AC side. The carbonator is **empty** (no water, no CO2) — the run is brief and intentional, just enough to confirm the AC leg switches and the suction line cools.

Trigger the firmware-override compressor-on command at the serial console. The firmware drops the 3-minute minimum-off-time guard for this command only, asserts GPIO 14, energizes the Teyleten relay #1, and closes the AC leg into the compressor terminal block inside the shroud.

Watch for, in order:

1. **PSU current bump** at the inline meter — the relay coil pulls ~70 mA additional through the 5 V rail; small but visible.
2. **Compressor audible start** — the PTC start relay clicks and the hermetic compressor's motor spins up. The clip-on overload should not trip on a healthy compressor; if the overload opens, kill the override immediately and return to [`refrigerant-loop.md`](refrigerant-loop.md) for diagnosis.
3. **Current draw at the AC side** — within nameplate (a couple of amps RMS on the 120 VAC leg for the harvested ice-maker compressor). Verify with a clamp meter on the switched-hot run AC-4 if the build bench has one.
4. **Suction-line DS18B20 temperature** — drops a few degrees within a couple of minutes. The cold core has no water to absorb heat, so the suction line cools faster than it will in normal operation; this is the intended diagnostic, not normal-operation behavior.

After 30–60 seconds, send the firmware-override compressor-off command. The compressor de-energizes, the suction-line probe begins warming back toward ambient, and the 3-minute minimum off-time guard re-arms.

This is **not** a refrigeration commissioning step. Full thermal cycling under water load happens at [`acceptance-and-burn-in.md`](acceptance-and-burn-in.md). All this step proves is: (a) relay #1 makes the AC leg, (b) the compressor draws nameplate current, (c) the suction-line probe is on the right probe.

### 9. Verify setpoints loaded

Query the firmware over serial for its loaded setpoints. Expected:

- Tank target: **2 °C**
- Hysteresis: **±2 °C** (compressor on at 4 °C, off at 2 °C)
- Freeze-protect cutoff: **−8 °C** on the suction-line probe
- Compressor minimum off-time: **3 min**
- Carbonator refill threshold: low-level reed (GPIO 17)
- Backflow alarm: armed on drip-pan moisture sensor

These are baked into the firmware on `main` as factory defaults; no per-unit setting is required here. Customer-side tuning (ratio adjust, Wi-Fi binding, cloud pairing) happens through the iOS/Android app post-install.

### 10. Archive the per-serial commissioning log

Snapshot the serial-monitor output from steps 6–9 into a per-serial log file. At minimum capture: firmware build ID (`fw_version.h`), I²C ACK list, DS18B20 addresses + first-read temperatures, all 10 reed baselines, flow-meter pulse count, air-switch press count, MQ-6 baseline, drip-pan baseline, valve self-test pass/fail per channel, suction-line probe temperatures before/during/after the relay #1 verification.

Where this log lives — local file under `/commissioning/<serial>/`, uploaded to cloud, both — is an Open item below. Working position: keep the file locally on the build host until that decision lands.

## Output condition

A commissioned unit is:

- All three MCUs flashed with current `main` firmware; build IDs captured in the per-serial log
- First DC power-on passed clean: 12 V / 5 V / 3.3 V rails in tolerance, no smoke, no trip, no thermal fuse open
- Both MCP23017s ACK'd at 0x20 + 0x21, DS3231 ACK'd at 0x68, both DS18B20 probes addressed on the 1-wire bus
- All 10 reed switches verified at no-magnet baseline and verified pull-low under a bench magnet
- DIGITEN flow meter pulses on hand rotation; KRAUS air switch debounces on hand press
- MQ-6 warmed to operating temperature and reads clean-air baseline; drip-pan moisture sensor reads dry
- All 12 solenoid valves clicked individually under firmware self-test; both peristaltic pumps spun dry under L298N drive; condenser fan spun briefly
- Relay #1 verified switching the compressor's AC leg under firmware override; suction-line probe drops a few degrees within a couple of minutes; relay de-energizes cleanly and the 3-minute guard re-arms
- Factory-default setpoints (2 °C target, ±2 °C hysteresis, −8 °C freeze cutoff, 3-min minimum off-time, low-reed refill threshold) confirmed loaded
- Per-serial commissioning log archived

The unit is now the input to [`acceptance-and-burn-in.md`](acceptance-and-burn-in.md), which adds water + CO2 and runs the first wet thermal cycle.

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Where the per-serial commissioning log lives.** Local file under `/commissioning/<serial>/` on the build host, cloud-uploaded for support recall, both, or some other format. Decision pending — working position is local-only until the support-recall workflow is specified.
2. **Whether the firmware has a dedicated "factory test" mode separate from production mode.** The valve self-test (step 7), the firmware-override compressor cycle (step 8), and the setpoint query (step 9) currently run as ad-hoc serial commands against production firmware. Whether to split these into a separate build target (e.g. `esp32dev_factory`) with a dedicated test menu, gated by a build-time flag, or leave them in production firmware behind a serial command, is undecided. The latter is cheaper but ships factory commands in the customer-facing image; the former needs a second build env in [`/platformio.ini`](../../platformio.ini).
3. **Calibration constants that vary per-unit vs. baked into firmware as constants.** The DIGITEN flow meter's pulses-per-mL and each reed switch's pull-in threshold (effective voltage on INPUT_PULLUP at the moment the magnet engages) are in principle per-build values, but in practice may be tight enough across the parts SKUs to ship a single constant. Whether step 6's sensor walkthrough captures these as per-unit numbers for the commissioning log, or whether they're constants in the firmware and step 6 only verifies they're within a wide envelope, is undecided. Resolve once the first ~3 units' commissioning data is in hand.
