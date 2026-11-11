# Longer nonplanar contact bands with a smaller gap

This prepared Mark1 plate retains the complete frozen faucet coupon, its build
pose, dense roof, side clearance, bridge process and printer calibration. The
[job](print-job.json) owns the selected gap, machine settings and estimate. No
printer submission is part of this preparation.

The [parameters](parameters.json) extend each continuous sloping band before
its reversal. The requested contact gap is smaller. Both support roofs and
adjoining model courses use the restored layer family; the physical model in
the archive is unchanged. The [mapping](mapping.json) records the geometric
restoration, and the [manifest](nonplanar-manifest.json) binds the executable.
Native reslicing alone does not reproduce these paths: apply the retained
[Rust recipe](../../nonplanar/experiment.rs) and this plate's parameters.

The [contact reading](bead-review.json) refines close interface/model pairs
before reporting their conservative separation. The [command reading](executable-review.json)
checks actual extruding motion, retained bed courses, calibration and archive
references. The speed margin accounts for emitted coordinate rounding without
changing the reviewed paths or extrusion. The [motion reading](motion-review.json)
retains the native preset's coarse height proxy. That proxy does not measure
the swept nozzle, cone, sock or carriage.

The [dispatch archive reading](archive-review.json) binds the print-only
container to the same G-code bytes. Physical release and underside finish
remain pending. Derek is stopping and inspecting the
[preceding article](../2026-11-10-faucet-nonplanar-bands-mark1/in-progress-observation.json).
Its partial-run observation supports this next bounded experiment; it does
not qualify the complete motion range or support release.
