# Above-core arrangement

The production arrangement is defined in [above-core.json](above-core.json).
[above_core.py](above_core.py) reads its native part frames;
[above_core_parts.py](above_core_parts.py) builds the purchased bodies, printed
fluid interfaces and local tubes. The enclosure, cold-core mounts and installed
wiring read those same frames. Coordinates below are enclosure-world millimetres:
−Y is forward, +Y is the rear connection face, and +Z is up.

## Equipment and supports

The nominal enclosure body is 215 × 466.3 × 361 mm; the rear nameplate field
projects 2.2 mm beyond its rear wall. The cold-core lid's plain outer face
is Z253.4. The back-top roof and rear wall use 9 mm stock; named roof pockets
retain at least 3 mm above the water and gas fittings.

| Equipment | Position | Mechanical parent |
|---|---|---|
| G Ganen pump | Motor fore–aft, discharge −X, four identical rubber feet | Cold-core cup/lid mount columns |
| PCB | Flat, west/forward, long axis fore–aft; JST connectors upward | Cold-core cup/lid mount columns |
| Mean Well PSU | On edge on the dry west wall, below the relays | Back-top wall mounts |
| V-B | Upright east of the PCB, ports fore–aft | Integral cold-core lid socket wall |
| V-A and V-K | Beside opposite sidewalls; inlet above, outlet below, underside flow arrow down | Integral back-top socket seats |
| Multiplex ASSE 1022 | Fore–aft above the pump; vent faces west | Two fixed-roof saddles and ties |
| YZMSZ 0.3 MPa water regulator | Transverse, above the forward pump body | Two fixed-roof saddles and ties |
| PISCO regulator and neoFit ACHV44-E check | Folded gas path at the east rear | Fixed east-wall saddles and ties |
| DIGITEN flow meter | On edge between pump and gas group, ports fore–aft, label east | Two back-top sidewall-rooted collar bearings |
| V-A turn | Low feed traveling with V-A to the front-top Y-A handoff | Connected tubing carried with back-top |
| V-B return union elbow | Fixed native fitting position | Integral cold-core lid bearing and retaining tie |
| Two relays | West wall, one above the other | Integral back-top bosses |
| Mains WAGOs | Beside C14, east of PSU screwdriver approaches | Rear-wall wells |
| DC/sensor/reed WAGOs and ground stack | Beside the PCB | Cold-core lid wells and ground boss |
| Reservoir A fill/draw pair | R14 fore passages and paired east-side seats, draw west of fill | Two integral cold-core lid paired seats, one shared narrow tie per station |
| Valve manifold commons | Beside their front valve rows | Front-top wells |

WAGO positions follow actual branch connections. The electronics ceiling is
continuous; the funnel frame is the removable roof closure.

The six rear fluid stations form two columns at X37.25 and X77.5, with 32 mm row
pitch. The upper row is water/CO2 inlet, the middle row vent/soda outlet, and the
lower row flavor A/B outlet. C14 is at X−68.5/Z330 and RJ11 at X−30/Z274.376.

Reservoir A's selected routes are defined in
[reservoir-a-routes.json](reservoir-a-routes.json). The fore seat's tube
centres are X50.5/58 at Y205; the aft pair is X86.5/94 at Y304, all at
Z259.5. The `fluid-14` fill warm span is 472.625 mm and the `fluid-16`
draw span is 415.300 mm, including the estimated front-valve receiving ends.
Each continues through its plain core guide without a joint or physical cut.
Only the connection points and paired-anchor centres/axes are fixed;
intervening bends, radii and displayed lengths illustrate routing and may
change for installed clearance. The actual open seats and nominal retaining
ties define the local fit where a tube bends away from an anchor.

## Core entries

The carbonator's existing water and soda fitting datums stay fixed. The gas guide
is at X77.5/Y368.7622 and its below-lid route retains the carbonator fitting and
support-ring lane. Reservoir A fill and B draw use shallow offsets through the
cap. Reservoir B fill uses a trimmed stem elbow at its cap bore, a short tube and
a JG elbow below the lid, with the upward exit aft of the PCB at X−33/Y287.5.
The reservoir cap bores remain on their own native datums. The lower fitting
has a 3.05 mm cover; a broad 2.4 mm upper cover retains the upward-facing
fitting beneath the PCB tails with 0.25 mm nominal CAD air. The original
cup-floor section remains intact outside the named bores. Assemble the pair
and short link in the open cup before closing its lid; these clearances do
not qualify physical fit or retention loads.

The soda tube rises from the fixed bottom outlet beside the coil, crosses above
the tank at Z239.4 and exits through the plain guide at X50/Y342.4148/Z253.4.
Its curved passage retains the cup floor and uses R14 bends. The same continuous
tube follows the accepted PET-GF R14 holder directly into the meter inlet.
The holder has a 2 mm wall and 3 mm legs. One square-ended 63 mm piece of owned
ID6.35/OD25.4 foam slides over the tube and holder before the meter connects.
The guide introduces no joint or extra tube insertion. Local foam compression
is a layout estimate informed by the recorded physical fit; its occupied
CAD shape is not a cutting pattern or physical clearance result.
Tighten all four pump screws before threading the inlet and connecting the
meter. The installed tube crosses one pump-driver approach; service of that
screw requires disconnecting and removing the inlet.

## Final access

The funnel frame drops vertically through the roof and is secured by four
recessed M3 × 12 screws into RX-M3 × 5.7 inserts. The drain cradle snaps into
the frame's 3 mm bottom web beneath its 19 mm silicone socket. Complete the
connections beneath the funnel and between the four quadrants before installing
the frame and its drain assembly. Frame removal requires disconnecting the
drain tube or releasing the cradle. The silicone funnel lifts separately for
cleaning.

Prepare the PSU, relays, meter, rear fittings and their connections with
back-top open on the bench. Complete the accessible central handoffs before
installing the funnel frame. The common upper M5 knuckle bearing is
Z318.0 on front-top, with back-top’s underside at Z318.25. The upper joints
use acquired M5 × 50 screws and the lower joints use
M5 × 120 screws.

## Evidence scope

Native CAD establishes placement, stock, screw reach and the explicitly recorded
interference/motion readings. It does not establish assembly force, fatigue,
insert strength, sealing or pressure suitability. The straight ASSE cuffs, pump
elbows, trimmed fitting insertions and selected compact gas components retain
the qualification limits in their part references. Existing accepted printed
fits retain their named material, orientation and artifact scope in the
[mechanical qualification index](../mechanical-qualification/README.md).

The funnel extends 35 mm aft (+Y), retaining the fore edge. Its drain is at
Y179.19575, at the enlarged mouth center. V-B's native origin is
X38/Y244.90434/Z280.41.
Its inlet uses level stem elbows with a 10.95 mm exposed straight tube;
its return crosses west above the PCB at Y280.69954 to the union at
X−24.83652/Z290.79407, then follows a 2 mm crowned R27.44 return into Y-B.
The union has a direct lid support near its fixed body band. Terminate the
PCB power connections before fitting the return. Disconnect and move aside
the flexible V-B return for J11 service. J11 unmates 6 mm upward, moves 6 mm
east, then lifts 20 mm with the funnel frame and drain removed.
The meter's origin is X50/Y390.9148/Z306.376.
Two 6 mm fixed-collar bearings reach the east wall through 9 × 3 mm beams.
The fore beam has a flat dogleg around the gas-drop column; the aft beam
passes below the gas regulator. Their complete nominal retaining strips use
84.22 and 87.76 mm of six-inch stock. The [local carrier reading](../mechanical-qualification/enclosure-above-core/wall-meter-review.json)
binds the printed stock, cached neighbors and access witnesses. Purchased tie
dimensions, threading, bend/twist transitions and retention remain unqualified.
Its inlet is the continuous insulated R14 tube. Its outlet meets the rear
return fitting at the collet faces; the tube between those two sockets has no
exposed length. The rear return reaches the soda bulkhead through nested
stem elbows.

Install both rear bulkheads and nuts with back-top open, and preassemble the
meter and nested soda elbows there. Their 32.591 mm concealed tube occupies
15.7 mm in the meter socket and 16.891 mm in the return elbow. The meter,
its external inlet tube, bend holder and foam belong to back-top. The inlet
continues uncut through the plain core guide. Closing and flexible handoff
geometry retain the scope of the manual assembly record. The [rear assembly record](../mechanical-qualification/enclosure-above-core/rear-plumbing-assembly.json)
names the exact staging and finite socket scope of each tested motion.
Its explicit 0.22493 mm³ nominal soda fitting contact does not establish
physical collet fit, threading, hand/tool access or connection force.

Tube cut lengths retain the insertion estimates named in the production data;
they are not physical assembly acceptance records.
