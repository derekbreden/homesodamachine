# Lever — Phase 1 Synthesis

**Season 1, Phase 1, Item 4**
**Scope:** Flat lever plate with 4 rectangular struts extending from its rear face. No dovetail or joint geometry at strut ends. No strut bores in interior plates (Phase 4). No front panel hole sizing (Season 2).

---

## 1. Starting Shape

A flat rectangular plate with four rectangular struts extending from its rear face. That is the geometry. No ribs, no bosses, no lips, no chamfers, no retention features. The plate is the pull surface — the user's fingers contact it through the rectangular hole in the front panel. The struts are pure rectangular prisms in Phase 1.

---

## 2. The Lever's Role in the Mechanism

The lever is one half of the squeeze mechanism. The user reaches through a rectangular hole in the front panel and curls their fingers up against the lever plate face. Their palm rests against the front panel face. Squeezing moves the lever plate rearward. The four struts transmit that motion through the pump tray and coupler tray to the release plate struts (joined in Phase 2), which in turn translate the release plate rearward, depressing the collets.

In Phase 1, the lever is printed and the geometry is confirmed against the interior plates. No force is transmitted yet — there is nothing to connect to at the strut ends. Phase 1 establishes the lever as a physical object with the correct plate size and strut positions.

---

## 3. Lever Plate Dimensions

### Width (X-axis)

The pump tray is 137.2mm wide. The lever plate will eventually be accessed through a hole in the front panel, which must be wide enough for comfortable finger access. The release plate (the part the lever ultimately drives) is approximately 80mm wide, centered within the cartridge. The lever plate must be at least as wide as the release plate to provide meaningful grip surface, but need not be as wide as the full pump tray.

**Lever plate width: 80mm**

Derivation: matches the release plate width (~80mm). The lever plate is centered on the cartridge width axis (X = 68.6mm from the pump tray left edge), so its left edge is at X = 28.6mm and right edge at X = 108.6mm within the cartridge coordinate system. This keeps the lever symmetrical with the release plate beneath it and with the strut pair positions derived in Section 5. No additional width is justified — a wider plate gives no mechanical benefit (force transmission is through the struts, not the plate perimeter) and would require a wider front panel hole.

### Height (Z-axis)

The release plate is approximately 65mm tall. The lever plate is the pull surface — it should span enough height for comfortable finger contact. The human finger pad spans approximately 15–20mm per finger; a two-finger grip (index and middle fingers typical for this pull posture) needs roughly 25–35mm of contact surface. The release plate height of 65mm provides ample spatial reference.

**Lever plate height: 50mm**

Derivation: 50mm provides a 40mm usable finger contact zone (the lower ~10mm is where the bottom struts attach and may be slightly less comfortable to grip, but this is not a Phase 1 concern — surface ergonomics are Season 4). 50mm is smaller than the release plate height (65mm), which is appropriate: the lever is a pull surface, not a structural plate. At 50mm, the plate is short enough to sit within the rectangular front panel hole without that hole being excessively tall, while being tall enough for multi-finger contact. No feature beyond a flat face is needed to achieve this.

### Thickness

**Lever plate thickness: 4.0mm**

Derivation: The plate must be rigid enough that it does not flex measurably when the user's fingers apply pull force during squeeze. The struts are attached at 4 points on the plate perimeter zone; if the plate is too thin, it bows in the center under finger load, which the user perceives as a mushy pull surface. At 4.0mm PETG with 4 strut attachment points, bending deflection at the plate center under a reasonable 30 N applied at the plate center is:

- Simplified as a simply-supported rectangular plate: δ = (F × L³) / (48 × E × I), where L is the span between strut pairs (≈30mm, the clear span in the Z-direction between the two strut rows), E for PETG ≈ 2,000 MPa (conservative), I = (b × h³) / 12 = (80mm × 4mm³) / 12 = 426.7 mm⁴
- δ ≈ (30 N × 30³ mm³) / (48 × 2000 N/mm² × 426.7 mm⁴) ≈ 0.063mm

0.063mm deflection under 30 N is imperceptible to the user. 4.0mm thickness satisfies the rigidity requirement with margin. Going thinner (3mm, the pump tray value) gives δ ≈ 0.15mm — still imperceptible, but 4mm is the better choice here because the plate is a user-contact surface and extra thickness gives a more solid feel. The plate is small (80mm × 50mm) and 4mm adds negligible print time or material. Any thickness below 3.0mm approaches the minimum structural wall requirement (1.2mm) too closely to be considered.

---

## 4. Strut Cross-Section

**Strut cross-section: 6mm × 6mm**

Derivation:

**Minimum size from force transmission:** The struts carry the entire lever pull force from the plate to the release plate junction (Phase 2). Peak force during squeeze is approximately 60 N (4 collets × 15 N each). Each of the 4 struts carries one-quarter of the load in compression: 15 N per strut. PETG compressive yield strength ≈ 50 MPa. Required cross-sectional area per strut: 15 N / 50 MPa = 0.3 mm². A 6mm × 6mm strut provides 36 mm² — 120× the minimum area. Compressive buckling (Euler column) at 6mm × 6mm cross-section and ~80mm length: critical load = π² × E × I / L² = π² × 2,000 N/mm² × (6⁴/12 mm⁴) / (80mm)² ≈ π² × 2,000 × 108 / 6,400 ≈ 333 N. This is 22× the design load. The struts will not buckle under any realistic squeeze force.

**Maximum size from pump tray clearance:** The pump tray holes are M3 clearance bores (3.3mm diameter). The holes themselves are not the constraint — the struts pass through bores that will be cut into the tray in Phase 4. The constraint is the distance between pump mounting holes and the zone where strut bores will be drilled. The minimum edge-to-edge distance from the proposed strut center to the nearest pump mounting hole center (see Section 5) is approximately 18mm. A strut bore for a 6mm × 6mm strut requires a 6.2mm × 6.2mm square bore (adding 0.2mm clearance per requirements.md). The bore center would sit at the strut center; the bore edge extends 3.1mm from center. With 18mm center-to-center to the nearest pump hole (radius 1.65mm), the edge-to-edge clearance between strut bore and pump hole is 18mm − 3.1mm − 1.65mm = 13.25mm. This is more than adequate.

**Minimum size from printability:** Requirements.md minimum structural wall is 1.2mm; minimum feature is 0.4mm. A 6mm × 6mm strut is 15 solid perimeters — no printability concern.

6mm × 6mm is the minimum square cross-section that is easily printable, easily measurable, provides enormous strength margin, and gives Phase 4 comfortable clearance for the bore geometry.

---

## 5. Strut Positions

The four strut positions must satisfy two constraints simultaneously:
1. Avoid the 8 pump mounting holes on the pump tray (3.3mm diameter bores at the positions documented in the pump tray synthesis)
2. Be compatible with the geometry of the release plate so that the Phase 2 joint design can connect lever struts to release plate struts

The lever is centered at X = 68.6mm, Z = 25.0mm (center of the lever plate, using the pump tray coordinate origin at the pump tray bottom-left corner). The lever plate spans X = 28.6mm to X = 108.6mm and Z = 0mm to Z = 50mm in the pump tray coordinate system.

**Strut positions are derived from the release plate bore geometry.**

The release plate (approximately 80mm wide × 65mm tall) carries its stepped bores at ±31mm horizontal and ±15mm vertical from plate center. The release plate is centered on the cartridge width axis — matching the lever plate center at X = 68.6mm. The release plate center in Z is independent of the lever, but the release plate's horizontal strut spacing (±31mm from its center = 62mm center-to-center) and the vertical strut spacing (±15mm from its center = 30mm center-to-center) establish the rectangle that the lever struts must match in X and Z.

**Strut centers (4 positions, using pump tray coordinate origin at bottom-left of pump tray):**

| Strut | X (mm) | Z (mm) | Label |
|-------|--------|--------|-------|
| Top-left     | 37.6 | 40.0 | TL |
| Top-right    | 99.6 | 40.0 | TR |
| Bottom-left  | 37.6 | 10.0 | BL |
| Bottom-right | 99.6 | 10.0 | BR |

**Derivation:**
- X positions: lever plate center X = 68.6mm, ±31mm → 37.6mm and 99.6mm. This matches the release plate bore horizontal spacing directly.
- Z positions: lever plate spans Z = 0 to Z = 50mm, center at Z = 25mm. Struts at Z = 25mm ± 15mm → Z = 10mm and Z = 40mm. This matches the release plate bore vertical spacing (30mm c-c). Struts sit 10mm from each horizontal edge of the lever plate, leaving 10mm of plate material at top and bottom — well above the 4mm structural wall minimum for strut-to-edge distance around a 6mm bore (requires 3.1mm from bore edge to plate edge minimum; 10mm − 3.1mm = 6.9mm margin).

**Clearance check against pump mounting holes:**

The pump mounting holes are at X = {9.3, 59.3, 77.9, 127.9} and Z = {9.3, 59.3}.

| Strut | Nearest pump hole | Center-to-center distance |
|-------|------------------|--------------------------|
| TL (37.6, 40.0) | (59.3, 59.3) | sqrt(21.7² + 19.3²) = 29.0mm |
| TL (37.6, 40.0) | (9.3, 59.3) | sqrt(28.3² + 19.3²) = 34.2mm |
| TR (99.6, 40.0) | (77.9, 59.3) | sqrt(21.7² + 19.3²) = 29.0mm |
| TR (99.6, 40.0) | (127.9, 59.3) | sqrt(28.3² + 19.3²) = 34.2mm |
| BL (37.6, 10.0) | (9.3, 9.3) | sqrt(28.3² + 0.7²) = 28.3mm |
| BL (37.6, 10.0) | (59.3, 9.3) | sqrt(21.7² + 0.7²) = 21.7mm |
| BR (99.6, 10.0) | (77.9, 9.3) | sqrt(21.7² + 0.7²) = 21.7mm |
| BR (99.6, 10.0) | (127.9, 9.3) | sqrt(28.3² + 0.7²) = 28.3mm |

Minimum center-to-center: 21.7mm (BL to hole at 59.3, 9.3; BR to hole at 77.9, 9.3).

With a 6mm × 6mm strut bore (3.1mm from center to bore edge) and a 3.3mm pump hole (1.65mm from center to hole edge), the minimum edge-to-edge clearance is 21.7mm − 3.1mm − 1.65mm = **17.0mm**. No interference. All four strut positions are clear of all pump mounting holes.

---

## 6. Strut Length

The struts must extend from the lever plate rear face rearward far enough to:
1. Pass through the pump tray (3.0mm thick) when strut bores are added in Phase 4
2. Pass through the coupler tray (estimated ~4.0mm thick, similar to pump tray)
3. Reach a zone where Phase 2 can design the dovetail/snap joint connecting lever struts to release plate struts

**Estimating the required strut length:**

The cartridge interior arrangement, front to back:
- Front panel (thickness TBD, ~3–5mm) — not in scope
- Gap between front panel rear face and lever plate front face: ~5mm (the lever rides on the struts; some clearance forward of the pump tray is needed for lever travel)
- Lever plate thickness: 4mm
- Lever pull travel: 3mm (matching release plate travel per the release plate synthesis — the lever and release plate move the same distance when the struts are rigidly joined in Phase 2)
- Pump tray: 3mm thick, at some position behind the lever
- Gap between pump tray and coupler tray: nominally 10–20mm (uncertain; the pumps are ~116mm deep and mount to the pump tray rear face, but the coupler tray sits at the cartridge rear zone and is a separate structural element — the gap between the two interior plates spans most of the cartridge interior depth)
- Coupler tray: ~4mm thick
- Gap between coupler tray and release plate: ~5–15mm (the release plate sits close to the rear wall; the coupler tray is somewhere in the mid-to-rear zone)

The release plate synthesis establishes that the cartridge interior depth must be at least ~50mm for the front zone (release plate + pin bores + fitting depth). The pumps are ~116mm deep. The total cartridge interior depth is therefore driven by the pump depth — likely 120–130mm. In a 120mm deep cartridge interior, the interior plate positions are approximately:

- Pump tray: near the front (the pumps mount to the rear face of the pump tray, extending rearward — to accommodate the 116mm motor body, the pump tray is positioned with its front face very close to the front panel, perhaps 10–15mm from the front panel rear face)
- Coupler tray: near the rear, approximately 5–15mm forward of the release plate/rear wall zone

A reasonable estimate: pump tray front face ≈ 12mm behind front panel rear face. Coupler tray sits approximately 90–100mm behind the pump tray front face (to give the 116mm pump body clearance past the pump tray rear face: pump tray rear face is 15mm in from front panel; pump body extends 116mm rearward to about 131mm from front panel; coupler tray would be positioned after the pump extent at roughly 130–140mm from front panel in a 150mm deep interior — but this is a rough estimate only).

**Working estimate for strut length: 90mm**

Derivation: The struts start at the lever plate rear face. The lever is positioned close to the front panel. The struts must reach past the pump tray (3mm) and coupler tray (est. 4mm) and extend into the mid-cartridge zone where Phase 2 will join them to the release plate struts. The release plate struts (extending from the release plate front face toward the user) will span some distance forward. The joint must occur somewhere between the coupler tray rear face and the release plate front face.

If the release plate front face is approximately 50–70mm from the front panel rear face (from the release plate synthesis: pin length 30mm forward from plate front face, but pins go rearward — so the release plate is positioned in the rear zone), the zone where the lever struts must terminate is approximately 70–90mm behind the lever plate rear face.

90mm is the estimate: it clears both interior plates by a large margin (pump tray at ~12mm, coupler tray at ~95–100mm — the 90mm strut from the lever plate rear face, positioned 12mm behind the front panel, would reach to ~102mm from the front panel, which is in the vicinity of the coupler tray). If the coupler tray is at ~100mm from the front panel and the lever is at ~15mm from the front panel, the strut length needed to reach the coupler tray rear face is approximately 100mm − 15mm − 4mm (lever plate) = 81mm. Adding 10mm beyond the coupler tray to give Phase 2 working space for the joint geometry: 91mm, rounded to **90mm**.

**This is an estimated dimension, not a verified one.** The strut length is the single open question for Phase 1 (see Section 9). Once the coupler tray synthesis establishes its position in the cartridge and the cartridge body depth is confirmed, the strut length may need adjustment. 90mm is the value to use for the Phase 1 print; the strut ends will protrude into the mid-cartridge interior with no functional consequence in Phase 1 since nothing connects to them yet.

---

## 7. Print Orientation

**Print with the lever plate face on the build plate (face-down).**

The lever plate face is the user contact surface and will benefit from the smoothest possible finish, achieved by printing directly on the build plate rather than on support. The struts extend upward (in the +Z print direction) from the plate rear face. At 6mm × 6mm cross-section and 90mm length, the struts are well within the unsupported span limit for columns — no bridging concern. No overhangs. No supports needed.

Print axis alignment: struts are vertical (Z), lever plate is horizontal (XY). The 80mm × 50mm plate fits easily within the 325mm × 320mm single-nozzle build area.

Layer lines run parallel to the lever plate face. The struts' 90mm length is along the Z-axis, so layer lines stack along the strut length. Force on the struts during squeeze is compressive along this same axis — compressive loads along the layer axis are strong in FDM (layers are in compression, not tension). This is the correct orientation.

---

## 8. Bill of Materials

This is a single printed part. No off-the-shelf components.

| Item | Spec | Qty |
|------|------|-----|
| Printed lever | PETG, 80mm × 50mm × 4mm plate + 4× 6mm × 6mm × 90mm struts | 1 |

**Material note:** PETG is preferred over PLA for mechanism parts that will see repeated use. The lever will be squeezed repeatedly over the cartridge lifetime; PETG's higher toughness (elongation at break ~100% vs. PLA ~6%) makes it more resistant to crack propagation if the strut-to-plate junction sees any bending from misaligned finger force.

---

## 9. Open Questions

1. **Strut length needs verification.** 90mm is derived from an estimated cartridge interior depth. The correct value depends on: (a) the coupler tray synthesis establishing that tray's position in the cartridge depth axis, and (b) the cartridge body synthesis confirming total interior depth. The strut length should be revisited and corrected before Phase 2 begins. For Phase 1, 90mm is the print value — the plain strut ends have no functional consequence at excess length.

2. **Lever plate Z-position within the cartridge.** The lever is assumed to be positioned such that its front face is inset ~5–10mm behind the front panel face (inside the pocket described in the release plate synthesis). The exact Z-position (how far the lever front face is inset from the front panel face) depends on the front panel pocket geometry, which is a Season 2 item. Phase 1 is unaffected — the lever is a free-standing part in Phase 1.

3. **Strut attachment to lever plate — print-as-one assumption.** The struts and plate are assumed to be a single printed part (no assembly). This is the simplest geometry. If the strut length (90mm) plus plate thickness (4mm) = 94mm total height causes difficulty with print orientation or build plate adhesion, the struts could be designed as separate press-fit pins into the plate. For Phase 1, print-as-one is the assumption.

4. **Release plate strut positions for Phase 2 compatibility.** The release plate synthesis (current version, Phase 1) describes the plate with 2 guide pins, not 4 struts. Phase 2 updates the release plate to 4 struts (Step 5 in the build sequence). The lever strut positions chosen here (37.6, 10.0), (37.6, 40.0), (99.6, 10.0), (99.6, 40.0) in pump tray coordinates are derived from the release plate bore positions (±31mm horizontal, ±15mm vertical from cartridge centerline). This derivation assumes the release plate struts in Phase 2 will emerge from positions matching or very near the bore positions. If Phase 2 places the release plate struts at different positions (e.g., outside the bore pattern rather than coincident with it), the lever strut positions will need to change and the Phase 1 lever will need to be reprinted. This is an acceptable risk — the Phase 1 lever is a low-cost single print.

---

## 10. What Is NOT in Scope

The following features are explicitly excluded from Phase 1. Their absence is correct and intentional.

| Feature | Phase |
|---------|-------|
| Dovetail or joint geometry at strut ends | Phase 2 |
| Strut bores in pump tray | Phase 4 |
| Strut bores in coupler tray | Phase 4 |
| Front panel hole geometry | Season 2 |
| Lever pull travel stop (limits rearward motion) | Season 2 or Phase 2 |
| Spring pockets or return spring features | Season 4, Phase 12 |
| Surface texture on lever plate face | Season 4, Phase 11 |
| Cartridge walls or enclosure | Season 2 |

---

## 11. Summary

**Part:** Lever, Phase 1
**Geometry:** Flat rectangular plate, 80mm × 50mm × 4mm, with 4 rectangular struts (6mm × 6mm × 90mm) extending from the rear face
**Strut positions (pump tray coordinate origin):** (37.6, 10.0), (37.6, 40.0), (99.6, 10.0), (99.6, 40.0)
**Material:** PETG
**Print orientation:** Lever plate face-down on build plate, struts extending upward
**BOM:** 1× printed PETG part, no hardware
