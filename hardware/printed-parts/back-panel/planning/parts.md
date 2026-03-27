# Back Panel

The rear face of the enclosure. Contains all external fluid connections and the power inlet.

See `../../../planning/architecture.md` for system architecture and `../../../planning/spatial-layout.md` for coordinates.

---

## 3D Printed Part: Back Panel

- **Type:** 3D printed (integral to enclosure or separate/removable)
- **Material:** ABS or ASA (match enclosure)
- **Envelope:** 220W x 4D x 400H mm (exterior face)
- **Features:**
  - **Upper zone (Z=340-380):**
    - IEC C14 panel-mount inlet: rectangular cutout 27.4W x 19.8H mm, two M3 mounting holes at 40mm horizontal c-t-c
    - Position: X=165, Z=370
    - 25mm interior clearance for terminal tabs
  - **Lower zone (Z=30-70):**
    - Tap water inlet: 15.9mm (5/8") hole for JG PP1208W bulkhead, at X=30, Z=50
    - Soda water inlet: 15.9mm hole, at X=80, Z=50
    - Soda water outlet: 15.9mm hole, at X=130, Z=50
    - All three with exterior 90-degree elbows (JG PP0308W)
    - 30mm interior clearance per fitting
  - **Mid zone (Z=180-220):**
    - Flavor line 1 exit: 12.5mm hole for PG7 cable gland, at X=50, Z=200
    - Flavor line 2 exit: 12.5mm hole, at X=170, Z=200
    - 15mm interior clearance per gland
  - Color-coding rings and embossed labels at each fitting position
- **Interfaces:**
  - IEC C14 interior tabs connect to PSU
  - JG water fittings connect to internal tubing
  - PG7 glands clamp around continuous 1/4" OD silicone flavor tubes
  - Flow meter mounts on interior behind soda water fittings (see `../../flow-meter-mount/planning/parts.md`)
- **Quantity:** 1
- **Open:** Whether integral or removable

---

## Purchased Parts

### JG PP1208W Bulkhead Union (x3, back panel water fittings)

Full geometry: `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`

- 1/4" push-to-connect on both sides, requires 15.9mm panel hole
- For: tap water inlet, soda water inlet, soda water outlet

### JG PP0308W 90-Degree Elbow (x3)

- ~20mm x 20mm x 15mm
- Direct incoming tubes downward on exterior, preventing kinking against cabinet wall

### IEC C14 Panel-Mount Inlet with Fuse (x1)

- Panel cutout: 27.4W x 19.8H mm, 40mm horizontal M3 mounting holes
- 10A 250VAC rated, integrated fuse holder (3A slow-blow)

### PG7 Nylon Cable Glands (x2)

- 12.5mm panel hole, clamping range 3-6.5mm (fits 6.35mm OD silicone tube)
- IP68 rated

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Back panel layout research:** `research/back-panel-layout.md`
- **Flow meter mount:** `../../flow-meter-mount/planning/parts.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
