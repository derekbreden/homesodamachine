# Complete faucet coupon with nonplanar contact bands

This trial prints the complete frozen faucet article through its first lower
curve, in the control's size and pose. The [job](print-job.json) owns its source
archive, printer calibration, settings and estimate. The dense roof process and
requested gap retain the [completed planar control](https://github.com/derekbreden/homesodamachine/blob/416bf47e9ded600fa3a0c7d19855d87d20b8b893/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-gap048-mark1/physical-result/physical-result.json).
Physical finish and release remain pending.

The [mapping](mapping.json) defines bounded layer bands near the dominant
inclined underside, blending into the ordinary layer family away from that
contact. Both the model and support roof follow those coordinates. Native
slicing runs on the mapped representation; the Rust recipe restores the
physical target and adjusts extrusion for the local vertical stretch. The
first bed courses and machine preparation retain their native executable
commands.

The [motion review](motion-review.json), [bead review](bead-review.json) and
[executable read-back](executable-review.json) describe the emitted paths and
their limits. The native clearance preset supplies a coarse head-height proxy;
it does not measure the nozzle tip's swept shape. These readings do not
establish surface finish or physical release.

The [manifest](nonplanar-manifest.json) identifies the restored G-code as the
print target. The archive retains the original physical model for reference.
Native reslicing requires the mapping and restoration procedure to reproduce
this experiment. Packaging retains the native plate's G-code and thumbnail
references. The [launch](launch.json) records printer acceptance. The
[first-layer status](first-layer-status.json) records deposition reported by
the printer without an error; it is telemetry rather than a camera inspection.
