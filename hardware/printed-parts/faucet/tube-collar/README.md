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
| bore | Ø[6.3](COLLAR_BORE) mm |
| width | Ø[12](COLLAR_OD) mm |
| height | [12](COLLAR_TALL) mm — [6](COLLAR_RISE) mm of rectangle over the axis, its own half circle under |
| length | [30](COLLAR_LENGTH) mm along the tube |
| wall | [2.85](COLLAR_WALL) mm, with [1.85](COLLAR_BACKING) mm of it behind the lettering |
| volume | [2.87](COLLAR_VOL) cm³ + [0.06](COLLAR_WORD_VOL) cm³ of word |

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

Cut [0.08](COLLAR_CLEARANCE) mm under the tube, so at nominal the fit is an interference and LLDPE —
the soft half of the pair — takes it. The tube is an extrusion held to about
[0.13](COLLAR_LLDPE_TOL) mm, and one at the low end of that leaves [0.08](COLLAR_CLEARANCE) mm of
diametral play. The collar threads on end-first over a tail that is still bare.

That play over [30](COLLAR_LENGTH) mm of bore is [0.15](COLLAR_ROCK)° of cock, and
[16](COLLAR_SWAY) µm at the flag's own face — the furthest anything on the collar stands from the
line it would turn about. The same play on a chip's [2](COLLAR_CHIP_THICK) mm is
[2.29](COLLAR_CHIP_ROCK)°. `rock()` and `flag_sway()` are those figures, and `selftest` reads the
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
