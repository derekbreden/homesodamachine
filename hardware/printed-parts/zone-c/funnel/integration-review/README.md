# Funnel integration review

The exported frame enters front-top along Y, and back-top captures its opposite
rails as the enclosure closes. `check_fit.py` measures the actual frame and shell
STLs through those motions. The seated pairs have no shared volume, and the
closed enclosure captures the frame against 2 mm translations in every axis
direction. [`rail-motion-check.json`](rail-motion-check.json) binds those
readings to the exported meshes.

The silicone capacity is 599.90 mL, nominally 600 mL. The frame's flat underside is Z299.9, its
plug seat is Z302.9, and both end corbels cross the full 207 mm width at 30°
from vertical. The drain hole is 11.25 mm, with the elbow cradle's two wing
slots beside it. Eight samples on a 17 mm-radius ring around the outlet measure
the remaining 3 mm web outside the hole and slots.

## Open geometry

The [assembly scorecard](/hardware/manifold-layout/enclosure-assembly.scorecard.json)
records the current placed machine. Fluid-18 intersects the frame by 450.8 mm³;
V-K has zero clearance to it. Fluid-24 and fluid-26 each clear the frame by
0.551 mm, and fluid-14 clears V-A by 0.805 mm, below the 1 mm routing target.
Fluid-2 clears the water pump by 1.421 mm. The regulator and fluid-1 clear the
frame. These readings cover the authored solids and tube paths.

[`assembly-intersections.json`](assembly-intersections.json) is a separate
mesh review bound to its recorded source hashes. Its measurements apply to
those meshes; the current machine's measurements are in the scorecard.

## Native slice readings

The stored [frame support audit](frame-support-audit.json) has four bed-rooted
support bodies, each serving a rail bearing region. Its first layer is one
body; every second-layer wall bead has more than half its area over the first
layer. The records name the source mesh, profile, project and emitted toolpaths.

The stored upper-enclosure toolpaths have no slicer warnings, and their
first-layer and local wall-count checks pass. The front-top audit retains
35 support bodies, including 29 without explicit interface labels. Back-top has
14 support bodies, including one without an explicit interface label.

The back-top review placement leaves only 2.958 mm between a support extrusion
and the shared bed edge, below the recipe's 10 mm target. Its print layout and
the upper shells' support removal need further review. The current frame and
upper shells require native slices bound to their current meshes. Physical
support removal and fit remain unqualified for this geometry.
