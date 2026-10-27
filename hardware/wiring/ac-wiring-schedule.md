# AC Wiring Schedule

Run-by-run physical wiring spec for the appliance's AC, 12 V, and signal distribution. Companion to the topology diagrams in this directory:

- [`power.mmd`](/hardware/wiring/power.mmd) — AC + 12 V topology (what connects to what)
- [`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) — ESP32 pin assignments
- [`valve-control.mmd`](/hardware/wiring/valve-control.mmd) — valve / reed expander map

This doc is the **physical wiring view** — gauges, run lengths, terminations, grounding. The topology files answer *what connects to what*; this file answers *how it's actually built*. The main-board end of every low-voltage run is fixed by the main board's edge connectors ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), the canonical pin map).

## Physical zones

The insulated cold core occupies the rear floor. Its dry upper lid supports the flat PCB, four junction WAGOs and the earth stack. Back-top carries the PSU and two raised relays on the dry west sidewall and the meter on its east-wall carriers. Its rear ceiling is continuous, so every end beneath it is landed while back-top is open on the bench, with its free end dressed to the funnel opening. The final connections are made through that opening with the funnel frame out. Three runs whose two ends both lie under the ceiling, AC-4, AC-5 and DC-3, meet in lever-nut joins there.

| Zone | Location | Contents |
|---|---|---|
| Core lid | Above the insulated core | Main PCB, +12 V/DC GND/sensor/reed WAGOs and ring-terminal earth stack |
| Fixed enclosure walls | Rear wall, west wall and front manifold | C14 and three mains WAGOs at the rear; Mean Well IRM-90-12ST and two Teyleten relays on the west wall; two manifold commons on front-top's east wall |
| Compressor zone | Front of the enclosure floor | Upright hermetic compressor on four floor posts, retained donor terminal/PTC cover, thermal fuse, condenser fan and low MQ-6 sensor |

The main board is a single JLCPCB-assembled PCB carrying the ESP32-WROOM-32E, both MCP23017 expanders, the DS3231 RTC, both TBD62083 sink drivers, both DRV8870 pump H-bridges, and its own logic rails — [5 V](V_LOGIC) from the on-board K7805 buck (U10), [3.3 V](V_IO) from the on-board AMS1117 LDO (U9). It takes [12 V](V_DC) at the J10 screw inlet and presents every field interface as a labeled edge connector (next section); J14 is the USB-C programming port (bench cable only, no loom). The board carries those logic functions internally; a low-voltage loom lands either on a main-board connector or on a relay module's terminals.

Both Teyleten relays are on back-top’s west wall above the PSU. The compressor lead carries [3](COMP_WIRES) cores in one jacket: switched H, N and PE. Switched H and N meet back-top's relay #1 and neutral pigtails in two lever-nut joins under the funnel opening; PE lands on the lid earth stack. Relay #2 switches the lid-mounted diaphragm pump through a third join. See [`/hardware/README.md`](/hardware/README.md) “Safety” for the qualification scope.

## Board connector map

Every low-voltage run below names its board connector and pin labels; the labels are on the silk, one JST XH wafer per loom (J10 is the lone screw block). There is no J12. [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) is canonical.

| Conn. | Silk label | Pins | Serves |
|---|---|---|---|
| J1 | MANIFOLD A | `COM`, `OUT1`–`OUT8` | 8 solenoid valves (DC-6) |
| J2 | MANIFOLD B | `COM`, `FAN`, `OUT1`–`OUT4` | 2 manifold solenoid valves (DC-7) + condenser fan (DC-8); `OUT3` → V-K water-supply valve (DC-9); `OUT4` spare |
| J3 | FAUCET | 1 `IO33` TX, 2 `IO35` RX, 3 `V5`, 4 `GND` | faucet display UART up the umbilical (SIG-6); physical pin numbers include the wafer rotation |
| J4 | SENSORS | `3V3`, `GND`, `V5`, `IO25`, `IO26`, `IO27`, `IO23` | DS18B20 bus (SIG-1), flow meter (SIG-4); IO23/IO27 reserved |
| J5 | RELAYS | `GND`, `V5`, `IO2`, `IO19` | both Teyleten relay modules (LV-1/2/3) |
| J6 | REEDS A | `GND`, `RA1`–`RA4` | reservoir A level reeds (SIG-10) |
| J7 | REEDS B | `RB1`–`RB4`, `CLO`, `CHI`, `GND` | reservoir B level reeds (SIG-11) + carbonator reeds (SIG-2, SIG-3) |
| J8 | I2C | `GND`, `3V3`, `SDA`, `SCL` | I²C expansion header; the bus's star point on the main board, no loom |
| J9 | DISPLAY | `B`, `A`, `GND`, `V12` | the enclosure display, RS485 + [12 V](V_DC) (SIG-7) |
| J10 | 12V | `GND`, `V12` — 5.0 mm screw block | board power inlet (DC-4) |
| J11 | GAS | `GND`, `V5`, `DOUT`, `AOUT` | MQ-6 gas / refrigerant-leak sensor (SIG-12) |
| J13 | PUMPS | `AM2`, `AM1`, `BM2`, `BM1` | peristaltic pumps A + B (DC-5) |
| J14 | — | USB-C receptacle | programming port; no loom |

## Conductor construction

Use **16 AWG solid tinned-copper appliance hookup wire** for fixed runs
**AC-1, AC-2 (H/N), AC-3, DC-1, DC-2 and DC-4**. Strip and land the solid conductor
directly in each screw cage and WAGO lever clamp, one conductor per entry;
no fork, ferrule or solder-added tip on these solid ends. AC-1's other end is
soldered to the C14 inlet's tabs. Use black for hot and DC, white for neutral
and green for AC-1's earth. The selected stock is marked UL1007, 300 V / 80°C;
its [black](https://www.amazon.com/dp/B0FK5HH8H1) and
[white](https://www.amazon.com/dp/B0FK5G1Q1J) 25 ft spools were bought
2026-10-17, and its [green](https://www.amazon.com/dp/B0FK5JHQW7) spool is a
Prime offer verified 2026-10-17, not purchased. Keep this fixed wire away from
hot refrigeration surfaces. WAGO's [221 documentation](https://www.wago.com/us/installation-221-ad)
covers solid copper; J10's KF301-5.0 block accepts 14–22 AWG.

The 18 AWG SJOOW compressor cord, DC-3's pump lead, protective-earth bonds
and the JST / Faston / removable-display harnesses use stranded wire. Retain
the specified crimps; use a correctly
sized ferrule where a stranded lead enters a screw cage. A screw at one end
does not make a moving or crimp-terminated run a solid-wire run. SIG-7's
JST-to-display loom therefore stays stranded at its display screw terminals.

The [Mean Well IRM-90-12ST](https://www.meanwell.com/Upload/PDF/IRM-90/IRM-90-spec.pdf)
is an encapsulated Class II module with two AC terminals, L and N, and no
protective-earth terminal. Bond the exposed
metalwork through the ground bus. Preform and terminate both PSU pigtail
pairs with power disconnected before fastening the module to its wall
bosses; leave the wire bends free of the nameplate backing and relay.

## Run table

Per-run gauges, terminations, and approximate lengths. Lengths assume the enclosure layout in [`/hardware/README.md`](/hardware/README.md) "Enclosure (back to front)"; revise once the prototype enclosure is mocked up and lengths are measured.

### AC mains ([120 V](V_LINE))

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| AC-1 | C14 inlet (+Y wall of back-top) | rear-wall mains WAGOs beside C14 | H + N + G | [16](AWG_MAINS) | [~150 mm](LEN_MID) (C14 tabs to the adjacent rear-wall mains blocks) | Solder to the C14 inlet's tabs; solid copper directly in the WAGO clamps | Inlet ships with solder-tab pins; [16 AWG](AWG_MAINS_U) solid black / white / green drops from the inlet to the adjacent rear-wall distribution blocks. The C14 inlet lands directly on the AC distribution block with no device in series; all downstream loads (PSU, compressor, etc.) tap the block. Ground-fault protection is deferred — see [`/future/pie-in-the-sky/gfci.md`](/future/pie-in-the-sky/gfci.md). |
| AC-2 | AC distribution block (H, N) | Mean Well IRM-90-12ST PSU primary terminals | H + N | [16](AWG_AC_BRANCH) | [~200 mm](LEN_SHORT_2) | Solid copper directly in PSU screw cages and WAGO clamps | PSU primary draws [0.67 A](PSU_PRI_A) at [80 W](PSU_W) full load; [16 AWG](AWG_AC_BRANCH_U) ample. The module has no earth terminal. |
| AC-3 | AC distribution block (H) | Teyleten relay #1 contact input | H | [16](AWG_AC_BRANCH) | [~150 mm](LEN_SHORT) | Solid copper directly in relay screw cage and WAGO clamp | Unswitched hot leg into the relay's "common" terminal. |
| AC-4 | Teyleten relay #1 contact output ("normally open") | Verified hot side of current donor compressor's factory-external electrical interface, through SF76E thermal fuse | H_switched | [16](AWG_AC_BRANCH) pigtail + [18](AWG_COMP_LEAD) core | [~300 mm](LEN_JOIN) pigtail; [~700 mm](LEN_COMPRESSOR) core stock | Solid copper in the relay screw cage; WAGO 221-413 join under the funnel opening, the core ferruled into it; current-donor external-interface connector TBD | Switched hot, in two pieces. A black solid pigtail from relay #1's NO terminal is landed on the open back-top and dressed forward to the funnel opening. One of the three conductors of the [18 AWG](AWG_COMP_LEAD_U) SJOOW lead, in a shared jacket through the fore floor lane, meets it in the join after the box closes. The terminal block and PTC stay under the retained donor cover; this run terminates only at the factory-external interface. Lengths include trim at the join. |
| AC-5 | AC distribution block (N) | Verified neutral side of current donor compressor's factory-external electrical interface | N | [16](AWG_AC_BRANCH) pigtail + [18](AWG_COMP_LEAD) core | [~300 mm](LEN_JOIN) pigtail; [~700 mm](LEN_COMPRESSOR) core stock | Solid copper in the rear N WAGO; WAGO 221-413 join under the funnel opening, the core ferruled into it; current-donor external-interface connector TBD | Neutral, in two pieces like AC-4: a white solid pigtail from the rear N WAGO, landed on the open back-top, and the SJOOW's second conductor, joined after the box closes. It terminates only at the factory-external interface without disturbing the retained donor cover. |
| AC-6 | Earth bus on chassis ground point | Compressor body, at its terminal-box earth screw | G | [18](AWG_COMP_LEAD) | [~700 mm](LEN_COMPRESSOR) | Ring terminal both ends | The SJOOW's third conductor, in the same jacket as AC-4 / AC-5. Bonds the compressor body to chassis ground — the machine's only bond to the refrigeration metalwork. The ring goes under the compressor's own terminal-box earth screw, never under a rubber-isolated floor mount. |

The condenser fan does **not** appear in the AC table: the harvested fan is a [12 V](V_DC) DC brushless axial motor (the donor ice maker's own PCB regulated mains to [12 V](V_DC) to drive it; on harvest we keep the fan and discard the PCB). It rides on the [12 V](V_DC) bus instead — see run DC-8 below.

### Low-voltage logic ([3.3 V](V_IO) control side of the relays)

One 22 AWG 4P ribbon carries RELAYS J5 (`GND` / `V5` / `IO2` / `IO19`) from the main board to the two Teyleten modules on the west wall; the rows below are its conductors.

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| LV-1 | RELAYS J5 `IO19` | Teyleten relay #1 input terminal (IN) | signal | [22](AWG_LV) | [~350 mm](LEN_RELAYS) | XH housing at J5; screw terminal at relay | [3.3 V](V_IO) GPIO drive into the opto input; no ground loop concern. |
| LV-2 | RELAYS J5 `IO2` | Teyleten relay #2 input terminal (IN) | signal | [22](AWG_LV) | [~350 mm](LEN_RELAYS) | XH housing at J5; screw terminal at relay | Diaphragm pump refill gate. IO2 is boot-safe here: the opto's LED load holds it low, which download mode also wants. |
| LV-3 | RELAYS J5 `V5` + `GND` | Relay #1 + #2 module VCC / GND | + + GND | [22](AWG_LV) | [~350 mm](LEN_RELAYS) | XH housing at J5; screw terminals at relays; tee V5 / GND to both modules at the relay end | Coil/opto [5 V](V_LOGIC) comes off the main board's K7805 rail through J5; opto isolation keeps the coil supply electrically separate from the mains contacts. |

### [12 V](V_DC) distribution

| # | From | To | Conductors | AWG | Approx. length | Termination | Notes |
|---|---|---|---|---|---|---|---|
| DC-1 | PSU [12 V](V_DC) output | [12 V](V_DC) distribution block on the core lid | + + GND | [16](AWG_MAINS) | [~350 mm](LEN_DC1) | Solid copper directly in PSU screw cages and WAGO clamps | PSU max [6.7 A](PSU_MAX_A); [16 AWG](AWG_MAINS_U) comfortable. |
| DC-2 | [12 V](V_DC) distribution block | Teyleten relay #2 contact input | + | [16](AWG_MAINS) | [~350 mm](LEN_DC2) | Solid copper directly in relay screw cage and WAGO clamp | Switched [12 V](V_DC) to diaphragm pump. |
| DC-3 | Teyleten relay #2 contact output | G Ganen diaphragm pump | + + GND | [16](AWG_MAINS) | [~300 mm](LEN_JOIN) relay pigtail and pump positive; [~350 mm](LEN_PUMP) pump negative | Ferrule in the relay screw cage; WAGO 221-413 join under the funnel opening; female disconnects at the pump; negative into the DC GND WAGO | Budgeted at [5 A](DIAPHRAGM_A); the pump's current is unmeasured. The relay pigtail is landed on the open back-top and the pump's positive on the open core, each dressed to the funnel opening and joined after the box closes. |
| DC-4 | [12 V](V_DC) distribution block | Board inlet J10 `V12` + `GND` | + + GND | [16](AWG_MAINS) | [~150 mm](LEN_MID) | Solid copper directly in J10 screw cages and WAGO clamps | Everything the main board feeds — [10](SOLENOID_COUNT) manifold valves + the V-K supply valve, both peristaltic pumps, the condenser fan, display [12 V](V_DC), and both logic rails — draws through this run: ~[3.33 A](BOARD_PEAK_A) peak (both pumps priming + [3](MAX_VALVES) valves + the fan), against [32 A](WAGO_RATED_A)-rated WAGO 221-413 lever nuts. The diaphragm pump's [5 A](DIAPHRAGM_A) budget on DC-3 parallels it off the same supply — [8.32 A](COINCIDENT_A) against [6.7 A](PSU_MAX_A) if a refill overlaps a dispense, which is why relay #2 is gated on the dispense window ([`power.mmd`](/hardware/wiring/power.mmd)). As installed, J10's throats face aft: `V12` seats in the west clamp (X−27.5) and `GND` in the east clamp (X−22.5), each beside its silk label. The Q4 pass FET blocks a reversed pair, which leaves the board unpowered. |
| DC-5 | PUMPS J13 (`AM2` / `AM1` → pump A, `BM2` / `BM1` → pump B) | Both peristaltic pumps' motor tabs inside the integral upper mount | 2 motor pairs, 4 conductors | 22 | [~500 mm](LEN_PUMP_FIXED) | J13 XH → 22 AWG 4P ribbon → four female Fastons on the motor tabs | Each DRV8870 H-bridge drives one motor differentially, so each conductor carries one motor lead at the pump's published ~[0.8 A](PUMP_PEAK_A). Conductor order, +X to −X: `AM2`, `AM1`, `BM2`, `BM1`; the +X pair serves pump A and the −X pair pump B. DC-5 crosses front-top's common rear electrical passage below SIG-7, then splits through the transverse channel to the motor terminal rooms. With front-top loose, thread its bare pump end through that passage and out underneath, crimp and ring out the Fastons, land them on the loose pumps, then raise the prepared pumps and lower retainer motor-first while drawing slack aft. Keep DC-5 bare through the printed channels and below the funnel frame, west of the Y-B stem elbow and over the J6 leads. Plug its XHP-4 into J13 through the funnel opening after closure. |
| DC-6 | MANIFOLD A J1 (`COM` + `OUT1`–`OUT8`) | 8 Beduan solenoid coils on manifold A | 9-conductor trunk | [22](AWG_SIG) | [~550 mm](LEN_MAN_A) to each coil, `COM` [~300 mm](LEN_MAN_A_COM) to the fan-out, then [~450 mm](LEN_MAN_A_FANOUT) per valve | XH housing at J1; `COM` into a Wago 221-420 at the manifold; female disconnects per valve | Low-side switching: `COM` carries the shared [12 V](V_DC) from the main board's V12 island to every valve +, exploded at the manifold Wago; each valve − returns on its `OUT` conductor to the on-board TBD62083 (U4). Valve ↔ `OUT` mapping per [`valve-control.mmd`](/hardware/wiring/valve-control.mmd). |
| DC-7 | MANIFOLD B J2 (`COM` + `OUT1`–`OUT2`) | 2 Beduan solenoid coils on manifold B | 5 of the 6-way J2 trunk populated | [22](AWG_SIG) | [~550 mm](LEN_MAN_B) to each coil; `COM` [~300 mm](LEN_MAN_B_COM) to the fan-out, then [~450 mm](LEN_MAN_B_FANOUT) maximum per positive branch | XH housing at J2; `COM` into a Wago 221-415 at the manifold; female disconnects per valve | Same pattern as DC-6. The trunk populates `COM` + `OUT1` + `OUT2` + `FAN` (the fan sink is DC-8) + `OUT3` (V-K's − on run DC-9); `OUT4` is wired on the main board but carries no valve — a spare channel, left unpopulated in the harness. |
| DC-8 | MANIFOLD B J2 `FAN` + a `COM` branch off the manifold fan-out | Condenser fan motor ([12 V](V_DC) DC brushless axial, ~[0.35 A](FAN_A)) | + + ULN-sink return | [22](AWG_SIG) | [~650 mm](LEN_FAN) switched return from J2; [~450 mm](LEN_MAN_B_FANOUT) positive from the lower +X-wall Wago | Donor fan lead; its exact terminal position and connector remain unlocated in CAD | The two conductors follow the clear approach to the condenser crown. Bench cuts reserve length for the donor lead and are trimmed at fitting. The fan + ties to the manifold's `COM` fan-out; `FAN` sinks the − side through TBD62083 #2 (U5, MCP23017 0x21 PA3). Flyback via the driver's integrated diode to `COM`. |
| DC-9 | MANIFOLD B J2 (`OUT3` + a `COM` tap) | V-K water-supply fill/shutoff coil, in back-top's east sidewall mount | 2 conductors off the J2 trunk | [22](AWG_SIG) | [~350 mm](LEN_VK) `OUT3` from the board; positive cut from the [~450 mm](LEN_MAN_B_FANOUT) branch stock, trimmed to the installed route plus termination allowance | Female disconnects at the valve | Low-side switching, same pattern as the manifold valves: `OUT3` sinks V-K's − through TBD62083 #2 (U5, MCP23017 0x21 PA5); + taps the shared J2 `COM` at the lower +X-wall Wago. Both legs land on V-K's blades on the open back-top; `OUT3`'s crimped contact seats in J2 cavity 4, and the positive in its Wago, after the box closes. V-K is a separate part from manifold B — mapping per [`valve-control.mmd`](/hardware/wiring/valve-control.mmd), plumbing per [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2. |

**Solenoid COM current budget.** Each Beduan coil is 5.5 W nameplate — ~[0.46 A](COIL_A) cold at 12 V, settling lower as the winding heats (`power.mmd` cites ~0.3 A sustained; measure hold current at bring-up to settle the figure). The canonical operating states ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)) open at most three valves at once, and at most three on a single manifold, so each manifold's shared 12 V COM contact (the `COM` pin on MANIFOLD A / J1 and MANIFOLD B / J2, a 2.50 mm XH contact rated ~3 A) carries ≤ ~1.4 A — comfortably inside the contact. MANIFOLD B adds the ~[0.35 A](FAN_A) condenser fan and V-K (~[0.46 A](COIL_A) on `OUT3`, sharing J2's `COM`); V-K is a supply valve, open only during a fill, so it does not stack with a manifold-B dispense in normal operation. Energizing a whole manifold at once is the only way to approach the limit (8 valves on MANIFOLD A ≈ 2.4–3.7 A across the 0.3–0.46 A range); no operating state does this, so firmware must not drive a full manifold simultaneously. Low-side switching means COM is the only conductor shared across valves — the manifold carries no separate ground return.

### Sensors and signal (low-voltage, low-current)

Three looms fan out from single connectors: SENSORS J4 carries SIG-1 / SIG-4 with a shared `GND` split at the core-lid sensor WAGO; REEDS B J7 carries SIG-2 / SIG-3 / SIG-11 with a shared `GND` exploded at the cold-core end; REEDS A J6 is SIG-10 alone. Every reed input rides its MCP23017's internal pull-up — no resistors in any loom. Every loom on this table is 22 AWG black silicone ribbon, one or two ribbons wide — the pairing per connector is in [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) § Ribbon pairs, and the AWG column below is the conductor gauge, which the ribbon and the bulk spool share.

| # | From | To | Conductors | AWG | Approx. length | Notes |
|---|---|---|---|---|---|---|
| SIG-1 | SENSORS J4 `IO26` + `3V3` + `GND` | 1-wire temp bus — DS18B20 (0x28, carbonator wall) + DS18S20 (0x10, evap suction) | data + [3.3 V](V_IO) + GND, parallel-bussed | [22](AWG_SIG) | [~650 mm](LEN_ONEWIRE) to the probes in the core | The [4.7 kΩ](DS18B20_PULLUP) data pull-up is on-board (R9) — nothing in the loom. |
| SIG-2 | REEDS B J7 `CLO` + `GND` | Reed switch — low (carbonator) | switch + shared GND | [22](AWG_LV) | [~500 mm](LEN_CARB_REEDS) | MCP23017 0x21 PB4, INPUT_PULLUP. |
| SIG-3 | REEDS B J7 `CHI` + shared GND | Reed switch — high (carbonator) | switch | [22](AWG_LV) | [~500 mm](LEN_CARB_REEDS) | MCP23017 0x21 PB5, INPUT_PULLUP. |
| SIG-4 | SENSORS J4 `IO25` + `V5` + `GND` | DIGITEN flow meter (on edge between pump and gas group, ports fore–aft and lead root downward) | pulse + [5 V](V_LOGIC) + GND | [22](AWG_LV) | [~300 mm](LEN_FLOW) (internal, above the core lid) | Pulse interrupt; flow detection is internal — does not leave the enclosure. |
| SIG-6 | FAUCET J3 (1 `IO33` TX / 2 `IO35` RX / 3 `V5` / 4 `GND`) | ESP32-S3-Touch-LCD-1.47 faucet display at the end of the gooseneck | UART + power | 22 in / 28 out | [~400 mm](LEN_FAUCET_INBOARD) inboard + [~2 m](LEN_UMBILICAL) outboard | J3 → 22 AWG black ribbon → RiteAV CAT3 USOC jack at X−30/Z274.376 in the +Y wall of back-top → RJ11 6P4C plug → 28 AWG black ribbon to the display. **J3 3/V5 → jack 2 (white/orange) → C1/VBUS; J3 4/GND → jack 3 (blue) → C2/GND; J3 2/IO35 RX → jack 4 (white/blue) → C3/TXD; J3 1/IO33 TX → jack 5 (orange) → C4/RXD.** Colors name the jack's printed labels; C1 is the outboard ribbon edge marked white at both ends. Contacts 1 and 6 are unused. Direct 3.3 V TTL UART, with [5 V](V_LOGIC) power across the joint. [Oriented plug and jack picture, page 15](https://homesodamachine.com/read/faucet-assembly-guide/faucet-assembly-guide.pdf#page=15). |
| SIG-7 | DISPLAY J9 (`B` / `A` / `GND` / `V12`) | ESP32-S3-Touch-LCD-4.3B enclosure display on the front face (fixed) | RS485 pair + [12 V](V_DC) + GND | [22](AWG_LV) | [~400 mm](LEN_FRONT_FACE) (flat PCB → front face, internal) | One 22 AWG 4P ribbon (`bom.md` §11). The RS485 transceiver is on-board (U7, COS13487 auto-direction; SM712 ESD array at the connector): A/B on a twisted pair to the 4.3B's onboard SP3485, and the display's 7–36 V screw input takes [12 V](V_DC) off `V12` on the same loom. Fixed mount in the 30° display facet per [`/hardware/printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md). Its ribbon shares front-top's rear electrical mouth with DC-5 and rises through the internal chimney to the display pocket. Keep it bare inside the print and finish the PET braid aft of the common mouth; land the display terminals while the facet is open. |
| SIG-9 | SENSORS J4 `IO23` + `IO27` | Reserved, unpopulated | No cable | — | — | ASSE discharge is visible at the separate faucet outlet. |
| SIG-10 | REEDS A J6 (`GND` + `RA1`–`RA4`) | Reservoir A level reeds (4) | 4 switches + shared GND | [22](AWG_LV) | [~600 mm](LEN_REEDS_A) | MCP23017 0x20 PB0–3, INPUT_PULLUP; one continuous `GND` from J6 with insulated taps at the reeds. See [`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md). |
| SIG-11 | REEDS B J7 `RB1`–`RB4` + shared GND | Reservoir B level reeds (4) | 4 switches | [22](AWG_LV) | [~500 mm](LEN_REEDS_B) | MCP23017 0x21 PB0–3, INPUT_PULLUP; shares the J7 loom and its cold-core-end Wago 221-413 `GND` with SIG-2 / SIG-3. |
| SIG-12 | GAS J11 (`GND` / `V5` / `DOUT` / `AOUT`) | MQ-6 combustible-gas / refrigerant-leak sensor, rear cabinet floor | analog + trip + [5 V](V_LOGIC) + GND | [22](AWG_LV) | [~600 mm](LEN_GAS) | One 22 AWG 4P ribbon (`bom.md` §11). `AOUT` (analog level) and `DOUT` (LM393 comparator trip) swing 0–5 V and are divided to 3.3 V on-board before IO39 / IO36, so a plain sensor cable is safe. The sensor heater runs on `V5`. Mounted low — R-600a is heavier than air. |

## Loom terminations

Board end: every low-voltage loom lands in a JST XH [2.5 mm](JST_PITCH) crimp housing mating its labeled wafer — one housing per connector, pin labels on the silk, so a loom cannot seat shifted. J4 and J7 share the 7P housing, so those two land by loom label ([`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)). The one exception is the [12 V](V_DC) inlet J10: ferrules under its 5.0 mm screw clamps.

Device end: female disconnects at valves, pumps, and fan; the current donor compressor uses its preserved factory-external electrical interface, whose connector and polarity mapping remain to be recorded; ring terminals land at ground studs; sensor and reed leads land per device. Shared-rail fan-outs happen at the device cluster, never at the main board — one `COM` / `GND` conductor rides the trunk. Reservoir A uses a continuous common with insulated reed taps; the four branched nodes use appropriately sized Wago lever nuts. The branch WAGOs occupy rooted wells at their device clusters:

| node | nut | ways | parent | what the branches reach |
|---|---|---|---|---|
| J1 MANIFOLD A `COM` | 221-420 | 9 of 10 | Front-top east wall, above the valve bank | V-A…V-H positives |
| J2 MANIFOLD B `COM` | 221-415 | 5 of 5 | Front-top east wall, below the 221-420 | V-I, V-J, condenser fan, V-K positives |
| J7 REEDS B `GND` | 221-413 | 3 of 3 | Core lid, aft of the PCB | reservoir B's 4 reeds + the carbonator's 2 |
| J4 SENSORS `GND` | 221-413 | 3 of 3 | Core lid, forward of the PCB | 1-wire bus, DIGITEN meter |

Three rear-wall 221-413 blocks carry **L, N and PE**, with ports facing forward. Four west-facing core-lid 221-413 blocks carry **sensor common, +12 V, DC GND and reed common**. The inlet earth pigtail reaches the lid earth stack through the rear PE block. Three more 221-413s, one port of each empty, join the compressor's switched H and N and the pump positive under the funnel opening; they go in last, with no printed well.

The manifold nuts face inboard. Leave their wire-entry faces and lever sweeps
open; the lower nut opens toward the front. Only shared positive conductors
enter these two nuts. Each switched return runs directly to its board OUT pin.

The [installed enclosure wiring model](README.md) carries all populated board
connectors and their shared-rail branches together in the complete machine.
[The resolved manifest](enclosure-wiring.json) names every
conductor, attachment, nominal profile, route, length and assembly owner. The
[worksheet](enclosure-wiring.csv) gives the same conductors as individual rows.

Board pin positions come from the fabricated circuit JSON and the native board
pose. Valve wire attachments follow the separate metal spades. Proposed wire
exits permit the flexible tab/disconnect dressing at G/J. The model includes the
removable XH housing envelopes and the fuse-splice insulation.

Routing status and terminal fidelity are separate. A proposed route remains an
assembly layout; unresolved routes stay visible and named. Exact donor lead
terminations, display connectors, motor tabs and the carbonator metal bond
landing retain their unlocated status. The [manual review](installed/routing-review.json)
records mesh intersections and native export readings against their artifact
hashes. It does not qualify physical harness fit or enclosure closing motions.

Each reservoir's four reeds share one continuous common in its 5P column, with
insulated local taps. The Wago joins that column common to the board return.
The carbonator pair has its own common branch at the reservoir-B Wago. The two
probes are parallel-bussed on the three 1-wire conductors.

The compressor cable uses [~700 mm](LEN_COMPRESSOR) preparation stock. The installed model
routes its switched-hot core through to relay #1 in two separate wire pieces: 606.306 mm
from the relay to the thermal fuse, then a 36.777 mm continuation from the fuse to the
compressor interface, 643.082 mm in all. The core ends at its join under the funnel
opening, short of the relay, so the same stock covers it; trim at the join. The shared
jacket occupies the fore floor lane; its insulated cores fan out to the two joins and
the lid earth stack. Dress and retain the jacket and fanouts before trimming the
conductors. The fuse's two leads reach separate insulated splice regions beside the
donor cover.

The model's centreline lengths exclude hidden contact insertion and final cut
reserve. The bench cuts remain fitting stock; use the current installed route
and its attachment status before settling a finished length. The fan routes
end at the condenser-crown approach while its donor lead remains unlocated.

The [local source-native receipts](installed/above-core-review/ground-j2-wiring-review.json)
and [routing witness receipt](installed/above-core-review/routing-witness-native-review.json)
give the preparation budget for the dressed fore connections:

| Conductor | Modeled path (mm) | Preparation stock | Nominal reserve (mm) |
|---|---:|---:|---:|
| PE-bus, rear PE WAGO → lid stack | 295.531 | [~400 mm](LEN_EARTH_BUS) | 104.469 |
| PE-carbonator, lid stack → carbonator | 423.501 | [~500 mm](LEN_EARTH_CARBONATOR) | 76.499 |
| J2-COM | 195.864 | [~300 mm](LEN_MAN_B_COM) | 104.136 |
| J2-FAN | 329.600 | [~650 mm](LEN_FAN) | 320.400 |
| DC3-negative | 253.272 | [~350 mm](LEN_PUMP) | 96.728 |
| J2-positive-K | 260.156 | [~450 mm](LEN_MAN_B_FANOUT) | 189.844 |
| J2-OUT3 | 277.762 | [~350 mm](LEN_VK) | 72.238 |

AC6-PE's modeled path is 333.114 mm within the same compressor cord; the
switched-hot budget above governs its common preparation stock. The carbonator
bond landing and donor fan lead remain unlocated. These reserves are fitting
allowances, not physical harness-fit measurements.

The peristaltic pumps have no such nut: DC-5 is two DRV8870 H-bridge pairs, each motor driven differentially on its own two conductors, so there is no rail to share and nothing to fan out. Four direct conductors run from J13 to the motor tabs.

Fabrication — bulk cut-to-length all-black wire, crimp tooling, sleeving, and per-assembly continuity testing — is [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md); stock is [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

## Grounding strategy

Single-point chassis ground at the core-lid ring-terminal stack, bonded back through the C14 inlet's earth pin to the building's protective earth.

- **C14 ground pin** → ground bus on the core lid (run AC-1 carries the green conductor from the inlet to the distribution block's G pole).
- **Ground bus** distributes to the compressor body (via AC-6) and the SS carbonator inside the cold core, via short bonding wires. The faucet carries no earth: its only conductors are SIG-6's SELV ribbon, and its tubes are plastic. Chassis grounding is via these discrete bonding wires; there is no metal chassis backbone.
- Separate ground bonds are [16 AWG](AWG_MAINS_U) green-insulated stranded wire with ring terminals at the bus and metalwork. AC-6 is the green 18 AWG conductor inside the SJOOW compressor cord, as specified in its run row.
- The chassis bond gives the appliance Class I status: if a fault energizes any exposed metal part, fault current returns to the building ground through the C14 cord and trips the upstream breaker before the user touches anything.

The stack's inlet bond uses its northeast-facing lug, the carbonator bond its
northwest-facing lug, and AC-6 its southwest-facing lug. Keep the inlet bond's
nominal 6 mm straight entry and the fore paired-tube tie head on the east side.
Fasten the stack before dressing AC4-H and AC5-N through the fore connection
area; hold those flexible leads clear of its vertical driver during service.
The complete installed harness has no simultaneous driver-clearance or
flexible handling-force qualification.

## What's not yet decided

- **Fuse on the AC primary** — a [5 A](PRIMARY_FUSE_A) fast-blow inline fuse between the C14 inlet and the AC distribution block was discussed in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) for bench testing. Whether it stays in the production unit (fuse holder in the +Y wall of back-top? fuse on the +X wall?) needs a decision.

## Revision

Lengths are bench cut targets, trimmed at each landing. Manifold, fan and V-K
cuts use the linked authored paths plus termination and dressing allowance.
Other fixed loom cuts use centre-based reach estimates; their complete installed
routes remain unqualified.

## Sources
[value](NAME) texts are updated by:
- `/hardware/wiring/_ac_wiring_schedule_sync.py`
