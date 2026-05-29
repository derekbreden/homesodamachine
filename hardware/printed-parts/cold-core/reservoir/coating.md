# Reservoir Interior Coating

The printed PETG reservoir cavity carries a one-time food-contact epoxy film, applied via sealed-cavity rotomold during build. The film seals FDM layer-line porosity and converts the wetted surface from print roughness to cured-epoxy smoothness.

Coating: **Craft Resin "Arts & Crafts" crystal-clear epoxy** (1400 cps, 1:1 mix, ~40 min work time, 24 h cure; Amazon [B083SRX7TJ](https://www.amazon.com/dp/B083SRX7TJ) 1 gal / [B07YCVVYFK](https://www.amazon.com/dp/B07YCVVYFK) 34 oz), marketed food-grade when cured. The medium 1400 cps viscosity is the rotomold fit: it flows into the corners and trough as the sealed part is rotated, yet builds a film and gels before it drains off the vertical walls. The lower-viscosity deep-pour grade sheets off the walls; the higher-viscosity table-top grade is too thick to redistribute in rotation (that grade is the brush choice).

## Floor + bulkhead port geometry

The cavity floor is a Y-symmetric V swept across the full cavity X width: from each ±Y wall the floor slopes inward and down to a flat rectangular trough at y=0 that spans the full interior X width and hosts the bulkhead port. The floor is a single Y–Z section — slope down, flat, slope up — extruded straight across X; the only curved floor boundary is the cavity's existing centerward arc. The bulkhead — PureSec 1/4" RO push-to-connect 90° elbow bulkhead ([B0968K4JRN](https://www.amazon.com/dp/B0968K4JRN)), white PP, water/RO-rated — clamps vertically through the trough: its threaded barrel passes down through the trough floor and a locknut threads on from below in the bag-pocket cavity. The wet-side PTC port faces up into the cavity; the integral 90° elbow on the dry side turns the line laterally below the floor toward the bag-pocket +Y pass-through, so no separate union elbow is needed. A TPU face seal in a shallow counterbore on the wet-side trough floor seals the barrel-to-floor joint (the PureSec ships without a panel o-ring, so the printed TPU washer supplies it); the part wants a ⌀16 mm mounting hole.

The nut sits in a hex pocket below the floor in the bag-pocket cavity, reached from outside the reservoir during install (the bag pocket itself is open to the assembly side at this stage).

Syrup drains by gravity from anywhere in the cavity down the V to the central trough and into the bulkhead port. The lowest drainable line is the bulkhead's wet port axis; residual film below that line stays in the bulkhead body itself.

## Coating procedure

The reservoir ships out of this procedure fully assembled with the cured coating in place.

1. **Pre-assemble**: body + bulkhead + bulkhead TPU face seal + locknut from below + the dry-side LLDPE tube pushed into the bulkhead's integral 90° elbow + the tube run out through the bag-pocket pass-through. Everything except the cap.
2. **Plug the bulkhead's wet-side PTC port** from inside the cavity with a sacrificial 1/4" OD LLDPE cutoff (~150 mm). The wet-side collet teeth grip it; the bulkhead is now closed at both ends.
3. **Pour ~40 mL of Craft Resin Arts & Crafts epoxy** (mixed 1:1, ~40 min work time at room temp) into the cavity through the open top.
4. **Bolt the blanking cap** on through a sacrificial TPU gasket. Cavity sealed for rotation.
5. **Rotomold**: mount in a BBQ rotisserie motor at ~4 rpm. Tip through the perpendicular axis every 2 min for the first 15 min, until rising viscosity stops further redistribution.
6. **Park** the assembly upright with the most-recently-coated wall horizontal, so initial-cure sag flows across already-coated film instead of draining off uncoated surface.
7. **Cure** 24 h at room temperature.
8. **Open** the blanking cap. Push the bulkhead's wet-side release ring, pull the sacrificial tube out. The tube-shaped hole through the cured film at the wet-side port mouth is the syrup path.
9. **Final assembly**: install the float rod into its body + cap bores, install the PTFE membrane + TPU retaining ring in the production cap's vent pocket, bolt the production cap on through a fresh TPU gasket.

## Blanking cap

The blanking cap is a flat-underside PETG print with the production cap's outer envelope and 6-hole screw pattern but none of the production cap's interior features (no vent boss, no rod register, no splash baffle). It seals the cavity during the rotomold coat. After the cure, it comes off, the sacrificial tube comes out, and the production cap installs as the last step of dry assembly through a fresh TPU gasket. The blanking cap is tooling — one print serves every reservoir built.

## Bulkhead-side residuals

The bulkhead's wet-side flange face and release-ring outer face sit in the coating's reach. The release-ring outer face takes a coating layer that cracks at the ring's travel boundary the first time the wet-side tube is released — cosmetic, not functional.

The PureSec PP shoulder face inside the cavity bonds epoxy mechanically, not chemically, and may delaminate over service life. If it does, the exposed face is the bulkhead's own water/RO-rated PP, itself food-contact.

The TPU face seal between the bulkhead shoulder and the floor counterbore is below the coating film. The film spans the flange-edge-to-counterbore-rim joint at the wet-side surface; the seal underneath does the fluid-barrier work.

## Materials

| Item | Notes | Per build |
|---|---|---|
| Craft Resin "Arts & Crafts" crystal-clear epoxy (1400 cps) | marketed food-grade when cured; production [B083SRX7TJ](https://www.amazon.com/dp/B083SRX7TJ) 1 gal, bench-test [B07YCVVYFK](https://www.amazon.com/dp/B07YCVVYFK) 34 oz | ~80 mL (40 mL × 2 reservoirs); 34 oz ≈ 12 builds, 1 gal ≈ 47 builds |
| Sacrificial 1/4" OD LLDPE tube cutoff | from existing JG LLDPE inventory | ~300 mm (~150 mm × 2 reservoirs) |
| Sacrificial TPU gasket | printed from the same TPU 85A stock as the production gasket | 2 (one per reservoir during coat) |
| Blanking cap | tooling — PETG print, one reusable across every build | 1 |
| BBQ rotisserie motor, ~4 rpm AC | tooling | 1 |

## Open items

- [ ] **CAD: adjust the bulkhead port to PureSec B0968K4JRN measurements**. The full-width-trough V floor + vertical-through-floor port is on `main`, but modeled to the JG PP1208E body (⌀17.5 panel hole, JG locknut hex). Adjust to the PureSec: ⌀16 mm mounting hole, its locknut/thread dimensions, an added-TPU-washer seal seat on the wet-side trough floor, and lateral clearance below the floor for the integral 90° elbow body. Best-estimate measurements from the listing/photos/similar RO 90° bulkheads are fine — do not wait for the part to arrive. Files: `reservoir.py` (`bulkhead_*` constants, the bulkhead-port section of `build_reservoir_body`) and [`../_cold_core_interface.py`](../_cold_core_interface.py) (`reservoir_bulkhead_port_*`).
- [ ] **Blanking cap CAD**: add `build_reservoir_blanking_cap()` to [`reservoir.py`](reservoir.py); export `reservoir-blanking-cap.step`.
- [ ] **Adhesion bench test**: SunTop PETG scrap with light abrasion + IPA wipe, Craft Resin epoxy film, 24 h cure, flex/scratch test. Green-lights the procedure or sends it back. (34 oz test kit on hand — arriving 2026-05-29.)
- [ ] **Single-reservoir pilot**: print one reservoir under the new geometry, full-assemble, run the rotomold coat once, cut in half on the band saw, inspect film thickness at inner fillets and around the bulkhead annulus. Commit-or-revise decision point before doing the second reservoir.
- [ ] **Cure exotherm check**: confirm thin-film exotherm peak stays well below PETG's ~80 °C Tg before locking in the procedure.
- [x] **Epoxy sourced**: Craft Resin "Arts & Crafts" crystal-clear epoxy, 34 oz bench-test kit ([B07YCVVYFK](https://www.amazon.com/dp/B07YCVVYFK)), bought 2026-05-28; recorded in [`../../../purchases.md`](../../../purchases.md) §5. Production size is the 1 gal ([B083SRX7TJ](https://www.amazon.com/dp/B083SRX7TJ)).
- [ ] **Rotisserie rig**: select + source the rotisserie motor and a spit-fork or chuck mount sized for the reservoir on Prime.
- [ ] **BOM**: sacrificial-gasket per-build line still to add in [`../../../bom.md`](../../../bom.md) (the epoxy coating per-build line is in §8; blanking cap is tooling, not per-build).
