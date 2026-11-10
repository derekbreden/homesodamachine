# G Ganen integration boundary

The measured reference supplies the fixed casing, motor, rails and independent
port profiles. Production selects the bare replica in the
[native equipment constructor](/tools/hsm/machine-data/src/equipment.rs), placed by
[above-core.json](../../manifold-layout/above-core.json).

The four rubber feet and their raised legs are complete removable sliders. They
slide out of the fixed casing rails. Production omits all four assemblies;
[common-foot](common-foot/README.md) describes the purchased parts separately.

The native +90° Z rotation maps discharge toward enclosure −X and suction toward
+X. The molded cable cover is the bare pump’s low point, at Z254.408545,
with 1.008545 mm of air above the Z253.4 lid face. The 61 mm motor saddle
supports the measured barrel and fixed rails. Its single 54.5 mm upper clip
has a 3.1 mm nominal arch, 3 mm wings and 3 mm solid axial end lands beside
the receiving pockets. Broad outside stock joins both fixed-rail end stops
to the saddle; the straight rail corridor and lead exits remain open.
The [installation procedure](installation/README.md) gives the pose,
bearing geometry and service sequence.

Each measured barb retains its own tip, axis and exterior profile. Reinforced
PVC joints, trimmed PP061208W reducers and two clamps per barb connect the pump
to the water header and discharge check. The pump and this fitting group use
the same vertical datum. The check's continuous outlet reaches the straight
core guide at X−82.5/Y420/Z253.4 through tangent bends of at least R14.246.

Generate cap, foam assembly and cold-core assembly before Box, printed shell
pieces and the full appliance. [Mechanical qualification](../../mechanical-qualification/enclosure-above-core/README.md)
binds the nominal clearances, assembly motion and native slices. Actual snap
retention, vibration, fitting retention and printed assembly force remain
physical observations.

The integration envelope fills reentrant casing and rail cavities for external
clearance. It describes occupied exterior space, not casing mass or hidden wall
thickness. [Native geometry queries](/tools/hsm/README.md) measure the retained
model's exported payload without rebuilding the reference.
