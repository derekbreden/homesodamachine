# Controller PCB — carrier board

A through-hole carrier board the controller modules plug into on 2.54 mm
headers — the ESP32 DevKitC, the two MCP23017 breakouts, the ULN2803 driver
boards, the L298N pump driver, and the relay / RTC / RS485 / buck modules. It
carries power, routes the signals between them, and lands every field harness on
a labeled connector. The connection contract is
[`../netlist.md`](/hardware/pcb/netlist.md).

## Boards

- `mini.tsx` — an ESP32 DevKitC socket and an MCP23017 (DIP-28) over I²C, with
  GPA0-7, GPB0-7, and four spare ESP32 GPIO on edge headers; the ESP's 3V3 pin
  powers the MCP. Through-hole, two layers, routed. The ESP socket rows are
  22.86 mm apart and the pin map is the standard DevKitC-32E 38-pin layout —
  both unconfirmed against the physical module.
- `carrier.tsx` — 11 module sockets and the 16 field connectors, realizing every
  net in `../netlist.md`. Module sockets are placeholder `dip{n}` footprints; the
  outline is provisional. Builds; not routed.
- `spike.tsx` — one ESP32 GPIO → gate resistor → low-side MOSFET → 12 V valve.
  Two layers, routed.
- `svg2png.ts` — SVG → PNG (resvg, headless).
- `out/` — rendered and exported artifacts.

## Toolchain

[tscircuit](https://tscircuit.com), run under bun (`bun install` already done in
this directory):

    bunx tsci build <board>.tsx                                    # eval + DRC -> dist/.../circuit.json
    bunx tsci export -f pcb-svg       -o out/<board>.pcb.svg <board>.tsx
    bunx tsci export -f schematic-svg -o out/<board>.sch.svg <board>.tsx
    bunx tsci export -f gerbers       -o out/<board>.gerbers.zip <board>.tsx
    bunx tsci export -f kicad_pcb     -o out/<board>.kicad_pcb <board>.tsx
    bunx tsci export -f step          -o out/<board>.step <board>.tsx
    bun svg2png.ts out/<board>.pcb.svg out/<board>.pcb.png

`tsci import` pulls footprints from JLCPCB part numbers; `tsci convert` ingests
`.kicad_mod` footprints.
