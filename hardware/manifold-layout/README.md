# Manifold layout

The ten flavor valves, both KPHM600 pumps and the [6](TEE_COUNT) junctions between them, placed
with nothing else in the box — no enclosure, no tray, no reservoir, no gooseneck, no funnel, no
carbonator. The connections are
[`topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)'s, with one difference:
each reservoir carries TWO MOUTHS of its own — the draw on the bulkhead at the bottom of its
wet V, the fill on a bore in its own cap — so each pair's two valves reach one directly and
neither channel has a reservoir junction. Segments 15 and 25 do not exist; 14 and 24 are the
fills, 16 and 26 the draws. Free here: where every body stands, how it is turned, and which of a junction's
three ports takes its run.

Built by [`manifold_layout.py`](manifold_layout.py) → `manifold-layout.step`. Two decks of valves over the pumps, the upper one folded onto the lower
about the hinge the four barb tees' front collets stand on.

## The bodies, and the figures that set the packing

| | |
|---|---|
| 10 × valve | Beduan 12 V NC solenoid ([`reference/beduan-solenoid`](/hardware/reference/beduan-solenoid/README.md)) — [59](VALVE_LEN) mm collet face to collet face, straight through, port axis [11.3](VALVE_PORT_Z) mm over its own mounting plane. Two of them pack no closer than [34.25](VALVE_PITCH) mm. |
| 2 × pump | Kamoer KPHM400 ([`reference/kamoer-kphm400`](/hardware/reference/kamoer-kphm400/)) — two barbs [59.75](BARB_PITCH) mm apart on one face, both facing the same way, [20.38](BARB_INSET) mm back from the head's front face. |
| [6](TEE_COUNT2) × tee | John Guest PP0208E ([`reference/tee-connector`](/hardware/reference/tee-connector/README.md)) — run collets [20.07](TEE_RUN) mm either side of the body centre, [40.14](TEE_SPAN) mm end to end, branch reaching the same distance. |
| 0 × Y-divider | Its two outlets stand [14.7](DIVIDER_PITCH) mm apart ([`reference/y-divider`](/hardware/reference/y-divider/README.md)). |
| [4](TUBE_COUNT2) × tube | 1/4" OD LLDPE, all straight — the four the collet plate's berth opens between each pump barb and its anchor tee. |

## Frame

X is width, mirrored about x = 0 — channel A west, channel B east, each over its own pump. Y is
depth; the two flavour mouths leave out the back (+Y) and the other four are turned onto +Z. Z is
height, 0 at the pumps' own floor; the valves stand on two decks above them, at z
[88.38](DECK_Z) and [147.78](UPPER_Z).

## Four limbs, folded in two

A tee dropped on a pump barb by its BRANCH puts its RUN across the head's face, so each pump
hands out two parallel lanes [59.75](BARB_PITCH2) mm apart, one branch reach off its own skin.
Every valve is straight through and every junction's run takes two valve ports, so a lane is
one line of valves and tees butted collet to collet, front to back. `LIMB_PITCH` is that
spacing and it is a knob: `HSM_LIMB_PITCH=<mm>` steps both tees toward the pump's axis and
draws the leaning tube each barb then needs to reach its tee.

```
                          `|` = the hinge; everything left of it is folded up and over
    A2   x [-79.82](LIMB_OUT_XW)          V-G | Y-D · V-F
    A1   x [-20.07](LIMB_IN_XW)    V-A · Y-A · V-C | Y-C · V-E
    ─────────────────────────────────────────────────────────  mirror plane
    B1   x [+20.07](LIMB_IN_XE)    V-B · Y-B · V-D | Y-F · V-H
    B2   x [+79.82](LIMB_OUT_XE)          V-J | Y-G · V-I
                            ↓
                          back   (every mouth)
```

The lower deck's port axes sit at z [88.38](DECK_Z2), [15.75](DECK_GAP) mm over the pump heads'
crowns; the folded deck's at z [147.78](UPPER_Z2). The two inner limbs leave
[5.89](INNER_GAP) mm between their valve bodies across the mirror plane.

## The fold

The four connections crossing the hinge — fluid-9, 17, 19 and 27 — each become one 180° turn:
a quarter-turn of R[14](SPINE_R), [31.40](SPINE_STRAIGHT) mm of straight, and a quarter-turn
back, [75.38](SPINE_LEN) mm of tube. Both ends meet their collet on its own axis, so the turn
carries no straight at either END — the straight is in the middle.

**The radius and the deck separation are two different numbers.** Any 180° that ends on both
collet axes will join them, and that family is one parameter wide: the semicircle is only the
member with no straight in it, and it is the worst to pick, because what the pack pays for a
turn is how far it reaches past the hinge — and that reach is the RADIUS. So the radius sits on
the stock's floor, R[14](MIN_BEND2), and the straight takes up whatever the decks leave.

The decks stand [59.4](DECK_SEP) mm apart, and that IS chosen. What stands over what is a
folded valve's underside against the SPADE TERMINALS of the valve beneath it — two 0.8 mm tabs
reaching 15 mm past a coil face, in a band 1.4 mm wide — and every bounding box that contains
those tabs also contains the coil crown 6 mm above them, so a box solve asks for 91.6 where the
metal needs 58.4. `HSM_DECK_SEP=` builds another: at 58.0 the clash check goes red at 15 mm³ a
corner, at 59.4 it is clean. `HSM_SPINE_R=` moves the radius on its own.

## The quarter turns

[2](QUARTER_COUNT4) more of the butts open into a 90° of R[14](QUARTER_R),
[21.99](QUARTER_LEN) mm of tube each, and both of them stand on one plane — y
[79.07](BEND_Y), the far collet of the valve that ends a limb. Each joint's fixed collet opens
+Y there, the tube turns onto +Z, and whatever was butted to it comes round with the turn. The
axis runs along X, so the pair shares one transform and still faces itself across the mirror.

| | |
|---|---|
| fluid-3, fluid-5 | V-A and V-B off Y-A and Y-B, up on the folded deck — the two source valves come off the deck's own plane and lie along +Z, then STEP once more (below) |

### The source valves' step

Once they are round, V-A and V-B go [19.72](STEP_TRAVEL) mm further along their run and
[7](STEP_JOG) mm across it, toward the foam shell's crown, without changing direction. Two arcs
of one radius with a straight between them do that, and the two distances fix the pair:

    travel = 2R·sinθ + s·cosθ        jog = 2R(1 − cosθ) + s·sinθ

which solve to `(2R − jog)·cosθ + travel·sinθ = 2R`, and at R[14](QUARTER_R) that is
θ = [29.601](STEP_ANGLE)° either side of s = [6.77](STEP_STRAIGHT) mm —
[21.24](STEP_LEN) mm of tube.

That pair has a member only while `(2R − jog)² + travel² ≥ (2R)²`, and the travel is not this
run's to choose: V-A and V-B stand on the cold core's cap, which the pack does not carry, so
every millimetre the pack goes aft — the collet plate's berth among them — comes off it. **THE
JOG IS WHAT THE FLOOR IS SET BY.** Written out, that floor is `√(jog·(4R − jog))`, and it climbs
with the jog for every jog under 2R: at [7](STEP_JOG2) mm across it is
[18.52](STEP_FLOOR) mm against a travel of [19.72](STEP_TRAVEL2), so each run is the pair of
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
only the length of the step is solved for. V-A takes [2.42](STEP_SPREAD) mm of that: it steps
[7.41](STEP_CROSS_A) mm across in the same [19.72](STEP_TRAVEL3) along, θ = [32.878](STEP_ANGLE_A)° either side of
s = [5.38](STEP_STRAIGHT_A) mm, [21.45](STEP_LEN_A) mm of tube. What the spread buys is the slot
on the mirror line — the pair stands a valve's half-width either side of x 0 and the funnel's
gravity drain threads the gap between their coils, so a valve carried outboard widens that lane
one for one.

**Y-C, Y-D, Y-F and Y-G** receive the four barbs through short straight runs, branch down, at
the hinge. **Y-A and Y-B** stand on the
inner limbs' own axes, one valve forward of the selects they feed, with their branches meeting
face to face across the mirror plane — [0.00](CROSSBAR) mm of tube between them. **NEITHER
RESERVOIR HAS A JUNCTION**: each carries two mouths of its own, so every one of the four gate
collets is a mouth of this study and leaves on its own axis, and every junction left in the pack
joins two VALVES rather than a valve and a reservoir.

Mirror-checked: [9](TWIN_COUNT) twinned pairs, worst off by [0.0000](MIRROR_OFF) mm.

## How each connection is made

[9](BUTT_COUNT) of the [17](SEGMENT_COUNT) segments the topology names between these bodies
are collet butted to collet: tube in both quick-connects, none between them, no solid drawn.
[4](TUBE_COUNT) are the straight reservoir crossings, [4](SPINE_COUNT) are the fold's 180°
turns and [2](QUARTER_COUNT2) are the quarter turns above. Every corner in the manifold —
[14](CORNER_COUNT) of them — sits on the stock's own floor of [14](MIN_BEND) mm.

The [8](MOUTH_COUNT) mouths that leave this study are drawn one bend radius long and stop, and
the fold turns all of them to face the back: V-A-I (tap), V-B-I (funnel), V-G-O (flavor A) and
V-J-O (flavor B) on the upper deck; and the four reservoir gates — V-F-O and V-E-I for A,
V-I-O and V-H-I for B — on the lower.

## Envelope

[194](ENV_X) × [169](ENV_Y) × [242](ENV_Z) mm — [7.90](ENV_L) L of bounding box over the
bodies and the tube between them, with [0](CLASHES) pairs of placed solids sharing volume.
Add one [14](STUB_LEN) mm mouth stub on each of the [8](MOUTH_COUNT2) and it is
[194](REACH_X) × [169](REACH_Y) × [256](REACH_Z).

Two figures in [`manifold_layout.py`](manifold_layout.py) are the study's own rather than any
part's. `BUTT` is the tube left outside a pair of butted quick-connects, and it is 0.

`BARB_STANDOFF` is the [6.98](BARB_STANDOFF) mm fore/aft projection between each pump barb and
its anchor tee's branch collet. Its first [1.28](PUMP_STATION_LEAD) mm holds the moving pump end
clear of the fixed plate-guide wall; the remaining [5.7](BARB_PLATE_BERTH) mm is **the
collet plate's berth**. The pump end stands [2](PUMP_DROP) mm below the stationary tee end, so
each straight has a [7.26](BARB_TUBE_LEN) mm centreline length and a shallow vertical rise.
Both pumps ride out of the box on their own pump cartridge and these four runs are what
release. A laser-cut 1/8" 316 flat stands on
edge in the gap with one large hole per tube — wide enough to pass the Ø6.35 tube, narrow enough
to catch the collet nose. So
pulling the pump cartridge draws the anchor tees forward against the steel and the tubes come out of
their collets. Push the pump cartridge home and the four click back in. Nothing is unscrewed for
pump cartridge service and no hand goes behind the deck.

`enclosure_assembly.py` strikes the plate off the placed barbs and writes `collet-plate.dxf`
beside this file — the flat
[`assembly/enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) stages with the
printed pieces and feeds into `enclosure-front-top` through that piece's own Z− face, up the slot
through the bay floor until its top edge comes up onto the cap's land above. The berth is steel and its two airs, so
the whole deck rides on it one millimetre for one: z [88.38](DECK_Z2) carries it, and so does
every millimetre of `SOURCE_TRAVEL` the source runs have left to step in.

## Standing it on the refrigeration stratum

[`enclosure_assembly.py`](enclosure_assembly.py) → `enclosure-assembly.step` mates its bodies with nothing between
them: the compressor's own +X tangent to the condenser's intake face, and the crown of the pair
to this pack's spine hairpins. The cold core is not one of them — it is packed off the +Y wall of back-top
instead, so a LANE stands between it and the stratum, and the two legs of the loop that cross it
are drawn in copper.

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
