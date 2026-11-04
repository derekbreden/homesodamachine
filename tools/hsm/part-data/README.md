# Printed-part scalar data

`part-data` owns the scalar construction recipes, source-file readers, independent
analytical measurements and document figures for these printed parts:

- ASSE vent adapter and straight cuffs; collet press and diaphragm-pump sleeve.
- Fake countertop, tube miter box and water-inlet jet drilling jaws.
- PCBA datums, populated-board GLB bounds and the shared electronics-tray recipe.
- Valve-seat socket and plinth figures.
- Funnel, drain-elbow cradle, removable frame, cover and casting mold.

The existing geometry programs consume these recipes. Python compatibility modules
expose their established names and functions through
`hardware/scripts/_rust_data.py`; `_zone_data.py` supplies the shared funnel inputs
and registers the files read by its Rust programs with the build trace.

One JSON request is either a command-line argument or a line on stdin with
`part-data --serve`. Each request names `part`, an optional `method`, and the raw
upstream inputs that provider uses. Each response is its JSON result, or an
`error` object. The server flushes one response per request and writes no diagnostic
text to stdout.

The pump-sleeve reader reads the scanned barb profiles. Its adaptive Simpson
integrals measure the smooth elbow's volume and foot area independently of mesh
chords. The cradle's cantilever calculation supplies its insertion deflection and
slot lane. The mold report reads binary STL vertices for its chamber envelope and
binds the report to its STEP, STL, fine-model and viewer-payload hashes.

`comparison.json` records the fixed source/input hashes and the completed provider
comparisons.
