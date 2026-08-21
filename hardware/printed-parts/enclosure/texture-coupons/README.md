# Texture coupons

Four samples of the enclosure's top-front corner, each carrying a different surface
treatment. The corner is the one place the box presents all three of its show surfaces
at once — a vertical wall, the 45° display facet, and a flat top — so a treatment that
only works on one of them fails visibly here.

Each coupon is [120 mm](COUPON_X) wide × [56 mm](COUPON_Y) deep × [44 mm](COUPON_Z)
tall, sitting on the bed on its z = 0 face. That is the orientation
[`enclosure.py`](../enclosure/enclosure.py) prints its four quadrants in, so the build
axis and the hanging faces are the ones the real piece has.

The show surface is one folded band: [18 mm](WALL_RISE) of vertical wall, then
[36.77 mm](FACET_SLOPE) up the 45° facet, then [30 mm](TOP_RUN) of flat top. Bottom,
back and sides are plain; the back carries the engraved label.

**Nothing on any coupon hangs steeper than 45°.** No supports.

Geometry source: [`texture_coupons.py`](texture_coupons.py).

## The four

### FLUTE

Half-round flutes running **along** the fold — up the wall, over the arris, across the
facet, over the second arris, and back along the top. Three lateral zones of
[40 mm](ZONE_X), at pitches [4 / 6 / 9 mm](FLUTE_PITCHES), all [1 mm](FLUTE_DEPTH) deep.
Depth stays inside what the 3 mm wall can give up, so what the coupon shows is what the
real wall can take: the enclosure profile lays 0.87 mm of shell per face — two loops,
0.42 outer and 0.45 inner — and a 1 mm flute leaves 2 mm of wall standing under it, so
both faces still get all four loops with 0.26 mm between them. The wall under the
deepest flute is full section, not a bridged skin.

Every cut surface on the wall is vertical, so the wall's flutes carry no layer
quantisation at all — they are as clean as the nozzle draws. On the top they are a
valley cut into a horizontal face, so they resolve in Z at the layer height. **The
contrast between the wall zone and the top zone is the thing to look at.**

### VEE

90° V-grooves running **across** X, arrayed up the fold at [7 mm](VEE_PITCH) pitch, full
width and continuous over both arrises. Depth ramps from [0.8 mm](VEE_DEPTH_MIN) at the
-X edge to [2.4 mm](VEE_DEPTH_MAX) at +X, so one coupon reads the whole depth question.

On the 45° facet a 90° V resolves into one **vertical** flank and one **horizontal**
flank — the two surfaces an FDM machine prints best. The facet band is where this
treatment earns its place.

### FACET

No micro-texture at all. Sections lofted ruled between alternating valley and ridge
stations [15 mm](FACET_PITCH) apart, standing [1.2 mm](FACET_RISE) proud, so the wall,
the facet and the top each break into a run of shallow planes and none of them is a true
plane. Tests the cheapest hypothesis on the list: that **flatness, not roughness**, is
what was betraying the surface.

Consecutive facets never share a slope. An arris between two planes at the same angle is
not an arris — it catches no light, and the surface reads as flat anyway.

### NOISE

Perlin fBm displacement baked into the mesh at [8 mm](NOISE_FEATURE) feature size, four
octaves, 0.5 persistence — the same octave and persistence Bambu Studio's own fractal
fuzzy skin runs at. Amplitude is zoned across X at
[0.2 / 0.4 / 0.7 mm](NOISE_AMPLITUDES).

Sampled in **world space**, so the grain runs continuously across both arrises and over
the corner. Slicer fuzzy skin cannot do this — it perturbs each layer's perimeter
independently, which is why it reads as noise rather than as a material.

Mesh only. There is no STEP of this one.

## Printing

`texture-coupons-plate.stl` is all four laid out on one plate,
[252 mm](PLATE_X) × [124 mm](PLATE_Y) — drop it in as a single object. The individual
`texture-coupon-*.stl` files are there to reprint one on its own, and
`texture-coupon-*.step` feeds the same pipeline the enclosure pieces use.

Slice on the enclosure's own profile — 0.4 mm High Flow nozzle, 0.24 mm layers, PETG
([enclosure/print-log.md](../enclosure/print-log.md)) — so the coupons and the box are
quantised the same. Drop `sparse_infill_density` for the coupons; nothing here is
structural.

Set `fuzzy_skin` to `none`. Every coupon's texture is in the geometry, and a slicer
texture on top of it measures neither one.

## Reading the result

Judge each coupon under a raking light, at the distance the machine is actually seen
from, and on all three surfaces. A treatment that fixes the wall and abandons the
facet is not a candidate — the facet carries the display and is where the eye goes.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/texture-coupons/texture_coupons.py`
