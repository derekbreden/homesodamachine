# White umbilical organizer — Mark2 right hotend

One current below-faucet tube/ribbon organizer prints in white PET-GF on
Mark2's right hardened standard-flow 0.4 mm hotend, external spool 255.
The printer reports that spool as white PET-CF. The
[launch record](launch.json) binds task **1346038475** and the accepted file.
The [startup observation](startup.json) reports the correct 42-layer job
running with no print error or HMS.

The [current production STL](../../umbilical-organizer.stl) is unchanged and
matches the [feature-level fit record](../../physical-acceptance.json):
three Ø6.65 mm beverage bores, one Ø4.40 mm drain bore and the current
5.4 × 1.8 mm flat ribbon slot, in Ø32 × 10 mm stock. The accepted round-bore
fits retain their measured scope; complete installed fit and ribbon threading
remain physically unassessed.

The organizer prints upright, centered in the right nozzle's usable bed area.
It retains the [saved organizer process](../2026-10-11-current-mark1/README.md):
0.20 mm first bed layer, 0.24 mm normal layers, two walls, 15% grid,
265/280°C nozzle, 80°C bed, flow ratio 0.9555 and its saved cooling, seam and
speed settings. The native slice emits no support or brim. This is a white
right-hotend preparation, with no changes to the production model.

Mark2 uses its normal +0.04 mm requested trim, emitting +0.02 mm on Textured
PEI, and its recorded right-nozzle XY registration. Right-tool assignment
is Manual at both project and plate scope. Timelapse and bed leveling are On;
flow dynamic and nozzle-offset calibration are Auto. The peer printer's
recorded acceptance is more than 180 seconds earlier.

[Native review](native-review.json) records 14 min 6 s and 4.14 g using the
saved profile density, with 135.77 mm minimum full-bead clearance to the
right nozzle's usable area. [Packaging](packaging.json) retains identical
G-code bytes in the print-only copy. [Readiness](readiness.json) binds the
project, source mesh, review and launch. Physical print inspection is pending.
