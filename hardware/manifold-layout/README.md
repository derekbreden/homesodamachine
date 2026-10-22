# Manifold layout

The ten flavor valves, both KPHM600 pumps and [6](TEE_COUNT) purchased PP0208E tees form the
flavor manifold. Two source tees join the source valves to the channel selects and to each
other. Four stand on the pump ports behind
front-top's collet plate, each taking a prepared pump's LLDPE tube in its branch; each pump
tee reaches its fore valve on a short upper tube and its rear valve on one R14 hairpin.

[`manifold_layout.py`](manifold_layout.py) writes `manifold-layout.step` with the purchased hardware, the pump tubes and the LLDPE members. The [complete enclosure assembly](enclosure_assembly.py) adds the collet plate, tee anchors and tee caps, valve trays and magnet columns from the [pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md).

The connections follow [`fluid-topology.md`](/hardware/topology/fluid-topology.md).
Each reservoir has separate fill and draw mouths; segments 14/24 fill them and 16/26 draw
from them. There are no reservoir junctions or segments 15/25.

## The bodies, and the figures that set the packing

| | |
|---|---|
| 10 × valve | Beduan 12 V NC solenoid ([`reference/beduan-solenoid`](/hardware/reference/beduan-solenoid/README.md)) — [59.5](VALVE_LEN) mm collet face to collet face, straight through, port axis [11.05](VALVE_PORT_Z) mm over its own mounting plane. Two of them pack no closer than [34.25](VALVE_PITCH) mm. |
| 2 × pump | Kamoer KPHM600-SW3B17, modelled on the measured KPHM400 head ([`reference/kamoer-kphm400`](/hardware/reference/kamoer-kphm400/)) — two barbs [59.75](BARB_PITCH) mm apart on one face, both facing the same way, [19.38](BARB_INSET) mm back from the head's front face. |
| [6](TEE_COUNT2) × tee | John Guest PP0208E ([`reference/tee-connector`](/hardware/reference/tee-connector/README.md)) — run collets [21.25](TEE_RUN) mm either side of the body centre, [42.5](TEE_SPAN) mm end to end, branch reaching the same distance. |
| 0 × Y-divider | Its two outlets stand [14.7](DIVIDER_PITCH) mm apart ([`reference/y-divider`](/hardware/reference/y-divider/README.md)). |
| [17](TUBE_COUNT2) × LLDPE cut | [8](PUMP_TEE_TUBE_COUNT) pump-tee tubes — four short upper tubes and four R14 hairpins — two formed source links, three fully swallowed butt-joint blanks and the four pump tubes, which come fitted in the prepared pumps. |

## Frame

X is width, mirrored about x = 0 — channel A west, channel B east, each over its own pump. Y is
depth; the two flavour mouths leave out the back (+Y) and the other four are turned onto +Z. Z is
height, 0 at the pumps' own floor. The unshifted authoring deck references are z
[90.81](DECK_Z) and [151.76](UPPER_Z); the fore and aft groups occupy their mounting planes independently of the pump tubes.

## Four limbs, folded in two

Each pump has two tees on its measured [59.75](BARB_PITCH2) mm port pitch, each branch on
its pump tube's axis and each run upright. Each fore valve stands directly over its tee's
connected axis. The inner rear valves stand on their tees' columns; the outer
two stand inboard of theirs.

The logical Y-C/D/F/G names identify the pump tees. Y-A/B identify the two source tees. The
lane diagram describes connectivity and the valve placement construction; the four hairpins
are the connections crossing its fold line.

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

## The lower returns

Fluid-9, 17, 19 and 27 are each one hairpin of black 1/4" LLDPE from a pump tee's lower port
to its rear valve's bottom collet, bent at the stock's R[14](SPINE_R) radius: a short straight
down, a turn aft, a straight, a turn up and a straight up into the valve. The outer two lean
inboard to V-G and V-J. Each hairpin flexes with its tee's travel. Its cut stock is the exposed
path, the tee's run insertion and a nominal valve insertion; a bare run of
[`_fluid_topology_sync.py`](/hardware/topology/_fluid_topology_sync.py) prints each figure.

The rear valve row and source crossbar stand 8 mm above their deck reference to clear the compressor and condenser; V-G and V-J stand 1.5 mm lower than that row offset. V-A and V-B keep their cold-core seats. Actual fully seated marks govern every cut. See the [pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md) and the [internal plumbing procedure](/hardware/assembly/internal-plumbing.md).

## The quarter turns

[2](QUARTER_COUNT4) more of the butts open into a 90° of R[14](QUARTER_R),
[21.99](QUARTER_LEN) mm of tube each, and both of them stand on one plane — y
[79.25](BEND_Y), the far collet of the valve that ends a limb. Each joint's fixed collet opens
+Y there, the tube turns onto +Z, and whatever was butted to it comes round with the turn. The
axis runs along X, so the pair shares one transform and still faces itself across the mirror.

| | |
|---|---|
| fluid-3, fluid-5 | V-A and V-B off Y-A and Y-B, up on the folded deck — the two source valves come off the deck's own plane and lie along +Z, then STEP once more (below) |

### The source valves' step

The internal SB-FPV-40 pressure regulator sits beside the water pump in one tied cradle on the cold-core lid. Fluid-1 feeds it below the funnel frame. Fluid-2 turns up at its rear end, returns through the west service corridor and crosses onto V-A's inlet approach. Both routes keep R14 bends.

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
[21.625](STEP_JOG) mm across it, toward the foam shell's crown, without changing direction. Two arcs
of one radius with a straight between them do that, and the two distances fix the pair:

    travel = 2R·sinθ + s·cosθ        jog = 2R(1 − cosθ) + s·sinθ

which solve to `(2R − jog)·cosθ + travel·sinθ = 2R`, and at R[14](QUARTER_R) that is
θ = [28.658](STEP_ANGLE)° either side of s = [37.94](STEP_STRAIGHT) mm —
[51.94](STEP_LEN) mm of tube.

That pair has a member only while `(2R − jog)² + travel² ≥ (2R)²`, and the travel is not this
run's to choose: V-A and V-B stand on the cold core's cap, which the pack does not carry, so
every millimetre the pack goes aft comes off it. **THE
JOG IS WHAT THE FLOOR IS SET BY.** Written out, that floor is `√(jog·(4R − jog))`, and it climbs
with the jog for every jog under 2R: at [21.625](STEP_JOG2) mm across it is
[27.26](STEP_FLOOR) mm against a travel of [46.72](STEP_TRAVEL2), so each run is the pair of
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
[21.71](STEP_CROSS_A) mm across in the same [46.72](STEP_TRAVEL3) along, θ = [28.771](STEP_ANGLE_A)° either side of
s = [37.93](STEP_STRAIGHT_A) mm, [51.99](STEP_LEN_A) mm of tube. V-A retains this
outboard offset.

**Y-C, Y-D, Y-F and Y-G** are the pump tees behind front-top's collet plate, each taking a
prepared pump tube in its branch collet. **Y-A and Y-B** are the source tees on the inner limbs, with branches
meeting face to face across the mirror plane — [0.00](CROSSBAR) mm exposed between them.
The four reservoir gate collets are external mouths of this study.

Mirror-checked: [9](TWIN_COUNT) twinned pairs, worst off by [0.0000](MIRROR_OFF) mm.

## How each connection is made

[3](BUTT_COUNT) of the [17](SEGMENT_COUNT) topology segments are collet butts, with no tube
exposed between the faces. Four prepared LLDPE pump tubes pass the collet plate into the pump
tees' branch collets. The [4](FORE_STUB_COUNT) upper tubes to V-E/F/H/I have
[15.251](FORE_STUB_EXPOSED) mm exposed; with each fore valve over its tee's connected axis,
a tube stands straight in service and bends the tee's stroke at release. The four
lower connections are each one R14 hairpin. Add the actual insertion depths for finished blanks;
the purchased valve's hidden insertion stop is not specified by its exterior model.

The two source quarter turns and their steps have [6](CORNER_COUNT) formed LLDPE corners.
Their R[14](MIN_BEND) geometry uses the user’s reported initial-flow observation.
The [neoFlo manufacturer sheet](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf)
publishes a 25.4 mm bend radius for this 1/4-inch OD, 0.170-inch ID LLDPE stock. The R14 bench
observation does not establish pressure or lifetime performance outside that published basis.
The four hairpins bend at the same R14 and flex with their tees at every pump change; the
same limit applies to them.

The [8](MOUTH_COUNT) mouths that leave this study are drawn one bend radius long and stop, and
the fold turns all of them to face the back: V-A-I (tap), V-B-I (funnel), V-G-O (flavor A) and
V-J-O (flavor B) on the upper deck; and the four reservoir gates — V-F-O and V-E-I for A,
V-I-O and V-H-I for B — on the lower.

## Envelope

[198](ENV_X) × [162](ENV_Y) × [272](ENV_Z) mm — [8.71](ENV_L) L of bounding box over the
bodies and the tube between them, with [0](CLASHES) pairs of placed solids sharing volume.
Add one [14](STUB_LEN) mm mouth stub on each of the [8](MOUTH_COUNT2) and it is
[198](REACH_X) × [162](REACH_Y) × [286](REACH_Z).

Two figures in [`manifold_layout.py`](manifold_layout.py) are the study's own rather than any
part's. `BUTT` is the tube left outside a pair of butted quick-connects, and it is 0.

`BARB_STANDOFF` is the [5.776](BARB_STANDOFF) mm pump-to-deck authoring placement
span. The pump station retains its fitted [3](PUMP_DROP) mm downward world-Z datum.
Each of the four straight LLDPE pump tubes projects [20.03](BARB_TUBE_LEN) mm from the
modeled free BPT tube plane. The tube setting jig sets all four tips against the cartridge's
flat back, so each bottoms at its tee's stop with the cartridge seated
([pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md)).

Both pumps ride out on the cartridge. Each pump head's own housing clamps its two tubes and
carries their insertion and withdrawal reactions into the head, which the cradle and cap
hold. The tubes pass front-top's collet plate into the pump tees' branch collets, which grip
them against pressure. Pulling the cartridge drags each tee forward its collet stroke until
the plate holds the collet in and the tube draws out. With the cartridge on its meeting
magnet poles, its flat back and the plate's bay face have 0.250 mm clearance.

The complete enclosure assembly supplies the collet plate, tee anchors and tee caps, valve
trays and the printed-in SB443-IN columns. Customers replace complete
prepared pumps using the [service procedure](/hardware/service/pump-replacement.md).

## Standing it on the compressor bay

[`enclosure_assembly.py`](enclosure_assembly.py) → `enclosure-assembly.step` mates its bodies with nothing between
them: the compressor's own +X tangent to the condenser's intake face, while the pack's pose is
read from the fixed manifold's occupied envelope above the pair's crown.
The eight deck valves bear in front-top's two trays. The pump tees run in front-top's tee
anchors under their tee caps. The cold core is not one of the pair — it
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
