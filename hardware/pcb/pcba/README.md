# Controller PCB — full PCBA

A JLCPCB-assembled SMD controller board: every active part is bare silicon JLCPCB
places, every field connector specified for JLCPCB through-hole assembly. Ordered
fully assembled — no modules added, nothing hand-soldered.

`pcba.tsx` is the canonical pin map (see [`../README.md`](/hardware/pcb/README.md)).
Every render writes the JLCPCB BOM + placements (`out/pcba.{bom,cpl}.csv`) and logs
the wired count (parts carrying a JLCPCB #), so the fab package is generated and
checked on every build rather than assembled at the end.

## Scope

- Active parts are silicon: ESP32 (bare WROOM), 2×MCP23017, 2×ULN2803A, DS3231,
  RS485, buzzer, 2× DRV8870 pump-motor H-bridges, 2× K78xx bucks. The MQ-6, displays,
  reeds, pump motors, relays, and solenoids stay off-board on the connectors.
- Single 12 V inlet; 3V3 and 5 V both made on-board (K7803 / K7805 switching bucks).
- Field connectors through-hole, JLCPCB-assembled.
- Two deferred items: gas/compressor interlock, input protection.
- Parts map to in-stock LCSC numbers, Basic-first; `tsci import <LCSC#>` for footprints.
  SMD footprints live in `pcba_parts`.

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
- [`routing-procedure.md`](routing-procedure.md) — the complete, followable procedure for moving
  the board off the autorouter onto manual traces: own a region, evict any autorouter trace that
  interferes (related or not), get the target clean, then re-add the router one trace at a time and
  hand-route whatever it fails. Output is a routed board, not a report.
- [`autorouter-is-deterministic.md`](autorouter-is-deterministic.md) — the capacity autorouter
  is deterministic (same input → byte-identical output); the "whack-a-mole" is a deterministic
  global re-solve with zero locality, not randomness. Read before reasoning about why a trace
  moved. Proof + reproduction; the *fact* behind the procedure above.
- [`route-hints.md`](route-hints.md) — how to influence PCB routing on this board: why the
  `pcbRouteHints` prop is inert under our capacity autorouter, `<tracehint>` for soft nudges,
  and `pcbPath` / `pcbComb` for deterministic paths, vias, and layers.
- [`hand-routing.md`](hand-routing.md) — placing manual `pcbPath` copper correctly: the
  coordinate frame (points are in the `from` component's resolved center + rotation, *not* board
  coordinates), the `frame` helper (`.at` board / `.off` local), moving a component tighter as a
  one-line change, and the render→floor verify loop. Read before writing a `pcbPath`.
- Per-step specs (`uln2803.md`, `mcp23017.md`, …).
