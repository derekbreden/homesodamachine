# Full enclosure print readiness

The complete enclosure trial prints the four shell quadrants (front-top, front-bottom,
back-top, back-bottom) and the separate parts that go into them: the tee carrier plate and its
two window covers, the pump cartridge and cap, the machine display cover and the two G Ganen
cold-core mounting parts.

Every reviewed print archive, the printer and settings it is sliced for, the geometry it binds
by hash and its support-removal review are in the
[slice reviews](tee-readiness/full-enclosure-print/native-slice-reviews/README.md). What
printed, when and on which machine is in the [print log](enclosure/print-log.md).

Derek's print request is the go and the plate-clear: send the named reviewed archive with the
black PET-GF mapping. There is no print order. A productive print keeps running while checks
proceed; a concretely defective one is cancelled and replaced.

New jobs use the saved [PET-GF profile](../petgf.3mf): black PET-GF on the fixed left 0.4 mm
nozzle and `auto_brim`. H2C uses +0.18 mm requested trim (+0.16 mm emitted for Textured PEI);
Mark2 uses +0.04 mm (+0.02 mm emitted). Both configured printable areas are 325 × 320 mm, with
at least 15 mm model border. Use a 0.20 mm first bed layer and 0.24 mm layers on
expanding print-down show edges, with an additive chamfer/taper and six walls locally.
Inward/top show rounds use 0.08 mm across their complete curved span. Other regions
use the normal 0.24 mm profile. Each actual slice reports
emitted brim and support paths, and every support contact has an accessible removal lane before
hardware installation, following the
[support-removal strategy](enclosure/README.md#support-removal-strategy).

Current fastener hosts and their roots also require the local 100% infill
[region specification](enclosure/heat-set-review/print-regions.json), including
the Y seam shanks, sockets and fore ligaments, Z hooks and end stops, and the
complete insert hosts and blind caps. The general 15% infill recipe does not
establish solid material in those regions. Each fresh native review must verify
their actual placement and emitted deposition as well as the show surfaces.
The separate [RC62 jobs](enclosure/magnet-retention/queue.json) bind their own
revised geometry and local settings; only a passing emitted-path record supports
submission.

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
bands, required support paths and complete dense fastener hosts; preferred
magnet grip remains pending the open-pocket samples.

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
window-cover holder broke. The [front-only flush sliding funnel frame](../zone-c/funnel/flush-roof-review/README.md)
has a flat display backing and complete 9 mm roof flanks, removes the fixed inward
roof ledge and passes native bearing, shell clearance
and insertion checks against the retained back-top. Its physical result is pending. Printed
receiver/rail fit, loom retention, load capacity and lifetime remain unqualified.

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
| Front-top v17 rim and support cleanup | Rejected for nearly impossible cleanup, fused normal/tree support masses, extreme supported fine-layer spaghettification and a broken tee-carrier window-cover holder. The [front-only flush roof and sliding frame](../zone-c/funnel/flush-roof-review/README.md) pass native bearing and clearance checks against the existing back-top. Physical cleanup and assembled fit remain pending. [Physical result](tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json); [bounded tree-clearance correction](enclosure/support-bottom-gap/README.md). |
| Tee-carrier visible rounds | The additive bottom chamfer/taper is physically accepted. It uses a 0.20 mm first layer, 0.24 mm bottom/body, 0.08 mm top R6, six walls in the lower 6.1 mm, and saved wall-first order, speeds and 15% overlap. No supports. Sliding is accepted with 1.00 mm above and 0.25 mm below against the existing front-top, with less tilt reported. Spring return and other parts remain separate checks. [Surface record](tee-carrier/physical-acceptance.json); [sliding-fit record](tee-carrier/low-force-trial/physical-acceptance.json). |
| Kamoer cartridge and cap | Derek confirms both pumps are firmly held with screws tightened and no vertical play. The current cap keeps the broad fitted holder geometry; its surrounding crown reaches the cartridge top while motor ends and spade-terminal wells remain open. This holder result does not qualify the cap's pogo connector. Raised-crown fit and four-tube operation remain full-assembly observations. [Physical record](../../reference/kamoer-kphm400/physical-fit.json). |
| Pump cartridge magnetic contacts | The YYFKGCP halves mount in pump-cap and front-top seats. Current exported seats and nominal mating pass the [mounting audit](../../reference/yyfkgcp-pogo-4p/mounting-audit.md). A separate [RC62 pair](enclosure/magnet-retention/README.md) has one paused-in ring in the lower cradle and one in front-top, centered on the tube axes. Its native geometry and independent paused sources are reviewed. The completed Mark2 lower-cradle print has its ring sealed in, with rattle and a wonky first covering layer reported; [open X/Y fit samples](enclosure/magnet-retention/fit-coupons/README.md) select the preferred grip. Full-assembly seating force and heat exposure remain unmeasured. The founder accepts connector fit and mating/compression in the printed test piece, reported 2026-10-04. Numerical full-enclosure compression, insert retention, continuity, magnetic retention, operating resistance and lifetime remain unmeasured. [Physical scope](../../reference/yyfkgcp-pogo-4p/physical-observations.json). |
| Beduan sockets | The Ø7.2 coupon has accepted easy insertion with zip ties providing positive retention. Derek requests a tighter front-top hand fit; [five upright four-post panels](../fixtures/valve-socket-fit/tighter-trial-v2/README.md) compare Ø7.2–6.8 sockets in production orientation. The preferred diameter is pending his sample selection. Production sockets retain Ø7.2 and zip ties. Installed tie access remains a full-assembly observation. [Accepted scope](../fixtures/valve-socket-fit/physical-acceptance.json); [tighter-fit request](../fixtures/valve-socket-fit/tighter-trial-v2/physical-request.json). |
| Faucet lever | The flat-sided lever with the 9 mm cylinder channel has accepted fit and function. Reuse it. [Physical record](../faucet/lever-replica/physical-acceptance.json). |
| Faucet display cover | Its broad, substantial flexing walls and retaining lips work in PET-GF. This is Derek's accepted simple snap-fit example. [Physical record](../faucet/faucet-display-cover/physical-acceptance.json). |
| Machine display cover | The face-up flat-wing cover passes shaking and has accepted appearance with a small residual bow. Its receiver uses 0.30 mm body X per side and 0.60 mm above the wings. The current front-top integrates those pockets; the complete deeper module clears the shell and current funnel in the [current native check](enclosure/accepted-fit-integration/current-geometry-check.json). Physical full-shell fit remains separate. [Physical record](display-cover/face-up-trial/physical-acceptance.json). |
| Nameplate | The support-free face-up plate and raised artwork have accepted appearance. Fit is accepted with the receiver at 0.15 mm body X per side, 0.25 mm centered wing-tip X and 0.45 mm wing-thickness clearance. The current back-top contains the accepted receiver geometry with native PSU clearance verified in the [current interface check](enclosure/accepted-fit-integration/README.md). The [accepted pair](nameplate/horizontal-wing-trial/physical-acceptance.json) retains its scope; physical full-enclosure fit remains separate. |
| C14 inlet and cord | Derek accepts the printed inlet/C13-cord station. Its fitted pocket and screw stations are preserved; the reference uses the measured flange outline and R6 corners. [Native interface evidence](tee-readiness/full-enclosure-print/hard-contact-review/README.md). |
| G Ganen feet and flow | Derek identifies four identical flexible rubber feet with approximately 7 mm pads; they slide fore/aft independently and can be removed. Captured scan positions are not a fixed bolt pattern. Discharge is enclosure −X, corresponding to reference +Y at +90° yaw. Actual screw passage, washer seating and loaded rubber behavior remain assembly observations. [Sample authority](../../reference/g-ganen-pump/scan-evidence.json). |

## Tee and release face

The registered tee envelope uses a conservative Ø16.5 fixed collar and Ø17.0 journal,
leaving 0.25 mm radial running air. Derek's run span is 42.5 mm extended / 39.2 mm pressed,
with 1.65 mm travel per run end. The branch measures **30.5 mm extended / 29.0 mm pressed**,
with **1.5 mm travel**; only the small outermost ring moves. The branch face stations
22.35 / 20.85 mm use the nominal Ø16.3 back-collar datum. The conservative clearance
envelope is a separate dimension. [Measurements](../../reference/jg-pp0208e-tee/branch-operating-measurements.json).

The Ø8.5 circular release aperture retains annular bearing against the observed terminal
face. The [terminal-bearing review](../../reference/jg-pp0208e-tee/terminal-bearing-review.json)
supports the full trial without another ring scan or caliper reading. Simultaneous contact,
release and relocking of all four actual rings remain physical checks.

## What the trial establishes

The complete printed assembly establishes valve tie installation; four-tube insertion,
capture, release and relocking; pump mounting, connectors and primed operation; and shell
closure. G Ganen screw/washer seating and rubber compression, DIGITEN arrow orientation, and
actual made-up gas-fitting fit are direct assembly observations. They do not require another
scan or a separate coupon before the trial. Production LLDPE routes retain nominal ¼-inch and
⅜-inch outside diameters.

Complete enclosure fit is an **outcome of this trial**, not a prerequisite to printing it.
