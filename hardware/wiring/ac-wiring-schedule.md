# AC Wiring Schedule

Run-by-run physical wiring spec for the appliance's AC, 12 V, and signal distribution. Companion to the topology diagrams in this directory:

- [`power.mmd`](/hardware/wiring/power.mmd) — AC + 12 V topology (what connects to what)
- [`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) — ESP32 pin assignments
- [`valve-control.mmd`](/hardware/wiring/valve-control.mmd) — valve / reed expander map

This doc is the **physical wiring view** — gauges, run lengths, terminations, grounding. The topology files answer *what connects to what*; this file answers *how it's actually built*. The board end of every low-voltage run is fixed by the controller PCBA's edge connectors ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), the canonical pin map).

## Physical zones

The appliance has two functional electrical zones, both on the AC inlet side. The cold core occupies the rear of the enclosure (insulated, no electronics). The compressor + condenser sit middle-bottom. Everything else lives at **two electronics stations: the power tray on the pump-2 column at the front-right, and the controller PCBA + 12 V distribution block standing in the rear service plenum, directly in front of the rear-panel C14 inlet**.

| Zone | Location | Contents |
|---|---|---|
| Power tray | Pump-2 column, front-right | AC distribution block, Mean Well IRM-90-12ST PSU, Teyleten relay #1 (compressor switch), Teyleten relay #2 (diaphragm pump switch), ground bus — fed from the rear-panel C14 inlet via the +X riser channel |
| Rear plenum | Behind the cold core, in front of the C14 inlet | Controller PCBA, [12 V](V_DC) distribution block |
| Compressor zone | Middle-bottom of enclosure | Hermetic compressor + clip-on PTC start relay/overload module, condenser fan, **fire-rated shroud over the compressor terminal block** (see [`/hardware/cut-parts/compressor-shroud/`](/hardware/cut-parts/compressor-shroud/)) |

The controller PCBA is a single JLCPCB-assembled board carrying the ESP32-WROOM-32E, both MCP23017 expanders, the DS3231 RTC, both TBD62083 sink drivers, both DRV8870 pump H-bridges, and its own logic rails — [5 V](V_LOGIC) from the on-board K7805 buck (U10), [3.3 V](V_IO) from the on-board AMS1117 LDO (U9). It takes [12 V](V_DC) at the J10 screw inlet and presents every field interface as a labeled edge connector (next section); J14 is the USB-C programming port (bench cable only, no loom). Nothing on the shelf wires module-to-module: a low-voltage loom lands either on a board connector or on a relay module's terminals.

The Teyleten relay #1 sits with the rest of the electronics, **outside** the compressor shroud. Switched AC enters the shroud as the only mains-side penetration. Rationale: avoid placing an arcing contact inside the protected hydrocarbon-refrigerant compartment, and minimize the wire count through the shroud wall ([3](SHROUD_WIRES) wires — switched H + N + G — vs. [5](SHROUD_WIRES_ALT) if the relay were inside). See [`/hardware/future.md`](/hardware/future.md) "Compressor compartment shroud".

## Board connector map

Every low-voltage run below names its board connector and pin labels; the labels are on the silk, one JST XH wafer per loom (J10 is the lone screw block). There is no J12. [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) is canonical.

| Conn. | Silk label | Pins | Serves |
|---|---|---|---|
| J1 | MANIFOLD A | `COM`, `OUT1`–`OUT8` | 8 solenoid valves (DC-6) |
| J2 | MANIFOLD B | `COM`, `FAN`, `OUT1`–`OUT4` | 4 solenoid valves (DC-7) + condenser fan (DC-8) |
| J3 | FAUCET | `GND`, `V5`, `IO35`, `IO33` | faucet display UART up the umbilical (SIG-6) |
| J4 | SENSORS | `3V3`, `GND`, `V5`, `IO25`, `IO26`, `IO27`, `IO23` | DS18B20 bus (SIG-1), flow meter (SIG-4), moisture sensor (SIG-9) |
| J5 | RELAYS | `GND`, `V5`, `IO2`, `IO19` | both Teyleten relay modules (LV-1/2/3) |
| J6 | REEDS A | `GND`, `RA1`–`RA4` | reservoir A level reeds (SIG-10) |
| J7 | REEDS B | `RB1`–`RB4`, `CLO`, `CHI`, `GND` | reservoir B level reeds (SIG-11) + carbonator reeds (SIG-2, SIG-3) |
| J8 | I2C | `GND`, `3V3`, `SDA`, `SCL` | off-board MPR121 cap-sense controller (SIG-8) |
| J9 | DISPLAY | `B`, `A`, `GND`, `V12` | 4.3B config display, RS485 + [12 V](V_DC) (SIG-7) |
| J10 | 12V | `GND`, `V12` — 5.0 mm screw block | board power inlet (DC-4) |
| J11 | GAS | `GND`, `V5`, `DOUT`, `AOUT` | MQ-6 gas / refrigerant-leak sensor (SIG-12) |
| J13 | PUMPS | `AM2`, `AM1`, `BM2`, `BM1` | peristaltic pumps A + B (DC-5) |
| J14 | — | USB-C receptacle | programming port; no loom |

## Run table

Per-run gauges, terminations, and approximate lengths. Lengths assume the enclosure layout in [`/hardware/future.md`](/hardware/future.md) "Enclosure layout"; revise once the prototype enclosure is mocked up and lengths are measured.

### AC mains ([120 V](V_LINE))

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| AC-1 | C14 inlet (rear panel) | AC distribution block on electronics shelf | H + N + G | [16](AWG_MAINS) | [~400 mm](LEN_COMPRESSOR) (the C14 inlet is on the rear panel; the run crosses to the power tray along the +X riser channel) | Crimp ferrules at C14 pigtail; crimp ferrules into Wago 221 lever block | Inlet ships with solder-tab pins; [16 AWG](AWG_MAINS_U) appliance wire runs the +X riser channel to the distribution block. The C14 inlet lands directly on the AC distribution block with no device in series; all downstream loads (PSU, compressor, etc.) tap the block. Ground-fault protection is deferred — see [`/pie-in-the-sky/gfci.md`](/pie-in-the-sky/gfci.md). |
| AC-2 | AC distribution block (H, N) | Mean Well IRM-90-12ST PSU primary terminals | H + N + G | [16](AWG_AC_BRANCH) | [~100 mm](LEN_SHORT_2) | Crimp ring or fork terminal at PSU; ferrule at distribution block | PSU primary draws [0.67 A](PSU_PRI_A) at [80 W](PSU_W) full load; [16 AWG](AWG_AC_BRANCH_U) ample. Ground bonds PSU chassis. |
| AC-3 | AC distribution block (H) | Teyleten relay #1 contact input | H | [16](AWG_AC_BRANCH) | [~50 mm](LEN_SHORT) | Crimp fork to relay screw terminal | Unswitched hot leg into the relay's "common" terminal. |
| AC-4 | Teyleten relay #1 contact output ("normally open") | Compressor terminal block (inside shroud) | H_switched | [16](AWG_AC_BRANCH) | [~400 mm](LEN_COMPRESSOR) | Crimp fork to relay; female disconnect to compressor terminal | Switched hot. Routes through the shroud's grommeted AC pass-through. Length includes service slack. |
| AC-5 | AC distribution block (N) | Compressor terminal block (inside shroud) | N | [16](AWG_AC_BRANCH) | [~400 mm](LEN_COMPRESSOR) | Crimp ferrule at distribution block; female disconnect to compressor terminal | Routes through the same grommet as AC-4. |
| AC-6 | Earth bus on chassis ground point | Compressor body / shroud ground lug | G | [16](AWG_MAINS) | [~400 mm](LEN_COMPRESSOR) | Ring terminal both ends | Bonds the metal shroud and the compressor body to chassis ground. Routes through the same grommet as AC-4 / AC-5. |

The condenser fan does **not** appear in the AC table: the harvested fan is a [12 V](V_DC) DC brushless axial motor (the donor ice maker's own PCB regulated mains to [12 V](V_DC) to drive it; on harvest we keep the fan and discard the PCB). It rides on the [12 V](V_DC) bus instead — see run DC-8 below.

### Low-voltage logic ([3.3 V](V_IO) control side of the relays)

One 4-conductor loom carries RELAYS J5 (`GND` / `V5` / `IO2` / `IO19`) from the board to the two Teyleten modules on the shelf; the rows below are its conductors.

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| LV-1 | RELAYS J5 `IO19` | Teyleten relay #1 input terminal (IN) | signal | [22](AWG_LV) | [~150 mm](LEN_MID) | XH housing at J5; screw terminal at relay | [3.3 V](V_IO) GPIO drive into the opto input; no ground loop concern. |
| LV-2 | RELAYS J5 `IO2` | Teyleten relay #2 input terminal (IN) | signal | [22](AWG_LV) | [~150 mm](LEN_MID) | XH housing at J5; screw terminal at relay | Diaphragm pump refill gate. IO2 is boot-safe here: the opto's LED load holds it low, which download mode also wants. |
| LV-3 | RELAYS J5 `V5` + `GND` | Relay #1 + #2 module VCC / GND | + + GND | [22](AWG_LV) | [~150 mm](LEN_MID) | XH housing at J5; screw terminals at relays; tee V5 / GND to both modules at the relay end | Coil/opto [5 V](V_LOGIC) comes off the board's K7805 rail through J5; opto isolation keeps the coil supply electrically separate from the mains contacts. |

### [12 V](V_DC) distribution

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| DC-1 | PSU [12 V](V_DC) output | [12 V](V_DC) distribution block on electronics shelf | + + GND | [16](AWG_MAINS) | [~100 mm](LEN_SHORT_2) | Crimp fork at PSU; ferrule at distribution block | PSU max [6.7 A](PSU_MAX_A); [16 AWG](AWG_MAINS_U) comfortable. |
| DC-2 | [12 V](V_DC) distribution block | Teyleten relay #2 contact input | + | [16](AWG_MAINS) | [~100 mm](LEN_SHORT_2) | Crimp fork to relay terminal | Switched [12 V](V_DC) to diaphragm pump. |
| DC-3 | Teyleten relay #2 contact output | SeaFlo diaphragm pump | + + GND | [16](AWG_MAINS) | [~250 mm](LEN_PUMP) | Female disconnect | Pump peaks at ~[5 A](DIAPHRAGM_A). |
| DC-4 | [12 V](V_DC) distribution block | Board inlet J10 `V12` + `GND` | + + GND | [16](AWG_MAINS) | [~150 mm](LEN_MID) | Ferrules under the J10 screw clamps | Everything the board feeds — [12](SOLENOID_COUNT) valves, both peristaltic pumps, the condenser fan, display [12 V](V_DC), and both logic rails — draws through this run: ~3.3 A peak (both pumps priming + a few valves + the fan), against a 17 A-rated block. `V12` seats on the east pad, `GND` west; reversing them cooks the polarized bulk cap, the buck, and the drivers. |
| DC-5 | PUMPS J13 (`AM1` / `AM2` → pump A, `BM1` / `BM2` → pump B) | Kamoer pump A / pump B | 2 motor pairs | [22](AWG_SIG) | [~250 mm](LEN_PUMP) to the pumps + [~100 mm](LEN_SHORT_2) of pump-lead pigtail | XH housing at J13; quick-disconnect spades on the pump leads (BOM §11) | DRV8870 H-bridge outputs, ~[0.8 A](PUMP_PEAK_A) peak per pump. The pumps are field-replaceable; the spade terminals are the tool-free disconnect. |
| DC-6 | MANIFOLD A J1 (`COM` + `OUT1`–`OUT8`) | 8 Beduan solenoid coils on manifold A | 9-conductor trunk | [22](AWG_SIG) | [~300 mm](LEN_MANIFOLD) to the manifold, then [~150 mm](LEN_MID) fan-out per valve | XH housing at J1; `COM` into a Wago 221-420 at the manifold; female disconnects per valve | Low-side switching: `COM` carries the shared [12 V](V_DC) from the board's V12 island to every valve +, exploded at the manifold Wago; each valve − returns on its `OUT` conductor to the on-board TBD62083 (U4). Valve ↔ `OUT` mapping per [`valve-control.mmd`](/hardware/wiring/valve-control.mmd). |
| DC-7 | MANIFOLD B J2 (`COM` + `OUT1`–`OUT4`) | 4 Beduan solenoid coils on manifold B | rides the 6-conductor J2 trunk | [22](AWG_SIG) | [~300 mm](LEN_MANIFOLD) to the manifold, then [~150 mm](LEN_MID) fan-out per valve | XH housing at J2; `COM` into a Wago 221-420 at the manifold; female disconnects per valve | Same pattern as DC-6; the trunk's remaining conductor is the fan sink (DC-8). |
| DC-8 | MANIFOLD B J2 `FAN` + a `COM` branch off the manifold fan-out | Condenser fan motor ([12 V](V_DC) DC brushless axial, ~[0.35 A](FAN_A)) | + + ULN-sink return | [22](AWG_SIG) | [~400 mm](LEN_COMPRESSOR) shelf → side-wall fan (branches off the J2 trunk at the manifold) | Female disconnects at the fan | Low-side switching, same pattern as the valves — the fan + ties to the manifold's `COM` fan-out; the `FAN` conductor sinks the − side through TBD62083 #2 (U5, MCP23017 0x21 PA3). Flyback via the driver's integrated diode to `COM`. |

**Solenoid COM current budget.** Each Beduan coil is 5.5 W nameplate — ~0.46 A cold at 12 V, settling lower as the winding heats (`power.mmd` cites ~0.3 A sustained; measure hold current at bring-up to settle the figure). The canonical operating states ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)) open at most three valves at once, and at most three on a single manifold, so each manifold's shared 12 V COM contact (the `COM` pin on MANIFOLD A / J1 and MANIFOLD B / J2, a 2.54 mm XH contact rated ~3 A) carries ≤ ~1.4 A — comfortably inside the contact. MANIFOLD B adds the ~[0.35 A](FAN_A) condenser fan. Energizing a whole manifold at once is the only way to approach the limit (8 valves on MANIFOLD A ≈ 2.4–3.7 A across the 0.3–0.46 A range); no operating state does this, so firmware must not drive a full manifold simultaneously. Low-side switching means COM is the only conductor shared across valves — the manifold carries no separate ground return.

### Sensors and signal (low-voltage, low-current)

Three looms fan out from single connectors: SENSORS J4 carries SIG-1 / SIG-4 / SIG-9 with a shared `GND` split near the shelf; REEDS B J7 carries SIG-2 / SIG-3 / SIG-11 with a shared `GND` exploded at the cold-core end; REEDS A J6 is SIG-10 alone. Every reed input rides its MCP23017's internal pull-up — no resistors in any loom.

| # | From | To | Conductors | AWG | Approx. length | Notes |
|---|---|---|---|---|---|---|
| SIG-1 | SENSORS J4 `IO26` + `3V3` + `GND` | 1-wire temp bus — DS18B20 (0x28, tank wall) + DS18S20 (0x10, evap suction) | data + [3.3 V](V_IO) + GND, parallel-bussed | [22](AWG_SIG) | [~600 mm](LEN_COLD_CORE) to back of cold core | The [4.7 kΩ](DS18B20_PULLUP) data pull-up is on-board (R9) — nothing in the loom. |
| SIG-2 | REEDS B J7 `CLO` + `GND` | Reed switch — low (carbonator) | switch + shared GND | [22](AWG_LV) | [~600 mm](LEN_COLD_CORE) | MCP23017 0x21 PB4, INPUT_PULLUP. |
| SIG-3 | REEDS B J7 `CHI` + shared GND | Reed switch — high (carbonator) | switch | [22](AWG_LV) | [~600 mm](LEN_COLD_CORE) | MCP23017 0x21 PB5, INPUT_PULLUP. |
| SIG-4 | SENSORS J4 `IO25` + `V5` + `GND` | DIGITEN flow meter (Zone B, on the carbonated-water line where it exits the cold core near the shelf) | pulse + [5 V](V_LOGIC) + GND | [22](AWG_LV) | [~150 mm](LEN_MID) (internal, within the electronics-shelf zone) | Pulse interrupt; flow detection is internal — does not leave the enclosure. |
| SIG-6 | FAUCET J3 (`GND` / `V5` / `IO35` / `IO33`) | ESP32-S3-Touch-LCD-1.47 faucet flavor display on the gooseneck head | UART + power | 28 | [~1 m](LEN_UMBILICAL) (up the umbilical) | Direct TTL UART (IO33 TX, IO35 RX) to the display's ESP32-S3, which breaks out TTL UART (no transceiver — RS485 is reserved for the 4.3B, which has no free TTL UART). On the BNTECHGO 28 AWG 4-conductor ribbon; the display takes [5 V](V_LOGIC) up the umbilical. |
| SIG-7 | DISPLAY J9 (`B` / `A` / `GND` / `V12`) | ESP32-S3-Touch-LCD-4.3B config display on the front face (fixed) | RS485 pair + [12 V](V_DC) + GND | [22](AWG_LV) | [~1 m](LEN_UMBILICAL) (electronics shelf → front face, internal) | The RS485 transceiver is on-board (U7, COS13487 auto-direction; SM712 ESD array at the connector): A/B on a twisted pair to the 4.3B's onboard SP3485, and the display's 7–36 V screw input takes [12 V](V_DC) off `V12` on the same loom. Fixed front-face mount per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md). |
| SIG-8 | I2C J8 (`GND` / `3V3` / `SDA` / `SCL`) | Off-board MPR121 cap-sense controller (0x5A) at the flavor-tube sleeves | I2C + [3.3 V](V_IO) + GND | [22](AWG_LV) | [~300 mm](LEN_MANIFOLD) | The only off-board I2C device — the MCP23017s and DS3231 are on the PCBA, and the bus pull-ups are on-board (R19/R20). The MPR121 mounts beside the cap-sense sleeves at the manifold ([`/hardware/printed-parts/flavor/cap-sense-sleeve/`](/hardware/printed-parts/flavor/cap-sense-sleeve/)). |
| SIG-9 | SENSORS J4 `IO23` + `IO27` + `GND` | Backflow vent moisture sensor | switched VCC + DO + GND | [22](AWG_LV) | [~600 mm](LEN_COLD_CORE) to drip pan inside cabinet | Per [`/hardware/future.md`](/hardware/future.md) "Backflow vent monitoring". VCC is GPIO-sourced (`IO23`), driven only while sampling — the wet electrodes sit unpowered between samples. |
| SIG-10 | REEDS A J6 (`GND` + `RA1`–`RA4`) | Reservoir A level reeds (4) | 4 switches + shared GND | [22](AWG_LV) | [~600 mm](LEN_COLD_CORE) | MCP23017 0x20 PB0–3, INPUT_PULLUP; `GND` into a Wago 221-415 at the reservoir. See [`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md). |
| SIG-11 | REEDS B J7 `RB1`–`RB4` + shared GND | Reservoir B level reeds (4) | 4 switches | [22](AWG_LV) | [~600 mm](LEN_COLD_CORE) | MCP23017 0x21 PB0–3, INPUT_PULLUP; shares the J7 loom and its cold-core-end Wago 221-420 `GND` with SIG-2 / SIG-3. |
| SIG-12 | GAS J11 (`GND` / `V5` / `DOUT` / `AOUT`) | MQ-6 combustible-gas / refrigerant-leak sensor, rear cabinet floor | analog + trip + [5 V](V_LOGIC) + GND | [22](AWG_LV) | [~600 mm](LEN_COLD_CORE) | `AOUT` (analog level) and `DOUT` (LM393 comparator trip) swing 0–5 V and are divided to 3.3 V on-board before IO39 / IO36, so a plain sensor cable is safe. The sensor heater runs on `V5`. Mounted low — R-600a is heavier than air. |

## Loom terminations

Board end: every low-voltage loom lands in a JST XH [2.54 mm](JST_PITCH) crimp housing mating its labeled wafer — one housing per connector, pin labels on the silk, so a loom cannot seat shifted. J4 and J7 share the 7P housing, so those two land by loom label ([`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)). The one exception is the [12 V](V_DC) inlet J10: ferrules under its 5.0 mm screw clamps.

Device end: female disconnects at valves, pumps, fan, and compressor; ring terminals at ground studs; sensor and reed leads land per device. Shared-rail fan-outs happen at the device cluster, never at the board — one `COM` / `GND` conductor rides the trunk and explodes in a Wago lever nut at the manifold or reservoir (221-420 for the >5-conductor nodes, 221-415 for the rest).

Fabrication — bulk cut-to-length all-black wire, crimp tooling, sleeving, and per-assembly continuity testing — is [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md); stock is [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

## Grounding strategy

Single-point chassis ground at the electronics shelf, bonded back through the C14 inlet's earth pin to the building's protective earth.

- **C14 ground pin** → ground bus on electronics shelf (run AC-1 carries the green conductor from the inlet to the distribution block's G pole).
- **Ground bus** distributes to: PSU chassis (via AC-2 ground), compressor body / shroud (via AC-6), and any other exposed metal (faucet via the SS under-counter plate, the SS pressure vessel inside the cold core, etc.) via short bonding wires. Chassis grounding is via these discrete bonding wires; there is no metal chassis backbone.
- All ground conductors are [16 AWG](AWG_MAINS_U) green-insulated. Ring terminals at the bus, ring or fork terminals at the load.
- The chassis bond gives the appliance Class I status: if a fault energizes any exposed metal part, fault current returns to the building ground through the C14 cord and trips the upstream breaker before the user touches anything.

## What's not yet decided

- **Fuse on the AC primary** — a [5 A](PRIMARY_FUSE_A) fast-blow inline fuse between the C14 inlet and the AC distribution block was discussed in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) for bench testing. Whether it stays in the production unit (fuse holder on the rear panel? fuse on the shelf?) needs a decision.

## Revision

Lengths are design targets from the [`/hardware/future.md`](/hardware/future.md) layout; measure and update once the first build's enclosure is in hand.

## Sources
[value](NAME) texts are updated by:
- `/hardware/wiring/_ac_wiring_schedule_sync.py`
