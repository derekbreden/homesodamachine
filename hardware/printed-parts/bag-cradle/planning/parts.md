# Bag Cradle

Profiled diagonal cradle holding two 2L Platypus bags at 35 degrees from horizontal.

See `../../../planning/architecture.md` for system architecture and `../../../planning/spatial-layout.md` for coordinates.

---

## 3D Printed Part: Diagonal Bag Cradle

- **Type:** 3D printed
- **Material:** PETG (food-safe, contacts bag exterior only)
- **Envelope:** ~200W x ~350L (along diagonal) x ~50H mm (profiled depth varies)
- **Features:**
  - Profiled channel matching lens-shaped cross-section of two stacked 2L Platypus bags
  - Channel depth at center (deepest point): ~40mm
  - Channel depth at ends: tapering to ~5mm
  - Channel width: 190mm (bag width) + 5mm margin per side = 200mm
  - 2-3mm lip on each side to prevent lateral bag sliding
  - Mounting tabs/brackets at ends and midpoint
  - Diagonal angle: 35 degrees from horizontal
  - Bag length supported: 350mm
- **Interfaces:**
  - Mounts to enclosure interior walls via brackets or snap-fit tabs
  - 6mm clearance per side between cradle edge and enclosure wall
  - Lower end (cap/connector end): approximately Y=25, Z=125
  - Upper end (sealed end): approximately Y=292, Z=392
- **Quantity:** 1 (may print as 2-3 segments)
- **Open:** Exact channel profile (needs physical measurement of filled 2L bag cross-section), mounting bracket design, print segmentation

## 3D Printed Part: Back-Wall Bag Pin / Clamp

- **Envelope:** ~100W x ~20D x ~30H mm
- **Features:**
  - Holds flat sealed end of each bag pinned against back wall at highest point
  - Accommodates two bags stacked (~2mm thick at sealed end)
  - Spring-loaded clamp with M3 screw adjustment
- **Interfaces:**
  - Mounts to interior back wall near Z=380-392, Y=288-292
- **Quantity:** 1 (shared for both bags)

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Bag research:** `research/diagonal-bag-placement.md`, `research/bag-dimensions-survey.md`, `research/2l-bags-at-300mm-depth.md`
- **Bag geometry:** `research/2l-rigid-body-geometry.svg`
- **Diagonal risks:** `research/diagonal-risks-and-failure-modes.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
