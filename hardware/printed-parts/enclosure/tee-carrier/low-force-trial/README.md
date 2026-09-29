# Tee-carrier low-force sliding trial

One complete carrier for the existing front-top enclosure. Each column's upper surface
has 0.75 mm of additional roof relief. Nominal roof clearance is 1.25 mm; floor
clearance is 0.25 mm. The spring bores, tee troughs, tie slots, main plate and release
travel retain their positions. Overall dimensions are unchanged.

The carrier opening reference is the retained front-top STL for H2C job 1277245499
(`2026-09-23-enclosure-front-top-h2c-v13`). This trial does not change that opening.
[Geometry checks](geometry-check.json) bind the trial to that mesh and verify the
opening, spring stations, release travel and valid print solid.

This tests **low-force clearance for rough overhang surfaces involved** at the carrier's
upper sliding contact. The supported front-top roof's physical finish determines the
usable space. Check free sliding and spring return with the existing front-top, with
the tees and springs installed, and assess unwanted play.

The print-bottom edge has an additive chamfer: 0.5 mm outward for each 1 mm of
height, tangent to the existing R6 taper at print Z 3.317 mm. Each affected bed edge
extends 3.708 mm farther out. The added 365.3 mm³ stays inside the carrier envelope
and behind the spring bores; no material is removed. The complete print-top round
is unchanged. This gives a maximum nominal outward step of 0.12 mm per 0.24 mm layer.

H2C prints black PET-GF on the left 0.4 mm hotend, with requested +0.18 mm bed trim.
The carrier lies on its back. The first bed layer is 0.20 mm. The bottom chamfer,
taper and main body use the shared PET-GF profile's 0.24 mm layer height; the top
R6 band uses 0.08 mm. Six walls apply only through print Z 6.1 mm, with two walls
above. Supports and brim are off; elephant-foot compensation is zero. Saved speeds,
wall-first order and 15% overlap are retained. Native verification checks first-layer
overlap, the complete bottom transition, and emitted wall count. No other parts
share the plate.

`low_force_trial.py` generates the geometry; `prepare_print.py` prepares and natively
slices the H2C job. Physical fit is pending.

Native H2C job 1292379739 is started: 140 layers, approximately 1 hour
46 minutes. The [slice review](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-tee-chamfer-h2c-v6/README.md) retains the geometry,
layer-overlap checks, wall counts and launch receipt.
