# Full enclosure print readiness

The next complete enclosure print is intended for a fully working appliance ready
to ship. Its design, materials, printed structure, surface finish, assembly, sealing,
retention and customer pump replacement are assessed against that use. Further
iteration is expected when evidence calls for it; the print has no reduced fit-test
acceptance standard. The complete operating assembly includes the integrated cold
core and refrigeration provisions, even when a bench build uses the external Lillium
carbonator.

The complete enclosure print includes the four shell quadrants (front-top, front-bottom,
back-top, back-bottom), pump cartridge and cap, machine display cover, empty
electronics access panel and six rear identification labels. The
[cold-core cap](../cold-core/foam-cap/README.md) carries its equipment columns,
valve walls and fitting bearings as integral stock. Front-top's tee wall holds the four purchased PP0208E pump tees in its
[bores](pump-dock/README.md#the-tees-bores) behind the collet plate.
The front flanks are continuous across the fixed dock room.

The complete dock requires assembled physical qualification: the tees' seals and their
release under the collet plate, the tees' running fit in their bores,
the pump heads' tube clamps and the printed-in SB443-IN columns that seat the cartridge.
The [pump-holder acceptance](../../reference/kamoer-kphm400/physical-fit.json) and
[connector coupon acceptance](../../reference/yyfkgcp-pogo-4p/physical-observations.json)
retain their identified scopes; neither establishes the current wet seals or
retention under pressure.

The [manual mesh-interface review](pump-dock/lint-interface-review.json) records
the exact air/boundary classifier diagnoses, specific cosmetic flute contours and
unresolved sensor, floor, rear-interface, warning and lid-fixture sections. Its full
six-class readings and native/source correspondence establish their geometry scope;
physical print quality, cleanup and load capacity remain unqualified.

Every reviewed print archive, the printer and settings it is sliced for, the geometry it binds
by hash and its support-removal review are in the
[slice reviews](tee-readiness/full-enclosure-print/native-slice-reviews/README.md). What
printed, when and on which machine is in the [print log](enclosure/print-log.md).

Derek's PET-GF print request is the go and the plate-clear: send the named reviewed archive with the
black PET-GF mapping. There is no print order. A productive print keeps running while checks
proceed; a concretely defective one is cancelled and replaced.

New PET-GF jobs use the saved [PET-GF profile](../petgf.3mf): two ordinary wall loops,
15% gyroid infill, black PET-GF on the fixed left 0.4 mm nozzle and `auto_brim`.
The two-wall/15% gyroid baseline remains in use unless Derek explicitly requests a change;
comparison-print results alone do not change it. Local solid reinforcement and six-wall
surface bands retain their specified settings.
H2C uses +0.18 mm requested trim (+0.16 mm emitted for Textured PEI);
Mark2 uses +0.04 mm (+0.02 mm emitted). Both configured printable areas are 325 × 320 mm, with
at least 15 mm model border. Use a 0.20 mm first bed layer and 0.24 mm layers on
expanding print-down show edges, with an additive chamfer/taper and six walls locally.
Inward/top show rounds use 0.08 mm across their complete curved span. Other regions
use the normal 0.24 mm profile. Each actual slice reports
emitted brim and support paths, and every support contact has an accessible removal lane before
hardware installation, following the
[support-removal strategy](enclosure/README.md#support-removal-strategy).

The [trial preparation](trial-preparation/README.md) writes each piece's fresh native project
from its current mesh with this recipe: the measured fine and six-wall bands, support-blocked
show transitions, back-top's sliding-groove ribbons and tie-channel windows, and the
solid-host modifiers below. Its review reads each sliced archive for those readings.

Current fastener hosts and their roots also require the local 100% infill
[region specification](enclosure/heat-set-review/print-regions.json), including
the Y seam's interlocking blocks and their roots, Z hooks and end stops, and the
complete insert hosts and blind caps. The general 15% infill recipe does not
establish solid material in those regions. Each fresh native review must verify
their actual placement and emitted deposition as well as the show surfaces.
The manual specification also identifies the SB443-IN column walls, their roofs and roots, and the recessed pogo hosts. The tee caps use six walls and 100% infill throughout, standing on their fore ends as exported. Bind these settings and modifier regions to each production native project and emitted paths; they do not establish support removal or physical load capacity.
Each pump-dock job binds the current magnetic mounts and seating faces to its native
geometry. The [SB443-IN native reading](pump-dock/printed-capture-native-review.json)
records clear loading slots, one insertion pause per part and rail paths joined into
the parent wall throughout both columns of the four-block jobs it binds; its
[filament footprints](pump-dock/printed-capture-beads.png) show those connections.
The two-block slots have no native reading. The [RC62 print jobs](enclosure/magnet-retention/queue.json) are evidence for
their identified ring-magnet articles; their pauses and covering layers do not qualify
the bare-face SB443-IN columns loaded at front-top's and the cartridge plate's pauses.

Front-top's display backing is one continuous plane at Y92.75, with at least
3.016 mm behind the deepest display-pocket corner. The
[fixed pump lead review](enclosure/fixed-pump-lead-review.json) binds that wall to
its identified export. The fixed lead passes below the funnel frame; the
[installed wiring review](../../wiring/installed/above-core-review/README.md)
records the current conductor routes against the exported appliance. The magnet-rail exception
applies only to the groove rails; unrelated display and seam findings retain
their recorded scope.

The show transitions print without support contacts. Back-top's roof side edges use
the additive 0.24 mm treatment. Keep supports for separate functional features and
use face-specific blockers on the show transitions. Inspect all emitted support paths, including short bodies without labelled
interfaces, against the rounded surfaces before sending a slice. Previously prepared archives
also require this check; their 0.08 mm layer-band checks alone do not establish it.

The current [cartridge and bottom preparation policy](enclosure/layer-policy-correction/README.md)
uses 0.24 mm through the cartridge's additive upper hand-pocket transition and
the front-bottom/back-bottom flute runouts. Their shallow decorative fade does
not require fine layers. The cartridge's genuine lower inward/top rim retains
its 0.08 mm span. Each new native revision binds the frozen mesh, local wall
bands, required support paths and complete dense fastener hosts. The
[C3 hand-fit selection](enclosure/magnet-retention/fit-coupons/physical-fit-selection.json)
records the X/Y fit of its RC62 ring-magnet articles and retains that scope.

Measure each retained inward/top curve's print-Z span on the STEP, then run
`hardware/scripts/verify_round_layer_band.py` on the exported `.gcode.3mf` for that object and
span. The emitted wall layers must cover the full span at 0.08 mm; the range setting in the
project alone does not establish this. The first bed layer stays 0.20 mm; verify
the emitted overlap into the next layer. New meshes require fresh slices and
support reviews; old archives do not establish the new treatment.

Every spool is used fully, with reloading during a print as needed; remaining filament
quantity is not a launch condition ([filament-use policy](tee-readiness/full-enclosure-print/filament-use-policy.json)).

## Reviewed front-top v17 H2C archive

The [front-top v17 review](tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/README.md)
binds the native STEP/STL and saved PET-GF recipe to one unmodified H2C archive.
Its results apply only to the source hashes in that review; they do not certify
the current recessed insert seats, seam stations or solid host/root regions.
The [launch receipt](tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/front-top-h2c-launch.json)
records H2C's acceptance as task **1305315362** at **2026-10-03 15:22:21 UTC**,
with one Send and 267.488 seconds since Mark2's recorded acceptance.
It has 878 model layers and estimates **25 h 44 min 45 sec**. All actual model slabs
have finite left-tool roads and every native stock section component receives
model walls. The full roof-round span has 0.08 mm walls and first-layer overlap
passes. All 1,526,926 support roads clear the protected
native exterior show faces. The native review assigns the 76 support bodies routes
through the empty bay, display storey, exposed flanks and aft opening.
The complete flank jaw retains 3 mm tip stock and 2.532 mm frame clearance;
its local DC5 entry lane remains clear. Exact source/road records name the
retained pogo seat, display recess and funnel receiver mating transitions.
The [physical result](tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json)
is rejected: top-rim support removal is nearly impossible, supported 0.08 mm
material has extreme spaghettification, normal snug and tree supports are
fused into masses too large for their cavities, and one embedded tee-carrier
window-cover holder broke. The [seam and frame review](enclosure/y-seam-plain-review.json)
records closed native quadrants, full funnel-brim bearing and sampled assembly motions
for its listed artifacts. The [fit review](enclosure/y-seam-fit-review.json) records
finite native gaps and complete local stock for its identified exports. The
[frame motion record](../zone-c/funnel/integration-review/rail-motion-check.json) records
insertion and capture for its listed source and native hashes. Physical receiver/rail fit,
cleanup, loom retention, load capacity and lifetime remain unqualified. The
[flush-roof review](../zone-c/funnel/flush-roof-review/README.md) applies to its identified
frame and back-top geometry.

## Reviewed back-top v9 native archive

The [back-top v9 review](tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-back-top-current-mark2-v9/README.md)
binds its corrected PRV crown, native STEP/STL and saved PET-GF recipe to one
unmodified Mark2 archive. It has 813 model layers and estimates **26 h 8 min
54 sec**; it has not been submitted. Both initial crown slabs contain model
roads across the full crown. All 1,050,514 support roads clear the nine protected
native exterior faces, and the 13 bodies and 34 labelled contacts have removal
routes through the empty shell. Model and support borders meet the respective
15 mm and 5 mm requirements. The complete cable retaining seat and both jack
catches have dense emitted coverage. The ground mounting annulus's final round
terminal has an explicit 0.126 mm layer-lattice deviation. Physical insert and
cable retention, show finish, cleanup effort and assembled fit remain separate.
These results apply only to its bound source hashes. Current enlarged hosts,
recessed PCBA entries, complete solid roots and the capped `carb-1` rib with its two
bridged catch windows need their own native slice; the v9 support review supplies no
load-capacity or drop result.

## Physical evidence

| Part or interface | Established result and current use |
| --- | --- |
| Integral handhold ceilings | The production enclosure uses the bottom pieces' printed lifting ceilings as its gripping surfaces. One complete R6 opening and exterior transition spans the Y seam and is mirrored on the two flanks. Their current bare-surface finish, support cleanup, comfort and loaded lifting are unqualified. The [receiver/cover coupon acceptance](grip-cover/physical-acceptance.json) retains its identified test-article scope; accepted underside results on the faucet and other parts do not qualify these handholds. |
| Current back-top support cleanup and wall finish | The [identified Mark1 article](../drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/physical-result.json) has trapped, fragile sliding-groove stems and reinforcement-boundary tracks on both X+ wall faces. The [next-print preparation](../drain-readiness/prints/2026-10-11-back-top-groove-supports-mark1/README.md) uses 23 infill-only solid regions, three named local groove ribbons, the 50 mm bridge limit and normal Mark1 trim. Native readings find zero artificial box-face outer walls and no support in the declared tie-floor windows. Physical cleanup, finish and installed fit are unassessed. |
| Front-top v17 rim and support cleanup | Rejected for nearly impossible cleanup, fused normal/tree support masses, extreme supported fine-layer spaghettification and a broken tee-carrier window-cover holder. The [seam and frame review](enclosure/y-seam-plain-review.json) records native bearing, closed clearances and sampled assembly motions for its listed artifacts; the [fit review](enclosure/y-seam-fit-review.json) records its identified exports' finite gaps and local stock. The [flush-roof review](../zone-c/funnel/flush-roof-review/README.md) retains its identified geometry scope. Physical cleanup and assembled fit remain pending. [Physical result](tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json); [bounded tree-clearance correction](enclosure/support-bottom-gap/README.md). |
| Tee-carrier visible rounds | The additive bottom chamfer/taper is physically accepted. It uses a 0.20 mm first layer, 0.24 mm bottom/body, 0.08 mm top R6, six walls in the lower 6.1 mm, and saved wall-first order, speeds and 15% overlap. No supports. Sliding is accepted with 1.00 mm above and 0.25 mm below against the existing front-top, with less tilt reported. Spring return and other parts remain separate checks. [Surface record](tee-carrier/physical-acceptance.json); [sliding-fit record](tee-carrier/low-force-trial/physical-acceptance.json). |
| Kamoer cartridge and cap | Derek confirms both pumps are firmly held with screws tightened and no vertical play. The current cap keeps the broad fitted holder geometry; its surrounding crown reaches the cartridge top while motor ends and spade-terminal wells remain open. This holder result does not qualify the cap's pogo connector. Raised-crown fit and four-tube operation remain full-assembly observations. [Physical record](../../reference/kamoer-kphm400/physical-fit.json). |
| Pump cartridge electrical contacts | The YYFKGCP halves mount in pump-cap and front-top seats, each recessed 0.125 mm for a 0.500 mm nominal contact-face gap. The [mounting audit](../../reference/yyfkgcp-pogo-4p/mounting-audit.md) records its identified exports, nominal mating and conditional 0.200–0.800 mm compression range. The founder accepts connector fit and mating/compression in the printed test piece, reported 2026-10-04; that result retains its own seat geometry. Full-enclosure compression, insert retention, continuity, operating resistance and lifetime remain unmeasured. [Physical scope](../../reference/yyfkgcp-pogo-4p/physical-observations.json). |
| RC62 ring-magnet print articles | The [C3 open-pocket selection](enclosure/magnet-retention/fit-coupons/physical-fit-selection.json), [v4 lower-cradle result](enclosure/magnet-retention/v4/physical-result.json) and [H2C C3/V69 covering-layer acceptance](enclosure/magnet-retention/selected-fit-v1/h2c-v20/physical-acceptance.json) retain their recorded ring-pocket fit, rattle and first-layer scopes. They establish no SB443-IN mount fit, force, heat exposure or endurance. |
| Pump dock and SB443-IN seat | No physical result. Each purchased PP0208E tee stands in its bore through front-top's tee wall; the collet plate holds each branch collet pressed, and a lower return of two stem elbows and a straight tube joins each tee to its rear valve. The complete dock's insertion and withdrawal force, the tees' running fit in their bores, the magnets' seat and hold against pressure, sealing, cleanability and repeated service cycles remain physical qualifications. The tees, valves and tubing remain installed during customer pump replacement. |
| Beduan sockets | The [upright hand-fit selection](enclosure/magnet-retention/fit-coupons/physical-fit-selection.json) sets V69 / Ø6.90 mm for production sockets. V70 / Ø7.00 mm is the conditional alternate for a valve or print orientation that does not fit V69 well. The shared seat retains its exterior envelope and zip-tie passages. The earlier Ø7.2 coupon's easy-insertion and positive tie-retention result retains its [bound scope](../fixtures/valve-socket-fit/physical-acceptance.json). Installed tie access, retention force and endurance remain full-assembly observations. |
| Faucet lever | The flat-sided lever with the 9 mm cylinder channel has accepted fit and function. Reuse it. [Physical record](../faucet/lever-replica/physical-acceptance.json). |
| Faucet display cover | Its broad, substantial flexing walls and retaining lips work in PET-GF. This is Derek's accepted simple snap-fit example. [Physical record](../faucet/faucet-display-cover/physical-acceptance.json). |
| Machine display cover | The face-up flat-wing cover passes shaking and has accepted appearance with a small residual bow. Its receiver uses 0.30 mm body X per side and 0.60 mm above the wings. Front-top integrates those accepted pockets. The [bound native check](enclosure/accepted-fit-integration/current-geometry-check.json) records deeper-module clearance for its listed shell and frame source hashes. Physical full-shell fit remains separate. [Physical record](display-cover/face-up-trial/physical-acceptance.json). |
| Nameplate | The support-free face-up plate and raised artwork have accepted appearance. Fit is accepted on that pair with the receiver at 0.15 mm body X per side, 0.25 mm centered wing-tip X and 0.45 mm wing-thickness clearance. The current receiver keeps the body X and wing-thickness clearances and uses 0.30 mm wing-tip X with 0.15 mm back air, so that acceptance does not establish its fit. The [current fit review](enclosure/y-seam-fit-review.json) checks back-top's nominal gaps and complete receiver backing against the placed PSU. The [accepted pair](nameplate/horizontal-wing-trial/physical-acceptance.json) retains its scope; physical full-enclosure fit remains separate. |
| C14 inlet and cord | The identified inlet/C13 station has earlier acceptance in the [native interface record](tee-readiness/full-enclosure-print/hard-contact-review/README.md). The [October 17 assembly feedback](enclosure/assembly-fit-review/assembly-feedback.json) reports that the female side fits and the mating cord body needs 3 mm more X access. The [assembly-fit review](enclosure/assembly-fit-review/README.md) specifies a centered 28.3 × 19.3 mm cord bore, independent of the flange pocket's 0.65 mm per-edge X/Z clearance, fixed Y seating depth and screw stations. Physical fit of the wider bore is unmeasured. |
| G Ganen feet and flow | Derek identifies four identical flexible rubber feet with approximately 7 mm pads; they slide fore/aft independently and can be removed. Captured scan positions are not a fixed bolt pattern. Discharge is enclosure −X, corresponding to reference +Y at +90° yaw. Actual screw passage, washer seating and loaded rubber behavior remain assembly observations. [Sample authority](../../reference/g-ganen-pump/scan-evidence.json). |

## Above-core production geometry

The production arrangement uses the flat PCB/PSU, three core-owned upright
valve walls, compact water/gas fittings and core-owned meter in
[above-core.md](../../manifold-layout/above-core.md). Its printable set includes
the upper quadrants, cap/cup and lid interfaces, the empty electronics panel,
compact rear chips and the 35 mm deeper funnel family. The frame installs
vertically after the final connections, with the drain cradle snapped into its
3 mm web. Disconnect the drain tube or release that cradle before lifting
the frame.

The [cap review](../cold-core/foam-cap/above-core-native-review.json),
[rear identification review](rear-identification/native-review.json) and
[frame review](../zone-c/funnel/drop-in-review/native-review.json) state their
native-geometry scopes. The upper M5 joint’s common bearing plane permits
back-top to pass above the populated valve walls. The C14 flange is accessible outside the wall, with
washer-backed M3 × 10 screws in blind hosts. The low nameplate field retains
the accepted flat-wing receiver and 1.09 mm nominal core clearance.
The [populated closure review](../../mechanical-qualification/enclosure-above-core/README.md)
records sampled opening/closing motions and the raised joint's native stock.

Print preparations must name these exact production meshes and their support
contacts before claiming that the new interfaces are ready to print. Accepted
coupons, surfaces and connector fits in this file retain their recorded artifact
scope. They establish no complete-assembly fit, support cleanup, insertion force,
load capacity, pressure seal or lifetime for this arrangement.

## Pump tees and returns

Four purchased PP0208E tees take the pump tubes behind the collet plate. Each stands in a teardropped Ø17 mm bore through front-top's tee wall, which holds the branch collar in X and Z, and the collet plate holds its branch collet pressed. A lower return joins each tee's lower collet to its rear valve's bottom collet: a trimmed stem elbow in each and one straight LLDPE tube between them, the elbows' lowest surface 5.1 mm over the condenser's top at the east-outer station. A short upper tube joins the tee to its fore valve. The rear valve row stands 8 mm above its deck reference to clear the compressor and condenser, all four rear valves at one height. The valve elbow's stem cut allows a layout estimate of the valve's seat; actual fully seated marks govern the factory cuts.

Two more purchased PP0208E tees form the source crossbar. The PP0208E's registered envelope
uses a conservative Ø16.5 fixed collar, run in a Ø17.0 bore through the tee wall. The received-part
[run and branch measurements](../../reference/jg-pp0208e-tee/branch-operating-measurements.json)
retain their commercial-fitting scope. Customer pump withdrawal actuates the four pump tees'
branch collets and not the source tees'. See the [pump dock](pump-dock/README.md) for its
stations, manufacturing outputs and assembly order.

## Remaining work for the complete working appliance

The current record does not establish release of a complete production print set or
a machine ready to ship. The following work remains in the readiness assessment.
Each item needs a resolved design or a specific decision; a statement that it is
unmeasured does not by itself supply a task or test for the founder.

| Area | Work needed |
| --- | --- |
| Final pump dock | Bind the cartridge's and front-top's two-block magnet slots to their production projects and emitted paths. The tees' running fit in their bores and the release under the collet plate remain scoped to the actual parts. See the [pump dock](pump-dock/README.md). |
| Remaining enclosure geometry | Resolve the front-top seam-to-roof and display-wing corners, plus the sensor/scarf, rear-interface, handhold/floor, warning, lid-perimeter and valve-fixture findings in the [manual interface review](pump-dock/lint-interface-review.json) and the [front-top findings](../lint-answers/enclosure/enclosure/enclosure-front-top.lint-answers). Keep each classifier diagnosis and supported functional section tied to its exact feature; unresolved inherited geometry remains open. |
| Production deposition and finish | Complete fresh native preparations for the final meshes, dense fastener hosts and roots, support removal, visible transitions and the back-top sliding grooves. The rejected full-shell articles and accepted local surfaces above retain their recorded scopes. Prepared settings do not establish deposited material or usable cleanup. |
| Complete assembly | Close the current [assembly feedback](enclosure/assembly-fit-review/README.md) against the populated machine: cord and driver access, valve and tube installation, pump feet and washers, routing, lid/deck stations, funnel frame and all four closing quadrants. A nominal CAD gap is not complete assembly acceptance. Production LLDPE routes retain nominal ¼-inch and ⅜-inch outside diameters. |
| Cold-core moisture boundary | The warm-side closure is the foil bands on the dry casing seams ([seam review](../cold-core/foam-cap/seam-moisture-review.json)) plus, at final assembly, a 3M 425 foil collar pressed from each conduit's tube or cable onto the lid face round its annulus, the same at both copper exits, a foil patch over each cap-screw head pocket and over any cap foam left showing ([cold core](../../assembly/cold-core.md#7-final-assembly)). It needs no printed sealing land; its effect on condensation inside the core is unmeasured. |
| Condensate and refill water | Condensate is addressed by insulating the meter, union and tails and by the umbilical's drip loop. The funnel's integral silicone apron covers the exposed frame/roof joints to the exterior sides; its broad, flat underside rests on the roof. The [overflow review](../zone-c/funnel/overflow-review/README.md) records the native geometry and assembly checks. Physical overpour and roof-runoff exclusion remain unqualified. Floor water needs feet under the slab, a purchase. |
| Loads, retention and electrical contacts | Assess the complete grip-to-floor and seam load paths, fastener/insert backing, cartridge seats, the four-pair magnetic seat, the four tees' collet joints and pogo contacts for actual operating, handling and customer replacement conditions. The dock's geometric motion allowance still needs the manufacturing, temperature and loaded-deformation contributions. Complete-assembly pressure/leak/prime performance, repeated tube restraint in the collets, the magnets' hold against pressure on four tubes, holding/removal force, electrical continuity, cleanability/drainage and creep/lifetime remain open. The [mechanical register](../../mechanical-qualification/README.md) and [contact audit](../../reference/yyfkgcp-pogo-4p/mounting-audit.md) identify the current basis and limits. Coupon fit, magnet catalogue pull and saved infill settings retain their specific scopes. |
| Finished appliance function | Close the relevant material, cleaning, fluid, electrical, control and commissioning work in [concerns](../../concerns.md) and [acceptance and burn-in](../../assembly/acceptance-and-burn-in.md). Any resolution that changes a printed part, access, load path or manufacturing process belongs in this print's design review. The current Lillium-fed soda observation retains its complete stated scope. |

Known design and manufacturing problems are addressed before releasing the affected
print. The actual printed assembly then supplies the evidence that depends on real
parts: cleanup and finish, complete seating and closure, fluid sealing and retention,
electrical contact, handling and customer pump replacement. Its complete operating
and cleaning results are part of readiness for shipping; they are not waived by the
print's development stage. The design and the evidence need their own conclusions.

This is a manual assessment of the requested readiness question. It adds no recurring
commit, edit or build check and requests no measurement, destructive test or purchase.
Any proposed physical check needs its decision, complete procedure, available tools
and application-derived acceptance criteria before the founder is asked to run it.
