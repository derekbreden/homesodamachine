# East water paths and west PCB

This isolated above-core arrangement has the forward water paths on the east
and the PCB on the west. V-A, its mounting seat, the upstream water group and
the photographed flat elbow under the pump head retain their established poses.
The drain elbow, stub, cradle, Y-A and Y-B retain their production datums.
WAGOs and ground placement remain deferred.

## Forward plumbing

V-B lies square on its side in the fore/east area, head east and flow fore.
Its native origin is `(40,143.29675,280.41)` mm. Its body occupies
X40..97.30, Y113.547..173.047 and Z263.66..297.16 mm. The drain turns east,
then fore directly into V-B. Its outlet turns west across the front and aft
into Y-B. Five added elbows connect the B chain; exposed tubing totals
70.86 mm. The short final tube has a minimum modeled centerline radius of
14.62 mm. No route crosses above the west PCB.

V-A's fore tube runs directly from the under-head elbow to Y-A's compact
return. Y-A has a stem elbow, a union on a concealed tube and a returning stem
elbow. The union-to-stem fold drops 30 degrees. The two Y-tee stem outlets face
fore, clocked 7.5 degrees outward to clear the retained drain cradle by 0.66 mm.
The V-A fore tube has a minimum modeled centerline radius of 53.91 mm and
15.56 mm to the board.

[route.json](route.json) records every fitting pose, tube centerline and
insertion assumption. The drain's stock stem retains 5.31 mm exposed stem to
clear the cradle, with nominal 15.7 mm receiving depth. Other stem shoulders
sit flush. Socket engagements are family-based layout estimates.

## V-B wall and mounting parent

The native [V-B support](parts/vb-frame-support.step) is one valid solid:
a 9.2 mm seat wall with four shared V69 blind sockets and the valve's port
channel, joined to a 4 mm overhead bridge at the east funnel-frame edge.
Each blind socket retains 3 mm of stock behind its floor. The entire extension
is carried by **front-top**; [mount-plan.json](mount-plan.json) fixes its
attachment and world coordinates. The geometry uses the existing
[valve-seat](../../../printed-parts/valve-seat/README.md) dimensions and retains
the scope of that part's physical fit evidence.

The wall carries V-B with the drain and Y-B as one front-top subassembly.
Its lower edge hangs above the cold core; it has no core-mounted foot.
The bridge clears the silicone funnel by 13.43 mm and V-B clears the frame
by 2.74 mm. Fusion into the production frame, installed post retention and
loads remain outside this arrangement study. PCB fasteners remain to design.

## PCB and connections

The flat board's long dimension runs fore–aft. Its footprint is
X−83..−10.200 and Y186.387..277.203 mm; underside Z257 and pin tails Z255.
It has 15.5 mm to the ideal west wall and 17.65 mm beside the west J5/J6
housings. The north/south gaps to V-A's support and the core's fore edge are
4.087 mm each. Normal local lead estimates travel with the board.

The [manual fit report](fit-report.json) has no unrelated solid-body or local
lead intersections. All ten 6 mm JST housing withdrawal sweeps and all ten
30 mm vertical columns above the housing outlines clear with the funnel/frame
installed and the roof removed. These are nominal housing/access envelopes;
finger reach and complete harness manipulation are not modeled. Local leads
are suppressed in the viewer; installed mating housings remain visible.

## Arrangement highlighting

One whole-arrangement camera supports Assembly quadrant, Latest changes and
Normal highlights. Changing highlight preserves the camera. Native walls,
V-B's support and the integral V-A/V-K/relay support overlays remain visible;
the roof is hidden for interior inspection.

[assembly-ownership.json](assembly-ownership.json) follows mounting parents.
The funnel/frame, V-B wall and complete B chain belong to front-top. Walls,
V-A/V-K, relays and rear fittings belong to back-top. Cold-core equipment,
the PCB, pump and Mean Well belong to back-bottom. No front-bottom equipment
is represented in this above-core scene. Part details identify attachment
bases and unfinished production integration.

Latest changes compares the selected geometry and poses against the explicit
[highlight baseline](highlight-baseline.json). Mesh signatures use decompressed
geometry and normalized poses, independently of compressed archive timestamps.

Rebuild the support through the shared native CAD queue, then query and package
the selected scene manually:

```sh
PYTHONPATH=. tmp/takeover/cadq "Fore east V-B frame support" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/build_support.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/funnel-gate/study.py --check
python3 hardware/manifold-layout/studies/funnel-gate/viewer.py hardware/manifold-layout/studies/funnel-gate/out/whole-arrangement.html
```

No command is added to the build or commit path. Production enclosure geometry
and complete harness routes retain their separate scope.
