# Reading The Pour

The Pour is a physical reference for the home soda machine's printed surfaces
and interfaces. Keep one assembled example for each filament and saved recipe
set. Its alternatives help select a setting to try on a particular machine
part; production dimensions and settings remain in their own source files.

Use diffuse light to compare overall finish, then grazing light to reveal layer
steps and seams. Stroke the same region in the same direction on each specimen.
For a sliding comparison, use the same tongue in each receiver. Read initial
release before handling changes it.

Write a reference ID on P's exposed **BATCH / DATE** flat and use the same ID in
a local copy of the blank [reference card](reference-card.csv). Enter one sample
per row, with filament/spool, printer/nozzle and saved project. State the setting
convention: X per side, Y per side, Z top air, support distance, layer height or
seam-gap percentage. Record initial condition separately from after-handling
feel, surface or travel. The last columns connect that reading to one setting
to try on a named part region and its recorded result. The card contains no
prefilled physical results. P's underside identifies the master as **POUR V2 /
MASTER 2026-10-11**.

The source necks carry no added lettering. Their D feet and K keepers both bear
the recipe ID: N08 uses N08D and N08K, each marked N08. Keep those three pieces
together. Sliders bear their decimal clearance, support windows their R IDs,
angle blades their A IDs, and captive shutters their decimal Z-top air. G/GR,
R6 and FH/FC are recognizable unmarked source components; their file and
assembled-model names identify them.

Essential horizontal recipe IDs and clearance numbers use Arial Bold at a
nominal 4 mm size with 0.48 mm raised relief. Side angle values use 3.6 mm bold
type aligned with their facet directions. The
[native lettering review](lettering-review.json) records emitted paths;
identifiers are recognizable in its overlays for all 69 raised marking windows
and both recessed underside identities. Physical readability is unrecorded.

## Read a feature, choose one next setting

| Mark or feature | Read it | Setting or action to try on the named machine region |
| --- | --- | --- |
| N08, N12, N24 — 0.08 / 0.12 / 0.24 mm layers | Compare the actual tilted neck, checking its seam and a clean region separately. | Try the coarsest acceptable height on the corresponding complete curved band. |
| A08, A12, A24 — the same three heights | Compare the facet closest to the part's slope and its matching curve direction. | Try that height in the corresponding print orientation and local show band. |
| NR00, NR05, NR15 — regular gaps 0 / 5 / 15% | Feel for a ridge, groove or open join; inspect the nearby wall. | Try one regular-gap value on the complete part while keeping its other seam settings fixed. |
| NS00, NS10, NS20 — scarf gaps 0 / 10 / 20% | Compare the curved join and any broad trough or disturbed finish around it. | Try one scarf-gap value with the remaining scarf settings held fixed. |
| S05, S15, S25, S35, S45 — X air 0.05 / 0.15 / 0.25 / 0.35 / 0.45 mm per side | Find the smallest lane with full hand travel and play suitable for the intended joint. | Try that lateral allowance on the specific moving interface, retaining its own roof/floor allowances. |
| Q24, Q48, Q72 — Z top air 0.24 / 0.48 / 0.72 mm | Record free off bed, gently freed at the handle, or fused; then travel, capture and surface damage. | Try one Z-top value on a fresh captive module with transverse Y and lower Z air held fixed. |
| R30, R45, R60 — requested support distance 0.30 / 0.45 / 0.60 mm | Compare removal and the remaining roof strands and continuity. | Try one top support distance on the affected supported ceiling, recording its emitted gap. |
| G, GR — complete grip strip and receiver | Compare full-span bowing, recovery and wing seating in this material. | Try a filament or print-recipe candidate on the full grip interface, preserving the wing section and span. |
| R6 — source expanding and top rounds | Compare the bed-start transition, retained curve and fine top shoulder. | Use its local wall/layer recipe on the corresponding expanding show round; inspect its fresh bead overlap and support contacts. |
| H fluted apron | Read the flute depth, fade and smooth lands under grazing light and touch. | Use N/A to select one wall-height candidate for the actual enclosure field. |
| FH, FC — complete source faucet snap | Compare whole-cover spreading, seating and recovery after support cleanup. | Try a filament or print-recipe candidate on the complete snap, keeping both full catches and the rigid host stock. |
| P bores and small lettering | Inspect hole shape, tube fit, layer starts and retained letter strokes. | Try a passage-size or detail-printing candidate on the actual organizer contact or marked part. |

Every project uses a 0.20 mm first bed layer. The N and A heights apply above
that first layer. Their finish specimens print separately from the carrier,
so each retains its own layer schedule. Physical results for The Pour are
unrecorded. Short sections and multi-object plates change cooling, layer return
time, warping and support placement. Judge the corresponding complete part
before changing its production recipe. Surface finish and hand feel do not
measure load capacity or lifetime.

## Assemble and remove the samples

Use files at 100% scale in their saved print poses. Print
[PIP-BASE](print-assemblies/pip-base.stl) or its editable project: P and Q24/Q48/Q72 share
that frame and all begin on the bed. Keep their positions and gaps together.
H is separately printed with automatic supports. The assembled STEP shows
display placement; the individual specimens use their own manufacturing frames.

With the basin upright:

1. Let PIP-BASE cool and record each shutter's initial condition before working
   it. Use its intended handle and X travel direction. Stop if release requires
   bending, levering, cutting or cracking the model.
2. Clear the separate pieces' supports. Seat S05R, S15R, S25R, S35R and S45R on
   the front peg pairs, numbered faces forward. Insert their tongues from the
   front with handles forward. Seat R30/R45/R60 on their peg pairs as shown in
   the assembled model; R45 is the rear window beneath the fin platform.
3. Seat R6 on its two right-side pegs and slide GR's lower footer onto P's
   left horizontal key toward world +X. Lower H vertically so its two root
   keys enter P, its right key enters
   R6's open interior top socket, and its upper cup receives GR's solid top
   footer. Keep the source round surfaces and grip slots exposed.
4. Seat A08/A12/A24 on H's three fin docks in the order shown in the assembled
   model. Their displayed rotation leaves their manufacturing azimuths intact.
5. Fit G into GR's upper and lower wing slots. Engage one wing, bow the centre
   outward to the left, then enter the other wing and release the strip.
   Its finger face points outboard left (world −X). Pull the centre in that
   same direction to free a wing for removal; the front of the receiver remains
   open for access.
6. Put each neck on its matching D foot: its bottom cut ring bears on the foot
   and the locator enters its existing passage. Place the matching K keeper's
   open local +Y slot over the internal T-head and slide K toward local +Y
   until its closed end seats against the T-head. Positions ascend along the
   helix as N08, N12, N24, NR00, NR05, NR15, NS00, NS10, NS20. Install each
   complete holder by reversing its withdrawal route below; the complete grip
   module comes off for N12.
7. Seat FH's rear S55 cut face on P's rear adapter and existing-passage locator.
   Park FC's two rear cut edges on the saddles behind S25R. This places the
   complete relaxed cover at its open loading offset, native N +9.5 mm.

Each neck holder removes independently. Lift the complete D/N/K unit 3 mm along
its foot's cut normal (local +Z), then pull radially outward along local +X,
parallel to the basin, to 50 mm total outward travel. Two units have an extra
step:

| Unit | Withdrawal route |
| --- | --- |
| N08, N24, NR00, NR05, NR15, NS00, NS10 | Lift 3 mm locally, then pull 50 mm radially outward. |
| N12 | First slide the complete G/GR module 10 mm outboard left (world −X) and set it aside; then use the standard holder route. |
| NS20 | Lift 3 mm locally, pull 10 mm radially outward, lift another 3 mm vertically (world +Z), then continue outward to 50 mm total. |

Hand-support H while the grip module's left bearing is absent. Return G/GR
along world +X so P's lower horizontal key and H's open upper cup seat. These
routes have sampled nominal CAD clearance; printed release force, stability
and lifetime are unrecorded.

With a holder off H, hold the foot and neck, slide K **uphill toward local
negative Y** by 7.2 mm, then slide
the neck off along its existing passage axis, leaning toward local positive Y
(away from the caption) by 15° from the cut-face normal. This is 0.268 mm of
positive Y travel per 1 mm of positive Z travel. The K underside clears the
source cut top by
0.10 mm; its T-slot has 0.15 mm side air and 0.30 mm roof air. Refit the same
marked keeper and foot. After unloading the neck holders and lifting the A fins
from their pegs, lift H vertically 4 mm to clear P's keys, R6's open top and
GR's upper-footer cup. G can remain fitted in GR.
R45 sits beneath the fin lands; its underside is accessible from the front.
Lift H off before lifting R45 from its pegs. R30 and R60 lift directly from P.

Lift FC out of its parking saddles before trying the snap. The production
loading path approaches from the tube-outlet end at native N +9.5 mm, slides
along the neck's S axis to align, then lowers squarely toward the neck. Both
complete lips enter their grooves; the broad walls spread elastically. Lift the
removable FH out of its rear adapter when closer access is needed. The open
display pose and storage saddles are separate from the snap's seated fit.

The keepers, source cover and removable storage seats park on an upright desk
reference. Their nominal clearances and modeled motions do not establish
printed release or qualify the assembly for inversion.

## Captive ripple readings

Q24, Q48 and Q72 bear **.24**, **.48** and **.72**. These are model-to-model
**Z TOP** gaps above P's fixed rail. The finite X travel is 26 mm. Transverse
running air is **Y 0.35 mm per face**; it does not describe X end space. Lower
Z air stays at 1.44 mm. Both bed-mouth edges have 0.30 mm chamfers. Only top
release air changes across this bracket.

The [native print reading](print-preparation.json) places the fixed rail's last
top nozzle Z at 6.44 mm. Each moving roof's nominal underside is its first
roof nozzle Z minus the common 0.24 mm model step:

| Shutter | Marked CAD gap | First roof nozzle Z | Nominal roof underside Z | Commanded top air |
| --- | ---: | ---: | ---: | ---: |
| Q24 | 0.24 mm | 6.92 mm | 6.68 mm | 0.24 mm |
| Q48 | 0.48 mm | 7.16 mm | 6.92 mm | 0.48 mm |
| Q72 | 0.72 mm | 7.40 mm | 7.16 mm | 0.72 mm |

The lower air is 1.44 mm: P's first rail nozzle Z4.28 minus its 0.24 mm model
step gives underside Z4.04, above the moving floor's last top nozzle Z2.60.
P and all three eyes begin with model deposition at nozzle Z0.20. The current
Bridge strand-flow HEIGHT is also 0.24 mm; it remains separate from the nominal
model slab used to compute air. No support strands enter the sampled gap windows.

The following full commanded-width footprint readings match at both +Y and
−Y probe lines on all three eyes. They subtract half of each facing strand's
width from its measured centerline separation:

| Probe region / nozzle Z | Centerline separation | Fixed / moving width | Footprint air per face |
| --- | ---: | ---: | ---: |
| First bed mouth and foot / 0.20 mm | 1.500 mm | 0.500 / 0.500 mm | 1.000 mm |
| First rail slab / 4.28 mm | 0.770 mm | 0.450 / 0.420 mm | 0.335 mm |
| Rail / 4.52–6.20 mm | 0.770 mm | 0.420 / 0.420 mm | 0.350 mm |

These are sampled commanded slabs and width footprints. Strand shape, sag,
solid-skin contact, physical clearance and release remain unmeasured.

Record **free off bed**, **gently freed at the intended handle**, or **fused**
before repeated motion. Then separately record full travel, continued capture,
roughness/play, and any loose or missing model strands. A gently freed sample
has a different initial result from one already free. A useful candidate is the
smallest top gap that releases without model damage and provides travel/play
suitable for this reference. If it binds, inspect the contact first, then try
one larger Z-top value on a fresh module. Do not infer a universal planar fit
or support-removal allowance from this reading.

The [PET-GF interface-edge result](../../../print-tests/petgf-interface-edges/results.json)
selected all eight 0.48 mm planned-gap specimens for the cleanest release with
roof strands preserved; none of the eight 0.24 mm specimens were in that
selected group. That comparison used sparse support interfaces. The solid
model skins here have different contact, anchorage and cooling. The result
informs the middle bracket value; it does not establish PIP pass/failure or
qualify the 0.72 mm bracket.

## Surface and seam readings

The neck specimens retain the actual Industrial faucet section: a 27 mm round
exterior, internal passages and production −15° manufacturing pose, cut
horizontally into an 18.2 mm tall section. Their frozen source is the
[faucet neck swatch](../../faucet/finish-coupons/scarf-swatches-v1/README.md).
Every source STL triangle is retained. The
[Industrial acceptance](../../faucet/industrial/physical-acceptance.json)
establishes the identified complete faucet's shipping appearance. The short
section's heat exposure and bed start differ from the complete faucet.

The prepared N and seam comparisons hold Classic walls. The accepted complete
Industrial base has its own Arachne object override. N12 matches that base's
0.12 mm fine-band height; it does not reproduce the complete variable-layer
recipe. NR15 matches its 15% regular seam gap, while the reference uses back
placement and the complete base uses aligned placement. The accepted recipe
has scarf off. NS10 and the other scarf specimens are exploratory comparisons.
Baseline marks identify only the matched parameter.

Regular and scarf gap percentages describe distance relative to the 0.4 mm
nozzle diameter: 5% is 0.02 mm, 15% is 0.06 mm and 20% is 0.08 mm. They are not
flow percentages. NS specimens keep a 10 mm scarf length, 10% start height,
ten steps, the smart 155° setting and inner-wall scarf; entire-loop scarf is
off. Their regular gap stays at 15%. Read the rear join under grazing light
and touch, then the nearby wall for an open gap, broad trough or disturbed finish.

The A blades are representative surfaces constructed for this object. Marked
ramps run from 0° to 90° above their manufacturing bed in 15° increments. Upper
R6 curves lie in the YZ print plane; the X-marked R6 shoulder lies in XZ.
Compare both directions on each blade. Their nominal curved strip is 3 mm
thick; N supplies the direct faucet-geometry comparison.

H's fluted apron uses the enclosure field dimensions: 4 mm flute width,
1.2 mm depth, nominal 5.1221 mm pitch and 5 mm end fades, with 5.8 mm intact backing
at full depth. It is a new short field using that profile, not a cropped complete
enclosure wall. The [enclosure flute evidence](../../cadlib/flute-evidence/README.md)
and shared [reeding geometry](../../cadlib/reeding.py) describe its source.
The full-enclosure photographs are qualitative appearance evidence without
calibrated light or scale. Compare a groove, its fade and an adjacent smooth land
separately.

## Sliding, support and grip readings

The S tongues travel front to back in Y; their numbers describe transverse X
air per side. S05 has 0.10 mm total X air; S45 has 0.90 mm. Floor air stays at 0.25 mm and
wing-roof air at 0.45 mm. The five functional tongues have the same geometry;
their printed values differ. Clear receiver supports before comparing with the
same tongue. The **.25 MOVE** mark identifies the current moving-fit convention.
Ordinary assembly seats use 0.15 mm per face, moving service fits 0.25 mm per
face, and a supported mating face has another 0.25 mm assigned once to its gap
in [fits.py](../../cadlib/fits.py). These are current design conventions.

The [tee-carrier low-force fit](../../enclosure/tee-carrier/low-force-trial/physical-acceptance.json)
is accepted at an asymmetric 1.00 mm roof gap and 0.25 mm floor gap. Its roof
roughness and available actuation force belong to that joint; a small reference
lane does not establish a gap for every mechanism. The storage keys also have
their own allowances: 0.15 mm per face for static seats and 0.25 mm per face for
the removable 6 × 8 mm neck keys. Those moving keys insert 2.5 mm with 0.25 mm
bottom air.

R windows share a 30 mm wide, 3 mm thick cantilever roof with open removal
access. Let them cool, inspect with supports still attached, then remove the
supports and compare remaining model edges, strands and continuity. Keep the
removed supports identified until comparison is complete. Their first roof
slab is Z17.00–17.24 mm in each specimen's manufacturing frame:

| Window | Requested top distance | Last interface nozzle Z | Emitted planned gap |
| --- | ---: | ---: | ---: |
| R30 | 0.30 mm | 16.76 mm | 0.24 mm |
| R45 | 0.45 mm | 16.52 mm | 0.48 mm |
| R60 | 0.60 mm | 16.28 mm | 0.72 mm |

The first roof nozzle Z is 17.24 mm with a 0.24 mm nominal model step and
0.24 mm Bridge flow-height metadata. These commanded gaps use the nominal
roof underside at Z17.00 mm; finished strand position and cleanup are physical
results. The
[interface-pattern result](../../../print-tests/petgf-interface-patterns/results.json)
identifies retained horizontal underside strands as the first model bridge
layer. Easy removal can include lost model material. Removal alone does not
establish the remaining roof's thickness or fit.

G uses the complete [flat-wing grip](../../enclosure/grip-cover/README.md):
79.7 × 11.558 × 3.36 mm body, 84.5 mm full length, with 2.4 mm reach × 5 mm span
× 1.68 mm thick end wings. Its complete flexible span is retained. GR keeps
3 mm end walls, 12 mm roof stock, 0.15 mm at body ends and wing sides, 0.45 mm
at retention faces and 0.25 mm behind the strip. G prints throughout at 0.08 mm
in this reference. The
[accepted grip receiver trial](../../enclosure/grip-cover/physical-acceptance.json)
establishes support removal and assembled fit for its identified coupons and
strip. This vertical side receiver has new storage footers and its own print
recipe; its physical assembly and repeated-flexing behavior are unrecorded.
The complete G/GR module also slides out of the sculpture without removing G
from its receiver, using P's horizontal seat and H's outboard-open cup.

## Source rounds, complete snap and details

R6 retains the tee column's exterior section and additive chamfer tangent to
its expanding round. Its plain stock excludes the spring and tee hardware.
The exterior spans 16.9 × 58.872 mm and 21.054 mm build height. Expansion is
0.5 mm outward per millimetre of build rise, tangent at about 3.317 mm with a
2.292 mm bed inset. The recipe uses Classic walls, 0.24 mm body/expanding layers,
0.08 mm in the top-round band, six walls locally through Z0–6.1 mm, walls before
infill, and 15% infill/wall overlap. Exterior transition supports are off.
The native slice has six wall roads at the expanding-wall witness through
nozzle Z6.20 mm and two from Z6.44 mm. Its fine band starts at nozzle Z15.16 mm
after Z15.08 mm. The first two outer-wall commanded-width footprints overlap
by 0.161 mm at that witness; physical bead contact and bonding are unmeasured.
No support strands are emitted for R6, and the first wall precedes the first
infill in each object layer. Its underside storage sockets and open interior
top seat preserve the source show surfaces. The
[tee surface acceptance](../../enclosure/tee-carrier/physical-acceptance.json)
establishes the identified bottom taper's reported appearance; it does not
establish this reference's finish, sliding fit or lifting load. The shared
[overhang geometry](../../cadlib/overhang_round.py) defines the profile.

FH and FC use the [frozen source features](inputs/source-features/sources.json).
FC is the complete relaxed Industrial cover: 29.8 × 49.75 mm, 1.3 mm bezel and
both broad side walls/lips intact. FH is the actual rigid tip cropped only at
rear S55; both full grooves, radial stock and source passages remain. The
1.2 mm lip engagement, 3 mm lip height, 0.48 mm bearing air and 0.30 mm end air
remain at source scale. Elastic spreading is required: the relaxed rigid cover
intersects the host at the seated datum. An open CAD pose does not establish a
seated elastic fit. P's rear-face adapter is a storage feature; its 1.8 mm
passage locator has a measured minimum CAD air of about 0.202 mm, rather than
a uniform per-face slip.

The [faucet snap acceptance](../../faucet/faucet-display-cover/physical-acceptance.json)
establishes the broad-wall design approach on its identified complete
cover. The current frozen FC bytes differ from the cover identified in the
Industrial shipping record. This complete cover/cropped-host reference has no
recorded assembled result. Keep full walls and catches intact when comparing
material behavior; a small catch alone changes the spring span and load path.

P's Ø4.40 and Ø6.65 mm holes use the
[umbilical organizer's nominal passages](../../faucet/umbilical-organizer/README.md).
Their 6.2 mm straight contact is shorter than the organizer's 9.2 mm contact and
lacks its 0.4 mm entrance chamfers. A tube passing through P records that
sample's fit, rather than the complete organizer contact. Raised top markings,
recessed master identification, smooth lands and the bed face provide detail
and first-layer appearance references. Record those under the same reference
ID and saved recipe as the larger surfaces. Use the uninked smooth edge beside
**BATCH / DATE** as P's finish datum.
