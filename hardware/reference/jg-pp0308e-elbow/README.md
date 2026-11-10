# John Guest PP0308E exterior reference

The purchased elbow reference uses smooth molded lands, broad rounds and planar
shoulders around its measured socket datums. [`elbow.rs`](elbow.rs) authors the
model. [`jg-pp0308e-elbow.step`](jg-pp0308e-elbow.step) and its native model and
viewer payload contain `fixed_body`, `y_collet` and `z_collet` in that order.

## Geometry and evidence

The socket axes meet at the origin and open along +Y and +Z. The exposed +Y
socket supplies the observed profile. The partly obscured +Z socket shares that
shape with the independently fitted root and collar diameter offsets. The +Z
nose and release ring are symmetry completions. Both release rings remain in
their captured resting position.

The fixed body retains the round bend core, thin outer web, small neck, radial
shoulder, tapered root, broad collar transition, outer collar, undercut and
rounded nose. Each conical land is a single profile line. Each broad molded
transition is a smooth curve. The release rings retain their taper, rounded rim
and planar release faces. Small surface fluctuations and molding texture are
outside this replica's scope.

[`scan-measurements.json`](scan-measurements.json) holds the native-scale rigid
frame, fitted bands, observed axial medians and measured face location.
[`scan-selection.json`](scan-selection.json) holds the inspected fixture
exclusion. [`source-cloud.ply.gz`](source-cloud.ply.gz) contains the untouched
scan, and [`observed-surface.ply.gz`](observed-surface.ply.gz) retains the open,
unfilled measured surface. [`measure_scan.py`](measure_scan.py),
[`derive_profiles.py`](derive_profiles.py) and [`scan_tools.py`](scan_tools.py)
read those observations. The sampled profiles are evidence for the nominal
surface, rather than a separate geometry recipe.

[`idealization-review.json`](idealization-review.json) records the smooth profile's
deviation from those sampled axial medians. That comparison describes the
idealization; it does not establish physical tolerances, coating thickness or
scan repeatability. The native capture remains in the local archive named in
the scan evidence.

## Interface scope

[`elbow.py`](elbow.py) supplies the existing `port()`, `stations()` and optional
native-CAD reader interfaces. The release-face datums and nominal tube diameter
remain the interface constraints. Socket insertion depth, internal stops, seals,
gripping teeth and release travel are unmeasured. The tube corridors establish
layout clearance without an insertion stop or internal mechanism.

## Regeneration

Run the Rust reference author from the repository root:

```sh
python3 tools/run.py -- cargo run --release --locked -j2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox --example jg-pp0308e-elbow \
  -- hardware/reference/jg-pp0308e-elbow
```

The [archived scan comparison](https://github.com/derekbreden/homesodamachine/blob/a78cf15ba5f85762e6ecaef94c03181b25ee272b/hardware/reference/jg-pp0308e-elbow/scan-model-check.json)
and [archived preview](https://github.com/derekbreden/homesodamachine/blob/a78cf15ba5f85762e6ecaef94c03181b25ee272b/hardware/reference/jg-pp0308e-elbow/model-preview.png)
retain the observation record for the geometry identified by their artifact
hashes. They are historical evidence rather than current model validation.
