# PCBA audit — Snapshot 2026-07-11

**This is a point-in-time snapshot, not a living document.** Board state: commit `f9355cc7`, rendered 2026-07-11. Re-running this audit later produces a fresh dated file against the then-current board.

## TL;DR

- Render gates **11/11 pass** (clearance floor 0.15 mm, 0 opens, 0 DRC errors), score 100 % (115 pcbPath, 0 auto, 0 deferred), 79/79 parts carry a JLCPCB #. `silk-audit.py`: 0 findings. `part-orientation-audit.py`: 79 parts, 0 flagged.
- **One measured board defect:** the V12 island void at mounting holes MH2/MH3 is r 2.2 mm from the hole centre; every fastener the mounting-hole comment anticipates (M3 head r ≈ 2.75, hex standoff r ≈ 3.2, washer r ≈ 3.5) reaches past it onto mask-covered 12 V copper. §Board findings. *Resolved later the same day — see item 1.*
- **Three pre-fab electrical decisions open:** buzzer flyback diode, flow-sensor 5 V-domain input, moisture-sensor VCC vs. the pulse instruction in `bom.md`. §Board findings. *Moisture-sensor VCC resolved 2026-07-12 — see item 4.*
- **Firmware:** `firmware/src/main.cpp` is the L298N prototype's. The only pins agreeing with this board are I²C IO21/IO22. §Firmware ↔ board.
- **The drift checker cannot read the board:** `check_pinmap.py` parses 0 GPIOs from the current trace syntax; `silk-audit.py` / `part-orientation-audit.py` run only by hand; the scorecard prints gates but fails nothing. §Checks.
- Doc rows in `jlcpcb-parts.md`, `ledger/bom.md`, and `pcb/pcba/README.md` describe earlier board states. §Docs ↔ board.

## Source-data state

- `hardware/pcb/pcba/pcba.tsx` at `f9355cc7`; `out/pcba.circuit.json` from `bun render-board.ts pcba.tsx` on 2026-07-11.
- Field loads from `wiring/ac-wiring-schedule.md`, `wiring/power.mmd`, `hardware/topology/fluid-topology.md`, `wiring/valve-control.mmd`, `ledger/bom.md`.

## Methodology

Read `pcba.tsx` and `parts.tsx` end-to-end; checked the polarity- and pinout-critical imports (`ESP32_WROOM_32E_N4`, `CH340C`, `TYPE_C_31_M_12`, `USBLC6_2SC6`, the three LED imports, `KH_CR2032_2_1`, `NXB_25V470_10_12_5`, `MLT_5020`, `KF301_5_0_2P`) pin-by-pin against manufacturer pinouts; ran the render plus both manual audits plus `check_pinmap.py`; measured the V12 pour voids from `out/pcba.circuit.json`; tallied the off-board load behind every connector from the wiring/ledger/topology docs; diffed the firmware's pin usage against the board.

To re-run: `bun render-board.ts pcba.tsx`, `python3 silk-audit.py`, `tools/cad-venv/bin/python part-orientation-audit.py`, `python3 hardware/scripts/check_pinmap.py`, then the read-and-cross-reference passes above with fresh eyes.

## Verified consistent

- **WROOM import**: all 39 pads match the ESP32-WROOM-32E datasheet position-for-position (incl. RXD0=IO3 / TXD0=IO1, the input-only IO34-39 row, flash pins 17–22 unconnected). Antenna section overhangs the west board edge; the render log clears the antenna box from all 3 pours.
- **USB-C block**: CC1 (A5) and CC2 (B5) each on 5.1 k Rd; D+ = A6+B6, D− = A7+B7; SBU open; VBUS isolated to the ESD rail. USBLC6 pass-through 1→6 / 3→4. CH340C V3 tied to VCC at 3V3, DTR pin 13 / RTS pin 14, TXD→IO3 / RXD→IO1. Q2/Q3 wiring matches the esptool ClassicReset truth table.
- **Strapping pins**: IO0 (10 k up + SW1 + Q3), IO2 (relay opto load holds low), IO5 open, IO12 (LED-to-GND load only), IO15 (LED; boot glint noted in `esp32-scope.md`).
- **Power-on state before firmware**: MCP GPA reset as inputs → ULN inputs float low → valves off; DRV8870 INs have internal pulldowns → pumps off; relay optos see no drive → off; Q1 base floats through R5 → buzzer off.
- **RS485**: /RE→GND, /SHDN→VCC, auto-direction on DI, 120 R termination, SM712 at the cable entry; 3V3 supply keeps RO inside input-only IO34's range.
- **Gas dividers**: 2.2 k / 3.3 k → 5 V × 0.6 = 3.0 V at IO36/IO39.
- **I²C / 1-wire**: 4.7 k pull-ups to 3V3 (R19/R20 on-board; R9 at the connector where the ~600 mm probe loom leaves). MCP addresses 0x20/0x21 strapped, /RESET high; DS3231 pin map correct; no coin-cell charge path.
- **Current vs. rating where documented**: XH contact 2 A vs. worst pin 1.38 A (MANIFOLD A COM at 3 valves); pump lines 0.4 mm for 0.8 A; valve lines 0.3 mm for ≤0.5 A; KF301 17 A vs. ~3.6 A board peak; motor/valve runs are top-layer only (no via in the path); 12 V-rail caps rated 25 V; battery-backup float 13.6 V is inside every connected input rating (K7805 36 V, DRV8870 45 V, C3 25 V, 4.3B display 7–36 V).
- **LED imports**: anode = pin1 in all three (the KENTO pad-numbering swap is handled in-file); rot 180 puts anodes at the resistors; cathodes to GND. C3 carries a `+` silk at pin1 (west, V12). J10 pin labels sit at the screws.

## Board findings

1. **MH2/MH3 fastener annulus vs. the V12 island.** Measured from the routed pour: void radius **2.2 mm** from hole centre (4.0 mm pad + 0.2 mm clearance) at MH2 (13.5, 33.0) and MH3 (13.5, −33.3). The mounting-hole comment (`pcba.tsx`) sizes the hardware: head ⌀ ~5.5 → r ~2.75, standoff r ~3.2, washer r ~3.5. Each reaches 0.55–1.3 mm past the void onto 12 V copper under solder mask, on the two corners inside the island; the island's `netClearance` rule widens voids for V3V3/V5/SDA/SCL nets and these pads are GND. MH1/MH4 have no top pour. Worth widening the island void at these two holes to r ≥ 3.75 mm before fab.
   **Resolved 2026-07-11 (same day):** `fastenerAnnulus="3.75mm top"` declared on MH1–MH4 in `pcba.tsx`, cut post-route by `pour-clearance.ts` `widenFastenerAnnuli` (square keepout). Measured from the re-rendered `out/pcba.circuit.json`: V12 island void **r = 3.750 mm** at both MH2 and MH3; inner planes and the bottom GND plane keep the solver's 2.2 mm antipad. Follow-through, same day: the holes carry no net — the screws drive into printed PETG bosses, and the `connectsTo="net.GND"` the comment claimed had never materialized (no port, no net linkage; the GND plane antipadded all four pads). At MH1: the RTS and EN lanes ride the bottom (routeBottom) through the corridor east of R18, ≥4.2 mm from the hole; R17 turned rot 0 (pads r 3.83) and SW1/SW2 slid east 0.5 to the J5 courtyard cap (SW2.C r 3.63, past the washer's 3.6 worst-case reach). Gates 11/11 after the change.
2. **Buzzer flyback.** The MLT-5020 is a magnetic transducer (~100 mA coil) PWM-switched by Q1; no clamp diode exists across it — `jlcpcb-parts.md` records the omission and names the diode as "the first thing to add if the transistor shows stress". The board is JLCPCB-assembled; adding it after fab is a bodge wire or a new order. Open decision: add the diode footprint pre-order, or run the bench and watch Q1.
3. **Flow-sensor input.** The DIGITEN sensor is powered from V5 (J4) and its output lands directly on IO25 (not 5 V-tolerant). The design note reads "flow uses the internal pull-up (open-collector)" — the input's safety rests on that assumption about the sensor's output stage; modules in this class ship both open-collector and pull-up-to-VCC variants. The MQ-6's two 5 V outputs got on-board dividers; IO25 has none. Worth bench-verifying this sensor's output stage (or powering it from 3V3 if its range allows) before the loom is built.
4. **Moisture-sensor VCC.** `bom.md:59`: "Bare electrodes electroplate under continuous DC, so firmware should pulse VCC only when sampling." The board wires the module's VCC to the 3V3 plane (J4 pin 1, shared with the temp probes) — not pulsable as wired. IO5/IO16/IO18/IO23 are unconnected and the module load is a few mA. Open decision: a GPIO-fed sensor supply, or revise the bom.md instruction to match the board.
   **Resolved 2026-07-12:** J4 grew to 7P — pin 7 is IO23, the module's switched VCC (GPIO-sourced, driven only while sampling). Room, at unchanged board outline (85.05 × 72.85): the north row swept west 2.75 (J5/J6/J13/J8; SW1/SW2 rotated pads-N/S at y 32.75 with signal/GND on fresh diagonals; R18 west 1.4; R19 to the U2/U11 channel at (-20.7, 26.67) rot 270), the east column climbed (J10 +2.90, J2 +2.83, J1 +2.73), and J9/J7 slid east 2.5 behind the grown J4. All six original J4 barrels kept their exact x (the 7P footprint numbers from the east; the label list appends). The IO23 haul rides the far-west flank on the bottom — through the antenna-keepout column x −67.3, the flank Q2's EN reach rides on top; radio unused — and ends at the new barrel with no closing via. Re-authored in copper: SW1's boot line (via the J5 GND/V5 ring channel), SW2's reset drop (the C21 pad channel), R18→Q2.E (west side), IO2's crossing (bottom at y 20.4, up IO2's own barrel column), GPB0→RB1's descent (east of J9's moved escape channel), J6's staircase lanes (renested west-going), J1.OUT7/J2.OUT2 (hook east of their riser walls). Gates 11/11 after the change; 116 pcbPath, 100 % hand-routed; MH1's washer annulus stays clear (nearest new copper r 3.78). `esp32-pinout.mmd`, `esp32-scope.md`, `ac-wiring-schedule.md` J4 + SIG-9, `cable-assemblies.md`, `assembly/wiring.md`, and `bom.md:59` carry the pin. J4 and J7 now share the 7P housing — item 5's label/colour mitigation surface extends to the pair (the SENSORS loom seated in J7 lands 3V3/V5 on MCP GPB pins).
5. **Misplug matrix.** Six XH-4P connectors (J3, J5, J8, J9, J11, J13). J3/J5/J11 share the GND, V5, sig, sig pin order; J8 is GND, 3V3, sig, sig; J9 is B, A, GND, V12; J13 carries four driver outputs and no supply. The PUMPS loom seated in J8 puts a motor coil across 3V3/GND; in J5, across two GPIOs. The DISPLAY loom is the one whose power pins land on signals in every wrong socket. Loom labels + housing colour are the current mitigation surface.
6. **MCP23017 /RESET tied high.** No hardware reset path to the expanders; bus-wedge recovery is SCL clock-out from the ESP (firmware-side).
7. **Deferred-item state** (deferrals recorded in `pcba/README.md` scope):
   - *Gas interlock*: the `pcba.tsx` gas block names the 74LVC1G08 gate and the two bench polarities it waits on; no footprint is reserved, so landing it is a board revision, not a stuffing option.
   - *Input protection*: no fuse, PTC, TVS, or reverse element exists between J10 and the parts the J10 comment names as the reverse-polarity casualties (C3, the bucks, the drivers).

## Power arithmetic

- **12 V supply**: IRM-90-12ST, 6.7 A. DC-4 board tally ~3.3 A (pumps priming + 3 valves + fan). The SeaFlo diaphragm pump (~5 A, `ac-wiring-schedule.md:77`) parallels the board on relay #2 — coincident total ≈ 8.3 A. `power.mmd` carries the refill interlock (relay #2 off during dispense) that keeps the sum inside the supply; it is a firmware invariant with no hardware backstop. The 4.3B config display's 12 V draw (through J9) appears in no tally.
- **5 V rail** (K7805, 2 A): documented loads are the two relay coils (~140 mA); no repo figure exists for the MQ-6 heater or the faucet display, and the AMS1117's 3V3 load sits on top. Worth measuring both unknowns at bring-up and recording the rail budget in `power.mmd`.
- **U4 during 3-valve states**: the truth-table maximum is 3 simultaneous valves, all on MANIFOLD A/U4 (fill-hopper, clean-water-fill, air-purge states). 3 × 0.46 A cold × Vce(sat) ≈ 1.2 V ≈ 1.7 W in one SOIC-18, settling toward ~0.9 W as coils warm to ~0.3 A; at θJA ≈ 60–70 °C/W that is a 55–115 °C rise while the state holds. Fill-state duration is not documented. Worth a U4 temperature measurement during a hopper fill at bring-up.

## Firmware ↔ board

`firmware/src/main.cpp` (env `esp32dev`) targets the L298N under-sink prototype — its header says so (`main.cpp:16-18`). Against this board:

- Pins agreeing: **IO21/IO22 (I²C) only.**
- Prototype outputs IO5/IO18 land on board-unconnected pins; board peripherals IO2, IO14, IO36, IO39 have no firmware.
- Conflicting roles on 12 pins (board → firmware): IO33 faucet TX → pump PWM; IO25 flow → pump dir; IO26 1-wire → pump dir; IO27 backflow → clean solenoid; IO17/IO4 pump INs → solenoid/valve; IO19 relay → pump PWM; IO15/IO12 LEDs → flow input + config TX / valve PWM; IO13 buzzer → input; IO32/IO34/IO35 roles shifted.
- Prototype-internal: GPIO 15 is defined as both `FLOW_PIN` (INPUT_PULLUP + ISR) and `CONFIG_TX_PIN` (Serial1 TX); both are configured in `setup()`. `firmware/README.md:81-82` lists both.
- No firmware exists for: MCP23017 banks (valves, reeds, CLO/CHI — including the GPPU enables `pcba.tsx` requires on unused GPB inputs), DRV8870 single-IN drive, 1-wire family-code probes (0x28 tank / 0x10 coil), gas AOUT/DOUT, relays, status LEDs, MLT-5020 buzzer, backflow.
- Constraints recorded only in prose that a port encodes: ≤3-valve simultaneity ("firmware must not drive a full manifold simultaneously", `ac-wiring-schedule.md:84`), the refill interlock (`power.mmd`), the GPPU requirement (`pcba.tsx` MCP block). The prototype's `analogWrite` (~1 kHz) is in the audible band on a motor; the DRV8870 accepts PWM to 100 kHz.

## Docs ↔ board

Rows describing a different board state than `f9355cc7`:

- `pcb/pcba/README.md:39`: "3V3 and 5 V both made on-board (K7803 / K7805 switching bucks)" — the board makes 3V3 with the AMS1117 LDO (U9) off the K7805's 5 V.
- `pcb/pcba/jlcpcb-parts.md`: J9 listed as XH 3P `C5374805` (board: 4P `C5359632`, B/A/GND/V12); a "J12 — PROG" row (no J12 exists; programming is J14 USB-C); buzzer "tone on IO4" (IO13); U1 "placed rot 180" (rot 0); J10 described on the north edge at y=30.39 with pin1 east (east edge at (12.35, −24.4), pin1 south); a maze-router paragraph (every signal is pcbPath); no row for D2 (red KT-0603R, `C2286`).
- `ledger/bom.md`: §1 lists the module-era electronics (DevKitC, DIN breakout, L298N-class stack); `:99` relays "GPIO 17"/"GPIO 16" (board: IO19/IO2); `:192` a DIYables piezo module "GPIO 4 … plugs into the carrier at U8" (board: MLT-5020 + Q1 on IO13, no carrier); `:59` backflow "GPIO 13" (board: IO27).
- `assembly/electronics-shelf.md` + `assembly/firmware-and-commissioning.md`: `relay_diaphragm_gpio` / `gpio_relay2` = 23 (board: IO2).
- `pcb/pcba/esp32-scope.md:40`: J14 "north edge … opening flush to the board edge" — the opening is flush to the **west** edge (footprint rotation math and the render agree).

## Checks — what runs, what doesn't

- On save: `render-board.ts` → the seven audits in `pick-data.ts` (clearance, connectivity, footprint, connector, ampacity, cap, fab stats) → scorecard. `scorecard.ts:9-13`: a failing gate is a red build "*(once gating is turned on)*" — `gatesPass` prints and gates nothing today.
- By hand only: `silk-audit.py`, `part-orientation-audit.py`, `trace-check.py`, `topreach.py`, `check_pinmap.py`. None appear in `package.json`, `.githooks/pre-commit` (which rebuilds the GLB), or CI.
- `check_pinmap.py:57` parses board GPIOs with `\.U1[AB]? > \.IO(\d+)`; the board's traces are written `from="U1.IO25"` → **"board GPIOs in use: 0"** and 22 false "documented but NOT used" lines around the 6 real drift hits. Its cross-table also expects `label="SCREEN"` (board: `DISPLAY`) and `\.U8 > \._NEG` (board: `from="Q1.C" to="U8._NEG"`), and the DS18S20 BOM row has no CROSS/NO_PIN entry.
- Worth wiring into `.githooks/pre-commit` alongside the GLB rebuild: the two Python audits, a `gatesPass` hard-fail, and a repaired `check_pinmap.py`.
- Properties no script measures (this pass hit the first): copper under fastener heads, cap voltage-rating vs. rail, Z-height/mating clearance (all body audits are XY), paste layer, CPL rotation vs. JLCPCB's datum (the imports are JLCPCB's own footprints; the order-preview render is the existing check).
- Stale artifacts: `out/_en.tmp.*`, `out/_step*.log`, and root `.diag.circuit.json` / `.verify.circuit.json` predate the current board.

## Ordering / first-article / bench-verify

- Fab options: 4-layer, 1 oz outer (the ampacity rules assume it), **via covering: epoxy filled & capped (POFV)** — every pad-via is via-in-pad (`plane-stitching.md:79`). THT assembly for the 8 through-hole parts. Note to fab: the WROOM antenna overhangs the west edge ~6 mm and the USB-C opening is flush to the same edge — panel rails belong on the other edges.
- Stock rows that were shallow at their last check: C3 470 µF (**91** on 2026-06-27), COS13487 (~530 on 2026-07-03; THVD1426DR `C5215921` is the named drop-in), J1 9P wafer (~380), DS3231 (335).
- First-article visual: BT1 `+` post at the silk `+`; C3 `+` west; D2–D6 anodes west (at the resistors); D1 seating; J10 GND south / V12 north against the loom.
- Bench-verify list (items source review cannot settle): relay-module trigger polarity and 3.3 V drive margin (boot-safety assumes the opto LED load holds IO2 low); MQ-6 DOUT polarity (input to the deferred interlock); DIGITEN flow output stage (finding 3); COS13487 DI behaviour while the ESP is in reset (bus idle state); solenoid hold current (`ac-wiring-schedule.md:84` carries 0.3–0.46 A as "measure at bring-up").

## What this snapshot is NOT

- Not a fix list that has been executed — every finding above is open as of this writing.
- Not the board's requirements — that's `pcb/pcba/requirements.md` and its scorecard.
- Not maintained going forward. **Re-running this audit produces a fresh dated snapshot rather than editing this one.**
