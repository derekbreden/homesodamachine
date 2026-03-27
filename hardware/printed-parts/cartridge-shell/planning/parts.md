# Cartridge Outer Shell

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale.

**Coordinate system:** Origin at exterior front-bottom-left corner of shell. X = width (positive right). Y = depth (positive toward rear/fittings). Z = height (positive up). Front face (Y=0) is twist-release knob side. Rear face (Y=130) carries JG fittings.

---

## 3D Printed Part: Outer Shell

- **Type:** 3D printed
- **Material:** PETG
- **Exterior envelope:** 148W x 130D x 80H mm
- **Wall thickness:** 4mm solid (all sides, no ribs)
- **Interior volume:** 140W x 122D x 72H mm
- **Features:**
  - Rectangular box, open on top (lid closes it)
  - Exterior slide rails on bottom face: 2x parallel rails, 2mm tall x 3mm wide, full 130mm depth, spaced to match dock floor rails
  - Exterior side guide contact surfaces: 1.5mm wide rail features on left/right walls, 0.3-0.5mm clearance per side to dock guides
  - Rear wall (Y=126 to Y=130, 4mm thick): 4x fitting pockets for JG PP0408W union bodies in 2x2 grid, 40mm horizontal x 28mm vertical center-to-center. **Barbell profile accommodation (caliper-verified):** The fitting has a 9.31mm center body flanked by 15.10mm body ends. Pocket bore 9.8mm diameter (sliding fit for 9.31mm center body, ~0.25mm clearance per side). The 15.10mm body ends protrude on both sides of the rear wall — the pocket only grips the narrow center section. The center body is 12.16mm long, so the 4mm wall engages a portion of the center section; the fitting shoulders (step-down from 15.10mm to 9.31mm) provide axial location against the wall faces. Through-holes for tube passage (must clear 6.30mm tube OD). Fitting pocket centers at X=54, X=94, Z=26, Z=54 (centered on rear wall). **Note:** The body ends (15.10mm OD) protrude ~12mm on each side of the wall.
  - Rear wall: release plate travel cavity on dock side of rear wall (between wall and dock), 6mm deep x 63mm wide x 51mm tall (clears 59x47mm plate with 2mm margin per side)
  - Rear wall: 2x printed bushings for guide pins (6.5mm bore, press-fit into wall), positioned at X=40, Z=40 and X=110.5, Z=40
  - Rear wall: 12.5mm bore (at X=74, Z=40) for strut passage to release plate
  - Front wall (Y=0 to Y=4, 4mm thick): 12.5mm bore (at X=74, Z=40) for PETG threaded strut (Tr12x3 2-start trapezoidal)
  - Top face: recessed pocket for pogo target PCB, 15W x 30L x 1.5D mm
  - Top face: wire entry slot from interior to pogo PCB pocket
  - Interior ledges for pump tray: 2x shelves on left/right interior walls, 2mm wide, at Z=4
  - Interior: tray locating tabs or slots on walls for lateral tray alignment
  - Chamfered front edges: 5mm x 45-degree chamfer on all four leading edges (aids dock entry)
- **Interfaces:**
  - Tray screws to shell ledges via 4x M3 heat-set inserts
  - Lid attaches to top via screws or snap clips
  - JG fittings press into rear wall pockets via 9.31mm center body. Collet rings (15.10mm) protrude on both sides of wall.
  - Release plate rides on 2x printed guide pins (6mm diameter PETG, integral with plate) sliding in printed bushings (6.5mm bore) in rear wall, plate sits on dock side of rear wall (between wall and dock)
  - 12mm PETG threaded strut (Tr12x3 2-start trapezoidal) passes through front and rear wall bores, attaches to release plate via press-fit + epoxy joint. Wing knob on front face threads onto strut. See `../../cartridge-twist-release/planning/research/3d-printed-approach.md`.
  - Pogo target PCB sits in top-face recess
  - Exterior rails and guides mate with dock floor rails and side guides (see `../../dock-back-wall/planning/parts.md`)
- **Quantity:** 1
- **Open:** Interior ledge Z-height depends on final pump tray thickness. Print orientation TBD.

---

## Purchased Parts Mounted in Shell

### John Guest PP0408W 1/4" Union (x4)

Full geometry: `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`

- **Envelope:** Barbell profile — 15.10mm body end OD x 9.31mm center body OD x 39.13mm overall (caliper-verified)
- **Mounting:** Press into rear wall pockets (pocket grips 9.31mm center body; 15.10mm body ends protrude on both sides)
- **Collet:** 9.57mm OD, 6.69mm ID, ~1.3mm travel per side (caliper-verified)
- **2x2 grid:** 40mm horizontal x 28mm vertical center-to-center

### 1/4" OD Hard Nylon Tube Stubs (x4, cartridge interior)

- 6.35mm OD, ~46mm length per stub (~16mm insertion + ~30mm protrusion)
- Connect BPT-to-hard-tube brass barb transitions to interior side of JG fittings

### Brass Barb Fittings (x4, BPT-to-Hard-Tube Transition)

- One end: barb for BPT pump tube (4.8mm ID)
- Other end: barb for 1/4" OD hard tubing
- Positioned between pump head tube exit and JG fitting

### Small Hose Clamps (x4)

- Secure BPT pump tube onto brass barb fittings
- Spring-clip style preferred

### Pogo Target PCB (x1)

- ~15W x 30L x 1.6H mm
- 3x contact pads: 8mm x 5mm each, 10mm center-to-center (GND | Motor A 12V | Motor B 12V)
- Sits in recessed pocket on shell top face

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Cartridge system architecture:** `../../../planning/cartridge-architecture.md`
- **JG fitting geometry:** `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
- **Fitting alternatives research:** `research/fitting-alternatives.md`
- **Dock interface:** `../../dock-back-wall/planning/parts.md`
- **Release mechanism:** `../../cartridge-release-plate/planning/parts.md`
- **Twist-release design:** `../../cartridge-twist-release/planning/research/decision.md`, `../../cartridge-twist-release/planning/research/3d-printed-approach.md`
