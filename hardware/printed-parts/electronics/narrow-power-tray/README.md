# Narrow power tray

A **wide-and-shallow** variant of the [power tray](/hardware/printed-parts/electronics/power-tray/)
for a Zone-B slot that is broad but not deep. Same parts, same retention idioms
(heat-set M3 bosses for the PSU and relay, angled press-fit slots for the Wagos,
a heat-set ground-stud boss for the ring-terminal stack) — only the layout
differs:

- **Mean Well PSU turned 90°** so its 109 mm length runs along **X** (the wide
  axis) instead of Y.
- **Relay #1 and the Wago column pack flush** to the PSU's right.
- **Ground ring-stack moved** into the open space above the PSU.

Net footprint ≈ **151 × 74 mm** (vs the power tray's ≈ 94 × 111) — more X, less Y.

```
   ┌──────────────────────────────────────────────┐
   │   ○(GND)                                       │
   │            ┌────────────────┐  ║relay║ ◹◹◹     │
   │  ○      ○  │   PSU (IRM-90)  │  ║ #1  ║ Wagos   │
   │            │   turned 90°    │  ║     ║ (flush  │
   │  ○      ○  └────────────────┘  ║     ║  column)│
   └──────────────────────────────────────────────┘
   ○ = M3 heat-set boss
```

## Shared engine

The geometry is built by `power_tray.build_tray(L)` from a `Layout` (component
centres + Z rotations). This module only defines the narrow `Layout` and calls
the shared engine; the retention/feature details live in
[`power_tray.py`](/hardware/printed-parts/electronics/power-tray/power_tray.py).

`narrow_power_tray.py` → `narrow-power-tray.step`; `narrow_power_assembly.py` →
`narrow-power-assembly.step` (tray + parts seated). Regenerate with
`tools/cad-venv/bin/python <script>`.
