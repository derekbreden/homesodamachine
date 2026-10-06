# Flavor reservoirs

Current bodies and matching caps carry the ASA Aero float guide at
**(x = ±106.25, y = +32.5) mm** in the assembled cold-core frame,
**20 mm inward from the wet far wall**. Use a 36 × 28 mm ASA Aero float with
a midplane RC62 on the 3.175 mm rod.

[Float installation and reed calibration](../magnetic-float/all-aero/installation.md) ·
[Level sensing](level-sensing.md) · [Floor and bulkhead](floor-and-bulkhead.md) ·
[Vent](vent.md)

## Water-holding print recipes

The **May 30 Bambu PETG clear recipe** has an identified successful water hold
with its bulkhead and TPU gaskets. Its complete saved settings and original
left-body mesh are in
[`reservoir-water-hold-2026-05-30.3mf`](reservoir-water-hold-2026-05-30.3mf):
0.6 mm nozzle, 0.18 mm layers, 255/260 °C, flow 1.02 and 10–20% part cooling.
The saved `Bambu PETG Water` preset uses the PETG Basic identity `GFG00`;
Derek confirms the actual filament was **Bambu PETG clear**.

Both September **0.8 mm nozzle recipes**, at 0.18 and 0.24 mm layer height,
also held water. Their projects and settings are in [seal-trial.md](seal-trial.md).
The [water-hold acceptance record](water-hold-acceptance.json) binds the reported
results to the May project and recovered September printer slices.
[watertight-petg.md](watertight-petg.md) compares the accepted recipes.

## Current print geometry

| Pair | Body | Cap |
| --- | --- | --- |
| Left | [STEP](reservoir-left.step) | [STEP](reservoir-cap-left.step) |
| Right | [STEP](reservoir-right.step) | [STEP](reservoir-cap-right.step) |

[`reservoir.py`](reservoir.py) generates these body/cap pairs together from
the shared [float interface](../_float_interface.py). Import these current
models for the next native project, carry the [watertight PETG recipe](watertight-petg.md),
and verify body and cap hashes against the [integration record](../magnetic-float/all-aero/integration-check.json).
The accepted native projects in the [print log](print-log.md) and
[seal trial](seal-trial.md) retain their recorded geometry and recipes.
A new slice must review the current guide locations, material, installed nozzle
and plate before submission.

Reservoir leak results belong to the articles and process tested. Moving the
rod bosses preserves their blind seats and the continuous wet floor; CAD
clearance does not establish a new print's sealing or finished float sliding.
