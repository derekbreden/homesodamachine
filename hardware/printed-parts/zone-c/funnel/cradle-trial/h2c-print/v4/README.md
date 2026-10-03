# Funnel elbow-cradle v4 print

One frozen Funnel 2 receiver on Mark2 and one cradle on H2C, using the
[bench procedure](../../README.md). The slots have 0.25 mm clearance at each
wing end. The hook catch gap is 0.65 mm, and the counterbore ends on the slots.
The [physical record](../../physical-acceptance.json) rates v3 insertion
"Very good" with the printed v2 receiver; retention and cycle testing are not
reported. This v4 pair requires its own physical result.

| Part | Printer | Requested Z trim | Native estimate | State |
| --- | --- | --- | --- | --- |
| Test cradle v4 | H2C | +0.18 mm | 29 min 37 sec | Printer accepted; task 1303667680 |
| Test receiver v4 | Mark2 | +0.04 mm | 23 min 06 sec | Printer accepted; task 1303677943 |

The [allocation](allocation.json) records the verified user request for one
fresh part per printer and both printers idle with black PET-GF loaded. Each
uses external black PET-GF, labelled PET-CF, on the fixed left hardened
0.4 mm nozzle. The first layer is 0.20 mm with ordinary 0.24 mm layers above
it. Both meshes retain the production print pose, with the receiver on its
flat underside and the cradle on its bottom, pocket opening upward.
Textured-plate compensation emits `G29.1 Z0.16` on H2C and `G29.1 Z0.02`
on Mark2. Elephant-foot compensation is zero, with no brim.

[Cradle preflight](cradle-h2c-preflight.json) and
[receiver preflight](receiver-mark2-preflight.json) bind the frozen STL, native
input project, archive and G-code hashes. The saved geometry source snapshots
match commit `29808fba7`, verified in
[source-commit-verification.json](source-commit-verification.json).

| Frozen mesh | SHA-256 |
| --- | --- |
| Receiver | `e23e82074fa6aaa0f6d93aefb8a95147908e24418021b2501e32e24a08c2eaad` |
| Cradle | `bfa9f8c089fd4a2dc11e59949f00431c3273bc0e78e48981ca891b832def34f1` |

The [receiver support audit](receiver-mark2-support-audit.json) finds no
supports. The [cradle support audit](cradle-h2c-support-audit.json) includes
every support body and finds exactly two bed-rooted supports beneath the
outward hook undersides. There are no model roots, unlabelled bodies or
support paths in the upward-opening pocket. The interfaces finish at
Z 33.32 mm; the first printed hook layer is Z 34.04 mm, with a nominal
bottom at Z 33.80 mm and a 0.48 mm support gap. No blockers are needed.

The native [cradle preview](cradle-h2c-preview.png) and
[receiver preview](receiver-mark2-preview.png) retain the print orientation.
Minimum second-layer bead overlap is 75.7% on the cradle and 80.4% on the
receiver; outer-wall minima exceed 99.7%. Native ZIP integrity and G-code
MD5 checks pass. The frozen mesh bytes match before and after slicing.

The background Bambu Connect sender uses one Send per job, with automatic
resends disabled and a settled print dialog. Print options are Timelapse On,
Bed Leveling On, Flow Dynamic Calibration Auto and Nozzle Offset Calibration
Auto. The [cradle launch](cradle-h2c-launch.json) verifies task `1303667680`
with a successful printer reply, one Send and the reviewed archive hashes.
The [receiver launch](receiver-mark2-launch.json) verifies task `1303677943`
and its successful single Send. Mark2's Send gate is 181 seconds after H2C
task confirmation, exceeding the 180-second minimum. The
[launch relay](launch-relay.json) records submission of both task IDs to
Funnel 2. H2C starts first; every later start or resume across H2C and Mark2 stays
at least 180 seconds after the other printer's accepted start or resume.

After cooling, remove the two hook supports outward into open space,
retaining the hook bearing dimensions. Follow the bench procedure with the
real PP0308E elbow for seating, hand insertion and release, hook retention
and five cycles without cracking, whitening or residual wing bend. The
nominal 3.2% root strain is a CAD estimate; slicing does not establish
physical retention or operating life.

To prepare a fresh native archive revision from these frozen v4 meshes:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/cradle-trial/h2c-print/v4/prepare_v4.py --revision 5
```

Each native revision has its own immutable `.cache/prints/` directory.
