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

- [`esp32-scope.md`](esp32-scope.md) — what the base ESP32 uses, and the SMD block.
- [`jlcpcb-parts.md`](jlcpcb-parts.md) — the JLCPCB parts library reference: the LCSC
  part each component maps to, library type, and how each was found.
- [`plane-stitching.md`](plane-stitching.md) — how SMD pads on a plane net are auto-stitched
  to the plane (and why a stitch via must carry the net), since DRC is pour-blind and won't
  flag a floating pad.
- [`route-hints.md`](route-hints.md) — how to influence PCB routing on this board: why the
  `pcbRouteHints` prop is inert under our capacity autorouter, `<tracehint>` for soft nudges,
  and `pcbPath` / `pcbFan` for deterministic paths, vias, and layers.
- Per-step specs (`uln2803.md`, `mcp23017.md`, …).
