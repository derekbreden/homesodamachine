# Complete Industrial faucet PET-GF project

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains all five current rigid parts: Industrial base, shared tip, Industrial cover, above-counter plate and side-down lever replica. The saved project targets Mark1's left hardened standard-flow 0.4 mm nozzle, external PET-GF and Textured PEI. The [current Mark2 print](prints/2026-10-13-a2-back-mark2/README.md) uses the same geometry and process with Mark2's own trim and spool colour.

The [selected recipe](finish-selection.json) uses A2 with Back on the base, tip and mounting plate, ordinary corner seams on the cover and lever, and E's eight coarse lip layers. The exact [launch record](prints/2026-10-13-a2-back-mark2/launch.json) binds the current print. The [physical inspection](prints/2026-10-13-a2-back-mark2/physical-result.json) accepts the identified print as the best faucet so far, with a known rear seam wobble. Black and white use the same rigid geometry; the TPU gasket and lever sleeve, PET-GF organizer and steel under-counter plate are separate parts.

| Position | Part | CAD X rotation |
| --- | --- | ---: |
| Left | Industrial shell base | −15° |
| Rear center | Shared faucet shell tip | −105° |
| Rear right | Industrial display cover | −50° |
| Front right | Industrial above-counter plate | 0° |
| Front center | Side-down lever replica | 0° of its print-oriented STL |

## Geometry and assembly

The lower passages, rigid plate and gasket use the centered mounting layout and measured 4.6 × 1.18 mm ribbon. Install the matching [18.15 × 7.25 mm steel rear opening](../../../cut-parts/faucet/under-counter-plate/README.md). The [mounting review](../../../cut-parts/faucet/under-counter-plate/centered-layout-check.json) binds nominal clearances and slide access. The identified complete print has reported overall acceptance; numerical assembly forces are unmeasured.

The curved joint is at 70°, with a female base and male tip and 20/18 mm overlap. Smooth tangent walls surround the tube and flat ribbon passages. The flavor pair shares a capsule without a central divider or outlet cusp. The drain ends square with 3 mm of local mouth clearance and an unsealed Ø4 mm underside fault-drip hole. The tip's hole cutter reaches 0.60 mm inward of the soda-clearance wall. No intermediate guide discs, drain bung or insertion tool are fitted.

The cover has 0.50 mm longer wings and matching arch headroom with the retaining-lip datum preserved. The [geometry review](prints/2026-10-11-centered-mounting-review-mark2/geometry-review.json) compares current meshes with the embedded meshes of the [accepted complete print](physical-acceptance.json), and binds the current [assembly readings](geometry-check.json) and [cover readings](display-cover-check.json). The upper base, cover and lever retain the accepted surfaces within the stated sampled comparison. Source review confines tip changes to the fault-drip cut and mesh cleanup.

One foot modifier supplies 100% zigzag infill and inherits the ordinary wall settings, with base Arachne and 15% infill/wall overlap. The [native box-face reading](prints/2026-10-11-infill-only-reinforcement-review/box-face-wall-review.json) finds zero artificial outer wall through material at the modifier faces. The existing three insert-host/root volumes are retained.

## Selected printing process

The first bed layer is 0.20 mm and normal model layers are 0.24 mm. The base retains eight 0.24 mm layers from the last-starting supported lip, nozzle Z15.32–17.00 mm, before the first 0.12 mm layer at Z17.12 mm. Base-only fine ranges are Z17.00–29.00 and Z55.16–68.12 mm; the lower shoulder deliberately retains its coarse starting portion.

| Parts | Seam position | Ordinary seam gap | Scarf |
| --- | --- | --- | --- |
| Base, shared tip, above-counter mounting plate | Back | 150% | A2: 60 mm length, 0% scarf gap |
| Display cover, lever | Aligned | 15% | Off; petgf.3mf corner defaults |

A2 retains 10% layer-relative start height, ten steps, smart application at 155°,
inner-wall scarf and partial-loop mode. Wipe is off. Base Arachne and the infill-only
solid foot are retained; the other objects use Classic.

The saved process uses two global walls, 15% grid infill, 265/280 °C nozzle temperatures, 80 °C bed temperature and 0–70% part cooling, with an 80% short-layer maximum and no part cooling for the first three layers. Tree (auto), saved Default style and Bambu's automatic support sections are retained: 0.45 mm top gap, 0.30 mm bottom gap, 0.40 mm XY gap, two top interface layers and 0.50 mm interface spacing. There are no support blockers or manual normal-support overrides.

Mark1's standard +0.18 mm requested trim emits +0.16 mm after Textured PEI compensation. Mark2 uses its own +0.04/+0.02 mm standard trim when explicitly selected. Timelapse and leveling are On; flow dynamic and nozzle offset calibration are Auto. Probing clump detection remains disabled.

The current Mark2 native estimate is 6 h 5 min 55 s, recorded with the source hashes, unchanged layer bands and effective per-part settings in the [native review](prints/2026-10-13-a2-back-mark2/native-review.json). The [seam-path reading](prints/2026-10-13-a2-back-mark2/seam-path-review.json) checks the scarfed parts and the plain cover/lever corners. The complete printed article has [overall acceptance](prints/2026-10-13-a2-back-mark2/physical-result.json), with the rear seam wobble recorded.

## Support cleanup and evidence

The [support review](prints/2026-10-11-centered-mounting-review-mark2/support-review.json) compares the accepted and current native support locations. It includes small bodies without explicit interface labels; their contact count and build-up remain unknown where Bambu supplies no interface feature.

| Part | Cleanup access |
| --- | --- |
| Base | Counter end, common rear opening, donor bay and lever opening. Fragment sacrificial stock; clear insert pilots and pedestal sockets while retaining their bearing faces. The lower passage and lever-roof section views locate actual support paths. |
| Tip | Open curved joint, display pocket and dispense openings. Fragment internal support stock through those openings before closing the joint and fitting the display. The Ø4 mm drip hole is not a large cleanup port. |
| Cover | Open underside before fitting the display; preserve wings and lip-bearing faces. |
| Plate | Open screw-head recesses; preserve their seats. |
| Lever | Side-down pose with open external cleanup access. |

The [shipping acceptance](physical-acceptance.json) and tag `faucet-industrial-shipping-2026-10-10` identify the complete physical reference. That article retains reported separation of the first model layer above supports and a visible seam. The centered complete print has its own [acceptance record](prints/2026-10-13-a2-back-mark2/physical-result.json) and tag `faucet-industrial-approved-2026-10-13`. Native paths and CAD clearances do not establish adhesion, cleanup force, fault discharge, strength or lifetime. Physical results belong in the [print log](print-log.md).

## Offline preparation

After generating and reviewing the source STLs:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prepare_print_project.py
```

The tool rebuilds all five current parts with the inherited PET-GF profile, continuous foot reinforcement and [selected per-part finish](finish-selection.json). The default target is Mark1; `--printer Mark2 --filament-colour '#161616'` applies Mark2's own trim and the specified spool colour. Verify the actual destination spool before use. Its optional `--slice-output` runs Bambu locally without a printer connection. The [current native reading](prints/2026-10-13-a2-back-mark2/native-review.json) binds the launched snapshot, per-part settings, source meshes, shoulder bands and placement. The [readiness record](faucet-industrial-petgf.readiness.json) binds the project and review files. No preparation or review tool submits a print.
