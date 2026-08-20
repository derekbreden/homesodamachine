# Texture tiles

Five square swatches at each of [50 and 100 mm](TILE_SIDES), [3 mm](TILE_Z) thick,
printed **flat**, one square face textured and the other left plain. Fast to print and
fast to judge: the question they answer is *which pattern*, not *what geometry*.

The plain face is the **bed** face, so every tile carries its texture and the
textured-PEI finish it is being judged against on opposite sides of the same 3 mm. Turn
it over. Each tile's name is sunk into that face, mirrored, so it reads when you do.

Every texture is a heightfield cut down from the show face, [1.2 mm](TEXTURE_DEPTH) at
its deepest, leaving [1.8 mm](FLOOR_LEFT) of solid under the deepest cut. The texture
runs full-bleed to all four edges rather than sitting in a border like a plaque.

Geometry source: [`texture_tiles.py`](texture_tiles.py).

## Why two sizes, and what stays fixed

**A pattern's scale is absolute.** `flute_pitch` is 5 mm on a 50 mm tile and 5 mm on a
100 mm one. The big swatch is *more repeats of the same texture*, not the same texture
enlarged — which is the only way the two sizes answer the same question. The 100 mm tile
is the one to judge on: a soda machine's panels are 215 mm across, and a pattern reads
differently over four times the area.

Both faces are sampled on a [200](GRID_CELLS) × 200 grid whatever the size — [0.25 mm](GRID_STEP_50) cells at 50 mm, [0.5 mm](GRID_STEP_100) at 100 mm. The cell **count**
is held constant, not the cell size: both sample finer than the 0.82 mm the nozzle
draws, so neither loses a feature the printer could have made, and the triangle budget —
and the file — stays put as the tile grows.

## What a flat tile can and cannot tell you

Everything here is a **top surface**, quantised in Z at the layer height. That is the
honest, hardest case, and it is what the box's top and its 45° display facet actually
face.

It is **not** what these patterns do on a vertical wall. There, a cut of the same shape
is drawn by the nozzle in XY and carries no layer quantisation at all — the flute that
steps in visible terraces here comes out as clean as the nozzle draws.
[`../texture-coupons/`](../texture-coupons/) is the set that shows both at once.

So: pick the *pattern* here, then confirm it on the corner coupon before it goes in the
box.

## The five

| | pattern | scale |
|---|---|---|
| **FLUTE** | Half-round grooves on one axis — linear, directional reeding. | [5 mm](FLUTE_PITCH) pitch |
| **CROSS** | The same grooves on both diagonals, deeper wins — a diamond knurl. Non-directional, so it catches light from any angle. | [6 mm](CROSS_PITCH) pitch |
| **HEX** | Grooves along the boundaries of a triangular lattice's Voronoi cells, which are regular hexagons. Geometric and deliberate. | [8 mm](HEX_CELL) cell, [2.2 mm](HEX_GROOVE) groove |
| **VORONOI** | Jittered sites, each cell dropped to one of [4](VORONOI_LEVELS) depths and meeting its neighbours on a vertical step. Bambu's own voronoi fuzzy skin, in geometry, at a size you choose. | [7 mm](VORONOI_CELL) mean cell, [0.4 mm](VORONOI_STEP) step |
| **PERLIN** | Fractal Perlin — the continuous-grain end of the range. | [7 mm](PERLIN_FEATURE) feature |

Depth is the same [1.2 mm](TEXTURE_DEPTH) on all five and at both sizes, so the only
variable under test is the pattern. One constant changes it for all of them.

VORONOI's levels are evenly spaced rather than random, so each lands on a layer boundary
at 0.4 mm and no two cells round to the same height. A continuous version would let the
slicer decide which distinctions survive.

## Printing

`texture-tiles-50-plate.stl` is all five 50 mm tiles laid out on one plate,
[166 mm](PLATE_50_X) × [108 mm](PLATE_50_Y) — drop it in as a single object.

**There is no 100 mm plate.** Five of them want [316 mm](PLATE_100_X) ×
[208 mm](PLATE_100_Y), and the H2C's LEFT extruder reaches only
[325 mm](BED_USABLE_X) in X — the band the bed draws as "left nozzle only" is the right
extruder's 25 mm dead zone, and the right extruder cannot reach the leftmost column at
all. That leaves no margin worth printing into, so the generator declines to build the
plate rather than emit one that will not fit. Import the five
`texture-tile-100-*.stl` files and arrange, or print them in batches.

Slice on the enclosure's own profile — 0.8 mm nozzle, 0.4 mm layers, PETG — so the tiles
and the box quantise identically. Set `fuzzy_skin` to `none`; the texture is in the
geometry, and a slicer texture on top measures neither. No supports: nothing here
overhangs.

**On the H2C, check the filament grouping before you print.** With one filament on a
two-nozzle machine the slicer's Auto grouping may assign it to the right extruder. If
the PETG is in the left AMS, drag it to the left extruder under *Filament grouping →
Custom*, or use Auto's *Convenience Mode*, which reads the printer's actual filament
status.

### The 3 mm / 0.4 mm layer note

3.0 mm is not a whole number of 0.4 mm layers. The slicer keeps **7 layers, topping out
at 2.80 mm**, and drops the last 0.20 mm. The deepest cut is still at 1.80 mm, so the
relief that actually prints is **1.00 mm, not 1.20**.

It is uniform across all five patterns and both sizes, so the comparison stays fair —
but if the full depth matters, `tile_z` at 3.2 mm is 8 whole layers and puts both the
show face and the deepest cut on layer boundaries.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/texture-tiles/texture_tiles.py`
