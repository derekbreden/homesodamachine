# Flush front roof and sliding funnel frame

Front-top's funnel opening clears the removable frame up to the exterior
Z355 ceiling. The frame carries a 196.5 mm wide front surround with 0.25 mm
air to each complete 9 mm shell flank. That surround ends at Y199.75 before the
Y200 seam. The rear frame envelope remains beneath Z349 and fits the
existing back-top roof; back-top's STEP, STL and viewer payload are retained
exactly.

The complete silicone brim bears on 3 mm of frame stock ending at Z349.
The silicone brim top and the removable front surround finish at Z355.
The display-side surround keeps a 3 mm landing behind the display roof
arris. Front-top's roof tongue clears this surround and the rear frame
envelope. The lower rails, socket, drain, cradle wing slots and their
placement datums remain unchanged.

Front-top has a solid display backing with one flat cavity face at Y95.208,
5.47 mm behind the deepest PCB-pocket corner. The frame's flat front at
Y95.458 has square plan corners and keeps 0.25 mm running air. A short
1.37 mm high 45° foot joins the wall to the bay lintel. Its loom bore passes
through the full wall; the proud cable clip occupies X68.5–86.5 above
Z285.796 and leaves its channel entrances open. The frame's lower 30° corbel
clears that clip. The silicone funnel and its 455.44 mL nominal capacity are
retained; capacity loss is 0 mL.
The combined rigid wall/frame boundary costs 66.57 mL of enclosure interior
air, measured against the bound geometry snapshot in `geometry-check.json`.

The front surround has the same width as the lower body. The frame has
no inward/top show round that needs a fine layer band. Functional
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
solids. It checks the full brim bearing, seated shell clearances, retained
lower socket/rail geometry, unchanged back-top, rear envelope, full roof
flank stock, flat display backing and clearance from nearby installed bodies.
[`rail-motion-check.json`](../integration-review/rail-motion-check.json)
reads the printable meshes at sampled front/rear insertion and shell
closing poses, with capture against 2 mm translations along all axes.

[`refresh_aggregate.py`](refresh_aggregate.py) replaces only the named
front-top and funnel-frame prototypes in each original STEP document using
the native XCAF API, the repository's assembly reader and viewer graft. Its
[`aggregate-refresh.json`](aggregate-refresh.json) verifies retained
names, native geometry and placements, colors and viewer arrays. A STEP
serialization that changes only spline integration readings receives a
native Boolean equivalence check as well as the geometry fingerprints.
This scoped refresh is not a fresh full-machine motion scorecard.

[`geometry-lint.json`](geometry-lint.json) binds the mesh review run after the
[`live publication check`](live-publication.json). Each intentional functional
bearing or supported ceiling has an answer beside its STL.
The [`v18 bead-backing record`](display-strip-backing-v18.json) binds only
its frozen native archive. Current geometry requires a fresh native slice
and support-removal review before a full-part print. Full-part printing is
deferred while the centered magnet and valve fit samples are evaluated.

The relevant physical failure is recorded in the
[`front-top v17 result`](../../../enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json).
The source geometry is a print candidate. Support
removal, rim finish, full-shell assembly fit and bearing under load need
their own physical observations; these checks do not qualify them.

## Reproduce

Run the scoped generator with the CAD environment, then refresh the
integration checks and aggregate members:

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/flush-roof-review/prepare_geometry.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/flush-roof-review/refresh_aggregate.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/flush-roof-review/check_geometry.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/integration-review/check_fit.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/print_regions.py
tools/cad-venv/bin/python tools/publish_now.py
```

Run geometry lint on the changed pieces after the publication is live,
following the printed-parts publish loop. Physical print qualification
remains separate from those lint results.

Read the display strip's previous-layer and support-tip footprints from a
frozen native review directory with:

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/flush-roof-review/check_display_strip.py <native-review-directory> --output <backing-record.json>
```

The retained-baseline comparisons use the immutable STEP/STL snapshots
in `.cache/flush-funnel-roof/baseline` and `.cache/front-roof-flat-wall/baseline`,
identified by the SHA256 values in the check records. The scoped generator and current mating-joint check
do not depend on those comparison snapshots.
