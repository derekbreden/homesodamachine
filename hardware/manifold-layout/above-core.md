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
| V-B | On its side east of the PCB, head east, flow aft | Integral cold-core lid socket wall |
| V-A and V-K | Beside opposite sidewalls; inlet above, outlet below, underside flow arrow down | Integral back-top socket seats |
| Multiplex ASSE 1022 | Fore–aft above the pump; vent faces west | Two fixed-roof saddles and ties |
| YZMSZ 0.3 MPa water regulator | Transverse, above the forward pump body | Two fixed-roof saddles and ties |
| PISCO regulator and neoFit ACHV44-E check | Folded gas path at the east rear | Fixed east-wall saddles and ties |
| DIGITEN flow meter | On edge between pump and gas group, ports fore–aft, label east | Two back-top sidewall-rooted collar bearings |
| V-A turn | Low feed traveling with V-A to the front-top Y-A handoff | Connected tubing carried with back-top |
| V-B return union elbow | Fixed native fitting position | Integral cold-core lid bearing and retaining tie |
| Two relays | West wall, one above the other | Integral back-top bosses |
| Mains WAGOs | Beside C14, east of PSU screwdriver approaches | Rear-wall wells |
| DC/sensor/reed WAGOs | Two rows on the PCB-facing back of V-B’s wall; fore/aft wire entries, west-opening levers | Integral 3 mm blank-backed wells |
| Ground stack | Fore of V-B | Cold-core lid ground boss |
| Reservoir A fill/draw pair | R14 fore passages and paired east-side seats, draw west of fill | Two integral fore C2 clips on one broad lid base; one shared narrow tie at the aft paired seat |
| Valve manifold commons | Beside their front valve rows | Front-top wells |

WAGO positions follow actual branch connections. The electronics ceiling is
continuous; the funnel frame is the removable roof closure.

The six rear fluid stations form two columns at X37.25 and X77.5, with 32 mm row
pitch. The upper row is water/CO2 inlet, the middle row vent/soda outlet, and the
lower row has flavor B at west X37.25 and flavor A at east X77.5. C14 is at
X−68.5/Z330 and RJ11 at X−30/Z274.376. The logical A circuit runs from V-G
through `fluid-18`; B runs from V-J through `fluid-28`. Their identified
umbilical tails mate with those same logical rear sockets.

The two 4 mm dispense lines follow gentle fore grades to Z296, then rise
between Y278 and Y348 to their roof axes at Z343. Flavor A runs at X−45 and
flavor B at X−55. Two common filled bases on back-top's roof carry paired
8 mm seats at Y354 and Y390. Their mouths face −Z for loading from below.
The 4.10 mm bores and 1.52 mm spring walls are provisional 4 mm fits; the
quarter-inch C2 coupon result does not qualify them.

Reservoir A's selected routes are defined in
[reservoir-a-routes.json](reservoir-a-routes.json). The fore seat’s tube centres
are X50.5/64.0 at Y209.75, Z258.5, with 13.5 mm centre spacing. Both under-valve runs use that height and
rise to Z259.5 after V-B, ahead of the aft tied seat at Y304. Their front-valve
ATEU44W stem elbows retain their 16.891 mm receiving ends.
Each continues through its plain core guide without a joint or physical cut.
Only the connection points and paired-anchor centres/axes are fixed;
intervening bends, radii and displayed lengths illustrate routing and may
change for installed clearance. The fore C2 clips use the accepted 6.35 mm bore,
2.40 mm spring wall and 8 mm span. Their mouths face +Z for downward tube insertion
and exposed-jaw upward release. The aft open seats and nominal retaining tie retain
their local fit. The [coupon result](../../future/snap-fit-tests/2026-10-26-mark2-combined/physical-result.json)
qualifies the selected C2 fit; the complete paired station's installation, numerical
retention force and lifetime remain unmeasured.

The front valves V-F, V-E and V-I carry three ATEU44W stem elbows, trimmed to
their receiving valves' actual tube-stop marks (12.7 mm nominal in CAD).
Their upper crowns clear the funnel frame by 3.933 mm. The reservoir tubes'
upper free runs are centred at Z295.5 and clear the frame by 1.225 mm.
The 4 mm flavor-A crossover lies at Y156/Z288.5. J9's four free fore dressing
stations are at Z281.5; its fixed printed-passage stations are retained.
The first free J1-positive-C/D bends are offset 0.6 mm west and 0.8 mm aft.
All electrical endpoints and hardware mounting stations retain their selected
coordinates. The scoped native routing record is
[stem-elbow-routing-review.json](../mechanical-qualification/enclosure-above-core/stem-elbow-routing-review.json).

## Core entries

The carbonator's existing water and soda fitting datums stay fixed. The gas guide
is at X77.5/Y368.7622 and its below-lid route retains the carbonator fitting and
support-ring lane. Reservoir A fill and B draw pass straight through the cap,
with their reservoir seats aligned to the upper guides. Reservoir B fill uses a trimmed stem elbow at its cap bore, a short tube and
a JG elbow below the lid, with the upward exit aft of the PCB at X−33/Y287.5.
The reservoir cap bores remain on their own native datums. The lower fitting
has a 3.05 mm cover; a broad 2.4 mm upper cover retains the upward-facing
fitting beneath the PCB tails with 0.25 mm nominal CAD air. The original
cup-floor section remains intact outside the named bores. Assemble the pair
and short link in the open cup before its lid goes on for the cap pour; these
clearances do not qualify physical fit or retention loads.

The soda tube rises from the fixed bottom outlet beside the coil, turns toward
its guide in the open main body at Z219.4, and passes straight through the cup
and lid at X50/Y342.4148/Z253.4. Its R14 turns are assembled before potting the
main body. The same continuous
tube follows the accepted PET-GF R14 holder directly into the meter inlet.
The holder has a 2 mm wall and 3 mm legs. One square-ended 63 mm piece of owned
ID6.35/OD25.4 foam slides over the tube and holder before the meter connects.
The guide introduces no joint or extra tube insertion. Local foam compression
is a layout estimate informed by the recorded physical fit; its occupied
CAD shape is not a cutting pattern or physical clearance result.
The water inlet also turns below the cup floor and passes straight through
X−53/Y288.7265. The check's aft outlet elbow faces upward, feeding an exposed
R18 arch into that guide. Its check body, pump connection and carbonator
metal fitting retain their installed datums.
Tighten all four pump screws before threading the inlet and connecting the
meter. The installed tube crosses one pump-driver approach; service of that
screw requires disconnecting and removing the inlet.

## Final access

The funnel frame drops vertically through the roof and is secured by four
recessed M3 × 12 screws into RX-M3 × 5.7 inserts. The drain cradle snaps into
the frame's 3 mm bottom web beneath its 19 mm silicone socket. Complete the
connections beneath the funnel and between the four quadrants before installing
the frame and its drain assembly. The plug, stub, elbow and cradle travel with
the frame; disconnect the V-B feed before removing it. The silicone funnel lifts
separately for cleaning.

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
X40/Y239.60434/Z279.41. The WAGO wells and V-B wall share a flat top at Z298.65, retaining 1.25 mm to the funnel frame.
Seat the fore-facing WAGO bodies before fitting V-B’s inlet plumbing. The
[south-return review](../printed-parts/cold-core/foam-cap/south-return-review/README.md)
binds the geometry and lid slice.
Its inlet uses an R14.07 minimum S-offset between level stem-elbow sockets.
The drain stem is 16.7 mm past its shoulder, including 1 mm showing above
the drain union's collet; its collar clears the cradle by 1 mm.
Its return crosses west on a level straight link at Y275.39954/Z279.41 to the
union at X5.16348, then runs forward to Y239 before one R20.99 minimum curve
enters Y-B. The union sits on a filled lid pedestal beneath its forward leg.
Both return fittings are level. Terminate the
PCB power connections and seat J11 before fitting the return. The recorded
J11 housing path (6 mm up, 6 mm east, then 20 mm up with the funnel frame and
drain removed) belongs to the X−50 return variant and does not qualify the
selected return.
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
