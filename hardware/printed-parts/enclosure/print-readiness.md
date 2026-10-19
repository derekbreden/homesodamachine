# Full enclosure print readiness

The complete enclosure trial prints the four shell quadrants (front-top, front-bottom,
back-top, back-bottom) and their separate parts: the pump cartridge and cap, four permanent
TPU dock receivers, four flat interior keepers and the common rear cuff support, the machine display cover and the two
G Ganen cold-core mounting parts. The fixed commercial tees mount behind the receiver wall.
The front flanks are continuous across the fixed dock room.

The four TPU receivers have a completed
[native plate preparation](pump-dock/print-preparation/2026-10-18-receivers-siraya85a-mark1/README.md)
using Siraya Tech Flex TPU85A Clear on the retained Mark1/right 0.6 mm Engineering
Plate recipe. Its emitted-path review covers all four parts, exterior support and
bore exclusion; the slicer estimates 2 h 14 min and 10.53 g including support/brim.
The archive is prepared for review and has not been sent to a printer. Internal
strands, support cleanup, seal fit and physical behavior remain unassessed on these receivers.
The remaining PET-GF dock parts require their own native slices. The complete pump
dock requires assembled physical qualification.
Its socket bores, flexible entrance funnels, keeper seating, rear cuff support, machined-stem flange capture, fixed tee support, positive
SB443-IN magnet capture and rigid cartridge stops belong to that qualification. The
[pump-holder acceptance](../../reference/kamoer-kphm400/physical-fit.json) and
[connector coupon acceptance](../../reference/yyfkgcp-pogo-4p/physical-observations.json)
retain their identified scopes; neither establishes receiver sealing or retention under pressure.

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

New PET-GF jobs use the saved [PET-GF profile](../petgf.3mf): black PET-GF on the fixed left 0.4 mm
nozzle and `auto_brim`. H2C uses +0.18 mm requested trim (+0.16 mm emitted for Textured PEI);
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
The manual specification also identifies the twelve dock-lock hosts, keeper guides,
magnet rails and bedding keys, rigid-stop roots, stem-flange shoulders, recessed
pogo hosts and the actual cut TPU mounting keys. Print the four station-specific
keepers, four cradles and four covers with six walls and 100% infill. Their
manufacturing exports already contain the print pose. Four M3×8 locks retain the
keepers; eight shared M3×12 locks fasten the cradles and covers. Those settings and
modifier boxes still require binding to each production native project and emitted
path review; they do not establish support removal or physical load capacity.
Each pump-dock job binds the current magnetic mounts and seating faces to its native
geometry. The [RC62 print jobs](enclosure/magnet-retention/queue.json) are evidence for
their identified ring-magnet articles; their pauses and covering layers do not qualify
the exposed-face SB443-IN mounts.

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
for its listed artifacts. The [current fit review](enclosure/y-seam-fit-review.json) records
finite native gaps and complete local stock for the production exports. The
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
recessed PCBA entries and complete solid roots need their own native slice;
the v9 support review supplies no load-capacity or drop result.

## Physical evidence

| Part or interface | Established result and current use |
| --- | --- |
| Integral handhold ceilings | The production enclosure uses the bottom pieces' printed lifting ceilings as its gripping surfaces. One complete R6 opening and exterior transition spans the Y seam and is mirrored on the two flanks. Their current bare-surface finish, support cleanup, comfort and loaded lifting are unqualified. The [receiver/cover coupon acceptance](grip-cover/physical-acceptance.json) retains its identified test-article scope; accepted underside results on the faucet and other parts do not qualify these handholds. |
| Current back-top support cleanup and wall finish | The [identified Mark1 article](../drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/physical-result.json) has trapped, fragile sliding-groove stems and reinforcement-boundary tracks on both X+ wall faces. The [next-print preparation](../drain-readiness/prints/2026-10-11-back-top-groove-supports-mark1/README.md) uses 23 infill-only solid regions, three named local groove ribbons, the 50 mm bridge limit and normal Mark1 trim. Native readings find zero artificial box-face outer walls and no support in the declared tie-floor windows. Physical cleanup, finish and installed fit are unassessed. |
| Front-top v17 rim and support cleanup | Rejected for nearly impossible cleanup, fused normal/tree support masses, extreme supported fine-layer spaghettification and a broken tee-carrier window-cover holder. The [seam and frame review](enclosure/y-seam-plain-review.json) records native bearing, closed clearances and sampled assembly motions for its listed artifacts; the [current fit review](enclosure/y-seam-fit-review.json) records the production exports' finite gaps and local stock. The [flush-roof review](../zone-c/funnel/flush-roof-review/README.md) retains its identified geometry scope. Physical cleanup and assembled fit remain pending. [Physical result](tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json); [bounded tree-clearance correction](enclosure/support-bottom-gap/README.md). |
| Tee-carrier visible rounds | The additive bottom chamfer/taper is physically accepted. It uses a 0.20 mm first layer, 0.24 mm bottom/body, 0.08 mm top R6, six walls in the lower 6.1 mm, and saved wall-first order, speeds and 15% overlap. No supports. Sliding is accepted with 1.00 mm above and 0.25 mm below against the existing front-top, with less tilt reported. Spring return and other parts remain separate checks. [Surface record](tee-carrier/physical-acceptance.json); [sliding-fit record](tee-carrier/low-force-trial/physical-acceptance.json). |
| Kamoer cartridge and cap | Derek confirms both pumps are firmly held with screws tightened and no vertical play. The current cap keeps the broad fitted holder geometry; its surrounding crown reaches the cartridge top while motor ends and spade-terminal wells remain open. This holder result does not qualify the cap's pogo connector. Raised-crown fit and four-tube operation remain full-assembly observations. [Physical record](../../reference/kamoer-kphm400/physical-fit.json). |
| Pump cartridge electrical contacts | The YYFKGCP halves mount in pump-cap and front-top seats, each recessed 0.125 mm for a 0.500 mm nominal contact-face gap. The [mounting audit](../../reference/yyfkgcp-pogo-4p/mounting-audit.md) records its identified exports, nominal mating and conditional 0.200–0.800 mm compression range. The founder accepts connector fit and mating/compression in the printed test piece, reported 2026-10-04; that result retains its own seat geometry. Full-enclosure compression, insert retention, continuity, operating resistance and lifetime remain unmeasured. [Physical scope](../../reference/yyfkgcp-pogo-4p/physical-observations.json). |
| RC62 ring-magnet print articles | The [C3 open-pocket selection](enclosure/magnet-retention/fit-coupons/physical-fit-selection.json), [v4 lower-cradle result](enclosure/magnet-retention/v4/physical-result.json) and [H2C C3/V69 covering-layer acceptance](enclosure/magnet-retention/selected-fit-v1/h2c-v20/physical-acceptance.json) retain their recorded ring-pocket fit, rattle and first-layer scopes. They establish no SB443-IN mount fit, force, heat exposure or endurance. |
| Permanent TPU pump dock and SB443-IN retention | The wall locates each asymmetric junction in X/Z and its flat interior keeper captures Y. Each rigid cradle and bolted cover support the four junction/return socket-stop locations and capture the TPU keys around straight tube links. The complete dock's insertion/withdrawal force, magnet capture, pressure retention, sealing, cleanability and repeated service cycles remain physical qualifications. The permanent wet parts and fixtures remain installed during customer pump replacement. |
| Beduan sockets | The [upright hand-fit selection](enclosure/magnet-retention/fit-coupons/physical-fit-selection.json) sets V69 / Ø6.90 mm for production sockets. V70 / Ø7.00 mm is the conditional alternate for a valve or print orientation that does not fit V69 well. The shared seat retains its exterior envelope and zip-tie passages. The earlier Ø7.2 coupon's easy-insertion and positive tie-retention result retains its [bound scope](../fixtures/valve-socket-fit/physical-acceptance.json). Installed tie access, retention force and endurance remain full-assembly observations. |
| Faucet lever | The flat-sided lever with the 9 mm cylinder channel has accepted fit and function. Reuse it. [Physical record](../faucet/lever-replica/physical-acceptance.json). |
| Faucet display cover | Its broad, substantial flexing walls and retaining lips work in PET-GF. This is Derek's accepted simple snap-fit example. [Physical record](../faucet/faucet-display-cover/physical-acceptance.json). |
| Machine display cover | The face-up flat-wing cover passes shaking and has accepted appearance with a small residual bow. Its receiver uses 0.30 mm body X per side and 0.60 mm above the wings. Front-top integrates those accepted pockets. The [bound native check](enclosure/accepted-fit-integration/current-geometry-check.json) records deeper-module clearance for its listed shell and frame source hashes. Physical full-shell fit remains separate. [Physical record](display-cover/face-up-trial/physical-acceptance.json). |
| Nameplate | The support-free face-up plate and raised artwork have accepted appearance. Fit is accepted with the receiver at 0.15 mm body X per side, 0.25 mm centered wing-tip X and 0.45 mm wing-thickness clearance. The [current fit review](enclosure/y-seam-fit-review.json) checks back-top's nominal gaps and complete receiver backing against the placed PSU. The [accepted pair](nameplate/horizontal-wing-trial/physical-acceptance.json) retains its scope; physical full-enclosure fit remains separate. |
| C14 inlet and cord | The identified inlet/C13 station has earlier acceptance in the [native interface record](tee-readiness/full-enclosure-print/hard-contact-review/README.md). The [October 17 assembly feedback](enclosure/assembly-fit-review/assembly-feedback.json) reports that the female side fits and the mating cord body needs 3 mm more X access. The [assembly-fit review](enclosure/assembly-fit-review/README.md) specifies a centered 28.3 × 19.3 mm cord bore, independent of the flange pocket's 0.65 mm per-edge X/Z clearance, fixed Y seating depth and screw stations. Physical fit of the wider bore is unmeasured. |
| G Ganen feet and flow | Derek identifies four identical flexible rubber feet with approximately 7 mm pads; they slide fore/aft independently and can be removed. Captured scan positions are not a fixed bolt pattern. Discharge is enclosure −X, corresponding to reference +Y at +90° yaw. Actual screw passage, washer seating and loaded rubber behavior remain assembly observations. [Sample authority](../../reference/g-ganen-pump/scan-evidence.json). |

## Permanent junction and return support

Four asymmetric TPU junctions connect through straight links and four fixed TPU
returns. The wall and flat keepers locate the junctions; the twelve rigid PET-GF
keepers, cradles and covers retain the permanent wet assembly. Each cover shares
its cradle's two M3×12 locks, so the retained wet body and cover cannot leave the
bolted base together. Tube-end stops and the closed diagonal guides constrain
withdrawal and bowing. Assembly clearance, loaded stop movement and permanent
seal life remain properties of the complete built article.

The two purchased PP0208E tees form the source crossbar. Their registered envelope
uses a conservative Ø16.5 fixed collar and Ø17.0 journal. The received-part
[run and branch measurements](../../reference/jg-pp0208e-tee/branch-operating-measurements.json)
retain their commercial-fitting scope. Customer pump withdrawal does not actuate
those collets. See the [permanent dock](pump-dock/README.md) for its station-specific
manufacturing outputs, fixture load paths and assembly order.

## What the trial establishes

The complete printed assembly establishes valve and permanent wet-fixture installation;
simultaneous four-stem insertion and withdrawal; permanent-receiver capture and
sealing; pump mounting, connectors and primed operation; and shell
closure. G Ganen screw/washer seating and rubber compression, DIGITEN arrow orientation, and
actual made-up gas-fitting fit are direct assembly observations. They do not require another
scan or a separate coupon before the trial. Production LLDPE routes retain nominal ¼-inch and
⅜-inch outside diameters.

Complete enclosure fit is an **outcome of this trial**, not a prerequisite to printing it.
