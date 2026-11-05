# Machine display cover reach trials

**Shake retention failed:** the +0.5 mm hook-reach cover with 0.9 mm skirt inset per
side pops out intact from the printed receiver. The [physical reading](https://github.com/derekbreden/homesodamachine/blob/archive-finished-trials/hardware/printed-parts/enclosure/display-cover/reach-trial/physical-acceptance.json)
binds this observation to Mark2 task 1289413482 and the exact printed geometry.
The broad-leaf pairing is recorded in the [retention trial](../retention-trial/README.md).
The [production cover](../README.md) uses the accepted horizontal wings.

Two full covers fit the printed [receiver trial](../receiver-trial/README.md).
Both have straight skirts inset 0.9 mm per side. Their hooks overlap the catches
by 1.3 mm when centered and at least 1.0 mm at full lateral float. Clearance
outside a straight leaf at the ledge is 0.5 mm centered and at least 0.2 mm at
full lateral float.

| Cover | Printer | Extra hook reach | Nominal clearance below ledge |
| --- | --- | --- | --- |
| display-cover-reach-05 | Mark2 | 0.5 mm | 0.98 mm |
| display-cover-reach-10 | H2C | 1.0 mm | 1.48 mm |

The bezel, window, skirt thickness, lip projection and insertion noses retain
their dimensions. Print face down. Removable supports carry the square hook
bearing faces. The nominal bearing clearance permits the same amount of outward
travel before the hooks bear.

After support removal, the insertion test reads whether each hook clears its
ledge, each leaf returns outward, and the bezel relaxes flat.

The [authored source snapshot](https://github.com/derekbreden/homesodamachine/blob/abcc5fea68ac87cf460142323977bbb66d5fed1b/hardware/printed-parts/enclosure/display-cover/reach-trial/cover_reach_trial.py) is retained in Git at `abcc5fea68ac87cf460142323977bbb66d5fed1b`. This directory retains its geometry and evidence.
[The geometry reading](geometry-check.json) checks the unchanged bezel, seated
clearance and both catches against the printed receiver. The +0.5 mm cover fails
the physical shake test without broken plastic. Retention force remains unmeasured;
no physical assessment is recorded for the +1.0 mm cover.

Print records: [Mark2](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-27-display-cover-reach-mark2-v11/README.md), [H2C](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-27-display-cover-reach-h2c-v1/README.md).
