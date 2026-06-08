# Kitchen Edition enclosure contents assembly

Every internal subsystem packed together: the [cold-core foam shell](../printed-parts/cold-core/foam-shell/),
the four [valve-manifold](../printed-parts/valve-manifold/) tray assemblies
(source-select, bag-circuit, bib-gate, nozzle-gate), two
[pump-case](../printed-parts/flavor/pump-case/) assemblies, the
[compressor shroud](../cut-parts/compressor-shroud/), plus placeholder boxes
for the harvested condenser+fan (178 × 151 × 56, two dims flush with the
compressor) and the SeaFlo 22-Series diaphragm pump (75 × 60 × 175). A layout
model for fit and tube-routing review, not a printed part. The shell that
wraps these contents lives in [`../enclosure/`](../enclosure/) and the
combined view in [`../enclosure-assembly/`](../enclosure-assembly/).

## Frame

+X right, +Y back, +Z up. Origin at the lower-front-left corner of the cold
core.

## Arrangement

Layout is first-fit-decreasing on bounding-box bricks, oriented to stay inside
the [H2C left-nozzle build envelope](https://bambulab.com/en/h2c/specs)
(325 × 320 × 320 mm) with 3 mm walls.

- **Cold core** (foam shell): spans the lower-front block, X-aligned to the
  origin, on the floor.
- **Compressor shroud**: behind the cold core across the back strip, rotated
  90° about Z so its 178 mm edge runs X (133 in Y fits the 133 mm gap).
- **Source-select tray**: stands on its long edge beside the compressor, in
  the back strip.
- **Bag-circuit tray**: stands vertical in the back corner.
- **Condenser + fan**: lays above the cold core's left half, airflow axis
  along X.
- **SeaFlo pump**: above the cold core, right of the condenser column, long
  axis along Y.
- **Two pump cases**: on their long sides on top of the cold core, one in the
  front-right corner, one in the back-left.
- **Bib-gate tray**: flat, on top of the source-select tray.
- **Nozzle-gate tray**: flat, on top of the cold core in the back-center.

Inter-part links are tubing and cable — not modelled here. Contents envelope
**317.3 × 314.0 × 289.4 mm**; no solid collisions.

## Regenerate

```
tools/cad-venv/bin/python hardware/enclosure-contents-assembly/enclosure_contents_assembly.py
```

→ `enclosure-contents-assembly.step`. Per-part rotations and anchors are at
the top of `build()` in `enclosure_contents_assembly.py`.
