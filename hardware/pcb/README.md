# Controller PCB

The controller board is a **through-hole carrier**: the controller modules plug
into 2.54 mm header sockets, and the board routes power and signals between them
and out to labeled field connectors. It lives in
[`carrier/`](/hardware/pcb/carrier/) — `mini.tsx` is the board, built in
[tscircuit](https://tscircuit.com); see
[`carrier/README.md`](/hardware/pcb/carrier/README.md) for the toolchain and the
render/verify loop.

`mini.tsx` is the **canonical source of truth for the pin map** — the ESP32 GPIO
assignments and the MCP23017 I²C bank usage (which MCP / port drives which valves
+ condenser fan, and reads which reeds). Those choices are layout-driven and the
board is what gets fabricated, so the wiring diagrams are **derived views kept in
sync with the board**, not the other way round:

- [`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) — the ESP32 GPIO map
  (a view of the carrier).
- [`valve-control.mmd`](/hardware/wiring/valve-control.mmd) — the MCP23017 I²C
  banks (0x20/0x21) and the valve / reed / condenser-fan wiring (a view of the
  carrier).
- [`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) — the
  run-by-run field-harness schedule (its own concern, not derived from the pin map).
- [`power.mmd`](/hardware/wiring/power.mmd) — the power topology (likewise).

"Canonical" here means *the single source everyone derives from* — not a claim the
pins are bring-up-validated (they are provisional until the board is tested). A pin
change lands in `mini.tsx` first, then propagates to these views.

Module part numbers are in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §1.
