# Above-core arrangement

[above-core.json](above-core.json) owns the appliance-world native frames.
[above_core_parts.py](above_core_parts.py) builds the purchased bodies;
[rear_plumbing.py](rear_plumbing.py) builds the inlet header, pump joints,
short links and rear continuations. The enclosure, core mounts and installed
wiring use those same frames. Front is −Y, rear is +Y and up is +Z.

## Equipment and supports

The enclosure body is 215 × 466.3 × 361 mm. The cold-core lid face is Z253.4.
Back-top has a 9 mm roof and rear wall. The PSU's shallow running well retains
6.25 mm of roof over its body. Its four M3 × 10 screws enter short RX-M3S × 4
inserts; the modeled ear range gives 2.3–4.3 mm of screw projection and 1 mm
of tip air. The four blind pilots retain 1.2 mm of roof behind them.

| Equipment | Arrangement | Support |
|---|---|---|
| Multiplex ASSE 1022 | Threaded inlet chain fore–aft on TAP; both wrench flats horizontal; vent down | Integral swept hex seat and lower hex snap cap |
| PISCO RVFUP1/4-1/4-0.3 | Its own inlet neck crosses the upper-right rear hole; ACVUS-44 stem check directly in its outlet | Integral slide seat and neck-catching snap cap |
| DIGITEN meter | Outlet directly against the soda union; larger housing side down, label east | Integral east-wall slide seat and west-entering snap cap |
| JG PP0208E water split | Raised on one gentle bend in the ASSE outlet stub | Connected header; V-K and regulator have their own mounts |
| YZMSZ water regulator | East–west, above the pump | Integral ceiling seat and lower snap cap |
| V-A | Hangs from the ceiling, its four posts upward; outlet turns east and then fore | Full-width integral socket plinth |
| V-K | Beside the east wall, inlet up and outlet down | Integral full socket wall |
| G Ganen pump | Motor fore–aft, suction east, discharge west; four matching rubber feet | Cold-core cup/lid columns |
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

The port columns are X37.25 and X77.5; rows are Z328, Z296 and Z264. TAP's bore
follows the scanned inlet adapter's axis. The top row is TAP/CO2, the middle
OVER/SODA, and the bottom flavor B/flavor A. The 1.8 mm identification tiles
slide into continuous channels between side rails and stand on the channel
floor at Z252. C14 is at X−68.5/Z330 and RJ11 at X−30/Z274.376.

## Continuous tubes

The soda guide is X77.5/Y359.51/Z253.4. The same blue tube runs from the
carbonator's bottom outlet, through the cap and the accepted R14 holder, into
the meter. The holder has 2 mm walls and 3 mm legs; it stands 9 mm from the
meter mouth. One square-cut 61 mm piece of ID6.35/OD25.4 foam covers the
external inlet and holder. The meter and soda union share a concealed tube.

The gas check's socket feeds one bend, then an S to the guide at
X59.101/Y354.664. The gas tube remains continuous to the carbonator's gas
fitting and support-ring lane. The water check feeds an R14 turn into the
straight guide at X−80.417/Y402.999. Neither guide adds a socket or tube cut.

V-A's feed passes beneath the header, drops in front of the pump and uses the
low Y-A handoff and upward-opening lid snap at X11/Y254.5/Z261.6. V-B retains
its frame-carried funnel drain connection and its return to Y-B. Complete
these connections through the uncovered funnel opening before fitting the frame.

The two black 4 mm dispense lines use the east pump aisle and approach the
Z264 rear sockets from below the meter. Each has a filled, upward-opening
lid snap on its rear straight. Their 4.10 mm bores and 1.52 mm spring walls
retain the selected modeled 4 mm section. Flavor A passes through a relief
in the meter cap's lower wing. All free 4 mm bends are R25 or larger.

Reservoir A retains its fore paired C2 snaps, aft paired tied seat, front valve
fittings and reservoir mouths. Its free aft bends pass outside the soda foam.
[reservoir-a-routes.json](reservoir-a-routes.json) owns their exact R14 segments.
The two routes remain continuous through their core guides. Reservoir B retains
its fore-entry fill passage, three recessed clamps and original TPU fill grip.

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

Build the pump and its clamped joints on the open core. Tighten its four screws
before loading tubes into the lid snaps. Complete the below-lid tube routes
before closing the core. Carry free cross-quadrant ends while positioning
back-top; make their central handoffs through the funnel opening. Install the
removable frame, drain assembly and silicone funnel after these connections.

The [internal plumbing procedure](../assembly/internal-plumbing.md) gives the
part sequence and actual insertion-mark method. Native CAD describes placement
and fit; the named physical acceptance records retain their material and part
scope.
