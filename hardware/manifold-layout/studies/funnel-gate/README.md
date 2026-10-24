# Expanded funnel and compact aft-side plumbing

This isolated above-core arrangement has an aft-expanded funnel, V-B on the
cold-core roof east of the PCB, and an edge-on flow meter between the pump and CO₂ path connected to the
soda bulkhead. V-A, V-K, the pump and PCB retain their established poses.
Ground and WAGO placement remain deferred.

## Funnel and opening

The silicone funnel extends 35 mm in +Y. Its fore edge remains Y87, its aft
edge is Y277.392, and its X width and Z elevations are fixed. The complete
native wet cavity to the mouth is 698.21 mL; cover displacement is excluded.
The outlet remains `(0,161.69575,306.05)` mm, and the drain elbow remains
`(0,161.69575,280.41)` mm.

The matching drop-in frame reaches Y270.692. Its four M3 fastener seats face
up; the rear stations are at Y259.492. A matching smooth gravity cover is
included in the native assets. The broad upper-wall and roof opening ends
at Y279, retaining the lower sidewalls and leaving 2.290 mm in plan before
the valve supports. The overflow apron remains continuous.

[funnel-expansion-plan.json](funnel-expansion-plan.json) specifies the native
construction. [funnel-expansion.json](funnel-expansion.json) records capacity,
source hashes, six valid solids and targeted fit results. The STEPs and meshes
in `parts/expanded-funnel*` use the study's world frame. Frame receivers and
production-shell integration remain separate.

## Forward water paths

V-B lies square on its side, head east and flow aft, at native origin
`(38,227.40434,280.41)` mm. Its inlet stem seats directly in the valve. The
opposed drain and valve stems have 10-degree upward clocks and an 11.59 mm
exposed tube between them. That tube's minimum modeled radius is 32.22 mm.

The outlet stem points west, rising 8 degrees. A straight 35.00 mm exposed
cross run goes above the PCB into a two-socket elbow. That elbow turns the
return fore, descending into Y-B's aft-facing stem. The descending tube has
59.62 mm exposed length and a 40.27 mm minimum modeled radius; its minimum
Y is 185.127. The plumbing remains on the aft side of Y-B. The highest fitting
surface is Z298.884, below the frame's Z299.9 underside.

[b_plumbing.py](b_plumbing.py) describes those fitting poses, seated interfaces,
centerlines and dimensions. V-A uses one continuous low tube into Y-A's single
aft-facing stem elbow, with minimum modeled radius 27.16 mm. Both tee stems
clock 7.5 degrees outward for drain-cradle clearance.

The native [V-B wall](parts/vb-core-support.step) rises from Z253.4 to Z299.21,
within X34..43.2 and Y208.379..246.429. Its 9.2 mm section contains four shared
V69 blind sockets and the port channel, retaining 3 mm behind socket floors.
The wall and valve travel with back-bottom. The existing
[valve-seat](../../../printed-parts/valve-seat/README.md) fit evidence keeps its
original scope; fusion into the production core lid and installed retention
remain separate.

[route.json](route.json) records all fitting poses, tube centerlines and socket
assumptions. The drain stem is 19.006 mm long with 3.306 mm exposed beyond its
nominal 15.7 mm insertion to clear the cradle. Other stem shoulders seat flush.
Dimensions and cut lengths are layout estimates.

## Soda line

The [measured DIGITEN reference](../../../reference/digiten-flow-sensor/README.md)
stands on edge between the pump and CO₂ path, with ports fore–aft, label east
and lead root down. Its native origin is `(52.4048,372,306.37605)` mm. The
collet faces are at Y341.5 and Y402.5. Main component axes remain square.

The core soda port stays `(77.5,271.6,253.4)` mm. Its straight riser enters a
union elbow, which receives an aft-facing stem elbow directly. That fold
places the feed west of V-K. The 51.09 mm exposed feed enters the meter
axially, with a gentle 4.512 mm lateral offset and minimum centerline radius
95.50 mm. The core-fold stem retains 3 mm of exposed stem to clear the
existing valve-wall root; its estimated insertion remains 15.7 mm.

The meter outlet has a straight 18.915 mm exposed tube into a fore-facing
stem elbow nested directly in the bulkhead's west-facing elbow. The bulkhead
grid is fixed. Four elbows total make the route's turns: one union and three
stems, with no tube between either nested pair. The riser extends 12 mm below
the core handoff plane. Socket depths remain layout estimates.

[soda_route.py](soda_route.py) records both routes, insertion assumptions and
all fitting poses. [fit-report.json](fit-report.json) records the combined
exterior clearance: meter to pump 1.46 mm, meter to CO₂ check 1.40 mm, core-fold
stem to valve-wall root 1.17 mm and meter to ceiling 30.47 mm. The meter pigtail
and retention detail remain pending; a core-roof carrier is proposed.

## PCB access and fit

The board footprint is X−83..−10.200 and Y186.387..277.203 mm, with underside
Z257 and pin tails Z255. Plumbing may pass above the PCB. Electrical
connections are completed before the funnel/frame drops in; the roof also
remains open for connection access.

The J11 local lead estimate dresses aft with a 1 mm straight exit and R4 bend.
Its four conductor paths and source records are in
[pcb-j11-dressed-lead-source.json](parts/pcb-j11-dressed-lead-source.json).
PCB and mating housing datums are fixed. Other local connection estimates
travel with their owners. Full harness routing is separate.

[fit-report.json](fit-report.json) records the combined exterior fit, intended
seats, local lead checks, nominal 6 mm JST withdrawal sweeps and 30 mm vertical
columns. Installed and funnel/frame-removed access states are both reported;
those columns are diagnostic envelopes, not mandatory clear space above every
connector. Finger reach and complete harness manipulation are not modeled.

## Arrangement highlighting

One whole-arrangement camera supports Assembly quadrant, Latest changes and
Normal highlights. Changing highlight preserves the camera. Native walls,
V-B's wall and the integral V-A/V-K/relay support overlays remain visible; the
roof is hidden. The matching funnel cover is a native asset; the interior
view shows the funnel open. Local leads are suppressed while mating housings
remain visible.

[assembly-ownership.json](assembly-ownership.json) follows mounting parents.
Funnel/frame and front manifold fittings are front-top; walls, V-A/V-K and
rear fittings are back-top; core-mounted equipment, PCB and V-B are back-bottom.
The meter carrier is proposed as back-bottom. Part details identify proposed
attachments and the final tube connections between quadrants.

Latest changes compares against [highlight-baseline.json](highlight-baseline.json).
Mesh signatures use decompressed geometry and normalized poses independently
of compressed archive timestamps.

Rebuild native assets through the shared CAD queue, then manually query and
package the selected scene:

```sh
PYTHONPATH=. tmp/takeover/cadq "Expanded funnel group" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/build_funnel.py
PYTHONPATH=. tmp/takeover/cadq "V-B cold-core roof wall" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/build_support.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/study.py --check
python3 hardware/manifold-layout/studies/funnel-gate/viewer.py hardware/manifold-layout/studies/funnel-gate/out/whole-arrangement.html
```

No command is added to the build or commit path. Production enclosure geometry,
retaining details and complete harness/tube routes retain their separate scope.
