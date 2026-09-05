# AC Wiring Schedule

Run-by-run physical wiring spec for the appliance's AC, 12 V, and signal distribution. Companion to the topology diagrams in this directory:

- [`power.mmd`](/hardware/wiring/power.mmd) — AC + 12 V topology (what connects to what)
- [`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) — ESP32 pin assignments
- [`valve-control.mmd`](/hardware/wiring/valve-control.mmd) — valve / reed expander map

This doc is the **physical wiring view** — gauges, run lengths, terminations, grounding. The topology files answer *what connects to what*; this file answers *how it's actually built*. The main-board end of every low-voltage run is fixed by the main board's edge connectors ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), the canonical pin map).

## Physical zones

The appliance has two functional electrical zones, both on the AC inlet side. The cold core occupies the rear of the enclosure (insulated, no electronics). The compressor + condenser sit middle-bottom. Everything else stands down the **+X wall of back-top**, feet on the cold core's foam-cap top, in line with the C14 inlet's crossing.

| Zone | Location | Contents |
|---|---|---|
| +X wall of back-top | On the foam-cap top in the band above the cold core, ahead of the +Y wall's port bodies | C14 inlet, AC distribution block, Mean Well IRM-90-12ST PSU, Teyleten relay #1 (compressor switch), Teyleten relay #2 (diaphragm pump switch), [12 V](V_DC) distribution block, main board, ground bus |
| Compressor zone | Front of the enclosure floor | Hermetic compressor bolted down on four floor posts, its terminal block and clip-on PTC start relay/overload module under the retained donor moulded cover, condenser fan beside it. The build adds no second sheet-metal shroud; see [`/business/regulatory.md`](/business/regulatory.md) for the qualification still owed on the retained cover. |

The main board is a single JLCPCB-assembled PCB carrying the ESP32-WROOM-32E, both MCP23017 expanders, the DS3231 RTC, both TBD62083 sink drivers, both DRV8870 pump H-bridges, and its own logic rails — [5 V](V_LOGIC) from the on-board K7805 buck (U10), [3.3 V](V_IO) from the on-board AMS1117 LDO (U9). It takes [12 V](V_DC) at the J10 screw inlet and presents every field interface as a labeled edge connector (next section); J14 is the USB-C programming port (bench cable only, no loom). Nothing on that wall wires module-to-module: a low-voltage loom lands either on a main-board connector or on a relay module's terminals.

The Teyleten relay #1 sits with the rest of the electronics, on that wall and **away from the refrigeration compartment**. Rationale: keep an arcing contact out of the volume a hydrocarbon leak pools in, and keep the mains reaching the compressor down to [3](COMP_WIRES) conductors — switched H + N + G — rather than the [5](COMP_WIRES_ALT) a relay at the compressor would need. See [`/hardware/README.md`](/hardware/README.md) "Safety".

## Board connector map

Every low-voltage run below names its board connector and pin labels; the labels are on the silk, one JST XH wafer per loom (J10 is the lone screw block). There is no J12. [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) is canonical.

| Conn. | Silk label | Pins | Serves |
|---|---|---|---|
| J1 | MANIFOLD A | `COM`, `OUT1`–`OUT8` | 8 solenoid valves (DC-6) |
| J2 | MANIFOLD B | `COM`, `FAN`, `OUT1`–`OUT4` | 2 manifold solenoid valves (DC-7) + condenser fan (DC-8); `OUT3` → V-K water-supply valve (DC-9); `OUT4` spare |
| J3 | FAUCET | `GND`, `V5`, `IO35`, `IO33` | faucet display UART up the umbilical (SIG-6) |
| J4 | SENSORS | `3V3`, `GND`, `V5`, `IO25`, `IO26`, `IO27`, `IO23` | DS18B20 bus (SIG-1), flow meter (SIG-4), moisture sensor (SIG-9) |
| J5 | RELAYS | `GND`, `V5`, `IO2`, `IO19` | both Teyleten relay modules (LV-1/2/3) |
| J6 | REEDS A | `GND`, `RA1`–`RA4` | reservoir A level reeds (SIG-10) |
| J7 | REEDS B | `RB1`–`RB4`, `CLO`, `CHI`, `GND` | reservoir B level reeds (SIG-11) + carbonator reeds (SIG-2, SIG-3) |
| J8 | I2C | `GND`, `3V3`, `SDA`, `SCL` | I²C expansion header; the bus's star point on the main board, no loom |
| J9 | DISPLAY | `B`, `A`, `GND`, `V12` | the enclosure display, RS485 + [12 V](V_DC) (SIG-7) |
| J10 | 12V | `GND`, `V12` — 5.0 mm screw block | board power inlet (DC-4) |
| J11 | GAS | `GND`, `V5`, `DOUT`, `AOUT` | MQ-6 gas / refrigerant-leak sensor (SIG-12) |
| J13 | PUMPS | `AM2`, `AM1`, `BM2`, `BM1` | peristaltic pumps A + B (DC-5) |
| J14 | — | USB-C receptacle | programming port; no loom |

## Run table

Per-run gauges, terminations, and approximate lengths. Lengths assume the enclosure layout in [`/hardware/README.md`](/hardware/README.md) "Enclosure (back to front)"; revise once the prototype enclosure is mocked up and lengths are measured.

### AC mains ([120 V](V_LINE))

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| AC-1 | C14 inlet (+Y wall of back-top) | AC distribution block on the +X wall of back-top | H + N + G | [16](AWG_MAINS) | [~150 mm](LEN_MID) (the C14 inlet's cordage drops the +Y wall of back-top and runs forward over the foam-cap top to the +X wall) | Solder to the C14 inlet's tabs; crimp ferrules into Wago 221 lever block | Inlet ships with solder-tab pins; [16 AWG](AWG_MAINS_U) appliance wire drops from the inlet to the distribution block on the wall below. The C14 inlet lands directly on the AC distribution block with no device in series; all downstream loads (PSU, compressor, etc.) tap the block. Ground-fault protection is deferred — see [`/future/pie-in-the-sky/gfci.md`](/future/pie-in-the-sky/gfci.md). |
| AC-2 | AC distribution block (H, N) | Mean Well IRM-90-12ST PSU primary terminals | H + N + G | [16](AWG_AC_BRANCH) | [~100 mm](LEN_SHORT_2) | Crimp ring or fork terminal at PSU; ferrule at distribution block | PSU primary draws [0.67 A](PSU_PRI_A) at [80 W](PSU_W) full load; [16 AWG](AWG_AC_BRANCH_U) ample. Ground bonds PSU chassis. |
| AC-3 | AC distribution block (H) | Teyleten relay #1 contact input | H | [16](AWG_AC_BRANCH) | [~50 mm](LEN_SHORT) | Crimp fork to relay screw terminal | Unswitched hot leg into the relay's "common" terminal. |
| AC-4 | Teyleten relay #1 contact output ("normally open") | Verified hot side of current donor compressor's factory-external electrical interface, through SF76E thermal fuse | H_switched | [18](AWG_COMP_LEAD) | [~400 mm](LEN_COMPRESSOR) | Crimp fork to relay; current-donor external-interface connector TBD | Switched hot. One of the three conductors of the [18 AWG](AWG_COMP_LEAD_U) SJOOW jacketed lead that runs unbroken from the +X wall of back-top to the compressor. The terminal block and PTC stay under the retained donor cover; this run terminates only at the factory-external interface. Length includes service slack. |
| AC-5 | AC distribution block (N) | Verified neutral side of current donor compressor's factory-external electrical interface | N | [18](AWG_COMP_LEAD) | [~400 mm](LEN_COMPRESSOR) | Crimp ferrule at distribution block; current-donor external-interface connector TBD | The SJOOW's second conductor, in the same jacket as AC-4. It terminates only at the factory-external interface without disturbing the retained donor cover. |
| AC-6 | Earth bus on chassis ground point | Compressor body, at its terminal-box earth screw | G | [18](AWG_COMP_LEAD) | [~400 mm](LEN_COMPRESSOR) | Ring terminal both ends | The SJOOW's third conductor, in the same jacket as AC-4 / AC-5. Bonds the compressor body to chassis ground — the machine's only bond to the refrigeration metalwork. The ring goes under the compressor's own terminal-box earth screw, never under a rubber-isolated floor mount. |

The condenser fan does **not** appear in the AC table: the harvested fan is a [12 V](V_DC) DC brushless axial motor (the donor ice maker's own PCB regulated mains to [12 V](V_DC) to drive it; on harvest we keep the fan and discard the PCB). It rides on the [12 V](V_DC) bus instead — see run DC-8 below.

### Low-voltage logic ([3.3 V](V_IO) control side of the relays)

One 22 AWG 4P ribbon carries RELAYS J5 (`GND` / `V5` / `IO2` / `IO19`) from the main board to the two Teyleten modules on the same wall; the rows below are its conductors.

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| LV-1 | RELAYS J5 `IO19` | Teyleten relay #1 input terminal (IN) | signal | [22](AWG_LV) | [~100 mm](LEN_RELAYS) | XH housing at J5; screw terminal at relay | [3.3 V](V_IO) GPIO drive into the opto input; no ground loop concern. |
| LV-2 | RELAYS J5 `IO2` | Teyleten relay #2 input terminal (IN) | signal | [22](AWG_LV) | [~100 mm](LEN_RELAYS) | XH housing at J5; screw terminal at relay | Diaphragm pump refill gate. IO2 is boot-safe here: the opto's LED load holds it low, which download mode also wants. |
| LV-3 | RELAYS J5 `V5` + `GND` | Relay #1 + #2 module VCC / GND | + + GND | [22](AWG_LV) | [~100 mm](LEN_RELAYS) | XH housing at J5; screw terminals at relays; tee V5 / GND to both modules at the relay end | Coil/opto [5 V](V_LOGIC) comes off the main board's K7805 rail through J5; opto isolation keeps the coil supply electrically separate from the mains contacts. |

### [12 V](V_DC) distribution

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| DC-1 | PSU [12 V](V_DC) output | [12 V](V_DC) distribution block on the +X wall of back-top | + + GND | [16](AWG_MAINS) | [~100 mm](LEN_SHORT_2) | Crimp fork at PSU; ferrule at distribution block | PSU max [6.7 A](PSU_MAX_A); [16 AWG](AWG_MAINS_U) comfortable. |
| DC-2 | [12 V](V_DC) distribution block | Teyleten relay #2 contact input | + | [16](AWG_MAINS) | [~100 mm](LEN_SHORT_2) | Crimp fork to relay terminal | Switched [12 V](V_DC) to diaphragm pump. |
| DC-3 | Teyleten relay #2 contact output | SeaFlo diaphragm pump | + + GND | [16](AWG_MAINS) | [~250 mm](LEN_PUMP) | Female disconnect | Pump peaks at ~[5 A](DIAPHRAGM_A). |
| DC-4 | [12 V](V_DC) distribution block | Board inlet J10 `V12` + `GND` | + + GND | [16](AWG_MAINS) | [~150 mm](LEN_MID) | Ferrules under the J10 screw clamps | Everything the main board feeds — [10](SOLENOID_COUNT) manifold valves + the V-K supply valve, both peristaltic pumps, the condenser fan, display [12 V](V_DC), and both logic rails — draws through this run: ~[3.33 A](BOARD_PEAK_A) peak (both pumps priming + [3](MAX_VALVES) valves + the fan), against a 17 A-rated block. The SeaFlo's [5 A](DIAPHRAGM_A) on DC-3 parallels it off the same supply — [8.32 A](COINCIDENT_A) against [6.7 A](PSU_MAX_A) if a refill overlaps a dispense, which is why relay #2 is gated on the dispense window ([`power.mmd`](/hardware/wiring/power.mmd)). `V12` seats on the east pad, `GND` west; reversing them cooks the polarized bulk cap, the buck, and the drivers. |
| DC-5 | PUMPS J13 (`AM2` / `AM1` → pump A, `BM2` / `BM1` → pump B) | The **pump jack**, a RiteAV RJ11 6P4C keystone in front-top's ridge wall behind the enclosure display; the pump cartridge's cord ends in the **pump plug**, an RJ11 6P4C modular plug | 2 motor pairs, 4 conductors | 22 fixed / 28 cord | [~350 mm](LEN_PUMP_FIXED) fixed J13 half + [~400 mm](LEN_CARTRIDGE) cartridge cord | J13 XH → 22 AWG 4P ribbon → 110 IDC on the jack; 28 AWG 4P ribbon crimped in the 3-prong 6P4C plug → four female Fastons kept on the pump tabs | Each DRV8870 H-bridge drives one motor differentially, so each of the jack's four contacts carries one motor conductor at the pump's published ~[0.8 A](PUMP_PEAK_A), never both pumps; a modular contact is rated 1.5 A continuous, and the 28 AWG cord drops 0.1 V of 12 V over its 400 mm at that current. Conductor order, plug clip down: `1 AM2`, `2 AM1`, `3 BM2`, `4 BM1`, punched down in the same order on the jack. The fixed half returns toward the main board through the +X ridge-wall cable clip; the cord is unclipped and follows the cartridge out. With power removed, draw the cartridge, press the plug's clip from below, pull the plug straight forward until it is clear of the plate cap, then lower it through the bay; the four Fastons stay on the pump tabs through routine cartridge service. |
| DC-6 | MANIFOLD A J1 (`COM` + `OUT1`–`OUT8`) | 8 Beduan solenoid coils on manifold A | 9-conductor trunk | [22](AWG_SIG) | [~350 mm](LEN_MAN_A) to each coil, `COM` [~250 mm](LEN_MAN_A_COM) to the fan-out, then [~150 mm](LEN_MID) per valve | XH housing at J1; `COM` into a Wago 221-420 at the manifold; female disconnects per valve | Low-side switching: `COM` carries the shared [12 V](V_DC) from the main board's V12 island to every valve +, exploded at the manifold Wago; each valve − returns on its `OUT` conductor to the on-board TBD62083 (U4). Valve ↔ `OUT` mapping per [`valve-control.mmd`](/hardware/wiring/valve-control.mmd). |
| DC-7 | MANIFOLD B J2 (`COM` + `OUT1`–`OUT2`) | 2 Beduan solenoid coils on manifold B | 4 of the 6-way J2 trunk populated | [22](AWG_SIG) | [~400 mm](LEN_MAN_B) to each coil and to the fan-out, then [~150 mm](LEN_MID) per valve | XH housing at J2; `COM` into a Wago 221-415 at the manifold; female disconnects per valve | Same pattern as DC-6. The trunk populates `COM` + `OUT1` + `OUT2` + `FAN` (the fan sink is DC-8) + `OUT3` (V-K's − on run DC-9); `OUT4` is wired on the main board but carries no valve — a spare channel, left unpopulated in the harness. |
| DC-8 | MANIFOLD B J2 `FAN` + a `COM` branch off the manifold fan-out | Condenser fan motor ([12 V](V_DC) DC brushless axial, ~[0.35 A](FAN_A)) | + + ULN-sink return | [22](AWG_SIG) | [~450 mm](LEN_FAN) +X wall → side-wall fan (branches off the J2 trunk at the manifold) | Female disconnects at the fan | Low-side switching, same pattern as the valves — the fan + ties to the manifold's `COM` fan-out; the `FAN` conductor sinks the − side through TBD62083 #2 (U5, MCP23017 0x21 PA3). Flyback via the driver's integrated diode to `COM`. |
| DC-9 | MANIFOLD B J2 (`OUT3` + a `COM` tap) | V-K water-supply fill/shutoff coil, at the aft strip by the water bulkhead | 2 conductors off the J2 trunk | [22](AWG_SIG) | [~100 mm](LEN_VK) +X wall → V-K, which stands against the board's own flank | Female disconnects at the valve | Low-side switching, same pattern as the manifold valves: `OUT3` sinks V-K's − through TBD62083 #2 (U5, MCP23017 0x21 PA5); + taps the shared J2 `COM`. V-K is a separate part from manifold B — mapping per [`valve-control.mmd`](/hardware/wiring/valve-control.mmd), plumbing per [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2. |

**Solenoid COM current budget.** Each Beduan coil is 5.5 W nameplate — ~[0.46 A](COIL_A) cold at 12 V, settling lower as the winding heats (`power.mmd` cites ~0.3 A sustained; measure hold current at bring-up to settle the figure). The canonical operating states ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)) open at most three valves at once, and at most three on a single manifold, so each manifold's shared 12 V COM contact (the `COM` pin on MANIFOLD A / J1 and MANIFOLD B / J2, a 2.54 mm XH contact rated ~3 A) carries ≤ ~1.4 A — comfortably inside the contact. MANIFOLD B adds the ~[0.35 A](FAN_A) condenser fan and V-K (~[0.46 A](COIL_A) on `OUT3`, sharing J2's `COM`); V-K is a supply valve, open only during a fill, so it does not stack with a manifold-B dispense in normal operation. Energizing a whole manifold at once is the only way to approach the limit (8 valves on MANIFOLD A ≈ 2.4–3.7 A across the 0.3–0.46 A range); no operating state does this, so firmware must not drive a full manifold simultaneously. Low-side switching means COM is the only conductor shared across valves — the manifold carries no separate ground return.

### Sensors and signal (low-voltage, low-current)

Three looms fan out from single connectors: SENSORS J4 carries SIG-1 / SIG-4 / SIG-9 with a shared `GND` split near the +X wall; REEDS B J7 carries SIG-2 / SIG-3 / SIG-11 with a shared `GND` exploded at the cold-core end; REEDS A J6 is SIG-10 alone. Every reed input rides its MCP23017's internal pull-up — no resistors in any loom.

| # | From | To | Conductors | AWG | Approx. length | Notes |
|---|---|---|---|---|---|---|
| SIG-1 | SENSORS J4 `IO26` + `3V3` + `GND` | 1-wire temp bus — DS18B20 (0x28, carbonator wall) + DS18S20 (0x10, evap suction) | data + [3.3 V](V_IO) + GND, parallel-bussed | [22](AWG_SIG) | [~300 mm](LEN_ONEWIRE) to the probes in the core | The [4.7 kΩ](DS18B20_PULLUP) data pull-up is on-board (R9) — nothing in the loom. |
| SIG-2 | REEDS B J7 `CLO` + `GND` | Reed switch — low (carbonator) | switch + shared GND | [22](AWG_LV) | [~350 mm](LEN_CARB_REEDS) | MCP23017 0x21 PB4, INPUT_PULLUP. |
| SIG-3 | REEDS B J7 `CHI` + shared GND | Reed switch — high (carbonator) | switch | [22](AWG_LV) | [~350 mm](LEN_CARB_REEDS) | MCP23017 0x21 PB5, INPUT_PULLUP. |
| SIG-4 | SENSORS J4 `IO25` + `V5` + `GND` | DIGITEN flow meter (inline on the carbonated-water riser, lying in the strip ahead of the cold core's front face, boss up) | pulse + [5 V](V_LOGIC) + GND | [22](AWG_LV) | [~300 mm](LEN_FLOW) (internal, ahead of the cold core's front face) | Pulse interrupt; flow detection is internal — does not leave the enclosure. |
| SIG-6 | FAUCET J3 (`GND` / `V5` / `IO35` / `IO33`) | ESP32-S3-Touch-LCD-1.47 faucet display at the end of the gooseneck | UART + power | 22 in / 28 out | [~1 m](LEN_UMBILICAL) (up the umbilical) | Direct TTL UART (IO33 TX, IO35 RX) to the display's ESP32-S3, which breaks out TTL UART (no transceiver — RS485 is reserved for the 4.3B, which has no free TTL UART). **The one signal run that crosses the enclosure wall**: J3 → 22 AWG loom → 110 IDC on the keystone jack at station 7 of the +Y wall of back-top → the customer's RJ11 plug → BNTECHGO 28 AWG ribbon up the umbilical. The display takes [5 V](V_LOGIC) across that joint. |
| SIG-7 | DISPLAY J9 (`B` / `A` / `GND` / `V12`) | ESP32-S3-Touch-LCD-4.3B enclosure display on the front face (fixed) | RS485 pair + [12 V](V_DC) + GND | [22](AWG_LV) | [~400 mm](LEN_FRONT_FACE) (+X wall of back-top → front face, internal) | One 22 AWG 4P ribbon (`bom.md` §11). The RS485 transceiver is on-board (U7, COS13487 auto-direction; SM712 ESD array at the connector): A/B on a twisted pair to the 4.3B's onboard SP3485, and the display's 7–36 V screw input takes [12 V](V_DC) off `V12` on the same loom. Fixed mount in the 45° display facet per [`/hardware/printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md). |
| SIG-9 | SENSORS J4 `IO23` + `IO27` + `GND` | Backflow vent moisture sensor | switched VCC + DO + GND | [22](AWG_LV) | [~350 mm](LEN_MOISTURE) to the dry LM393 board beside the pan's −X-wall cable clip | Per [`/hardware/README.md`](/hardware/README.md) "Safety". VCC / DO / GND land on the comparator board; its uninterrupted two-conductor plate lead passes through the wall-integrated clip and leaves a service loop into the open pan. Draw the pan until the plate is reachable, lift the plate out, then remove the empty pan. VCC is GPIO-sourced (`IO23`), driven only while sampling — the wet electrodes sit unpowered between samples. |
| SIG-10 | REEDS A J6 (`GND` + `RA1`–`RA4`) | Reservoir A level reeds (4) | 4 switches + shared GND | [22](AWG_LV) | [~450 mm](LEN_REEDS_A) | MCP23017 0x20 PB0–3, INPUT_PULLUP; `GND` into a Wago 221-415 at the reservoir. See [`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md). |
| SIG-11 | REEDS B J7 `RB1`–`RB4` + shared GND | Reservoir B level reeds (4) | 4 switches | [22](AWG_LV) | [~400 mm](LEN_REEDS_B) | MCP23017 0x21 PB0–3, INPUT_PULLUP; shares the J7 loom and its cold-core-end Wago 221-420 `GND` with SIG-2 / SIG-3. |
| SIG-12 | GAS J11 (`GND` / `V5` / `DOUT` / `AOUT`) | MQ-6 combustible-gas / refrigerant-leak sensor, rear cabinet floor | analog + trip + [5 V](V_LOGIC) + GND | [22](AWG_LV) | [~600 mm](LEN_GAS) | One 22 AWG 4P ribbon (`bom.md` §11). `AOUT` (analog level) and `DOUT` (LM393 comparator trip) swing 0–5 V and are divided to 3.3 V on-board before IO39 / IO36, so a plain sensor cable is safe. The sensor heater runs on `V5`. Mounted low — R-600a is heavier than air. |

## Loom terminations

Board end: every low-voltage loom lands in a JST XH [2.5 mm](JST_PITCH) crimp housing mating its labeled wafer — one housing per connector, pin labels on the silk, so a loom cannot seat shifted. J4 and J7 share the 7P housing, so those two land by loom label ([`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)). The one exception is the [12 V](V_DC) inlet J10: ferrules under its 5.0 mm screw clamps.

Device end: female disconnects at valves, pumps, and fan; the current donor compressor uses its preserved factory-external electrical interface, whose connector and polarity mapping remain to be recorded; ring terminals land at ground studs; sensor and reed leads land per device. Shared-rail fan-outs happen at the device cluster, never at the main board — one `COM` / `GND` conductor rides the trunk and explodes in a Wago lever nut at the manifold or reservoir (221-420 for the >5-conductor nodes, 221-415 for the rest). Each of the five stands in a press-fit well printed into the side wall its own cluster stands against, so the splice is held where the branches part:

| node | nut | ways | wall | what the branches reach |
|---|---|---|---|---|
| J1 MANIFOLD A `COM` | 221-420 | 9 of 10 | +X, over the manifold | V-A…V-H |
| J2 MANIFOLD B `COM` | 221-415 | 5 of 5 | −X, over the manifold | V-I, V-J, condenser fan, V-K's `+` tap |
| J7 REEDS B `GND` | 221-420 | 7 of 10 | −X, aft, over the core's lid | reservoir B's 4 reeds + the carbonator's 2 |
| J6 REEDS A `GND` | 221-415 | 5 of 5 | −X, aft, over the core's lid | reservoir A's 4 reeds |
| J4 SENSORS `GND` | 221-415 | 4 of 5 | −X, aft | 1-wire bus, DIGITEN meter, moisture plate |

The peristaltic pumps have no such nut: DC-5 is two DRV8870 H-bridge pairs, each motor driven differentially on its own two conductors, so there is no rail to share and nothing to fan out. Four direct conductors run from J13 to the pump jack's punchdown and four more from the pump plug to the motor tabs. The mating faces are the cartridge's service disconnect; the four Fastons stay on the pumps.

Fabrication — bulk cut-to-length all-black wire, crimp tooling, sleeving, and per-assembly continuity testing — is [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md); stock is [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

## Grounding strategy

Single-point chassis ground at the +X wall of back-top, bonded back through the C14 inlet's earth pin to the building's protective earth.

- **C14 ground pin** → ground bus on the +X wall of back-top (run AC-1 carries the green conductor from the inlet to the distribution block's G pole).
- **Ground bus** distributes to: PSU chassis (via AC-2 ground), compressor body (via AC-6), and any other exposed metal (faucet via the SS under-counter plate, the SS carbonator inside the cold core, etc.) via short bonding wires. Chassis grounding is via these discrete bonding wires; there is no metal chassis backbone.
- All ground conductors are [16 AWG](AWG_MAINS_U) green-insulated. Ring terminals at the bus, ring or fork terminals at the load.
- The chassis bond gives the appliance Class I status: if a fault energizes any exposed metal part, fault current returns to the building ground through the C14 cord and trips the upstream breaker before the user touches anything.

## What's not yet decided

- **Fuse on the AC primary** — a [5 A](PRIMARY_FUSE_A) fast-blow inline fuse between the C14 inlet and the AC distribution block was discussed in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) for bench testing. Whether it stays in the production unit (fuse holder in the +Y wall of back-top? fuse on the +X wall?) needs a decision.

## Revision

Lengths are design targets from the [`/hardware/README.md`](/hardware/README.md) layout; measure and update once the first build's enclosure is in hand.

## Sources
[value](NAME) texts are updated by:
- `/hardware/wiring/_ac_wiring_schedule_sync.py`
