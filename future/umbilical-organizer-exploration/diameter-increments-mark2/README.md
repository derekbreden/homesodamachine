# Three organizer bore increments — Mark2

This plate contains three production-size PET-GF organizers. A is byte-identical
to the production STL captured for this print, including the drain bore's 0.10 mm diameter increase
from the accepted L article. B adds 0.10 mm to every saved hole diameter; C adds
0.20 mm. The signal passage receives the same increments as the four tube bores.
Stock, bore axes, chamfers and upright orientation remain the saved geometry.
There is no embossing or other identification geometry.

Facing the printer from the front, identify the pucks **left to right: A, B, C**.
Keep that identity when removing them. Their centres are at X119.5, X162.5 and
X205.5 mm, all at Y160 mm; adjacent stock edges are 11 mm apart.

| Puck | Relative diameter increment | Three quarter-inch bores | 4 mm drain bore | Signal passage |
| --- | ---: | ---: | ---: | ---: |
| A — left, saved | 0.00 mm | 6.65 mm | 4.30 mm | 5.00 mm |
| B — centre | +0.10 mm | 6.75 mm | 4.40 mm | 5.10 mm |
| C — right | +0.20 mm | 6.85 mm | 4.50 mm | 5.20 mm |

The [reported fit comparison](physical-result.json) selects A for the three
quarter-inch bores and B for the 4 mm drain bore. The
[production organizer](../../../hardware/printed-parts/faucet/umbilical-organizer/README.md)
combines Ø6.65 mm beverage bores with Ø4.40 mm drain bore and retains its
Ø5.00 mm signal passage. The combined article is unprinted. These are
feature-level fit results, without quantified force or endurance readings.
The [physical acceptance record](../../../hardware/printed-parts/faucet/umbilical-organizer/physical-acceptance.json)
preserves the original L result and binds the current selections to A and B.

The saved single-puck [preparation](../drain-fit-mark2/README.md) supplies the
settings unchanged: Mark2's fixed left hardened standard-flow 0.4 mm nozzle,
physical black PET-GF mapped to PET-CF/GFT01 external slot254, Textured PEI,
0.20 mm first layer and 0.24 mm above it, two walls and 15% grid infill.
No supports, brim, programmed pause or probing clump checks are emitted.
Nozzle temperatures are 265°C first/280°C above; bed 80°C; flow ratio 0.9555.
XY hole and contour compensation are zero; elephant-foot compensation is 0.15 mm.
Mark2's requested +0.04 mm trim emits `G29.1 Z0.02` after `G29.1 Z0`.

The native estimate is **33 min 49 s**, **12.28 g** at the saved profile density.
All 42 layers are shared by the three organizers, ending at commanded Z10.04 mm.
The complete conservative bead envelope retains **103.29 mm** bed clearance.
Every second-layer wall segment intersects the first-layer commanded footprint;
that reading does not establish physical adhesion.

- [Editable project](2026-10-09-organizer-saved-plus010-plus020-petgf-left04-z004-mark2.3mf)
- [Native print archive](2026-10-09-organizer-saved-plus010-plus020-petgf-left04-z004-mark2.gcode.3mf)
- [Preparation, source hashes and native checks](2026-10-09-organizer-saved-plus010-plus020-petgf-left04-z004-mark2.print.json)
- [Native preview](plate_1.png) and [first/second-layer contact review](first-second-layer-review.json)
- [Fresh both-printer preflight](preflight.json), [launch plan](launch-plan.json) and [launch receipt](launch.json)
- [Manual preparation script](../prepare_increment_trial.py), which never submits a print

Foreground options are Timelapse On, Auto bed leveling On, Flow dynamic
calibration Auto and Nozzle Offset Calibration Auto. No scheduled monitor or
automatic resume is requested.

Mark2 accepted task/job `1325126748` at 2026-10-09 22:37:36 CDT
(03:37:36 UTC) after one foreground import and one Send. Fresh
readings of both machines confirm the exact new archive RUNNING with 42 layers,
print error0 and no HMS entries. Mark1 continues its back-top job `1324612230`;
its recorded accepted start at 2026-10-09 22:46:10 UTC is more than 180 seconds
before this launch. The native completion forecast is around 23:11 CDT on
October 9. Startup telemetry does not establish first-layer adhesion or bore fit.
