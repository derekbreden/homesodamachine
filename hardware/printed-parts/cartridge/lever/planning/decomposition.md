# Lever — Decomposition

**Step:** 4d — Sub-Component Decomposition
**Input:** concept.md (Step 4a), synthesis.md, hardware/requirements.md, hardware/vision.md
**Scope:** Season 1, Phase 1, Item 4

---

## Decision: Pass Through

This part is a single geometric paradigm. No decomposition needed.

---

## Rationale

The lever is a flat rectangular plate (80mm × 50mm × 4mm) with four rectangular struts (6mm × 6mm × 90mm) extending perpendicular from its rear face. Every feature in the part is produced by a single CadQuery paradigm: **box extrusion**.

- The plate body is a box: `box(80, 4, 50)` with chamfered bottom perimeter edge.
- Each strut is a box: `box(6, 90, 6)` positioned at the four specified centers on the plate rear face.
- The strut-to-plate junction is a flush right-angle transition between two box extrusions — no sweep, no revolve, no loft, no helical feature.
- The 2–3mm corner radii on the plate perimeter are in-plane fillets on a prismatic body — a standard CadQuery `.edges().fillet()` call, not a separate geometric paradigm.

Every feature is rectilinear and prismatic. A single CadQuery agent can model the entire part with box primitives and one fillet operation. There are no features from different paradigms that would pull the generation agent in two directions. There is no natural boundary where a split would simplify either sub-problem — splitting the plate from the struts would create a composition boundary that adds pipeline complexity (6c step, two parts.md files, two drawings, two generation scripts) without reducing the difficulty of either sub-problem. Each sub-part after such a split would still be trivially simple; the composition join would be the only added work.

The quality gate criterion for pass-through is satisfied: a single CadQuery agent handles this without complex operations.

---

## Full Part Description

**Part name:** Lever, Phase 1

**All features (complete inventory):**

| Feature | Description | Operation | Paradigm |
|---------|-------------|-----------|----------|
| Plate body | 80mm × 50mm × 4mm rectangular slab | Box extrusion | Prismatic |
| Plate bottom chamfer | 0.3mm × 45° chamfer on bottom perimeter edge of plate (elephant's foot prevention) | Edge fillet/chamfer | Prismatic |
| Plate corner radii | 2–3mm radii on plate XY-plane perimeter corners | Edge fillet | Prismatic |
| Strut TL | 6mm × 6mm × 90mm rectangular prism at top-left position, extending from plate rear face | Box extrusion | Prismatic |
| Strut TR | 6mm × 6mm × 90mm rectangular prism at top-right position, extending from plate rear face | Box extrusion | Prismatic |
| Strut BL | 6mm × 6mm × 90mm rectangular prism at bottom-left position, extending from plate rear face | Box extrusion | Prismatic |
| Strut BR | 6mm × 6mm × 90mm rectangular prism at bottom-right position, extending from plate rear face | Box extrusion | Prismatic |

All features accounted for. No feature is orphaned.

**Geometric paradigm:** Box extrusion (prismatic). One paradigm throughout.

**CadQuery work required:** Box primitives, union, edge fillet. No sweeps, no revolves, no lofts, no helical operations.

---

## Pipeline Routing

Because this part passes through decomposition as a single unit, it proceeds directly:

```
4d (pass through — single part)
  │
  └── 4s (spatial resolution) → 4b (parts.md) → 5 (drawing) → 6g (CadQuery generation)
```

No composition step (6c) is needed.
