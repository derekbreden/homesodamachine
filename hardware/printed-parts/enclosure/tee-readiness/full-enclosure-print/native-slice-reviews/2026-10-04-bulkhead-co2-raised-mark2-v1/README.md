# Face-up raised CO2 ring on Mark2

Mark2 accepted task **1307189764** at 2026-10-04T06:32:18Z. The native estimate is
**13 min 36 sec**, **3.15 g** at the saved profile density. The plate holds one
`co2`-station ring: a red body with white CO2 letters.

The ring prints face up with **0.48 mm raised lettering** and no supports, on the
process of the [SODA ring](../2026-10-04-bulkhead-soda-raised-mark2-v1/README.md)
and the accepted [TAP and FLAVOR collars](../2026-09-30-bulkhead-raised-mark2-v2/README.md).
Layers are 0.20 mm first and 0.24 mm normal. A 0.12 mm closing layer ends at the
2.0 mm fitting face, and two 0.24 mm letter layers rise to 2.48 mm. The letters
clear the neoFit ABU44 flange by 1.56 mm in CAD, with no intersection.

| nozzle | spool | paths |
| --- | --- | --- |
| left 0.4 mm | white PET-GF, external 254 | letters |
| right 0.4 mm | red PET-GF, external 255 | body |

Both spools read PET-CF in the printer. The right nozzle's native extruder offset
applies X −0.50 mm, Y +0.70 mm to the red body's paths. This is the correction in the
[Mark2 registration record](../../../../../calibration/dual-nozzle-registration/mark2-registration.json).
The white letters and nominal CAD keep their original coordinates. The
[registration comparison](registration-verification.json) checks every
object/tool/layer against the [uncorrected slice](uncorrected-preparation.json).
The requested Z trim is +0.04 mm, emitted as `G29.1 Z0.02` on Textured PEI.
Timelapse and bed leveling are On, and flow and nozzle-offset calibration are Auto.

[`prepare.py`](prepare.py) builds the geometry with `raised_rings.build('co2')`
from the committed sources. It loads `bulkhead_ring.py`, `raised_rings.py`,
`_y_wall_dimensions.py` and `_materials.py` from HEAD in place of their working
copies, and records the commit and every other loaded source in
[`geometry-snapshot.json`](geometry-snapshot.json). [`verify.py`](verify.py) checks
the archive, layers, letter nozzle, filament colours, trim, support absence and the
correction ([verification](verification.json)). [Preflight](preflight.json) records
both printers before the send.

The first send, at 06:05Z, came while the right nozzle was still at 232 °C from
loading the red spool. Mark2 refused it with `ERROR STATE` 0502400D, "filament
loading/unloading not completed" ([rejected send](rejected-send.json)). The same
archive sent after the load cycle ended was accepted ([launch](launch.json)).
