# Single full-base TPU elbow — Mark1

Mark1 accepted task **1337352366** on **2026-10-13 at 19:48:59 CDT**.
The [launch receipt](launch.json) binds the submitted archive and G-code.
The plate contains exactly **one elbow**. The printer is stopped and this
geometry is rejected; the [result record](physical-result.json) binds that
scope. Physical printing success, fit and sealing remain unmeasured.

Convex exterior stock surrounds the fitting, with annular air gaps beneath
the cuffs. The integral base contacts **447.716 mm²**, measures approximately
34.14 × 14.82 mm, and supports a 22.22 mm tall body. The interior socket and
flow bores retain the 11 mm barb / 15 mm tube insertion depths. Mouth-open,
1.2 mm radial channels leave room around both complete 9 mm clamp-band seats.
The added stock is permanent part material, with 100% infill.

The native archive verifies one body, one normal volume, one object and one
build instance. Its estimate is **81 minutes / 7.80 g**, 184 layers. The saved
Mark1 recipe uses loaded black TPU 85A, the right fixed 0.6 mm nozzle,
0.20 mm first / 0.12 mm normal layers, six requested walls, 225°C nozzle,
35°C textured PEI and a 5 mm outer brim. Spiral mode and supports are off.
Maximum flow is 2.2 mm³/s; Mark1's +0.18 mm user trim emits `G29.1 Z0.16`.
Timelapse and bed leveling are On; flow and nozzle offset calibration are Auto.

- [Native print archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-full-base-single-tpu85a-mark1/2026-10-13-full-base-single-elbow-tpu85a-right06-z018-mark1.gcode.3mf)
- [Editable project](2026-10-13-full-base-single-elbow-tpu85a-right06-z018-mark1.3mf)
- [Actual print mesh](full-base-single-elbow-print.stl)
- [Native CAD](full-base-single-elbow.step)
- [Native readback](2026-10-13-full-base-single-elbow-tpu85a-right06-z018-mark1.readiness.json)
- [Geometry review](geometry-review.json)
- [Footprint review](full-base-native-footprint.json) and
  [local deposition review](full-base-single-native-audit.json)

The bed contact equals the complete XY projection. The first-layer region is
continuous, but the clamp channels interrupt vertical support beneath the
cuffs. Reviewed clamp-channel strokes retain prior-layer bead overlap;
the internal throat's remaining closing stroke is 0.232 mm long with a
0.536 mm bead. These are geometric and slice observations, without a model
of TPU sag, cooling or adhesion.

This is the full-base print trial. The extra stock is outside the compact
fitting envelope used in the installed layout study; its installed clearance,
loaded deformation and clamp-housing access have no acceptance result.
The [two-elbow print's failed result](../2026-10-13-continuous-body-tpu85a-mark1/physical-result.json)
retains its identified-job scope.

`prepare_mark1.py` regenerates the native files offline without sending a job.
