# Bulkhead ring

A flat printed chip lying in a pocket cut into the +Y wall of back-top's outer face, under a
through-wall fitting's own flange. The pocket is the chip's own thickness deep, so colour and wall come out one
plane; the fitting's nut draws flange, chip and wall together. One at every crossing the wall
passes a tube through, and each carries a raised word.

All six labels are [32](RING_OD) mm wide, with [2](RING_LOWER_RADIUS) mm lower-corner radii and square upper corners. The bottom edge meets the flange envelope; the additional band above the flange carries the word. Each matching wall pocket follows the same outline with its assembly clearance. Its offset bore holds the text upright.

| | union station | CO2 station |
|---|---|---|
| fitting | John Guest PP1208E | neoFit ABU44 |
| width | [32](RING_OD) | [32.00](CO2_RING_OD) |
| bore | Ø[17.44](RING_BORE) | Ø[17.3](CO2_RING_BORE) |
| height | [30.22](RING_TALL) mm | [30.01](CO2_RING_TALL) mm |
| volume | [1.39](RING_VOL) cm³ | [1.41](CO2_RING_VOL) cm³ |

The 4 mm DRAIN chip is [32](RING_OD) × 29.789 mm, with a Ø15.3 mm barrel opening and a 2 mm mounting thickness. Its bottom edge is 11 mm below the bore axis. The DRAIN word stands 0.48 mm proud, in black on white.

| | |
|---|---|
| thickness | [2](RING_THICK) mm — the depth the pocket is cut to, so the two faces come out one plane, and how far the fitting's flange bears outboard of the wall's stock |
| additional text band above the flange | [7.05](RING_W) mm |
| rectangle above the axis | [18.789](RING_RISE) mm on water/flavour stations; [19.039](CO2_RING_RISE) mm on CO2 |

The top row stands close enough to the ceiling that a rectangle stopped on its own radius would
leave a strip of wall over the colour too thin for a nozzle to lay. Those three run out on the top
face instead: fenced left, right and below, open above.
The CO2 inlet axis stands [0.25](CO2_AXIS_DROP) mm below the water row. Its chip and pocket
carry that same extra height above the bore, keeping their tops on the enclosure's top face.
Each word is centered between its fitting's flange and the chip's top. A chip's height is
its rise plus the fitting flange radius.

The tube identification is [`../../faucet/tube-collar/`](../../faucet/tube-collar/README.md) — one collar per chip, carrying that station's word out to the end of the tube.

## Where each one goes

| station | word | fitting | colour |
|---|---|---|---|
| `bulkhead-water` | TAP | union | white — tap water, the customer's teed-in supply |
| `bulkhead-carb` | SODA | union | blue — carbonated water, the umbilical riser |
| `co2-inlet` | CO2 | ABU44 | red — the customer's regulator tether |
| `bulkhead-flavor-a` | FLAVOR | union | black — flavour |
| `bulkhead-flavor-b` | FLAVOR | union | black — flavour |
| `bulkhead-drain` | DRAIN | neoFit ABU44M-E, 4 mm | white — ASSE vent discharge |

A chip's colour matches its tube. Six stations share four filament colours. What a
colour means on the rear face is stated in
[`../y-wall-of-back-top/_y_wall_dimensions.py`](../y-wall-of-back-top/_y_wall_dimensions.py); which
fitting stands where is [`../y-wall-of-back-top/README.md`](../y-wall-of-back-top/README.md) §"Bulkhead array arrangement".

Both flavour stations wear the same black chip and the same word: a customer pushes black into
either one and the manifold sorts them, so nothing on that face tells A from B.

## The word

A second solid in a second colour, filling a recess [1](WORD_DEPTH) mm into the chip's outboard
face and standing [0.48](WORD_RAISE) mm proud of it, [2.48](WORD_TOP) mm off the pocket floor.
[Helvetica](WORD_FONT) [bold](WORD_KIND) at a [4.951](WORD_CAP) mm cap, set in the band between the
flange's edge and the top of the chip — the face the build deck and the customer's quick start are
already set in, so a customer holding that sheet beside the machine reads one typeface and not two.
At their nearest the letters stand [1.32](WORD_FLANGE_CLEAR) mm off a union's flange and
[1.58](CO2_WORD_FLANGE_CLEAR) mm off the ABU44's, so the flange lands on the chip alone.

The letters are loose — six solids for FLAVOR, nothing joining them. Nothing needs to: the chip
opens as one part carrying both bodies and the lettering is assigned the second filament, so there
is no word to place and none to lose. `_cadq_export._per_solid_color` writes each letter as its
own component, so every one of them carries the colour into `/3d`.

| | |
|---|---|
| narrowest stroke | [0.771](WORD_MIN_STROKE) mm, measured off the built letterforms |
| narrowest bridge of chip between two letters | [0.346](WORD_MIN_BRIDGE) mm — FLAVOR's, between the L and the A |
| bead | [0.42](WORD_BEAD) mm laid through a [0.4](WORD_NOZZLE) mm tip |

Every stroke is wider than one bead. The bridge is not: the slicer runs a single outer wall of chip
through FLAVOR's L and A up to the face, and the raised tops stand apart above it.

Which of black and white a chip's word letters in is
[`_y_wall_dimensions.chip_word_colors`](../y-wall-of-back-top/_y_wall_dimensions.py), one entry per
spool in `chip_filaments` beside it. The two white chips take **black**; the other three take
**white**.

`bulkhead_ring.WORD_WIDTHS` carries what each word measures across. The face is the system's, not this
repo's, so a machine that resolves it to something else letters a different part; `words_hold`
reads the built solid back against those figures.

## Print

Face up on Mark2, the inboard face on the bed and no supports: the chip off one hardened
[0.4](WORD_NOZZLE) mm nozzle and the word off the other, both in PET-GF, the enclosure's own stock
([`bom.md`](/hardware/ledger/bom.md) §7). The profile is the nameplate's, saved in
[`nameplate-001-petgf.3mf`](../nameplate/nameplate-001-petgf.3mf): a
[0.2](WORD_FIRST_LAYER) mm first layer and [0.24](WORD_LAYER) mm after it, one
[0.12](WORD_CLOSING_LAYER) mm layer closing the face at [2](RING_THICK) mm, and the letters in the
[2](WORD_RAISE_LAYERS) layers above it. Mark2 runs it at its +0.04 mm Z trim, and its
[registration correction](../../calibration/dual-nozzle-registration/mark2-registration.json) moves
every right-nozzle path, whichever colour that nozzle carries; the CAD stays nominal.

[`face-up-trial/`](face-up-trial/README.md) prepares and verifies the TAP and FLAVOR plate, and its
[print review](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-30-bulkhead-raised-mark2-v2/README.md)
records the [physical result](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-30-bulkhead-raised-mark2-v2/physical-result.json):
accepted finish and clear lettering, with mounting fit not separately reported. The
[SODA](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-04-bulkhead-soda-raised-mark2-v1/README.md)
and [CO2](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-04-bulkhead-co2-raised-mark2-v1/README.md)
rings' reviews each hold their own preparation and verification.

The pocket it drops into is struck by [`enclosure.py`](../enclosure/enclosure.py) from the same
`back_ports` stations that bore the wall — cut [2](RING_THICK) mm into the outer face, with a boss
of the same shape one rim larger standing that far inboard behind it, so the wall keeps its whole
thickness under every chip.

## Files

- `bulkhead_ring.py` — the part, and the figures the wall and the drawings read
- `bulkhead-ring-<station>.step` — one station, both bodies: the chip and the word standing in its
  recess, each carrying the colour of the spool it comes off. `bulkhead_ring.split` takes the pair
  back apart for anything that places them one at a time.
- `face-up-trial/` — the TAP and FLAVOR plate's preparation and verification

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads each chip
against the fitting it rings, the band its word stands in, the flange its letters stand beside, the
layers they print in, and the word's own built width.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py`
