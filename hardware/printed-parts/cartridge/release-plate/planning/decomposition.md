# Release Plate — Decomposition Decision

**Step:** 4d — Sub-Component Decomposition
**Input:** concept.md (Step 4a output)
**Output:** Pass-through declaration — no decomposition

---

## Decision: Pass Through

**This part is a single geometric paradigm. No decomposition needed.**

The release plate is entirely an extrude-and-cut problem. Every feature on the part belongs to the same paradigm: prismatic and cylindrical operations using box bodies, cylinder unions, revolved-profile cuts, and a perimeter fillet. No feature requires a different technique from any other feature. A single CadQuery agent can handle this in one script.

---

## Rationale

The part's complete feature set:

| Feature | Operation | CadQuery technique |
|---|---|---|
| Plate body (80mm × 65mm × 5mm) | Add | `box()` |
| Guide pin × 2 (Ø5mm × 30mm, rear face, diagonal corners) | Add | `cylinder()` union |
| Stepped bore × 4 (Ø15.6mm outer / Ø10.07mm inner / Ø6.5mm through) | Remove | revolved profile cut |
| Perimeter edge radius (3mm, front face rearward edge) | Add/blend | `fillet()` on selected edges |
| Perimeter corner radii (2–3mm, XY corners) | Add/blend | `fillet()` on selected edges |
| Elephant's foot chamfer (0.3mm × 45°, bottom perimeter edge) | Remove | `chamfer()` on selected edge |

Every operation in this list is standard 2.5D CadQuery work. The stepped bores are the most complex feature — they require a revolved profile cut — but that is a documented, preferred CadQuery pattern (see 6-step-generation.md Section 5: "Stepped bores with chamfers — use revolved profiles"). The guide pins are simple vertical cylinder unions. The fillets and chamfer are single-edge selections on a compact body. No sweeps, no lofts, no helical operations, no multi-paradigm work of any kind.

The concept document confirms this: it describes one printed PETG part with no joints, no sub-assemblies, and no features whose geometry is independent of the surrounding plate body. The bores and the pins share a coordinate system and have clearance constraints relative to each other — they are geometrically interdependent and belong in the same model.

Decomposing this part would add pipeline complexity (two 4s passes, two 4b passes, two drawings, two CadQuery scripts, one composition agent) with no benefit. The single-agent script for this part is straightforward.

---

## Pipeline routing

The release plate proceeds as a single unit through the remaining pipeline steps:

```
4d (this document — pass through, no decomposition)
  │
  └── 4s (spatial resolution) → 4b (parts specification) → 5 (engineering drawing) → 6g (CadQuery generation)
```

No composition step (6c) is needed. The CadQuery generation agent receives the parts.md from 4b and produces a single STEP file for the complete release plate.
