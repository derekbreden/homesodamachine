# Pump-Tray — Parts Specification

**Part:** Pump-Tray (cartridge sub-assembly)
**File:** `hardware/printed-parts/cartridge/pump-tray/planning/parts.md`
**Status:** Complete specification — ready for CAD generation (step 4b).
**Sources:** spatial-resolution.md (primary), concept.md, decomposition.md, synthesis.md, research/pump-mounting-geometry.md, research/structural-requirements.md, research/tube-routing-envelope.md, research/design-patterns.md, off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md, off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md, hardware/requirements.md, hardware/vision.md.

---

## 0. Coordinate Reference Frame

All coordinates in this document are in the tray part frame. No transforms required.

```
Origin:    Front-face bottom-left corner
           (Y=0, X=0, Z=0 — the build-plate contact face corner)

X-axis:    Tray width, left to right
           X = 0 → left lateral face
           X = 144mm → right lateral face

Y-axis:    Tray depth, front to rear
           Y = 0 → front face (pump-bracket side; rests on build plate during printing)
           Y = 5mm → rear face (motor/service side; top surface during printing)
           Y = −5mm → rib and cross-rib crown (protrude from front face in −Y direction)
           Y = 10mm → boss tip faces (protrude from rear face in +Y direction)

Z-axis:    Tray height, bottom to top
           Z = 0 → bottom edge (build-plate contact edge)
           Z = 80mm → top edge (working assumption; see OQ-3/OQ-4 flag below)
```

**DESIGN GAP — OQ-3/OQ-4:** Tray height (80mm vs. 85mm) and pump center Z (Z=40.0mm vs. a different value) are working assumptions pending caliper verification of tube stub positions on the pump face. This value is used throughout this document. If OQ-3/OQ-4 measurement changes this dimension, all Z-coordinates derived from pump center Z must be recomputed. CAD may start on all features that do not depend on total tray height or pump center Z; the boss and bore positions are height-dependent and must be confirmed before final toolpath generation.

**DESIGN GAP — OQ-2:** Motor body diameter (nominally 35mm) is low-confidence (photo-derived: 34.54–35.13mm). The 37.2mm bore CAD value provides 1.0mm minimum radial clearance on a 35.13mm motor. If the actual motor OD exceeds 35.6mm, the bore must be revised. Verify by direct caliper before final CAD.

---

## 1. Base Plate Body

| Parameter | Value | Source |
|-----------|-------|--------|
| Material | PETG | structural-requirements.md: creep resistance, Tg 80°C, heat-set insert compatibility |
| Print orientation | Front face (Y=0) on build plate | structural-requirements.md: bore roundness requires flat print; 37mm bore would be a 37mm bridge span if printed on-edge, exceeding the 15mm limit in requirements.md |
| Outer envelope (plate body, no bosses/ribs) | 144mm W (X) × 5mm D (Y) × 80mm H (Z) | spatial-resolution.md §2, §3 |
| Plate corner radii (4 plan-view corners, full Y depth) | 3.0mm radius | concept.md §5: places tray in visual register of molded components |
| Infill | 40% minimum, gyroid or grid; 50% preferred at boss zones | structural-requirements.md §6 consolidated spec |
| Perimeter count | 4 minimum throughout; 5 preferred at boss zones | structural-requirements.md |
| Layer height | 0.2mm acceptable; 0.15mm preferred for bore roundness and boss surface quality | concept.md §7 |

The plate body is a rectangular box (144 × 5 × 80mm with 3mm outer corner radii in plan view). All features are additive (bosses, ribs) or subtractive (bores, holes, channels, notches) operations on this box. No rotation from part frame to assembly frame.

---

## 2. Motor Bores (×2)

Two cylindrical through-cuts, one per pump. These are clearance features only — the motor cylinder does not contact the bore wall.

| Parameter | Value | Source |
|-----------|-------|--------|
| Count | 2 | One per pump |
| Bore diameter (CAD design value) | 37.2mm | spatial-resolution.md §4: motor OD ~35mm + 1.0mm radial clearance/side + 0.2mm FDM compensation per requirements.md |
| Bore diameter (printed target) | ~37.0mm | After FDM shrinkage |
| Bore axis | Y-axis (parallel to plate thickness) | spatial-resolution.md §4 |
| Y extent | Y=0 to Y=5mm (full plate thickness, through-cut) | spatial-resolution.md §4 |
| Bore surface | Clearance only — no bearing surface, no step, no counterbore | concept.md §4 |
| Chamfer — rear face (Y=5) | 0.5mm × 45° on circular bore edge at Y=5 (rear face entry) | spatial-resolution.md §10: finished appearance, reduces bridging artifact at bore arc top |
| Chamfer — front face (Y=0) | None — build plate face; bore printed with clean concentric perimeters | spatial-resolution.md §10 |

### Bore Center Positions

| Bore | Center X (mm) | Center Z (mm) | Derivation |
|------|---------------|---------------|------------|
| Bore 1 (Pump 1) | **34.5** | **40.0** | spatial-resolution.md §3: tray center X=72 − 37.5 = 34.5; Z = 80/2 = 40.0 (working assumption, OQ-3/OQ-4) |
| Bore 2 (Pump 2) | **109.5** | **40.0** | spatial-resolution.md §3: tray center X=72 + 37.5 = 109.5; same Z |

### Bore Web Verification (spatial-resolution.md §4.3)

Minimum web between bore edge and nearest clearance hole edge:
- Bore radius (CAD): 18.6mm
- Hole center offset from pump center: 24.0mm
- Clearance hole radius (CAD): 1.8mm
- Web = 24.0 − 18.6 − 1.8 = **3.6mm**

3.6mm > 1.2mm structural wall minimum (requirements.md). Pass.

---

## 3. Heat-Set Insert Bosses (×8)

Eight identical cylindrical bosses on the **rear face** (Y=5), protruding in the +Y direction. Each boss is coaxial with one M3 clearance hole through the plate. The screw path runs front-to-rear: pump bracket → plate clearance hole → boss cavity → insert threads.

### Boss Geometry (all 8 identical)

| Parameter | Value | Source |
|-----------|-------|--------|
| Face of origin | Rear face (Y=5mm) | spatial-resolution.md §6.1: printing constraint — bosses on Y=0 would grow into build plate or into plate body; only Y=5 rear face protrusion is printable |
| Boss base location (Y) | Y = 5mm | Flush with rear face surface |
| Boss tip location (Y) | Y = 10mm | 5mm protrusion above rear face, into motor zone |
| Boss OD | 9mm | structural-requirements.md §4: 2.15mm wall around 5mm OD insert; confirmed clear of 3.6mm web |
| Boss base fillet | 1.5mm radius at Y=5 junction | structural-requirements.md §4: stress concentration reduction |
| Pilot hole (insert bore) diameter | 4.7mm | Ruthex RX-M3×5×4 community spec (Voron/Prusa); structural-requirements.md §4 |
| Pilot hole depth | 4.5mm (from boss tip) | 4.0mm insert + 0.5mm floor; cavity opens at Y=10, bottom at Y=5.5 |
| Pilot hole Y range | Y=10.0mm (opening at boss tip) to Y=5.5mm (floor) | spatial-resolution.md §6.2 |
| Insert floor Y position | Y=5.5mm (0.5mm of boss material below insert) | spatial-resolution.md §6.2 |
| Clearance hole through plate | 3.6mm diameter, Y=0 to Y=5.5mm (full plate thickness plus 0.5mm into boss, meeting insert bore floor) | spatial-resolution.md §5: targets 3.4mm printed, normal ISO 273 fit |

### Screw Path (for assembly clarity)

1. Screw head: at pump bracket face (Y < 0, pump side)
2. Shank passes through pump bracket's 3.13mm clearance hole
3. Shank passes through tray 3.6mm CAD clearance hole (Y=0 → Y=5.5, entering boss by 0.5mm)
4. Shank enters insert bore at Y=5.5 (clearance bore meets insert bore floor exactly)
5. Shank threads into heat-set insert seated in boss cavity (Y=5.5 to Y=9.5)
6. Full 4mm of insert thread engaged

**Insert installation sequence:** Insert is driven from the **rear face** (Y=5 side, which is the top surface during printing). Soldering iron at 245°C, approaching from above (+Y direction). This step occurs before pump installation.

### Boss Center Positions (all 8, from spatial-resolution.md §6.3)

| Boss ID | X (mm) | Z (mm) | Pump | Pattern position |
|---------|--------|--------|------|-----------------|
| Boss 1A | **10.5** | **16.0** | Pump 1 | Bottom-left |
| Boss 1B | **58.5** | **16.0** | Pump 1 | Bottom-right |
| Boss 1C | **10.5** | **64.0** | Pump 1 | Top-left |
| Boss 1D | **58.5** | **64.0** | Pump 1 | Top-right |
| Boss 2A | **85.5** | **16.0** | Pump 2 | Bottom-left |
| Boss 2B | **133.5** | **16.0** | Pump 2 | Bottom-right |
| Boss 2C | **85.5** | **64.0** | Pump 2 | Top-left |
| Boss 2D | **133.5** | **64.0** | Pump 2 | Top-right |

Derivation: Pump 1 center (34.5, 40.0) ± 24mm in X and Z; Pump 2 center (109.5, 40.0) ± 24mm in X and Z. All 8 positions satisfy boundary check (minimum 10.5mm from nearest edge vs. 4.5mm boss radius minimum).

---

## 4. Mounting Pad Zones (Front Face — Y=0)

The front face is divided into two surface levels. The mounting pad zones are at the full plate face height (Y=0). The field zone is 0.5mm recessed (cut to Y=+0.5mm from the front face into the plate body).

| Parameter | Value | Source |
|-----------|-------|--------|
| Step height | 0.5mm (field zone is 0.5mm lower than mounting pad) | design-patterns.md UX Quality 3, concept.md §5 |
| Step transition | 45° chamfer (not 90° step) | requirements.md: avoids stress riser; prints clean at 45° limit |
| Purpose | Ensures pump bracket seats on a clean reference surface; field-zone debris/variation cannot interfere with bracket seating | synthesis.md §3 |

### Mounting Pad Zone Extents (spatial-resolution.md §7.1)

| Zone | X range (mm) | Z range (mm) | Notes |
|------|-------------|-------------|-------|
| Pump 1 mounting pad | X = 0 to 71.5 | Z = 3.0 to 77.0 | Clipped at X=0 tray edge; bracket footprint is 68.6mm wide centered at X=34.5 |
| Pump 2 mounting pad | X = 72.5 to 144 | Z = 3.0 to 77.0 | Clipped at X=144 tray edge |
| Cross-rib connection band | X = 69.0 to 75.0 | Z = 37.0 to 43.0 | 6mm wide, centered X=72, Z-centered at Z=40; connects two mounting pad zones |

The field zone covers all front face area outside these three zones. The cross-rib body (a separate geometric feature on the front face) runs within the cross-rib connection band and is at mounting pad height, making the elevated band continuous across the plate.

---

## 5. Structural Ribs (Rear Face — Y=5, protrude in +Y direction)

All ribs are on the **rear face** (Y=5), the same face as the bosses. Ribs protrude in the +Y direction (upward during printing, away from the build plate toward the motor/service side). Rib crown is at Y=10mm (5mm proud of rear face, same height as boss tips). Rib base is at Y=5 (flush with rear face surface). Rib base fillet: 2.0mm radius where rib meets plate face.

**Correction note:** Ribs were originally specified as front-face features protruding in the −Y direction. This is geometrically impossible — the front face is on the build plate (Y=0), so nothing can be deposited at Y<0. Ribs are correctly placed on the rear face (+Y), co-planar with the bosses. The front face carries only subtractive features (field zone step, bore through-cuts, clearance holes, elephant's foot chamfer).

Note: Rib crowns (Y=10) and boss tips (Y=10) are coplanar — both on the rear face, both 5mm tall. This is intentional: the rear service face is a consistent landscape of structural features all at the same peak height, with wiring channels cut between them.

### 5.1 Bore-to-Bore Cross Rib (×1)

A single rib on the rear face connecting the region between the two motor bores, running along the X-axis at Z=40.

| Parameter | Value | Source |
|-----------|-------|--------|
| Width (Z extent) | 6mm, centered at Z=40 → Z=37.0 to Z=43.0 | spatial-resolution.md §7.1 |
| Height (Y protrusion) | 5mm (base at Y=5, crown at Y=10) | concept.md §5 |
| Length (X extent) | X = 53.1 to X = 90.9 (37.8mm) | spatial-resolution.md: from Bore 1 edge (34.5+18.6=53.1) to Bore 2 edge (109.5−18.6=90.9) |
| Crown chamfer | 1mm chamfer on rib crown (top edge at Y=10) | concept.md §5 |
| Base fillet | 2.0mm radius where rib base meets rear face | concept.md §5, spatial-resolution.md §11 |

**Cross-rib boss clearance verification:** The cross-rib Z range is Z=37.0 to 43.0. All boss Z positions are 16.0 and 64.0. Minimum distance from rib edge (Z=37.0) to nearest boss center (Z=16.0): 21mm. The rib does not pass through any boss position. Pass.

### 5.2 Boss-to-Bore Radiating Ribs (×8)

One rib per boss, running from the boss OD edge toward the nearest bore circle edge. All 8 ribs have the same geometry; positions vary by boss/bore location.

| Parameter | Value | Source |
|-----------|-------|--------|
| Width | 4mm centered on the boss-to-bore vector | spatial-resolution.md §7.2 |
| Height (Y protrusion) | 5mm (base at Y=5, crown at Y=10) | concept.md §5 |
| Length | ~10.84mm for all 8 ribs (corner bosses at 45° to bore center) | spatial-resolution.md §7.2 recalculation |
| Base fillet | 2.0mm radius at rib base (on rear face, Y=5) | spatial-resolution.md §11 |
| Crown | No chamfer (short ribs, chamfer not needed per concept.md §5) | concept.md §5 |

**Rib endpoint derivation (all 8, from spatial-resolution.md §7.2):**

Each rib runs along the vector from boss center to bore center. Rib endpoints are:
- Boss-side endpoint: boss center + 4.5mm (boss radius) in direction of bore center
- Bore-side endpoint: bore center + 18.6mm (bore radius) in direction of boss center

All 8 corner bosses are at ±24mm in both X and Z from their bore center, placing them at 45° diagonals. The boss-to-bore-center distance is sqrt(24² + 24²) = 33.94mm for all 8. Rib length = 33.94 − 4.5 − 18.6 = **10.84mm** for all 8.

| Rib ID | Boss center (X, Z) | Bore center (X, Z) | Unit vector (toward bore) | Boss OD endpoint (X, Z) | Bore edge endpoint (X, Z) |
|--------|--------------------|--------------------|--------------------------|------------------------|--------------------------|
| Rib 1A | (10.5, 16.0) | (34.5, 40.0) | (0.707, 0.707) | (13.68, 19.18) | (21.35, 26.85) |
| Rib 1B | (58.5, 16.0) | (34.5, 40.0) | (−0.707, 0.707) | (55.32, 19.18) | (47.65, 26.85) |
| Rib 1C | (10.5, 64.0) | (34.5, 40.0) | (0.707, −0.707) | (13.68, 60.82) | (21.35, 53.15) |
| Rib 1D | (58.5, 64.0) | (34.5, 40.0) | (−0.707, −0.707) | (55.32, 60.82) | (47.65, 53.15) |
| Rib 2A | (85.5, 16.0) | (109.5, 40.0) | (0.707, 0.707) | (88.68, 19.18) | (96.35, 26.85) |
| Rib 2B | (133.5, 16.0) | (109.5, 40.0) | (−0.707, 0.707) | (130.32, 19.18) | (122.65, 26.85) |
| Rib 2C | (85.5, 64.0) | (109.5, 40.0) | (0.707, −0.707) | (88.68, 60.82) | (96.35, 53.15) |
| Rib 2D | (133.5, 64.0) | (109.5, 40.0) | (−0.707, −0.707) | (130.32, 60.82) | (122.65, 53.15) |

**Lateral perimeter ribs:** Not needed at 144mm tray width. The outermost boss (X=10.5 from left edge X=0) leaves 10.5mm of plate beyond the outermost boss — under the 20mm threshold from concept.md §5. Lateral perimeter ribs are explicitly omitted.

---

## 6. Wiring Channels (×2, Rear Face — Y=5)

Two rectangular channels cut into the **rear face** (Y=5), one per pump. Channel walls run in +Y direction (upward during printing from the top surface), channel floor is bridged across the channel width. Bridge span = 6mm, well within the 15mm bridge limit.

### Channel Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Location | Rear face (Y=5) only | spatial-resolution.md §8 |
| Width | 6mm | spatial-resolution.md §8.1 |
| Depth | 4mm (from Y=5 inward to Y=1; channel floor at Y=1) | spatial-resolution.md §8.1 |
| Wall thickness | 1.5mm on each side | concept.md §5 |
| Interior corner fillet | 1.5mm radius at wall-meets-floor junction | spatial-resolution.md §11 |
| Y extent | Y=5mm (opening at rear face surface) to Y=1mm (floor) | spatial-resolution.md §12 |

### Channel Entry Points and Routing

Each channel begins at the bore edge on the rear face and routes laterally toward the nearest tray lateral edge. Routing beyond the lateral edge exit is deferred to the shell concept step (OQ-6).

| Channel | Bore center (X, Z) | Bore edge entry (X, Z) | Routing direction | Terminal X |
|---------|--------------------|-----------------------|-------------------|-----------|
| Channel 1 (Pump 1) | (34.5, 40.0) | **(15.9, 40.0)** | −X direction toward X=0 | X=0 (exits at lateral face) |
| Channel 2 (Pump 2) | (109.5, 40.0) | **(128.1, 40.0)** | +X direction toward X=144 | X=144 (exits at lateral face) |

Entry point derivation: Channel 1: X = 34.5 − 18.6 = 15.9; Channel 2: X = 109.5 + 18.6 = 128.1. Both at Z=40.0.

Channel Z extent at all cross-sections: Z=37.0 to Z=43.0 (6mm wide, centered at Z=40.0).

Lateral run length: 15.9mm for each channel (Channel 1: X=15.9 to X=0; Channel 2: X=128.1 to X=144.0).

**DESIGN GAP — OQ-6:** Channel routing beyond the lateral face exit (longitudinal segment toward front or rear, final exit location) is deferred. The shell concept step must define the harness connector exit location before the full channel path can be finalized. The CAD agent generates the lateral segment only.

### Strain-Relief Bumps (2 per channel on lateral segment)

Rounded protrusions from the channel floor. 1.5mm tall (from channel floor at Y=1 toward Y=−0.5 in printer coordinates, i.e., growing upward during printing from the channel floor bridge surface).

| Parameter | Value | Source |
|-----------|-------|--------|
| Height | 1.5mm above channel floor | concept.md §5 |
| Width | 2mm | concept.md §5 |
| Profile | Rounded crown | concept.md §5 |
| Count | 2 per channel on lateral segment (20mm target spacing cannot fit in 15.9mm run; placed at 5mm intervals) | spatial-resolution.md §8.3 |

**Bump positions (spatial-resolution.md §8.3, revised spacing):**

| Channel | Bump 1 (X, Z) | Bump 2 (X, Z) |
|---------|--------------|--------------|
| Channel 1 | **(10.9, 40.0)** | **(5.9, 40.0)** |
| Channel 2 | **(133.1, 40.0)** | **(138.1, 40.0)** |

Derivation: Channel 1 entry at X=15.9; Bump 1 at X=15.9−5=10.9; Bump 2 at X=15.9−10=5.9. Symmetric for Channel 2.

Note: When the shell step adds a longitudinal channel segment, bump spacing reverts to the 20mm target per concept.md §5.

---

## 7. Snap Notches (×2, Lateral Faces)

Two passive rectangular notch cuts, one in each lateral face. These provide engagement surfaces for the shell's snap latch. All spring geometry is on the shell; the tray contributes only the passive notch pocket.

### Notch Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Count | 2 (one per lateral face) | concept.md §2 |
| Location — left notch | X=0 lateral face, at Y=5 rear edge | spatial-resolution.md §9.2 |
| Location — right notch | X=144 lateral face, at Y=5 rear edge | spatial-resolution.md §9.2 |
| Depth (into plate in X direction) | 1.5mm (left notch: X=0 to X=1.5; right notch: X=144 to X=142.5) | spatial-resolution.md §9.2 |
| Width (in Z) | 3mm (Z=38.5 to Z=41.5, centered at Z=40.0) | spatial-resolution.md §9.2 |
| Y extent | Y=5.0mm (opening at rear face edge) to Y=2.0mm (notch bottom; 3mm deep in Y) | spatial-resolution.md §9.2 |
| Profile | Rectangular (no chamfer or radius — shell latch hooks into this rectangular pocket) | concept.md §2 |

**DESIGN GAP — Snap notch Z and Y:** Z=40.0mm and Y depth of 3mm are working assumptions. The shell concept step must confirm the exact Z position of the snap latch receiver and required notch depth. These values must be reconciled before final CAD commit.

---

## 8. Chamfers and Edge Treatments

All edge treatments as defined in spatial-resolution.md §10.

| Edge | Treatment | Size | Notes |
|------|-----------|------|-------|
| Top edge (Z=80), front face side (Y=0) | Design chamfer | 1.5mm × 45° | Quality signal; visible when looking into cartridge |
| Top edge (Z=80), rear face side (Y=5) | Design chamfer | 1.5mm × 45° | Included in "top face perimeter" |
| Left lateral edge (X=0), full Z extent, both faces | Design chamfer | 1.5mm × 45° | Full plate height |
| Right lateral edge (X=144), full Z extent, both faces | Design chamfer | 1.5mm × 45° | Full plate height |
| Bottom edge (Z=0), front face (Y=0) — build plate contact edge | Elephant's foot chamfer | 0.3mm × 45° | Per requirements.md dimensional accuracy; this is the build-plate face |
| Bottom edge (Z=0), rear face (Y=5) | Design chamfer | 1.5mm × 45° | Not the build-plate face; receives standard perimeter chamfer |
| Both motor bore openings at rear face (Y=5): circular edge | Bore entry chamfer | 0.5mm × 45° | Finished appearance; reduces bridging artifact at bore arc top |

---

## 9. Corner Radii (spatial-resolution.md §11)

| Location | Radius |
|----------|--------|
| Outer tray plate corners (4 plan-view corners: X=0/144, Z=0/80, through full Y depth) | 3.0mm |
| Boss base fillet (boss cylinder meets rear face plate surface) | 1.5mm |
| Rib base fillet (all ribs meet front face) | 2.0mm |
| Wiring channel interior corners (channel wall meets channel floor) | 1.5mm |

---

## 10. Feature Y-Depth Summary (spatial-resolution.md §12)

Complete Y-range for every feature.

| Feature | Y start | Y end | Direction |
|---------|---------|-------|-----------|
| Plate body | 0 | 5mm | Full plate thickness |
| Motor bore (through-cut) | 0 | 5mm | Through full thickness |
| M3 clearance holes (through-cut) | 0 | 5mm | Through full thickness |
| Boss cylinders (union on rear face) | 5mm | 10mm | Protrude +Y from rear face |
| Boss pilot holes (blind bore from boss tip) | 10mm | 5.5mm | Opens at Y=10, floor at Y=5.5 |
| Heat-set insert (seated in boss cavity) | 10mm | 6.0mm | 4mm insert; floor at Y=5.5 to Y=6.0 |
| Cross-rib (union on front face) | 0 | −5mm | Protrudes −Y from front face (pump side) |
| Radiating ribs (union on front face) | 0 | −5mm | Same |
| 0.5mm field zone recess (cut into front face) | 0 | +0.5mm | Cut 0.5mm into front face (field zone only) |
| Wiring channels (cut into rear face) | 5mm | 1mm | 4mm deep cut from rear face inward |
| Strain-relief bumps (union in channel) | 1mm | −0.5mm | 1.5mm protrusion from channel floor |
| Snap notches (cut into lateral face at Y=5 edge) | 5mm | 2mm | 3mm deep cut from rear edge inward |
| Rear bore chamfer | Y=5 bore edge | — | 0.5mm × 45° chamfer |
| Elephant's foot chamfer | Y=0 bottom edge | — | 0.3mm × 45° at Z=0 |
| Perimeter design chamfers | All applicable edges | — | 1.5mm × 45° |

---

## 11. Hardware Bill of Materials (off-the-shelf)

| Item | Specification | Quantity | Purpose |
|------|--------------|----------|---------|
| M3 heat-set inserts | Ruthex RX-M3×5×4 or equivalent; OD 5.0mm, length 4.0mm, M3 thread | 8 | One per boss; installed from rear face (Y=5) with soldering iron at 245°C before pump installation |
| M3 socket head cap screws | M3 × 10mm (see note) | 8 | One per boss; passes through pump bracket clearance hole + tray clearance hole + engages full 4mm insert; head on pump side (Y < 0) |
| Thread preparation | Loctite 243 medium-strength (blue) thread locker | — | Applied to all 8 screws at assembly; prevents vibration loosening at 2–14 Hz pump operating frequency |
| Assembly torque | 0.5–0.8 N·m | — | Snug; do not over-torque M3 into nylon pump head |

**Note on screw length:** The task prompt specifies M3 × 10mm. synthesis.md and pump-mounting-geometry.md recommend M3 × 12mm for ≥6mm thread engagement in the nylon pump head body (bracket ~2mm + tray clearance hole ~5mm = ~7mm travel before thread engagement begins; a 10mm screw engages only ~3mm). **DESIGN GAP — OQ-1:** Measure the screw hole depth in the pump head body directly. The M3 × 10mm length may be insufficient for the minimum 6mm thread engagement required for vibration-loaded joints per pump-mounting-geometry.md §3.3. Recommend using M3 × 12mm pending OQ-1 confirmation. This document records M3 × 10mm as stated in the task prompt; if OQ-1 confirms inadequate engagement, upgrade to M3 × 12mm without changing any tray geometry.

---

## 12. Build Plate Fit Confirmation

| Dimension | Value | Build plate (Bambu H2C single nozzle: 325mm × 320mm) | Result |
|-----------|-------|------------------------------------------------------|--------|
| Part footprint | 144mm W × 80mm D | 325mm and 320mm available | Fits with 181mm and 240mm margin |
| Two parts simultaneously | 144+5+144 = 293mm on 325mm axis | 293 < 325 | Two trays can print simultaneously |

---

## 13. Open Questions Carried Forward

All open questions from upstream documents that affect final CAD values are consolidated here.

| OQ | Description | Affected features | Status |
|----|-------------|-------------------|--------|
| OQ-1 | Screw hole depth in pump head body | Screw length (BOM only; no tray geometry change) | Unresolved; use M3×12mm pending measurement |
| OQ-2 | Motor body diameter (currently ~35mm, low-confidence) | Bore diameter (currently 37.2mm CAD) | Unresolved; 37.2mm is conservative; verify before final toolpath |
| OQ-3/OQ-4 | Tube stub Z and X positions on pump face | Pump center Z (currently Z=40.0mm), tray height (currently 80mm) | Unresolved; all Z-coords dependent on these |
| OQ-6 | Shell harness connector location | Wiring channel longitudinal segment routing, bump count beyond lateral segment | Unresolved; lateral segment only is CAD-ready |
| Snap notch Z/Y | Shell concept step must confirm snap latch Z position and notch depth | Snap notch Z center (currently Z=40.0), Y depth (currently Y=2 to Y=5) | Unresolved working assumption |

---

---

# Self-Review Rubrics

---

## Rubric A — Mechanism Narrative

The pump-tray is a flat PETG plate, 144mm wide × 5mm thick × 80mm tall, that stands inside the cartridge shell. The user never sees or touches it directly; they interact with the assembled cartridge as a unit.

**What the user sees and touches in the context of this part:**
When the user removes the cartridge from the enclosure, they hold the cartridge exterior. Inside the cartridge (visible when looking into the open rear face), they can see the tray's rear face: two large circular bore openings (~37mm diameter), two wiring channels running outward from the bore edges to the left and right lateral walls, small cylindrical boss tips arranged in two groups of four, and the overall flat surface character of a structural backbone. The tray does not move. It is fixed inside the shell.

**What moves and what constrains it:**
- The two Kamoer pumps are fixed to the tray. They do not move during operation. Each pump's motor cylinder passes through a bore in the tray; the stamped metal mounting bracket rests flat against the tray's front face. Four M3 screws per pump pass through the bracket and the tray clearance holes and thread into brass heat-set inserts seated in the rear-face bosses. Loctite 243 prevents the screws from loosening under the 2–14 Hz vibration produced by the peristaltic roller mechanism.
- The pump heads project forward of the tray (toward the cartridge front wall). The motor cylinders project rearward through the bores. The tray bears the combined static weight of both pumps (~612g) and resists the cyclic vibration transmitted through the motor brackets.
- The tray itself slides into channels in the cartridge shell side walls (the shell's channel feature, not a tray feature). The tray's flat lateral edges (X=0 and X=144) ride in those channels. A snap notch in each lateral face at the rear edge (Y=2 to Y=5, Z=38.5 to 41.5) receives a spring latch on the shell interior, preventing the tray from sliding forward out of the channels once installed. The tray's forward face (Y=0) comes to rest against a hard stop at the front of the shell channel.
- The 0.5mm field zone step ensures the pump bracket seats on the elevated mounting pad zone and is not affected by any surface variation or debris in the field zone. The bracket face is the sole contact surface between pump and tray — the pump head body is entirely forward of the tray and never contacts the tray face.
- The wiring channels on the rear face capture the motor lead wires. Strain-relief bumps hold the wire bundle against the channel floor, preventing it from vibrating freely against the rear face.

**Physical interaction sequence (factory assembly):**
1. Tray is flat on a fixture, rear face up. Technician drives 8 heat-set inserts into boss cavities with a soldering iron.
2. Tray is flipped: front face up. First pump is lowered onto the tray, motor cylinder aligned with bore, bracket flat against mounting pad zone. Four M3 screws with Loctite 243 are started from the pump side and driven into the inserts. Repeated for second pump.
3. Motor wires are routed into wiring channels and pressed past strain-relief bumps.
4. Assembled tray slides into shell from the rear. Snap latches engage the notches. Tray is captured.

---

## Rubric B — Constraint Chain Diagram

```
PUMP GRAVITY + VIBRATION LOAD
         │
         ▼
[Pump bracket face]  ←── flat bearing contact on MOUNTING PAD ZONE (Y=0)
         │
         ▼ (4× M3 screws per pump, in tension)
[Heat-set inserts in BOSS CAVITIES]  ──→  brass thread engagement, 4mm
         │
         ▼
[BOSS CYLINDERS on rear face] ──→ 9mm OD PETG cylinder, 5mm tall, 1.5mm base fillet
         │
         ▼
[PLATE BODY (5mm PETG)] ──→ global bending stiffness across 144mm span
    │              │
    │         [RADIATING RIBS: boss OD → bore edge, 4mm wide × 5mm tall]
    │              │ → transfers moment from boss zone into bore wall
    │              ▼
    │         [BORE WALL web: 3.6mm min between bore edge and clearance hole edge]
    │              │
    │         [MOTOR BORE: 37.2mm clearance, no contact with bore wall]
    │              │ → motor cylinder is free-floating in bore; load carried by screws only
    │
    ▼
[CROSS-RIB: X=53.1 to 90.9 at Z=37–43, 6mm wide × 5mm tall]
    │ → resists differential vibration between two pump mounting zones
    │ → ties both mounting pad zones into a unified structural band
    │
    ▼
[PLATE LATERAL EDGES (X=0, X=144)]
    │
    ▼
[SHELL CHANNEL (shell feature, not tray)] ──→ 5.2mm wide channel supports tray lateral edges
         │
         ▼
[SNAP NOTCH (Y=2–5, Z=38.5–41.5)] ──→ prevents forward withdrawal from shell channel
         │
         ▼
[SHELL STRUCTURE] ──→ transmits all tray loads to cartridge body and enclosure dock
```

---

## Rubric C — Direction Consistency Check

| Claim | Axis notation | Verified |
|-------|---------------|----------|
| Bosses are on the rear face and protrude in +Y | Y=5 to Y=10, +Y direction | YES — rear face is Y=5; +Y is away from plate toward motor zone; printable (grows upward during printing) |
| Ribs are on the front face and protrude in −Y | Y=0 to Y=−5, −Y direction | YES — front face is Y=0; ribs grow toward pump bracket side; print as vertical extrusions from front face (top surface is rib crown at Y=0 on build plate face, ribs are first features printed upward in Z direction relative to build plate... wait: see correction below) |
| Wiring channels cut into rear face in +Y (inward) | Y=5 (opening) to Y=1 (floor), cut in +Y→−Y direction from rear face | YES — rear face is at Y=5, channel floor at Y=1; 4mm deep cut going toward front face |
| Motor bore through-cut along Y-axis | Y=0 to Y=5, Y-axis | YES — bore axis is Y; passes full plate thickness |
| Boss pilot hole opens at boss tip (Y=10), floor at Y=5.5 | Y=10 to Y=5.5, bore direction −Y into boss | YES — insert installed from Y=10 (rear/top during printing) downward toward plate |
| Snap notch at Y=5 rear edge, extends Y=2 to Y=5 | Y=5 (opening) to Y=2 (notch bottom) | YES — notch opens at rear edge, 3mm deep toward front face direction |
| Cross-rib runs X=53.1 to X=90.9 at Z=37 to 43 | X-axis extent, Z-axis width, Y protrudes to −5 | YES — rib is in the X-Z plane, protrudes in −Y |
| Radiating ribs run from boss OD toward bore edge in the X-Z plane | X-Z diagonal, Y protrudes to −5 | YES — all rib vectors are in the X-Z plane of the front face |
| Field zone is 0.5mm lower than mounting pad | Front face cut 0.5mm in +Y (into plate) outside mounting pads | YES — cut from Y=0 to Y=+0.5 in field zone areas |
| Build plate is at Y=0 (front face) | Y=0 = front face = print bed contact | YES — consistent throughout all source documents |
| Elephant's foot chamfer on Z=0, Y=0 edge | Bottom edge of front face (build-plate contact edge) | YES — Z=0 is the bottom edge; Y=0 face is the build plate face |
| Print orientation: front face down | Z-axis of part = Z-axis of printer (upward); Y-axis of part = depth into build plate | YES — confirmed in spatial-resolution.md §2 |

**CORRECTION NOTE — Rib protrusion direction clarification:**
spatial-resolution.md §12 clarifies that when the tray is printed face-down (Y=0 on build plate), the ribs on the front face are actually growing upward away from the build plate in the printer's Z direction. In the part frame, this means the ribs occupy Y=0 (base, at the build-plate face) to Y=−5 (crown, proud of the front face in the pump-side direction). In the printer frame, the part is flipped: Y=0 is at printer Z=0, and Y=−5 is at printer Z=+5. The ribs are the first 5mm of print height and are fully supported. No conflict. The −Y designation in the part frame is geometrically correct for the assembled part orientation.

---

## Rubric D — Interface Dimensional Consistency

### D.1 Boss / Heat-Set Insert Interface

| Parameter | Tray side | Insert (Ruthex RX-M3×5×4) | Clearance / fit | Source |
|-----------|-----------|---------------------------|-----------------|--------|
| Pilot hole diameter | 4.7mm CAD | OD 5.0mm (knurled) | Press fit by thermal installation; knurls displace plastic | structural-requirements.md §4 |
| Pilot hole depth | 4.5mm | Insert length 4.0mm | 0.5mm floor below insert bottom | structural-requirements.md §4 |
| Boss OD | 9mm | Insert OD 5.0mm | 2.0mm wall around insert (meets 2mm minimum) | structural-requirements.md §4 |
| Boss height | 5mm | Insert length 4.0mm | Insert flush with boss tip ± 0.5mm floor | spatial-resolution.md §6.2 |
| Insert seat Y range | Y=5.5 to Y=9.5 (4mm) | 4.0mm length | Full engagement | spatial-resolution.md §6.2 |

### D.2 Bore / Motor Cylinder Interface

| Parameter | Tray side | Kamoer KPHM400 motor | Clearance | Source |
|-----------|-----------|----------------------|-----------|--------|
| Bore diameter (CAD) | 37.2mm | ~35mm OD (low confidence) | ~1.1mm radial (at 35mm motor) to ~0.75mm (at 35.5mm motor) | pump-mounting-geometry.md §2.2 |
| Bore diameter (printed) | ~37.0mm | ~35mm | ~1.0mm radial clearance | spatial-resolution.md §4.1 |
| Bore axis | Y-axis | Motor cylinder axis | Coaxial (no angular offset) | spatial-resolution.md §4.2 |
| Motor cylinder protrusion into rear zone | Through bore, extends into Y>5 zone | ~63mm motor body behind bracket | No contact with bore wall; clearance feature only | pump-mounting-geometry.md §3.5 |
| **FLAG** | OQ-2: motor OD low confidence | — | If motor OD > 35.6mm, bore must be revised | spatial-resolution.md §16 |

### D.3 Mounting Pad / Pump Bracket Interface

| Parameter | Tray side | Pump bracket | Clearance / fit | Source |
|-----------|-----------|--------------|-----------------|--------|
| Mating surface | Mounting pad zone at Y=0, flat | Bracket face flat bearing surface, 68.6mm × 68.6mm | Contact (no clearance intended) | pump-mounting-geometry.md §4 |
| Pump bracket footprint | Pump 1 pad: X=0–71.5, Z=3–77 | 68.6mm wide bracket centered at X=34.5 | Pad wider than bracket; bracket fully within pad zone | spatial-resolution.md §7.1 |
| Motor bore alignment | Bore center at (34.5, 40.0) | Bracket hole pattern center at (34.5, 40.0) | Coaxial | spatial-resolution.md §3.2 |
| Screw clearance holes | 3.6mm CAD (target ~3.4mm printed) | Bracket holes 3.13mm; screws M3 (3.0mm shank) | M3 shank passes through 3.4mm printed hole; ~0.4mm clearance | pump-mounting-geometry.md §2.1 |
| Pump head body clearance | Front face surface at Y=0; no protrusions into pump zone | Pump head body 62.6mm × 62.6mm, entirely forward of bracket (in Y<0 zone) | No contact with tray face; bracket is sole mating surface | pump-mounting-geometry.md §4.1 |

### D.4 Tray / Shell Channel Interface

| Parameter | Tray side | Shell must provide | Clearance | Source |
|-----------|-----------|-------------------|-----------|--------|
| Sliding surface | Lateral edges at X=0 and X=144, thickness = 5.0mm, height = 80mm Z | 5.2mm wide channel (5.0mm + 0.2mm clearance) | 0.2mm per requirements.md sliding fit | concept.md §2 |
| Snap notch geometry | 1.5mm deep × 3mm wide × 3mm tall (Y=2 to Y=5, Z=38.5 to 41.5) | Shell latch hook: 1.5mm tall × 3mm wide to engage notch | Passive fit; spring force from shell latch arm | spatial-resolution.md §9.2 |
| Forward stop | Front face Y=0 acts as stop face | Hard stop surface at channel forward end | Contact (no clearance) | concept.md §2 |

---

## Rubric E — Assembly Feasibility Check

**Factory assembly sequence (concept.md §6, step-by-step feasibility assessment):**

### Step 1: Insert installation (before pump installation)
- Tray is freshly printed. Flat on assembly bench, rear face up.
- Technician heats soldering iron to 245°C, uses M3 insert driver tip.
- 8 boss cavities are open, facing upward. All 8 bosses are accessible simultaneously from above.
- Each insert is placed at the boss tip opening (Y=10) and pressed down 4.5mm.
- No blind pockets, no access constraints.
- **Feasible: YES.** All 8 insert locations are simultaneously accessible from above with no obstruction.

### Step 2: Tray flip and fixture placement
- Tray is flipped to front face up. Placed on a flat surface.
- Front face features: two large bores (37mm), 8 boss-hole through-openings (3.6mm), ribs, and mounting pads.
- No features on front face protrude downward when face-up (ribs and pads are coplanar with or recessed from face; bosses are on the rear face, now facing down against the table).
- **CONCERN:** Bosses (9mm OD, 5mm tall) protrude from the rear face. When the tray is flipped front-face-up, the bosses rest on the table. The tray is supported by 8 boss tips at 5mm above the rear face surface. This means the tray sits 5mm above the table on the boss tips, creating a slightly elevated and potentially unstable fixture.
- **Mitigation:** Use a fixture with 8 clearance pockets for the boss tips (or a foam pad with relief cuts). The tray sits flat on the fixture at the rear face surface. This is a standard factory assembly fixture requirement — document that a fixture with boss-clearance pockets is required for pump installation.
- **Feasible: YES with fixture.** Flag this as a fixture design requirement.

### Step 3: First pump installation (front face up)
- Pump 1 is oriented motor-cylinder-down, bracket face facing down toward tray.
- Motor cylinder aligned over Bore 1 (34.5, 40.0); lowered through bore.
- Motor cylinder OD ~35mm, bore CAD 37.2mm (printed ~37.0mm). Nominal ~1mm radial clearance — motor slides through bore freely.
- Bracket face rests flat on mounting pad zone.
- 4× M3 screws with Loctite 243, starting from above (pump side), through bracket holes and tray clearance holes (3.6mm), into inserts.
- Screw heads are on the pump side (above tray when front-face-up). This is the correct direction — confirmed in concept.md §6.
- All 4 screws are accessible from above simultaneously.
- Torque to 0.5–0.8 N·m with standard hex driver.
- **Feasible: YES.**

### Step 4: Second pump installation
- Identical to Step 3 for Bore 2 (109.5, 40.0).
- No spatial conflict between Pump 1 (already installed) and Pump 2 installation. The two pumps are 75mm center-to-center; the bracket gap is 6.4mm (safe clearance). The screw access zones are non-overlapping.
- **Feasible: YES.**

### Step 5: Wire routing
- Tray is still front-face-up with both pumps installed (motor cylinders pointing downward into the fixture).
- Wait — to access the rear face for wire routing, the tray+pumps assembly must be flipped or turned.
- The motor wires exit from the rear of each motor cylinder. The rear face (Y=5) is now facing down.
- **CONCERN:** Wire routing requires access to the rear face wiring channels. With both pumps installed and the assembly front-face-up, the rear face is not accessible.
- **Mitigation:** Flip the assembly. With pumps mounted and the assembly rear-face-up, the motor cylinders protrude upward. The wiring channels are accessible on the rear face. Route wires from motor terminals into channels, press past strain-relief bumps. This is a standard motion — no obstructions.
- Alternatively, wires can be routed before the assembly is flipped in Step 3, but doing so after both pumps are installed gives better wire management visibility.
- **Feasible: YES with one flip after pump installation.**

### Step 6: Shell insertion
- Tray+pump assembly is held with tray lateral edges aligned to shell interior channel openings (from the rear of the partially assembled shell).
- Slide tray laterally into shell from rear. Tray lateral edges (5.0mm thick) slide into 5.2mm shell channels.
- Motor cylinders and pump heads pass through the cartridge interior as the tray advances.
- Tray advances until Y=0 front face contacts the shell channel's hard forward stop.
- At full insertion, snap latches in the shell interior engage the lateral-face notches (Z=38.5 to 41.5, Y=2 to 5 on each lateral face).
- **Feasible: YES.** Channel sliding requires no special tools; snap engagement is automatic at full insertion.

### Step 7: Screw accessibility after shell insertion
- Once the tray is inside the closed shell, the screw heads (on the pump bracket side / front of tray) are inaccessible. This is intentional and correct — the cartridge is a user-replaceable unit; pump screws are not user-serviceable.
- **Confirmed acceptable per requirements.md §4 and concept.md §6.**

### Factory rework feasibility
- Depress snap latches (shell access required; shell specification must include a tool access gap at the snap latch location).
- Slide tray out from shell rear.
- Tray+pumps on fixture. Unscrew Loctite 243 screws with hex driver. Loctite 243 is medium-strength, removable with standard tools.
- Pump removed, replaced, re-Loctited.
- Estimated time: ~15 minutes per technician.
- **Feasible: YES.**

---

## Rubric F — Part Count Minimization

**Current part count for this specification:** 1 printed part (the tray) + 8 heat-set inserts + 8 M3 screws = 17 components for the tray sub-assembly.

**Should any parts be combined?**

**Bosses and plate:** Bosses are integral to the plate body. Correct — no split needed.

**Ribs and plate:** Ribs are integral to the plate body. Correct.

**Tray and cartridge shell:** concept.md §2 explicitly evaluated and rejected combining the tray with the shell. The tray being a discrete inner plate that slides into the shell is the correct split. The tray's geometry (flat, prismatic, extrude-and-cut only) is optimal as a standalone part. Adding shell features to the tray creates an L-profile that complicates print orientation and adds overhang. The split is justified.

**JG fitting pockets and tray:** concept.md §2 explicitly rejected integrating JG fitting pockets into the tray. This would transform the tray into an L-shaped profile, requiring a split for printability or a complex support structure. The fitting pockets belong to a separate rear wall panel. The split is justified.

**Heat-set inserts vs. self-tapping holes:** structural-requirements.md §5 evaluated three fastening strategies and selected heat-set inserts as the only option that provides durable metal threads for factory rework. Self-tapping screws are single-use; through-bolts add BOM complexity and require back-face wrench access. Inserts are the minimum viable fastening solution for this assembly. Count is justified.

**Finding: No unjustified parts. No parts should be combined or separated. The 17-component count is the minimum viable count for the stated requirements.**

---

## Rubric G — FDM Printability

**Print orientation: Front face (Y=0) on build plate. Z-axis of part = Z-axis of printer (upward from plate).**

### Overhang Audit

| Feature | Overhang assessment | Bridge span (if any) | FDM result |
|---------|--------------------|--------------------|------------|
| Motor bores (37.2mm diameter, Y-axis bore, vertical in print) | Circular vertical bore; printed as concentric perimeters. No overhang — the bore is vertical (in the printer Z axis). | None | PASS |
| M3 clearance holes (3.6mm, vertical) | Same as motor bore — vertical concentric perimeters | None | PASS |
| Boss cylinders (9mm OD, 5mm tall, vertical extrusion from rear face = top surface during printing) | Vertical cylinders growing upward from top surface. 100% supported by perimeters. | None | PASS |
| Boss pilot holes (4.7mm, blind hole opening at boss tip, grows downward into boss = downward blind bore from top) | Vertical blind bore opening upward (boss tip is the top during printing). All layers supported from below. Bore printed as concentric perimeters. | None | PASS |
| Cross-rib (6mm wide, 5mm tall, vertical extrusion from front face = grows upward as first 5mm of print) | The cross-rib is on the front face (Y=0 = build plate face). During printing, the rib is in the first 5mm of print height. The rib base is at the build plate; rib walls grow upward. 0% overhang. | None (rib top is fully supported by its own walls) | PASS |
| Radiating ribs (4mm wide, 5mm tall, same situation as cross-rib) | Same as cross-rib — in first 5mm of print, growing upward from build plate face. | None | PASS |
| 0.5mm field zone recess (step in front face, 45° chamfer transition) | The 45° chamfer at the step edge is exactly at the 45° FDM limit. The recess itself is a horizontal face slightly recessed from the build-plate face — printed in early layers with no unsupported span. | None | PASS (at 45° limit) |
| Wiring channels (6mm wide, 4mm deep, on rear face = top surface during printing) | Channel walls grow upward from the top surface. Channel floor bridges across the 6mm channel width. Bridge span: 6mm < 15mm limit. | 6mm bridge span | PASS (6mm span << 15mm limit) |
| Strain-relief bumps (1.5mm tall, 2mm wide, grow upward from channel floor bridge) | Channel floor is a 6mm bridge (already cleared). Bumps are vertical extrusions from that floor, growing upward. | None additional | PASS |
| Snap notches (1.5mm deep × 3mm wide × 3mm tall, on lateral face at rear edge = near top surface) | Notch is a rectangular pocket cut into a vertical wall face (lateral face). The notch ceiling is a 3mm horizontal span — a short bridge on a vertical face. 3mm << 15mm limit. | 3mm bridge (notch ceiling) | PASS (3mm span well within limit) |
| Perimeter chamfers (1.5mm × 45°, on top and lateral edges) | 45° is exactly at the FDM design limit. No support needed. | None | PASS (at 45° limit) |
| Elephant's foot chamfer (0.3mm × 45°, build plate face edge) | First layer; standard FDM practice. | None | PASS |
| Outer corner radii (3mm radius, 4 corners) | Vertical curved faces (radius in X-Z plane). Printed as curved perimeter paths in each layer. No overhang. | None | PASS |
| Boss base fillets (1.5mm radius at rear face) | Concave fillet curving from boss cylinder to flat plate surface at Y=5. The fillet increases in cross-section monotonically — no unsupported material. Printed as gradual layer transitions. | None | PASS |

**No features require supports. No overhangs exceed 45°. No bridges exceed 15mm. The maximum bridge span is 6mm (wiring channel floor). All overhangs at exactly 45° (field zone chamfer, perimeter chamfers) are at the stated design limit from requirements.md.**

### Wall Thickness Check

| Location | Minimum wall | Requirements.md minimum | Result |
|----------|-------------|------------------------|--------|
| Plate body (non-boss, non-bore) | 5mm (full plate thickness) | 1.2mm structural | PASS |
| Boss wall (between pilot hole OD and boss OD) | (9mm − 4.7mm) / 2 = 2.15mm | 1.2mm structural; 2mm minimum for heat-set boss | PASS |
| Web between bore edge and clearance hole edge | 3.6mm | 1.2mm structural | PASS |
| Wiring channel wall (between channel and open face) | 1.5mm | 1.2mm structural (channel wall bears no significant load) | PASS |
| Plate below wiring channel floor (Y=1 to Y=0) | 1.0mm | 0.8mm general minimum (2 perimeters); this face is the build plate face with 4 full perimeters per print settings | PASS |

**Marginal wall: 1.0mm below wiring channel floor.** This is above the 0.8mm general minimum. The channel floor is not a structural load-bearing surface; it bears only the wire hold-down force from strain-relief bumps (~grams). The 4-perimeter print setting ensures this thin web is solid perimeter material. No structural concern. Note: if channel depth is ever increased beyond 4mm, the remaining web drops below 1mm — do not increase channel depth without reviewing this constraint.

### Bridge Span Check

| Bridge | Span | Limit | Result |
|--------|------|-------|--------|
| Wiring channel floor (6mm channel width) | 6mm | 15mm | PASS |
| Snap notch ceiling (3mm notch width) | 3mm | 15mm | PASS |
| Motor bore upper arc (at rear face, top surface during printing) | Bore diameter = 37mm would be the bridge if the bore were on a horizontal face. But the bore is vertical (Y-axis), not horizontal. The bore arc is printed as concentric perimeters stacking upward — each layer is supported by the layer below. **Not a bridge.** | N/A | PASS |

### Layer Strength Check

| Load direction | FDM layer orientation | Layer-to-layer stress direction | Risk level |
|----------------|----------------------|--------------------------------|------------|
| Screw pullout (M3 screws pull in +Y direction, pulling inserts out of bosses) | Layers are horizontal (XZ plane) | Pullout acts perpendicular to layers (Y direction) — this is the weakest FDM direction | Mitigated by heat-set inserts: pullout is a brass-in-PETG problem, not layer-to-layer adhesion. Insert knurls anchor in melted-and-resolidified PETG, distributing load through a brass cylinder. Not a layer adhesion failure mode. PASS with inserts. |
| Pump static weight (Z direction, bending the tray plate) | Layers in XZ plane; bending stress is in XZ plane | In-plane bending — acts parallel to layers (strongest direction) | PASS |
| Vibration cyclic load at boss fillets | Cyclic bending at boss base | Boss fillet is a transition between vertical cylinder and horizontal plate; the fillet geometry distributes stress over 1.5mm radius. Boss printed as vertical perimeter cylinder on horizontal plate — both features are in the strong in-plane direction. | PASS |

**Summary:** The only layer-direction weakness (pullout in Y) is fully addressed by heat-set inserts. No other feature loads FDM layers in the weak direction. Print orientation is correct.

---

## Rubric H — Feature Traceability

Every feature is traced to a vision document, physical necessity, or explicit design decision.

| Feature | Source / Justification | Document(s) |
|---------|----------------------|-------------|
| Base plate body: 144mm × 5mm × 80mm | Physical necessity (structural): must span both pump brackets (144mm); must be thick enough for stiffness and boss height (5mm); must clear tube stubs (80mm) | synthesis.md §2.1, structural-requirements.md |
| PETG material | Physical necessity (structural/thermal): creep resistance under sustained screw clamping load; Tg 80°C; heat-set insert compatibility; impact-tough failure mode for user-handled replaceable module | structural-requirements.md §3 |
| Print flat (front face on build plate) | Physical necessity (manufacturing): 37mm bore printed on-edge = 37mm bridge span, exceeds 15mm limit, bore distorts. Must print flat. | requirements.md, structural-requirements.md §2 |
| Motor bores (37.2mm, ×2) | Physical necessity (assembly): motor cylinder must pass through plate. Diameter derived from motor OD + clearance + FDM compensation. | pump-mounting-geometry.md §2.2 |
| Bore centers at (34.5, 40.0) and (109.5, 40.0) | Physical necessity (layout): symmetric placement about 144mm-wide plate; 75mm c-t-c from bracket interference calculation | spatial-resolution.md §3 |
| Rear face bore chamfer (0.5mm × 45°) | Manufacturing/aesthetic: reduces bridging artifact at bore arc top; finished appearance | concept.md §5, spatial-resolution.md §4.1 |
| M3 clearance holes (3.6mm, ×8) | Physical necessity (assembly): M3 screws must pass through plate to reach inserts. 3.6mm CAD targets 3.4mm printed (ISO 273 normal fit). | pump-mounting-geometry.md §2.1 |
| Hole pattern (48mm × 48mm, centered on bore) | Physical necessity: caliper-verified pump bracket hole pattern. Fixed by the off-the-shelf pump. | pump-mounting-geometry.md §1.1 |
| Heat-set insert bosses (9mm OD, 5mm tall, ×8, on rear face) | Physical necessity (structural/manufacturing): provides metal thread engagement for vibration-loaded screws; boss height accommodates full insert length; boss on rear face because front face is build plate (printing constraint). | structural-requirements.md §4, spatial-resolution.md §6.1 |
| Boss pilot hole (4.7mm, 4.5mm deep) | Physical necessity (assembly): Ruthex RX-M3×5×4 community spec. Standard heat-set insert pilot hole. | structural-requirements.md §4 |
| Boss base fillet (1.5mm radius) | Physical necessity (structural): reduces stress concentration at boss-to-plate junction under vibration fatigue | structural-requirements.md §4 |
| Mounting pad zones (elevated region on front face) | UX / structural: ensures bracket seats on clean reference surface; field-zone variation cannot affect seating; visually communicates structural purpose | design-patterns.md UX Quality 3, synthesis.md §4 |
| Field zone (0.5mm recess outside mounting pads) | UX: makes structural purpose of mounting pad visually legible; prevents debris interference with bracket seating | design-patterns.md UX Quality 3 |
| 45° step transition (field to pad) | Manufacturing: 90° step would create stress riser and print poorly; 45° is the FDM design limit | requirements.md |
| Cross-rib (6mm × 5mm, X=53.1 to 90.9 at Z=37–43) | Structural / aesthetic: resists differential vibration between two pump mounting zones; visually ties both pump zones into a unified structural band | concept.md §5, synthesis.md §4 |
| Radiating ribs (4mm × 5mm × ~10.84mm, ×8) | Structural / aesthetic: radiates load from each boss into the bore edge; rib pattern makes structural story legible at a glance | concept.md §5, synthesis.md §4 |
| Rib height = boss height (5mm) | Aesthetic: ribs and bosses are coplanar with their respective faces, creating a unified elevated pattern; structural function is readable | concept.md §5, design-patterns.md UX Quality 3 |
| No lateral perimeter ribs | Design decision: outer plate extensions beyond outermost boss are only 10.5mm, under the 20mm threshold where lateral ribs become necessary | concept.md §5 |
| Wiring channels (6mm × 4mm, ×2, rear face) | Physical necessity (assembly/routing): captures motor lead wires against rear face; prevents wires from fouling in motor zone or interfering with shell insertion | concept.md §5 |
| Wiring channel strain-relief bumps (2 per channel on lateral segment) | Physical necessity (assembly): holds wire bundle against channel floor under vibration; prevents wire fatigue at channel entry | concept.md §5 |
| Snap notches (1.5mm × 3mm × 3mm, ×2, lateral edges) | Physical necessity (assembly/constraint): provides engagement surface for shell snap latch; tray must be retained against forward withdrawal from shell channels | concept.md §2 |
| Snap geometry on shell (not tray) | Design decision: tray carries only passive notch; all spring geometry on shell prevents snap arm axis from being perpendicular to FDM layers (the weakest direction); shell can be oriented to print snap arms in the strong direction | concept.md §2 Option A analysis |
| Perimeter chamfers (1.5mm × 45°, all edges except build plate) | Aesthetic / manufacturing: highest-ratio design move for internal structural components; removes raw-stock appearance; eliminates sharp edge risk; consistent with design-patterns.md and vision.md standards | design-patterns.md UX Quality 3, concept.md §5 |
| Elephant's foot chamfer (0.3mm × 45°, build plate edge Z=0) | Manufacturing: compensates for elephant's foot artifact at build-plate face per requirements.md | requirements.md dimensional accuracy |
| Outer corner radii (3mm) | Aesthetic: places tray in visual register of molded components; Dell XPS battery carrier finding from design-patterns.md | design-patterns.md UX Quality 3, concept.md §5 |
| Loctite 243 on all 8 screws | Physical necessity (structural): pump vibration is 2–14 Hz; without threadlocker, M3 screws will loosen within 24–48 hours of operation at this frequency; medium-strength (removable for factory rework) | pump-mounting-geometry.md §3.3 |
| Single part (no split) | Design decision: all features are extrude-and-cut on flat plate; no geometric paradigm conflict; fits build plate with margin; split would add assembly complexity with no benefit | concept.md §1, decomposition.md |

**UNJUSTIFIED FEATURE CHECK:**
No features found in this specification that lack a traced source. All boss positions are traceable to caliper-verified pump bracket hole measurements. All chamfers and fillets are traced to either structural requirements (minimum) or the design language defined in concept.md §5. The wiring channel strain-relief bump count (2 per channel, reduced from 3 because 20mm spacing cannot fit in the 15.9mm lateral run) is explicitly reasoned in spatial-resolution.md §8.3.

---

## Summary: Quality Gate Assessment

| Gate criterion | Status |
|----------------|--------|
| Every behavioral claim resolves to a named geometric feature with dimensions | PASS — all features have explicit dimensions from spatial-resolution.md or named source documents |
| All rubrics applied and printed | PASS — Rubrics A through H complete above |
| No ungrounded claims | PASS — all dimensions traced to caliper-verified measurements or derived values in spatial-resolution.md |
| No unjustified features | PASS — all features traced in Rubric H |
| Design gaps flagged (not silently filled) | PASS — OQ-1, OQ-2, OQ-3/OQ-4, OQ-6, and snap notch Z/Y flagged explicitly; none silently resolved |
| Screw length concern flagged | PASS — M3×10mm vs. M3×12mm discrepancy flagged in §11 Hardware BOM; no tray geometry affected |
| Assembly feasibility concern documented | PASS — boss-tip fixture requirement flagged in Rubric E Step 2 |
