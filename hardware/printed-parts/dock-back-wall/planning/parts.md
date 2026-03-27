# Dock Back Wall (Cartridge Dock System)

The dock is the enclosure-side structure that receives the removable pump cartridge. This part includes the back wall, floor rails, side guides, and chamfered slot entrance — all elements of the cartridge dock interface.

See `../../../planning/architecture.md` for system architecture and `../../../planning/spatial-layout.md` for enclosure coordinates.

**Coordinate system:** Enclosure coordinates — origin at exterior front-bottom-left corner of enclosure. X = width (0-220mm). Y = depth (0-300mm). Z = height (0-400mm).

---

## 3D Printed Part: Dock Back Wall

- **Type:** 3D printed
- **Material:** PETG
- **Envelope:** ~148W x ~10D x ~84H mm
- **Features:**
  - Structural wall at Y=130-140 (behind fully-inserted cartridge)
  - Four 7mm through-holes for 1/4" OD (6.35mm) tube stub pass-throughs with 0.65mm clearance
  - Tube stub spacing: ~40mm horizontal x ~28mm vertical center-to-center (matching cartridge JG fitting positions)
  - Each hole sealed with rubber grommet (7mm ID, ~11mm OD, compression fit into countersunk pocket)
  - Wall thickness at tube holes: 6-8mm
  - Pogo pin mount area on ceiling face (Z=80-84): see `../../pogo-pin-mount/planning/parts.md`
  - Drainage channel on ceiling surface sloping away from pogo pin pockets
- **Interfaces:**
  - Tube stubs protrude from both faces — front into cartridge cavity, rear into valve rack zone
  - Cartridge JG fittings slide onto front-facing tube stubs during dock-in
  - Pogo pins mount to ceiling face
- **Quantity:** 1
- **Open:** Grommet vs O-ring vs adhesive seal

## 3D Printed Part: Dock Floor Rails (x2)

- **Envelope:** 2x rails, each ~3W x 130D x 2H mm
- **Features:**
  - Two parallel rails on enclosure floor
  - Inside edge to inside edge ~142mm center-to-center
  - Smooth top face for low-friction sliding
  - Chamfered/ramped entry
- **Interfaces:**
  - Cartridge base grooves (3mm wide x 2.5mm deep) ride on these rails
  - Rail clearance: 0.3-0.5mm per side

## 3D Printed Part: Dock Side Guides (x2)

- **Envelope:** 2x guides, each ~1.5W x 130D x 84H mm
- **Features:**
  - 1.5mm wide rails on enclosure side walls within cartridge slot zone
  - Prevent lateral wobble during insertion
  - Clearance: 0.3-0.5mm per side to cartridge shell

## 3D Printed Part: Chamfered Slot Entrance

- **Envelope:** ~158W x ~20D x ~94H mm
- **Features:**
  - 5mm chamfer on all edges of cartridge slot opening
  - Funnel from ~158W x ~94H to ~148W x ~84H over 15-20mm depth
  - Accepts cartridge with 10-15mm initial misalignment

---

## Purchased Parts

### 1/4" OD Hard Nylon Tube Stubs (x4, dock side)

- 6.35mm OD, ~60-80mm length (passes through wall, protrudes both sides)
- Front protrusion: ~30mm (cartridge JG fittings slide onto these)
- Rear protrusion: connects to valve rack tubing

### Rubber Grommets (x4)

- 7mm ID, ~11mm OD
- Seal tube stub pass-throughs in dock back wall

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Dock placement research:** `research/dock-placement.md`
- **Guide alignment research:** `research/guide-alignment.md`
- **Cartridge shell (mating part):** `../../cartridge-shell/planning/parts.md`
- **Pogo pin mount (ceiling):** `../../pogo-pin-mount/planning/parts.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
