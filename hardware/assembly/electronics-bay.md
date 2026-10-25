# Electronics above the cold core

The PCB lies flat on the west side of the cold-core roof, with its long axis
fore–aft. The PSU and diaphragm pump stand aft of it on that roof. V-B mounts
on the core's integral upright wall. V-A/V-K also travel with the lid on
uprights beside the sidewalls; the two relay modules belong to
`enclosure-back-top`. The display, fixed pump contacts and front valve coils
belong to `enclosure-front-top`.

The fore–aft flow meter belongs to the cold-core lid, between the CO₂ group
and pump. Its three leads leave the downward-facing native wire boss; their
installed paths approach from below and clear the two open-west collar supports.

The electronics access panel and funnel frame close the roof after the final
connections. Neither closure carries an electrical component or a cable
restraint. The drain cradle snaps into the removable frame’s 3 mm lower web.
The drain tube must be disconnected or the cradle snap released for frame removal.

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

The PSU's wire entries face fore/aft. Its terminal screws face upward through
the electronics opening. The WAGO bodies and their wells clear these vertical
driver approaches. Leave the opening free while landing and inspecting those
terminals.

## Inputs

Use the per-unit [BOM](/hardware/ledger/bom.md),
[AC and DC wiring schedule](/hardware/wiring/ac-wiring-schedule.md), and
[cable assembly instructions](cable-assemblies.md) for wire stock, contact
assignments, preparation, stripping and termination. Preserve the schedule's
run IDs and loom labels. Use the specified connector graph.

The PCB, PSU and pump use their own native mounting-hole patterns on the
cold-core lid/cup columns. The PCB uses M3 × 8 screws through its 1.6 mm board;
the flat PSU uses M3 × 20 through its 6.7 mm ledges and lid. These columns take
RX-M3×5.7 inserts. The pump retains its specified rubber-pad/washer stack.
Relay mounting screws and their back-top bosses belong to the enclosure
mechanical assembly. The five-ring stack and tooth washer clamp under M3 × 10
into an RX-M3S×4 short insert in the upward-facing core-lid boss. Its 4.8 mm
clamp stack gives 5.2 mm screw projection into a 7 mm blind pilot. Do not
interchange screw lengths between these stacks.

Tools: ESD mat, suitable wire and contact crimpers, soldering tools for the
specified soldered joints, helping hands, insulated driver and multimeter.
Keep the appliance unplugged throughout this assembly.

## Assembly

1. Prepare the cold-core internal wiring and the lid-mounted equipment while
   their entries and screws are exposed. Each reservoir reed column has one
   five-conductor loom. The sensor passage carries the temperature supply,
   data and common, the two carbonator-reed signals and their common, and the
   carbonator PE lead. The printed passages retain the original lower entries
   and guide the upper exits clear of the PCB and PSU. Follow these curved
   passages; a straight chord between the lower and upper mouths does not
   describe their path. Complete the cold-core assembly in
   [cold-core.md](cold-core.md).
2. Seat bare V-A, then bare V-K, in their lid uprights. Attach their prepared
   downward-blade leads while the open bench is clear, before installing the
   PCB, PSU, pump or meter. The bare seating review stages those leads out;
   female-housing fit and connection force remain unqualified.
   Seat the junctions in their named wells and label their electrical purpose.
   Check that each seated body's levers can open and close before populating
   it. Mount the PCB, PSU, pump, meter, V-B and ground stack on their core
   features. Mount the relay modules on back-top.
   Keep both roof closures removed. The PCB's J14 remains the
   programming interface.
3. Land the fixed AC and DC runs by the schedule: C14 to H/N/G, H/N to the
   PSU primary, H to relay 1 COM, the PSU secondary to V12/GND, V12 to relay 2
   COM, and V12/GND to PCB J10. Relay 2 NO feeds the pump positive lead;
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
5. Stage the front-top looms at their fixed display, front coil and pump-contact
   endpoints. Install the core/back-bottom and upper quadrants with the final
   roof openings clear. Use these openings to connect J1/J2 valve commons
   and returns, J13 pump contacts, J9 display, the remaining PCB sensor/data
   headers, the rear relay connections and the core-to-rear power leads.
   Pass the four J9 display conductors through the existing ridge loom bore
   near X32/Z308, then dress them to the display terminals.
   Keep the leads with their mounting parents and dress each crossing below
   the closing surfaces. Clear the two lid-rooted valve-union bearings and their
   cable-tie paths while dressing the leads. Keep the coil leads outside the
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
   before lifting the frame. Fit the electronics access panel independently;
   no electrical connection is made to either closure.

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
