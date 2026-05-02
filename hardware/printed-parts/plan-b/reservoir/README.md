# Printed Flavor Reservoir

Plan B for replacing the permanent Platypus bladders with custom hard reservoirs that conform to the cold-core envelope. The user-visible experience stays the same: flavor lives inside the machine, dispenses instantly, fills from the top hopper or rear BiB input, and cleans in place. This plan exists because under-sink volume is tight enough that an off-the-shelf bottle's extra cap, handle, shoulder, and clearance features cost real appliance volume.

The reservoir is not the carbonator and is not a service pressure vessel. It is a vented syrup reservoir that must reliably hold flavor concentrate, survive pump suction and fill/clean cycles, fit the thermal envelope, and not create dead syrup pockets.

## Candidate Filament

Initial test prints should use natural / uncolored PET-family material with explicit food-contact paperwork available from the seller or manufacturer. Buy small quantities first; this phase is about proving print process and reservoir behavior, not locking a production supplier.

| Candidate | Purchase link | Current purchase notes checked 2026-05-02 | Why it is in the test set |
|-----------|---------------|--------------------------------------------|----------------------------|
| CARBON by Comfy Materials certified food-grade PETG, 1.75 mm, 1 kg | [Comfy Materials direct](https://comfymaterials.com/product/certified-food-grade-petg-3d-printer-filament-carbon-by-comfy-materials-lab-tested-fda-compliant-food-safe-1-75mm-1kg-accuracy-0-02/) | $34.99-$35.99; seller contact page lists Tampa, FL; direct product page allows add-to-cart but does not state stock count or lead time. | Strongest retail claim found: Eastman GN071 copolyester, NSF/ANSI 51 raw resin, claimed TÜV SÜD + SGS testing to FDA 21 CFR 177.1630. Good first material for liquid-hold and process tests. |
| Fillamentum PETG Natural, 1.75 mm, 1 kg | [Fillamentum USA](https://fillamentumusa.com/products/petg-natural-1) | $30.00; page states "Low stock - 7 in stock, ready to ship" and also has a Shopify backorder notice for the selected variant, so confirm at checkout. Site states orders before 11:00 CET ship same day and average delivery is 2-4 days worldwide. | Natural PETG with food-contact declaration available by request; good second source for comparing printability, taste/odor, and long-dwell syrup behavior. |

Use a dedicated stainless nozzle/hotend path for this work, and keep non-test filaments away from it while hot.

## Reservoir Architecture Under Test

Target features for the first design:

- One reservoir per flavor, shaped to the cold-core shell instead of shaped like a bottle.
- Approximately 1 L usable volume, with any extra volume treated as headspace and drain margin.
- Sloped internal floor to a low outlet sump.
- Outlet boss sized for the same 1/4" hard-line ecosystem used elsewhere in the flavor manifold.
- High vent port with a replaceable hydrophobic membrane filter, protected by a splash labyrinth or short standpipe.
- Fill path from the valve manifold, not a user-opened cap on the reservoir.
- No internal support material, no internal threads, no decorative texture, no sharp inside corners.

The first printable shape can be ugly. It needs to preserve the real wall thicknesses, bosses, vent geometry, outlet sump, and sealing surfaces. Exterior packaging elegance comes after the liquid behavior is proven.

## Test Sequence

Pressure testing is a print-process screen, not a service condition. In the appliance the reservoir is vented. The pressure ladder exists to expose under-fused walls, weak seams, and bad boss geometry before syrup ever goes into the part.

### 1. Coupon And Boss Tests

Print small artifacts before printing a tank:

- Flat wall coupon with the intended wall schedule.
- Corner coupon with the intended internal radius.
- Outlet boss coupon with the intended fitting/seal stack.
- Vent boss coupon with the intended filter holder geometry.
- Weld-line / seam coupon using the same orientation expected on the reservoir.

Checks:

- Weigh dry.
- Fill or submerge with dyed water for 24 hours.
- Pressurize gently from the wet side and inspect for weep paths.
- Run a pressure ladder on water-filled coupons: 5, 15, 30, 60, then 100 PSI if the earlier steps are boring. Hold each step for 10 minutes and inspect before moving up.
- Dry exterior, weigh again, and note any mass gain.
- Cut at least one coupon open and inspect wall fusion under magnification.

Pass condition: no visible weeping, no dye path through corners or bosses, no pressure-step bubble trail, and no obvious under-fused internal void chain.

### 2. Mini Reservoir

Print a 100-250 mL reservoir that uses the same wall schedule, vent boss, outlet sump, and fitting geometry as the full part.

Water tests:

- Fill with dyed water and hold upright for 24 hours.
- Hold on each side and inverted for 24 hours per orientation.
- Plug the vent and outlet, then run a low-pressure submerged bubble test.
- If the bubble test is clean, repeat the coupon pressure ladder on the mini reservoir before printing the full-volume part.
- Pull from the outlet with the actual peristaltic pump and confirm flow does not become vacuum-limited when the vent is active.
- Fill through the intended fill port and confirm the vent clears displaced air without burping liquid.

Cleaning tests:

- Run water in, water out.
- Run air in, air out.
- Repeat until the outlet runs visibly clear after dyed water.
- Open the test reservoir and inspect the outlet sump, vent standpipe, and corners.

Pass condition: no liquid escape except through intended ports, no pump starvation with the vent installed, no trapped dyed water after the clean cycle.

### 3. Full-Volume Water Reservoir

Print the first approximately 1 L reservoir using the same settings that passed the mini reservoir.

Checks:

- 48-hour dyed-water hold in normal installed orientation.
- 24-hour hold at each credible shipping/service orientation.
- Refrigerator-temperature soak at 2-8°C for 48 hours.
- Five fill/dispense/clean cycles using the manifold path.
- Pump dosing comparison against a known-good Platypus bladder at the same syrup-equivalent viscosity.

Pass condition: no weeping, no dosing drift attributable to vent restriction or reservoir geometry, no retained rinse water that would dilute the next fill.

### 4. Syrup Dwell

Use actual SodaStream-compatible concentrate only after water behavior is boring.

Checks:

- 7-day cold dwell with Diet Mountain Dew syrup or equivalent acidic concentrate.
- Daily exterior wipe check for tackiness or syrup odor.
- Dispense a measured volume each day and compare pump time to delivered mass.
- Run the normal clean cycle after the dwell and inspect for color/smell retention.

Pass condition: reservoir stays dry outside, pump delivery stays repeatable, and the clean cycle leaves no obvious syrup hold-up.

## Promotion Criteria

Printed hard reservoirs move from Plan B toward the main architecture only after:

- Two different reservoir prints pass the full water sequence.
- At least one print passes the syrup dwell sequence.
- The vent/filter geometry survives fill, dispense, and clean cycles without becoming the flow limiter.
- The part fits the cold-core packaging better than the Platypus-shell design by enough margin to matter.

Until then, Platypus bladders remain the known-good fallback because they already work in the prototype.
