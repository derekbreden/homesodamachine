# Controller PCB

A through-hole board the controller modules plug into on 2.54 mm headers,
routing power and signals between them and landing each field harness on a
labeled connector. The logical design it realizes — the ESP32 GPIO map, the
MCP23017 I²C banks (0x20/0x21), and the valve / reed / sensor wiring — is the
source of truth in [`/hardware/wiring/`](/hardware/wiring/)
([`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd),
[`valve-control.mmd`](/hardware/wiring/valve-control.mmd)).

## Boards

- `mini.tsx` — an ESP32 DevKitC socket; two MCP23017 (DIP-28) on a shared I²C bus
  (U2 at 0x20, U3 at 0x21); U2's GPA0-7 driving a ULN2803 (U4) that sinks eight
  12 V solenoid outputs on J_VA; U2's GPB and both of U3's banks on edge headers;
  four spare ESP32 GPIO on JE. J12 brings 12 V in for the ULN common and the
  solenoid high side; the ESP's 3V3 pin powers the MCPs. Through-hole, two layers,
  routed. ESP socket rows are 25.4 mm apart (DevKitC-32E); the pin map is the
  standard 38-pin layout.
- `render-board.ts` — `bun render-board.ts <board>.tsx [scheme]`: exports the
  Gerbers and composes the three copper views into `out/`. The dev watcher
  (`web/dev-server`) runs it on every save of a board under `pcb/`, so the
  site's Boards viewer (`/pcb`) stays current.
- `gerber-compose.ts` — composes a Gerber folder into Top (front copper + front
  silk), Bottom (back copper + back silk), and Overlay (both copper, **front silk
  only**) SVGs, aligned in one frame at the real trace widths. `SCHEMES` holds
  the colour schemes (`copper` default, `blueprint`, `ink`).
- `bottom-silk.ts` — tscircuit draws the legend on the front only; this mirrors
  it onto `B_SilkScreen` *in place* (each label stays on its own pad, glyphs flip
  left-right) so the back face reads correctly from the solder side. `render-board`
  synthesizes it into both the bottom view and the fabrication zip.
- `out/` — exactly what `render-board.ts` produces, so a save keeps it current
  and `build:check` guards it: `<board>.{top,bottom,overlay}.{svg,png}` (the
  three copper views the site shows) and `<board>.gerbers.zip` (the fabrication
  set they're built from).

## Toolchain

[tscircuit](https://tscircuit.com), run under bun (`bun install` already done in
this directory):

    bunx tsci build <board>.tsx           # eval + DRC -> dist/.../circuit.json
    bun render-board.ts <board>.tsx       # gerbers + the three copper views (svg+png), "copper"
    bun render-board.ts <board>.tsx ink   # or "blueprint"

`render-board.ts` is what fills `out/`. Other formats export on demand and are
not committed (they'd drift, since nothing regenerates them):

    bunx tsci export -f <schematic-svg|kicad_pcb|step|specctra-dsn|…> -o <path> <board>.tsx

`tsci import` pulls footprints from JLCPCB part numbers; `tsci convert` ingests
`.kicad_mod` footprints.
