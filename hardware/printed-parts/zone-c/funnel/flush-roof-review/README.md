# Flush front roof and sliding funnel frame

Front-top's funnel opening clears the removable frame up to the exterior
Z355 ceiling. The frame carries a 208.5 mm wide front surround with 0.25 mm
air at each vertical shell wall. That surround ends at Y199.75 before the
Y200 seam. The rear frame envelope remains beneath Z349 and fits the
existing back-top roof; back-top's STEP, STL and viewer payload are retained
exactly.

The complete silicone brim bears on 3 mm of frame stock ending at Z349.
The silicone brim top and the removable front surround finish at Z355.
The display-side surround keeps a 3 mm landing behind the display roof
arris. Front-top's roof tongue clears this surround and the rear frame
envelope. The lower rails, socket, drain, cradle wing slots and their
placement datums remain unchanged.

The side expansion grows 6 mm per side over machine Z334–346, equivalent
to print Z34.1–46.1. Its 0.5 outward/build-rise slope uses normal 0.24 mm
layers, six walls locally and no supports on the expansion. The frame has
no new inward/top show round that needs a fine layer band. Functional
rail bearings retain accessible supports. Front-top keeps its existing
RC62 sealed-pocket dimensions pending the separate friction-fit sample
results.

## Exports and review

[`generation.json`](generation.json) binds the sources, declared box and
the fresh front-top/frame STEP, STL and viewer payloads. It also records
the exact retained back-top triplet. The individual frame exports place
its underside on print Z0; front-top retains its machine-coordinate
exports and production mouth-down orientation.

[`geometry-check.json`](geometry-check.json) reads the exported native
solids. It checks the full brim bearing, seated shell clearances, unchanged
lower frame and shell geometry, unchanged back-top, rear envelope and
clearance of added stock from nearby installed bodies.
[`rail-motion-check.json`](../integration-review/rail-motion-check.json)
reads the printable meshes at sampled front/rear insertion and shell
closing poses, with capture against 2 mm translations along all axes.

[`refresh_aggregate.py`](refresh_aggregate.py) replaces only the named
front-top and funnel-frame members using the repository's assembly
import/export and viewer graft APIs. Its
[`aggregate-refresh.json`](aggregate-refresh.json) verifies retained
names, native geometry and placements, colors and viewer arrays.
This scoped refresh is not a fresh full-machine motion scorecard.

The relevant physical failure is recorded in the
[`front-top v17 result`](../../../enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json).
The revised geometry and native slice are print candidates. Support
removal, rim finish, full-shell assembly fit and bearing under load need
their own physical observations; these checks do not qualify them.

## Reproduce

Run the scoped generator with the CAD environment, then refresh the
integration checks and aggregate members:

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/flush-roof-review/prepare_geometry.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/flush-roof-review/check_geometry.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/integration-review/check_fit.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/flush-roof-review/refresh_aggregate.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/print_regions.py
tools/cad-venv/bin/python tools/publish_now.py
```

Run geometry lint on the changed pieces after the publication is live,
following the printed-parts publish loop. Physical print qualification
remains separate from those lint results.
