# Fake countertop

The bench stand that stands in for a counter: an inverted U across
and tall, its legs apart, the narrow cavity under the
counter in Derek's kitchen, and as deep as the H2C's plate takes under its left nozzle with a
5 mm border. One thickness of throughout: 3 cm, the thickness most US kitchen
counters are and the one the faucet layout stands the faucet on. One faucet clamps through its
 hole, the 1-3/8" the shank is sized for, and the umbilical hangs and
bends under the slab with clear: the shank and the umbilical stub reach
 below the counter's top face with the gather's bend, and the rest is
hand room. The two open sides are where the umbilical leaves and where a camera looks in.

**Status: CAD checked, print untested.** This is bench tooling, separate from the machine
assembly and its BOM.

| File | Use |
|---|---|
| [`fake_countertop.rs`](fake_countertop.rs) | The program: the print, its model and their geometric checks |
| [`numbers.rs`](numbers.rs) | Dimensions |
| [`fake-countertop.stl`](fake-countertop.stl) | The print, show face down |
| [`fake-countertop.step`](fake-countertop.step) | Material-coloured model in the print frame |
| [`fake-countertop.step.npz`](fake-countertop.step.npz) | Full fine model for measurement |
| [`prepare_print.py`](prepare_print.py) | The project and slice for either machine, from the shared PET-GF settings |

## Print

Print in the owned PET-GF15 at 15% infill, show face on the textured plate, legs up:
nothing needs support, and the plate's texture is the counter's surface. No brim. The Mark2
project carries that machine's +0.04 and the H2C project its +0.18. A plate that has never
printed out to 5 mm from its front and back edges holds this first layer only after one layer
there at Bambu's own offset, the stock project (`prepare_print.py --variant black-mark2-stock`),
stopped once that layer is down. The slab's edges
on the plate are sharp. The four outer corners are rounded at, the
legs meet the slab on a root, and the legs' inner edges and feet are
rounded at. The STL uses 0.005 mm absolute-tolerance triangulation,
read back and refused on any open or non-manifold edge, so the
rounds print as rounds. The solid is before infill; the slice says
what it weighs.

## Use

Stand it legs down. The faucet's shank goes through the hole with its plate and gasket on
the show face and the under-counter plate and nut below, the way the counter takes them.
The slab is the thickness of a stone counter, inside the 3/4 to 1-1/2 in the install guide takes.
