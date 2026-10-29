# Single elbow — Siraya Tech Flex TPU 85A Clear

Mark1 accepted task **1337804197** on **2026-10-14 at 00:11:26 CDT**.
The [physical record](physical-result.json) preserves Derek's finished result:
**“Turned out perfect.”** Three finished-part photos show the complete elbow
and its sloping exterior surfaces. Derek also reports **internal stringing**;
the exterior acceptance does not establish clean passages. Completion telemetry
reports FINISH at layer 184/184 with no printer errors. Siraya fit remains
unassessed. Native estimate: **65 minutes / 3.93 g**, using 1.16 g/cm³ for mass.
The record retains the earlier [printer-camera view](past-layer28.png) and
positive report past layer 28.

The [two-object trial](../2026-10-14-compact-two-siraya85a-overhang10-engineering-z000-mark1/README.md)
uses the same geometry, material and thermal recipe with revised seam/travel
settings. Its finished result is separate from this single-article acceptance.

The [loading record](material-loading.json) and [package photo](filament-label.jpg)
identify Siraya Tech Flex TPU 85A Clear, SKU ST3008. The user reports Mark1
ready after the load/purge process. The right external slot reports TPU and
white metadata; the physical material is labelled Clear.

One compact 15 mm tube-socket elbow uses the right fixed **0.6 mm** nozzle,
glued **Engineering Plate**, **35°C bed** and **zero user Z trim**. Native
model members and pose match the prepared overhang10 candidate byte for byte.
The shape retains the cuff dimensions of the rough Bambu TPU 85A article
with [accepted manual fit](../2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json).
That acceptance does not establish fit of this material.

The user requests the lower-temperature trial: **215°C normal layers** and
**225°C first layer**, with the first-layer setting retained from the adhered
earlier articles. The bag gives 210–230°C; Siraya's
[general guide](https://siraya.tech/pages/flex-tpu-85a-filament-user-guide)
gives 200–225°C. Its downloadable H2C 0.6 mm project uses 230°C. The
[material record](material-profile.json) identifies that source and the local
temperature and throughput choices.

Siraya's [H2C 0.6 mm material profile](https://siraya.tech/pages/print-settings-download)
supplies **0.96 flow ratio**, **0.8 mm retraction**, **100% part cooling** and
**auxiliary cooling off**. The local 2.2 mm³/s flow cap and 20-second cooling
slowdown are retained; the downloaded profile allows 8 mm³/s and disables
that slowdown. The process retains 0.20 mm first / 0.12 mm normal layers,
0.62 mm line widths, six requested walls, 100% infill, inner/outer wall order,
5 mm outer brim and no supports.

The [emitted-command review](emitted-command-review.json) uses the shared
[G-code reader](../../../../tools/gcode/README.md) to verify the actual leftmost
lip at **10 mm/s on layers 17–33**. An independent modal-feed scan finds all
13,728 normal-layer moves labelled Outer wall at 10 mm/s. The record also
identifies the single tiny separately labelled Overhang wall move on layer 68
at 25 mm/s. The native temperature transition is `M104 S215` on layer 2;
the stock start emits only `G29.1 Z0` for plate trim.

This trial combines the newly selected material with its material settings,
the user-requested 215°C normal layers and the corrected exterior speed.
It does not isolate a material, moisture, cooling or temperature cause of
curl. The older spool's drying record does not apply to this newly opened spool.

- [Editable project](2026-10-14-compact-single-elbow-siraya85a-overhang10-engineering-right06-z000-mark1.3mf)
- [Native sliced archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/2026-10-14-compact-single-elbow-siraya85a-overhang10-engineering-right06-z000-mark1.gcode.3mf)
- [Native readback](native-readback.json)
- [Manual preparation script](prepare_mark1.py)
- [Startup spacing](startup-spacing.json)

The preparation script only slices offline. Submission uses the reviewed
archive and the standard sender; no global printer preset is changed.
