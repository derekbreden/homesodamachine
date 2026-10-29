# Single TPU 85A elbow — 10 mm/s outer wall

Mark1 accepted task **1337583437** on **2026-10-13 at 21:45:04 CDT**.
The [launch receipt](launch.json) binds the submitted archive and G-code.

One compact V elbow on Mark1's right fixed 0.6 mm nozzle, with TPU 85A,
a glued Engineering Plate and zero user Z trim. The native estimate is
67 minutes / 4.30 g.

The outer-wall setting is 10 mm/s. The [native readback](native-readback.json)
confirms that this setting and the recipe label are the only differences from
the identified [Engineering Plate trial](../2026-10-13-compact-single-tpu85a-engineering-z000-mark1/README.md).
The complete native mesh and pose match. The recipe retains 225°C nozzle,
35°C bed, 0.20 mm first / 0.12 mm normal layers, 0.62 mm line widths, inner/outer
wall order, 100% part and auxiliary fans from layer 2, and `G29.1 Z0`.

The [complete-perimeter speed comparison](outer-speed-comparison.json)
shows **15.83–21.80 mm/s at the actual left lip on layers 26–33**, versus
14.60–17.60 mm/s in the original archive. Separate process overhang speeds
replace the normal outer-wall value. This archive does not test a 10 mm/s lip.
Nominal whole-layer motion stays near 20 seconds. The manual review retains
feed-only speed changes within each continuous perimeter and records the
actual lip commands and their modal feeds.

The target is an intact underside without upward curl, nozzle pickup or a
carried glob. The baseline's reported fan reduction worsened curl; full cooling
is retained. Slower deposition may reduce disturbance of the soft edge, but
longer local exposure to the hot nozzle is a competing effect. Printed surface
quality and sealing remain unqualified.

**Reported fit baseline:** Derek reports that this rough-edged article fits
beautifully, with firm friction and elastic stretch. Insertion takes force
but is manageable without a jig. The [physical record](physical-result.json)
binds the exact report to this print and its mesh. The cuff bores, insertion
depths, wall thickness and entries supply the fit baseline for surface work.
Fit after improving the 45° surfaces requires its own result.

The [physical record](physical-result.json) contains three wider views and six
close-ups, including the user's reassessment of apparent sagging. Raised,
distorted rim material and ragged underside strands are visible. A curl-to-sag
crossover or dependable benefit from the speed change is unestablished.
The user declines the
[13 mm/s midpoint](../2026-10-13-compact-single-tpu85a-outer13-engineering-z000-mark1/README.md);
it is not selected or submitted. The
[215°C normal-layer candidate](../2026-10-13-compact-single-tpu85a-t215-engineering-z000-mark1/README.md)
retains this trial's geometry, requested outer-wall speed and 225°C first layer.
The [corrected overhang-speed candidate](../2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1/README.md)
retains this article's 225°C recipe and has verified 10 mm/s lip commands.
It is prepared offline and not submitted.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-outer10-engineering-right06-z000-mark1.3mf)
- [Native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/2026-10-13-compact-single-elbow-tpu85a-outer10-engineering-right06-z000-mark1.gcode.3mf)
- [Manual preparation script](prepare_mark1.py)

The script slices the saved baseline geometry offline. It does not submit a job
or change a global printer preset.
