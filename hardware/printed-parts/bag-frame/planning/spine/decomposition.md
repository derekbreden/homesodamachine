# Spine — Decomposition Decision

**Date:** 2026-03-29
**Inputs:** concept.md §1, §2, §5, §6, §7; hardware/requirements.md; hardware/pipeline/steps/6-step-generation.md; cradle-platform/parts.md §Feature 6 and §Interface table

---

## Decision: Pass Through — No Decomposition

The spine is a single printed part. It requires no sub-component split.

---

## Geometric Inventory

Every feature on every face of the spine, categorized by operation type:

| Face | Feature | Operation | Shape |
|------|---------|-----------|-------|
| Front face | Transverse ribs (×~22 across 220mm at 10mm spacing) | Add | Rectangular boss strips extruded from face |
| Front face | Fold-end slots ×2 (195mm wide × 20mm tall × 10mm deep) | Remove | Rectangular pocket cut into face |
| Rear face | Horizontal snap-tab slots ×4 (8.2mm wide × 15mm deep, open at top) | Remove | Rectangular blind slot, open top |
| Left end face | Snap posts ×2 (10mm × 6mm oval, 8mm protrusion) | Add | Oval boss extruded from end face |
| Right end face | Snap posts ×2 (10mm × 6mm oval, 8mm protrusion) | Add | Oval boss extruded from end face |
| All corners | Fillets (2mm on face-to-wall transitions; 1mm chamfer on post entry edges) | Add/remove | Edge treatments |

---

## Paradigm Analysis

**CadQuery 2.5D definition (from 6-step-generation.md):** A feature is "2.5D prismatic" if it can be realized as a 2D sketch on a workplane, then extruded along a single axis — either as a positive extrusion (boss, wall, rib) or a negative extrusion (pocket, slot, cut-through). Revolved profiles and simple chamfers/fillets are also within scope. The 2.5D paradigm covers all of: rectangular bosses, rectangular pockets, rectangular slots, oval bosses, stadium slots, chamfers, fillets, and combinations thereof via boolean union/subtract.

**Every spine feature is a workplane-sketch-extrude operation:**

- **Transverse ribs:** Rectangular profile sketched on the front face (XZ workplane), extruded outward in Y. Repeated at 10mm Z intervals. Identical operation, different Z position.
- **Fold-end slots:** Rectangular pocket sketched on the front face, extruded inward (negative Y). Two instances, one per bag position at different Z heights.
- **Snap-tab slots:** Rectangular blind slot on the rear face, open at top. Sketched as a rectangle on the rear face (XZ workplane), cut inward (positive Y toward front). Four instances spaced along Z and distributed between two X positions (two per cradle position). Open at top = slot walls stop at the spine's top face, no bridging required.
- **Snap posts:** Oval (stadium) profile sketched on the end face (YZ workplane), extruded outward in X. Two per end face at different Z heights.
- **Edge treatments:** Fillets and chamfers applied to edges — standard CadQuery `.edges().fillet()` and `.edges().chamfer()` operations.

There is no feature on the spine that requires a swept profile, a revolved solid, a lofted surface, or any cross-sectional shape that varies along the extrusion axis. Every feature is constant cross-section through its full depth. This is the definition of a 2.5D prismatic part.

---

## Why Not Decompose

**The decomposition criterion is:** split when features combine fundamentally different geometric paradigms.

The spine has no such combination. All features — ribs, pockets, slots, bosses, chamfers — live within the 2.5D prismatic paradigm that CadQuery handles natively via workplane-sketch-extrude. There is no feature that requires a different approach, a different modeling paradigm, or a geometry kernel operation that cannot be composed from extrudes and booleans.

**Specific cases considered and rejected:**

1. **Snap posts vs. prismatic body:** Oval bosses on end faces could be imagined as a separate "post sub-part" unioned to the body. But oval extrusions are explicitly within CadQuery's 2.5D repertoire (`slot2D()` or direct polyline profile). The posts are simple protrusions from a planar face. No paradigm boundary exists here.

2. **Front face rib texture vs. structural body:** Transverse ribs are rectangular boss strips from a flat face. They are simpler than the body itself — a loop of `box.extrude()` calls at incremented Z positions. No justification for splitting the "rib zone" from the "structural zone."

3. **Different faces, different features:** The front face (ribs + slots), rear face (tab slots), and end faces (snap posts) each bear different feature sets. But all features are the same paradigm applied to different workplanes. CadQuery's workplane model is designed exactly for this: `cq.Workplane("XZ")` for front and rear faces, `cq.Workplane("YZ")` for end faces. This is not a paradigm difference — it is a plane rotation, which is handled by the composition rule "rotations."

4. **Print orientation check:** The spine prints front-face-down, 220mm along X. In this orientation: ribs and fold-end slots (front face) are on the build plate side — they print as the first layers, giving best surface quality. Rear-face slots open toward the top of the print — no overhang. Snap posts protrude horizontally in X from the end faces — they print as walls in the XY plane without overhang. No feature in any orientation creates a geometry that would require splitting the part to remain printable.

5. **Load path integrity:** concept.md §7 and the structural analysis confirm the spine carries ~40N total bag load through four snap posts to the enclosure. This load passes through the spine body as a single continuous solid. Splitting the spine — even at a "natural" geometric boundary like the rib zone — would introduce an interface into the load path that is strictly worse than continuous material. Structural continuity is a positive argument for the single-part solution.

---

## Interface Context: Cradle Tab Engagement

The spine's rear-face slots receive the cradle platform snap tabs. From cradle-platform/parts.md §Feature 6 and §Interface table:

- Tab body: 8mm wide (Z direction on cradle), 2mm thick, 15mm cantilever
- Hook: 1.2mm height, 90° retention face
- Mating slot in spine: 8.2mm wide (Z) × 15mm deep, open at top

These are rectangular slots cut into the rear face of the spine body — standard rectangular pockets in CadQuery. The slot dimensions are already specified in the concept. The interface adds no geometric complexity that would motivate decomposition.

---

## Feature Assignment (Complete — No Orphans)

| Feature | Assigned to |
|---------|-------------|
| Transverse ribs (×~22, front face) | Spine body |
| Fold-end slots ×2 (front face) | Spine body |
| Snap-tab slots ×4 (rear face) | Spine body |
| Snap posts ×2 left end | Spine body |
| Snap posts ×2 right end | Spine body |
| Edge fillets (2mm face transitions) | Spine body |
| Post entry chamfers (1mm) | Spine body |

All features assigned. No feature orphaned.

---

## Output for Next Step

The spine passes to parts specification as a single part with the following geometric summary:

- **Envelope:** 220mm (X, enclosure width) × ~40mm (Y, front-to-back depth) × ~60mm (Z, height)
- **Print orientation:** Front face down on build plate; 220mm along X
- **Paradigm:** 2.5D prismatic — all features are workplane-sketch-extrude operations on four faces (front, rear, left end, right end)
- **No sub-components. No assembly interfaces. No composition required.**

The parts.md file for the spine will enumerate all features from this inventory and provide final dimensions for each.
