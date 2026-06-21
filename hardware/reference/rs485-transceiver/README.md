# TTL-to-RS485 transceiver — reference solid

The ALMOCN auto-direction RS485 module on the controller tray
(`hardware/ledger/bom.md`: **B09998FY4X**) — base side of the SIG-7 link to the
front 4.3″ config display (the 4.3B has onboard RS485).

Geometry read off the Amazon product photos: blue PCB, 3-position screw terminal
on the RS485 end, 4-pin 2.54 mm header on the TTL end, and **2 plated mounting
holes placed diagonally** (one per end). A verified review notes the holes match
the Adafruit Feather pattern.

| | mm |
|---|---|
| Footprint | **44 × 18** (estimated from photo) |
| Mounting holes | **2**, diagonal, ⌀3.0 |
| Height | ~11 (screw terminal) |

Footprint is estimated from the photo (scaled off the screw-terminal pitch) —
verify by caliper. Regenerate with `tools/cad-venv/bin/python rs485_transceiver.py`.
