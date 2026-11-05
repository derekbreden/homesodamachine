# Tube identification collars

A printed collar threaded onto a 1/4-inch or 4 mm line, carrying the word and the colour of the rear chip under the
fitting that line goes through. The chip in [`../../enclosure/rear-identification/`](../../enclosure/rear-identification/README.md) marks the wall; this marks
the tube.

The collar has a half circle below the bore's axis and a rectangle above it for the word. The word reads along the tube. The wall chip is rectangular.

| | |
|---|---|
| tube | Ø mm 1/4" OD LLDPE on TAP, SODA and CO2; 4 mm OD on DRAIN and both FLAVOR lines |
| bore, 1/4-inch stations | Ø mm modelled; Ø mm PETG calibration estimate |
| bore, 4 mm stations | Ø4.28 mm modelled for the DRAIN and both FLAVOR tails |
| width | Ø mm |
| height | mm — mm of rectangle over the axis, its own half circle under |
| length | along the tube |
| wall | mm, with mm of it behind the lettering |
| volume | cm³ + cm³ of word |

## Where each one goes

| station | word | colour | tube |
|---|---|---|---|
| `water` | TAP | white | the customer's tap-water run, up to their angle stop |
| `carb` | SODA | blue | the umbilical's blue carbonated-water tail |
| `drain` | DRAIN | white | the umbilical's 4 mm atmospheric-vent tail |
| `co2` | CO2 | red | the customer's red tether, +Y wall of back-top to regulator |
| `flavor-a` | FLAVOR | black | the umbilical's first black flavour tail |
| `flavor-b` | FLAVOR | black | the umbilical's second black flavour tail |

One collar per chip, on the same six stations, with the same station words and fluid colours —
`bulkhead_ring.STATIONS` and `_y_wall_dimensions.chip_filaments` are what both read.

The four on the umbilical go on at [`assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)
§4, up to the braid's own end, and ride to the +Y wall of back-top on the un-sleeved tail. The other
two go on at [`assembly/finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md) §6, onto the customer's own two runs, which
ship made up in the install kit.

## The bore

Sized off the biggest tube a spool runs and not off the nominal. The extrusion is held to about
 mm, so the tube the bench meets can be Ø, and
 of bore turns any interference at all into a collar that goes on with a
mallet or not at all. It threads on end-first over a tail that is still bare, by hand.

The collar prints flat face down with the bore's axis along the bed, so the hole's crown is
unsupported. The mm diameter allowance comes from a PETG collar printed
with a 0.2 mm nozzle. For the 1/4-inch stations, Ø goes to the slicer;
the calibrated Ø estimate gives mm of slip on the
specified high tube diameter and mm on the low diameter. The production
PET-GF collar bore has no corresponding caliper record. Confirm that every finished collar
threads by hand onto its actual tube before assembling the tail.

WHAT HOLDS A COLLAR IS THE BEND THE TUBE CAME OFF THE SPOOL WITH, and not the bore. 1/4" LLDPE is
never straight through of bore, so it stands against the wall at both ends
of one and the collar stays where it is put. Neither end of the play above is close to enough to
let go of a tube that is not straight.

That play over of bore is ° of cock, and
 µm at the flag's own face — the furthest anything on the collar stands from the
line it would turn about. The same play on a chip's mm is
°. `rock()` and `flag_sway()` are those figures, and `selftest` reads the
pair against each other.

## The word

A second solid in a second colour, lying in a recess mm into the flat and
filling it flush, at [`../../enclosure/bulkhead-ring/`](../../enclosure/bulkhead-ring/README.md)'s own em and in its own face. The advance runs along the tube and the cap stands across it, in a flat that leaves
 mm one way and mm the other. FLAVOR is the longest
of the station words and what `LENGTH` is set from.

The letters are loose, one solid each. `_cadq_export._per_solid_color` writes every one as its own
component, so all of them carry the colour into `/3d`.

## Print

Flat face down on the bed, two colours to a plate — the collars off one spool, the words off the
other, and the lettering in the first layers. The half circle stands as the arch above. PET-GF,
the enclosure's own stock ([`bom.md`](/hardware/ledger/bom.md) §7).

## Files

| | |
|---|---|
| `tube_collar.py` | the part, its six stations and its selftest |
| `tube-collar-<station>.step` | one per station, both bodies in the frame `seat()` places them by |
