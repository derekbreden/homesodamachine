# Tee carrier on Mark2 — 1.00 mm upper clearance

Mark2 accepted task **1297480230** at 2026-09-30T22:25:06.578180+00:00.
The native estimate is **1 h 45 min 40 s**, **55.82 g**, **140 layers**.
Only the complete tee carrier is on the plate. Black PET-GF uses the left 0.4 mm
hotend with requested +0.04 mm trim, emitted as +0.02 mm on textured PEI.

The upper gap is **1.00 mm**: 0.25 mm running clearance, 0.25 mm for the rough
roof and 0.50 mm for low-force motion. The lower gap is **0.25 mm**. These are
separate contacts; total vertical play is 1.25 mm. The front-top carrier opening
matches the printed reference, task 1277245499. Spring bores, tee stations and
release travel keep their positions. [Geometry checks](geometry-check.json)
bind the unchanged geometry to that opening.

The bottom chamfer/taper uses a 0.20 mm first layer and normal 0.24 mm layers
above it. Six walls apply through print Z 6.1 mm; two walls above. The complete
top R6 uses 0.08 mm layers. Saved speeds, wall-first order and 15% overlap apply.
Supports, brim and elephant-foot compensation are off.

[Native verification](verification.json) checks the source hashes, archive,
layer bands, emitted wall counts and absence of every support body. The first
two [layer transitions](first-layer-overlap.json) have supported outer-wall
centerlines and 94.42% / 93.91% bead-footprint overlap. The first-to-second
transition has at least as much support as the second-to-third transition.
The [printer comparison](mark2-retarget-check.json) proves identical embedded
geometry, placement and layer ranges to the reviewed H2C input; only trim and
printer labels differ.

[Preflight](preflight.json) records Mark2 idle, both printers error-free, the
left black external spool and the user's cleared-bed authorization. The
[launch receipt](launch.json) binds the original and imported archive hashes,
usual startup options including Auto nozzle offset, and
5014.8 seconds after H2C's display-receiver start.
[Postlaunch](postlaunch.json) confirms this task RUNNING without errors.

Physical qualification: use the existing front-top with the actual tees and
springs to check free sliding, spring return and unwanted play. The accepted
chamfer/taper surface reference does not establish this gap's physical fit.
