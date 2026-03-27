# Flow Meter Mount

Bracket for mounting the DIGITEN inline flow sensor behind the back panel.

See `../../../planning/spatial-layout.md` for enclosure coordinates.

---

## 3D Printed Part: Flow Meter Mount Bracket

- **Type:** 3D printed bracket/clip
- **Material:** PETG or ABS
- **Envelope:** ~70W x ~40D x ~45H mm
- **Features:**
  - Holds DIGITEN 1/4" quick-connect flow sensor (63.5L x 30.5W x 38.1H mm)
  - Clip or saddle with two M3 screw holes into heat-set inserts on enclosure floor
  - Sensor oriented with 1/4" QC ports facing left and right (toward inlet and outlet bulkheads)
- **Interfaces:**
  - Position: approximately X=80-144, Y=262-292 (against back wall), Z=0-40
  - Signal cable (3-wire) routes up back wall interior to electronics zone
  - 1/4" hard tube: ~80mm from soda inlet bulkhead to sensor inlet; ~80mm from sensor outlet to soda outlet bulkhead
- **Quantity:** 1

---

## Purchased Part: DIGITEN 1/4" Quick-Connect Hall-Effect Flow Sensor (x1)

- **Material:** Food-grade POM body
- **Envelope:** 63.5L x 30.5W x 38.1H mm
- **Features:**
  - 1/4" push-to-connect fittings on both ends
  - Flow range: 0.3-10 L/min
  - Pulse output: F = 36 x Q (L/min)
  - Working voltage: DC 3-24V
  - 3-wire cable: VCC (red), GND (black), signal (yellow), ~15cm factory length
- **Interfaces:**
  - Inline between soda water inlet and outlet bulkheads on back panel
  - Signal cable to ESP32 GPIO 23 (extend to ~300mm)

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Back panel (bulkhead fittings):** `../../back-panel/planning/parts.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
