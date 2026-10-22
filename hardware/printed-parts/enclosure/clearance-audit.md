# Enclosure fit clearances

The enclosure's PET-GF-to-PET-GF mating interfaces use the shared allowances in
[fits.py](/hardware/printed-parts/cadlib/fits.py). This page describes the source geometry and
its artifact-scoped verification coverage. The [native fit review](enclosure/y-seam-fit-review.json)
records the current measured interfaces and complete local stock. The rules determine
the required geometry between printed faces, including faces loaded by screws or gravity.

This pass is bounded to the enclosure's PET-GF-to-PET-GF interfaces. Rigid-part fits
elsewhere remain subject to the same printed-face allowances; this pass does not resolve
them. Compliant gaskets and seals use their specified installed squeeze in the compression
direction. Steel washer bearing planes retain their nominal source positions and are outside
this pass's fit assessment. The core crown remains at its Z253.4 reference; the native
review checks the enclosure pocket and hold-downs against the five external printed bodies.

An allowance is surface, not air. A printed face stands proud of its CAD face: press two
printed 1 mm parts together and they measure 2.15 mm. So 0.15 mm between two nominal faces
is a friction fit, hard to slide; sliding needs 0.25 and is still tight; an overhang's
underside sags into bumps and takes 0.25 more. Each allowance describes the surface of the
face it is on and stays on that face. It is not free space a stack can spend elsewhere, and
a body resting on a face rests on its rough surface, about where it is drawn.

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

The horizontal-wing nameplate gives each wing tip **0.30 mm of X clearance** at the
centered position: 0.15 mm body travel plus 0.15 mm static clearance. The body locates X
at 0.15 mm per side; the wing tips retain 0.15 mm at the extreme of body travel.
DATA uses the same construction. The wing tips retain their capture within the slots.

The nameplate receiver has 0.45 mm of local relief above each 1.68 mm wing and
0.15 mm static clearance beneath it, giving a 2.28 mm slot. The body back also has
0.15 mm clearance. The retaining face and entry bevel retain 1.23 mm of stock over
the flat bearing. The production station stands 0.30 mm west of the rear-field midpoint;
the hidden east backing remains 2.14 mm thick to preserve the specified 1 mm PSU margin.
Both pads carry their full ordinary backing before the 45° print-down run-out.
The DATA jack and its complete receptacle stand 0.16 mm farther inboard than the
plate's nominal back plane. The flat jack lip retains 3 mm behind the 0.15 mm
printed back gap; the required 50° swing ease has its own functional profile.
The [receiver trial](nameplate/horizontal-wing-trial/README.md) records its own source and
physical support-removal scope; it does not validate the current receiver's added back gap.

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

Opposite-side clearances do not collapse into one allowance: the identified tee-carrier trial's
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

Rigid printed screw-clamping faces, bearing planes, seating shoulders and stroke stops
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
| Enclosure quadrant seams | Y-normal head-on closure faces use 0.15 mm static clearance. Tangential sliding tongues, rail channels and pin passages use 0.25 mm running clearance; the floor tongue and the handholds' inner walls end square with the same 0.25 mm, more than the head-on closure faces keep. Both broad Z shoulders use 0.25 mm: front-top's mating face is bedded, and the rear shoulder pair looks print-up. The separate front catch has one supported face and retains 0.50 mm; the rear catch has two and retains 0.75 mm. |
| Pump cartridge and cap | PET-GF bay, bulkhead and casing interfaces use their static or sliding allowances. The receiving floor is 0.35 mm below the unchanged cartridge bed: 0.25 running + 0.10 local cavity-floor transition. Supported PET-GF shoulders and recesses receive directional relief with backing retained. |
| Rear printed receivers | Nameplate, DATA plate and bulkhead-ring backs have 0.15 mm static clearance. Supported PET-GF pocket edges receive directional relief. Normal ring backing remains 4 mm; the CO2 land retains 3 mm. The clamped barrel stack includes the 0.15 mm ring-back gap. |
| Funnel frame | Front rail receivers have 0.50 mm above the frame feet: 0.25 running + 0.25 supported receiver underside. The cradle's 2.75 mm hooks have 0.40 mm over the full 3 mm web: 0.15 static + 0.25 supported finish. Frame rail and foot stock remain at their specified sections. |
| Other rigid-part interfaces | Their fit remains unresolved by this bounded pass. Component records identify their geometry; the same rigid printed-face allowances apply. |

## Enclosure dimensions in the source

These are nominal source dimensions. The retained native readings below apply only
to the geometry identified by their input hashes.

| Location | Modeled dimensions and allowance |
|---|---|
| Lower seam blocks and handholds | Lower screw axes are at X±98.25, 9.25 mm from the exterior. The blocks reach 13.75 mm from `interior_x` and stop 0.25 mm short of the core. Each complete 3 mm blind handhold wall spans 90.75 to 93.75 mm from the centreline, 0.25 mm outboard of the core flank. |
| Lower stack faces | Back-bottom's lower knuckle stands on the handhold ceiling at Z29.25. Front-bottom's knuckle starts at Z41.453553 on an underside rising 45° aft from the seam plane Y200, over back-bottom's top at Z41.1. Front-bottom's top rises 45° inboard from Z125.95 at `interior_x`; back-bottom's upper knuckle starts at Z126.303553 and ends on the Z seam at Z160. Each sloped pair keeps 0.353553 mm in Z, 0.25 mm square to the faces. |
| Upper stack faces | Upper axes are at X±97.7, 9.8 mm from the exterior. Front-top's insert mouth is Z299.65 and back-top's block starts at Z299.9, leaving 0.25 mm. |
| Screw-head pockets | The lower opening runs 11.55 mm up from the handhold ceiling to its floor at Z40.8 and ends on the handhold inner wall's finger-facing plane; the upper runs 8 mm down from the roof to its floor at Z347. Each M5 head bears directly on its printed floor: the lower head's face stands 6.55 mm above the ceiling, the upper 3 mm inside the roof. |
| Pump receiver floor | Floor Z164.845 is 0.35 mm below the cartridge bed Z165.195. Front-top's actual bed is Z160.25, leaving 4.595 mm of floor stock. |
| Funnel front rail | Frame foot Z306.9 to receiver underside Z307.4 gives 0.50 mm: 0.25 running + 0.25 supported. |
| Core pocket and hold-downs | The pocket follows the rounded core plan with 0.25 mm around it, from the floor to Z253.65. The whole floor is one plane at Z−0.35, the core's 0.25 mm running + 0.10 mm cavity-floor transition, over a 5.65 mm slab. The complete hold-down profile stands 0.25 mm above the nominal Z253.4 crown. The native review checks finite material at both hold-foot lands and the complete 8 mm foot stock. |
| PRV chase beside core | Lip X−90.75 to core flank X−90.5 gives 0.25 mm. |

The lower washer's separate 35° entry moves with the lower screw axis and complete
inner wall, preserving their relative entry geometry. Practical ease remains
unqualified. Modeled PET-GF-to-PET-GF block, floor and bracket gaps reserve room for
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

The [native enclosure fit review](enclosure/y-seam-fit-review.json) binds nine targeted
stages to its identified artifacts. It retains every measured finite planar
patch, its normal, print direction, required allowance and actual gap, together with
complete local stock checks. The stages cover quadrants and frame, four M5 insert
hosts and four washer floors,
pump receiver, nameplate and DATA, rings, window covers, tee carrier, the 45° bedding
edge and the five external core bodies. The [cradle finish](enclosure/cradle-finish-review.json)
binds the canonical body to its measured lower-mouth candidate by native equality and
records complete local stock and capture. Its lower mouth is open aft of local Y15.5;
the forward elbow-following pocket retains 302.779 mm² of native surface. The area is
geometric pocket surface, not loaded contact. Protected upper-body and hook/leaf equality,
the unchanged frame and actual silicone preserve the identified hook gaps, webs and upper
bearing measurements. Earlier route readings remain conservative lower bounds under the
measured cradle-subset chain; their original input and model scopes are retained.
The identified physical tee carrier retains separate native stock/void and same-plane
interpretations of its 18 ranked thickness pairs, without a whole-mesh thickness pass.
The 35 insert-station readings
and 14 finished-knuckle queries remain evidence for their original artifact hashes.
The current stock-only stage does not refresh screw engagement or blind-tip reserve.
Those records do not qualify the permanent pump dock; its wall bores, keeper and
rear-support seats, flange captures and magnetic mounts have their own
[engineering record](pump-dock/README.md).

The [quadrant reading](mating-clearance-check.json) records the four current enclosure
STEP hashes and its complete finite-patch and explicit-probe results. Its measured
local gaps include:

| Intersection | Locations | Gap | Accounting |
|---|---:|---:|---|
| Handhold backing tab beneath the front roof | 2 | 0.50 mm in Z | 0.25 running + 0.25 rough roof |
| Front rail entrance behind the tee wall | 2 | 0.25 mm in Y | Local gap above the 0.15 mm head-on minimum |
| Vent-chase split above the back-bottom rim | 1 | 0.25 mm in Z | Running; both faces print upward |
| Closed-end rail blocks and top-piece foot ends | 4 | 0.25 mm in Y | Local gap above the 0.15 mm head-on minimum; blocks bound overtravel |

The check requires the applicable static or running clearance plus each supported-face
allowance on every measured PET-GF-to-PET-GF mating patch, including screw-clamping faces,
Y closure ends, main Z seating shoulders and rail ends. Its bed-face classification uses
each part's actual minimum Z for +Z printing or maximum Z for −Z printing.
Zero-clearance contacts fail this requirement.
Each closed-end block retains 3.75 mm of length. Input hashes, actual finite witnesses
and acceptance criteria define each reading's scope. The review does not establish
unmeasured curved contacts, a complete insertion sweep or physical surface finish.

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

The separate [copper-plug reading](../cold-core/copper-plugs/clearance-check.json) records its
own input hashes, scope and result. This enclosure pass does not resolve those rigid-part
fits or waive their required allowances. Neither source values nor a retained reading of
another build establish the final printed fit.
