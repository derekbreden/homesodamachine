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
about the layout's fold line. The valve rows and pump-side tees are fixed in the enclosure;
the [permanent dock](/hardware/printed-parts/enclosure/pump-dock/README.md) supplies the
TPU receivers, keepers and prepared machined stems.

## The bodies, and the figures that set the packing

| | |
|---|---|
| 10 × valve | Beduan 12 V NC solenoid ([`reference/beduan-solenoid`](/hardware/reference/beduan-solenoid/README.md)) — [59.5](VALVE_LEN) mm collet face to collet face, straight through, port axis [11.05](VALVE_PORT_Z) mm over its own mounting plane. Two of them pack no closer than [34.25](VALVE_PITCH) mm. |
| 2 × pump | Kamoer KPHM600-SW3B17, modelled on the measured KPHM400 head ([`reference/kamoer-kphm400`](/hardware/reference/kamoer-kphm400/)) — two barbs [59.75](BARB_PITCH) mm apart on one face, both facing the same way, [19.38](BARB_INSET) mm back from the head's front face. |
| [6](TEE_COUNT2) × tee | John Guest PP0208E ([`reference/tee-connector`](/hardware/reference/tee-connector/README.md)) — run collets [21.25](TEE_RUN) mm either side of the body centre, [42.5](TEE_SPAN) mm end to end, branch reaching the same distance. |
| 0 × Y-divider | Its two outlets stand [14.7](DIVIDER_PITCH) mm apart ([`reference/y-divider`](/hardware/reference/y-divider/README.md)). |
| [8](TUBE_COUNT2) × tube | Four permanent straight 1/4" OD LLDPE receiver-to-tee tails and [4](FORE_STUB_COUNT) fixed fore S links. The four pump stems are machined PP-H components, supplied on the prepared pumps. |

## Frame

X is width, mirrored about x = 0 — channel A west, channel B east, each over its own pump. Y is
depth; the two flavour mouths leave out the back (+Y) and the other four are turned onto +Z. Z is
height, 0 at the pumps' own floor. The unshifted authoring deck references are z
[90.81](DECK_Z) and [151.76](UPPER_Z); the fixed fore and aft groups carry the explicit
offsets described below.

## Four limbs, folded in two

A fixed pump-side tee takes its prepared pump stem through a permanent TPU receiver
and straight tail on its BRANCH. Its RUN lies across the head's face, giving each pump
two parallel lanes [59.75](BARB_PITCH2) mm apart.
Every valve is straight through and every junction's run takes two valve ports, so a lane is
one line of valves and tees, front to back. Three interior pairs are butted collet to collet;
the four pump-side tees meet V-E/F/H/I through stationary fore S links. Their branch
axes align with the prepared pump stems and permanent receivers.

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

## The fold

The four connections across the fold — fluid-9, 17, 19 and 27 — are stationary
180° hairpins with two quarter circles and a tangent straight between them. Both
ends meet their fixed collets on their own axes. The radius is R[14](SPINE_R), with
[75.93](SPINE_LEN) mm for each inner hairpin and
[77.55](OUTER_SPINE_LEN) mm for each outer one. Their geometry comes from the fixed
tee and valve stations; pump service does not flex these paths.

V-G and V-J stand [8.28](OUTER_AFT_INSET) mm inboard of their pump-connected tees. Their hairpins
lean between the two axes. The valves' tray sockets and external tube routes follow their
placed ports; the tees keep their pump alignment.

**The radius and the deck separation are two different numbers.** Any 180° that ends on both
collet axes will join them, and that family is one parameter wide: the semicircle is only the
member with no middle chord in it, and it is the worst to pick, because what the pack pays for
a turn is how far it reaches past the hinge — and that reach is the RADIUS. The radius therefore
starts at the stock's floor, R[14](MIN_BEND2), and opens as the end separation decreases.

The authoring fold uses [60.95](DECK_SEP) mm separation. The fixed tee, fore-valve
and aft-valve groups also carry their explicit offsets in `manifold_layout.py`.
The [native fluid review](/hardware/printed-parts/enclosure/pump-dock/fluid-geometry-review.json)
records the occupied pack, keeper access and valve insertion routes.

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

**Y-C, Y-D, Y-F and Y-G** receive the four permanent receiver tails along the
prepared pump stems' axes, branch down in this authoring frame. **Y-A and Y-B** stand on the
inner limbs' own axes, one valve forward of the selects they feed, with their branches meeting
face to face across the mirror plane — [0.00](CROSSBAR) mm of tube between them. **NEITHER
RESERVOIR HAS A JUNCTION**: each carries two mouths of its own, so every one of the four gate
collets is a mouth of this study and leaves on its own axis, and every junction left in the pack
joins two VALVES rather than a valve and a reservoir.

Mirror-checked: [9](TWIN_COUNT) twinned pairs, worst off by [0.0000](MIRROR_OFF) mm.

## How each connection is made

[3](BUTT_COUNT) of the [17](SEGMENT_COUNT) segments the topology names between these bodies
are collet butted to collet: tube in both quick-connects, none between them, no solid drawn.
[4](STRAIGHT_COUNT) pump branches contain a prepared machined stem, permanent TPU
receiver and 18.175 mm straight LLDPE tail. The [4](FORE_STUB_COUNT) connections from
those fixed tees to V-E/F/H/I have [15.2531](FORE_STUB_EXPOSED) mm exposed R14 S paths.
Add the actual insertion inside each fitting for their finished blanks.
[4](SPINE_COUNT) are the fold's stationary 180° turns and
[2](QUARTER_COUNT2) are the source quarter turns above. The hairpin and source
routes contain [14](CORNER_COUNT) formed corners at the stock's
[14](MIN_BEND) mm minimum radius; each fore S link adds two reverse arcs.

The [8](MOUTH_COUNT) mouths that leave this study are drawn one bend radius long and stop, and
the fold turns all of them to face the back: V-A-I (tap), V-B-I (funnel), V-G-O (flavor A) and
V-J-O (flavor B) on the upper deck; and the four reservoir gates — V-F-O and V-E-I for A,
V-I-O and V-H-I for B — on the lower.

## Envelope

[198](ENV_X) × [166](ENV_Y) × [279](ENV_Z) mm — [9.14](ENV_L) L of bounding box over the
bodies and the tube between them, with [0](CLASHES) pairs of placed solids sharing volume.
Add one [14](STUB_LEN) mm mouth stub on each of the [8](MOUTH_COUNT2) and it is
[198](REACH_X) × [166](REACH_Y) × [293](REACH_Z).

Two figures in [`manifold_layout.py`](manifold_layout.py) are the study's own rather than any
part's. `BUTT` is the tube left outside a pair of butted quick-connects, and it is 0.

`BARB_STANDOFF` is the [5.776](BARB_STANDOFF) mm pump-to-deck authoring placement
span. The pump station retains its fitted [3](PUMP_DROP) mm downward world-Z datum.
Four smooth prepared stems project [9.85](BARB_TUBE_LEN) mm from the modeled free
BPT tube plane. Their production setting uses the cartridge's actual flat aft
face: all four tips lie 7.746 mm aft of it, at machine Y87.015 mm.

Both pumps ride out on the cartridge. Their integral stem flanges transfer
insertion and withdrawal reactions into the lower cradle, while the cap closes
upward escape. The four stems enter the TPU funnels and six-millimetre tight lands.
A rigid wall locates each receiver in X/Z and one flat interior keeper captures Y.
The receiver remains in the wall when the cartridge is withdrawn; its permanent
18.175 mm rear tail and commercial tee stay fixed. The stem tips remain 0.50 mm
short of the receiver shoulders with the cartridge on its dedicated outboard stop
lands. The broad cartridge and wall planes retain 0.246 mm clearance.

The standalone study draws the four short pump-axis spans and permanent tails.
The [complete enclosure assembly](enclosure_assembly.py) supplies the manufactured
flanged-stem geometry, installed TPU envelopes, flat keepers, rear cuff support,
fixed tee saddles and positive SB443-IN mounts. The customer changes complete
prepared pumps using the [service procedure](/hardware/service/pump-replacement.md).

## Standing it on the compressor bay

[`enclosure_assembly.py`](enclosure_assembly.py) → `enclosure-assembly.step` mates its bodies with nothing between
them: the compressor's own +X tangent to the condenser's intake face, while the pack's pose is
read from the fixed manifold's occupied envelope above the pair's crown.
The eight fixed valves bear in front-top's two trays and the four pump-side tees
stand in its integral saddles. The cold core is not one of the pair — it
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
