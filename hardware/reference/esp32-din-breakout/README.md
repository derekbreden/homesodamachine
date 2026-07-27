# ESP32-DevKitC-32E on DIN-rail breakout — reference solid

An ESP32 **B09MQJWQN2** on the breakout **B0BW4SJ5X2** — the "ESP32 Super
Breakout Board DIN Rail Mount". The Kitchen edition's MCU is the bare WROOM on the
[controller PCBA](/hardware/pcb/pcba/).

The carrier sockets the DevKitC into 2×19 @ 2.54 mm rows, has 3.81 mm screw
terminals down both edges, and **ships with a bracket for 35 mm DIN rail**.

| | mm |
|---|---|
| Footprint | **72 × 54** (estimated) |
| Mounting | native **35 mm DIN-rail clip** (PCB also has mounting holes per the silkscreen) |
| Height | ~16 (ESP32 module + sockets) |

> **Most-estimated reference.** The listing publishes pitches (2×19 @ 2.54, screw
> @ 3.81) but **not the overall footprint**, and it's a DIN-mount board — verify
> by caliper. The 4-hole pattern in the model is a placeholder; on a flat tray
> this part likely wants a short DIN-rail segment rather than 4 corner bosses.

Regenerate with `tools/cad-venv/bin/python esp32_din_breakout.py`.
