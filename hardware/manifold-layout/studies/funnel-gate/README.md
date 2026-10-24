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
front, west of its mounting wall. Their fold plane rises 20 degrees; the
valve stays aligned with the enclosure axes. The return follows one straight
fore run and a formed U into Y-B. Five added elbows connect the B chain;
exposed tubing totals 208.80 mm. The U has a minimum modeled centerline
radius of 20.91 mm. No route crosses above the west PCB.

V-A's fore tube runs directly from the under-head elbow to Y-A's compact
return. Y-A has a stem elbow, a union on a concealed tube and a returning stem
elbow. The union-to-stem fold drops 30 degrees. The two Y-tee stem outlets face
fore, clocked 7.5 degrees outward to clear the retained drain cradle by 0.66 mm.
The V-A fore tube has a minimum modeled centerline radius of 53.91 mm and
15.56 mm to the board.

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
lead intersections. V-B clears the funnel frame by 10.39 mm. The nested outlet
clears the pump by 1.27 mm and its mounting wall by 1.38 mm. The return tube
passes Y-A's union by 0.83 mm; the outlet elbow clears the native right wall
by 0.91 mm. The shortened drain stem clears the cradle by 0.76 mm. These are
nominal mesh gaps, with purchased-part dimensions and socket depths partly
estimated.

All ten 6 mm JST housing withdrawal sweeps and all ten 30 mm vertical columns
above the housing outlines clear with the funnel/frame installed and the roof
removed. These are nominal housing/access envelopes; finger reach and complete
harness manipulation are not modeled. Local leads are suppressed in the viewer;
installed mating housings remain visible.

## Arrangement highlighting

One whole-arrangement camera supports Assembly quadrant, Latest changes and
Normal highlights. Changing highlight preserves the camera. Native walls,
V-B's support and the integral V-A/V-K/relay support overlays remain visible;
the roof is hidden for interior inspection.

[assembly-ownership.json](assembly-ownership.json) follows mounting parents.
The funnel/frame, drain and Y-A/Y-B fittings belong to front-top. Walls,
V-A/V-K, relays and rear fittings belong to back-top. Cold-core equipment,
V-B and its wall, the PCB, pump and Mean Well belong to back-bottom. No
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
