# Printed parts

[Printing the Machine](../printing-the-machine/README.md) tells the lessons behind these
rules on the prints that taught them, sorted by plastic. Use it for both parts and coupons.

## Publish loop

Find a part by the description Derek uses:

    node tools/find-part.mjs "water regulator"

The search shares the website's catalog and matcher. Its source producers and build targets
come from the build graph. Use the returned targets to select the affected parts; include the
assembly producer when changing installation or adding a source to an assembly.

Before the first rebuild of an enclosure geometry change, take its
[before snapshot](../../changes/README.md):

    node tools/changes/change.mjs snapshot

Build and publish through the normal print build, with the selected native targets:

    tools/run -- hsm-print-build -- //:enclosure-back-top

Multiple target labels select related parts together. With no labels this runs the normal
print build. It resolves generator programs and dependencies, carries their completed outputs,
and publishes each changed producer while the rest continue. Use this entry point for an
ordinary edit; standalone Cargo and generator commands serve investigation of a specific stage.

Link the published model as soon as a relevant changed part is available. Continue focused
inspection while Derek can view the attempt, and state what remains under review. A partial
assembly can contain parts from different completed producers; first view does not establish
print readiness.

The pump retainer's standalone files carry one printable clamp. Its seated model places
independent copies and their purchased hardware in the assemblies and named views. Select the
assembly producer when changing their installation; the publisher retains the installed bodies.

After the publish is live — never before, and never as a gate in the build path — lint the
piece you changed and fix what it flags while Derek is already looking:

    tools/run -- tools/hsm/target/release/geometry-lint <piece>.stl

The [native review command](../../tools/hsm/mesh-review/README.md) reads the saved print mesh
and optional exact-facet source binding; it starts no geometry build.

Findings print as pick text: paste one into the model viewer's Find box, or feed it to `hsm-pick read`.
Answers live in `lint-answers/`, at each piece's own path; its AGENTS.md says when a finding is
answered instead of fixed. A defect fixed at one station usually has siblings; the lint's job is
to find them before Derek does.

Once the publish is live, record the change from that snapshot: the view that shows it, before
and after, as [`changes/README.md`](../../changes/README.md) describes.

## What each file shows

The physical print is the part. The files answer different questions about it:

- Rust source and `.step.npz` — the authored construction and its fine model, with recorded
  surfaces and source contributors. A standalone `.step` is an export where a consumer needs it.
- `.stl` — the tessellated geometry the slicer reads: the closest file to the print.
- `.step.mesh` — the payload the model viewer draws. Assembly payloads reference immutable part meshes
  and their placements. Picks name the displayed payload and its digest.
- `hsm where`, `gap`, `section` and `ray` answer questions about those exported meshes without
  rebuilding them. A source edit reaches a query after its producer writes the new payload.
- [`hsm-pick compose`](../../tools/hsm/inspection/README.md) composes typed numeric picks;
  `hsm-pick read` locates pasted pick text on the available representations.

That last reading is a LOCATION AND NOT A VERDICT. The payload's tolerance is a distance
bound, so a feature shorter than it is collapsed and bridged while the reading never leaves
budget: a coordinate can be real on the payload alone and still be a real defect — that is the
payload reporting geometry it could not draw, and what cannot be drawn at that scale usually
cannot be printed at it either. A surface comparison says where a thing shows up. It never
settles whether what somebody saw in the viewer was there.

## Supports

PET-GF uses Support D's contact and bridge settings from the shared
[`petgf.profile.json`](petgf.profile.json). Current preparers inherit those settings even when
their other settings come from an accepted older print. Keep embedded filament
bridge speeds consistent with the project. The
[rollout record](support-D-rollout.json) identifies the current projects and
their slice status. Historical print archives retain their original settings.
Support D selects contact and interface treatment; each part retains its
support style, rooting, removal access, authored fins and support-free regions.
Check the actual emitted contact planes and underside recovery paths when
preparing a part. Coupon acceptance does not establish full-part removal.

The [inclined faucet result](https://github.com/derekbreden/homesodamachine/blob/7b4d4c7d87dda9db021665b2e7c7e255d996a39d/hardware/print-tests/petgf-dense-roofs/D-representative-mark2/physical-result.json)
records broken tree stems with contact material retained on the base. D's
removal acceptance covers the tested flat rail ceilings and their access;
inclined and curved faucet contacts remain unqualified. Prepare the incline
comparisons before treating D as an accepted faucet support recipe.
The [explicit Slim faucet trial](https://github.com/derekbreden/homesodamachine/blob/be19fb8a4693edecead5753aa2bcb42c54dcdbf0/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-mark1/physical-result/physical-result.json)
also failed release despite generating interface paths along the curve. The
[larger-gap trial](https://github.com/derekbreden/homesodamachine/blob/a261387d7021b9f74675793f5b1a3fd188cfccec/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-gap048-mark1/physical-result/physical-result.json)
records easier release with connected roof mats and essentially unchanged
underside finish. The [nonplanar faucet result](https://github.com/derekbreden/homesodamachine/blob/542ced3900b6b513c521c525582c22f167c9584d/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-gap024-widebands-mark1/physical-result/physical-result.json) records improved underside finish and trapped insert supports. Keep the heat-insert recesses clear of support. Bridge the shoulders and blind pilot roofs, and read the emitted paths through both stages. The [rim-fin release observation](https://github.com/derekbreden/homesodamachine/blob/534b87cc5f8d6911f8bcfa38378116d8dcdcb6bd/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/physical-result.json) records the dense roof and support coming off together. The [tree and contoured-rim trial](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-11-faucet-trees-only-mark1/print-job.json) uses the dense roof and bridge-only pockets on the complete lower curve.
The [archived incline comparisons](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/petgf-dense-roofs/inclines/matrix.json)
retain D's dense interface and vary contact gap and tree generation. Interface
density and the contact footprint selected by the tree algorithm are distinct.

Use Tree (auto) with the saved Bambu default style for accessible exterior
features. Enclosed cavities must not contain rectangular normal supports,
whether explicitly added or chosen automatically. Select Tree Slim for the
front pump cavities, lower pump retainer and rear enclosure, and inspect the
emitted branches and their removal openings. Geometric access alone does not
establish easy removal. A bed-footprint constraint does not justify trapped
normal supports.

Every tree support stands on a trunk that thickens toward its root and branches
thinner only near its tips. No support is a trunkless tower, whether a cluster
of tip-sized columns or one or two alone. Recipes keep the shared profile's
branch diameter, diameter growth and wall count (`tree_support_branch_diameter`,
`tree_support_branch_diameter_angle`, `tree_support_wall_count`), and a
`tree_support_branch_angle` override still leans enough for tips to merge into
a trunk. The
[stopped Mark 1 back-top](https://github.com/derekbreden/homesodamachine/blob/442ac2b7c23d85ee12d16088b3ad89388730cc91/hardware/printed-parts/enclosure/enclosure/prints/2026-11-14-back-top-engineering-stock-z-mark1/physical-result/physical-result.json)
records tip-sized towers that did not survive, so some of the surfaces they
were to carry printed with no support under them.

Back-bottom retains Default for its floor-rooted rail trees; local native
targets cover the accessible handhold mouths and seam lips.

Derek confirms easy removal of short Bambu tree supports rooted on the floor inside
the rail cavities. Preserve that local rooting and the open sliding lane. Normal
supports and tall trees starting well below the cavity do not share that acceptance.
Read the actual rail-tree bases and interfaces from the native slice; allowing
supports on model material alone does not establish where the slicer roots them.

Back-top prints ceiling-down, with the rear flutes standing clear of the bed.
The four rear receivers and the carbonator pump use the
[shared fitted spring and cheek](enclosure/enclosure/numbers/equipment_snap.rs).
Check seating against the installed hardware. The water regulator bears on its
cap before the feet reach the pocket roofs. The sideways flow-meter receiver
needs removable support under its short wing guide, retaining return, long-catch
shelf, screw-head ledges and exposed housing surfaces. The trees come out of
the open west side before the meter goes in.
[Rear fit record](enclosure/rear-equipment-caps/production-fit.json)
The rear ceiling recess runs flush to
the flanks and to the rear wall, whose panel relief runs from the rim up to it
at the face of the core's pocket, and it runs round the connector wells' row.
The bulkhead nuts and the Pisco's shoulder seat on that relief's face. Whatever stands on that ceiling is rooted in
it: the ASSE and Pisco receivers, both rear corner columns, the wells, the
power-supply bosses and the inlet tunnel. A part that stands on a face takes
its root from that face's own plane, never from a second number for it.
The meter's sideways channels return to the flank on bevels.
The meter's fore shoulder and the lip under its cap's upper leaf take support
through the open west side. The aft boss-channel crown grows from a permanent
45° slope. See the [measured rear cap fits](enclosure/rear-equipment-caps/production-fit.json).
The Pisco leaves stop ahead of the rear corner column; its body retains the
full fitted span.
The C14 inlet's flange pocket and cord passage take support; its blind pilots
stay clear. The meter's fitted boss channels, screw-head channels and wire
chamber take support through the receiver's open west side. Preserve the
[approved](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/pointed-snaps/physical-result/physical-result.json)
component seats and the spring walls and roots.
Receiver coupons retain this production layer direction. Ordinary layers apply
except where a specific show round requires a fine band.
Covered rear bulkhead bores and horizontal valve sockets retain teardrop
clearances pointing in the build direction. The vent cap has a rooted chamfer;
its passage stays clear of supports. Back-top's rail caps have narrow removable
roots on their own cavity floors. The nameplate receiver's two ledges grow
from the rear wall on corbels. Manual Tree Slim supports exposed joint ends,
funnel receivers, the valve seat and initial boss curves. The fill tube seat's
free upper wing prints on breakaway strips rooted on its corbelled lower wing.
The cable hooks' beak lands overhang too little to need support, as
front-bottom's same hooks show. Read the
actual removal openings and first model courses in the native slice. Keep blind pilot roofs
outside support enforcers. Connector insertion pockets bridge between their well
walls and remain support-free. A bridge path needs a landing at both ends. Follow
the first paths across the opening to the deposited courses that carry them.
Read each exposed underside's first deposited courses
and its actual support contacts; the support topology alone does not establish
coverage. Derive contact bands from the complete receiver stock and its exposed
undersides; keep the self-supporting bed chamfer outside joint enforcers.
Back-top allows native roots on the part and the plate. Read the slice for
passage clearance, bead margins and access to the tree roots and interfaces.
The rail supports were removable in the full-size physical article; its loose
underside and subsequent glossy courses require localized foundation cooling.

The [rear equipment fit trial](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/rear-snap-retention/physical-result/physical-result.json)
records easy screwdriver removal of tiny supports in accessible coupons. That
result applies only where the same access remains available in the complete
part.

For visible overhang edges with reported roughness, follow the edge with a
removable fin wall and retain Tree(auto)/Default on the remaining surfaces.
Use interrupted arcs on curved edges, with release gaps away from the most
visible midpoint. The [accepted faucet-base arc result](https://github.com/derekbreden/homesodamachine/blob/9a785be8163fcb13a7efd24e78b249419bc0806e/hardware/printed-parts/faucet/finish-coupons/2026-10-15-edge-supports/base-mark2/physical-result/physical-result.json)
records the best observed underside and very easy snap-off in PET-GF at the
retained −15° pose. Contact placement, release breaks and bed anchorage belong
to the specific edge geometry; this result does not establish other features'
finish or release. Keep each manual support's reason and scope beside its part.

Fewer edges takes priority over thicker material. Prefer broad continuous faces
and simple pocket boundaries. With equally simple boundaries, prefer thicker
stock and greater printed volume. Add a curve, step or local recess only for
a named fit, bearing, drainage or access requirement.

A pocket near a wall extends flush to that wall. Do not leave a lip, strip or
ledge between the pocket and the wall. When a larger pocket with a uniformly
lower floor replaces a group of small pockets, choose the simpler floor and
carry it clear to the wall, even when that removes more material. Preserving
printed volume does not justify extra edges.

One job is one solid object: a part that needs a second part to hold it together is
redesigned, not covered or keyed. Fewer edges is better. Saving material is not a goal;
no part is thinned, skeletonized or pocketed to use less of it.

Every printable piece in the enclosure assembly follows **Support-removal strategy** in
[`enclosure/enclosure/README.md`](enclosure/enclosure/README.md#support-removal-strategy).
Enclosure parts and their receiver coupons use the shared `petgf.profile.json` tree supports and their
production print orientation. The four-screw nameplate prints without supports, with its flat back
directly on the bed and counterbores facing upward. Ordinary enclosure walls, webs and joint ends
use the nominal 3 mm wall section. Remove cut remnants and tapered tips that leave thin fins.
Apply thinner-section exceptions only to the specific flexure, cover or other feature that
requires them.

Use the shared project's first bed layer and ordinary layer schedule. Keep the
production schedule for geometry and fit comparisons. If a requested dimension
slices to the same opening, report the emitted dimension. Treat any change to
the layer schedule as its own experiment. Expanding
print-down show rounds use an additive chamfer tangent to their retained taper,
following [`enclosure/enclosure/numbers/structure.rs`](enclosure/enclosure/numbers/structure.rs): 0.5 mm outward per millimetre of build rise.
Use six walls locally through that transition band, saved speeds and wall-first order,
15% infill/wall overlap, and no supports on that exterior transition. Derek's accepted
tee-carrier surface is recorded in
[`enclosure/tee-carrier/physical-acceptance.json`](https://github.com/derekbreden/homesodamachine/blob/fa06bf904fc54d0a998a34233ca37fedfd55c3c0/hardware/printed-parts/enclosure/tee-carrier/physical-acceptance.json).

Retain 0.08 mm for inward/top show rounds. Functional flat lifting ceilings, sliding
seats and retention bearings keep their required shape and receive accessible supports
where needed. Check emitted first/second-layer bead overlap and support contacts;
small bodies without interface labels count. A fine layer band alone excludes no support.
Other parts using the shared geometry still require their own native slice and physical
surface check before claiming the tee result transfers to them.

## Filament use

PET-GF uses the [localized cooling policy](cooling/README.md): ordinary part
cooling and auxiliary part cooling are off. High cooling is for the bridges
and substantially unsupported wall paths and their fresh foundation courses, not whole layers,
short layer times or ordinary walls. The shared `petgf.profile.json` and current
preparers select 70% bridge/overhang cooling at the 50% unsupported-width
threshold. A 0% threshold cools every exterior wall in Bambu Studio and does
not express this policy. Keep fan-always-on and fan pre-start off. A feature
may use up to 100% cooling when its underside needs it; scope that choice to
the actual paths. The shared output stage retains cooling and bridge-limited
deposition speed in those recent underside footprints. Ordinary structural
paths retain their selected recipe. Historical G-code is evidence, not the current recipe.

Derek wants every spool used fully, with reloading during a print as needed. Remaining
spool quantity is not a launch condition: do not ask for its weight or an estimate, or
hold a ready print for a quantity confirmation. Use the correct material mapping and
ask for reloading only when an actual runout requires it.

## Printer allocation

Read [bed placement guidance](../../tools/bambu-printers.md#placement-on-unseasoned-plates)
before laying out a plate. On unseasoned outer regions, keep model/support/brim
beads at least 20 mm inside the usable bed boundary; center small coupon plates
and aim for 80 mm where the complete test fits. Verify the native full-bead
envelope, not only the CAD bounds.

Derek's request to start a print on a printer confirms that its bed is clear.
Do not ask for a separate bed-clear confirmation.

When both printers are loaded with suitable material, have clear beds and are ready,
distribute the authorized test parts across both printers. Derek prefers using both
ready machines to leaving one loaded and idle while combining everything on a single
plate. Preserve each printer's own profile, nozzle mapping and Z trim, and keep the
startup spacing below.

For a single job that either ready printer can handle, prefer the printer that
has been idle with suitable filament loaded longer. Compare the idle-and-loaded
period, not idle time alone. A printer without the required material loaded is
not an equivalent candidate; both printers are not always loaded with PET-GF.

## Printer startup spacing

H2C and Mark2 share a circuit. Wait at least **three minutes after one printer accepts
a job before starting or resuming a job on the other**. Apply this to power-loss
recovery too, checking for an already-running job before sending anything. This is
Derek's trial interval for the reported startup breaker trips. The sender serializes
app access but does not enforce the interval. Record both launch times; see
[`tools/bambu-printers.md`](../../tools/bambu-printers.md#shared-circuit-startup-spacing).
