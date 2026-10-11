# Complete Industrial faucet PET-GF project

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains all five current rigid parts: Industrial base, shared tip, Industrial cover, above-counter plate and side-down lever replica. The [current preparation and native review](prints/2026-10-11-centered-mounting-review-mark2/README.md) are for Mark2's left hardened standard-flow 0.4 mm nozzle, external PET-GF and Textured PEI.

Final seam/scarf and coarse-layer choices above supports await the [combined coupon result](../finish-coupons/coarse-start-v1/combined/README.md). This project is preparation only. Black and white use the same rigid geometry; the TPU gasket and lever sleeve, PET-GF organizer and steel under-counter plate are separate parts.

| Position | Part | CAD X rotation |
| --- | --- | ---: |
| Left | Industrial shell base | −15° |
| Rear center | Shared faucet shell tip | −105° |
| Rear right | Industrial display cover | −50° |
| Front right | Industrial above-counter plate | 0° |
| Front center | Side-down lever replica | 0° of its print-oriented STL |

## Geometry and assembly

The lower passages, rigid plate and gasket use the centered mounting layout and measured 4.6 × 1.18 mm ribbon. Install the matching [18.15 × 7.25 mm steel rear opening](../../../cut-parts/faucet/under-counter-plate/README.md). The [mounting review](../../../cut-parts/faucet/under-counter-plate/centered-layout-check.json) binds nominal clearances and slide access. The centered mounting set has no physical fit acceptance.

The curved joint is at 70°, with a female base and male tip and 20/18 mm overlap. Smooth tangent walls surround the tube and flat ribbon passages. The flavor pair shares a capsule without a central divider or outlet cusp. The drain ends square with 3 mm of local mouth clearance and an unsealed Ø4 mm underside fault-drip hole. The tip's hole cutter reaches 0.60 mm inward of the soda-clearance wall. No intermediate guide discs, drain bung or insertion tool are fitted.

The cover has 0.50 mm longer wings and matching arch headroom with the retaining-lip datum preserved. The [geometry review](prints/2026-10-11-centered-mounting-review-mark2/geometry-review.json) compares current meshes with the embedded meshes of the [accepted complete print](physical-acceptance.json), and binds the current [assembly readings](geometry-check.json) and [cover readings](display-cover-check.json). The upper base, cover and lever retain the accepted surfaces within the stated sampled comparison. Source review confines tip changes to the fault-drip cut and mesh cleanup.

One continuous foot modifier supplies six walls and 100% zigzag infill, with base Arachne and 15% infill/wall overlap. The [native check](prints/2026-10-11-centered-mounting-review-mark2/native-check.json) finds no reinforcement-partition starts/stops at the three reported screw-host exterior defect sites. The [insert deposition reading](faucet-industrial-petgf.insert-beads.json) retains the three host/root regions and their commanded backing stock.

## Provisional process

The frozen recipe from the accepted complete print supplies the baseline: 0.20 mm first bed layer, 0.24 mm normal model layers and base-only 0.12 mm bands at print Z13.40–29.00 and Z55.16–68.12 mm. The native review checks that both selected annular shoulders lie within those bands. Seam/scarf and the number of coarse model layers above supports are pending physical coupon choices.

The saved process uses two global walls, 15% grid infill, 265/280 °C nozzle temperatures, 80 °C bed temperature and 0–70% part cooling, with an 80% short-layer maximum and no part cooling for the first three layers. Tree (auto), saved Default style and Bambu's automatic support sections are retained: 0.45 mm top gap, 0.30 mm bottom gap, 0.40 mm XY gap, two top interface layers and 0.50 mm interface spacing. There are no support blockers or manual normal-support overrides.

Mark2's +0.04 mm requested trim emits +0.02 mm after Textured PEI compensation. Timelapse and leveling are On; flow dynamic and nozzle offset calibration are Auto. Probing clump detection remains disabled.

The provisional native estimate is **5 h 54 min 2 s** and **161.90 g** at the saved profile density. All emitted model/support/brim beads retain at least **44.86 mm** of usable-bed clearance. Final finish choices require a fresh native slice and a review of the paths those choices affect.

## Support cleanup and evidence

The [support review](prints/2026-10-11-centered-mounting-review-mark2/support-review.json) compares the accepted and current native support locations. It includes small bodies without explicit interface labels; their contact count and build-up remain unknown where Bambu supplies no interface feature.

| Part | Cleanup access |
| --- | --- |
| Base | Counter end, common rear opening, donor bay and lever opening. Fragment sacrificial stock; clear insert pilots and pedestal sockets while retaining their bearing faces. The lower passage and lever-roof section views locate actual support paths. |
| Tip | Open curved joint, display pocket and dispense openings. Fragment internal support stock through those openings before closing the joint and fitting the display. The Ø4 mm drip hole is not a large cleanup port. |
| Cover | Open underside before fitting the display; preserve wings and lip-bearing faces. |
| Plate | Open screw-head recesses; preserve their seats. |
| Lever | Side-down pose with open external cleanup access. |

The [shipping acceptance](physical-acceptance.json) and tag `faucet-industrial-shipping-2026-10-10` identify the complete physical reference. That article retains reported separation of the first model layer above supports and a visible seam. Its acceptance does not establish physical fit of the centered mounting set. Native paths and CAD clearances do not establish adhesion, cleanup force, fault discharge, strength or lifetime. Physical results belong in the [print log](print-log.md).

## Offline preparation

After generating and reviewing the source STLs:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prepare_print_project.py
```

The tool rebuilds all five parts with current meshes, the accepted profile, one continuous foot modifier and the accepted provisional layer bands. Its optional `--slice-output` runs Bambu locally without a printer connection. The manually requested [review reader](prints/2026-10-11-centered-mounting-review-mark2/review.py) records retained native meshes, emitted settings, first/second-layer contact, shoulder bands, screw-site contours, support topology and insert stock. The [readiness record](faucet-industrial-petgf.readiness.json) binds the project and review files. No preparation or review tool submits a print.
