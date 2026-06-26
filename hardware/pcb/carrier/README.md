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
  supply (feeds the ULN commons). Through-hole, **four layers**, routed,
  128 × 99 mm. The four power nets each get a plane — top a V12 pour over the
  valve block, inner1 the 3V3 plane, inner2 the 5V plane, bottom the GND plane —
  and every power/ground pin commons to its plane at its through-hole barrel, so
  only the point-to-point signals and the I²C bus are routed, on the two outer
  layers (see Routing optimization below). ESP socket rows are 25.4 mm apart
  (DevKitC-32E); the pin map is the standard 38-pin layout.
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
  — x-mirrored, the board flipped over), and Overlay (every copper layer at once
  — the x-ray "seen through the board" view, **front silk only**, each layer its
  own hue) SVGs, at the real trace widths. On a board with inner layers it also
  emits one solo view per inner copper layer (`<board>.inner1`, `inner2`, …).
  `SCHEMES` holds the colour schemes (`copper` default, `blueprint`, `ink`).
- `bottom-silk.ts` — tscircuit draws the legend on the front only; this emits a
  throwaway board of `layer="bottom"` copies of every front silk element (same
  positions). `render-board` builds that with tscircuit and lifts its
  `B_SilkScreen`, so the back legend is rendered by the same engine — identical
  font + per-size stroke to the front, mirrored in place so it reads correctly
  from the solder side — into both the bottom view and the fabrication zip.
- `out/` — exactly what `render-board.ts` produces, so a save keeps it current
  and `build:check` guards it: `<board>.{top,bottom,overlay[,inner1,inner2,…]}.{svg,png}`
  (the copper views the site shows) and `<board>.gerbers.zip` (the fabrication
  set they're built from — `F_Cu`/`B_Cu` plus `In1_Cu`/`In2_Cu` on a 4-layer board).

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

## Routing optimization (optional)

Two levers steer the autorouter; `_clrsweep.ts` explores them — it rewrites only
the `<board>` tag, re-exports, and prints the realized copper floor + via count
per setting. `bun _clrsweep.ts`, or pass board widths: `bun _clrsweep.ts 134,160,180`.

- **`autorouter={{ traceClearance }}`** — the trace-spacing knob. A core patch
  (`patches/`) fans it to the capacity router's `defaultObstacleMargin` +
  `minTraceToPadEdgeClearance` (stock core can't set the first). It is a *soft
  target*, not a floor: the capacity mesh only re-routes a trace out of a channel
  once clearance crosses a whole-trace capacity threshold, so the realized gap
  moves in plateaus and cliffs — **sweep to find the best value, don't compute it**,
  and re-sweep after any placement change (the optimum drifts).
- **board `width` / size** — a second, independent lever: more area gives the
  router room to detour and relieves pinches `traceClearance` alone can't. With
  components at fixed coordinates a bigger board mostly adds *peripheral* room; the
  fuller "make it airy" lever is spreading the components themselves (their coords
  here). Width is the cheap first cut, placement the deep one.

### Four-layer planes

The board is 4-layer: signals on the two outer copper layers, the four power nets
each poured as a plane (3V3 on inner1, 5V on inner2, GND on bottom, V12 a bounded
pour on top). Every through-hole pin commons to its plane at the barrel, so the
power nets add no vias. Two patches (`patches/`) make this work:

- **core patch** (alongside the `traceClearance` + pour-skip plumbing): when inner
  layers carry a copperpour it strips them from the autorouter's obstacle model and
  caps the router's layer count — handing it a *2-layer (top+bottom) view*. The
  capacity router routes contiguous layers and would otherwise run signals across
  the inner planes (slicing them); this keeps them pristine copper while signals
  stay on the outer layers with normal through-vias. Auto-detects poured inner
  layers, no per-board config.
- **`@tscircuit/cli` patch** — the stock gerber exporter only emits `F_Cu`/`B_Cu`,
  silently dropping inner copper from the fabrication set. The patch emits
  `In{n}_Cu` for boards with `num_layers > 2`; `gerber-compose` then renders them.

Caveat on the metric: the "floor" `_clrsweep`/`_analyze` report is the single
tightest pad/trace gap — a weak proxy for **legibility** (can a human read the
board). For that, look at the rendered views (airy bundles, no nests) and the
typical spacing + via count, not the floor number. Compact and legible trade off;
the width×clearance grid traces that front, so you can choose the smallest board
that is still easy to inspect by eye.
