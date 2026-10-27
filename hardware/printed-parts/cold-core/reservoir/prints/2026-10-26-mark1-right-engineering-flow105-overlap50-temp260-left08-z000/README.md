# Mark1 right reservoir: 50% overlap

The **right reservoir and current matching lid** are running as **Mark1
task 1378532609**, accepted **2026-10-26T17:39:03.553720-05:00 / 2026-10-26T22:39:03.553720+00:00** through one Studio Send
and a `project_file SUCCESS` reply. [Launch](launch.json) ·
[Preflight](preflight.json) · [Startup](startup.json).

The [completed left article, task 1377101665](../2026-10-26-mark1-left-engineering-flow105-overlap50-temp260-left08-z000/physical-result/physical-result.json)
is reported holding water so far. This right pair retains every saved print
setting from that article: **50% overlap, flow 1.05, five Arachne walls,
255/260 °C nozzle, 70 °C Engineering Plate bed, 0.30/0.24 mm layers**,
100% solid zig-zag floor/cap fill, Tree(auto)/Default bed-only supports, no
brim, zero added/effective Z trim and ironing Off.
[Complete settings](settings.json) · [Source and geometry](preparation.json).

The right body uses current unchanged body geometry. Its matching current
lid carries the approved flush TPU tube-grip countersinks and air path;
its STEP hash matches `tube-grip-integration.json`. The lid prints exterior
face down; the body prints mouth up.

Use Mark1's fixed **left 0.8 mm Standard** nozzle and **A2 clear PETG** with
Auto Refill. A1 is empty; A2 reports 9%, with matching A3/A4 at 100% in the
initial preflight. A2 is the most depleted suitable spool. Remaining quantity
is not a launch condition. Send verifies **Mark1, Engineering, A2 PETG L,
Auto Refill, Timelapse On, Bed Leveling On, Flow Dynamics Auto and Nozzle
Offset Calibration Auto**.

Native slice: **5 h 41 min, 443.37 g, 833 layers**, with **50% overlap**
and both trim commands `G29.1 Z0`. The minimum full-bead bed-edge inset is
**80.519 mm**. [Native review](native-review.json) · [Export hashes](packaging.json).
Studio's global plate/grouping metadata and preset/resource identities differ
as listed in the review; the selected plate, emitted header and surface
detection are Engineering. Studio sends its current native slice; the retained
export hashes identify its reviewed copy, not byte identity of the upload
container.

Mark2 task **1378515009** is observed for at least **180 seconds**
before Send, exceeding the 180-second shared-circuit interval. Mark2 is not
controlled by this launch. Startup is **RUNNING**,
layer **0/833**,
with print error 0 and no HMS. Right-article adhesion, new-lid fit and water
holding remain unassessed.

Derek:

> All right, that reservoir print turned out well. It's holding water so far. So now that we've got that side, left I guess it was, with a 50% overlap, I'd like to get the other side, right side, with a 50% overlap, or whatever the other side is that you didn't just print. Mark one is available, plate is glued and ready.

## Printed lid opening

Derek's [lid photograph and slice diagnosis](physical-result/lid-port-supports.json)
show two liquid holes open while the air opening appears filled or backed.
The retained native slice places tree supports through the air port to reach
the closed baffle floor. Its model geometry has the updated countersinks;
the obstruction is generated support and the floor behind it.

The [replacement lid pair](../2026-10-26-mark1-lids-flush-grips-no-supports/README.md)
has a plain open air port, retains the TPU grommet and uses supports Off.
