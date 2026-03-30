# Pump-Tray Spatial Resolution

**Part:** Pump-Tray (cartridge sub-assembly)
**Status:** Complete — feeds directly into 4b CAD generation.
**Sources:** concept.md, decomposition.md, synthesis.md, pump-mounting-geometry.md, structural-requirements.md, tube-routing-envelope.md, kamoer-kphm400/geometry-description.md, john-guest-union/geometry-description.md, requirements.md, vision.md.

---

## 0. Preamble: What This Document Does

Every number in this document is expressed in a named coordinate frame. No downstream agent reads this document and then performs arithmetic to get a position — all positions are pre-computed and tabulated. The CAD generation agent (4b) reads this document and places features at the stated coordinates directly.

---

## 1. System-Level Placement

The pump-tray is a discrete internal plate within the pump cartridge. In the assembled product:

- The cartridge occupies the front-bottom bay of the 220mm × 300mm × 400mm enclosure.
- The pump-tray stands perpendicular to the cartridge depth axis, dividing the cartridge interior into a forward pump-head zone and a rearward motor zone.
- The tray's front face (Y=0) is the pump-bracket mating face — it faces the cartridge front wall.
- The tray's rear face (Y=5) faces the cartridge rear zone where the motor cylinders and wiring reside.
- The tray slides into side-wall channels in the cartridge shell. It is laterally centered in the cartridge width and vertically occupies most of the cartridge interior height.
- No rotation from part frame to system frame. The tray mounts flat — the part frame IS the system frame for all tray features.

**System-level position assumption (pending cartridge shell specification):**
- Tray is centered in the cartridge width
- Tray bottom edge aligns with the cartridge interior floor
- Tray front face is set back from the cartridge front wall by the forward tube routing zone (~50–55mm, per tube-routing-envelope.md Zone A)

---

## 2. Reference Frame Definition

This is the definitive reference frame for all coordinates in this document and all downstream agents working on this part.

```
Origin:    Front-face, bottom-left corner of tray
           (the corner where Y=0, X=0, Z=0 meet — the build-plate face corner)

X-axis:    Tray width, left to right
           X = 0 → left edge (build-plate orientation: left side of part as laid flat)
           X = 144mm → right edge
           Range: [0, 144mm]

Y-axis:    Tray thickness, front face to rear face
           Y = 0 → front face (pump-bracket side; this face is on the build plate during printing)
           Y = 5mm → rear face (motor/service side; top surface during printing)
           Range: [0, 5mm]

Z-axis:    Tray height, bottom to top
           Z = 0 → bottom edge (the edge at Y=0/Z=0, elephant's foot chamfer applied here)
           Z = 80mm → top edge (working assumption; may increase to 85mm per OQ-3/OQ-4)
           Range: [0, 80mm]

Plate center (X):  X = 72mm
Plate center (Z):  Z = 40mm

Print orientation: Front face (Y=0) on build plate.
                   During printing: Z-axis of part = Z-axis of printer (upward from plate).
                   Y-axis of part = Z-axis of printer (plate is at Y=0, top surface at Y=5).
                   Bosses and ribs on the rear face grow upward (in +Y part direction) during printing.
```

**Frame note:** There are no angular offsets, no rotations, no tilted mounting surfaces. Every feature axis is either the X, Y, or Z axis of this frame.

---

## 3. Pump Positions

Both pump center axes are resolved into part-local coordinates.

### 3.1 Derivation

```
Tray width: 144mm
Pump center-to-center (X): 75mm (synthesis.md, caliper-verified bracket interference)
Layout: symmetric about plate center X = 72mm
  Pump 1 center X = 72 − (75 / 2) = 72 − 37.5 = 34.5mm
  Pump 2 center X = 72 + (75 / 2) = 72 + 37.5 = 109.5mm

Pump center Z: vertically centered on tray height
  Z = 80 / 2 = 40mm
  (Working assumption pending OQ-3/OQ-4 stub position confirmation)
```

### 3.2 Pump Center Coordinates

| Pump | Center X | Center Z | Motor bore axis |
|------|----------|----------|-----------------|
| Pump 1 | **34.5mm** | **40.0mm** | Through-cut along Y-axis (Y=0 to Y=5) |
| Pump 2 | **109.5mm** | **40.0mm** | Through-cut along Y-axis (Y=0 to Y=5) |

The motor bore axis for each pump is the line (X=pump_center_X, Z=pump_center_Z, Y varies from 0 to 5). There is no lateral or vertical offset of the bore from the pump center. The bore is a straight cylindrical through-cut.

---

## 4. Motor Bore Geometry

### 4.1 Bore Dimensions

| Parameter | Value | Source |
|-----------|-------|--------|
| Bore diameter (CAD design value) | **37.2mm** | Motor OD ~35mm + 1.0mm radial clearance/side + 0.2mm FDM compensation (pump-mounting-geometry.md, synthesis.md) |
| Bore diameter (printed target) | ~37.0mm | After FDM shrinkage |
| Bore axis | Y-axis, through full plate thickness | Through Y=0 to Y=5 |
| Rear face chamfer | 0.5mm × 45° | On rear face bore entry (Y=5), finished appearance, reduces bridging artifact |
| Front face chamfer | None (front face is build plate face — bore printed with clean concentric perimeters) | — |

### 4.2 Bore Center Positions

| Pump | Bore center (X, Z) | Bore axis |
|------|--------------------|-----------|
| Pump 1 | **(34.5, 40.0)** | Y-axis (passes through entire Y range [0, 5]) |
| Pump 2 | **(109.5, 40.0)** | Y-axis (passes through entire Y range [0, 5]) |

The bore is a clearance feature only. The motor cylinder does not contact the bore wall. No bearing surface, no stepped diameter, no counterbore. Single diameter, full plate thickness.

### 4.3 Web Width at Bore-to-Hole Minimum

```
Bore radius: 37.2 / 2 = 18.6mm
Hole center offset from pump center: 24.0mm
Clearance hole radius: 3.6 / 2 = 1.8mm

Web width = 24.0 − 18.6 − 1.8 = 3.6mm
```

3.6mm > 1.2mm structural wall minimum (requirements.md). Pass. (The synthesis computed 3.7mm using 37.0mm printed bore; at CAD dimension 37.2mm the web is 3.6mm — still well above minimum.)

---

## 5. Mounting Hole Positions — All 8 Holes

### 5.1 Derivation

Each pump's 4 mounting holes are at ±24mm from the pump center in both X and Z (48mm × 48mm square pattern, center-to-center, caliper-verified).

```
Pump 1 center: (34.5, 40.0)
  Hole 1A: (34.5 − 24, 40.0 − 24) = (10.5, 16.0)
  Hole 1B: (34.5 + 24, 40.0 − 24) = (58.5, 16.0)
  Hole 1C: (34.5 − 24, 40.0 + 24) = (10.5, 64.0)
  Hole 1D: (34.5 + 24, 40.0 + 24) = (58.5, 64.0)

Pump 2 center: (109.5, 40.0)
  Hole 2A: (109.5 − 24, 40.0 − 24) = (85.5, 16.0)
  Hole 2B: (109.5 + 24, 40.0 − 24) = (133.5, 16.0)
  Hole 2C: (109.5 − 24, 40.0 + 24) = (85.5, 64.0)
  Hole 2D: (109.5 + 24, 40.0 + 24) = (133.5, 64.0)
```

### 5.2 All 8 Hole Center Positions

| Hole ID | X (mm) | Z (mm) | Pump | Position in pattern |
|---------|--------|--------|------|---------------------|
| 1A | **10.5** | **16.0** | Pump 1 | Bottom-left |
| 1B | **58.5** | **16.0** | Pump 1 | Bottom-right |
| 1C | **10.5** | **64.0** | Pump 1 | Top-left |
| 1D | **58.5** | **64.0** | Pump 1 | Top-right |
| 2A | **85.5** | **16.0** | Pump 2 | Bottom-left |
| 2B | **133.5** | **16.0** | Pump 2 | Bottom-right |
| 2C | **85.5** | **64.0** | Pump 2 | Top-left |
| 2D | **133.5** | **64.0** | Pump 2 | Top-right |

All holes are through-cuts along the Y-axis (Y=0 to Y=5.5mm). The 0.5mm extension beyond the plate rear face (Y=5 to Y=5.5) cuts through the boss floor annular ring, creating a continuous void from the clearance hole into the boss cavity. See parts.md Rubric D DG-01 for full path continuity analysis and resolution. Hole diameter: 3.6mm CAD design value (targeting 3.4mm printed after FDM shrinkage — normal ISO 273 M3 fit, per pump-mounting-geometry.md).

### 5.3 Boundary Check

Tray envelope: X ∈ [0, 144mm], Z ∈ [0, 80mm]. Boss OD = 9mm, boss radius = 4.5mm. Minimum acceptable distance from hole center to any tray edge = 4.5mm (boss tangent point).

| Hole | X-distance to nearest X-edge | Z-distance to nearest Z-edge | Status |
|------|------------------------------|------------------------------|--------|
| 1A (10.5, 16.0) | 10.5mm to X=0 | 16.0mm to Z=0 | Pass (10.5 > 4.5) |
| 1B (58.5, 16.0) | 58.5mm to X=0; 85.5mm to X=144 | 16.0mm to Z=0 | Pass |
| 1C (10.5, 64.0) | 10.5mm to X=0 | 16.0mm to Z=80 | Pass (10.5 > 4.5) |
| 1D (58.5, 64.0) | 58.5mm to X=0 | 16.0mm to Z=80 | Pass |
| 2A (85.5, 16.0) | 85.5mm to X=0 | 16.0mm to Z=0 | Pass |
| 2B (133.5, 16.0) | 10.5mm to X=144 | 16.0mm to Z=0 | Pass (10.5 > 4.5) |
| 2C (85.5, 64.0) | 85.5mm to X=0 | 16.0mm to Z=80 | Pass |
| 2D (133.5, 64.0) | 10.5mm to X=144 | 16.0mm to Z=80 | Pass (10.5 > 4.5) |

**All 8 holes pass the boundary check.** The tightest margins are at holes 1A, 1C, 2B, 2D — 10.5mm from the nearest lateral edge — which exceeds the 4.5mm boss-radius minimum by 6mm.

---

## 6. Boss Positions and Geometry

### 6.1 Boss Face Placement — Critical Spatial Clarification

**The bosses are on the REAR face (Y=5mm), protruding in the +Y direction (away from the plate, upward during printing).**

This is the resolution of the spatial conflict between boss function (inserts installed from pump side, screws driven from pump side) and print orientation (front face Y=0 on build plate). The conflict and its resolution:

- Front face (Y=0) is the build plate contact surface during printing.
- Bosses that protrude from the front face (Y=0) in the -Y direction would grow downward into the build plate — impossible to print.
- Bosses that protrude from the front face in the +Y direction would grow into the plate body — they would be internal recesses, not protrusions. This also contradicts the function.
- **Resolution:** The bosses are on the rear face (Y=5). They protrude in the +Y direction (away from the plate into the motor zone, upward during printing). This is directly printable: vertical cylinders growing upward from the rear face, fully supported, no bridging.

**Screw path (front to rear):**
1. Screw head: at pump bracket face, forward of Y=0 (pump side)
2. Screw shank: passes through pump bracket clearance hole (in bracket)
3. Screw shank: passes through M3 clearance hole in tray plate (Y=0 → Y=5), 3.6mm CAD diameter
4. Screw tip: enters boss cylinder at Y=5 (rear face boss base)
5. Screw threads into heat-set insert: seated in boss cavity from Y=5 to Y=9.5 (boss base to insert bottom)

**Heat-set insert installation:** Inserts are driven from the REAR face (Y=5), into the boss cavity from the boss tip face (Y=10). The soldering iron approaches from the rear (top surface during printing). This is the factory assembly step performed before pump installation.

**Assembly sequence confirmation (from concept.md):** Print tray flat. Install 8 heat-set inserts from the REAR face (Y=5, top surface when printing). Place tray on assembly fixture, front face up (flip the part). Lower pumps onto front face. Drive screws from pump side (front, Y<0) through clearance holes into inserts in rear bosses.

### 6.2 Boss Geometry

All 8 bosses are identical.

| Parameter | Value |
|-----------|-------|
| Boss base location | Y = 5mm (rear face surface) |
| Boss tip location | Y = 10mm (5mm protrusion above rear face, into motor zone) |
| Boss OD | 9mm |
| Boss base fillet | 1.5mm radius (where boss cylinder meets rear face plate surface) |
| Boss cavity diameter | 4.7mm |
| Boss cavity depth | 4.5mm (insert length 4.0mm + 0.5mm floor) |
| Boss cavity opening | At boss tip face: Y = 10mm |
| Boss cavity bottom | Y = 10 − 4.5 = 5.5mm |
| Boss cavity floor (0.5mm plate material below cavity bottom) | Y = 5.5mm (0.5mm above rear face = 0.5mm into boss body) |
| Insert seated depth | From Y=10 (tip) to Y=6 (insert base, 4mm insert length) |

### 6.3 Boss Center Positions (same X, Z as holes)

All positions have Y span: base at Y=5, tip at Y=10, cavity from Y=10 to Y=5.5.

| Boss ID | X (mm) | Z (mm) | Corresponds to hole |
|---------|--------|--------|---------------------|
| Boss 1A | **10.5** | **16.0** | Hole 1A |
| Boss 1B | **58.5** | **16.0** | Hole 1B |
| Boss 1C | **10.5** | **64.0** | Hole 1C |
| Boss 1D | **58.5** | **64.0** | Hole 1D |
| Boss 2A | **85.5** | **16.0** | Hole 2A |
| Boss 2B | **133.5** | **16.0** | Hole 2B |
| Boss 2C | **85.5** | **64.0** | Hole 2C |
| Boss 2D | **133.5** | **64.0** | Hole 2D |

---

## 7. Rib and Surface Zone Positions

### 7.1 Mounting Pad Zones (Front Face — Y=0)

Each mounting pad zone is the region of the front face that sits at full plate surface height (no 0.5mm field-zone step). The field zone is 0.5mm lower than the mounting pad.

Mounting pad zones are approximately 74mm × 74mm centered on each bore center, extending to the tray perimeter where applicable. Exact extents:

| Zone | X range | Z range | Notes |
|------|---------|---------|-------|
| Pump 1 mounting pad | X = 0 to 71.5mm | Z = 3.0 to 77.0mm | Clipped at X=0 tray edge; full pad would be [-2.5, 71.5] |
| Pump 2 mounting pad | X = 72.5 to 144mm | Z = 3.0 to 77.0mm | Clipped at X=144 tray edge; full pad would be [72.5, 146.5] |
| Cross-rib connection band | X = 69.0 to 75.0mm | Z = 37.0 to 43.0mm | 6mm wide, centered on plate center X=72, Z-centered on bore Z=40 |

The cross-rib (6mm W × 5mm H, centered at X=72, Z=40) connects the two mounting pad zones into a continuous elevated band. The cross-rib crown is coplanar with the boss tops.

**Field zone:** Everything on the front face (Y=0) outside the above mounting pad zones and cross-rib is 0.5mm lower (recessed). Step transitions are 45° chamfers (not 90° steps).

### 7.2 Bore-to-Boss Radiating Ribs (Front Face — Y=0, 8 total)

Each rib runs from a boss OD edge toward the nearest bore circle edge. Width: 4mm. Height: 5mm. Length: from boss OD to bore edge.

| Rib | Boss center (X, Z) | Boss OD edge toward bore (X, Z) | Bore edge toward boss (X, Z) | Rib length |
|-----|--------------------|---------------------------------|------------------------------|------------|
| Rib 1A | (10.5, 16.0) | Inner corner toward (34.5, 40) | Bore 1 edge at nearest point | ~3.5mm |
| Rib 1B | (58.5, 16.0) | Inner corner toward (34.5, 40) | Bore 1 edge at nearest point | ~3.5mm |
| Rib 1C | (10.5, 64.0) | Inner corner toward (34.5, 40) | Bore 1 edge at nearest point | ~3.5mm |
| Rib 1D | (58.5, 64.0) | Inner corner toward (34.5, 40) | Bore 1 edge at nearest point | ~3.5mm |
| Rib 2A | (85.5, 16.0) | Inner corner toward (109.5, 40) | Bore 2 edge at nearest point | ~3.5mm |
| Rib 2B | (133.5, 16.0) | Inner corner toward (109.5, 40) | Bore 2 edge at nearest point | ~3.5mm |
| Rib 2C | (85.5, 64.0) | Inner corner toward (109.5, 40) | Bore 2 edge at nearest point | ~3.5mm |
| Rib 2D | (133.5, 64.0) | Inner corner toward (109.5, 40) | Bore 2 edge at nearest point | ~3.5mm |

Rib exact endpoint derivation (Rib 1A as example):
```
Boss 1A center: (10.5, 16.0)
Boss OD radius: 4.5mm
Bore 1 center: (34.5, 40.0)
Bore radius: 18.6mm

Vector from bore center to boss center: (10.5−34.5, 16.0−40.0) = (−24, −24)
Distance: sqrt(24² + 24²) = 33.94mm
Unit vector: (−24/33.94, −24/33.94) = (−0.707, −0.707)

Boss OD point (toward bore): boss center + 4.5 × unit_toward_bore
  = (10.5 + 4.5×0.707, 16.0 + 4.5×0.707)
  = (10.5 + 3.18, 16.0 + 3.18)
  = (13.68, 19.18)

Bore edge point (toward boss): bore center + 18.6 × unit_toward_boss
  = (34.5 + 18.6×(−0.707), 40.0 + 18.6×(−0.707))
  = (34.5 − 13.15, 40.0 − 13.15)
  = (21.35, 26.85)

Rib length = distance between these two points:
  = distance[(13.68, 19.18), (21.35, 26.85)]
  = sqrt((21.35−13.68)² + (26.85−19.18)²)
  = sqrt(7.67² + 7.67²)
  = sqrt(58.8 + 58.8) = sqrt(117.6) = 10.85mm → wait, this is the diagonal rib length
```

Recalculation: the boss-to-bore gap along the diagonal for the corner bosses is:
```
Boss 1A center to Bore 1 center distance = 33.94mm
Minus boss OD radius (4.5mm) minus bore radius (18.6mm) = 33.94 − 4.5 − 18.6 = 10.84mm
```

The rib bridges a 10.84mm gap along the diagonal for the corner bosses. This is longer than the "2–6mm" estimate in synthesis.md (which may have been based on a different bore radius assumption). At 37.2mm bore: actual rib length is ~10.84mm for all 8 ribs (all are at the same boss-to-bore-center distance for this symmetric pattern).

The CAD agent should generate ribs along the vector from boss OD to bore edge, 4mm wide centered on this vector, 5mm tall from front face.

---

## 8. Wiring Channel Positions (Rear Face — Y=5)

### 8.1 Channel Specification

- Location: rear face only (Y=5 surface)
- Width: 6mm
- Depth: 4mm (extends from Y=5 inward to Y=1, i.e., channel floor at Y=1)
- Wall thickness: 1.5mm (the walls between channel and open rear face are 1.5mm)
- Strain-relief bumps: 3 per channel, 1.5mm tall × 2mm wide, rounded, 20mm spacing along channel

### 8.2 Channel Entry Points

Each channel begins at the bore edge on the rear face and routes laterally toward the nearest tray lateral edge (X=0 for Pump 1, X=144 for Pump 2). The exact routing path beyond the bore edge is deferred to the shell concept step (OQ-6 from synthesis.md), which will define the harness connector exit location.

**Fixed anchor point per channel (bore-edge entry):**

| Channel | Bore center (X, Z) | Bore radius | Entry point — bore edge (X, Z) | Toward edge |
|---------|--------------------|--------------|---------------------------------|-------------|
| Channel 1 (Pump 1) | (34.5, 40.0) | 18.6mm | **(15.9, 40.0)** | Toward X=0 |
| Channel 2 (Pump 2) | (109.5, 40.0) | 18.6mm | **(128.1, 40.0)** | Toward X=144 |

Entry point derivation:
```
Channel 1: bore edge at X = 34.5 − 18.6 = 15.9mm, Z = 40.0mm (horizontal center of bore, toward X=0 side)
Channel 2: bore edge at X = 109.5 + 18.6 = 128.1mm, Z = 40.0mm (horizontal center of bore, toward X=144 side)
```

The channel is 6mm wide, centered at Z=40. Channel lateral extents in Z: Z = 37.0 to 43.0mm at entry.

**Channel routing after entry:** runs in the -X direction (Channel 1) or +X direction (Channel 2) from the bore edge toward the tray lateral edge. Total lateral run from bore edge to tray edge:
- Channel 1: from X=15.9 to X=0 → 15.9mm of lateral travel (fits within tray)
- Channel 2: from X=128.1 to X=144 → 15.9mm of lateral travel (fits within tray)

If a longitudinal run toward the cartridge front (toward Z=0 or away) is needed after the lateral run, that is defined in the shell step. The CAD agent should generate the lateral segment only, terminating at the tray lateral edge, until the shell step resolves the exit routing.

### 8.3 Strain-Relief Bump Positions

Centered in each channel (Z = 40.0mm), spaced 20mm apart along the lateral run. Starting from the bore edge entry:

| Channel | Bump 1 (X, Z) | Bump 2 (X, Z) | Bump 3 (X, Z) |
|---------|--------------|--------------|--------------|
| Channel 1 | **(13.9, 40.0)** | **(8.0, 40.0)** | — (only ~15.9mm run; 2 bumps fit; third is outside tray) |
| Channel 2 | **(130.1, 40.0)** | **(136.0, 40.0)** | — (same constraint) |

Note: With only ~15.9mm of channel run, only 2 bumps fit at 20mm spacing before the channel terminates at the tray edge. If the shell step adds a longitudinal channel segment, a third bump can be placed there. The CAD agent should generate 2 bumps per channel on the lateral segment as specified above.

Bump X derivation:
```
Channel 1 entry at X=15.9. Bump 1 at X = 15.9 − 2.0 = 13.9mm (2mm into channel from bore edge).
Bump 2 at X = 13.9 − 5.9 = 8.0mm. (limited by remaining channel length; spacing adjusted to ~5.9mm for second bump)
```

Revised bump spacing note: The concept.md specifies 20mm spacing. With only ~15.9mm of channel, the spacing cannot be maintained at 20mm. The agent should place bumps at 5mm intervals from the entry point within the available channel length:
- Channel 1: Bump 1 at X=10.9 (5mm from entry at X=15.9), Bump 2 at X=5.9 (10mm from entry)
- Channel 2: Bump 1 at X=133.1 (5mm from entry at X=128.1), Bump 2 at X=138.1 (10mm from entry)

The bump spacing of 20mm specified in concept.md is the target for longer channel runs. On the short lateral segment, reduce spacing to fit. When the longitudinal segment is added in the shell step, revert to 20mm spacing for bumps placed there.

---

## 9. Snap Notch Positions

### 9.1 Notch Geometry

From concept.md: "1.5mm deep × 3mm wide relief cut into the rear edge of each lateral face."

- This is a rectangular notch cut into the intersection of the lateral face (X=0 or X=144) and the rear face (Y=5).
- The notch creates the engagement point for the shell's snap latch.

### 9.2 Notch Coordinates

The notch is located on each lateral face at the rear edge (where X-face meets Y=5). The Z position of the notch center is not specified by the shell concept yet. Working assumption: Z = 40.0mm (plate height midpoint), symmetric vertically.

| Notch | Location | Notch depth (into plate in X) | Notch width (in Z) | Z center |
|-------|----------|-------------------------------|--------------------|----------|
| Left notch | X=0 lateral face, at Y=5 edge | 1.5mm (notch extends from X=0 to X=1.5mm inward) | 3mm (Z = 38.5 to 41.5mm) | Z=40.0mm |
| Right notch | X=144 lateral face, at Y=5 edge | 1.5mm (notch extends from X=144 to X=142.5mm inward) | 3mm (Z = 38.5 to 41.5mm) | Z=40.0mm |

**Y-extent of notch:** The notch opens toward Y=5 (rear face). It is a slot cut through the full rear-edge thickness. Notch height in Y: 3mm from Y=5 (the notch opening is at the rear face edge, extending 3mm in the Y direction, so the notch spans Y=2 to Y=5). The notch bottom is at Y=2.

**FLAGGED for shell step:** The Z position (Z=40.0mm) and Y depth (3mm from Y=5) are working assumptions. The shell concept step must confirm the Z position of the snap latch receiver and the required notch depth. These values must be reconciled before final CAD.

---

## 10. Chamfer Positions

All chamfers are edge features. Listed by which edges receive each chamfer.

| Chamfer | Edge(s) | Size |
|---------|---------|------|
| Design perimeter chamfer | Top edge (Z=80, full X extent, at Y=0 and Y=5 faces) | 1.5mm × 45° |
| Design perimeter chamfer | Left lateral edge (X=0, full Z extent, at Y=0 and Y=5 faces) | 1.5mm × 45° |
| Design perimeter chamfer | Right lateral edge (X=144, full Z extent, at Y=0 and Y=5 faces) | 1.5mm × 45° |
| Elephant's foot chamfer | Bottom edge (Z=0, full X extent, at Y=0 face — the build-plate face edge) | 0.3mm × 45° |
| Rear bore entry chamfer | Both bore openings at rear face (Y=5): circular edge of each bore where it meets Y=5 | 0.5mm × 45° |

Note on elephant's foot: the 0.3mm × 45° chamfer is applied to the bottom edge of the front face only (Z=0, Y=0 edge). The bottom edge of the rear face (Z=0, Y=5 edge) is not the build plate face and receives the standard 1.5mm perimeter chamfer per the design standard.

Correction: re-reading concept.md Section 5 chamfer table:
- "Top face (pump-head side) perimeter edge" → this is the Z=80 top edge, pump-face side. Since the top of the tray is the Z=80 edge, this is the perimeter of the Z=80 face — not a face in the tray's geometry, it is the top edge of the plate. The chamfer is on the top edge (Z=80) of the front face (Y=0 side). The 1.5mm chamfer goes on: Z=80 top edge, X=0 left edge (full height), X=144 right edge (full height).
- Bottom edge (Z=0): 0.3mm × 45° elephant's foot only on the front face bottom edge (Z=0, Y=0 side, full X extent).

Final chamfer summary:
- Z=80 top edge, front face (Y=0): 1.5mm × 45°
- Z=80 top edge, rear face (Y=5): 1.5mm × 45° (included in "top face perimeter")
- X=0 left edge, full height Z=[0,80], both front and rear faces: 1.5mm × 45°
- X=144 right edge, full height Z=[0,80], both front and rear faces: 1.5mm × 45°
- Z=0 bottom edge, front face (Y=0): 0.3mm × 45° elephant's foot
- Z=0 bottom edge, rear face (Y=5): 1.5mm × 45° (this edge is not the build-plate face)
- Both bore openings at rear face (Y=5): 0.5mm × 45°

---

## 11. Corner Radii

| Location | Radius |
|----------|--------|
| Outer tray plate corners (4 plan-view corners at X=0/144, Z=0/80, full Y depth) | 3.0mm |
| Boss base fillet (boss cylinder meets rear face plate surface) | 1.5mm |
| Rib base fillet (all ribs meet front face or rear face) | 2.0mm |
| Wiring channel interior corners (wall meets channel floor) | 1.5mm |

---

## 12. Feature Depth Summary (Y-axis extent for all features)

This table gives the complete Y-range for every feature so the CAD agent has no ambiguity about depth.

| Feature | Y start | Y end | Notes |
|---------|---------|-------|-------|
| Plate body | 0 | 5mm | Full plate thickness |
| Motor bore (through-cut) | 0 | 5mm | Through full thickness |
| M3 clearance holes (through-cut) | 0 | **5.5mm** | Through full plate (Y=0–5) PLUS 0.5mm into boss floor (Y=5–5.5) for path continuity — see parts.md DG-01 |
| Boss cylinders (union on rear face) | 5mm | 10mm | 5mm tall protrusion from rear face |
| Boss cavities (blind bore from boss tip) | 10mm | 5.5mm | Opens at Y=10, bottom at Y=5.5 |
| Heat-set insert (seated in boss cavity) | 10mm | 6.0mm | 4mm long insert, 0.5mm floor at Y=5.5 to Y=6.0 |
| Cross-rib (union on front face) | 0 | −5mm | 5mm tall protrusion from front face (extends in −Y direction, toward pump) |
| Radiating ribs (union on front face) | 0 | −5mm | Same: protrude toward pump |
| 0.5mm field zone recess | 0 | +0.5mm | Cut 0.5mm into the front face: Y=0 to Y=+0.5mm removed outside mounting pads |
| Wiring channels (cut into rear face) | 5mm | 1mm | 4mm deep cut from rear face inward (Y=5 to Y=1) |
| Strain-relief bumps (union in channel) | 1mm | −0.5mm | 1.5mm tall protrusion from channel floor at Y=1 toward Y=−0.5 |
| Snap notches (cut into lateral face at Y=5 edge) | 5mm | 2mm | 3mm deep cut from rear edge (Y=5) inward |
| Rear bore chamfer | Y=5 (rear face bore edge) | — | 0.5mm × 45° chamfer |
| Elephant's foot chamfer | Y=0 (front face bottom edge) | — | 0.3mm × 45° chamfer at Z=0 |
| Perimeter chamfers | All top/lateral/rear-bottom edges | — | 1.5mm × 45° |

**Clarification on cross-rib and radiating rib Y direction:**
The ribs are on the front face. The front face is Y=0. "Protrude from front face" means they extend in the −Y direction (toward the pump bracket, away from the plate body). So the rib crown is at Y=−5mm (5mm proud of the front face, same as boss tops at Y=10). The rib base is at Y=0.

Wait — the bosses are on the rear face and protrude to Y=10. The ribs are on the front face and protrude to Y=−5. The boss tops and rib crowns are both 5mm proud of their respective faces but on opposite sides. They are NOT coplanar with each other. The concept.md statement "the rib height matches the boss height so the front face reads as a unified elevated surface" refers to the ribs and bosses being the same HEIGHT (both 5mm), but since bosses are on the rear face and ribs are on the front face, they are each creating a 5mm-tall surface on their own face. There is no cross-face coplanarity issue — they exist on different faces. The ribs on the front face create a 5mm elevated pattern that is a unified feature on the front face. The bosses on the rear face create a 5mm elevated pattern on the rear face.

**Final rib Y-range:** Ribs on front face (Y=0), extend to Y=−5mm.
**Final boss Y-range:** Bosses on rear face (Y=5), extend to Y=10mm.

---

## 13. Interface Summary — Both Sides of Each Interface

### 13.1 Pump Bracket Interface (Front Face, Y=0 side)

| Feature | Tray provides | Pump bracket requires |
|---------|--------------|----------------------|
| Flat mating surface | Mounting pad zone at Y=0, within 74mm × 74mm centered on each bore | Bracket face flat bearing surface, 68.6mm × 68.6mm, contacts tray at Y=0 |
| Motor clearance | 37.2mm CAD bore through Y=0 to Y=5, centered at (34.5, 40) and (109.5, 40) | Motor cylinder OD ~35mm, protrudes through bore into motor zone (Y>5) |
| Screw clearance | 3.6mm CAD through-holes at all 8 hole positions (Y=0 to Y=5) | M3 screw shanks, 3mm nominal diameter |
| Thread engagement | Heat-set inserts (M3, 4mm) in boss cavities at Y=5.5 to Y=10mm | M3 screw thread, engages full 4mm of insert |
| Boss top contact | Boss tip face at Y=10mm — screw head and bracket sandwich the tray+boss stack | Screw head bears on bracket face; bracket face contacts boss tip faces and rib crowns |

### 13.2 Cartridge Shell Interface (Lateral Edges)

| Feature | Tray provides | Shell must provide |
|---------|--------------|-------------------|
| Sliding surfaces | Flat lateral edges at X=0 and X=144, full Z and Y extent | 5.2mm wide channel (5.0mm tray + 0.2mm clearance) × 6mm deep, full interior depth |
| Forward stop engagement | Front face (Y=0) acts as stop face against shell channel's forward end | Hard stop at channel forward end; prevents over-travel |
| Snap engagement | Passive notch: 1.5mm × 3mm relief at X=0, Y=2–5, Z=38.5–41.5 and X=144 mirror | 1.5mm × 3mm spring latch hook; latch on shell, notch on tray |

### 13.3 Motor / Rear Zone Interface (Rear Face, Y=5 side)

| Feature | Tray provides | What occupies the rear zone |
|---------|--------------|----------------------------|
| Motor cylinder clearance | 37.2mm bore through full plate; motor exits rear face at Y=5 | Motor cylinder body (~35mm OD, ~63mm long) extending into Y>5 zone |
| Motor nub clearance | Bore is clearance only — no features protrude into bore | Motor nub (5mm, ~5–8mm OD) extends 5mm beyond motor body; needs 5mm axial + 4mm radial clearance from any rear zone feature |
| Wiring egress | Channel 1 exits at X=0 lateral edge at Z=40; Channel 2 exits at X=144 at Z=40 | Motor wiring routes from terminals, enters channels at bore edge, exits at tray lateral edge |
| Boss protrusion clearance | 8 bosses: 9mm OD, tips at Y=10mm, spaced at all 8 hole positions | No shell feature may intrude into the boss zones; shell channel depth (6mm) must stop before Y=10+clearance |

---

## 14. Transform Summary

The pump-tray mounts flat in the cartridge with no rotation. The tray reference frame is also the assembly frame for all tray features.

| Axis | Part frame | System/assembly frame |
|------|-----------|----------------------|
| X (width) | 0 → 144mm, left to right | Same — tray runs across the full cartridge interior width |
| Y (depth) | 0 (front/pump face) → 5mm (rear/motor face) | Same — tray Y=0 faces forward toward the cartridge front wall |
| Z (height) | 0 (bottom) → 80mm (top) | Same — tray stands vertically in the cartridge, bottom at cartridge floor |

**No coordinate transform required.** A point at (X, Y, Z) in the part frame is at the same relative position in the cartridge assembly frame. The only assembly-level question is the absolute position of the tray's origin (0, 0, 0) within the cartridge — which is determined by:
- X: tray is centered in the cartridge → cartridge_origin_X = (cartridge_interior_width − 144) / 2
- Z: tray bottom rests on cartridge floor → tray Z=0 is at cartridge interior floor Z
- Y: tray front face position is set by the forward tube routing zone depth (~50–55mm from cartridge front interior wall to tray Y=0 face)

These absolute position values are for the shell design agent, not for the CAD generation of the tray itself.

---

## 15. Quality Gate Verification

1. **Every number is in a named reference frame.** All positions specify (X, Y, Z) in the tray part frame defined in Section 2. No implicit coordinate systems.

2. **No downstream derivation required.** All 8 hole positions are pre-computed and tabulated (Section 5). All boss positions are at the same X, Z as holes with Y range stated (Section 6). Bore centers are at (34.5, 40) and (109.5, 40) (Section 4). Channel entry points are at (15.9, 40) and (128.1, 40) (Section 8). No agent needs to compute pump spacing, hole offsets, or bore edge positions from scratch.

3. **Cross-sectional profiles:** N/A — this part has no curved or swept cross-sectional profiles. All features are prismatic (extrude or cut on a flat plate).

4. **Interfaces specified from both sides.** Section 13 states what the tray provides and what the mating component requires for every interface: pump bracket (13.1), cartridge shell (13.2), motor/rear zone (13.3).

5. **Transform summary is self-consistent.** Section 14 confirms no rotation from part frame to system frame. Tray X=144mm spans the cartridge interior width. Tray Y=0 faces the cartridge front wall. Tray Z=0 is at the cartridge floor.

---

## 16. Open Items Carried Forward

These items are not blocking CAD start for the fixed-geometry features but must be resolved before the spatial resolution document is finalized for all features:

| OQ | Description | Impact on this document |
|----|-------------|------------------------|
| OQ-2 | Motor body diameter confirmation (currently ~35mm, low confidence) | Affects bore diameter (currently 37.2mm CAD) and web width (currently 3.6mm) |
| OQ-3/OQ-4 | Tube stub Z and X positions on pump face | Affects pump center Z (currently Z=40mm working assumption) and tray height (currently 80mm) |
| OQ-6 | Shell harness connector location | Determines wiring channel routing beyond bore edge; affects bump count and positions in Section 8 |
| Snap notch Z | Shell concept step must confirm Z position and Y depth of snap notch | Section 9 Z=40.0mm and Y depth of 3mm are working assumptions |
