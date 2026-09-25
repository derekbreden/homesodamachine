# Machine display cover

A PET-GF bezel with a smooth, rounded face, let into the enclosure's 30° display plane.
The cover measures [125.5 mm](COVER_X) across by [83 mm](COVER_SLOPE) up the slope,
with [6 mm](COVER_CORNER_R) outside corner radii and a [2 mm](COVER_T) face.
Its [107.5 mm](WINDOW_X) window laps the display glass on the TPU gasket.
The reveal has [0.3 mm](COVER_SLIP) clearance per side.

Two broad side skirts snap into the housing. Each is the nameplate's snap tab run along
the display: [1.3 mm](SKIRT_WALL) thick, [24 mm](SKIRT_LENGTH) long, reaching
[13.3 mm](SKIRT_DEPTH) below the face. Its square [1.8 mm](LIP_ENGAGEMENT) lip starts
[8.5 mm](LIP_START) below the cover plate, stands on a [1.2 mm](LIP_LAND) land above a tapered
nose, and rests [0.48 mm](BEARING_SLIP) under the housing's catch. Under each catch the housing
is open straight down into the pump bay.
Each cover skirt sits [0.9 mm](SKIRT_INSET) inboard of its receiver datum; the housing's
slots stay fixed. Each lip overlaps its catch by [0.6 mm](CATCH_OVERLAP) when centered.

Place the display and gasket in the housing, then press the cover normal to the screen until
both lips click under their catches. The cover carries no screws.

Print face down, with the visible face on the plate and both skirts pointing up, as the
[nameplate](../nameplate/README.md) prints. Each lip's square catch face takes a support
standing on the plate beside the cover's edge, with the nameplate's 0.24 mm top gap and its
small-overhang filter off. Peel each support off whole and keep the catch faces flat. Physical
seating, retention and repeated-use measurements remain to be recorded for this geometry.
The [fit trial](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-25-display-cover-mark2-v8/README.md)
places the complete cover on one Mark2 plate.

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/display-cover/display_cover.py`
exports the complete cover and checks its solid, glass clearance and seated skirt pockets.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/display-cover/display_cover.py`
