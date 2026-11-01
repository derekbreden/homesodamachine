# Above-core arrangement

[above-core.json](above-core.json) owns the appliance-world native frames.
[above_core_parts.py](above_core_parts.py) builds the purchased bodies;
[rear_plumbing.py](rear_plumbing.py) builds the inlet header, pump joints,
short links and rear continuations. The enclosure, core mounts and installed
wiring use those same frames. Front is −Y, rear is +Y and up is +Z.

## Equipment and supports

The enclosure body is 215 × 466.3 × 361 mm. The cold-core lid face is Z253.4.
Back-top has a 9 mm roof and rear wall. The PSU's shallow running well retains
8.05 mm of roof over its body. Its four M3 × 10 screws enter short RX-M3S × 4
inserts; the modeled ear range gives 2.3–4.3 mm of screw projection and 1 mm
of tip air. The four blind pilots end below the full 3 mm roof show skin.

| Equipment | Arrangement | Support |
|---|---|---|
| Multiplex ASSE 1022 | Threaded inlet chain fore–aft on TAP; both wrench flats horizontal; vent down | Integral swept hex seat and lower hex snap cap |
| PISCO RVFUP1/4-1/4-0.3 | Its own inlet neck crosses the upper-right rear hole; ACVUS-44 stem check directly in its outlet | Integral slide seat and neck-catching snap cap |
| DIGITEN meter | Outlet directly against the soda union; larger housing side down, label east | Integral east-wall slide seat and west-entering snap cap |
| JG PP0208E water split | Raised on one gentle bend in the ASSE outlet stub | Connected header; V-K and regulator have their own mounts |
| YZMSZ water regulator | East–west, above the pump | Integral ceiling seat and lower snap cap |
| V-A | Hangs from the ceiling, its four posts upward; outlet turns east and then fore | Full-width integral socket plinth |
| V-K | Beside the east wall, inlet up and outlet down | Integral full socket wall |
| G Ganen pump | Motor fore–aft, suction east, discharge west; complete rubber feet and legs removed | Lid casing bearing and two joined wide-tie loops |
| Pump joints | Reinforced 3/8-inch PVC, trimmed PP061208W reducers and two butterfly clamps per barb | Clamped barb and reducer engagements |
| Pump discharge check | ACVUS-44 stem directly in the discharge elbow | Discharge joint; continuous inlet enters the core guide |
| Mean Well IRM-90 | Base upward in its shallow ceiling well, AC end aft | Four integral ceiling hosts |
| Teyleten relays | One above the other on the west wall | Two filled end bars, four bearing tips per PCB and two diagonal screws |
| PCB and V-B | Board flat and connector-up; V-B on its side east of it | Core columns and the integral V-B socket wall |

ASSE, Pisco and meter enter their seats 16 mm fore of their stations and slide
aft. The ASSE seat permits 1.5 mm of threaded-joint variation in either direction.
The regulator enters upward. Seats use 0.25 mm running fit; caps use 0.15 mm
slip fit. The four separate caps are in
[rear-equipment-caps](../printed-parts/enclosure/rear-equipment-caps/README.md).

V-K stands upright with 17.57 mm to the continuous ceiling. Its lower elbow
clears the plain lid by 1.59 mm. The water-split run has a 3.39° tilt; its
short V-K and regulator links retain full receiving depths on gentle R555
and R531 bends. ASSE, regulator and V-A retain their aligned frames. The
[native local fit](../mechanical-qualification/enclosure-above-core/vk-local-fit-review.json)
records the body clearances and tube extrema.

The water elbows retain 0.4 mm exposed male shoulder lands outside their full
receiving depths. The suction PVC uses two tangent arcs, minimum R39.968,
while the bare pump and V-K keep their aligned body frames.

The port columns are X37.25 and X77.5; rows are Z328, Z296 and Z264. TAP's bore
follows the scanned inlet adapter's axis. The top row is TAP/CO2, the middle
OVER/SODA, and the bottom flavor B/flavor A. The 1.8 mm identification tiles
slide into continuous channels between side rails and stand on the channel
floor at Z252. C14 is at X−68.5/Z330 and RJ11 at X−64/Z291.5.

The common chassis joint is Z160. The lowest tee-return elbow is Z160.913,
above the entering front wall. The four straight upper links have 5.251 mm
exposed tube. The lower returns use two tangent arcs between parallel socket
axes, R18.084 on the inner pair and R19.360 on the outer pair. Their rear
mouths stand 3.749 mm lower. The funnel return descends from V-B to Y-B.

## Continuous tubes

The soda guide is X77.5/Y359.51/Z253.4. The same blue tube runs from the
carbonator's bottom outlet, through the cap and the accepted R14 holder, into
the meter. The holder has 2 mm walls and 3 mm legs; it stands 9 mm from the
meter mouth. One square-cut 61 mm piece of ID6.35/OD25.4 foam covers the
external inlet and holder. The meter and soda union share a concealed tube.

The gas check's socket feeds one bend, then an S to the guide at
X59.101/Y354.664. The gas tube remains continuous to the carbonator's gas
fitting and support-ring lane. The water check feeds two tangent bends, minimum R14.923, into the
straight guide at X−82.5/Y420. Neither guide adds a socket or tube cut.

V-A's feed crosses above the pump and descends east of the regulator. Its
continuous tangent bends pass above the PCB before entering the fore lane.
The upward-opening snap at X16.608/Y207.300/Z268.970 has one filled root on
the lid. Y-A's stem elbow points east, keeping the connector on XYZ axes
and clear of the drain cradle. Both receiving lengths stay straight through
the full 16.891 mm socket depth. All bends retain at least R14.
V-B has a straight, fully inserted drain link with 1.585 mm exposed tube.
Its return to Y-B retains at least R24.66; the cross-link has 0.542 mm
exposed tube between full insertions. Complete
these connections through the uncovered funnel opening before fitting the frame.

The two black 4 mm dispense lines use the east pump aisle and approach the
Z264 rear sockets from below the meter. Flavor A has an upward-opening crossover snap at
X26.5/Y266/Z296, backed into V-B’s full wall. Flavor B has its filled
upward-opening rear snap at X35/Y414/Z264. Their 4.10 mm bores and 1.52 mm spring walls
retain the selected modeled 4 mm section. Flavor A passes through a relief
in the meter cap's lower wing. All free 4 mm bends are R25 or larger.

Reservoir A uses its fore paired C2 snaps and a filled, open paired saddle
at Y390, inside the casing footprint. One tie holds both existing curved
paths in their unequal-height seats. The front valve fittings and reservoir
mouths retain their datums. Its free aft bends pass outside the soda foam.
[reservoir-a-routes.json](reservoir-a-routes.json) owns their exact R14 segments.
The two routes remain continuous through their core guides. Reservoir B's draw
line steps 13 mm east above its core mouth on two R14 bends before joining the
west fore corridor. It clears the V-B return and keeps J11's service lane open.
Reservoir B retains its fore-entry fill passage, three recessed clamps and
original TPU fill grip.

The downward ASSE vent takes one
[TPU cup with an aft-facing socket](../printed-parts/asse-drain-adapter/README.md).
Its white 4 mm return runs directly to OVER. The dedicated faucet outlet remains
open over the bowl.

## Assembly

Populate back-top ceiling-down on the bench. Install inserts and electronics,
slide in the threaded ASSE and Pisco/check groups, and close their caps. Fit the
regulator and V-A/V-K header. Prepare the meter with its continuous inlet,
holder, foam and concealed outlet tube, slide it onto the soda union and fit
its west cap. Fit the vent cup and direct OVER return with both ties accessible.

Build the bare pump and its clamped joints on the open core. Tighten its two motor loops
before loading tubes into the lid snaps. Complete the below-lid tube routes
before closing the core. Keep the pump's suction elbow and its short
quarter-inch inlet link loose while positioning back-top. Carry free
cross-quadrant ends and make their central handoffs through the funnel opening. Install the
removable frame, drain assembly and silicone funnel after these connections.

The [internal plumbing procedure](../assembly/internal-plumbing.md) gives the
part sequence and actual insertion-mark method. Native CAD describes placement
and fit; the named physical acceptance records retain their material and part
scope.
