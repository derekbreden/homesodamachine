# Cold Core Assembly

The production procedure for assembling the cold core — the back-of-enclosure subsystem that contains the carbonator vessel (already wrapped in its evaporator coil per [`refrigerant-loop.md`](refrigerant-loop.md)), two flavor reservoirs, and the surrounding pour-in-place polyurethane foam, all held together inside a 3D-printed PETG shell stack.

The bulk of the foam-pour geometry, shell architecture, copper-plug binder-clip cross-section, and TPU-gasket seam analysis lives in [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) — that doc is detailed, current, and source-of-truth for the part design. This document is the production-procedure framing: where the cold core sits relative to upstream (vessel + refrigerant loop) and downstream (final enclosure integration), and what the build-cadence steps are at the appliance level.

## Scope

In: one carbonator vessel already wrapped in its bonded evaporator coil and plumbed into the refrigerant loop (output of [`refrigerant-loop.md`](refrigerant-loop.md)); the printed PETG shell stack (foam-shell, foam-cap × 2, foam-cap-lid × 2, copper-plug × 3, reservoir × 2); TPU 90A gaskets × 2; pour-in-place 2 lb closed-cell polyurethane foam (two-part 1:1); M3 × 25 SHCS × 12 and ruthex M3 inserts × 12.

Out: a fully foam-poured cold core, capped + gasketed top and bottom, with every penetration routed through the shell wall. Ready for installation into the enclosure.

Not in scope: enclosure-side assembly (electronics shelf, compressor + condenser + fan placement, AC wiring), faucet install, final integration.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §6 (cold-core insulation, pour-in-place foam + 3M 425 foil tape + foam-pour consumables) + §13 (mechanical attach hardware + reservoir-cap vent filter) + §7 (the printed parts themselves, on $/kg-PETG basis). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`../purchases.md`](../purchases.md) §6 + §11. The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

The **3M 425 aluminum foil tape** is *already applied to the vessel OD* at this point per [`refrigerant-loop.md`](refrigerant-loop.md) step 4. It's listed in bom.md §6 because it's a cold-core thermal-interface part, but it's installed during refrigerant-loop assembly. Not a fresh input to the procedure below.

| Item | Source | Status (per purchases.md) |
|---|---|---|
| Vessel + bonded coil + refrigerant loop | Output of [`refrigerant-loop.md`](refrigerant-loop.md) | Charged, leak-checked |
| Foam-shell (printed PETG) | [`../printed-parts/cold-core/foam-shell/`](../printed-parts/cold-core/foam-shell/) | Print, Bambu H2C, 0.8 mm nozzle |
| Foam cap × 2 + foam cap lid × 2 (printed PETG) | Same | Print |
| Copper plug × 3 (printed PETG) | Same | Print |
| Flavor reservoir × 2 (printed) | [`../printed-parts/cold-core/reservoir/`](../printed-parts/cold-core/reservoir/) | Print, Comfy Materials FDA-compliant food-grade PETG-Carbon B0BTLNK74C — ACQUIRED |
| TPU 90A gasket × 2 (printed) | [`../printed-parts/cold-core/foam-shell/`](../printed-parts/cold-core/foam-shell/) | Print |
| M3 × 25 mm SHCS, 12.9 alloy, black oxide × 12 (body cap screws) | BNUOK B0DJQGF665 | ON-ORDER |
| M3 × 12 mm SHCS, 12.9 alloy, black oxide × 12 (reservoir-cap screws — upstream of cold-core assembly per "Open items") | BNUOK B0DJQGVK8S | ON-ORDER |
| ruthex M3 short heat-set inserts × 26 per build (12 outer_shell + 12 reservoir + 2 touch-flo-shell) | ruthex B0D39W228K (100-pc bag = ~3.8 builds) | ON-ORDER |
| LVDALAB PTFE membrane filter Ø13 mm × 0.45 µm × 2 (reservoir vent — upstream of cold-core assembly) | B0D41KT345 (100-pc bag = 50 builds) | ON-ORDER |
| Pour-in-place 2 lb 2-part closed-cell PU foam, 1 qt kit | Fiberglass Supply Depot B08R7TX8QJ | ON-ORDER |
| Foam-pour consumables (mixing cups × 4, stir sticks × 4, nitrile gloves × 1 pair per build) | B08JHH1DBF / B09H6ZP447 / B0G8SSMVKW | ACQUIRED |

## Procedure

The foam pour happens in **three independent operations**: top cap, bottom cap, body. None chain across each other.

### 1. Cap foam pour (top and bottom, in parallel, before body assembly)

Each cap is a 16 mm-tall foam-filled cup. With the cap inverted and the foam-cap-lid sealing its open face from above, liquid foam enters through the lid's Ø10 mm pour hole; air escapes through two Ø6 mm vents. Foam expands to fill, cures to a self-contained puck. Trim flush after cure.

Both caps are identical and not body-dependent — pour them in parallel. Geometry detail at [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "foam_cap and foam_cap_lid".

### 2. Press ruthex inserts into the outer shell

Six ruthex M3 short heat-set inserts pressed into the top face of the outer_shell, six into the bottom face. Each insert seats in a Ø4.0 mm × 4 mm-deep printed pocket; another 4 mm of relief below the insert clears the M3 × 25 screw tip. Standard heat-set procedure: soldering iron tip on the insert, press straight down until flush.

Geometry detail at [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Cap-to-outer-shell joinery".

### 3. Body-side install (everything goes in before the body pour)

With the outer shell open-top-up on the bench, install every internal component:

- **Pressure vessel + coil** (already wrapped and plumbed per [`refrigerant-loop.md`](refrigerant-loop.md)) lowered into the cylindrical center cavity, seated on the printed-in `tank_support_ring`
- **Reservoirs** seated into the two ±X bag pockets
- **Penetrations routed through the outer shell walls:**
  - CO2 inlet → enters from above through the foam-cap-top boss + foam-cap-lid-top Ø6.5 hole at (x=0, z=−68.75); inside the cavity, a John Guest PP0308E 1/4" PTC 90° elbow seats in the Ø16 doorway in the −Z support arch, and the line continues to the vessel's bottom-plate TAISHER NPT elbow via a PP010822E 1/4" PTC × 1/4" NPT M adapter
  - Water outlet → dedicated Ø6.5 hole, +Z outer wall
  - Reservoir lines (+X, −X) → dedicated Ø6.5 holes in the bag_pocket_shell ±X far walls
  - Refrigerant inlet (low), refrigerant outlet (high), water inlet → shared Y-elongated slot at x=0 on the +Z outer wall. The water-inlet line transitions from the warm-side GASHER 1/4" NPT check valve via a first JG PP010822E 1/4" PTC × 1/4" NPT M adapter (warm-side NPT→PTC, same fitting used on the §4 CO2 path) before entering the slot as 1/4" OD LLDPE; downstream of the slot a second cold-side JG PP010822E (PTC → NPT) takes the LLDPE back to NPT before threading into the TAISHER 1/4" NPT 90° vessel-port elbow on Port 2 (top plate).
- **Three copper plugs** slid down into the shared +Z slot from above, sealing between and above the three pass-throughs (binder-clip geometry in [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Shared +Z slot and copper plug stack")
- **In-cavity PP0308E elbow** is angled in through the −Z support-arch doorway from above before the vessel drops into the cavity — its perpendicular legs cannot clear the bore axially, so installation order matters.

Per the foam-shell README "build decision": all fitting-size transitions (3/8" → 1/4", larger fittings) happen on the *warm side* of the shell, so every penetration through the shell wall is the same 1/4" OD tubing. Keep that boundary.

### 4. Body foam pour

Mix the two-part PU foam 1:1. Pour the liquid directly into the body's open +Y top — all at once, no cap on, no down-channels. Foam falls into the body and reaches every cavity in parallel: outer foam gap, bag pockets, corner pockets at ±Z, and the tank cavity inside the cylinder. The geometry choices that make this single top-down pour work are documented in [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Assembly and foam pour".

Foam expansion may push small amounts of material out through the 0.5 mm clearance bands around tubes in the +Z slot and the tight-fit tube exits at other penetrations. Expected; trim flush after cure.

### 5. Final assembly

After all three pours (top cap, bottom cap, body) have fully cured:

- TPU gasket onto the body's top edge — perimeter ring with 8 × 8 mm pads at each of the six screw positions
- Top cap (foam-filled, trimmed from step 1) seated over the gasket, six M3 × 25 SHCS through the cap's screw positions and into the top-face inserts
- Bottom cap onto the body's underside, six M3 × 25 SHCS — no gasket on the bottom (the body floor handles the air seal there)

The cold core is now sealed and ready for enclosure integration.

## Output condition

A finished cold core:

- All three foam pours cured, flush-trimmed at visible surfaces and tube exits
- Vessel + coil + refrigerant loop installed, seated in the cylinder cavity, surrounded by foam
- Both reservoirs seated in their bag pockets
- All seven penetrations routed through their designated holes / slot
- Top + bottom caps installed with M3 × 25 SHCS into the heat-set inserts
- TPU gasket compressed under the top cap (the bottom cap relies on the body floor for its seal)
- External envelope ~251 × 181 × 213.4 mm, ready to drop into the enclosure rear

## Open items

Procedure-level gaps not resolved by parts already committed in [`../purchases.md`](../purchases.md):

1. **Foam data-sheet spec (mix proportions, pot life, cure time, pour temperature window).** Vendor is committed (Fiberglass Supply Depot B08R7TX8QJ, ON-ORDER — Amazon order 112-5359790-0932202, May 15, 2026, arriving Sat May 16); the data sheet still needs to be read and the numbers locked into this doc once the kit is in hand.
2. **Trim method after foam cure.** What gets flush-cut, with what — knife, oscillating tool, both depending on location.
3. **Reservoir-internal assembly procedure (upstream of this doc).** The reservoir arrives in this procedure already assembled — cap installed, six M3×12 SHCS into ruthex inserts clamping a TPU gasket, PTFE vent membrane installed. That reservoir-internal sequence is not captured in any production-procedure doc.
4. **Reservoir final-qualification status.** The Comfy Materials PETG-Carbon filament is ACQUIRED but the reservoir is still under qualification. Production sign-off pending water + syrup-dwell pass.
