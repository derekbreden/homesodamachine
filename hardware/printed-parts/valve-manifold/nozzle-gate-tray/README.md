# Nozzle-gate tray (2 valves)

The [fluid-topology](/hardware/topology/fluid-topology.md) nozzle gates —
V-G / V-J — as a bare two-valve tray.

```
   V-G ●    inner port ← Y-D (deferred) · outer port → Nozzle A
   V-J ●    inner port ← Y-G (deferred) · outer port → Nozzle B
```

## Arrangement

One valve column — **V-G and V-J butted on the two channel rows**, ports along
X, no tilt — and nothing else: the pump-discharge tees (Y-D / Y-G) that feed
the inner ports are the enclosure's to pack, and every port runs bare until
its line lands. The enclosure hangs the tray **INVERTED** (180° about Y, like
the bag-circuit tray) in the pocket east of the bag assembly, so the inner
ports face west at the bag tray's own port plane and the outer
(nozzle-outlet) ports face east. The inverted hang keeps local Y, so V-G
rides the −Y row (world channel A, forward, beside V-F) and V-J rides +Y.
Valve placement, the tray builder, and the bare-port accessor's constants are
shared with the
[bag-circuit tray](/hardware/printed-parts/valve-manifold/bag-circuit-tray/)
via `build_tray`.

Origin = cell center, Z = 0 the mounting plane, ports at Z = [11.3](PORT_Z).

## The tray

A frame plate (Z [-3](TRAY_BOT_Z) → [6](TRAY_TOP_Z)), **[38](NOZ_PLATE_W) × [74](NOZ_PLATE_D) × [61.3](STACK_PITCH) mm**, hugging the single
−X valve column with a **solid floor**: one valve cradle (four sockets + a port
saddle). Two **side walls** (±Y) rise to Z = [56.6](NOZ_WALL_TOP_Z) — level with the valve coils they
retain, since this tray seats on its floor and its wall tops face open air — for a
**[61.3](STACK_PITCH) mm stack pitch**;
the X-ends stay open for the ports.

`nozzle_gate_tray.py` → `nozzle-gate-tray.step`; `nozzle_gate_assembly.py` →
`nozzle-gate-assembly.step` (tray + valves seated). Regenerate with
`tools/cad-venv/bin/python <script>`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/nozzle-gate-tray/nozzle_gate_tray.py`
