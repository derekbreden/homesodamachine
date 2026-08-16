# Port ring

A flat printed chip lying in a pocket cut into the back wall's outer face, under a through-wall
fitting's own flange. The pocket is the chip's own thickness deep, so colour and wall come out one
plane; the fitting's nut draws flange, chip and wall together. One at every crossing the wall
passes a tube through, and each carries a word.

The outline is a D on its back — a half circle below the bore's axis, the shape the port itself
is, and a rectangle above it, which is where the word goes. It takes its pocket one way up and no
other.

| | union station | CO2 station |
|---|---|---|
| fitting | John Guest PP1208E | neoFit ABU44 |
| width | Ø[36.96](RING_OD) | Ø[36.04](CO2_RING_OD) |
| bore | Ø[18](RING_BORE) | Ø[17.86](CO2_RING_BORE) |
| volume | [1.85](RING_VOL) cm³ | [1.83](CO2_RING_VOL) cm³ |

| | |
|---|---|
| thickness | [2](RING_THICK) mm — the depth the pocket is cut to, so the two faces come out one plane, and how far the fitting's flange bears outboard of the wall's stock |
| colour showing past the flange | [7.05](RING_W) mm |
| height, bottom row | [36.96](RING_TALL) mm |
| height, top row | [37.27](TOP_TALL) mm — the rectangle runs out flush with the box's top face |

The top row stands close enough to the ceiling that a rectangle stopped on its own radius would
leave a strip of wall over the colour too thin for a nozzle to lay. Those three run out on the top
face instead: fenced left, right and below, open above.
`enclosure_assembly.check_top_row` is the reading that holds them there.

## Where each one goes

| station | word | fitting | colour |
|---|---|---|---|
| `bulkhead-water` | TAP | union | white — tap water, the customer's teed-in supply |
| `bulkhead-carb` | SODA | union | blue — carbonated water, the umbilical riser |
| `co2-inlet` | CO2 | ABU44 | red — the customer's regulator tether |
| `bulkhead-flavor-a` | FLAVOR | union | black — flavour |
| `bulkhead-flavor-b` | FLAVOR | union | black — flavour |

A chip's colour is the colour of the tube that goes into it, and there are four of them. What a
colour means on the rear face is stated in
[`../back-panel/_back_panel_dimensions.py`](../back-panel/_back_panel_dimensions.py); which
fitting stands where is [`../back-panel/README.md`](README.md) §"Bulkhead array arrangement".

Both flavour stations wear the same black chip and the same word: a customer pushes black into
either one and the manifold sorts them, so nothing on that face tells A from B.

## The word

A second solid in a second colour, lying in a recess [1](WORD_DEPTH) mm into the chip's outboard
face and filling it flush. [Arial Black](WORD_FONT) at a [5](WORD_CAP) mm cap, set in the band
between the flange's edge and the top of the chip.
[`_back_panel_dimensions.word_color`](../back-panel/_back_panel_dimensions.py) picks black or
white off the chip's own luminance — white on TAP's, black on the other four.

`port_ring.WORD_WIDTHS` carries what each word measures across. The face is the system's, not this
repo's, so a machine that resolves it to something else letters a different part; `words_hold`
reads the built solid back against those figures.

## Print

Flat on the bed, two colours to a plate — the chips off one spool, the words off the other. PETG,
the enclosure's own stock ([`bom.md`](/hardware/ledger/bom.md) §7).

The pocket it drops into is struck by [`enclosure.py`](../enclosure/enclosure.py) from the same
`back_ports` stations that bore the wall — cut [2](RING_THICK) mm into the outer face, with a boss
of the same shape one rim larger standing that far inboard behind it, so the wall keeps its whole
thickness under every chip.

## Files

- `port_ring.py` — the part, and the figures the wall and the drawings read
- `port-ring-<station>.step` — one chip per station, its word's recess cut into it
- `port-ring-<station>-word.step` — that word, in the second colour

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads each chip
against the fitting it rings, the band its word stands in, and the word's own built width.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/port-ring/port_ring.py`
