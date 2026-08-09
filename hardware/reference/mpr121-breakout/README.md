# HiLetgo MPR121-Breakout-V12 — reference solid

The one I²C device that is not on the controller PCBA
([`hardware/ledger/bom.md`](/hardware/ledger/bom.md) §2). Twelve charge-transfer electrode
inputs behind address **0x5A**, reached over the board's J8 loom (SIG-8,
[`wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md)).

It sits at the manifold beside the cap-sense sleeves, and that is what puts it off the
board: the sleeves' foil rings are the electrodes, and the wire between a ring and this
part is inside the measurement. SIG-8 runs the I²C the distance so the electrodes do not.

`mpr121-breakout.step` is a generated stand-in. The outline is SparkFun's MPR121 Breakout
(SEN-09695), which this board is a copy of: **1.2" × 0.8"** on 0.1" headers.

## Geometry

| | mm |
|---|---|
| PCB | **30.48 × 20.32 × 1.6** |
| Header pins, below the board | **6.0**, 0.64 square, 2.54 pitch |
| Electrode row (`ELE0`…`ELE11`) | **12 pins** on the −Y edge, spanning 27.94 |
| Bus row (`IRQ` / `SCL` / `SDA` / `3V3` / `GND` / `ADD`) | **6 pins** on the +Y edge, spanning 12.7 |
| Envelope | **30.48 × 20.32 × 7.6** |

The MPR121QR2 is a 3 × 3 × 0.65 QFN, the bus pull-ups and the VREG cap are 0603s; all of
it is flush SMD and none of it is modeled.

## Frame

PCB in the XY plane, components up (+Z), pins down (−Z), pin tips at **Z = 0** — so the
box's floor is the pins and the board rides 6 mm above it. X is the 1.2" long axis, which
both header rows run along.

**−Y is the electrode edge and +Y is the bus edge.** The two rows face opposite ways, so
which way the board is turned decides which of its two conductor bundles is the short one.

| station | what |
|---|---|
| `electrode(i)` / `electrodes()` | one of `ELE0`…`ELE11`, at its pin tip |
| `electrode_row()` | the electrode row's centre — where an electrode lead is measured from |
| `bus_pin(i)` / `bus()` | the six bus pins, and the row's centre where the J8 loom lands |
| `card_plane()` | the board's own centre on its mid-plane, for whatever holds it |

## Jumpers

Four solder jumpers on the underside, all closed from the factory: `ADD` to ground, which
is what makes the address 0x5A, and 10 kΩ pull-ups on `SDA`, `SCL` and `IRQ`. The bus's
pull-ups are R19/R20 on the controller PCBA ([`pcb/pcba/`](/hardware/pcb/pcba/)), so this
board's three sit in parallel with them on the far end of a 300 mm loom.

No regulator on the board: it wants 2.5–3.6 V, which is the `3V3` the J8 loom carries.

## Where it stands

[`enclosure_assembly.build_mpr121`](/hardware/manifold-layout/enclosure_assembly.py) seats
it between the two nozzle risers at the manifold, and the sleeves it reads are
[`printed-parts/flavor/cap-sense-sleeve/`](/hardware/printed-parts/flavor/cap-sense-sleeve/).

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/mpr121-breakout/mpr121_breakout.py
```
