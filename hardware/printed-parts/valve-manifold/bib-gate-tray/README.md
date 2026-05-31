# BiB-gate tray (2 valves + 4 dividers)

The [fluid-topology](../../../topology/fluid-topology.md) BiB gates: V-K-A →
Y-KA → Y-C, V-K-B → Y-KB → Y-F.

```
   V-K-A ┐
         ├  Y-KA ─ Y-C ─→
   V-K-B ┘
         ├  Y-KB ─ Y-F ─→
```

## Arrangement

One valve column — **V-K-A over V-K-B**, butted, ports along X, no tilt —
feeds the center dividers (Y-KA, Y-KB); each of those feeds a **+X divider**
(Y-C, Y-F) in series, sitting where a second valve column would. The +X
dividers' outlets leave the tray to a pump and the channel-select line. Valve
placement, divider orientation, and the tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/) via `build_tray`.

Origin = cell center, Z = 0 the mounting plane, ports at Z = 11.3. The six
bodies are clash-free.

## The tray

A frame plate (Z −3 → 6), **140 × 72 × 63 mm**, reaching far enough on +X to
clear Y-C / Y-F. One valve cradle (four sockets + shared-row port saddles) and
a central open gap holding all four dividers. Two **side walls** (±Y) rise to
Z = 60 for a **63 mm stack pitch**; the X-ends stay open for the ports and
outlets.

`bib_gate_tray.py` → `bib-gate-tray.step`; `bib_gate_assembly.py` →
`bib-gate-assembly.step` (tray + valves + dividers seated). Regenerate with
`tools/cad-venv/bin/python <script>`.
