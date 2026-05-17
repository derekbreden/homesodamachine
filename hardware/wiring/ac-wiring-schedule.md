# AC Wiring Schedule

Run-by-run physical wiring spec for the appliance's AC and 12 V distribution. Companion to the topology diagrams in this directory:

- [`power.mmd`](power.mmd) — AC + 12 V topology (what connects to what)
- [`esp32-pinout.mmd`](esp32-pinout.mmd) — ESP32 pin assignments
- [`valve-control.mmd`](valve-control.mmd) — solenoid bus

This doc is the **physical wiring view** — gauges, run lengths, terminations, grounding. The topology files answer *what connects to what*; this file answers *how it's actually built*.

## Physical zones

The appliance has two functional electrical zones, both on the AC inlet side. The cold core occupies the rear of the enclosure (insulated, no electronics). The compressor + condenser sit middle-bottom. Everything else lives in **one electronics shelf at the top-back of the enclosure, directly behind the rear-panel C14 inlet**.

| Zone | Location | Contents |
|---|---|---|
| Electronics shelf | Top-back of enclosure, immediately behind C14 inlet | C14 inlet, AC distribution block, Mean Well IRM-90-12ST PSU, Teyleten relay #1 (compressor switch), Teyleten relay #2 (diaphragm pump switch), ESP32-DevKitC-32E, MCP23017, 2× ULN2803A modules, L298N pump driver, 5 V + 3.3 V regulators, ground bus |
| Compressor zone | Middle-bottom of enclosure | Hermetic compressor + clip-on PTC start relay/overload module, condenser fan, **fire-rated shroud over the compressor terminal block** (see [`../cut-parts/compressor-shroud/`](../cut-parts/compressor-shroud/)) |

The Teyleten relay #1 sits with the rest of the electronics, **outside** the compressor shroud. Switched AC enters the shroud as the only mains-side penetration. Rationale: avoid placing an arcing contact inside the protected hydrocarbon-refrigerant compartment, and minimize the wire count through the shroud wall (3 wires — switched H + N + G — vs. 5 if the relay were inside). See [`../future.md`](../future.md) "Compressor compartment shroud".

## Run table

Per-run gauges, terminations, and approximate lengths. Lengths assume the enclosure layout in [`../future.md`](../future.md) "Enclosure layout"; revise once the prototype enclosure is mocked up and lengths are measured.

### AC mains (120 V)

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| AC-1 | C14 inlet (rear panel) | AC distribution block on electronics shelf | H + N + G | 16 | ~50 mm (pigtail) | Crimp ferrules into Wago 221 lever block (or screw terminal block) | Inlet ships with solder-tab pins; pigtail with 16 AWG appliance wire and crimp ferrules to the distribution block. |
| AC-2 | AC distribution block (H, N) | Mean Well IRM-90-12ST PSU primary terminals | H + N + G | 18 | ~100 mm | Crimp ring or fork terminal at PSU; ferrule at distribution block | PSU primary draws 0.67 A at 80 W full load; 18 AWG ample. Ground bonds PSU chassis. |
| AC-3 | AC distribution block (H) | Teyleten relay #1 contact input | H | 18 | ~50 mm | Crimp fork to relay screw terminal | Unswitched hot leg into the relay's "common" terminal. |
| AC-4 | Teyleten relay #1 contact output ("normally open") | Compressor terminal block (inside shroud) | H_switched | 18 | ~400 mm | Crimp fork to relay; female disconnect to compressor terminal | Switched hot. Routes through the shroud's grommeted AC pass-through. Length includes service slack. |
| AC-5 | AC distribution block (N) | Compressor terminal block (inside shroud) | N | 18 | ~400 mm | Crimp ferrule at distribution block; female disconnect to compressor terminal | Routes through the same grommet as AC-4. |
| AC-6 | Earth bus on chassis ground point | Compressor body / shroud ground lug | G | 16 | ~400 mm | Ring terminal both ends | Bonds the metal shroud and the compressor body to chassis ground. Routes through the same grommet as AC-4 / AC-5. |
| AC-7 | AC distribution block (H) or compressor terminal | Condenser fan motor | H_switched + N | 18 | ~300 mm | Female disconnects | Condenser fan switches with the compressor (same Teyleten relay). Tap point is electrically equivalent — convention is to tap at the compressor terminal block alongside the compressor leads, so a single switched-H wire leaves the shroud rather than two. |

### Low-voltage logic (3.3 V control side of the relays)

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| LV-1 | ESP32 GPIO 14 (relay #1 control) | Teyleten relay #1 input pin (IN) | signal + GND | 24 | ~150 mm | Dupont female on ESP32 side; pin header on relay | 3.3 V opto-isolated; no ground loop concern. |
| LV-2 | ESP32 GPIO 4 (relay #2 control) | Teyleten relay #2 input pin (IN) | signal + GND | 24 | ~150 mm | Dupont female; pin header | Diaphragm pump refill gate. |
| LV-3 | 5 V regulator output | Teyleten relay #1 + #2 module VCC | + + GND | 24 | ~100 mm each | Pin header | Both relays share 5 V module power; opto-isolation keeps the coil supply electrically separate from logic. |

### 12 V distribution

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| DC-1 | PSU 12 V output | 12 V distribution block on electronics shelf | + + GND | 16 | ~100 mm | Crimp fork at PSU; ferrule at distribution block | PSU max 6.7 A; 16 AWG comfortable. |
| DC-2 | 12 V distribution block | Teyleten relay #2 contact input | + | 16 | ~100 mm | Crimp fork to relay terminal | Switched 12 V to diaphragm pump. |
| DC-3 | Teyleten relay #2 contact output | SeaFlo diaphragm pump | + + GND | 16 | ~250 mm | Female disconnect | Pump peaks at ~5 A. |
| DC-4 | 12 V distribution block | L298N motor driver VS terminal | + + GND | 22 | ~150 mm | Screw terminal | Two peristaltic pumps draw 300–500 mA each. |
| DC-5 | L298N OUT-A / OUT-B | Kamoer pump A / pump B | + + GND each | 22 | ~250 mm to manifold + ~100 mm via pogo pins to cartridge | Magnetic pogo connector at the cartridge interface (BOM §8) | Pump cartridge is field-replaceable; pogo pins are the tool-free disconnect. |
| DC-6 | 12 V distribution block | ULN2803A #1 + #2 COM pin (each) | + | 18 | ~150 mm | Pin header on ULN modules | Solenoid coil supply; ULN sinks to GND. |
| DC-7 | ULN2803A outputs (12 channels used) | 12× Beduan solenoid coils on the manifold | + (per valve, GND shared at COM) | 22 | ~300 mm to manifold, then ~150 mm fan-out per valve | Female disconnects per valve | Group as a 24-conductor ribbon or wiring loom from the electronics shelf to the manifold; fan-out at the manifold to per-valve wires. |
| DC-8 | 12 V distribution block | 5 V regulator input | + + GND | 22 | ~50 mm | Pin header / screw terminal | 5 V rail feeds MCUs. |

### Sensors and signal (low-voltage, low-current)

| # | From | To | Conductors | AWG | Approx. length | Notes |
|---|---|---|---|---|---|---|
| SIG-1 | DS18B20 1-wire bus (tank wall + evap suction probes) | ESP32 GPIO 16 + 3.3 V + GND | data + 3.3 V + GND, parallel-bussed | 22 | ~600 mm to back of cold core | 4.7 kΩ pull-up between data and 3.3 V (BOM §1). |
| SIG-2 | Reed switch — low (carbonator) | ESP32 GPIO 17 + GND | switch + GND | 24 | ~600 mm | INPUT_PULLUP. |
| SIG-3 | Reed switch — high (carbonator) | ESP32 GPIO 27 + GND | switch + GND | 24 | ~600 mm | INPUT_PULLUP. |
| SIG-4 | DIGITEN flow meter | ESP32 GPIO 23 + 5 V + GND | pulse + V + GND | 24 | ~1.0 m (from faucet zone through grommet) | Pulse interrupt. |
| SIG-5 | KRAUS air switch | ESP32 GPIO 13 + GND | switch + GND | 24 | ~1.0 m | Above-counter, through countertop grommet. |
| SIG-6 | RP2040 round display | ESP32 GPIO 32 (TX) + GPIO 35 (RX) + 5 V + GND | UART + power | 24 | ~1.5 m | Cat6 run through the countertop per [`../requirements.md`](../requirements.md) §5; uses 4 of 8 conductors. |
| SIG-7 | ESP32-S3 config display | ESP32 GPIO 15 (TX) + GPIO 34 (RX) + 5 V + GND | UART + power | 24 | ~1.5 m | Same Cat6 run, separate cable. |
| SIG-8 | DS3231 RTC + MCP23017 (I2C) | ESP32 GPIO 21 (SDA) + GPIO 22 (SCL) + 3.3 V + GND | I2C bus | 24 | ~150 mm shared bus on shelf | Both devices co-located on the electronics shelf. |
| SIG-9 | Backflow vent moisture sensor | ESP32 GPIO (TBD) + GND | switch + GND | 24 | ~600 mm to drip pan inside cabinet | Per [`../future.md`](../future.md) "Backflow vent monitoring"; pin not yet assigned in [`esp32-pinout.mmd`](esp32-pinout.mmd). |

## Inter-module connectors

Module-to-module logic connections on the electronics shelf use JST XH 2.54 mm headers + housings. Pin-count assignments:

| Pin count | Use | Per-unit qty |
|---|---|---:|
| 4-pin | I²C and UART hops between modules — ESP32↔MCP23017 (I²C), ESP32↔ESP32-S3 (UART), ESP32↔RP2040 (UART) | ~3 |
| 6-pin | DS3231 RTC bus (VCC / GND / SDA / SCL / SQW / 32K), or any 6-conductor module hop | ~1 |
| 9-pin | ULN2803A module sides (8 channels + COM/GND) and MCP23017 Port A / Port B rows (2 ULNs × 2 sides + 2 MCP ports) | ~6 |

Two wire-stock formats feed those housings:

- **Bonded ribbon (CQRobot B0F6C7X5CR, 15 cm × 12-conductor × 8 ribbons)** — short-hop module-to-module connections under ~6". Factory pre-crimped female XH terminals on both ends; pop pins into the housing of choice at build time. Typical per-unit use: ~2 ribbons (e.g., one 9-conductor MCP↔ULN, one 4-conductor I²C / UART trunk).
- **Pre-crimped silicone pigtails (Keszoox B0F8HMQRRN, 50 cm × 22 AWG × 20 wires × 10 colors)** — medium-length runs that span the cabinet. Typical use: ULN→solenoid fan-outs (~12 valve fan-outs/unit) and sensor pigtails. One 20-wire pack covers a build with spares.

Per-build parts in [`../bom.md`](../bom.md) §11.

## Grounding strategy

Single-point chassis ground at the electronics shelf, bonded back through the C14 inlet's earth pin to the building's protective earth.

- **C14 ground pin** → ground bus on electronics shelf (run AC-1 carries the green conductor).
- **Ground bus** distributes to: PSU chassis (via AC-2 ground), compressor body / shroud (via AC-6), and any other exposed metal (faucet via the SS under-counter plate, the SS pressure vessel inside the cold core, etc.) via short bonding wires. The appliance has no metal floor pan, back panel, or front-panel insert — see [`../future.md`](../future.md) "Other metal candidates considered, decided against" — so chassis grounding is via these discrete bonding wires rather than via a metal chassis backbone.
- All ground conductors are 16 AWG green-insulated. Ring terminals at the bus, ring or fork terminals at the load.
- The chassis bond gives the appliance Class I status: if a fault energizes any exposed metal part, fault current returns to the building ground through the C14 cord and trips the upstream breaker before the user touches anything.

## What's not yet decided

- **Fuse on the AC primary** — a 5 A fast-blow inline fuse between the C14 inlet and the AC distribution block was discussed in [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) for bench testing. Whether it stays in the production unit (fuse holder on the rear panel? fuse on the shelf?) needs a decision.
- **Distribution block hardware** — Wago 221 lever blocks vs. screw terminal block vs. PCB-mounted block. Wago is the fastest hand-build option.
- **Wiring loom organization between the electronics shelf and the valve manifold** — 24 conductors want to be a single bundled run (ribbon cable, twisted pairs, or a simple zip-tied loom). TBD when the manifold is mocked up.
- **Backflow moisture sensor pin assignment** — needs to land in `esp32-pinout.mmd`.

## Revision

Initial draft. Lengths are estimates based on the [`../future.md`](../future.md) layout; measure and update once the first build's enclosure is in hand.
