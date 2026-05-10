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

- **Top-down cross-section:** rectangle bounded at the far face (x = ±104.5 mm) and the +Z / −Z walls (z = ±70.5 mm), with a **concave cylindrical face** on the centerward side following the `tank_copper_shell`'s outer surface (radius 71.5 mm, vertical axis). Closer to a `[` than a `D` — three straight sides and one concave curve, not three straight sides and a convex bulge.
- **Vertical extent:** y ∈ [1, 212.4] mm = 211.4 mm tall.
- **Air volume:** ~1.42 L per cavity (up from the 0.984 L rectangular void that the previous envelope assumed).

A reservoir designed to fill that cavity is a rectangular prism with a concave cylindrical cutout on its centerward face. Outer volume ~1.42 L; with a 2 mm reservoir wall, internal volume ≈ 1.30 L; with a 1.5 mm wall, ≈ 1.34 L. Both well over the 1 L usable target with comfortable headroom for sump, vent standpipe, fillets, and bosses.

The previous "enlarge the bag-pocket gross envelope slightly in X" guidance is **obsolete** — that recipe was based on the 0.984 L rectangle, where a 1 L print barely fit. The current cavity exceeds 1 L by ~40 %; no envelope change is needed. Y and Z stay where they are because the pressure-vessel and plumbing envelope haven't changed.

The first printable shape can be ugly. It needs to preserve the real wall thicknesses, bosses, vent geometry, outlet sump, and sealing surfaces. Exterior packaging elegance comes after the liquid behavior is proven.

### Thermal coupling: actual goal is refrigerator-level

The cooling target is refrigerator-level — roughly 2–5 °C in the syrup itself. The "8–15 °C passive pre-chill" range in [`../../future.md`](../../future.md) (line 68) was an aspirational realistic-target framing rather than a rigorous prediction; this section walks the actual thermal path.

#### Why the "7 mm of foam" model is wrong

The radial space inside `tank_copper_shell` is 7 mm, but most of it is occupied by the 1/4" (6.35 mm OD) ACR copper evaporator coil pressed against the tank wall under 3M 425 thermal tape. The coil tube center sits at radius **66.7 mm**; the `tank_copper_shell` inner face sits at radius **70.5 mm**. The radial gap between coil center and `tank_copper_shell` inner face is **3.8 mm** — but that's a center-to-wall distance, not a foam thickness, because the coil is a 6.35 mm-diameter cylinder, not a line.

The foam fills the space between the coil tube's outer surface and the `tank_copper_shell` inner face. That space varies in thickness as you walk around the coil tube's circumference:

| Position on coil circumference | Radial gap to `tank_copper_shell` inner face |
|---|---|
| Outermost line on the coil (closest to the shell) | **0.6 mm** (minimum) |
| 90° around the tube (top or bottom of the coil) | ~3.8 mm |
| Innermost line (against the tank wall) | ~7.0 mm |

So 0.6 mm is the *minimum* gap, not the average. There's a small line on the coil where the foam is 0.6 mm thick, and the foam thickens away from that line.

#### Effective resistance via the shape factor

For a circular pipe sitting near a parallel flat wall through a uniform medium, there's a standard thermal-conduction formula (the "shape factor" for cylinder-to-plane):

R_per_meter_of_pipe = (1 / (2 · π · k)) · acosh(d / a)

where `a` is the pipe radius (3.175 mm), `d` is the pipe-center-to-wall distance (3.775 mm), and `k` is the foam conductivity (0.025 W/m·K). Plugging in: acosh(1.189) = 0.617, R per meter of pipe ≈ **3.93 m·K/W**.

For close-wound coils (pitch ≈ coil OD ≈ 6.35 mm), one wrap of pipe covers 6.35 mm of vertical `tank_copper_shell` height, so R per unit `tank_copper_shell` area = 3.93 · 0.00635 ≈ **0.025 m²·K/W**. That's the foam-zone resistance from the coil's outer surface to the `tank_copper_shell` inner face, accounting for the geometry — equivalent to about 0.6–0.8 mm of uniform foam, not the literal 0.6 mm minimum and not the 7 mm of the bare radial gap.

Coil outer face temperature, which is the cold-side source temperature, swings with compressor state:
- **Compressor running:** R-600a saturating on the suction side ≈ **−5 to −10 °C**.
- **Compressor off:** coil equalizes toward tank water ≈ 2 °C.
- **Duty-cycle averaged:** roughly 0 °C in normal operation. The ESP32 firmware uses 2 °C / 4 °C hysteresis on the tank-wall probe with a hard −8 °C cutout on the suction-line probe, so the coil rarely sits long below −8 °C, but the time-weighted average is well below the tank water temperature.

#### Cold side (per-area resistance, syrup → cold structures)

| Layer | R (m²·K/W) |
|---|---|
| Reservoir wall (PETG, 2 mm) | 0.010 |
| `tank_copper_shell` wall (PETG, 1 mm) | 0.005 |
| Foam zone (shape-factor-effective, close-wound coil, see above) | 0.030 |
| **R_cold total (effective)** | **0.045** |

The PETG layers contribute ~33 % of R_cold (the 1 mm + 2 mm of PETG insulating about as effectively as 0.6 mm of foam). The foam-zone term carries the rest. The 1 mm of `tank_copper_shell` PETG is real and doing real work — it just isn't the bottleneck.

#### Warm side (syrup → kitchen ambient)

| Layer | R (m²·K/W) |
|---|---|
| Reservoir wall (PETG, 2 mm) | 0.010 |
| Bag pocket far wall (PETG, 1 mm) | 0.005 |
| Outer foam (2 lb closed-cell PU, 16 mm) | 0.640 |
| Outer shell wall (PETG, 1 mm) | 0.005 |
| Outer convection (vertical, still cabinet air, h ≈ 5 W/m²·K) | 0.200 |
| **R_warm total** | **0.860** |

#### Equilibrium syrup temperature

The reservoir's centerward face (A_c ≈ 0.042 m²) is the cold side. Its other five faces (far + 2 long sides + top + bottom, A_w ≈ 0.082 m²) are the warm side. Heat in from the warm side balances heat out to the cold side at:

T_syrup = (T_amb · A_w/R_warm + T_cold · A_c/R_cold) / (A_w/R_warm + A_c/R_cold) = (22 · 0.096 + 0 · 0.949) / 1.045 ≈ **2 °C**

The model says the architecture is plausibly **already refrigerator-cold**. The cooling capacity comes from a thin foam layer over a cold copper coil, not from a 7 mm bulk foam layer over a lukewarm tank wall.

#### Implications

1. The earlier "thin the inner foam to reach 4 °C" recipe in this section was wrong — it assumed a 7 mm foam layer that doesn't exist (the copper coil occupies that space). **Disregard it.** Foam thickness is set by `(radial gap) − (coil OD)` and isn't an independent design variable.

2. The dominant risk is now **freeze**, not insufficient chilling. With T_coil dropping to −5 to −10 °C during compressor pulls and only 0.6 mm of foam at the coil-to-`tank_copper_shell` minimum gap, the `tank_copper_shell`'s outer face directly opposite a coil row can fall below 0 °C. Whether syrup actually freezes depends on internal convection, syrup composition (sucralose concentrates have non-zero freezing-point depression but not unlimited), compressor duty cycle, and how tightly the reservoir wall sits against the `tank_copper_shell`.

3. Bladder vs hard reservoir is still not the dominant variable. Replacing 2 mm of PETG (0.010) with 75 µm of LDPE (≈ 0.0002) drops R_cold to 0.035, moving T_syrup by roughly 0.5 °C — colder, not warmer. So the hard reservoir is *less aggressive* on freeze risk than the bladder by a small margin, which is a quiet point in its favor.

4. **Model says 2–5 °C, future.md says 8–15 °C, gap to resolve via instrumentation.** Add a third DS18B20 inside the reservoir during bench testing alongside the existing tank-wall and suction-line probes; the current two probes tell you the cold side, and a syrup-side probe tells you whether the model above is right and whether the actual operating point is above, near, or below freezing.

5. Levers that *do* exist for tuning the operating point:
   - Coil pitch (loosening the wind reduces the at-coil fraction and softens cooling)
   - Compressor hysteresis band (raising the lower bound from 2 °C narrows the pull-down range)
   - Suction-line cutout temperature (currently −8 °C; raising it caps how cold the coil can get)
   - Outer foam thickness (reducing it raises T_syrup; the geometry already budgets 16 mm)

These all live in the foam-bag-shell + firmware architecture, not in the reservoir architecture.

### Condensation

With T_syrup ≈ 2–3 °C and ~0.5 °C of gradient across the 2 mm reservoir wall, the `tank_copper_shell`'s **outer** face (the side facing the reservoir / bag cavity) sits at roughly **2–3 °C** in steady state. Kitchen-air dew point at 22 °C and 50 % RH is ~12 °C. So the `tank_copper_shell`'s outer face is well below dew point any time the kitchen is at indoor temperatures, and any humid air in contact with it will deposit water.

#### What the geometry exposes

After removing the centerward bag-pocket / support-shell wall, the bag/corner-pocket air space wraps around the round side of the `tank_copper_shell`. The air-exposed surface area of the `tank_copper_shell` outer face per side is now roughly the centerward arc of the cavity ≈ **0.04 m²**. A hard reservoir flush against that face removes the air gap (no air, no condensation possible at the contact line); but with finite manufacturing tolerance, some millimeter-scale air gaps remain along that face.

#### Sealed-cavity case (if the cavity is air-tight)

Once the bag/corner-pocket cavity is closed off from kitchen-cabinet air, the cold `tank_copper_shell` outer face pulls humidity out of whatever air was sealed in. The total water available is bounded:

- Cavity air volume: ~1.4 L per side
- Air mass at room conditions: 0.0017 kg
- Absolute humidity at 22 °C, 50 % RH: ~8 g/kg
- Saturated absolute humidity at 2.5 °C: ~4.5 g/kg
- Maximum condensable water: 0.0017 · (8 − 4.5) ≈ **6 mg per cavity**

Six milligrams. A drop. Once it's out of the air, it's done — the air dries to a dew point matching the cold surface, and no further condensation forms. Bladder swap or service events that reintroduce kitchen air repeat the 6 mg deposit each time.

#### Imperfect-seal case (if humid air leaks in continuously)

The current cap-stack relies on **friction-fit corner pins** between `foam_cap` and `outer_shell` (4× 2 mm-radius pins, 6 mm engagement) and between `foam_cap_lid` and `foam_cap`, and on the cured outer-pour foam sitting around them. There's no explicit gasket. **The seal is not specified, and friction-fit pins are not airtight** — kitchen air can diffuse in around the pins, around the lid edges, and through any micro-gaps the foam pour didn't fill.

If humid kitchen air bleeds in continuously, the 6 mg-per-cycle bound becomes a 6 mg-per-time-constant ongoing deposit. Order-of-magnitude estimate: a 1 cm² leak path with mm-scale gap and natural-convection-driven humidity transport could drive grams of water onto the `tank_copper_shell` outer face per month. Over the lifetime of a "lifetime wetted part" reservoir (Plan B intent: years), unbounded. Unless something else removes it (running off, evaporating during compressor-off cycles, etc.), it accumulates.

This argues for **explicit gasketing** somewhere in the cap stack, OR a defined drying mechanism (e.g., desiccant cartridge in the cap, or a compressor-off duty-cycle long enough to evaporate accumulated water back into the cavity air). Neither is currently in the design. Worth flagging as an open architecture question — not a Plan B reservoir question, but the reservoir doesn't get to ignore it because moisture accumulating on the `tank_copper_shell` is moisture sitting against the reservoir's centerward face.

#### Sub-freezing transients → frost

When the compressor is pulling and T_coil is at −5 to −10 °C, the `tank_copper_shell`'s outer face directly opposite a coil row may briefly drop below 0 °C. Any liquid water at that location freezes to the surface; subsequent condensation cycles add more ice. This is the classic freezer-frost mechanism. With a sealed cavity it's bounded (the 6 mg condenses once and freezes once); with an imperfect seal it grows. Frost on the outside of the `tank_copper_shell` doesn't break anything immediately, but it changes thermal coupling over time and is hard to inspect or service without disassembly.

### Can we engineer around the condensation?

#### Increasing the tank_copper_shell radius doesn't help

The shell outer face temperature in steady state is set by where the shell sits in the resistor chain between the coil and the syrup:

T_outer = T_syrup · (1 − R_res_wall / R_cold_total) + T_coil · (R_res_wall / R_cold_total)

This is a weighted average of T_syrup and T_coil. Since T_coil < T_syrup always, **T_outer ≤ T_syrup always**. For refrigerator-level (T_syrup ≤ 5 °C), T_outer ≤ 5 °C — below the ~12 °C kitchen-air dew point, regardless of how thick the inner foam is.

Adding inner foam thickness (= increasing the shell radius beyond what the coil needs) warms both the syrup and the shell outer face by similar amounts. Worked example: pushing R_cold from 0.045 to 0.53 m²·K/W (~10× more inner foam) brings T_syrup up to ~12 °C; T_outer is then also ~12 °C, right at dew point. So the only shell radius that "solves" condensation is the one that gives up refrigerator-level entirely.

#### Firmware buys frost immunity, not condensation immunity

The split matters: liquid condensation drips, evaporates back into cavity air during compressor-off intervals, and is manageable. **Frost** (water condensing at T_outer < 0 °C and freezing) sticks to the surface, accumulates over time, and degrades the thermal coupling.

Frost requires T_outer < 0 °C. Solving the formula above for the minimum coil temperature that keeps T_outer ≥ 0:

T_coil ≥ −T_syrup · (R_cold_total / R_res_wall − 1)

For T_syrup = 2 °C, R_cold_total = 0.045, R_res_wall = 0.010: T_coil ≥ −7 °C.

Currently `future.md:45` specifies a suction-line cutout at −8 °C. **Raising the cutout to −7 or −6 °C buys frost immunity** at the cost of slower pull-down (the coil can't get as cold during pulls, so the tank takes longer to chill back down). For a low-duty cabinet appliance, that tradeoff is usually fine.

Adjacent firmware levers in the same direction:
- Wider tank-water hysteresis (e.g., 3 °C / 5 °C instead of 2 °C / 4 °C): T_coil time-average shifts warmer.
- Minimum compressor-off time long enough for the shell to warm above 0 °C between pulls: any frost that did form during a pull melts to liquid before the next pull.
- Periodic defrost cycle (compressor off for ~hours): standard freezer approach; melts and evaporates accumulated frost. Tank-water temperature rises during defrost, so dispense-pour timing has to accept the warming excursion.

What firmware *cannot* do is push T_outer above the kitchen dew point (~12 °C) while keeping T_syrup at refrigerator-level. That's a math constraint, not a control problem.

#### Smart sensing on top

A humidity sensor in the bag/corner-pocket cavity (SHT4x or similar, ~$5, I²C, fits on the existing bus alongside MPR121 and DS3231) turns "we hope the seal works" into "we can tell if it doesn't":

- Persistent high humidity → flag seal failure to the iOS app.
- Humidity spike after a service event → run an automatic warm-and-dry cycle.
- Cross-check predicted vs observed humidity decay → bound the actual leak rate without disassembly.

Optional addition, not strictly needed, but cheap and informative.

#### The real fix is mechanical

Two options that genuinely close the condensation problem:

1. **Tight reservoir fit + cap-stack gasketing.** Reservoir wall pressed flush against the `tank_copper_shell` outer face removes the air gap at the coldest surface. Explicit silicone gasketing between `foam_cap` / `outer_shell` / `foam_cap_lid` (replacing the current friction-fit corner pins) closes the cabinet-air ingress path. With both, the residual ~6 mg of trapped-air condensation is one-time and bounded.

2. **Replaceable cavity desiccant.** Desiccant cartridge inside the bag/corner-pocket cavity absorbs ongoing moisture from any imperfect seal. Bounds the accumulation between service events. Requires a defined service interval, which a lifetime-wetted-part Plan B reservoir has to address anyway.

Neither is currently specified anywhere in the design. Worth pulling into the cap-stack architecture discussion before promoting Plan B to the main path. Whichever is chosen, **option 1 + firmware frost immunity is probably the smallest change** that gets the architecture into a defensible operating regime: a one-time bounded condensation event, no frost accumulation, no continuous moisture ingress.

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
