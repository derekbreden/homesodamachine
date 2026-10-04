# Vent routing and leak collection geometry

This geometry study proposes an external ASSE vent route and a front-removable
catch drawer beneath the appliance, with an independent load frame. The comparison
also includes a local collector beside the machine and a lift-off pan beneath its
footprint. The production enclosure is unchanged.

The lift-off pan is separate from the enclosure. The appliance rests on
pads inside it, so removing this candidate pan requires lifting the machine.
It is not an independently sliding service drawer. Its rear rim extends above
the base underside and cannot pass beneath that base during withdrawal. A
service drawer needs a separate appliance load path and full rim clearance.

## Front-removable drawer

The appliance stays on a fixed U-frame while the tray moves forward. Two side
webs and a rear tie carry 2 mm bearing lips beneath the case's side edges. The
front is open. A 42 × 70 mm opening through the west lip lets the vent discharge
fall into the drawer. The drawer's lowest flood rim is at Z = −8.5 mm, 0.5 mm
below the lips' undersides. Its floor is 2 mm thick. The nominal vertical stack
therefore leaves wet depth equal to added height minus 4.5 mm.

| Added height | Installed height, including cover | Wet depth | Static net volume to rim |
| --- | ---: | ---: | ---: |
| 8 mm | 372 mm | 3.5 mm | 446 mL |
| 10 mm | 374 mm | 5.5 mm | 712 mL |
| 12 mm | 376 mm | 7.5 mm | 978 mL |
| 16 mm | 380 mm | 11.5 mm | 1,510 mL |

The initial interactive review uses +10 mm. The +8 mm option leaves only 1.8 mm
of wet depth above a bare 1.7 mm sensing band. A +5 mm version would leave 0.5 mm
wet depth and does not fit the band. Band thickness is not a verified trip depth.
The calculation subtracts the five moving probe envelopes; all water is below
the appliance and frame lips, so neither displaces this cavity.

The drawer is rectangular across the full west receiver width. An irregular
receiver ear would sweep through a stationary west frame rail during withdrawal.
The frame and handle occupy approximately 288.6 × 512.5 mm in the closed state;
the drawer alone is 280.6 mm wide. Full removal takes 485 mm of forward travel.
The tray bottom rests and slides directly on the cabinet floor. No skid, roller,
adhesive or tolerance allowance is hidden in the height figures.

The frame's bearing lips, side webs and case support are geometry proposals.
The broad west shelf has approximately 61 mm of free span; its 2 mm thickness
and 0.5 mm drawer clearance do not establish load capacity or resistance to
binding from deflection. A formed metal frame or stiffening above the shelf
needs its own load-path design. Underside ribs consume drawer clearance.

The main tray, handle, sensing strips and presence target move together. The
internal floor witness, frame, tube and presence-switch envelope stay fixed.
The fixed outlet's full OD remains above the moving water opening for about
95.7 mm of withdrawal. The comparison marks loss of that receiving opening at
95.5 mm. Water supply and dispensing need inhibition as soon as service begins;
presence sensing alone does not drain stored pressurized water. Sensor lead
retention, a dry front disconnect, drawer retention, a drain/purge procedure and
service discharge handling remain unresolved.

Capacities are level, static and zero-freeboard. For scale, an ideal rectangular
basin tilted 1° fore/aft reaches first spill at approximately 97, 240 and 446 mL
gross for the +8, +10 and +12 mm versions, before sensor displacement. The
viewer does not simulate tilt, water motion or splashing during withdrawal.

The interactive comparison uses named, tessellated native assembly bodies and
parametric proposal solids. Its controls select collection geometry, overall
height and close views of the vent, outlet and base. Water represents the static
void filled to the rim, with installed solids, supports and sensor bands removed.
It is not a flow or splash simulation.

## Proposed route

The replacement clear hose seats continuously over the existing ASSE vent barb,
follows two 30 mm centreline-radius bends separated by a 5 mm tangent, and runs
down outside the west wall. The nominal hose is 9.525 mm OD and 6.35 mm ID.
Two open saddles locate the downcomer. Its end remains open above the collector's
flood rim. The 25.4 mm rim-to-outlet air gap is a review assumption, not an approval
or a requirement established for this device.

The route requires a local downward extension to the existing pan opening. A flush
closure envelope fills the unused original slot. The red display solid marks
material to remove; it is excluded from proposal STEP exports. Original case
surfaces remain display context. Attachment, sealing, the hose's permitted bend
radius and vent-extension hydraulics are unresolved.

The source vent datum is the end of the modeled PVC stub, not the brass barb.
The proposal replaces that stub with the upstream sleeve of the continuous hose.
Its sleeve bore is a geometry envelope for the barb fit and transition;
it does not qualify stretch, clamping or the actual hose bore.

The lift-off pan has a 225 × 485 mm main footprint and a connected west receiver
under the external downcomer. Its complete width is approximately 281 mm.
The receiver extends about 61 mm past the case's west face, exceeding the current
40 mm side allowance. The comparison reports approximately 316 mm cabinet width
to retain 40 mm on the other side. That is a packaging allowance, not an airflow
or cabinet installation acceptance.

## Collection alternatives

All lift-off pan variants have a 2 mm floor, a flood rim at world Z = −1 mm and
different clearances beneath the appliance base. Increasing clearance adds
capacity without raising that rim relative to the appliance. The inside-floor
datum is Z = 0; the existing base underside is Z = −6 mm. The current nominal
case is 215 × 466.3 × 361 mm. Its existing funnel cover adds 3 mm above the roof;
the comparison reports installed height including that cover. The upper pan's
pull face brings the current case-plus-pan width to approximately 221 mm.

| Collection | Added appliance height | Clear gap below base | Wet depth | Coverage |
| --- | ---: | ---: | ---: | --- |
| Local collector | 0 mm | Not beneath base | 60 mm | Modeled ASSE vent discharge |
| Deeper local collector | 0 mm | Not beneath base | 100 mm | Modeled ASSE vent discharge |
| Full tray | 5 mm | 3 mm | 8 mm | Footprint plus vent receiver |
| Full tray | 8 mm | 6 mm | 11 mm | Footprint plus vent receiver |
| Full tray | 12 mm | 10 mm | 15 mm | Footprint plus vent receiver |
| Full tray | 16 mm | 14 mm | 19 mm | Footprint plus vent receiver |

The local collector is 50 × 120 mm externally and has a 2 mm floor and walls.
It occupies cabinet-floor space beside the machine, so it adds no appliance
height. It does not collect other appliance leaks or leaks in upstream plumbing.

The full tray uses eight proposed support pads beneath existing floor stations
and the cold-core area. Water can pass around the pads. Four 8 × 1.7 mm sensing
band envelopes run beneath the base near its perimeter; another lies in the
receiver. The smallest clearance leaves 1.3 mm above a bare band. Adhesive or
retainer geometry, lead routing and electrode exposure need resolution before
the band placement is a build specification.

Both alternatives include one additional 8 × 50 × 1.7 mm witness band on the
existing internal floor, aft of the MQ-6. Native Boolean checks against the
frozen assembly found no positive-volume clash at X −97.5…−89.5,
Y 80…130 and Z 0…1.7 mm. It can witness floor water without waiting for water
to reach the lower tray. Placement does not establish that every internal leak
reaches this band; electrode exposure, retention and leads remain unresolved.

The full-tray rim remains 4 mm below the saved MQ-6's lowest solid. This is a
static geometric separation. It supplies no protection claim for splashing,
wicking, tilt, external floor water or a blocked/overflowing collector. A full
tray also does not establish that leaks leaving high side openings land inside it.

## Capacity and design boundary

[Study metadata](study-metadata.json) and [geometry validation](geometry-validation.json)
record maximum static capacities, the displacement calculation and dimensions
for each preset. For the lift-off pan, a plan-area × wet-depth calculation
overstates storage because the enclosure base occupies much of that depth.
Its calculation subtracts the frozen saved STEP solids, support pads and bands
from the actual connected cavity. The front drawer's water is below the base;
its calculation subtracts only the moving probe envelopes.
Reported capacities are level and have zero freeboard.

The lower collector is useful only alongside prompt sensing and a master supply
shutoff upstream of the appliance's vulnerable water path. Neither is implemented
by this geometry. A capacity requirement must include releasable stored water,
incoming flow during detection and closure, drainable lines, and an allowance
for freeboard and installation tilt. The carbonator's nominal high-level gross
volume is approximately 992 mL before internal displacement. It is relevant to
whole-appliance leak storage; it does not imply that this amount drains through
the ASSE vent. The study does not establish a maximum vent-discharge rate.

The 2 mm pan floor and pads are packaging proposals, not qualified load paths
or watertight manufacturing specifications. The 485 mm continuous pan requires
a manufacturing plan; splitting it introduces a joint that needs sealing.
No print readiness, water hold, support strength or life result is asserted.
Existing accepted enclosure results retain the scope in the
[physical-evidence register](../../hardware/mechanical-qualification/README.md).

The intended lower receiver preserves an open, inspectable discharge path and
keeps the outlet above its flood rim. [ASSE 1022-2023, §4.2.4](https://codes.iapmo.org/epubs/standards/ASSE/ASSE-1022-2023e1/)
requires an approved air-gapped termination with visible discharge for the sight
tube; the standard does not establish this proposed extension's hydraulic
performance. The [manufacturer's device description](https://www.andersonbrass.com/asse-1022-backflow-preventers)
explains the vent's exhaust function. Sensors alone do not provide a discharge
receiver or establish compliance.

## Source and review scope

[Context provenance](context-provenance.json) identifies the frozen STEP, saved
facts, source state at capture, display omissions and mesh processing. Proposal
capacity and context use the same frozen STEP. The frozen refreshed facts agree
with the saved STEP, scorecard and traced source digest at capture. Selected
hardware uses the matching source-stamped mesh sidecar; the case and outer core
use native STEP tessellations. Native source bodies determine displacement;
display triangulation is not used for acceptance.
The display omits decorative flutes, front-top, pump-cap and internal cold-core
equipment. Routing faces and outer core bodies remain native tessellations.

The saved appliance appears as reference context. Proposed STEP exports contain
the new collector, supports or fixed frame, sensor envelopes, hose, clips and
slot closure. Drawer exports include presence-switch and target envelopes.
They exclude water and reference cutters. The frozen source and generated STEP
files are local artifacts; the compact display packs preserve the review scene
in this directory.

## Regenerate

```sh
tools/cad-venv/bin/python future/leak-containment-study/build_context.py
tools/cad-venv/bin/python future/leak-containment-study/build_study.py
python3 future/leak-containment-study/compose.py /absolute/output/leak-containment.html
```

`build_context.py` freezes a source snapshot and exports only study files.
`build_study.py` uses that snapshot and writes proposal STEP files plus the
display pack. `compose.py` rejects a context/capacity snapshot mismatch and
fragments at or above 1 MB. [geometry.py](geometry.py) exposes the route, gap,
collector depth and air gap as parameters for subsequent geometry review.
[drawer.py](drawer.py) adds the fixed frame, moving tray and withdrawal checks.

`build_study.py --reuse-water` avoids importing the large appliance STEP again
for display-only revisions. It checks the frozen STEP digest, all wetted
parameters and parts, and that the internal witness remains outside the water
void before retaining the verified native-subtraction capacity and water mesh.
