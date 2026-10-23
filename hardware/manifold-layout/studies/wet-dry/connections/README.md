# Local electrical connections

This library supplies the selected installed connector bodies and local wire
departures for the wet/dry enclosure study. It contains ten mated JST housings
and twenty lead groups: ten JST groups, the two J10 supply leads, four Mean Well
leads and four relay contact leads. Complete harness routes are outside this
library's scope. J8's physical header is populated; its expansion cable is
unused and its mating envelope is optional.

`model.py` reads only frozen JSON and NPZ files in this directory. Its source
frames match the associated component meshes identified in
[`source-evidence.json`](source-evidence.json).

```python
geometries.update(connections.library())
scene["instances"].extend(connections.instances(layout["instances"]))
scene["mates"].extend(connections.mates())
datums = connections.world_datums(layout["instances"])
```

`instances(..., probes=True)` adds ten axial housing sweeps and fourteen
screwdriver probes. `optional_j8=True` adds the unused expansion plug/lead
envelopes. `owners={"pcba"}` limits instance generation to a focused PCB study.
Layouts may be an instance list, its containing JSON object, or a name-to-pose
mapping using `translation` or `translation_mm`.

`world_datums` returns all JST cavity exits, separate J10 wire mouths and screw
heads, and all six physical PSU poles plus all six relay contact poles. Its
`logical` map supplies the terminal record's conductor `point`/`outward` and
separate `screw_head_mm`/`screw_axis`. It selects one inner screw on each duplicate
DC bus; unused physical poles remain in the physical datum table. Relay wire
entries face the block's end; their screw heads face the board normal.

The [official JST catalog](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf)
establishes 2.5 mm pitch and a 9.8 mm mated height above the PCB top. Housings use
the published width/depth and include the small bottom projection. Imported
wafer geometry verifies straight pins and 7 mm shrouds normal to the board.
The local 1.7 mm wire model uses a 3 mm straight exit, a 4 mm centerline bend and
an 8 mm tangent toward the nearest board edge. The 6 mm housing pull is a stated
geometric allowance, not a manufacturer extraction-stroke specification.

The [Mean Well drawing](https://www.meanwell.com/Upload/PDF/IRM-90/IRM-90-spec.pdf)
establishes the physical 7.5 mm AC pair pitch and 5 mm DC four-pole pitch.
Block heights/insets and relay side-entry mouth positions remain representative
estimates. Selected AC leads turn upward with 2 mm straight exit, a 5 mm
centerline radius and an 8 mm tangent. J10, PSU DC and relay contact departures
use the source wire's 3 mm insulation allowance. Tool probes represent a 3.5 mm
diameter working shaft, without a hand or handle envelope.

Installed connector and wire clearance uses the closed roof. Normal mating and
tool access removes the roof; the silicone funnel is removed only for a path
that needs it. Full normal PSU/relay terminal access lifts the single PCB
carrier. J10 remains accessible in place with the roof removed.

[`selected-audit.json`](selected-audit.json) records mutual lead/plug/access
queries and service conditions. [`arrangement-audit.json`](arrangement-audit.json)
records the selected surrounding-body and access results. The raw relay tool
contacts with PCB-connected J9 leads are retained alongside the carrier-lift
service interpretation. The twenty installed lead groups have no mutual wire
or other-plug collision; the axial housing sweeps clear neighboring local leads.

`rebuild.py` manually regenerates nominal meshes from the frozen
[`mesh-recipes.json`](mesh-recipes.json). It needs NumPy/trimesh, performs no CAD
job, and imports no production source. It is separate from normal study builds.
The PDFs in `sources/`, captured source hashes and original interface metadata
preserve the evidence and its estimate limits.
