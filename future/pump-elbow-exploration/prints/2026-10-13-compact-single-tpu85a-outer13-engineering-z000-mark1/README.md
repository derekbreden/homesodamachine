# Single TPU 85A elbow — 13 mm/s outer wall

**Prepared offline; not submitted.** One compact elbow, Mark1 right fixed
0.6 mm nozzle, TPU 85A, Engineering Plate and zero user Z trim. Native estimate:
**64 minutes / 4.30 g**.

The target is an intact underside without drooping beads, upward curl or
nozzle pickup. The [10 mm/s physical record](../2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json)
contains the user's sagging report and three photos. Drooping strands are
visible along the undersides; the raised or built-up right rim leaves the
presence of curl unresolved.

The [native comparison](outer-speed-comparison.json) confirms **13 mm/s** at
the left lip on layers 26–33, between 10 mm/s and the original emitted
15–17 mm/s around curl onset. The original requested setting is 25 mm/s;
its cooling slowdown makes the emitted speed lower in that region. The
13 mm/s choice is an approximate midpoint there, not across every layer.
Nominal whole-layer motion remains near 20 seconds.

The [native readback](native-readback.json) confirms that the outer-wall
setting and recipe label are the only differences from the original
Engineering Plate recipe. Native meshes and pose match. The candidate retains
225°C nozzle, 35°C bed, 100% part and auxiliary fan commands from layer 2,
0.20 mm first / 0.12 mm normal layers, 0.62 mm line widths and `G29.1 Z0`.
The selected geometry has nominal 45° underside regions.

An intermediate speed tests the effect of outer-wall deposition speed. The
observations do not establish that sagging and upward curl vary monotonically
or balance at this value. Printed quality, socket fit and sealing remain
unqualified.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-outer13-engineering-right06-z000-mark1.3mf)
- [Native archive](2026-10-13-compact-single-elbow-tpu85a-outer13-engineering-right06-z000-mark1.gcode.3mf)
- [Manual preparation script](prepare_mark1.py)

The preparation script does not connect to a printer or submit a job.
