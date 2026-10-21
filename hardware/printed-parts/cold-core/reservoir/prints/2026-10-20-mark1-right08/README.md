# Reservoir and cap on Mark1

Plate 1 contains the current **reservoir-left** and matching **reservoir-cap-left**:
a full-height body with one flat floor, with fill and draw entering through the cap.
The body prints mouth up; the cap prints exterior face down. The
[current project](../../reservoir.3mf) preserves the September 0.24 mm PETG recipe
with ironing off, right-nozzle assignment and Mark1's calibrated trim.

Use Mark1's **right 0.8 mm Standard-flow hotend**, clear Bambu PETG Translucent
from **AMS A4**, and Textured PEI. The recipe uses **255 °C** nozzle, **70 °C** bed,
**0.30 / 0.24 mm** first / normal layers, **0.97** flow ratio, **6 mm³/s** volumetric
limit and **+0.18 mm** user trim, emitted as **G29.1 Z0.16**. Native estimates are
**19 h 21 min, 410.28 g and 833 layers**, with an empty warning field.

The [native review](../../slice-review.json) identifies the current geometry,
right nozzle, trim and full-bead envelope. Model, support and brim beads stay at
least **70.519 mm inside the right nozzle's usable bed**. All seven detected
support bodies start at the bed. The matching body and cap are 10.042 mm apart
at their nearest deposited bead envelopes.
The [float integration record](../../../magnetic-float/all-aero/integration-check.json)
checks upright float travel against these body/cap exports. Physical water hold,
cap sealing and installed float motion remain unassessed for this article.

## Launch file

[prepare_launch.py](prepare_launch.py) selects plate 1 from the reviewed native
two-plate archive and makes a print-only copy. [Packaging](packaging.json) binds
the hashes and confirms unchanged native G-code and project settings.
The launch file is
`.cache/reservoir-mark1-right08/slice/2026-10-20-reservoir-left-cap-clear-right08-z018-mark1.gcode.3mf`.

Derek requests **A4 → A2 → A3 → A1**, using each spool fully. All four trays
report matching clear PETG and form an Auto-Refill group. The available controls
select A4 but do not set a custom backup order. Launch awaits the spool-order
choice; no print has been sent.
