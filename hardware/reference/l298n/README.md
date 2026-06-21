# L298N dual H-bridge module — reference solid

The peristaltic-pump driver on the driver tray (`hardware/ledger/bom.md`:
**B0C5JCF5RS**) — drives both Kamoer pumps; its onboard 78M05 also makes the 5 V
logic rail.

The classic red L298N module — footprint and hole pattern are well documented
across multiple sources; heatsink height is approximate.

| | mm |
|---|---|
| Footprint | **43 × 43** |
| Mounting holes | **4 × ⌀3.2 (M3)** on a **37 × 37** square |
| Height | ~28 (finned heatsink) |

Regenerate with `tools/cad-venv/bin/python l298n.py`.
