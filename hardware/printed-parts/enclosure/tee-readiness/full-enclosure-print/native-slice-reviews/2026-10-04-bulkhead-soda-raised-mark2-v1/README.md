# Face-up raised SODA ring on Mark2

Mark2 accepted task **1307088867** at 2026-10-04T05:16:40Z. The native estimate is
**13 min 58 sec**, **3.23 g** at the saved profile density. The plate holds one
`carb`-station ring: a blue body with white SODA letters.

The ring prints face up with **0.48 mm raised lettering** and no supports, on the
process of the accepted [TAP and FLAVOR collars](../2026-09-30-bulkhead-raised-mark2-v2/README.md).
Layers are 0.20 mm first and 0.24 mm normal. A 0.12 mm closing layer ends at the
2.0 mm fitting face, and two 0.24 mm letter layers rise to 2.48 mm. The letters
clear the union fitting's flange by 1.20 mm in CAD.

| nozzle | spool | paths |
| --- | --- | --- |
| left 0.4 mm | white PET-GF, external 254 | letters |
| right 0.4 mm | blue PET-GF, external 255 | body |

Both spools read PET-CF in the printer. The right nozzle's native extruder offset
applies X −0.50 mm, Y +0.70 mm to the blue body's paths. This is the correction in the
[Mark2 registration record](../../../../../calibration/dual-nozzle-registration/mark2-registration.json).
The white letters and nominal CAD keep their original coordinates. The
[registration comparison](registration-verification.json) checks every
object/tool/layer against the [uncorrected slice](uncorrected-preparation.json).
The requested Z trim is +0.04 mm, emitted as `G29.1 Z0.02` on Textured PEI.
Timelapse and bed leveling are On, and flow and nozzle-offset calibration are Auto.

[`prepare.py`](prepare.py) takes the geometry from `raised_rings.build('carb')`.
It snapshots the meshes and their source commit into
[`geometry-snapshot.json`](geometry-snapshot.json) and builds the plate from that
snapshot. [`verify.py`](verify.py) checks the archive, layers, letter nozzle,
filament colours, trim, support absence and the correction
([verification](verification.json)). [Preflight](preflight.json) records both
printers before the send, and [launch](launch.json) records the acceptance.
Mark2 reported `FINISH` at 05:43:26Z, all 11 layers, no print error or HMS
([postlaunch](postlaunch.json)).

Derek's [photo](../2026-10-04-bulkhead-co2-raised-mark2-v1/physical-result.jpg) of the printed rings shows the white letters crisp and seated in their
recess with no visible offset ([physical result](physical-result.json)); no verdict or mounting fit
was stated.
