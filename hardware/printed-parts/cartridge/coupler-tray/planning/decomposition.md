# Coupler Tray — Decomposition Decision

**Pipeline step:** 4d — Sub-Component Decomposition
**Input:** `hardware/printed-parts/cartridge/coupler-tray/planning/concept.md`

---

## Decision

This part is a single geometric paradigm. No decomposition needed.

---

## Rationale

The Phase 1 coupler tray is an 80mm × 50mm × 15mm rectangular plate with four stepped-bore pockets. Every feature in the part belongs to one paradigm: prismatic extrusion and cylindrical cuts.

- The plate body is a box extrusion.
- Each pocket is a two-diameter stepped bore — a revolved profile cut from one face to the other. The preferred CadQuery technique from `6-step-generation.md` (section 5, "Stepped bores with chamfers") handles this exactly: define the full axial cross-section as (R, Y) coordinate pairs and revolve once. Four pockets, four identical revolve-and-cut operations.
- The entry chamfer on the bottom face (elephant's foot mitigation) is a small additional point in each revolved profile — no separate operation required.

There are no sweeps, no lofts, no helical features, no separate rotational bodies, and no regions of the part with geometric independence from each other. The bore positions are interdependent with the plate body. The bore pattern drives the overall plate dimensions and pocket wall thicknesses.

A single CadQuery agent can model this part correctly using `box()` + `polyline().revolve()` × 4. This is one of the simplest problems the pipeline will encounter.

Decomposing this part would add a composition step where none is warranted, producing pipeline overhead with no geometric benefit.

---

## Pipeline routing

The coupler tray proceeds as a single unit through steps 4s → 4b → 5 → 6g. No composition step (6c) is needed.
