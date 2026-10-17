# Complete Industrial faucet PET-GF project

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) is the current planned production project. Its seam and layer-band reference is tagged `faucet-industrial-production-2026-10-14`. The current raised display seat, matching cover and localized cooling require their own physical result; the identified references below retain their original scope. It contains all five rigid parts: Industrial base, shared tip, Industrial cover, above-counter plate and side-down lever replica. The saved project targets Mark1's left hardened standard-flow 0.4 mm nozzle, external PET-GF and Textured PEI. The [accepted seam-fixed Mark2 print](prints/2026-10-13-complete-rear-seam-base-tip-mark2/README.md) uses Mark2's own trim and spool colour.

The [selected recipe](finish-selection.json) uses A2 with Back on the base, tip and mounting plate, rear-center seam enforcement through the base's full rear silhouette and the tip's exposed curved neck, ordinary corner seams on the cover and lever, and E's eight coarse lip layers. The [production approval](prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json) binds the exact base-and-tip print, complete project and source meshes. The other three rigid parts retain the [accepted complete-print reference](prints/2026-10-13-a2-back-mark2/physical-result.json). Black and white use the same rigid geometry; the TPU gasket and lever sleeve, PET-GF organizer and steel under-counter plate are separate parts.

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

The display seat and bezel have 1.50 mm additional outward clearance over the
flavor tubes, giving 1.80064 mm nominal hardware clearance. The neck snap
datums are fixed. The cover also retains 0.50 mm longer wings and matching arch headroom with the retaining-lip datum preserved. The [geometry review](prints/2026-10-11-centered-mounting-review-mark2/geometry-review.json) compares current meshes with the embedded meshes of the [accepted complete print](physical-acceptance.json), and binds the current [assembly readings](geometry-check.json) and [cover readings](display-cover-check.json). That comparison applies to its identified meshes. The [current display-clearance reading](../sculpted/prints/2026-10-17-localized-cooling-display-clearance-mark2/display-clearance.json) binds the raised pads and bezel, fixed snap datums and 1.80064 mm nominal flavor-tube clearance. The bearing-pad inner walls meet the existing open channel.

One foot modifier supplies 100% zigzag infill and inherits the ordinary wall settings, with base Arachne and 15% infill/wall overlap. The [native box-face reading](prints/2026-10-11-infill-only-reinforcement-review/box-face-wall-review.json) finds zero artificial outer wall through material at the modifier faces. The existing three insert-host/root volumes are retained.

## Selected printing process

The first bed layer is 0.20 mm and normal model layers are 0.24 mm. The base retains eight 0.24 mm layers from the last-starting supported lip, nozzle Z15.32–17.00 mm, before the first 0.12 mm layer at Z17.12 mm. Base-only fine ranges are Z17.00–29.00 and Z55.16–68.12 mm; the lower shoulder deliberately retains its coarse starting portion.

| Parts | Seam position | Ordinary seam gap | Scarf |
| --- | --- | --- | --- |
| Base, shared tip, above-counter mounting plate | Back | 150% | A2: 60 mm length, 0% scarf gap |
| Display cover, lever | Aligned | 15% | Off; petgf.3mf corner defaults |

A2 retains 10% layer-relative start height, ten steps, smart application at 155°,
inner-wall scarf and partial-loop mode. Wipe is off. The [rear-center seam enforcement](seam-placement/rear-center-v2/README.md) follows the full base silhouette and exposed curved tip. Native lateral start offsets are at most 0.543 mm on the base and 0.188 mm on the curved tip; the mounting rim starts at X=0. Base Arachne and the infill-only
solid foot are retained; the other objects use Classic.

The saved process uses two global walls, 15% grid infill, 265/280 °C nozzle temperatures
and an 80 °C bed. All five rigid parts receive native **125% bridge flow,
15 mm/s bridges, and overhang limits at most 15 mm/s**, retaining the existing
10 mm/s fully overhung-wall limit. The [localized PET-GF cooling policy](../../cooling/README.md)
keeps ordinary part and auxiliary cooling off. After three fan-off bed layers,
bridges and walls meeting the 50% overhang threshold receive 70% cooling.
Fan-always-on and pre-start are off. Ordinary supported-wall and infill speeds
retain their saved settings. The identified earlier
[whole-project reading](overhang-native-review.json) is evidence for its own
archive; current settings require their matching native commands. The
[tip result](../finish-coupons/2026-10-15-tip-fins/mark2/physical-result/physical-result.json)
reports the best observed bottom-side rim appearance, with the opposite side still
rough. The [base result](../finish-coupons/2026-10-14-foot-fins-current-angle/full-annulus/mark1/physical-result/physical-result.json)
reports tighter material and better finish with trees than radial fins. Those
short-section observations do not establish the complete faucet's material finish.

Tree (auto), saved Default style and Bambu's automatic support sections serve the
remaining surfaces:
0.45 mm top gap, 0.30 mm bottom gap, 0.40 mm XY gap, two top interface layers and
0.50 mm interface spacing. The base's visible outer edge receives the exact
seven segmented arc fins and narrow contact-strip blockers from the
[accepted Mark2 result](../finish-coupons/2026-10-15-edge-supports/base-mark2/physical-result/physical-result.json).
Derek reports excellent support, very easy snap-off and the best faucet underside
he has observed. Each wall follows the rim: 0.90 mm width, 41° arcs, 4° release
gaps and a requested 0.24 mm vertical gap. The front arc remains uninterrupted
under the lever. Trees serve the rest of the underside and the arc gaps.

The [arc transfer and native contact reading](rim-support-native-review.json)
binds the exact accepted support meshes to this full-project placement. The
base is translated 3 mm inward on the plate to retain the saved 40 mm native
bead margin; its −15° rotation and support heights are unchanged. The part
geometry, material settings, seams and layer bands are preserved. The tip retains
the exact eight fin walls and hidden-root disc from the
[accepted Mark1 article](../finish-coupons/2026-10-15-tip-root-anchor/mark1/physical-result/physical-result.json).
The seam-side low joint lip receives the accepted local tree enforcers: downward
joint-plane facets below build Z21 and within CAD X ±8 mm. Other joint-plane
facets retain their fin-contact blockers. The 10 × 8 mm bed disc bonds directly
to the terminal male insertion end through its narrow neck. Its removal leaves
a scuff accepted only on that hidden end; keep bonded contact off visible faces.
Edge/underside appearance and release are accepted on the identified base
section; complete-height printing and mating fit with this treatment remain
unreported.

Mark1's standard +0.18 mm requested trim emits +0.16 mm after Textured PEI compensation. Mark2 uses its own +0.04/+0.02 mm standard trim when explicitly selected. Timelapse and leveling are On; flow dynamic and nozzle offset calibration are Auto. Probing clump detection remains disabled.

The current Industrial editable project is prepared; its matching complete native
slice is pending. The [seam-path reference](prints/2026-10-13-a2-back-mark2/seam-path-review.json) checks
the scarfed parts and plain cover/lever corners on its identified print. The
[physical production approval](prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json)
retains its exact seam-fixed print and material scope.

The [complete two-printer run](prints/2026-10-15-all-learnings/README.md) contains
one of each rigid part: the base with rim arcs on Mark2 and the tip with its
accepted supports, cover, rigid plate and lever on Mark1. Its individual native
slices and launch receipts bind each printer's own trim, spool colour and placement.

## Support cleanup and evidence

The [support review](prints/2026-10-11-centered-mounting-review-mark2/support-review.json) compares the accepted and current native support locations. It includes small bodies without explicit interface labels; their contact count and build-up remain unknown where Bambu supplies no interface feature.

| Part | Cleanup access |
| --- | --- |
| Base | Counter end, common rear opening, donor bay and lever opening. Fragment sacrificial stock; clear insert pilots and pedestal sockets while retaining their bearing faces. The lower passage and lever-roof section views locate actual support paths. |
| Tip | Open curved joint, display pocket and dispense openings. Fragment internal support stock through those openings before closing the joint and fitting the display. The Ø4 mm drip hole is not a large cleanup port. |
| Cover | Open underside before fitting the display; preserve wings and lip-bearing faces. |
| Plate | Open screw-head recesses; preserve their seats. |
| Lever | Side-down pose with open external cleanup access. |

The current [production acceptance](prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json) and tag `faucet-industrial-production-2026-10-14` identify the seam-fixed model. The [shipping acceptance](physical-acceptance.json) and tag `faucet-industrial-shipping-2026-10-10`, and the centered complete print's [acceptance record](prints/2026-10-13-a2-back-mark2/physical-result.json) and tag `faucet-industrial-approved-2026-10-13`, retain their identified physical scope. Native paths and CAD clearances do not establish adhesion, cleanup force, fault discharge, strength or lifetime. Physical results belong in the [print log](print-log.md).

## Offline preparation

After generating and reviewing the source STLs:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prepare_print_project.py
```

The tool rebuilds all five current parts with the inherited PET-GF profile, continuous foot reinforcement, [selected per-part finish and overhang treatment](finish-selection.json). The default target is Mark1; `--printer Mark2 --filament-colour '#161616'` applies Mark2's own trim and the specified spool colour. Verify the actual destination spool before use. Its optional `--slice-output` runs Bambu locally without a printer connection. The [preparation](faucet-industrial-petgf.print.json) and [native support audit](faucet-industrial-petgf.support-audit.json) bind the per-part settings, source meshes, shoulder bands and placement. The [readiness record](faucet-industrial-petgf.readiness.json) binds the project and review files. No preparation or review tool submits a print.
