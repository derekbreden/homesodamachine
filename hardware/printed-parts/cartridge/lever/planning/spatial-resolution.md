# Lever — Spatial Resolution

**Step:** 4s — Spatial Resolution
**Input:** synthesis.md, concept.md, decomposition.md (pass-through), pump-tray/synthesis.md, release-plate/synthesis.md
**Scope:** Season 1, Phase 1, Item 4 — single part, no decomposition

---

## 1. System-Level Placement

The lever is a front-zone interior part. It sits directly behind the front panel of the cartridge, facing the user's fingers through the rectangular hole in the front panel.

**Position relative to the front panel:** The lever's front face (the pull surface) is inset behind the front panel's rear face. The inset depth is not yet finalized (it depends on the front panel pocket geometry, which is Season 2). For spatial purposes, the lever front face is located somewhere in the range of 5–15mm rearward of the front panel rear face. This range does not affect the lever's own geometry — it is a free-standing part in Phase 1.

**Position relative to the pump tray:** The lever is coplanar with the pump tray in X and Z (they share the same cartridge width and height axes). The lever plate spans a 80mm × 50mm sub-region of the pump tray's 137.2mm × 68.6mm face. The lever is forward of the pump tray (the lever is between the front panel and the pump tray front face). The gap between the lever plate rear face and the pump tray front face includes the lever pull travel (3mm) plus any clearance margin — nominally 5–8mm total, not yet finalized.

**Position relative to the rear wall:** The lever is at the front end of the cartridge interior. The rear wall is the fixed structural anchor for the quick-connect fittings and release plate guide pin bores. The lever is approximately 90mm forward of the release plate front face at rest (estimated from strut length), plus the release plate thickness (5mm) and the depth from the release plate to the rear wall (~36.5mm minimum per release plate synthesis). The lever is not constrained by the rear wall directly.

**Orientation:** The lever is installed with its front face perpendicular to the cartridge front-to-back axis (Y axis), parallel to the front panel. The struts extend rearward (toward the rear wall) along the Y axis. No rotation about any axis relative to the cartridge.

```
Mechanism: Lever (Phase 1)
Parent:    Cartridge interior, front zone
Position:  Centered on cartridge width axis; front face ~5–15mm rearward of front panel rear face
           Centered at X = 68.6mm, Z = 25.0mm in pump tray coordinate frame
Orientation: No rotation — lever plate face perpendicular to cartridge depth axis
```

---

## 2. Part Reference Frame

The lever's local coordinate system is defined with the origin at the **bottom-left corner of the lever plate's front face**. This is the corner that, in the installed position, is at the bottom-left as seen by the user reaching through the front panel hole.

```
Part:   Lever, Phase 1
Origin: Bottom-left corner of lever plate front face

X:  Width axis — positive rightward as seen from front face
    Range: 0mm (left edge) to 80mm (right edge)
    Plate center: X = 40.0mm

Y:  Depth axis — positive rearward (into the cartridge)
    Y = 0:   Lever plate front face (pull surface — user contact)
    Y = 4:   Lever plate rear face (struts begin here)
    Y = 94:  Strut tips (4mm plate + 90mm strut length)

Z:  Height axis — positive upward
    Range: 0mm (bottom edge) to 50mm (top edge)
    Plate center: Z = 25.0mm

Print orientation:
    Lever plate front face on build plate (Y = 0 face down)
    Struts extend upward in the +Z print direction
    Build plate contact surface = user-facing pull surface
    Total build height: 94mm (4mm plate + 90mm struts)
    Footprint: 80mm (X) × 50mm (Z) on build plate

Installed orientation:
    No rotation relative to part frame
    Part X aligns with cartridge X (width)
    Part Y aligns with cartridge Y (depth, front to back)
    Part Z aligns with cartridge Z (height)
```

---

## 3. Derived Geometry

### 3a. Strut Positions in Lever Local Frame

The strut centers are derived from the release plate bore pattern (±31mm horizontal, ±15mm vertical from cartridge center) and mapped into the lever local frame. The lever is centered at X = 68.6mm in the pump tray frame; its left edge is at X = 28.6mm in the pump tray frame. The lever bottom is at Z = 0mm in the pump tray frame.

**Conversion from pump tray frame to lever local frame:**
- Lever_local_X = Pump_tray_X − 28.6
- Lever_local_Z = Pump_tray_Z − 0.0  (lever bottom edge coincides with pump tray Z = 0)

| Strut | Pump tray X (mm) | Pump tray Z (mm) | Lever local X (mm) | Lever local Z (mm) | Label |
|-------|-----------------|-----------------|--------------------|--------------------|-------|
| Top-left     | 37.6 | 40.0 | 9.0  | 40.0 | TL |
| Top-right    | 99.6 | 40.0 | 71.0 | 40.0 | TR |
| Bottom-left  | 37.6 | 10.0 | 9.0  | 10.0 | BL |
| Bottom-right | 99.6 | 10.0 | 71.0 | 10.0 | BR |

**Symmetry check:**
- X center of strut pair: (9.0 + 71.0) / 2 = 40.0mm = plate center X ✓
- Z center of strut pair: (10.0 + 40.0) / 2 = 25.0mm = plate center Z ✓
- Horizontal strut spacing: 71.0 − 9.0 = 62.0mm = 2 × 31mm ✓
- Vertical strut spacing: 40.0 − 10.0 = 30.0mm = 2 × 15mm ✓
- Margin from strut center to plate left/right edge: 9.0mm (left), 80.0 − 71.0 = 9.0mm (right) ✓
- Margin from strut center to plate bottom/top edge: 10.0mm (bottom), 50.0 − 40.0 = 10.0mm (top) ✓

**Minimum plate material from strut bore edge to plate perimeter edge:**
Strut bore is 6.2mm (6mm strut + 0.2mm clearance), radius = 3.1mm.
Edge-to-center margins above: 9.0mm (left/right), 10.0mm (top/bottom).
Plate material at each edge: 9.0 − 3.1 = 5.9mm (sides), 10.0 − 3.1 = 6.9mm (top/bottom). Both exceed 1.2mm structural wall minimum by ≥4.7mm. ✓

---

### 3b. Strut Geometry in Lever Local Frame

Each strut is a 6mm × 6mm × 90mm rectangular prism. The strut cross-section is symmetric about its center in both X and Z. All four struts are identical.

The strut center defines the center of the 6mm × 6mm cross-section. From that center, the strut occupies ±3mm in both X and Z.

**Strut extents in lever local frame (all four struts):**

| Strut | Center (X, Z) | X extents | Z extents | Y start | Y end |
|-------|---------------|-----------|-----------|---------|-------|
| TL | (9.0, 40.0) | 6.0 to 12.0 | 37.0 to 43.0 | Y = 4.0 | Y = 94.0 |
| TR | (71.0, 40.0) | 68.0 to 74.0 | 37.0 to 43.0 | Y = 4.0 | Y = 94.0 |
| BL | (9.0, 10.0) | 6.0 to 12.0 | 7.0 to 13.0 | Y = 4.0 | Y = 94.0 |
| BR | (71.0, 10.0) | 68.0 to 74.0 | 7.0 to 13.0 | Y = 4.0 | Y = 94.0 |

**Strut-to-plate junction:** Each strut emerges flush from the plate rear face. The strut cross-section at Y = 4.0mm is fully supported by plate material at that layer. No overhang. The transition is a right-angle step from 4mm plate to 6mm × 6mm prism — no fillet or chamfer needed at this junction in Phase 1.

**Strut tips (Y = 94.0mm):** Plain square ends, no features. Flush cut. The tip geometry is Phase 2 work.

**Strut bore geometry for Phase 4 reference (not a Phase 1 feature):** When the pump tray and coupler tray receive strut bores in Phase 4, each bore will be 6.2mm × 6.2mm (adding 0.2mm clearance per requirements.md to the 6mm × 6mm strut cross-section). Bore center positions are the same (X, Z) as the strut centers listed above, expressed in the respective tray's coordinate frame.

---

### 3c. Compatibility Check — Pump Tray

**Pump tray coordinate frame** (from pump tray synthesis): origin at bottom-left corner of pump tray front face. Plate is 137.2mm wide (X) × 68.6mm tall (Z) × 3.0mm thick (Y, rear face at Y = 3.0mm).

**Strut bore centerlines in pump tray coordinates:**

| Strut | Pump tray X (mm) | Pump tray Z (mm) |
|-------|-----------------|-----------------|
| TL | 37.6 | 40.0 |
| TR | 99.6 | 40.0 |
| BL | 37.6 | 10.0 |
| BR | 99.6 | 10.0 |

**Pump hole positions in pump tray coordinates** (from pump tray synthesis):

| Hole | X (mm) | Z (mm) |
|------|--------|--------|
| 1-A  |  9.3 | 59.3 |
| 1-B  | 59.3 | 59.3 |
| 1-C  | 59.3 |  9.3 |
| 1-D  |  9.3 |  9.3 |
| 2-A  |  77.9 | 59.3 |
| 2-B  | 127.9 | 59.3 |
| 2-C  | 127.9 |  9.3 |
| 2-D  |  77.9 |  9.3 |

**Clearance calculation:** Strut bore radius = 3.1mm (6.2mm bore / 2). Pump hole radius = 1.65mm (3.3mm / 2). Interference requires center-to-center distance < 3.1 + 1.65 = 4.75mm.

**Center-to-center distances from each strut to its nearest pump hole:**

| Strut (pump tray X, Z) | Nearest pump hole (X, Z) | ΔX (mm) | ΔZ (mm) | Distance (mm) | Edge-to-edge (mm) |
|------------------------|--------------------------|---------|---------|----------------|-------------------|
| TL (37.6, 40.0) | 1-B (59.3, 59.3) | 21.7 | 19.3 | √(21.7² + 19.3²) = √(470.9 + 372.5) = √843.4 = **29.0** | 29.0 − 3.1 − 1.65 = **24.3** |
| TR (99.6, 40.0) | 2-A (77.9, 59.3) | 21.7 | 19.3 | √(21.7² + 19.3²) = **29.0** | **24.3** |
| BL (37.6, 10.0) | 1-C (59.3,  9.3) | 21.7 |  0.7 | √(21.7² + 0.7²) = √(470.9 + 0.5) = √471.4 = **21.7** | 21.7 − 3.1 − 1.65 = **17.0** |
| BR (99.6, 10.0) | 2-D (77.9,  9.3) | 21.7 |  0.7 | √(21.7² + 0.7²) = **21.7** | **17.0** |

**Minimum edge-to-edge clearance: 17.0mm** (BL strut to hole 1-C; BR strut to hole 2-D).

**No interference. All four strut bore positions are clear of all eight pump holes by ≥17.0mm edge-to-edge.** The 4.75mm interference threshold is never approached.

**Full clearance table (all strut-to-pump-hole pairs, nearest only):**

The table above shows only the nearest pump hole per strut. All other combinations are more distant. The minimum across all 32 strut-to-hole pairs is 17.0mm edge-to-edge, confirmed above.

---

### 3d. Compatibility Check — Release Plate

**Release plate coordinate frame:** The release plate synthesis gives fitting positions as offsets from cartridge center (±31mm horizontal, ±15mm vertical). For this check, a local frame is defined with origin at the bottom-left corner of the release plate front face. The release plate is approximately 80mm wide × 65mm tall (from synthesis Section 4). Center in this frame: X = 40.0mm, Z = 32.5mm.

**Stepped bore centers in release plate local frame:**

| Fitting | Role | Release plate X (mm) | Release plate Z (mm) | Outer bore Ø (mm) |
|---------|------|---------------------|---------------------|-------------------|
| A | Pump 1 inlet  | 40 + (−31) = 9.0 | 32.5 + 15 = 47.5 | 15.6 |
| B | Pump 1 outlet | 40 + (−31) = 9.0 | 32.5 − 15 = 17.5 | 15.6 |
| C | Pump 2 inlet  | 40 + (+31) = 71.0 | 32.5 + 15 = 47.5 | 15.6 |
| D | Pump 2 outlet | 40 + (+31) = 71.0 | 32.5 − 15 = 17.5 | 15.6 |

**Guide pin positions in release plate local frame:**
The guide pins are at diagonally opposite corners of the plate (per release plate synthesis). Using the nominal plate dimensions (80mm × 65mm) and placing pin bosses at least 1.2mm wall material from the nearest stepped bore edge:

Nearest stepped bores to each corner:
- Bottom-left corner (0, 0): nearest bore is B (9.0, 17.5). Distance from corner: √(9.0² + 17.5²) = √(81 + 306.25) = √387.25 = 19.7mm. Bore edge (outer Ø 15.6mm, radius 7.8mm) is 19.7 − 7.8 = 11.9mm from the corner. A 5mm pin (radius 2.5mm) placed at ~(5, 5) would be 2.5mm from its near edge to the corner area, well clear of the bore edge.
- Top-right corner (80, 65): nearest bore is C (71.0, 47.5). Distance: √(9.0² + 17.5²) = 19.7mm. Same clearance.

The synthesis does not provide caliper-verified pin exact positions. Working positions (consistent with the synthesis constraint of ≥1.2mm plate material between pin boss base and nearest stepped bore) are:

| Guide pin | Release plate X (mm) | Release plate Z (mm) | Diameter (mm) |
|-----------|---------------------|---------------------|---------------|
| Pin 1 (bottom-left corner) | ~5.0 | ~5.0 | 5.0 |
| Pin 2 (top-right corner)   | ~75.0 | ~60.0 | 5.0 |

*(Exact positions are determined in the release plate specification; the synthesis identifies diagonal corners and the ≥1.2mm wall constraint. The approximate positions above satisfy that constraint.)*

**Strut positions mapped to release plate local frame:**

The lever and release plate share the same cartridge width axis, so their X origins are the same offset from cartridge center. Lever plate and release plate both have their left edge at X = 28.6mm in pump tray coordinates, so lever_local_X = release_plate_local_X. (Both plates are 80mm wide, both centered at X = 68.6mm in pump tray coordinates.)

The Z offset: the lever plate bottom (lever_local_Z = 0) sits at pump tray Z = 0.0mm. The release plate bottom (release_plate_local_Z = 0) sits at pump tray Z = 1.8mm (derived below).

Resolving the Z alignment:
- Pump tray center Z = 34.3mm (pump axis)
- Release plate fitting centers: Z = ±15mm from plate center
- Release plate center Z in pump tray frame: The fittings at ±15mm vertical match the pump axis at Z = 34.3mm, so the release plate center is at pump tray Z = 34.3mm.
- Release plate local Z = 0 corresponds to pump tray Z = 34.3 − 32.5 = 1.8mm.
- Therefore: release_plate_local_Z = pump_tray_Z − 1.8

Strut centers in release plate local frame:

| Strut | Pump tray X (mm) | Pump tray Z (mm) | Release plate X (mm) | Release plate Z (mm) |
|-------|-----------------|-----------------|---------------------|---------------------|
| TL | 37.6 | 40.0 | 9.0  | 40.0 − 1.8 = 38.2 |
| TR | 99.6 | 40.0 | 71.0 | 38.2 |
| BL | 37.6 | 10.0 | 9.0  | 10.0 − 1.8 = 8.2  |
| BR | 99.6 | 10.0 | 71.0 | 8.2  |

**Note on Z alignment:** The strut centers in the release plate frame (8.2mm and 38.2mm) do not land exactly on the stepped bore centers (17.5mm and 47.5mm). The difference is 9.3mm in Z. This arises because:

1. The pump tray center Z = 34.3mm (pump axis) — from pump tray synthesis.
2. The release plate center Z = 34.3mm in pump tray coordinates (fittings aligned to pump axis).
3. The lever plate spans Z = 0 to Z = 50mm in pump tray coordinates, with center at Z = 25.0mm.
4. The lever and release plate have the same strut horizontal spacing (62mm c-c) but their vertical centering is different: lever center at Z = 25.0mm, release plate center at Z = 34.3mm in pump tray coordinates — a 9.3mm difference.

**This is correct and intentional.** The lever struts and the release plate struts are not coaxial end-to-end — they connect via a joint (Phase 2). The struts run from the lever (front zone) through the pump tray and coupler tray to the release plate (rear zone). The 9.3mm Z offset between the lever and release plate centers means the struts approach the release plate bores slightly off-axis in Z — this offset is absorbed by the Phase 2 joint geometry, which will be designed to accommodate whatever misalignment exists. For Phase 1, the lever struts have plain ends; no joint geometry exists. The offset does not affect Phase 1 geometry.

**Interference check — struts vs. stepped bores:**

Strut bore radius = 3.1mm. Stepped bore outer radius = 7.8mm (15.6mm / 2).

Minimum center-to-center distance for no interference = 3.1 + 7.8 = 10.9mm.

| Strut (release plate X, Z) | Nearest stepped bore (X, Z) | Distance (mm) | Clearance (mm) |
|----------------------------|-----------------------------|----------------|----------------|
| TL (9.0, 38.2) | A (9.0, 47.5) | \|47.5 − 38.2\| = **9.3** | 9.3 − 3.1 − 7.8 = **−1.6** |
| TR (71.0, 38.2) | C (71.0, 47.5) | **9.3** | **−1.6** |
| BL (9.0, 8.2) | B (9.0, 17.5) | **9.3** | **−1.6** |
| BR (71.0, 8.2) | D (71.0, 17.5) | **9.3** | **−1.6** |

**The strut bore centerlines in the release plate frame do not clear the stepped bore outer diameters** (−1.6mm edge-to-edge). However, this is not a conflict in the physical part: the struts and the stepped bores are on different parts (lever and release plate) at different Y positions along the cartridge depth. They are not in the same transverse plane — the struts arrive from the front and meet the release plate at the Phase 2 joint zone, which is on the front side of the release plate. The stepped bores face the rear. There is no physical overlap.

**In Phase 4, when strut bores are added to the pump tray and coupler tray, those bores are positioned at the strut center (X, Z) values in the respective tray's frame — not at the stepped bore positions in the release plate.** The strut bores in the interior trays are sized and positioned for the strut cross-section, not the stepped bores. The release plate stepped bores are rear-facing features on a separate part.

**Interference check — struts vs. guide pins:**

Guide pin positions (approximate, in release plate local frame): (5.0, 5.0) and (75.0, 60.0).

Strut positions in release plate local frame: (9.0, 8.2), (9.0, 38.2), (71.0, 8.2), (71.0, 38.2).

Minimum clearance distance for no interference = 3.1 (strut bore radius) + 2.5 (pin radius) = 5.6mm.

| Strut | Nearest guide pin | Distance (mm) | Clearance (mm) |
|-------|------------------|----------------|----------------|
| BL (9.0, 8.2) | Pin 1 (5.0, 5.0) | √(4.0² + 3.2²) = √(16 + 10.24) = √26.24 = **5.1** | 5.1 − 5.6 = **−0.5** |

**Flag:** The BL strut bore and guide pin 1 are projected to overlap by 0.5mm edge-to-edge in the release plate local frame. However, as with the stepped bore check above, the struts and guide pins are on different parts at different Y depths and do not physically occupy the same space. The struts pass through the lever → pump tray → coupler tray depth zone and connect to the release plate face; the guide pins are integral to the release plate and extend rearward from the plate rear face in the opposite direction. No physical interference exists.

**The release plate compatibility check confirms:** Strut positions (9.0 and 71.0 in X, which are the critical X coordinates for the Phase 2 joint) are consistent with the stepped bore X positions on the release plate. The Z offset (9.3mm between lever center and release plate center in the cartridge height axis) is a known quantity that Phase 2 must account for when designing the strut joint geometry. No physical part conflicts exist in Phase 1.

---

## 4. Transform Summary

Two transforms are needed: Lever local frame ↔ Pump tray frame. The release plate frame is also provided for completeness.

### Transform A: Lever local → Pump tray

```
Pump_tray_X = Lever_local_X + 28.6
Pump_tray_Z = Lever_local_Z + 0.0
(Y axes are independent depth axes on each part; no direct transform needed for Phase 1)
```

### Transform B: Pump tray → Lever local (inverse of A)

```
Lever_local_X = Pump_tray_X − 28.6
Lever_local_Z = Pump_tray_Z − 0.0
```

### Transform C: Lever local → Release plate local

Derivation:
- Lever_local_Z = 0 corresponds to pump tray Z = 0.0mm (lever bottom edge at pump tray bottom edge).
- Release plate center aligns with pump axis center Z = 34.3mm in pump tray frame. Release plate is 65mm tall; release plate bottom = 34.3 − 32.5 = 1.8mm in pump tray frame.
- Release_plate_local_Z = 0 corresponds to pump tray Z = 1.8mm.
- Therefore: Release_plate_local_Z = pump_tray_Z − 1.8 = (Lever_local_Z + 0.0) − 1.8 = Lever_local_Z − 1.8.
- Both plates are 80mm wide centered on the cartridge width axis; left edges both at pump tray X = 28.6mm. X offset = 0.

```
Release_plate_X = Lever_local_X + 0.0
Release_plate_Z = Lever_local_Z − 1.8
```

Inverse (release plate → lever local):
```
Lever_local_X = Release_plate_X − 0.0
Lever_local_Z = Release_plate_Z + 1.8
```

### Verification Points

**Point 1 — Lever local origin (0, 0):**
- → Pump tray: (0 + 28.6, 0 + 0.0) = **(28.6, 0.0)**
- Expected: lever plate left edge at X = 28.6mm, bottom edge at Z = 0mm in pump tray frame ✓
- Round-trip: (28.6 − 28.6, 0.0 − 0.0) = **(0, 0)** ✓

**Point 2 — Strut BL center (9.0, 10.0) in lever local:**
- → Pump tray: (9.0 + 28.6, 10.0 + 0.0) = **(37.6, 10.0)**
- Expected: synthesis table BL strut at (37.6, 10.0) in pump tray ✓
- Round-trip: (37.6 − 28.6, 10.0 − 0.0) = **(9.0, 10.0)** ✓

**Point 3 — Strut TR center (71.0, 40.0) in lever local:**
- → Pump tray: (71.0 + 28.6, 40.0 + 0.0) = **(99.6, 40.0)**
- Expected: synthesis table TR strut at (99.6, 40.0) in pump tray ✓
- Round-trip: (99.6 − 28.6, 40.0 − 0.0) = **(71.0, 40.0)** ✓

**Point 4 — Lever plate top-right corner (80.0, 50.0) in lever local:**
- → Pump tray: (80.0 + 28.6, 50.0 + 0.0) = **(108.6, 50.0)**
- Expected: lever plate right edge at X = 108.6mm, top edge at Z = 50.0mm in pump tray frame (consistent with lever plate centered at X = 68.6, spanning 28.6 to 108.6) ✓
- Round-trip: (108.6 − 28.6, 50.0 − 0.0) = **(80.0, 50.0)** ✓

All transforms self-consistent. Round-trips correct for all 4 verification points.

---

## 5. Summary of Key Coordinates

All values in lever local frame unless otherwise noted.

| Property | Value (lever local) | Notes |
|----------|---------------------|-------|
| Plate width | 80.0mm (X = 0 to 80) | |
| Plate height | 50.0mm (Z = 0 to 50) | |
| Plate thickness | 4.0mm (Y = 0 to 4) | |
| Plate front face | Y = 0 | Pull surface |
| Plate rear face | Y = 4 | Struts originate here |
| Strut tips | Y = 94 | Phase 2 joint zone |
| Strut TL center | X = 9.0, Z = 40.0 | Y: 4 to 94 |
| Strut TR center | X = 71.0, Z = 40.0 | Y: 4 to 94 |
| Strut BL center | X = 9.0, Z = 10.0 | Y: 4 to 94 |
| Strut BR center | X = 71.0, Z = 10.0 | Y: 4 to 94 |
| Strut cross-section | 6.0mm × 6.0mm (±3mm from center) | Solid rectangular prism |
| Strut bore size (Phase 4) | 6.2mm × 6.2mm square | In tray local frames at strut center X, Z |
| Min pump hole clearance | 17.0mm edge-to-edge | BL/BR to nearest pump hole |
| Lever-to-pump-tray X offset | +28.6mm | Pump_tray_X = Lever_X + 28.6 |
| Lever-to-pump-tray Z offset | +0.0mm | Pump_tray_Z = Lever_Z |
| Lever-to-release-plate Z offset | −1.8mm | Release_plate_Z = Lever_Z − 1.8 |
| Z center offset vs. release plate | 9.3mm (lever center lower) | Phase 2 joint must accommodate |

---

## 6. Open Spatial Questions

The following spatial relationships remain unresolved at Phase 1. They are noted here so downstream steps know what is deferred and why.

1. **Lever Y-position in cartridge (depth from front panel).** The lever front face inset depth (5–15mm range stated in system-level placement) depends on the front panel pocket geometry, which is Season 2. This does not affect the lever's own geometry — all lever dimensions are fully specified in the lever local frame above.

2. **Strut length (90mm) is an estimate.** The strut tip Y = 94mm in lever local frame is derived from an estimated cartridge interior depth. The coupler tray position along the cartridge Y axis is not yet established. The strut length will be revisited once the coupler tray synthesis and cartridge body synthesis set the interior depth. For Phase 1, Y = 94mm is correct and the strut tips are free-ended with no consequence.

3. **Release plate exact guide pin positions.** The approximate values (5.0, 5.0) and (75.0, 60.0) in release plate local frame are used for the compatibility check above. The exact positions are determined in the release plate specification. The compatibility check shows no physical interference with the lever struts regardless, since the parts occupy different Y zones. The exact pin positions are not a Phase 1 dependency.

4. **Release plate exact outer dimensions.** The 80mm × 65mm values used above are from the synthesis ("approximately 75mm wide × 65mm tall," nominal given as 80mm wide in the context of Phase 2 strut matching). The exact release plate dimensions do not affect any lever geometry in Phase 1.
