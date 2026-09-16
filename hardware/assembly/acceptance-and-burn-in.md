# Acceptance and Burn-In

The production procedure for the bench acceptance test and multi-hour burn-in on a finished, commissioned appliance — the last sign-off step before the unit moves to [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md), and the bench that empties it for transit. Inputs are a chassis that has come out of [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) with sensors healthy and setpoints loaded; outputs are a per-serial test log and a unit cleared to ship.

This is the first service fill after the water-filled hydro-test, draining and passivation in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md). The carbonator is integrated dry through [`cold-core.md`](/hardware/assembly/cold-core.md) and [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md). Its [water-inlet jet](/hardware/assembly/water-inlet-jet.md) must have a completed fit and full-root-fusion qualification record. The bench rig represents the customer water and CO2 connections; temporary measurement instruments record the actual operating conditions.

**Firmware prerequisite:** the actuator, interlock and acceptance controls described below must be implemented and commissioned before this is a production acceptance run. [`src_appliance/main.cpp`](/firmware/src_appliance/main.cpp) currently documents the dispense-then-refill policy but does not yet drive either relay. References here to a fill command, automatic refill, burn-in timer and log download describe required acceptance behavior, not available controls. Record first-unit bench measurements separately when those controls are absent; a manual test does not sign off unimplemented automatic behavior. This procedure does not authorize a firmware or power-policy change.

## Scope

In: a chassis fresh out of [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) — powered, firmware flashed, all sensors healthy on first read (both temperature probes (DS18B20 carbonator + DS18S20 coil), both reed pairs on each flavor reservoir, both reeds on the carbonator, the DIGITEN flow sensor, the MQ-6, the ASSE drip pan's moisture sensor), all [11](VALVE_COUNT) solenoid valves cycled through their firmware self-test, compressor + condenser fan firmware-gated together, setpoints loaded (carbonator wall [2 °C](WALL_SETPOINT) [± 2 °C](WALL_BAND), evap-coil freeze cutout [−8 °C](FREEZE_CUTOUT), compressor min-off [3 min](MIN_OFF)); a bench test rig consisting of a test-rig water source feeding the +Y wall's PP1208E 1/4" JG QC inlet, a test-rig CO2 supply feeding the ABU44 bulkhead at a recorded primary setting, including a qualification run at the nominal [90 PSI](CO2_CENTERLINE) gas-feed ceiling, a [12 oz](GLASS_OZ) target glass, a graduated cylinder ([250 mL](CYL_MIN) or larger), a thermocouple gun or food thermometer ([0–20 °C](THERMO_RANGE) range), a stopwatch, and a refractometer if available for ratio check; two SodaStream concentrate bottles (Diet Mountain Dew + one other) primed in the flavor reservoirs via the funnel before the test sequence begins.

Out: a unit that has passed every step of the functional acceptance test below (first water fill of the carbonator without leak; CO2 and carbonator pressures measured through refill and hold, PRV does not weep, ASSE drip pan stays dry; refill completes and restarts; first and successive carbonated-water dispenses ~[12 oz](GLASS_OZ) at ≤ [~6 °C](DISP_TEMP_MAX) with the agreed strong-carbonation result; first flavor A and flavor B dispenses at the target ratio with measured pump output; clean cycle through both channels; air-purge cycle; all level-sensing transitions observed correctly) and a multi-hour burn-in (with periodic dispenses on a timer, watching compressor cycle count, watching for nuisance freeze-protect trips, watching for leaks, watching for MQ-6 trips). Per-serial test log archived.

Not in scope: cosmetic inspection, nameplate verification, packaging — all in [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md). Customer-side install commissioning (running the unit on the customer's tap-water + CO2 bottle for the first time in their kitchen) is a separate procedure, not part of factory acceptance.

## Inputs per appliance

Per-unit BOM is the entire BOM of record at this step — by acceptance the unit is fully built. The table below is the bench-rig and per-test consumable summary, not appliance parts; appliance BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md).

| Item | Source / spec | Notes |
|---|---|---|
| Test-rig water source | Bench cold-water tap, regulated [40–80 PSI](WATER_PRESS_RANGE), terminated in 1/4" LLDPE pushed into the appliance's PP1208E 1/4" JG QC inlet on the +Y wall of back-top | Stands in for the customer's under-sink supply line. Cold (≤ [~20 °C](WATER_TEMP_MAX)) so the carbonator's first chill-down matches real-world conditions. |
| Test-rig CO2 source | [5 lb](CO2_CYL_SMALL) or [10 lb](CO2_CYL_LARGE) CO2 cylinder + CGA-320 primary regulator set to [70–100 PSI](CO2_PRIMARY_RANGE) + PM4508F4S flare connector, PI061008S stem reducer and red 1/4" LLDPE into the ABU44 bulkhead on the +Y wall | Stands in for the customer's CO2 bottle; the CGA-320 primary regulator ships with the appliance. The WR1110 limits incoming gas to nominally [90 PSI](CO2_CENTERLINE); below that ceiling the primary sets the gas-feed pressure. Water refill can raise carbonator pressure above the gas setting. Record the primary, gas-feed and actual carbonator pressures separately. |
| Target glass | [12 oz](GLASS_OZ) drinking glass, clear, room-temperature | Receives every dispense in the acceptance sequence. Use the same clean glass and temperature for carbonation comparisons; foam duration alone is not a carbonation measurement. |
| Graduated cylinder | [250 mL](CYL_MIN) or larger, food-grade plastic or borosilicate glass | Measures dispense volume by pour-into-cylinder for the metered dispenses. Replaces the target glass on metered steps. |
| Thermocouple gun or food thermometer | [0–20 °C](THERMO_RANGE) range, [±0.5 °C](THERMO_ACC) or better | Measures dispensed-water temperature at the gooseneck and inside the target glass. Probe-style is preferred over IR for liquid temperature; IR reads surface only. |
| Stopwatch | Phone stopwatch is fine | Times the dispense window for the metered-flow steps. |
| Refractometer (optional) | [0–32 °Brix](BRIX_RANGE) handheld, ATC-equipped | If available, measures sucralose-equivalent °Brix on the dispensed mix to back-check the [1:20](RATIO) ratio. SodaStream concentrate is sucralose-based, not sugar-based, so the Brix reading is a sweetener proxy not a literal sugar concentration — useful as a relative check between channels, not as an absolute. |
| SodaStream concentrate, Diet Mountain Dew | [0.44 L](BOTTLE_L) bottle | Channel A test syrup. Whether factory-supplied or customer-supplied is an Open item below. |
| SodaStream concentrate, second flavor | [0.44 L](BOTTLE_L) bottle | Channel B test syrup. Same open item. |
| Temporary pressure and electrical measurement fixture | Rated gauges or transducers at pump inlet, pump discharge and carbonator-side line; DC voltmeter and current measurement | Record instrument locations, range and accuracy. Use existing line connections and leave the dedicated PRV connected and unobstructed. Instrument availability and fixture fit must be established before the hydraulic qualification. |
| Per-serial test log file | Placeholder `logs/<serial>/acceptance.json` | Every metered value captured at the appliance and saved to a serial-keyed file. Format + final path is an Open item below. |

Tooling (bench, shared across all units — not per-build consumed): the test-rig water + CO2 connections themselves, the [12 oz](GLASS_OZ) glass, the graduated cylinder, the thermocouple, the stopwatch, and the optional refractometer. The pressure fixture above is not yet a built rig: one SENCTRL gauge is owned, and additional gauges or transducers may be needed to capture the three pressure locations together. Two SodaStream concentrate bottles are consumed per unit in small dispense volumes ([~50 mL](CONC_ML) of concentrate across the full test sequence, [~11 %](CONC_PCT) of one bottle); whether they are factory-supplied or customer-supplied is an Open item.

## Procedure

### 1. Pre-test inspection + connect bench rig

Verify the chassis came out of [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) with all checkboxes signed off. The unit is sitting on the bench, AC cord unplugged, all +Y wall's connections capped or plugged. Visually inspect the exterior — no displaced fittings, no shipping-damage cracks in the printed enclosure, the compressor's four floor screws are home, its ground ring is under its own earth screw, and the donor moulded cover is intact, unmodified, and securely retained over the terminal/PTC assembly with its factory lead exit undamaged; the C14 inlet recess is clean; the umbilical bulkheads on the +Y wall are seated. Both integral carrier tabs must be sound, their faces even, and the center lap held firmly by its two screws. Both pump brackets bear in the lower cradle behind the cartridge face, the top clamp is screwed down and their DC-5 spade pairs are on the motor tabs, landed at [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3. Behind the display, the pump plug is clicked home in the pump jack; the fixed J13-side 4P ribbon lies flat in the ridge wall's +X cable clip and the cartridge's cord does not pass through that clip.

Cycle the pump connection dry before attaching either bench supply. Brace the enclosure and pull the cartridge straight forward. The four tied tees must follow it through the 2.15 mm stroke from the aft stop to the fore stop. The plate takes up the 0.5 mm nose gap and depresses the sleeves through their measured 1.65 mm stroke. It then holds all four sleeves continuously while the tubes withdraw. The two springs return the empty carrier evenly to the aft stop. Watch the four bowed tee-to-valve stubs and four tee-side hairpin ends throughout: none may kink, scrape, go taut or pull a fixed valve from its tray. Draw the cartridge fully, reach up through the empty bay behind the display, press the pump plug's downward-facing clip, pull the plug straight forward until it is clear of the plate cap, and lower it through the bay without pulling either ribbon. Verify the fixed half stays snapped into its panel and the +X clip keeps the J13 half against the ridge wall. Raise the cartridge receptacle back into line and push it home until it clicks, then tug the housing to prove the latch. With each hand spanning a cartridge pocket and the carrier tab on the same side, squeeze the cartridge aft and carrier fore until the four tubes reach their measured 10 mm bottoms at the fore stop; verify the cartridge is still 2.15 mm short of seating. Relax both hands together, let the carrier return aft and push the cartridge through its final 2.15 mm. Its tubes must reach the aft body stops with fully extended sleeves and 0.5 mm of nose air. The cartridge face should finish flush, but flushness alone is not proof of four connections. Both tabs must reach the aft stop together; gently tug all four connections to prove their grip.

The [physical collet observations](/hardware/reference/tee-connector/README.md#observed-push-connect-action) establish the push-connect action. This dry cycle records the assembled unit’s guided motion, retention, empty return and flexible-link behavior.

Connect the test-rig water source to the +Y wall's PP1208E 1/4" JG QC inlet, pushing the 1/4" LLDPE home into the collet. Route the Multiplex 19-0897 atmospheric vent telltale line to its ASSE drip pan (this run was made during enclosure-mechanical; verify it is still seated over the pan and the moisture sensor is dry). Connect the test-rig CO2 source to the ABU44 bulkhead — same +Y wall as the water and umbilical connections, on the umbilical row's own storey one column east of the blue-ringed union — red 1/4" LLDPE pushed home with the collet fully seated. Open the CO2 cylinder valve at the recorded trial primary setting. Include a separate qualification at the nominal [90 PSI](CO2_CENTERLINE) gas-feed ceiling; do not treat every primary setting as the same test. Record the initial charging, air removal and conditioning sequence so carbonation comparisons use the same CO2 headspace condition. Do not yet open the water-side test-rig valve. Place the [12 oz](GLASS_OZ) target glass on the bench under the faucet position (the faucet itself is on its under-counter mount; the bench can take the chassis with the faucet temporarily oriented over a catch tray or with a stub line into the same target glass — bench-rig detail at operator discretion).

**Pass:** the carrier releases all four tubes, returns empty to park, squeezes without racking, and settles at connected after all four tubes bottom; both integral tabs and the center joint remain sound; the pump plug parts by its clip, the pump jack and cable clip remain seated, and it re-plugs with an audible click; all eight flexible ends move without damage; all bench-rig connections are leak-free at the +Y wall against the now-pressurized CO2 line, water side still off; backflow vent telltale is routed over the dry ASSE drip pan; the pump cartridge face is flush. **Fail:** unequal tab positions, incomplete return, a tube that will not grip after full seating, a cracked tab or loose center joint, a connector or fixed lead that moves instead of unlatching, any damaged flexible link, any audible CO2 hiss at the ABU44 bulkhead or any back-of-rig joint — correct the fault and repeat the dry cycle before continuing.

### 2. Power on + interlock check

Plug the C14 inlet into a bench outlet via the supplied NEMA 5-15P → C13 cord. Firmware boots and the main board sounds `welcome` — a rising four-note chime on U8, which is how a unit coming up is heard from across a line without watching it. Silence here is a finding: either the main board did not reach the end of `setup()`, or U8's chain (IO13 → R5 → Q1) is open, which `buzz` on the bench console separates. The ESP32-S3 rotary display lights up showing the selected flavor and reports sensor health on first read: both temperature probes (DS18B20 carbonator + DS18S20 coil) reporting within [±0.5 °C](THERMO_ACC) of bench ambient, MQ-6 in normal range, ASSE drip pan dry, all reed switches in their expected state for an empty system (carbonator-empty, flavor-reservoirs-full from the funnel pre-prime, faucet closed).

Firmware should NOT dispense, should NOT energize the compressor, and should NOT energize the SeaFlo refill pump until the operator enters bench-acceptance mode and water-fill is explicitly commanded. The on-boot state is idle, sensors live, actuators dark.

**Pass:** the `welcome` chime is heard; display reports all green sensors; no actuator energizes on boot. **Fail:** no sound at boot, any sensor reads out-of-range on first read, or any actuator energizes without command — return to firmware-and-commissioning.

A sound at boot is not an actuator energizing. U8 is a 100 mA coil and IO13 is parked before anything else in `machineBegin()`, so a board that resets mid-alarm comes up silent; what is heard here is the end of `setup()`, after everything that reaches a load is already dark.

### 3. First fill, refill and restart

Retain the SeaFlo SFDP1-013-100-22 pump and Mean Well IRM-90-12ST supply. With the faucet closed, open the bench water valve and run the commissioned fill control through V-K and relay #2 (ESP32 [GPIO 2](GPIO_RELAY2)). Water passes through the backflow preventer, split, V-K, SeaFlo and discharge check, then the `water-in` conduit and top Port 2 elbow. The water-inlet jet at the elbow's final downward passage discharges into the gas headspace. CO2 was admitted in step 1; this is not an atmospheric-pressure fill unless the measured carbonator pressure says so.

Log flowing pressure **at the pump inlet**, pump discharge pressure, carbonator pressure, actual water volume and fill time, pump-terminal voltage, pump current and total supply load. The high-level reed must end the commanded fill. After dispensing enough to request a refill, prove the pump restarts and reaches CHI again with the faucet closed. Record switch cut-out, restart, interruptions and each reed transition. Keep the dispense-then-refill policy; concurrent refill is not part of this baseline.

House pressure contributes to pump inlet pressure and reduces its required pressure rise. It does not add to the nominal 100 psi outlet switch setting. The WR1110 gas-feed setting also does not clamp carbonator pressure during refill: the incoming water compresses headspace while CO2 is absorbed. These effects must appear in the same log, not be inferred from free-flow pump specifications.

**Pass:** initial fill and repeated refill reach CHI, the control stops the pump, restart succeeds, the operating point remains within verified component limits, and every joint and the ASSE vent pan stay dry. First-unit measured fill times establish the production acceptance envelope; no “tens of seconds” limit is qualified yet. **Fail:** cut-out before CHI, failure to restart, sustained cycling or overrun, invalid level transitions, supply sag, or leakage. Use the measurements and [Carbonation Plan B](/future/carbonation-plan-b.md) to identify the cause before changing the pump, jet or supply.

### 4. CO2 pressure, reverse sealing and leak hold

The gas path is ABU44 → WR1110 → GASHER check → plain bottom Port 1. The check is downstream of the regulator to stop reverse water flow reaching it. Gas bubbles through the water when the available forward pressure permits; gas admission stops when that pressure difference disappears. There is no sparge stone and no assumed continuous bubbling.

Record actual gas-feed and carbonator pressure during refill and a [2-minute](PRV_HOLD) hold with the pump stopped. Use a gauge or transducer; silence is not a pressure measurement. Carbonator pressure can change as CO2 dissolves and temperature changes, so pressure decay alone is not proof of a leak. Inspect accessible joints with an appropriate external leak-detection method, keep the PRV vent unobstructed, and confirm the ASSE pan stays dry. Include a reverse-sealing check of the downstream gas check in the rated bench fixture before connecting the regulator to that qualified chain; record pressure differential, duration and evidence of liquid passage.

**Pass:** no detected external leak, no reverse liquid passage past the CO2 check, no PRV weep, and a dry ASSE pan. **Fail:** leakage, reverse flow or a relief event. Stop the run and identify whether pressure came from gas supply, water refill or another fault. The nominal 125 psi PRV setting is not an operating target, and PRV opening by itself does not identify a WR1110 fault. A wet backflow vent requires investigation of the protected water chain.

### 5. First and successive carbonated-water dispenses

Run the commissioned refrigeration control to the carbonator-wall setpoint of [2 °C](WALL_SETPOINT) [± 2 °C](WALL_BAND), retaining the coil freeze cutout and compressor minimum-off protections. Record incoming-water temperature, both probes and the time to the first compressor-off event. Follow [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) for charge and thermal-contact diagnostics. A cold wall reading does not prove the bulk water is equally cold.

With flavor injection disabled through the commissioned controls, dispense approximately [12 oz](GLASS_OZ) into the target glass after a recorded idle period. Measure liquid temperature immediately with an immersed probe. Record pour duration, delivered volume, gas setting and any sputter. Compare the carbonation against the agreed strongly carbonated reference at matched temperature and pour conditions; the existing external-carbonator setup can provide that reference. Record dissolved CO2 if suitable measuring equipment is available. Bubble appearance and a ten-second foam head are not standalone pass criteria.

Then run **three successive [12 oz](GLASS_OZ) pours** at the intended home-use cadence, recording the interval between them, every refill start/stop, immediate in-glass temperatures and carbonation judgments. Record any time the machine needs before the next complete pour. Do not insert an unrecorded full chill-down between glasses. Measure recovery to the same initial condition after the sequence. Keep the current level positions, SeaFlo, IRM-90 and dispense-then-refill sequence for this qualification.

**Pass:** the first and successive glasses deliver the agreed strong carbonation, each at ≤ [~6 °C](DISP_TEMP_MAX), with complete pours and repeatable refill/restart at the recorded cadence. That cadence, refill time, recovery time and carbonation reference become the first-unit performance record and the basis for production limits. **Fail:** a weak first glass, falling carbonation despite cold water, warming successive glasses, incomplete pours or refill failure. A sputter is a symptom to diagnose, not a unique indication of inadequate carbonation. [Carbonation Plan B](/future/carbonation-plan-b.md) separates pressure/flow, gas transfer, supply-current and thermal shortfalls.

### 6. First flavor A dispense + flavor pump metering

Re-fill the carbonator (step 3 cycle repeats automatically since the low-level reed is asserted; let it run through). Place the graduated cylinder under the faucet. Set the bench-acceptance UI to "Channel A, metered ratio test" — firmware will run a fixed-duration carbonated water dispense alongside a peristaltic-pump A pulse train sized to the documented [1:20](RATIO) ratio.

Run the metered dispense (target [~250 mL](METERED_WATER) water + [~12.5 mL](METERED_FLAVOR) flavor A concentrate, totalling [~262.5 mL](METERED_TOTAL)). The graduated cylinder receives the mixed product; the carbonator low-reed will likely assert mid-pour and queue a refill which firmware will defer until the dispense window closes.

Measure: total volume in the graduated cylinder, and (if refractometer available) °Brix of the mixed dispense. Compute actual ratio against the [1:20](RATIO) target. Tasting is allowed but not the pass criterion; the volume and the refractometer reading are.

**Pass:** total dispense volume within [~5 %](RATIO_TOL) of [~262.5 mL](METERED_TOTAL) (i.e., [~249–276 mL](METERED_RANGE)); refractometer reading consistent with a [1:20](RATIO) dilution of the SodaStream concentrate (no absolute number locked here — see Open items for the ratio-tolerance gap); pump A audibly running during the dispense window, no missed steps, no pump slip. **Fail:** volume far outside the [±5 %](RATIO_TOL_SIGNED) band (suggests pump A under- or over-delivery, indicating a tube-fatigue problem in the peristaltic head); refractometer reading suggests a far-off ratio; any pump audible stall.

### 7. First flavor B dispense + flavor pump metering

Repeat step 6 with Channel B selected. Same metered dispense, same measurements, same pass criteria. The two channels are mechanically identical; cross-comparing the channel-A and channel-B numbers (volume, refractometer if used) checks the pump-to-pump consistency.

**Pass:** same as step 6, plus channel A and channel B agree to within [~10 %](CHANNEL_TOL) on the refractometer reading (if used) — both channels are running the same target ratio against the same carbonated water source. **Fail:** any single-channel failure as in step 6; or both channels passing the absolute criterion but disagreeing by > [10 %](CHANNEL_TOL_FAIL) between channels (suggests one pump has drifted; both will need recalibration before ship).

### 8. Clean cycle through both channels

From the bench-acceptance UI, run "clean cycle, Channel A." Firmware executes the topology-table sequence (per [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) "Clean Water Fill → Bag A" followed by "Clean Flush A (water out)"): tap-water source fills the flavor reservoir A through the manifold, then the same path that dispenses syrup is run to flush it out the gooseneck into the target glass. The target glass receives faintly-tinted rinse water.

Repeat with "clean cycle, Channel B."

**Pass:** the clean cycle completes without operator intervention; rinse-water emerging at the gooseneck is faintly tinted on the first pass and runs clear on a follow-up pass if commanded; no leak anywhere in the manifold during the clean cycle; firmware reports both cycles complete and ready. **Fail:** any solenoid valve fails to open or close as expected (firmware will normally flag this on the enclosure display); rinse never runs clear (suggests a reservoir-internal cleanability problem, escalate); any leak observed.

### 9. Air-purge cycle through both channels

From the bench-acceptance UI, run "air purge, Channel A." Firmware executes the topology-table "Air Purge In → Bag A" + "Air Purge Out A" sequence: with the funnel dry and open to air, pump A pulls air through V-B → V-C → P-A → V-F into the now-rinsed reservoir, then pushes the rinse-water + air slug out the gooseneck through V-E → P-A → V-G.

Repeat with "air purge, Channel B."

**Pass:** the air-purge cycle completes; the gooseneck delivers a slug of mixed air + residual rinse water, then sputters dry; firmware reports the reservoir as empty (reed transitions through the levels as it drains). **Fail:** the reservoir doesn't fully drain (suggests a level-sensing misread or a topology-table programming bug — escalate); pump A or B audibly stalls under the air-load condition.

### 10. Level-sensing transitions observed correctly

Across steps 3 through 9, every level-sensing reed has had at least one chance to assert and de-assert. Confirm on the per-serial log that:

- Carbonator low-reed and high-reed both fired during the multiple refill cycles in steps 3, 5, 6, 7.
- Each flavor reservoir's 4 reeds (8 total) have each been observed in both states during the fill (step 1 pre-prime, plus clean-cycle fills in step 8) and drain (steps 6, 7, 8, 9) sequences.

**Pass:** every reed has at least one asserted reading and one de-asserted reading in the log. **Fail:** any reed shows constant state across the entire acceptance run (suggests a wiring fault, a magnet-strength problem, or a stuck float — escalate).

### 11. Multi-hour burn-in

Re-fill both flavor reservoirs to [~50 %](RESERVOIR_FILL_PCT) via the funnel (so there is enough concentrate for the in-burn-in dispenses without needing operator intervention). Re-fill the carbonator. Verify both probes read steady state. Set the bench-acceptance UI to "burn-in mode": firmware runs a timer that performs one metered [~6 oz](BURN_IN_DISP) carbonated-water-plus-flavor dispense every [75 minutes](DISP_INTERVAL) for the duration of the burn-in window.

Target burn-in window: **at least [8 hours](BURN_IN_HOURS) sustained**, with at least **[6 metered dispenses](BURN_IN_MIN_DISP)** across that window. (These numbers are the proposed default; production-final values are an Open item below.) The burn-in is the closest a factory acceptance test gets to a customer-side use profile: dispense, refill, chill, dispense again, hours of compressor cycling. During the burn-in, the operator is not on the bench continuously — firmware is logging — but checks in at the 1-hour, 4-hour, and 8-hour marks (operator discretion on between-checks) to:

- Watch the compressor cycle count and average on-time per cycle. Sustained on-time greater than [~70 %](DUTY_HIGH) duty cycle suggests the loop is undersized or the freeze cutout is misbehaving; sustained on-time below [~10 %](DUTY_LOW) duty cycle (excluding the initial chill-down) suggests the carbonator wall sensor is in the wrong thermal contact (reading colder than the actual water — the probe may have detached or migrated against a cold spot on the coil).
- Watch for any nuisance freeze-protect trips (evap-coil DS18S20 hits [−8 °C](FREEZE_CUTOUT) and firmware shuts the compressor down). One trip during the initial chill-down can be tolerated as recharge-mass-calibration overhang per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) Open items §1; recurrent trips in steady state require investigation of the charge or the suction-line bond.
- Watch for any wet spot anywhere on the appliance — any port, the ASSE drip pan, the floor under the chassis, the foam-shell exits where the coil stubs emerge. Place an absorbent shop towel under the chassis at the start of the burn-in window so any slow leak shows up as a visible patch on the towel at the 4-hour and 8-hour checks.
- **Measure the ASSE drip pan's pull face at the start of the window and again at the end.** The pan must remain against its solid backstop, the moisture plate must remain flat under the vent's fall, and the lead must rise freely into the retained service loop without pulling the pan west. Log the pull-face figure both times; any outward walk requires the loop to be redressed before testing continues.
- Watch for any MQ-6 hydrocarbon-sensor alarm (visible on the enclosure display and audible at the buzzer). Any MQ-6 trip is hard-fail, escalate immediately, do not attempt to continue the burn-in. The MQ-6 stands on edge low in the refrigeration bay, in the open floor strip down the -X wall beside the compressor, and reads the bottom of the cabinet volume where dense R-600a pools from any of the dominant brazed-joint leak sites; a trip means R-600a has reached the LFL-relevant range in the cabinet floor zone, which is the leak case the firmware interlock + SF76E thermal fuse + leak-detection architecture were built to catch.
- Watch for the iOS-app or buzzer alarm raised by the ASSE drip pan's moisture sensor. Any backflow-vent telltale event is hard-fail — it means check #1 in the Multiplex 19-0897 has started to leak, which on a factory-fresh unit indicates a defective backflow preventer, not a customer-side install issue.

Every metered dispense during the burn-in is logged to the per-serial test file: timestamp, dispense volume, dispense temperature (if the thermocouple is left in place between dispenses — operator-discretion bench setup), refractometer reading if available, compressor cycle count since boot, evap-coil minimum temperature since previous dispense, carbonator wall temperature at dispense start. After the [8-hour](BURN_IN_HOURS_DASH) window closes the burn-in ends and the unit is ready for the per-serial log archival in step 12.

**Pass:** burn-in window completes; ≥ [6 dispenses](BURN_IN_MIN_DISP_SHORT) recorded; no nuisance freeze trips after the initial chill-down; no leaks; no MQ-6 trips; no backflow-vent telltale events; compressor duty cycle in the [10–70 %](DUTY_BAND) band averaged over the burn-in window. **Fail:** any of the watch-items above triggers — see Open items below for failure-handling policy.

### 12. Archive per-serial test log

At burn-in end, retrieve the per-serial JSON or CSV file at the bench-acceptance UI's "log download" command. File contains every metered reading from steps 3 through 11. Verify the file is non-empty, the serial number in the file matches the nameplate-pending serial on the chassis, and every step in the procedure has a corresponding log entry.

File is archived to the per-serial path (placeholder `logs/<serial>/acceptance.json` — see Open items for the final committed path). On archive success the unit moves to step 13.

### 13. Drain + air-purge for transit

The burn-in at step 11 refilled the carbonator and both reservoirs, so the unit is wet at the end of the test sequence and has to be emptied before it ships. This is the step [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md) verifies; nothing downstream of here can correct a wet unit.

Close the bench rig's water-side valve and leave the CO2 supply connected — the residual head is what pushes the carbonator out. Drain the carbonator through the dispense path into the bench catch until it runs dry and the low reed sits asserted. Then run the air-purge cycle from step 9 again on both channels, funnel dry and open to air, so each reservoir empties through the gooseneck and the reservoir reeds walk down to empty. Close the CO2 supply, crack the faucet to bleed the appliance side to atmosphere, and disconnect both rig lines.

Confirm before releasing the unit: no water audible on a gentle tilt, both reservoir sumps dry, and a cracked faucet on the de-pressurized appliance discharges nothing. A unit that still holds liquid repeats this step — it does not move to the finish bench wet.

## Output condition

A unit that has passed acceptance and burn-in:

- Carbonator first-water-fill completed without leak
- Pump connection cycled dry through connected → release → park → squeeze → connected; all four tubes released and reconnected together, the pump plug unclipped from the pump jack and clicked home without disturbing the jack or the +X cable clip, both integral tabs and the center joint remained sound, and all four bowed stubs plus four moving hairpin ends remained clear and undamaged
- Gas-feed and carbonator pressures recorded through refill and hold; downstream check reverse sealing qualified; no external leakage or SV-125 relief event during normal operation
- ASSE drip pan dry throughout
- Initial fill, refill and pump restart completed with measured inlet/discharge/carbonator pressure and supply margin
- First and successive ~[12 oz](GLASS_OZ) glasses at ≤ [~6 °C](DISP_TEMP_MAX) with the agreed strong carbonation; pour cadence, refill timing and recovery recorded
- First flavor A dispense at the documented [1:20](RATIO) ratio ([±5 %](RATIO_TOL_SIGNED) volume) with measured pump output
- First flavor B dispense at the same ratio with channel-to-channel pump agreement within [~10 %](CHANNEL_TOL)
- Clean cycle through both channels completed without operator intervention
- Air-purge cycle through both channels completed
- All 10 reeds (carbonator 2 + reservoirs 8) observed transitioning during the test sequence
- ≥ [8-hour](BURN_IN_HOURS_DASH) burn-in with ≥ [6 metered dispenses](BURN_IN_MIN_DISP), no nuisance freeze trips, no leaks, no MQ-6 trips, no backflow-vent telltale events, compressor duty cycle in the [10–70 %](DUTY_BAND) band
- Per-serial test log archived
- Carbonator and both flavor reservoirs drained and air-purged dry for transit, both rig lines disconnected, appliance side bled to atmosphere

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Burn-in duration + cycle-count thresholds.** The [8-hour / 6-dispense](BURN_IN_TARGET) target is a reasonable starting point but the production-ready number isn't yet decided. Compressor duty-cycle bands ([10–70 %](DUTY_BAND)) are also placeholder bracketing. Tighten or loosen against early-unit observed data; commit a final value once units 1–3 have run through.
2. **Per-serial log path, format, storage location.** Placeholder is `logs/<serial>/acceptance.json` on the bench machine running the acceptance UI. Open: filesystem (local-only) vs cloud (sync to a per-unit folder) vs both; JSON vs CSV vs structured columnar format; retention policy and access path for service callbacks against shipped units.
3. **Acceptance failure handling.** What is the policy for a unit that fails any test step? Rework on the bench, scrap, send-to-investigation? This mirrors the same gap in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) "Open items" §2 at hydro-test — the same decision tree should apply across both gates and ideally lives in one place once committed.
4. **Test-syrup supply for acceptance.** [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) treats SodaStream concentrate as user-supplied at install. Acceptance consumes [~11 %](CONC_PCT) of one bottle per unit ([~50 mL](CONC_ML) across the test sequence) regardless. Open: do two bottles ship with the unit (factory-supplied for acceptance, then continued in service by the customer), or does the factory keep a bench stock and the customer buys their own bottles from day one?
5. **Ratio acceptance threshold.** The [1:20](RATIO) ratio is documented as the design target. The [±5 %](RATIO_TOL_SIGNED) volume band and the [~10 %](CHANNEL_TOL) channel-to-channel agreement band in this doc are starting points; the production-final ratio tolerance (especially the cross-channel agreement) needs a committed number that ties back to the perceived-taste impact of small ratio drifts on the SodaStream concentrate formulation.
6. **Refractometer use — required or optional?** Currently listed as optional bench tooling. If the volume measurement on its own is not a sufficient ratio proxy (especially in light of item 5), the refractometer becomes required and a specific °Brix target per flavor needs to be locked.

7. **First-unit operating envelope.** Commit the measured pressure setting, refill and restart limits, initial CO2 conditioning, pour cadence, carbonation reference and recovery time from steps 3–5. Instrument fixture and gauge locations belong in that record. Nominal pump flow and gas setpoint are not substitutes.
8. **Automatic acceptance controls.** Complete and commission the controls identified in the firmware prerequisite before claiming automatic fills, timed burn-in or log download. Manual bench evidence must name its actual control method.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_acceptance_and_burn_in_sync.py`
