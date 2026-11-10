# PET-GF dense support roofs

This plate compares the current support interface with a denser interface and
a solid interface. The open-front ceilings expose a broad underside, wall
junctions and an accessible peel edge. Raised letters stay on each roof; the
front of the roof stays flat for a caliper measurement.

Derek reports that all ceilings separate from the supports on cooling without
manual support removal. The retained roof strands remain visibly separate and
locally projecting. None is an acceptable supported underside. The
[physical result and photos](physical-result.json) record the observations;
the [close-contact plate](close-contact/README.md) tests tighter gaps and the
selected bridge flow and speed.

Facing Mark1, the coupons run left to right:

| Label | Interface |
| --- | --- |
| A | Current spacing; control |
| B | Denser spacing |
| C | Solid interface |

[`recipe.json`](recipe.json) owns the dimensions, arrangement, settings and
source hashes. [`verification.json`](verification.json) records the emitted
interface pitch, layer count, actual planned gap, nozzle, trim and deposited
bed envelope. The archive retains the shared profile's temperature, bridge
flow, cooling treatment and support construction. The printer and process
binding uses Mark1's established textured-plate PET-GF trim. This local
experiment leaves the shared material profile as it is.

The ceiling height aligns with the shared layer schedule. The short walls
keep the screen quick, and the roof leaves room for the support interface to
form. This screens density on a flat ceiling; it does not qualify tall trees,
long enclosed passages or a finished enclosure surface.

## Read the cooled samples

Keep each support and lettered roof together. Try removing the tree and then
peeling the contact mat from the open front. Record removal effort, remaining
interface, loose model strands and damage separately. Compare the center,
wall junctions and free edge. A mat that comes away readily can still leave
an unacceptable first model layer.

Feel the retained underside and measure roof thickness along its flat front
edge, away from the label and walls. The designed thickness is in the recipe.
Record thickness before and after peeling loose material. Photograph the
underside beside the removed support so the interface can be distinguished
from the model's first bridge course.

## Follow-up recommendation

Test interface density against actual vertical gap next. Denser contact can
reduce unsupported strand spans, while a smaller gap can reduce sag and
increase adhesion. Their interaction needs a physical comparison. Retain the
winning density and the current-spacing control at each gap, with repeated
controls spread across the plate. Read the emitted gaps rather than assuming
the slicer's requested value is the deposited separation.

Then vary interface thickness if the removed mat is uneven or breaks apart.
Use the same ceiling in perpendicular print directions and include a longer
ceiling and an actual mating-cavity sample before applying a result to the
enclosure. Direction, wall anchoring and support access affect what this
small coupon establishes.

If the first model course remains loose over an intact mat, compare bridge
speed and bridge flow using the candidates already supported by the
[bridge experiments](../petgf-fins/README.md). Change those after the contact
comparison so their effects remain identifiable. Keep nozzle temperature and
general cooling fixed during the density/gap work; the manufacturer's
material guidance and the local bridge results inform a later controlled
thermal comparison.

[`recommendations.json`](recommendations.json) holds the proposed factor levels,
source links and scope of each recommendation. The
[representative enclosure scenarios](../enclosure-support-scenarios/README.md)
provide rail, handhold and holed-pad samples for carrying selected densities
forward after a useful ceiling contact is established. Printing those variants
is deferred while the close-contact ceiling experiment runs.

## Reproduce

`coupons.rs` authors the meshes in the Rust kernel. Link it into the sandbox's
ignored examples directory and run it through the shared build wrapper:

```sh
ln -s ../../../../hardware/print-tests/petgf-dense-roofs/coupons.rs tools/hsm/sandbox/examples/dense-roofs.rs
python3 tools/run.py -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox --example dense-roofs -- hardware/print-tests/petgf-dense-roofs/parts
tools/cad-venv/bin/python hardware/print-tests/petgf-dense-roofs/prepare.py --cli-output .cache/runs/dense-roofs-reproduction/input/dense-roofs.3mf
```

Slice that CLI input with the installed Bambu Studio, preserving orientation
and arrangement. Apply the existing `petgf-cooling --directory ... --project ...`
stage using the editable project, then inspect the final archive's paths and
checksum before submission. The accepted archive and launch receipt live in
[`mark1/`](mark1/). The separate editable project preserves the per-object
settings and normal cooling hook for Studio.
