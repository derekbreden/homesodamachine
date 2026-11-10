# Close-contact PET-GF ceilings

This plate compares tighter contact gaps on solid interface mats. The target is
a continuous, well-bonded first roof course with support that provides useful
contact and can still be removed. The near-contact condition intentionally
tests the strongly bonded end of that range.

The lettered ceilings run D, E and F from left to right facing Mark1. D has the
largest gap and F the smallest. All use the same solid interface, extra contact
mat thickness and selected bridge flow and speed. The span matches the
[initial ceiling screen](../README.md); the support height and roof thickness
are reduced. No initial-screen condition is repeated.

The exact dimensions, requested gaps and common treatments belong to
[`recipe.json`](recipe.json). The actual sliced contacts belong to
[`verification.json`](verification.json). Its bead-gap calculation subtracts
the slicer's bridge bead height, which increases with the selected bridge
flow. The record also retains clearance to the CAD underside plane, so those
different measurements remain explicit. The gap is planned geometry, not a
measurement of real strand shape.

The slim tree style permits different top contact heights. Every coupon uses
native slicer settings, the established Mark1 PET-GF textured-plate trim and
the existing local cooling treatment. The shared material profile is unchanged.
The flow and speed candidates come from the
[local PET-GF bridge experiments](../../petgf-fins/README.md).

After cooling, keep the removed mat beside its lettered ceiling. Compare
removal effort with the retained underside's continuity, loose strands and
damage. A fused mat with a clean-looking underside does not establish useful
support removal. The first screen's spontaneous release is recorded in
[`physical-result.json`](../physical-result.json).

`coupons.rs` makes the labeled meshes in Rust. `prepare.py` uses the existing
ceiling-plate writer with the local recipe's process and object settings. The
editable project is here; the accepted machine archive and launch receipt
are in [`mark1/`](mark1/).

To regenerate the authored specimens and editable project:

```sh
ln -s ../../../../hardware/print-tests/petgf-dense-roofs/close-contact/coupons.rs tools/hsm/sandbox/examples/close-contact.rs
python3 tools/run.py -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox --example close-contact -- hardware/print-tests/petgf-dense-roofs/close-contact/parts
tools/cad-venv/bin/python hardware/print-tests/petgf-dense-roofs/close-contact/prepare.py --cli-output .cache/runs/close-contact-reproduction/input/close-contact.3mf
```

Slice the CLI input with arrangement and orientation preserved, then apply the
existing cooling stage using the editable project. Inspect the native contact
planes, bridge bead height, speeds, checksum, nozzle and bed footprint before
another submission. This is a manual print experiment, outside the normal build.
