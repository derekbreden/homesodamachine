# Pump Tray — Phase 1 Synthesis

**Season 1, Phase 1, Item 2**
**Scope:** Flat plate with 8 mounting holes for 2 Kamoer KPHM400 pumps. Nothing else.

---

## 1. Starting Shape

A flat rectangular plate. That is the geometry. No ribs, no bosses, no lips. A flat plate with holes.

The pump bracket face mates to the front face of this plate. Screws pass through the plate from the back and thread into the pump head. The motor body protrudes behind the plate. No bore is required in Phase 1 because the motor does not need to pass through the plate — it extends freely from the back face with no obstruction.

---

## 2. Hole Pattern

Each pump requires 4x M3 holes in a 50mm × 50mm square pattern, center-to-center. The pattern is caliper-verified from the physical pump (geometry-description.md, photo 05/06).

**Per pump:**
- 4x holes
- Pattern: 50mm × 50mm square, center-to-center
- Hole diameter: 3.3mm (nominal M3 = 3.0mm, +0.2mm for loose clearance fit per requirements.md)

**Two pumps total: 8 holes**

The two hole patterns are identical. They are separated by the pump-center-to-pump-center spacing (see Section 3).

---

## 3. Plate Outer Dimensions

### Width (X-axis, across both pumps)

The pump bracket is 68.6mm wide (caliper-verified, geometry-description.md). The outermost mounting hole centers are 25mm from the pump's center axis (50mm c-c / 2). This places the outermost hole centers 34.3mm from the bracket edge — 9.3mm of bracket material between hole center and bracket edge.

**Pump center-to-pump-center spacing: 68.6mm**

This is the minimum spacing at which the two pump brackets are flush against each other with no gap. The inner hole pair (25mm from each pump center, facing each other) falls at 25mm and 43.6mm from the left bracket edge, giving 18.6mm between the inner holes — no conflict.

**Plate width: 137.2mm**

Derivation: 2 × 68.6mm bracket width. The outermost hole centers sit 9.3mm from each plate edge. An M3 hole requires a minimum of ~4mm edge-to-center to maintain structural integrity; 9.3mm exceeds this. No additional margin is justified.

### Height (Z-axis, single pump height)

The pump head is 62.6mm square (caliper-verified). The mounting holes are in a 50mm square pattern, centered on the motor axis. This places hole centers 25mm from the motor axis in each direction. With the pump head at 62.6mm, the hole centers are 6.3mm from the pump head face edge. The bracket (68.6mm wide) matches the pump head height — the pump head height is also effectively 62.6mm, and the bracket overhangs ~3mm per side in the width direction.

**Plate height: 68.6mm**

Derivation: matches the bracket outer dimension (the largest feature at the mounting face). The outermost hole centers in the height axis sit (68.6mm - 50mm) / 2 = 9.3mm from the plate edge — same margin as the width direction.

### Thickness

**Plate thickness: 3.0mm**

Derivation: M3 screw threads need engagement. A standard M3 screw has 0.5mm pitch; 3mm of thickness provides 6 thread engagements minimum, which is adequate for the pump weight load (pump mass is negligible — the pumps are under 200g each and mount horizontally). The requirements.md minimum structural wall is 1.2mm (3 perimeters). 3.0mm (7–8 perimeters) is structurally conservative for this load and provides a non-trivial depth for the screw threads to engage. Below 3.0mm, thread engagement drops to fewer than 4 passes and risks pull-out under vibration.

No feature beyond flat geometry is justified. The plate does not deflect meaningfully under the static pump load.

---

## 4. Motor Cylinder Bore — Not Included in Phase 1

The motor body is 35.73mm in diameter (caliper-verified, geometry-description.md, photo 16) and protrudes behind the mounting bracket face.

**A bore is not included in Phase 1.**

Justification: The pump bracket face mates to the front face of the plate. The motor extends from the back face of the plate with no obstruction. A bore through the plate would only be needed if the motor were required to pass through the plate — which is not the case in this mounting geometry. The motor hangs freely behind the plate.

**Note for future phases:** If the cartridge geometry (Season 2) requires the pump assembly depth to be reduced by recessing the motor into or through the tray, a 37mm bore (35.73mm motor + 0.6mm radial clearance on radius, per requirements.md +0.2mm on diameter = 36.13mm minimum, rounded to 37mm for safety margin) would be added at that time with a geometric justification. That decision belongs to the Season 2 wall-to-interior-plate fit analysis, not Phase 1.

---

## 5. Hole Positions — Summary Table

Coordinate origin: bottom-left corner of plate front face.

**Pump 1 center axis: X = 34.3mm, Z = 34.3mm**

| Hole | X (mm) | Z (mm) |
|------|--------|--------|
| 1-A (top-left)     |  9.3 | 59.3 |
| 1-B (top-right)    | 59.3 | 59.3 |
| 1-C (bottom-right) | 59.3 |  9.3 |
| 1-D (bottom-left)  |  9.3 |  9.3 |

**Pump 2 center axis: X = 102.9mm, Z = 34.3mm**

| Hole | X (mm) | Z (mm) |
|------|--------|--------|
| 2-A (top-left)     |  77.9 | 59.3 |
| 2-B (top-right)    | 127.9 | 59.3 |
| 2-C (bottom-right) | 127.9 |  9.3 |
| 2-D (bottom-left)  |  77.9 |  9.3 |

All hole positions are ±0.1mm of the 50mm c-c datasheet value. Hole diameter: 3.3mm per hole (8 holes total).

---

## 6. Print Orientation

**Print flat — bottom face on the build plate.**

Justification: The plate is a flat panel with through-holes. Printing flat gives maximum XY dimensional accuracy for the hole positions, which are the critical features. Hole accuracy is highest when the holes are drilled through the Z-axis of the print (perpendicular to layer lines). The plate's through-holes are parallel to the Y-axis of the part but will be printed as Z-axis cylinders, giving the best roundness and dimensional accuracy.

No overhang concerns. No supports needed.

Layer lines run parallel to the plate face — bending loads (if any, from pump weight) act perpendicular to layer lines, but at 3.0mm thickness with negligible static pump load, this is not a failure mode.

---

## 7. Bill of Materials

| Item | Spec | Qty |
|------|------|-----|
| M3 screws | M3 × length TBD (must exceed plate thickness 3.0mm + bracket 1.5mm + engagement into pump head — recommend M3 × 10mm or M3 × 12mm pending measurement of pump head thread depth) | 8 |

**Note:** Screw length requires one additional measurement — the depth of the threaded hole in the pump head from the bracket face. This is not in the current datasheet. An M3 × 10mm screw is the tentative recommendation (3.0mm plate + 1.5mm bracket + ~5mm engagement), but confirm before ordering.

---

## 8. What Is NOT in Scope

The following features are explicitly excluded from Phase 1. Their absence is correct and intentional.

| Feature | Phase |
|---------|-------|
| Strut bores (4× holes for lever struts to pass through) | Phase 4 |
| Rail features (protruding tabs that slide into side wall channels) | Season 2 |
| Retention/joinery (detents, snap features, bosses locking the tray in place) | Season 3 |
| Tube clearance cutouts or pump-head envelope clearance features | Not yet justified |
| Motor bore | Not in Phase 1; conditionally Season 2 if depth budget requires it |

Do not add any of these features to the Phase 1 print. They will be designed when their dependencies (the parts they interface with) exist.

---

## 9. Conflicts and Open Questions

### Open Questions

1. **Screw length:** The threaded depth in the pump head (from bracket face) is not in the datasheet. Measure before ordering M3 screws. Tentative: M3 × 10mm. If pump head thread depth is less than 5mm, use M3 × 8mm.

2. **Pump orientation (rotational):** The pump bracket face has a 50mm square hole pattern. The pump head is nearly square (62.6mm). The two tube connectors exit from the pump head front face at offset positions. The pumps can be mounted in any of 4 rotational orientations (0°, 90°, 180°, 270°). Phase 1 does not require a specific orientation — the holes are symmetric. However, the final cartridge geometry (Season 2) will constrain tube routing and require a specific pump orientation. This decision should be documented before Season 2 begins, but it does not affect Phase 1.

3. **Pump spacing:** 68.6mm center-to-center (brackets flush) is the minimum. If the tube connectors on adjacent pump heads conflict in a flush arrangement, the spacing must increase. This is not verifiable without the tube connector positions (listed as unknown in the geometry datasheet). Phase 1 is unaffected — the tray can be reprinted in Season 2 if spacing needs adjustment.

### No Conflicts

There are no conflicts between the pump datasheet, requirements.md, and vision.md for this scope. The pump mounting pattern is simple and well-documented. The plate geometry is within the printer's build volume (137.2mm × 68.6mm × 3mm, well within the 325mm × 320mm × 320mm build envelope).

---

## 10. Summary

**Part:** Pump tray, Phase 1
**Geometry:** Flat rectangular plate, 137.2mm × 68.6mm × 3.0mm
**Features:** 8× M3 clearance holes (3.3mm diameter) in two 50mm × 50mm square patterns
**Material:** PLA or PETG (no structural requirement for exotic material at this phase)
**Print orientation:** Flat on build plate
**BOM:** 8× M3 screws (length TBD pending pump head thread depth measurement, tentative M3 × 10mm)
