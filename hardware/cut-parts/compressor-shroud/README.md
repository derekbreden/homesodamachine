# Compressor Shroud

Sheet-metal shroud that drops over the compressor from above — a 5-sided open-bottom box (top panel + four walls bent down), SendCutSend laser-cut and bent. The compressor sits on the printed enclosure floor; the open bottom clears its feet and the refrigerant/process stubs.

## What it covers

**Inside:** the compressor body (~[95 mm](COMP_OD) OD × ~[110 mm](COMP_H) tall, [100 W](COMP_CLASS_W)-class hermetic), its terminal block + clip-on PTC start relay/overload module ([140](PTC_TEMP_LOW)–[150 °C](PTC_TEMP) in normal use), and the [18 AWG](AC_AWG) wire stub from the terminals to the AC pass-through.

**Outside:** the condenser fan ([12 V](FAN_V) DC), the electronics shelf, the AC distribution block — everything else.

## Dimensions

Interior **[130 mm](INT_W) (W) × [175 mm](INT_D) (D) × [150 mm](INT_H) (H)**; outer [133 mm](OUT_W) × [178 mm](OUT_D) × [151.5 mm](OUT_H) (each wall and the top add one wall thickness). ≥[10 mm](TB_CLEARANCE) clearance to the terminal block.

Face names used below follow the part as modelled: the **back face** is a 130 × 150 wall (normal along depth); the **left face** is a 175 × 150 wall (normal along width).

## Material

**[0.059"](WALL_IN) G90 hot-dipped galvanized steel** ([1.499 mm](WALL_MM)). [10-year](DESIGN_LIFE) design life. Inside bend radius [0.063"](BEND_R_IN) ([1.6 mm](BEND_R_MM)), K-factor [0.36](K_FACTOR) — SendCutSend's published G90 0.059" gauge spec, so the flat develops to the intended interior.

## Penetrations

Six laser-cut holes — three pass-throughs, an earth-bond point, and two mounting holes:

| # | Hole | Face | Purpose |
|---|---|---|---|
| 1 | [7/8"](PANEL_HOLE) (Ø[22.22 mm](AC_HOLE_MM)) | back, centered H + V | 120 V AC cable — 3-conductor [18 AWG](AC_AWG) SJOOW (switched H + N + G). SS 1/2" NPT cable gland (B0F2HP5FWB), [6](GLAND_LOW)–[12 mm](GLAND_HIGH) clamping range. |
| 2 | Ø[8 mm](CU_HOLE) | left | refrigerant discharge — clearance for [1/4"](CU_OD) OD ACR copper, on the condenser's own inlet pick |
| 3 | Ø[8 mm](CU_HOLE) | front | refrigerant suction — clearance for [1/4"](CU_OD) OD ACR copper, on the cold core's evaporator-outlet station |
| 4 | Ø[6 mm](GND_HOLE) | back, beside the AC hole | earth bond — ring terminal to the ground bus (wiring AC-6) |
| 5 | 2× Ø[4.5 mm](MOUNT_HOLE) | left + right, near the base | mounting — fastens the shroud to the enclosure floor |

The AC hole is centered on the back face. **The two copper holes take different faces, because the machine mates a different body against each:** the shroud's left face stands against the condenser and its front face against the cold core, so each stub is made up across a plane the two bodies already share and no copper is drawn outside the shroud on either. The discharge is centered vertically on the left face at a quarter point of its depth; the suction stands on the cold core's west port lane, at the height the evaporator's outlet crosses the core's own front wall. `front_half.refrigerant_joints()` measures both joints at every build of the machine and fails the build if either opens.

## Bend relief

A square relief notch at each corner where two bends meet, centered on the bend-line intersection so it serves both bends. Depth 4.6 mm past each bend line (SendCutSend's minimum is bend radius + thickness + 0.020" = 3.6 mm); width 9.2 mm (minimum is 50% of thickness). Required for the flat to pass review — see [SendCutSend's bend-relief requirements](https://sendcutsend.com/faq/what-are-your-bend-relief-requirements/).

## Grounding & mounting

The appliance enclosure is all plastic — there is **no metal chassis**. This shroud is an internal metal cover over the compressor's 120 V terminals; the user-facing barrier is the plastic enclosure, not this part.

The shroud bonds to earth at the Ø[6 mm](GND_HOLE) hole on the back face — a ring terminal to the electronics-shelf ground bus, run AC-6 in [`/hardware/assembly/wiring.md`](/hardware/assembly/wiring.md). Exposed metal parts bond single-point to the C14 earth pin; the shroud is one of them.

It mounts by dropping over the compressor from above and fastening through the two Ø[4.5 mm](MOUNT_HOLE) holes near the base of the side walls to the enclosure floor.

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
- Max 4-sided box flange height with hardware: [3.00"](MAX_BOX_IN) ([76 mm](MAX_BOX_MM)). This part's walls are 150 mm with no inserted hardware; the order below passed review.

**Hole-to-bend distance:** ≥1.5×T + R = [0.15"](HTB_IN) ([3.8 mm](HTB_MM)).

**Hardware insertion** (PEM nuts, studs, standoffs): SendCutSend min part size [1" × 1.5"](HW_MIN) — relevant only if the earth-bond stud above is added.

**Tapping:** [M3 × 0.5](TAP_THREAD) supported at this thickness.

## SendCutSend order

Quoted 2026-06-03: **$278.30 for qty 10** ($27.83/part) — `compressor-shroud-flat.dxf` uploaded with four 90° "down" bends.

## Files

- `compressor_shroud.py` — parametric generator (imports its dimensions from `_compressor_shroud_dimensions.py`); builds the STEP, the flat DXF, and the JSON sidecars.
- `compressor-shroud.step` — formed shroud, for the viewer and reference.
- `compressor-shroud-flat.dxf` — flat pattern: cut outline + holes on layer 0, the four bend lines dashed on a separate BEND layer.
- `compressor-shroud.step.json`, `compressor-shroud-flat.dxf.json` — material/thickness sidecars.

Run: `tools/cad-venv/bin/python compressor_shroud.py`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/cut-parts/compressor-shroud/_compressor_shroud_dimensions.py`
