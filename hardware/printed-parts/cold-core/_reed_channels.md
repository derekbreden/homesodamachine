# _reed_channels.py — naming and structure notes

Companion to `_reed_channels.py`. Captures what we like about how that file
ended up, and how we got there. Intended as a quality bar + playbook for the
same level of effort on other Python files in the repo.

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
  Z range derives from reed Z range:
  ```python
  reed_cavity_z_range = (reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w)
  reed_envelope_z_range = (reed_cavity_z_range[0] - w, reed_cavity_z_range[1] + w)
  cable_cavity_z_range = (reed_cavity_z_range[0], cable_z_max)
  cable_envelope_z_range = (reed_envelope_z_range[0], cable_z_max + w)
  ```
- Named 2D anchor points for shared geometric joints
  (`wedge_apex_at_wall`, `corner_arc_terminus`, `fillet_axis_x/z`) — coupling
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
  a noun phrase: "the slope wedge at the envelope's Y top, over the
  envelope's Z range."
- The return composition tells the story: total_envelope → cut by
  total_cavity → channels.

**Hygiene**

- Comments only carry design rationale the code can't say (why cable Y is
  shared with the cable hole; why envelope bottom is y=0).
- Lowercase for all single-letter abbreviations (`w`, `s`, `_w`, `_r`).
- No decorative whitespace alignment — no `=` columns, no padded commas,
  no aligned operators. The next rename doesn't silently break neighbors.

## How we accomplished them

**Principles**

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
- *Function signatures shape call-site reading.* When a helper takes six
  scalars that compose into three ranges, change the signature.

**Process**

- Establish a regression sieve before refactoring — four scalars (volume +
  bbox + COM). Re-verify after every batch. Never adjust geometry to match
  the baseline.
- Don't reach into other files to verify or fix. Flag cross-file concerns
  in the report; don't cross scope.
- Spawn agents for delimited tasks with explicit principles + sieve gates;
  hand-edit for surgical follow-ups. Agents tend to over- or under-apply
  principles unless the brief is concrete; hand-edits are cheaper for
  small, well-scoped fixes.
- Read the file end-to-end after each pass. Anything still vague? Anywhere
  a reader would have to do algebra to see a relationship? Fix it before
  declaring done.

**Critical-noun consistency passes**

For each critical noun, verify every use carries exactly one meaning.

- *Domain nouns* (this file): `envelope`, `cavity`, `reed`, `cable`,
  `channel`. Plus `wall`, `fillet`, `bag_pocket`, `corner` to a lesser
  extent. Other files will have different domain nouns; identify them
  first by scanning the module-scope and function-name vocabulary.
- *Structural nouns* (mostly carry across files): `range`, `depth`,
  `height`, `axis`, `apex`, `anchor`, `terminus`, `profile`. Each should
  name the same kind of geometric role wherever it appears.

**Hygiene passes**

- Casing: all single-letter abbreviations lowercase.
- Whitespace: strip any decorative alignment (`=` columns, padded commas,
  aligned operators inside argument lists). Single space around `=`,
  single space after `,`.
- Trailing commas, stray underscores, unused imports — the small things
  that accumulate.

**Stopping condition**

- Keep reading the file until nothing bothers you. Cosmetic concerns count;
  if a name still reads off, fix it. The bar is "happy to have someone else
  review it in detail with no outstanding items from your perspective."

---

*For reference, this file's transformation runs from `7b691bc` (correct
geometry, full of artifacts) to `9635172` (current state) — eight commits,
geometry preserved at every step. `git diff 7b691bc..9635172 -- hardware/printed-parts/cold-core/_reed_channels.py`
shows the full arc.*
