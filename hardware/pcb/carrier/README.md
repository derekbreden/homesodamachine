# Controller PCB — carrier board

A single through-hole carrier board that the existing controller modules plug
into, collapsing the hand-wired module stack on the electronics shelf onto one
board. Every active part stays a known-good off-the-shelf module — the ESP32
DevKitC, the two MCP23017 breakouts, the ULN2803 driver boards, the L298N pump
driver, the relay / RTC / RS485 / buck modules — seated on 2.54 mm headers. The
board carries power and routes the signals between them, and lands every field
harness on a labeled connector. No SMD, no reflow: it is hand-solderable on the
bench.

The connection contract is [`../netlist.md`](/hardware/pcb/netlist.md). The nets
there are realized here at module-header and field-connector level instead of
bare-chip pads. The chip-level consolidated board in
[`../README.md`](/hardware/pcb/README.md) is the later cost-down; this carrier is
the buildable-now board.

## Toolchain

Design-as-code with [tscircuit](https://tscircuit.com): the board is a `.tsx`
file, and one command renders it and exports the fab / CAD / KiCad outputs — the
same "run a script, get an artifact + a PNG" loop the CAD parts of this repo
use. Everything runs under bun (`bun install` already done in this directory).

    bunx tsci build carrier.tsx                                   # eval + DRC -> dist/.../circuit.json
    bunx tsci export -f pcb-svg       -o out/carrier.pcb.svg carrier.tsx
    bunx tsci export -f schematic-svg -o out/carrier.sch.svg carrier.tsx
    bunx tsci export -f gerbers       -o out/carrier.gerbers.zip carrier.tsx   # JLCPCB
    bunx tsci export -f step          -o out/carrier.step carrier.tsx          # drop into CAD
    bunx tsci export -f kicad_pcb     -o out/carrier.kicad_pcb carrier.tsx     # open in KiCad
    bun svg2png.ts out/carrier.pcb.svg out/carrier.pcb.png                     # rasterize to view

`tsci import` also pulls real footprints from JLCPCB part numbers, and
`tsci convert` ingests `.kicad_mod` footprints — both for pinning module and
connector footprints to real parts.

## Files

- `carrier.tsx` — the carrier board. Every module socket (ESP32 DevKitC, 2×
  MCP23017, 2× ULN2803, L298N, DS3231, MP1584 buck, RS485, 2× relay) and all 16
  field connectors, with every net from `../netlist.md` realized between them.
  The floor plan is a single `PCB`/`SCH` table near the top — one place to edit.
- `spike.tsx` — toolchain proof. The board's unit cell (an ESP32 GPIO → gate
  resistor → low-side MOSFET → 12 V valve), the motif repeated ~14× on the real
  board. Built only to prove the loop end to end: code → rendered PNG →
  Gerbers + KiCad + STEP.
- `svg2png.ts` — headless SVG → PNG rasterizer (resvg, no browser).
- `out/` — rendered + exported artifacts, committed alongside the source.
  `carrier.netlist.txt` is the machine-readable connection list, verified
  net-by-net against `../netlist.md`.

## Status

v0.1 — connectivity complete and verified. Every net in `../netlist.md` is
realized at module-socket + field-connector level; the board builds clean
(connectivity DRC passes) and exports. Carrier-correct simplifications vs the
chip-level netlist: USB/CH340, the 3.3 V regulator, the relay opto/driver
stages, and the RTC coin cell all live on their modules, not the board.

Next iterations, in order:

1. **Real footprints.** Module sockets are placeholder `dip{n}` parts (hence the
   oversized provisional outline). Pin each to its actual vendor breakout via
   `tsci import` / `tsci search --kicad`, which shrinks the board toward the
   100 × 100 target.
2. **Floor plan + routing.** Settle placement against real footprints, then
   route (the autorouter struggles at this density on the placeholder layout —
   expect to grow the board, add a layer, or route the power pours by hand).
3. **Schematic cleanup.** The flat single sheet is dense; split into hierarchical
   sheets per subsystem for review.
