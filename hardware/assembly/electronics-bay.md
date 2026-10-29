# Electronics above the cold core

The PCB lies flat on the west side of the cold-core roof, with its long axis
fore–aft. The diaphragm pump and V-B belong to that core. Back-top carries
V-A/V-K, their fitted plumbing, the water header, the PSU and both relays.
The PSU mounts to the dry west sidewall, with the relays above it. The display,
the two pumps with their underside retainer and the front valve coils belong to `enclosure-front-top`.

The fore–aft flow meter travels with back-top between the CO₂ group and pump.
Its two fixed collars sit in integral east-wall carriers; the moving collets
remain free. Its three leads leave the downward-facing native wire boss.
The accepted R14 holder, continuous inlet and foam sleeve travel with the meter;
the uncut tube passes through the core's plain guide.

The ceiling is continuous behind the funnel aperture, so every end beneath it
is landed while back-top is open on the bench. Once the box is closed, the
final connections are made through the funnel opening with the drop-in frame,
silicone and cover off. The frame stays out through commissioning. The plug,
stub, elbow and drain cradle travel with the removable frame; disconnect the
V-B feed before lifting it.

The production placements are in
[`above_core.py`](/hardware/manifold-layout/above_core.py) and
[`above_core_wiring.py`](/hardware/manifold-layout/above_core_wiring.py).
The complete installed electrical graph, native terminal frames, individual
conductors, connector housings and shared cable routes are in
[`installed/`](/hardware/wiring/installed/). These are proposed installed
geometry. The [native review records](/hardware/wiring/installed/above-core-review/)
state their artifact-bound geometry scopes. Actual harness dressing, connector
fit and donor terminal locations retain their stated qualification limits.

## Junctions and mounting parents

| Junction | Connector | Parent | Connections |
|---|---|---|---|
| H | 221-413 | Back-top rear wall | C14 L; PSU L; relay 1 COM |
| N | 221-413 | Back-top rear wall | C14 N; PSU N; compressor neutral pigtail |
| G | 221-413 | Back-top rear wall | C14 PE; ground ring stack |
| V12 | 221-413 | Cold-core lid | PSU V12; relay 2 COM; PCB J10 V12 |
| GND | 221-413 | Cold-core lid | PSU GND; pump negative; PCB J10 GND |
| Sensor common | 221-413 | Cold-core lid | PCB J4 GND; temperature common; flow-meter common |
| Reservoir B common | 221-413 | Cold-core lid | PCB J7 GND; reservoir B reed common; carbonator reed common |
| Manifold A common | 221-420 | Front-top east wall | PCB J1 COM; valve A–H positive leads |
| Manifold B common | 221-415 | Front-top east wall | PCB J2 COM; valve I/J/K and condenser-fan positive leads |
| Compressor H join | 221-413 | Free, under the funnel opening | Relay 1 NO pigtail; compressor switched-H core |
| Compressor N join | 221-413 | Free, under the funnel opening | N junction pigtail; compressor neutral core |
| Pump positive join | 221-413 | Free, under the funnel opening | Relay 2 NO pigtail; pump positive |
| Protective-earth ring stack | M3 ring-terminal stack | Cold-core lid | C14 earth feed; compressor earth; carbonator bond lead |

The rear H/G connectors share a vertical row beside the C14 inlet; N stands
14.5 mm forward on its own broad rear-rooted well. Their wire entries face
forward and their levers open upward. The four core-side
221-413 connectors sit in two vertical pairs on the PCB-facing back of V-B's
wall. The fore pair holds sensor common above V12; the aft pair holds
reservoir-B common above GND. Their wire entries face fore or aft and their
levers open west toward the PCB. The printed wells capture each connector's blank
rear half with 3 mm stock. The manifold common connectors retain their native
front-top stations and their two lever faces remain accessible from the front
assembly's open interior and through the funnel opening. The three joins have no
well; they go in last, where their leads meet, with one port of each empty.

The PSU's wire entries face fore/aft. Its screw axes point inward from the
west sidewall. Land and inspect these terminals on accessible back-top before
closing the quadrants; the continuous ceiling provides no separate rear hatch.

## Inputs

Use the per-unit [BOM](/hardware/ledger/bom.md),
[AC and DC wiring schedule](/hardware/wiring/ac-wiring-schedule.md), and
[cable assembly instructions](cable-assemblies.md) for wire stock, contact
assignments, preparation, stripping and termination. Preserve the schedule's
run IDs and loom labels. Use the specified connector graph.

The PCB and pump use their own native mounting-hole patterns on the cold-core
lid/cup columns. The PCB uses M3 × 8 screws through its 1.6 mm board into
RX-M3×5.7 inserts. The pump retains its specified rubber-pad/washer stack.
The PSU and relay wall-host stacks are defined by
[`_above_core_shell.py`](/hardware/printed-parts/enclosure/enclosure/_above_core_shell.py)
and allocated in the [BOM](/hardware/ledger/bom.md); use the stack assigned to
each device. The ring stack and its Ø9 × 0.8 flat washer clamp under M3 × 8 into an
RX-M3S×4 short insert in the upward-facing core-lid boss. Its 3.2 mm clamp
stack gives 4.8 mm screw projection into a 7 mm blind pilot.

Tools: ESD mat, suitable wire and contact crimpers, soldering tools for the
specified soldered joints, helping hands, insulated driver and multimeter.
Keep the appliance unplugged throughout this assembly.

Follow the carrying parts and closing order in
[enclosure-mechanical.md](enclosure-mechanical.md); [wiring.md](wiring.md)
tables the stage at which each end lands. The
[carried-group review](../mechanical-qualification/enclosure-above-core/approved-carried-group-review.json)
records the current rigid-slide and final-connection limits.

## Assembly

1. Prepare the cold-core internal wiring and the lid-mounted equipment while
   their entries and screws are exposed. Each reservoir reed column has one
   five-conductor loom. A rises straight through the cup and lid before
   turning toward J6. Lay B's ribbon through the 10 × 6 mm shell-rim notch
   before seating the cap, then dress it outside the B-fill block to J7 and
   the existing common WAGO. The `sensor-cable` passage
   carries the temperature supply, data and common together with the
   carbonator PE lead. Route the carbonator's `CLO`, `CHI` and shared common
   through the separate straight `carbonator-reeds` passage. Thread the cup
   and lid over the free earth-wire end before crimping its lid-side ring.
   Follow each loom's printed guide along its modeled path. Complete the
   cold-core assembly in
   [cold-core.md](cold-core.md).
2. On open back-top, seat V-A/V-K with their fitted plumbing. Land their legs
   on the downward blades: J1 `OUT1` and positive-A at V-A, J2 `OUT3` and
   positive-K at V-K, each XH contact crimped but left out of its housing.
   Female-housing fit and connection force remain unqualified.
   Seat the rear junctions in their named wells and label their electrical purpose.
   Check that each seated body's levers can open and close before populating
   it. Fasten the PSU on bare back-top before seating the rear WAGO-H junction;
   its aft mounting-driver path crosses that connector. Mount the relays and
   meter, and prepare the meter’s inlet and concealed outlet plumbing. Solder
   J4's flow pair and the sensor-GND branch to the meter's three factory leads,
   heat-shrink each joint, and dress them below V-K's coil, east ahead of the
   foam and forward to the funnel opening. Keep the funnel frame removed.
3. Still on open back-top, land the fixed AC runs by the schedule: C14 to
   H/N/G, H/N to the PSU primary, and H to relay 1 COM. Then land the back-top
   ends of the runs that finish under the funnel opening: the PSU secondary
   (DC-1), relay 2 COM (DC-2), the relay 1 NO and N-junction pigtails (AC-4,
   AC-5), the relay 2 NO pigtail (DC-3), the PE bus from G, and J5 at the two
   relay modules: IO19 to relay 1 IN, IO2 to relay 2 IN, V5 and GND to both
   modules. The shared relay-end rail termination remains subject to the
   installed model's stated termination limit. Punch J3 down on the rear
   keystone. Dress every free end forward so it lies within the funnel
   opening's footprint once the box is closed, clear of the seams and every
   sliding surface, and flag it with its run ID. Retain the specified direct
   solid-wire clamp and stranded-wire termination choices.
4. On the open core, close the three B-fill lid clamps and thread the tube
   before installing the PCB, per [cold-core.md](cold-core.md); the board
   covers the clamp-driver approaches. Land the two prepared J10 power
   leads on the loose PCB, `V12` and `GND` each in the clamp beside its silk
   label. Mount the PCB, pump, V-B and ground boss
   on their core features. Land the J10 leads' free ends in the V12 and GND
   junctions, and the pump negative in GND. Land the pump positive on the
   pump's lead and dress it forward to the funnel opening. Land V-B's leg on
   its blades: J1 `OUT2` and positive-B, `OUT2`'s contact crimped but out of
   its housing. Seat J6, J7 and J4 at the PCB, J4 with cavities 4 and 5 empty.
   Populate the sensor and reservoir-B common junctions without adding
   junctions to the continuous reservoir-A reed common.
5. Close the box per [enclosure-mechanical.md](enclosure-mechanical.md); the
   front-bottom and front-top looms have landed at their devices by then
   ([wiring.md](wiring.md)). Through the funnel opening, with the frame out:
   - Stack the ground rings on the lid boss: carbonator bond at 120°, inlet PE bus at
     300° and compressor PE at 240°, then the flat washer and M3 × 8. Angles run from
     +X toward +Y about +Z. Dress the inlet earth feed around the fore side of the
     stack, keeping its last 6 mm straight into the crimp barrel.
   - Land the free ends of DC-1 and DC-2 in the V12 and GND junctions.
   - Make the three joins: the compressor's switched-H core with the relay 1
     NO pigtail, its neutral core with the N-junction pigtail, and the pump
     positive with the relay 2 NO pigtail, each in a 221-413.
   - Seat the loose contacts: J1 cavities 2 and 3 (`OUT1`, `OUT2`), J2
     cavities 2 and 4 (`FAN`, `OUT3`), J4 cavities 5 and 4 (`V5`, `IO25`).
     Then seat J1 and J2 on their wafers. Land the V-A, V-B, V-K and fan
     positives in the manifold commons and the meter's GND in the sensor
     common.
   - Seat J3 and J5. Seat J11 before the V-B return union and its flexible
     return tube go in ([internal plumbing](internal-plumbing.md)); the
     return lies over J11 and the J10 clamps.
   - Feed the J9 display end from inside through the shared pump/display passage,
     whose rear diamond mouth is centred at X0/Z280, and out the open facet. Land it on the display's terminals,
     seat the display ([enclosure-mechanical.md](enclosure-mechanical.md) §8),
     then seat J9.
   - Seat the J13 pump ribbon's XHP-4. Its Fastons are already landed and the pumps
     retained from the loose front-top bench assembly
     ([internal plumbing §3](internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps)).
   Keep both shared-passage looms clear of the funnel-frame seats. Keep the leads with their mounting parents and dress each crossing below
   the closing surfaces. Clear the V-B return bearing and its
   cable-tie path while dressing the leads. Keep the coil leads outside the
   continuous soda inlet's holder and foam sleeve.
   Route lengths describe centerlines; allow the
   specified termination reserve and assembly slack when fabricating looms.
6. Inspect the wiring and plumbing in the central four-quadrant connection
   region while the roof opening is clear. Leave the rigid frame out for
   [firmware-and-commissioning.md](firmware-and-commissioning.md): its USB
   console at J14 and its rail test points lie beneath the frame. The frame
   carries no electrical connection.

## Unpowered completion checks

Confirm continuity from C14 L/N/PE to each scheduled destination, with H, N
and PE isolated from one another, per [wiring.md](wiring.md) step 3. Check
the DC polarity at J10 (`V12` west, `GND` east) and at both pump supply
leads. Confirm protective-earth continuity through each completed metal bond
back to C14 PE. Confirm each populated terminal and join retains its wire and
each plug is squarely seated and labeled. Inspect the funnel opening's edge
and the seams for trapped conductors.

The compressor, fan, display and carbonator bond interfaces retain the
installed model's nominal or unlocated status. A plastic mounting screw does
not provide a carbonator metal bond. These limits prevent claiming a completed
bond or exact donor termination from CAD alone.

Leave the assembly unpowered. Firmware and first power-up belong to
[firmware-and-commissioning.md](firmware-and-commissioning.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_electronics_bay_sync.py`
