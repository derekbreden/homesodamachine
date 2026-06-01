# touch_flo_shell.py — naming and structure notes

Companion to `touch_flo_shell.py`. Names the idioms that file embodies, so a
reader told to "follow these patterns" knows what the patterns are. The code
is the example; this is the gloss. When the two disagree, the code is right —
fix this doc.

## Vocabulary

- Module-scope vocabulary defines the part once; every call site references a
  named piece, never an inlined scalar. A literal at a call site is a missing
  name.
- Derivations are written as derivations. A dimension that follows from others
  is the expression that produces it —
  `shell_outer_r = max(_body_bore_farthest_from_shell_center,
  _pill_farthest_from_shell_center) + wall_thickness_min` — not a pre-computed
  number with its origin lost.
- Named anchors carry the joints. Where solids meet, the meeting place has a
  name: `split_junction_y/z`, `back_arch_center_z`, `lever_ramp_y_start`, the
  gooseneck path's `_path_p2 … _path_p5`. The coupling is then visible at every
  site that reads it.
- Named profiles and sketches. A 2D outline that is extruded or swept is a
  named shape — `_tube_shell_outer_sketch`, the `build_lever_clearance`
  polyline, the `_arch_extrude` profile — not an anonymous vertex list buried
  in a chain.
- Envelope and cavity are one materialized pair. Each zone is a
  `build_zoneN_outer` (the solid) and a `build_zoneN_inner_cut` (the void it
  removes); `build_shell` fuses the outers, fuses the inners, and cuts. The
  return composition tells the whole story.

## Frame discipline

- One world frame, declared once in the module docstring (X lateral, −Y
  forward toward the glass, +Z up). Every number is in it.
- Workplanes are named for what they are — `_horizontal_plane`,
  `_vertical_plane`, `_path_plane`, `_profile_plane` — each with its `xDir` and
  `normal` stated, so a drawn `(a, b)` maps to a world axis you can predict
  without re-deriving it. The machinery is `../../cadlib/world_workplane.py`.

## Dimensions that also appear in prose

- A number written in both the code and a human-facing doc is written once and
  coupled, never copied. `[value](NAME)` markers (`tools/docgen/`) tie a comment
  or a markdown dimension to the constant that owns it; `main()` rewrites them
  and asserts their counts. A dimension in prose that docgen doesn't own is a
  dimension waiting to drift.

## Comments

- Comments describe the geometry, never the code. Good names already say what a
  line is and does; a comment that narrates a line, restates its arithmetic, or
  argues why it was written that way is deleted. The file reads as mostly silent
  code on purpose — that silence is what sends a reader here.
- A comment earns its place only for a geometric or physical fact the names
  cannot hold: a constraint a dimension must satisfy, what a shape is in the
  real assembly, a spatial relationship the math hides.

## Hygiene

- No decorative whitespace alignment — no `=` columns, no padded commas. The
  next rename can't silently break a neighbor.
- Lowercase for single-letter abbreviations.

## Principles

- *Name what's shared.* Referenced more than once → name it. A scalar that
  feeds one solid through one derivation can stay a scalar; an anchor two
  solids both read is a name.
- *Surface hidden dependencies.* When one solid reads `other_edge + w` instead
  of a shared anchor, the names lie about the relationship. Rename to expose it.
- *Fill the dimensional-ladder gaps.* Scalars and finished solids get names; the
  2D anchors and profile shapes between them often don't. The joints are where
  the coupling lives — surface the missing rungs.
- *Meaningful nouns earn names, even at one use. Vague nouns don't, even at
  many.*
- *Function signatures shape call-site reading.* A helper that takes the three
  ranges it composes reads as named slices of space; one that takes six scalars
  reads as a flood of numbers. Change the signature.
- *Keep fixing until nothing bothers you.* If a name reads off, fix it. If a
  reader would do algebra to see a relationship, fix it. Cosmetic counts.

## On what is

These idioms serve one discipline: every line describes what the part *is* —
never what it was, what it will be, what was considered and rejected, why this
and not that, or how sure the author is. The comment rule above is one face of
it. The whole is `calibration/Principle.md`; read it.
