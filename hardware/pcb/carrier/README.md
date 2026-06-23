# Controller PCB

A through-hole board the controller modules plug into on 2.54 mm headers,
routing power and signals between them and landing each field harness on a
labeled connector. The full connection contract — every module and net — is
[`../netlist.md`](/hardware/pcb/netlist.md).

## Boards

- `mini.tsx` — an ESP32 DevKitC socket; two MCP23017 (DIP-28) on a shared I²C bus
  (U2 at 0x20, U3 at 0x21); U2's GPA0-7 driving a ULN2803 (U4) that sinks eight
  12 V solenoid outputs on J_VA; U2's GPB and both of U3's banks on edge headers;
  four spare ESP32 GPIO on JE. J12 brings 12 V in for the ULN common and the
  solenoid high side; the ESP's 3V3 pin powers the MCPs. Through-hole, two layers,
  routed. ESP socket rows are 25.4 mm apart (DevKitC-32E); the pin map is the
  standard 38-pin layout.
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
