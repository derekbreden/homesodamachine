# Longer complete rail cavity coupon

This plate extends the [archived complete rail cavity coupon](https://github.com/derekbreden/homesodamachine/tree/27c433f164134e1de2bab17fc0ab6501c2fbd401/hardware/print-tests/petgf-dense-roofs/rail-cavity-20) along
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

## Article sources

The specimen geometry is defined in `samples.rs`. The [plate preparation source](https://github.com/derekbreden/homesodamachine/blob/22a3f0d2e5ab3d0f06018a8fb12baea51ba14578/hardware/print-tests/petgf-dense-roofs/rail-cavity-30/prepare.py) is archived in Git.
The retained project, slice and launch records identify the prepared article.
