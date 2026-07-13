# Controller PCB — full PCBA

A JLCPCB-assembled SMD controller board: every active part is bare silicon JLCPCB
places, every field connector specified for JLCPCB through-hole assembly. Ordered
fully assembled — no modules added, nothing hand-soldered.

`pcba.tsx` is the canonical pin map (see [`../README.md`](/hardware/pcb/README.md)).
Every render writes the JLCPCB BOM + placements (`out/pcba.{bom,cpl}.csv`) and logs
the wired count (parts carrying a JLCPCB #), so the fab package is generated and
checked on every build rather than assembled at the end.

## Building

```sh
bun render-board.ts pcba.tsx
```

regenerates the fab + 2D set: the gerbers + drill (`out/pcba.gerbers.zip`), the 2D
copper/mask views (`out/pcba.{top,bottom,overlay,…}.{svg,png}`), the routed circuit-json,
the BOM/CPL, and `picks.json`. It runs on every save and is meant to stay fast, so it does
**not** build the 3D (CadQuery is ~14 s) — iterate freely without waiting on it.

The 3D assembly (`out/pcba.glb` + the `top3d/bottom3d` face textures, composed by
[`board-3d.py`](board-3d.py) → [`board-texture.ts`](board-texture.ts)) is reconciled at
**commit** time: the [`.githooks/pre-commit`](/.githooks/pre-commit) hook rebuilds it once,
only when it's behind the gerbers and only when the commit touches this board, then stages
it — so the GLB never lands stale and no render ever waits on it. (New clones: point git at
the committed hooks with `git config core.hooksPath .githooks`.) The dev-server also rebuilds
the GLB in the background for the live `/3d` view; rebuild by hand anytime with
`tools/cad-venv/bin/python board-3d.py`. Gerber-injected silk (the LED knockout badges,
[`led-knockout.ts`](led-knockout.ts)) reaches the 3D too, since the face textures are
composed from those gerbers.

## Scope

- Active parts are silicon: ESP32 (bare WROOM), 2×MCP23017, 2×ULN2803A, DS3231,
  RS485, buzzer, 2× DRV8870 pump-motor H-bridges, K7805 buck, AMS1117 LDO. The MQ-6,
  displays, reeds, pump motors, relays, and solenoids stay off-board on the connectors.
- Single 12 V inlet; 5 V made on-board (K7805 switching buck), 3V3 by the AMS1117
  LDO (U9) off the 5 V rail.
- Field connectors through-hole, JLCPCB-assembled.
- Safety hardening is on-board: a firmware-independent gas→compressor interlock (U15, a
  74LVC1G08 AND gate that lets IO19 reach the relay only while the MQ-6 reads clear) and
  reverse-polarity + surge protection at the 12 V inlet (Q4 pass-FET, D8 TVS, D9 Vgs clamp).
- Parts map to in-stock LCSC numbers, Basic-first; `tsci import <LCSC#>` for footprints.
  Part wrappers live in `parts.tsx`.

## Files

- [`requirements.md`](requirements.md) — the board's requirements enumerated: the fab-ready
  **gates** (clearance, DFM, sourcing, …) and the manual-routing **goals** (every signal net
  hand-routed on outer copper, no vias). Each is an executable check in [`scorecard.ts`](scorecard.ts),
  printed on every build and shown at the top of the viewer's Board-checks panel — one verdict, from
  the same geometry, that no report can narrate around.
- [`esp32-scope.md`](esp32-scope.md) — what the base ESP32 uses, and the SMD block.
- [`jlcpcb-parts.md`](jlcpcb-parts.md) — the JLCPCB parts library reference: the LCSC
  part each component maps to, library type, and how each was found.
- [`plane-stitching.md`](plane-stitching.md) — how SMD pads on a plane net are auto-stitched
  to the plane (and why a stitch via must carry the net), since DRC is pour-blind and won't
  flag a floating pad.
- [`hand-routing.md`](hand-routing.md) — placing manual `pcbPath` copper correctly: the
  `route`/`routeBottom`/`routeInner` frame idiom (every waypoint derives from a pad and rides its
  part), pad shadows as through-stack walls, moving a component tighter as a one-line change, and
  the render→floor verify loop. Read before writing a `pcbPath`.
- Per-step specs (`uln2803.md`, `mcp23017.md`, …).
