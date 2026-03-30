# Enclosure Bottom Half — Decomposition Decision

**Date:** 2026-03-29
**Input:** hardware/printed-parts/enclosure/planning/concept.md
**Decision:** Pass through — no decomposition needed

---

## Decision

This part is a single geometric paradigm. No decomposition needed.

---

## Rationale

Every feature of the enclosure bottom half belongs to the same geometric paradigm: **extrude-and-cut** (prismatic/2.5D). The complete feature inventory confirms this:

| Feature | Operation | CadQuery technique |
|---|---|---|
| Box body — 5 walls + floor | Add | `box()` then `shell()`, or explicit wall extrusions |
| Exterior 3 mm vertical edge fillets | Modify | `fillet()` on selected edges |
| Front-face RP2040 circular cutout (33 mm) | Remove | Cylinder cut through vertical wall |
| Front-face RP2040 retention pocket (bayonet ring geometry) | Remove | Cylinder cut + rotated slot cuts |
| Front-face S3 square cutout (48.2 mm) | Remove | Box cut through vertical wall |
| Front-face S3 33.1 mm deep pocket | Remove | Box cut, same wall, shallower depth |
| Front-face KRAUS circular through-hole (31.75 mm) | Remove | Cylinder cut through vertical wall |
| Dock opening in lower front face | Remove | Box cut through vertical wall |
| 24 cantilever snap arms on top seam edge | Add | Extrusion of hook profile from top edge, frangible support tabs |
| Continuous tongue on top seam face | Add | Perimeter extrusion from top face |
| 4 corner alignment pins on top seam face | Add | Cylinder extrusions from top face |
| 4 printed integral feet on bottom exterior | Add | Cylinder (or small box) extrusions from bottom face |
| Snap pockets in interior floor (dock cradle) | Remove | Box cuts into floor from above |
| Internal dividing wall at ~175 mm from front | Add | Box extrusion from floor |
| Seam edge 0.5 mm reveal geometry | Add/Modify | Exterior wall profile shaping |
| 0.3 mm × 45° elephant's foot chamfer on bottom perimeter | Modify | `chamfer()` on bottom perimeter edge |
| 0.5 mm × 45° chamfers on front-face cutout edges | Modify | `chamfer()` on cutout perimeter edges |
| 2 mm × 45° chamfer on dock opening perimeter | Modify | `chamfer()` on dock opening edge |

No feature in this list requires a helical sweep, a loft, a revolve of a complex profile, or any technique outside CadQuery's standard `box / cylinder / extrude / cut / fillet / chamfer` vocabulary. The snap arms are prismatic cantilever extrusions — not revolves, not sweeps. The tongue is a linear perimeter extrusion. The retention geometry behind the RP2040 cutout is the most locally complex feature (bayonet slot cuts behind the front face), but it reduces to cylinder cuts and short rotational slot pockets — all 2.5D operations on a single workplane.

### Why the total complexity does not force decomposition

The concern that a 220 × 300 × 185 mm shell with many features might overwhelm a single agent is valid, but the features are architecturally simple. The CadQuery generation agent for this part will encounter:

- One large box shell (straightforward)
- Three cutouts in one face (each a single cut operation)
- One large rectangular opening in one face (one cut)
- 24 snap arms (24 repetitions of one identical extrusion — a loop)
- One perimeter tongue (one extrusion along the top perimeter)
- Four pins (four cylinder extrusions)
- Four feet (four cylinder or small box extrusions)
- A handful of chamfer and fillet passes at the end

The repetitive character of the snap arms and alignment features is handled by a loop, not by geometric complexity. The S3 pocket is a two-step cut (full-depth box cut for the 48.2 mm through-hole, then a second shallower cut for the 33.1 mm deep pocket recess) — two standard box cuts.

**Decomposition would create a composition boundary problem with no geometric payoff.** Any split of this shell — for example, separating the snap arm array from the box body, or separating the front-face panel from the shell — would require the composition agent to boolean-union two large overlapping solids and apply interface treatments that serve no purpose the single-agent script would not handle in the same number of lines. The boundary between any hypothetical sub-components is not a natural geometric boundary; it is an arbitrary cut through an interdependent shell.

All cutouts, all snap arms, all tongue geometry, and all foot geometry depend on the box body's wall positions and dimensions. They are not independent regions — the snap arm root is flush with the top wall interior; the cutout positions are offsets from the corner edges; the feet are at corner-referenced positions on the floor. Separating any of these from the box body would require passing the box body's dimensions into the sub-component — at which point the sub-component is not genuinely independent.

---

## Pipeline routing

This part routes through the standard single-part pipeline with no fan-out:

```
4d (this document — pass through)
  │
  └── 4s (spatial resolution) → 4b (parts.md) → 5 (engineering drawing) → 6g (CadQuery generation)
```

No composition step (6c) is needed.

---

## Notes for downstream steps

The parts specification agent (4b) should be aware that the two most feature-dense zones of this part are:

1. **The top seam edge:** tongue, 24 snap arms, 4 alignment pins, and the 0.5 mm reveal step all originate from the same top perimeter. The CadQuery generation agent will need a clear statement of the order these features are built relative to each other (wall body first, tongue extrusion second, snap arm extrusions third, pin extrusions fourth, then chamfer/fillet passes last). The specification should flag this ordering requirement.

2. **The front-face component panel (107–185 mm from bottom):** three distinct cutout profiles in close lateral proximity (RP2040 at 55 mm from left, S3 at 110 mm from left, KRAUS at 165 mm from left) with different diameters, depths, and retention geometries. The specification should call out the component cutout positions and depths explicitly and in one consolidated section so the generation agent can lay them in without hunting across the document.

The RP2040 retention ring geometry (Gap 3 from the concept document — integral bayonet ring vs. separate part) must be resolved in the specification before the CadQuery agent begins. If integral, the generation agent needs the bayonet slot profile. If a separate part, the bottom half's contribution is simply the 33 mm through-hole with a 0.5 mm × 45° chamfer, and the retention ring is a separate part with its own pipeline entry. This decomposition document does not resolve Gap 3 — it flags it as a prerequisite for 4b.
