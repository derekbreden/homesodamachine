# Cartridge and cap support review

The current cartridge and matching cap are printing on Mark2 as task `1279835918`.
The cartridge stands on its flat underside and the cap prints crown-down. Both
use black PET-GF on the left 0.4 mm nozzle. The exact native plate contains the
current STEP/STL geometry and passes its layer, support-contact and path-clearance
checks. Estimated time is **13 h 35 m 37 s** across **1088 plate layers**.

The first layer is 0.20 mm. The cartridge's complete grip-floor rounds use 0.08 mm
layers at print Z 6–18.4 mm, and its complete grip-ceiling rounds at Z 100.3–113.2 mm.
The remaining model, including the cap, uses 0.24 mm. Six walls apply only to the
upper grip-round band; the normal setting is two walls. Wall order, speeds,
accelerations, temperatures and cooling retain the saved pump profile, with
15% infill/wall overlap. Requested Mark2 trim is +0.04 mm, emitted +0.02 mm for
Textured PEI.

**The visible rounded grip surfaces have no support contacts.** Painted blockers
cover the downward rounds and extend 0.8 mm onto the adjoining flat ceilings to
keep the support bead width clear of the curve. The native contact check includes
all upper Support, Support transition and Support interface paths, full bead
width and a 0.05 mm XY allowance. No support road approaches a downward round
within 0.60 mm vertically. The two ceiling interfaces fit entirely within the
flat ceiling projections.

| Piece / support | Contact region | Root | Build-up | Removal lane before hardware installation |
| --- | --- | --- | --- | --- |
| Cartridge west | Flat hand-pull ceiling, inset from its rounded border | Bed | 106.07 mm | Detach the interface and withdraw through the open −X pocket mouth |
| Cartridge east | Flat hand-pull ceiling, inset from its rounded border | Bed | 106.07 mm | Detach the interface and withdraw through the open +X pocket mouth |
| Cap west motor opening | Flat terminal-well annulus | Bed | 4.08 mm | Withdraw through the open Ø45 mm well toward the original +Z crown |
| Cap east motor opening | Flat terminal-well annulus | Bed | 4.08 mm | Withdraw through the open Ø45 mm well toward the original +Z crown |
| Cap aft screw | Flat screw-head seat | Bed | 14.16 mm | Withdraw through the open head counterbore in original +Z |
| Cap fore screw | Flat screw-head seat | Bed | 14.16 mm | Withdraw through the open head counterbore in original +Z |

Remove supports while both parts are loose, before installing pumps, wires or
screws. The screw-seat support leaves through the head counterbore. The six bodies
and six interface islands describe the slice; there are no extra unlabelled
support bodies. Physical finish, removal effort and assembled fit are not yet
assessed for this print.

The [native review and launch record](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-pump-cartridge-cap-mark2-v8/README.md)
binds the source geometry, exact archive, support contacts and removal lanes.
