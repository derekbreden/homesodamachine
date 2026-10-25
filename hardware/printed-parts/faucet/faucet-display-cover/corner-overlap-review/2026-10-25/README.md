# Sculpted cover front-corner overlap

This is a **cover-only print trial** against Mark2 task **1372253517**.
The [eight photographs and physical record](../../../industrial/prints/2026-10-24-buttons-sculpted-bands020-mark2/physical-result/physical-result.json)
establish reported good fit of the cover, display, tubes and wiring. Photo 8
identifies the remaining visible opening below the front corner of the skirt.
The [single-cover print](../../prints/2026-10-25-front-overlap-black-mark2/README.md)
is Mark2 task **1374330388**, accepted on October 25. Its
[physical result](../../prints/2026-10-25-front-overlap-black-mark2/physical-result/physical-result.json)
reports that it worked and is approved. The photographs still show a corner gap;
that gap is accepted as good enough, with no further iteration requested.

The proposed cover extends both sloping front skirt edges across that opening.
Its lower trim follows **N = 10.5 − 1.8 S**. At the front of the tip pocket,
S2.0, the trim reaches N6.9 and overlaps the N8.1 tip ledge by **1.2 mm in
side projection**. The existing circular neck clearance and inner cavity trim
the added stock away from the hardware. This is an integral extension of the
cover, with a clearance seam against the tip.

| Front trim at pocket station S2.0 | Accepted printed cover | Proposed cover |
| --- | --- | --- |
| Normal trim intercept | N14.0 mm | N10.5 mm |
| Edge height | N10.4 mm | N6.9 mm |
| Relation to N8.1 ledge | 2.3 mm opening | 1.2 mm projected overlap |

The [native reading](native-review.json) uses the exact accepted tip and cover
STEP inputs from the [lowered-head fit study](../../fit-review/2026-10-24/README.md).
The reproduced baseline has zero symmetric difference from that accepted cover.
The candidate adds **20.6138 mm³** at the front corners and removes no material.
Both its nominal seated shape and relaxed printable shape are one valid solid.
The seated candidate has zero intersection volume with the tip, display body,
screen and complete vendor switches. Its added stock remains **4.9234 mm**
from the switches. The bezel and retaining-lip regions have zero material change.

The display retains its 4.5 mm inward reduction, four 1 mm foot recesses and two
1 mm switch pockets. The cover retains its 0.6 mm glass gap, 0.65 mm arch-crown
clearance, 1.3 mm bezel, lip positions, 1.2 mm engagement and 1.25 mm preload at
the lip tops. The tip itself has no proposed change.

The lateral sightline reading samples both corners above the ledge. It records
cover material on each ray that passes through the accepted cover's corner
opening. These samples support the cosmetic overlap; they do not establish
occlusion at every angle, a liquid seal or physical installation performance of
this extension.

`review.py` generates the native STEP/STL proposal, measurements and packed
before/after meshes. Run it with `tools/cad-venv/bin/python` from the repository.
Its inputs are the local exports from the linked fit study's `measure.py` and
`button_relief.py`. Generated native files retain their hashes in the reading.
The published production cover builder is unchanged.
