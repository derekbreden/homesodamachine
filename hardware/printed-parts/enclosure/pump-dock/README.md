# Permanent pump dock

The customer withdraws the complete two-pump cartridge, changes the prepared pumps under its two-screw cap, and pushes the cartridge home. Four short straight LLDPE stubs, clamped in the pump heads, enter permanent TPU junctions together. The junctions, purchased elbows, tubing, keepers and magnets remain in the machine. Customer service requires only complete prepared replacement pumps.

## Fluid path and support

Each asymmetric junction has a pump-facing funnel, an upward outlet and a lower socket aimed at a supported [scanned John Guest PP0308E elbow](../../../reference/jg-pp0308e-elbow/README.md). Its front seal is a continuous 6 mm long Ø6.10 mm TPU land around the smooth Ø6.35 mm pump stub. A straight upper link reaches the fore valve. A short lower stub joins the junction to the elbow, and a formed black 1/4-inch LLDPE run reaches the aft valve. Two purchased PP0208E tees form the source crossbar.

The closed PET-GF wall locates each junction in X/Z. Three flat 3 mm PET-GF keepers capture its rear groove in Y: one per outer junction and one for the inner pair. Their plain Ø12.4 mm U openings face downward and seat on the occupied junction necks by gravity. Each keeper parks above the collar during factory insertion, then slides down over the necks. The slots have 0.25 mm sliding clearance on both faces and a raised 45-degree roof. The wall backs the keeper against aft load. The upper link clocks each junction.

Broad flat-sided TPU connects each junction's rear collar and two sealing sockets. Connected Ø4.3 mm circular bores form the internal passages. The inner inlet is level; the outer inlet rises 4.5 mm within the web to leave 3 mm above the occupied lower tube stop. Both branch sealing lands remain circular, 6 mm long with a 0.5 mm entry and a 0.9 mm radial annular stop.

Each purchased elbow's fixed collar bears on a broad U seat integral with front-top. Its aft opening admits the connected junction/elbow group from inside the loose shell. The seat supports the fixed body below its collar and clears both release collets. Pressure separating the short stub and junction is reacted through the gripped stub, elbow collar, seat and shell. The elbow collet restrains the stub; the TPU land supplies the seal. The short stub targets 0.15 mm axial room at the TPU stop; the complete supported joint must keep total movement within 0.5 mm to retain at least 5.5 mm seal engagement.

The inner elbows lean 25 degrees, directing their tubes below V-C/V-D's terminal region. The outer elbows yaw toward V-G/V-J and stand above the condenser. The formed runs use R14 centerline bends, the existing spool's recorded no-kink observation in `_routing.STOCKS`. CAD insertion lengths of 15.7 mm in the elbow and 12 mm in the valve are layout estimates: the exterior scan establishes neither internal stop. Actual fully seated mouth marks govern factory cuts. The nominal lower stub is 23.05 mm; see the [current geometry review](elbow-review/README.md) for station dimensions, fit and limitations.

## Cartridge and magnets

Each prepared pump carries two straight 26 mm stubs of the machine's black 1/4" LLDPE, pushed into its BPT tube ends in place of Kamoer's barbs. The pump head's own housing, tightened at the factory, clamps the tube around each stub. Docking and withdrawal friction pass from each stub through that clamp into the rigid head, which the cradle and cap hold; the flexible tube outside the clamp carries no axial load as a free column. Each stub seals on its own 6.35 mm OD at both ends, so pressure inside it nearly balances along its length. The stubs pass the cradle's plain open tube passages. The four tips end at Y90.015 mm, 7.750 mm behind the cartridge's Y82.265 mm back datum: across the 0.250 mm body air, the junction's 1 mm entry and 6 mm seal land, and 0.5 mm beyond it. The [pump procedure](../../../service/pump-replacement.md#factory-preparation-of-replacement-pumps) sets each tip against the tube setting jig.

The meeting poles of the two SB443-IN columns seat the cartridge, with 0.250 mm of air between the broad faces. Each pump's own load line carries one column of four attracting pairs; each block sits in one slot per part, held by printed rails and loaded at that part's print pause. At K&J's 3.42 lbf steel rating each column carries 60.9 N against the 52.4 N screen for its pump's 80 psi blocked fill. The [magnet design](magnet-retention.md) defines polarity, slots and loading. Pull force to steel is not an installed retention rating. Follow the [contact mounting audit](../../../reference/yyfkgcp-pogo-4p/mounting-audit.md) for actual assembly and compression.

## Factory assembly

Keep front-top loose, with access from its interior and underside. The [internal plumbing procedure](../../../assembly/internal-plumbing.md) owns the complete sequence.

1. Finish the shell's rigid seats. Insert the three keepers from the seam and park them above the junction collars.
2. Prepare each junction, straight upper link, fore valve, short lower stub and purchased elbow off the wall. Mark actual fully seated tube depths before cutting; retain the specified TPU seal engagement and stop room.
3. Move each connected group toward the pump side in −Y. Seat the fore valve on its posts, fold the junction's flexible inlet lip through its wall bore and slide the elbow into its aft-open seat. Confirm full lip recovery and fixed-collar bearing without pressing a release collet.
4. Turn front-top upright and lower the keepers onto the junction necks. Check the rear grooves are captured in Y. Lift a keeper into its parked position for factory removal.
5. Fit the aft valves and connect the formed tubes while the underside is open. Seat each end fully to its actual mouth mark and tug-check the purchased push-fit connections. Preserve access to the electrical terminals and the outgoing elbow/valve release collets. The upper elbow stub is prepared off the wall; lift the junction off that stub after removing the connected group for factory work.
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
