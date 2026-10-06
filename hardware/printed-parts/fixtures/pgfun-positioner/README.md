# PGFUN swivel and pivot fixture

The [build instructions](../../../gun-positioner/README.md) govern this
two-axis gun fixture on the existing rotator. `design.json` controls the
nominal print pose and received fits. `build.py` emits all 60 STL/STEP pairs,
viewer payloads, a complete assembly and the downloadable `print-pack.zip`.
The six bearing coupons and one optional lens shim are included in that count.

Run with the repository CAD environment:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/pgfun-positioner/build.py
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/pgfun-positioner/check.py
```

`check.py` checks sampled clearances against pinned gun/rotator references and
screens loads. The receipt describes those numerical limits. Assembly sweeps
and the specified loaded commissioning establish actual received behaviour.
All individual exports share their specified print frame; assembly exports
retain rotator coordinates. Geometry is distributed by the CAD publication
bundle. The print archive contains the STLs, design and part manifest.
