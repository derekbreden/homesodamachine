# Rear support removal

This packet records the native toolpaths that implement the rear enclosure's support-removal
requirements. The [finished article feedback](../prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json)
identifies the trapped rail supports and inaccessible receiver interiors.

The native producer owns the support exclusions and bridge regions in
[the print features](../enclosure-back-top.print-features.json). The preparation carries those
regions into the native project. The review reads emitted support beads inside the actual
passage profiles, including branches serving other features.

The [prepared native print](native-print.json) binds the final project and sliced archive.
Its [native review](native-review.json) records the bed envelope, layer bands, reinforced
interiors, protected passages and support topology. It has not been submitted to a printer.

The [passage reading](passage-reading.json) separates the functional interiors from
the exterior support-request box. The [access reading](support-access.json) locates
the emitted tree bodies beyond the rear wall and records their removal opening.
The [vertical-travel reading](height-reading.json) includes the final clearance move.

The [native-input comparison](native-input-equivalence.json) binds the preserved
slice input and the review project by every uncompressed project member. The
review-scope metadata does not alter their meshes, support selections or settings.

The [vent clearance reading](vent-clearance.json) checks the added backing against the assembled
cold-core shell, lid and inlet valve.

The [build-axis reading](build-axis-reading.json) inspects the rails and receiver catches through the printed layers.
Native mesh lint belongs
to the published source artifact; functional host ceilings and previously answered findings
retain their own scope. Physical surface quality and support-removal effort remain observations
from the finished print.

The preparation readings retain hashes and findings from superseded digital files; those
preparations were not sent to a printer.
