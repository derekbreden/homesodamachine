# Magnetic-float ASA Aero combined plate at +0.04 mm trim

One frozen core and one insert share Mark2's Textured PEI plate, printing by
layer on its right standard-flow hardened 0.4 mm nozzle. The operator requested:
**"Stopped again. Bed clear. Try same plate again back to 0.04 all else the same."**

The combined job is accepted as **Mark2 task 1304010811**,
`magnetic-float-pair-mark2-aero-v4.gcode.3mf`. One Send received
`project_file SUCCESS`, and the matching new task entered `RUNNING`, layer 0
of 220. This establishes startup; visual first-layer acceptance, printed
density and physical fit remain unreported. The native estimate is **1 h
56 min**, with **18.05 g** slicer mass and **18.03 g** model extrusion mass.

At 2026-10-03 04:38 UTC, the same task reported `FAILED`, layer 0, with
error **0300400C** (50348044). Bambu Connect and the installed Bambu Studio
English error catalog identify it as **"The task was canceled."** No first-layer
progress was observed for this trial. Who canceled it and any physical print
problem are unreported. No retry or resume has been submitted; neither part
has a completed-print or physical-acceptance result.

## Selected recipe

| Setting | Value |
| --- | --- |
| Material and source | Bambu ASA Aero White 46100, GFB02; AMS HT unit 128 tray 0 |
| Actual Send mapping | HT - A ASA-AERO R, under Right Nozzle |
| Nozzle / bed / chamber | 270 / 90 / 60 °C |
| Flow ratio | 0.52 |
| First / normal layer height | 0.20 / 0.20 mm |
| Nominal line width | 0.48 mm |
| Ordinary wall / infill speeds | 80 mm/s |
| First-layer wall / infill speed settings | 50 / 105 mm/s, with acceleration and cooling limits |
| Walls / top / bottom layers | 3 / 5 / 5 |
| Infill | 100% zigzag |
| Requested user Z trim | +0.04 mm |
| Emitted textured-plate correction | `G29.1 Z0.02` after reset to 0 |
| Skirt / brim / supports / pauses | None / none / none / none |
| Elephant-foot compensation | 0 mm |
| XY contour / hole compensation | +0.05 / −0.05 mm |
| Print order | Both objects by layer, on one plate |
| Send options | Timelapse On, bed leveling On, flow calibration Auto, nozzle offset calibration Auto |

The user trim adds to the stock −0.02 mm Textured PEI correction. Adhesive
application is unreported. Cool the parts and plate to **35 °C or below**
before release.

## Frozen plate and emitted commands

This is physical trial **v3**, using native archive revision **v4**. Geometry
and orientation are bound to export commit
`f3cefbe360b7a8019741d177868d1e6c6770b93f`. The core STL SHA starts
`63d12cbb` and the insert starts `c69cdc55`; full hashes are in the preflight.
Their centres are (125,145) and (175,145) mm, with the original bases at Z=0.

The revision derives from the reviewed native combined plate. A byte comparison
verifies every non-trim printer command is identical, including all extrusion
paths, travel, feed rates, temperatures and cooling commands. The only changed
executable command is the plate's Z trim. The corresponding configuration and
comments agree with +0.04 mm user trim, and the G-code MD5 has been updated.
The old frozen archive is retained. All native geometry, previews, non-trim
settings and other archive members are unchanged.

The parent native reviews therefore retain their scope: two objects, no warnings,
no support/skirt/brim/prime-tower paths, no insertion pauses, and each object's
minimum second-layer nominal bead overlap above 56%. The core has 220 layers
and the insert has 50. The preview was inspected. Those path checks do not
establish physical adhesion, density or fit.

- [Preflight, parent archive binding and frozen hashes](pair-preflight.json)
- [One-Send guard and printer acceptance](pair-mark2-launch.json)
- [Queue](queue.json)
- [Preparation and exact command comparison](prepare.py)
- [Operator stop report for the preceding combined trial](../v2/pair-mark2-launch.json)

![Combined plate native preview](pair-preview.png)
