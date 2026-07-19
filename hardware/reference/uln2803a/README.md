# ULN2803A Darlington driver module — reference solid

Used 2× on the driver tray (`hardware/ledger/bom.md`: **B0F872W528**, 2-pc) — sink
the 10 solenoid coils + the condenser fan to GND; COM tied to 12 V for flyback.

Geometry **calipered from the physical board**. A small purple SOIC breakout
(ULN2803A SOIC-18 centred), a 9-pin 2.54 mm header along each long edge, and 2
mounting holes on the centreline. Frame matches the `module_tray` convention:
**X = length = the 24 mm axis (the 9-pin rows run along X), Y = width = the 23 mm
axis (the two rows sit at Y = ±10)**, origin at the footprint centre.

| Feature | Measurement |
|---|---|
| Footprint | **24 (X, length) × 23 (Y, width)** mm |
| Mounting holes | **2 × ⌀3.0**; 17.5 apart along X, centred in Y (on the Y = 0 centreline) → (±8.75, 0) |
| Channel headers | **2 × 9-pin, 2.54 mm**; rows 20.0 apart across Y (±10), running along X; span ≈ 20.3 (8 × 2.54), slightly +X-biased (≈1.5 from the first edge, ≈2.5 to the other) |

Pitch is the standard 2.54 mm 0.1″ header. Each row is **9 pins**: one edge is
1B…8B + GND, the other is 1C…8C + COM (IC pins 9/10 land on the 9th header pin).
Drive: GPIO → the B pins; loads' low side → the C pins; COM → +12 V; GND → board
ground. Inputs and outputs are on opposite long edges. Onboard the ULN2803A has
internal flyback diodes (to COM) and 2.7 kΩ input base resistors — the carrier
adds neither. No regulator, no I²C, no level shifter on the module.

Regenerate the solid with `tools/cad-venv/bin/python uln2803a.py`.
