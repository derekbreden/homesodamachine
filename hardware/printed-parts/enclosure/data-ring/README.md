# DATA frame

The RJ11 jack carries a black PET-GF identification frame with white DATA lettering.
Its visible face is 32 mm wide, with square upper corners and R2 lower corners,
matching the six fluid labels. The jack sits 3.36 mm behind the rear show plane
in its own fixed receptacle. The removable frame's 20.8 × 18.3 mm opening leaves
the plug and latch accessible.

Two lateral flexures snap into separately backed wall pockets. Each stem is
1.2 mm wide, has a 17.4 mm free length and an R0.6 root. The snap noses are
1.68 mm thick, with a 1.9 mm outward projection. The retaining lips have
1.2 mm of complete plain stock, clear of the decorative flutes. Diamond openings
inside the enclosure let a small tool press each stem inward for removal.
The fixed jack receptacle carries cable insertion and withdrawal loads.

Print the frame flat-back-down with its lettering facing up. Open side reliefs
keep the snaps free of enclosed bridges. The frame and lettering use the black
identification plate in the [DRAIN print set](../../drain-readiness/README.md),
with black PET-GF on Mark2's right nozzle and white PET-GF on its left nozzle.
No supports are required. Clean the relief slots before pressing the frame
squarely into its pocket; do not glue the stems.

The [fit check](fit-check.json) records native clearances, complete retention
stock and the nominal flexure screening. A 2.4 mm inward deflection gives a
1.43% nominal linear cantilever strain estimate. That estimate does not establish
insertion force, printed fit, pullout load or endurance; those properties belong
to the finished frame and wall.

`data_ring.py` exports the colored frame and lettering. The shared
[`_data_wing_interface.py`](../enclosure/_data_wing_interface.py) supplies both
the frame and its enclosure pocket.
