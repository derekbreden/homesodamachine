# Engineering Drawing Standards

This document defines the standards for engineering drawings in this project. Every custom part that will become a STEP file gets a third-angle orthographic projection drawing first. The drawing is the specification — it must faithfully represent the physical geometry of the part and every component it interfaces with.

---

## 1. What These Drawings Are

These are **engineering drawings** — precise technical documents that a machinist, 3D printer, or CAD operator could use to produce the part. They are not sketches, not diagrams, not approximations.

That means:
- Every dimension is caliper-verified or derived from caliper-verified measurements
- Every off-the-shelf component depicted matches its actual physical geometry — its real shape, not a simplified box
- Profiles, cross-sections, and mounting interfaces reflect the actual part, not a guess at what it might look like
- The drawing demonstrates that the author understood the physical reality of every component shown

Off-the-shelf parts that interface with custom parts have **caliper-verified geometry descriptions and reference photographs** in `../off-the-shelf-parts/`. Each part's `extracted-results/geometry-description.md` contains dimensioned descriptions, ASCII art profiles, and references to numbered caliper photos in the sibling `raw-images/` directory. These are the authoritative source for purchased component geometry — the geometry descriptions explain the measurements, and the photographs show the actual physical object being measured.

---

## 2. Drawing Format

- **Projection:** Third-angle orthographic (front, side, top views as needed)
- **Format:** SVG, hand-authored (not exported from CAD)
- **Views:** Minimum 2-3 orthographic views plus detail insets for complex interfaces
- **Scale:** Noted per view (e.g., "3 px/mm"), detail insets at higher magnification
- **Line conventions:**
  - Solid lines: visible edges
  - Dashed lines: hidden features (behind viewing surface)
  - Center lines: axes of symmetry, hole centers
  - Dimension lines: with extension lines and arrowheads

---

## 3. Source Material

For each part being drawn, the complete specification chain is:

1. **The part's `planning/parts.md`** — dimensions, features, interfaces, assembly notes
2. **Cross-referenced geometry descriptions** — linked from parts.md for every off-the-shelf component that mounts in or interfaces with the custom part (in `off-the-shelf-parts/*/extracted-results/geometry-description.md`)
3. **Reference photographs** — caliper photos of the physical off-the-shelf parts (in `off-the-shelf-parts/*/raw-images/`), referenced by number in the geometry descriptions
4. **Research files** — linked from parts.md, containing design analysis and rationale
5. **Requirements and vision** — `hardware/requirements.md` and `hardware/vision.md`

Every cross-reference in parts.md is a relative path. Follow them all.

---

## 4. Self-Review Rubrics

Apply these rubrics **after** generating the SVG, by reading back the source. Multiple review rounds encouraged. If the same problem persists after 2 attempts, move on rather than making things worse.

### Rubric 1 — Orthographic projection (MANDATORY axis lookup table)

Before drawing, fill out this table and reference it for every feature:

```
VIEW          | LOOKING ALONG | HORIZONTAL AXIS | VERTICAL AXIS
--------------+---------------+-----------------+--------------
Front view    | -Y            | X (width)       | Z (height)
Side view     | -X            | Y (depth)       | Z (height)
Top view      | -Z            | X (width)       | Y (depth)
```

For each cylindrical feature, determine its axis, then:
- View looking along that axis → CIRCLE (cross-section)
- Other two views → RECTANGLE / parallel lines (side profile)

Per-feature checklist (fill out for EVERY 3D feature):
- Feature name: ___
- 3D shape: ___ (cylinder, box, etc.)
- Axis it runs along: ___
- Front view (along Y): should show ___, I drew ___
- Side view (along X): should show ___, I drew ___
- Top view (along Z): should show ___, I drew ___
- MATCH? If any mismatch → FIX IT

### Rubric 2 — Visibility/masking

For each SVG element:
1. Does it have an opaque fill (fill="white", solid color, anything other than fill="none")?
2. Is it inside a section view? → OK (section views use fill for material/cutouts)
3. Is it outside a section view and covering other geometry? → BUG, use fill="none"

### Rubric 3 — Dash visibility at rendered scale

For each dashed line, compute: line_length_px / (dash + gap). If this ratio < 6, the line won't clearly read as dashed at screen resolution.

For thin views (e.g., 6mm depth at 8:1 = 48px), use stroke-dasharray="2,2" (not "5,3" or "6,3") to get enough dash repetitions. Use stroke-width 0.8 for hidden lines in thin views to visually distinguish from solid edges.

### Rubric 4 — Hidden line convention

- Features behind the viewing surface → dashed lines
- Visible features → solid lines
- In thin views where both surfaces are visible, features internal to the part (bores, channels) are still hidden

### Rubric 5 — View labeling and axis alignment

1. Each label directly above/beside its view?
2. Front and top views share same X pixel range?
3. Front and side views share same Z pixel range?

### Rubric 6 — Containment

**Part A — Required containers:** Detail view insets, section views at different scales, and callout magnifications MUST have an explicit bounding `<rect>` frame. If a detail/inset view exists without a frame → BUG, add one.

**Part B — Container must contain:** Every bounding box, detail view frame, or section cut boundary must fully contain its geometry. For each container element:
1. List all child geometry elements inside this container
2. Compute the bounding box of those children from their SVG coordinates
3. Compare children's bounding box against the container's rect coordinates
4. If children exceed the container on ANY side → BUG, either enlarge container or shrink contents

Note: Intentional physical protrusions (snap clips, fittings extending beyond a housing) are NOT containment bugs.

### Rubric 7 — Dimensional agreement

Every dimension callout must match the SVG geometry it references. For each dimension annotation:
1. Read the callout value (e.g., "55" meaning 55mm)
2. Find the two SVG elements/edges the dimension line spans
3. Compute the pixel distance between those edges
4. Divide by the drawing scale (px/mm) to get the implied real-world dimension
5. If the computed dimension doesn't match the callout value → BUG, fix geometry or callout

### Rubric 8 — Annotation collision (TOOL-ASSISTED)

Run `python3 tools/svg_label_check.py <file.svg>` after generating the SVG. The tool reports:

- **TEXT-TEXT**: Two text labels overlap. Always a bug — reposition one.
- **TEXT-BORDER**: A label crosses a rect edge. Usually a bug — should be fully inside or outside.
- **TEXT-LINE**: A label overlaps a non-dimension line. Often a bug — reposition.

Target: zero TEXT-TEXT collisions (non-negotiable), minimal TEXT-BORDER and TEXT-LINE.

### Rubric 9 — Physical adjacency (TOOL-ASSISTED)

Every sub-component must physically touch the parent body it attaches to. Run `python3 tools/svg_adjacency_check.py <file.svg>` after generating the SVG. Fix any FLOAT warnings.

**Root cause of adjacency bugs:** Child and parent coordinates computed independently from mm→px conversions, with rounding errors creating gaps. **Fix by anchoring child position to parent's already-computed pixel coordinates**, not recomputing from mm.

---

## 5. Workflow

1. Read the part's `planning/parts.md` and follow every cross-reference
2. Generate the SVG from scratch (do NOT read/edit an existing drawing — rewrite completely)
3. Apply all 9 self-review rubrics by reading back the SVG source
4. Run both checking tools and fix any issues
5. Re-run tools until clean

---

## 6. Related Documents

- **Off-the-shelf part geometry and photographs:** `hardware/off-the-shelf-parts/*/`
- **SVG label collision checker:** `../../tools/svg_label_check.py`
- **SVG adjacency checker:** `../../tools/svg_adjacency_check.py`
