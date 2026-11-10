# Close-contact PET-GF ceilings

This plate compares tighter contact gaps on solid interface mats. The target is
a continuous, well-bonded first roof course with support that provides useful
contact and can still be removed. The near-contact condition intentionally
tests the strongly bonded end of that range.

Derek reports that D and E release without taking the first model layer with
the support. Their surrounding walls anchor that layer, limiting transfer to
less enclosed geometry. The [physical result and photos](physical-result.json)
record the outcome. The [D peel scenarios](../peel-scenarios/README.md) apply
D alone to a cantilever, free panels and a production holed pad.

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

`coupons.rs` defines the labeled meshes in Rust. The [plate preparation source](https://github.com/derekbreden/homesodamachine/blob/d24b111b5d10e1eed4574db786e5ae1d0b96d445/hardware/print-tests/petgf-dense-roofs/close-contact/prepare.py) is archived in Git.
The editable project is here; the accepted machine archive and launch receipt
are in [`mark1/`](mark1/).
