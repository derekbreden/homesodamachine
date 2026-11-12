# Printed-part scalar data

`part-data` owns the scalar construction recipes, source-file readers, independent
analytical measurements and document figures for these printed parts:

- Water-inlet jet drilling jaws.
- Valve-seat socket and plinth figures.
- Funnel, drain-elbow cradle, removable frame, cover and casting mold.
- Dimension and port providers used from `hardware/reference` by the normal build.

The geometry and inspection tools consume these native recipes. The reference catalog
provides explicitly requested dimension and port readings from its retained source data.

One JSON request is the command-line argument. It names `part`, an optional `method`,
and the raw upstream inputs that provider uses. The response is its JSON result on
stdout.

The cradle's cantilever calculation supplies its insertion deflection and
slot lane. The mold report reads binary STL vertices for its chamber envelope and
binds the report to its STEP, STL, fine-model and viewer-payload hashes.

The reference catalog compiles its formulas, source readers and control flow into Rust.
Its native JSON request interface returns the requested values and records the raw files read.

`comparison.json` and `tools/hsm/conversion-results/parts-final-2026-11-04.json` record the
fixed source/input hashes and completed provider comparisons.
