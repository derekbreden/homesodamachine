# PCB low and forward

The main PCB lies flat, components upward, on the forward part of the cold core.
Its underside is Z257 mm, 3.6 mm above the plain cap datum. The populated board
spans X−72..0.80, Y182..272.82 and Z255..276.10 mm. Its tails have 1.6 mm nominal
clearance to the plain cap. Mating JST housings and local wire departures move
with the board; the connected envelope reaches Z276.25 mm.

The water header, power supply, relays, rear connectors, funnel/frame and
ideal wall/ceiling solids retain the selected poses in
[`../wet-dry/`](../wet-dry/). V-B and the reservoir routes are outside this
component group; V-B is available for placement on the other side.

Place WAGO junctions last, after the primary components and wire routes, where
the connections are actually needed. Their locations remain unspecified while
the funnel and primary components are arranged. All nine WAGOs are deferred
from this study's scene and clearance queries.

[`study.json`](study.json) records the selected poses and the manual intersection
query. The repositioned PCB, plugs and local leads have no surface intersection
with this selected group. Complete harness routes, PCB mounting details and a
full service sequence remain outside this arrangement study.
[`connection-datums.json`](connection-datums.json) carries the electrical interfaces.

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/pcb-low-fore/study.py --check
```

The generator reads frozen meshes and connector interfaces from the existing
studies. It adds no production dependency or automatic check.
