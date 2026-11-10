# Above-core arrangement

[above-core.json](above-core.json) owns the appliance-world native frames.
[machine_equipment.rs](/hardware/manifold-layout/machine_equipment.rs) builds the purchased bodies;
[rear.rs](/tools/hsm/layout-data/src/rear.rs) builds the inlet header, pump joints,
short links and rear continuations. The enclosure, core mounts and installed
wiring use those same frames. Front is −Y, rear is +Y and up is +Z.

## Equipment and supports

The enclosure body is 215 × 466.3 × 361 mm. The cold-core lid face is Z253.4.
Back-top has a 9 mm roof and rear wall. The PSU's shallow running well retains
7.75 mm of roof over its body. A plain pocket above the ASSE and PISCO caps
ends at Z348.55, leaving 6.45 mm of roof and 0.5 mm above their pointed tips.
The PSU's four M3 × 10 screws enter short RX-M3S × 4
inserts; the modeled ear range gives 2.3–4.3 mm of screw projection and 0.7 mm
of tip air. The four blind pilots end below the full 3 mm roof show skin.

| Equipment | Arrangement | Support |
|---|---|---|
| Multiplex ASSE 1022 | Threaded inlet chain fore–aft on TAP; both wrench flats horizontal; vent down | Integral swept hex seat and lower hex snap cap |
| PISCO RVFUP1/4-1/4-0.3 | Its own inlet neck crosses the CO2 rear hole; ACVUS-44 stem check directly in its outlet | Integral slide seat and lower cap with approved body, neck and rear-hole fit |
| DIGITEN meter | Outlet directly against the soda union; larger housing side down, label east | Integral east-wall slide seat and west-entering snap cap |
| JG PP0208E water split | Raised on one gentle bend in the ASSE outlet stub | Connected header; V-K and regulator have their own mounts |
| YZMSZ water regulator | East–west, above the pump | Integral ceiling seat and lower snap cap |
| V-A | Hangs from the ceiling, its four posts upward; outlet turns east and then fore | Full-width integral socket plinth |
| V-K | Beside the east wall, inlet up and outlet down | Integral full socket wall |
| G Ganen pump | Motor fore–aft, suction east, discharge west; complete rubber feet and legs removed | Two rail seats, continuous 54.5 mm filled box cap and bilateral rail-end stops |
| Pump joints | Reinforced 3/8-inch PVC, trimmed PP061208W reducers and two butterfly clamps per barb | Clamped barb and reducer engagements |
| Pump discharge check | ACVUS-44 stem directly in the discharge elbow | Discharge joint; continuous inlet enters the core guide |
| Mean Well IRM-90 | Base upward in its shallow ceiling well, AC end aft | Four integral ceiling hosts |
| Teyleten relays | One above the other on the west wall | Board-plane corner bearings and M2 screw-and-insert sets |
| PCB and V-B | Board flat and connector-up; V-B on its side east of it | Core columns and the integral V-B socket wall |

ASSE, Pisco and meter enter their seats 16 mm fore of their stations and slide
aft. The ASSE seat permits 1.5 mm of threaded-joint variation in either direction.
The regulator enters upward. Seats use 0.25 mm running fit; caps use 0.15 mm
slip fit. The four separate caps are in
[rear-equipment-caps](../printed-parts/enclosure/rear-equipment-caps/README.md).

V-K stands upright with 17.57 mm to the continuous ceiling. Its lower elbow
clears the plain lid by 1.59 mm. The water-split run has a 3.39° tilt; its
branch clocks 7.56° about that run to meet the raised ASSE outlet through a
tangent stub with at least 55.9 mm bend radius. Both through-run sockets
retain their stations, and the short V-K and regulator links retain full
receiving depths on tangent bends. ASSE, regulator and V-A retain their aligned frames. The
[native local fit](../mechanical-qualification/enclosure-above-core/vk-local-fit-review.json)
records the body clearances and tube extrema.

The water elbows retain 0.4 mm exposed male shoulder lands outside their full
receiving depths. The suction PVC has a 12.119 mm free span on two tangent
arcs, minimum R27.343. Its elbow rotates 3.307° around the seated V-K stem.
The discharge elbow rotates 4.745° around the check's seated stem; the PVC
cuff bends 10.289°. The check and core water guide keep their fixed frames.
The bare pump and V-K keep their aligned body frames.

The pump cap has a 6.2 mm filled crown, one east clearance shoulder and two
independent 2.6 mm spring leaves with 22.5 mm free lengths. Its flat catches overlap by 2.6 mm. The
straight 49.62 mm cover channel is recessed 2.5 mm, retaining 4.9 mm of lid
floor. The four rear snap caps use the same flat-catch section; their leaves
have 3.2 mm of outward release travel.

Viewed from behind, the left port column is X76.5 and the right is X28.8;
rows are Z331.2, Z294.2 and Z264. TAP's bore follows the scanned inlet adapter's
axis. The top row is CO2/TAP, the middle SODA/FLAVOR and the bottom DRAIN/FLAVOR.
The 42 × 38 × 1.8 mm identification tiles slide into continuous channels with
2 mm of overlap at each side, leaving 38 mm square visible faces. Their
channel floor is Z240.6 and the seams between cards are 0.2 mm. The bottom
row carries its words below the fittings; the other rows carry them above.
The nameplate is centered at X0/Z200. C14 is at X−68.5/Z330 and RJ11 at
X−64/Z291.5.

The common chassis joint is Z160. The lowest tee-return elbow is Z160.913,
above the entering front wall. The four straight upper links have 5.251 mm
exposed tube. The lower returns use two tangent arcs between parallel socket
axes, R18.084 on the inner pair and R19.360 on the outer pair. Their rear
mouths stand 3.749 mm lower. The funnel return descends from V-B to Y-B.

## Continuous tubes

The soda guide is X77.5/Y359.51/Z253.4. The same blue tube runs from the
carbonator's bottom outlet, through the cap and the accepted R14 holder, into
the meter. The holder has 2 mm walls and 3 mm legs; it stands 7.75 mm from the
meter mouth. A tangent S transition carries the tube from the fixed core
guide into the holder. One square-cut 56 mm piece of ID6.35/OD25.4 foam covers the
external inlet and holder. The meter and soda union share a concealed tube.

The gas check's socket feeds one bend, then an S to the guide at
X59.101/Y354.664. The gas tube remains continuous to the carbonator's gas
fitting and support-ring lane. The gas bend retains at least R24.7. The water
check feeds two tangent bends, minimum R14.246, into the
straight guide at X−82.5/Y420. Neither guide adds a socket or tube cut.

V-A's outlet union clocks 50° downward about the seated valve connection;
the nested stem elbow clocks 15° outward. Both full stem engagements remain
coaxial. Its feed crosses above the pump and passes beneath the regulator. Its
continuous tangent bends pass above the PCB before entering the fore lane.
The upward-opening snap at X16.608/Y207.300/Z268.970 has one filled root on
the lid. Y-A's stem elbow points east, keeping the connector on XYZ axes
and clear of the drain cradle. Both receiving lengths stay straight through
the full 16.891 mm socket depth. All bends retain at least R14.
The funnel’s uncut ATEU44W stem reaches the bowl opening at Z317.315; its bend
is Z290.289 and its collar clears the frame by 1.713 mm. V-B’s inlet turn and
the attached drain outlet elbow share a 12.725° descending axis. Their straight
36.469 mm tube includes both 16.891 mm socket engagements and has 2.687 mm
exposed tube.
Its return to Y-B retains at least R24.66; the cross-link has 0.542 mm
exposed tube between full insertions. Complete
these connections through the uncovered funnel opening before fitting the frame.

The two black 4 mm dispense lines use the east pump aisle and approach the
Z264 rear sockets from below the meter. Flavor A has an upward-opening crossover snap at
X26.5/Y266/Z296, backed into V-B’s full wall. Flavor B has its filled
upward-opening rear snap at X35/Y414/Z264. Their 4.10 mm bores and 1.52 mm spring walls
retain the selected modeled 4 mm section. Flavor A descends ahead of the meter and runs above its complete lower wing. All free 4 mm bends are R25 or larger.

Reservoir A uses its fore paired C2 snaps and a filled, open paired saddle
at Y390.5, inside the casing footprint. One tie holds both existing curved
paths in their unequal-height seats. The front valve fittings and reservoir
mouths retain their datums. The fill entry in the equipment lid is X56/Y426.3;
an internal R14 S bend joins the fixed reservoir bore through the open space
beneath the lid. Its external aft seat follows the fill tube 5 mm west. Its free aft bends pass outside the soda foam.
[reservoir-a-routes.json](reservoir-a-routes.json) owns their exact R14 segments.
The two routes remain continuous through their core guides. Reservoir B's draw
line steps 13 mm east above its core mouth on two R14 bends before joining the
west fore corridor. It clears the V-B return and keeps J11's service lane open.
Reservoir B retains its fore-entry fill passage, three recessed clamps and
original TPU fill grip.

The downward ASSE vent takes one
[TPU cup with an aft-facing socket](../printed-parts/asse-drain-adapter/README.md).
Its white 4 mm return runs directly to DRAIN. The dedicated faucet outlet remains
open over the bowl.

## Assembly

Populate back-top ceiling-down on the bench, separated from the cold core.
Install inserts and electronics, then the Pisco/check group and regulator.
Prepare the meter with its continuous inlet, holder, foam and concealed outlet
tube, and slide it onto the soda union. Load its cap 20 mm west and 40 mm fore
of its station, slide it aft and press it east into the catches. Fit the ASSE
group's lower cap after the meter cap. Fit the V-A/V-K header, vent cup and
direct DRAIN return with both ties accessible.

Service the rear caps with back-top separated from the core. Disconnect and
dress their tubing and leads aside. Remove the ASSE cap first. Spread the
meter cap's leaves, withdraw it 20 mm west, relax the leaves, then move it
40 mm fore. The cold core must be absent to open the meter's lower leaf.
With the meter and ASSE caps removed, spread the Pisco cap's leaves, lower
it 3.6 mm and slide it 45 mm fore through the flank exits with the leaves held open.

Lower the bare pump into its half-pipe cradle on the open core and close the upper
clip. Fit its clamped joints before loading tubes into the lid snaps. Complete the below-lid tube routes
before closing the core. Keep the pump's suction elbow and its short
quarter-inch inlet link loose while positioning back-top. Carry free
cross-quadrant ends and make their central handoffs through the funnel opening. Install the
removable frame, drain assembly and silicone funnel after these connections.

The [internal plumbing procedure](../assembly/internal-plumbing.md) gives the
part sequence and actual insertion-mark method. Native CAD describes placement
and fit; the named physical acceptance records retain their material and part
scope.

Seat each relay directly against its wall-mounted corner bearings. Fit the M2
socket-head screws through every board mounting hole into the RX-M2×4 inserts,
aligning the board before tightening. The insert mouths share the PCB bearing
plane. The [wall-host datums](../printed-parts/enclosure/enclosure/numbers/rear_wall.rs)
own the hole pattern, screw stack and blind pilots; the
[relay reference](../reference/teyleten-relay/README.md) owns the board and component
geometry. The [BOM](../ledger/bom.md#13-mechanical-attach-hardware) identifies the
acquired hardware.
