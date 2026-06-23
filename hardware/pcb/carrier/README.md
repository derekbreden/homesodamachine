# Controller PCB

A through-hole board the controller modules plug into on 2.54 mm headers,
routing power and signals between them and landing each field harness on a
labeled connector. The full connection contract — every module and net — is
[`../netlist.md`](/hardware/pcb/netlist.md).

## Boards

- `mini.tsx` — an ESP32 DevKitC socket and two MCP23017 (DIP-28) on a shared I²C
  bus (U2 at 0x20, U3 at 0x21); each MCP's GPA0-7 / GPB0-7 on an edge header,
  four spare ESP32 GPIO on JE, the ESP's 3V3 pin powering both MCPs. Through-hole,
  two layers, routed. ESP socket rows are 25.4 mm apart (DevKitC-32E); the pin map
  is the standard 38-pin layout.
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
