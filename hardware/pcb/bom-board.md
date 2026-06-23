# Controller PCB — Board BOM

The discrete-component bill for the consolidated controller board — the parts that land
on the PCB, as distinct from the module-stack lines they replace in
[`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §1 (see that file's "BOM delta" and
[`README.md`](/hardware/pcb/README.md) for the cost accounting). Reference designators
match [`netlist.md`](/hardware/pcb/netlist.md).

**Sourcing convention.** LCSC part numbers are JLCPCB-orderable candidates, given where the
part is confidently identified and stocked. Everything marked *verify* needs a cart check at
quote time — relay coil voltage and AC inrush rating, the RS485 part, inductor value/saturation
per the chosen buck, TVS standoffs, JST pin-count C-numbers, and the DRV8871 current-limit
resistor value. LCSC numbers and Basic/Extended status drift; re-confirm every line against the
live library before ordering. This is the LCSC cart the [`README.md`](/hardware/pcb/README.md)
"BOM delta" lists as pending.

**JLCPCB class** drives assembly cost: *Basic/Preferred* parts load free; each unique *Extended*
part adds a one-time feeder fee per order. The design keeps Basic where it can (all generic
0402/0603 R/C, AMS1117, common transistors/diodes/LEDs, USB-C, tactiles) and carries ~8–10
unique Extended lines (the ICs that hold value). See
[`fabrication.md`](/hardware/pcb/fabrication.md).

## Controllers and logic

| Ref | Qty | Part / value | Package | LCSC candidate | Class | Note |
|---|--:|---|---|---|---|---|
| U1 | 1 | ESP32-WROOM-32E | SMD module | C701341 | Basic | Edge placement, antenna keepout. 10 µF + 100 nF at 3V3 pin. |
| U2 | 1 | CH340X USB-UART | MSOP-10 | C435377 | Extended | No crystal needed. Or CH340C (C84681). Skippable if a UART-flash header is used instead. |
| U3, U4 | 2 | MCP23017-E/SO | SOIC-28 | C36658 | Extended | Addr 0x20 / 0x21 via A0–A2; /RESET → 3V3; 100 nF each. |
| U9 | 1 | DS3231SN# | SOIC-16 | C9866 | Extended | Integrated TCXO — no external 32.768 kHz crystal. VBAT → BT1. |
| U12 | 1 | RS485 transceiver (SP3485 / MAX3485 / THVD1450) | SOIC-8 | C9632 *verify* | Extended | 3.3 V part so RO can't over-volt GPIO 34. Auto-direction part saves a DE/RE GPIO. 120 Ω termination (bus end). |

## Drivers and switching

| Ref | Qty | Part / value | Package | LCSC candidate | Class | Note |
|---|--:|---|---|---|---|---|
| U5, U6 | 2 | ULN2803A | SOIC-18 | C963561 *verify body* | Extended | COM → +12 V (integrated flyback). Sinks 12 solenoids + condenser fan. |
| U7, U8 | 2 | DRV8871DDA, 3.6 A | HSOP-8, thermal pad | C86590 | Extended | Peristaltic pumps (~0.3–0.5 A, well within rating). Thermal-pad via array to a copper pour. |
| R_ILIM1, R_ILIM2 | 2 | DRV8871 ILIM resistor (~40–60 kΩ) | 0603 | *verify (per pump stall)* | Basic | One per DRV8871: ILIM → GND, sized for ~1–1.5 A trip. |
| K1 | 1 | AC relay, ≥16 A 250 VAC, reinforced creepage (HF115F-class) | PCB power relay | *verify HF115F-005-1ZS3* | Extended | Compressor leg. Rated for hermetic-compressor LRA inrush (~5–7× run). **Not** the bargain SRD. |
| K2 | 1 | DC relay, ≥10 A (SRD-12VDC / HF115F-012) | PCB power relay | *verify* | Extended | Gates 12 V to the SeaFlo pump (~5 A peak). 12 V coil off the bus. |
| OK1, OK2 | 2 | Optocoupler PC817 | DIP-4 / SOP-4 | C7470 | Basic | Relay-control gate isolation; preserves the fenced-corner discipline. |
| Q1, Q2 | 2 | 2N7002 low-side coil driver | SOT-23 | C8545 | Basic | One per relay coil; gate resistor from OK output. |
| D_K1, D_K2 | 2 | Flyback (1N4148W / SS14 for 12 V coil) | SOD-123 / SMA | C2128 / C2480 | Basic | One across each relay coil. |
| R_OPTO | 2 | 1 kΩ opto LED series | 0603 | C21190 | Basic | PC817 LED current from 3.3 V GPIO (~1–2 mA). |

## Power

| Ref | Qty | Part / value | Package | LCSC candidate | Class | Note |
|---|--:|---|---|---|---|---|
| U10 | 1 | Buck 12 V → 5 V, ≥3 A (MP2315) | SOIC-8 EP | C88288 | Extended | 5 V rail. MP1584EN (C107203) is the cheap async alternate. |
| U11 | 1 | Buck → 3.3 V, **or** AMS1117-3.3 LDO from 5 V | SOT-23-6 / SOT-223 | C6186 (AMS1117) | Basic | 3.3 V rail. LDO acceptable from 5 V (~1 W, copper pour); a 12 V→3.3 V LDO is not (8.7 W). |
| L1, L2 | 1–2 | Power inductor ~4.7–10 µH, ≥3 A sat | SMD 4×4 / 5×5 | *verify per buck* | Extended | One per buck stage (L2 omitted if U11 is an LDO). |
| C1 | 1 | 470 µF / 25 V low-ESR | radial Ø10 / SMD can | C516567 *verify* | Extended | 12 V input bulk (migrated from `bom.md` §1 Rubycon line). |
| C_buck | 4 | 22 µF 25 V / 22 µF 6.3 V MLCC | 0805/1210 | *verify* | Extended | Buck in/out ceramics (input derated to 25 V on the 12 V rail). |
| D1 | 1 | TVS SMAJ15A (12 V rail) | SMA | C913944 *verify* | Extended | 12 V input transient clamp. |
| D_RP | 1 | Reverse-polarity protection (P-FET or Schottky) on 12 V IN | — | *verify* | — | 12 V IN is the battery-backup splice seam — guard against a reversed pack. |

## Passives, protection, indicators

| Ref | Qty | Part / value | Package | LCSC candidate | Class | Note |
|---|--:|---|---|---|---|---|
| R1, R2 | 2 | 4.7 kΩ I²C pull-up | 0603 | C25900 | Basic | SDA / SCL to 3.3 V. |
| R3 | 1 | 4.7 kΩ 1-wire pull-up | 0603 | C25900 | Basic | DS18B20 data to 3.3 V (migrated from `bom.md` §1 EDGELEC line). |
| R4, R5 | 2 | 10 kΩ carbonator-reed pull-up | 0603 | C25804 | Basic | GPIO 36 / 39 (input-only pads — external pull-ups required). The 8 reservoir reeds use MCP internal pull-ups. |
| R_FLOW | 1 | 10 kΩ flow-meter pull-up | 0603 | C25804 | Basic | Open-collector pulse to GPIO 23; add level handling for the 5 V sensor. |
| R_CC1, R_CC2 | 2 | 5.1 kΩ USB-C CC | 0603 | C25905 | Basic | One per CC line to GND (advertise sink). |
| R_EN, R_IO0 | 2 | 10 kΩ strap pull-up | 0603 | C25804 | Basic | EN + IO0; plus strap states for IO2/IO12/IO15 per the WROOM table. |
| C_EN, C_IO0 | 2 | 1 µF (EN RC) + 100 nF (IO0) | 0603 | C15849 / C14663 | Basic | Auto-boot RC per DevKitC. |
| C_dec | ~12 | 100 nF X7R | 0603 | C14663 | Basic | One per IC power pin — the most-used reel part. |
| C_bulk | 3 | 10 µF 25 V | 0805 | C15850 *verify* | Basic | Local bulk on 5 V, 3.3 V, and the ESP32 3V3 (TX burst). |
| D_ESD | ~4 | ESD array (3.3 V/5 V SOT-23 dual) | SOT-23 | *verify per net* | Extended | On cable-leaving nets: 1-wire, flow, faucet UART TX/RX. RS485 has its own clamp. |
| LED1, LED2 | 2 | Green power-good + status | 0805 | C72043 / C2286 | Basic | Each with a 1 kΩ series resistor. |
| R_LED | 2 | 1 kΩ | 0603 | C21190 | Basic | LED series. |
| SW1, SW2 | 2 | Tactile (BOOT, EN) | SMD 3×6 / TH 6×6 | C318884 | Basic | TH version is fine for the hand-solder pass. |
| BT1 | 1 | CR2032 holder | SMD | C70376 | Extended | RTC backup. Cell is a hand-fit consumable. |

## Connectors

| Ref | Qty | Part / value | Package | Note |
|---|--:|---|---|---|
| J1 | 1 | USB-C 2.0, 16P | SMD | C2765186 (Basic). Service/flash port. |
| J2 | 1 | 12 V IN — JST-VH 2P or 5.08 mm screw | TH | ≥10 A. Trunk current; see power budget below. |
| J3, J4 | 2 | AC terminal block, 300 V, 5.08/7.62 mm | TH | Fenced corner. **Not** JST. J3 = AC in (2P), J4 = compressor out (3P). |
| J5 | 1 | Diaphragm pump 12 V — screw or XH paralleled | TH | ~5 A peak; XH ~3 A/pin → double up or screw. |
| J6, J7 | 2 | JST-XH 2P | TH | Pump A / B outputs. |
| J8 | 1 | JST-XH ~9P | TH | U5 → solenoids V-A…V-H + COM. |
| J9 | 1 | JST-XH ~7P | TH | U6 → V-I…V-K-B + condenser fan + COM. |
| J10, J11 | 2 | JST-XH 5P | TH | Reservoir A / B reeds + GND. |
| J12 | 1 | JST-XH 3P | TH | Carbonator reeds low/high + GND. |
| J13, J14 | 2 | JST-XH 3P | TH | DS18B20 1-wire; flow meter. |
| J15 | 1 | JST-XH 2P | TH | Backflow moisture + GND. |
| J16, J17 | 2 | JST-XH 4P (edge) | TH | Config-display RS485; faucet-display UART. |

JST-XH C-numbers (C158012 2P, C157930 3P, C144401 4P, C157931 5P) *verify pin count at order.*

## Power budget

The board takes one 12 V input from the off-board Mean Well IRM-90-12ST (80 W / 12 V /
**6.7 A** ceiling) and is the 12 V fan-out for the whole appliance. Loads from
[`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) and
[`/hardware/future.md`](/hardware/future.md):

| Rail | Loads | Typical | Peak |
|---|---|--:|--:|
| 12 V (fan-out) | diaphragm pump (relay #2), 12 solenoids, condenser fan, 2 peristaltic pumps, 4.3B display, buck input | ~1.0–1.5 A | **6.7 A** (design basis = PSU ceiling) |
| 5 V | faucet display, flow meter, relay opto/coil, 3.3 V stage input | ~0.6 A | ~1.05 A |
| 3.3 V | ESP32 (~0.5 A WiFi TX), 2× MCP23017, DS3231, RS485, pull-ups/logic | ~0.18 A | ~0.57 A |

- **Worst reachable 12 V state ≈ 6.0 A** — a refill cycle (SeaFlo ~5 A + fan + display +
  buck). The firmware refill-vs-dispense interlock (relay #2 / GPIO 16 held off during a
  dispense, per `power.mmd`) is load-bearing for the power design: it guarantees the pump
  and the full valve bank are never concurrent, so every reachable state stays under the
  6.7 A PSU ceiling. Valve concurrency is low by architecture (source-selection energizes
  ~3–4 of 12), so the 3.6 A all-on figure is a copper-margin bound, not an operating point.
- **U10 (12 V → 5 V):** size ≥2 A (peak ~1.05 A, ≥2× headroom for the faucet-display/WiFi
  transient up the umbilical). MP2315 (3 A) first pick.
- **U11 (→ 3.3 V):** size ≥1 A (peak ~0.57 A). Second buck preferred; AMS1117 from 5 V
  acceptable (~1 W). A 12 V → 3.3 V LDO would dissipate ~8.7 W — the explicit reason for a
  buck.
- **12 V input + copper:** size to the 6.7 A ceiling. JST-VH (≥10 A/contact) or a 5.08 mm
  screw block, not a barrel jack. Route the 12 V net as a **pour**, not a trace — 2 oz outer
  pour, ≥100 mil minimum neck, ≥6× 0.3 mm stitching vias at layer changes. Reverse-polarity
  protection (D_RP) on the input.
