# Fake countertop

The bench stand that stands in for a counter: an inverted U the size of the H2C's bed,
[320 × 310 mm](FCT_SLAB) across and [220 mm](FCT_HEIGHT) tall, one thickness of
[12 mm](FCT_T) throughout. One faucet clamps through its [34.92 mm](FCT_HOLE) hole, the
1-3/8" the shank is sized for, and the umbilical hangs and bends under the slab with
[208 mm](FCT_CLEAR) clear: the shank and the umbilical stub reach [104 mm](FCT_UMBILICAL)
below the counter's top face with the gather's bend, and the rest is hand room. The two
open sides are where the umbilical leaves and where a camera looks in.

**Status: CAD checked, print untested.** This is bench tooling, separate from the machine
assembly and its BOM.

| File | Use |
|---|---|
| [`fake_countertop.py`](fake_countertop.py) | Generator, dimensions and geometric checks |
| [`fake-countertop.stl`](fake-countertop.stl) | The print, show face down |
| [`fake-countertop.step`](fake-countertop.step) | Exact, material-coloured solid |

## Print

Print in the owned PET-GF15 at 15% infill, show face on the textured plate, legs up:
nothing needs support, and the plate's texture is the counter's surface. The slab's show
edges are rounded at [6 mm](FCT_SHOW_EDGE_R) down to the 45-degree point of the round and
run out to the plate at 45 degrees over the last [3.5 mm](FCT_RUNOUT), which is what an
edge on the plate can be printed as; the four outer corners are rounded at
[6 mm](FCT_CORNER_R), the legs' free edges and feet at [3 mm](FCT_FOOT_R). The solid is
[2711 cm³](FCT_VOLUME) before infill; the slice says what it weighs.

## Use

Stand it legs down. The faucet's shank goes through the hole with its plate and gasket on
the show face and the under-counter plate and nut below, the way the counter takes them.
The slab is thinner than a counter (the install guide takes 3/4 to 1-1/2 in), and the nut
runs up the shank to it.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/fixtures/fake-countertop/fake_countertop.py`
