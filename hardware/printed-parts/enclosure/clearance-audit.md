# Enclosure fit clearances

The enclosure assembly and its printed accessories use the shared allowances in
[fits.py](/hardware/printed-parts/cadlib/fits.py). This page describes the source geometry and
its verification coverage. It does not certify dimensions measured from a physical print.
The faucet has its own completed fit tests and is outside this adjustment.

The allowances reserve room for rough or oozed printed material beyond the nominal CAD
face. Seating under gravity or screw load uses that room too. A modeled gap does not
assume an equally large empty space after printing.

| Mating surface | Ordinary clearance | Extra for each supported face |
|---|---:|---:|
| Static assembly | 0.15 mm | 0.25 mm |
| Sliding or moving service fit | 0.25 mm: 0.15 base + 0.10 sliding | 0.25 mm |

A gap with one supported face therefore has 0.40 mm for static assembly or 0.50 mm for
sliding. If both opposing printed faces require support, their two 0.25 mm allowances add
to the same gap. Each supported face is counted once, on that face or its mate.

Sliding describes a joint whose mating surfaces constrain movement and whose function
requires an easy slide. It includes the pump cartridge, enclosure assembly slides and
spring-driven hook engagement; travel length alone does not decide the category. The
hand-flexed flat-wing nameplate uses static clearances.
For the enclosure's Y assembly motion, Y-normal end faces approach head-on and use
0.15 mm static clearance. X/Z faces that slide past their mates use 0.25 mm running
clearance, as do sloping laps with tangential motion. The rail ends retain a local
0.25 mm gap, conservatively above the 0.15 mm head-on minimum.

The horizontal-wing nameplate gives each wing
tip **0.25 mm of X clearance** at the centered position. This is a local
narrow-slot relief of 0.10 mm beyond the body's shared static X fit gap. The body locates X
at 0.15 mm per side; the wing tips retain 0.10 mm at the extreme of body travel.
These tips need capture, not a second X locating fit. This trial allowance does
not add to every face or establish a low-force rule.

The [nameplate receiver trial](nameplate/horizontal-wing-trial/README.md) uses
a separate 0.45 mm total thickness gap above its 1.68 mm seated wing. This local
fit combines ordinary body X clearance with local wing Y relief and a fixed seating floor. The retaining face and
entry bevel define a 2.13 mm slot with 1.23 mm of stock over its flat bearing.
The physical comparison uses the existing nameplate; the shared static rule
remains unchanged.

The [face-up display receiver](display-cover/face-up-trial/README.md) uses
0.30 mm per side around the body's full-depth X seating pocket. The wing tips
have 0.55 mm centered clearance and retain 0.25 mm at maximum sideways travel.
Their pocket geometry is held to isolate the main-body X fit.
Its wing-thickness gap is 0.60 mm: 0.15 static, 0.25 for one supported roof,
and 0.20 local pinching-test relief. That thickness direction is display-local
Z, corresponding to nameplate Y. Body Y and wing end gaps remain 0.15 mm each.
These are local fit trials with the cover's seating datum fixed.

**Low-force clearance for rough overhang surfaces involved** uses a working addition
of **0.50 mm on the identified moving gap**, after its ordinary sliding and rough-face
allowances. Apply it only where the available force is small, such as spring return or
leaf spring-back. It is not a blanket addition to every side of a part or every sliding
fit. Each interface requires its own physical motion and retention check.

| Low-force interface | Gap accounting | Nominal result |
|---|---|---:|
| Display hook, two rough mating faces | 0.25 sliding + 0.25 + 0.25 rough faces + 0.50 low-force | 1.25 mm working target |
| Tee-carrier roof, one rough mating face | 0.25 sliding + 0.25 rough roof + 0.50 low-force | 1.00 mm |
| Tee-carrier floor | 0.25 sliding | 0.25 mm |

The selected display cover has a measured-in-CAD 1.23 mm hook-to-catch gap and a
passing physical fit. Its 0.75 mm designation is an arm-length increment, not an
extra clearance rule. The 1.25 mm working target approximates that accepted gap;
the accepted cover remains at 1.23 mm. See its
[physical record](display-cover/physical-acceptance.json).

Opposite-side clearances do not collapse into one allowance: the tee carrier's
1.00 mm roof gap plus 0.25 mm floor gap gives 1.25 mm total vertical travel.
Two rough faces of the same gap are distinct from two gaps on opposite sides of a part.

Ordinary clearance is measured normal to the mating surface. A circular fit adds twice its
radial clearance to the diameter. A 45° sliding lap uses the corresponding axial projection.
The bridge allowance follows the part's print direction: a supported cavity crown retreats
0.25 mm toward print-up without moving its nominal axis or its opposite locating edge.
Surrounding stock grows where that retreat needs backing. Vertical holes, upward-open seats,
bedded faces and support-free slopes do not acquire a bridge allowance merely because they
belong to a supported part.
A face printed against the build plate keeps its base allowance; the extra 0.25 mm
is for a supported overhang's retained finish.

Printed screw-clamping faces, bearing planes, seating shoulders and stroke stops
receive the applicable allowances above. Locating a face from a datum does not waive
its clearance or supported-face allowance. Manufacturer heat-set pilot cores
retain their prescribed diameter; supported horizontal pilots receive crown relief only.
Tube routing space, tool access, electrical isolation space and structural thickness are not
ordinary mating clearances.

The [enclosure geometry and support policy](enclosure/README.md#support-removal-strategy)
define the working faces. The [cold-core fit coverage](../cold-core/fit-clearances.md)
records the separate printed cold-core components and their print orientations.

## Coverage in the source

Front-top, front-bottom and back-bottom print with machine +Z as print-up. Back-top and the
pump cap print with machine −Z as print-up. The pump cartridge uses +Z.
The same clearance policy follows these orientations rather than the assembled appearance.

| Interface family | Source coverage |
|---|---|
| Enclosure quadrant seams | Y-normal head-on closure faces use 0.15 mm static clearance. Tangential sliding tongues, scarf laps, rail channels and pin passages use 0.25 mm running clearance. Both broad Z shoulders use 0.25 mm: front-top's mating face is bedded, and the rear shoulder pair looks print-up. The separate front catch has one supported face and retains 0.50 mm; the rear catch has two and retains 0.75 mm. |
| Pump cartridge and cap | Bay, fixed-bulkhead and casing passages use their static or sliding allowances. Supported shoulders, recesses and cap screw-head seats carry bridge relief with backing retained. Bracket and floor-bearing faces are included in the printed-fit policy. |
| Display | The glass cavity is 113.8 × 77.3 mm and the PCB passage is 106.3 × 69.3 mm, providing 0.15 mm per side around their nominal envelopes. The glass seat is 4 mm deep. The deeper cover land has its own 0.15 mm inner-wall clearance. The facet's 45° walls and insert axes are support-free; the PCB opening's start ridge is carried by the solid rib. |
| Rear ports and accessories | C14 flange/shroud and keystone body pockets use 0.15 mm static clearance. Nameplate and bulkhead-ring pockets use the shared static allowance; supported pocket edges receive directional relief. The dedicated 4 mm OVER uses a 15.3 mm rear-wall bore for its M15 barrel. |
| Hardware supports | Wago pocket roofs and tabs, supported tube/body-seat crowns, anchor tie cavities, ASSE seats and the PRV chase receive their applicable bridge allowance. The surrounding towers and ribs retain their working sections. |
| Fasteners | M3 through clearance is Ø3.3 mm and nominal Ø5.5 mm heads receive Ø5.8 mm counterbores. Horizontal supported shank/insert crowns and supported head seats receive directional relief; bedded vertical insert openings retain the prescribed pilot. |
| Other enclosure accessories | Display cover, gasket, nameplate, bulkhead rings and collet press retain their stated print orientations. Supported head seats are treated locally; flat bedded plates and support-free tools do not receive blanket offsets. |
| Cold-core printed parts | Foam shell/caps, reservoirs/caps, copper plugs, PRV shroud and reed bridge follow the [component coverage](../cold-core/fit-clearances.md). Copper-plug tabs have 0.50 mm wall clearance and their opposite channel faces have 0.25 mm running clearance. |

## Enclosure dimensions in the source

These are nominal source dimensions. The retained native readings below apply only
to the geometry identified by their input hashes.

| Location | Modeled dimensions and allowance |
|---|---|
| Lower seam blocks and handholds | Lower screw axes are at X±98.25, 9.25 mm from the exterior. The blocks reach 13.75 mm from `interior_x` and stop 0.25 mm short of the core. Each complete 3 mm blind handhold wall spans 90.75 to 93.75 mm from the centreline, 0.25 mm outboard of the core flank. |
| Lower stack faces | Front-bottom's first block starts at Z66.2. Its top block ends at Z174.8; back-top's hub starts at Z175.05, leaving 0.25 mm. The supported middle gaps retain 0.50 mm. |
| Upper stack faces | Upper axes are at X±98, 9.5 mm from the exterior. Front-top's insert mouth is Z299.65 and back-top's block starts at Z299.9, leaving 0.25 mm. |
| Screw-head pockets | Each 8.4 mm deep pocket includes 0.40 mm at the supported washer seat: 0.15 static + 0.25 supported. Floors are Z37.65 and Z346.60. Nominal metal poses retain the 2 mm head recess. |
| Funnel front rail | Frame foot Z306.9 to receiver underside Z307.4 gives 0.50 mm: 0.25 running + 0.25 supported. |
| Whole core pocket and hold-downs | The pocket follows the rounded core plan with 0.25 mm around it and extends from Z−0.25 to Z253.65. The floor retains 5.75 mm. The complete hold-down profile stands 0.25 mm above the core crown. |
| PRV chase beside core | Lip X−90.75 to core flank X−90.5 gives 0.25 mm. |

The lower washer's separate 35° entry moves with the lower screw axis and complete
inner wall, preserving their relative entry geometry. Practical ease remains
unqualified. Modeled block, floor, bracket and washer-seat gaps reserve room for
printed material; they are not guaranteed empty spaces after assembly or tightening.

## Physical observations

Derek's PET-GF tests show that clean removal of a tree support and its dense interface does
not necessarily remove the loose roof or bridge strands left on the supported model face.
Those strands can remain attached at their edges and reduce a fitted opening. Peeling them
away can bring the measured opening back to the designed size. The geometric allowance is
room for that retained surface finish.

In the overnight numbered test, samples **1, 2, 7, 8, 9, 10, 12 and 16** had the cleanest
support removal while retaining the roof strands. Derek ranked **10, then 16, then 8** as the
cleanest of that group. The retained strands still felt looser than the next model layer.
In the four-sample test, B and C were not visibly distinguishable despite C's removed end
connections; D released some complete strips including their edges, but most remained.
These are removal observations, not a new measurement of the required clearance.

Derek also reports that the enclosure display fits well in the tested print, and that an
RJ11 jack fits in the tested enclosure back-top. Those observations are retained alongside
the nominal hardware envelopes used to size the CAD pockets.

## Verification

The [current enclosure fit review](enclosure/y-seam-fit-review.json) binds the
current source and native artifact hashes. Its 111 finite planar pairs meet the
applicable allowances, with zero deficits above the 0.00001 mm native tolerance.
It records all 17 corrected contact patches in six interface families, the four
0.40 mm washer-seat allowances and complete 3 mm backing, M5 insert backing,
the full-height core pocket and lower-corner separation, and a positive-separation
proof for the hub passing the unchanged PRV route under pure Y motion.
The record does not certify curved/nonparallel contacts, every internal cold-core
interface or physical support finish. Those scope limits do not waive any modeled
clearance requirement.

The [retained quadrant reading](mating-clearance-check.json) records opposing planar
faces from those four identified enclosure STEPs: 59 passing patches and 11 passing
local probes. Its measured local gaps include:

| Intersection | Locations | Gap | Accounting |
|---|---:|---:|---|
| Handhold backing tab beneath the front roof | 2 | 0.50 mm in Z | 0.25 running + 0.25 rough roof |
| Floor scarf beside the handhold backing wall | 2 | 0.25 mm in X | Running, vertical faces |
| Front rail entrance behind the tee wall | 2 | 0.25 mm in Y | Local gap above the 0.15 mm head-on minimum |
| Vent-chase split above the back-bottom rim | 1 | 0.25 mm in Z | Running; both faces print upward |
| Closed-end rail blocks and top-piece foot ends | 4 | 0.25 mm in Y | Local gap above the 0.15 mm head-on minimum; blocks bound overtravel |

The check requires the applicable static or running clearance plus each supported-face
allowance on every measured printed mating patch, including screw-clamping faces,
Y closure ends, main Z seating shoulders and rail ends. Its bed-face classification uses
each part's actual minimum Z for +Z printing or maximum Z for −Z printing.
Zero-clearance contacts fail this requirement.
Each closed-end block retains 3.75 mm of length. A retained reading's input hashes
and acceptance criteria define its scope; its status alone does not establish
compliance with the requirements on this page.

Run `tools/cad-venv/bin/python hardware/scripts/check_enclosure_mating_clearance.py`
after materializing the quadrants. Its scope is parallel planar patches larger
than 0.05 mm² within 0.751 mm of a mate, plus explicit surface probes at the eleven
intersections above. Curved and nonparallel contacts, full insertion sweeps,
accessories and physical support finish need their separate checks.

Feature checks read supported relief on the actual print-up side, ordinary clearance on the
opposite and lateral faces, retained wall sections, and clearance at seating planes. Enclosure
assembly checks also cover whole-part intersections, cap/cartridge withdrawal, hardware
envelopes, and seam capture. Zero whole-part overlap does not establish positive
clearance between printed mating faces.

[check_copper_plug_clearance.py](/hardware/scripts/check_copper_plug_clearance.py) reads the
finished standalone front-top, foam assembly and both copper-plug STEPs. It places the plugs
through the production transforms and writes a focused, hashed reading beside the plugs.
Run it after those outputs have been regenerated:

```sh
tools/cad-venv/bin/python hardware/scripts/check_copper_plug_clearance.py
```

The [focused reading](../cold-core/copper-plugs/clearance-check.json) records its input hashes,
scope and pass/fail result. Use those hashes when interpreting its measurements. The enclosure
and cold-core scorecards carry the results for the geometry they built; neither the source
values on this page nor a retained reading of another build establish the final printed fit.
