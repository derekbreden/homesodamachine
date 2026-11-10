# Complete rail cavity coupon

This plate preserves the front-bottom enclosure's west rail cavity, supporting
arm and catch roof over a short longitudinal section. The floor retains thin
stock beneath the channel. The section keeps the source's print orientation
and layer phase so locally rooted trees can grow through the complete cavity.

The coupon uses D's contact distance, solid interface, bridge flow, bridge speed
and PET-GF cooling treatment. Tree style and branch angle follow the recorded
production rail recipe so branches root on the channel floor instead of reaching
around the open cut ends to the bed. Model infill retains the production solid
stock setting.

[`samples.json`](samples.json) owns the crop bounds and process overrides.
[`preparation.json`](preparation.json) binds the source mesh to the plate.
[`verification.json`](verification.json) records the retained stock, contact
planes, locally rooted support body, production build-up comparison, archive
hashes and print estimate. These are planned toolpaths; removal performance
requires a physical result.

The editable native project is beside this file. The sliced machine archive and
estimate are in [`ready/`](ready/). The plate is prepared offline and has not
been submitted to a printer.

## Reproduce

`samples.rs` crops the production mesh with the installed Rust geometry engine.
`prepare.py` reuses the native plate writer with a separate sandbox example name.
Temporary conversions and slicer output stay in the run directory; finished
meshes and machine files remain here.

```sh
tools/cad-venv/bin/python hardware/print-tests/petgf-dense-roofs/rail-cavity-20/prepare.py --geometry --slice
```

The generator submits no printer job and adds no ordinary build or commit check.
