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
| volume | [1.87](RING_VOL) cm³ | [1.84](CO2_RING_VOL) cm³ |

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
face and filling it flush. [Helvetica](WORD_FONT) [bold](WORD_KIND) at a [4.951](WORD_CAP) mm cap,
set in the band between the flange's edge and the top of the chip — the face the build deck and the
customer's quick-start sheet are already set in, so a customer holding that sheet beside the
machine reads one typeface and not two.

Behind the lettering a bar [0.3](WORD_TIE) mm thick lies across the letters' feet, which makes the
word ONE body. That earns its place twice: the second colour is a single connected run rather than
six loose islands per word to place and to lose, and the reader `/3d` runs surfaces a colour only
for a single-solid component, so an untied word is lettering the viewer draws grey. It runs along
the baseline and no higher, so it stays clear of the counters in O, A, P, R and D — a bar at
mid-cap would cut those off the chip's own floor and leave them as islands too.

| | |
|---|---|
| narrowest stroke | [0.771](WORD_MIN_STROKE) mm, measured off the built letterforms |
| nozzle | [0.2](WORD_NOZZLE) mm — about four beads to a stroke |

Which of black and white each chip takes is
[`_back_panel_dimensions.chip_word_colors`](../back-panel/_back_panel_dimensions.py), decided
against the filament that chip actually prints in rather than against the tube colour it is named
for. The two saturated hues do not answer alike: red 30201 takes **black** and navy 30604 takes
**white**.

`port_ring.WORD_WIDTHS` carries what each word measures across. The face is the system's, not this
repo's, so a machine that resolves it to something else letters a different part; `words_hold`
reads the built solid back against those figures, and against being one solid.

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
