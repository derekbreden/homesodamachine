# Firmware and Commissioning

The production procedure for first-time firmware flash and DC-side commissioning of a fully wired chassis. Takes the never-powered output of [`wiring.md`](/hardware/assembly/wiring.md) — AC and DC continuity checks already passed — through three MCU flashes, a controlled first power-on under PSU, a sensor-health walkthrough, a valve self-test, and a brief firmware-driven compressor cycle confirming relay #1 switches the AC leg. Stops short of any test that requires water or CO2 — those live in [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md).

Customer-side firmware binding (Wi-Fi credentials, cloud pairing, app association, per-customer ratio tuning) is **not** done here. Firmware ships with factory defaults; the iOS/Android app handles binding at first install. This procedure ends with a unit that boots clean, self-tests clean, and is ready to take water + CO2 in the next station.

Design intent and runtime behavior live in [`/hardware/README.md`](/hardware/README.md) "Refrigeration" + "Carbonation". Pin assignments and wiring topology live in [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd). The PlatformIO environment names live at the repo root in [`/platformio.ini`](/platformio.ini).

## Scope

In: a fully wired chassis fresh out of [`wiring.md`](/hardware/assembly/wiring.md) — AC and DC continuity checks passed, never powered. The flash tooling — a USB-C cable (the main board's J14 programming port and both displays present USB-C), PlatformIO on the build host, and the firmware source tree at `/firmware/` configured per [`/platformio.ini`](/platformio.ini). A multimeter for runtime DC-rail spot checks. A serial console (`pio device monitor`) for log capture.

Out:

- All three MCUs — the main board's ESP32-WROOM, the 4.3" enclosure display, the 1.47" faucet display — flashed with the current firmware on `main`.
- First DC power-on under PSU control succeeds with no smoke, no breaker trip, no thermal-fuse open.
- Sensor health passes: both 1-wire probes addressed on the bus — one DS18B20 (carbonator, family 0x28) + one DS18S20 (coil, family 0x10) — and reporting within [±2 °C](AMBIENT_TOL) of room ambient; all [10](REEDS_TOTAL) reed switches ([2](REEDS_CARB) carbonator + [4](REEDS_PER_RSVR) per flavor reservoir × [2](RSVR_COUNT) reservoirs) settled to their no-magnet "empty" baseline; the DIGITEN flow meter ticks pulses when its impeller is rotated by hand; the MQ-6 hydrocarbon sensor in the refrigeration bay's -X wall slot has reached operating temperature and reads its clean-air baseline; the ASSE drip pan's moisture sensor reads dry.
- Both MCP23017 GPIO expanders ACK on the I²C bus at [0x20](MCP_VALVES) and [0x21](MCP_RESERVOIRS), with the DS3231 RTC at [0x68](RTC_ADDR) also responsive.
- Valve self-test pass: each of the [11](VALVE_COUNT) Beduan solenoids clicks once with audible / visual confirmation, and both Kamoer peristaltic pumps spin briefly under DRV8870 drive.
- Relay #1 verified switching the compressor's AC leg under a deliberate firmware override: the suction-line probe (the DS18S20, family 0x10) reads a few degrees lower within a couple of minutes of the override starting (running dry, no water in the carbonator), confirming the relay is making AND that the DS18S20 is physically mounted on the suction line (its identity among the two probes is already fixed by family code, not by this test).
- Firmware setpoints loaded with factory defaults: **carbonator target [2 °C](TANK_TARGET), hysteresis [±2 °C](HYSTERESIS)** (compressor off at [2 °C](COMP_OFF_TEMP), on at [4 °C](COMP_ON_TEMP)), **freeze-protect cutoff [−8 °C](FREEZE_CUTOFF)** on the suction-line probe, **[3-minute](MIN_OFF_TIME) minimum off-time** for the compressor start capacitor, refill threshold on the carbonator's low-level reed.
- Per-serial commissioning log archived (sensor readings, I²C ACK list, valve click confirmation, compressor-cycle suction-line ΔT).

Not in scope: any acceptance test that requires water or CO2 (that's [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md)); customer-side firmware binding via the iOS/Android app at install (post-shipping); the over-the-air firmware-update flow (not in scope for first-unit shipping).

## Inputs per appliance

| Item | Source / spec | Notes |
|---|---|---|
| Wired chassis | Output of [`wiring.md`](/hardware/assembly/wiring.md) | Never powered. AC + DC continuity checks passed. Compressor bolted down and grounded; donor terminal cover intact, unmodified, and securely retained; factory lead exit undamaged. |
| Firmware source tree | [`/firmware/`](/firmware/) on the build host, current `main` | PlatformIO project; envs `appliance`, `esp32s3_front`, `esp32s3_faucet` (see [`/platformio.ini`](/platformio.ini) and [`/firmware/README.md`](/firmware/README.md)). The `appliance` tree is an Open item below. |
| PlatformIO | On the build host | `pio run -e <env> -t upload` builds and flashes. One board on USB at a time, or name the port — PlatformIO picks the S3 otherwise and esptool leaves that panel dark. |
| USB-C cable | Fits the main board's J14, the 4.3B, and the 1.47" faucet display | Build-bench stock; not per-unit consumable. |
| Multimeter | Build-bench stock | DC-rail spot checks at [12 V](RAIL_12V) (J10 clamps), [5 V](RAIL_5V) + [3.3 V](RAIL_33V) (connector pins). |
| Serial monitor | `pio device monitor -e appliance` (115200 baud) | Captures the ESP32 boot log + structured commissioning output for the per-serial archive. |
| Commissioning-log template | TBD — see Open items | Per-unit serial + sensor readings + I²C ACK list + valve confirmation + suction-line ΔT during the relay #1 verification. |

Tooling (per-unit-amortized): one build-bench station with a PSU-controlled outlet feeding the C14 input, a current meter inline with the PSU output for the 12 V rail, and a USB hub on the bench host.

## Procedure

### 1. Verify wiring-out inputs

Before any power, walk the chassis once against [`wiring.md`](/hardware/assembly/wiring.md) output condition: compressor bolted down and grounded; donor moulded cover intact, unmodified, and securely retained over the terminal/PTC assembly; factory lead exit undamaged; power column populated and fastened; ground bus continuous from C14 earth pin to every exposed-metal bond point; all JST XH looms seated on their labeled wafers (J4 vs J7 by loom label per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)); the J10 polarity verified (`V12` east / `GND` west).

This is a *re-look*, not a re-test — the AC and DC continuity sign-offs from `wiring.md` are not repeated here. If anything in the power column has moved since `wiring.md` signed off, return the unit there before continuing.

### 2. First DC power-on under PSU control

Power the C14 inlet through a bench PSU-controlled outlet, not direct wall power. The Teyleten relay #1 must remain de-energized for this step — the firmware boots into "all off" by default, but the PSU-controlled outlet is the hardware backstop.

When mains reaches the C14 inlet, AC propagates directly through the distribution block to the PSU primary — the AC path is C14 inlet → AC distribution block → PSU, with no device in series (ground-fault protection is deferred, see [/future/pie-in-the-sky/gfci.md](/future/pie-in-the-sky/gfci.md)). If no DC rails come up in the next sub-step, check AC-1 wiring back to the C14 inlet and the distribution-block landings.

Bring up in this order, verifying each rail with the multimeter before the next:

1. PSU output enabled — verify **[12 V](RAIL_12V)** at the distribution-block test point (PSU is the Mean Well IRM-90-12ST, see [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) run DC-1). Expected ~[12 V](RAIL_12V) [± 0.2 V](RAIL_12V_TOL) at no load.
2. **[5 V](RAIL_5V) rail** at a `V5` connector pin (J4 or J5) — expected [5 V](RAIL_5V) [± 0.1 V](RAIL_5V_TOL). The rail is the main board's K7805 buck (U10) off the J10 12 V inlet; it feeds the 3.3 V LDO, the relay-module VCC (via J5), the flow meter, and the MQ-6 heater. Power tree: [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd).
3. **[3.3 V](RAIL_33V) rail** at a `3V3` connector pin (J4 or J8) — expected [3.3 V](RAIL_33V) [± 0.05 V](RAIL_33V_TOL). The rail is the main board's AMS1117 LDO (U9) off the 5 V buck; it feeds the WROOM, both MCP23017s, the DS3231, the RS485 transceiver, and the on-board pull-ups.

Under *full* logic load — all MCUs flashed and both display backlights on (revisit after step 6) — the 5 V rail holds tolerance.

If any rail is out of tolerance, kill the PSU and return the unit to `wiring.md`. Do **not** energize the AC side (compressor + fan) at this step — relay #1 stays de-energized until step 8.

Spot-check current draw at the PSU: cold idle sits low — the WROOM's boot-ROM idle, the main board's rail LEDs, and the relay-module opto quiescent draw tens of mA; the relay coils are de-energized, no valves are driven, no pumps.

### 3. Flash the base ESP32 (main board)

Plug the USB-C cable into the main board's J14, flush on the west edge of the main board. The on-board CH340C (U13) enumerates as a USB CDC port on the build host, with auto-reset driving EN/IO0 into download mode.

From the repo root:

```
pio run -e appliance -t upload
```

Per [`/platformio.ini`](/platformio.ini). Expected outcome: build succeeds, upload reaches 100 %, ESP32 resets, the serial monitor at 115200 baud shows the firmware boot banner with the `fw_version.h` build ID.

`src_appliance/` boots to that banner, parks every actuator dark and turns one flavor pump — the rest of this procedure is written against firmware that fills it in, and that is the Open item below.

### 4. Flash the ESP32-S3 enclosure display

Plug the USB-C cable into the ESP32-S3-Touch-LCD-4.3B (the enclosure display, let into the 45° facet chamfered across `enclosure-front-top`'s top-front arris per [`/hardware/printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md); its SIG-7 RS485 link to the main board's J9 lands at [`wiring.md`](/hardware/assembly/wiring.md)). It enumerates as a native USB-CDC device — the build flag `ARDUINO_USB_CDC_ON_BOOT=1` in `[env:esp32s3_front]` brings the CDC port up immediately on boot.

```
pio run -e esp32s3_front -t upload
```

Confirm the LVGL splash renders on the 800×480 panel after reset.

### 5. Flash the ESP32-S3 faucet display

Plug the USB-C cable into the 1.47" faucet display at the end of the gooseneck. Same native USB-CDC boot as the 4.3B.

```
pio run -e esp32s3_faucet -t upload
```

Confirm the flavor UI renders after reset. The touch-toggle check lands in step 6, once the base ESP32 is broadcasting flavor frames over the SIG-6 UART.

### 6. Sensor health walkthrough

With both MCUs running their default firmware, open the serial monitor on the ESP32:

```
pio device monitor -e appliance
```

The default firmware periodically prints a sensor-health frame. Step through each line:

- **I²C scan** — expect ACKs at [0x20](MCP_VALVES) (MCP23017: 8 valves + Reservoir A reeds), [0x21](MCP_RESERVOIRS) (MCP23017: 3 valves + condenser-fan driver bit + Reservoir B reeds + carbonator reeds), and [0x68](RTC_ADDR) (DS3231 RTC). All three are on the main board, so a missing ACK is a main-board fault.
- **1-wire temperature bus** — expect exactly two devices on the bus on [GPIO 26](GPIO_ONEWIRE): one DS18B20 (family `0x28`, carbonator-wall) and one DS18S20 (family `0x10`, suction-line). Firmware routes each reading by family code, so the `0x28`/`0x10` split is itself the pass criterion — two same-family devices, or a missing family, is a wrong-part or mounting error. Both should report within [±2 °C](AMBIENT_TOL) of room ambient with the compressor de-energized. If only one address enumerates, suspect a parasitic-power miswire in the J4 loom (the [4.7 kΩ](ONEWIRE_PULLUP) pull-up R9 is on the main board).
- **Carbonator reeds** (MCP23017 [0x21 PB4](REED_LOW) low, [0x21 PB5](REED_HIGH) high) — both on the MCP internal pull-up, both reading high (no magnet present, no float installed yet). Bring a small bench magnet near each reed in turn and confirm it pulls low.
- **Reservoir reeds** — all 8 (Reservoir A on MCP23017 [0x20](MCP_VALVES) PB[0:3], Reservoir B on [0x21](MCP_RESERVOIRS) PB[0:3]) reading their no-magnet baseline. Architecture and calibration in [`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md). Same bench-magnet check per reed.
- **DIGITEN flow meter** ([GPIO 25](GPIO_FLOW)) — manually rotate the impeller with a clean implement; expect a pulse count increment per rotation in the serial output.
- **Faucet display toggle** — touch the 1.47" faucet display; the selected flavor switches and the base ESP32 logs the change over the SIG-6 UART.
- **MQ-6 hydrocarbon sensor** — needs ~60 s warm-up to reach operating temperature. After warm-up, expect a clean-air baseline reading on its analog input (verify the bench air is free of solvents or LPG nearby — wave clean air across the sensor or move the chassis briefly to a clean-air environment if needed). Architecture: the MQ-6 stands on edge low in the refrigeration bay, in the open floor strip down the -X wall beside the compressor, mesh horizontal and looking aft along that strip (the bare sensor's orientation is unconstrained per the Winsen datasheet; what the position is for is height -- the bay's floor is one connected pool that every dominant brazed-joint leak site drains into, and dense R-600a spreads over the slab as one layer) — the hardware-only backstop to the firmware-controlled cutoffs ([`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) "Safety").
- **ASSE drip pan's moisture sensor** — reads dry (high impedance). Confirm by briefly bridging the sensor pads with a damp probe and watching the firmware reading swing.

Record each reading in the per-serial commissioning log. Any out-of-bounds reading at this step blocks the unit from proceeding to step 7.

### 7. Valve and peristaltic-pump self-test

The firmware exposes a self-test command over the serial console that walks each of the [11](VALVE_COUNT) Beduan solenoids individually and then spins each peristaltic pump briefly. Trigger it from the monitor prompt.

- **Solenoid sequence** — the firmware drives each valve output in turn: [0x20](MCP_VALVES) PA through TBD62083 U4 (V-A through V-H), [0x21](MCP_RESERVOIRS) PA[6:7] through U5 (V-I, V-J), and [0x21](MCP_RESERVOIRS) PA5 through U5 channel 3 to `J2.OUT3` (V-K); see [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd). Each coil energizes for ~250 ms then releases. Expected: [11](VALVE_COUNT) distinct clicks. Listen for stuck-on coils (no audible release click). Ten clicks come from the manifold pack; V-K's comes from its cradle on the cold core's crown, at the far end of the DC-9 run.
- **Condenser fan** — driven by MCP23017 [0x21](MCP_RESERVOIRS) PA3 through TBD62083 U5 channel 5. The self-test gives the fan a brief 1-second run. Expected: audible spin-up of the [12 V](RAIL_12V) DC brushless axial mounted to the enclosure side wall, then coast-down.
- **Peristaltic pumps** — driven by the on-board DRV8870 H-bridges (U11/U12) through J13. The self-test spins Pump A forward for ~1 s, then Pump B. Expected: each silicone tube head rotates visibly. No flavor is loaded yet; the head turns dry.

Any failure here is loom wiring, a device fault, or a board fault. Resolve and re-run before continuing.

### 8. Relay #1 compressor-cycle smoke test

This is the only step that energizes the AC side. The carbonator is **empty** (no water, no CO2) — the run is brief and intentional, just enough to confirm the AC leg switches and the suction line cools.

Trigger the firmware-override compressor-on command at the serial console. The firmware drops the [3-minute](MIN_OFF_TIME) minimum-off-time guard for this command only and asserts [GPIO 19](GPIO_RELAY1); the on-board gas→compressor interlock (U15) passes it to J5 only while the MQ-6 reads clear — a missing or cold gas sensor holds relay #1 open (step 6's warm-up is a prerequisite). The relay energizes and closes the AC leg through the SF76E into the verified hot side of the compressor assembly's factory-external electrical interface; the terminal/PTC assembly remains under the donor cover.

Watch for, in order:

1. **PSU current bump** at the inline meter — the relay coil pulls ~70 mA additional through the 5 V rail; small but visible.
2. **Compressor audible start** — the PTC start relay clicks and the hermetic compressor's motor spins up. The clip-on overload should not trip on a healthy compressor; if the overload opens, kill the override immediately and return to [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) for diagnosis.
3. **Current draw at the AC side** — within nameplate (a couple of amps RMS on the 120 VAC leg for the harvested ice-maker compressor). Verify with a clamp meter on the switched-hot run AC-4 if the build bench has one.
4. **Suction-line probe (DS18S20) temperature** — drops a few degrees within a couple of minutes. The cold core has no water to absorb heat, so the suction line cools faster than it will in normal operation; this is the intended diagnostic, not normal-operation behavior.

After 30–60 seconds, send the firmware-override compressor-off command. The compressor de-energizes, the suction-line probe begins warming back toward ambient, and the [3-minute](MIN_OFF_TIME) minimum off-time guard re-arms.

This is **not** a refrigeration commissioning step. Full thermal cycling under water load happens at [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md). All this step proves is: (a) relay #1 makes the AC leg, (b) the compressor draws nameplate current, (c) the suction-line probe is on the right probe.

### 9. Verify setpoints loaded

Query the firmware over serial for its loaded setpoints. Expected:

- Carbonator target: **[2 °C](TANK_TARGET)**
- Hysteresis: **[±2 °C](HYSTERESIS)** (compressor on at [4 °C](COMP_ON_TEMP), off at [2 °C](COMP_OFF_TEMP))
- Freeze-protect cutoff: **[−8 °C](FREEZE_CUTOFF)** on the suction-line probe
- Compressor minimum off-time: **[3 min](MIN_OFF_TIME_BARE)**
- Carbonator refill threshold: low-level reed (MCP23017 [0x21 PB4](REED_LOW))
- Backflow alarm: armed on the ASSE drip pan's moisture sensor
- Sound volume: **70%**, quiet hours **off** (`volume` / `quiet` on the main board's console)

These are baked into the firmware on `main` as factory defaults; no per-unit setting is required here. Customer-side tuning (ratio adjust, Wi-Fi binding, cloud pairing) happens through the iOS/Android app post-install.

Then query the three limits the hardware imposes. Each one is a part's rating, and the firmware is the only thing holding the machine inside it:

- Valves energized at once: **at most [3](MAX_VALVES)**. Eight coils on MANIFOLD A cross J1's `COM` contact rating and land in one TBD62083 — [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Solenoid COM current budget".
- Refill gated on the dispense window: **relay #2 ([GPIO 2](GPIO_RELAY2)) de-energized while a dispense is open**. The main board peaks at [3.33 A](BOARD_PEAK_A) and the SeaFlo at [5 A](DIAPHRAGM_A) on one [6.7 A](PSU_MAX_A) supply — [8.32 A](COINCIDENT_A) if they overlap. The low reed asserts mid-pour, so the refill it queues waits ([`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) step 5).
- Reed pull-ups: **`GPPU` written on both MCP23017s**. No loom carries a resistor and the main board pulls none of these inputs ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx)), so a reed with no pull-up floats and step 6's baselines are meaningless.

A unit that walks step 7 and passes step 6 can still be failing all three — nothing here reads them off behavior. The query is the check, and step 7's own walk goes through the state machine holding them (Open item 3).

Then confirm the one safety property that lives entirely in firmware and has no hardware behind it: **the gas alarm cannot be silenced.** Volume, mute and quiet hours reach every sound the machine makes except that one, and a unit that let a customer mute a refrigerant-leak alarm would ship a defect nothing downstream would catch. Set the clock first, since quiet hours will not engage without one:

```
rtc set <YYYY-MM-DD> <HH:MM:SS>
volume 0
sound tick
sound alarm
sound stop
volume 70
```

**Pass:** `sound tick` reports `silenced, so nothing will be heard` and the main board stays silent; `sound alarm` reports `alarm at 100%` and the transducer sounds at full volume. **Fail:** either the tick is audible at volume 0, or the alarm is not — do not ship the unit; the exemption is `SND_F_UNSILENCEABLE` in [`/firmware/lib/sound/sound.h`](/firmware/lib/sound/sound.h).

`sound list` prints what every sound would play at right now, which is the fastest read on whether volume and quiet hours are where this step expects them. U15 holds the compressor off the same MQ-6 signal in hardware with no firmware in the path — that interlock is step 8's, and it is a different check from this one.

### 10. Archive the per-serial commissioning log

Snapshot the serial-monitor output from steps 6–9 into a per-serial log file. At minimum capture: firmware build ID (`fw_version.h`), I²C ACK list, 1-wire probe addresses + family codes (0x28 carbonator / 0x10 coil) + first-read temperatures, all [10](REEDS_TOTAL) reed baselines, flow-meter pulse count, MQ-6 baseline, drip-pan baseline, valve self-test pass/fail per channel, suction-line probe temperatures before/during/after the relay #1 verification, the DS3231 time as set, and the volume-0 alarm check from step 9.

Where this log lives — local file under `/commissioning/<serial>/`, uploaded to cloud, both — is an Open item below. Working position: keep the file locally on the build host until that decision lands.

## Output condition

A commissioned unit is:

- Both MCUs flashed with current `main` firmware; build IDs captured in the per-serial log
- First DC power-on passed clean: [12 V](RAIL_12V) / [5 V](RAIL_5V) / [3.3 V](RAIL_33V) rails in tolerance, no smoke, no trip, no thermal fuse open
- Both MCP23017s ACK'd at [0x20](MCP_VALVES) + [0x21](MCP_RESERVOIRS), DS3231 ACK'd at [0x68](RTC_ADDR), both temperature probes addressed on the 1-wire bus (DS18B20 0x28 + DS18S20 0x10)
- All [10](REEDS_TOTAL) reed switches verified at no-magnet baseline and verified pull-low under a bench magnet
- DIGITEN flow meter pulses on hand rotation; the faucet display's touch toggle switches the selected flavor
- MQ-6 warmed to operating temperature and reads clean-air baseline; the ASSE drip pan's moisture sensor reads dry
- All [11](VALVE_COUNT) solenoid valves clicked individually under firmware self-test; both peristaltic pumps spun dry under DRV8870 drive; condenser fan spun briefly
- Relay #1 verified switching the compressor's AC leg under firmware override; suction-line probe drops a few degrees within a couple of minutes; relay de-energizes cleanly and the [3-minute](MIN_OFF_TIME) guard re-arms
- Factory-default setpoints ([2 °C](TANK_TARGET) target, [±2 °C](HYSTERESIS) hysteresis, [−8 °C](FREEZE_CUTOFF) freeze cutoff, [3-min](MIN_OFF_TIME_HYPHEN) minimum off-time, low-reed refill threshold) confirmed loaded
- The three hardware limits confirmed held: [3](MAX_VALVES)-valve ceiling, refill gated on the dispense window, `GPPU` written on both expanders
- Per-serial commissioning log archived

The unit is now the input to [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md), which adds water + CO2 and runs the first wet thermal cycle.

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **`src_appliance/` runs one flavor pump and nothing else.** It boots to step 3's banner and idle state, brings up J9, and turns a pump — held from the enclosure display's glass, or bounded from its own console ([`/firmware/src_appliance/README.md`](/firmware/src_appliance/README.md)). Steps 6, 7 and 9 are the specification the rest gets written against, and every figure in them is settled. Until it walks the valves, reads the reeds and answers the setpoint query, a unit reaching those steps gets `pio run -e pcba_bench -t upload` and a console session against [`/firmware/src_pcba_bench/README.md`](/firmware/src_pcba_bench/README.md)'s command table — on a bare board, before the manifold is plugged in.
2. **Where the per-serial commissioning log lives.** Local file under `/commissioning/<serial>/` on the build host, cloud-uploaded for support recall, both, or some other format. Decision pending — working position is local-only until the support-recall workflow is specified.
3. **What the step-7 and step-9 commands are allowed to touch.** They run as serial commands against the one shipping image — there is no separate factory build. A command here asks the state machine to do a thing (`selftest valves` walks the census; `selftest pumps` turns both heads) and never writes a pin, because a command that writes a pin is outside the [3](MAX_VALVES)-valve ceiling and the refill interlock by construction, and step 9 is where those are confirmed held. `src_pcba_bench` is the surface that does write pins, and it runs on a bare board with the manifold unplugged.
4. **Calibration constants that vary per-unit vs. baked into firmware as constants.** The DIGITEN flow meter's pulses-per-mL and each reed switch's pull-in threshold (effective voltage on INPUT_PULLUP at the moment the magnet engages) are in principle per-build values, but in practice may be tight enough across the parts SKUs to ship a single constant. Whether step 6's sensor walkthrough captures these as per-unit numbers for the commissioning log, or whether they're constants in the firmware and step 6 only verifies they're within a wide envelope, is undecided. Resolve once the first ~3 units' commissioning data is in hand.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_firmware_and_commissioning_sync.py`
