# Electronics Shelf

Mounting shelf for all control electronics in the top-rear corner of the enclosure, above and behind the diagonal bags.

See `../../../planning/architecture.md` for system architecture and `../../../planning/spatial-layout.md` for coordinates.

---

## 3D Printed Part: Electronics Mounting Shelf

- **Type:** 3D printed
- **Material:** PETG or ABS
- **Envelope:** ~190W x ~92D x ~4H mm (flat plate)
- **Features:**
  - Flat plate with standoff bosses (M3 heat-set inserts) for mounting PCBs
  - Mounting positions for:
    - ESP32 dev board: ~50 x 25mm
    - L298N motor drivers (x2): ~43 x 43mm each
    - MCP23017 breakout: ~25 x 25mm
    - DS3231 RTC module: ~25 x 25mm
    - PSU board: ~80 x 50mm (estimated)
  - Wire routing channels along edges
  - Ventilation holes/slots for PSU heat dissipation
- **Interfaces:**
  - Mounts to enclosure walls via brackets at Z≈275-280
  - Position: behind upper bag surface, above Y=200
  - PSU adjacent to IEC C14 inlet (shortest AC wire run)
  - Available height: ~117mm (Z=275-392), varies by depth due to diagonal bag above
- **Quantity:** 1
- **Open:** Exact component layout, single shelf vs multiple brackets, PSU dimensions

---

## Purchased Parts (Electronics)

### MCP23017 I2C GPIO Expander (x1)
- 16 GPIO: 10 for valves (GPB0-7, GPA0-1), 6 spare
- I2C to ESP32 (SDA=21, SCL=22)

### L298N Motor Driver Board (x2)
- ~43 x 43 x 27mm with heatsink
- Dual H-bridge, 12V, PWM speed control
- 2A continuous, 3A peak per channel

### PSU (x1)
- ~80 x 50 x 25mm estimated
- 120V AC in → 12V DC + 5V/3.3V out
- Power budget: ~23W typical, ~36W peak

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
- **System architecture:** `../../../planning/architecture.md`
