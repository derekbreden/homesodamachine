# Under-head V-A feed and centered PCB

V-A supplies clean water to **Y-A port1**, the flavor manifold's shared-source
tee. That junction connects the water and funnel gates to the two channel
selects. Its retained production mouth is `(22.35,166.24,270.675)` mm, facing
upward. A trimmed NeoFit stem elbow seats in that mouth, with its female
socket facing aft toward the arriving tube.

The V-A outlet stem elbow points east. The 1/4-inch tube passes beneath the
pump head and enters the purchased, scanned JG PP0308E union elbow lying
flat on the core beneath the head. The union elbow's axis intersection is
`(33.1317,309.1355,261.6)` mm. Its inlet faces west (−X) and its outlet faces
fore (−Y); both axes are horizontal. A shallow aft offset in the incoming
tube places its socket behind the lower pressure-switch block. One direct
tube rises gently 15.12 mm to the Y-A stem elbow. Both tube ends enter their
sockets squarely. The arrangement follows the received pump's
[flat-elbow photographs](../../../reference/g-ganen-pump/under-head-tube/flat-elbow-observation.json)
and [tube-passage photographs](../../../reference/g-ganen-pump/under-head-tube/physical-observations.json).
Pump and water-group positions are retained.

The [route](route.json) records the two smooth centerline spans, fitting poses,
actual Y-A datum and nominal socket engagements. The incoming and onward
spans have minimum sampled radii of 61.75 mm and 95.74 mm. The union elbow's
underside is at nominal Z253.437, effectively resting at the core's Z253.4
crown. The physical photographs establish the flat arrangement; this nominal
position does not supply a clearance allowance. The JG scan does not establish
insertion depth; the 15.7 mm engagement is a family-based layout estimate.

The pump reference represents the rigid underside measured in two raw scans;
flexible lead loops are separate from that rigid envelope. The corrected
native exterior supplies the study's pump body while the three installed feet
and independently positioned fourth slider retain their study poses. The
[frozen study mesh and its sources](parts/pump-under-head-source.json) record
that geometry and the exact native-to-enclosure transform.

The selected exterior query reports no unrelated intersections with either
ordered regulator. Nominal elbow gaps are 0.19 mm to the corrected rigid pump,
4.04 mm to the existing pump-side elbow and 27.78 mm to V-K. The onward tube
clears the PCB by 19.46 mm and the funnel frame by 20.00 mm. These mesh
distances are layout results; the photographs establish the received-part
fit and do not measure these installed clearances.

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
