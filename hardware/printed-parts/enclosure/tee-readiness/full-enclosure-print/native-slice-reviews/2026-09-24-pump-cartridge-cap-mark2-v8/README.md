# Pump cartridge and cap — Mark2

Mark2 task **1279835918** is running the current cartridge and matching cap in black
PET-GF on the left 0.4 mm nozzle. Native estimate: **13 h 35 m 37 s**, 1088 plate
layers. The [launch receipt](launch.json) identifies the accepted archive and the
[subsequent reading](observed-start.json) confirms the matching job with no error.

The cartridge stands on its flat underside; the cap prints crown-down. The source
STEP/STL files and placement match the reviewed geometry. The first layer is
0.20 mm. The cartridge's complete grip-floor rounds use 0.08 mm layers at print
Z 6–18.4 mm, and its grip-ceiling rounds at Z 100.3–113.2 mm. Other model layers,
including the cap, use 0.24 mm.

**Six walls apply only at Z 100.3–113.2 mm**, where the grip closes over its opening.
The normal setting remains two walls. Inner walls precede outer walls and infill;
all saved speed, acceleration, temperature and fan settings remain intact, with
15% infill/wall overlap. This plate applies Derek's preferred six-wall-only
treatment; its physical outcome is not yet assessed.

Painted blockers cover all downward rounded grip faces. The two cartridge trees
support the flat hand-bearing ceilings, with a 0.8 mm painted inset to clear the
rounded borders. Four cap trees support the two motor-terminal annuli and two
screw-head seats. Each has an open removal lane before hardware installation.
The [support review](support-removal-review.json) describes those lanes.

The [native verification](verification.json) confirms complete fine-layer
coverage, original global settings, nozzle and filament mapping, and plate
clearance. The [wall check](wall-scope-check.json) reads six emitted wall crossings
in the upper round and two above it. The [round contact check](round-contact-check.json)
checks all 7,548 upper support road segments, including bodies without interface
labels, with full bead width plus 0.05 mm XY allowance: none approaches a rounded
grip face within 0.60 mm vertically. Interface bead footprints stay entirely
within the flat ceiling projections. Physical contact finish and removal effort
remain print observations.

Requested Mark2 trim is +0.04 mm, emitted +0.02 mm for Textured PEI. Timelapse and
bed leveling are On; flow and nozzle-offset calibration are Auto. The
[manifest](manifest.json) binds the exact source, archive, settings and launch.
