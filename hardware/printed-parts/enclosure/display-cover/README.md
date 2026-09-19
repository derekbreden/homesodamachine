# Machine display cover

A PET-GF bezel with a smooth, rounded face, let into the enclosure's 30° display plane.
The cover measures [125.5 mm](COVER_X) across by [83 mm](COVER_SLOPE) up the slope,
with [6 mm](COVER_CORNER_R) outside corner radii and a [2 mm](COVER_T) face.
Its [107.5 mm](WINDOW_X) window laps the display glass on the TPU gasket.
The reveal has [0.3 mm](COVER_SLIP) clearance per side.

Two broad side skirts flex inward during insertion. Each has [2 mm](SKIRT_WALL) walls,
a [24 mm](SKIRT_LENGTH) run and [34 mm](SKIRT_DEPTH) reach below the face.
A gradual lead-in carries each [3 mm](LIP_HEIGHT) lip through the opening; its flat
shoulder engages the rigid housing by [1.8 mm](LIP_ENGAGEMENT). The nominal inward
preload at the retaining shoulder is [0.35 mm](PRELOAD). The groove leaves
[0.48 mm](ROOF_AIR) above the lip for the supported surface.

The printed STEP and STL contain the relaxed cover. The enclosure assembly shows the
skirts in their seated positions. Place the display and gasket in the housing, then
press the cover normal to the screen until both lips engage. The cover carries no screws.

Print with the visible face upward and both skirts on the bed. Supports carry the
bezel's hidden underside. Physical seating, retention and repeated-use measurements
remain to be recorded for this geometry.

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/display-cover/display_cover.py`
exports the complete cover and checks its solid, glass clearance and seated skirt pockets.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/display-cover/display_cover.py`
