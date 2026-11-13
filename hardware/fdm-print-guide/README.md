# FDM print guide

Start with the fundamentals, then follow the entry for the feature, filament or
printer in your task. The linked part recipes and native reviews supply the full
settings. Physical observations stay with the print they describe.
[Illustrated PDF](fdm-print-guide.pdf) · [Website reader](https://homesodamachine.com/read/fdm-print-guide/fdm-print-guide.pdf)

| When you are working on | Start here |
| --- | --- |
| A bridge, fit coupon, layer schedule or support | [Fundamentals](#fundamentals) |
| The handholds or sliding rails | [Enclosure front-bottom](#enclosure-front-bottom) |
| A rigid structural part or faucet | [PET-GF](#pet-gf) |
| A reservoir, lid or small PETG part | [Clear PETG and PETG Basic](#clear-petg-and-petg-basic) |
| A gasket, sleeve, grommet or elbow | [TPU](#tpu) |
| The float or its magnet insertion | [ASA Aero](#asa-aero) |
| Printer, hotend, plate, trim or recovery | [Bambu Lab H2C](#bambu-lab-h2c) |
| Why a process or part changed | [Trial history](#trial-history) |

## Fundamentals

### Bridges and corbels

A bridge needs a landing at **both ends**. In the production pose, read the
first lines that span the opening, including the perimeter across the mouth.
Trace both ends onto material already deposited in the preceding courses.
A slicer's Bridge label alone tells you which process it selected. A relief
that removes a column leaves a span without its second landing. A corbel carries each new course
on the preceding one as the wall advances. Check overlap along the length of
the feature, especially where a straight face meets a corner or a seam.

Use the shorter span when it has two continuous landings. Preserve bearing and
fit faces and the stock that carries them. Put any slope or reinforcing stock
behind the working face where the design allows it. Read bridges and supports
at their actual printed orientation. [Enclosure support-removal strategy](../printed-parts/enclosure/enclosure/README.md#support-removal-strategy) · [Wago roof failure and photos](https://github.com/derekbreden/homesodamachine/blob/a8f24b2b5d16fcc4a23abb2832802df7cbcf50ca/hardware/print-tests/front-top-wago-fit/2026-11-12-mark2/physical-result/physical-result.json)

Keep each load-bearing body continuous. Merge adjoining stock that serves the
same function. Remove remnant edges and thin fins unless the feature needs
them for release, retention or flex. Coupon walls carry the same seat and
landings as the production feature when the experiment is comparing fit.
[Enclosure geometry rules](../printed-parts/AGENTS.md#supports)

### Layer height and fit

Keep the production layer schedule, orientation and process settings when
comparing geometry or fit. Layer height changes where a floor or roof lands
and how much of a bead is carried by the preceding course. It also changes
support separation, deposition timing and the thermal conditions at the
overhang. Read the emitted Z opening from the last solid floor course to
the underside of the first roof course. If a requested change slices to
the same opening, report it. Compare each size separately.

Fine layers belong to a named, reviewed process or a layer-height experiment.
The selected enclosure recipe uses a local band on specified inward/top
show rounds. Its expanding print-down transitions use geometry and ordinary
layers. The full Industrial and Sculpted faucet production recipes use
their ordinary layer schedule. Preserve the native layer heights on a fit
plate, including the first layer. [Wago standard-layer reading](https://github.com/derekbreden/homesodamachine/blob/ae3a1e7b7f32f119eacd22981c5fe22108f52d30/hardware/print-tests/front-top-wago-fit/2026-11-12-mark1-dots-3-4-standard-layers/print-job.json) · [Faucet fine-layer failure](https://github.com/derekbreden/homesodamachine/blob/a52c29539341168479df7e6e0f836ef37ed8c516/hardware/printed-parts/faucet/industrial/prints/2026-10-09-tip-root024-mark2/physical-result/physical-result.json) · [Enclosure layer features](../printed-parts/enclosure/trial-preparation/README.md#declared-features)

### Support and removal

For each intentional supported face, find the actual contact, the root
that carries it, the route a tool takes and the opening the support leaves
through. Check the first model courses above the contact. Include support
paths without interface labels. A dense interface can hold a roof together
for removal. It still needs suitable roots, separation and an exit.

Keep normal supports out of enclosed cavities. Use the part's prescribed tree
style and confirm where its trees actually start. A supported flat bearing can
be the simplest solution when a tool reaches it and the support can leave cleanly.
For an inaccessible receiver, keep the hardware's seat and movement envelope
and use the part's bridge, corbel, or rooted geometry. [Support rules](../printed-parts/AGENTS.md#supports) · [Full enclosure strategy](../printed-parts/enclosure/enclosure/README.md#support-removal-strategy) · [Rear receiver access evidence](https://github.com/derekbreden/homesodamachine/blob/65066d840d91f1a18332a0be6c9940d14a5190fc/hardware/printed-parts/enclosure/enclosure/prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json)

### From model to bench

Use the named part's current construction, production STL, saved project and
preparer. Read the emitted paths in the ready archive for the question at hand.
Geometry describes the shape. The slice describes where material is commanded,
including supports, trim, tool assignment and cooling. A physical result
describes the tested print. Keep the result's scope when applying it to another
pose, material, feature or scale. [Print-preparation review](../printed-parts/enclosure/trial-preparation/README.md#review) · [Mesh review](../../tools/hsm/mesh-review/README.md)

Save a result with the article, project or archive identity, printer job,
settings and the operator's observations. Link the archived Git revision for
completed or retired trials. Use the fitted ledger for physical fit of the
named production part. [Print and publication workflow](../printed-parts/AGENTS.md#publish-loop) · [Fitted ledger](../ledger/fitted.json)

## Enclosure front-bottom

Use this part to study how one design makes support removal easy. The
continuous handhold corbels carry their own gripping roofs in the normal
build direction. The reviewed front-bottom slice has one east and one west
supported face, both flat roofs of the sliding-rail cavities. Its support trees
start on the cavity floors. The open sliding lanes give a tool room to pry
and the freed support room to come out before assembly. Keep the complete
rail bearing, the corbel and the lane.

The rail coupon released as a single piece and its mate slid in. Derek's
full-part observation identifies short, cavity-rooted trees as easy to remove.
The support-contact review documents the two roofs for the named full-part
slice. Coupon looseness is a reason to check the full-length assembly before
changing clearance. [Open front-bottom in the machine](https://homesodamachine.com/3d#step:manifold-layout%2Fenclosure-assembly.step?find=solid%3A%20enclosure-front-bottom) · [Contact review](../printed-parts/enclosure/enclosure/prints/2026-11-11-front-bottom-D-mark2/support-contact-review.json) · [Tool access and roots](../printed-parts/enclosure/enclosure/front-rail-support-review.json) · [Rail coupon result and photos](https://github.com/derekbreden/homesodamachine/blob/4642937f98c1b55f2ae3cc0b15b10e39e1f027a4/hardware/print-tests/petgf-dense-roofs/rail-fit-30/physical-result.json)

## PET-GF

**Start with the shared project.** The [Polymaker Fiberon PET-GF15 project](../printed-parts/petgf.3mf)
carries the full machine, process and filament settings. Use the left abrasive
path with the recorded nozzle, bed and printer trim for the selected part.
The printer can report the spool as PET-CF. Read the selected material and
nozzle row in the archive and match it to the loaded spool.

**Cooling follows deposited paths.** Leave ordinary part and auxiliary cooling
off. The shared project applies part cooling to bridges and qualifying
overhangs. The output stage follows those paths into their fresh foundation
courses above and limits recovery deposition to the bridge speed there. Part
recipes may name additional local cooling. Read the native paths and
commands when diagnosing a surface or bond. Use the production batch's time
between visits when comparing small parts. A qualified single-part recipe may
create that interval with a separate tower. [Cooling and recovery policy](../printed-parts/cooling/README.md) · [Fan-off cover result](https://github.com/derekbreden/homesodamachine/blob/9ae148e1d78407917c1e8f6d0a78132e2fcbae5c/hardware/printed-parts/faucet/faucet-display-cover/prints/2026-10-17-cooling-off-prepared-mark2/physical-result.json) · [Recovery implementation and rollout](https://github.com/derekbreden/homesodamachine/commit/f62c528c4952e5a24860e2be57f77749d0bbb6c9)

**Support D is the shared contact and bridge recipe.** It defines the dense
interface, its top gap and bridge flow and speed. Tree style, roots, contact
footprint, authored fins and clear passages belong to the part. Flat rail
release has physical evidence. For the faucet, keep the selected rim fins,
shared contact band and contoured first perimeter. Bridge the insert shoulders
and pilots and keep their blind recesses clear. The angled-contact trials
document where stems tore and where an interface and support lifted together.
Use the complete part's selected recipe and its reviewed native archive.
[Support D settings and rollout](../printed-parts/support-D-rollout.json) · [Industrial recipe](../printed-parts/faucet/industrial/faucet-industrial-petgf.md) · [Sculpted recipe](../printed-parts/faucet/sculpted/README.md) · [Inclined support failure](https://github.com/derekbreden/homesodamachine/blob/de202da37ef6b132a07fe1863b304381f4ccc394/hardware/print-tests/petgf-dense-roofs/D-representative-mark2/physical-result.json) · [Rim release](https://github.com/derekbreden/homesodamachine/blob/b388123d2ac2fdc31fd091f980334b9c99443ab8/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/physical-result.json)

**Fit pressure is a separate question.** A Wago can enter at an angle by
flexing the receiver. Forcing it straight can split the edge. Test insertion,
retention and lever access on the intended walls with the production depth and
layer direction. [Cracked receiver and caliper readings](https://github.com/derekbreden/homesodamachine/blob/cbd8efc66d97a04f201751ebca58af4a1dcfe3d5/hardware/print-tests/front-top-wago-fit/2026-11-12-mark1/physical-result/physical-result.json)

## Clear PETG and PETG Basic

**Clear PETG reservoirs.** Use the selected left hotend, glued Engineering
Plate, body recipe and spool order from the current print records. The body
uses multiple Arachne walls, a specified flow and floor-fill overlap, and
ironing off. Review how the floor roads join the walls and read the physical
water-hold result separately. The identified left article held water at the
time of the report. The earlier photographed leak was reported at the
wall/floor-fill line, with its task identity and internal leak path unresolved.
The flat-square finish comparison selected ironing off for this recipe.

**Clear PETG lids.** The open ports take separate TPU grips. Use the lid's
saved support-free recipe and read the port cores all the way through. The
countersinks carry themselves and the screw seats bridge their clearance
bores. The tube and grommet provide the intended connection.
[Reservoir and lid recipes](../printed-parts/cold-core/reservoir/README.md) · [Full selected body settings](../printed-parts/cold-core/reservoir/prints/2026-10-26-mark1-left-engineering-flow105-overlap50-temp260-left08-z000/settings.json) · [Left water-hold result](https://github.com/derekbreden/homesodamachine/blob/d8b36a14b7da88039b67198fa4d150a9d0dd8003/hardware/printed-parts/cold-core/reservoir/prints/2026-10-26-mark1-left-engineering-flow105-overlap50-temp260-left08-z000/physical-result/physical-result.json) · [Leak report and photos](https://github.com/derekbreden/homesodamachine/blob/09e7854ea837782a2a196e41c560f40d17823a67/hardware/printed-parts/cold-core/reservoir/water-hold-evidence/2026-10-26-two-hour-leak/physical-result.json) · [Ironing study](../printed-parts/cold-core/reservoir/ironing-study/README.md) · [Lid preparation](../printed-parts/cold-core/reservoir/prints/2026-10-26-mark1-lids-flush-grips-no-supports/README.md)

**PETG Basic parts.** The black funnel cover project supplies the filament
profile for the PRV shroud, reed bridge, coil mandrel, setting gauge and fuse
clamp. Use the named part’s process overrides and pose. Read the relevant
open cavity, lead groove or locating feature. Dual-nozzle identification
pieces use their own plate and registration. [Black PETG project](../printed-parts/zone-c/funnel-cover/funnel-cover-petg.3mf) · [Part recipes](../printed-parts/enclosure/trial-preparation/README.md#recipe) · [Identification plate](../printed-parts/enclosure/display-cover/prints/2026-11-08-identification-set-mark1-right-z005/physical-result.json)

## TPU

Use the named stock, hardness, external feed path, nozzle, plate and trim for
the particular sleeve, gasket, grommet or elbow. Print flat seals in their
saved pose. For soft hollow parts, inspect where a strand can attach when
the nozzle leaves a wall. Keep articles close where the recipe allows and
check actual travel across openings. The deposited-path elbow and sleeve
require their processed archives. Opening their editable projects shows the
geometry and recipe. The selected path processing is part of what prints.

The Siraya elbow trial reports no visible strings and a qualitative seal
comparison. The Bambu sleeve result covers general print quality. The
white Sculpted gasket and reservoir grips have separate recipes and
qualification records. A cap's CAD thickness and the deposited solid cap
can differ with a spiral recipe. [Siraya elbow result](https://github.com/derekbreden/homesodamachine/blob/5b0d29be2fe9dc792998a0a165f77e78acd801e0/future/pump-elbow-exploration/prints/2026-10-22-deposited-links-siraya85a-mark2/physical-result.json) · [Bambu sleeve and processed archive](../printed-parts/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/README.md) · [White gasket recipe](../printed-parts/faucet/above-counter-gasket/prints/2026-10-16-white-tpu90a-right-mark1/README.md) · [Reservoir grip recipe](../printed-parts/enclosure/trial-preparation/README.md#recipe)

## ASA Aero

Use the float's selected dry feed, nozzle, chamber, flow and nested-wall
recipe together. Foaming and retained density depend on deposition conditions.
At the programmed pause, seat the magnet below the pocket rims with the
bore clear and the print still attached. Read the pause, first covering
roads and their inner and outer landings in the native slice. The observed
trial covers seating and initial overprinting. Measure the finished float's
lift and reed response when qualifying it for use.
[Float recipe and preflight](../printed-parts/cold-core/magnetic-float/all-aero/README.md#current-cad-and-print-preparation) · [Overprint observation and photo](https://github.com/derekbreden/homesodamachine/blob/a992c49c6069b824c81cbce32578fa2b4fa99490/hardware/printed-parts/cold-core/magnetic-float/all-aero/physical-observations.json) · [Installed float calibration](../printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration)

## Bambu Lab H2C

Mark1 uses the connection key `H2C`. Match the target printer, mounted nozzle and side, loaded material, plate
and effective Z trim before sending. Confirm the trim in startup G-code.
Center small plates on seasoned area and measure the whole deposited
footprint, including brim and supports. Check the live machine state and
leave the recorded shared-circuit interval between starts or resumes on
different machines. Verify the new task ID, archive identity and first
model layer when following startup. Use Bambu Connect or Studio for
protected printer controls. A user instruction to start on the named
machine confirms its bed is clear. Use suitable spools through runout.

For extrusion overload after sitting loaded, follow the recorded
cut, unload, pull, reload and resume procedure when that error occurs.
Keep the source project, reviewed G-code and operator results associated
with the same job. [Printer runbook](../../tools/bambu-printers.md) · [Bed placement](../../tools/bambu-printers.md#placement-on-unseasoned-plates) · [Trim by machine and plate](../../tools/bambu-printers.md#z-trim) · [Shared circuit](../../tools/bambu-printers.md#shared-circuit-startup-spacing) · [Overload recovery](../../tools/bambu-printers.md#extrusion-overload-after-sitting-loaded) · [Maintenance log](../../tools/bambu-maintenance.md)

## Trial history

Use these entry points when the current recipe and the native slice leave an
open question. Each record carries its own article, pose and process.

| Question | Records |
| --- | --- |
| Which supports can come out of the enclosure? | [Integral handhold construction](https://github.com/derekbreden/homesodamachine/commit/3dc5416a8ec6d0b16eb18d157ab49c4c53fe8550), [rail root and removal](https://github.com/derekbreden/homesodamachine/commit/d5bf35612032733c6b542526b44886021e3061c7), [Pisco landing](https://github.com/derekbreden/homesodamachine/commit/e2a98701e25adfc43a480f04c59aeba86f08726f) |
| Which PET-GF trials changed cooling and support? | [Cover fracture](https://github.com/derekbreden/homesodamachine/blob/9ae148e1d78407917c1e8f6d0a78132e2fcbae5c/hardware/printed-parts/faucet/faucet-display-cover/prints/2026-10-17-cooling-off-prepared-mark2/reported-failure.json), [rail cooling reading](https://github.com/derekbreden/homesodamachine/blob/f62c528c4952e5a24860e2be57f77749d0bbb6c9/hardware/printed-parts/enclosure/enclosure/prints/2026-11-05-back-top-smooth-corners-mark2/rail-cooling.json), [Support D rollout](../printed-parts/support-D-rollout.json) |
| What happened when fit and layer height changed together? | [Cancelled fine-layer plate](https://github.com/derekbreden/homesodamachine/commit/48e5d53646b516e235259e7f5422a69bd68494c2), [standard-layer comparison](https://github.com/derekbreden/homesodamachine/blob/ae3a1e7b7f32f119eacd22981c5fe22108f52d30/hardware/print-tests/front-top-wago-fit/2026-11-12-mark1-dots-3-4-standard-layers/print-job.json) |
| How did the reservoir settings settle? | [Historical recipe review](../printed-parts/cold-core/reservoir/corner-lifting/historical-recipe-review.json), [walls and fill trials](../printed-parts/cold-core/reservoir/README.md#50-overlap-prints), [water-hold acceptance](../printed-parts/cold-core/reservoir/water-hold-acceptance.json) |
| Why keep the TPU processed paths and the Aero pause? | [Soft elbow trials](https://github.com/derekbreden/homesodamachine/blob/5b0d29be2fe9dc792998a0a165f77e78acd801e0/future/pump-elbow-exploration/prints/2026-10-22-deposited-links-siraya85a-mark2/README.md), [sleeve cap path review](../printed-parts/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/emitted-path-review.json), [float insertion and covering record](../printed-parts/cold-core/magnetic-float/all-aero/physical-observations.json) |

## Rebuild the illustrated guide

The numbered HTML leaves supply the text, captions and links. The binder
reads the numeric examples from the selected project and trial records,
renders the leaves and writes the PDF with its source receipt. This is an
on-demand guide build.

```sh
tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-manual-guides
tools/run -- tools/hsm/target/release/hsm-manual-guides bind fdm-print-guide
```

The [art sources](art/manifest.json) identify the photo originals, render
inputs and camera settings. Use the [render jobs](art/render-jobs.json)
for a fresh reading of the current CAD payloads. Update a guide claim from
its owning recipe or physical record and keep its evidence link beside it.
