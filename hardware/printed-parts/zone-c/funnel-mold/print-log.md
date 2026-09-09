# Funnel mold print log

## Cavity — 2026-09-09, settings per [`funnel-mold-cavity-2026-09-09.gcode.3mf`](funnel-mold-cavity-2026-09-09.gcode.3mf)

Derek reported starting the print and saving the editable project afterward.
Bambu Studio's Mark2 device page identifies plate 2, the cavity, with 315 layers,
22 h 50 min 33 s estimated duration and 1,271.49 g PETG. The linked job archive
contains the G-code from that Bambu Studio session; its embedded checksum passes.

- Printer: `Bambu Lab H2C 0.8 High Flow +0.04 Z trim`; left extruder.
- Filament: `Funnel mold PETG Translucent - HF 255C 18mm3s`.
- Process: `Funnel mold - 0.16 mm slopes - 0.40 mm structure`.
- `nozzle_temperature` **255 °C** (initial 255).
- `layer_height` **0.40 mm** (initial 0.40), with the cavity's 0.16 mm fine bands.
- Bed: Textured PEI, 70 °C.
- High Flow cap: 18 mm³/s; flow ratio 0.97.
- Four walls, 100% residual fill, supports disabled.
- Start-code trim commands: `G29.1 Z0`, then `G29.1 Z0.02` (stock −0.02 plus +0.04).
- Left Auto Refill panel: PETG Group 1 contains A1, A2, A3 and A4.

[The start check](print-start-check.json) records the saved-project and job
digests, geometry comparison, complete setting differences, nozzle assignment and
layer-schedule comparison. The first-run editable save is retained at Git
revision `f039270ea` and contains no embedded G-code.
The cavity and core retain manual left High Flow assignment. The witness plate
records automatic assignment to the right extruder.

Camera observation during preparation: a small purge clump near the rear-left
of the plate. Derek: “I hit it with some canned air.” The following camera view
shows a clear plate during auto bed leveling, with the bed at 70 °C.

Derek reported the first run had adhesion trouble: “The brim lifted up and
caused some problems on our first run.” He requested a brim-free mold with
intentional permanent contact material. The extent of damage and the final
stop time were not recorded.

## Permanent-feet project — 2026-09-09

The [current editable project](funnel-mold-petg-hf08-variable-016-040.3mf) has
permanent rounded feet, an 8 mm cavity frame and 6.4 mm rib lands. Its saved
process is `Funnel mold - no brim - 0.16 mm slopes - 0.40 mm structure`.
Brim and skirt are disabled on all three plates. Both +0.04 and +0.18 mm trim
variants are sliced and inspected; +0.04 mm is the default.

The cavity estimates 23 h 23 min and the core 18 h 39 min. Physical adhesion
and completed-print outcome for this geometry are not yet recorded.
