# Printed parts

The [FDM print guide](../fdm-print-guide/README.md) routes printing work to the
fundamentals, material recipes, and examples. Use it for both parts and coupons.

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

Findings print as pick text: paste one into the /3d Find box, or feed it to `hsm-pick read`.
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
- `.step.mesh` — the payload `/3d` draws. Assembly payloads reference immutable part meshes
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
[`petgf.3mf`](petgf.3mf). Current preparers inherit those settings even when
their other settings come from an accepted older print. Keep embedded filament
bridge speeds consistent with the project. The
[rollout record](support-D-rollout.json) identifies the current projects and
their slice status. Historical print archives retain their original settings.
Support D selects contact and interface treatment; each part retains its
support style, rooting, removal access, authored fins and support-free regions.
Check the actual emitted contact planes and underside recovery paths when
preparing a part. Coupon acceptance does not establish full-part removal.

The [inclined faucet result](https://github.com/derekbreden/homesodamachine/blob/de202da37ef6b132a07fe1863b304381f4ccc394/hardware/print-tests/petgf-dense-roofs/D-representative-mark2/physical-result.json)
records broken tree stems with contact material retained on the base. D's
removal acceptance covers the tested flat rail ceilings and their access;
inclined and curved faucet contacts remain unqualified. Prepare the incline
comparisons before treating D as an accepted faucet support recipe.
The [explicit Slim faucet trial](https://github.com/derekbreden/homesodamachine/blob/1fe50e4ff3209adc4afd6299082bfca21cd8511c/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-mark1/physical-result/physical-result.json)
also failed release despite generating interface paths along the curve. The
[larger-gap trial](https://github.com/derekbreden/homesodamachine/blob/416bf47e9ded600fa3a0c7d19855d87d20b8b893/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-gap048-mark1/physical-result/physical-result.json)
records easier release with connected roof mats and essentially unchanged
underside finish. The [nonplanar faucet result](https://github.com/derekbreden/homesodamachine/blob/b06ab316f6c796a314a30f0dc8ffda66113b2e4e/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-gap024-widebands-mark1/physical-result/physical-result.json) records improved underside finish and trapped insert supports. Keep the heat-insert recesses clear of support. Bridge the shoulders and blind pilot roofs, and read the emitted paths through both stages. The [rim-fin release observation](https://github.com/derekbredensteiner/homesodamachine/blob/b388123d2ac2fdc31fd091f980334b9c99443ab8/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/physical-result.json) records the dense roof and support coming off together. The [tree and contoured-rim trial](../print-tests/petgf-dense-roofs/inclines/prints/2026-11-11-faucet-trees-only-mark1/print-job.json) uses the dense roof and bridge-only pockets on the complete lower curve.
The [active incline comparisons](../print-tests/petgf-dense-roofs/inclines/matrix.json)
retain D's dense interface and vary contact gap and tree generation. Interface
density and the contact footprint selected by the tree algorithm are distinct.

Use Tree (auto) with the saved Bambu default style for accessible exterior
features. Enclosed cavities must not contain rectangular normal supports,
whether explicitly added or chosen automatically. Select Tree Slim for the
front pump cavities, lower pump retainer and rear enclosure, and inspect the
emitted branches and their removal openings. Geometric access alone does not
establish easy removal. A bed-footprint constraint does not justify trapped
normal supports.

Back-bottom retains Default for its floor-rooted rail trees; local native
targets cover the accessible handhold mouths and seam lips.

Derek confirms easy removal of short Bambu tree supports rooted on the floor inside
the rail cavities. Preserve that local rooting and the open sliding lane. Normal
supports and tall trees starting well below the cavity do not share that acceptance.
Read the actual rail-tree bases and interfaces from the native slice; allowing
supports on model material alone does not establish where the slicer roots them.

The full rear enclosure's [physical result](enclosure/enclosure/prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json)
requires the Pisco and ASSE receiver interiors to print without supports: the
full-size walls prevent screwdriver access. Preserve their approved component
seats, catch planes and wing travel. Back-top prints ceiling-down, with the
rear flutes standing clear of the bed. Its catches bridge along their pockets
between the complete end shoulders. Native preparation selects that bridge
direction, retains solid catch and rail bands, and excludes supports from the
receiver interiors. The sideways meter host uses authored removable trees under its exposed end
shoulders. Their trunks stand beside the Pisco pocket and their forks branch
below it, outside the fitted cap pocket. Receiver
coupons retain this production layer direction. Ordinary layers apply except
where a specific show round requires a fine band.
Covered rear bulkhead bores and horizontal valve sockets retain teardrop
clearances pointing in the build direction. The vent cap has a rooted chamfer;
its passage stays clear of supports. Back-top's rail caps have narrow removable
roots on their own cavity floors. The exterior nameplate panel follows both
receiver ledges and pulls aft. Manual Tree Slim supports exposed joint ends,
funnel receivers, the valve seat, initial boss curves and routing lands. Read the
actual removal openings and first model courses in the native slice. Keep blind pilot roofs
outside support enforcers. Connector insertion pockets bridge between their well
walls and remain support-free. A bridge path needs a landing at both ends. Follow
the first paths across the opening to the deposited courses that carry them.
Read each exposed underside's first deposited courses
and its actual support contacts; the support topology alone does not establish
coverage. Derive contact bands from the complete receiver stock and its exposed
undersides; keep the self-supporting bed chamfer outside joint enforcers.
The current back-top recipe retains bed-only native roots. Its
[replacement audit](enclosure/enclosure/prints/2026-11-10-back-top-D-coverage-mark1/support-audit.json)
remains unqualified: adding contact targets does not establish passage clearance
or a compliant bed envelope. Model-floor roots on other parts retain their own
removal paths.
The rail supports were removable in the full-size physical article; its loose
underside and subsequent glossy courses require localized foundation cooling.

The [rear equipment fit trial](../print-tests/rear-snap-retention/physical-result/physical-result.json)
records easy screwdriver removal of tiny supports in accessible coupons. That
result applies only where the same access remains available in the complete
part. Where a screwdriver cannot reach, the feature must print without supports.

For visible overhang edges with reported roughness, follow the edge with a
removable fin wall and retain Tree(auto)/Default on the remaining surfaces.
Use interrupted arcs on curved edges, with release gaps away from the most
visible midpoint. The [accepted faucet-base arc result](faucet/finish-coupons/2026-10-15-edge-supports/base-mark2/physical-result/physical-result.json)
records the best observed underside and very easy snap-off in PET-GF at the
retained −15° pose. Contact placement, release breaks and bed anchorage belong
to the specific edge geometry; this result does not establish other features'
finish or release. Keep each manual support's reason and scope beside its part.

Prefer simple solid stock and broad flat interior walls with few face breaks.
Set one wall plane that preserves the required hardware clearance and backing
thickness. Add a curve, step or local recess only for a named fit, bearing,
drainage or access requirement. Do not contour the wall around every available
void to gain volume; quantify any useful capacity tradeoff against the simpler
wall before choosing the boundary.

One job is one solid object: a part that needs a second part to hold it together is
redesigned, not covered or keyed. Fewer edges is better. Saving material is not a goal;
no part is thinned, skeletonized or pocketed to use less of it.

Every printable piece in the enclosure assembly follows **Support-removal strategy** in
[`enclosure/enclosure/README.md`](enclosure/enclosure/README.md#support-removal-strategy).
Enclosure parts and their receiver coupons use the shared `petgf.3mf` tree supports and their
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
[`enclosure/tee-carrier/physical-acceptance.json`](https://github.com/derekbreden/homesodamachine/blob/d8d50f9a54222ccd40bc1e74111d2d87d893fa78/hardware/printed-parts/enclosure/tee-carrier/physical-acceptance.json).

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
short layer times or ordinary walls. The shared `petgf.3mf` and current
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
