# CO2 chip width comparison

This plate compares narrower CO2 chips in the enclosure's retaining rails. Derek
accepts the [identification set's appearance and visual nozzle registration](../../../display-cover/prints/2026-11-08-identification-set-mark1-right-z005/physical-result.json);
its side-to-side fit needs more clearance.

[Variant dimensions](variants.json) define symmetric cuts from the native chip's
X edges. A sits on the left of the bed and B on the right, viewed from the front
of Mark One. Both keep the approved bore, lettering, height and thickness. The
existing full-width chip remains the comparison reference.

The [geometry preparation](preparation.json) records the source match, cuts and
plate placement. [Rust source](prepare_geometry.rs), fine models and STLs are
retained here with the editable project and native sliced archive. The canonical
tile generator applies the clearance Derek approves in the
[physical result](physical-result.json).

The [native slice review](review.json) records the active red and white PETG,
right-side hotends, full bead envelope and accepted clearance recipe. The
[launch record](launch.json) identifies the new job, actual AMS assignments,
calibration options, stopped dryers and shared-circuit spacing.

The physical result records the assessed comparison prints and the approved
production clearance between them.
