# Mark1 reservoir: 50% overlap

The **left reservoir and matching lid** are running as **Mark1 task
1377101665**, freshly verified **09:18:30 CDT / 14:18:30 UTC October 26**
after a single Studio Send and a `project_file SUCCESS` reply. This is the
first retained active-task observation, not an exact acknowledgment timestamp.
[Launch](launch.json) · [Preflight](preflight.json) · [Startup](startup.json).

Use the glued **Engineering Plate**, fixed **left 0.8 mm Standard** nozzle and
**A2 clear PETG**, with Auto Refill visible. A1 is empty; A2 reports 58% and
matching A3/A4 report 100% at final preflight. A2 is the most depleted suitable
spool. Remaining quantity is not a launch condition.

The recipe uses **50% Infill/Wall overlap**, **flow 1.05**, five Arachne walls,
**255/260 °C** first/subsequent nozzle temperatures and a **70 °C** bed.
Retain 0.30/0.24 mm layers, 0.8 mm nominal widths, 100% solid zig-zag floor/cap
fill, Tree(auto)/Default bed-only supports, no brim, zero added/effective Z
trim and ironing Off. Both native trim commands are `G29.1 Z0`.
[Complete settings](settings.json) · [Preparation and geometry](preparation.json).

The saved body/lid pair is the source geometry for this sealing trial. The
body is unchanged; the included lid has the earlier port geometry and does
not include the current flush TPU-grip countersinks.

Studio's native slice estimates **5 h 42 min 25 s, 444.89 g, 833 layers**.
It emits 50% overlap, the Engineering Plate detection commands, left-nozzle
selection and zero Z compensation. The minimum full-bead bed-edge inset is
**80.519 mm**; body/cap bead envelopes are **10.042 mm** apart. Preset/resource
labels and global plate/grouping metadata differences are retained in the
[native review](native-review.json); the selected plate and emitted commands
are Engineering. [Exported slice and unchanged G-code hashes](packaging.json).

Send verifies **Mark1, Engineering, A2 PETG L, Auto Refill, Timelapse On,
Bed Leveling On, Flow Dynamics Auto and Nozzle Offset Calibration Auto**.
Studio sends its current reviewed native slice. The retained export hashes
identify that slice's exported copy; upload-container byte identity is not
claimed. The printer reports the source model title
`Left_reservoir_and_cap_-_PETG_0.24_mm`, distinct from the send-dialog title.
The new task ID and successful reply identify the launch.

The same Mark2 task **1375153599** is observed before Send for at least
**467 seconds**, exceeding the 180-second shared-circuit interval. Mark2
is not controlled by this launch. Fresh startup at **14:19:59 UTC** is
**RUNNING, layer 0/833, print error 0 and no HMS**. Preparation is active;
model deposition, adhesion and water holding remain unassessed. A2 is the
selected starting slot; loaded-tray state at deposition is unobserved.

Derek:

> Please make that 50% instead, thanks.

> Mark 1 is clear and ready for your next print. Got the bed, the industrial plate glued and ready to go.
