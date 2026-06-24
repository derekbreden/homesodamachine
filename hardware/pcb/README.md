# Controller PCB

The controller board is a **through-hole carrier**: the controller modules plug
into 2.54 mm header sockets, and the board routes power and signals between them
and out to labeled field connectors. It lives in
[`carrier/`](/hardware/pcb/carrier/) — `mini.tsx` is the board, built in
[tscircuit](https://tscircuit.com); see
[`carrier/README.md`](/hardware/pcb/carrier/README.md) for the toolchain and the
render/verify loop.

The board realizes a logical design that lives upstream of it. The source of
truth for that design is [`/hardware/wiring/`](/hardware/wiring/):

- [`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) — the ESP32 GPIO map.
- [`valve-control.mmd`](/hardware/wiring/valve-control.mmd) — the MCP23017 I²C
  banks (0x20/0x21) and the valve / reed / condenser-fan wiring.
- [`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) — the
  run-by-run field-harness schedule (connectors, conductors, AWG, lengths).
- [`power.mmd`](/hardware/wiring/power.mmd) — the power topology.

Module part numbers are in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §1.
