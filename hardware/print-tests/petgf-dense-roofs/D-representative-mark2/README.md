# D contact treatment on representative supported surfaces

This plate applies D's dense interface and requested contact distance to the
approved Industrial faucet base, the enclosure handhold arch and the holed pad.
Each crop retains the actual contact surface and its surrounding wall stock.

| Specimen | Retained geometry |
| --- | --- |
| FD | The complete lower faucet width, original tilted bed contact and first lower rounded transition. |
| HD | The handhold underside, curved opening end, open seam end and wall junction. |
| PD | The square pad underside, hole mouth, blind pilot and surrounding wall root. |

The faucet uses the frozen approved production base in its manufacturing pose.
The crop ends above the first lower curve; it preserves the original starting
contact and support rise. The faucet has no raised label and is recognizable
by its full round foot. HD and PD carry raised labels on their cut caps.
FD is at the front, PD at the rear left and HD at the rear right, facing Mark2.

This plate tests native tree interfaces on the lower faucet section. Its source
is the approved model; the separate production fin meshes and their local
blockers are outside this tree-interface experiment. The automatic exterior
tree recipe follows the faucet's saved Default style. The rear arch and pump
pad use Tree Slim. Faucet and arch bodies retain ordinary sparse infill; the
pad retains solid stock. D's interface spacing, count, requested top distance,
bridge flow, bridge speed and local cooling treatment are shared.

[`samples.json`](samples.json) owns the crop bounds and object settings.
[`preparation.json`](preparation.json) binds the source meshes and positions.
The native slice and estimate are in [`ready/`](ready/). The verification record
retains the actual support bodies, contact planes, bead envelope and Mark2 trim.
Physical finish and support removal require their own results.

Mark2's accepted job, selected send options and startup reading are in
[`mark2/`](mark2/). The companion [rail pair](../rail-fit-30/) prints on Mark1,
with each machine retaining its own trim and external-spool mapping.

## Reproduce

`samples.rs` authors the crops in Rust on the installed geometry engine.
`prepare.py` uses the existing native plate writer and retains Mark2's own
filament mapping and trim. Temporary conversions and slice output stay in the
run directory; finished meshes and machine files remain here.

```sh
tools/cad-venv/bin/python hardware/print-tests/petgf-dense-roofs/D-representative-mark2/prepare.py --geometry --slice
```

The generator submits no printer job and adds no ordinary build or commit check.
