# White above-counter faucet gasket

This gasket retains the exact footprint and openings of the successful black
85A plate for the printed September 18 white Sculpted faucet. The
[source binding](source-binding.json) names the frozen source and mesh hash.
It uses white Bambu TPU 90A through Mark2’s fixed right standard 0.6 mm nozzle,
external slot 255, on the engineering plate with the reported glue coating.

The [settings comparison](settings-comparison.json) resolves the bundled Bambu
TPU 85A and TPU 90A H2C presets and the 0.18 mm Balanced Quality process.
Temperatures, flow and material speed limits follow the corresponding Bambu
material preset. The selected 90A preset supplies 225 °C nozzle, 35 °C bed,
flow ratio 1.0, 2.8 mm³/s flow limit, 1 mm retraction at 10 mm/s,
100% cooling, and a 14-second minimum layer time. Native TPU slicing owns
layer-change retraction; no manual retraction or flow tuning is applied.

| Setting | Successful black 85A | White 90A |
| --- | --- | --- |
| Nozzle | 225 °C | 225 °C |
| Bed | 35 °C, Textured PEI | 35 °C, Engineering Plate with glue |
| Flow ratio | 1.0 | 1.0 |
| Volumetric limit | 2.2 mm³/s | 2.8 mm³/s |
| Minimum layer time | 20 s | 14 s |
| Mark2 requested trim | +0.04 mm | +0.04 mm |
| Native emitted trim | +0.02 mm | +0.04 mm |

The retained seal-specific process uses Arachne walls and 100% zig-zag fill,
including the associated solid-fill and top/bottom surface pattern settings.
The 0.30 mm first layer, 0.18 mm normal layers, 0.62 mm nominal line width,
two walls and three top/bottom shells match the selected Bambu process.
No supports are required. Model, brim and support bead clearance is measured
against the right nozzle’s usable bed area, with a 123.39 mm minimum inset.

Mark2 retains its standard +0.04 mm requested trim. Bambu’s Textured PEI
compensation subtracts 0.02 mm; the engineering plate emits +0.04 mm directly.
Timelapse and bed leveling are On at Send, flow dynamic and nozzle offset
calibration are Auto, and probing clump detection remains off.

The [native review](native-review.json) binds ten complete deposition layers,
archive/G-code checksums and the engineering-plate trim. Its native estimate
is about 35 minutes and 5.77 g using the saved density. The
[launch receipt](launch.json) records the foreground transaction and identity.
Physical fit and appearance of the white 90A gasket remain unobserved.
