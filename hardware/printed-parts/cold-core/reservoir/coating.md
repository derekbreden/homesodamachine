# Reservoir Interior Coating

The printed PETG reservoir cavity carries a one-time food-contact epoxy film, applied via sealed-cavity rotomold during build. The film seals FDM layer-line porosity and converts the wetted surface from print roughness to cured-epoxy smoothness.

Coating: **MAX CLR A/B** — FDA 21 CFR 175.300 compliant epoxy marketed for direct food-contact use on 3D-printed plastics.

## Floor + bulkhead port geometry

The cavity floor is a Y-symmetric V: both ±Y walls slope inward to a flat circular pad at y=0 that hosts the bulkhead port. The bulkhead — JG PP1208E 1/4" PTC, same SKU as the rear-panel umbilical — clamps vertically through the pad. Its integral flange seats on a wet-side TPU face seal in a horizontal counterbore in the cavity floor; the nut threads on from below in the bag-pocket cavity under the floor. The wet-side PTC port faces up into the cavity; the dry collet hangs straight down, where a JG PP0308E 1/4" PTC 90° elbow (same SKU already in the BOM for the CO2 in-cavity bend) turns the line laterally to exit the bag-pocket +Y pass-through.

The nut sits in a hex pocket below the floor in the bag-pocket cavity, reached from outside the reservoir during install (the bag pocket itself is open to the assembly side at this stage).

Syrup drains by gravity from anywhere in the cavity down the V to the central pad and into the bulkhead port. The lowest drainable line is the bulkhead's wet port axis; residual film below that line stays in the bulkhead body itself.

## Coating procedure

The reservoir ships out of this procedure fully assembled with the cured coating in place.

1. **Pre-assemble**: body + bulkhead + bulkhead TPU face seal + nut from below + dry-side LLDPE tube + PP0308E elbow + tube run out through the bag-pocket pass-through. Everything wet-side except the cap.
2. **Plug the bulkhead's wet-side PTC port** from inside the cavity with a sacrificial 1/4" OD LLDPE cutoff (~150 mm). The wet-side collet teeth grip it; the bulkhead is now closed at both ends.
3. **Pour ~40 mL of MAX CLR A/B** (mixed 1:1, ~25 min working time at room temp) into the cavity through the open top.
4. **Bolt the blanking cap** on through a sacrificial TPU gasket. Cavity sealed for rotation.
5. **Rotomold**: mount in a BBQ rotisserie motor at ~4 rpm. Tip through the perpendicular axis every 2 min for the first 15 min, until rising viscosity stops further redistribution.
6. **Park** the assembly upright with the most-recently-coated wall horizontal, so initial-cure sag flows across already-coated film instead of draining off uncoated surface.
7. **Cure** 24 h at room temperature.
8. **Open** the blanking cap. Push the bulkhead's wet-side release ring, pull the sacrificial tube out. The tube-shaped hole through the cured film at the bulkhead's o-ring location is the syrup path.
9. **Final assembly**: install the float rod into its body + cap bores, install the PTFE membrane + TPU retaining ring in the production cap's vent pocket, bolt the production cap on through a fresh TPU gasket.

## Blanking cap

The blanking cap is a flat-underside PETG print with the production cap's outer envelope and 6-hole screw pattern but none of the production cap's interior features (no vent boss, no rod register, no splash baffle). It seals the cavity during the rotomold coat. After the cure, it comes off, the sacrificial tube comes out, and the production cap installs as the last step of dry assembly through a fresh TPU gasket. The blanking cap is tooling — one print serves every reservoir built.

## Bulkhead-side residuals

The bulkhead's wet-side flange face and release-ring outer face sit in the coating's reach. The release-ring outer face takes a coating layer that cracks at the ring's travel boundary the first time the wet-side tube is released — cosmetic, not functional.

The PP/acetal flange face inside the cavity bonds epoxy mechanically, not chemically, and may delaminate over service life. If it does, the exposed flange is the bulkhead's own NSF 51 + NSF 61 PP, itself food-contact.

The TPU face seal between the bulkhead flange and the floor counterbore is below the coating film. The film spans the flange-edge-to-counterbore-rim joint at the wet-side surface; the seal underneath does the fluid-barrier work.

## Materials

| Item | Notes | Per build |
|---|---|---|
| MAX CLR A/B epoxy resin kit | FDA 21 CFR 175.300 compliant for direct food-contact use on 3D-printed plastics | ~80 mL (40 mL × 2 reservoirs); a 48 fl oz kit covers ~17 builds |
| Sacrificial 1/4" OD LLDPE tube cutoff | from existing JG LLDPE inventory | ~300 mm (~150 mm × 2 reservoirs) |
| Sacrificial TPU gasket | printed from the same TPU 85A stock as the production gasket | 2 (one per reservoir during coat) |
| Blanking cap | tooling — PETG print, one reusable across every build | 1 |
| BBQ rotisserie motor, ~4 rpm AC | tooling | 1 |

## Open items

- [ ] **CAD update**: rewrite the bulkhead pocket + floor wedge in [`reservoir.py`](reservoir.py) for the V-slope-to-center floor + vertical-through-floor bulkhead. Files affected: `reservoir.py` (the `bulkhead_*` constants, `floor_baseline_z`, slope/wedge logic, and the bulkhead pocket section of `build_reservoir_body`) and [`../_cold_core_interface.py`](../_cold_core_interface.py) (`reservoir_bulkhead_port_*`, `reservoir_bulkhead_nut_z`).
- [ ] **Blanking cap CAD**: add `build_reservoir_blanking_cap()` to [`reservoir.py`](reservoir.py); export `reservoir-blanking-cap.step`.
- [ ] **Adhesion bench test**: SunTop PETG scrap with light abrasion + IPA wipe, MAX CLR A/B film, 24 h cure, flex/scratch test. Green-lights the procedure or sends it back.
- [ ] **Single-reservoir pilot**: print one reservoir under the new geometry, full-assemble, run the rotomold coat once, cut in half on the band saw, inspect film thickness at inner fillets and around the bulkhead annulus. Commit-or-revise decision point before doing the second reservoir.
- [ ] **Cure exotherm check**: confirm thin-film exotherm peak stays well below PETG's ~80 °C Tg before locking in the procedure.
- [ ] **Source MAX CLR A/B** on Prime; record the purchase event in [`../../../purchases.md`](../../../purchases.md).
- [ ] **Rotisserie rig**: select + source the rotisserie motor and a spit-fork or chuck mount sized for the reservoir on Prime.
- [ ] **BOM**: per-build line for MAX CLR A/B portion + sacrificial gasket in [`../../../bom.md`](../../../bom.md); blanking cap as tooling, not per-build.
