# Expanded funnel and compact aft-side plumbing

This isolated above-core arrangement has an aft-expanded funnel, V-B on the
cold-core roof east of the PCB, and an edge-on flow meter between the pump and CO₂ path connected to the
soda bulkhead. V-A, V-K, the pump and PCB retain their established poses.
Ground and WAGO placement remain deferred.

## Funnel and opening

The silicone funnel extends 35 mm in +Y. Its fore edge remains Y87, its aft
edge is Y277.392, and its X width and Z elevations are fixed. The complete
native wet cavity to the mouth is 698.21 mL; cover displacement is excluded.
The outlet is centered fore–aft on the mouth at `(0,179.19575,306.05)` mm.
The drain elbow is `(0,179.19575,280.41)` mm and points aft. The existing
cradle snaps through the removable frame's 3 mm bottom web. The plug, stub,
elbow and cradle travel with that frame; disconnect the V-B feed before
removing it. Silicone forming air is 0.30 mm.

The matching drop-in frame reaches Y270.692. Its four M3 fastener seats face
up; the rear stations are at Y259.492. A matching smooth gravity cover is
included in the native assets. The broad upper-wall and roof opening ends
at Y279, retaining the lower sidewalls and leaving 2.290 mm in plan before
the valve supports. The overflow apron remains continuous.

[funnel-expansion-plan.json](funnel-expansion-plan.json) specifies the native
construction. [funnel-expansion.json](funnel-expansion.json) records capacity,
source hashes and six valid solids.
[centered-drain-review.json](centered-drain-review.json) records the drain attachment
and connector-access review; [fit-report.json](fit-report.json) has the full
isolated-scene fit query. The STEPs and meshes
in `parts/expanded-funnel*` use the study's world frame. Frame receivers and
production-shell integration remain separate.

## Forward water paths

V-B lies square on its side, head east and flow aft, at native origin
`(38,244.90434,280.41)` mm. Its inlet stem seats directly in the valve. The
opposed drain and valve stems point level east/west, with a straight 10.95 mm
exposed tube between them.

The outlet stem points west, rising 8 degrees. A straight 60.41 mm exposed
cross run goes above the PCB into a two-socket elbow. That elbow turns the
return fore, descending into Y-B's aft-facing stem. The descending tube has
82.38 mm exposed length and a 30.31 mm minimum modeled radius; its minimum
Y is 185.127. Its flexible span has a shallow 3 mm crown. The return turn is
at `(−50,280.69954,294.33057)` mm, aft of the frame's Y270.692 edge. The
plumbing remains on the aft side of Y-B. Both PCB power-terminal driver
axes are clear.

[b_plumbing.py](b_plumbing.py) describes those fitting poses, seated interfaces,
centerlines and dimensions. V-A uses one continuous low tube into Y-A's single
aft-facing stem elbow, with minimum modeled radius 27.16 mm. Both tee stems
clock 7.5 degrees outward for drain-cradle clearance.

The native [V-B wall](parts/vb-core-support.step) rises from Z253.4 to Z299.21,
within X34..43.2 and Y225.879..263.929. Its 9.2 mm section contains four shared
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
stands on edge aft between the pump and CO₂ path, with ports fore–aft, label
east and lead root down. Its native origin is `(50,390.9148,306.37605)` mm.
The collet faces are at Y360.4148 and Y421.4148. Main component axes remain
square; the bulkhead grid is fixed.

The outlet collet meets the rear elbow's fore-facing collet. No tube is
exposed between them; their nominal 32.591 mm tube is entirely seated inside
the two sockets. The rear nested stem retains 2.4048 mm exposed stem to place
the meter clear of the CO₂ check; it remains shorter than the full factory
stem. The bulkhead's own stem seats shoulder-flush.

One directly seated inlet stem turns down at `(50,354.3696,306.37605)` mm.
Its straight tube enters a proposed core guide at `(50,354.3696,253.4)` mm,
aft of the pump inlet elbow, with 33.926 mm exposed above the roof. The tube
extends 12 mm below that handoff. The carbonator bottom outlet retains its
own fixed port; the guide and the internal tube route above the endcap need
production integration. The study does not model a vertical continuation
through the pressure vessel.

Three stem elbows and two tube pieces form this above-core line. Socket
depths remain family-based layout estimates. [soda_route.py](soda_route.py)
records the poses and seated interfaces; [fit-report.json](fit-report.json)
records the combined exterior clearance. The measured exterior clears the
pump by 6.83 mm and CO₂ check by 1.05 mm. The inlet elbow clears the pump by
1.85 mm; the new drop clears its inlet TPU elbow by 13.84 mm. Meter pigtail
and core-roof retention detail remain pending.

### Tube insulation

One 15 mm square-cut sleeve of the owned CARGEN pipe foam covers the middle
of the vertical soda tube at X50, Y354.3696, Z264.5..279.5 mm. Its nominal
6.35 mm bore and 9.525 mm wall give 25.4 mm outside diameter. A straight
longitudinal slit allows installation around the connected tube; close the
slit with the existing foil tape. No shaped relief, printed retainer or
component movement is needed. The lower 11.1 mm and upper 7.826 mm of the
33.926 mm exposed tube remain bare. The meter outlet join has no exposed tube.
The meter and fitting bodies remain bare.

[tube_insulation.py](tube_insulation.py) owns the cut-stock envelope and manual
query; [tube-insulation-review.json](tube-insulation-review.json) records its
isolated exterior fit. The native envelope is in
[parts/soda-rise-insulation.step](parts/soda-rise-insulation.step). Stock foam
dimensions are nominal; the model does not establish thermal performance.
Production mounts and complete wiring retain their separate scope.

## PCB access and fit

The board footprint is X−83..−10.200 and Y186.387..277.203 mm, with underside
Z257 and pin tails Z255. Plumbing may pass above the PCB. Electrical
connections are completed before the funnel/frame drops in; the roof also
remains open for connection access.

The J11 local lead estimate dresses aft with a 1 mm straight exit and R4 bend.
Its four conductor paths and source records are in
[pcb-j11-dressed-lead-source.json](parts/pcb-j11-dressed-lead-source.json).
J3 uses cropped native conductor departures from the current installed wiring
cache, recorded in [pcb-j3-dressed-lead-source.json](parts/pcb-j3-dressed-lead-source.json).
PCB and mating housing datums are fixed. Other local connection estimates
travel with their owners. Full harness routing is separate.

With the funnel/frame and disconnected drain assembly removed, the actual J11
housing has a bounded service path: 6 mm up, 6 mm east, then another 20 mm up.
Conservative continuous housing sweeps clear the return by at least 0.439 mm.
This is a housing-envelope check, excluding fingers and flexible lead motion;
[centered-drain-review.json](centered-drain-review.json) records its scope.

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
