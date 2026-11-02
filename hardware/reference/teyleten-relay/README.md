# Teyleten 3.3 V relay module — reference solid

The opto-isolated **1-channel relay module** (`hardware/ledger/bom.md` §1, Amazon
B07XGZSYJV), used **2× per appliance**: relay #1 switches the compressor's
120 VAC hot leg, relay #2 gates 12 V to the G Ganen diaphragm pump. Both sit
on back-top's dry west wall. Each board bears on four solid edge ledges and
fastens at its two header-end holes with M3 × 8 screws and short RX-M3S×4
inserts. Rigid 3 mm rails capture the terminal-end edges. Slide each board
6.5 mm aft into the rails before fitting its two screws. The insert faces
stand 2.5 mm behind the PCB underside, leaving the pins clear during insertion. The 5 mm pilot preserves at least
4.31 mm of backing beneath the selected outer flute envelope. The [wall-mount record](../../mechanical-qualification/enclosure-above-core/wall-mount-review.json)
defines the native pin-clearance and fastener scope; actual board fit and
retention remain unqualified.
The acquired module contains a **Songle SRD-03VDC-SL-C** SPDT relay,
10 A @ 250 VAC, with a **3 V nominal coil**. The [seller's connection diagram](https://www.amazon.com/dp/B07XGZSYJV)
specifies **3.3 V at the module's VCC terminal**; `IN` is the high-level trigger.

`teyleten-relay.step` is a generated stand-in. It's a generic reseller board with
no controlled drawing, so geometry is **calipered**, not from a datasheet.

## Geometry

| | mm |
|---|---|
| PCB | **70 × 17 × 1.5** |
| Outer envelope (with can above + pins below) | **70 × 17 × 19** |
| Mounting | 4× ⌀3.2 (M3) on a **66 × 13 mm** rectangle (~2 mm corner inset) |
| Below board | pins protrude **~2 mm**; the selected wall hosts provide 2.5 mm of nominal space before the full insert body |
| Ends | 3-pole COM/NO/NC screw block on +X, VCC/GND/IN 3-pin header on −X |

In the file's frame: X = length (70), Y = width (17), Z up from the PCB
underside; origin at the footprint center, Z = 0 the PCB bottom = the standoff
plane (pins to Z = −2, relay can top near Z = +17).

Hole diameter wasn't calipered (M3 clearance assumed); the relay-can / terminal /
header blocks are representative — the **board outline, hole rectangle, and
envelope are calipered**. The frozen STEP and display payload are recorded in
[frozen-asset.json](frozen-asset.json).
