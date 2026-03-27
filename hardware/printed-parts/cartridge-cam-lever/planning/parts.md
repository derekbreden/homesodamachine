# Cartridge Cam Lever

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale.

---

## 3D Printed Part: Cam Lever

- **Type:** 3D printed
- **Material:** PETG
- **Envelope:** 90L x 18W x 14H mm (handle length x width x cam body diameter)
- **Features:**
  - Handle: 76mm long from pivot center, ergonomic grip cross-section (18W x 10H mm, rounded edges)
  - Eccentric cam lobe at pivot end: 1.5mm eccentricity (produces 3mm stroke over 180-degree rotation)
  - Cam OD: 14mm
  - Pivot bore: 5mm diameter for pivot pin
  - Over-center geometry: cam profile allows lever to pass 2 degrees past maximum displacement for self-locking
  - Small detent bump (0.3mm) on cam track for tactile click at locked position
  - Push rod contact surface on cam face: slightly convex (1mm crown over 10mm)
- **Interfaces:**
  - Pivots on 5mm steel pin through outer shell front wall
  - Cam face pushes against push rod, which transmits force to release plate
  - Handle serves as pull grip for cartridge removal
  - Over-center position locks lever against shell front face
- **Quantity:** 1
- **Open:** Lever handle shape (straight vs curved). External vs internal cam.

---

## Purchased Parts

### Push Rod (x1)

- 5mm steel rod (smooth ground), 118mm long
- Front end contacts cam lobe, rear end contacts release plate push rod boss
- Slides through front wall hole (5.5mm through-hole, 0.25mm diametral clearance)

### Pivot Pin (x1)

- 5mm steel, 26mm long (4mm wall + 18mm lever + 4mm retention)
- Retained by E-clip on exterior end

### E-Clip (x1)

- 5mm shaft size, spring steel
- Prevents axial withdrawal of pivot pin

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Cam lever research:** `research/cam-lever.md`
- **Release plate (receives force):** `../../cartridge-release-plate/planning/parts.md`
- **Shell (pivot mount):** `../../cartridge-shell/planning/parts.md`
