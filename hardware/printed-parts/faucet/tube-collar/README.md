# Tube collar

A printed collar threaded onto a 1/4" line, carrying the word and the colour of the port ring that
line goes through. The chip in [`../../enclosure/port-ring/`](../../enclosure/port-ring/README.md) marks the wall; this marks
the tube.

The outline is the chip's — a half circle below the bore's axis, a rectangle above it where the word
goes — bored for the tube instead of the fitting's barrel and run along it, so the word reads down
the line rather than across the face.

| | |
|---|---|
| tube | Ø[6.35](COLLAR_TUBE_OD) mm — 1/4" OD LLDPE, every line the customer meets |
| bore | Ø[6.73](COLLAR_BORE) mm modelled, Ø[6.63](COLLAR_BORE_PRINTED) mm printed |
| width | Ø[12](COLLAR_OD) mm |
| height | [13.05](COLLAR_TALL) mm — [7.05](COLLAR_RISE) mm of rectangle over the axis, its own half circle under |
| length | [30 mm](COLLAR_LENGTH) along the tube |
| wall | [2.635](COLLAR_WALL) mm, with [1.635](COLLAR_BACKING) mm of it behind the lettering |
| volume | [3.00](COLLAR_VOL) cm³ + [0.17](COLLAR_WORD_VOL) cm³ of word |

## Where each one goes

| station | word | colour | tube |
|---|---|---|---|
| `water` | TAP | white | the customer's tap-water run, up to their angle stop |
| `carb` | SODA | blue | the umbilical's blue carbonated-water tail |
| `co2` | CO2 | red | the customer's red tether, rear wall to regulator |
| `flavor-a` | FLAVOR | black | the umbilical's first black flavour tail |
| `flavor-b` | FLAVOR | black | the umbilical's second black flavour tail |

One collar per chip, on the same five stations, off the same five words and four spools —
`port_ring.STATIONS` and `_back_panel_dimensions.chip_filaments` are what both read.

The three on the umbilical go on at [`assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)
§4, between the cut and the sleeve, and ride to the rear wall in the un-sleeved last 3". The other
two go in the install kit, for the two runs the customer cuts in their own kitchen.

## The bore

Sized off the biggest tube a spool runs and not off the nominal. The extrusion is held to about
[0.13](COLLAR_LLDPE_TOL) mm, so the tube the bench meets can be Ø[6.48](COLLAR_TUBE_HIGH), and
[30 mm](COLLAR_LENGTH) of bore turns any interference at all into a collar that goes on with a
mallet or not at all. It threads on end-first over a tail that is still bare, by hand.

The collar prints flat face down with the bore's axis along the bed, so the hole's crown is
unsupported and sags into it: the printer takes [0.1](COLLAR_SHRINK) mm off the diameter, and the
model carries that. Ø[6.73](COLLAR_BORE) goes to the slicer and Ø[6.63](COLLAR_BORE_PRINTED) comes
off the plate — [0.15](COLLAR_SLIP) mm of slip on the biggest tube, which is the tightest a collar
comes out, and [0.41](COLLAR_CLEARANCE) mm of diametral play on the smallest.

WHAT HOLDS A COLLAR IS THE BEND THE TUBE CAME OFF THE SPOOL WITH, and not the bore. 1/4" LLDPE is
never straight through [30 mm](COLLAR_LENGTH) of bore, so it stands against the wall at both ends
of one and the collar stays where it is put. Neither end of the play above is close to enough to
let go of a tube that is not straight.

That play over [30 mm](COLLAR_LENGTH) of bore is [0.78](COLLAR_ROCK)° of cock, and
[96](COLLAR_SWAY) µm at the flag's own face — the furthest anything on the collar stands from the
line it would turn about. The same play on a chip's [2](COLLAR_CHIP_THICK) mm is
[11.59](COLLAR_CHIP_ROCK)°. `rock()` and `flag_sway()` are those figures, and `selftest` reads the
pair against each other.

## The word

A second solid in a second colour, lying in a recess [1](COLLAR_WORD_DEPTH) mm into the flat and
filling it flush — [`../../enclosure/port-ring/`](../../enclosure/port-ring/README.md)'s own construction, at its own em, in
its own face. The advance runs along the tube and the cap stands across it, in a flat that leaves
[28](COLLAR_BAND_ALONG) mm one way and [10](COLLAR_BAND_ACROSS) mm the other. FLAVOR is the longest
of the five and what `LENGTH` is set from.

The letters are loose, one solid each. `_cadq_export._per_solid_color` writes every one as its own
component, so all of them carry the colour into `/3d`.

## Print

Flat face down on the bed, two colours to a plate — the collars off one spool, the words off the
other, and the lettering in the first layers. The half circle stands as the arch above. PETG, the
enclosure's own stock ([`bom.md`](/hardware/ledger/bom.md) §7).

## Files

| | |
|---|---|
| `tube_collar.py` | the part, its five stations and its selftest |
| `tube-collar-<station>.step` | one per station, both bodies in the frame `seat()` places them by |

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/tube-collar/tube_collar.py`
