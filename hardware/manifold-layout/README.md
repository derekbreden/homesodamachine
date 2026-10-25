# Manifold layout

The production assembly combines eight fixed front valves, two KPHM600 pumps,
six purchased PP0208E tees and the above-core equipment. Its native placements
and physical tube paths are defined in [above-core.md](above-core.md) and
[above-core.json](above-core.json). [enclosure_assembly.py](enclosure_assembly.py)
composes those parts with the refrigeration base, cold core, printed enclosure
and installed wiring.

The connections follow [fluid-topology.md](/hardware/topology/fluid-topology.md).
Each reservoir has separate fill and draw mouths; segments 14/24 fill them and
16/26 draw from them. The two source valves connect the water and funnel feeds
to the front manifold through explicit compact fittings and continuous tubes.
V-A and V-K mount on the cold-core lid's upright socket walls beside the
sidewalls. V-B uses the lid's upright wall east of the PCB. All three travel
with the populated core during enclosure assembly.

## Fixed front manifold and pump dock

The eight front valves stand on two decks in `enclosure-front-top`. Four pump
tees pass through the tee wall behind its collet plate. Each tee's branch takes
one prepared pump tube; its upper run reaches a fore valve through a short
straight tube, and its lower run reaches a rear valve through two trimmed
NeoFit ATEU44W stem elbows and one straight LLDPE tube. The two source tees,
Y-A and Y-B, meet V-C and V-D through their existing collet butt joints.

The pump cradle and top clamp hold both prepared pumps. Their housings clamp
the four tubes, which pass front-top's collet plate into the purchased tees;
each branch collet stands extended in its recess and grips its tube, and those
four collets hold the cradle home.

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
the frame with its drain assembly and fitting its four screws. Disconnect the
drain tube or release the cradle before removing the frame.
The independent electronics panel is also empty and installs after its
connection work.

The production route definitions retain each fitting's own native geometry
and receiving-socket insertion estimate. Cut lengths are sums of actual tube
centreline lengths and the explicitly modeled insertions; fittings are not
represented by fabricated continuous tube. Follow the [internal plumbing
procedure](/hardware/assembly/internal-plumbing.md) and actual fully seated
marks when making the assembly.

## Authoring modules

[manifold_layout.py](manifold_layout.py) owns the reusable front manifold,
pump-dock connections and their authoring reference frames. Its standalone
`manifold-layout.step` includes the source-valve authoring construction;
production takes the selected V-A/V-B poses and source routes from the
above-core modules instead. The fixed front valve, tee and pump datums retain
their common source.

[above_core_parts.py](above_core_parts.py) builds the selected native purchased
bodies, trimmed fittings, TPU interfaces and local tubes.
[above_core_routes.py](above_core_routes.py) continues them to the core and rear
ports. [above_core_wiring.py](above_core_wiring.py) supplies junction positions
and their mounting features. The complete electrical graph and conductors
live in [installed wiring](/hardware/wiring/installed/).

The refrigerator loop retains its own compressor, condenser and cold-core
fitting datums. Its physical joints and formed copper runs remain distinct
from these flavor and water paths.
