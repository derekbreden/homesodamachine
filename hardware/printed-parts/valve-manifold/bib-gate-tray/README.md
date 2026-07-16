# BiB-gate tray (2 valves + 4 Tees)

> **De-scoped from the shipping product.** The bag-in-box path is not part of the current single-configuration appliance — the shipping [`bom.md`](/hardware/ledger/bom.md) §8 and the [fluid topology](/hardware/topology/fluid-topology.md) carry the 10-valve, hopper-only manifold. This tray (V-K-A/V-K-B gates + the Y-KA/Y-KB merge Tees) is retained here for a possible future commercial/office SKU; the board keeps its two now-unused MANIFOLD-B outputs.

The bag-in-box (BiB) gates: V-K-A →
Y-KA → Y-C and V-K-B → Y-KB → Y-F, a near-valve Tee and a far Tee per row.

```
   V-K-A ──┬─ Y-KA ╲Y-C     near Tee: run along X, branch ↑;
   V-K-B ──┴─ Y-KB ╲Y-F     far Tee: branch ↓ butting that riser, run at 45°
```

## Arrangement

One valve column — **V-K-A over V-K-B**, butted, ports along X, no tilt —
feeds a near-valve **Tee** (Y-KA / Y-KB) on each row: the valve butts its −X run
end and its **branch rises (+Z)** to a butt point at Z = 31.366. The row's far
**Tee** (Y-C / Y-F) hangs **branch-down on that riser** — its branch port butts
the near Tee's branch top — with its run swung 45° about Z, up clear of the tray.
An **elbow** on each valve's outer (−X BiB-inlet) port turns that line +Z up out
of the tray. Valve placement, the Tee placers, and the tray builder are shared
with the [bag-circuit tray](/hardware/printed-parts/valve-manifold/bag-circuit-tray/).

Origin = cell center, Z = 0 the mounting plane, ports at Z = [11.3](PORT_Z). The six
bodies are clash-free.

## The tray

A frame plate (Z [-3](TRAY_BOT_Z) → [6](TRAY_TOP_Z)), **[38](BIB_PLATE_W) × [74](BIB_PLATE_D) × [63](STACK_PITCH) mm**, hugging the single
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
