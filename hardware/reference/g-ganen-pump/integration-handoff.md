# G Ganen integration boundary

The measured reference supplies the fixed casing, motor, rails and independent
port profiles. Production uses the bare pump from
[g_ganen_installation.py](installation/g_ganen_installation.py), placed by
[above-core.json](../../manifold-layout/above-core.json).

The four rubber feet and their raised legs are complete removable sliders. They
slide out of the fixed casing rails. Production omits all four assemblies;
[common-foot](common-foot/README.md) describes the purchased parts separately.

The native +90° Z rotation maps discharge toward enclosure −X and suction toward
+X. The fixed lower casing bears directly on the Z253.4 lid at its front and on
the 20 × 12 mm rear land. Two loops, each made from two joined owned wide ties,
pass through underside-open lid grooves. There are no pump screw stations or
cup columns. The [installation procedure](installation/README.md) gives the
pose, bearing height, strap dimensions and service sequence.

Each measured barb retains its own tip, axis and exterior profile. Reinforced
PVC joints, trimmed PP061208W reducers and two clamps per barb connect the pump
to the water header and discharge check. The pump and this fitting group use
the same vertical datum. The check's continuous outlet reaches the straight
core guide at X−82.5/Y420/Z253.4 through tangent bends of at least R14.923.

Generate cap, foam assembly and cold-core assembly before Box, printed shell
pieces and the full appliance. [Mechanical qualification](../../mechanical-qualification/enclosure-above-core/README.md)
binds the nominal clearances, assembly motion and native slices. Actual strap
retention, vibration, fitting retention and printed assembly force remain
physical observations.

The integration envelope fills reentrant casing and rail cavities for external
clearance. It describes occupied exterior space, not casing mass or hidden wall
thickness. `native_queries.intersect_components` reads components individually;
`occupied_bounds` returns `None` for an empty section.
