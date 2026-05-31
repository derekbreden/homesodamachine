# Nozzle-gate tray (2 valves + 2 Tees)

The [fluid-topology](../../../topology/fluid-topology.md) nozzle gates: a Tee
on each row carries V-G / V-J.

```
   V-G ──┬──→     Y-D run; branch ↑
   V-J ──┴──→     Y-G run; branch ↑
```

## Arrangement

One valve column — **V-G over V-J**, butted, ports along X, no tilt — meets a
**Tee** on each row. The Tee run lies along X (valve on the −X end); the +X run
end and the **branch (+Z)** leave the tray to a pump and a nozzle. Valve
placement, the Tee placer, and the tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/) via `build_tray`.

Origin = cell center, Z = 0 the mounting plane, ports at Z = 11.3. The four
bodies are clash-free.

## The tray

A frame plate (Z −3 → 6), **89 × 72 × 63 mm** (+X edge trimmed to the Tee run
port), with one valve cradle (four
sockets + shared-row port saddles) and a central open gap holding both Tees.
Two **side walls** (±Y) rise to Z = 60 for a **63 mm stack pitch**; the X-ends
stay open for the ports and outlets.

`nozzle_gate_tray.py` → `nozzle-gate-tray.step`; `nozzle_gate_assembly.py` →
`nozzle-gate-assembly.step` (tray + valves + Tees seated). Regenerate with
`tools/cad-venv/bin/python <script>`.
