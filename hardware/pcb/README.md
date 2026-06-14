# Controller PCB

A single consolidated controller board for the integrated appliance, replacing the
module stack on the electronics shelf. Designed in-repo (KiCad) under Derek's
guidance, fabbed as bare boards by a web fab (JLCPCB-class), assembled in-house:
SMD placement and reflow on our own equipment, through-hole (connectors, relays,
coin holder) as a hand-solder pass.

## Scope

On the board:

- **ESP32-WROOM-32E** module (replaces the DevKitC + DIN-rail breakout), USB-C
  service port, BOOT/EN buttons.
- **2× MCP23017** (SOIC-28) at 0x20/0x21 — valve bank + reed banks, as in
  [`/hardware/assembly/firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md).
- **2× ULN2803A** (SOIC-18) — solenoid bank + condenser fan low-side drive.
- **2× DRV8871-class H-bridges** — the two peristaltic flavor pumps (replaces the
  L298N module).
- **DS3231SN + CR2032 holder** (replaces the RTC module).
- **2× relays, integrated with their opto/driver stages** (replaces the Teyleten
  modules): relay #1 switches the compressor's 120 VAC hot leg in a fenced,
  creepage-isolated corner of the board; relay #2 gates 12 V to the SeaFlo
  diaphragm pump.
- **12 V → 5 V → 3.3 V regulation** on-board (two buck stages, in place of the
  dev modules' onboard linear regulators; absorbs the shelf's DC distribution
  block — the board's pours are the 12 V fan-out).
- Bulk capacitance, DS18B20 pull-up, status LEDs, ESD/TVS at field connectors.

Off the board, unchanged:

- **Mean Well IRM-90-12ST** — the board takes one `12 V IN` connector. The 12 V
  bus between PSU and board is the splice seam for
  [`/hardware/battery-backup/README.md`](/hardware/battery-backup/README.md)
  (transfer module + LiFePO4 pack), and keeps a dead PSU a part-swap.
- **C14 inlet, GFCI, AC distribution Wagos, ground bus** — AC stays on the shelf
  except the compressor leg routed through relay #1's fenced corner.
- Both ESP32-S3 displays (4.3B config + faucet), all field sensors and actuators —
  these connect to the board, they don't live on it.

## Layout

Target: **100 × 100 mm, 4-layer.**

Connectors are vertical-entry JST XH in **islands adjacent to their owners** —
reed-bank headers on their MCP23017's port rows, pump/valve headers at the driver
stages, sensor headers near the ESP32 — with the harness leaving vertically into
a loom. Edge positions are reserved for what humans touch in service: the two
display UARTs, USB-C, and the AC corner. Silkscreen labels per island/bank rather
than per header; wire identity rides the harness heat-shrink flags (SIG-N IDs per
[`/hardware/assembly/wiring.md`](/hardware/assembly/wiring.md)).

Fab panel: 2-up or 4-up with rails for in-house placement.

## BOM delta

Lines deleted from [`bom.md`](/hardware/ledger/bom.md) §1 (delivered-cost
convention, per unit):

| Deleted line | $ |
|---|---:|
| ESP32-DevKitC-32E | $11.00 |
| ESP32 DIN Rail Breakout Board | $25.99 |
| L298N dual H-bridge (1 of 4 pk) | $2.68 |
| MCP23017 expander #1 | $12.99 |
| MCP23017 expander #2 (bom.md §9 line) | $12.99 |
| DS3231 RTC module (1 of 2 pk) | $3.54 |
| ULN2803A module 2-pack | $6.59 |
| Teyleten opto relay modules × 2 | $5.20 |
| **Total deleted** | **$80.98** |

The DC distribution block (an unpriced TBD in bom.md §11) is also absorbed. The
470 µF bulk cap and the 4.7 kΩ pull-up migrate onto the board as reel parts. The
module-to-module XH hop harnesses disappear; field-harness connectors remain.

What the board adds per unit — estimates pending the first JLCPCB quote and LCSC
cart, stated as ranges:

| Qty | Bare PCB (4L, 100×100, panelized) | Components (reel/cut-tape + TH) | Board total (est.) | Net vs. $80.98 deleted |
|---:|---:|---:|---:|---:|
| 10 | ~$4–6 | ~$32–38 | ~$36–44 | ≈ −$37 to −$45 |
| 50 | ~$2–3 | ~$26–30 | ~$28–33 | ≈ −$48 to −$53 |
| 100 | ~$1.50–2.50 | ~$24–28 | ~$26–30 | ≈ −$51 to −$55 |

Deleted-module prices are retail-constant with quantity; board cost falls with
quantity, so the per-unit saving grows with the batch. Assembly equipment
(pick-and-place, feeders, stencil, reflow) is capital in
[`/hardware/ledger/tools.md`](/hardware/ledger/tools.md) terms, not per-unit BOM.

## Firmware

Same firmware tree, new pin map revision: the MCP23017s, ULN channels, pump
drivers, relays, RTC, and both display UART links keep their roles; GPIO
assignments move to the board's netlist. USB-C service port carries the same
flash/debug path as the DevKitC.

## Status

Plan. No schematic yet. First artifact is the KiCad project in this directory.
