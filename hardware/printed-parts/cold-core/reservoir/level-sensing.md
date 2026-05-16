# Flavor Reservoir Level Sensing

Reed-and-float level sensing for each flavor reservoir, following the same architecture as the carbonator vessel ([future.md](../../../future.md) "Level sensing" section) but with **4 reed switches per reservoir** instead of 2, for ~13-serving-step granularity over the usable fill range.

## Why this approach

Density-independent, mechanically overfill-safe, zero electrical penetrations of the reservoir, reuses the carbonator's parts pattern, and skips the entire optical/ToF complexity (FoV math, float-top reflectivity, dark-syrup absorption). Precision is coarser than load-cell or ToF — each reed represents ~25% of usable volume ≈ ~13 servings of 12 oz soda at 1:20 ratio — but adequate for the customer-facing UX: a 5-state fuel-gauge display, refill prediction, overfill safety, low-fill warning. The losses (per-dispense ratio verification, sub-mL/day leak detection, continuous level display) are telemetry / preventive-maintenance benefits, not primary-UX benefits.

## Architecture

**Inside the reservoir:**

- A vertical 4 mm OD PETG **strut**, integral to the reservoir BODY, anchored in the wedge at `(x = ±88, z = -45)` — the −Z half of the reservoir, opposite the bulkhead pocket (which lives on the +Z half at z=28..64). Extends upward through the cavity to a boss on the cap's underside that the strut tip enters from below. Matches the carbonator's pattern (rod welded to the bottom plate, captured at the top). Mechanically stiffer than a one-end cantilever. Specified in [`generate_step_cadquery.py`](generate_step_cadquery.py) — `STRUT_POSITION_X`, `STRUT_POSITION_Z`, `STRUT_DIAMETER`, `STRUT_BOTTOM_Y`, `STRUT_BOSS_OD`, `STRUT_BOSS_BORE`, `STRUT_BOSS_HEIGHT`. The cavity at z=−45 is ~38 mm wide (vs ~24 mm at z=0), giving generous clearance for the donor donut float regardless of its precise OD.
- A small **magnetic float** sliding on the strut. Donor is the DEVMO MINI float switch (Amazon B07T18PGJ4) already in the BOM for the carbonator — harvest the donut, reuse its ferrite magnet. The carbonator pairs this donut with a 3.175 mm SS rod; the 4 mm PETG strut is the same family of fit, comfortably inside the wider cavity at z=−45 where sliding clearance is the dominant constraint, not a tight hole tolerance.

**Outside the reservoir:**

- A pre-soldered **column of 4 reed switches** wired to a multi-conductor cable. Each reed has both leads hand-soldered to a corresponding pair of conductors (one signal + the shared common return). The cable runs the length of the column past all four reeds. The whole assembly is rigid enough to slide into the foam-shell channel as a single pre-assembled piece — no per-reed mounting feature needed inside the cold core.
- The **foam shell carries the channel that holds the column** — no separate printed reed-holder part. The channel is a **3-walled box that extrudes OUTWARD** from the bag_pocket_shell's far ±X wall into the outer foam zone. The original wall is the channel's back / inner face; two new ±z side walls extend outward; a new outer face closes the box on the foam-zone side. The channel has two segments:
  - A **vertical segment** at the reed positions, centered on z=−45, sized to slip-fit the reed-and-wire column. Full height — top open at the wall top so the column can be dropped in from above before the cap is installed.
  - A **horizontal segment** sitting on the foam shell floor (cavity y range = `[wall_and_floor_thickness, wall_and_floor_thickness + 8]` = [2, 10]). Sitting on the floor makes the segment printable — the foam shell floor IS the channel's bottom wall, no unsupported envelope floor mid-air. Runs from the vertical channel in +Z direction along the bag-pocket far ±X wall to a **dedicated ⌀6.5 coaxial cable hole** through both the bag-pocket far ±X wall and the outer ±X shell wall, at `(y = reservoir_bulkhead_port_y = 18, z = bag_pocket_width/2 − 10)` — same y, z as the existing bulkhead tube pass-through, just on the ±X side and a few mm offset from the bulkhead's +Z hole. The cable runs at y ≈ 6 inside the channel, exits the wall opening at that y, and bends up to y = 18 inside the bag-pocket interior between exiting the wall opening and entering the cable hole.
- The column is **held mechanically** by the channel — bottom shelf catches it from below, ±z side walls constrain it laterally, the cap on top traps it from above when installed. **No foam encapsulation** — the bag pocket is an air cavity per the cold-core's overall pour architecture, so foam doesn't reach the reed column. This differs from the carbonator's reeds, which ARE foam-encapsulated because the carbonator vessel sits in the foam-poured center of the cold core.

## Reed pitch and what it gets you

Useful Y range for the float on the strut: ~40 mm above the floor (above the wet slope max) to ~210 mm (just below the cap) = ~170 mm of float travel.

| Reeds | Pitch (mm) | Servings per step |
|---|---|---|
| 3 | ~70 | ~17 |
| **4** | **~45** | **~13** |
| 5 | ~35 | ~10 |

4 reeds at ~45 mm pitch is the working spec. The customer-facing display is a 5-state fuel gauge (0, 1, 2, 3, 4 reeds triggered) corresponding to roughly empty / quarter / half / three-quarter / full, with each step ≈ 13 servings.

## Magnet–reed signal-path geometry

The reed column sits IN the foam-shell channel, so the reed sensors land roughly at the wall's mid-thickness in x. Path from the float's centered magnet (donor donut OD ~8 mm, magnet outer surface at strut + ~4 mm) to the reed sensor crosses the reservoir wall (4 mm) + the cavity-side air gap (~0.5 mm) + roughly half a reed body (~1.5 mm) ≈ **~6 mm**.

**Honest signal-strength numbers** for the donor ferrite donut (~8 mm OD × 4 mm ID × 2 mm thick, Br ≈ 0.3 T):

| Distance | Field on axis (approx) | Reed pull-in needed |
|---|---|---|
| ~4 mm (column flush with reservoir wall's outer face) | ~150–200 gauss | ~60–100 gauss — comfortable margin |
| ~6 mm (column centered in the channel — current spec) | ~70–100 gauss | ~60–100 gauss — adequate margin |
| ~7.5 mm (column on the wall's outer face, no channel) | ~40–60 gauss | ~60–100 gauss — marginal |

Cutting the channel into the wall (rather than mounting the column on the wall's outer face) gets us into the adequate-margin range without a neodymium upgrade. Same magnet as the carbonator. One SKU saved.

## GPIO budget

4 reeds × 2 reservoirs = **8 input GPIOs needed** for the flavor reservoir level sensing.

The current ESP32 plan ([`../../../wiring/esp32-pinout.mmd`](../../../wiring/esp32-pinout.mmd)) routes 12 solenoids through one MCP23017 (16 channels, 4 currently spare). 8 reed inputs exceed those 4 spare bits by 4, so we need 4 more bits somewhere. Three viable options:

- **Second MCP23017** at I²C address 0x21. Uses 4 of its 16 channels for Reservoir B reeds; 12 spare for headroom. Simplest from a firmware standpoint (same I²C driver as 0x20). ~$13/build.
- **ESP32 direct GPIO** for 4 reeds: GPIO 2 and 12 (bootstrap-sensitive but usable with `INPUT_PULLUP`), GPIO 36 and 39 (input-only, need external 10 kΩ pull-ups). Saves the chip but adds 2 external resistors + slightly more firmware paths.
- **74HC165 shift register**. SPI-ish 8-bit input expansion. Cheaper than MCP if scaling, overkill at this count.

The split is: Reservoir A's 4 reeds → MCP 0x20 PB[4:7] (the existing chip's spare bits, no firmware change). Reservoir B's 4 reeds → one of the three options above. Decision deferred.

## Parts (per build)

Per-build additions for the flavor-reservoir level sensing are tracked in [`../../../bom.md`](../../../bom.md) §12 "Level sensing":

- **8 Gebildet reed switches** (B0CW9418F6) for the flavor reservoirs — same SKU as the carbonator's 2 reeds; 2 × 6-pack covers all 10 reeds per build (2 carbonator + 8 flavor) with 2 spares.
- **2 DEVMO MINI floats** (B07T18PGJ4) — one per flavor reservoir. Donor donut + its ferrite magnet kept; switch body / cable discarded. With the reed column inside the foam-shell channel (~6 mm magnet-to-reed path), no neodymium upgrade needed. The carbonator's existing 1 unit becomes 3 units per build (1 carbonator + 2 reservoirs).
- **2 multi-conductor cables** for the harnesses (≥ 5 conductors each: 4 reed signals + 1 common return per reservoir). Research candidate under evaluation at the time of writing: KWANGIL 22 AWG 12-conductor UL2464 ([B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21)) — characterize once it arrives.
- **(Conditional) 1 second MCP23017** GPIO expander (B07P2H1NZG) — same SKU as the existing expander, at I²C address 0x21. Only needed if the ESP32-direct-GPIO and 74HC165 alternatives are rejected.

## Calibration

Each reed's position along the column is fixed by how the cable is laid out and where each reed is soldered in. The column's vertical position in the foam-shell channel is set by the channel's bottom shelf. 4 reeds span the float's useful Y range with one reed per ~25% of usable volume.

The firmware reads the reed states as a 5-level encoding (0/4 through 4/4 triggered) and reports "servings remaining" in ~13-serving steps.

## Service

The reed column is mechanically held in the channel, not foam-encapsulated, so in principle it can be replaced — lift the cap off, pull the column up and out of the channel from above (the cap above is the only thing trapping it axially). Whether this is practical in the field depends on whether the reservoir has to come out first; the reservoir's outer +X face sits ~0.5 mm from the channel, so the column likely needs to be sized to clear that gap or the reservoir needs to lift out first.

The expected failure mode (reed glass tube fractures, contact corrodes) is well below the appliance's 10-year design lifetime for sealed glass reeds in a dry air environment.

The internal strut is integral to the reservoir body. The float is reachable by removing the cap (six M3 × 12 SHCS + gasket) and lifting it off the strut.

## Open items

- **Foam-shell channel CAD.** Implemented in `_foam_shell_geometry.py` `build_reed_channels()`, `cut_reed_channel_openings()`, and `cut_reed_cable_holes()`. Vertical reed channel at z=−45, 6 mm × 8 mm cavity, full height (cavity y = 2..213.4), top open. Horizontal cable channel sitting on the foam shell floor (cavity y = 2..10, cable Y = 6), running in +Z to z = 70.5 (the +Z bag-pocket wall's inner face), 5 mm × 8 mm cavity. The bag-pocket far ±X wall is cut in the channel footprint (vertical reed-column band + horizontal cable band, extending through the +Z corner arc material) so the channels are open to the bag-pocket interior. Coaxial ⌀6.5 cable hole in +Z direction at (x = ±(reservoir_bulkhead_port_x + 8), y = 18, z = 62.5), piercing the +Z bag-pocket wall AND the +Z outer shell wall — exits parallel to and ±8 mm offset from the existing bulkhead pass-through. Cable's path: reed column → vertical channel → horizontal channel → wall opening into bag-pocket interior → bend up from y=6 to y=18 inside the pocket while traversing −X through dry-side empty space → +Z cable hole → outside cold core. Refine the channel cross-section (currently 6mm vertical × 8mm horizontal cavity widths) once the cable's actual OD is characterized.
- **Cable selection.** Multi-conductor cable on order ([B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21)). Once it arrives: measure jacket OD, verify individual-conductor strip-ability for the reed-end terminations, decide whether 12-conductor is the spec or if a smaller conductor count is sufficient (we only need 5 conductors per cable: 4 reed signals + 1 common return).
- **GPIO allocation for Reservoir B's 4 reeds.** Pick one of second MCP23017 / ESP32 direct GPIO / 74HC165.
