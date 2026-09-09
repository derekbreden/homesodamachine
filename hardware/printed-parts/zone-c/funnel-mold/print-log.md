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

## Cavity with permanent feet — 2026-09-09, settings per [`funnel-mold-cavity-no-brim-2026-09-09.gcode.3mf`](funnel-mold-cavity-no-brim-2026-09-09.gcode.3mf)

Derek: “Print started. 3mf saved.” Mark2 identifies plate 2, the cavity, with
315 layers, 23 h 23 min 12 s estimated duration and 1,305.22 g PETG. The linked
archive preserves the exact job sent from the active Bambu Studio session;
its embedded G-code checksum passes.

- Printer: `Bambu Lab H2C 0.8 High Flow +0.04 Z trim`; left extruder.
- Filament: `Funnel mold PETG Translucent - HF 255C 18mm3s`.
- Process: `Funnel mold - no brim - 0.16 mm slopes - 0.40 mm structure`.
- `nozzle_temperature` **255 °C** (initial 255).
- `layer_height` **0.40 mm** (initial 0.40), with the cavity's 0.16 mm fine bands.
- Bed: Textured PEI, 70 °C.
- High Flow cap: 18 mm³/s; flow ratio 0.97.
- Four walls, 100% residual fill, supports disabled.
- Brim disabled, width 0; skirt loops 0. Permanent rounded feet, an 8 mm
  cavity frame and 6.4 mm rib lands provide bed contact.
- Start-code trim commands: `G29.1 Z0`, then `G29.1 Z0.02` (stock −0.02 plus +0.04).

[The no-brim start check](print-start-no-brim-check.json) verifies all seven
saved components, the recipe settings, local speed controls, fine-layer ranges,
active nozzle and G-code checksum. The first-layer commands match the reviewed
slice exactly apart from progress reports. The saved cavity plate uses Auto For
Flush and resolves to the left High Flow nozzle; the witnesses and core retain
manual left High Flow assignment.

The [editable save](funnel-mold-petg-hf08-variable-016-040.3mf) contains the model
and settings without embedded G-code. The complete three-plate reviewed slice
is retained at Git revision `911c25b1c`. The alternate +0.18 project remains
fully sliced.

The live camera showed an unobstructed textured plate during auto bed leveling.
At 11:05 CDT, Mark2 is printing layer 1 of 315 at 255 °C nozzle and 70 °C bed.
Early paths are visible; the first layer is incomplete and its adhesion is not
yet established from this camera view. Completed-print outcome is not yet recorded.
