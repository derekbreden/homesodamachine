# PCB tools

`hsm-pcb` builds the detailed populated board and answers optional copper and silkscreen queries.
The PCB build runs when preparing a board order, outside the print build.

| Command | Purpose |
| --- | --- |
| `model` | Instance vendor models at the circuit's placements and build the drilled board |
| `harness-crops` | Crop the published J2 and J13 models and fabrication textures for the bench guides |
| `orientation` | Compare each placed vendor model with its courtyard or pad envelope |
| `trace-check` | Report foreign trace, pad and pad-shadow approaches to authored copper |
| `topreach` | Find connected top-layer centerline space between named pads |
| `plot-region` | Draw pads, routes, vias and pin names for a board region |
| `silk-audit` | Measure the installed Gerber font's ink against copper and other ink |
| `run-lock` | Hold the board render's mutex for its parent process |

`model` reads routed circuit JSON, or asks the installed tscircuit exporter for it.
The [supplier source pack](../../../hardware/pcb/pcba/vendor-models.json) binds
reviewed detailed mesh prototypes, normals and colors to the supplier STEP hashes.
New models can use the supplier's native OBJ geometry. `--step` places the original
vendor B-rep geometry and the drilled native board in board coordinates. Downloads
use the board's existing model cache. `--out-dir` selects an isolated destination
for a requested comparison. The normal destination also receives the existing
Bun board-texture pass.

`harness-crops [J2 J13]` reads the released PCBA GLB, circuit placements and
fabrication PNGs. It keeps each connector's hierarchy and materials, clips board
triangles, and embeds the original fabrication pixels with their crop UVs.
The source hashes must match `hardware/cad-artifacts.json`. `--source-dir`,
`--out-dir` and `--release` select explicit inputs and destinations for a requested
comparison. The generated provenance carries the connector pins and bench pose.

`plot-region` rasterizes its board-coordinate SVG with `rsvg-convert`.
`silk-audit` reads the exact stroke font from the installed Gerber exporter.
`topreach` uses the authored board outline for its centerline raster.
These tools add no automatic check to rendering, the print build or commits.
