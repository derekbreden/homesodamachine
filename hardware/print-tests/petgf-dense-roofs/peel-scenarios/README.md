# D support-contact and peel scenarios

This plate applies D's unchanged process to less anchored roofs and a production
pad surface. The target is support removal that retains the first model course
without relying on a ceiling enclosed by model walls.

Facing Mark1, the front row is XD then ND. The rear row is OD then PD.

| Specimen | Question |
| --- | --- |
| XD — cantilever | Does the first course survive peeling when only the west edge meets a permanent model wall? The bridge strands run outward from that wall. |
| ND — flat panel | Does the first course stay with a larger roof held entirely by slicer supports? |
| OD — holed panel | Does the first course survive removal around a hole and free outer edges without any permanent supporting walls? |
| PD — production pad | Does the actual enclosure's square holed underside and surrounding wall root release usefully? |

The cantilever and flat panel have a larger footprint than the enclosed screen.
The roof thickness, contact height, material and print treatment remain D's.
PD retains the production underside and pilot mouth, with lower empty height
and excess stock above removed. It is a contact-surface sample, rather than a
complete insert-post qualification.

ND and OD each have a small detached witness post beside the panel. It permits
the native slicer to process an object with a floating roof. It has no model
connection to the roof and does not stand beneath it. Keep it separate during
the examination. The native reading confirms no model deposition below either
free panel's underside, and bed-rooted slicer supports beneath each.

[`samples.json`](samples.json) owns the dimensions, wall placement and selected
scenarios. [`preparation.json`](preparation.json) binds the source surfaces,
models, plate positions and native object settings. [`verification.json`](verification.json)
records the unchanged D process, emitted contact planes, planned bead clearance,
bridge direction, trim and deposited bed envelope. It distinguishes D's
requested contact distance from the clearance below the thicker bridge bead.

The accepted machine archive is in [`ready/`](ready/), with its launch receipt
in [`mark1/`](mark1/). Neither the shared material profile nor the production
enclosure geometry changes.

## Examine after cooling

Keep each support beside its labeled panel. Start the peel at a free edge,
holding the model rather than its support mat. Record whether the interface
separates while the complete first model course stays on the roof, whether it
lifts individual model strands, or whether an entire model skin follows it.
Inspect both the removed sheet and the retained underside before discarding
either. Compare the cantilever's attached edge with its free end.

For the holed panels, inspect the hole mouth and the free outer edge separately.
Record removal effort, protruding strands and damage independently of surface
appearance. The earlier D/E outcome is in the
[physical result](../close-contact/physical-result.json); its wall anchoring
does not establish this plate's result.

## Reproduce

`samples.rs` authors the cantilever and free panels in Rust and crops the pad
from the retained production surface. `prepare.py` uses the existing native
plate writer and explicitly loads the reviewed D recipe. Temporary source
conversions and slice output stay in the run directory; the finished meshes
and machine file remain here.

```sh
tools/cad-venv/bin/python hardware/print-tests/petgf-dense-roofs/peel-scenarios/prepare.py --geometry --slice
```

The generator submits no printer job. Review the emitted contacts, model
anchoring and bed footprint before another submission. This manual comparison
adds no ordinary build or commit check.
