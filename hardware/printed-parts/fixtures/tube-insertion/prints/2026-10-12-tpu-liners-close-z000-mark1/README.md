# Compact TPU grip-liner retry — Mark1

This plate contains two preformed TPU 85A grip liners F for the
[tube insertion tool](../../README.md). Each liner prints upright on its
8 × 20 mm end, with the gripping channel vertical through 28 mm of height.
The model centres are X 172.5 and 182.5 mm, Y 160 mm, giving a **2 mm edge
gap**. The native full-bead envelopes retain at least **1.789 mm** between
objects and **143.39 mm** of bed-edge clearance.

The [native project](2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.3mf)
and [reviewed G-code archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-tpu-liners-close-z000-mark1/2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.gcode.3mf)
use Mark1's **right fixed 0.6 mm hotend**, black TPU 85A on external spool
255, and Textured PEI. The requested user Z trim is **0.00 mm** for this
print. Native startup emits `G29.1 Z0` and then `G29.1 Z-0.02`, retaining
the stock textured-plate compensation. Mark1's standard +0.18 mm user trim
remains its normal setting.

The TPU recipe uses 225 °C nozzle, 35 °C bed, 2.2 mm³/s maximum flow,
two Arachne walls, 100% zigzag infill, three top/bottom layers, a 0.30 mm
first layer and 0.18 mm normal layers. Supports are disabled and automatic
brim is enabled; the native slice generates neither support nor brim.
The [preparation record](2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.print.json)
and [native review](2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.readiness.json)
bind the mesh, recipe, placement and archive hashes. The
[first/second-layer review](layer-review.json) checks bead contact and both
object envelopes. Normalized extrusion amounts, widths, feature order and
arc offsets match the source slice; one translated arc endpoint has a
0.001 mm rounding difference. These readings do not establish physical
bed adhesion. [prepare_mark1.py](prepare_mark1.py) reproduces the native
project and slice using an empty named scratch directory; it submits no print.

Mark1 accepted task/job **1333964128**, first observed RUNNING at
**5:28:44 pm CDT on October 12, 2026**, following one Send. Bambu Connect
shows the exact new archive, 0/155 layers and the selected right hotend.
Telemetry reports no error or HMS. Timelapse and leveling are On; flow and
nozzle-offset calibration are Auto. The native estimate is **1 h 05 min /
8.8 g**, plus additional startup calibration and any pauses.

The [preflight](preflight.json), [launch receipt](launch.json),
[post-send readings](after-send.json) and [startup reading](startup.json)
record the mapping, source/submitted
G-code hashes and circuit spacing. Printer 2 has the accepted job and time.
Mark2's last accepted start remains 19:42:29 UTC; the earliest other-printer
start or resume after this retry is **22:31:44 UTC / 5:31:44 pm CDT**.

This is a retry of the [fallen-liner job](../2026-10-12-tpu-liners-mark1/failure.json).
The physical result of this retry is pending. Cleanup, fit, grip performance
and printed strength remain unassessed.
