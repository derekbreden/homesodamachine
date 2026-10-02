# Mechanical evidence and qualification

This register connects the current fasteners and print settings to their physical evidence
and to the measurements needed to establish structural and lifetime performance. It covers
the printed enclosure, cold-core caps, reservoir closures and attached hardware. Reviewed
2026-10-01 against the generators, saved print projects and linked physical records.

Reported bench issues are addressed. The accepted results below retain their stated scope.
An accepted fit establishes that fit; a geometric clearance establishes that clearance.
Neither supplies an unmeasured load capacity or endurance result.

The design objectives are in [design pressures](../design-pressures.md): compactness,
assemblability, operation, rigidity and substantial feel. Qualification should first establish
those outcomes and durable operation. Material price and printer occupancy describe the
consequences of a candidate after its performance is assessed. The pump cartridge is the
field-service operation; the other joints must work without customer retightening.

## Accepted physical evidence

The [enclosure print-readiness index](../printed-parts/enclosure/print-readiness.md#physical-evidence)
also covers the valve sockets, display, nameplate, inlet and donor water pump. The records
linked here are the authority for each observation, including their print bindings and scope.

| Interface | Established result | Scope still requiring measurement |
| --- | --- | --- |
| [Kamoer cartridge and cap](../reference/kamoer-kphm400/physical-fit.json) | Both pumps held firmly with screws tightened; no vertical play reported. | The report does not independently identify the bearing surfaces. Operating vibration, handling loads and the complete four-tube mechanism need their own results. |
| [Enclosure grips](../printed-parts/enclosure/grip-cover/physical-acceptance.json) | Support removal and assembled receiver/cover fit accepted on H2C and Mark2. | Loaded lifting, grip retention force and repeated flexing are unmeasured. |
| [Faucet display cover](../printed-parts/faucet/faucet-display-cover/physical-acceptance.json) | The broad PET-GF walls provide accepted give, spring, fit and retention. | Retention force and cycle life are unmeasured. A differently proportioned flexure needs its own result. |
| [Tee-carrier surface](../printed-parts/enclosure/tee-carrier/physical-acceptance.json) and [sliding fit](../printed-parts/enclosure/tee-carrier/low-force-trial/physical-acceptance.json) | Expanding show transition accepted with additive chamfer/taper and six local walls. Sliding and observed tilt accepted with the existing front-top. | Spring return, actuation force and simultaneous release of all four collets remain separate observations. Preserve the accepted surface treatment in structural profile trials. |
| [Faucet lever](../printed-parts/faucet/lever-replica/physical-acceptance.json) | Fit and functional operation accepted for the identified print. | Operating force and endurance are unmeasured. |
| [Reservoir water hold](../printed-parts/cold-core/reservoir/print-log.md) | The identified earlier reservoir assembly held water for several hours with its bulkhead and TPU gaskets. | This result belongs to that geometry and recipe. The current 0.8 mm nozzle trials have no recorded water-test result; warm aging and retained sealing load remain unmeasured. |

## Screw diameter and insert anchorage

The [enclosure interface](../printed-parts/enclosure/enclosure/_enclosure_interface.py)
uses M3 inserts with a 4.0 mm nominal bore. Short inserts are 4.0 mm long; full-length
inserts are 5.7 mm long. The [compressor floor posts](../printed-parts/enclosure/enclosure/enclosure.py)
use M5 inserts 9.5 mm long and a 6.8 mm nominal bore. Thread engagement and blind relief
are separate dimensions.

The [ruthex RX-series drawing](https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf)
specifies the following dimensions. Its minimum surrounding wall is measured from the bore.

| Insert | Knurl OD | Recommended nominal bore | Minimum surrounding wall | Relevant CAD feature |
| --- | --- | --- | --- | --- |
| RX-M3Sx4.0 and RX-M3x5.7 | 4.6 mm | 4.0 mm | 1.6 mm | The shared 7.0 mm mount boss gives a nominal 1.5 mm annulus. Some stations join a wall or web, so the complete feature needs assessment. |
| RX-M5x9.5 | 7.1 mm | 6.4 mm | 2.6 mm | Compressor posts are 12.0 mm OD with a 6.8 mm bore, giving a nominal 2.6 mm annulus. The bore is 0.4 mm larger than the drawing's recommendation. |

**Assessment:** M3 is a plausible fastener for the light mounts and the distributed closures.
A larger steel screw alone does not establish a stronger printed joint. Insert pullout,
torque-out, splitting, the supporting print layers and the boss root can govern capacity.
M5 requires a larger anchoring feature and head seat; its suitability depends on room for
those features and on the load path. The current metal grades have no demonstrated
relationship to the limiting load of these printed assemblies.

**Priority verification:** measure the actual M5 printed bore and qualify its retention.
Do not interpret the nominal 6.8 mm value as an established defect or replace it solely from
the drawing. [Controlled printed-hole experiments](https://www.cnckitchen.com/blog/are-our-heat-set-insert-datasheets-wrong)
demonstrate that nominal and actual hole diameters can differ materially; those PLA/M3
results provide a method, not an allowable for this PET-GF/M5 joint.

Use representative post-and-root specimens printed in the intended orientation, material
and process. Measure holes before insertion; record insertion temperature and final position.
Compare 6.4, 6.6 and 6.8 mm nominal M5 bores with repeat specimens, recording pullout,
torque-out, splitting and failure location. Test the current infill against a locally filled
post and supporting floor. Establish an assembly torque window below the measured damage
threshold and verify screw-tip clearance. Screen the smallest standalone M3 features the
same way before deciding which need more surrounding material or a larger fastener.

[SPIROL's FDM insert guidance](https://www.spirol.com/assets/files/inserts-for-3d-printed-assemblies-us.pdf?s=how+to+select+a+threaded+insert+for+your+3d+printed+assembly)
supports treating walls, infill, bore geometry and installation as joint variables. Its
published PLA/SPIROL insert loads cannot be transferred to ruthex inserts in this appliance.

## Screw quantity and location

| Joint | Current arrangement and load path | Assessment and required observation |
| --- | --- | --- |
| Enclosure Y seam | Six M3 cross-pin screws, three levels on each flank. The telescoping seam, floor scarf and hooked Z rails also retain the shell. | The screws prevent reverse assembly motion; a six-way equal division of total appliance weight is not a load model. Measure seam opening, racking and permanent movement while lifting the fully loaded enclosure through its intended grips. Review anchors or additional stations where movement localizes. |
| Cold-core cap stacks | Ten M3 stations per face with 5.7 mm inserts. The four mid stations avoid conduits; the largest straight long-wall center spacing is 91.5 mm. [Station geometry](../printed-parts/cold-core/_cold_core_interface.py). | The pattern addresses gasket spans and routing. Establish compression around the entire perimeter, cap bow and retained sealing after aging. Add or relocate stations where those measurements show a deficit. These caps enclose the foam core; they are not carbonator pressure-vessel endcaps. |
| Flavor reservoir caps | Six M3 screws; M3x12 engages 5.0 mm of each 5.7 mm insert. The body bosses are 10.0 mm OD. [Closure geometry](../printed-parts/cold-core/reservoir/reservoir.py). | Vented reservoirs carry liquid head and handling loads. Gasket compression, cap bending and relaxation require measurement over the intended temperature and life. Insert length supplies anchorage; it does not by itself preserve gasket preload. |
| Compressor | Four M5 stations follow the donor plate and grommets. [Mount geometry](../manifold-layout/enclosure_assembly.py). | Preserve the donor mounting pattern and isolation geometry. Measure retention when tipped and under transport loads, including post-root and floor behavior. |
| Pump cartridge cap | Two M3x60 screws clamp the shared cap into full-length inserts. | Firm assembled fit is established by the linked physical report. Measure operational and handling retention before increasing the number or diameter of screws. |

The [floor thickness is 6.0 mm and grip roofs are 12.0 mm](../printed-parts/enclosure/enclosure/enclosure.py).
Those geometric dimensions do not define load capacity. The complete test must include the
grips, their supports, seams, floor and attached masses. Record actual operating mass and
center of gravity; assess asymmetric and single-grip loading where the grip geometry permits
it. Set proof loads, acceptable deflection and permanent-set limits from the intended handling
conditions before testing. A successful lift at operating weight is useful evidence but
does not establish a transport or endurance margin.

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
[the comparison data](profile-comparison.json). The saved trial has the same post diameters
as the current CAD; it does not qualify the current complete enclosure mesh.

**Candidate treatment:** fill the high-load insert features and their roots locally, carrying
that material into the supporting floor or wall. Preserve the rubber isolator geometry.
For enclosure rigidity, compare added wall thickness, floor skins and ribs as well as sparse
infill. Preserve accepted flexure behavior and print treatments when changing a profile.
The reservoir's dense watertight recipe remains a separate process.

**Pattern assessment:** gyroid deserves a controlled trial because its paths do not cross
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
strength, deflection, noise, surface or endurance result. Qualify loaded specimens and
preserve accepted fits before selecting a production profile.

## Other defaults requiring evidence

| Choice | Current evidence or assumption | Next useful measurement |
| --- | --- | --- |
| Retained clamping force | Printed bearing surfaces and elastomer gaskets remain in several clamping stacks. Full-length inserts improve anchorage; plastic and gasket relaxation remain separate mechanisms. | Measure clamp retention and sealing after warm dwell and operating cycles. Evaluate metal compression limiters that contact the insert where retained screw preload is critical; evaluate controlled gasket squeeze separately. [SPIROL's insert design guide](https://my.spirol.com/assets/files/ins-threaded-inserts-design-guide-uk.pdf) describes the required metal load path. |
| Compressor isolation | `FLOOR_GROMMET_SQUEEZE` is 0.4 mm; the flange thickness needed to express that as strain is unmeasured in the [mount source](../manifold-layout/enclosure_assembly.py). The design uses the post crown as the washer stop; contact with the installed insert face is not physically established. | Measure the donor rubber, actual washer/insert/post bearing and retained seating, transmitted vibration and audible noise in the assembled cabinet. Establish screw preload and rubber squeeze from the actual contact path. |
| Screw material and finish | The [BOM](../ledger/bom.md) specifies black-oxide 12.9 steel for many dry-zone joints and credits its strength over 304 stainless. Joint capacity and environmental exposure are not quantified. | Establish the required fastener strength from the whole joint, then assess moisture and corrosion resistance. Qualify any stainless or protective finish candidate with its specified grade and installation process. |
| PET-GF print process | The shared profile is labelled PET-GF but retains PET-CF type metadata and 1.29 g/cm3 density. The [PET-GF15 data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf) gives 1.43 g/cm3 and identifies annealed specimens for its mechanical data. | Correct interpretation of mass estimates; qualify layer bonding, drying and maximum flow on actual printers. Use the production print state and measured compartment temperature for aging tests. Published annealed strength and heat resistance are not production allowables. |
| Insulation thickness | The [15 mm cylinder-to-pocket spacing](../printed-parts/cold-core/_cold_core_interface.py) is explicitly set by packing geometry, not a thermal target; the coil occupies part of it. | Measure standby power, reservoir and delivered-water temperatures, recovery and condensation under intended warm/humid cabinet conditions. Use those results to assess foam thickness, thermal bridges and envelope tradeoffs. |
| Transit packaging | Carton, foam end-caps and exact shipping mass are open in [finish and shipping](../assembly/finish-pack-ship.md). | Test the complete packed appliance against its shipping conditions, then inspect mounting shifts, seams, appearance and functional performance. Fastener changes alone do not qualify the packed product. |
| Lifetime and acceptance duration | [Acceptance and burn-in](../assembly/acceptance-and-burn-in.md) explicitly marks its eight-hour duration and compressor-duty limits as proposed defaults. | Set measurable product life and use conditions, then qualify representative assemblies for those exposures. Keep production defect screening distinct from design endurance evidence. |

## Maintaining the evidence

For a physical issue or optimization, identify the affected interface and customer outcome,
then update its canonical physical record and this index. Record the current result, reporter,
date, part and mating-part hashes, print archive or process, and measurement conditions.
Keep observation and engineering interpretation separate. Mark a reported issue addressed
with the resolution evidence; keep prior attempts in the print log and Git history.

Before reopening an issue, read the current acceptance record and follow its links. Before
transferring an accepted result, check that the relevant geometry, materials, print orientation,
process and mating part are represented by that evidence. State which property remains
unmeasured. Do not turn a documentation gap into a claim of a physical failure.

For an optimization, record the target, expected benefit, current evidence, candidate and
measurement that would select between them. Use catalog geometry as design guidance and
actual tests as application evidence. Record material and time consequences alongside the
performance result. There is no requirement to finish lifetime qualification before printing
the authorized assembly trial; that trial supplies evidence the design needs.
