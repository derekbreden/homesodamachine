# Manifold layout

The ten flavor valves, both KPHM400 pumps and the [8](TEE_COUNT) junctions between them, placed
with nothing else in the box — no enclosure, no tray, no reservoir, no nozzle, no hopper, no
carbonator. The connections are
[`topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)'s, with one difference:
each reservoir has ONE port here and meets its channel's fill and draw gates at a junction, so
segments 24, 25 and 26 mirror 14, 15 and 16. The machine gives reservoir B two mouths of its
own instead. Free here: where every body stands, how it is turned, and which of a junction's
three ports takes its run.

Built by [`manifold_layout.py`](manifold_layout.py) → `manifold-layout.step`, and the three
elevations beside it. Two decks of valves over the pumps, the upper one folded onto the lower
about the hinge the four barb tees' front collets stand on.

![plan](manifold-layout.top.png)

## The bodies, and the figures that set the packing

| | |
|---|---|
| 10 × valve | Beduan 12 V NC solenoid ([`reference/beduan-solenoid`](/hardware/reference/beduan-solenoid/README.md)) — [59](VALVE_LEN) mm collet face to collet face, straight through, port axis [11.3](VALVE_PORT_Z) mm over its own mounting plane. Two of them pack no closer than [34.25](VALVE_PITCH) mm. |
| 2 × pump | Kamoer KPHM400 ([`reference/kamoer-kphm400`](/hardware/reference/kamoer-kphm400/)) — two barbs [57](BARB_PITCH) mm apart on one face, both facing the same way, [20.38](BARB_INSET) mm back from the head's front face. |
| [8](TEE_COUNT2) × tee | John Guest PP0208E ([`reference/tee-connector`](/hardware/reference/tee-connector/README.md)) — run collets [20.07](TEE_RUN) mm either side of the body centre, [40.14](TEE_SPAN) mm end to end, branch reaching the same distance. |
| [2](ELBOW_COUNT) × elbow | John Guest PP0308E ([`reference/elbow-connector`](/hardware/reference/elbow-connector/README.md)) — [19.56](ELBOW_LEG) mm from bend corner to each collet face. |
| 0 × Y-divider | Its two outlets stand [14.7](DIVIDER_PITCH) mm apart ([`reference/y-divider`](/hardware/reference/y-divider/README.md)). |
| [6](TUBE_COUNT2) × tube | 1/4" OD LLDPE, both straight. |

## Frame

X is width, mirrored about x = 0 — channel A (pump B) west, channel B (pump A) east. Y is
depth; the two nozzle mouths leave out the back (+Y) and the other four are turned onto +Z. Z is
height, 0 at the pumps' own floor; the valves stand on two decks above them, at z
[91.67](DECK_Z) and [151.07](UPPER_Z).

## Four limbs, folded in two

A tee dropped on a pump barb by its BRANCH puts its RUN across the head's face, so each pump
hands out two parallel lanes [57](BARB_PITCH2) mm apart, one branch reach off its own skin.
Every valve is straight through and every junction's run takes two valve ports, so a lane is
one line of valves and tees butted collet to collet, front to back. `LIMB_PITCH` is that
spacing and it is a knob: `HSM_LIMB_PITCH=<mm>` steps both tees toward the pump's axis and
draws the leaning tube each barb then needs to reach its tee.

```
                          `|` = the hinge; everything left of it is folded up and over
    A2   x [-72.38](LIMB_OUT_XW)          V-G | Y-D · V-F · Y-E
    A1   x [-20.07](LIMB_IN_XW)    V-A · Y-A · V-C | Y-C · V-E
    ─────────────────────────────────────────────────────────  mirror plane
    B1   x [+20.07](LIMB_IN_XE)    V-B · Y-B · V-D | Y-F · V-H
    B2   x [+72.38](LIMB_OUT_XE)          V-J | Y-G · V-I · Y-H
                            ↓
                          back   (every mouth)
```

The lower deck's port axes sit at z [91.67](DECK_Z2), [17.76](DECK_GAP) mm over the pump heads'
crowns; the folded deck's at z [151.07](UPPER_Z2). The two inner limbs leave
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

Six more of the butts open into a 90° of R[14](QUARTER_R), [21.99](QUARTER_LEN) mm of tube
each, and all [6](QUARTER_COUNT) stand on one plane — y [79.07](BEND_Y), the far collet of the
valve that ends a limb. Each joint's fixed collet opens +Y there, the tube turns onto +Z, and
whatever was butted to it comes round with the turn. The axis runs along X, so the six share one
transform per deck and a mirrored pair still faces itself.

| | |
|---|---|
| fluid-3, fluid-5 | V-A and V-B off Y-A and Y-B, up on the folded deck — the two source valves come off the deck's own plane and lie along +Z, then STEP once more (below) |
| fluid-14, fluid-24 | Y-E and Y-H off the fill gates, so each reservoir junction lies along +Z with its own line leaving that way |
| fluid-16, fluid-26 | the draw gates' elbows, which come round with their tees, so the crossing between them keeps its [12.69](F16_LEN2) mm and its skew exactly |

### The source valves' step

Once they are round, V-A and V-B go [28](STEP_TRAVEL) mm further along their run and
[14](STEP_JOG) mm across it, toward the foam shell's crown, without changing direction. Two arcs
of one radius with a straight between them do that, and the two distances fix the pair:

    travel = 2R·sinθ + s·cosθ        jog = 2R(1 − cosθ) + s·sinθ

which solve to `(2R − jog)·cosθ + travel·sinθ = 2R`, and at R[14](QUARTER_R) that is
θ = [36.870](STEP_ANGLE)° either side of s = [14.00](STEP_STRAIGHT) mm —
[32.02](STEP_LEN) mm of tube.

**A 90° pair is the member of that family with no straight in it, and it puts the jog EQUAL to
the travel**, because each quarter spends R on both axes. So 90° turns step 28 across as well as
28 along, and 28 across lands the valve's mounting plane inside the core's crown.

**Y-C, Y-D, Y-F and Y-G** sit on the four barbs, branch down, at the hinge. **Y-A and Y-B** stand on the
inner limbs' own axes, one valve forward of the selects they feed, with their branches meeting
face to face across the mirror plane — [0.00](CROSSBAR) mm of tube between them. **Y-E and
Y-H** stand at the far end of the outer limbs behind the fill gates, each carrying its
reservoir's line out the back on its run and crossing the pump on its branch to the draw gate:
[12.69](F16_LEN) mm of tube onto an elbow that turns that collet, [2.3](JOIN_SKEW)° off axis.

Mirror-checked: [10](TWIN_COUNT) twinned pairs, worst off by [0.0000](MIRROR_OFF) mm.

## How each connection is made

[11](BUTT_COUNT) of the [21](SEGMENT_COUNT) segments the topology names between these bodies
are collet butted to collet: tube in both quick-connects, none between them, no solid drawn.
[6](TUBE_COUNT) are the straight reservoir crossings, [4](SPINE_COUNT) are the fold's 180°
turns and [6](QUARTER_COUNT2) are the quarter turns above. Every corner in the manifold —
[18](CORNER_COUNT) of them — sits on the stock's own floor of [14](MIN_BEND) mm.

The [6](MOUTH_COUNT) mouths that leave this study are drawn one bend radius long and stop, and
the fold turns all of them to face the back: V-A-I (tap), V-B-I (hopper), V-G-O (nozzle A) and
V-J-O (nozzle B) on the upper deck; Y-E-2 (reservoir A) and Y-H-2 (reservoir B) on the lower.

## Envelope

[179](ENV_X) × [162](ENV_Y) × [252](ENV_Z) mm — [7.29](ENV_L) L of bounding box over the
bodies and the tube between them, with [0](CLASHES) pairs of placed solids sharing volume.
Add one [14](STUB_LEN) mm mouth stub on each of the six and it is
[179](REACH_X) × [162](REACH_Y) × [266](REACH_Z).

Two figures in [`manifold_layout.py`](manifold_layout.py) are the study's own rather than any
part's. `BUTT` is the tube left outside a pair of butted quick-connects, and it is 0.
`BARB_STANDOFF` is the climb given to a barb over and above what `LIMB_PITCH` demands, and it
is 0 as well; a barb is not a quick-connect, so that one is a modelling convenience, and z
[91.67](DECK_Z2) rides on it one millimetre for one.

![front](manifold-layout.front.png)

![right](manifold-layout.right.png)

## Standing it on the refrigeration stratum

[`front_half.py`](front_half.py) → `front-half.step` mates three bodies with nothing between
them: the compressor shroud's aft face to the condenser's west face, and the crown of those two
to this pack's pump-head front face. The gaps are 0 by intent — the compressor stands well
inside its shroud with its ports free, and the condenser's are cornered but leave by whichever
of that corner's faces suits, so touching is what makes the run between them short.

![front half](front-half.right.png)

## Regenerate

```
tools/cad-venv/bin/python hardware/manifold-layout/manifold_layout.py
```

Prints the limbs, every connection and how it is made, the mouths, the envelope, the mirror
check and the clash check, and writes the figures above back into this file.

## Sources
[value](NAME) texts are updated by:
- `/hardware/manifold-layout/manifold_layout.py`
