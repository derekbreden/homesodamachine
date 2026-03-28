# Sub-Component Composition

This document defines the procedure for the composition agent (Step 6c). This agent takes the CadQuery scripts produced by the parallel sub-component generation agents (Step 6g) and combines them into a single validated STEP file. Its job is mechanical: translate, rotate, union, apply interface treatments, validate. It does not design geometry or make spatial reasoning decisions — those were made upstream.

**Why this step exists.** Each sub-component generation agent produces a valid solid in its own local reference frame. The composition agent assembles these solids into the final part using the transforms and operations specified in the decomposition document (Step 6d). This separation means the composition agent needs only CadQuery boolean operation skills, not complex modeling skills.

---

## What the agent receives

1. **The decomposition document** from Step 6d — contains the composition specification: transforms, operation order, interface treatments, boolean operation notes
2. **The sub-component CadQuery scripts** from Step 6g — one per sub-component, each producing a valid solid
3. **The original parts.md** — for the final validation suite (bounding box, feature probes, etc.)
4. **The STEP generation standards** — `hardware/pipeline/steps/6-step-generation.md` — for validation rubrics

---

## Script structure

The composition script follows this structure:

```python
#!/usr/bin/env python3
"""
[Part Name] — Composition Script

Combines sub-component solids into the final part.
Source: [decomposition document path]
Sub-components:
  A: [name] — [script path]
  B: [name] — [script path]
"""

import cadquery as cq
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator

# ============================================================
# 1. BUILD SUB-COMPONENTS
# ============================================================

# Option A: Import and call sub-component build functions
# Option B: Inline the sub-component geometry (for simple cases)
# Option C: Load pre-exported STEP files with cq.importers.importStep()

# The preferred approach is Option A: each sub-component script defines
# a build_*() function that returns a CadQuery Workplane, and this script
# imports and calls them. This avoids re-exporting/re-importing STEP files
# and keeps the geometry in CadQuery's native representation.

# ============================================================
# 2. APPLY TRANSFORMS (from decomposition spec)
# ============================================================

# sub_b = sub_b.translate((tx, ty, tz))
# sub_b = sub_b.rotate((0,0,0), (1,0,0), angle)  # if rotation needed

# ============================================================
# 3. BOOLEAN OPERATIONS (in specified order)
# ============================================================

# result = sub_a.union(sub_b)
# result = result.union(sub_c)  # etc.

# ============================================================
# 4. INTERFACE TREATMENTS
# ============================================================

# Fillets, chamfers at joints — only if specified in decomposition doc
# result = result.edges(...).fillet(radius)

# ============================================================
# 5. EXPORT
# ============================================================

# cq.exporters.export(result, output_path)

# ============================================================
# 6. VALIDATE COMPOSED SOLID
# ============================================================

# Full validation suite from step-generation-standards.md:
# - Feature probes for EVERY feature from parts.md (not just interface points)
# - Solid validity, single body, volume check
# - Bounding box reconciliation against full part envelope
# - PLUS: interface boundary probes (see below)
```

---

## Interface boundary probes

In addition to the standard validation suite, the composition agent must probe the interface boundaries between sub-components:

1. **Solid at the joint center.** If sub-components A and B meet at a face, probe the center of that face — it must be solid (no gap).
2. **Solid on both sides of the joint.** Probe 0.5mm inside each sub-component at the joint face — both must be solid (the union didn't create a void).
3. **Void outside the joint.** Probe 0.5mm outside the expected part boundary at the joint — must be void (the union didn't create spurious material).
4. **No self-intersection.** `v.check_valid()` catches this, but note that boolean operations on complex geometry (especially helical sweeps) are the most common source of self-intersecting faces in OCCT.

---

## Boolean operation ordering

OCCT (the geometry kernel behind CadQuery) is sensitive to the order of boolean operations, especially when complex geometry is involved. The decomposition document may specify an ordering. General guidelines:

1. **Union simple geometry first.** Cylinders, boxes, and extruded features before swept or lofted features.
2. **Perform cuts after all unions.** If any sub-component has features that cut into the combined solid (rare — most cuts are internal to a sub-component), do those last.
3. **If a union fails,** try the reverse order (`b.union(a)` instead of `a.union(b)`) — OCCT sometimes handles one direction better than the other.
4. **If a union produces a multi-body result,** the interface faces are not touching or overlapping. Check transforms — a translation error of even 0.01mm can cause this.

---

## When there is no decomposition

If Step 6d determined the part needs no decomposition ("pass through"), Step 6c is skipped entirely. The single CadQuery agent from Step 6g produces the final STEP file directly, and its built-in validation suite is sufficient.

---

## Agent prompt must include

- Path to the decomposition document (Step 6d output)
- Paths to all sub-component CadQuery scripts (Step 6g outputs)
- Path to the original parts.md (for full validation)
- Path to `hardware/pipeline/steps/6-step-generation.md` (for validation rubrics)
- Path to `hardware/requirements.md` (printer constraints for bounding box checks)
- Instruction to follow the composition specification exactly — no improvised transforms or interface treatments
- Instruction to run the script and achieve zero validation FAILs before exporting
- **Instruction that if a boolean operation fails, the agent should try reordering operations or adjusting overlap before reporting failure** — OCCT boolean sensitivity is a known issue, not a design flaw

---

## Quality gate

The final STEP file must:

1. **Pass all standard validation rubrics** from `6-step-generation.md`: feature probes, solid validity, single body, volume, bounding box
2. **Pass interface boundary probes** for every joint between sub-components
3. **Be a single solid body.** Multi-body results indicate a failed union.
4. **Match the bounding box of the full part** as specified in parts.md — not just the sub-components individually
5. **The script must run.** As with all STEP generation in this pipeline, an unrun script is not a deliverable.

---

## Output

- **Script:** `hardware/printed-parts/<part-name>/generate_step_cadquery.py` — the composition script replaces any prior generation script. It IS the generation script for this part.
- **STEP file:** `hardware/printed-parts/<part-name>/<part-name>-cadquery.step`
- **Sub-component scripts** (if separate files): `hardware/printed-parts/<part-name>/sub_<name>.py` — kept for auditability but not the deliverable. The composition script is the deliverable.
