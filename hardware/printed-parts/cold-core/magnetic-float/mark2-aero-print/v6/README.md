# Magnetic-float ASA Aero on glued Engineering plate

The combined frozen core and insert plate is accepted on Mark2 as task
**1304125241**, `magnetic-float-pair-mark2-aero-v6.gcode.3mf`, using the right
standard-flow hardened 0.4 mm nozzle and a glued Engineering plate. One Send
received `project_file SUCCESS`. Matching task telemetry reached layer **1 of
220** at 06:08:41 UTC on 2026-10-03, with the right nozzle at 270 °C, bed at
90 °C and chamber at 60 °C, and no reported print error or HMS alert. These are
observed readings, and the layer count describes printer progress. This is
physical trial **v6**, native archive **v6**. Visual adhesion and physical fit
remain unreported. Full acceptance, mapping, heater readings
and startup spacing are in the [launch record](pair-mark2-launch.json).
The [prior plate report](../v5/physical-observations.json) records the limited
scope of the Textured PEI result.

Both objects print by layer. The recipe uses **+0.04 mm user Z trim**, emitted
as `G29.1 Z0.04` after reset to zero, **270 / 90 / 60 °C nozzle / bed / chamber**,
and **0.52 flow**. There is no skirt, brim or support on the parts. ASA Aero White
GFB02 uses AMS HT unit 128 tray 0 on the right nozzle. Normal Send options are
Timelapse On, bed leveling On, flow dynamic calibration Auto and nozzle offset
calibration Auto.

The front-right priming strip has 12 adjacent 60 mm passes at 20 mm/s, a 0.20 mm
layer and 0.48 mm lines. Its footprint including bead width is 60.48 × 5.43 mm,
with centreline X230–290 / Y15–19.95. It uses about 13.70 mm filament feed and
0.033 g. A 5 mm wipe ends the strip; the part program retains its own retraction.
Adaptive leveling covers X110–291 / Y14–160 mm. The complete strip program is
byte-identical to the reviewed corner-priming trial and stays clear of the parts
and bed exclusions.

The native Engineering export selects `M972 S36 P0 C0 X1` for plate-surface
detection and emits the Engineering compensation branch. These are the only
startup printing-command differences associated with the plate selection.
Every part printing command and every native geometry member is unchanged.
Only progress estimates differ within the part program. Core and insert STL
hashes remain `63d12cbb…` and `c69cdc55…`, bound to export commit
`f3cefbe360b7a8019741d177868d1e6c6770b93f`. Full hashes are in the preflight.

The native estimate is about **1 h 57 min**, including the corner strip; actual
heating, calibration and bed probing times vary. The native preview shows the
parts; startup priming coordinates are verified separately.

Startup success means the strip stays on the plate, no loose strand reaches
the parts and the first part loop adheres. Printer progress is not visual
adhesion or evidence of density, fit or buoyancy. The parts and plate retain a
conservative **35 °C** cooling threshold before release from the glued plate.
No physical acceptance is recorded for this Engineering trial.

The active printer reports local job `RC62 magnetic float - aero`, task ID
`6700`, with cloud job ID `0`. Its archive identity is unverified, and its
progress is recorded separately in [operator observations](operator-print.json).
The user reports that feeding from the Polymaker drybox works better, with
flaking and material carried during travel moves still present. The current
print is being allowed to finish. These observations establish neither the
local archive settings nor the terminal state of accepted cloud task 1304125241.

- [Preflight and native comparison](pair-preflight.json)
- [Native preparation](prepare.py)
- [Queue](queue.json)
- [Prior physical plate report](../v5/physical-observations.json)

![Combined part preview](pair-preview.png)
