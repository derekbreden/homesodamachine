# Rear-port identification figures

[`numbers.rs`](numbers.rs) holds the figures the rear-port identification reads, and
[`bulkhead_ring.py`](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py) serves them with the label envelope. Neither builds a part. [`../rear-identification/`](../rear-identification/README.md) cuts the six
installed tiles and [`../../faucet/tube-collar/`](../../faucet/tube-collar/README.md) the matching
tube collars, and both take each station's word, its filament key and the lettering from here.

| station | word | filament key |
|---|---|---|
| `water` | TAP | `water` |
| `carb` | SODA | `carb` |
| `co2` | CO2 | `co2` |
| `flavor-a` | FLAVOR | `flavor` |
| `flavor-b` | FLAVOR | `flavor` |
| `drain` | DRAIN | `drain` |

What each key's chip and word print in is shared-data's `color.chips`, in
[`tools/hsm/shared-data/src/color.rs`](/tools/hsm/shared-data/src/color.rs).

## The lettering

Helvetica bold at a 6.5 mm em, which is a 4.951 mm cap. The face is the system's, not this
repo's, so `WORD_WIDTHS` carries what each word measures across at that em: TAP 12.657, SODA
18.411, CO2 12.813, FLAVOR 25.952 and DRAIN 19.671 mm. A reader that sets a word at another em
scales those widths with it. A word fills a 1 mm recess in its label's outboard face, stands
0.48 mm proud of it (two 0.24 mm layers in the word's colour alone) and keeps 1 mm clear of the
edges of its band.

## The label envelope

`od`, `bottom`, `rise` and `THICK` are what `enclosure_assembly` reads for the wall's port
pockets, the bosses behind them and the clamp stack. A pocket is 32 mm wide plus its slip. It
runs from the fitting's flange radius below the bore axis to 18.789 mm above it, or 19.039 mm at
CO2, whose axis stands 0.25 mm lower. It is cut 2 mm into the outer face, with a boss as tall
behind it. `RING_W` is 7.05 mm: the tube collar letters its word in a band that tall.

`split` takes a two-colour label STEP back apart as `(tile, word)`. The one body on the inboard
face, y = 0, is the tile, and every other body is a letter.
