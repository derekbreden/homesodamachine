# Acceptance and Burn-In

The production procedure for the bench acceptance test and multi-hour burn-in on a finished, commissioned appliance — the last sign-off step before the unit moves to [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md). Inputs are a chassis that has come out of [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) with sensors healthy and setpoints loaded; outputs are a per-serial test log and a unit cleared to ship.

This is the first time the carbonator vessel sees water in service. The vessel was hydro-tested empty during [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) and integrated dry through [`cold-core.md`](/hardware/assembly/cold-core.md) and [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md); first water-fill is here. CO2 supply is first energized here against a wet vessel. The bench test rig stands in for customer-side plumbing — the appliance sees nothing different from what it will see at install.

## Scope

In: a chassis fresh out of [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) — powered, firmware flashed, all sensors healthy on first read (both temperature probes (DS18B20 tank + DS18S20 coil), both reed pairs on each flavor reservoir, both reeds on the carbonator, the DIGITEN flow sensor, the MQ-6, the backflow drip-pan moisture sensor), all ten solenoid valves cycled through their firmware self-test, compressor + condenser fan firmware-gated together, setpoints loaded (carbonator wall [2 °C](WALL_SETPOINT) [± 2 °C](WALL_BAND), evap-coil freeze cutout [−8 °C](FREEZE_CUTOUT), compressor min-off [3 min](MIN_OFF)); a bench test rig consisting of a test-rig water source feeding the rear-panel FFL38BARB38 inlet, a test-rig CO2 supply feeding the DERPIPE bulkhead at [70–100 PSI](CO2_PRIMARY_RANGE) primary, a [12 oz](GLASS_OZ) target glass, a graduated cylinder ([250 mL](CYL_MIN) or larger), a thermocouple gun or food thermometer ([0–20 °C](THERMO_RANGE) range), a stopwatch, and a refractometer if available for ratio check; two SodaStream concentrate bottles (Diet Mountain Dew + one other) primed in the flavor reservoirs via the top hopper before the test sequence begins.

Out: a unit that has passed every step of the functional acceptance test below (first water fill of the carbonator without leak; CO2 supply on, WR1110 holds [90 PSI](CO2_CENTERLINE), PRV does not weep, backflow drip pan stays dry; first carbonated water dispense ~[12 oz](GLASS_OZ) at ≤ [~6 °C](DISP_TEMP_MAX); first flavor A and flavor B dispenses at the target ratio with measured pump output; clean cycle through both channels; air-purge cycle; all level-sensing transitions observed correctly) and a multi-hour burn-in (with periodic dispenses on a timer, watching compressor cycle count, watching for nuisance freeze-protect trips, watching for leaks, watching for MQ-6 trips). Per-serial test log archived.

Not in scope: cosmetic inspection, nameplate verification, packaging — all in [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md). Customer-side install commissioning (running the unit on the customer's tap-water + CO2 bottle for the first time in their kitchen) is a separate procedure, not part of factory acceptance.

## Inputs per appliance

Per-unit BOM is the entire BOM of record at this step — by acceptance the unit is fully built. The table below is the bench-rig and per-test consumable summary, not appliance parts; appliance BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md).

| Item | Source / spec | Notes |
|---|---|---|
| Test-rig water source | Bench cold-water tap, regulated [40–80 PSI](WATER_PRESS_RANGE), terminated in 3/8" FFL to mate the appliance's FFL38BARB38 inlet | Stands in for the customer's under-sink supply line. Cold (≤ [~20 °C](WATER_TEMP_MAX)) so the carbonator's first chill-down matches real-world conditions. |
| Test-rig CO2 source | [5 lb](CO2_CYL_SMALL) or [10 lb](CO2_CYL_LARGE) CO2 cylinder + CGA-320 primary regulator set to [70–100 PSI](CO2_PRIMARY_RANGE) + 5/16" beer line into the DERPIPE front-panel bulkhead | Stands in for the customer's CO2 bottle; the CGA-320 primary regulator ships with the appliance. The in-appliance WR1110 holds the appliance-side [90 PSI](CO2_CENTERLINE) regardless of where the primary is set; setting the primary anywhere in [70–100 PSI](CO2_PRIMARY_RANGE) is the same test. |
| Target glass | [12 oz](GLASS_OZ) drinking glass, clear, room-temperature | Receives every dispense in the acceptance sequence. Visual evidence of carbonation + color + foam head behavior. |
| Graduated cylinder | [250 mL](CYL_MIN) or larger, food-grade plastic or borosilicate glass | Measures dispense volume by pour-into-cylinder for the metered dispenses. Replaces the target glass on metered steps. |
| Thermocouple gun or food thermometer | [0–20 °C](THERMO_RANGE) range, [±0.5 °C](THERMO_ACC) or better | Measures dispensed-water temperature at the nozzle and inside the target glass. Probe-style is preferred over IR for liquid temperature; IR reads surface only. |
| Stopwatch | Phone stopwatch is fine | Times the dispense window for the metered-flow steps. |
| Refractometer (optional) | [0–32 °Brix](BRIX_RANGE) handheld, ATC-equipped | If available, measures sucralose-equivalent °Brix on the dispensed mix to back-check the [1:20](RATIO) ratio. SodaStream concentrate is sucralose-based, not sugar-based, so the Brix reading is a sweetener proxy not a literal sugar concentration — useful as a relative check between channels, not as an absolute. |
| SodaStream concentrate, Diet Mountain Dew | [0.44 L](BOTTLE_L) bottle | Channel A test syrup. Whether factory-supplied or customer-supplied is an Open item below. |
| SodaStream concentrate, second flavor | [0.44 L](BOTTLE_L) bottle | Channel B test syrup. Same open item. |
| Per-serial test log file | Placeholder `logs/<serial>/acceptance.json` | Every metered value captured at the appliance and saved to a serial-keyed file. Format + final path is an Open item below. |

Tooling (bench, shared across all units — not per-build consumed): the test-rig water + CO2 connections themselves, the [12 oz](GLASS_OZ) glass, the graduated cylinder, the thermocouple, the stopwatch, and the optional refractometer. Two SodaStream concentrate bottles are consumed per unit in small dispense volumes ([~50 mL](CONC_ML) of concentrate across the full test sequence, [~11 %](CONC_PCT) of one bottle); whether they are factory-supplied or customer-supplied is an Open item.

## Procedure

### 1. Pre-test inspection + connect bench rig

Verify the chassis came out of [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) with all checkboxes signed off. The unit is sitting on the bench, AC cord unplugged, all rear-panel connections capped or plugged. Visually inspect the exterior — no displaced fittings, no shipping-damage cracks in the printed enclosure, the compressor shroud is in place, the C14 inlet recess is clean, the rear-panel umbilical bulkheads are seated. Open the Zone C top door, lift out the funnel, and confirm both Kamoer pumps are seated and their leads spade-connected to the DC-5 harness; reinstall the funnel and close the door.

Connect the test-rig water source to the rear-panel FFL38BARB38 inlet, hand-tight on the 3/8" FFL swivel. Route the Multiplex 19-0897 atmospheric vent telltale line to its internal drip pan (this run was made during enclosure-mechanical; verify it is still seated over the pan and the moisture sensor is dry). Connect the test-rig CO2 source to the front-panel DERPIPE bulkhead, 5/16" beer line pushed home with the collar fully seated. Open the CO2 cylinder valve and set the primary CGA-320 regulator to [90 PSI](CO2_CENTERLINE) (anywhere in [70–100 PSI](CO2_PRIMARY_RANGE) is acceptable; [90 PSI](CO2_CENTERLINE) is the centerline). Do not yet open the water-side test-rig valve. Place the [12 oz](GLASS_OZ) target glass on the bench under the faucet position (the faucet itself is on its under-counter mount; the bench can take the chassis with the faucet temporarily oriented over a catch tray or with a stub line into the same target glass — bench-rig detail at operator discretion).

**Pass:** all bench-rig connections leak-free at the rear panel against the now-pressurized CO2 line, water side still off; backflow vent telltale routed over the dry drip pan; both pumps seated. **Fail:** any audible CO2 hiss at the DERPIPE bulkhead or any back-of-rig joint — recheck the push-to-connect seating, re-test before continuing.

### 2. Power on + interlock check

Plug the C14 inlet into a bench outlet via the supplied NEMA 5-15P → C13 cord. Firmware boots; the ESP32-S3 rotary display lights up showing the selected flavor and reports sensor health on first read: both temperature probes (DS18B20 tank + DS18S20 coil) reporting within [±0.5 °C](THERMO_ACC) of bench ambient, MQ-6 in normal range, backflow drip pan dry, all reed switches in their expected state for an empty system (carbonator-empty, flavor-reservoirs-full from the hopper pre-prime, faucet closed).

Firmware should NOT dispense, should NOT energize the compressor, and should NOT energize the SeaFlo refill pump until the operator enters bench-acceptance mode and water-fill is explicitly commanded. The on-boot state is idle, sensors live, actuators dark.

**Pass:** display reports all green sensors; no actuator energizes on boot. **Fail:** any sensor reads out-of-range on first read, or any actuator energizes without command — return to firmware-and-commissioning.

### 3. First water fill of the carbonator

Open the test-rig water-side valve. The carbonator low-level reed reads empty; with the faucet closed and the empty-reed asserted, firmware now permits a refill cycle. Operator commands "fill carbonator" from the bench-acceptance UI. The SeaFlo diaphragm pump energizes (relay #2, ESP32 GPIO 16). Water flows from the bench tap through the Multiplex 19-0897 backflow → FFL38BARB38 → SeaFlo → GASHER water-side check → PP010822E adapter pair → +Z foam-shell slot → TAISHER 90° elbow → vessel top-plate Port 2 → vessel headspace, against the not-yet-charged CO2 side (atmospheric).

Pump runs until the high-level reed asserts, then firmware closes the cycle and de-energizes the pump.

**Pass:** the high-level reed asserts within the expected fill time (sized to vessel volume + SeaFlo flow rate; tens of seconds, not minutes); the pump stops; no leak at the FFL38BARB38, no leak at the +Z slot transitions, no leak at the top-plate elbow joint, no water at the backflow vent (vent drip pan dry). **Fail:** pump runs past the expected fill window without high-reed assert (suggests reed fault, float stuck, or pump-pull short-circuit elsewhere); any leak observed at any joint.

### 4. CO2 supply on, leak-tight at [90 PSI](CO2_CENTERLINE)

The CO2 cylinder valve was opened in step 1; the line is already pressurized up to the WR1110 secondary regulator's inlet. At this point the WR1110 holds the appliance-side at [90 PSI](CO2_CENTERLINE); the gas path is closed at the bottom-plate Port 1 against the sparge stone. With water now in the vessel, the sparge stone is wetted and CO2 begins to bubble through into the headspace.

Watch for two minutes. The WR1110 should reach and hold [90 PSI](CO2_CENTERLINE) on the appliance-side gauge (the customer-facing dual-gauge regulator above the cylinder is the primary; the WR1110 is internal and not directly readable — proxy is the audible cessation of in-rush hiss and steady-state silence). The SV-125 PRV does not weep audibly or visibly. The Multiplex 19-0897 atmospheric vent drip-pan moisture sensor stays dry (firmware should not have raised an alarm).

**Pass:** steady [90 PSI](CO2_CENTERLINE) on the appliance side; no PRV weep over the [2-minute](PRV_HOLD) hold; no backflow vent telltale; no audible leak at any port elbow, the WR1110 inlet/outlet, or any CO2-side push-to-connect joint. **Fail:** PRV opens (above 125 PSI set pressure — indicates WR1110 fault), audible leak anywhere on the CO2 path, or any wetness at the backflow vent (cross-contamination of the water and CO2 paths, fault).

### 5. First carbonated-water dispense

Wait for the carbonator wall DS18B20 to reach [2 °C](WALL_SETPOINT) [± 2 °C](WALL_BAND) as the refrigeration loop pulls the new water-fill down to service temperature. First chill from [~20 °C](TAP_WATER_TEMP) tap water down to [2 °C](WALL_SETPOINT) takes meaningfully longer than the steady-state hysteresis cycle that follows — expect tens of minutes to the first compressor-off event, not the few-minute cycle interval of normal service. This first-chill window is also when the recharge-mass calibration (per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) Open items §1) is most visibly stressed: if the charge is short, the evap-coil DS18S20 will hit the [−8 °C](FREEZE_CUTOUT) freeze-protect cutout before the wall reaches setpoint; if the charge is long, the wall will reach setpoint but the compressor will run a longer-than-expected duty cycle to hold it. Firmware reports both temperatures on the config display continuously; the operator does not need to be at the bench during chill-down but should check in once it's past.

Once the wall reads ≤ [4 °C](WALL_DISP_GATE) and the compressor has shut off on hitting [2 °C](WALL_SETPOINT), place the [12 oz](GLASS_OZ) target glass under the faucet. Open the faucet lever for a full pour; firmware reads the DIGITEN flow sensor and the active flavor selector (set to "carbonator only" via the bench-acceptance UI for this step — no flavor injection). The faucet stays open until the glass is roughly full; close the lever.

Immediately measure the dispensed water temperature with the thermocouple inserted into the glass. Read carbonation behavior: visible bubble train at the side wall of the glass, foam head that persists for at least [10 seconds](FOAM_HOLD) before breaking, no sputter or air-gulp during the pour. The first pour is the most informative on the chilled-dispense run's heat pickup — the line from the cold core's bottom port up through the foam shell to the Westbrass faucet is the most temperature-critical path in the system, and any departure from spec here suggests an insulation gap on the CARGEN nitrile sleeve or a missing foil-bond contact.

**Pass:** dispense volume approximately [12 oz](GLASS_OZ) on a full pour; temperature in the glass ≤ [~6 °C](DISP_TEMP_MAX); carbonation visible and behaving normally (foam head, bubble train, no sputter); the low-level reed asserts at some point during or just after the pour, triggering the next refill cycle. **Fail:** sputtering pour (indicates inadequate carbonation or air ingress on the dispense line); dispense temperature > [6 °C](DISP_TEMP_FAIL) (indicates the wall temp wasn't actually at setpoint when the pour started, or the dispense line picked up heat — re-check insulation along the chilled run); volume far off [12 oz](GLASS_OZ) (indicates flow-sensor calibration drift or faucet seat issue).

### 6. First flavor A dispense + flavor pump metering

Re-fill the carbonator (step 3 cycle repeats automatically since the low-level reed is asserted; let it run through). Place the graduated cylinder under the faucet. Set the bench-acceptance UI to "Channel A, metered ratio test" — firmware will run a fixed-duration carbonated water dispense alongside a peristaltic-pump A pulse train sized to the documented [1:20](RATIO) ratio.

Run the metered dispense (target [~250 mL](METERED_WATER) water + [~12.5 mL](METERED_FLAVOR) flavor A concentrate, totalling [~262.5 mL](METERED_TOTAL)). The graduated cylinder receives the mixed product; the carbonator low-reed will likely assert mid-pour and queue a refill which firmware will defer until the dispense window closes.

Measure: total volume in the graduated cylinder, and (if refractometer available) °Brix of the mixed dispense. Compute actual ratio against the [1:20](RATIO) target. Tasting is allowed but not the pass criterion; the volume and the refractometer reading are.

**Pass:** total dispense volume within [~5 %](RATIO_TOL) of [~262.5 mL](METERED_TOTAL) (i.e., [~249–276 mL](METERED_RANGE)); refractometer reading consistent with a [1:20](RATIO) dilution of the SodaStream concentrate (no absolute number locked here — see Open items for the ratio-tolerance gap); pump A audibly running during the dispense window, no missed steps, no pump slip. **Fail:** volume far outside the [±5 %](RATIO_TOL_SIGNED) band (suggests pump A under- or over-delivery, indicating a tube-fatigue problem in the peristaltic head); refractometer reading suggests a far-off ratio; any pump audible stall.

### 7. First flavor B dispense + flavor pump metering

Repeat step 6 with Channel B selected. Same metered dispense, same measurements, same pass criteria. The two channels are mechanically identical; cross-comparing the channel-A and channel-B numbers (volume, refractometer if used) checks the pump-to-pump consistency.

**Pass:** same as step 6, plus channel A and channel B agree to within [~10 %](CHANNEL_TOL) on the refractometer reading (if used) — both channels are running the same target ratio against the same carbonated water source. **Fail:** any single-channel failure as in step 6; or both channels passing the absolute criterion but disagreeing by > [10 %](CHANNEL_TOL_FAIL) between channels (suggests one pump has drifted; both will need recalibration before ship).

### 8. Clean cycle through both channels

From the bench-acceptance UI, run "clean cycle, Channel A." Firmware executes the topology-table sequence (per [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) "Clean Water Fill → Bag A" followed by "Clean Flush A (water out)"): tap-water source fills the flavor reservoir A through the manifold, then the same path that dispenses syrup is run to flush it out the nozzle into the target glass. The target glass receives faintly-tinted rinse water.

Repeat with "clean cycle, Channel B."

**Pass:** the clean cycle completes without operator intervention; rinse-water emerging at the nozzle is faintly tinted on the first pass and runs clear on a follow-up pass if commanded; no leak anywhere in the manifold during the clean cycle; firmware reports both cycles complete and ready. **Fail:** any solenoid valve fails to open or close as expected (firmware will normally flag this on the config display); rinse never runs clear (suggests a reservoir-internal cleanability problem, escalate); any leak observed.

### 9. Air-purge cycle through both channels

From the bench-acceptance UI, run "air purge, Channel A." Firmware executes the topology-table "Air Purge In → Bag A" + "Air Purge Out A" sequence: with the hopper funnel dry and open to air, pump A pulls air through V-B → V-C → P-A → V-F into the now-rinsed reservoir, then pushes the rinse-water + air slug out the nozzle through V-E → P-A → V-G.

Repeat with "air purge, Channel B."

**Pass:** the air-purge cycle completes; the nozzle delivers a slug of mixed air + residual rinse water, then sputters dry; firmware reports the reservoir as empty (reed transitions through the levels as it drains). **Fail:** the reservoir doesn't fully drain (suggests a level-sensing misread or a topology-table programming bug — escalate); pump A or B audibly stalls under the air-load condition.

### 10. Level-sensing transitions observed correctly

Across steps 3 through 9, every level-sensing reed has had at least one chance to assert and de-assert. Confirm on the per-serial log that:

- Carbonator low-reed and high-reed both fired during the multiple refill cycles in steps 3, 5, 6, 7.
- Each flavor reservoir's 4 reeds (8 total) have each been observed in both states during the fill (step 1 pre-prime, plus clean-cycle fills in step 8) and drain (steps 6, 7, 8, 9) sequences.

**Pass:** every reed has at least one asserted reading and one de-asserted reading in the log. **Fail:** any reed shows constant state across the entire acceptance run (suggests a wiring fault, a magnet-strength problem, or a stuck float — escalate).

### 11. Multi-hour burn-in

Re-fill both flavor reservoirs to [~50 %](RESERVOIR_FILL_PCT) via the hopper (so there is enough concentrate for the in-burn-in dispenses without needing operator intervention). Re-fill the carbonator. Verify both probes read steady state. Set the bench-acceptance UI to "burn-in mode": firmware runs a timer that performs one metered [~6 oz](BURN_IN_DISP) carbonated-water-plus-flavor dispense every [75 minutes](DISP_INTERVAL) for the duration of the burn-in window.

Target burn-in window: **at least [8 hours](BURN_IN_HOURS) sustained**, with at least **[6 metered dispenses](BURN_IN_MIN_DISP)** across that window. (These numbers are the proposed default; production-final values are an Open item below.) The burn-in is the closest a factory acceptance test gets to a customer-side use profile: dispense, refill, chill, dispense again, hours of compressor cycling. During the burn-in, the operator is not on the bench continuously — firmware is logging — but checks in at the 1-hour, 4-hour, and 8-hour marks (operator discretion on between-checks) to:

- Watch the compressor cycle count and average on-time per cycle. Sustained on-time greater than [~70 %](DUTY_HIGH) duty cycle suggests the loop is undersized or the freeze cutout is misbehaving; sustained on-time below [~10 %](DUTY_LOW) duty cycle (excluding the initial chill-down) suggests the carbonator wall sensor is in the wrong thermal contact (reading colder than the actual water — the probe may have detached or migrated against a cold spot on the coil).
- Watch for any nuisance freeze-protect trips (evap-coil DS18S20 hits [−8 °C](FREEZE_CUTOUT) and firmware shuts the compressor down). One trip during the initial chill-down can be tolerated as recharge-mass-calibration overhang per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) Open items §1; recurrent trips in steady state require investigation of the charge or the suction-line bond.
- Watch for any wet spot anywhere on the appliance — any port, the backflow drip pan, the floor under the chassis, the foam-shell exits where the coil stubs emerge. Place an absorbent shop towel under the chassis at the start of the burn-in window so any slow leak shows up as a visible patch on the towel at the 4-hour and 8-hour checks.
- Watch for any MQ-6 hydrocarbon-sensor alarm (visible on the config display and audible at the buzzer). Any MQ-6 trip is hard-fail, escalate immediately, do not attempt to continue the burn-in. The MQ-6 sits low on the rear interior enclosure wall (mesh facing horizontally inward) and reads the bottom of the cabinet volume where dense R-600a pools from any of the dominant brazed-joint leak sites; a trip means R-600a has reached the LFL-relevant range in the cabinet floor zone, which is the leak case the firmware interlock + SF76E thermal fuse + leak-detection architecture were built to catch.
- Watch for the iOS-app or buzzer alarm raised by the backflow drip-pan moisture sensor. Any backflow-vent telltale event is hard-fail — it means check #1 in the Multiplex 19-0897 has started to leak, which on a factory-fresh unit indicates a defective backflow preventer, not a customer-side install issue.

Every metered dispense during the burn-in is logged to the per-serial test file: timestamp, dispense volume, dispense temperature (if the thermocouple is left in place between dispenses — operator-discretion bench setup), refractometer reading if available, compressor cycle count since boot, evap-coil minimum temperature since previous dispense, carbonator wall temperature at dispense start. After the [8-hour](BURN_IN_HOURS_DASH) window closes the burn-in ends and the unit is ready for the per-serial log archival in step 12.

**Pass:** burn-in window completes; ≥ [6 dispenses](BURN_IN_MIN_DISP_SHORT) recorded; no nuisance freeze trips after the initial chill-down; no leaks; no MQ-6 trips; no backflow-vent telltale events; compressor duty cycle in the [10–70 %](DUTY_BAND) band averaged over the burn-in window. **Fail:** any of the watch-items above triggers — see Open items below for failure-handling policy.

### 12. Archive per-serial test log

At burn-in end, retrieve the per-serial JSON or CSV file at the bench-acceptance UI's "log download" command. File contains every metered reading from steps 3 through 11. Verify the file is non-empty, the serial number in the file matches the nameplate-pending serial on the chassis, and every step in the procedure has a corresponding log entry.

File is archived to the per-serial path (placeholder `logs/<serial>/acceptance.json` — see Open items for the final committed path). On archive success the unit moves to [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md).

## Output condition

A unit that has passed acceptance and burn-in:

- Carbonator first-water-fill completed without leak
- CO2 supply on, WR1110 holds [90 PSI](CO2_CENTERLINE), SV-125 PRV does not weep at working pressure
- Backflow drip pan dry throughout
- First carbonated-water dispense ~[12 oz](GLASS_OZ) at ≤ [~6 °C](DISP_TEMP_MAX) with normal carbonation behavior
- First flavor A dispense at the documented [1:20](RATIO) ratio ([±5 %](RATIO_TOL_SIGNED) volume) with measured pump output
- First flavor B dispense at the same ratio with channel-to-channel pump agreement within [~10 %](CHANNEL_TOL)
- Clean cycle through both channels completed without operator intervention
- Air-purge cycle through both channels completed
- All 10 reeds (carbonator 2 + reservoirs 8) observed transitioning during the test sequence
- ≥ [8-hour](BURN_IN_HOURS_DASH) burn-in with ≥ [6 metered dispenses](BURN_IN_MIN_DISP), no nuisance freeze trips, no leaks, no MQ-6 trips, no backflow-vent telltale events, compressor duty cycle in the [10–70 %](DUTY_BAND) band
- Per-serial test log archived

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Burn-in duration + cycle-count thresholds.** The [8-hour / 6-dispense](BURN_IN_TARGET) target is a reasonable starting point but the production-ready number isn't yet decided. Compressor duty-cycle bands ([10–70 %](DUTY_BAND)) are also placeholder bracketing. Tighten or loosen against early-unit observed data; commit a final value once units 1–3 have run through.
2. **Per-serial log path, format, storage location.** Placeholder is `logs/<serial>/acceptance.json` on the bench machine running the acceptance UI. Open: filesystem (local-only) vs cloud (sync to a per-unit folder) vs both; JSON vs CSV vs structured columnar format; retention policy and access path for service callbacks against shipped units.
3. **Acceptance failure handling.** What is the policy for a unit that fails any test step? Rework on the bench, scrap, send-to-investigation? This mirrors the same gap in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) "Open items" §2 at hydro-test — the same decision tree should apply across both gates and ideally lives in one place once committed.
4. **Test-syrup supply for acceptance.** [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) treats SodaStream concentrate as user-supplied at install. Acceptance consumes [~11 %](CONC_PCT) of one bottle per unit ([~50 mL](CONC_ML) across the test sequence) regardless. Open: do two bottles ship with the unit (factory-supplied for acceptance, then continued in service by the customer), or does the factory keep a bench stock and the customer buys their own bottles from day one?
5. **Ratio acceptance threshold.** The [1:20](RATIO) ratio is documented as the design target. The [±5 %](RATIO_TOL_SIGNED) volume band and the [~10 %](CHANNEL_TOL) channel-to-channel agreement band in this doc are starting points; the production-final ratio tolerance (especially the cross-channel agreement) needs a committed number that ties back to the perceived-taste impact of small ratio drifts on the SodaStream concentrate formulation.
6. **Refractometer use — required or optional?** Currently listed as optional bench tooling. If the volume measurement on its own is not a sufficient ratio proxy (especially in light of item 5), the refractometer becomes required and a specific °Brix target per flavor needs to be locked.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_acceptance_and_burn_in_sync.py`
