# Lite enclosure shell

The transparent PETG box that wraps the contents placed by
[`../enclosure-assembly/_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py). Six walls — floor, four
sides, lid — with a square hole in the lid that clears the
[funnel](/pie-in-the-sky/lite/printed-parts/funnel/) inlet so it sits flush with the top of the
cabinet.

## Frame

The contents' frame carries through: Z+ up, X left/right, Y front/back (depth),
floor on Z=0. The −X wall is the enclosure front (where the tray-stack ports
and the pump column sit); +X is the cabinet back; +Y is the cabinet wall the
source-select tray stands against; the lid plane is z = 289 where the funnel
inlet sits.

## Dimensions

Walls [3 mm](WALL), interior clearance [5 mm](INTERIOR_CLEARANCE) off the
contents bbox, lid hole clearance [2 mm](LID_HOLE_CLEARANCE) off the funnel
rim. Read live from the contents placed by `../enclosure-assembly/_contents.py`
and from `funnel.step`, so any move in the contents propagates.

Outer envelope [313.5 mm](LITE_OUTER_X) × [235 mm](LITE_OUTER_Y) × [295 mm](LITE_OUTER_Z)
(X × Y × Z); lid hole [134 mm](LID_HOLE_X) × [134 mm](LID_HOLE_Y) centered on
the funnel column.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/enclosure/enclosure.py`
→ `enclosure.step`. Wall, clearance, and lid-hole clearance are the constants
at the top of `enclosure.py`.

## Sources
[value](NAME) texts are updated by:
- `/pie-in-the-sky/lite/enclosure/enclosure.py`
