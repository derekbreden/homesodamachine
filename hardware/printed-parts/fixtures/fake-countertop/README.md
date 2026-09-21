# Fake countertop

The bench stand that stands in for a counter: an inverted U as large as the H2C's plate
takes under its left nozzle inside the 15 mm border every print here keeps, [295 × 290 mm](FCT_SLAB) across and [220 mm](FCT_HEIGHT) tall,
one thickness of [12 mm](FCT_T) throughout. One faucet clamps through its
[34.92 mm](FCT_HOLE) hole, the 1-3/8" the shank is sized for, and the umbilical hangs and
bends under the slab with [208 mm](FCT_CLEAR) clear: the shank and the umbilical stub reach
[104 mm](FCT_UMBILICAL) below the counter's top face with the gather's bend, and the rest is
hand room. The two open sides are where the umbilical leaves and where a camera looks in.

**Status: CAD checked, print untested.** This is bench tooling, separate from the machine
assembly and its BOM.

| File | Use |
|---|---|
| [`fake_countertop.py`](fake_countertop.py) | Generator, dimensions and geometric checks |
| [`fake-countertop.stl`](fake-countertop.stl) | The print, show face down |
| [`fake-countertop.step`](fake-countertop.step) | Exact, material-coloured solid |
| [`prepare_print.py`](prepare_print.py) | The project and slice for either machine, from the shared PET-GF settings |

## Print

Print in the owned PET-GF15 at 15% infill, show face on the textured plate, legs up:
nothing needs support, and the plate's texture is the counter's surface. The project adds a
5 mm outer brim by hand, the only way a brim appears here: a first layer this wide holds its
outline with one, and an outline laid at the plate's edge without one lifted within a dozen
lines. The slab's edges
on the plate are sharp. The four outer corners are rounded at [6 mm](FCT_CORNER_R), the
legs meet the slab on a [6 mm](FCT_ROOT_R) root, and the legs' inner edges and feet are
rounded at [3 mm](FCT_FOOT_R). The STL is the faucet's absolute-tolerance print mesh
(`cadlib/print_mesh.py`), read back and refused on any open or non-manifold edge, so the
rounds print as rounds. The solid is [2456 cm³](FCT_VOLUME) before infill; the slice says
what it weighs.

## Use

Stand it legs down. The faucet's shank goes through the hole with its plate and gasket on
the show face and the under-counter plate and nut below, the way the counter takes them.
The slab is thinner than a counter (the install guide takes 3/4 to 1-1/2 in), and the nut
runs up the shank to it.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/fixtures/fake-countertop/fake_countertop.py`
