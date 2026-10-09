# Complete industrial faucet at 0.08 mm

This Mark2 plate contains the industrial shell base, shared shell tip, industrial
cover, counter plate and accepted side-down lever replica. All five use 0.08 mm
normal layers above the usual 0.20 mm first bed layer. Their meshes and placements
match the [complete fine-shoulder plate](../2026-10-09-two-shoulders008-with-lever-mark2/README.md).

The complete base foot, CAD Z−0.01–14.01 mm, receives six walls and 100% zigzag
infill in one perimeter-spanning modifier. The base alone uses Arachne wall widths;
the other four objects retain Classic. Infill/wall overlap remains 15%. The native
paths have zero exterior starts/stops within 0.6 mm of all three original screw-host
box boundaries. The [printed-source comparison](../2026-10-09-all008-estimate-mark2/README.md)
records the repeated starts/stops associated with the photographed tracks.

[Insert deposition](insert-beads.json) reviews 190 native slabs per host. Minimum
nominal bead coverage within the host body/cap is 98.23%, 98.15% and 98.30%; the
installed Ø4.6 mm brass envelope retains at least 2.10 mm of connected outer
backing in sampled directions. These are commanded-path readings. Physical finish,
insert retention and load capacity are not established by this slice.

The reviewed native estimate is 13 h 54 min 59 s and 167.46 g at the saved profile
density. [Native checks](native-check.json) bind all five object identities and
layer heights, unchanged normal meshes, G-code checksums and 24.83 mm minimum
model/support/brim bed clearance. The [preview](native-preview.png) includes the
lever. The [deposition input](deposition-input.json) is the frozen report used by
the native slab review; its captured runtime paths describe that review invocation.

Black PET-GF maps to PET-CF external left slot 254 with the fixed hardened 0.4 mm
nozzle and Textured PEI. Mark2's requested +0.04 mm trim emits +0.02 mm. The
265/280°C nozzle and 80°C bed temperatures and accessible tree-support settings
are retained. Nozzle Clumping Detection by Probing remains disabled. Foreground
options are Timelapse On, Auto bed leveling On, Flow dynamic calibration Auto and
Nozzle Offset Calibration Auto.

[Preparation](preparation.json), [launch plan](launch-plan.json), [preflight](preflight.json)
and [launch](launch.json) bind the approved archive and printer observations.

Mark2 accepted task/job `1323545051` at 2026-10-09 10:40:27 CDT
(15:40:27 UTC) through one foreground Send. A fresh post-start
reading reports the exact archive RUNNING at layer 0/2749, print error 0 and no HMS
faults. Native completion is forecast near 2026-10-10 00:35 CDT. Timelapse On was
verified in the Send dialog; captured frames have not been checked.
