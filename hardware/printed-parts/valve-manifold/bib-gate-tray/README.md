# BiB-gate tray (2 valves + 4 Tees)

The [fluid-topology](/hardware/topology/fluid-topology.md) BiB gates: V-K-A →
Y-KA → Y-C and V-K-B → Y-KB → Y-F, two Tees in series per row.

```
   V-K-A ──┬──┬──→     Y-KA · Y-C  (branches ↑)
   V-K-B ──┴──┴──→     Y-KB · Y-F  (branches ↑)
```

## Arrangement

One valve column — **V-K-A over V-K-B**, butted, ports along X, no tilt —
feeds a near-valve **Tee** (Y-KA / Y-KB) on each row; a second **Tee** (Y-C /
Y-F) butts against its +X run port. All four Tee runs lie along X and their
**branches rise (+Z)** — the near-valve branches are the V-C / V-D inlets from
a source-select tray stacked above; the far branches and +X run ends leave the
tray to a pump and the channel-select line. An **elbow** on each valve's outer
(−X BiB-inlet) port turns that line +Z up out of the tray. Valve placement, the
Tee placer, and the tray builder are shared with the [bag-circuit tray](/hardware/printed-parts/valve-manifold/bag-circuit-tray/).

Origin = cell center, Z = 0 the mounting plane, ports at Z = [11.3](PORT_Z). The six
bodies are clash-free.

## The tray

A frame plate (Z [-3](TRAY_BOT_Z) → [6](TRAY_TOP_Z)), **[37](BIB_PLATE_W) × [74](BIB_PLATE_D) × [63](STACK_PITCH) mm**, hugging the single
−X valve column with a **solid floor**: one valve cradle (four sockets + a port
saddle). The Tees still seat in the assembly, but the tray no longer floors or
grooves them — which leaves it **identical to the [nozzle-gate
tray](/hardware/printed-parts/valve-manifold/nozzle-gate-tray/)**. Two **side
walls** (±Y) rise to Z = [60](WALL_TOP_Z) for a **[63](STACK_PITCH) mm stack pitch**; the X-ends stay
open for the ports and the outlet elbows.

`bib_gate_tray.py` → `bib-gate-tray.step`; `bib_gate_assembly.py` →
`bib-gate-assembly.step` (tray + valves + Tees seated). Regenerate with
`tools/cad-venv/bin/python <script>`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/bib-gate-tray/bib_gate_tray.py`
