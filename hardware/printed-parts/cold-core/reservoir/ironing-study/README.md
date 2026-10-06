# PETG ironing calibration

[ironing-study.3mf](ironing-study.3mf) contains **nine flat 35 × 35 mm squares**
with varied ironing settings and **one un-ironed OFF reference**. Every square
has an uninterrupted top face. Its label sits on a lower tab outside that face.
The plate uses Bambu PETG Translucent Clear, Mark2's **left 0.8 mm Standard-flow
hotend** and textured PEI.

Bambu Studio 02.08.02.61 estimates **25.53 g and 1 h 55 min** for the complete
plate, including **46 min of ironing**. Each square is 1.50 mm thick: one
0.30 mm first layer and five 0.24 mm layers. There are no supports.

## Settings and labels

Labels read **speed in mm/s / ironing flow in percent**. For example,
**30/10** means 30 mm/s and 10% flow. All nine conditions use **0.15 mm line
spacing**, the same 0.31 mm inset and zig-zag ironing pattern.

| Speed | 10% flow | 20% flow | 30% flow |
| --- | --- | --- | --- |
| 15 mm/s | 15/10 | 15/20 | 15/30 |
| 30 mm/s | 30/10 | 30/20 | 30/30 |
| 60 mm/s | 60/10 | 60/20 | 60/30 |

**OFF** has no ironing. It is the plate's single reference. Ironing applies only
to each square's highest face at Z = 1.50 mm; the lower label tabs stay un-ironed.
The 30/10 square uses the September recipe's ironing flow, speed and spacing.

The underlying process uses **255 °C** nozzle, **70 °C** bed, **0.97** filament
flow ratio, **6 mm³/s** ceiling, six requested Arachne walls, 100% fill and the
September cooling and seam settings. [study.json](study.json) records the
calibration overrides and geometry. The full reservoir's official print
settings remain the [September 0.24 mm recipe](../README.md#next-print).

## Mark2 placement and filament

The compact central envelope, including every native model/brim bead, stays
**84.98 mm from the nearest usable bed edge** and 90.50 mm from the front and
back. The closest specimen bead envelopes are **4.90 mm apart**. Follow the
[unseasoned-plate placement guidance](../../../../../tools/bambu-printers.md#placement-on-unseasoned-plates).

Use **A4 → A3 → A1**, oldest first, starting on A4. Filament assignment is
**Manual, left nozzle**. Bambu Connect exposes the starting-slot selector and
AMS Auto-Refill, but its automatic backup order is unverified.

Mark2 expects **+0.04 mm user Z trim** over stock compensation. The verified
0.8 mm textured-PEI slice clears the trim with `G29.1 Z0` and then emits
**`G29.1 Z0.02`**. Preserve the destination printer's calibrated trim following
[printer profiles](../../../../../tools/bambu-printers.md).

![Flat square calibration with native ironing paths](plate-layout.png)

## Read the finish

After cooling, inspect the **top** of each labelled square under the same side
lighting and lightly run a fingertip across it. Compare the broad middle and
then the edges. Record the smoothest labels and any visible grooves, raised
ridges, dragged plastic or edge buildup. Gloss is a separate observation.
Prefer a face that feels smooth and even without loose material or raised
edges; among comparable finishes, the faster setting saves ironing time. If
none is clearly better than OFF, record that result.

This is a flat-surface calibration. It does not assess sloped faces, gasket
sealing or water holding. The customer outcome is a contact face that lets a
rubber seal sit evenly without raised lines or loose PETG; selecting a setting
from these squares alone does not establish that outcome on a reservoir.

## Verification and reproduction

[slice-review.json](slice-review.json) verifies the actual native flow, speed,
spacing and ironing height for all nine conditions, zero ironing on OFF and
zero supports. It checks emitted left-nozzle assignment, 0.8 mm diameter and
Mark2's resolved Z trim. Native full-bead placement includes arc extrema and
bead width; vendor startup purge/calibration paths are excluded. The review
enforces an 80 mm edge inset and 4 mm specimen envelope separation.

From the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/reservoir/ironing-study/prepare_print.py
mkdir -p .cache/reservoir-ironing-squares/slice
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio \
  --arrange 0 --orient 0 --slice 0 --export-3mf ironing-squares-review.3mf \
  --outputdir "$PWD/.cache/reservoir-ironing-squares/slice" \
  "$PWD/hardware/printed-parts/cold-core/reservoir/ironing-study/ironing-study.3mf"
tools/cad-venv/bin/python hardware/printed-parts/cold-core/reservoir/ironing-study/review_slice.py
```

The editable calibration is the only 3MF in this directory. Derived native
archives and meshes live in ignored `.cache/reservoir-ironing-squares/`.

## Physical records

[Current square-calibration launch](prints/2026-10-06-mark2-squares-v1/launch.json),
Mark2 task **1314288755**.

[Feature-crop comparison observation](prints/2026-10-06-mark2-centered-v3/physical-result.json) ·
[Centered feature-crop launch](prints/2026-10-06-mark2-centered-v3/launch.json) ·
[Stopped edge-placement job](prints/2026-10-06-mark2/physical-result.json).
Historical projects are retained in Git, identified by the launch records.

Prusa's [ironing documentation](https://help.prusa3d.com/article/ironing_177488)
describes smoothing flat top faces and tuning flow, speed and spacing. The
ranges on this plate are calibration candidates; they are not a selected PETG
recipe.
