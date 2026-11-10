# Manifold layout

The production assembly combines eight fixed front valves, two KPHM600 pumps,
six purchased PP0208E tees and the above-core equipment. Its native placements
and physical tube paths are defined in [above-core.md](above-core.md) and
[above-core.json](above-core.json). [The installed machine](installed_machine.rs)
composes those parts with the refrigeration base, cold core, printed enclosure
and installed wiring, and writes the shared mesh scene the site draws, its
facts and its named views. The machine's clash checks are off during the Rust conversion;
they come back written in Rust once the parts they read have moved.

The connections follow [fluid-topology.md](/hardware/topology/fluid-topology.md).
Each reservoir has separate fill and draw mouths; segments 14/24 fill them and
16/26 draw from them. The two source valves connect the water and funnel feeds
to the front manifold through explicit compact fittings and continuous tubes.
V-A hangs from back-top's ceiling socket plinth; V-K uses its east-wall socket seat.
V-B uses the core lid's upright wall east of the PCB. The PCB and pump also
remain on the core. Back-top carries the ceiling PSU, two west-wall relays, the threaded ASSE chain,
Pisco/check group, meter and its continuous inlet, holder and insulation.
Their integral slide seats and removable snap caps share the production datums.

V-F's outlet, V-E's inlet and V-I's outlet each take a trimmed ATEU44W stem
elbow. Their reservoir tubes pass below the funnel frame with 1.225 mm nominal
air. The 4 mm flavor-A line crosses at Y266/Z296; the J9 ribbon's free fore
bends pass below it. The fixed cable passage, connectors, valve poses and
paired reservoir anchors retain their selected stations.

## Fixed front manifold and pump dock

The eight front valves stand on two decks in `enclosure-front-top`. Four pump
tees pass through the tee wall behind its collet plate. Each tee's branch takes
one prepared pump tube; its upper run reaches a fore valve through a short
straight tube, and its lower run reaches a rear valve through two trimmed
NeoFit ATEU44W stem elbows and one gently formed LLDPE tube. The two source tees,
Y-A and Y-B, meet V-C and V-D through their existing collet butt joints.

Front-top's integral upper pockets and the broad lower retainer capture
both prepared pumps. Two integral snap wings secure the retainer before the
four tee/upper-tube/fore-valve groups approach individually from aft. The pump
housings clamp the four tubes; each tee's extended branch collet grips and seals
its tube. The retainer and fixed upper pockets carry the pumps.

See the [pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md) for
its native interfaces. Retain the accepted pump-holder result within its
recorded material, orientation and artifact scope. Native geometry does not
establish tube insertion force, pressure retention, sealing, cleanability or
lifetime.

## Source paths and final access

V-A's selected low route reaches Y-A below the funnel. V-B's return stays aft
of the funnel, crosses west above the PCB and descends into Y-B. The funnel's
drain cradle snaps into the removable rigid frame's bottom web. Complete the
front-to-core and rear-quadrant connections through this opening before lowering
the frame with its drain assembly and fitting its four screws. The plug,
elbow and cradle travel with the frame; disconnect the V-B feed before removing
it. The rear ceiling is continuous.

Keep the cross-quadrant tube ends free while positioning back-top. Make the
V-A/Y-A, V-K/pump and continuous core-tube handoffs through the open funnel
area, then fit the frame. The rear equipment is populated on the inverted
back-top before closure. Keep the pump suction elbow and short quarter-inch
inlet link loose during approach and make that connection after closure.

The production route definitions retain each fitting's own native geometry
and receiving-socket insertion estimate. Cut lengths are sums of actual tube
centreline lengths and the explicitly modeled insertions; fittings are not
represented by fabricated continuous tube. Follow the [internal plumbing
procedure](/hardware/assembly/internal-plumbing.md) and actual fully seated
marks when making the assembly.

## Iterating on the installed machine

[`above-core.json`](above-core.json) owns the equipment's placements and local dimensions.
[`junctions.json`](junctions.json) owns the enclosure junctions' placements, connector choices
and pocket fit. The printed pockets, installed connectors and wire terminals share those
junction values. These documents are runtime inputs to the compiled Rust programs.

Build the affected printed pieces and installed machine through the normal print build:

```sh
tools/run -- hsm-print-build //:enclosure-back-top //:installed-machine
```

The assembly retains unchanged stages and conductor geometry in the shared realized cache.
Its completed placement and mechanical scenes can reach the website while dependent wiring
continues. A partial scene carries its pending stages; it does not establish print readiness.
Runtime parameter edits reuse the executable. Construction-code edits rebuild the program.

[`route-overrides.json`](../wiring/installed/route-overrides.json) owns the selected wire-route
stations. A route edit uses the same command with only `//:installed-machine`; unchanged
mechanical stages, conductors and terminations keep their retained geometry.

The assembly's retained stages are reported in `.cache/realized/installed-machine/last-run.json`.
Its wiring's retained fine and presentation entries are reported beside them under
`wiring/parts/last-run.json`. These are run receipts, outside the website and print outputs.

## Authoring modules

[manifold_layout.rs](manifold_layout.rs) owns the reusable front manifold,
pump-dock connections and their authoring reference frames. Its standalone
`manifold-layout.step` includes the source-valve authoring construction;
production takes the selected V-A/V-B poses and source routes from the
above-core modules instead. The fixed front valve, tee and pump datums retain
their common source.

[machine_equipment.rs](machine_equipment.rs) builds the selected native purchased
bodies, trimmed fittings, TPU interfaces and local tubes.
[machine_routes.rs](machine_routes.rs) continues them to the core and rear
ports. The enclosure's [junction reader](../printed-parts/enclosure/enclosure/numbers/junctions.rs)
supplies the shared connector and pocket placements. The complete electrical graph and conductors
live in [installed wiring](/hardware/wiring/installed/).

The refrigerator loop retains its own compressor, condenser and cold-core
fitting datums. Its physical joints and formed copper runs remain distinct
from these flavor and water paths.

## The interior, written down

[`enclosure-box.json`](enclosure-box.json) holds where the enclosure is cut and built up
for the parts inside it: the condenser's cradles, mount and airway, the pump and valve trays,
the cold core's stops and holds, the floor bosses, the ceiling, flank and corner-column
reliefs, the vent chase, the collet plate and the pump bay's wall. The enclosure's printed
pieces and the whole-machine assembly read it as it is committed; nothing in the build works
it out.

The native installed-machine producer resolves the current arrangement and retains the
placement-derived enclosure context. Use the progressive print build for a mechanical edit:

```sh
tools/run -- hsm-print-build //:installed-machine
```
