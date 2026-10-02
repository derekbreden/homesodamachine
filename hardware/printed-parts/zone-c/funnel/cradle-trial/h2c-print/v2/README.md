# Funnel elbow-cradle v2 print

One receiver on Mark2 and one cradle on H2C, using Funnel 2's frozen v2 meshes
and the [bench procedure](../../README.md). The v1 [physical record](../../physical-acceptance.json)
reports easy insertion; retention and cycle testing are not reported. V2 has a
2 mm higher body top, 9.24 mm wing free length and 15.05 mm body half-width.
The hook tips have 0.15 mm nominal clearance to the counterbore walls, and the
frame web beside the drain hole is 4.75 mm. Nominal 5.5% root strain is a CAD
estimate; insertion, elastic return and retention require the printed trial.

| Part | Printer | Requested Z trim | Native estimate | State |
| --- | --- | --- | --- | --- |
| Test receiver | Mark2 | +0.04 mm | 23 min 00 sec | Reviewed; submission pending |
| Test cradle | H2C | +0.18 mm | 30 min 29 sec | Accepted task 1303335008 |

The [cradle launch](cradle-h2c-launch.json) verifies the new task and a successful
printer reply. The receiver launch remains pending the shared-circuit interval.

Both use external black PET-GF, labelled PET-CF, on the fixed left hardened
0.4 mm nozzle. The 0.20 mm first layer and 0.24 mm layers retain the production
print poses. Textured-plate compensation emits `G29.1 Z0.02` on Mark2 and
`G29.1 Z0.16` on H2C. Elephant-foot compensation is zero, with no brim.
Print options are Timelapse On, Bed Leveling On, Flow Dynamic Calibration Auto
and Nozzle Offset Calibration Auto. Starts and resumes across printers remain
at least 180 seconds apart. The user's request for new prints supplies bed
clearance for this pair.

[Receiver preflight](receiver-mark2-preflight.json) and
[cradle preflight](cradle-h2c-preflight.json) bind the frozen STL, native input
project, archive and G-code hashes. [Receiver preparation](receiver-mark2-preparation.json)
and [cradle preparation](cradle-h2c-preparation.json) save the geometry source
snapshot. The source commit binding is pending Funnel 2's export commit.

The [receiver support audit](receiver-mark2-support-audit.json) finds no supports.
The [cradle support audit](cradle-h2c-support-audit.json) includes all support paths,
including any bodies without interface labels. Exactly two supports rise from
the bed outside the cradle's X sides and contact only the outward hook undersides.
There are no supports in the upward-opening pocket, no roots on the model and
no unlabelled support bodies. Interfaces finish at Z 33.08 mm; the first hook
layer is Z 33.80 mm, with 0.48 mm between its nominal bottom and the interface.
No support blockers or geometry changes are needed.

Every second-layer model bead has more than half its area over the first-layer
footprint. Native ZIP integrity and G-code MD5 checks pass. The frozen STL bytes
match the exporting session's receipt before and after slicing. The previews
show the receiver on its flat underside and the cradle bottom down with its
pocket open upward.

Remove the two supports outward into open space beside the cradle, retaining
the hook bearing dimensions. Follow the bench procedure with the real PP0308E
elbow: seating without rocking, hand insertion and release, hook retention and
five cycles without cracking, whitening or residual wing bend. Record the
physical result beside the trial parts. Print telemetry establishes completion;
physical fit, retention and operating life remain unverified for v2.

To prepare a fresh native archive revision from these frozen v2 meshes:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/cradle-trial/h2c-print/v2/prepare_v2.py --revision 3
```

Each native revision has its own immutable `.cache/prints/` directory.
