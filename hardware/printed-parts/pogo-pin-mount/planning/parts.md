# Pogo Pin Mount

Spring-loaded electrical contact for delivering 12V motor power to the removable pump cartridge.

See `../../../planning/spatial-layout.md` for enclosure coordinates.

---

## 3D Printed Part: Pogo Pin Mount

- **Type:** 3D printed bracket or small PCB mount
- **Material:** PETG bracket + FR4 PCB (if PCB-mounted)
- **Envelope:** ~60W x ~30D x ~10H mm
- **Features:**
  - Mounts to dock ceiling (underside of dock back wall top face at Z=80-84)
  - Holds 3-6 spring-loaded pogo pins (P75 or P100 series)
  - Pin diameter: 2-3mm, stroke: 1-2mm
  - Pin center-to-center spacing: 10mm
  - Minimum 3 pins: GND, Motor A 12V, Motor B 12V
  - Optional 3 more: cartridge ID, temp sensor, spare
  - Conformal coating on PCB traces; contact surfaces bare metal
  - X-position: centered at X=106 (centered on cartridge width)
  - Drainage channel in surrounding dock ceiling slopes away from pin pockets
- **Interfaces:**
  - Pins press onto cartridge top face pads (8mm x 5mm each, nickel-plated, 10mm c-t-c)
  - Guide rails position cartridge within ~0.5mm lateral tolerance
  - Oversized pads (8mm target for 2mm pin tip) tolerate 2-3mm misalignment
  - Wipe action: pin tip drags across elongated pad during slide-in
- **Quantity:** 1
- **Open:** PCB vs printed bracket. Exact pin count (3 min, 6 max).

---

## Purchased Parts

### Pogo Pins (x3-6)

- P75 or P100 series, brass/gold-plated tip, stainless steel spring
- 2-3mm diameter x ~16mm length
- Current rating: adequate for 3A transient
- Solder-tail for PCB mounting

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Electrical mating research:** `research/electrical-mating.md`
- **Dock back wall (mounting surface):** `../../dock-back-wall/planning/parts.md`
- **Cartridge shell (target pads):** `../../cartridge-shell/planning/parts.md`
