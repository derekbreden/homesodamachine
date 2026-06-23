# Controller PCB — Netlist

The connection list for the consolidated controller board: every component with a
reference designator, every net, and the ESP32-WROOM-32E GPIO map. This is the input
to schematic capture — it is the [`README.md`](/hardware/pcb/README.md) scope expressed
as connections.

**Board-authoritative.** Where this file and the legacy prototype firmware
(`firmware/src/main.cpp`) disagree on a GPIO, this file wins — the consolidated board
follows the wiring topology docs, and `main.cpp` predates the move of the valves to the
MCP23017 bank (it still `#define`s GPIO 17/27 as clean solenoids, GPIO 4 as a dispensing
solenoid, GPIO 13 as the removed flavor switch). A firmware pin-map revision to match
this netlist is one of the [Open decisions](#open-decisions).

Reconciled from:
[`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd),
[`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd),
[`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd),
[`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md),
[`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §1, and
[`/hardware/assembly/electronics-shelf.md`](/hardware/assembly/electronics-shelf.md).

## Components

Reference designators are stable across this file and [`bom-board.md`](/hardware/pcb/bom-board.md).

### Active devices

| Ref | Part | Package | Role |
|---|---|---|---|
| U1 | ESP32-WROOM-32E | SMD module, castellated | Main MCU. I²C, 2× UART, 1-wire, flow input, carbonator reeds, pump drive, relay drive. Replaces ESP32-DevKitC. |
| U2 | CH340X (or CP2102N) | MSOP-10 / QFN-24 | USB-UART bridge for the service port — WROOM has no native USB. DTR/RTS → EN/IO0 auto-boot. |
| U3 | MCP23017 @ 0x20 | SOIC-28 | Valve bank: PA0–7 + PB0–3 → ULN inputs; PB4–7 ← Reservoir A reeds. |
| U4 | MCP23017 @ 0x21 | SOIC-28 | PA0–3 ← Reservoir B reeds; PA4 → ULN U6 ch5 (condenser fan); PA5–7 + PB0–7 spare. |
| U5 | ULN2803A #1 | SOIC-18 | Sinks solenoids V-A…V-H (ch1–8). COM → +12 V (integrated flyback). |
| U6 | ULN2803A #2 | SOIC-18 | Sinks V-I, V-J, V-K-A, V-K-B (ch1–4) + condenser fan (ch5). ch6–8 free. COM → +12 V. |
| U7 | DRV8871 (pump A) | HSOP-8, thermal pad | Peristaltic flavor pump A H-bridge. Replaces L298N channel A. |
| U8 | DRV8871 (pump B) | HSOP-8, thermal pad | Peristaltic flavor pump B H-bridge. |
| U9 | DS3231SN | SOIC-16 | I²C RTC @ 0x68, integrated TCXO. VBAT from BT1. Replaces the DS3231 module. |
| U10 | Buck 12 V → 5 V | SOIC-8 / SOT-23-6 + L | 5 V logic rail. Replaces the L298N's onboard 7805. |
| U11 | Buck (or LDO) → 3.3 V | SOT-23-6 + L / SOT-223 | 3.3 V logic rail. Replaces the ESP32 module's AMS1117. |
| U12 | RS485 transceiver | SOIC-8 | UART1 ↔ A/B to the 4.3B config display (which carries its own SP3485). 3.3 V part. |
| OK1, OK2 | Optocoupler (PC817-class) | SOIC-4 / DIP-4 | Gate isolation for relay #1 / #2 control. |
| Q1, Q2 | Low-side coil driver (2N7002-class) + flyback | SOT-23 | Drive K1 / K2 coils from OK1 / OK2. |
| K1 | AC relay, ≥16 A 250 VAC, reinforced creepage | PCB power relay | Switches the 120 VAC compressor hot leg in the fenced corner. Rated for hermetic-compressor LRA inrush. |
| K2 | DC relay, ≥10 A | PCB power relay | Gates +12 V to the SeaFlo diaphragm pump (~5 A peak). |
| BT1 | CR2032 holder | SMD/TH coin holder | DS3231SN VBAT. |

### Passives, protection, indicators

| Ref | Part | Role |
|---|---|---|
| L1, L2 | Power inductor, ~4.7–10 µH, ≥3 A sat | One per buck stage (L2 omitted if U11 is an LDO). |
| C1 | 470 µF / 25 V low-ESR | 12 V bulk at the input (migrated from `bom.md` §1 Rubycon line). |
| C2, C3 | 100–470 µF | 5 V and 3.3 V rail bulk. |
| C_dec (×~12) | 100 nF X7R | One per IC power pin. |
| R1, R2 | 4.7 kΩ | I²C SDA / SCL pull-ups to 3.3 V. |
| R3 | 4.7 kΩ | DS18B20 1-wire pull-up to 3.3 V (migrated from `bom.md` §1 EDGELEC line). |
| R4, R5 | 10 kΩ | Carbonator-reed pull-ups (GPIO 17 / 27). The 8 reservoir reeds use the MCP23017 internal pull-ups. |
| D1 | TVS, SMAJ15A | 12 V input transient clamp. |
| D2… | ESD arrays | At each off-board signal connector (1-wire, flow, UARTs, reeds). |
| LED1, LED2 | Power-good + status | On-board indication, each with a series resistor. |
| SW1, SW2 | BOOT, EN tactile | Download-mode and reset buttons. |

### Connectors

Field connectors are vertical-entry JST-XH in islands adjacent to their owners, except
the AC corner (300 V pluggable terminal blocks) and the 12 V input (stepped up to VH or a
screw block for the trunk current). Per [`README.md`](/hardware/pcb/README.md) "Layout".

| Ref | Type | Pins | Net / destination |
|---|---|---|---|
| J1 | USB-C | — | Service port: flash + serial, to U2. |
| J2 | JST-VH 2P / screw | 2 | +12 V IN from the Mean Well PSU. Battery-backup splice seam ([`/hardware/battery-backup/README.md`](/hardware/battery-backup/README.md)). |
| J3 | 300 V terminal block | 2 | Unswitched AC H + N into the fenced corner (AC-3). |
| J4 | 300 V terminal block | 3 | Switched-H (K1 NO) + N + earth → compressor (AC-4/5/6). |
| J5 | Screw / XH paralleled | 2 | K2-switched +12 V → SeaFlo diaphragm pump (~5 A, DC-3). |
| J6, J7 | JST-XH 2P | 2 | DRV8871 U7 / U8 → Kamoer pump A / B (DC-5, spade-connected at the cartridge). |
| J8 | JST-XH ~9P | 9 | ULN U5 ch1–8 → solenoids V-A…V-H + 12 V COM. |
| J9 | JST-XH ~7P | 7 | ULN U6 ch1–4 → V-I…V-K-B, ch5 → condenser fan + 12 V COM. |
| J10 | JST-XH 5P | 5 | Reservoir A reeds 1–4 + GND → U3 PB4–7. |
| J11 | JST-XH 5P | 5 | Reservoir B reeds 1–4 + GND → U4 PA0–3. |
| J12 | JST-XH 3P | 3 | Carbonator reeds low (GPIO 17) + high (GPIO 27) + GND. |
| J13 | JST-XH 3P | 3 | DS18B20 1-wire: data (GPIO 16) + 3.3 V + GND (2 probes bussed). |
| J14 | JST-XH 3P | 3 | DIGITEN flow meter: pulse (GPIO 23) + 5 V + GND. |
| J15 | JST-XH 2P | 2 | Backflow drip-pan moisture sensor (SIG-9) + GND. GPIO TBD. |
| J16 | JST-XH 4P (edge) | 4 | Config-display RS485: A + B + 12 V + GND → 4.3B (SIG-7). |
| J17 | JST-XH 4P (edge) | 4 | Faucet-display TTL UART: TX + RX + 5 V + GND, up the umbilical (SIG-6). |

## ESP32-WROOM-32E GPIO map

| GPIO | Function | Connects |
|---|---|---|
| 21 | I²C SDA (R1 pull-up) | U3 0x20, U4 0x21, U9 0x68 |
| 22 | I²C SCL (R2 pull-up) | U3, U4, U9 |
| 16 | 1-wire data (R3 pull-up) | J13 → 2× DS18B20 (tank wall + suction line) |
| 17 | Carbonator reed LOW, pull-up | J12 — refill threshold. *(legacy `main.cpp`: clean solenoid)* |
| 27 | Carbonator reed HIGH, pull-up | J12 — full threshold. *(legacy `main.cpp`: clean solenoid)* |
| 23 | Flow pulse (interrupt) | J14 → DIGITEN flow meter |
| 14 | Relay #1 drive | OK1 → Q1 → K1 (compressor 120 VAC) |
| 4 | Relay #2 drive | OK2 → Q2 → K2 (diaphragm pump 12 V). *(legacy `main.cpp`: dispensing solenoid)* |
| 25 | Pump A IN1 | U7 |
| 26 | Pump A IN2 | U7 |
| 33 | Pump A — legacy A_ENA | **Decision:** free spare, or PWM-bearing IN to U7 (DRV8871 is 2-wire). |
| 18 | Pump B IN1 | U8 |
| 5 | Pump B IN2 (strapping pin) | U8 |
| 19 | Pump B — legacy B_ENA | **Decision:** free spare, or PWM-bearing IN to U8. |
| 15 | UART1 TX (strapping pin) | U12 DI → RS485 → 4.3B config display |
| 34 | UART1 RX (input-only) | U12 RO |
| 32 | UART2 TX | J17 → faucet display |
| 35 | UART2 RX (input-only) | J17 ← faucet display |
| 0 | BOOT strap | SW1 + 10 k + U2 RTS |
| EN | Reset | SW2 + 10 k + RC + U2 DTR |
| 1 / 3 | UART0 TX/RX | U2 (service console) |
| — | Backflow moisture (SIG-9) | **Unassigned.** Candidates: GPIO 2, 12, 13 (or input-only 36/39 with external pull-up). |

Spare after assignment: GPIO 2, 12, 13 (bootstrap-sensitive), input-only 36, 39.

## Nets (summary)

- **+12 V** — J2 in; C1; U5/U6 COM; U7/U8 VM; U10 VIN; K2 common; J8/J9 valve+fan COM; J16 display 12 V. The board's pours are the 12 V fan-out.
- **+5 V** — U10 out; U2; U11 VIN; relay opto/coil stages; J14 flow 5 V; J17 faucet 5 V.
- **+3.3 V** — U11 out; U1; U3/U4; U9; U12; R1/R2/R3 pull-ups; J13 DS18B20 3.3 V.
- **GND** — common logic ground. The AC-corner protective earth is a separate net, tied to logic ground only at the single-point chassis bond off-board.
- **I2C_SDA / I2C_SCL** — U1 21/22 ↔ U3, U4, U9.
- **VALVE_A…VALVE_H** — U3 PA0–7 → U5 IN1–8 → J8.
- **VALVE_I…VALVE_K-B** — U3 PB0–3 → U6 IN1–4 → J9.
- **FAN_DRIVE** — U4 PA4 → U6 IN5 → J9 (low-side; fan + on +12 V).
- **RSVR_A_REED1–4 / RSVR_B_REED1–4** — J10/J11 → U3 PB4–7 / U4 PA0–3 (INPUT_PULLUP).
- **CARB_REED_LOW / _HIGH** — J12 → GPIO 17 / 27.
- **ONEWIRE_DATA** — GPIO 16 + R3 → J13.
- **PUMP_A/B_IN1/IN2** — GPIO 25/26, 18/5 → U7/U8; OUT → J6/J7.
- **RELAY1/2_DRIVE** — GPIO 14/4 → OK1/OK2 → Q1/Q2 → K1/K2 coils.
- **COMPRESSOR_AC_HOT** — J3 → K1 → J4 (switched). Creepage-isolated corner.
- **UART1 (RS485) / UART2** — GPIO 15/34 → U12 → J16; GPIO 32/35 → J17.
- **USB** — J1 → U2 → UART0 + EN/IO0.
- **VBAT** — BT1 → U9.

## Open decisions

Resolved at schematic capture; each changes a footprint, a net, or a part value.

1. **Pump driver enable pins.** The DRV8871 is a 2-wire (IN1/IN2) bridge; the L298N it
   replaces was 3-wire (ENA/IN1/IN2). For each pump, either drop the ENA pin (GPIO 33,
   19 become free spares; speed via PWM on one IN) or keep GPIO 33/19 as the PWM-bearing
   IN. The choice sets which GPIO carries PWM into U7/U8.
2. **Backflow moisture-sensor GPIO (SIG-9).** Unassigned in `esp32-pinout.mmd`;
   [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md)
   step 6 expects it live, so it must be assigned on the board. Pick from GPIO 2/12/13.
3. **Relay coil voltage (5 V vs 12 V).** Sets Q1/Q2 sizing and the flyback rail. 5 V keeps
   coil current low; 12 V avoids loading the 5 V buck.
4. **3.3 V rail: second buck vs AMS1117 LDO from 5 V.** A buck is preferred; an LDO from
   the 5 V rail (~1 W at peak) is acceptable with a copper pour. An LDO from 12 V is not
   (8.7 W) — see [`bom-board.md`](/hardware/pcb/bom-board.md) power notes.
5. **Diaphragm-pump connector (J5).** XH is ~3 A/pin; the ~5 A peak needs paralleled pins
   or a screw terminal.
6. **Flow-meter level.** The DIGITEN sensor is 5 V-powered; its pulse into GPIO 23 needs an
   open-collector pull-up to 3.3 V or a level step — confirm it does not over-volt the pin.
7. **0x21 vs direct GPIO.** `valve-control.mmd` notes 0x21 could be dropped for direct
   ESP32 GPIO (2/12 + input-only 36/39) or a 74HC165. The board commits to 2× MCP23017;
   capture treats the direct-GPIO option as not-populated unless chosen.
8. **AC corner.** Enforce ≥8 mm creepage and a milled isolation slot under K1; AC
   terminals are 300 V blocks, not JST; the corner stays isolated from logic ground.
9. **USB-UART bridge vs flash header.** U2 + auto-reset preserves the DevKitC service path;
   a bare 6-pin UART-flash header drops an Extended part but needs an external adapter.
10. **Firmware pin-map revision.** Update the firmware GPIO map to match this netlist (the
    legacy `main.cpp` `#define`s for GPIO 4/12/13/17/27 are prototype-era).
