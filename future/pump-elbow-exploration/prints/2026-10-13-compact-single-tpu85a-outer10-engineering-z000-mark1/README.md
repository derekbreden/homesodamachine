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

The [emitted-speed comparison](outer-speed-comparison.json) confirms 10 mm/s
at the left lip on layers 26–33, where the baseline emits approximately
15–18 mm/s. Nominal whole-layer time stays near 20 seconds because the cooling
slowdown redistributes other path speeds. Slower outer-wall deposition is the
trial variable; increased time between layers is not established.

The target is an intact underside without upward curl, nozzle pickup or a
carried glob. The baseline's reported fan reduction worsened curl; full cooling
is retained. Slower deposition may reduce disturbance of the soft edge, but
longer local exposure to the hot nozzle is a competing effect. Physical print
quality, socket fit and sealing remain unqualified.

The [physical record](physical-result.json) contains the user-reported sagging
along 45° undersides and three supplied photos. The right rim also appears
raised or built up; absence of curl is not established. The
[13 mm/s candidate](../2026-10-13-compact-single-tpu85a-outer13-engineering-z000-mark1/README.md)
is prepared offline for an intermediate deposition-speed trial.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-outer10-engineering-right06-z000-mark1.3mf)
- [Native archive](2026-10-13-compact-single-elbow-tpu85a-outer10-engineering-right06-z000-mark1.gcode.3mf)
- [Manual preparation script](prepare_mark1.py)

The script slices the saved baseline geometry offline. It does not submit a job
or change a global printer preset.
