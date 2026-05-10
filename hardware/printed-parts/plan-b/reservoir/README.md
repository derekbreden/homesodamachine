# Printed Flavor Reservoir

Plan B for replacing the permanent Platypus bladders with custom hard reservoirs that conform to the cold-core envelope. The user-visible experience stays the same: flavor lives inside the machine, dispenses instantly, fills from the top hopper or rear BiB input, and cleans in place. This plan exists because under-sink volume is tight enough that an off-the-shelf bottle's extra cap, handle, shoulder, and clearance features cost real appliance volume.

The reservoir is not the carbonator and is not a service pressure vessel. It is a vented syrup reservoir that must reliably hold flavor concentrate, survive pump suction and fill/clean cycles, fit the thermal envelope, and not create dead syrup pockets.

For Plan B, the fluid reservoir remains a separate printed part from the foam-bag shell. Printing the reservoir and foam shell as one integrated part may be possible, but it couples leak integrity, foam-pour geometry, print failure, cleaning access, and service replacement into one experiment. That belongs in a later Plan C, not in the first hard-reservoir path.

## Serviceability Constraint

Plan B is intended to be a lifetime wetted part in normal use, but not a potted or sacrificial cold-core component. The foam cap / shell stack must preserve a non-destructive service path: removable dowels, screws, or heat-set-insert fasteners are acceptable, but glue in the reservoir access path is not. Reservoir replacement may require appliance disassembly, but it must not require cutting foam, cutting tubing, disturbing the refrigeration loop, or replacing the cold core.

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
- 1 L usable volume target, with any extra volume treated as headspace and drain margin.
- Sloped internal floor to a low outlet sump.
- Outlet boss sized for the same 1/4" hard-line ecosystem used elsewhere in the flavor manifold.
- High vent port with a replaceable hydrophobic membrane filter, protected by a splash labyrinth or short standpipe.
- Fill path from the valve manifold, not a user-opened cap on the reservoir.
- No internal support material, no internal threads, no decorative texture, no sharp inside corners.

### Cavity envelope (post centerward-wall removal)

Each bag pocket cavity in `../foam-bag-shell/` opens along its centerward face directly into the support shell's interior — the bag pocket's tank-facing wall and the support shell's matching ±X wall were removed because they had air on both sides (bag cavity inside, corner-pocket air outside; see the foam-bag-shell README for the wall analysis). Each cavity per side is now:

- **Top-down cross-section:** rectangle bounded at the far face (x = ±104.5 mm) and the +Z / −Z walls (z = ±70.5 mm), with a **concave cylindrical face** on the centerward side following the round cup's outer surface (radius 71.5 mm, vertical axis). Closer to a `[` than a `D` — three straight sides and one concave curve, not three straight sides and a convex bulge.
- **Vertical extent:** y ∈ [1, 212.4] mm = 211.4 mm tall.
- **Air volume:** ~1.42 L per cavity (up from the 0.984 L rectangular void that the previous envelope assumed).

A reservoir designed to fill that cavity is a rectangular prism with a concave cylindrical cutout on its centerward face. Outer volume ~1.42 L; with a 2 mm reservoir wall, internal volume ≈ 1.30 L; with a 1.5 mm wall, ≈ 1.34 L. Both well over the 1 L usable target with comfortable headroom for sump, vent standpipe, fillets, and bosses.

The previous "enlarge the bag-pocket gross envelope slightly in X" guidance is **obsolete** — that recipe was based on the 0.984 L rectangle, where a 1 L print barely fit. The current cavity exceeds 1 L by ~40 %; no envelope change is needed. Y and Z stay where they are because the pressure-vessel and plumbing envelope haven't changed.

The first printable shape can be ugly. It needs to preserve the real wall thicknesses, bosses, vent geometry, outlet sump, and sealing surfaces. Exterior packaging elegance comes after the liquid behavior is proven.

### Thermal coupling: actual goal is refrigerator-level

The cooling target is refrigerator-level — roughly 2–5 °C in the syrup itself. The "8–15 °C passive pre-chill" range in [`../../future.md`](../../future.md) (line 68) describes what the *current geometry actually delivers*, not the goal we'd ideally hit.

Per-area thermal resistances (m²·K/W) for a 2 mm-walled hard reservoir sitting flush against the round cup wall, with kitchen ambient T_amb ≈ 22 °C and tank water T_cold ≈ 2 °C:

**Cold side** (syrup → tank water):

| Layer | k (W/m·K) | R (m²·K/W) |
|---|---|---|
| Reservoir wall (PETG, 2 mm) | 0.20 | 0.010 |
| Round cup wall (PETG, 1 mm) | 0.20 | 0.005 |
| Inner foam (2 lb closed-cell PU, 7 mm) | 0.025 | 0.280 |
| Tank wall (316 SS, 1.65 mm) | 16 | 0.0001 |
| **R_cold total** | | **0.295** |

**Warm side** (syrup → kitchen ambient):

| Layer | k (W/m·K) | R (m²·K/W) |
|---|---|---|
| Reservoir wall (PETG, 2 mm) | 0.20 | 0.010 |
| Bag pocket far wall (PETG, 1 mm) | 0.20 | 0.005 |
| Outer foam (2 lb closed-cell PU, 16 mm) | 0.025 | 0.640 |
| Outer shell wall (PETG, 1 mm) | 0.20 | 0.005 |
| Outer convection (vertical, still cabinet air, h ≈ 5 W/m²·K) | — | 0.200 |
| **R_warm total** | | **0.860** |

Equilibrium syrup temperature, balancing the two heat paths:

T_syrup = (T_amb × R_cold + T_cold × R_warm) / (R_cold + R_warm) = (22 × 0.295 + 2 × 0.860) / 1.155 ≈ **7.1 °C**

The **dominant resistance on the cold side is the inner foam** — 0.28 of 0.295, or 95 % of R_cold. Substituting the bladder's 75 µm of LDPE (≈ 0.0002 m²·K/W) for the reservoir's 2 mm of PETG (0.010) removes ~0.010 from R_cold and shifts T_syrup by ≈ 0.1 °C. So **bladder vs hard reservoir is not the dominant variable for chilling performance**; both will sit in the ~7 °C range with the current foam thickness, regardless of wall material. The wall-thickness penalty for going hard-reservoir is real but small compared to the foam term.

To hit the 4 °C target with this architecture, R_cold needs to drop from 0.295 to roughly 0.135 m²·K/W. The only large-impact lever is the inner foam:

| Inner foam thickness | R_cold | T_syrup |
|---|---|---|
| 7 mm (current) | 0.295 | 7.1 °C |
| 5 mm | 0.215 | 5.7 °C |
| 3 mm | 0.135 | 4.7 °C |
| 1 mm (structural floor) | 0.055 | 3.2 °C |

Thinning the inner foam comes with trade-offs:
- Less freeze margin if the carbonator briefly dips below 2 °C; the cup-wall outer face would track tank water more closely.
- Reduced bag-side / reservoir-side condensation control (closed-cell foam normally prevents water from wicking against the reservoir under transient warm-up cycles).
- Less acoustic / mechanical isolation between the cold core and the bag pocket.

These are foam-bag-shell architecture decisions, not Plan B reservoir decisions — flagged here so the reservoir doesn't get blamed for falling short of refrigerator-level when the foam thickness is what sets the floor.

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
