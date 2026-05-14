# Flavor Reservoir Level Sensing

Reed-and-float level sensing for each flavor reservoir, following the same architecture as the carbonator vessel ([future.md](../../../future.md) "Level sensing" section) but with **10 reed switches per reservoir** instead of 2, for ~5-serving-step granularity over the usable fill range.

## Why this approach

Density-independent, mechanically overfill-safe, zero electrical penetrations of the reservoir, reuses the carbonator's parts pattern, and skips the entire optical/ToF complexity (FoV math, float-top reflectivity, dark-syrup absorption). Precision is coarser than load-cell or ToF — each reed represents ~10% of usable volume ≈ ~5 servings of 12 oz soda at 1:20 ratio — but adequate for the customer-facing UX: servings-remaining display, refill prediction, overfill safety, low-fill warning. The losses (per-dispense ratio verification, sub-mL/day leak detection, continuous level display) are telemetry / preventive-maintenance benefits, not primary-UX benefits.

## Architecture

**Inside the reservoir:**

- A vertical 4 mm OD PETG **strut**, integral to the reservoir BODY, anchored in the wedge at `(x = ±88, z = -45)` — the −Z half of the reservoir, opposite the bulkhead pocket (which lives on the +Z half at z=28..64). Extends upward through the cavity to a slip-fit register pocket cut into the cap's base plate. Matches the carbonator's pattern (rod welded to the bottom plate, captured at the top by a register). Mechanically stiffer than a one-end-cantilever cap-mounted strut. Specified in [`generate_step_cadquery.py`](generate_step_cadquery.py) — `STRUT_POSITION_X`, `STRUT_POSITION_Z`, `STRUT_DIAMETER`, `STRUT_BOTTOM_Y`, `STRUT_REGISTER_DIAMETER`, `STRUT_REGISTER_DEPTH`. The cavity at z=−45 is ~38 mm wide (vs ~24 mm at z=0), giving generous clearance for the donor donut float regardless of its precise OD.
- A small **magnetic float** sliding on the strut. Donor is the DEVMO MINI float switch (Amazon B07T18PGJ4) already in the BOM for the carbonator — harvest the donut, reuse its ferrite magnet. The carbonator pairs this donut with a 3.175 mm SS rod; the 4 mm PETG strut is the same family of fit, comfortably inside the wider cavity at z=−45 where sliding clearance is the dominant constraint, not a tight hole tolerance.

**Outside the reservoir:**

- A vertical **printed PETG reed-holder strip** carrying 10 reed switches at ~17 mm pitch in press-fit pockets. The strip sits in a **full-height vertical channel** cut through the bag_pocket_shell's far ±X wall at z=−45 — a single 15-mm-wide rectangular slot from floor to wall top. The strip slides into the channel from the outer-foam side before the body pour. Reeds are individually wired (no custom PCB) — 22 conductors (20 reed signals + 2 commons across the two reservoirs) routed up out of the bag pocket.
- The strip is **foam-encapsulated** during the body pour: foam flows through the channel from both the outer foam zone and the bag pocket side, embedding the strip. Same retention principle as the carbonator's reeds — sealed glass tubes inside cured foam, robust for the 10-year design life.
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

The reed strip sits IN the channel (not on either face of the wall), so the reed sensors land roughly at the wall's mid-thickness in x. Path from the float's centered magnet (donor donut OD ~8 mm, magnet outer surface at strut + ~4 mm) to the reed sensor crosses the reservoir wall (4 mm) + the cavity-side air gap (~0.5 mm) + roughly half a reed body (~1.5 mm) ≈ **~6 mm**.

**Honest signal-strength numbers** for the donor ferrite donut (~8 mm OD × 4 mm ID × 2 mm thick, Br ≈ 0.3 T):

| Distance | Field on axis (approx) | Reed pull-in needed |
|---|---|---|
| ~4 mm (strip flush with reservoir wall's outer face) | ~150–200 gauss | ~60–100 gauss — comfortable margin |
| ~6 mm (strip centered in the channel — current spec) | ~70–100 gauss | ~60–100 gauss — adequate margin |
| ~7.5 mm (strip on the wall's outer face, no channel) | ~40–60 gauss | ~60–100 gauss — marginal |

Cutting the channel through the wall (rather than mounting the strip on the wall's outer face) gets us into the adequate-margin range without a neodymium upgrade. Same magnet as the carbonator. One SKU saved. If the channel-centered position turns out borderline in practice, the strip can be pushed cavity-side within the channel (toward the 4 mm path) or the reservoir wall can be locally thinned at the strip's z range — both are bounded follow-ups.

## GPIO budget

10 reeds × 2 reservoirs = **20 input GPIOs needed** for the flavor reservoir level sensing alone.

The current ESP32 plan ([`../../../wiring/esp32-pinout.mmd`](../../../wiring/esp32-pinout.mmd)) routes 12 solenoids through one MCP23017 (16 channels, 4 currently spare). 20 new inputs exceed those 4 spare bits. Two viable additions:

- **Second MCP23017** on the same I²C bus (different address, e.g., 0x21 vs 0x20). Adds 16 channels — 20 needed leaves 12 spare for headroom. ~$13/build.
- **74HC165 shift-register chain** (3 × 8-bit). Cheaper (~$2 in parts), three-wire SPI-ish interface, no I²C address pressure.

Either works. MCP23017 is the path-of-least-resistance because the I²C library and the existing MCP23017 driver are already in the firmware.

## Parts (per build)

Per-build additions for the flavor-reservoir level sensing are tracked in [`../../../bom.md`](../../../bom.md) §12 "Level sensing":

- **20 Gebildet reed switches** (B0CW9418F6) — same SKU as the carbonator's 2 reeds; 4 × 6-pack covers 22 reeds (the 2 carbonator + 20 flavor) with 2 spares per build.
- **2 printed PETG reed-holder strips** — included in §7 print mass (no separate filament line). Geometry: thin vertical strip with 10 press-fit reed pockets at 17 mm pitch, sized to slide into the bag_pocket_shell's channel from the foam-zone side.
- **1 second MCP23017** GPIO expander (B07P2H1NZG) — same SKU as the existing expander, second instance at I²C address 0x21.
- **Float**: each reservoir reuses one DEVMO MINI float (B07T18PGJ4) directly — donor donut harvested, ferrite magnet kept (no neodymium upgrade needed once the reed strip moves inside the bag pocket). The carbonator's existing 1 unit becomes 3 units per build (1 carbonator + 2 reservoirs).
- **Wiring**: ~22 conductors of ribbon or pre-crimped silicone-insulated wire (20 reed signals + 2 commons), routed from the foam-shell exit to the electronics shelf. 40 hand-solder joints per build (20 reeds × 2 leads each); could be replaced with a custom JLCPCB in a future revision if labor cost matters.

## Calibration

Each reed's trigger position is set by where it sits in the printed PETG holder strip and where the strip sits vertically in the foam-shell channel. The 10 reeds span the float's useful Y range with one reed per 10% of usable volume.

The firmware reports level as the index of the highest-triggered reed (counting from the bottom), giving a step-function readout that maps directly to the "X servings left" UI.

## Service

Reed strip is foam-encapsulated and not field-serviceable without cutting foam. The expected failure mode (reed glass tube fractures, contact corrodes) is well below the appliance's 10-year design lifetime for sealed glass reeds in a dry foam-bonded environment, so this is acceptable.

The internal strut is integral to the cap and replaceable as a unit with the cap-plus-strut print if ever needed (cap is removable, six M3 × 12 SHCS + gasket + filter). The float is reachable by lifting it off the strut once the cap is removed.

## Open items

- **Printed reed-holder strip CAD.** A new file under `printed-parts/cold-core/` describing the strip geometry: 10 press-fit reed pockets at 17 mm pitch in a vertical PETG strip sized to fit the foam-shell channel. Not yet written.
- **Wire routing exit.** 11-wire harness per reservoir exits via the existing 6.5 mm reservoir-line pass-through, or a small dedicated hole if that pass-through is too crowded. TBD which.
