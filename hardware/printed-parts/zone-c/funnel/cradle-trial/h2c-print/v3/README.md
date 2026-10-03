# Funnel elbow-cradle v3 print

One frozen Funnel 2 cradle on Mark2, with the printed v2 receiver from task
`1303345379` reused for the [bench procedure](../../README.md). The cradle has
12.24 mm free wings and a 30.1 mm body width. Nominal 3.3% root strain is a CAD
estimate. The [physical record](../../physical-acceptance.json) rates v3 insertion
"Very good" with the printed v2 receiver. Retention and cycle testing are not
reported. The [v4 print records](../v4/README.md) describe the current trial pair.

| Part | Printer | Requested Z trim | Native estimate | State |
| --- | --- | --- | --- | --- |
| Test cradle v3 | Mark2 | +0.04 mm | 29 min 31 sec | Finished; task 1303516417 |
| Reused test receiver v2 | Mark2 | +0.04 mm | Already printed | Finished; task 1303345379 |

The [allocation](allocation.json) records both beds clear and Mark2's longer
idle period with black PET-GF loaded. The cradle uses external black PET-GF,
labelled PET-CF, on the fixed left hardened 0.4 mm nozzle. It retains its bottom
on the bed and its pocket opening upward, with a 0.20 mm first layer and 0.24 mm
layers. Textured-plate compensation emits `G29.1 Z0.02` for the requested
+0.04 mm trim. Elephant-foot compensation is zero, with no brim.

[Preflight](cradle-mark2-preflight.json) and
[preparation](cradle-mark2-preparation.json) bind the frozen cradle STL, native
input project, archive and G-code hashes. Every saved geometry source hash
matches export commit `5a1fb5f08`. The cradle STL SHA-256 is
`ab1875532b46a0254c945a2a263b9c00689502c580705a9070b8f558e395a251`.
The reused receiver belongs to the v2 launch and has SHA-256
`cd25b650c948d38fbe8880bfb51b223620adec2f44bfc56b13316797c308bd4e`.

The [native support audit](cradle-mark2-support-audit.json) includes every
support body. Exactly two supports rise from the bed outside the cradle's
X sides and contact only the flat outward hook undersides. There are no model
roots, unlabelled support bodies or support paths in the upward-opening pocket.
Interfaces finish at Z 33.08 mm. The first printed hook layer is Z 33.80 mm,
with a nominal bottom at Z 33.56 mm and a 0.48 mm support gap.

The [native preview](cradle-mark2-preview.png) retains the production print
orientation. Minimum second-layer bead overlap is 75.7%; outer-wall overlap is
99.9%. Native ZIP integrity and G-code MD5 checks pass. No support blockers are
needed for this slice.

The [launch record](cradle-mark2-launch.json) verifies task `1303516417` and a
successful printer reply. The send gate is 5388 seconds after
confirmation of the last H2C task. The background Bambu Connect sender uses
one Send with automatic resends disabled. The launch record also confirms progress
beyond the first layer with no printer error or HMS notice. Print options are Timelapse On, Bed Leveling On, Flow Dynamic
Calibration Auto and Nozzle Offset Calibration Auto. Starts and resumes across
H2C and Mark2 remain at least 180 seconds apart.

The [completion record](cradle-mark2-completion.json) confirms all 148 layers
finished at 100%, with no printer error or HMS notice. The cradle and reused
v2 receiver are ready for the bench trial after the cradle cools. Print telemetry
establishes completion. The physical record rates insertion "Very good";
retention and cycle testing are not reported. Completion does not establish
a clear bed for another job.

After cooling, remove the two supports outward into the open space beside the cradle,
retaining the hook bearing dimensions. Use the real PP0308E elbow and the
printed v2 receiver for the bench procedure: elbow seating without rocking,
hand insertion and release, hook retention and five cycles without cracking,
whitening or residual wing bend. Native slicing does not establish physical
retention or operating life.

To prepare a fresh native archive revision from this frozen v3 cradle:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/cradle-trial/h2c-print/v3/prepare_v3.py --revision 4
```

Each native revision has its own immutable `.cache/prints/` directory.
