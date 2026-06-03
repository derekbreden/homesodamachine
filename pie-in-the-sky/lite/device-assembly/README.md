# Lite device assembly

The whole Lite Edition as one package: the
[reservoir-pockets](../printed-parts/reservoir-pockets/) box with the four
[valve-manifold](../../../hardware/printed-parts/valve-manifold/) tray
assemblies — source-select, bag-circuit, bib-gate, nozzle-gate — packed around
it. A layout model for fit and tube-routing review, not a printed part.

## Frame

The reservoir's frame carries through: Z+ up, X left/right, Y front/back
(depth), floor on Z=0. The reservoir's +X doorway faces the enclosure **back**
(bags load from the rear); its −X wall is the enclosure **front** and carries
both bag-spout exits low (y = ±36, z ≈ 12). The manifold therefore sits in
front of the −X face, on the same floor.

## Arrangement

Inter-tray links are tubing (the topology
[Tube Segments](../../../hardware/topology/fluid-topology.md) tables), so the
packing keeps connected trays close with their valve/Tee branches pointing up
(+Z) for the pumps, bag lines, and nozzles. The dispense path runs back to
front, so the three pump-circuit trays are flow rows marching forward from the
reservoir, each rotated 90° (long axis along Y) and centered on Y=0:

```
 back                                                      front
 ┌───────────┐  ┌────────────┐  ┌──────────┐  ┌─────────────┐
 │ reservoir │  │ bag-circuit│  │ bib-gate │  │ nozzle-gate │
 │  (bags)   │  │  bag lines │  │ + pumps  │  │  → faucet   │
 └───────────┘  └────────────┘  └──────────┘  └─────────────┘
                                  source-select along +Y side
```

- **bag-circuit** hugs the −X face, centered so it straddles both bag exits.
- **bib-gate** sits one row forward; the two pumps fill the bib ↔ nozzle gap.
- **nozzle-gate** is front-most so its nozzle outlets reach the faucet at the
  enclosure front.
- **source-select**, the largest tray and the only one that touches just
  bib-gate, lies along the +Y side in its native orientation (long axis along
  X), running the length of the rows beside bib-gate rather than widening the
  block.

Overall envelope **403 × 257 × 289 mm** (X × Y × Z), no part-to-part
collisions.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/device-assembly/device_assembly.py`
→ `device-assembly.step` (27 solids; one translucent reservoir plus the four
trays, each a distinct color). Placement constants — `GAP_RES`, `ROW_GAP`,
`COL_GAP`, the per-tray rotations and anchors — are at the top of
`device_assembly.py` and in `build()`.
