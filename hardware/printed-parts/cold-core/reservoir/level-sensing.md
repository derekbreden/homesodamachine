# Flavor Reservoir Level Sensing

Reed-and-float level sensing for each flavor reservoir, following the same architecture as the carbonator vessel ([future.md](../../../future.md) "Level sensing" section), with **[4](REEDS_PER_RES) reed switches per reservoir** for ~13-serving-step granularity over the usable fill range.

## Architecture

**Inside the reservoir:**

- A vertical **1/8" ([3.175 mm](ROD_DIAMETER)) 316L SS rod** (Tandefio B0CY4DWJFQ — same SKU as the carbonator vessel's float rod), separately supplied (not printed). The rod sits at `(x = ±[100](ROD_POSITION_X), z = [-45](ROD_POSITION_Z))` — the −Z half of the reservoir, opposite the bulkhead pocket (which lives on the +Z half at z=28..64). Bottom end drops into a blind bore in a standing printed **boss** rising from the reservoir BODY wet slope — the slope itself stays continuous and unbroken, no hole cut through it. Top end slips into the existing register **boss** hanging from the cap's underside (resized for the [3.175 mm](ROD_DIAMETER) rod). Specified in `reservoir.py` in this directory — `ROD_POSITION_X`, `ROD_POSITION_Z`, `ROD_DIAMETER`, `ROD_BORE`, `ROD_BOSS_OD`, `ROD_BOSS_HEIGHT`, `BODY_BOSS_HEIGHT`, `BODY_BOSS_FLOOR`. The cavity at z=−45 is ~38 mm wide (vs ~24 mm at z=0), giving clearance for the donor donut float regardless of its precise OD.
- A small **magnetic float** sliding on the rod. Donor is the DEVMO MINI float switch (Amazon B07T18PGJ4) already in the BOM for the carbonator — harvest the polypropylene donut, reuse its ferrite magnet. PP body pairs cleanly with the SS rod (no galvanic, no sticky contact).

**Outside the reservoir:**

- A pre-soldered **column of [4](REEDS_PER_RES) reed switches** wired to a multi-conductor cable. Each reed has both leads hand-soldered to a corresponding pair of conductors (one signal + the shared common return). The cable runs the length of the column past all [4](REEDS_PER_RES) reeds. The whole assembly is rigid enough to slide into the foam-shell channel as a single pre-assembled piece — no per-reed mounting feature needed inside the cold core.
- The **foam shell carries the channel that holds the column** — no separate printed reed-holder part. The channel is a **3-walled box that extrudes OUTWARD** from the reservoir pocket's far ±X wall into the outer foam zone. The original wall is the channel's back / inner face; two new ±z side walls extend outward; a new outer face closes the box on the foam-zone side. The channel has two segments:
  - A **vertical segment** at the reed positions, centered on z=−45, sized to slip-fit the reed-and-wire column. Full height — top open at the wall top so the column can be dropped in from above before the cap is installed.
  - A **horizontal segment** sitting on the foam shell floor (cavity y range = `[wall_and_floor_thickness, wall_and_floor_thickness + 8]` = [2, 10]). Sitting on the floor makes the segment printable — the foam shell floor IS the channel's bottom wall, no unsupported envelope floor mid-air. Runs from the vertical channel in +Z direction along the pocket far ±X wall to a **dedicated ⌀6.5 coaxial cable hole** through both the pocket far ±X wall and the outer ±X shell wall, at `(y = cable_y_center = 6, z = bag_pocket_width/2 − 10)` — same z as the existing bulkhead tube pass-through, on the ±X side a few mm offset from it, but 12 mm lower in y to match the channel's cable level. The cable runs at y = 6 from the channel exit straight through the pocket interior to the cable hole — no bend.
- The column is **held mechanically** by the channel — bottom shelf catches it from below, ±z side walls constrain it laterally, the cap on top traps it from above when installed. **No foam encapsulation** — the bag pocket is an air cavity per the cold-core's overall pour architecture, so foam doesn't reach the reed column.

## Reed pitch and what it gets you

Useful Y range for the float on the rod: ~40 mm above the floor (above the wet slope max) to ~210 mm (just below the cap) = ~170 mm of float travel.

| Reeds | Pitch (mm) | Servings per step |
|---|---|---|
| 3 | ~70 | ~17 |
| **4** | **~45** | **~13** |
| 5 | ~35 | ~10 |

[4](REEDS_PER_RES) reeds at ~45 mm pitch is the working spec. The customer-facing display is a 5-state fuel gauge (0, 1, 2, 3, [4](REEDS_PER_RES) reeds triggered) corresponding to roughly empty / quarter / half / three-quarter / full, with each step ≈ 13 servings.

## Magnet–reed signal-path geometry

The reed column sits IN the foam-shell channel, so the reed sensors land roughly at the wall's mid-thickness in x. Path from the float's centered magnet (donor donut OD ~8 mm, magnet outer surface at rod + ~4 mm) to the reed sensor crosses the reservoir wall (4 mm) + the cavity-side air gap (~0.5 mm) + roughly half a reed body (~1.5 mm) ≈ **~6 mm**.

**Honest signal-strength numbers** for the donor ferrite donut (~8 mm OD × 4 mm ID × 2 mm thick, Br ≈ 0.3 T):

| Distance | Field on axis (approx) | Reed pull-in needed |
|---|---|---|
| ~4 mm (column flush with reservoir wall's outer face) | ~150–200 gauss | ~60–100 gauss — comfortable margin |
| ~6 mm (column centered in the channel — current spec) | ~70–100 gauss | ~60–100 gauss — adequate margin |
| ~7.5 mm (column on the wall's outer face, no channel) | ~40–60 gauss | ~60–100 gauss — marginal |

Cutting the channel into the wall puts the reed column at the ~6 mm magnet-to-reed distance — adequate-margin range with the same ferrite donut the carbonator uses.

## GPIO budget

[4](REEDS_PER_RES) reeds × 2 reservoirs = **8 input GPIOs needed** for the flavor reservoir level sensing. Allocation:

- **Reservoir A's [4](REEDS_PER_RES) reeds** → existing MCP23017 0x20 PB[4:7] (the chip's spare bits after 12 valves). No firmware change beyond reading [4](REEDS_PER_RES) new bits.
- **Reservoir B's [4](REEDS_PER_RES) reeds** → new MCP23017 at I²C address 0x21, PA[0:3]. 12 spare bits on the new chip for future expansion. Same I²C driver as 0x20.

## Parts (per build)

Per-build additions for the flavor-reservoir level sensing are tracked in [`../../../bom.md`](../../../bom.md) §12 "Level sensing":

- **8 Gebildet reed switches** (B0CW9418F6) for the flavor reservoirs — same SKU as the carbonator's 2 reeds; 2 × 6-pack covers all 10 reeds per build (2 carbonator + 8 flavor) with 2 spares.
- **2 DEVMO MINI floats** (B07T18PGJ4) — one per flavor reservoir. Donor donut + its ferrite magnet kept; switch body / cable discarded. With the reed column inside the foam-shell channel (~6 mm magnet-to-reed path), no neodymium upgrade needed. The carbonator's existing 1 unit becomes 3 units per build (1 carbonator + 2 reservoirs).
- **2 multi-conductor cables** for the harnesses (≥ 5 conductors each: 4 reed signals + 1 common return per reservoir). Research candidate under evaluation at the time of writing: KWANGIL 22 AWG 12-conductor UL2464 ([B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21)) — characterize once it arrives.
- **1 second MCP23017** GPIO expander (B07P2H1NZG) — same SKU as the existing expander, at I²C address 0x21.

## Calibration

Each reed's position along the column is fixed by how the cable is laid out and where each reed is soldered in. The column's vertical position in the foam-shell channel is set by the channel's bottom shelf. [4](REEDS_PER_RES) reeds span the float's useful Y range with one reed per ~25% of usable volume.

The firmware reads the reed states as a 5-level encoding (0/4 through 4/4 triggered) and reports "servings remaining" in ~13-serving steps.

## Service

The reed column is mechanically held in the channel, not foam-encapsulated, so in principle it can be replaced — lift the cap off, pull the column up and out of the channel from above (the cap above is the only thing trapping it axially). Whether this is practical in the field depends on whether the reservoir has to come out first; the reservoir's outer +X face sits ~0.5 mm from the channel, so the column likely needs to be sized to clear that gap or the reservoir needs to lift out first.

The expected failure mode (reed glass tube fractures, contact corrodes) is well below the appliance's 10-year design lifetime for sealed glass reeds in a dry air environment.

The internal SS rod is a separately-supplied part captured at both ends by printed features: bottom in a blind bore inside a standing boss on the BODY wet slope, top in a slip-fit register boss on the cap's underside. Removing the cap (six M3 × 12 SHCS + gasket) lifts the rod's top out of the cap-side boss; the rod can then be drawn upward out of the body-side boss along with the float, or left standing in the body boss while the float alone is lifted off. The body boss has a printed-solid floor inside it (BODY_BOSS_FLOOR) — the rod tip bottoms out on PETG, never reaches the wet slope, and the slope itself is uncut so the rod cannot fall through into anything beneath it.

## Open items

- **Cable characterization + channel cross-section refinement.** Multi-conductor cable on order ([B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21)). Once it arrives: measure jacket OD, verify individual-conductor strip-ability for the reed-end terminations, decide whether 12-conductor is the spec or if a smaller conductor count is sufficient (we only need 5 conductors per cable: 4 reed signals + 1 common return), and refine the foam-shell channel cross-section (currently 6 mm reed-channel depth × 5 mm cable-channel depth, 8 mm wide along z / y) to fit the actual cable OD.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
