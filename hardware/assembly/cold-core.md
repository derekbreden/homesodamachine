# Cold Core Assembly

The production procedure for assembling the cold core — the back-of-enclosure subsystem that contains the carbonator vessel, its wound evaporator coil, two flavor reservoirs, and the surrounding pour-in-place polyurethane foam, all held together inside a 3D-printed PETG shell stack. The coil is wound around the vessel as the first step of this procedure; the coil's inlet/outlet stubs come out of the foam-shell's copper-plug exits and hang free, awaiting refrigerant-loop integration ([`refrigerant-loop.md`](refrigerant-loop.md)) on a later day.

The bulk of the foam-pour geometry, shell architecture, copper-plug binder-clip cross-section, and TPU-gasket seam analysis lives in [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) — that doc is detailed, current, and source-of-truth for the part design. This document is the production-procedure framing: where the cold core sits relative to upstream (vessel) and downstream (refrigerant-loop integration, final enclosure integration), and what the build-cadence steps are at the appliance level.

## Scope

In: one hydro-tested + passivated carbonator vessel (output of [`pressure-vessel.md`](pressure-vessel.md)); GOORY 1/4" OD × 0.031" wall ACR copper tubing for the evaporator coil; 3M 425 aluminum foil tape; the printed coil-winding mandrel; the printed PETG shell stack (foam-shell, foam-cap × 2, foam-cap-lid × 2, copper-plug × 3, reservoir × 2); TPU 90A gaskets × 2; pour-in-place 2 lb closed-cell polyurethane foam (two-part 1:1); M3 × 25 SHCS × 12 and ruthex M3 inserts × 12.

Out: a fully foam-poured cold core, capped + gasketed top and bottom, with the wound evaporator coil bonded around the vessel and its inlet/outlet stubs (~2 ft each) protruding through the foam-shell's copper-plug exits. Ready for installation into the enclosure and subsequent refrigerant-loop integration ([`refrigerant-loop.md`](refrigerant-loop.md)).

Not in scope: refrigerant-loop integration — the brazing of the coil stubs onto the donor unit's cap tube and suction line, vacuum, charge, and run-up — happens in [`refrigerant-loop.md`](refrigerant-loop.md), as a single-session procedure on a later day after this assembly is complete. Also not in scope: enclosure-side assembly (electronics shelf, compressor + condenser + fan placement, AC wiring), faucet install, final integration.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §5 (refrigeration — GOORY copper tubing for the coil) + §6 (cold-core insulation, 3M 425 foil tape + pour-in-place foam + foam-pour consumables) + §13 (mechanical attach hardware + reservoir-cap vent filter) + §7 (the printed parts themselves, on $/kg-PETG basis). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`../purchases.md`](../purchases.md) §6 + §11. The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

| Item | Source | Status (per purchases.md) |
|---|---|---|
| Carbonator vessel | Output of [`pressure-vessel.md`](pressure-vessel.md) | Hydro-tested + passivated |
| GOORY 1/4" OD × 0.031" wall ACR copper tubing | B0DKSW5VL9 | ~24 ft per vessel for coil wrap + tie-in stubs (1/2 of 50 ft roll per build) — ACQUIRED |
| 3M 425 aluminum foil tape | B07BTW7C2N | Coil-to-vessel thermal interface; applied as continuous skin under the coil; one 180 ft roll covers ~12 builds — ACQUIRED |
| Coil-winding mandrel (printed PETG) | [`../printed-parts/cold-core/coil-mandrel/`](../printed-parts/cold-core/coil-mandrel/) | Print, reusable across builds |
| Foam-shell (printed PETG) | [`../printed-parts/cold-core/foam-shell/`](../printed-parts/cold-core/foam-shell/) | Print, Bambu H2C, 0.8 mm nozzle |
| Foam cap × 2 + foam cap lid × 2 (printed PETG) | Same | Print |
| Copper plug × 3 (printed PETG) | Same | Print |
| Flavor reservoir × 2 (printed) | [`../printed-parts/cold-core/reservoir/`](../printed-parts/cold-core/reservoir/) | Print, SunTop food-contact-compliant PETG (FDA 21 CFR 177.1630), 1.75 mm × 1 kg, Clear/Transparent B0FP34MJ94 — ON-ORDER |
| TPU 90A gasket × 2 (printed) | [`../printed-parts/cold-core/foam-shell/`](../printed-parts/cold-core/foam-shell/) | Print |
| M3 × 25 mm SHCS, 12.9 alloy, black oxide × 12 (body cap screws) | BNUOK B0DJQGF665 | ON-ORDER |
| M3 × 12 mm SHCS, 12.9 alloy, black oxide × 12 (reservoir-cap screws — upstream of cold-core assembly per "Open items") | BNUOK B0DJQGVK8S | ON-ORDER |
| ruthex M3 short heat-set inserts × 26 per build (12 outer_shell + 12 reservoir + 2 touch-flo-shell) | ruthex B0D39W228K (100-pc bag = ~3.8 builds) | ON-ORDER |
| LVDALAB PTFE membrane filter Ø13 mm × 0.45 µm × 2 (reservoir vent — upstream of cold-core assembly) | B0D41KT345 (100-pc bag = 50 builds) | ON-ORDER |
| Pour-in-place 2 lb 2-part closed-cell PU foam, 1 qt kit | Fiberglass Supply Depot B08R7TX8QJ | ON-ORDER |
| Foam-pour consumables (mixing cups × 4, stir sticks × 4, nitrile gloves × 1 pair per build) | B08JHH1DBF / B09H6ZP447 / B0G8SSMVKW | ACQUIRED |

## Procedure

The coil winding happens first (step 1). The three foam pours — top cap, bottom cap, body — are independent operations that don't chain across each other (top + bottom pour in parallel as step 2, body pours as step 5). Final cap-on assembly is step 6.

### 1. Wind the evaporator coil around the vessel

Wind GOORY 1/4" OD × 0.031" wall ACR copper tubing as a single-layer helical coil at ~1/8" pitch around the vessel OD — ~22 ft of wrap per vessel + ~2 ft each end for the refrigerant-loop tie-in stubs. The tie-in stubs get brazed to the donor unit's cap tube and suction line during refrigerant-loop integration ([`refrigerant-loop.md`](refrigerant-loop.md)) on a later day; they exit the finished cold core through the foam-shell's copper-plug holes and hang free until then. The 0.031" wall was specifically chosen to resist kinking at the bend radius around the 5" OD vessel; thinner wall kinks, this wall holds.

Bond the coil to the vessel OD with 3M 425 aluminum foil tape applied as a continuous skin between vessel and coil. The tape spans the tank-to-coil thermal interface.

Wind around the printed [coil-mandrel](../printed-parts/cold-core/coil-mandrel/generate_step_cadquery.py) — hollow PETG cylinder with a shallow 1 mm helical guide groove, mandrel OD 123 mm vs. tank OD 127 mm so the as-wound coil inner radius is 3 mm under the tank radius and tightens onto the vessel after slip-off. Wind length 120.4 mm and 9.687 wraps (pitch 12.43 mm) are set to align the coil's inlet/outlet ends with the foam-shell copper plugs at Y=46 and Y=166.4, so the exit bends are purely radial with no vertical jog. Pull the wound coil off the mandrel and slip it onto the foil-taped vessel; coil springback (1–3 mm radial) leaves a net interference fit.

[`../handwork.md`](../handwork.md) "Bend copper around the pressure vessel" is the summary-level dev-phase entry for this step.

### 2. Cap foam pour (top and bottom, in parallel, before body assembly)

Each cap is a 16 mm-tall foam-filled cup. With the cap inverted and the foam-cap-lid sealing its open face from above, liquid foam enters through the lid's Ø10 mm pour hole; air escapes through two Ø6 mm vents. Foam expands to fill, cures to a self-contained puck. Trim flush after cure.

Both caps are identical and not body-dependent — pour them in parallel. Geometry detail at [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "foam_cap and foam_cap_lid".

### 3. Press ruthex inserts into the outer shell

Six ruthex M3 short heat-set inserts pressed into the top face of the outer_shell, six into the bottom face. Each insert seats in a Ø4.0 mm × 4 mm-deep printed pocket; another 4 mm of relief below the insert clears the M3 × 25 screw tip. Standard heat-set procedure: soldering iron tip on the insert, press straight down until flush.

Geometry detail at [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Cap-to-outer-shell joinery".

### 4. Body-side install (everything goes in before the body pour)

With the outer shell open-top-up on the bench, install every internal component:

- **Pressure vessel + coil** (already wrapped per step 1; coil stubs not yet plumbed — they exit the foam-shell's copper-plug holes and hang free for now, awaiting refrigerant-loop integration after this assembly completes) lowered into the cylindrical center cavity, seated on the printed-in `tank_support_ring`
- **Reservoirs** seated into the two ±X bag pockets
- **Penetrations routed through the outer shell walls:**
  - CO2 inlet → enters from above through the foam-cap-top boss + foam-cap-lid-top Ø6.5 hole at (x=0, z=−68.75); inside the cavity, a John Guest PP0308E 1/4" PTC 90° elbow seats in the Ø16 doorway in the −Z support arch, and the line continues to the vessel's bottom-plate TAISHER NPT elbow via a PP010822E 1/4" PTC × 1/4" NPT M adapter
  - Water outlet → dedicated Ø6.5 hole, +Z outer wall
  - Reservoir lines (+X, −X) → dedicated Ø6.5 holes in the bag_pocket_shell ±X far walls
  - Refrigerant inlet (low), refrigerant outlet (high), water inlet → shared Y-elongated slot at x=0 on the +Z outer wall. The water-inlet line transitions from the warm-side GASHER 1/4" NPT check valve via a first JG PP010822E 1/4" PTC × 1/4" NPT M adapter (warm-side NPT→PTC, same fitting used on the §4 CO2 path) before entering the slot as 1/4" OD LLDPE; downstream of the slot a second cold-side JG PP010822E (PTC → NPT) takes the LLDPE back to NPT before threading into the TAISHER 1/4" NPT 90° vessel-port elbow on Port 2 (top plate).
- **Three copper plugs** slid down into the shared +Z slot from above, sealing between and above the three pass-throughs (binder-clip geometry in [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Shared +Z slot and copper plug stack")
- **In-cavity PP0308E elbow** is angled in through the −Z support-arch doorway from above before the vessel drops into the cavity — its perpendicular legs cannot clear the bore axially, so installation order matters.

Per the foam-shell README "build decision": all fitting-size transitions (3/8" → 1/4", larger fittings) happen on the *warm side* of the shell, so every penetration through the shell wall is the same 1/4" OD tubing. Keep that boundary.

### 5. Body foam pour

Mix the two-part PU foam 1:1. Pour the liquid directly into the body's open +Y top — all at once, no cap on, no down-channels. Foam falls into the body and reaches every cavity in parallel: outer foam gap, bag pockets, corner pockets at ±Z, and the tank cavity inside the cylinder. The geometry choices that make this single top-down pour work are documented in [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Assembly and foam pour".

Foam expansion may push small amounts of material out through the 0.5 mm clearance bands around tubes in the +Z slot and the tight-fit tube exits at other penetrations. Expected; trim flush after cure.

### 6. Final assembly

After all three pours (top cap, bottom cap, body) have fully cured:

- TPU gasket onto the body's top edge — perimeter ring with 8 × 8 mm pads at each of the six screw positions
- Top cap (foam-filled, trimmed from step 2) seated over the gasket, six M3 × 25 SHCS through the cap's screw positions and into the top-face inserts
- Bottom cap onto the body's underside, six M3 × 25 SHCS — no gasket on the bottom (the body floor handles the air seal there)

The cold core is now sealed; coil inlet/outlet stubs protrude from the foam-shell's copper-plug exits, ready for [`refrigerant-loop.md`](refrigerant-loop.md) integration and enclosure install.

## Warm-side check valves (PTFE-on-metal rationale)

Both the water-inlet and CO2-inlet lines carry an inline 1/4" NPT SS check valve (GASHER B0FV2D2FFX, 2-pack covers both) on the warm side, upstream of the shared +Z slot. Both are PTFE soft-seat on metal poppet (confirmed by inspection 2026-04-25), not elastomer:

- **Water-side check** sits between the SeaFlo pump's MAACFLOW 1/4" NPT adapter and the first JG PP010822E PTC adapter that takes the line into 1/4" OD LLDPE for the run through the +Z slot. The pump's own internal elastomer checks are a redundant layer #3, not the primary seal — elastomer checks creep under sustained CO2 back-pressure, and gas molecules migrate through elastomer seals that would hold liquid indefinitely. PTFE-on-metal is the standard soft-seat construction in commercial beverage/brewery/food-process check valves at this pressure class: chemically inert to carbonic acid and CO2, no gas-permeation problem, suitable for long-term field service.
- **CO2-side check** sits on the dry side, between the DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the LTWFITTING bottom-plate barb adapter. Prevents water from back-flowing through the sparge stone, up the silicone tube, and into the CO2 regulator if pressures invert under fault.

## Output condition

A finished cold core:

- All three foam pours cured, flush-trimmed at visible surfaces and tube exits
- Vessel + bonded coil installed, seated in the cylinder cavity, surrounded by foam; coil inlet/outlet stubs (~2 ft each) protruding through the foam-shell's copper-plug exits, unconnected — awaiting refrigerant-loop integration
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
4. **Reservoir final-qualification status.** The SunTop food-contact-compliant PETG filament (B0FP34MJ94) is ON-ORDER; reservoir final qualification is still pending water + syrup-dwell pass.
