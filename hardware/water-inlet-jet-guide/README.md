# Build the water-inlet jet

The [illustrated build guide](water-inlet-jet-guide.pdf) follows the tools and
parts in assembly order. It starts with the drilling fixture, makes the cap,
connects the welding setup, then seats, tacks and welds the cap to the elbow.

| Phase | Pages | Physical build |
|---|---|---|
| A | 2-5 | Identify the two prints, load the rod, close the jaws with two horizontal clamps, attach the base with two vertical clamps |
| B | 6-8 | Set depth, drill the handling blank, cut off and finish the cap |
| C | 9-10 | Join the gas fittings; hold the elbow and seat the cap |
| D | 11-13 | Aim at the seam, tack opposite sides and close the welded rim |
| Reference | 14 | Drawings, machine manuals and supporting procedures |

The opening map links to each phase, and PDF bookmarks identify every step.
Pages 2-3 show the issued drilling-fixture STL geometry. The blue result box
on each build page identifies the assembly carried to the next step.

The finished product is HSM-000338: one HSM-000011 drilled cap and one
purchased TAISHER elbow. Jaws, clamps, holder and gas fittings are bench tools.
The [cap drawing](../cold-core-layout/water-inlet-jet-cap-drawing.pdf) and
[welded elbow drawing](../cold-core-layout/water-inlet-jet-elbow-drawing.pdf)
control the product. The
[fabrication procedure](../assembly/water-inlet-jet.md) carries fitting
measurements, sectioned trial weld, cleaning/passivation and flow checks.

The metal body holder and separate cap restraint have no dimensioned build
package. The guide identifies this physical assembly detail explicitly.
Actual fitting compatibility, fixture grip and the small-joint weld recipe
remain subject to the procedure's physical trial; pictures do not establish
measured performance.

## Author and print

Run by hand from the repository root:

```sh
tools/cad-venv/bin/python tools/water-inlet-jet-guide/build.py
```

The generator projects the issued STL files and uses the shared Letter-guide
typography and vector primitives. It runs no appliance build, print job or
welder. [guide-sources.json](guide-sources.json) records selected numeric
inputs, file hashes and reference links. The PDF, cover and publication sidecar
are committed for the document library and both jet material records.

Print Letter, single sided, at 100% / no scaling. Pictures explain placement
and order; drawings and actual fitting measurements govern sizes.
