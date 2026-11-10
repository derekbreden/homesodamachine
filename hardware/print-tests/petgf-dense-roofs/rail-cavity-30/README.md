# Longer complete rail cavity coupon

This plate extends the [complete rail cavity coupon](../rail-cavity-20/) along
the slide direction. Its production cross-section, surrounding stock, D contact
treatment and locally rooted tree recipe remain the same.

[`samples.json`](samples.json) owns the crop bounds and process overrides.
[`preparation.json`](preparation.json) binds the source mesh to the plate.
[`verification.json`](verification.json) records the native estimate, support
root and build-up, emitted contact planes and archive hashes.

The editable native project is beside this file. The sliced machine archive and
estimate are in [`ready/`](ready/). The plate is prepared offline and has not
been submitted to a printer. The [matching pair](../rail-fit-30/) adds the actual
front-top rail and surrounding wall to this longer cavity on the same plate.

## Reproduce

`samples.rs` crops the production mesh with the installed Rust geometry engine.
`prepare.py` reuses the existing native plate writer. Temporary conversions and
slicer output stay in the run directory; finished meshes and machine files
remain here.

```sh
tools/cad-venv/bin/python hardware/print-tests/petgf-dense-roofs/rail-cavity-30/prepare.py --geometry --slice
```

The generator submits no printer job and adds no ordinary build or commit check.
