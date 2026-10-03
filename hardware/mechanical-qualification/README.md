# Mechanical evidence and qualification

This register connects the current fasteners and print settings to their design basis and
physical evidence. Evidence limits describe what can be claimed; they do not assign tests
or measurements to the founder. It covers
the printed enclosure, cold-core caps, reservoir closures and attached hardware. Reviewed
2026-10-01 against the generators, saved print projects and linked physical records.

Reported bench issues are addressed. The accepted results below retain their stated scope.
An accepted fit establishes that fit; a geometric clearance establishes that clearance.
Neither supplies an unmeasured load capacity or endurance result.

The design objectives are in [design pressures](../design-pressures.md): compactness,
assemblability, operation, rigidity and substantial feel. Engineering choices prioritize
those outcomes and durable operation. Material price and printer occupancy describe the
consequences of a candidate after its performance is assessed. The pump cartridge is the
field-service operation; the other joints must work without customer retightening.

## Choosing the starting specification

Start from the customer outcome, the complete load path, mating-hardware requirements and
applicable manufacturer guidance. A value already in CAD or a saved slicer project has no
presumption of correctness. An accepted fit supports that fit, not every dimension or process
setting used to produce it. A departure from supplier guidance needs an application-specific
reason, such as measured print compensation or a demonstrated improvement.

Implement a supported correction when the available evidence already selects it. Testing is
useful when its possible results would change a consequential design or production decision.
Consider analysis, a conservative local improvement and an observation during ordinary
assembly before designing a separate test. Founder time, fixtures, consumables, tool purchases
and the risk of damaging an assembly belong in that tradeoff.

No founder measurement or tool purchase is requested by this register. Before making such a
request, supply the decision to be made, the expected benefit of the information, the exact
part and print state, the setup and load direction, tools already available, procedure,
readings and stopping conditions, and acceptance criteria derived from the application.
An unspecified request to test whether an insert holds an adequate force is not a test plan.
Any proposed purchase needs an Amazon Prime link and an explanation of its purpose.

## Accepted physical evidence

The [enclosure print-readiness index](../printed-parts/enclosure/print-readiness.md#physical-evidence)
also covers the valve sockets, display, nameplate, inlet and donor water pump. The records
linked here are the authority for each observation, including their print bindings and scope.

| Interface | Established result | Evidence limit |
| --- | --- | --- |
| [Kamoer cartridge and cap](../reference/kamoer-kphm400/physical-fit.json) | Both pumps held firmly with screws tightened; no vertical play reported. | The report does not independently identify the bearing surfaces or establish operating vibration, handling capacity or the complete four-tube mechanism's performance. |
| [Enclosure grips](../printed-parts/enclosure/grip-cover/physical-acceptance.json) | Support removal and assembled receiver/cover fit accepted on H2C and Mark2. | Loaded lifting, grip retention force and repeated flexing are unmeasured. |
| [Faucet display cover](../printed-parts/faucet/faucet-display-cover/physical-acceptance.json) | The broad PET-GF walls provide accepted give, spring, fit and retention. | Retention force and cycle life are unmeasured. A differently proportioned flexure needs its own result. |
| [Tee-carrier surface](../printed-parts/enclosure/tee-carrier/physical-acceptance.json) and [sliding fit](../printed-parts/enclosure/tee-carrier/low-force-trial/physical-acceptance.json) | Expanding show transition accepted with additive chamfer/taper and six local walls. Sliding and observed tilt accepted with the existing front-top. | Spring return, actuation force and simultaneous release of all four collets remain separate observations. Preserve the accepted surface treatment in structural profile trials. |
| [Faucet lever](../printed-parts/faucet/lever-replica/physical-acceptance.json) | Fit and functional operation accepted for the identified print. | Operating force and endurance are unmeasured. |
| [Reservoir water hold](../printed-parts/cold-core/reservoir/print-log.md) | The identified earlier reservoir assembly held water for several hours with its bulkhead and TPU gaskets. | This result belongs to that geometry and recipe. The current 0.8 mm nozzle trials have no recorded water-test result; warm aging and retained sealing load remain unmeasured. |

## Screw diameter and insert anchorage

The [enclosure interface](../printed-parts/enclosure/enclosure/_enclosure_interface.py)
uses M3 inserts with a 4.0 mm nominal bore. Short inserts are 4.0 mm long; full-length
inserts are 5.7 mm long. The [compressor floor posts](../printed-parts/enclosure/enclosure/enclosure.py)
use M5 inserts 9.5 mm long and a 6.4 mm nominal bore. Thread engagement and blind relief
are separate dimensions.

The [ruthex RX-series drawing](https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf)
specifies the following dimensions. Its minimum surrounding wall is measured from the bore.

| Insert | Knurl OD | Recommended nominal bore | Minimum surrounding wall | Relevant CAD feature |
| --- | --- | --- | --- | --- |
| RX-M3Sx4.0 and RX-M3x5.7 | 4.6 mm | 4.0 mm | 1.6 mm | The shared 7.0 mm mount boss gives a nominal 1.5 mm annulus. Some stations join a wall or web, so the complete feature needs assessment. |
| RX-M5x9.5 | 7.1 mm | 6.4 mm | 2.6 mm | Compressor posts are 12.0 mm OD with a 6.4 mm bore, giving a nominal 2.8 mm annulus. CAD checks the M5 manufacturer's minimum surrounding wall. |

**Selection basis:** use the mating component's fastening requirements where they constrain
the diameter. The compressor's four M5 stations are derived from its donor mounting plate
and grommets. For designed closures and mounts, select the screw, insert, surrounding material
and root together from the clamping, handling and operating loads. M3 does not earn that
selection simply by being the existing choice. A larger steel screw alone does not establish
a stronger printed joint. Insert pullout,
torque-out, splitting, the supporting print layers and the boss root can govern capacity.
M5 requires a larger anchoring feature and head seat; its suitability depends on room for
those features and on the load path. The current metal grades have no demonstrated
relationship to the limiting load of these printed assemblies.

**M5 starting specification:** use ruthex's 6.4 mm recommended nominal bore. No recorded
print compensation or retention result supports a departure from that dimension. A pullout
experiment is not a prerequisite for using the supplier's starting geometry. The 9.5 mm
insert has a 10.5 mm blind pocket, including 1.0 mm relief.

[Controlled printed-hole experiments](https://www.cnckitchen.com/blog/are-our-heat-set-insert-datasheets-wrong)
demonstrate that nominal and actual hole diameters can differ materially. They explain why
measured process compensation may be useful; they do not justify an arbitrary larger bore.
Those PLA/M3 results are not an allowable for this PET-GF/M5 joint. If ordinary installation
reveals a bore problem, establish its cause and consider a narrowly targeted calibration.
Any capacity test also needs the load it must withstand, the relevant root and floor, and
a decision that the result would change. This register specifies no such test.

For standalone M3 bosses, the supplier's minimum gives a 7.2 mm nominal OD around a 4.0 mm
bore. The shared 7.0 mm feature needs review at each station: determine the actual surrounding
wall or web and mating-component clearance before selecting a compliant local section.
Neither a successful fit nor inheritance from a board tray establishes an adequate anchorage.

[SPIROL's FDM insert guidance](https://www.spirol.com/assets/files/inserts-for-3d-printed-assemblies-us.pdf?s=how+to+select+a+threaded+insert+for+your+3d+printed+assembly)
supports treating walls, infill, bore geometry and installation as joint variables. Its
published PLA/SPIROL insert loads cannot be transferred to ruthex inserts in this appliance.

## Screw quantity and location

| Joint | Current arrangement and load path | Design basis and evidence limit |
| --- | --- | --- |
| Enclosure Y seam | Six M3 cross-pin screws, three levels on each flank. The telescoping seam, floor scarf and hooked Z rails also retain the shell. | The screws prevent reverse assembly motion. Determine which stations carry that motion, racking and handling loads through the grips and attached masses; a six-way equal division of appliance weight is not a load model. The existing count has no demonstrated structural margin. |
| Cold-core cap stacks | Ten M3 stations per face with 5.7 mm inserts. The four mid stations avoid conduits; the largest straight long-wall center spacing is 91.5 mm. [Station geometry](../printed-parts/cold-core/_cold_core_interface.py). | Select locations from gasket clamping demand, cap stiffness, corner support and routing. The 91.5 mm span is a geometric fact, not an acceptable-deflection limit. These caps enclose the foam core; they are not carbonator pressure-vessel endcaps. |
| Flavor reservoir caps | Six M3 screws; M3x12 engages 5.0 mm of each 5.7 mm insert. The body bosses are 10.0 mm OD. [Closure geometry](../printed-parts/cold-core/reservoir/reservoir.py). | Vented reservoirs carry liquid head and handling loads. Select the pattern and cap section for controlled gasket compression with allowance for relaxation. Insert length supplies anchorage; it does not by itself preserve gasket preload. |
| Compressor | Four M5 stations follow the donor plate and grommets. [Mount geometry](../manifold-layout/enclosure_assembly.py). | The donor mounting pattern and isolation geometry provide a starting basis. They do not establish the strength of the printed posts, roots or floor under handling and transport. |
| Pump cartridge cap | Two M3x60 screws clamp the shared cap into full-length inserts. | Firm assembled fit is established by the linked physical report. Select any improvement from the cap's load distribution, access and operating requirements; additional screws or larger diameter do not need to wait for a reported failure. |

The [floor thickness is 6.0 mm and grip roofs are 12.0 mm](../printed-parts/enclosure/enclosure/enclosure.py).
Those geometric dimensions do not define load capacity. Engineering assessment must include
the grips, their supports, seams, floor and attached masses, with asymmetric loading where
the grip geometry permits it. Derive any proof load, acceptable deflection and permanent-set
limit from intended handling conditions before proposing a test. A successful lift at
operating weight is useful evidence but does not establish a transport or endurance margin.

## Infill and deposited structure

The shared [PET-GF profile](../printed-parts/petgf.3mf) requests two wall loops and 15% grid
infill, with local exceptions. Actual material around a loaded feature depends on nozzle and
line width, both bore and outer walls, solid layers, narrow-region filling and modifiers.
Thin cold-core walls can already be filled by their perimeter paths. Thick floors, posts
and grip roofs can retain sparse interiors. Wall count alone is not a strength measurement.

A path inspection of one saved compressor-post section found both wall paths and sparse
infill in its 12.0/6.8 mm annulus; it is not filled throughout. The nominal extrusion-footprint
audit leaves approximately 23% of that section uncovered. This is a slice observation,
not measured porosity or strength. Its source and method are in
[the comparison data](profile-comparison.json). The saved trial's post diameters are
recorded in that comparison; its 6.8 mm bore is not the current M5 starting
specification. The footprint audit does not qualify the current complete enclosure mesh.

**Structural starting treatment:** fill the high-load insert features and their roots locally, carrying
that material into the supporting floor or wall. Preserve the rubber isolator geometry.
For enclosure rigidity, compare added wall thickness, floor skins and ribs as well as sparse
infill. Preserve accepted flexure behavior and print treatments when changing a profile.
The reservoir's dense watertight recipe remains a separate process.

**Pattern assessment:** gyroid is a supported starting candidate because its paths do not cross
within a layer and its internal structure supports multiple directions. Grid crosses within
each layer, creating a possible buildup and nozzle-interference mechanism. Rectilinear is
another candidate when avoiding crossings and supporting solid skins are the main purposes.
[Prusa's pattern documentation](https://help.prusa3d.com/article/infill-patterns_177130)
explains these distinctions. They do not demonstrate that gyroid makes this complete FDM
part stronger or eliminates weak layer interfaces.

### Native slice comparison

The comparison uses one front-top mesh and identical orientation, supports and layer bands.
The 15% gyroid trial changes only the sparse pattern. The 25% gyroid/four-wall trial is a
combined candidate; its individual wall and density effects cannot be separated from it.
Estimates include supports and printer overhead. Source hashes, settings differences,
native output status and density correction are recorded in
[profile-comparison.json](profile-comparison.json).

| Settings | Estimated total time | Estimated PET-GF15 mass | Change from grid baseline |
| --- | --- | --- | --- |
| Two walls, 15% grid | 29 h 39 m | 1.198 kg | Baseline |
| Two walls, 15% gyroid | 34 h 26 m | 1.205 kg | +4 h 47 m; +7 g |
| Four walls, 25% gyroid | 46 h 14 m | 1.529 kg | +16 h 35 m; +331 g |

These predictions describe material use and printer occupancy. No candidate has a measured
strength, deflection, noise, surface or endurance result. That limits performance claims; it
does not require a physical comparison before choosing a supported starting recipe. Select
wall paths and local solid regions for the load path, choose the sparse pattern for the
remaining interior, and preserve the identified accepted flexures and surface treatments.

## Other choices to assess

| Choice | Current evidence or assumption | Customer outcome and design question |
| --- | --- | --- |
| Retained clamping force | Printed bearing surfaces and elastomer gaskets remain in several clamping stacks. Full-length inserts improve anchorage; plastic and gasket relaxation remain separate mechanisms. | Reliable sealing and retention without customer retightening. Design retained preload around its bearing path; metal compression limiters must contact the insert where used, and gasket squeeze needs its own control. [SPIROL's insert design guide](https://my.spirol.com/assets/files/ins-threaded-inserts-design-guide-uk.pdf) describes that metal load path. |
| Compressor isolation | `FLOOR_GROMMET_SQUEEZE` is 0.4 mm; the flange thickness needed to express that as strain is unmeasured in the [mount source](../manifold-layout/enclosure_assembly.py). The design uses the post crown as the washer stop; contact with the installed insert face is not physically established. | Quiet operation with secure mounting. Base squeeze and preload on the rubber and actual bearing path. The existing 0.4 mm does not establish appropriate rubber strain or isolation. |
| Screw material and finish | The [BOM](../ledger/bom.md) specifies black-oxide 12.9 steel for many dry-zone joints and credits its strength over 304 stainless. Joint capacity and environmental exposure are not quantified. | Durable, corrosion-resistant joints. Select sufficient fastener strength for the complete joint and appropriate protection for its moisture exposure; steel tensile strength alone does not select the best material. |
| PET-GF print process | The shared profile is labelled PET-GF but retains PET-CF type metadata and 1.29 g/cm3 density. The [PET-GF15 data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf) gives 1.43 g/cm3 and identifies annealed specimens for its mechanical data. | Accurate mass estimates and consistent printed material. Use the correct density for estimates, the intended drying and flow process, and the actual production material state in engineering analysis. Published annealed properties are not production allowables. |
| Insulation thickness | The [15 mm cylinder-to-pocket spacing](../printed-parts/cold-core/_cold_core_interface.py) is explicitly set by packing geometry, not a thermal target; the coil occupies part of it. | Cold delivered soda, acceptable recovery, energy use and condensation. Select foam and thermal-bridge treatment from the heat load and intended cabinet environment; available packing space alone does not establish the thermal optimum. |
| Transit packaging | Carton, foam end-caps and exact shipping mass are open in [finish and shipping](../assembly/finish-pack-ship.md). | An intact, functional appliance on arrival. Design packaging support for the complete mass, vulnerable surfaces and shipping exposures; a larger fastener alone does not settle this system problem. |
| Lifetime and acceptance duration | [Acceptance and burn-in](../assembly/acceptance-and-burn-in.md) explicitly marks its eight-hour duration and compressor-duty limits as proposed defaults. | Durable operation and useful production screening. Derive exposures and acceptance limits from product life and use conditions. A production screen and design endurance answer different questions; eight hours alone establishes neither. |

## Maintaining the evidence

For a physical issue or optimization, identify the affected interface and customer outcome,
then update its canonical physical record and this index. Record an actual result, reporter,
date, part and mating-part hashes, print archive or process, and measurement conditions.
Keep observation and engineering interpretation separate. Mark a reported issue addressed
with the resolution evidence; keep prior attempts in the print log and Git history.

Before reopening an issue, read the current acceptance record and follow its links. Before
transferring an accepted result, check that the relevant geometry, materials, print orientation,
process and mating part are represented by that evidence. State which property remains
unmeasured. Do not turn a documentation gap into a claim of a physical failure.

For an optimization, record the target, expected benefit, design basis and supporting
evidence. Explain whether the available information already selects the correction, whether
analysis can decide it, or whether a specific experiment would change the choice. Describe
evidence limits without turning them into an uncosted task list. Record material and time
consequences alongside the performance basis. Lifetime qualification is not a prerequisite
for an authorized assembly trial.

## Guided ASA Aero floats

The [float physical record](../printed-parts/cold-core/magnetic-float/all-aero/physical-observations.json) binds successful paused RC62 insertion and initial overprinting to accepted Mark2 task 1306080180. It also records the operator's printed-float reed test: 20 mm from float edge to reed center is usable, 21–24 mm intermittent, and 25 mm consistently absent. The [installation check](../printed-parts/cold-core/magnetic-float/all-aero/integration-check.json) enforces a provisional 18 mm float-edge limit and covers current guide datums and an upright CAD sweep; it is not physical acceptance. Finished liquid immersion, installed directional reed crossings, welding/cleaning exposure, pressure life and flavor compatibility remain unmeasured. [Reed calibration](../printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration) defines the height-placement test; its [record](../printed-parts/cold-core/magnetic-float/all-aero/reed-calibration.json) contains no invented results.
