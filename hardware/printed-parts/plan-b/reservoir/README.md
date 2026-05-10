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

The cooling target is refrigerator-level — roughly 2–5 °C in the syrup itself. The "8–15 °C passive pre-chill" range in [`../../future.md`](../../future.md) (line 68) was an aspirational realistic-target framing rather than a rigorous prediction; this section walks the actual thermal path.

**Don't model the cold side as 7 mm of foam.** The radial space inside `tank_copper_shell` is 7 mm, but most of it is occupied by the 1/4" (6.35 mm OD) ACR copper evaporator coil pressed against the tank wall under 3M 425 thermal tape. Foam fills only the ~0.6 mm of remaining radial gap between the coil's outer surface and the cup wall's inner face. Between coil wraps (vertically), the full 7 mm gap exists, but only over the small fraction of cup height that isn't covered by a coil row.

Two-zone cold-side path, tiled vertically along the cup wall:

| Zone | Vertical fraction (close-wound, pitch ≈ coil OD) | Foam thickness | Cold source |
|---|---|---|---|
| At-coil rows | ~80 % | ~0.6 mm | coil outer face ≈ refrigerant saturation temp |
| Between-coil rows | ~20 % | ~7 mm | tank wall ≈ tank water temp |

Coil outer face temperature swings with compressor state:
- **Compressor running:** R-600a saturating on the suction side ≈ **−5 to −10 °C**.
- **Compressor off:** coil equalizes toward tank water ≈ 2 °C.
- **Duty-cycle averaged:** roughly 0 °C in normal operation. The ESP32 firmware uses 2 °C / 4 °C hysteresis on the tank-wall probe with a hard −8 °C cutout on the suction-line probe, so the coil rarely sits long below −8 °C, but the time-weighted average is well below the tank water temperature.

**Cold side (per-area resistance, syrup → cold structures):**

| Layer | R (m²·K/W) |
|---|---|
| Reservoir wall (PETG, 2 mm) | 0.010 |
| Round cup wall (PETG, 1 mm) | 0.005 |
| Foam zone, parallel-effective: 0.80 / 0.024 + 0.20 / 0.28 → R_eff = 1 / 33.6 | 0.030 |
| **R_cold total (effective)** | **0.045** |

Effective cold-side temperature, weighted by per-unit-area conductance:

T_cold_eff = (0.80 / 0.024) · 0 °C + (0.20 / 0.28) · 2 °C all divided by 33.6 ≈ **0.04 °C**

**Warm side (syrup → kitchen ambient):**

| Layer | R (m²·K/W) |
|---|---|
| Reservoir wall (PETG, 2 mm) | 0.010 |
| Bag pocket far wall (PETG, 1 mm) | 0.005 |
| Outer foam (2 lb closed-cell PU, 16 mm) | 0.640 |
| Outer shell wall (PETG, 1 mm) | 0.005 |
| Outer convection (vertical, still cabinet air, h ≈ 5 W/m²·K) | 0.200 |
| **R_warm total** | **0.860** |

**Equilibrium syrup temperature**, weighted by surface areas (centerward face A_c ≈ 0.042 m² counters the four warm-side faces A_w ≈ 0.082 m²):

T_syrup = (T_amb · A_w/R_warm + T_cold · A_c/R_cold) / (A_w/R_warm + A_c/R_cold) = (22 · 0.096 + 0.04 · 0.949) / 1.045 ≈ **2.1 °C**

The architecture is plausibly **already refrigerator-cold**. The cooling capacity comes from a thin film of foam over a cold copper coil, not from a 7 mm bulk foam layer over a lukewarm tank wall.

**Implications for Plan B:**

1. The earlier "thin the inner foam to reach 4 °C" recipe in this section was wrong — it assumed a 7 mm foam layer that doesn't exist (the copper coil occupies that space). **Disregard it.** Foam thickness is set by `(radial gap) − (coil OD)` and isn't an independent design variable.

2. The dominant risk is now **freeze**, not insufficient chilling. With T_coil dropping to −5 to −10 °C during compressor pulls and only 0.6 mm of foam between the coil and the cup wall, the cup-wall outer face directly opposite a coil row can fall below 0 °C. Whether syrup actually freezes depends on internal convection, syrup composition (sucralose concentrates have non-zero freezing-point depression but not unlimited), compressor duty cycle, and how tightly the reservoir wall sits against the cup wall.

3. Bladder vs hard reservoir is still not the dominant variable. Replacing 2 mm of PETG (0.010) with 75 µm of LDPE (≈ 0.0002) drops R_cold to 0.035, moving T_syrup by roughly 0.5 °C — colder, not warmer. So the hard reservoir is *less aggressive* on freeze risk than the bladder by a small margin, which is a quiet point in its favor.

4. **Bench instrumentation should add a third DS18B20** in the reservoir interior, alongside the existing tank-wall and suction-line probes. The current two probes tell you the cold side; a syrup-side probe tells you whether the model above is right and whether the actual operating point is above, near, or below freezing.

5. Levers that *do* exist for tuning the operating point:
   - Coil pitch (loosening the wind reduces the at-coil fraction and softens cooling)
   - Compressor hysteresis band (raising the lower bound from 2 °C narrows the pull-down range)
   - Suction-line cutout temperature (currently −8 °C; raising it caps how cold the coil can get)
   - Outer foam thickness (reducing it raises T_syrup; the geometry already budgets 16 mm)

These all live in the foam-bag-shell + firmware architecture, not in the reservoir architecture.

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
