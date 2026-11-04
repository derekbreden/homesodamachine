# Rear-port identification figures

[`bulkhead_ring.py`](bulkhead_ring.py) holds the figures the rear-port identification reads. It
builds no part. [`../rear-identification/`](../rear-identification/README.md) cuts the six
installed tiles and [`../../faucet/tube-collar/`](../../faucet/tube-collar/README.md) the matching
tube collars, and both take each station's word, its filament key and the lettering from here.

| station | word | filament key |
|---|---|---|
| `water` | TAP | `water` |
| `carb` | SODA | `carb` |
| `co2` | CO2 | `co2` |
| `flavor-a` | FLAVOR | `flavor` |
| `flavor-b` | FLAVOR | `flavor` |
| `drain` | OVER | `drain` |

What each key's chip and word print in is `chip_filaments` and `chip_word_colors` in
[`../y-wall-of-back-top/_y_wall_dimensions.py`](../y-wall-of-back-top/_y_wall_dimensions.py).

## The lettering

Helvetica bold at a 6.5 mm em, which is a 4.951 mm cap. The face is the system's, not this
repo's, so `WORD_WIDTHS` carries what each word measures across at that em: TAP 12.657, SODA
18.411, CO2 12.813, FLAVOR 25.952 and OVER 17.827 mm. A reader that sets a word at another em
scales those widths with it. A word fills a 1 mm recess in its label's outboard face, stands
0.48 mm proud of it (two 0.24 mm layers in the word's colour alone) and keeps 1 mm clear of the
edges of its band.

## The label envelope

`od`, `bottom`, `rise` and `THICK` are what `enclosure_assembly` reads for the wall's port
pockets, the bosses behind them and the clamp stack. A pocket is 32 mm wide plus its slip. It
runs from the fitting's flange radius below the bore axis to 18.789 mm above it, or 19.039 mm at
CO2, whose axis stands 0.25 mm lower. It is cut 2 mm into the outer face, with a boss as tall
behind it. `RING_W` is 7.05 mm: the tube collar letters its word in a band that tall, and the
line art paints each port's mark that far past its fitting.

`split` takes a two-colour label STEP back apart as `(tile, word)`. The one body on the inboard
face, y = 0, is the tile, and every other body is a letter.
