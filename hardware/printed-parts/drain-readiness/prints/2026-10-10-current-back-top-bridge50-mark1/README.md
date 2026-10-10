# Back top — Mark1

Tree (auto), Default style uses a **50 mm maximum bridge length**. Bambu's
bridge exemption compares both dimensions of a classified bridge surface's
bounding box. The short-span tie roofs include surfaces up to 31.6 mm long.
The historical shared profile at commit `06bae4528` records this 50 mm value.
This limit applies to the back-top profile.

The model, placement, 23 solid reinforcement modifiers and layer schedule
match the [stopped article](../2026-10-09-current-back-top-tree-mark1/physical-result.json).
All other process settings and Bambu's automatic support choices are retained.
Mark1 uses its normal +0.18 mm requested/+0.16 mm emitted Textured PEI trim,
black PET-GF, left external slot 254 and fixed hardened standard-flow 0.4 mm
nozzle. First layer is 0.20 mm and ordinary layers are 0.24 mm.

The native estimate is **27 h 23 min**.
The complete model/support/brim bead margin is 21.40 mm.
The [native review](native-review.json) binds the archive and unchanged meshes.
The [23 floor-window reading](tie-cavity-support-review.json) finds zero
support bead-envelope crossings. The [full cavity reading](full-cavity-support-reading.json)
finds zero support centrelines in its ten declared regions, including the ASSE
passage. All 579,816 remaining support roads clear the nine protected show
faces in the [exterior review](show-support-clearance-summary.json).
The [larger contact reading](large-overhang-support-review.json) retains
automatic interface contact beneath all eight inspected large original
support-contact components. These readings establish commanded paths;
physical support release, finish and installed fit are pending.

The [launch receipt](launch.json) records the one authorized foreground Send.
Mark1 accepted task/job `1325371485` at 2026-10-10 01:36:57 CDT.
The native estimate places completion near 2026-10-11 05:00 CDT.
Timelapse and leveling are On; flow and nozzle-offset calibration are Auto.
Probing clump detection is disabled. No automatic resume or monitor is scheduled.
