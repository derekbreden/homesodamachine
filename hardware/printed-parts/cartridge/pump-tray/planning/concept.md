# Pump Tray — Phase 1 Concept

**Season 1, Phase 1, Item 2**
**Scope:** Flat plate with 8 mounting holes for 2 Kamoer KPHM400 pumps. Nothing else.

---

## What This Part Is

A flat rectangular plate, 137.2mm × 68.6mm × 3.0mm, with 8× M3 clearance holes (3.3mm diameter) arranged in two 50mm × 50mm square patterns. Each pattern mounts one Kamoer KPHM400 pump via 4 M3 screws through the metal mounting bracket. The motor body extends freely from the back face of the plate with no obstruction. This is the complete Phase 1 deliverable.

---

## 1. Piece Count and Split Strategy

**One piece.**

There is no geometric or assembly reason to split a flat plate. The plate has no features that require access from inside a closed form, no joint geometry, and no internal cavity. It prints as a single part. No split strategy applies.

---

## 2. Join Methods

**Not applicable.** This is a single flat plate. There are no joints between printed parts in this phase.

The only fasteners in scope are the 8× M3 screws that attach the pumps to the plate. Those are off-the-shelf hardware, not printed joints.

---

## 3. Seam Placement

**Not applicable.** A single flat plate has no seams.

---

## 4. User-Facing Surface Composition

The user never sees or touches this part. It is an interior plate inside the pump cartridge, inaccessible during normal use and during cartridge replacement. The user interacts with the cartridge as a black box — they see the front panel and side walls, not the interior plates.

The design standard for interior parts applies: simplest geometry that works. There are no cosmetic requirements on any surface of this plate. Both faces, all edges, and all holes are purely functional.

---

## 5. Design Language

This is an interior structural part. No design language requirements apply. Surface finish is whatever the printer produces at standard settings. Corner treatment is whatever results from the flat plate geometry — no radii, chamfers, or surface details are required or warranted in Phase 1.

If a future phase requires this part to be visible (it will not), cosmetic treatment would be addressed at that time.

---

## 6. Service Access Strategy

The user never accesses this part directly. The pump cartridge is a user-replaceable assembly, but the interior plates — including the pump tray — are not individually serviceable. When the pumps wear out, the user replaces the entire cartridge. The pump tray stays inside the cartridge for its service life.

No service access features are required on this part.

---

## 7. Manufacturing Constraints

**Build volume:** 137.2mm × 68.6mm × 3.0mm. The printer build volume (single nozzle) is 325mm × 320mm × 320mm. The part fits with large margin in all axes.

**Print orientation:** Flat on the build plate — the 137.2mm × 68.6mm face down, 3.0mm in the Z-axis. This orientation gives maximum XY dimensional accuracy for the hole pattern, which is the only critical feature. Holes print as Z-axis cylinders, giving the best roundness and positional accuracy.

**Overhang:** None. A flat plate with through-holes printed in this orientation has no overhangs. No supports required.

**Minimum wall thickness:** The plate is 3.0mm thick — 7–8 perimeters at 0.4mm nozzle. Well above the 1.2mm structural wall minimum in requirements.md.

**Hole sizing:** Holes are 3.3mm diameter (nominal M3 = 3.0mm + 0.2mm loose clearance per requirements.md). No elephant's foot correction is needed on the hole entrances — the holes are interior features not at the base perimeter. The bottom edge chamfer per requirements.md (0.3mm × 45°) applies to the plate's bottom perimeter if the bottom face is a mating surface; in Phase 1 this is not a mating surface, so this is not required.

**Material:** PLA or PETG. No structural, thermal, or chemical requirement at this phase justifies a more demanding material. Either is acceptable.

**Layer orientation and load:** Layer lines run parallel to the plate face. Any pump weight load acts perpendicular to layer lines (bending across layers). At 3.0mm thickness under negligible static pump weight (under 200g per pump), this is not a failure mode.

---

## Summary

| Property | Value |
|----------|-------|
| Piece count | 1 |
| Outer dimensions | 137.2mm × 68.6mm × 3.0mm |
| Holes | 8× 3.3mm diameter, two 50mm × 50mm square patterns |
| Print orientation | Flat on build plate |
| Supports required | None |
| Material | PLA or PETG |
| User-facing | No |
| Cosmetic requirements | None |
| Features beyond flat plate + holes | None |
