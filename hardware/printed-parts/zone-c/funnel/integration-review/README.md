# Funnel integration review

The exported frame enters front-top along Y, and back-top captures its opposite
rails as the enclosure closes. `check_fit.py` measures the actual frame and shell
STLs through those motions. The seated pairs have no shared volume, and both
shells provide capture against 2 mm translations in each axis direction.

The silicone capacity is 299.90 mL. The frame's flat underside is Z299.9, its
plug seat is Z302.9, and both end corbels cross the full 207 mm width at 30°
from vertical. The drain is a plain 6.85 mm hole.

## Open geometry

[`assembly-intersections.json`](assembly-intersections.json) records the closed
exported meshes, their source digest, collision regions and valve clearances.

The frame intersects V-K, the flow regulator, fluid-1 and fluid-18. V-A and V-B
clear it by at least 2.43 mm. Their seats are 2.225 mm above the cold-core lid
at world Y244.710.

The V-A plinth shares 232.46 mm³ with the fluid-14 anchor, and that anchor also
intersects V-A itself. Fluid-2 has 0.712 mm
clearance to the G Ganen pump, and fluid-14 has 0.805 mm clearance to V-A;
both are below the 1 mm routing target. The anchor and the authored tube paths
remain in place. Tube retention through the frame and the connection to V-B
are unresolved.

## Native slice readings

The frame's slice has four bed-rooted support bodies, each serving a rail
bearing region. Its first layer is one body; every second-layer wall bead has
more than half its area over the first layer. The records name the source
mesh, profile, project and emitted toolpaths.

Both upper enclosure pieces produce native toolpaths without slicer warnings.
Their first-layer and local wall-count checks pass. The front-top audit retains
35 support bodies, including 29 without explicit interface labels. Back-top has
14 support bodies, including one without an explicit interface label.

The back-top review placement leaves only 2.958 mm between a support extrusion
and the shared bed edge, below the recipe's 10 mm target. Its print layout and
the upper shells' support removal need further review. These are design and
slice records, not a print release or physical fit qualification.
