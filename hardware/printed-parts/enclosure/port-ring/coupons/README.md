# Port-ring coupons

**A coupon is a [port ring](../README.md).** Same D outline, same Ø[36.96](CPN_OD) mm width, same
bore, same [2](CPN_THICK) mm thickness, same word in the same band — `port_ring`'s own builders
cut it, so it drops into the wall's pocket like any other chip.

[6](CPN_N) chips, one plate: [115 × 77](CPN_PLATE) mm and [11.65](CPN_VOL) cm³. **Each one is a
decision, not a step in a sweep.**

**The plate was printed and the proposal was not taken.** Nothing on it read better than what
the part already stood at, so the part keeps its em and its recess and the word stays flush.
The sections below are the case each chip was cut to make; the print is the answer to it.

## What the plate proposed

| | the part now | proposed |
|---|---|---|
| em | [6.5](CPN_PART_EM) → cap [4.951](CPN_PART_CAP), stroke [3.65](CPN_PART_BEADS) beads | **[7.127](CPN_EM)** → cap [5.429](CPN_CAP), stroke **[4](CPN_WALLS) whole beads** |
| word stands | flush | **[0.16](CPN_RELIEF) mm proud — [2](CPN_RELIEF_L) layers** |
| recess | [1](CPN_PART_DEPTH) mm — [12.5](CPN_PART_LAYERS) layers | **[0.48](CPN_DEPTH) mm — [6](CPN_DEPTH_L) layers** |

Chip 5 carries all three at once. Chips 1 and 3 stand either side of the em so the recommendation
has something to be read against, and chip 6 carries the recommendation on the word that cannot
take it.

## The six

| | chip | word | em | cap | stroke | rim | recess | relief | what it reads |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [smaller](CPN_NAME1) | FLAVOR | [5.345](CPN_EM1) | [4.071](CPN_CAP1) | [3.00](CPN_BEADS1) beads | [1.644](CPN_RIM1) mm | [12](CPN_DEPTH1) | [0](CPN_RELIEF1) | one whole bead down |
| 2 | [matched](CPN_NAME2) | FLAVOR | [7.127](CPN_EM2) | [5.429](CPN_CAP2) | [4.00](CPN_BEADS2) beads | [0.965](CPN_RIM2) mm | [12](CPN_DEPTH2) | [0](CPN_RELIEF2) | **the em to take** |
| 3 | [larger](CPN_NAME3) | FLAVOR | [8.018](CPN_EM3) | [6.107](CPN_CAP3) | [4.50](CPN_BEADS3) beads | [0.626](CPN_RIM3) mm | [12](CPN_DEPTH3) | [0](CPN_RELIEF3) | half a bead past what the band takes |
| 4 | [raised](CPN_NAME4) | FLAVOR | [7.127](CPN_EM4) | [5.429](CPN_CAP4) | [4.00](CPN_BEADS4) beads | [0.965](CPN_RIM4) mm | [12](CPN_DEPTH4) | [2](CPN_RELIEF4) | **the relief to take** |
| 5 | [recommended](CPN_NAME5) | FLAVOR | [7.127](CPN_EM5) | [5.429](CPN_CAP5) | [4.00](CPN_BEADS5) beads | [0.965](CPN_RIM5) mm | [6](CPN_DEPTH5) | [2](CPN_RELIEF5) | **all three, and the recess to take** |
| 6 | [co2](CPN_NAME6) | CO2 | [7.127](CPN_EM6) | [5.429](CPN_CAP6) | [3.84](CPN_BEADS6) beads | [1.196](CPN_RIM6) mm | [6](CPN_DEPTH6) | [2](CPN_RELIEF6) | the same on the word that misses |

Every adjacent pair moves one thing: 1→2→3 the em, 2→4 the relief, 4→5 the recess, 5→6 the word.

Which chip is which is a row of Ø[1.5](CPN_MARK_D) mm dimples [0.4](CPN_MARK_DEPTH) mm into the
**back** — the face that lands on the pocket floor. The face a customer reads carries nothing a
chip in the wall does not; turn one over to count.

## Why the em is [7.127](CPN_EM)

The nozzle bore meters; it does not set the width of what comes out. The bead is laid at the
width `line_width` asks for — [0.22](CPN_LINE_W) mm — and squashed to [0.08](CPN_LAYER_H) mm
against the layer below. That figure is also the slicer's own divisor: a feature's width over the
bead is how many perimeters fit in it, and the remainder is gap fill or nothing. `wall_generator`
on that profile is **classic**, so what does not divide becomes gap fill; `detect_thin_wall` is
off, so anything under one bead is dropped rather than thinned.

At [7.127](CPN_EM) em the narrowest stroke is [0.88](CPN_STROKE) mm — exactly
[4](CPN_WALLS) beads, which is exactly the [4](CPN_WALLS) wall loops the profile lays. **Every
stroke comes out all perimeter: no gap fill down its middle and no infill inside it.** The part's
own [6.5](CPN_PART_EM) lands at [3.65](CPN_PART_BEADS) — two whole perimeters and a ribbon of gap
fill in every limb, which is the worst place on the scale to sit.

**It is also as large as this part goes.** Five beads wants a [6.786](CPN_FIVE_CAP) mm cap in a
[7.359](CPN_BAND) mm band and leaves [0.287](CPN_FIVE_RIM) mm of rim, which is one bead. Four
beads leaves [0.965](CPN_RIM) — [4.39](CPN_RIMB) beads, so the rim still gets its full
[0.88](CPN_WALLSTACK) mm wall stack and a tenth of a bead over. There is no larger whole-bead em
on this chip, which is why `matched` and "the biggest that works" are the same chip.

The cost is that [0.965](CPN_RIM) sits [0.035](CPN_RIM_SHORT) mm under the [1](CPN_MARGIN) mm the
part nominally allows over a cap. That is a round number, not a physical one — the physical floor
is the wall stack, and the rim clears it. **Chip 2 is on the plate to confirm that.**

## Why the relief is [2](CPN_RELIEF_L) layers

One layer is inside the variation of a top surface, and it is the single course most easily
dragged by a nozzle crossing it. Two gives an edge that catches light and a step a fingertip
finds. Past two it is a lip on the back of a kitchen appliance that collects what the room has
and reads no better at this cap height.

It also takes the colour seam off the visible face. A flush word meets the chip in the same
layer, so whatever the two nozzles disagree about lands on the edge a customer looks at. A raised
word's visible edge is its own free edge, with the seam two layers below it.

## Why the recess is [6](CPN_DEPTH_L) layers

Every layer from the recess floor up to the face carries both colours. `filament_map` on that
plate stands both spools on **one nozzle**, so each of those layers is a filament change and
`flush_volumes_matrix` charges [990](CPN_FLUSH) mm³ for a black-to-white-and-back round trip. The
recess is the largest cost on the plate, and the part currently cuts [12.5](CPN_PART_LAYERS)
layers of it — half of them buying nothing but depth behind lettering whose back nobody sees.

Six is the recommendation and chip 5 is what confirms it: six layers of white PETG standing over
black, which is the direction the flavour pair reads in.

(Independently of the recess: two 0.2 nozzles and two filaments should take one spool each, which
turns every one of those changes into the tower's own priming instead of a flush.)

## The bridge, which is what really sets the floor

The narrowest thing on a chip is not a stroke. It is the bridge of chip standing between two
letters — 0.346 mm on FLAVOR at the part's own em, between the L and the A, which is 1.57 beads
where the narrowest stroke is [3.65](CPN_PART_BEADS). Strokes come off the word's spool and
bridges off the chip's, both through the same nozzle at the same width, so the bridge runs out
first.

It scales with the em, so the recommendation improves it: at [7.127](CPN_EM) the bridge is 1.72
beads rather than 1.57. Going *smaller* is what the bridge forbids — chip 1 at
[5.345](CPN_EM1) holds 1.29 beads, and below about 4.6 em nothing reaches between the letters at
all.

## Why chip 6 is CO2

The five words are within 4% of each other at one em, so **one em cannot stand all five on whole
beads.** It can stand one. FLAVOR is the one worth standing, being the longest and the tightest
in bridges — and CO2 then lands at [3.84](CPN_CO2_BEADS) beads, the furthest miss of the set.

Chip 6 is the recommendation lettered CO2, so the plate says whether a sixth of a bead off
matters. Its band is wider, so it keeps [1.196](CPN_CO2_RIM) mm of rim at the same cap, above
the [1](CPN_MARGIN) mm rule that FLAVOR sits just under. It is drawn in the flavour pair rather
than its own red, so the plate runs on two spools.

## Print

Flat on the bed, face up, two colours — the chips off [PETG Basic Black 30105](CPN_CHIP_FILAMENT)
and the letters off white, the flavour chip's own pair, which is the direction the second colour
stands over the first. Running the plate again with the spools exchanged reads the other
direction, which is what the other three stations letter in.

A STEP carries one component per solid, so Bambu Studio opens this as [6](CPN_N) chip parts and
one part per letter. The letters take the second filament together.

Settings as sliced in [`../port-ring-water.3mf`](../port-ring-water.3mf): Bambu Lab H2C, 0.2
nozzle, `0.08mm High Quality`, [0.22](CPN_LINE_W) mm line width, [4](CPN_WALLS) wall loops,
textured PEI, no ironing.

## Files

- `port_ring_coupons.py` — the six chips, the decisions they carry, and the figures this README
  reads
- `port-ring-coupons.step` — the plate: six port rings and the letters standing in each, every
  body carrying the colour of the spool it comes off

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads every chip
back off the STEP against the port ring it is one of — outline, height, thickness and bore — and
then against the decision it carries.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/port-ring/coupons/port_ring_coupons.py`
