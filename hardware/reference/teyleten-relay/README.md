# Teyleten 3.3 V relay module — reference solid

The opto-isolated **1-channel relay module** (`hardware/ledger/bom.md` §1, Amazon
B07XGZSYJV), used **2× per appliance**: relay #1 switches the compressor's
120 VAC hot leg, relay #2 gates 12 V to the SeaFlo diaphragm pump. Relay #1 bolts
through its PCB's four holes to four printed bosses on the enclosure's +X wall,
stacked over the PSU's crown; relay #2 has no station yet (see
[`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md) Open items).
SRD-style SPDT relay, 10 A @ 250 VAC; 3.3 V coil.

`teyleten-relay.step` is a generated stand-in. It's a generic reseller board with
no controlled drawing, so geometry is **calipered**, not from a datasheet.

## Geometry

| | mm |
|---|---|
| PCB | **70 × 17 × 1.5** |
| Outer envelope (with can above + pins below) | **70 × 17 × 19** |
| Mounting | 4× ⌀3.2 (M3) on a **66 × 13 mm** rectangle (~2 mm corner inset) |
| Below board | pins protrude **~2 mm** — the tray must stand the board off at least this far |
| Ends | 3-pole COM/NO/NC screw block on +X, VCC/GND/IN 3-pin header on −X |

In the file's frame: X = length (70), Y = width (17), Z up from the PCB
underside; origin at the footprint center, Z = 0 the PCB bottom = the standoff
plane (pins to Z = −2, relay can top near Z = +17).

Hole diameter wasn't calipered (M3 clearance assumed); the relay-can / terminal /
header blocks are representative — the **board outline, hole rectangle, and
envelope are calipered**. Regenerate with
`tools/cad-venv/bin/python teyleten_relay.py`.
