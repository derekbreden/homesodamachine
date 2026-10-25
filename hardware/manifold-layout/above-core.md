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
| Mean Well PSU | Flat, west/aft; terminal screw approaches from above | Cold-core cup/lid mount columns |
| V-B | Upright east of the PCB, ports fore–aft | Integral cold-core lid socket wall |
| V-A and V-K | Beside opposite sidewalls; inlet above, outlet below, underside flow arrow down | Integral cold-core lid upright socket walls |
| Multiplex ASSE 1022 | Fore–aft above the pump; vent faces west | Two fixed-roof saddles and ties |
| YZMSZ 0.3 MPa water regulator | Transverse, above the forward pump body | Two fixed-roof saddles and ties |
| PISCO regulator and neoFit ACHV44-E check | Folded gas path at the east rear | Fixed east-wall saddles and ties |
| DIGITEN flow meter | On edge between pump and gas group, ports fore–aft, label east | Two integral cold-core lid collar bearings |
| V-A turn and V-B return union elbows | Fixed native fitting positions | Integral cold-core lid bearings and retaining ties |
| Two relays | West wall, one above the other | Integral back-top bosses |
| Mains WAGOs | Beside C14, east of PSU screwdriver approaches | Rear-wall wells |
| DC/sensor/reed WAGOs and ground stack | Beside the PCB | Cold-core lid wells and ground boss |
| Valve manifold commons | Beside their front valve rows | Front-top wells |

WAGO positions follow actual branch connections. Both removable roof closures
remain clear of wiring and tubing attachments.

The six rear fluid stations form two columns at X37.25 and X77.5, with 32 mm row
pitch. The upper row is water/CO2 inlet, the middle row vent/soda outlet, and the
lower row flavor A/B outlet. C14 is at X−61.75/Z323 and RJ11 at X−30/Z274.376.

## Core entries

The carbonator's existing water and soda fitting datums stay fixed. The gas guide
is at X77.5/Y368.7622 and its below-lid route retains the carbonator fitting and
support-ring lane. Reservoir A fill and B draw use shallow offsets through the
cap. Reservoir B fill uses a trimmed stem elbow at its cap bore, a short tube and
a JG elbow below the lid, with the upward exit aft of the PCB at X−48/Y287.5.
The reservoir cap bores remain on their own native datums. A solid roof over the
lower fitting retains at least 3 mm stock; the PCB solder tails clear its top
nominally. The original cup-floor section remains intact outside the named bores.

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

The electronics panel is an empty 100 × 126.55 × 9 mm closure, retained by four
recessed M3 × 12 screws. Remove it to reach the rear electrical connections.
It carries no components, clips, tubing or wires. Both closures install after
their respective connection work. The common upper M5 knuckle bearing is
Z318.0 on front-top, with back-top’s underside at Z318.25. This leaves the
entry path above the core-owned valve walls; the upper joints use acquired M5 × 50 screws and the lower joints use
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
X−50/Z294.33057, then follows a 3 mm crowned R30.31 return into Y-B.
The union has a short direct lid support near its fixed body band. The
power-terminal screwdriver paths remain open. J11 unmates 6 mm upward,
moves 6 mm east, then lifts 20 mm with the funnel frame and drain removed.
The meter's origin is X50/Y390.9148/Z306.376.
Its inlet is the continuous insulated R14 tube. Its outlet meets the rear
return fitting at the collet faces; the tube between those two sockets has no
exposed length. The rear return reaches the soda bulkhead through nested
stem elbows.

Install both rear bulkheads and nuts with back-top open, and preassemble the
nested soda elbows with their 32.591 mm concealed tube. This group rides with
the back column; the free 15.7 mm tube end enters the fixed meter during the
last 15.7 mm of closing. Connect the flexible drain-vent line and remaining
inter-quadrant wiring through the open roof afterward. The
[rear assembly record](../mechanical-qualification/enclosure-above-core/rear-plumbing-assembly.json)
covers the continuous conservative closing envelope and finite meter-outlet
capture. It records the explicit 0.22493 mm³ nominal soda fitting contact;
physical collet fit, threading, hand/tool access and connection force remain
unqualified.

Tube cut lengths retain the insertion estimates named in the production data;
they are not physical assembly acceptance records.
