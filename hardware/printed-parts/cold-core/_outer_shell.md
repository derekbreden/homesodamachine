# _outer_shell.py — notes specific to this file

Companion to `_outer_shell.py`. Strictly file-specific content not
already in `_reed_channels.md`. Read that first; this file only
captures what's new.

## Single-builder shape

One `build_outer_shell` returning the unioned cup + bosses minus the
insert pockets. No cuts-into-foam_shell utility functions (those live
in `_port_cuts.py` and `_reed_channels.py`); no shared module-scope
helpers (those live in `_foam_cap.py`). The simplest builder shape in
the cold-core directory — appropriate because the outer shell is one
geometrically self-contained part.

## insert_pockets_at(y_floor) — inner helper parameterized by Y only

```python
def insert_pockets_at(y_floor):
    return (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=y_floor)
        .pushPoints(foam_cap_attachment_xz_positions)
        .circle(insert_pocket_radius)
        .extrude(insert_pocket_depth)
    )
bottom_pockets = insert_pockets_at(0)
top_pockets = insert_pockets_at(foam_shell_outer_height - insert_pocket_depth)
```

The two pockets differ only in starting Y; everything else is shared.
Compare `_foam_cap.py:attachment_pads_extrude(height)`, which is
parameterized by height instead (offset is always 0 there). Same
attachment positions, same circle radius, same extrude depth — only
the Y at which the pocket sits varies.

Kept as an inner function (not module-scope) because both call sites
are inside one builder. Same precedent as `slope_wedge` in
`_reed_channels.py`.

## Attachment positions are shared with the foam cap

`foam_cap_attachment_xz_positions` is imported and pushed three times:
once for the bosses (square pillars), once for each pocket pair (round
recesses inside the boss tops/bottoms). Cap-side joinery sits at the
same xz positions — see `_foam_cap.md` for the cap, lid, and gasket
that mate at these positions. The two files share the constant rather
than each redefining the 6-position list.

## Critical domain nouns

- `shell` — the rectangular cup (floor + four perimeter walls).
- `boss` — an 8×8 mm square pillar at one attachment position,
  extruded the full `foam_shell_outer_height`. Same noun as in
  `_foam_cap.md`; here it's the outer-shell side of the joint.
- `pocket` — a ⌀4 mm cylindrical recess for a heat-set insert. Two
  per boss, one at each ±Y face.
- `attachment` — the 6 screw positions where outer shell, foam cap,
  lid, and gasket all meet. Cross-file concept, lives in
  `_cold_core_interface.py` as `foam_cap_attachment_xz_positions`.

## See also

`WorldWorkplane` usage and `xz_plane_y_up` conventions:
[`_world_workplane.md`](_world_workplane.md). Cap-side joinery:
[`_foam_cap.md`](_foam_cap.md).
