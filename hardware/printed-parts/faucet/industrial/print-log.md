# Industrial faucet print log

## Display seating feedback — 2026-10-24

The [eight photographs and physical observation](prints/2026-10-23-black-complete-mark2/physical-result/physical-result.json)
record an approximately 1.5 mm display/cover gap and substantial apparent tube
clearance on a black Industrial head. Derek requests removing the earlier
additional 1.5 mm of clearance, the original supports, and adding 1 mm foot
recesses at the same locations. The
[4.5 mm lower review candidate](display-seat-review/2026-10-24/README.md)
contains the requested geometry and before/after views. Its conservative
component model intersects the tube routes and tip. It has no physical fit
result or submitted print; production geometry remains the reference.

## Above-counter mounting gasket — 2026-10-23, Mark2

Mark2 accepted [one current Industrial TPU gasket](prints/2026-10-23-mounting-gasket-tpu85a-right06-mark2/README.md)
as task **1368637649** at **17:07 CDT**. The flat, centered gasket uses black
Bambu TPU 85A through the right fixed 0.6 mm nozzle, the cleared and glued
Engineering Plate at 35°C, zero added user Z trim and 225°C nozzle temperature.
The dense recipe has two Arachne walls, 100% zigzag infill and 0.30/0.18 mm layers.
The native estimate is 43 minutes / 5.88 g, with ten layers.

Every layer follows deposited tours through turns, with straight contained
transfers. All 3,955 native deposition commands are accounted for without
added plastic. Both openings remain present; no checked free attachment chord
crosses them, including the conservative 1 mm attachment-run check. In-part
retractions, Z hops and camera commands are absent. Timelapse is Off, bed
leveling On, flow and nozzle-offset calibration Auto. Native startup/shutdown
bytes and their entry/final positions are retained. Printed stringing,
flatness, counter fit and spill sealing are unreported.
At **17:15:51 CDT**, the exact task is RUNNING at **1/10** beyond plate
detection, with **225°C** at the right nozzle, **35°C** at the bed, timelapse
disabled, no print error and no HMS. Bambu Connect displays Printing, 1/10.

## Complete black faucet — 2026-10-23, Mark2

The [complete five-part plate](prints/2026-10-23-black-complete-mark2/README.md)
is task [1366512080](prints/2026-10-23-black-complete-mark2/launch.json),
observed accepted at 03:06:47 CDT in PREPARE with no reported fault. It contains
one base, shared tip, Industrial display cover, rigid counter plate and
side-down lever, using current source geometry, selected rear seams, base fine
bands, seven rim arcs, tip fins and hidden-root disc. The print uses black
PET-GF on Mark2's fixed left hardened standard-flow 0.4 mm nozzle, external
slot 254, Textured PEI and its +0.04/+0.02 mm trim.

Ordinary part and auxiliary cooling are off; bridges and qualifying overhangs
receive 70% after three fan-off layers. Bridge flow is 125%, bridges 15 mm/s
and overhang limits 15/10 mm/s. Timelapse and bed leveling are On, with flow
dynamic and nozzle-offset calibration Auto. The
[full settings export](prints/2026-10-23-black-complete-mark2/all-settings.json)
contains the prepared and native dictionaries, object/component settings,
filament presets and layer ranges. The native slice has no warnings, 1245
layers, 41.8755 mm minimum full-bead bed margin and an estimate of 6 h 48 min
35 s / 162.74 g at saved profile density. Physical completion and assembly
acceptance remain unreported.

## Complete faucet with selected edge supports — 2026-10-15

The [complete five-part run](prints/2026-10-15-all-learnings/README.md) is
Mark2 base task [1342687225](prints/2026-10-15-all-learnings/mark2/launch.json),
accepted at 13:19:25 CDT, and Mark1 tip, cover, rigid counter plate and lever
task [1342697013](prints/2026-10-15-all-learnings/mark1/launch.json), accepted
at 13:22:57 CDT. Starts are 212.222 seconds apart. Each plate contains only
the requested parts, with no repeat control. Native estimates are 4 h 21 min
51 s / 102.39 g and 2 h 29 min 42 s / 59.05 g at the saved profile density.

The base carries the physically accepted seven rim arcs and automatic trees.
The tip carries the accepted eight fins, local lip trees and directly bonded
hidden-root disc. All five parts retain the selected cooling, bridge flow,
overhang speeds, seams, layer bands and production geometry. Native root
starting-course bearing, visible-rim contacts, full-bead bed clearance and
each printer's own trim and spool mapping are recorded beside the jobs.
The complete faucet's physical result remains unreported.

## Rim support candidates — 2026-10-15

The [two single edge-support prints](../finish-coupons/2026-10-15-edge-supports/README.md)
are Mark1 task `1341173963`, a −105° tip section with the eight plain fins
retained and local trees added at the rough seam-side lip, and Mark2 task
`1341188908`, a −15° foot with seven curved rim fins and Tree(auto)/Default
on the remaining underside. The starts are 594.405 seconds apart. Each plate
has one candidate and no repeated control. The
[Mark2 physical result](../finish-coupons/2026-10-15-edge-supports/base-mark2/physical-result/physical-result.json)
accepts excellent edge support, very easy arc-fin snap-off and the best faucet
underside Derek has observed. The complete faucet project selects the exact
seven curved edge walls and narrow blocker strips, with trees elsewhere.
Mating fit and complete-height printing with those arcs remain unreported. The
[Mark1 physical result](../finish-coupons/2026-10-15-edge-supports/tip-mark1/physical-result/physical-result.json)
records failure of the male insertion section despite telemetry reporting
167/167 layers and `FINISH`. Native G-code starts that section at Z0.44 with
no lower-bead bearing and no model deposition on the bed course. A
[single corrected tip candidate](../finish-coupons/2026-10-15-tip-root-anchor/README.md)
adds a directly bonded sacrificial root foot, retaining the pose, eight fins,
lip support paint and material recipe. Native root bearing and lip contacts
are reviewed. The [corrected tip launch](../finish-coupons/2026-10-15-tip-root-anchor/mark1/launch.json)
is Mark1 task `1342500038`, accepted at 12:13:00 CDT on 2026-10-15 after Derek
confirmed both beds clear. The [physical result](../finish-coupons/2026-10-15-tip-root-anchor/mark1/physical-result/physical-result.json)
accepts the print and removable disc, with a removal scuff acceptable on the
hidden male insertion end. That bonded contact is unsuitable for a visible face.
Dimensional mating fit and removal force are unmeasured.

The [preceding tip result](../finish-coupons/2026-10-15-tip-fins/mark2/physical-result/physical-result.json)
records the best observed bottom-side rim appearance and a still-rough opposite
side. The [Full-annulus base result](../finish-coupons/2026-10-14-foot-fins-current-angle/full-annulus/mark1/physical-result/physical-result.json)
reports tighter material but better underside and front-face finish with trees.
The [selected complete-faucet recipe](finish-selection.json) retains 125% bridge
flow, 70% cooling after three fan-off layers, 15 mm/s bridges and overhang limits
at most 15 mm/s with the existing 10 mm/s limit retained. The
[whole-project command reading](overhang-native-review.json) covers all five rigid
parts, including Floating vertical shell. The complete project retains automatic
supports on the remaining surfaces. The curved base-rim treatment has direct
physical finish and release acceptance; the tip's local treatments remain
scoped to their candidates.

## Planned production approval — 2026-10-14

Derek's [physical inspection](prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json)
accepts the seam-fixed faucet as the official planned production model,
tagged `faucet-industrial-production-2026-10-14`. The exact Mark2 task
`1337767162` contains the corrected base and tip. Their meshes and seam paint
match the complete [production project](faucet-industrial-petgf.3mf), which
contains all five rigid parts. The cover, mounting plate and lever retain the
[accepted complete-print reference](prints/2026-10-13-a2-back-mark2/physical-result.json).

The saved [recipe](finish-selection.json) applies A2/Back/150% to base, tip
and mounting plate, complete rear seam enforcement to base and exposed
curved tip, default Aligned/15%/scarf-off seams to cover and lever, and eight
coarse lip layers before the 0.12 mm bands. The normal complete-print
requirement is retained.

## One-time base-only seam evaluation — launched 2026-10-13, Mark2

Derek explicitly limited [this evaluation](prints/2026-10-13-rear-seam-base-only-mark2/README.md)
to the base. Mark2 accepted task `1337160395` at 6:20 pm CDT with no reported
fault. The copied base retains the rear seam paint and saved recipe; the native
neck starts remain within 0.45 mm of center. Estimate: 3 h 54 min and 101.67 g.
The normal project remains the complete five-part faucet. The
[physical result](prints/2026-10-13-rear-seam-base-only-mark2/physical-result.json)
confirms the middle neck and reports both lower transitions still misplaced.

## Rear-center placement correction — prepared 2026-10-13

The [complete corrected slice](seam-placement/rear-center-v1/README.md) retains
all settings and geometry of task `1335906696` and adds rear-center seam paint
to the base neck. Its maximum measured start offset is 0.45 mm. The
identified candidate carries the height-limited enforcer. Its
[base-only physical result](prints/2026-10-13-rear-seam-base-only-mark2/physical-result.json)
confirms the middle neck and reports both lower transitions still misplaced.

## Selected Back/A2 recipe — launched 2026-10-13, Mark2

The [complete print](prints/2026-10-13-a2-back-mark2/README.md) is task `1335906696`.
Back applies to base, tip and mounting plate; A2 and 150% gap apply to those three.
Cover and lever use Aligned, 15% gap and scarf off. Wipe is off, and the eight
coarse lip layers and infill-only foot are retained. The source geometry matches
task `1334704608`, whose reported seam placement did not match the expected rear
line. Derek's [physical inspection](prints/2026-10-13-a2-back-mark2/physical-result.json)
accepts this as the best faucet print so far, with everything checking out well
apart from a seam swerve on the base gooseneck. The identified article and recipe
are tagged `faucet-industrial-approved-2026-10-13`.

## Selected SB/E complete faucet — launched 2026-10-11, Mark1

- Derek selected SB scarf gap 10% and E eight coarse layers from the
  [combined coupon plate](../finish-coupons/coarse-start-v1/combined/physical-result.json).
  He reports difficulty distinguishing scarf finishes, ugly recovery through
  four coarse layers, and recovery in the latter four layers of E. The
  supplied images identify the labels; they are not physical surface photos.
- The [complete five-part plate](prints/2026-10-11-scarf10-lift8-mark1/README.md)
  uses the current centered Industrial base, shared tip, cover, counter plate
  and side-down lever. Current source geometry retains the reviewed 70° joint,
  smooth common passages, 0.50 mm cover reach and unsealed Ø4 mm fault drip.
- The base retains eight 0.24 mm layers from the last-starting lip at nozzle
  Z15.32–17.00 mm, then 0.12 mm at Z17.12 mm. Fine bands are base-only
  Z17.00–29.00 and Z55.16–68.12 mm. All five parts carry SB contour scarf:
  10% slope gap, 10 mm length, 10% start height, ten steps, smart 155°,
  inner walls, partial loop, ordinary gap 15% and Back seam. Base Arachne and
  the continuous six-wall solid foot are retained.
- Mark1 uses black PET-GF in left external slot 254, fixed left hardened
  standard-flow 0.4 mm, Textured PEI and its normal +0.18/+0.16 mm trim.
  Saved temperatures, cooling and Tree(auto)/Default with all automatic
  sections are retained. Timelapse and leveling are On; dynamic-flow and
  nozzle-offset calibration are Auto. Probing clump detection is disabled.
- The [native review](prints/2026-10-11-scarf10-lift8-mark1/native-check.json)
  confirms exact meshes/poses, emitted scarf ramps, eight coarse layers,
  first/second-layer footprint contact, absent screw-host partition tracks,
  nominal reinforcement and at least 44.86 mm full-bead bed clearance.
  The insert reading projects scarf passes into nominal layers; it does not
  establish instantaneous scarf volume or deposited strength.
- Exact task/job `1329852853` and archive
  `2026-10-11-industrial-faucet-complete-scarf10-lift8-petgf-left04-z018-mark1.gcode.3mf`
  were observed RUNNING at 2026-10-11 16:31:18.176833 UTC / 11:31:18 am CDT,
  layer 0/1,244, no print error and no HMS fault. Both printers were freshly
  read before the single Send; the peer's known accepted start was over
  three minutes earlier. The two earlier sender transactions stopped before
  importing or sending. Original archive and G-code hashes and actual options
  are in the [receipt](prints/2026-10-11-scarf10-lift8-mark1/launch.json).
- Native estimate: 5 h 51 min 5 s, 160.72 g at saved profile density.
  Finish forecast from observed acceptance: 5:22 pm CDT, plus calibration
  and any pauses. Physical underside continuity, cleanup, seam finish and
  centered-mounting fit remain unassessed. Earlier shipping acceptance and
  its tag retain their original physical scope.

## Complete 0.12 mm shoulder faucet — held 2026-10-09, Mark2

- Complete five-part plate (`hardware/printed-parts/faucet/industrial/prints/2026-10-09-shoulders012-wing050-drip4-mark2/README.md`, in git at 45dd5672e9),
  including the side-down lever, corrected continuous six-wall solid foot,
  base Arachne and 15% infill/wall overlap.
- 0.20 mm first bed layers and normal 0.24 mm layers; the base alone uses
  0.12 mm at print Z13.40–29.00 and Z55.16–68.12 mm.
- Industrial cover wings extend 0.50 mm with matching arch headroom;
  retaining-lip datum and engagement are preserved. Physical seating is
  unassessed. The shared tip uses an unsealed pocket and a round Ø4 mm
  underside drip hole with no drain bungs or insertion tool.
- Derek requested: "Apologies, pause on that print". No import or Send was
  attempted for the held candidate. Its launch plan retains the hold and
  needs a separate go-ahead before fresh printer gates and one Send.
- Native and physical scope are recorded in the selection and exact job
  records. Beautiful 0.08 mm finish remains accepted only on its identified
  earlier complete article; 0.12 mm finish, corrected exterior and new drip
  behavior require observation.

## Complete variable-layer recipe — selected 2026-10-09

- Derek selects the earlier successful complete five-part print: base, shared
  tip, industrial display cover, counter plate and side-down lever. The
  [frozen recipe](prints/2026-10-09-two-shoulders008-with-lever-mark2/preparation.json) binds the archive and source
  hashes for Mark2 task/job `1322285082`.
- 0.20 mm first bed layer, 0.24 mm normal layers, and 0.08 mm on the base in
  print Z13.40–29.00 and Z55.16–68.12 mm only. Native estimate: 6 h 13 min 4 s.
- The [reported physical result](prints/2026-10-09-two-shoulders008-with-lever-mark2/physical-result/physical-result.json)
  accepts beautiful fine-band finish and removal of their few thin-layer
  supports. Lines/defects beside the screw points remain documented on this
  exact article. No further complete faucet is submitted by this selection.
- Variable layer height is the accepted shipping compromise; further
  whole-faucet 0.08 mm iteration and research are deferred. Selection does not
  establish structural strength, endurance or complete product qualification.

## Tip starting-band complete faucet — failed 2026-10-09, Mark2

- Exact accepted task/job `1324374637`,
  `2026-10-09-industrial-faucet-complete008-tip-root024-petgf-left04-z004-v6-mark2.gcode.3mf`.
  Archive SHA-256: `3dfb53e7a76e024790d88a4fbcfee1696c2c9e5a76e51989a1040cfeeb798c01`.
  The [physical record and five photographs](prints/2026-10-09-tip-root024-mark2/physical-result/physical-result.json)
  retain the exact G-code hash, original acceptance and process.
- Complete five-part black PET-GF plate, fixed left hardened 0.4 mm nozzle,
  Textured PEI, Mark2 +0.04 mm requested/+0.02 mm emitted trim. A 0.20 mm first
  bed layer is followed by 0.08 mm model layers except for the tip's eight
  0.24 mm starting layers through Z2.12, returning to 0.08 mm at Z2.20.
  Saved temperatures, speeds, tree supports and normal motion settings are
  retained. Base reinforcement is the continuous six-wall solid foot with
  Arachne and 15% infill/wall overlap.
- Derek reports failure of the tip and wing after they gained more height,
  noting their small XY footprint relative to Z. Tip photos show localized
  ragged/raised bands and loose strands. The rectangular display-cover wing
  region shows an uneven/separated edge and loose extrusion above standing
  supports. Loose debris is visible on the plate; the still photos do not
  establish whether a piece tipped, shifted or contacted the nozzle.
- Possible print-head dragging, potentially worsened by layer lifting, is
  Derek's hypothesis. The initiating event and failure height are
  unmeasured. No timelapse causal diagnosis is made for this article.
- A fresh matching-job reading at 2026-10-10 03:25:28 UTC reports `FAILED`,
  layer 0, print error 0 and no HMS entries. The terminal layer counter is
  not the photographed failure height; telemetry does not assess physical
  finish or identify the initiating event.

## Black PET-GF — 2026-09-18, Mark2

- Complete Industrial shell base, shared shell tip, Industrial display cover
  and Industrial above-counter plate. The gasket is a separate TPU print.
- CAD X rotations: base −15°, tip −105°, cover −50° bezel-up, plate 0°.
- Black Polymaker PET-GF loaded by Derek, with the existing PET-CF mapping
  on the left external spool and 0.4 mm nozzle. Right nozzle unused.
- The snap uses 1.25 mm inward preload per wing, 1.20 mm engagement,
  3.00 mm lips, 3.48 mm grooves, 0.48 mm roof clearance, 0.30 mm end
  clearance and 0.25 mm inner-edge relief. The shared tip and Industrial
  cover STL hashes match the passing 36-row cover-fit reading.
- The complete emitted profile matches the successful white Sculpted job:
  0.24 mm layers, 0.20 mm first layer, two walls, 15% grid infill, 265 °C
  first-layer / 280 °C later nozzle temperatures, and an 80 °C Textured PEI
  plate. Requested +0.18 mm Z trim emits `G29.1 Z0.16`.
- Native slice: 4 h 45 min 12 s, 131.23 g at the saved profile density,
  1,019 layers. Minimum toolpath bed margin 22.38 mm; separation 26.24 mm.
- Support reading: one base body/nine labelled islands, one shared-tip body
  with unlabelled interfaces, one cover body/two labelled islands and three
  plate counterbore bodies. No sampled cover outer-bezel or lip-bearing
  contact. Physical removal, finish and Industrial fit are not yet observed.
- Sent once through Bambu Connect as `industrial-black-z018-mark2.gcode.3mf`.
  Bed leveling On; timelapse Off; flow dynamic calibration and nozzle-offset
  calibration Auto.
- Telemetry at 2026-09-19 02:20:53 UTC confirms that exact job RUNNING,
  0/1,019 layers, 285 minutes remaining, no print error and no HMS entries.
- Native archive SHA-256:
  `e3abe2fe5eaf94d0c40a0c1fea98f7bac52f1fe052eb0a28154087b11ab5a3c3`.
  Project, source, profile, support and launch hashes are in the
  [readiness record](faucet-industrial-petgf.readiness.json).
