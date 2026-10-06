# PETG ironing calibration record

**OFF** is the selected finish for the [current reservoir recipe](../README.md#next-print).
Derek reported that it was the best result by a long shot, the smoothest and
best feeling. Among the ironed conditions, he tentatively preferred the entire
**30% flow column: 15/30, 30/30 and 60/30**. **60/30 felt more papery** than
the other two. No preference between 15/30 and 30/30 was reported.
[Physical observation](prints/2026-10-06-mark2-squares-v1/physical-result.json).

## Printed comparison

Mark2 task **1314288755** printed nine flat **35 × 35 mm squares** and one
un-ironed **OFF** reference. Each had an uninterrupted top face and a label
on a lower tab. The material was Bambu PETG Translucent Clear, with the
**left 0.8 mm Standard hotend** on textured PEI, starting on **A4**.
[Launch and completion](prints/2026-10-06-mark2-squares-v1/launch.json).

Labels read **speed in mm/s / ironing flow in percent**. All nine ironed
conditions used **0.15 mm spacing**, a 0.31 mm inset and zig-zag ironing.
Ironing applied only to the highest face at Z = 1.50 mm; the label tabs had
no ironing.

| Speed | 10% flow | 20% flow | 30% flow |
| --- | --- | --- | --- |
| 15 mm/s | 15/10 | 15/20 | 15/30 |
| 30 mm/s | 30/10 | 30/20 | 30/30 |
| 60 mm/s | 60/10 | 60/20 | 60/30 |

Each square was 1.50 mm thick: a 0.30 mm first layer and five 0.24 mm layers.
The process used **255 °C** nozzle, **70 °C** bed, **0.97** filament flow
ratio, **6 mm³/s** ceiling, six requested Arachne walls, 100% fill and the
September cooling and seam settings. There were no supports.
Bambu Studio 02.08.02.61 estimated **25.53 g and 1 h 55 min**, including
**46 min of ironing**.

The [native review](slice-review.json) verified the nine ironing conditions,
zero ironing on OFF, left-nozzle assignment and Mark2's **+0.04 mm user Z trim**,
emitted as **`G29.1 Z0.02`** after the initial zero reset. The full bead
footprint stayed **84.98 mm from the nearest usable bed edge**; specimen
bead envelopes were at least **4.90 mm apart**.

![Flat-square calibration and native ironing paths](plate-layout.png)

This was a flat-surface finish comparison. It supplied no sloped-surface,
gasket-sealing, reservoir water-hold or lifetime result.

## Source and earlier observations

[study.json](study.json) preserves the settings, geometry and source hashes.
The completed project's 3MF and generator/reviewer sources are retained in
Git at **`ee5270c53cd4cfda339ffc97352cf9a16bc392d9`**, under this directory. The current reservoir project is
[reservoir.3mf](../reservoir.3mf).

[Feature-crop comparison observation](prints/2026-10-06-mark2-centered-v3/physical-result.json) ·
[Centered feature-crop launch](prints/2026-10-06-mark2-centered-v3/launch.json) ·
[Stopped edge-placement job](prints/2026-10-06-mark2/physical-result.json).
The earlier projects are identified by their launch records and retained in Git.

The calibration used flow, speed and spacing variables described in Prusa's
[ironing documentation](https://help.prusa3d.com/article/ironing_177488).
