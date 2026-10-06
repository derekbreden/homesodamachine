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
accepted **September 0.24 mm recipe**. Plate 1 holds the left body and cap;
plate 2 holds the right body and cap. Bodies print mouth up and caps exterior
face down. Both plates use the left **0.8 mm Standard-flow nozzle**, Bambu
PETG Translucent Clear and the textured PEI plate.

The saved process uses a **0.30 mm first layer / 0.24 mm normal layer**,
**255 °C** nozzle, **70 °C** bed, **0.97** flow, **6 mm³/s** volumetric ceiling,
**30 mm/s** requested wall/fill speeds and **20%** ordinary cooling. It retains
six requested Arachne walls, 100% zig-zag fill, aligned unconditional scarf
seams, zero seam gap, top ironing and the accepted support settings.
[Complete current settings](print-settings.json) ·
[Printing guide](watertight-petg.md) · [Project verification](reservoir.print.json) ·
[Native slice review](slice-review.json). Each current body/cap plate estimates
about **20 h 20 min and 420 g** in Bambu Studio 02.08.02.61.

The printer configuration carries the accepted Mark2 **+0.04 mm user Z trim**
over stock plate compensation. Retain the destination printer's own calibrated
trim when assigning a job, per [printer profiles](../../../../tools/bambu-printers.md).
The recipe's reported water hold is identified by `september-08-024` in the
[acceptance record](water-hold-acceptance.json).

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
meshes, bed placement and preservation of the accepted print settings.

Past settings, reported outcomes and source commits are in the
[print log](print-log.md) and [September inspection record](history/seal-trial.md).
Historical 3MFs are retained in Git.

Reservoir leak results belong to the articles and process tested. Moving the
rod bosses preserves their blind seats and the continuous wet floor; CAD
clearance does not establish a new print's sealing or finished float sliding.
