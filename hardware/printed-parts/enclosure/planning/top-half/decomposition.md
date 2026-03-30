# Enclosure Top Half — Geometric Decomposition

**Date:** 2026-03-29
**Input:** concept.md, synthesis.md, bottom-half/parts.md (interface reference)
**Next step:** spatial-resolution.md

---

## Geometric Paradigm

**Single paradigm: linear extrude-and-cut.** All features are boxes, cylinders, or prisms added to or subtracted from a rectangular shell. No swept profiles, no lofts, no shell operations.

Build sequence:
1. Start with a solid box (220×300×215.5mm, Z:[184.5, 400])
2. Add exterior protrusions (none — top half has no upward protrusions at seam level; the seam lip is integral to the box)
3. Cut interior cavity (open seam face at Z=185)
4. Add interior features: cradle ledges, spine slot bosses, electronics rail ledges
5. Cut seam interface features: groove, snap ledge pockets, alignment pin sockets
6. Cut rear wall port holes, add boss rings
7. Cut exterior bay recesses on rear wall
8. Apply fillets/chamfers

All features satisfy the extrude-and-cut paradigm. No feature requires a spatial paradigm change.

## Feature Count

17 features — same count as bottom half by design (matching complexity).
