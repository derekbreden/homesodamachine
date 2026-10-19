# Manifold layout

The ten flavor valves, both KPHM600 pumps and [2](TEE_COUNT) purchased source tees form the
flavor manifold. Four permanent asymmetric TPU junctions receive the prepared pump stems
through the enclosure wall. Each junction has one straight upper link and one lower link to
a fixed printed return. Each return contains its directional changes, so both of its LLDPE
connections are straight.

[`manifold_layout.py`](manifold_layout.py) writes `manifold-layout.step` with the purchased
hardware, prepared-stem spans, LLDPE members and eight printed wet bodies. The
[complete enclosure assembly](enclosure_assembly.py) adds the manufactured flanged stems,
flat keepers and PET-GF supports from the
[permanent dock](/hardware/printed-parts/enclosure/pump-dock/README.md).

The connections follow [`fluid-topology.md`](/hardware/topology/fluid-topology.md).
Each reservoir has separate fill and draw mouths; segments 14/24 fill them and 16/26 draw
from them. There are no reservoir junctions or segments 15/25.

## The bodies, and the figures that set the packing

| | |
|---|---|
| 10 × valve | Beduan 12 V NC solenoid ([`reference/beduan-solenoid`](/hardware/reference/beduan-solenoid/README.md)) — [59.5](VALVE_LEN) mm collet face to collet face, straight through, port axis [11.05](VALVE_PORT_Z) mm over its own mounting plane. Two of them pack no closer than [34.25](VALVE_PITCH) mm. |
| 2 × pump | Kamoer KPHM600-SW3B17, modelled on the measured KPHM400 head ([`reference/kamoer-kphm400`](/hardware/reference/kamoer-kphm400/)) — two barbs [59.75](BARB_PITCH) mm apart on one face, both facing the same way, [19.38](BARB_INSET) mm back from the head's front face. |
| [2](TEE_COUNT2) × tee | John Guest PP0208E ([`reference/tee-connector`](/hardware/reference/tee-connector/README.md)) — run collets [21.25](TEE_RUN) mm either side of the body centre, [42.5](TEE_SPAN) mm end to end, branch reaching the same distance. |
| 0 × Y-divider | Its two outlets stand [14.7](DIVIDER_PITCH) mm apart ([`reference/y-divider`](/hardware/reference/y-divider/README.md)). |
| 4 × TPU junction | Permanent wall-mounted pump receivers with an upward outlet and an aft/downward 45° outlet. Six-millimetre sealing lands and the pump funnel share one printed wet body. |
| 4 × TPU return | One permanent compound return per lower port. R[6](SPINE_R) internal turns and a horizontal passage join two straight tube links. |
| [17](TUBE_COUNT2) × LLDPE cut | [12](STRAIGHT_LLDPE_COUNT) straight pump-junction links, two formed source links and three fully swallowed butt-joint blanks. Pump stems are separate machined PP-H parts supplied on prepared replacement pumps. |

## Frame

X is width, mirrored about x = 0 — channel A west, channel B east, each over its own pump. Y is
depth; the two flavour mouths leave out the back (+Y) and the other four are turned onto +Z. Z is
height, 0 at the pumps' own floor. The unshifted authoring deck references are z
[90.81](DECK_Z) and [151.76](UPPER_Z); the fore and aft groups occupy their mounting planes independently of the pump stems.

## Four limbs, folded in two

Each pump has two permanent wall junctions on its measured [59.75](BARB_PITCH2) mm port
pitch. The inlet, upward outlet and aft/downward outlet share one TPU body. The outer lower
outlets are clocked slightly about the inlet axis to align their straight links with the
inboard return valves. The upper outlets align with the fore valve ports.

The logical Y-C/D/F/G names identify these printed junctions. Y-A/B identify the two purchased
source tees. The lane diagram describes connectivity and the valve placement construction;
printed returns join the connections crossing its fold line.

```
                          `|` = the hinge; everything left of it is folded up and over
    A2   x [-82.10](LIMB_OUT_XW)          V-G | Y-D · V-F
    A1   x [-22.35](LIMB_IN_XW)    V-A · Y-A · V-C | Y-C · V-E
    ─────────────────────────────────────────────────────────  mirror plane
    B1   x [+22.35](LIMB_IN_XE)    V-B · Y-B · V-D | Y-F · V-H
    B2   x [+82.10](LIMB_OUT_XE)          V-J | Y-G · V-I
                            ↓
                          back   (every mouth)
```

The unshifted deck port references are z [90.81](DECK_Z2) and
[151.76](UPPER_Z2). The two inner limbs leave
[10.45](INNER_GAP) mm between their valve bodies across the mirror plane.

## The fixed lower returns

Fluid-9, 17, 19 and 27 each use one permanently mounted TPU return and two straight LLDPE
links. The return contains an approximately 45° entry turn, a horizontal flow passage and a
90° upward turn, all with R[6](SPINE_R) internal flow radius. The printed-body radius describes
the fluid passage, not a bend imposed on LLDPE.

The inner links have 33.282 mm exposed between junction and return; the outer links have
20.169 mm. Each return's upper mouth stands 2 mm below its purchased valve's collet face.
The two LLDPE members therefore total [35.28](SPINE_LEN) mm exposed at each inner port and
[22.17](OUTER_SPINE_LEN) mm at each outer port. The finished blanks also include the socket
and valve insertion lengths.

The junction-to-return link is captured between two supported bottoming shoulders. Its
nominal insertion is 6.5 mm at each end, including the 0.5 mm entrance lead. Factory cutting
references the actual mounted stop span; total axial play, including the complete assembled
and loaded tolerance budget, is limited to 0.5 mm to retain at least 5.5 mm of either 6 mm
sealing land. The PET-GF channel constrains bowing. The short return-to-valve link is anchored
by the valve's commercial collet. These are geometric retention provisions; pressure holding,
assembly force and endurance remain physical qualification limits.

V-G/J stand [8.28](OUTER_AFT_INSET) mm inboard of their pump ports. The outer return planes
follow those port axes. The authoring deck separation is [60.95](DECK_SEP) mm. The
[shared layout module](/hardware/printed-parts/enclosure/pump-dock/fixed_returns.py) derives the
junction mouths, return paths, socket stops and straight tube spans from the supplied wall
and actual valve ports.

## The quarter turns

[2](QUARTER_COUNT4) more of the butts open into a 90° of R[14](QUARTER_R),
[21.99](QUARTER_LEN) mm of tube each, and both of them stand on one plane — y
[71.25](BEND_Y), the far collet of the valve that ends a limb. Each joint's fixed collet opens
+Y there, the tube turns onto +Z, and whatever was butted to it comes round with the turn. The
axis runs along X, so the pair shares one transform and still faces itself across the mirror.

| | |
|---|---|
| fluid-3, fluid-5 | V-A and V-B off Y-A and Y-B, up on the folded deck — the two source valves come off the deck's own plane and lie along +Z, then STEP once more (below) |

### The source valves' step

The flavour flow regulator sits aft of tube-water-2. Fluid-1 feeds it below the
funnel frame. Fluid-2 turns through the rear service lane, rises west of the water pump,
and crosses directly to V-A's vertical inlet approach. Both routes keep R14 bends.

Y-A/B and V-C/D sit 9.5 mm below the outer limbs in the enclosure. Both source
bends move with that group. V-A and V-B have mounting planes 1.4 mm below the cap
lid's outer face, with 3 mm beneath their blind socket floors, aft of the
455 mL funnel frame.

Fluid-4 drains the funnel into V-B. It leaves the PP0308E elbow under the funnel
frame aft and level through the gap between V-A and V-B, turns west behind V-B's
coil and short of the G Ganen pump's head, runs aft down V-B's west flank, and
makes one U east and down into V-B's aft-facing inlet. All four corners are R14,
and the line only falls.

Once they are round, V-A and V-B go [46.72](STEP_TRAVEL) mm further along their run and
[13.625](STEP_JOG) mm across it, toward the foam shell's crown, without changing direction. Two arcs
of one radius with a straight between them do that, and the two distances fix the pair:

    travel = 2R·sinθ + s·cosθ        jog = 2R(1 − cosθ) + s·sinθ

which solve to `(2R − jog)·cosθ + travel·sinθ = 2R`, and at R[14](QUARTER_R) that is
θ = [17.844](STEP_ANGLE)° either side of s = [40.07](STEP_STRAIGHT) mm —
[48.79](STEP_LEN) mm of tube.

That pair has a member only while `(2R − jog)² + travel² ≥ (2R)²`, and the travel is not this
run's to choose: V-A and V-B stand on the cold core's cap, which the pack does not carry, so
every millimetre the pack goes aft comes off it. **THE
JOG IS WHAT THE FLOOR IS SET BY.** Written out, that floor is `√(jog·(4R − jog))`, and it climbs
with the jog for every jog under 2R: at [13.625](STEP_JOG2) mm across it is
[24.03](STEP_FLOOR) mm against a travel of [46.72](STEP_TRAVEL2), so each run is the pair of
arcs and nothing else.

Under that floor the family has no member at all, and a run that cannot span its jog has to go
BACKWARD first — a hairpin of half a turn, a straight and the other half, which leaves the
heading exactly where it found it and hands the step the travel it was short of, at a cost of
`2πR` and the chord. `hairpins_drawn` counts the ones drawn and it is [0](HAIRPIN_COUNT).

**A 90° pair is the member of that family with no straight in it, and it puts the jog EQUAL to
the travel**, because each quarter spends R on both axes. So 90° turns step 28 across as well as
28 along, and 28 across lands the valve's mounting plane inside the core's crown.

**A CROSS-MOVE IS A VECTOR AND NOT A DISTANCE.** Both arcs and the straight lie in the one plane
that holds the run and the way it steps, so leaning that plane about the run costs the step
nothing — one pair of arcs carries a valve toward the crown and outboard at the same time, and
only the length of the step is solved for. V-A takes [1.92](STEP_SPREAD) mm of that: it steps
[13.76](STEP_CROSS_A) mm across in the same [46.72](STEP_TRAVEL3) along, θ = [18.028](STEP_ANGLE_A)° either side of
s = [40.02](STEP_STRAIGHT_A) mm, [48.83](STEP_LEN_A) mm of tube. V-A retains this
outboard offset.

**Y-C, Y-D, Y-F and Y-G** are permanent printed wall junctions receiving the prepared
pump stems. **Y-A and Y-B** are purchased source tees on the inner limbs, with branches
meeting face to face across the mirror plane — [0.00](CROSSBAR) mm exposed between them.
The four reservoir gate collets are external mouths of this study.

Mirror-checked: [9](TWIN_COUNT) twinned pairs, worst off by [0.0000](MIRROR_OFF) mm.

## How each connection is made

[3](BUTT_COUNT) of the [17](SEGMENT_COUNT) topology segments are collet butts, with no tube
exposed between the faces. Four prepared PP-H pump stems enter the permanent wall junctions.
The [4](FORE_STUB_COUNT) upper links to V-E/F/H/I are straight and have
[14.501](FORE_STUB_EXPOSED) mm exposed. Four lower connections each have two straight LLDPE
members and one fixed printed return. Add the actual insertion depths for finished blanks;
the purchased valve's hidden insertion stop is not specified by its exterior model.

The two source quarter turns and their steps retain [6](CORNER_COUNT) formed LLDPE corners.
Their R[14](MIN_BEND) geometry uses the user’s reported initial-flow observation.
The [neoFlo manufacturer sheet](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf)
publishes a 25.4 mm bend radius for this 1/4-inch OD, 0.170-inch ID LLDPE stock. The R14 bench
observation does not establish pressure or lifetime performance outside that published basis.
The pump-junction upper and lower links impose no formed bend on LLDPE.

The [8](MOUTH_COUNT) mouths that leave this study are drawn one bend radius long and stop, and
the fold turns all of them to face the back: V-A-I (tap), V-B-I (funnel), V-G-O (flavor A) and
V-J-O (flavor B) on the upper deck; and the four reservoir gates — V-F-O and V-E-I for A,
V-I-O and V-H-I for B — on the lower.

## Envelope

[198](ENV_X) × [173](ENV_Y) × [272](ENV_Z) mm — [9.27](ENV_L) L of bounding box over the
bodies and the tube between them, with [0](CLASHES) pairs of placed solids sharing volume.
Add one [14](STUB_LEN) mm mouth stub on each of the [8](MOUTH_COUNT2) and it is
[198](REACH_X) × [173](REACH_Y) × [286](REACH_Z).

Two figures in [`manifold_layout.py`](manifold_layout.py) are the study's own rather than any
part's. `BUTT` is the tube left outside a pair of butted quick-connects, and it is 0.

`BARB_STANDOFF` is the [5.776](BARB_STANDOFF) mm pump-to-deck authoring placement
span. The pump station retains its fitted [3](PUMP_DROP) mm downward world-Z datum.
Four smooth prepared stems project [12.85](BARB_TUBE_LEN) mm from the modeled free BPT
tube plane. Their production setting references the cartridge's actual flat aft face: all
four tips lie 7.750 mm aft of that face at machine Y90.015 mm.

Both pumps ride out on the cartridge. Integral stem flanges transfer insertion and withdrawal
reactions into the lower cradle; the cap closes upward escape. The stems enter TPU funnels
and six-millimetre tight lands. The wall locates each permanent junction in X/Z and a flat
interior keeper captures Y. Stem tips remain 0.50 mm short of their stops with the cartridge
on its outboard stop lands. Broad cartridge and wall planes have 0.250 mm clearance.

The complete enclosure assembly supplies the flanged stems, flat keepers, fixed return
fixtures and positive SB443-IN mounts. Customers replace complete
prepared pumps using the [service procedure](/hardware/service/pump-replacement.md).

## Standing it on the compressor bay

[`enclosure_assembly.py`](enclosure_assembly.py) → `enclosure-assembly.step` mates its bodies with nothing between
them: the compressor's own +X tangent to the condenser's intake face, while the pack's pose is
read from the fixed manifold's occupied envelope above the pair's crown.
The eight deck valves bear in front-top's two trays. The permanent pump junctions and lower
returns have separate PET-GF fixtures. The cold core is not one of the pair — it
is packed off the +Y wall of back-top instead, so a LANE stands between it and the compressor bay, and
the two legs of the loop that cross it are drawn in copper.

The gaps that ARE 0 are by intent, and the refrigerant loop is what they are for. The compressor
is an oblong can whose stubs stand on its own tangent lines and the condenser is an envelope
whose headers are re-dressed to whichever face suits — so the loop's first leg crosses a plane
those two bodies already share, both its stations are one point read twice, and no copper is
drawn between them. The other two cross the lane in front of the core: the condenser's liquid
line into the evaporator's inlet, one straight on the core's own port column, and the
compressor's suction out of its west tangent into the evaporator's outlet. `_lines` draws both.
`refrigerant_joints` reads all three at every build — a mating on its two stations, a tube on
both its mouths — and `check_refrigerant_joints` writes the card red for any leg standing open
and for any with no pair of placed stations to measure.

## Regenerate

```
tools/cad-venv/bin/python hardware/manifold-layout/manifold_layout.py
```

Prints the limbs, every connection and how it is made, the mouths, the envelope, the mirror
check and the clash check, and writes the figures above back into this file.

## Sources
[value](NAME) texts are updated by:
- `/hardware/manifold-layout/manifold_layout.py`
