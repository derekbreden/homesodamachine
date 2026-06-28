# Controller PCB — SMD / full-PCBA successor

A JLCPCB-assembled successor to the through-hole carrier
([`../carrier/`](/hardware/pcb/carrier/)): the same logical design and pin map, every
plug-in module as bare SMD silicon JLCPCB places, every field connector specified for
JLCPCB through-hole assembly. Ordered fully assembled — no modules added, nothing
hand-soldered.

The carrier ([`../carrier/mini.tsx`](/hardware/pcb/carrier/mini.tsx)) stays the
canonical pin map and is unchanged. The PCBA board starts as a copy of it and converts
one module at a time. Each step is an in-place swap — one module's socket becomes its
SMD equivalent in the same silk rectangle, same position, same nets — rendered and read
against the carrier. Fabrication is once, after every module is converted and the board
passes assembly DFM. Every render also writes the JLCPCB BOM + placements
(`out/pcba.{bom,cpl}.csv`) and logs the wired count (parts carrying a JLCPCB #), so the fab
package is generated and checked from step 1 rather than assembled at the end.

## Scope

- On-carrier modules become silicon: ESP32, 2×MCP23017, 2×ULN2803A, DS3231, RS485,
  buzzer. The L298N, MQ-6, displays, reeds, pumps, and solenoids stay off-board on the
  connectors.
- Split 12 V / 5 V inlets. 3V3 made on-board (one LDO); 5 V external.
- Field connectors through-hole, JLCPCB-assembled.
- Carries the carrier's two deferred items (gas/compressor interlock, input protection).
- Parts map to in-stock LCSC numbers, Basic-first; `tsci import <LCSC#>` for footprints.
  The render / route / silk pipeline and the four patches come from the carrier; SMD
  footprints live in `pcba_parts`.

## Files

- [`conversion-plan.md`](conversion-plan.md) — the modules in order, what each becomes,
  what's involved.
- [`esp32-scope.md`](esp32-scope.md) — what the base ESP32 uses, and the SMD block.
- [`jlcpcb-parts.md`](jlcpcb-parts.md) — the JLCPCB parts library reference: the LCSC
  part each component maps to, library type, and how each was found. Grows per step.
- [`plane-stitching.md`](plane-stitching.md) — how SMD pads on a plane net are auto-stitched
  to the plane (and why a stitch via must carry the net), since DRC is pour-blind and won't
  flag a floating pad.
- Per-step specs (`uln2803.md`, `mcp23017.md`, …) land here as steps are taken.
