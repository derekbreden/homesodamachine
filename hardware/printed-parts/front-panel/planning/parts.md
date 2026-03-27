# Front Panel

The front face of the enclosure. Contains the cartridge slot opening and two display dock recesses.

See `../../../planning/architecture.md` for system architecture and `../../../planning/spatial-layout.md` for coordinates.

---

## 3D Printed Part: Front Panel

- **Type:** 3D printed
- **Material:** ABS or ASA (match enclosure shell)
- **Envelope:** 220W x 4D x 400H mm
- **Features:**
  - Cartridge slot opening: 148W x 84H mm, centered in width, bottom at Z=0
  - Chamfered slot entrance: 5mm chamfer on all edges of cartridge opening for blind insertion
  - Two display dock recesses: 50mm diameter x 5mm deep, centered at X=55 Z=275 and X=157 Z=275
  - Cable exit holes in dock recesses: ~8mm diameter for flat cat6
  - Status LED window: small, near cartridge slot (position TBD)
- **Interfaces:**
  - Attaches to enclosure main body front edge
  - Display dock recesses accept magnetic display pucks (magnets in recess surround)
  - Cartridge slot edges align with internal floor rails
- **Quantity:** 1
- **Open:**
  - Whether front panel is integral to main body or separate/removable
  - Display dock recess sizing: both currently spec'd at 50mm diameter. The S3 module is 48x48mm (good fit). The RP2040 is 33mm diameter (oversized at 50mm). Options: uniform 50mm (simpler), different diameters (better fit), or S3 in square recess without puck shell. See `../../display-system/planning/parts.md` for variant analysis.

---

## Display Module Dimensions (for recess design)

### RP2040 Variant (Waveshare RP2040-LCD-0.99-B)
- 33mm diameter x 9.8mm thick (CNC aluminum case)
- 0.99" IPS display, ~25mm visible area
- USB-C on side

### S3 Variant (Meshnology ESP32-S3 Rotary Display)
- 48 x 48 x 33mm (square with rounded corners)
- 1.28" IPS, 32.4mm active area
- Rotary encoder knob (reason for 33mm depth)
- FPC + MX1.25 connectors on bottom (NOT USB-C)

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Display system (pucks, reels):** `../../display-system/planning/parts.md`
- **Display research:** `research/display-and-front-panel.md`
- **RP2040 dimensions:** `../../display-system/planning/research/waveshare-rp2040-lcd-dimensions.md`
- **S3 dimensions:** `../../display-system/planning/research/meshnology-s3-display-dimensions.md`
- **Enclosure shell:** `../../enclosure-shell/planning/parts.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
