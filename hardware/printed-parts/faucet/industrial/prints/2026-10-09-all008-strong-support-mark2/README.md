# Complete industrial faucet with strong tree supports

This Mark2 plate contains the shell base, shell tip, display cover, counter plate
and accepted side-down lever replica. All five objects use 0.08 mm normal layers
above a 0.20 mm first bed layer. The normal meshes, orientations and placements
match the [frozen complete faucet](../2026-10-09-all008-solid-foot-mark2/README.md).

The [failed article's evidence](../2026-10-09-all008-solid-foot-mark2/physical-result/physical-result.json)
locates the disrupted extrusion near the tip. The timelapse shows loose material
while the tip ring and larger objects remain at their bed locations. It does not
capture the instant of impact or establish what initiated the displacement.

| Process setting | This plate |
| --- | --- |
| Model layers / first bed layer | 0.08 / 0.20 mm |
| Support type / style | Automatic tree / Strong |
| Tree support wall count | Two |
| Branch diameter | 3 mm |
| Support body / interface speed | 60 / 40 mm/s |
| Independent support height | Enabled; native tip body includes 0.2764 mm slabs |
| Support top / bottom Z separation | 0.45 / 0.30 mm |
| Support XY separation | 0.40 mm |
| PET-GF nozzle temperatures | 265°C first layer, 280°C above |
| Textured PEI bed | 80°C |
| Mark2 Z trim | +0.04 mm requested, +0.02 mm emitted |
| Probing clump detection | Disabled |

Strong trees, forced two-wall branches and reduced support speeds target support
stability. The [native tip sections](tip-support-comparison.png) show the compact
supporting branch and its thicker deposited slabs. Fine contact areas still use
thin layers; independent support height does not make every support slab coarse.
[Native support readings](support-layer-review.json) retain the actual heights.
These are overrides on this prepared plate; the shared PET-GF profile is unchanged.
Bambu's [support-style definitions](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp)
describe Strong as a larger support structure. Stability and cleanup of this
specific article require the physical print.

The base's continuous foot modifier retains six walls and 100% zigzag infill, with
Arachne widths on the base alone and 15% infill/wall overlap. The other four
objects use Classic. [Exterior paths](outer-wall-review.json) have zero starts or
stops at all three original screw-host boundaries. [Insert deposition](insert-beads.json)
passes 190 model slabs per host: minimum nominal body/cap coverage is 98.23%,
98.15% and 98.30%, with at least 2.10 mm connected outer backing around the
installed Ø4.6 mm brass envelope. These readings establish commanded material,
not measured insert retention or load capacity.

[Native checks](native-check.json) bind all five identities, unchanged normal
geometry, fine model layer heights, disabled probing commands and a 25.16 mm
minimum complete model/support/brim bed margin. The native reader retains modal
feature labels across object and layer changes, so independently spaced support
planes are excluded from model-stock review. The [deposition input](deposition-input.json)
is the exact captured input to that review; its runtime paths describe the
offline invocation.

The native estimate is 12 h 17 min 27 s and 161.98 g at the saved profile density.
[Preview](native-preview.png), [preparation](preparation.json), [launch plan](launch-plan.json),
[preflight](preflight.json) and [launch receipt](launch.json) describe this complete
five-part plate. Foreground Send options are Timelapse On, Auto bed leveling On,
Flow dynamic calibration Auto and Nozzle Offset Calibration Auto.

After cooling, remove the external tree scaffolds through the parts' open sides.
The retained separation gaps provide the cleanup allowance; the stronger two-wall
supports may require more removal effort. Inspect the tip-side support result,
the three screw-side exterior surfaces and support-contact finish before recording
physical acceptance.

Mark2 accepted task/job `1323967341` at 2026-10-09 13:13:31 CDT
(18:13:31 UTC) through one foreground Send. The matching archive reports the
canceled job idle, with print error0 and no HMS faults, in the 19:32 UTC reading.
Derek [reports displaced material at the same tip-side support](physical-result/physical-result.json)
and confirms the job stopped and bed cleared for a retry. The disruption's
initiating contact and height, recovery and complete article outcome are unobserved. The native paths
contain same-height support wipes before the 0.4 mm lift, including the retained
fine support regions. A curled strand catching during that motion is a working
hypothesis. The [tip grid and no-wipe plate](../2026-10-09-all008-tip-grid-no-wipe-mark2/README.md)
targets this mechanism. Timelapse On was verified in the Send dialog.
