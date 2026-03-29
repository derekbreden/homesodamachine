# Linkage Arms (Left and Right, Parts 6 and 7) -- Decomposition

This part is a single geometric paradigm. No decomposition needed.

Each linkage arm is a rigid PETG bar approximately 155mm long, 6mm wide, and 3mm thick, with a 3mm cylindrical pin at each end. The bar and both pins are prismatic/cylindrical features that can be modeled entirely with extrude and cylinder union operations in CadQuery. No sweeps, no lofts, no revolved profiles, no multi-paradigm geometry.

The front pin (Z-axis, vertical) is a cylinder unioned to the top face of the bar at the front end. The rear pin (X-axis, horizontal) is a cylinder unioned to the end face of the bar at the rear end. Both pins are simple cylinder primitives positioned and oriented on planar faces of the bar body.

The left and right arms are mirror images of each other -- the right arm mirrors the left arm's rear pin direction (pin extends in -X instead of +X). The bar body and front pin are identical between the two arms.

**Pipeline path:** This part proceeds directly through 4s, 4b, 5, and 6g as a single unit. No composition step (6c) is needed.
