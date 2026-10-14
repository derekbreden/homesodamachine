# Shared-reader cross-check

These are manual readings from [tools/gcode](../../../../../../../tools/gcode/README.md)
of the exact base-and-tip archive accepted as Mark2 task 1337767162. The
mounting plate is read from the complete candidate. Each CSV retains its
selected largest loop for every layer, without a height window.

- [Base profile](base.json) and [all-layer CSV](base.csv): 1,125 exterior-loop
  layers, maximum 0.543 mm, no zones past 0.6 mm. The Z64.64 scarf's 0.001 mm
  zero-E connector remains within its original run.
- [Tip profile](tip.json) and [all-layer CSV](tip.csv): includes the concealed
  joint plug, display-frame corners and terminal contours as well as the
  exposed curved neck. The target direction is CAD +Z to select the outer
  side of the curved bend; lateral X is independent of that direction.
- [Plate profile](plate.json) and [all-layer CSV](plate.csv): includes the
  three off-center mounting pedestals above the outer rim.

The tip's large profile offsets at print Z0.2–9.32 and Z15.32–16.04 are
plug contours; those near X−11.9 at Z95.24–137.48 are frame/terminal
contours. The plate's X22.885 row is a pedestal. Those global-X measurements
are not rear-meridian errors on the exposed curved neck or outer plate rim.
The [feature-aware trace](../complete-trace/trace.json) retains every external
run, its source-STL boundary, the tip arc classification and assembled-cover
ray interception. It measures 0.188 mm on the exposed curved tip and X=0 on
the plate's outer rim.

The reader's paint selection returns exactly 477 base facets and 186 tip
facets from this multi-part project. The known base-only physical reference
also reproduces its 1.955 mm foot and 1.556 mm lower-neck deviations with
the shared reader's numerical-connector handling.
