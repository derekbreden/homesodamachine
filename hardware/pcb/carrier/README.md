# Controller PCB

A through-hole board the controller modules plug into on 2.54 mm headers,
routing power and signals between them and landing each field harness on a
labeled connector. The logical design it realizes — the ESP32 GPIO map, the
MCP23017 I²C banks (0x20/0x21), and the valve / reed / sensor wiring — is
**canonical here in `mini.tsx`**; [`/hardware/wiring/`](/hardware/wiring/)
([`esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd),
[`valve-control.mmd`](/hardware/wiring/valve-control.mmd)) holds human-readable
views derived from it (canonical-but-provisional until bring-up).

## Boards

- `mini.tsx` — the carrier. An ESP32 DevKitC socket (U1), two MCP23017 (U2 at
  0x20, U3 at 0x21) and a DS3231 RTC (U6) on a shared I²C bus, two ULN2803 sink
  drivers (U4/U5), and an RS485 transceiver (U7). Each MCP's GPA0-7 drives one
  ULN, whose outputs leave on the manifold connectors J1/J2 (eight valve channels
  + a 12 V COM each; one U5 channel is the condenser fan). The MCP GPB banks read
  the reed inputs (J6/J7: reservoir A/B + carbonator). The ESP GPIO harness lands
  on J3 (faucet UART + 5 V), J4 (flow / 1-wire / backflow sensors), and J5 (L298N
  pump signals + two relay drives). RS485 bridges the ESP UART to the front config
  display: its line side exits on J9. Power is split — J8 brings in the 5 V logic
  rail (the ESP's 3V3 pin then powers the I²C devices) and J10 the 12 V valve
  supply (feeds the ULN commons). Through-hole, two layers, routed, 134 × 100 mm.
  ESP socket rows are 25.4 mm apart (DevKitC-32E); the pin map is the standard
  38-pin layout.
- `render-board.ts` — `bun render-board.ts <board>.tsx [scheme]`: exports the
  Gerbers and composes the three copper views into `out/`. The dev watcher
  (`web/dev-server`) runs it on every save of a board under `pcb/`, so the
  site's Boards viewer (`/pcb`) stays current. Single-flight per board
  (`run-lock.ts`): a new render supersedes any older run of the same board, which
  stops mid-build and logs which run took over.
- `run-lock.ts` — per-board single-flight lock for `render-board`: a starting run
  SIGTERMs an older live run of the same board; a superseded run kills its child
  and exits, naming the run that took over. `RENDER_SOURCE` (`dev-server` /
  `build-all`, else `manual`) names each run in those messages.
- `gerber-compose.ts` — composes a Gerber folder into Top (front copper + front
  silk, looking down), Bottom (back copper + back silk **as viewed from the back**
  — x-mirrored, the board flipped over), and Overlay (both copper, **front silk
  only** — the x-ray "seen through the board" view) SVGs, at the real trace
  widths. `SCHEMES` holds the colour schemes (`copper` default, `blueprint`, `ink`).
- `bottom-silk.ts` — tscircuit draws the legend on the front only; this emits a
  throwaway board of `layer="bottom"` copies of every front silk element (same
  positions). `render-board` builds that with tscircuit and lifts its
  `B_SilkScreen`, so the back legend is rendered by the same engine — identical
  font + per-size stroke to the front, mirrored in place so it reads correctly
  from the solder side — into both the bottom view and the fabrication zip.
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
