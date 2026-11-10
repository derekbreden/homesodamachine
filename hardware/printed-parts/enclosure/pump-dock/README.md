# Pump mount and tee wall

Front-top contains tapered pump loading wells, fitted cylindrical motor guides and local
flange stops in continuous stock up to the display housing and enclosure roof. Each pump
has an identical solid flange retainer secured from below with socket-head screws and
short heat-set inserts. Each retainer's straight-sided loading room has a flat ceiling
carrying its insert pilots. Continuous stock surrounds the pump wells and joins the
retainer rooms; solid stock remains between pumps.
The [mount source](../enclosure/front/mount.rs) and
[retainer dimensions](../enclosure/retainer-numbers/lib.rs) own their geometry.

The [scan-derived reference](../../../reference/kamoer-kphm400/scan-review.md) supplies the
pump's actual head, flange, adapter, motor and flexible outlet geometry. The identified
motor-side scan artifact is replaced by the fitted cylinder. The guide’s straight band retains the bore with the accepted physical motor fit; narrow
keyways clear the terminals during insertion.

## Tees and tube preparation

Each pump carries straight stubs of the machine's black quarter-inch LLDPE in its flexible
BPT ends in place of the supplied barbs. The pump head clamps the BPT around each stub.
Use the [tube-length gauge](../enclosure/enclosure-pump-tube-setting-jig.stl) to prepare
blanks. Final tube position is established with the actual tee seated at its wall datum
before tightening the pump-head housing.

PP0208E tees stand on the pump outlet axes, their branches facing the pumps and their runs
upright. Each branch enters a teardropped bore through the tee wall, with its extended
collet clear in the fore opening. The bore locates the branch laterally; its annular face
stops the fixed barrel fore. The fitted lower return restrains it aft. The collet grips
the prepared pump tube and its O-ring seals it.

Each upper tube joins its fore valve. Each lower return uses NeoFit ATEU44W stem elbows
and one continuous formed tube to the rear valve. Trim stems against actual insertion
marks, keep the tube bends clear of the condenser and chassis slide, and tug-check each
push-fit connection. The production manifold owns the tee, valve and tube stations.

## Factory assembly and service

Follow [internal plumbing](../../../assembly/internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps).
Keep front-top loose while installing inserts, landing the motor leads, loading each pump
motor-first and securing its local retainer. Feed the flexible stubs through the closed
wall bores. Draw wire slack through the shared rear passage without loading the terminals.
Fit tee and fore-valve groups from aft before the rear valve row and lower returns.

The motor guide holds the pump straight while fixed upper stops and the removable lower
retainer capture the flange. For service, open front-top, disconnect power, release the
pump's plumbing and motor leads, support it and remove its retainer screws from below.
The other pump's retainer stays assembled.

## Manufacture and fit

Front-top stands on its seam plane. Tapered loading wells reduce the flat overhang area.
Each retainer prints with its flange-bearing face on the bed and screw-head recesses
facing upward. Its screw seats and bearing lip use local solid infill.
The screw heads sit in shallow counterbores. Accessible cavity supports use Tree Slim;
inspect their emitted contacts and removal paths in the native slice.

The [accepted holder result](../../../reference/kamoer-kphm400/physical-fit.json) covers
its identified holder and good cylindrical motor fit. The independent flange clamps
require a physical assembly trial. Tube retention and sealing are verified during
[assembly acceptance](../../../assembly/acceptance-and-burn-in.md).
