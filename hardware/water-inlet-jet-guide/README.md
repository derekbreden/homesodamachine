# Water-inlet jet drilling and welding guide

[The illustrated bench guide](water-inlet-jet-guide.pdf) follows the finished
316 cap from a clamped handling blank through drilling, cutting, elbow fit,
purging, welding, root inspection, cleaning and flow checking.

The largest setup and action pictures are on the drilling and welding pages.
The [cap engineering drawing](../cold-core-layout/water-inlet-jet-cap-drawing.pdf)
controls the component; [the fabrication procedure](../assembly/water-inlet-jet.md)
holds its assembly requirements and qualification scope.

| Pages | Work at the bench |
|---|---|
| 1-2 | Operation map, bench kit and actual fitting measurements |
| 3-5 | Four-clamp setup, stopped-spindle alignment, tip depth and drilling motion |
| 6 | Cut the slice; finish and inspect both bore ends |
| 7 | Separate argon purge branch and torch shielding |
| 8-10 | Metal workholding, gun aim, opposing tacks and circumferential travel |
| 11 | Sectioned-root comparison and coupon examination |
| 12 | Clean, passivate, flow-check and install at Port 2 |
| 13-14 | Coupon record, primary references and picture key |

The cap dimensions are defined. Actual elbow fit, the small-joint numerical
weld recipe and flow acceptance still require the recorded trial. The four-tack
and opposite-arc pictures describe the coupon handling plan; the accepted
record identifies the sequence used for production. Fitting bores, clamp
frames and the illustrated fusion zone are schematics rather than measured
catalog geometry or a predicted weld section.

## Author and print

Run by hand from the repository root:

```sh
tools/cad-venv/bin/python tools/water-inlet-jet-guide/build.py
```

The generator uses the shared Letter-guide typography and vector primitives.
It imports no CAD and runs no appliance build, printer or welder.
[guide-sources.json](guide-sources.json) records the selected numeric inputs,
source hashes, reference links and review scope. The PDF, cover and publication
sidecar are committed for the document library and material page.

Print Letter, single sided, at 100% / no scaling. The pictures explain the
setup; the engineering drawing and actual fit measurements govern sizes.
