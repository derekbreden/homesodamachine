# ULN2803A Darlington driver module — reference solid

Used 2× on the driver tray (`hardware/ledger/bom.md`: **B0F872W528**, 2-pc) — sink
the 12 solenoid coils + the condenser fan to GND; COM tied to 12 V for flyback.

Geometry read off the Amazon photos: a **small purple SOIC breakout** (ULN2803A
SOIC-18 centred), a 9-pin 2.54 mm header along each long edge (1B-8B+GND /
1C-8C+COM), and **2 plated mounting holes placed diagonally**. This is the
compact pin-header breakout, not a screw-terminal slab.

| | mm |
|---|---|
| Footprint | **31 × 22** (estimated from photo) |
| Mounting holes | **2**, diagonal, ⌀3.0 |
| Height | ~12 (2.54 mm headers) |

Footprint is estimated from the photo — verify by caliper. Regenerate with
`tools/cad-venv/bin/python uln2803a.py`.
