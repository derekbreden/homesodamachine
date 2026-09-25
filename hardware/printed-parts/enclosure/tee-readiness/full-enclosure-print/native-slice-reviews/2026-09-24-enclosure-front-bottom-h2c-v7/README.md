# Front-bottom — H2C

H2C accepted task **1279923918** for the current front-bottom in black PET-GF on
left external spool 254. Native estimate: **21 h 58 m 44 s**, 1502 plate layers.
The [launch receipt](launch.json) identifies the accepted archive. The
[subsequent reading](observed-running.json) confirms RUNNING with the matching
job name and 1502-layer total, nozzle heating during startup, no print error
and no HMS alert.

The shell prints upright on its flat underside. Its STEP/STL geometry and plate
placement are unchanged. The first layer is 0.20 mm and the base height is 0.24 mm.
Complete downward R6 handhold rounds span print Z 29.25–41.25 mm. Their fine-layer
band begins at 29.15 mm and continues through the visible flute run-outs to
44.3 mm; the [emitted layer check](verification.json) confirms 0.08 mm coverage
through the entire curves and run-outs.

**Six walls apply only at Z 29.15–41.3 mm.** The normal setting is two walls,
including the upper flute run-outs. The [wall check](wall-scope-check.json) reads
six paths through the downward round and two before and after it. Inner walls
precede outer walls and infill; original speeds, accelerations, temperatures,
fans and 15% infill/wall overlap remain intact. Physical performance of this
six-wall treatment on front-bottom remains unassessed.

Support paint blocks all 15,984 downward rounded handhold facets. A 0.8 mm inset
on the flat lifting ceilings keeps support beads clear of their rounded borders.
The [contact check](round-contact-check.json) examines all 8,161 support road
segments near the round band, including Support, Support transition and Support
interface, using full bead width plus 0.05 mm XY allowance. None approaches a
rounded face within 0.60 mm vertically. Interface bead footprints stay entirely
within the actual flat-ceiling projections.

Four bed-rooted support bodies retain four functional contacts: the west and
east flat lifting ceilings and the two seam-catch undersides. The handhold trees
pull downward through open bottoms; the catch trees detach outboard through the
exposed flank grooves before hardware and top-shell installation. Their
[removal review](support-removal-review.json) preserves those working faces.
Physical cleanup effort and finish remain print observations.

On 2026-09-25 Derek reported that both printers lost power when their power cord
was accidentally unplugged. H2C was mid-print, mid-extrusion, and recovered with
no visible defect at the interruption point. A subsequent software reading at
18:26:02 UTC showed this front-bottom job RUNNING at layer 1170 of 1502. That
reading is after recovery; it does not identify the interrupted layer.

Requested H2C trim is +0.18 mm, emitted +0.16 mm for Textured PEI. Timelapse and
bed leveling are On; flow and nozzle-offset calibration are Auto. A macOS
notification obstructed the first transaction before the send dialog opened.
The next fresh import settled for 20 seconds and submitted with one Send click;
the printer returned SUCCESS. The preceding job's dirty-nozzle-camera advisory
is absent from the accepted job's status. The [manifest](manifest.json) binds
source geometry, slice, verification and launch.
