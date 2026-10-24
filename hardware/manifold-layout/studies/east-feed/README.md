# Under-head V-A feed and centered PCB

V-A supplies clean water to **Y-A port1**, the flavor manifold's shared-source
tee. That junction connects the water and funnel gates to the two channel
selects. Its retained production mouth is `(22.35,166.24,270.675)` mm, facing
upward. A trimmed NeoFit stem elbow seats in that mouth, with its female
socket facing the arriving straight tube.

The V-A outlet stem elbow points east. The 1/4-inch tube passes beneath the
pump head, rises beyond the head and enters the purchased, scanned JG
PP0308E union elbow. One straight, level tube connects that elbow to the
Y-A stem elbow. Both ends enter their sockets squarely. The route follows
the [physical head-side passage photographs](../../../reference/g-ganen-pump/under-head-tube/physical-observations.json).
The G Ganen reference and water-group positions are retained.

The [route](route.json) records the two smooth centerline spans, fitting poses,
actual Y-A datum and nominal socket engagements. Its minimum sampled bend
radius is 15.64 mm. The selected exterior-mesh query finds 2.09 mm to the
pump and a nominal 1.425 mm from the tube underside to the plain cold-core
crown. The straight downstream tube clears the PCB by 31.76 mm and the
funnel frame by 20.00 mm. These are geometry results, not received-part
measurement accuracy or physical installation acceptance. The JG scan does
not establish insertion depth; the 15.7 mm engagement is a family-based
layout estimate.

## PCB placement

The PCB is flat at underside Z257, with its long dimension across X and J10
facing east. Its footprint is X−88..2.816 and Y195.395..268.195 mm. The north
and south ends each have 13.095 mm to V-A's mounting support fore face at
Y281.290 and the cold-core fore edge at Y182.300. The ideal west wall is
10.5 mm from the board edge and 18.97 mm from the west-side J11 housing.

Carried mating plugs and local lead envelopes participate in the fit query;
harness drawings are omitted. Their westmost envelope is 10.32 mm inside
the ideal wall. JST pull sweeps clear the selected stationary geometry.
Long vertical J10 screwdriver service requires funnel/frame removal.
The complete installed harness and PCB retention remain separate work.

## Ordered inline water regulators

The working choice is the purchased [YZMSZ fixed 0.3 MPa regulator](../../../reference/yzmsz-water-regulator/README.md),
with an explicitly estimated 67 × Ø27 mm exterior and native 1/4-inch OD
push-connects. Its nominal output is 43.5 psi. The alternative
[Frizzlife PRV01](../../../reference/frizzlife-prv01/README.md) has published
66.802 × Ø26.67 mm overall dimensions, native 1/4-inch OD push-connects and
a manufacturer-stated 50–60 psi regulated range. The reference folders contain
native STEP models, frozen meshes, source links, dimensions and estimates.

Both are arranged on the same straight westward path from the tee to V-A.
The available mouth-to-mouth gap is 74.5 mm. Nominal exposed inlet tube is
7.5 mm with YZMSZ and 7.698 mm with Frizzlife; the outlet connects to V-A's
existing elbow through a concealed tube. Socket engagements are included
as layout estimates. YZMSZ's working size interval is 60–74 mm long and
24–30 mm in diameter, inferred from photographs rather than a dimensioned
manufacturer drawing. The nominal fit is the basis for this candidate.

The study roof has a shallow regulator recess up to Z349, leaving 6 mm of
roof stock. The nominal regulator-to-roof gaps are 1.12 mm for YZMSZ and
1.29 mm for Frizzlife. Existing ASSE and CO2 recesses retain 3 mm stock.
The [roof plan](ceiling-plan.json) and native STEP are specific to this
arrangement study; the production shell is not migrated here.

Both complete selected queries report no unrelated intersections. The
[working scene](study.json) and [Frizzlife alternative](alternative.json)
record their poses and results. The free-space comparison includes the
Yetaha reference and both ordered inline regulators. No NPT adapter chain
is included in either selected inline choice.

Only Y-A is added as destination context. Its mesh is the existing frozen
Y-B tee mirrored across X0 with reversed winding. The mouth datum comes
from `manifold_layout.port('Y-A','front')` carried into the enclosure frame;
`fluid-topology.md` segment3 defines the V-A-O → Y-A1 connection. V-B and
reservoir routes, final WAGO positions and production-pack migration remain
deferred. Valve seats, relays, rear fittings and the gas path retain their
wall-supported poses.

Rebuild the study roof manually through the shared CAD queue, then query
the two selected arrangements:

```sh
PYTHONPATH=. tmp/takeover/cadq "Inline water regulator roof" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/ceiling-fit/ceiling.py --plan hardware/manifold-layout/studies/east-feed/ceiling-plan.json --out hardware/manifold-layout/studies/east-feed/parts/east-feed-ceiling
tools/cad-venv/bin/python hardware/manifold-layout/studies/east-feed/study.py --check
```
