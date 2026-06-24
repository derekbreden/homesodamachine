# MCP23017 I²C GPIO expander — reference solid

Used 2× on the controller tray (0x20, 0x21). ASIN **B07P2H1NZG** is the
**Waveshare MCP23017 IO Expansion Board**.

Geometry **calipered from the physical board**. Frame matches the `module_tray`
convention: **X = length = the 38.5 mm long axis, Y = width = the 23.3 mm short
axis**, origin at the footprint centre.

| Feature | Measurement |
|---|---|
| Footprint | **38.5 (X, long) × 23.3 (Y, short)** mm |
| Mounting holes | **2 × ⌀2.0 (M2)**; 18.8 apart across Y (±9.4); both pushed to the +X (I²C) end, hole centre 2.5 from the +X edge (X = +16.75) |
| GPIO headers | **2 × 10-pin, 2.54 mm**; rows 20.0 apart across Y (±10), running along X; pin-1→pin-10 span 22.5; row offset 9.5 from the −X edge / 6.5 from the +X edge |
| I²C header | **6-pin, 2.54 mm**, running along Y on the far +X edge (2 from the edge, X = +17.25), centred in Y, between the two mounting holes; pin-1→pin-6 span 12.8 |

Pitch is the standard 2.54 mm 0.1″ header — the spans confirm it (10-pin 22.5 ≈
9 × 2.54 = 22.86; 6-pin 12.8 ≈ 5 × 2.54 = 12.7). The mounting holes sit at one
short end only, so the board mounts **cantilevered**.

Pin order (Waveshare schematic): each GPIO header is VCC, GND, then GPB7…GPB0
(one edge) / GPA0…GPA7 (the other); the I²C header is VCC, GND, SDA, SCL, INTA,
INTB. Onboard 10 kΩ I²C pull-ups, address/reset pull-ups and decoupling — the
carrier adds none of these. Address 0x20/0x21 is set by soldering the A0/A1/A2
jumpers (ships at 0x27).

Regenerate the solid with `tools/cad-venv/bin/python mcp23017.py`.
