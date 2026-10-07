# Flavor reservoirs

Current bodies and matching caps carry the ASA Aero float guide at
**(x = ±106.25, y = +32.5) mm** in the assembled cold-core frame,
**20 mm inward from the wet far wall**. Use a 36 × 28 mm ASA Aero float with
a midplane RC62 on the 3.175 mm rod.

[Float installation and reed calibration](../magnetic-float/all-aero/installation.md) ·
[Level sensing](level-sensing.md) · [Floor and bulkhead](floor-and-bulkhead.md) ·
[Vent](vent.md)

## Next print

Use **[reservoir.3mf](reservoir.3mf)**, the current body/cap pairs with the
**September 0.24 mm baseline with ironing off**. Plate 1 holds the left body and cap;
plate 2 holds the right body and cap. Bodies print mouth up and caps exterior
face down. Both plates use the left **0.8 mm Standard-flow nozzle**, Bambu
PETG Translucent Clear and the textured PEI plate.

The saved process uses a **0.30 mm first layer / 0.24 mm normal layer**,
**255 °C** nozzle, **70 °C** bed, **0.97** flow, **6 mm³/s** volumetric ceiling,
**30 mm/s** requested wall/fill speeds and **20%** ordinary cooling. It retains
six requested Arachne walls, 100% zig-zag fill, aligned unconditional scarf
seams, zero seam gap, **no ironing** and the September support settings.
[Complete current settings](print-settings.json) ·
[Printing guide](watertight-petg.md) · [Project verification](reservoir.print.json) ·
[Native slice review](slice-review.json). Each current body/cap plate estimates
about **19 h 23 min and 419 g** in Bambu Studio 02.08.02.61. The native
model/support/brim envelope stays at least **80.5 mm inside the usable bed**.
Filament assignment is Manual on the left nozzle. Start Mark2 on **A4**, with
the preferred **A4 → A3 → A1** consumption order in the
[printer guidance](../../../../tools/bambu-printers.md#mark2-clear-petg-spool-order).

The [flat-square finish record](ironing-study/prints/2026-10-06-mark2-squares-v1/physical-result.json)
selects **OFF** as the smoothest and best-feeling finish. The
[calibration record](ironing-study/README.md) preserves the tested settings and
observations. This finish selection supplies no new reservoir water-hold result.

The printer configuration carries the accepted Mark2 **+0.04 mm user Z trim**
over stock plate compensation. Retain the destination printer's own calibrated
trim when assigning a job, per [printer profiles](../../../../tools/bambu-printers.md).
The September baseline's reported water hold is identified by `september-08-024` in the
[acceptance record](water-hold-acceptance.json).

[Mark2 reservoir and cap launch](prints/2026-10-06-mark2-no-ironing-v1/launch.json),
task **1314692596**, uses plate 1 with ironing off.
The [right reservoir and cap launch](prints/2026-10-07-mark2-right-no-ironing-v1/README.md),
task **1317261284**, uses the matching frozen plate 2, accepted at **09:34:45 CDT
on October 7**. Finished-part and water-hold results are unassessed.

## Current print geometry

| Pair | Body | Cap |
| --- | --- | --- |
| Left | [STEP](reservoir-left.step) | [STEP](reservoir-cap-left.step) |
| Right | [STEP](reservoir-right.step) | [STEP](reservoir-cap-right.step) |

[`reservoir.py`](reservoir.py) generates these body/cap pairs together from
the shared [float interface](../_float_interface.py).
[prepare_print.py](prepare_print.py) builds the one current project from these
STEP files and the complete frozen recipe. Run it with `tools/cad-venv/bin/python`;
it checks source hashes against the
[integration record](../magnetic-float/all-aero/integration-check.json), closed
meshes, centered bed placement and preservation of the September baseline
with the declared ironing and assignment settings.
[review_slice.py](review_slice.py) checks the native recipe, absence of ironing,
left-nozzle assignment, Z trim, full bead inset and bed-rooted supports.

Past settings, reported outcomes and source commits are in the
[print log](print-log.md) and [September inspection record](history/seal-trial.md).
Historical 3MFs are retained in Git.

Reservoir leak results belong to the articles and process tested. Moving the
rod bosses preserves their blind seats and the continuous wet floor; CAD
clearance does not establish a new print's sealing or finished float sliding.
