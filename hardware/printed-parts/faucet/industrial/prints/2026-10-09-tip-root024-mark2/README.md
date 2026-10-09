# Complete industrial faucet with a thicker tip starting band

This Mark2 plate contains the industrial shell base, shared shell tip, industrial
display cover, above-counter plate and accepted side-down lever replica. The
normal process settings match the [complete solid-foot plate](../2026-10-09-all008-solid-foot-mark2/README.md)
byte-for-byte. The model meshes, placements, 0.20 mm first bed layer, temperatures,
tree supports, speeds, acceleration, retract wiping and Auto Lift are retained.

The sole process change is one layer-height range on the shell tip: 0.24 mm through
print Z2.12 mm, then 0.08 mm above. The emitted sequence is a 0.20 mm first bed
layer, eight 0.24 mm model layers ending at Z2.12, then 0.08 mm model layers starting
at Z2.20. The other four models use 0.08 mm above their first bed layers.

[The operator's observation](../2026-10-09-all008-tip-grid-no-wipe-mark2/physical-result/physical-result.json)
identifies the model's narrow starting edge as the lifting material in the last
article. The [native first/second-layer comparison](tip-root-comparison.png) shows
1.339 mm² of model bead footprint for the all-0.08 tip start and 2.636 mm² for this
starting band. The following 0.24 mm model layer has 97.54% nominal footprint
overlap with the first. At the return to 0.08 mm, Z2.20 has 89.44% overlap with the
preceding model layer. These are ideal commanded bead envelopes, not measured
bonding. The [root review](tip-root-review.json) lists every sampled early model
layer, including the expanding edges. Support paths are excluded from this reading.

The base retains Arachne and one continuous foot modifier with six walls, 100%
zigzag infill and 15% infill/wall overlap. The native outer walls retain zero
starts/stops near all three original screw-host boundaries. Normal body geometry
and reinforcement are preserved. All complete model/support/brim beads retain a
24.83 mm minimum bed margin.

Black PET-GF maps to PET-CF/GFT01 external left slot254, fixed hardened standard-flow
0.4 mm nozzle and Textured PEI. Mark2's +0.04 mm requested Z trim emits +0.02 mm.
Nozzle temperature is 265°C first layer and 280°C above; bed temperature is 80°C.
Nozzle Clumping Detection by Probing remains disabled. Foreground options are
Timelapse On, Auto bed leveling On, Flow dynamic calibration Auto and Nozzle Offset
Calibration Auto. There is no programmed insertion pause or scheduled monitor.

The native estimate is **12 h 55 min 9 s**, using 161.24 g at the saved profile
density. [Native checks](native-check.json), [native preview](native-preview.png),
[preparation](preparation.json), [launch plan](launch-plan.json),
[preflight](preflight.json) and [launch receipt](launch.json) bind the complete
five-part plate and the single local layer-height change. The tip's early edge
bonding, support cleanup and complete faucet finish require physical inspection.

Mark2 accepted task/job `1324374637` at 2026-10-09 15:57:34 CDT
(20:57:34 UTC). There is one imported archive and one Send click.
The foreground launcher exited before Send because its name filter did not include
the dialog's selected Mark1. Native UI selected Mark2 and continued the existing
import, with left external PET-CF and the standing print options verified. Fresh
readings of both printers identify the new faucet archive in RUNNING state,
print error0 and no HMS faults. First-layer adhesion is not visually observed.
The native completion forecast is 2026-10-10 04:52:43 CDT.
