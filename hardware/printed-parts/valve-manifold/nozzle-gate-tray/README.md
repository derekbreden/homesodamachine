# Nozzle-gate tray (2 valves + 4 elbows)

The [fluid-topology](/hardware/topology/fluid-topology.md) nozzle gates —
V-G / V-J — as the valve-manifold stack's top tray.

```
   V-G ●  EI down to Y-D-3 · EO aft to Nozzle A
   V-J ●  EI down to Y-G-3 · EO aft to Nozzle B
```

## Arrangement

One valve column — **V-G and V-J butted on the two channel rows**, ports along
X, no tilt — with an **elbow on each port**. The enclosure hangs the tray
**INVERTED directly over the bag-circuit tray's east bank** (the same
180°-about-Y hang the bag tray rides, sharing its X/Y origin), which lands
each inlet-elbow corner on a bag east elbow column:

* the **−X inlet elbows** keep the local up-turn, pointed straight **down** by
  the inversion — each collet coaxial over the bag tray's up-facing V-F-I /
  V-I-I collet, with a pump-discharge tee (Y-D / Y-G) standing on the shared
  vertical, one straight stub at every collet;
* the **+X outlet elbows** roll −90° to local +Y, world **aft** — facing the
  rear wall the nozzle lines (fluid-18/28) leave by.

The inversion keeps local Y, so V-G rides the −Y row (world channel A,
forward) and V-J rides +Y. Valve placement, the elbow placer + its collet
accessor (`boundary_collets`), and the tray builder are shared with the
[bag-circuit tray](/hardware/printed-parts/valve-manifold/bag-circuit-tray/)
via `build_tray`.

Origin = cell center, Z = 0 the mounting plane, ports at Z = [11.3](PORT_Z). The six
bodies are clash-free.

## The tray

A frame plate (Z [-3](TRAY_BOT_Z) → [6](TRAY_TOP_Z)), **[38](NOZ_PLATE_W) × [74](NOZ_PLATE_D) × [63](STACK_PITCH) mm**, hugging the single
−X valve column with a **solid floor**: one valve cradle (four sockets + a port
saddle). Two **side walls** (±Y) rise to Z = [60](WALL_TOP_Z) for a **[63](STACK_PITCH) mm stack pitch**;
the X-ends stay open for the ports and both elbow banks.

`nozzle_gate_tray.py` → `nozzle-gate-tray.step`; `nozzle_gate_assembly.py` →
`nozzle-gate-assembly.step` (tray + valves + elbows seated). Regenerate with
`tools/cad-venv/bin/python <script>`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/nozzle-gate-tray/nozzle_gate_tray.py`
