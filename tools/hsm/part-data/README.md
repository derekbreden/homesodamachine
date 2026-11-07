# Printed-part scalar data

`part-data` owns the scalar construction recipes, source-file readers, independent
analytical measurements and document figures for these printed parts:

- Water-inlet jet drilling jaws.
- Valve-seat socket and plinth figures.
- Funnel, drain-elbow cradle, removable frame, cover and casting mold.
- Dimension and port providers used from `hardware/reference` by the normal build.

The shop-storage providers left in `reference_catalog.rs`, their value types in
`storage.rs` and their `$env`, `$holder` and `$namespace` codecs in
`hardware/reference/_reference_data.py` serve no part. The next change to this crate takes
them out; edited alone, the crate reruns every build rule that reads it.

The existing geometry programs consume these recipes. Python compatibility modules
expose their established names and functions through
`hardware/scripts/_rust_data.py`; `_zone_data.py` supplies the shared funnel inputs
and registers the files read by its Rust programs with the build trace.

One JSON request is either a command-line argument or a line on stdin with
`part-data --serve`. Each request names `part`, an optional `method`, and the raw
upstream inputs that provider uses. Each response is its JSON result, or an
`error` object. The server flushes one response per request and writes no diagnostic
text to stdout.

The cradle's cantilever calculation supplies its insertion deflection and
slot lane. The mold report reads binary STL vertices for its chamber envelope and
binds the report to its STEP, STL, fine-model and viewer-payload hashes.

The reference catalog compiles its formulas, source readers and control flow into Rust.
`hardware/reference/_reference_data.py` marshals tuples, paths, envelope records,
holder records and callback inputs, and registers raw files consumed by Rust.

`comparison.json` and `tools/hsm/conversion-results/parts-final-2026-11-04.json` record the
fixed source/input hashes and completed provider comparisons.
