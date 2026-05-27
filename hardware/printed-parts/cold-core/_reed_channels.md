# _reed_channels.py — naming and structure notes

Companion to `_reed_channels.py`. Captures what we like about how that file
is written. Intended as a quality bar for Python files in this repo.

## Things we like

**Vocabulary structure**

- Module-scope vocabulary defines the channel system once; every call site
  references named pieces, never inlined scalars.
- Symmetric envelope/cavity pairs (`cable_cavity_y_range` ↔
  `cable_envelope_y_range`; `reed_cavity_z_range` ↔ `reed_envelope_z_range`).
- Single-axis range tuples (`cable_cavity_y_range = (w, w + cable_y_height)`)
  rather than paired scalars (`cable_y_low`, `cable_y_high`). Two-tuples
  describing one extent of space, not two halves of an implicit one.
- Derivations are visible — envelope ranges derive from cavity ranges, cable
  Y range derives from reed Y range:
  ```python
  reed_cavity_z_range = (reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w)
  reed_envelope_z_range = (reed_cavity_z_range[0] - w, reed_cavity_z_range[1] + w)
  cable_cavity_z_range = (reed_cavity_z_range[0], cable_z_max)
  cable_envelope_z_range = (reed_envelope_z_range[0], cable_z_max + w)
  ```
- Named 2D anchor points for shared geometric joints
  (`wedge_apex_at_wall`, `corner_arc_terminus`, `fillet_axis_x/y`) — coupling
  between solids is visible at every reference site.
- Named profile shapes — `missing_wall_profile` is a named list of vertices;
  `slope_wedge` helper uses named anchor tuples internally.
- Channel concept materialized as a variable, showing what a channel IS:
  ```python
  total_envelope = reed_envelope.union(cable_envelope).union(missing_wall)
  total_cavity = reed_cavity.union(cable_cavity)
  channels = total_envelope.cut(total_cavity)
  ```
- `_channel_` lives at the function-name level (`build_reed_channels`,
  `cut_reed_channel_openings`); variables use bare `reed_` / `cable_`
  prefixes. Whole-system noun lives at the function level; pieces live at
  the variable level.

**Reading qualities**

- `make_box(x_range, y_range, z_range)` takes 3 ranges, not 6 scalars —
  call sites read as named slices of space, not floods of numbers.
- `slope_wedge(cable_envelope_y_range[1], cable_envelope_z_range)` reads as
  a noun phrase: "the slope wedge at the envelope's Z top, over the
  envelope's Y range."
- The return composition tells the story: total_envelope → cut by
  total_cavity → channels.

**Hygiene**

- Comments only carry design rationale the code can't say (why cable Z is
  shared with the cable hole; why envelope bottom is z=0).
- Lowercase for all single-letter abbreviations (`w`, `s`, `_w`, `_r`).
- No decorative whitespace alignment — no `=` columns, no padded commas,
  no aligned operators. The next rename doesn't silently break neighbors.

## Principles

- *Comments are diagnostics of confusion.* If a comment narrates what the
  code already says, the code isn't speaking — fix the names, not the
  comments. The urge to add a comment to defend a name = uncertainty in
  the writer.
- *Name what's shared.* If information is referenced more than once, name
  it. If a scalar exists only to feed one solid through one derivation,
  demote it. The dimensional ladder should be populated where the coupling
  lives — mostly at the joints (points and ranges), not the parts
  (scalars) or the wholes (solids).
- *Surface hidden dependencies.* When one solid reads `other_y_high + w`
  instead of `this_solid_y_high`, the names lie about the relationship.
  Rename to expose the real shared anchor.
- *Fill the dimensional-ladder gaps.* Scalars and complex solids often get
  names; 2D/3D anchor points and profile shapes don't. The joints are
  where coupling lives — surface the missing rungs.
- *Meaningful nouns earn names even at a single use.* Vague nouns don't,
  even with many uses.
- *Critical nouns carry one meaning.* Each file has its own domain nouns
  (this file: `envelope`, `cavity`, `reed`, `cable`, `channel`). Structural
  nouns carry across files — `range`, `depth`, `height`, `axis`, `apex`,
  `anchor`, `terminus`, `profile` — each naming the same kind of geometric
  role wherever it appears.
- *Function signatures shape call-site reading.* When a helper takes six
  scalars that compose into three ranges, change the signature.
- *Keep fixing until nothing bothers you.* If a name reads off, fix it. If
  a reader would have to do algebra to see a relationship, fix it. Cosmetic
  concerns count. The bar is "happy to have someone else review it in
  detail with no outstanding items from your perspective."
