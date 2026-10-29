# Single TPU 85A elbow — 13 mm/s outer wall

**Not selected for printing; not submitted.** The user declines a speed
midpoint because the observed difference between the two printed trials may
be nonexistent. The photos do not establish a curl-to-sag crossover.

One compact elbow, Mark1 right fixed
0.6 mm nozzle, TPU 85A, Engineering Plate and zero user Z trim. Native estimate:
**64 minutes / 4.30 g**.

The target is an intact underside without drooping beads, upward curl or
nozzle pickup. The [10 mm/s physical record](../2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json)
contains the user's reports, three wider views and six close-ups. Raised,
distorted rim material and ragged underside strands are visible. A dependable
improvement from the speed change is unestablished.

The [complete-perimeter comparison](outer-speed-comparison.json) shows
**14.95–19.40 mm/s at the actual left lip on layers 26–33**, despite the
13 mm/s ordinary outer-wall setting. Separate overhang speeds replace that
value. This archive establishes neither a 13 mm/s lip nor an actual speed
midpoint. Nominal whole-layer motion remains near 20 seconds.

The [native readback](native-readback.json) confirms that the outer-wall
setting and recipe label are the only differences from the original
Engineering Plate recipe. Native meshes and pose match. The candidate retains
225°C nozzle, 35°C bed, 100% part and auxiliary fan commands from layer 2,
0.20 mm first / 0.12 mm normal layers, 0.62 mm line widths and `G29.1 Z0`.
The selected geometry has nominal 45° underside regions.

The emitted-speed comparison describes the unsent slice. The observations do
not establish that sagging and upward curl vary monotonically or balance at
this value. Printed quality, socket fit and sealing remain unqualified.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-outer13-engineering-right06-z000-mark1.3mf)
- [Native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-outer13-engineering-z000-mark1/2026-10-13-compact-single-elbow-tpu85a-outer13-engineering-right06-z000-mark1.gcode.3mf)
- [Manual preparation script](prepare_mark1.py)

The preparation script does not connect to a printer or submit a job.
