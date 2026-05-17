# _foam_cap.py — notes specific to this file

Companion to `_foam_cap.py`. Strictly file-specific content not
already in `_reed_channels.md`. Read that first; this file only
captures what's new.

## Three builders sharing attachment-position helpers

First cold-core module with three separate `build_*` returns
(`build_foam_cap`, `build_foam_cap_lid`, `build_foam_cap_gasket`).
All three consume `foam_cap_attachment_xz_positions` and reuse the
same square footprint or screw-clearance circle, varying only the
extrude height.

Two module-scope helpers fill the dimensional ladder for that
shared shape:

```python
def attachment_pads_extrude(height): ...        # rect(screw_boss_size, screw_boss_size)
def attachment_clearances_extrude(height): ...  # circle(screw_clearance_radius)
```

Each builder passes its own height (`foam_cap_height`,
`lid_cut_through_depth`, `gasket_thickness`). The cap-boss / gasket-
pad / lid-clearance / gasket-hole patterns reduce to one-liners at
call sites.

## Cut-through depth as a named constant

`lid_cut_through_depth = wall_and_floor_thickness * 3` names the
otherwise-magic `* 3` overshoot. CSG doesn't care about the exact
depth so long as it exceeds the lid's Y extent; the constant
documents that any sufficiently large value works and prevents the
`* 3` from looking semantically meaningful.

## Lid 2D anchor naming

`inset_x` and `inset_z` are magnitudes; signs live in the anchor
tuples (`pour_xz`, `vent_plus_z_xz`, `vent_minus_z_xz`). The two
vent holes are constructed with explicit `+inset_z` / `-inset_z`
rather than mirroring, since the third anchor (pour) breaks the
±z symmetry anyway.

## Removed: `cap.union(cap)`

The post-cut `return cap.union(cap).unwrap()` "consolidate
Compound into Solid" trick is unnecessary after the WorldWorkplane
migration — the STEP exporter handles the Compound directly. Test
gate: `cq.exporters.export(cap.unwrap(), path)` followed by
re-import yields a single Solid with the expected volume.

## Critical domain nouns

- `cap` / `lid` / `gasket` — the three solids this module builds.
- `attachment` — the 6 screw positions where cap, lid, gasket, and
  outer-shell all meet (`foam_cap_attachment_xz_positions`).
- `boss` — the cap's upright screw column (cap-only). `attachment`
  is the broader concept; `boss` is the cap's physical pillar.
- `clearance` — the through-cylinder for the M3 SHCS shank.
- `pad` — gasket's square footprint at each attachment position,
  shaped to match the cap-boss footprint above it.
- `pour` / `vent` — the two kinds of lid through-holes for the
  foam pour.

## See also

`WorldWorkplane` usage and `xz_plane_y_up` conventions:
[`_world_workplane.md`](_world_workplane.md).
