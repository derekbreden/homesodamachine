# Expanded funnel and compact aft-side plumbing

This isolated above-core arrangement has an aft-expanded funnel, V-B on the
cold-core roof east of the PCB, and an edge-on flow meter between the pump and CO₂ path connected to the
soda bulkhead. V-A, V-K, the pump and PCB retain their established poses.
Ground and WAGO placement remain deferred.

## Implementation target

[approved-arrangement.json](approved-arrangement.json) records the selected
component frames and display bounds.
[assembly-ownership.json](assembly-ownership.json) records the carrying pieces
and connections between them. V-A, V-K and their low feed plumbing attach to
back-top. V-B attaches to the cold-core lid, carried by back-bottom. Component
position and attachment are both part of the implementation target. Retaining
details follow those assignments. A necessary layout or attachment compromise
requires discussion with Derek before adoption.

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

The outlet stem points west, rising 8 degrees. A straight 35.00 mm exposed
cross run goes above the PCB into a two-socket elbow. That elbow turns the
return fore, descending into Y-B's aft-facing stem. The descending tube has
76.67 mm exposed length and a 27.44 mm minimum modeled radius; its minimum
Y is 185.127. Its flexible span has a shallow 2 mm crown. The selected return
turn is at `(−24.836524,280.69954,290.794074)` mm, aft of the frame's Y270.692
edge. The plumbing remains on the aft side of Y-B.

The X−50 return in [centered-drain-review.json](centered-drain-review.json)
is an implementation variant with recorded PCB power-driver and J11 access.
It requires discussion with Derek before adoption. Its clearance readings do
not qualify the selected return at X−24.836524.

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

## Purchased check valves

Both the pump-discharge and CO₂ paths use the shared
[neoFit ACHV44-E reference](../../../reference/neofit-achv44-check/README.md).
[purchased_checks.py](purchased_checks.py) imports its native STEP and derives
socket datums and engagement from its API. The 55.432 mm mouth spacing and
16.863 mm maximum barrel diameter are estimates from supplier display media
scaled against the published sibling neoFit fixed collar. Socket engagement
is a same-family estimate of 16.891 mm.

The pump-side inlet stays fixed. The outlet's stem elbow points down, with
a 7.719 mm exposed vertical tube to the proposed passive core guide at
`(−32.8018,410.05329,253.4)` mm. The guide adds no fitting; the continuous
internal tube to the real carbonator port is production integration work.

The CO₂ fold retains its five stem elbows. Each nominal male shoulder has
0.4 mm exposure. The regulator and fold are 0.7 mm east and 1.2 mm down from
their fixed-terminal construction frame; shallow tube transitions keep the
rear bulkhead and core guide fixed. The upper U has a single rectangular
ceiling pocket, roof Z352, with 3 mm of ceiling retained and 1.041 mm air above
the fitting. The meter clears the purchased gas check by 1.072 mm in the
exterior-mesh query.

[purchased-checks-native.json](purchased-checks-native.json) records the shared
source hashes, selected frames, seated interfaces, valid native solids and
ceiling pocket. The local NPZ files are display derivatives of that reference.
The manual native export captures the selected production frames and tube
curves in this record. Routine study queries use that snapshot; subsequent
production placement edits cannot move the clean study's components.

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

### Selected continuous inlet and insulation

[continuous_soda_bend.py](continuous_soda_bend.py) consumes the shared production
[soda_inlet.py](../../soda_inlet.py) plan and native builders. It shows a continuous
1/4-inch LLDPE tube through the accepted R14 PET-GF bend holder, with its 2 mm wall and
3 mm legs, into the meter's inlet socket. The holder carries no fluid joint.
One approximately 63 mm square-cut piece of the owned foam slides over the
tube and holder before the meter connects. The holder displaces foam inside
the sleeve; the nominal outside diameter is 25.4 mm.

The meter and every main component keep their poses. The passive core entry
is `(50,342.4148,253.4)` mm.
The external CAD span starts at that handoff. The production tube continues
below it; it is not cut or joined at the guide.
The inlet has no push-fit elbow or additional tube joint. The carbonator's
bottom outlet retains its own fixed port. Two nested stem elbows form the
meter-to-bulkhead return; [soda_route.py](soda_route.py) supplies its interfaces.
Socket depths remain family-based layout estimates.

The [printed-elbow foam fit](../../../reference/cargen-pipe-insulation/elbow-fit-2026-10-24/physical-observation.json)
records the pictured holder fitting inside the owned sleeve with little visible
outer expansion and local compression inside. This is qualitative fit evidence
for that article.

[continuous-soda-bend-review.json](continuous-soda-bend-review.json) records no
unrelated rigid contacts. The holder clears the meter by 1 mm and the pump
inlet TPU by 4.124 mm; the tube clears that TPU by 1.891 mm. The stock foam
compresses locally against the pump, V-K and pump inlet hardware. The tightest
sampled radial space leaves approximately 1.89 mm between tube and TPU.
The translucent occupied-space foam mesh illustrates this compression; it is
not a shaped cutting pattern or a prediction of strain or thermal performance.
The uncompressed stock envelope and occupied-space estimate both come from the
production native API. Its occupied estimate uses the four named native neighbors.

[continuous-soda-bend.json](continuous-soda-bend.json) supplies the source,
selection, holder acceptance, datums and native geometry. Production integration
of the printed supports, under-lid continuation and complete installed harness
is pending. The selected layout fixes the main component poses; any integration
change to them requires an explicit arrangement review.

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

The bounded J11 housing service path in
[centered-drain-review.json](centered-drain-review.json) applies to its recorded
X−50 return variant with the funnel/frame and disconnected drain assembly
removed. It moves 6 mm up, 6 mm east, then another 20 mm up, with 0.439 mm
minimum nominal clearance. This is a housing-envelope check, excluding fingers
and flexible lead motion. Access with the selected return is an open integration
question in [implementation-review.json](implementation-review.json).

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
PYTHONPATH=. tmp/takeover/cadq "Shared purchased checks" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/purchased_checks.py --freeze
tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/study.py --check
python3 hardware/manifold-layout/studies/funnel-gate/viewer.py hardware/manifold-layout/studies/funnel-gate/out/whole-arrangement.html
```

No command is added to the build or commit path. Production enclosure geometry,
retaining details and complete harness/tube routes retain their separate scope.
