# Bottom Shell — Sub-Component Decomposition

This part is a single geometric paradigm. No decomposition needed.

## Rationale

The bottom shell is entirely prismatic extrude-and-cut work. Every feature falls within one geometric paradigm:

- **Body:** A half-box (floor + lower side walls + rear wall) created by extruding a rectangular profile and hollowing it, or by unioning rectangular wall slabs. Standard box construction.
- **Rail grooves:** Rectangular channel cuts into the side walls. Straight extrude-cut along the insertion axis.
- **JG fitting press-fit bores:** Stepped cylindrical bores in the rear wall. These use a revolved axial profile in CadQuery (the standard technique for multi-diameter bores with chamfers), but the geometry itself is cylindrical holes in a flat wall -- subtractive cylinders, not a separate rotational paradigm. No helical features, no swept profiles.
- **Linkage arm channels:** Shallow rectangular slots cut into the floor. Straight extrude-cut.
- **Snap-fit catch ledges:** Rectangular ledges on the upper edges of the side walls with 45-degree chamfered undersides. Rectangular extrusion + chamfer cut. The catch is a passive feature (no flex arm) -- just a shelf that the top shell's hooks engage.
- **Return spring bosses:** Small cylinders (3mm diameter, 3mm tall) unioned onto the inboard face of the rear wall. Simple cylinder-on-flat-surface.
- **Mounting partition slot channels:** Vertical rectangular slots cut into the interior faces of the side walls. Straight extrude-cut.
- **Rail groove entry chamfers:** Tapered cuts at the front mouth of each rail groove. Achievable with a chamfer or angled cut.
- **Exterior fillets:** 1mm radius fillets on all exterior edges. Standard CadQuery fillet operation.
- **Elephant's foot chamfer:** 0.3mm x 45-degree chamfer on the bottom perimeter edge. Standard chamfer.
- **M3 development screw bosses:** Cylindrical bosses with threaded bore geometry on the top face. Simple cylinder + bore.

No feature requires sweeps, lofts, helical geometry, or complex surface modeling. The revolved-profile technique for the JG stepped bores is the CadQuery-standard method for producing cylindrical pockets and does not constitute a second geometric paradigm -- it produces the same kind of geometry (round holes in a flat wall) that a series of cylindrical cuts would produce, just more reliably.

A single CadQuery agent can handle this part as one extrude-and-cut script following the box + rectangular cuts + cylindrical bores + chamfers/fillets pattern. Decomposition would add pipeline complexity (two sub-component specs, two drawings, a composition step) without any benefit, since no sub-component boundary exists that would simplify the CadQuery work.
