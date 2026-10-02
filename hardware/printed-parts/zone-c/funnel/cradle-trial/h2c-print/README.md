# H2C elbow-cradle trial

One test receiver and one test cradle, retaining their production print poses and
the [trial geometry and bench procedure](../README.md). The native slice estimates
45 minutes 18 seconds. It uses black PET-GF on H2C's fixed left hardened 0.4 mm
nozzle, the requested **+0.18 mm Z trim**, a 0.20 mm first layer and ordinary
0.24 mm layers. Textured-plate compensation emits `G29.1 Z0.16`.

The shared PET-GF automatic tree profile puts exactly two supports under the
flat outward hooks. Both start on the bed and stand in open air outside the
cradle's sides. Their interfaces finish at Z 33.08 mm; the first printed hook
layer is Z 33.80 mm with a nominal bottom at Z 33.56 mm, leaving 0.48 mm between
support and bearing. The receiver and upward-opening pocket have no support
paths. No blockers or geometry amendments are needed for this slice.

[support-audit.json](support-audit.json) retains the complete support topology,
including bodies without interface labels. [preflight.json](preflight.json)
binds the frozen meshes, input project and native G-code archive, and records
both nozzle mapping and first/second-layer bead overlap. Every second-layer
model bead has more than half its area over the first-layer model footprint;
the outer-wall minima are 99.7% on the receiver and 99.9% on the cradle.
Elephant-foot compensation is zero and there is no brim.

[preparation.json](preparation.json) records the saved profile, source snapshot
and separated bed positions. The production generators belong to the Funnel 2
session; these print records describe the frozen trial meshes.
Every source in that snapshot matches the export commit `f8f59be7e`, and both
STL hashes match the exporting session's frozen-mesh receipt.

This job follows the contact-seat coupons in the H2C queue. It has not been
submitted. Submission requires the preceding job to finish, the printed pieces
and supports to be removed, and a current clear-bed confirmation. Use the
background Bambu Connect sender with the external PET-CF-labelled black PET-GF
spool. Print options are Timelapse On, Bed Leveling On, Flow Dynamic Calibration
Auto and Nozzle Offset Calibration Auto. Keep at least three minutes after
either printer accepts or resumes a job before starting the other.

To prepare and review a fresh revision:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/cradle-trial/h2c-print/prepare.py --revision 2
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/cradle-trial/h2c-print/verify.py --revision 2
```

Each revision has a separate immutable directory in `.cache/prints/`.

Remove both supports outward into the open space beside the cradle before
installing the elbow. Inspect the hook undersides and retain the as-printed
bearing dimensions. The bench trial checks hand insertion and removal, elastic
return, elbow seating and hand retention over five insert/remove cycles, using
the real scanned PP0308E elbow. Record any retained support, bearing roughness,
cracking, whitening or residual wing bend with the result.

The accepted [display snap](../../../../enclosure/display-cover/physical-acceptance.json)
provides a design precedent. This differently proportioned cradle requires its
own physical result; native support counts and the nominal bend estimate do not
establish retention force or operating life.
