# Texture corner

Two standing walls meeting at the box's own outside corner, textured on the outside,
printed the way the enclosure prints: **standing**, build axis up the wall.

Each is [50 mm](LEG) of flat wall either side of a [12 mm](CORNER_R) rounded corner,
[50 mm](HEIGHT) tall, in a [3 mm](WALL) wall. `corner_r` is
`enclosure.corner_round` — the anti-warp relief the box strikes on every standing
vertical — and `wall` is `enclosure.wall`, so what the coupon shows is what the box can
take: the deepest cut leaves [1.8 mm](WALL_LEFT) behind, on the flat and round the turn
alike.

Geometry source: [`texture_corner.py`](texture_corner.py). The flute vocabulary is
[`../../cadlib/reeding.py`](../../cadlib/reeding.py), shared with
[`../texture-tiles/`](../texture-tiles/) so the wall and the tile provably lay down the
*same* texture.

## Why this exists

A flat tile can only answer what a texture does on a **top surface**, where relief is
quantised in Z at the layer height. On a standing wall the same groove is drawn by the
nozzle in XY and carries **no layer quantisation at all** — it comes out as clean as the
nozzle draws.

That is the condition the box's own walls are in, and no tile can show it. Hold a corner
up beside the matching tile: same pattern, same pitch, same depth, two completely
different surfaces. That comparison is the entire point.

## What it answers that nothing else does

**What a flute does round a corner.** The texture is sampled by **arc length** along the
wall's outer path, so it crosses the corner's [18.85 mm](QUARTER_TURN) quarter turn
without knowing the corner is there — no seam, no restart, no bunching. Measured on the
generated field, the [5 mm](FLUTE_PITCH) flute spacing holds to 4.998–5.004 mm across
all [118.8 mm](PATH_LENGTH) of path, with four groove centres landing inside the turn
itself.

That is not free by default. A texture laid out in the part's own X/Y would stretch or
tear at the turn; one laid out in arc length cannot.

## The three

**FLUTE** straight, the control · **CHEVRON** [34.1°](CHEVRON_LIMB) limb ·
**WAVE** [42.7°](WAVE_LIMB) limb

Same three as the tiles, at the same pitch and depth, so the vertical and flat sets are
read against each other rather than against memory.

On a standing wall the limb angle is not cosmetic: it is how far the warp tilts the
groove's own side surface off vertical, and 45° is what this box strikes every relief
at. Both stay inside it. Nothing else here overhangs at all — every cut is drawn in XY.

## Details that are not decoration

**The inner foot.** A 3 mm wall standing 50 mm on its own edge is a warp and adhesion
risk. A [5 mm](FOOT) foot ramps 45° off the inside face at the base, roughly tripling
bed contact. It is on the **inside**, so it costs the show face nothing.

**The plain band.** The texture fades in over that same 5 mm, so the first layers go
down as a clean solid L rather than a wavy one — and the band it leaves is the plain
wall, right there to read the textured wall against.

**The label** is sunk into the inner face, reading from inside the box.

## Printing

`texture-corners-plate.stl` is all three, [206 mm](PLATE_X) × [62 mm](PLATE_Y) — drop it
in as one object. About 14.6 cm³ each.

Slice on the enclosure's own profile — 0.8 mm nozzle, 0.4 mm layers, PETG, textured PEI.
Set `fuzzy_skin` to `none`; the texture is in the geometry. **No supports.** Keep the
brim: the footprint is an L, not a slab.

On the H2C, check the filament grouping before printing — with one filament on a
two-nozzle machine the Auto grouping may hand it to the right extruder.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/texture-corner/texture_corner.py`
