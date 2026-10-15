# Mark1 faucet-rim comparison

Mark1 accepted **job 1340913124 at 23:53:32 CDT on 2026-10-14** and reported
**RUNNING, 0/70 layers, no errors**. Bambu Connect displayed the correct file
and homing sequence. The [launch receipt](launch.json) preserves acceptance,
the subsequent 70-layer reading, print options and file hashes. Physical finish
and support-removal results are pending.

| Facing Mark1 | Condition |
| --- | --- |
| A, left | 34 annulus-scoped Full-mode fins plus three low rear walls; Tree(auto)/Default elsewhere |
| B, right | Production Tree(auto)/Default, including its automatic normal sections |

Both specimens keep the accepted **−15° pose**, original model geometry and
bed contact, 0.20 mm first layer and 0.24 mm following layers. Both receive
native **125% bridge flow, 70% part fan after three fan-off layers, 15 mm/s
Bridge moves and 10 mm/s fully overhung walls**. The [comparison description](../README.md)
records the local support scope, customer outcome, path measurements and
physical assessment procedure. No production profile is promoted.

The [editable project](2026-10-14-faucet-foot-full-annulus-fins-vs-tree-current15-bridge125-fan70-z018-mark1.3mf)
copies the reviewed Mark2 comparison's complete geometry and placement. Its
printer-specific settings come from the accepted Mark1 tip project's saved
start code, preset identity and black filament colour. Mark1 uses the fixed left
hardened standard-flow **0.4 mm nozzle**, **external PET-GF spool 254** (reported
PET-CF, `000000FF`), Textured PEI, 265°C first-layer/280°C normal nozzle and
80°C bed. The **+0.18 mm requested trim emits `G29.1 Z0.16`** after the native
trim-clear command. Mapping and loaded material were verified before Send.

The [native review](review.json), [selected-path review](rim-path-review.json)
and [whole-annulus review](annulus-review.json) verify the Mark1 copy itself.
The [packaging record](packaging.json) binds the submitted print-only archive
to unedited native G-code. The native estimate is **2 h 7 min 49 s**, **48.26 g**,
**70 layers**, with **89.959 mm** minimum full-bead bed-edge clearance.

Timelapse and bed leveling are On; Flow Dynamics and Nozzle Offset Calibration
are Auto. One Send was accepted with `project_file SUCCESS`. The foreground
sender stopped at the file picker before Send; the computer-use tool completed
the import, verified the Mark1 dialog and submitted the reviewed file.

The [prelaunch record](prelaunch.json) includes Derek's clear-bed instruction
and both printer states. Mark2's stock-fin job 1340828943 remained running.
The Mark1 acceptance is **3,466.814 seconds** after Mark2's recorded acceptance,
exceeding the 180-second minimum. The earliest subsequent other-printer start
or resume is **04:56:32 UTC on 2026-10-15**. No further print is submitted here.
