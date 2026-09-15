# PET-GF support interface test

This job was cancelled before extrusion. It has no physical results. The active
experiment is [PET-GF interface edges](../petgf-interface-edges/README.md).

Sixteen numbered, open-front ceiling specimens share one Mark2 plate. All use
`hardware/printed-parts/petgf.3mf`, the left 0.4 mm nozzle, and +0.04 mm Z offset.
The object settings below vary; temperature, cooling, support type, line width,
layer height, print speed and model geometry remain common.

The roof is **3.84 mm thick**. Its underside is at Z24.20 mm. The shallow V marks
on the outside walls meet that plane at the mouth. Raised numbers are on the
roof; the front strip stays flat for caliper measurements.

## Examine the print

1. Keep each numbered roof intact. Break away its tree supports and note whether
   the interface sheet comes away with them.
2. If a sheet remains, try peeling it from the open front edge. Keep one removed
   sheet beside its specimen. Record removal effort and visible residue separately.
   Score the three wall junctions and the free front edge separately; also note
   whether the center releases while a rim stays bonded.
3. Compare the exposed underside with the V-mark tips as a visual reference.
   Measure roof thickness at several places along the flat front edge, avoiding walls and the raised label.
   Extra thickness or local ridges can obstruct a fit. Missing thickness, torn skin
   or separation within the roof indicates model damage. Droop can remain even
   after all interface material is removed.
4. Compare the repeated controls **01, 04, 10, 13 and 16**. Prefer a setting that
   exposes a clean underside while retaining the full roof thickness. Easy tree
   removal alone does not establish a successful result.

The blank [observations.csv](observations.csv) records both removal stages,
residue, thickness and damage. Photographs showing specimen numbers and undersides
are also sufficient for the next review.

The reported adhesion is concentrated at interface edges, particularly wall junctions;
free edges also retain material. The center usually releases. Each specimen presents
three wall junctions and one free edge for that comparison.

The sliced organic interface uses connected zigzags with runs along its boundary.
This experiment holds the boundary generation and lateral clearance constant.

## Specimens

| ID | Requested gap, mm | Actual planned gap, mm | Interface spacing, mm | Interface layers |
|---|---:|---:|---:|---:|
| 01 | 0.30 | 0.24 | 0.50 | 2 |
| 02 | 0.60 | 0.72 | 0.90 | 2 |
| 03 | 0.60 | 0.72 | 0.50 | 4 |
| 04 | 0.30 | 0.24 | 0.50 | 2 |
| 05 | 0.30 | 0.24 | 0.50 | 4 |
| 06 | 0.30 | 0.24 | 0.90 | 4 |
| 07 | 0.60 | 0.72 | 0.90 | 4 |
| 08 | 0.30 | 0.24 | 0.90 | 2 |
| 09 | 0.45 | 0.48 | 0.50 | 4 |
| 10 | 0.30 | 0.24 | 0.50 | 2 |
| 11 | 0.60 | 0.72 | 0.50 | 2 |
| 12 | 0.45 | 0.48 | 0.90 | 4 |
| 13 | 0.30 | 0.24 | 0.50 | 2 |
| 14 | 0.45 | 0.48 | 0.50 | 2 |
| 15 | 0.45 | 0.48 | 0.90 | 2 |
| 16 | 0.30 | 0.24 | 0.50 | 2 |

IDs increase left to right across each bed row, starting at the front. The corner
controls are 01, 04, 13 and 16; 10 is the baseline cell within the factorial.
Spacing is the slicer's added spacing between interface lines, not the resulting
center-to-center extrusion pitch. The actual gap is the first ceiling extrusion Z
minus its deposited layer height, minus the last interface extrusion Z. It measures planned separation, not real strand sag.
All 16 gaps and interface-layer counts are verified in `verification.json`.

## Files

- `prepare.py` builds the labeled specimens and single-plate project with per-object settings.
- `experiment.json` records dimensions, arrangement, recipe and source hashes.
- `support-interface.3mf` is the editable project.
- `verification.json` records the sliced settings, support paths and file hashes.
- `print-job.json` records printer acceptance and the started job.

Generate with `tools/cad-venv/bin/python hardware/print-tests/petgf-support-interface/prepare.py`.

The default tree setting selects organic support for this fixed-layer model.
That implementation rounds the top gap into whole model layers: the baseline
0.30 mm setting produces a planned 0.24 mm separation here.
[Bambu default-style selection](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/Support/SupportParameters.hpp#L143),
[Bambu gap rounding](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/Support/TreeSupportCommon.hpp#L280).

Audit the sliced file with:

```sh
python3 hardware/print-tests/petgf-support-interface/audit_gcode.py \
  --gcode .cache/prints/2026-09-15-support-interface-mark2/petgf-support-interface-mark2.gcode.3mf \
  --regions hardware/print-tests/petgf-support-interface/regions.json
```
