# MCP23017 I²C GPIO expander — reference solid

Used 2× on the controller tray (0x20, 0x21). ASIN **B07P2H1NZG** is the
**Waveshare MCP23017 IO Expansion Board**.

Footprint and hole size are from the Waveshare user manual; hole positions read
off the official photos.

| | mm |
|---|---|
| Footprint | **38 × 23** (Waveshare spec) |
| Mounting holes | **2 × ⌀2.0 (M2)**, both on ONE short end, ~19 mm apart |
| Height | ~13 (2.54 mm headers) |

Note: only the one end has holes, so the board mounts **cantilevered** — the
opposite (PH2.0-connector) end overhangs. Two 10-pin GPIO headers run along the
long edges. Source: Waveshare MCP23017 IO Expansion Board user manual. Regenerate
with `tools/cad-venv/bin/python mcp23017.py`.
