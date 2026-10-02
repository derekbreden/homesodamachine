# Funnel elbow-cradle v1 print

The [v2 print records](v2/README.md) describe the shorter wings and wider cradle.

One frozen Funnel 2 test receiver and one test cradle, retaining their production
print poses and the [trial geometry and bench procedure](../README.md). Both use
black PET-GF on the fixed left hardened 0.4 mm nozzle, with a 0.20 mm first layer
and ordinary 0.24 mm layers. The user's request to start the pair confirmed both
beds clear.

| Part | Printer | Task | Requested Z trim | Native estimate | Printer state |
| --- | --- | --- | --- | --- | --- |
| Test receiver | Mark2 | 1303210057 | +0.04 mm | 22 min 56 sec | Finished, 2026-10-02 21:32:31 UTC |
| Test cradle | H2C | 1303138499 | +0.18 mm | 27 min 38 sec | Finished, 2026-10-02 21:02:54 UTC |

Textured-plate compensation emits `G29.1 Z0.02` on Mark2 and `G29.1 Z0.16`
on H2C. The [receiver launch](receiver-mark2-launch.json) and
[cradle launch](cradle-h2c-launch.json) bind the archive and G-code hashes to
the new printer task IDs. Mark2 returned `project_file` SUCCESS with error code
zero. Its accepted import is byte-identical to the reviewed archive and uses a
20-second settled print dialog. The
[explicitly rejected submission](receiver-mark2-rejected-send.json) created no
new task. Automatic resends are disabled.

The [receiver completion](receiver-mark2-completion.json) reports all 50 layers
finished, and the [cradle completion](cradle-h2c-completion.json) reports all 148.
Both printers report 100%, no printer error and no HMS notice. The pair is ready
for removal after cooling and the bench procedure below. The
[physical record](../physical-acceptance.json) reports easy v1 insertion.
Retention and cycle testing are not reported; the insertion result applies to
these frozen v1 meshes.

The shared PET-GF automatic tree profile puts exactly two supports under the
flat outward hooks. Both start on the bed and stand in open air outside the
cradle's sides. Their interfaces finish at Z 33.08 mm; the first printed hook
layer is Z 33.80 mm with a nominal bottom at Z 33.56 mm, leaving 0.48 mm between
support and bearing. The receiver and upward-opening pocket have no support
paths. No blockers or geometry amendments are needed for this slice.

[receiver-mark2-support-audit.json](receiver-mark2-support-audit.json) and
[cradle-h2c-support-audit.json](cradle-h2c-support-audit.json) retain the complete
support topology, including bodies without interface labels. Their
[receiver preflight](receiver-mark2-preflight.json) and
[cradle preflight](cradle-h2c-preflight.json) bind the frozen meshes, input projects
and native G-code archives, including nozzle mapping and first/second-layer bead
overlap. Every second-layer model bead has more than half its area over the
first-layer model footprint; outer-wall minima are 99.7% on the receiver and
99.9% on the cradle. Elephant-foot compensation is zero and there is no brim.

[receiver preparation](receiver-mark2-preparation.json) and
[cradle preparation](cradle-h2c-preparation.json) record the saved profile, source
snapshot and bed positions. The production generators belong to the Funnel 2
session; these print records describe the frozen trial meshes. Every source in
that snapshot matches export commit `f8f59be7e`, and both STL hashes match the
exporting session's frozen-mesh receipt. The
[combined-plate preflight](preflight.json), [preparation](preparation.json) and
[support audit](support-audit.json) are an unsent profile reference.

The [allocation and queue](../../../../enclosure/enclosure/contact-pair-coupon/h2c-print/queue.json)
record one part per printer. The background Bambu Connect sender uses the
external PET-CF-labelled black PET-GF spool. Print options are Timelapse On, Bed
Leveling On, Flow Dynamic Calibration Auto and Nozzle Offset Calibration Auto.
The receiver's send gate was 1,760 seconds after confirmation of the cradle's new
task, exceeding the shared-circuit minimum of 180 seconds. A subsequent start
or resume must retain that minimum interval. Printer completion alone does not
clear a bed for a following job.

To prepare and review a fresh revision:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/cradle-trial/h2c-print/prepare_split.py --revision 2
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
