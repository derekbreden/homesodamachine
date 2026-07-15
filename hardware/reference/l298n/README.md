# L298N dual H-bridge module — reference solid

The peristaltic-pump driver on the legacy under-counter prototype and the Lite
logic tray (**B0C5JCF5RS**, [purchases.md](/hardware/ledger/purchases.md) §9) —
drives both Kamoer pumps; its onboard 78M05 also makes those builds' 5 V logic
rail. The Kitchen appliance's [controller PCBA](/hardware/pcb/pcba/) drives the
pumps with on-board DRV8870 H-bridges (U11/U12); this module serves the
prototype and the Lite only.

The classic red L298N module — footprint and hole pattern are well documented
across multiple sources; heatsink height is approximate.

| | mm |
|---|---|
| Footprint | **43 × 43** |
| Mounting holes | **4 × ⌀3.2 (M3)** on a **37 × 37** square |
| Height | ~28 (finned heatsink) |

Regenerate with `tools/cad-venv/bin/python l298n.py`.
