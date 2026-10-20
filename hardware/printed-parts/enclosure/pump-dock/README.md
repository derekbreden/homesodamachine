# Permanent pump dock

The customer withdraws the complete two-pump cartridge, changes the prepared pumps under its two-screw cap, and pushes the cartridge home. Four short straight LLDPE stubs, clamped in the pump heads, enter permanent TPU junctions together. The junctions, purchased elbows, tubing, keepers and magnets remain in the machine. Customer service requires only complete prepared replacement pumps.

## Fluid path and support

Each junction has a pump-facing funnel, an upward outlet to the fore valve and a downward outlet. A black 1/4-inch LLDPE tube leaves the downward outlet, bends once at R14 and enters the forward leg of a [scanned John Guest PP0308E elbow](../../../reference/jg-pp0308e-elbow/README.md) directly beneath the rear valve. A short straight tube joins that elbow's upper leg to the valve. The front seal is a continuous 6 mm long Ø6.10 mm TPU land around the smooth Ø6.35 mm pump stub. Two purchased PP0208E tees form the source crossbar.

The closed PET-GF wall locates each junction in X/Z. Three flat 3 mm PET-GF keepers capture its rear groove in Y: one per outer junction and one for the inner pair. Their plain Ø12.4 mm U openings face downward and seat on the occupied junction necks by gravity. Each keeper parks above the collar during factory insertion, then slides down over the necks. The slots have 0.25 mm sliding clearance on both faces and a raised 45-degree roof. The wall backs the keeper against aft load. The upper link clocks each junction.

Broad flat-sided TPU connects each junction's rear collar and two sealing sockets. One continuous Ø4.3 mm inlet passage turns downward through R6; a straight vertical branch reaches the upper socket. All four junctions use this common geometry. Both branch sealing lands remain circular, 6 mm long with a 0.5 mm entry, and their Ø4.3 mm throats retain annular tube stops.

Each purchased elbow stands upright beneath V-C, V-D, V-G or V-J, with a nominal 1 mm gap between its upper release face and the valve's bottom release face. Both push-fit collets grip the short joining tube. The rear valve row and source crossbar stand 8 mm above their deck reference to clear the compressor and condenser. V-A and V-B retain their cold-core seats; their connecting tube bends follow the raised crossbar. Round clearances in the rear tray foot clear the elbow bodies.

Each lower tube has one R14 centerline bend, following the existing spool observation in `_routing.STOCKS`. Its straight ends enter the TPU land and purchased elbow coaxially. Nominal insertion allowances are 6.35 mm into TPU, 15.7 mm into the elbow and 12 mm into the valve; actual fully seated marks govern purchased-fitting cuts. The nominal valve joining tube is 28.7 mm. The bent tube's grip in TPU is an unqualified interference fit, with no claimed positive axial stop from the bend. See the [current geometry review](elbow-review/README.md) for placement and evidence limits.

## Cartridge and magnets

Each prepared pump carries two straight 26 mm stubs of the machine's black 1/4" LLDPE, pushed into its BPT tube ends in place of Kamoer's barbs. The pump head's own housing, tightened at the factory, clamps the tube around each stub. Docking and withdrawal friction pass from each stub through that clamp into the rigid head, which the cradle and cap hold; the flexible tube outside the clamp carries no axial load as a free column. Each stub seals on its own 6.35 mm OD at both ends, so pressure inside it nearly balances along its length. The stubs pass the cradle's plain open tube passages. The four tips end at Y90.015 mm, 7.750 mm behind the cartridge's Y82.265 mm back datum: across the 0.250 mm body air, the junction's 1 mm entry and 6 mm seal land, and 0.5 mm beyond it. The [pump procedure](../../../service/pump-replacement.md#factory-preparation-of-replacement-pumps) sets each tip against the tube setting jig.

The meeting poles of the two SB443-IN columns seat the cartridge, with 0.250 mm of air between the broad faces. Each pump's own load line carries one column of four attracting pairs; each block sits in one slot per part, held by printed rails and loaded at that part's print pause. At K&J's 3.42 lbf steel rating each column carries 60.9 N against the 52.4 N screen for its pump's 80 psi blocked fill. The [magnet design](magnet-retention.md) defines polarity, slots and loading. Pull force to steel is not an installed retention rating. Follow the [contact mounting audit](../../../reference/yyfkgcp-pogo-4p/mounting-audit.md) for actual assembly and compression.

## Factory assembly

Keep front-top loose, with access from its interior and underside. The [internal plumbing procedure](../../../assembly/internal-plumbing.md) owns the complete sequence.

1. Finish the shell's rigid seats. Insert the three keepers from the seam and park them above the junction collars.
2. Prepare each junction, straight upper link and fore valve off the wall. Mark actual fully seated tube depths before cutting; preserve the upper link's TPU engagement and stop room.
3. Seat the fore valve on its posts and fold the junction's flexible inlet lip through its wall bore. Confirm full lip recovery.
4. Turn front-top upright and lower the three keepers onto the junction necks, one per outer junction and one for the inner pair. Each crown rests on the occupied neck; check capture by pushing and pulling along Y.
5. Join each rear valve to its upright purchased elbow with the short straight tube, then fit the rear valves on their posts. Connect the R14 bent tubes between the junctions and the elbows' forward legs. Use actual insertion marks and tug-check the push-fit joints. Complete the work with front-top loose and accessible.
6. Prepare the complete pumps and their stubs, close the cartridge cap and set the four tips against the tube setting jig. Assemble the pogo contacts before loading the dock; load the SB443-IN blocks at each printed part's pause.
7. Join front-top to the lower enclosure after its plumbing and fixtures are fitted. Follow [assembly acceptance](../../../assembly/acceptance-and-burn-in.md) and the [customer pump procedure](../../../service/pump-replacement.md).

Removing a complete wet branch for factory work requires an isolated, demonstrated depressurized flavor circuit; it is not part of customer pump replacement.

## Manufacture

Seven printed dock pieces have manufacturing outputs under `../enclosure/`; station-specific wet parts carry the suffixes `west-outer`, `west-inner`, `east-inner` and `east-outer`:

| Part / quantity | Material / export stem |
| --- | --- |
| Asymmetric junction, 4 | Siraya Tech Flex TPU85A Clear; `enclosure-pump-receiver-{station}` |
| Outer keeper, 2 | PET-GF; `enclosure-pump-keeper-outer` |
| Inner-pair keeper, 1 | PET-GF; `enclosure-pump-keeper-middle` |
| Purchased union elbow, 4 | John Guest PP0308E; scanned native reference in the assembly |

STEP and STL manufacturing outputs contain the print pose. Junctions stand on their broad aft web landing; keepers lie flat on their wall face. The [PET-GF handoff](petgf-production-parts.md) specifies the keepers' process. Prepare each wet part as one object per plate and inspect actual bore crossings and attachment paths. The saved [October 18 wet projects](print-preparation/2026-10-18-asymmetric-wet-siraya85a-mark1/README.md) are evidence only for their recorded meshes; they do not prepare the current junctions. Current feed and printing-time estimates require source-bound native projects.

The retained Siraya elbow observation accepts exterior quality and reports internal stringing. The [finned-pair failure](../../../../future/pump-elbow-exploration/prints/2026-10-16-vertical-center-web-tpu85a-mark1/physical-result.json) records bore-crossing strands despite connected fins. Enclosed nozzle travel does not prove that a taut ooze strand stays outside a bore. Each record keeps its own material, geometry and process scope.

The one factory tool is separate from the appliance's installed dock pieces: the [tube setting jig](../enclosure/enclosure-pump-tube-setting-jig.stl), which seats on the cartridge back and stops all four stub tips at their datum.

## Engineering evidence

The [pressure and retention review](pressure-retention-review.json) preserves the actual single-channel paths, reachable blocked-fill case, compound comparisons and isolated qualification procedure: at its 80 psi blocked-fill screen each port separates with 17.5 N. These are engineering evidence, not a system pressure rating.

The current dock has no physical seal, lifetime or cleaning acceptance. The complete frame still needs measured simultaneous seal seating, extraction effort, hydraulic retention and permanent-part aging under the actual fluid, temperature and cleaning exposure. The short factory assembly and geometry readings establish none of those properties. The prepared pump's stub clamp also requires an actual free-rotation, pumping and stub pull-out result. Material data alone do not establish finished wet-part food-contact suitability.

Customer release requires a demonstrated depressurization route for a failed or stalled pump. A timed command or accepted PWM does not establish rotation, flow or that both ports have vented. The customer procedure remains conditional on the qualified depressurized service state.
