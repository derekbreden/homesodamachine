# Nozzle-gate tray (2 valves + 2 dividers)

The [fluid-topology](../../../topology/fluid-topology.md) nozzle gates: Y-D
feeds V-G, Y-G feeds V-J.

```
   V-G ┐
       ├  Y-D  ─→
   V-J ┘
       ├  Y-G  ─→
```

## Arrangement

One valve column — **V-G over V-J**, butted, ports along X, no tilt — feeds
the two **parallel Y-dividers** (Y-D, Y-G) in the center. Each divider's stem
meets its valve's inner port; the two +X outlets leave the tray to a pump and
a nozzle. Valve placement, divider orientation, and the tray builder are
shared with the [bag-circuit tray](../bag-circuit-tray/) via `build_tray`.

Origin = cell center, Z = 0 the mounting plane, ports at Z = 11.3. The four
bodies are clash-free.

## The tray

A frame plate (Z −3 → 6), **92 × 72 × 63 mm**, with one valve cradle (four
sockets + shared-row port saddles) and a central open gap holding both
dividers. Two **side walls** (±Y) rise to Z = 60 for a **63 mm stack pitch**;
the X-ends stay open for the ports and outlets.

`nozzle_gate_tray.py` → `nozzle-gate-tray.step`; `nozzle_gate_assembly.py` →
`nozzle-gate-assembly.step` (tray + valves + dividers seated). Regenerate with
`tools/cad-venv/bin/python <script>`.
