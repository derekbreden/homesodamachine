# Cold-core printed fits

The [native fit catalog](/tools/hsm/catalog/src/lib.rs) supplies 0.15 mm per mating face for static assembly and
0.25 mm for a sliding face. Each supported mating face gets an additional 0.25 mm allowance for the
retained bridge strands, allocated once on that face or its mate. Two supported
faces contribute 0.50 mm to their shared gap. Cylindrical fits
add two radial allowances to the diameter. Printed bearing and seating faces
receive the same applicable allowances; a datum does not waive them.

| Part and print orientation | Fit and supported-face allowance |
|---|---|
| Foam shell, floor down (+Z) | Reservoir guides have 0.25 mm per side. Tube crossings keep their lower envelope and gain 0.25 mm at their crowns. Bottom blind insert pockets gain 0.25 mm depth; top pockets are upward openings. |
| Bottom cap, exterior floor on the bed (+Z) | Its open upper rim seats 0.15 mm below the shell. Integral M5 head pads retain a full 2 mm bearing section above the supported head pockets' additional 0.25 mm depth. Four Ø30 pour openings and two Ø6 air vents cross the floor. |
| Top equipment lid, flat underside down (+Z) | The uniform plate is 7.4 mm thick and seats 0.15 mm above the shell rim. Its four PCB insert posts are integral. Tube openings cross the plate; the B-fill holder has a plain clearance window. Tie tunnels gain 0.25 mm at their opposing floors, preserving the roof and seated body datum. Sideways tube seats gain 0.25 mm at the crown and the post grows equally above it, retaining 3 mm of stock. Upward-open tube and valve seats need no support allowance. |
| Reservoir body, flat floor down (+Z) | Body guides use the shared running allowance, the floor's underside included. The floor, the walls and the rod boss grow from the bed and have no supported face. |
| Reservoir cap, exterior face down (−Z) | Supported screw-head counterbore floors gain 0.25 mm depth. Rod register, fill, draw and air bores open along the build axis. |
| B-fill R14 holder, flat D back down (+Z) | The Ø6.8 teardrop channel and 0.5 mm entry lead-ins retain the accepted holder geometry. Its channel roof prints without trapped tunnel supports; there is no straight outlet leg. |
| PRV shroud, closed cap down (−Z) | Static elbow seat has 0.15 mm radial clearance. The radial vent gains 0.25 mm only toward print-up; the axial cavity opens upward. |
| Reed bridge, convex face down | Tube seat and glass pockets use 0.15 mm static clearance. The glass pockets pass through. The lead-groove floor bridges above the bed; the outer plateau rises 0.25 mm to preserve wire room beneath retained strands while keeping the groove floor, 0.8 mm backing, and tube seat fixed. |

Heat-set insert bores retain the insert manufacturer's geometry. TPU interference
fits, gasket squeeze and the purchased washer dimensions retain their separate
mechanical definitions. The 0.5 mm space protecting reed glass from copper is
an isolation space, not a sliding fit. Foam-pour bands, tube routing rooms,
fastener tool access and structural backing are not mating tolerances.

The support ring, straight pocket walls and reed channels grow from the shell
floor and have no supported mating face. Straight fluid and air tubes are
positioned before the body pour; foam locates their dry spans beneath the lid.
The coil mandrel is forming tooling. The current
[one-piece ASA Aero float](magnetic-float/all-aero/README.md) closes its annular
magnet pocket during the same print; its pocket clearances and insertion pause
require their own native slice review. The
[separate PETG-shell bench reference](magnetic-float/petg-bench-reference.md)
defines the press fits of its retained Aero core and insert.

Copper feed-throughs are Ø7.5 mm through the continuous shell wall, with 0.575 mm radial clearance to nominal 6.35 mm ACR copper.
