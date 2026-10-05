# Gun positioner assembly guide

[Assembly guide](gun-positioner-guide.pdf) · [Actual-size drilling templates](gun-positioner-drill-templates.pdf) · [Plan and Prime purchases](../gun-positioner/README.md)

The shop guide builds one six-axis screw positioner and two retracting camera
stations. Every assembly operation has a picture, required parts, tools,
sequence and a ready check with its failure remedy. Its scope is loaded dry
commissioning: nominal command spacing does not establish attained micrometer
motion or live weld tracking.

Print the book single-sided on Letter at actual size. Print only the required
template tiles at 100%, measure their 50 mm bars before drilling and align the
red registration crosses. The bar must be within ±0.25 mm. Assembly pictures
are illustrations; the templates, part registries and STEP files set dimensions.
Formed angles, hubs and tube spacers use their specific fabrication notes and
three-dimensional STEP geometry.

The governing interfaces are the [mechanical parts and requirements](../printed-parts/fixtures/gun-positioner/),
[camera fabrication manifest](../printed-parts/fixtures/gun-positioner-observation/manifest.json),
[controller mount manifest](../gun-positioner/mounting/manifest.json),
[wiring manifest](../gun-positioner/wiring-manifest.json),
[controller instructions](../gun-positioner/control.md) and
[commissioning procedures](../gun-positioner/commissioning.md). Keep the complete
kit together so its part IDs, firmware and guide agree.

The [page manifest](page-manifest.json), [CAD scene receipt](art/scene-receipt.json),
[schematic receipt](art/schematic-receipt.json), [template receipt](drill-template-receipt.json)
and [bound source receipt](source-receipt.json) record input and output hashes.
The [visual review receipt](visual-qa-receipt.json) records the final PDF and
template page checks separately from physical hardware qualification.
The PDF includes chapter and operation bookmarks. Its page text and wiring
figures remain vectors; the mechanical pictures are renders of the actual CAD
builders, with catalog and gun envelopes identified separately.

Guide generation uses the repository's CadQuery environment and browser renderer.
Run these commands from the repository root after the governing files are stable:

```sh
tools/cad-venv/bin/python tools/gun-positioner-guide/templates.py
tools/cad-venv/bin/python tools/gun-positioner-guide/art.py --all
tools/cad-venv/bin/python tools/gun-positioner-guide/clamp_art.py
tools/cad-venv/bin/python tools/gun-positioner-guide/schematic_detail.py
tools/cad-venv/bin/python tools/gun-positioner-guide/author.py
tools/cad-venv/bin/python tools/gun-positioner-guide/build.py
tools/cad-venv/bin/python tools/gun-positioner-guide/qa.py --render
```

The build refuses missing pictures, stale source hashes, mixed template revisions,
noncontiguous leaves and PDF pages with the wrong Letter dimensions. Rendered
review files live in the ignored `out/` directory. A final visual pass checks
every printed page and template tile after generation.
After inspecting all rendered pages and critical full-page views, record that
completed review with `tools/cad-venv/bin/python tools/gun-positioner-guide/qa.py --record`.
