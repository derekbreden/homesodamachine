# GPIO & I/O Planning -- ESP32 + MCP23017

Comprehensive pin assignment map for the soda flavor injector system. Covers all 34 ESP32 GPIOs (0-39), the MCP23017 I2C expander (16 pins), and the I2C bus device inventory.

**Last updated from firmware:** `src/main.cpp` pin definitions, verified against hardware research documents.

---

## 1. ESP32 GPIO Map -- Complete

### 1a. Currently Assigned (Firmware)

| GPIO | Direction | Function | Driver/Peripheral | Notes |
|------|-----------|----------|-------------------|-------|
| 4 | Output | B_ENB -- Flavor 2 dispensing solenoid | L298N Board B ENB | PWM capable |
| 5 | Output | B_IN2 -- Flavor 2 pump direction | L298N Board B IN2 | Strapping pin (must be HIGH at boot or left floating) |
| 12 | Output | A_ENB -- Flavor 1 dispensing solenoid | L298N Board A ENB | Strapping pin (must be LOW at boot to avoid flash voltage error). Current assignment works because solenoid is off at boot |
| 13 | Input | FLAVOR_SW -- Air switch (flavor select toggle) | Digital input, pulled up | Usable at boot, no restrictions |
| 15 | Output | CONFIG_TX -- UART TX to ESP32-S3 | Serial1 TX | Strapping pin (controls boot log silence). Chosen to free GPIO 2 |
| 17 | Output | CLEAN_SOL2 -- Clean solenoid flavor 2 | L298N Board C ENB | No restrictions |
| 18 | Output | B_IN1 -- Flavor 2 pump direction | L298N Board B IN1 | No restrictions |
| 19 | Output | B_ENA -- Flavor 2 pump PWM | L298N Board B ENA | PWM capable |
| 21 | I/O | I2C SDA | Wire library | Shared bus: DS3231, FDC1004, MCP23017 |
| 22 | I/O | I2C SCL | Wire library | Shared bus: DS3231, FDC1004, MCP23017 |
| 23 | Input | FLOW -- Flow meter pulse | Interrupt-driven | No restrictions |
| 25 | Output | A_IN1 -- Flavor 1 pump direction | L298N Board A IN1 | DAC1 (analog output capable, unused) |
| 26 | Output | A_IN2 -- Flavor 1 pump direction | L298N Board A IN2 | DAC2 (analog output capable, unused) |
| 27 | Output | CLEAN_SOL1 -- Clean solenoid flavor 1 | L298N Board C ENA | No restrictions |
| 32 | Output | DISPLAY_TX -- UART TX to RP2040 | Serial2 TX | No restrictions |
| 33 | Output | A_ENA -- Flavor 1 pump PWM | L298N Board A ENA | PWM capable, input-only on some ESP32 variants (safe on DevKitC) |
| 34 | Input | CONFIG_RX -- UART RX from ESP32-S3 | Serial1 RX | **Input-only** (no output driver). Appropriate for RX |
| 35 | Input | DISPLAY_RX -- UART RX from RP2040 | Serial2 RX | **Input-only** (no output driver). Appropriate for RX |

**Total assigned: 18 GPIOs**

### 1b. Planned Assignment (From Research)

| GPIO | Direction | Function | Notes |
|------|-----------|----------|-------|
| 14 | Output | Hopper solenoid valve flavor 1 (SV-H1) | Via MOSFET driver. Last free output GPIO pair. See Section 5 for alternative |
| 16 | Output | Hopper solenoid valve flavor 2 (SV-H2) | Via MOSFET driver. GPIO 16 is UART2 RXD by default -- safe to reassign since UART2 RX is on GPIO 35 |

**After hopper solenoids: 0 free output-capable GPIOs on ESP32.**

### 1c. Available but Restricted GPIOs

| GPIO | Restriction | Status |
|------|-------------|--------|
| 0 | Strapping pin: must be HIGH at boot (internal pull-up). Connected to BOOT button on DevKitC. Usable as output AFTER boot, but risky -- pulling LOW during reset causes download mode | **Reserve -- do not assign** |
| 1 | Default UART0 TX (USB serial console/programming). Reassigning breaks USB debug output | **Reserved for USB serial** |
| 2 | Strapping pin: must be LOW at boot for normal flash. Connected to onboard LED on some boards. Can cause flash failures if driven HIGH externally at boot | **Reserve -- do not assign** |
| 3 | Default UART0 RX (USB serial console/programming). Reassigning breaks USB serial input | **Reserved for USB serial** |
| 6-11 | **Connected to internal SPI flash.** Using these GPIOs crashes the ESP32 | **Unavailable -- do not use** |

### 1d. Input-Only GPIOs (No Output Capability)

| GPIO | Status |
|------|--------|
| 34 | **Assigned** -- CONFIG_RX (S3 UART) |
| 35 | **Assigned** -- DISPLAY_RX (RP2040 UART) |
| 36 (SVP) | **Free** -- input-only. Could be used for an additional sensor input (e.g., second flow meter, analog sensor). No internal pull-up/pull-down |
| 39 (SVN) | **Free** -- input-only. Same constraints as GPIO 36. No internal pull-up/pull-down |

### 1e. Complete GPIO Summary Table

| GPIO | Status | Assignment |
|------|--------|------------|
| 0 | Reserved | Boot strapping (BOOT button) |
| 1 | Reserved | UART0 TX (USB serial) |
| 2 | Reserved | Boot strapping (must be LOW at boot) |
| 3 | Reserved | UART0 RX (USB serial) |
| 4 | **Assigned** | B_ENB (flavor 2 dispensing solenoid) |
| 5 | **Assigned** | B_IN2 (flavor 2 pump direction) |
| 6-11 | Unavailable | Internal SPI flash |
| 12 | **Assigned** | A_ENB (flavor 1 dispensing solenoid) |
| 13 | **Assigned** | FLAVOR_SW (air switch input) |
| 14 | **Planned** | Hopper solenoid flavor 1 |
| 15 | **Assigned** | CONFIG_TX (S3 UART TX) |
| 16 | **Planned** | Hopper solenoid flavor 2 |
| 17 | **Assigned** | CLEAN_SOL2 (clean solenoid 2) |
| 18 | **Assigned** | B_IN1 (flavor 2 pump direction) |
| 19 | **Assigned** | B_ENA (flavor 2 pump PWM) |
| 20 | N/A | Not exposed on ESP32-WROOM-32 |
| 21 | **Assigned** | I2C SDA |
| 22 | **Assigned** | I2C SCL |
| 23 | **Assigned** | FLOW (flow meter pulse) |
| 24 | N/A | Not exposed on ESP32-WROOM-32 |
| 25 | **Assigned** | A_IN1 (flavor 1 pump direction) |
| 26 | **Assigned** | A_IN2 (flavor 1 pump direction) |
| 27 | **Assigned** | CLEAN_SOL1 (clean solenoid 1) |
| 28-31 | N/A | Not exposed on ESP32-WROOM-32 |
| 32 | **Assigned** | DISPLAY_TX (RP2040 UART TX) |
| 33 | **Assigned** | A_ENA (flavor 1 pump PWM) |
| 34 | **Assigned** | CONFIG_RX (S3 UART RX, input-only) |
| 35 | **Assigned** | DISPLAY_RX (RP2040 UART RX, input-only) |
| 36 | **Free** | Input-only, no pull-up. Available for sensor input |
| 39 | **Free** | Input-only, no pull-up. Available for sensor input |

---

## 2. I2C Bus Device Inventory

All devices share the single I2C bus on GPIO 21 (SDA) / GPIO 22 (SCL).

| Device | I2C Address | Function | Bus Speed | Notes |
|--------|-------------|----------|-----------|-------|
| DS3231 RTC | 0x68 | Real-time clock for scheduling and logging | 400 kHz | Already in firmware. Battery-backed |
| FDC1004 | 0x50 | 4-channel capacitive sensor (liquid/air detection) | 400 kHz | Planned. Detects empty bags, air in lines, hopper empty. No new GPIOs needed |
| MCP23017 | 0x20 (default) | 16-pin GPIO expander | 400 kHz (max 1.7 MHz) | Planned. Address set by A0-A2 pins to GND. Up to 8 devices possible (0x20-0x27) |

**Bus topology:** ESP32 (master) -- short run (~100-200mm) to DIN rail area where all three devices mount. 4.7k pull-ups on SDA and SCL (may already be on DS3231 breakout board -- verify to avoid double pull-up).

**Bus capacity:** Three devices at 400 kHz is well within I2C limits. Total bus capacitance stays under 200pF with short wire runs.

---

## 3. MCP23017 Pin Assignment Plan

The MCP23017 provides 16 GPIOs in two 8-pin banks: GPA0-GPA7 and GPB0-GPB7. Each pin can be independently configured as input (with optional 100k internal pull-up) or output (push-pull, 25mA sink/source max per pin, 125mA per bank).

### 3a. Pin Assignments

| MCP Pin | Direction | Function | Priority | Notes |
|---------|-----------|----------|----------|-------|
| GPA0 | Output | Hopper solenoid valve flavor 1 (SV-H1) | High | Via MOSFET driver (solenoid draws ~500mA at 12V, far exceeds MCP pin current). See Section 5 for ESP32-vs-MCP decision |
| GPA1 | Output | Hopper solenoid valve flavor 2 (SV-H2) | High | Same MOSFET driver circuit as GPA0 |
| GPA2 | Input | Cartridge detection (microswitch or hall sensor) | High | Detects cartridge fully docked. Enables/disables pump drive. Use internal pull-up |
| GPA3 | Input | Lever position sensor (optional) | Medium | Detects cam lever locked vs. unlocked. Could be same microswitch as GPA2 if single sensor suffices |
| GPA4 | Output | Status LED -- green (cartridge locked) | Medium | Front panel indicator. Direct drive OK (~10-20mA) |
| GPA5 | Output | Status LED -- amber (cartridge unlocked/present) | Medium | Front panel indicator. Direct drive OK |
| GPA6 | -- | **Unassigned** | -- | Reserve for expansion |
| GPA7 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB0 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB1 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB2 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB3 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB4 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB5 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB6 | -- | **Unassigned** | -- | Reserve for expansion |
| GPB7 | -- | **Unassigned** | -- | Reserve for expansion |

**Assigned: 6 of 16 pins. Free: 10 pins.**

### 3b. MCP23017 Hardware Configuration

| Parameter | Value |
|-----------|-------|
| I2C address | 0x20 (A0=A1=A2 tied to GND) |
| VDD | 3.3V (from ESP32 3.3V rail) |
| RESET pin | Tied HIGH through 10k pull-up (or connected to ESP32 reset for synchronized reboot) |
| INTA/INTB | Optional. Connect to ESP32 GPIO 36 or 39 (input-only, free) for interrupt-on-change notification from cartridge detection switch. Eliminates polling |

### 3c. Interrupt Strategy (Optional but Recommended)

The MCP23017 has two interrupt output pins (INTA for bank A, INTB for bank B). Connecting INTA to ESP32 GPIO 36 (input-only, free) allows the ESP32 to receive immediate notification when the cartridge detection switch changes state, rather than polling the MCP23017 over I2C.

| Connection | ESP32 GPIO | Purpose |
|------------|------------|---------|
| MCP23017 INTA | GPIO 36 (SVP) | Interrupt on cartridge insert/remove, lever lock/unlock |
| MCP23017 INTB | GPIO 39 (SVN) | Reserve for future bank B interrupts |

This is not strictly required -- polling the MCP23017 every 100ms over I2C adds negligible bus load. But hardware interrupts give instant response for cartridge detection safety interlock.

---

## 4. FDC1004 Channel Assignment

The FDC1004 has 4 capacitive measurement channels (CIN1-CIN4). Each channel connects to an electrode (copper tape or foil strip) wrapped around a section of tubing.

| Channel | Sensing Location | Purpose |
|---------|-----------------|---------|
| CIN1 | Flavor 1 inlet tube (between bag and dock) | Detect empty bag / air ingestion for flavor 1 |
| CIN2 | Flavor 2 inlet tube (between bag and dock) | Detect empty bag / air ingestion for flavor 2 |
| CIN3 | Hopper 1 drain tube (funnel outlet) | Detect hopper empty (fill complete) for flavor 1 |
| CIN4 | Hopper 2 drain tube (funnel outlet) | Detect hopper empty (fill complete) for flavor 2 |

No additional GPIOs needed -- the FDC1004 communicates entirely over I2C.

---

## 5. ESP32-Native vs. MCP23017 Assignment Decision

### What MUST Stay on ESP32 Native GPIO

| Signal | Reason |
|--------|--------|
| Pump PWM (A_ENA, B_ENA) | Requires hardware PWM (LEDC) for speed control. MCP23017 has no PWM capability |
| Pump direction (A_IN1/IN2, B_IN1/IN2) | Time-critical during direction changes. Must be synchronous with PWM. Could technically go on MCP23017 but adds I2C latency to safety-critical motor control |
| UART TX/RX (all 4 pins) | Hardware UART peripherals are mapped to specific GPIOs. Cannot route through I2C |
| I2C SDA/SCL | Bus master pins, obviously must be native |
| Flow meter pulse (GPIO 23) | Interrupt-driven pulse counting at up to several kHz. MCP23017 interrupt latency (~1ms I2C round trip) would miss pulses |
| Air switch input (GPIO 13) | Could go on MCP23017, but it is already assigned and working. No reason to move it |

### What CAN Go on MCP23017

| Signal | Reason It Works on MCP23017 |
|--------|----------------------------|
| Hopper solenoid valves | On/off control only (no PWM). Latency tolerance: hundreds of milliseconds. Driven through MOSFET, so MCP pin just controls the gate |
| Cartridge detection switch | Slow-changing digital input. Polling at 100ms or interrupt via INTA is fine |
| Lever position sensor | Same as cartridge detection |
| Status LEDs | On/off or slow-blink. No timing sensitivity |
| Clean solenoid valves | Currently on ESP32 (GPIO 17, 27) and working. Could be migrated to MCP23017 to free 2 ESP32 GPIOs, but there is no need to move working assignments |
| Dispensing solenoid valves | Same as clean solenoids -- could move but no benefit |

### Recommendation

**Put hopper solenoids on MCP23017 (GPA0, GPA1), not on ESP32 GPIO 14/16.** This preserves GPIO 14 and 16 as the last two free output-capable ESP32 pins for any future need that genuinely requires native GPIO (e.g., an additional hardware PWM output, a bit-banged protocol, or a timing-critical signal). Hopper solenoids are simple on/off valves with no timing sensitivity -- they are ideal MCP23017 candidates.

If GPIO 14 and 16 are consumed by hopper solenoids, ANY future output need requires adding another MCP23017 (easy, but adds one more I2C device and another breakout board). Keeping them free provides a safety margin.

---

## 6. Signal Routing Notes

### 6a. Wire Groups and Proximity

| Wire Group | Wires | Gauge | Routing Zone | Keep Near |
|------------|-------|-------|-------------|-----------|
| I2C bus (SDA, SCL, VCC, GND) | 4 | 22 AWG | DIN rail area, upper zone | DS3231, MCP23017, FDC1004 -- all within ~200mm of ESP32 |
| UART to RP2040 (TX, RX, 5V, GND) | 4 | Cat6 (4 of 8 conductors) | Upper zone to front-face display | Magnetic pogo breakaway at display holder |
| UART to S3 (TX, RX, 3.3V, GND) | 4 | Cat6 (4 of 8 conductors) | Upper zone to front-face display | Magnetic pogo breakaway at display holder |
| L298N control (6 pins per board) | 6+6 | 22 AWG | ESP32 to L298N boards, upper zone | Route together per board, keep away from motor power |
| Motor power (L298N out to dock pogo) | 3 | 18-20 AWG | Upper zone down to dock fitting wall | GND, Motor A+, Motor B+. JST disconnect at pogo pin block |
| Solenoid power (L298N out to solenoids) | 2 per solenoid | 20 AWG | Upper zone down to dock/valve zone | Route with motor power, separate from signal wires |
| Flow meter signal | 3 | 22 AWG | Dock zone up to ESP32 | VCC, GND, pulse (GPIO 23). Keep away from motor power wires |
| Air switch | 2 | 22 AWG | Back panel to ESP32 | GPIO 13, GND |
| MCP23017 to MOSFET drivers | 2+ | 22 AWG | DIN rail area to MOSFET board | Short runs, signal level only |
| MOSFET driver to hopper solenoids | 2 per solenoid | 20 AWG | Upper zone to hopper solenoid mounting area | 12V switched power, keep away from signal wires |
| FDC1004 to sensing electrodes | 4 shielded | Coax or shielded 26 AWG | DIN rail area to tube sensing locations | Shielded cable critical for capacitive sensing accuracy. Keep away from solenoid/motor wires |
| Cartridge detection switch | 2 | 22 AWG | Dock fitting wall up to MCP23017 | Signal + GND. Can share conduit with pogo pin wires |
| Status LEDs | 2 per LED | 24 AWG | MCP23017 to front panel | Low current, no routing constraints |

### 6b. EMI Separation Rules

1. **Motor/solenoid power wires** (18-20 AWG, carrying switched inductive loads) must be physically separated from **signal wires** (I2C, UART, sensor) by at least 10-15mm, or cross at 90 degrees only.
2. **FDC1004 electrode cables** are the most noise-sensitive signals in the system. Route them away from all power wires and solenoid drivers. Shielded cable with shield grounded at the FDC1004 end only.
3. **I2C bus** is moderately noise-tolerant at 400 kHz with 4.7k pull-ups. Keep runs under 300mm. If noise is observed (I2C errors in logs), add 100-ohm series resistors on SDA and SCL near the ESP32.

---

## 7. Future Expansion Headroom

### 7a. Available Resources After Full Build-Out

| Resource | Available | Notes |
|----------|-----------|-------|
| ESP32 output GPIOs | 2 (GPIO 14, 16) | Only if hopper solenoids go on MCP23017 as recommended |
| ESP32 input-only GPIOs | 0-2 (GPIO 36, 39) | Free if MCP23017 INTA/INTB not used; 0 if interrupts are wired |
| MCP23017 pins | 10 of 16 | GPA6-7, GPB0-7 all unassigned |
| Additional MCP23017 devices | 7 more (112 GPIOs) | Addresses 0x21-0x27 available on same I2C bus |
| FDC1004 channels | 0 of 4 | All 4 channels assigned. A second FDC1004 would need a different address (not possible -- fixed at 0x50). Alternative: use MCP23017 GPIO + external RC circuit for crude capacitive sensing |
| I2C address space | ~120 addresses free | Ample room for additional I2C sensors/expanders |

### 7b. Possible Future Additions

| Feature | GPIO Source | Pins Needed | Notes |
|---------|------------|-------------|-------|
| Temperature/humidity sensor (SHT30/BME280) | I2C bus | 0 (I2C) | Environmental monitoring inside enclosure |
| Second flow meter | ESP32 GPIO 36 or 39 | 1 input | Requires interrupt-capable input; MCP23017 interrupt adds latency |
| Buzzer/beeper | MCP23017 GPB0 | 1 output | Simple on/off tone, no PWM needed for alert beep |
| Door/panel open sensor | MCP23017 GPBx | 1 input | Magnetic reed switch on enclosure access panel |
| Water leak detector | MCP23017 GPBx | 1 input | Conductivity probe in drip tray |
| Additional solenoid valves | MCP23017 GPBx + MOSFET | 1 output each | E.g., third flavor, bypass valve |
| Addressable LED strip (WS2812) | ESP32 GPIO 14 or 16 | 1 output | Requires native GPIO for precise bit-bang timing (can also use RMT peripheral) |

---

## 8. MOSFET Driver Circuit for MCP23017-Controlled Solenoids

The MCP23017 pins can sink/source 25mA max per pin. Solenoid valves draw ~500mA at 12V. A MOSFET driver is required between the MCP23017 output and the solenoid.

```
MCP23017 GPA0 ──── [10k] ──┬── Gate ┐
                            │        │
                         [100k]   IRLZ44N (logic-level N-MOSFET)
                            │        │
                           GND    Drain ── Solenoid (−) ── Solenoid (+) ── 12V
                                     │
                                  Source ── GND

                    Flyback diode (1N4007) across solenoid terminals
```

- **IRLZ44N**: Logic-level MOSFET, fully enhanced at 3.3V gate drive. RDS(on) < 0.1 ohm at 3.3V VGS.
- **10k gate resistor**: Limits inrush current from MCP23017 pin during switching.
- **100k pull-down**: Ensures MOSFET stays OFF if MCP23017 resets or I2C bus glitches.
- **1N4007 flyback diode**: Suppresses inductive kick when solenoid de-energizes. Cathode to 12V, anode to drain.

This same circuit applies to each solenoid controlled via MCP23017 (2 hopper solenoids = 2 MOSFET circuits).

---

## References

- `src/main.cpp` -- All current GPIO assignments (verified)
- `hardware/enclosure/research/layout-spatial-planning.md` -- Enclosure zones, MCP23017 placement, hopper solenoid GPIO discussion
- `hardware/enclosure/research/hopper-and-bag-management.md` -- Hopper solenoid valves, GPIO 14/16 as last free pair, MCP23017 alternative
- `hardware/cartridge/planning/research/dock-mounting-strategies.md` -- Cartridge detection sensor, MCP23017 for dock sensors
- `hardware/cartridge/planning/research/electrical-mating.md` -- Pogo pin contacts, moisture separation
- `hardware/enclosure/research/back-panel-and-routing.md` -- Wire routing, signal types, GPIO references
- [ESP32 Technical Reference Manual](https://www.espressif.com/en/support/documents/technical-documents) -- GPIO restrictions, strapping pins, input-only pins
- [MCP23017 Datasheet (Microchip)](https://www.microchip.com/en-us/product/MCP23017) -- Pin current limits, I2C addressing, interrupt outputs
- [FDC1004 Datasheet (TI)](https://www.ti.com/product/FDC1004) -- Fixed I2C address 0x50, 4-channel capacitive sensing
