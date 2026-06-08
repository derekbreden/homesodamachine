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
| Electronics shelf | Top-back of enclosure, immediately behind C14 inlet | C14 inlet, AC distribution block, Legrand Radiant 1597BKCCD12 GFCI (UL 943 Class A, [6 mA](GFCI_TRIP), self-test; inline between C14 inlet LOAD and the AC distribution block — see [`/business/regulatory.md`](/business/regulatory.md) "UL 943 — ground-fault protection"), Mean Well IRM-90-12ST PSU, Teyleten relay #1 (compressor switch), Teyleten relay #2 (diaphragm pump switch), ESP32-DevKitC-32E, MCP23017, 2× ULN2803A modules, L298N pump driver, [5 V](V_LOGIC) + [3.3 V](V_IO) regulators, ground bus |
| Compressor zone | Middle-bottom of enclosure | Hermetic compressor + clip-on PTC start relay/overload module, condenser fan, **fire-rated shroud over the compressor terminal block** (see [`/hardware/cut-parts/compressor-shroud/`](/hardware/cut-parts/compressor-shroud/)) |

The Teyleten relay #1 sits with the rest of the electronics, **outside** the compressor shroud. Switched AC enters the shroud as the only mains-side penetration. Rationale: avoid placing an arcing contact inside the protected hydrocarbon-refrigerant compartment, and minimize the wire count through the shroud wall ([3](SHROUD_WIRES) wires — switched H + N + G — vs. [5](SHROUD_WIRES_ALT) if the relay were inside). See [`/hardware/future.md`](/hardware/future.md) "Compressor compartment shroud".

## Run table

Per-run gauges, terminations, and approximate lengths. Lengths assume the enclosure layout in [`/hardware/future.md`](/hardware/future.md) "Enclosure layout"; revise once the prototype enclosure is mocked up and lengths are measured.

### AC mains ([120 V](V_LINE))

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| AC-1a | C14 inlet (rear panel) | Legrand Radiant 1597BKCCD12 GFCI **LINE** terminals (mounted on the electronics shelf) | H + N + G | [16](AWG_MAINS) | [~150 mm](LEN_MID) (short run on the shelf — C14 inlet sits directly behind the shelf) | Crimp ferrules at C14 pigtail; backstab or screw at LINE terminals | Inlet ships with solder-tab pins; [16 AWG](AWG_MAINS_U) appliance wire makes a short on-shelf run to the GFCI's LINE terminals. Earth conductor passes through the device (LINE earth → LOAD earth) without being sensed — only H and N feed the CT. See [`/business/regulatory.md`](/business/regulatory.md) "UL 943 — ground-fault protection". |
| AC-1b | Legrand Radiant 1597BKCCD12 GFCI **LOAD** terminals | AC distribution block on electronics shelf | H + N + G | [16](AWG_MAINS) | [~150 mm](LEN_MID) (short on-shelf run — both ends co-located) | Backstab or screw at LOAD terminals; crimp ferrules into Wago 221 lever block | Switched mains downstream of the GFCI feeds the distribution block; all downstream loads (PSU, compressor, etc.) are protected. |
| AC-2 | AC distribution block (H, N) | Mean Well IRM-90-12ST PSU primary terminals | H + N + G | [18](AWG_AC_BRANCH) | [~100 mm](LEN_SHORT_2) | Crimp ring or fork terminal at PSU; ferrule at distribution block | PSU primary draws [0.67 A](PSU_PRI_A) at [80 W](PSU_W) full load; [18 AWG](AWG_AC_BRANCH_U) ample. Ground bonds PSU chassis. |
| AC-3 | AC distribution block (H) | Teyleten relay #1 contact input | H | [18](AWG_AC_BRANCH) | [~50 mm](LEN_SHORT) | Crimp fork to relay screw terminal | Unswitched hot leg into the relay's "common" terminal. |
| AC-4 | Teyleten relay #1 contact output ("normally open") | Compressor terminal block (inside shroud) | H_switched | [18](AWG_AC_BRANCH) | [~400 mm](LEN_COMPRESSOR) | Crimp fork to relay; female disconnect to compressor terminal | Switched hot. Routes through the shroud's grommeted AC pass-through. Length includes service slack. |
| AC-5 | AC distribution block (N) | Compressor terminal block (inside shroud) | N | [18](AWG_AC_BRANCH) | [~400 mm](LEN_COMPRESSOR) | Crimp ferrule at distribution block; female disconnect to compressor terminal | Routes through the same grommet as AC-4. |
| AC-6 | Earth bus on chassis ground point | Compressor body / shroud ground lug | G | [16](AWG_MAINS) | [~400 mm](LEN_COMPRESSOR) | Ring terminal both ends | Bonds the metal shroud and the compressor body to chassis ground. Routes through the same grommet as AC-4 / AC-5. |

The condenser fan does **not** appear in the AC table: the harvested fan is a [12 V](V_DC) DC brushless axial motor (the donor ice maker's own PCB regulated mains to [12 V](V_DC) to drive it; on harvest we keep the fan and discard the PCB). It rides on the [12 V](V_DC) bus instead — see run DC-9 below.

### Low-voltage logic ([3.3 V](V_IO) control side of the relays)

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| LV-1 | ESP32 GPIO 14 (relay #1 control) | Teyleten relay #1 input terminal (IN) | signal + GND | [24](AWG_LV) | [~150 mm](LEN_MID) | Screw terminals both ends (DIN-breakout → relay input terminal) | [3.3 V](V_IO) opto-isolated; no ground loop concern. |
| LV-2 | ESP32 GPIO 4 (relay #2 control) | Teyleten relay #2 input terminal (IN) | signal + GND | [24](AWG_LV) | [~150 mm](LEN_MID) | Screw terminals both ends | Diaphragm pump refill gate. |
| LV-3 | [5 V](V_LOGIC) regulator output | Teyleten relay #1 + #2 module VCC | + + GND | [24](AWG_LV) | [~100 mm](LEN_SHORT_2) each | Screw terminals (relay VCC) | Both relays share [5 V](V_LOGIC) module power; opto-isolation keeps the coil supply electrically separate from logic. |

### [12 V](V_DC) distribution

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| DC-1 | PSU [12 V](V_DC) output | [12 V](V_DC) distribution block on electronics shelf | + + GND | [16](AWG_MAINS) | [~100 mm](LEN_SHORT_2) | Crimp fork at PSU; ferrule at distribution block | PSU max [6.7 A](PSU_MAX_A); [16 AWG](AWG_MAINS_U) comfortable. |
| DC-2 | [12 V](V_DC) distribution block | Teyleten relay #2 contact input | + | [16](AWG_MAINS) | [~100 mm](LEN_SHORT_2) | Crimp fork to relay terminal | Switched [12 V](V_DC) to diaphragm pump. |
| DC-3 | Teyleten relay #2 contact output | SeaFlo diaphragm pump | + + GND | [16](AWG_MAINS) | [~250 mm](LEN_PUMP) | Female disconnect | Pump peaks at ~[5 A](DIAPHRAGM_A). |
| DC-4 | [12 V](V_DC) distribution block | L298N motor driver VS terminal | + + GND | [22](AWG_SIG) | [~150 mm](LEN_MID) | Screw terminal | Two peristaltic pumps draw [300](PERI_MA_LOW)–[500 mA](PERI_MA_HIGH) each. |
| DC-5 | L298N OUT-A / OUT-B | Kamoer pump A / pump B | + + GND each | [22](AWG_SIG) | [~250 mm](LEN_PUMP) to manifold + [~100 mm](LEN_SHORT_2) via pogo pins to cartridge | Magnetic pogo connector at the cartridge interface (BOM §8) | Pump cartridge is field-replaceable; pogo pins are the tool-free disconnect. |
| DC-6 | [12 V](V_DC) distribution block | ULN2803A #1 + #2 COM pin (each) | + | [18](AWG_AC_BRANCH) | [~150 mm](LEN_MID) | Pin header on ULN modules | Solenoid coil supply; ULN sinks to GND. |
| DC-7 | ULN2803A outputs ([12](SOLENOID_COUNT) channels used) | 12× Beduan solenoid coils on the manifold | + (per valve, GND shared at COM) | [22](AWG_SIG) | [~300 mm](LEN_MANIFOLD) to manifold, then [~150 mm](LEN_MID) fan-out per valve | Female disconnects per valve | Group as a [24](LOOM_CONDUCTORS)-conductor ribbon or wiring loom from the electronics shelf to the manifold; fan-out at the manifold to per-valve wires. |
| DC-8 | [12 V](V_DC) distribution block | [5 V](V_LOGIC) regulator input | + + GND | [22](AWG_SIG) | [~50 mm](LEN_SHORT) | Pin header / screw terminal | [5 V](V_LOGIC) rail feeds MCUs. |
| DC-9 | [12 V](V_DC) distribution block (+) and ULN2803A #2 channel 5 output (−) | Condenser fan motor ([12 V](V_DC) DC brushless axial, ~[0.35 A](FAN_A)) | + + ULN-sink return | [22](AWG_SIG) | [~400 mm](LEN_COMPRESSOR) (electronics shelf → side wall fan) | Female disconnects at the fan; pin header / screw terminal at ULN module | Low-side switching, same pattern as the solenoid coils (DC-7) — fan + side ties to the [12 V](V_DC) bus; ULN channel 5 sinks the − side to GND when commanded. Driven by MCP23017 0x21 PA4. Flyback path provided by the ULN2803A's integrated diode to COM (already wired to [12 V](V_DC) via DC-6). |

### Sensors and signal (low-voltage, low-current)

| # | From | To | Conductors | AWG | Approx. length | Notes |
|---|---|---|---|---|---|---|
| SIG-1 | DS18B20 1-wire bus (tank wall + evap suction probes) | ESP32 GPIO 16 + [3.3 V](V_IO) + GND | data + [3.3 V](V_IO) + GND, parallel-bussed | [22](AWG_SIG) | [~600 mm](LEN_COLD_CORE) to back of cold core | [4.7 kΩ](DS18B20_PULLUP) pull-up between data and [3.3 V](V_IO) (BOM §1). |
| SIG-2 | Reed switch — low (carbonator) | ESP32 GPIO 17 + GND | switch + GND | [24](AWG_LV) | [~600 mm](LEN_COLD_CORE) | INPUT_PULLUP. |
| SIG-3 | Reed switch — high (carbonator) | ESP32 GPIO 27 + GND | switch + GND | [24](AWG_LV) | [~600 mm](LEN_COLD_CORE) | INPUT_PULLUP. |
| SIG-4 | DIGITEN flow meter | ESP32 GPIO 23 + [5 V](V_LOGIC) + GND | pulse + V + GND | [24](AWG_LV) | [~1 m](LEN_UMBILICAL) (from faucet zone through grommet) | Pulse interrupt. |
| SIG-7 | ESP32-S3 rotary display on front face (detachable) | ESP32 GPIO 15 (TX) + GPIO 34 (RX) + [5 V](V_LOGIC) + GND | UART + power | [24](AWG_LV) | [~1 m](LEN_UMBILICAL) extended (coiled when seated) | Per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism" — cord pays out behind the panel when the customer detaches the display. Cable type (Cat6 vs coiled stretch vs flat ribbon) TBD with the detach mechanism. |
| SIG-8 | DS3231 RTC + MCP23017 (I2C) | ESP32 GPIO 21 (SDA) + GPIO 22 (SCL) + [3.3 V](V_IO) + GND | I2C bus | [24](AWG_LV) | [~150 mm](LEN_MID) shared bus on shelf | Both devices co-located on the electronics shelf. |
| SIG-9 | Backflow vent moisture sensor | ESP32 GPIO (TBD) + GND | switch + GND | [24](AWG_LV) | [~600 mm](LEN_COLD_CORE) to drip pan inside cabinet | Per [`/hardware/future.md`](/hardware/future.md) "Backflow vent monitoring"; pin not yet assigned in [`esp32-pinout.mmd`](esp32-pinout.mmd). |

## Inter-module connectors

Module-to-module logic connections that land on **pin headers** use JST XH [2.54 mm](JST_PITCH) headers + housings; connections that land on **screw terminals** (the ESP32 DIN-breakout hub, the L298N power/motor terminals, the Teyleten relay in/out terminals) stay as screws — already vibration-secure. Some boards ship their headers pre-soldered (MCP23017 GPIO rows, L298N control row); desolder those before soldering the XH header. Pin-count assignments for the JST side:

| Pin count | Use | Per-unit qty |
|---|---|---:|
| 4-pin XH | DS3231 I²C (VCC / GND / SDA / SCL) + the UART trunk header (SIG-7). ESP32 ends land on DIN-breakout screws; the MCP I²C side is PH2.0, not XH | ~3 |
| 6-pin XH | L298N control row (ENA / IN1–4 / ENB) — the 6 lines driving both peristaltic pumps | ~1 |
| 9-pin XH | ULN2803A module sides (8 channels + COM or GND) — 2 ULNs × 2 sides | ~4 |
| 10-pin XH | MCP23017 GPIO rows (VCC + GND + 8 GPIO). The port row is **10 holes**; a 10-pin header fills the row so it — and the mating housing — cannot seat off-by-one. | ~3–4 |

**Pitch / pin-count note.** The MCP23017 **GPIO rows are 10-pin** (VCC + GND + 8 GPIO), 2.54 mm — earlier drafts called them 9-pin, which silently drops the VCC pin and leaves a 9-pin header free to seat one hole off on the 10-hole row (every signal shifts by one). Use a **10-pin** there. Separately, the MCP23017's **I²C side is PH2.0 (2.0 mm)**, not 2.54 mm XH: daisy-chain the I²C bus through each MCP on its native PH2.0 connector (or hand-solder its weld pads). A 2.54 mm XH header does **not** fit the MCP I²C connector — only the ESP32 and DS3231 ends of the I²C trunk are XH.

Two wire-stock formats feed those housings:

- **Bonded ribbon (CQRobot B0F6C7X5CR, 15 cm × 12-conductor × 8 ribbons)** — short-hop module-to-module connections under ~6". Factory pre-crimped female XH terminals on both ends; pop pins into the housing of choice at build time. Typical per-unit use: ~2 ribbons (e.g., one 9-conductor MCP↔ULN, one 4-conductor I²C / UART trunk).
- **Pre-crimped silicone pigtails (Keszoox B0F8HMQRRN, 50 cm × [22 AWG](AWG_SIG_U) × 20 wires × 10 colors)** — medium-length runs that span the cabinet. Typical use: ULN→solenoid fan-outs (~[12](SOLENOID_COUNT) valve fan-outs/unit) and sensor pigtails. One 20-wire pack covers a build with spares.

Per-build parts in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

## Grounding strategy

Single-point chassis ground at the electronics shelf, bonded back through the C14 inlet's earth pin to the building's protective earth.

- **C14 ground pin** → ground bus on electronics shelf (runs AC-1a + AC-1b carry the green conductor through the GFCI's pass-through earth terminals; earth is not sensed by the device).
- **Ground bus** distributes to: PSU chassis (via AC-2 ground), compressor body / shroud (via AC-6), and any other exposed metal (faucet via the SS under-counter plate, the SS pressure vessel inside the cold core, etc.) via short bonding wires. Chassis grounding is via these discrete bonding wires; there is no metal chassis backbone.
- All ground conductors are [16 AWG](AWG_MAINS_U) green-insulated. Ring terminals at the bus, ring or fork terminals at the load.
- The chassis bond gives the appliance Class I status: if a fault energizes any exposed metal part, fault current returns to the building ground through the C14 cord and trips the upstream breaker before the user touches anything.

## What's not yet decided

- **Fuse on the AC primary** — a [5 A](PRIMARY_FUSE_A) fast-blow inline fuse between the C14 inlet and the AC distribution block was discussed in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) for bench testing. Whether it stays in the production unit (fuse holder on the rear panel? fuse on the shelf?) needs a decision.
- **Distribution block hardware** — Wago 221 lever blocks vs. screw terminal block vs. PCB-mounted block. Wago is the fastest hand-build option.
- **Wiring loom organization between the electronics shelf and the valve manifold** — [24](LOOM_CONDUCTORS) conductors want to be a single bundled run (ribbon cable, twisted pairs, or a simple zip-tied loom). TBD when the manifold is mocked up.
- **Backflow moisture sensor pin assignment** — needs to land in `esp32-pinout.mmd`.

## Revision

Initial draft. Lengths are estimates based on the [`/hardware/future.md`](/hardware/future.md) layout; measure and update once the first build's enclosure is in hand.

## Sources
[value](NAME) texts are updated by:
- `/hardware/wiring/_ac_wiring_schedule_sync.py`
