# Enclosure Shell

The outer box of the system. Houses all internal components. The front panel, back panel, and top panel are separate parts (may be integral or removable).

See `../../../planning/architecture.md` for system architecture and `../../../planning/spatial-layout.md` for full coordinate table.

---

## 3D Printed Part: Enclosure Main Body

- **Type:** 3D printed (multi-piece assembly) or injection molded
- **Material:** ABS or ASA
- **Envelope:** 220W x 300D x 400H mm (exterior)
- **Features:**
  - Wall thickness: 4mm solid, no ribs
  - Interior: 212W x 292D x 392H mm
  - Interior volume: ~24.3 liters
  - Front panel opening for cartridge slot: 148W x 84H mm, centered in width (X=36-184), bottom at Z=0
  - Back panel cutouts: see `../../back-panel/planning/parts.md`
  - Internal mounting bosses for electronics shelf, cradle brackets, valve rack, reel housings
- **Interfaces:**
  - Front panel: see `../../front-panel/planning/parts.md`
  - Back panel: integral or removable (M3 screws into heat-set inserts)
  - Top panel: removable or hinged for hopper access
  - Bottom: flat base with printed floor rails for cartridge dock
- **Quantity:** 1 (may be printed as 2-4 sub-pieces and bonded)
- **Open:** Print orientation and split line locations

## 3D Printed Part: Top Panel

- **Type:** 3D printed
- **Material:** ABS or ASA (match main body)
- **Envelope:** 220W x 300D x ~10H mm
- **Features:**
  - Central hole: 100mm diameter for hopper funnel, centered at X=110, Y=~40
  - Flip-up lid or removable cap over hopper hole
  - Seal: silicone gasket or lip around hopper opening
- **Interfaces:**
  - Mates to main body top edge via snap-fits, magnets, or M3 screws
  - Hopper funnel seats into opening from below (see `../../hopper/planning/parts.md`)
- **Quantity:** 1
- **Open:** Hinge mechanism type, seal design

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **System architecture:** `../../../planning/architecture.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
- **Front panel:** `../../front-panel/planning/parts.md`
- **Back panel:** `../../back-panel/planning/parts.md`
- **Hopper:** `../../hopper/planning/parts.md`
