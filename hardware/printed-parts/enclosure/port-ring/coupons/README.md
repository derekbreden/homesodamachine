# Port-ring coupons

Four combs. Each one sweeps one of the figures the [chip's lettering](../README.md) is struck
from and stands the other three at the part's own numbers, so a tooth that comes out badly names
what did it. [20](CPN_TEETH) teeth over the four, [12.08](CPN_VOL) cm³ of filament.

| coupon | sweeps | teeth | size | spine holes |
|---|---|---|---|---|
| `cap` | the em the word is set at | 5 | [43.3 × 48.3](CPN_SIZE_CAP) mm | 1 |
| `relief` | how far the word stands past the face | 5 | [37.2 × 48.7](CPN_SIZE_RELIEF) mm | 2 |
| `depth` | how deep the recess is cut | 5 | [37.2 × 48.7](CPN_SIZE_DEPTH) mm | 3 |
| `fit` | the air the recess leaves round the word | 5 | [37.2 × 48.7](CPN_SIZE_FIT) mm | 4 |

## A tooth is the band

The lettering a customer sees is the strip between the fitting's flange edge and the chip's own
top edge — [7.359](CPN_BAND) mm, fixed at both ends. A tooth carries that strip at full size:
the cap, the rim of chip standing over it, and the word's own margins. Under the word it carries
[2](CPN_BELOW) mm and stops; on the chip that is 30 mm of material hidden under the flange.

The specimen is **[FLAVOR](CPN_WORD)** on every tooth — the longest of the five words, two
counters that close, one that comes to a point, two diagonals meeting in a stroke narrower than
either. Two of the five chips wear it.

## The bead is [0.22](CPN_LINE_W) and not 0.2

The nozzle bore meters; it does not set the width of what comes out. The bead is laid at the
width `line_width` asks for and squashed to [0.08](CPN_LAYER_H) mm against the layer below.
`line_width` is also the slicer's own divisor: a feature's width over the bead is how many
perimeters fit in it, and the remainder is gap fill or nothing. `wall_generator` on that profile
is **classic**, which lays whole beads and gap-fills the remainder; `detect_thin_wall` is off, so
anything under one bead is dropped rather than thinned.

The part's own em stands its narrowest stroke on [3.65](CPN_PART_BEADS) beads — two whole
perimeters and a ribbon of gap fill down the middle of every stroke. CO2, the finest of the five
words, lands at [3.50](CPN_CO2_BEADS) on the same em. The five words are within 4% of each other,
so one em cannot stand all five on whole beads; it can stand one, and the rest fall within a
sixth of a bead of it.

## The narrowest thing on a chip is not a stroke

It is the bridge of chip standing between two letters — [0.346](CPN_GAP) mm on the specimen at
the part's own em, between the L and the A. That is [1.57](CPN_GAP_BEADS) beads, where the
narrowest stroke is [3.65](CPN_PART_BEADS). The strokes come off the word's spool and the bridges
off the chip's, both through the same nozzle at the same width, so the bridge is what runs out
first. It scales with the em like everything else, which puts a floor under how small the
lettering can go that is nothing to do with the strokes.

### `cap` — one em per tooth, solved backwards from the bead

The band does not grow, so a cap grows out of the rim of chip over it.

| tooth | em | cap | stroke | rim | bridge | word |
|---|---|---|---|---|---|---|
| 1 | [4.454](CPN_EM1) | [3.393](CPN_CAP1) | [2.50](CPN_BEADS1) beads | [1.983](CPN_RIM1) mm = [9.01](CPN_RIMB1) beads | [1.08](CPN_GAPB1) beads | [17.78](CPN_WIDE1) mm |
| 2 | [5.345](CPN_EM2) | [4.071](CPN_CAP2) | [3.00](CPN_BEADS2) beads | [1.644](CPN_RIM2) mm = [7.47](CPN_RIMB2) beads | [1.29](CPN_GAPB2) beads | [21.34](CPN_WIDE2) mm |
| 3 | [6.500](CPN_EM3) | [4.951](CPN_CAP3) | [3.65](CPN_BEADS3) beads | [1.204](CPN_RIM3) mm = [5.47](CPN_RIMB3) beads | [1.57](CPN_GAPB3) beads | [25.95](CPN_WIDE3) mm |
| 4 | [7.127](CPN_EM4) | [5.429](CPN_CAP4) | [4.00](CPN_BEADS4) beads | [0.965](CPN_RIM4) mm = [4.39](CPN_RIMB4) beads | [1.72](CPN_GAPB4) beads | [28.46](CPN_WIDE4) mm |
| 5 | [8.018](CPN_EM5) | [6.107](CPN_CAP5) | [4.50](CPN_BEADS5) beads | [0.626](CPN_RIM5) mm = [2.85](CPN_RIMB5) beads | [1.94](CPN_GAPB5) beads | [32.01](CPN_WIDE5) mm |

Tooth 1 stands its bridges on [1.08](CPN_GAPB1) beads. Everything smaller than it letters a word
the chip cannot reach between.

Tooth 3 is the part as it stands. Teeth 4 and 5 stand their caps in rims under the
[1](CPN_MARGIN) mm the part allows: a whole-bead stroke at [7.127](CPN_FOUR_EM) em wants a
[5.429](CPN_FOUR_CAP) mm cap and leaves [0.965](CPN_FOUR_RIM) mm of chip over it, which is four
wall loops and a tenth of a bead. Whether that rim comes off the plate is what decides whether a
whole-bead stroke is available to this part at all.

### `relief` — 0 to 4 whole layers proud of the face

A flush word's visible edge is a seam between two colours laid in the same layer. A raised word's
is the letter's own free edge, and the layers above the chip's face carry one colour alone.

### `depth` — 3, 6, 9, 12 and 18 layers of second filament

Two readings on one comb. The second colour stands over the first rather than beside it on the
[flavor](CPN_FLUID) pair, so this is where white stops reading grey over black. And the recess
depth *is* the count of layers carrying two colours: the part's [1](CPN_PART_DEPTH) mm is
[12.5](CPN_PART_LAYERS) of them, and the shallowest tooth is three.

That count is what a colour change is charged against. On the sliced plate both spools stand on
one nozzle, so a change is a filament change, and `flush_volumes_matrix` charges
[990](CPN_FLUSH) mm³ for a black-to-white-and-back round trip. One nozzle per spool takes that to
the priming the tower does anyway.

### `fit` — 0 to 0.08 mm of air all round the word

The part cuts its recess with the word itself and leaves none. Two nozzles hold one origin
between them, and what they are out by lands here: a seam closing on one side of every stroke and
opening on the other.

The sweep is bounded by the bridge. A tooth takes twice its own figure out of
[0.346](CPN_GAP) mm — one side of the bridge per letter — so at [0.063](CPN_GAP_CEIL) mm the
chip between the L and the A falls to a single bead, and the last tooth stands past that.

A tooth reads two ways. The gap that comes out even all round is the clearance this machine
wants; and where a tooth is tight on one side of a stroke and open on the other, the direction it
leans is the direction the two nozzles disagree.

The recess is grown by unioning the letterforms with [8](CPN_KERNEL) copies of themselves round a
circle of the offset, which leaves a corner short by 7.6% of it — 6 µm on the widest tooth here.

## Reading a comb

Holes down the spine count which coupon it is — `cap` one, `fit` four. Steps down the free end
count which tooth: tooth 1 is the shortest and each one below it is [1.1](CPN_STEP) mm longer.
Neither mark is in the second colour, which two of these coupons sweep.

## Print

Flat on the bed, face up, two colours to a plate — the comb off one spool and every word off the
other. [PETG Basic Black 30105](CPN_CHIP_FILAMENT) and white, the [flavor](CPN_FLUID) chip's own
pair, which is the direction the word's colour stands over the chip's. Running a comb a second
time with the two spools exchanged reads the other direction, which is what the other three chips
letter in.

All four stand on one plate — [43.3 × 48.3](CPN_SIZE_CAP) and three at
[37.2 × 48.7](CPN_SIZE_RELIEF) mm, 155 mm across the bed with the wipe tower beside them.

A STEP carries one component per solid, so Bambu Studio opens a comb as the comb and one part per
word. The words take the second filament together.

`filament_map` on that plate stands both spools on one nozzle. Two 0.2 nozzles and two filaments
takes one spool each, and a colour change costs the tower's priming instead of a flush.

Settings as sliced in [`../port-ring-water.3mf`](../port-ring-water.3mf): Bambu Lab H2C, 0.2
nozzle, `0.08mm High Quality`, [0.22](CPN_LINE_W) mm line width, [4](CPN_WALLS) wall loops,
textured PEI, no ironing.

## Files

- `port_ring_coupons.py` — the combs, and the figures the README reads
- `port-ring-coupon-<figure>.step` — one comb, both bodies: the comb and every word standing on
  it, each carrying the colour of the spool it comes off

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads each tooth
against the band it stands in, the chip it stands for, and the layers the plate lays.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/port-ring/coupons/port_ring_coupons.py`
