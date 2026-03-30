# Enclosure Top Half — Spatial Resolution

**Date:** 2026-03-29
**Inputs:** concept.md, synthesis.md, bottom-half/spatial-resolution.md (interface), bottom-half/generate_step_cadquery.py (arm geometry)
**Coordinate system:** Global enclosure frame — same as bottom half.
  Origin: exterior bottom-left-front corner of assembled enclosure.
  X: 0→220 (left to right), Y: 0→300 (front to back), Z: 0→400 (bottom to top).
  Top half spans Z:[184.5, 400].

---

## Interface Dimensions from Bottom Half (seam face)

These come directly from the validated bottom half STEP:

| Interface | Value |
|---|---|
| Seam plane | Z = 185 |
| Exterior wall thickness | WALL_T = 2.4 mm |
| Interior extents | X:[2.4, 217.6] Y:[2.4, 297.6] |
| Tongue width | 3.0 mm |
| Tongue height | 4.0 mm (Z:[185, 189]) |
| Tongue setback from exterior | 2.0 mm |
| Tongue Y-position (front) | Y:[2.0, 5.0] |
| Tongue Y-position (rear) | Y:[295.0, 298.0] |
| Tongue X-position (left) | X:[2.0, 5.0] |
| Tongue X-position (right) | X:[215.0, 218.0] |
| Tongue gap (dock span) | X:[31.5, 188.5] on front wall |
| Arm root Z | Z = 183 |
| Arm body Z | Z:[183, 185] (ARM_ROOT=2mm, ARM_TIP=1.4mm) |
| Hook protrusion (perpendicular to wall) | 1.2 mm |
| Hook height (Z) | 1.4 mm (ARM_TIP), Z:[183, 184.4] |
| Hook base Z | Z = 183 |
| Arm width | 8.0 mm |
| Front arm X-centers | 40, 80, 120, 160, 200 mm |
| Rear arm X-centers | 40, 80, 120, 160, 200 mm |
| Left/Right arm Y-centers | 40, 80, 120, 160, 200, 240, 280 mm |
| Pin diameter | 4.0 mm |
| Pin height | 8.0 mm (Z:[183, 191]) — corrected, ARM_Z0+PIN_H=183+8=191 |
| Pin positions (XY) | (10,10), (210,10), (10,290), (210,290) |

---

## Feature-by-Feature Coordinate Resolution

### Feature 1 — Box body (exterior shell)
- Full box: X:[0, 220] Y:[0, 300] Z:[184.5, 400]
- Seam lip: the bottom 0.5mm of the box (Z:[184.5, 185]) laps over the bottom half exterior
- Build: solid box 220×300×215.5mm, corner at (0, 0, 184.5)

### Feature 2 — Interior cavity
- X:[2.4, 217.6] Y:[2.4, 297.6] Z:[185, 397.6] (open at Z=185, 2.4mm ceiling at Z=397.6)
- Cut: box 215.2×295.2×212.6mm from (2.4, 2.4, 185) to (217.6, 297.6, 397.6)

### Feature 3 — Groove (tongue-and-groove)
- Width: 3.1 mm (tongue 3.0mm + 0.05mm each side clearance)
- Depth: 4.2 mm (tongue 4.0mm + 0.2mm bottom clearance)
- Setback: tongue centerline is 3.5mm from exterior (2.0mm + 1.5mm half-tongue). Groove interior edge at 1.95mm from exterior.
- Front groove: Y:[1.95, 5.05], Z:[185, 189.2], X:[3.5, 28.0] + X:[192.0, 216.5] (flanking dock gap at X:[31.5, 188.5]) + full span where no gap
  - Front-left: X:[3.5, 28.0], Y:[1.95, 5.05], Z:[185, 189.2]
  - Front-right: X:[192.0, 216.5], Y:[1.95, 5.05], Z:[185, 189.2]
- Rear groove: Y:[295.0, 298.05], X:[3.5, 216.5], Z:[185, 189.2]
- Left groove: X:[1.95, 5.05], Y:[3.5, 296.5], Z:[185, 189.2]
- Right groove: X:[214.95, 218.05], Y:[3.5, 296.5], Z:[185, 189.2]
- 5 segments total (same split logic as bottom half tongue)

### Feature 4 — Snap ledge pockets (24 total)
- Each pocket opens downward at Z=185, cut upward 3.0mm to Z=188
- Width: ARM_W + 0.2mm clearance = 8.2mm (centered on arm X or Y position)
- Depth: through full wall thickness = WALL_T = 2.4mm
- Front pockets (5×): X_centers=[40,80,120,160,200]; each X:[Xc-4.1, Xc+4.1], Y:[0, 2.4], Z:[185, 188]
- Rear pockets (5×): X_centers=[40,80,120,160,200]; each X:[Xc-4.1, Xc+4.1], Y:[297.6, 300], Z:[185, 188]
- Left pockets (7×): Y_centers=[40,80,120,160,200,240,280]; each X:[0, 2.4], Y:[Yc-4.1, Yc+4.1], Z:[185, 188]
- Right pockets (7×): Y_centers=[40,80,120,160,200,240,280]; each X:[217.6, 220], Y:[Yc-4.1, Yc+4.1], Z:[185, 188]

### Feature 5 — Alignment pin sockets (4 total)
- Diameter: 4.15mm (4.0mm + 0.15mm clearance)
- Depth: 9.0mm (8mm pin + 1mm bottom clearance), Z:[185, 194]
- Entry chamfer: 1.0mm×45° at Z=185
- Centers: (10, 10), (210, 10), (10, 290), (210, 290) — matching bottom half pins

### Feature 6 — Rear wall thickening at port zone
- Standard rear wall: Y:[297.6, 300] (2.4mm thick)
- Port zone thickened to 3.5mm: add 1.1mm boss on interior face
- Boss region: X:[15, 205], Z:[295, 325], Y:[296.5, 297.6] (1.1mm × 10mm×210mm slab on inner rear wall)

### Feature 7 — Rear wall port holes (5×)
- All at Z=310 (port centerline), through rear wall
- Hole diameter: 17.2mm
- Through: Y:[296.5, 300] (through thickened wall)
- X positions: 25, 60, 110, 160, 195 mm

### Feature 8 — Interior boss rings (5×)
- OD: 22mm, hole: 17.2mm (same as port), height: 2.0mm on interior face
- At Y=[296.5-2, 296.5] = Y:[294.5, 296.5], centered on each port X, Z=310
- Ring: annular disc, OD=22mm, ID=17.2mm, height 2.0mm
- Underside (Z=310-11) chamfer 45° on outer edge to eliminate overhang when printed inverted

### Feature 9 — Rear exterior port bays
- Group A bay (X:[15, 70]): 1.5mm deep recess, Z:[295, 325], exterior face
  - Cut: X:[15, 70], Y:[299.0, 300], Z:[295, 325] → 1.0mm depth (from 300 to 299.0)
- Group B boss recess: 30mm diameter, 1.0mm deep at port X=110, Z=310
  - Cut: cylinder D=30mm, depth 1.0mm into exterior rear face
- Group C bay (X:[150, 205]): same as Group A
  - Cut: X:[150, 205], Y:[299.0, 300], Z:[295, 325]

### Feature 10 — Spine oval slot bosses (4 total: 2 per side wall)
- Spine posts: 10mm×6mm oval cross-section, 8mm long (per synthesis)
- Slot: 10.2mm×6.2mm oval opening (+0.2mm clearance), 8.5mm deep (8mm + 0.5mm)
- Boss: rectangular thickening on inner wall face to provide 8.5mm depth
  - Left wall: boss at X:[2.4, 10.9] (8.5mm deep), Y:[145, 155] (10mm wide), at Z=235 and Z=275
  - Right wall: boss at X:[209.1, 217.6] (8.5mm deep), Y:[145, 155], at Z=235 and Z=275
- Oval cuts through boss (opening faces -Z, cut from Z=239.1 downward 8.5mm):
  - Left lower: center X=6.65, Y=150, Z:[226.5, 235] — oval 10.2×6.2mm, axis Z
  - Left upper: center X=6.65, Y=150, Z:[266.5, 275]
  - Right lower: center X=213.35, Y=150, Z:[226.5, 235]
  - Right upper: center X=213.35, Y=150, Z:[266.5, 275]
- NOTE: oval slots open downward (accessible from seam face Z=185 for spine insertion before halves close)

### Feature 11 — Cradle locating ledges (2× per side wall = 4 total)
- Cross-section: 3mm wide × 3mm tall
- Run front-to-back: Y:[2.4, 297.6] (full interior depth)
- Heights: Z=195 (lower ledge bottom face) and Z=295 (upper ledge bottom face)
- Left wall: X:[2.4, 5.4] (3mm in +X from inner face), Z:[195, 198] and Z:[295, 298]
- Right wall: X:[214.6, 217.6] (3mm in -X from inner face), Z:[195, 198] and Z:[295, 298]
- 45° chamfer on underside of each ledge (the Z- face of the ledge)

### Feature 12 — Electronics tray snap rails (2 total, inner rear wall)
- Cross-section: 3mm deep (in -Y from rear inner wall) × 3mm tall (Z)
- Run left-to-right: X:[2.4, 217.6]
- Heights: Z=340 (lower rail bottom face) and Z=370 (upper rail bottom face)
- Position: Y:[294.6, 297.6] (3mm in -Y from inner rear wall face Y=297.6), Z:[340, 343] and Z:[370, 373]
- 45° chamfer on underside of each rail

### Feature 13 — Exterior vertical edge fillets (R=3mm)
- Same 4 vertical edges as bottom half: (X=0,Y=0), (X=220,Y=0), (X=0,Y=300), (X=220,Y=300)
- Z:[184.5, 400] full height of top half
- Applied with try/except (OCCT may refuse on complex geometry)

### Feature 14 — Seam lip chamfer
- 0.3mm×45° on the bottom exterior perimeter edge of the seam lip (Z=184.5)
- Guides the top half over the bottom half during assembly
- Applied to exterior bottom edges (faces with min Z)

---

## Bounding Box

X:[0, 220] Y:[0, 300] Z:[184.5, 400]

No protrusions beyond this envelope.
