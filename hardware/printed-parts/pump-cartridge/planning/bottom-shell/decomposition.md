# Bottom Shell -- Decomposition Decision

## Decision: Pass Through

This part is a single geometric paradigm. No decomposition needed.

## Rationale

The bottom shell is entirely extrude-and-cut geometry:

- **Outer walls:** A rectangular box shell, extruded from the build-plate face, with uniform 1.5 mm wall thickness. No lofts, no sweeps, no revolved profiles.
- **T-slot rail grooves:** Rectangular cuts into each side wall exterior, running the full depth of the part. Straight extrude-and-cut along Y.
- **Finger bar slot:** A rectangular opening cut through the front face. Straight cut with small edge fillets.
- **Snap-fit hooks (x4):** Prismatic protrusions on the interior walls -- rectangular tabs with a deflection arm and hook tip. These are box-plus-chamfer geometry, oriented so the flex direction is parallel to the build plate (layers stack along the flex axis).
- **Alignment pins (x2):** Cylindrical bosses extruded from the interior floor. Simple cylinder unions.
- **Seam chamfers:** 0.15 mm x 45-degree chamfers on external edges at the mating face. Standard edge treatment.
- **Elephant's foot chamfer:** 0.3 mm x 45-degree chamfer on the build-plate face bottom edge. Standard edge treatment.

Every feature is a box, cylinder, or rectangular cut. No feature requires a sweep, loft, revolve, or any operation beyond extrude-and-cut with simple boolean unions and subtractions. A single CadQuery agent handles this without difficulty.

No feature has geometric dependency on a feature in a different paradigm. The snap-fit hooks are prismatic. The alignment pins are simple cylinders unioned to a flat floor. The T-slot grooves are rectangular channel cuts. These are all tightly coupled to the same rectangular shell body and share the same coordinate system.

Decomposing this part would add pipeline complexity (two sub-component specs, two drawings, a composition step) with zero benefit -- every sub-component would still be extrude-and-cut, and the composition boundary would introduce unnecessary interface management at the shell body.
