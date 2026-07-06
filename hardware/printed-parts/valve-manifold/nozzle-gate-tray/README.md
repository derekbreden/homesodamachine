# Nozzle-gate tray (2 valves + 2 Tees)

The [fluid-topology](/hardware/topology/fluid-topology.md) nozzle gates: a Tee
on each row carries V-G / V-J.

```
   V-G ●╲ Y-D       Y-D branch butts V-G; run swung about X
   V-J ●╲ Y-G       Y-G branch butts V-J; run swung about X
```

## Arrangement

One valve column — **V-G over V-J**, butted, ports along X, no tilt — meets a
**Tee** on each row. Each Tee plugs its **branch into its valve's inner port** —
the run no longer butts the valve — then both runs swing the same way about their
branch (X) axes (parallel), tilted **~64° from vertical** so the lower run port
stays clear of the tray underside (a mirror would overlap the two inner run
ports). An **elbow** on each valve's outer (−X nozzle-outlet) port turns that
line +Z up out of the tray. Valve placement, the Tee placers, and the tray
builder are shared with the
[bag-circuit tray](/hardware/printed-parts/valve-manifold/bag-circuit-tray/) via `build_tray`.

Origin = cell center, Z = 0 the mounting plane, ports at Z = [11.3](PORT_Z). The four
bodies are clash-free.

## The tray

A frame plate (Z [-3](TRAY_BOT_Z) → [6](TRAY_TOP_Z)), **[38](NOZ_PLATE_W) × [74](NOZ_PLATE_D) × [63](STACK_PITCH) mm**, hugging the single
−X valve column with a **solid floor**: one valve cradle (four sockets + a port
saddle). The Tees still seat in the assembly, but the tray no longer floors or
grooves them — which leaves it **identical to the [bib-gate
tray](/hardware/printed-parts/valve-manifold/bib-gate-tray/)**. Two **side
walls** (±Y) rise to Z = [60](WALL_TOP_Z) for a **[63](STACK_PITCH) mm stack pitch**; the X-ends stay
open for the ports and the outlet elbows.

`nozzle_gate_tray.py` → `nozzle-gate-tray.step`; `nozzle_gate_assembly.py` →
`nozzle-gate-assembly.step` (tray + valves + Tees seated). Regenerate with
`tools/cad-venv/bin/python <script>`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/nozzle-gate-tray/nozzle_gate_tray.py`
