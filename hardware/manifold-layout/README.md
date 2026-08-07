# Manifold layout

The ten flavor valves, both KPHM400 pumps and the seven junctions between them, placed with
nothing else in the box — no enclosure, no tray, no reservoir, no nozzle, no hopper, no
carbonator. The connections are
[`topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)'s. Free here: where every
body stands, how it is turned, and which of a junction's three ports takes its run.

Built by [`manifold_layout.py`](manifold_layout.py) → `manifold-layout.step`, and the three
elevations beside it.

![plan](manifold-layout.top.png)

## The bodies, and the figures that set the packing

| | |
|---|---|
| 10 × valve | Beduan 12 V NC solenoid ([`reference/beduan-solenoid`](/hardware/reference/beduan-solenoid/README.md)) — [59](VALVE_LEN) mm collet face to collet face, straight through, port axis [11.3](VALVE_PORT_Z) mm over its own mounting plane. Two of them pack no closer than [34.25](VALVE_PITCH) mm. |
| 2 × pump | Kamoer KPHM400 ([`reference/kamoer-kphm400`](/hardware/reference/kamoer-kphm400/)) — two barbs [57](BARB_PITCH) mm apart on one face, both facing the same way, [20.38](BARB_INSET) mm back from the head's front face. |
| 7 × tee | John Guest PP0208E ([`reference/tee-connector`](/hardware/reference/tee-connector/README.md)) — run collets [20.07](TEE_RUN) mm either side of the body centre, [40.14](TEE_SPAN) mm end to end, branch reaching the same distance. |
| 1 × elbow | John Guest PP0308E ([`reference/elbow-connector`](/hardware/reference/elbow-connector/README.md)) — [19.56](ELBOW_LEG) mm from bend corner to each collet face. |
| 0 × Y-divider | Its two outlets stand [14.7](DIVIDER_PITCH) mm apart ([`reference/y-divider`](/hardware/reference/y-divider/README.md)). |
| 2 × tube | 1/4" OD LLDPE, both straight. |

## Frame

X is width, mirrored about x = 0 — channel A (pump B) west, channel B (pump A) east. Y is
depth: the front (−Y) carries the tap, the hopper and both nozzles; the back (+Y) carries all
three reservoir lines. Z is height, 0 at the pumps' own floor.

## Four limbs

A tee dropped on a pump barb by its BRANCH puts its RUN across the head's face, so each pump
hands out two parallel lanes [57](BARB_PITCH2) mm apart, one branch reach off its own skin.
Every valve is straight through and every junction's run takes two valve ports, so a lane is
one line of valves and tees butted collet to collet, front to back. `LIMB_PITCH` is that
spacing and it is a knob: `HSM_LIMB_PITCH=<mm>` steps both tees toward the pump's axis and
draws the leaning tube each barb then needs to reach its tee.

```
                          front  (tap · hopper · nozzle A · nozzle B)
                            ↑
    A2   x [-78.50](LIMB_OUT_XW)          V-G · Y-D · V-F · Y-E
    A1   x [-21.50](LIMB_IN_XW)    V-A · Y-A · V-C · Y-C · V-E
    ─────────────────────────────────────────────────────────  mirror plane
    B1   x [+21.50](LIMB_IN_XE)    V-B · Y-B · V-D · Y-F · V-H
    B2   x [+78.50](LIMB_OUT_XE)          V-J · Y-G · V-I
                            ↓
                          back   (reservoir A · reservoir B draw · reservoir B fill)
```

All four limbs share one port-axis height, z [82.68](DECK_Z), which stands
[8.77](DECK_GAP) mm over the pump heads' crowns. The two inner limbs leave
[8.75](INNER_GAP) mm between their valve bodies across the mirror plane.

**Y-C, Y-D, Y-F and Y-G** sit on the four barbs, branch down. **Y-A and Y-B** stand on the
inner limbs' own axes, one valve forward of the selects they feed, with their branches facing
each other across the mirror plane — [2.86](CROSSBAR) mm of tube between them. **Y-E** stands
in line behind V-F and faces V-E-I across the pump, reached by an elbow on that collet and
[17.38](F16_LEN) mm of tube.

## How each connection is made

[17](BUTT_COUNT) of the [19](SEGMENT_COUNT) segments the topology names between these bodies
are collet butted to collet: tube in both quick-connects, none between them, no solid drawn.
The other [2](TUBE_COUNT) are the straight lengths above. No corner turns anywhere in the
manifold; the tightest centreline radius 1/4" LLDPE takes is [25.4](MIN_BEND) mm.

The [7](MOUTH_COUNT) mouths that leave this study are drawn one bend radius long and stop:
V-A-I (tap), V-B-I (hopper), V-G-O (nozzle A) and V-J-O (nozzle B) out the front; Y-E-2
(reservoir A), V-H-I (reservoir B draw) and V-I-O (reservoir B fill) out the back.

## Envelope

[191](ENV_X) × [297](ENV_Y) × [128](ENV_Z) mm — [7.28](ENV_L) L of bounding box over the
bodies and the tube between them, with [0](CLASHES) pairs of placed solids sharing volume.
Add one [25.4](STUB_LEN) mm mouth stub on each of the seven and it is
[191](REACH_X) × [348](REACH_Y) × [128](REACH_Z).

Two figures in [`manifold_layout.py`](manifold_layout.py) are the study's own rather than any
part's. `BUTT` is the tube left outside a pair of butted quick-connects, and it is 0.
`BARB_STANDOFF` is the climb given to a barb over and above what `LIMB_PITCH` demands, and it
is 0 as well; a barb is not a quick-connect, so that one is a modelling convenience, and z
[82.68](DECK_Z2) rides on it one millimetre for one.

![front](manifold-layout.front.png)

![right](manifold-layout.right.png)

## Regenerate

```
tools/cad-venv/bin/python hardware/manifold-layout/manifold_layout.py
```

Prints the limbs, every connection and how it is made, the seven mouths, the envelope and the
clash check, and writes the figures above back into this file.

## Sources
[value](NAME) texts are updated by:
- `/hardware/manifold-layout/manifold_layout.py`
