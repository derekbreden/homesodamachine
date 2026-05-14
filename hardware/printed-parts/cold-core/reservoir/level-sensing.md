# Flavor Reservoir Level Sensing

Reed-and-float level sensing for each flavor reservoir, following the same architecture as the carbonator vessel ([future.md](../../../future.md) "Level sensing" section) but with **10 reed switches per reservoir** instead of 2, for ~5-serving-step granularity over the usable fill range.

## Why this approach

Density-independent, mechanically overfill-safe, zero electrical penetrations of the reservoir, reuses the carbonator's parts pattern, and skips the entire optical/ToF complexity (FoV math, float-top reflectivity, dark-syrup absorption). Precision is coarser than load-cell or ToF — each reed represents ~10% of usable volume ≈ ~5 servings of 12 oz soda at 1:20 ratio — but adequate for the customer-facing UX: servings-remaining display, refill prediction, overfill safety, low-fill warning. The losses (per-dispense ratio verification, sub-mL/day leak detection, continuous level display) are telemetry / preventive-maintenance benefits, not primary-UX benefits.

## Architecture

**Inside the reservoir:**

- A vertical 5 mm OD PETG **strut** integral to the reservoir cap, hanging down from the cap's bottom face by 185 mm. Specified in [`generate_step_cadquery.py`](generate_step_cadquery.py) — search for `STRUT_POSITION_X` / `STRUT_LENGTH`. Position: `(x = ±88, z = 0)` in the reservoir frame, mirrored across x=0 for the two reservoirs.
- A small **magnetic float** sliding on the strut. Equivalent to the carbonator's harvested float from the DEVMO MINI float switch (Amazon B07T18PGJ4), but with a **neodymium ring magnet** in place of (or in addition to) the donor's ferrite donut. The reed-magnet separation is larger here than in the carbonator (~6.5 mm of PETG + ~3 mm of air gaps vs the carbonator's 1.65 mm SS wall), so the magnet field needs to be stronger to ensure reliable reed triggering. Suggested magnet: neodymium ring ~10 mm OD × 5 mm ID × 3 mm thick, N42 or N52, axially magnetized, with a food-safe coating (nickel or PTFE).

**Outside the reservoir:**

- A vertical **reed-switch strip** mounted on the OUTSIDE of the bag_pocket_shell's far +X wall (see [`../foam-shell/`](../foam-shell/)). The strip is a small custom FR4 PCB (~15 mm wide × ~170 mm tall) carrying 10 reed switches at ~17 mm pitch, with a JST-XH header at one end for the 11-wire harness (10 reeds × signal + common return).
- The strip is **attached to the bag_pocket_shell with adhesive or a small printed bracket** before the body foam pour, then **foam-encapsulated** during the pour. Same approach as the carbonator's reeds — sealed glass tubes inside foam, robust for the 10-year design life.
- **Wiring exit**: the 11-wire harness exits through the same 6.5 mm pass-through used for the reservoir line (`Reservoir line (+X)` / `Reservoir line (−X)` in the foam-shell penetration table, [`../foam-shell/README.md`](../foam-shell/README.md) "Penetrations"). If that pass-through is too crowded with the reservoir tube plus the reed harness, a dedicated small (~3 mm) hole can be added in a future foam-shell revision.

## Reed pitch and what it gets you

Useful Y range for the float on the strut: ~40 mm above the floor (above the wet slope max) to ~210 mm (just below the cap) = ~170 mm of float travel.

| Reeds | Pitch (mm) | Servings per step |
|---|---|---|
| 8 | ~22 | ~6 |
| 10 | ~17 | ~5 |
| 12 | ~14 | ~4 |

10 reeds at 17 mm pitch is the working spec. 12 is feasible if we accept tighter mounting. Below 8 starts to make the "servings remaining" display feel chunky.

## Magnet–reed signal-path geometry

Working from the reservoir's +X face outward to the reed:

| Layer | Thickness |
|---|---|
| Reservoir wall (PETG, +X far face) | 4 mm |
| reservoir_clearance gap | 0.5 mm |
| bag_pocket_shell far +X wall (PETG) | 2 mm |
| Reed-to-wall standoff (adhesive / bracket) | ~1 mm |
| **Total magnet-to-reed separation** | **~7.5 mm** |

At that separation, a ferrite donor donut (like the carbonator's harvested float) is marginal for reliable triggering. A neodymium N42/N52 ring at the recommended size produces ~80–150 gauss at 7.5 mm — well above typical reed pull-in thresholds (~30–50 gauss). The carbonator's 1.65 mm SS wall is a much easier magnetic path, but the flavor reservoir's all-PETG stack works fine with the upgraded magnet.

## GPIO budget

10 reeds × 2 reservoirs = **20 input GPIOs needed** for the flavor reservoir level sensing alone.

The current ESP32 plan ([`../../../wiring/esp32-pinout.mmd`](../../../wiring/esp32-pinout.mmd)) routes 12 solenoids through one MCP23017 (16 channels, 4 currently spare). 20 new inputs exceed those 4 spare bits. Two viable additions:

- **Second MCP23017** on the same I²C bus (different address, e.g., 0x21 vs 0x20). Adds 16 channels — 20 needed leaves 12 spare for headroom. ~$13/build.
- **74HC165 shift-register chain** (3 × 8-bit). Cheaper (~$2 in parts), three-wire SPI-ish interface, no I²C address pressure.

Either works. MCP23017 is the path-of-least-resistance because the I²C library and the existing MCP23017 driver are already in the firmware.

## Parts (per build)

Per-build additions for the flavor-reservoir level sensing are tracked in [`../../../bom.md`](../../../bom.md) §12 "Level sensing":

- **20 Gebildet reed switches** (B0CW9418F6) — same SKU as the carbonator's 2 reeds; 4 × 6-pack covers 22 reeds (the 2 carbonator + 20 flavor) with 2 spares per build.
- **2 neodymium ring magnets** — one per reservoir's float.
- **2 reed-PCB strips** — custom JLCPCB or equivalent, ~10 reeds at 17 mm pitch.
- **1 second MCP23017** GPIO expander (B07P2H1NZG) — same SKU as the existing expander, second instance at I²C address 0x21.
- **Float**: each reservoir reuses one DEVMO MINI float (B07T18PGJ4) for the plastic donut body, with the donor ferrite replaced by the neodymium ring above. The carbonator's existing 1 unit becomes 3 units per build (1 carbonator + 2 reservoirs).
- **Wiring**: ~22 conductors of ribbon or pre-crimped silicone-insulated wire (20 reed signals + 2 commons), routed from the foam-shell exit to the electronics shelf.

## Calibration

Each reed's trigger position is set by where it sits on the PCB strip and where the strip mounts on the bag_pocket_shell wall. The strip's vertical position relative to the float's strut range is the calibration variable. With the strip top aligned to the cap-side face of the bag_pocket_shell wall and the strip bottom aligned ~40 mm above the bag_pocket_shell floor, the 10 reeds span the float's useful Y range with one reed per 10% of usable volume.

The firmware reports level as the index of the highest-triggered reed (counting from the bottom), giving a step-function readout that maps directly to the "X servings left" UI.

## Service

Reed strip is foam-encapsulated and not field-serviceable without cutting foam. The expected failure mode (reed glass tube fractures, contact corrodes) is well below the appliance's 10-year design lifetime for sealed glass reeds in a dry foam-bonded environment, so this is acceptable.

The internal strut is integral to the cap and replaceable as a unit with the cap-plus-strut print if ever needed (cap is removable, six M3 × 12 SHCS + gasket + filter). The float is reachable by lifting it off the strut once the cap is removed.

## Open items

- **Specific magnet SKU.** Need to pick a neodymium ring magnet that's Prime-available, food-safe-coated, and fits the float's center hole. Placeholder above.
- **Reed PCB design.** ~$10/build at JLCPCB once finalized; geometry should be a thin rectangular strip with 10 reed footprints at 17 mm pitch, two mounting holes (for an optional printed bracket), and a 4-pin or 11-pin JST connector at the top end.
- **Reed-strip mounting bracket.** Decide between adhesive (simpler) or a small printed PETG bracket that hooks onto a feature in the bag_pocket_shell's far +X wall (would need a small CAD addition to the foam-shell).
- **MCP23017 wiring update.** Add the second expander to [`../../../wiring/esp32-pinout.mmd`](../../../wiring/esp32-pinout.mmd) and update the wiring schedule.
