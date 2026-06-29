# Controller PCB

The controller board is a **full PCBA**: JLCPCB-assembled SMD silicon with
through-hole field connectors, no plug-in modules. It lives in
[`pcba/`](/hardware/pcb/pcba/) — `pcba.tsx` is the board, built in
[tscircuit](https://tscircuit.com); see
[`pcba/README.md`](/hardware/pcb/pcba/README.md) for the toolchain and the
render/verify loop.

`pcba.tsx` is the **canonical source of truth for the pin map** — the ESP32 GPIO
assignments and the MCP23017 I²C bank usage (which MCP / port drives which valves
+ condenser fan, and reads which reeds). Those choices are layout-driven and the
board is what gets fabricated, so the wiring diagrams are **derived views kept in
sync with the board**, not the other way round:

- [`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) — the ESP32 GPIO map
  (a view of the board).
- [`valve-control.mmd`](/hardware/wiring/valve-control.mmd) — the MCP23017 I²C
  banks (0x20/0x21) and the valve / reed / condenser-fan wiring (a view of the
  board).
- [`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) — the
  run-by-run field-harness schedule (its own concern, not derived from the pin map).
- [`power.mmd`](/hardware/wiring/power.mmd) — the power topology (likewise).

"Canonical" here means *the single source everyone derives from* — not a claim the
pins are bring-up-validated (they are provisional until the board is tested). A pin
change lands in `pcba.tsx` first, then propagates to these views.

This direction is **enforced** by a drift-check:
[`/hardware/scripts/check_pinmap.py`](/hardware/scripts/check_pinmap.py) reads the
canonical pin map from `pcba.tsx` and fails if `esp32-pinout.mmd`, the assembly
sync drivers, or the BOM disagree — a board pin missing from the docs, a sync GPIO
on the wrong role, or an electrical BOM part with no pad (the failure that left the
piezo buzzer and the MQ-6 gas sensor wired to nothing). Run `python3
hardware/scripts/check_pinmap.py` before committing a pin change or ordering the
board; it is CI-ready (exit 0 = in sync, 1 = drift).

Module part numbers are in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §1.
