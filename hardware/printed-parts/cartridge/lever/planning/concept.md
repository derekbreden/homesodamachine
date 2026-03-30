# Lever — Conceptual Architecture

**Step:** 4a — Conceptual Architecture
**Input:** synthesis.md (execution plan), hardware/requirements.md, hardware/vision.md, release-plate/planning/concept.md
**Scope:** Season 1, Phase 1, Item 4 — flat plate with 4 rectangular struts extending from rear face. No joint geometry at strut ends.

---

## What This Design Is

A single printed PETG part: a flat rectangular plate (80mm × 50mm × 4mm) with four rectangular struts (6mm × 6mm × 90mm) extending perpendicular from its rear face. The plate face is the user's pull surface. The struts are plain rectangular prisms that will eventually pass through bores in the pump tray and coupler tray to reach the release plate struts — but in Phase 1, their ends are free. The part prints in one piece, plate face down, struts pointing up. No hardware, no assembly, no joints.

---

## 1. Piece Count and Split Strategy

**One printed part. No splits.**

The lever is the simplest geometry in the build sequence: a flat plate with four rectangular extrusions. There is no geometric complexity that motivates splitting it into multiple pieces. No feature requires access from two directions during printing. No feature requires capturing a hardware insert. The plate and struts can be printed as one unit in the correct print orientation with zero overhangs and zero supports.

The synthesis raises one conditional: if 94mm total height (4mm plate + 90mm struts) causes build-plate adhesion problems, the struts could be designed as separate press-fit pins. This is not a Phase 1 concern — 94mm is well within the 320mm build height, and a 80mm × 50mm footprint provides excellent bed adhesion for an 80×50mm slab. The press-fit variant would add assembly, tolerance stack at the strut/plate interface, and risk of strut pull-out under load. Print-as-one is correct.

---

## 2. Join Methods

**Phase 1: nothing connects. The lever is a free-standing part.**

The lever is designed to connect to the rest of the mechanism via two paths:

**Path 1 — Strut-to-release-plate joints (Phase 2):** The four strut ends will be joined to the release plate struts via tapered dovetail + snap detent geometry. In Phase 1, the strut ends are plain rectangular prisms — no joint geometry exists. The struts extend into free space. Phase 1 establishes the correct plate geometry and strut positions; the joints are Step 6 in the build sequence.

**Path 2 — Strut-through-interior-plates (Phase 4):** The struts will eventually pass through square bores in the pump tray and coupler tray, which align and guide the lever during the squeeze stroke. In Phase 1, those bores do not exist. The interior plates have no strut bores yet — they are Phase 4 work.

In Phase 1, the lever has no joints, no fasteners, no connections to anything. It is evaluated as a physical object: correct plate size, correct strut positions, correct strut cross-section. Nothing more is expected of it.

---

## 3. Seam Placement

**No external seams. The lever is an interior part.**

The lever never reaches the cartridge exterior. It sits behind the front panel face at all times. The front panel has a rectangular hole through which the user's fingers reach the lever plate face — but the lever plate itself is inset behind the front panel, not flush with it. The lever is not visible in normal use; its front face is at the bottom of the pocket formed by the front panel hole depth.

There is no seam to treat on the lever because it is a one-piece part. The only edge of interest is the plate's front face perimeter — the edge where the user's finger pads bear during the pull stroke. That edge treatment is a Season 4 surface refinement, not a Phase 1 concern.

---

## 4. User-Facing Surface Composition

**The front face of the lever plate is the pull surface — the only surface the user contacts.**

The user reaches through the rectangular hole in the front panel and curls their fingers upward against this face. The surface the user actually touches is approximately 80mm wide × 50mm tall, flat, PETG, printed face-down on the build plate. In Phase 1, it is printed as-is with no texture treatment.

What the user does NOT see or touch in any phase:
- The struts (they are behind the plate, extending rearward into the cartridge interior)
- The strut ends (deep inside the cartridge, inaccessible without disassembly)
- The plate rear face (faces rearward, away from the user)

The lever plate face is the deepest surface the user touches during the squeeze — their fingers reach past the front panel face and into the cartridge interior. The front panel surrounding the hole is the palm surface (their palm presses forward against the front panel while fingers curl to pull the lever). The lever plate face is at a depth set by the interior plate arrangement; that depth is not specified until the walls and front panel exist (Season 2).

---

## 5. Design Language

**Consistent with the release plate: PETG, flat print, clean edges.**

The lever and the release plate are the two hand-contact surfaces in the squeeze mechanism. They should be coherent:

- **Material:** PETG, matching the release plate. PETG's slight natural satin sheen is appropriate for a finger-contact surface. The same material language as the release plate pull surface.
- **Print orientation:** Lever plate face down, same as the release plate's front face down. Both surfaces get the smoothest achievable FDM finish (build plate contact surface) as their user-facing face.
- **Corner treatment:** The plate perimeter corners are rounded at 2–3mm in the XY plane, consistent with the release plate's corner language. This prevents sharp corners from reading as raw rectangular stock and keeps the lever visually consistent with the release plate it will eventually drive.
- **Surface finish:** As-printed in Phase 1. Season 4 Phase 11 is the point where surface texture on the pull face is addressed (currently listed as smooth or very lightly textured, matching the release plate pull surface intent — the finger pads need to slide slightly as they flex, so a heavily textured surface would be counterproductive).
- **No features for show:** No embossed text, no indicator lines, no decorative geometry. The lever is a mechanism part. Its design language is clean geometry and material quality.

The lever's pull surface is smaller than the release plate's pull surface (50mm tall vs. 65mm tall, 80mm wide for both). The lever is the user's pull surface; the release plate is a hidden mechanism part. The lever need not match the release plate in size — it only needs to match it in design language.

---

## 6. Service Access Strategy

**None required in Phase 1. None required in any phase.**

The lever is a captive interior part. It is not user-serviceable. The vision describes the cartridge as a "black box" from the user's perspective — the lever is one of the components inside that box. When the user replaces the cartridge, they replace the lever along with everything else inside. There is no scenario in which the user needs to access, remove, or replace the lever independently.

The lever has no access holes, no deliberate break features, no user-facing retention tabs, and no service markings. The struts pass through bores in the interior plates (Phase 4) — those bores constrain the lever to translate along the correct axis and prevent it from being removed without disassembling the cartridge. This is the correct behavior.

---

## 7. Manufacturing Constraints

### Print orientation

**Lever plate face down on the build plate. Struts extend upward (+Z).**

This is the correct and only orientation:

- The lever plate front face is the user contact surface. Printing it face-down on the build plate gives it the smoothest achievable FDM surface finish — the same logic that drives the release plate to print front-face-down.
- The struts extend straight up from the plate rear face. At 6mm × 6mm cross-section and 90mm length, they are solid rectangular columns — no overhang, no bridging, no support needed.
- All four struts are vertical in the print orientation: layers stack along the strut length. The compressive load on the struts during squeeze acts along the strut length (Z print axis). Compressive loads along the layer axis are strong in FDM — layers in compression, not tension. This is the mechanically correct orientation.
- Total build height: 4mm (plate) + 90mm (struts) = 94mm. Well within the 320mm build height.
- Footprint: 80mm × 50mm (plate base). Fits the 325mm × 320mm single-nozzle build area with margin.

### Overhang analysis

**No overhangs. No supports required.**

- The lever plate is a flat horizontal slab. Bottom face (front face) is on the build plate. Top face (rear face) is fully supported by the plate body.
- The struts are vertical rectangular columns. Each strut face is vertical (parallel to the Z axis) — no overhang on any strut face.
- The strut-to-plate junction: the struts emerge from the plate rear face (the top of the slab in print orientation). Each strut's base is fully supported by the plate material below it. The junction is a simple right-angle transition from horizontal plate to vertical strut — no cantilever, no ledge, no overhang.
- The 2–3mm perimeter corner radii on the plate (XY plane) are in-plane curves — no overhang implication.

No unsupported feature angle below 45° from horizontal exists anywhere in this geometry.

### Wall thickness

All critical wall thicknesses are well above the 1.2mm minimum structural wall requirement:

| Feature | Dimension | Minimum required |
|---------|-----------|------------------|
| Lever plate thickness | 4.0mm | 1.2mm |
| Strut wall (solid cross-section, no hollow) | 6mm solid | 1.2mm |
| Plate material at plate edge to strut edge | 10mm from strut center to plate edge = 6.9mm from strut bore edge to plate perimeter | 1.2mm |

The struts are solid rectangular prisms — there are no thin walls within the strut cross-section.

### Strut orientation for strength

The synthesis establishes that compressive load per strut during squeeze is approximately 15 N (60 N total / 4 struts). The struts' critical axis for strength is along their length — the load is compressive along the strut long axis, which in the print orientation is the Z axis. FDM layer stacking runs parallel to this load. Compressive loads along the layer axis are the strong case in FDM. The Euler buckling critical load at this cross-section and length is approximately 333 N — 22× design load. No structural concern.

The weak axis of FDM parts is tensile or bending load across layer lines. The struts will not experience significant bending in Phase 1 (nothing is connected to the strut ends). In Phase 2 and later, when the struts carry the full squeeze load through the joint to the release plate, any small lateral bending from misalignment will be resisted by material in-plane (XY), which is the strong direction for that load case.

### Elephant's foot

The 80mm × 50mm plate base is a flat perimeter edge printed on the build plate. Per requirements.md, the first 0.2–0.3mm of the part may flare outward from bed adhesion. A 0.3mm × 45° chamfer on the bottom perimeter edge of the plate prevents elephant's foot from affecting the critical front face edge geometry. This chamfer is small enough to be imperceptible in normal use and is required for dimensional accuracy on the pull surface perimeter.

### Build plate adhesion note

The 80mm × 50mm plate footprint provides a good adhesion surface for PETG. The four 6mm × 6mm struts rising 90mm above the plate create a top-heavy structure with a center of mass well above the base. In practice this is not a concern — the plate base is large relative to the strut footprint, and PETG adheres reliably at this scale on a textured PEI plate. No brim required.

---

## Summary

**What the design is:**

One printed PETG part. Flat rectangular plate (80mm × 50mm × 4mm) with four rectangular struts (6mm × 6mm × 90mm) extending from the rear face. Strut positions: TL (37.6, 40.0), TR (99.6, 40.0), BL (37.6, 10.0), BR (99.6, 10.0) in pump tray coordinates. Printed face-down, struts up. No hardware. No assembly. No joints in Phase 1.

**Key decisions:**
1. One piece — no split, no press-fit struts. Simplest geometry that works.
2. Phase 1 join method is none — the part is free-standing. All joints are future phases.
3. No external seam — the lever is fully interior. The only edge of note is the plate front face perimeter, treated in Season 4.
4. Pull surface is the plate front face — flat, PETG, build-plate-contact finish. Same design language as the release plate pull surface.
5. Print orientation is face-down with struts vertical — zero overhangs, correct load axis for FDM layer strength, best surface finish on the pull face.
6. No service access features — the lever is captive and non-user-serviceable by design.

**Open questions carried from synthesis (no new conflicts found):**
- Strut length (90mm) is an estimate pending coupler tray and cartridge body depth confirmation. The value is acceptable for Phase 1; excess strut length past the intended joint zone has no Phase 1 consequence.
- Lever Z-position within the cartridge is not finalized until Season 2 front panel and wall geometry exists. Phase 1 is unaffected.
