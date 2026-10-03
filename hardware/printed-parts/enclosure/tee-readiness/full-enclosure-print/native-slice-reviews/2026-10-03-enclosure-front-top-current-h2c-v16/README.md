# Front-top H2C native print review

This source-bound front-top archive is superseded for the current part and must
not be submitted. Its native review remains specific to the recorded geometry. The
[manifest](manifest.json) binds the materialized STEP/STL, frozen source/profile,
exact native archive and each review. Printer submission and actual assembled fit
are separate records.

It prints mouth-down at 215 × 207.55 × 195 mm on the fixed left 0.4 mm Standard
hardened nozzle. The saved PET-GF recipe uses a 0.20 mm bed layer, normal 0.24 mm
layers and two walls, wall-first order, 15% infill/wall overlap and `auto_brim`.
The full inward roof-round span, print Z187.392–195 mm, has emitted 0.08 mm walls.
H2C's requested +0.18 mm trim emits +0.16 mm for Textured PEI. The archive has
878 model layers and estimates **25 h 46 min 48 sec**. Its profile-density mass
estimate is 949.56 g; remaining spool quantity is not a launch condition.

The [native emitted-path review](emitted-path-review.json) checks every model
slab against its source-STL section. Every stock section component receives
model wall paths, and all model roads use the left tool with finite positive
widths and linear extrusion. Local midpoint perimeter diagnostics remain in
[their record](emitted-perimeter-diagnostics.json). The [exact surface record](native-functional-surface-emission.json)
identifies the magnetic pogo seat and insert bores, the lower display recess
planes and R6.15 corners, the funnel receiver’s 45° mating end, and the R18
swept roof curve. Every layer in each local feature window contains emitted
model roads. Bridge/top fill and oblique mating or curved boundaries require
the complete feature reading; they are not unwanted flat exterior-roof fins. The slicer's
[diagnostic review](native-diagnostics-review.json) retains the ZFiller message
and verifies that the special tool tokens belong to its exact native start/end
recipes. The unmodified archive passes ZIP CRC and embedded G-code MD5 checks.

The [first-layer bead review](first-layer-overlap.json) passes. The complete
[fine-roof overlap reading](roof-layer-overlap.json) retains one centreline
trigger on the final inward terminal road. Its [actual-width review](final-roof-corner-review.json)
shows 78.85% nominal bead support over that 0.738 mm road, with 99.94% nominal
support across the complete final exterior layer. The native roof has no flat
corner fins. Printed finish and bond are unmeasured.

All **1,535,891 support roads**, including short bodies without interface labels,
clear the 119 protected native exterior show faces under their actual
width/height envelopes. The [support review](support-removal-review.json) assigns
all 75 support bodies and 11 labelled contacts to removal routes. Functional
rail, pocket and interior ceiling contacts remain supported. Clear the empty
shell through its open bay, display storey, exposed flanks and aft funnel opening;
break sacrificial branches where necessary. Remove every branch and loose
fragment before installing hardware, the frame, tubes or loom. Native access
lines are geometric examples; physical removal effort remains an observation
on the print.

Every emitted road has at least **24.246 mm** shared-bed border, and the model
has **55 mm** border. Timelapse and bed leveling are On; Flow dynamic calibration
and Nozzle Offset Calibration are Auto. The signed sender verifies these options,
the fixed-left head and the black external mapping before submission. The user’s
H2C request confirms the bed is clear; spool quantity requires no confirmation.
