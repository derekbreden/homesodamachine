# E contact treatment on the complete rail cavity

This plate prints the complete production rail cavity with E's closer contact
distance. It retains the [D rail coupon's](../rail-cavity-30/) cross-section,
surrounding stock, print orientation, solid interface, bridge flow, bridge speed,
cooling and locally rooted production tree recipe. The raised label identifies RE.

[`samples.json`](samples.json) owns the crop bounds and process override.
[`preparation.json`](preparation.json) binds the production mesh to the plate.
The sliced machine archive and estimate are in [`ready/`](ready/).
The [verification record](verification.json) retains the emitted contact planes,
support roots, deposited bed envelope and archive hashes. The native rail slice
rounds the requested distance onto a full model-layer step. The record distinguishes
the requested contact distance from the nominal bridge-bead overlap at the interface.

Mark1's accepted job and startup reading are in [`mark1/`](mark1/). The
[physical result](physical-result.json) records removable supports with more
effort than the usual rail trees, fragmented removal and a pale roughened
corner. The user selects D for the following trials.

The [D peel result](../peel-scenarios/physical-result.json) records clean removal
reported by the user and the retained underside photographs. The complete rail
cavity preserves the production support height for the closer-contact trial.

## Article sources

The specimen geometry is defined in `samples.rs`. The [plate preparation source](https://github.com/derekbreden/homesodamachine/blob/d24b111b5d10e1eed4574db786e5ae1d0b96d445/hardware/print-tests/petgf-dense-roofs/rail-cavity-30-E/prepare.py) is archived in Git.
The retained project, slice and launch records identify the prepared article.
