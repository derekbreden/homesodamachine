# V-B on the cold-core roof, east of the PCB

This isolated above-core arrangement places V-B on the cold-core roof east of
the PCB. V-A, its mounting seat, the upstream water group and the photographed
flat elbow under the pump head retain their established poses. The drain
elbow, stub, cradle, Y-A and Y-B retain their production datums. WAGOs and
ground placement remain deferred.

## Forward plumbing

V-B lies square on its side, head east and flow aft. Its native origin is
`(38,241.92153,280.41)` mm. Its body occupies X38..95.30,
Y212.172..271.672 and Z263.66..297.16 mm. The funnel drain turns east, then
aft directly into V-B. Two nested stem elbows reverse its outlet toward the
front, west of its mounting wall. Their fold plane rises 25 degrees; the
valve stays aligned with the enclosure axes. The return follows one straight
fore run and a formed U into Y-B. Five added elbows connect the B chain;
exposed tubing totals 210.47 mm. The U has a minimum modeled centerline
radius of 21.17 mm. The two feed fittings clock their transverse arms upward
10 degrees; the short joining tube rises between their mouths. No route crosses above the west PCB.

V-A has one continuous low tube and one stem elbow at Y-A. The elbow faces
aft, clocked 7.5 degrees east. The tube stays low and west of V-B's mounting
wall before rising into Y-A; its two tangent spans have a minimum modeled
centerline radius of 27.16 mm. Y-B's stem faces fore, clocked 7.5 degrees west.
Both stems clear the retained drain cradle by 0.66 mm. V-A's tube clears the
board by 31.17 mm. The high B return passes above the low A feed.

[route.json](route.json) records every fitting pose, tube centerline and
insertion assumption. The drain stem is 19.006 mm long, with 3.306 mm exposed
beyond its nominal 15.7 mm receiving depth to clear the cradle. Other stem
shoulders sit flush. Socket engagements are family-based layout estimates.

## V-B wall and mounting parent

The native [V-B support](parts/vb-core-support.step) is one valid solid:
an upright 9.2 mm seat wall with four shared V69 blind sockets and the valve's
port channel. It rises from the core roof at Z253.4 to Z299.21 mm, within
X34..43.2 and Y222.897..260.947 mm. Each blind socket retains 3 mm of stock
behind its floor. The wall and valve are carried by **back-bottom**;
[mount-plan.json](mount-plan.json) fixes their attachment and world coordinates.
The geometry uses the existing
[valve-seat](../../../printed-parts/valve-seat/README.md) dimensions and retains
the scope of that part's physical fit evidence. Fusion into the production
core lid, installed post retention and loads remain outside this arrangement
study. PCB fasteners remain to design.

The funnel drain outlet stem and Y-B elbow are carried by front-top. V-B's
inlet and return tubes are carried by back-bottom and connect to those two
front-top fittings during final assembly.

## Fit and PCB connections

The flat board's long dimension runs fore–aft. Its footprint is
X−83..−10.200 and Y186.387..277.203 mm; underside Z257 and pin tails Z255.
It has 15.5 mm to the ideal west wall and 17.65 mm beside the west J5/J6
housings. The north/south gaps to V-A's support and the core's fore edge are
4.087 mm each. Normal local lead estimates travel with the board.

The [manual fit report](fit-report.json) has no unrelated solid-body or local
lead intersections. V-B clears the funnel frame by 10.39 mm. Its nested outlet
clears the pump by 1.27 mm and its wall by 0.54 mm. The low A tube clears the
B inlet union by 0.73 mm; the A and B feed elbows clear by 1.17 mm. The raised
B feed tube passes its high return by 0.39 mm. These are nominal mesh gaps,
with purchased-part dimensions and socket depths partly estimated.

All ten 6 mm JST housing withdrawal sweeps and all ten 30 mm vertical columns
above the housing outlines clear with the funnel/frame installed and the roof
removed. These are nominal housing/access envelopes; finger reach and complete
harness manipulation are not modeled. Local leads are suppressed in the viewer;
installed mating housings remain visible.

## Flow-meter placement candidate

The [measured DIGITEN reference](../../../reference/digiten-flow-sensor/README.md)
sits above the pump, aft of the ASSE, with its label up and port axis fore–aft.
Its native origin is `(0,412,326.1)` mm. The exterior occupies
X−9.15..26.50, Y381.50..442.50 and Z316.70..345.00 mm. Its nominal inlet is
at `(0,381.5,326.1)` and outlet at `(0,442.5,326.1)` mm, using the reference's
port convention. This candidate clears the pump by 4.57 mm, ASSE by 9.98 mm
and the ordinary ceiling underside by 1 mm. It requires no roof relief at
this pose.

[The frozen mesh source record](parts/digiten-flow.source.json) identifies its
reference and source hashes. Placement is open for review. A back-bottom
carrier from the cold-core roof is proposed; retaining details and complete
carbonated-water connections are pending. The flexible pigtail is omitted.

## Arrangement highlighting

One whole-arrangement camera supports Assembly quadrant, Latest changes and
Normal highlights. Changing highlight preserves the camera. Native walls,
V-B's support and the integral V-A/V-K/relay support overlays remain visible;
the roof is hidden for interior inspection.

[assembly-ownership.json](assembly-ownership.json) follows mounting parents.
The funnel/frame, drain and Y-A/Y-B fittings belong to front-top. Walls,
V-A/V-K, relays and rear fittings belong to back-top. Cold-core equipment,
V-B and its wall, the PCB, pump and Mean Well belong to back-bottom. The
flow-meter carrier is proposed as back-bottom. No
front-bottom equipment is represented in this above-core scene. Part details
identify attachment bases and unfinished production integration.

Latest changes compares the selected geometry and poses against the explicit
[highlight baseline](highlight-baseline.json). Mesh signatures use decompressed
geometry and normalized poses, independently of compressed archive timestamps.

Rebuild the support through the shared native CAD queue, then query and package
the selected scene manually:

```sh
PYTHONPATH=. tmp/takeover/cadq "V-B cold-core roof support" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/build_support.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/study.py --check
python3 hardware/manifold-layout/studies/funnel-gate/viewer.py hardware/manifold-layout/studies/funnel-gate/out/whole-arrangement.html
```

No command is added to the build or commit path. Production enclosure geometry
and complete harness routes retain their separate scope.
