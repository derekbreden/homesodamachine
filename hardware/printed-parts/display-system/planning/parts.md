# Display System

Two tethered display modules (RP2040 flavor display + S3 config display) connected via retractable flat cat6 cables. Each display sits in a magnetic puck shell that docks to the front panel.

See `../../../planning/architecture.md` for system architecture.

---

## 3D Printed Part: Display Reel Housing (x2)

- **Material:** ABS or PETG
- **Envelope:** ~70mm diameter x ~22mm deep (per reel)
- **Features:**
  - Spool hub: 24mm diameter
  - Winding width: 10mm (cable 7mm + 3mm margin)
  - Full spool OD: 70mm (calculated for 1m of flat cat6)
  - Spring housing: integrated, adds ~8mm depth
  - Constant-force or spiral torsion spring, 0.3-0.5N retraction force
  - Pull-to-lock, pull-to-release mechanism
  - Cable exit with ball-and-socket strain relief
- **Interfaces:**
  - Mounts behind front panel, cable exits through panel hole
  - Two reels side-by-side: 140mm total width (70mm each)
  - Reel depth: Y=0-22mm behind front panel
  - Positions: reel 1 at X≈71, reel 2 at X≈141
- **Connector variants:**
  - **RP2040:** USB-C on module side → USB-C breakout PCB in reel
  - **S3:** 12-pin FPC 0.5mm pitch + MX1.25 connectors → FPC breakout PCB or direct soldering
- **Open:** Spring type, lock mechanism, connector breakout PCB design

## 3D Printed Part: Display Puck Shell (x2)

- **Material:** ABS or polycarbonate
- **Envelope:** 50mm diameter x 12-15mm thick (see variant notes)
- **Features (common):**
  - Flat base with rubber grip ring, fold-out kickstand
  - 2-3 neodymium disc magnets (6mm dia x 2mm thick, 1-2 kg total pull force)
  - RJ45 jack recess with rubber flap (IPX2 minimum)
- **Interfaces (common):**
  - RJ45 jack connects to flat cat6 cable
  - Magnets mate with steel disc or magnets in front panel dock recess
  - Kickstand for countertop use

### RP2040 Variant (Waveshare RP2040-LCD-0.99-B)

- **Module:** 33mm diameter x 9.8mm thick, 17g, USB-C on side
- **Display:** 0.99" IPS (GC9107), 128x115px, ~25mm visible area
- **Fit:** 33mm module in 50mm shell = 8.5mm wall each side (oversized — consider 38-40mm puck)
- **Puck thickness:** ~13.3mm (9.8mm + 1.5mm lens + 2mm magnet recess)
- **Weight:** 25-32g total

### S3 Variant (Meshnology ESP32-S3 Rotary Display)

- **Module:** 48 x 48 x 33mm, 50g, rotary encoder knob
- **Display:** 1.28" IPS (GC9A01A), 240x240px, 32.4mm active area
- **Touch:** CST816D capacitive (I2C)
- **RGB LEDs:** 5x WS2812 around perimeter
- **Connectors:** 12-pin FPC + MX1.25 (NOT USB-C)
- **Fit:** 48mm in 50mm shell = 1mm wall each side (tight but workable)
- **Puck thickness:** ~35-37mm (33mm module depth). May not suit thin "puck" — consider direct dock seating.
- **Weight:** 55-65g total (exceeds 25-40g target; may need stronger magnets)

### Puck Diameter Design Decision (Open)

1. **Uniform 50mm** — simpler enclosure, RP2040 puck has thick walls
2. **Different diameters** — RP2040 ~38-40mm, S3 ~50mm. Better fit, more complex.
3. **S3 not in puck** — sits directly in square recess (48x48mm), only RP2040 gets a puck

---

## Purchased Parts

### Neodymium Disc Magnets (x4-6)
- 6mm diameter x 2mm thick, 0.3-0.5 kg pull each

### Constant-Force Springs (x2)
- Pre-stressed stainless steel strip, 0.3-0.5N, ~12mm hub

### Flat Cat6 Cable (x2)
- ~7mm wide x 3mm thick x 1000mm long
- Pinout: pins 1-2 (UART), pin 3 (RESET), pins 4-5 (VCC +5V), pin 6 (backlight PWM), pins 7-8 (GND)

### RJ45 Jacks (x2)
- Panel mount vertical, 8-pin cat6 rated

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **RP2040 dimensions:** `research/waveshare-rp2040-lcd-dimensions.md`
- **S3 dimensions:** `research/meshnology-s3-display-dimensions.md`
- **Display and front panel research:** `../../front-panel/planning/research/display-and-front-panel.md`
- **Front panel (dock recesses):** `../../front-panel/planning/parts.md`
