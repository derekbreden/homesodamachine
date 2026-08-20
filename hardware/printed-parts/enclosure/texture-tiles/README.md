# Texture tiles

Five [50 mm](TILE_SIDE) × 50 mm × [3 mm](TILE_Z) swatches, printed **flat**, one
50 × 50 face textured and the other left plain. Fast to print and fast to judge: the
question they answer is *which pattern*, not *what geometry*.

The plain face is the **bed** face, so every tile carries its texture and the textured-PEI
finish it is being judged against on opposite sides of the same 3 mm. Turn it over.

Every texture is a heightfield cut down from the show face, [1.2 mm](TEXTURE_DEPTH) at
its deepest — three layers at the enclosure's 0.4 mm — leaving [1.8 mm](FLOOR_LEFT) of
solid under the deepest cut. Both faces are sampled at [0.25 mm](GRID_STEP), well under
the 0.8 mm nozzle. The texture runs full-bleed to all four edges rather than sitting in
a border like a plaque.

Each tile's name is sunk into its bed face, mirrored, so it reads when you turn it over.

Geometry source: [`texture_tiles.py`](texture_tiles.py).

## What a flat tile can and cannot tell you

Everything here is a **top surface**, quantised in Z at the layer height. That is the
honest, hardest case, and it is what the box's top and its 45° display facet actually
face.

It is **not** what these patterns look like on a vertical wall. There, a cut of the same
shape is drawn by the nozzle in XY and carries no layer quantisation at all — the same
flute that steps in three visible terraces here comes out as clean as the nozzle draws.
[`../texture-coupons/`](../texture-coupons/) is the set that shows both at once.

So: pick the *pattern* here. Confirm it on the corner coupon before it goes in the box.

## The five

| | pattern | scale |
|---|---|---|
| **FLUTE** | Half-round grooves on one axis — linear, directional reeding. | [5 mm](FLUTE_PITCH) pitch |
| **CROSS** | The same grooves on both diagonals, deeper wins — a diamond knurl. Non-directional, so it catches light from any angle. | [6 mm](CROSS_PITCH) pitch |
| **HEX** | Grooves along the boundaries of a triangular lattice's Voronoi cells, which are regular hexagons. Geometric and deliberate. | [8 mm](HEX_CELL) cell, [2.2 mm](HEX_GROOVE) groove |
| **VORONOI** | Jittered sites, each cell dropped to one of [4](VORONOI_LEVELS) depths and meeting its neighbours on a vertical step. Bambu's own voronoi fuzzy skin, in geometry, at a size you choose. | [7 mm](VORONOI_CELL) mean cell, [0.4 mm](VORONOI_STEP) step |
| **PERLIN** | Fractal Perlin — the continuous-grain end of the range. | [7 mm](PERLIN_FEATURE) feature |

Depth is the same [1.2 mm](TEXTURE_DEPTH) on all five, so the only variable under test
is the pattern. One constant changes it for all of them.

VORONOI's levels are evenly spaced rather than random, so each lands on a layer boundary
at 0.4 mm and no two cells round to the same height. A continuous version would let the
slicer decide which distinctions survive.

## Printing

`texture-tiles-plate.stl` is all five, [166 mm](PLATE_X) × [108 mm](PLATE_Y) — drop it
in as one object.

Slice on the enclosure's own profile — 0.8 mm nozzle, 0.4 mm layers, PETG — so the tiles
and the box quantise identically. Set `fuzzy_skin` to `none`; the texture is in the
geometry, and a slicer texture on top measures neither.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/texture-tiles/texture_tiles.py`
