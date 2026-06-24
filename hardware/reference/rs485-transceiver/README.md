# ALMOCN TTL-to-RS485 transceiver — reference solid

Base side of the SIG-7 link to the front 4.3″ config display (`hardware/ledger/bom.md`:
**B09998FY4X**). The 4.3B carries its own RS485 transceiver at the far end.

Geometry **calipered from the physical board**. Frame matches the `module_tray`
convention: **X = length = the 51.85 mm long axis, Y = width = the 22.75 mm short
axis**, origin at the footprint centre.

| Feature | Measurement |
|---|---|
| Footprint | **51.85 (X, length) × 22.75 (Y, width)** mm (published nominal 52 × 23) |
| Mounting holes | **4 × ⌀2.0 (M2)** in the corners at (±23.8, ±9.5); c-t-c 47.6 along X, 19.0 along Y (matches the Adafruit Feather pattern) |
| Screw terminal | **3-pos 5.08 mm** (A+ / B− / Earth) at the −X short end, along Y |
| TTL header | **4-pin 2.54 mm** (VCC / TXD / RXD / GND) at the +X short end, along Y |

**Electrical.** Auto-direction (**no DE/RE pin** — Tx/Rx switching is detected on
the TTL Tx line, saving a GPIO). VCC range is 3.0–30 V; on the carrier it runs at
**3.3 V** so its receiver output can't over-volt the ESP32's input-only GPIO 34.
An onboard **120 Ω** termination is present but **OFF by default** — enabled only
by shorting the R0 pads at the bus end, so the carrier adds no termination. The
third line terminal is **"Earth"** — an isolated chassis/shield reference, **not
the chip GND**; leave it isolated unless the bus needs a common. **No pin carries
12 V.** (The 4.3B display's 12 V is a separate bus feed to its own screw input.)

> Reliability note: the unmarked clone driver IC sits at the low edge of its
> rating at 3.3 V — part-to-part variability is reported. 3.3 V is the correct,
> in-spec choice; just be aware.

Regenerate the solid with `tools/cad-venv/bin/python rs485_transceiver.py`.
