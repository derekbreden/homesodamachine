# Compressor Shroud

Sheet-metal shroud over the compressor terminal block and PTC relay/overload module. SendCutSend laser-cut + bent.

## What's inside vs outside the shroud

**Inside:**
- Compressor body
- Compressor terminal block + clip-on PTC start relay/overload module ([140](PTC_TEMP_LOW)–[150 °C](PTC_TEMP) in normal use)
- The wire stub from the terminals to the AC pass-through grommet (a few cm of [18 AWG](AC_AWG))
- Refrigerant line stubs (suction, discharge, process tube) exit through the open bottom

**Outside:**
- Teyleten relay #1 (electronics shelf)
- Condenser fan motor — [12 V](FAN_V) DC brushless axial on the side-to-side intake → condenser → exhaust airflow path
- AC distribution block (electronics shelf)
- Everything else

## Shape concept

A **5-sided open-bottom box** that drops over the compressor from above. Top panel + 4 side walls. Compressor sits on its [M5](FOOT_THREAD) mounting feet on the printed enclosure floor; refrigerant tubes exit downward/sideways.

Single SendCutSend part, bent on 4 sides.

## Dimensions

**Status: TBD.** The donor compressor (HD48Y11 from the generic ice-maker unit, or the equivalent in the Frigidaire EFIC117-SS) needs to be measured before final dimensions are committed. Per [`/hardware/harvested/ice-maker/README.md`](/hardware/harvested/ice-maker/README.md) "Open items": *Physical dimensions of compressor + condenser pair, for enclosure layout* is still pending.

Working assumptions:

- Compressor body: ~[95 mm](COMP_OD) OD × ~[110 mm](COMP_H) tall ([100 W](COMP_CLASS_W)-class hermetic)
- Terminal block + PTC module envelope: ~[50 mm](TB_W) wide × ~[40 mm](TB_H) tall × ~[30 mm](TB_STANDOFF) radial standoff above the terminal pins
- Internal clearance to terminal block: ≥[10 mm](TB_CLEARANCE) on all sides

Working envelope:

- Outer dimensions: ~[130 mm](OUTER_X) (X, depth into appliance) × ~[130 mm](OUTER_Y) (Y, width across appliance) × ~[100 mm](OUTER_Z) (Z, vertical height above floor)
- Wall thickness: [0.059"](WALL_IN) ([1.5 mm](WALL_MM))
- Internal headroom over compressor: ≥[20 mm](HEADROOM)
- Side wall flange height: [90](FLANGE_LOW)–[100 mm](FLANGE_HIGH)

## Material

**[0.059"](WALL_IN) G90 hot-dipped galvanized steel.**

[10-year](DESIGN_LIFE) design life.

Cost: ~[$5](COST_LOW)–[$10](COST_HIGH)/part at qty [5](QTY_LOW)–[10](QTY_HIGH) from SendCutSend.

## Penetrations

| # | Hole | Purpose |
|---|---|---|
| 1 | [1/2"](PANEL_HOLE) panel hole, one side wall | AC cable pass-through (3-conductor: switched H + N + chassis G, [18 AWG](AC_AWG) SJOOW bundle) from Teyleten relay #1 on the electronics shelf to the compressor terminal block. Heyco SB-500-6 snap bushing (B01LPBST9G), [5.6](BUSHING_LOW)–[6.4 mm](BUSHING_HIGH) cable-OD range, fits [18 AWG](AC_AWG) SJOOW (~[6.4 mm](AC_OD) OD). |
| 2 | 2× [M3](TAB_THREAD) mounting tab through-holes at base flange | Anchor to the compressor's [M5](FOOT_THREAD) mounting feet using [M5](FOOT_THREAD)→[M3](TAB_THREAD) step-down adapter washers. |
| 3 | Ø ~[6 mm](GND_HOLE) chassis ground stud hole | PEM stud for the chassis bonding wire (run AC-6 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md)). |

No ventilation holes.

## SendCutSend specs

For [0.059"](WALL_IN) G90 galvanized steel:

**Laser cutting:**
- Cut tolerance: [±0.005"](CUT_TOL)
- Min hole diameter: [0.022"](MIN_HOLE_IN) ([0.56 mm](MIN_HOLE_MM))
- Min hole-to-edge: [0.02"](MIN_HE_IN) ([0.51 mm](MIN_HE_MM))
- Min part size: [0.25" × 0.375"](MIN_PART)

**Bending:**
- Min bend part size: [0.375" × 1.5"](MIN_BEND_PART)
- Max bend length: [44"](MAX_BEND_LEN)
- Min flange length (after bend, [90°](BEND_ANGLE)): [0.311"](MIN_FLANGE_IN) ([7.9 mm](MIN_FLANGE_MM))
- Effective bend radius @ [90°](BEND_ANGLE): [0.063"](BEND_R_IN) ([1.6 mm](BEND_R_MM))
- Bend deduction @ [90°](BEND_ANGLE): [0.112"](BEND_DED)
- K factor: [0.36](K_FACTOR)
- Bend angle tolerance: [±1°](BEND_TOL) (bend length ≤[24"](BEND_TOL_LEN))
- Max 4-sided box flange height with hardware: [3.00"](MAX_BOX_IN) ([76 mm](MAX_BOX_MM))

**Hole-to-bend distance:** ≥1.5×T + R = [0.15"](HTB_IN) ([3.8 mm](HTB_MM)).

**Hardware insertion** (PEM nuts, studs, standoffs): SendCutSend min part size [1" × 1.5"](HW_MIN). Chassis-ground stud is a press-in PEM stud inserted by SendCutSend.

**Tapping:** [M3 × 0.5](TAP_THREAD) supported at this thickness.

## Files (planned)

- `compressor_shroud.py` — parametric flat-pattern DXF generator (ezdxf), once compressor measurements are in hand
- `compressor-shroud-flat.dxf` — generated flat pattern with bend lines marked
- `compressor-shroud-drawing.pdf` — annotated drawing showing bend angles + bend lines + grommet location, generated from CadQuery `.section()` projections

Run with `tools/cad-venv/bin/python compressor_shroud.py`.

## Open items

1. **Measure the donor compressor** — terminal block envelope, PTC module standoff, mounting foot pattern ([M5](FOOT_THREAD) thread spacing + bolt circle), body OD/height.
2. **Decide one-piece 5-sided box vs. two-piece U-channel + back-wall.**
3. **Decide the AC pass-through grommet location.**
4. **Write `compressor_shroud.py`** once items 1–3 are settled.

## Sources
[value](NAME) texts are updated by:
- `/hardware/cut-parts/compressor-shroud/_compressor_shroud_dimensions.py`
