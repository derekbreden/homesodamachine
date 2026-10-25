# Electronics above the cold core

The PCB lies flat on the west side of the cold-core roof, with its long axis
fore–aft. The diaphragm pump and V-B belong to that core. Back-top carries
V-A/V-K, their fitted plumbing, the water header, the PSU and both relays.
The PSU mounts to the dry west sidewall, with the relays above it. The display,
the pump cradle in its bay and the front valve coils belong to `enclosure-front-top`.

The fore–aft flow meter travels with back-top between the CO₂ group and pump.
Its two fixed collars sit in integral east-wall carriers; the moving collets
remain free. Its three leads leave the downward-facing native wire boss.
The accepted R14 holder, continuous inlet and foam sleeve travel with the meter;
the uncut tube passes through the core's plain guide.

The ceiling is continuous behind the funnel aperture. Keep the drop-in frame,
silicone and cover off during the final connections. The drain cradle snaps
into the removable frame’s 3 mm lower web. Disconnect its tube or release
the cradle snap before lifting the frame.

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
| N | 221-413 | Back-top rear wall | C14 N; PSU N; compressor neutral |
| G | 221-413 | Back-top rear wall | C14 PE; ground ring stack |
| V12 | 221-413 | Cold-core lid | PSU V12; relay 2 COM; PCB J10 V12 |
| GND | 221-413 | Cold-core lid | PSU GND; pump negative; PCB J10 GND |
| Sensor common | 221-413 | Cold-core lid | PCB J4 GND; temperature common; flow-meter common |
| Reservoir B common | 221-413 | Cold-core lid | PCB J7 GND; reservoir B reed common; carbonator reed common |
| Manifold A common | 221-420 | Front-top east wall | PCB J1 COM; valve A–H positive leads |
| Manifold B common | 221-415 | Front-top east wall | PCB J2 COM; valve I/J/K and condenser-fan positive leads |
| Protective-earth ring stack | M3 ring-terminal stack | Cold-core lid | C14 earth feed; compressor earth; carbonator bond lead |

The rear H/G connectors share a vertical row beside the C14 inlet; N stands
14.5 mm forward on its own broad rear-rooted well. Their wire entries face
forward and their levers open upward. The four core-side
221-413 connectors form a fore–aft column beside the PCB; wire entries face
−X toward the PCB and levers face upward. The printed wells capture each connector's blank
rear half with 3 mm stock. The manifold common connectors retain their native
front-top stations and their two lever faces remain accessible from the front
assembly's open interior.

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
each device. The five-ring stack and tooth washer clamp under M3 × 10 into an
RX-M3S×4 short insert in the upward-facing core-lid boss. Its 4.8 mm clamp
stack gives 5.2 mm screw projection into a 7 mm blind pilot.

Tools: ESD mat, suitable wire and contact crimpers, soldering tools for the
specified soldered joints, helping hands, insulated driver and multimeter.
Keep the appliance unplugged throughout this assembly.

Follow the carrying parts and closing order in
[enclosure-mechanical.md](enclosure-mechanical.md). The
[carried-group review](../mechanical-qualification/enclosure-above-core/approved-carried-group-review.json)
records the current rigid-slide and final-connection limits.

## Assembly

1. Prepare the cold-core internal wiring and the lid-mounted equipment while
   their entries and screws are exposed. Each reservoir reed column has one
   five-conductor loom. The sensor passage carries the temperature supply,
   data and common, the two carbonator-reed signals and their common, and the
   carbonator PE lead. The printed passages retain the original lower entries
   and guide the upper exits clear of the equipment. Follow these curved
   passages; a straight chord between the lower and upper mouths does not
   describe their path. Complete the cold-core assembly in
   [cold-core.md](cold-core.md).
2. Seat V-A/V-K on open back-top with their fitted plumbing. Attach their
   prepared downward-blade leads while that subassembly is accessible.
   Female-housing fit and connection force remain unqualified.
   Seat the junctions in their named wells and label their electrical purpose.
   Check that each seated body's levers can open and close before populating
   it. Land the two prepared J10 power leads on the loose PCB before fastening
   it to the core; leave their WAGO ends free. The captured upper B-fill fitting
   limits a straight lead-entry approach at the installed board. Mount the PCB,
   pump, V-B and ground stack on their core features.
   Fasten the PSU on bare back-top before seating the rear WAGO-H junction;
   its aft mounting-driver path crosses that connector. Mount the relays and
   meter, and prepare the meter’s inlet and concealed outlet plumbing. Service
   of that PSU mounting screw may require withdrawing WAGO-H from its well. Keep the funnel frame removed. The PCB's J14 remains the
   programming interface.
3. Land the fixed AC and DC runs by the schedule: C14 to H/N/G, H/N to the
   PSU primary, H to relay 1 COM, the PSU secondary to V12/GND, V12 to relay 2
   COM, and the free ends of the prelanded J10 leads to V12/GND. Keep the V-B
   return union and its flexible return tube clear while tightening J10, then
   fit them at their selected poses. The installed lead and vertical screw
   tools clear the selected B-fill fitting; the nominal 8 mm straight wire-entry
   land does not. Field retermination may require unbolting and staging the PCB
   and flexible leads. That handling and its service path remain unqualified.
   Relay 2 NO feeds the pump positive lead;
   pump negative returns to GND. Relay 1 NO, neutral and protective earth
   are the continuous three cores of the compressor's single SJOOW lead. Its
   jacket rises through the open front floor lane near X48/Y130 and ends at
   approximately X48/Y165.76/Z274.77 in the fore connection area. The same
   individually insulated cores fan out from there to the existing relay,
   neutral junction and earth stack, without an inline splice. The jacket's
   lower end approaches the thermal-fuse/donor-interface region. Retain the specified direct solid-wire clamp
   and stranded-wire termination choices.
4. Land J5 at the two relay modules: IO19 to relay 1 IN, IO2 to relay 2 IN,
   V5 and GND to both modules. The shared relay-end rail termination remains
   subject to the installed model's stated termination limit. Populate the
   sensor and reservoir-B common junctions without adding junctions to the
   continuous reservoir-A reed common.
5. Stage the front-top looms at their fixed display and front coil endpoints.
   Install the core/back-bottom and upper quadrants with the final
   funnel opening clear. Use this opening to connect J1/J2 valve commons
   and returns, the J13 pump ribbon at the pump cradle's installation
   ([internal plumbing §3](internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps)),
   J9 display, the remaining PCB sensor/data headers, the rear relay
   connections and the core-to-rear power leads.
   Bounded J11 housing service uses 6 mm up, 6 mm east and 20 mm up after
   removing the funnel/frame and disconnected cradled drain and releasing the
   flexible B return from its path. Flexible lead handling remains unqualified.
   Pass the four J9 display conductors through the existing ridge loom bore
   near X32/Z308, then dress them to the display terminals.
   Keep the leads with their mounting parents and dress each crossing below
   the closing surfaces. Clear the V-B return bearing and its
   cable-tie path while dressing the leads. Keep the coil leads outside the
   continuous soda inlet's holder and foam sleeve. Dress the three meter leads
   below V-K's coil, cross east ahead of the foam and run aft outside its wall.
   Route lengths describe centerlines; allow the
   specified termination reserve and assembly slack when fabricating looms.
6. Inspect the wiring and plumbing in the central four-quadrant connection
   region while the roof opening is clear. Lower the rigid frame vertically,
   engage the drain cradle’s snaps in its lower web and seat the four
   upward-accessible M3 screws. Complete and inspect the drain connection
   before fitting the silicone funnel onto the standing stub and bearing
   surfaces. The geometric frame-lift review removes the cradle, elbow, stub
   and tubing; it does not qualify connected-tube motion or snap-release
   access and force. Disconnect the drain tube or release the cradle snap
   before lifting the frame. The frame carries no electrical connection.

## Unpowered completion checks

Confirm continuity from C14 L/N/PE to each scheduled destination, with H, N
and PE isolated from one another. Check the DC polarity at J10 and at both
pump supply leads. Confirm protective-earth continuity through each completed
metal bond back to C14 PE. Confirm each populated terminal retains its wire
and each plug is squarely seated and labeled. Inspect the final roof seats
for trapped conductors before closing them.

The compressor, fan, display and carbonator bond interfaces retain the
installed model's nominal or unlocated status. A plastic mounting screw does
not provide a carbonator metal bond. The faucet plate's earth landing is
unresolved in the wiring schedule. These limits prevent claiming a completed
bond or exact donor termination from CAD alone.

Leave the assembly unpowered. Firmware and first power-up belong to
[firmware-and-commissioning.md](firmware-and-commissioning.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_electronics_bay_sync.py`
