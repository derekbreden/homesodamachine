# Cylindrical-base pad — Mark1 task 1334447551

This job prints a TPU hand pad bearing on donor axial coordinates 0–12 mm
of the cylindrical metal base. The broad hand face is 2 mm above the
PET-GF walls; the 12.8 mm compression tongue fits the 11.8 mm shank canyon.
Its [dimensions](dimensions.json) and
[printed STL](cylindrical-body-pad-print.stl) identify that contact shape.

The [launch record](launch.json) identifies the archive accepted by Mark1
on October 12 at 9:20 pm CDT. Derek's instruction “Let it finish” authorizes
this job to continue. This record establishes submission and observed
startup, with no physical fit or hand-pressure result.

- [Editable native project](donor-hold-down-tpu85a-right06-z018-mark1.3mf)
- [Exact launched slice](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/donor-hold-down/prints/2026-10-12-mark1/donor-hold-down-tpu85a-right06-z018-mark1.gcode.3mf)
- [Project settings](donor-hold-down-tpu85a-right06-z018-mark1.print.json)
- [Native slice review](donor-hold-down-tpu85a-right06-z018-mark1.readiness.json)
- [Observed startup](startup.json)

The native slice uses black TPU 85A through Mark1's right fixed 0.6 mm
nozzle and external spool 255, textured PEI, 0.18 mm layers, a 0.30 mm
first layer and 100% zig-zag infill. Standard +0.18 mm user Z trim emits
`G29.1 Z0.16`. The slice has 138 layers, no supports, and estimates
12.8 g and 1 hour 36 minutes.

The [half-body cover](../../README.md) has its own geometry,
project and slice.
