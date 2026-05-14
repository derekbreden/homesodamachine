# Flavor Reservoir Level Sensing

Reed-and-float level sensing for each flavor reservoir, following the same architecture as the carbonator vessel ([future.md](../../../future.md) "Level sensing" section) but with **10 reed switches per reservoir** instead of 2, for ~5-serving-step granularity over the usable fill range.

## Why this approach

Density-independent, mechanically overfill-safe, zero electrical penetrations of the reservoir, reuses the carbonator's parts pattern, and skips the entire optical/ToF complexity (FoV math, float-top reflectivity, dark-syrup absorption). Precision is coarser than load-cell or ToF — each reed represents ~10% of usable volume ≈ ~5 servings of 12 oz soda at 1:20 ratio — but adequate for the customer-facing UX: servings-remaining display, refill prediction, overfill safety, low-fill warning. The losses (per-dispense ratio verification, sub-mL/day leak detection, continuous level display) are telemetry / preventive-maintenance benefits, not primary-UX benefits.

## Architecture

**Inside the reservoir:**

- A vertical 4 mm OD PETG **strut**, integral to the reservoir BODY, anchored in the wedge at `(x = ±88, z = -45)` — the −Z half of the reservoir, opposite the bulkhead pocket (which lives on the +Z half at z=28..64). Extends upward through the cavity to a slip-fit register pocket cut into the cap's base plate. Matches the carbonator's pattern (rod welded to the bottom plate, captured at the top by a register). Mechanically stiffer than a one-end-cantilever cap-mounted strut. Specified in [`generate_step_cadquery.py`](generate_step_cadquery.py) — `STRUT_POSITION_X`, `STRUT_POSITION_Z`, `STRUT_DIAMETER`, `STRUT_BOTTOM_Y`, `STRUT_REGISTER_DIAMETER`, `STRUT_REGISTER_DEPTH`. The cavity at z=−45 is ~38 mm wide (vs ~24 mm at z=0), giving generous clearance for the donor donut float regardless of its precise OD.
- A small **magnetic float** sliding on the strut. Donor is the DEVMO MINI float switch (Amazon B07T18PGJ4) already in the BOM for the carbonator — harvest the donut, reuse its ferrite magnet. The carbonator pairs this donut with a 3.175 mm SS rod; the 4 mm PETG strut is the same family of fit, comfortably inside the wider cavity at z=−45 where sliding clearance is the dominant constraint, not a tight hole tolerance.

**Outside the reservoir:**

- A vertical **printed PETG reed-holder strip** carrying 10 reed switches at ~17 mm pitch in press-fit pockets. The strip sits in a localized recess (a "bulge out") on the bag_pocket_shell's far +X wall at z=−45, INSIDE the bag pocket air space — between the reservoir's outer +X face and the bag_pocket_shell. The bulge pushes the bag_pocket_shell wall locally outward by ~3 mm to create the cavity for the strip without compressing the reservoir clearance. Reeds are individually wired (no custom PCB) — 22 conductors (20 reed signals + 2 commons across the two reservoirs) routed up out of the bag pocket.
- The strip is **press-fit into the bag_pocket_shell recess** before the body foam pour, then **foam-encapsulated** during the pour (foam fills behind the strip and bonds it into the wall). Same approach as the carbonator's reeds — sealed glass tubes inside foam, robust for the 10-year design life.
- **Wiring exit**: 11-wire harness per reservoir exits via the existing 6.5 mm reservoir-line pass-through (`Reservoir line (+X)` / `Reservoir line (−X)` in the foam-shell penetration table, [`../foam-shell/README.md`](../foam-shell/README.md) "Penetrations") or a small dedicated hole if that pass-through is too crowded.

## Reed pitch and what it gets you

Useful Y range for the float on the strut: ~40 mm above the floor (above the wet slope max) to ~210 mm (just below the cap) = ~170 mm of float travel.

| Reeds | Pitch (mm) | Servings per step |
|---|---|---|
| 8 | ~22 | ~6 |
| 10 | ~17 | ~5 |
| 12 | ~14 | ~4 |

10 reeds at 17 mm pitch is the working spec. 12 is feasible if we accept tighter mounting. Below 8 starts to make the "servings remaining" display feel chunky.

## Magnet–reed signal-path geometry

The reed-holder mount location drives the magnet-to-reed distance. Three options exist; the project's current design picks **option B** (holder inside the bag pocket air space, against the bag_pocket_shell inner face, made possible by a localized outward bulge in the wall), which is the cleanest combination of "donor donut works" and "reservoir geometry doesn't get carved."

| Option | Holder location | Path through | Distance | Donor ferrite OK? |
|---|---|---|---|---|
| A | Outside the bag_pocket_shell, foam-side | reservoir wall (4) + clearance (0.5) + bag-shell wall (2) + standoff (~1) | ~7.5 mm | Marginal |
| **B** | **Inside the bag pocket air space (bag_pocket_shell bulged out for clearance)** | **reservoir wall (4) + clearance (~0.5) + reed body offset (~1.5)** | **~6 mm** | **Yes — adequate** |
| C | B + locally thin the reservoir wall to 2 mm at the reed strip | 2 mm wall + 0.5 + 1.5 | ~4 mm | Yes — generous |

Option B requires a small foam-shell CAD change: the bag_pocket_shell's far +X wall needs a vertical "bulge out" (~3 mm outward of the wall's inner face × ~15 mm wide × ~170 mm tall) at z=−45 (matching the strut position) to make room for the printed reed-holder strip without compressing the reservoir clearance gap. The bulge displaces ~3 mm of foam locally on the outer-foam side; thermal impact is minor (the bulge is small and the outer foam zone has plenty of remaining thickness).

Option C is the fallback if option B turns out to be borderline in practice. Thinning the reservoir wall from 4 mm to 2 mm over a ~15 × 170 mm vertical strip is bounded and mechanically safe — the area is not load-bearing under the reservoir's vented service pressure.

**Honest signal-strength numbers** for the donor ferrite donut (~8 mm OD × 4 mm ID × 2 mm thick, Br ≈ 0.3 T):

| Distance | Field on axis (approx) | Reed pull-in needed |
|---|---|---|
| 4 mm (option C) | ~150–200 gauss | ~60–100 gauss — comfortable margin |
| 6 mm (option B) | ~70–100 gauss | ~60–100 gauss — adequate margin |
| 7.5 mm (option A) | ~40–60 gauss | ~60–100 gauss — at or below threshold |

So at the original 7.5 mm path the donor would have been marginal; with option B the donor ferrite donut works with adequate margin and **no neodymium upgrade is needed**. Same magnet as the carbonator. One SKU saved.

## GPIO budget

10 reeds × 2 reservoirs = **20 input GPIOs needed** for the flavor reservoir level sensing alone.

The current ESP32 plan ([`../../../wiring/esp32-pinout.mmd`](../../../wiring/esp32-pinout.mmd)) routes 12 solenoids through one MCP23017 (16 channels, 4 currently spare). 20 new inputs exceed those 4 spare bits. Two viable additions:

- **Second MCP23017** on the same I²C bus (different address, e.g., 0x21 vs 0x20). Adds 16 channels — 20 needed leaves 12 spare for headroom. ~$13/build.
- **74HC165 shift-register chain** (3 × 8-bit). Cheaper (~$2 in parts), three-wire SPI-ish interface, no I²C address pressure.

Either works. MCP23017 is the path-of-least-resistance because the I²C library and the existing MCP23017 driver are already in the firmware.

## Parts (per build)

Per-build additions for the flavor-reservoir level sensing are tracked in [`../../../bom.md`](../../../bom.md) §12 "Level sensing":

- **20 Gebildet reed switches** (B0CW9418F6) — same SKU as the carbonator's 2 reeds; 4 × 6-pack covers 22 reeds (the 2 carbonator + 20 flavor) with 2 spares per build.
- **2 printed PETG reed-holder strips** — included in §7 print mass (no separate filament line). Geometry: thin vertical strip with 10 press-fit reed pockets at 17 mm pitch, two mounting features matching the bag_pocket_shell recess.
- **1 second MCP23017** GPIO expander (B07P2H1NZG) — same SKU as the existing expander, second instance at I²C address 0x21.
- **Float**: each reservoir reuses one DEVMO MINI float (B07T18PGJ4) directly — donor donut harvested, ferrite magnet kept (no neodymium upgrade needed once the reed strip moves inside the bag pocket). The carbonator's existing 1 unit becomes 3 units per build (1 carbonator + 2 reservoirs).
- **Wiring**: ~22 conductors of ribbon or pre-crimped silicone-insulated wire (20 reed signals + 2 commons), routed from the foam-shell exit to the electronics shelf. 40 hand-solder joints per build (20 reeds × 2 leads each); could be replaced with a custom JLCPCB in a future revision if labor cost matters.

## Calibration

Each reed's trigger position is set by where it sits on the PCB strip and where the strip mounts on the bag_pocket_shell wall. The strip's vertical position relative to the float's strut range is the calibration variable. With the strip top aligned to the cap-side face of the bag_pocket_shell wall and the strip bottom aligned ~40 mm above the bag_pocket_shell floor, the 10 reeds span the float's useful Y range with one reed per 10% of usable volume.

The firmware reports level as the index of the highest-triggered reed (counting from the bottom), giving a step-function readout that maps directly to the "X servings left" UI.

## Service

Reed strip is foam-encapsulated and not field-serviceable without cutting foam. The expected failure mode (reed glass tube fractures, contact corrodes) is well below the appliance's 10-year design lifetime for sealed glass reeds in a dry foam-bonded environment, so this is acceptable.

The internal strut is integral to the cap and replaceable as a unit with the cap-plus-strut print if ever needed (cap is removable, six M3 × 12 SHCS + gasket + filter). The float is reachable by lifting it off the strut once the cap is removed.

## Open items

- **Foam-shell CAD update for the PCB recess.** The bag_pocket_shell's far +X wall needs a vertical inner-face recess (~3–4 mm deep × ~15 mm wide × ~170 mm tall) at z=−45 (aligned with the strut and float location) to make room for the reed PCB strip inside the bag pocket air space (option B in the signal-path table above). This is a small but real addition to [`../foam-shell/generate_step_cadquery.py`](../foam-shell/generate_step_cadquery.py).
- **Reed PCB design.** Custom JLCPCB. Thin rectangular FR4 strip, 10 reed footprints at 17 mm pitch, two M2 mounting holes for the printed bracket, JST-XH 11-pin connector at the top end. Wires exit upward and out the bag pocket via the cap-side seam (or the existing reservoir-line pass-through if the timing works).
- **Reed-strip mounting bracket on the bag_pocket_shell.** Project pattern strongly favors a printed feature integrated into the bag_pocket_shell CAD over adhesive — heat-set inserts and screws everywhere else in the cold core, adhesive nowhere as primary fastener. Either a printed channel that snap-retains the PCB or two screw bosses with M2 heat-set inserts.
