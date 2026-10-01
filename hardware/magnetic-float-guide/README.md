# Magnetic float build guide

[Open the illustrated guide](magnetic-float-guide.pdf).

Published beside the other booklets on
[homesodamachine.com/drawings](https://homesodamachine.com/drawings).
The shell uses **Bambu PETG Translucent Clear (32101)**, the same filament as
the flavor reservoirs.

Sixteen Letter pages cover spool drying, H2C setup, the two ASA Aero prints,
brim removal, bench seating of the RC62, the PETG print, insertion at the pause,
roof closure and finishing. The style, type and CAD illustration conventions
match the [weld-rotator guide](../weld-rotator-guide/README.md).

The [float source and projects](../printed-parts/cold-core/magnetic-float/README.md)
provide its dimensions, prepared print files and engineering record. The guide
gives the build order and actions. Research and pressure-test procedures remain
in that engineering record.

## Print files

- [ASA Aero core and upper insert, two plates](../printed-parts/cold-core/magnetic-float/magnetic-float-aero.3mf).
- [PETG Translucent Clear shell, with insertion pause](../printed-parts/cold-core/magnetic-float/magnetic-float.3mf).

The PDF links to the public print projects and manufacturer references.

## Authoring and rebuilding

The booklet is a manually built artifact, separate from the regular CAD build.
Its HTML leaves, artwork, PDF, cover and document sidecar stand together here.
`out/` holds local page renders and is ignored. The artwork generator uses
temporary directories for intermediate STEP files.
The PDF, cover and sidecar are committed files; `render.yaml` deploys changes
to this directory, and the sidecar places the guide on the drawings shelf.

```sh
tools/cad-venv/bin/python tools/magnetic-float-guide/author.py
tools/cad-venv/bin/python tools/magnetic-float-guide/float_art.py
tools/cad-venv/bin/python tools/magnetic-float-guide/build.py
```

[author.py](../../tools/magnetic-float-guide/author.py) writes the pages and
reads dimensions/timings from the current design and slice records.
[float_art.py](../../tools/magnetic-float-guide/float_art.py) renders actual
CadQuery solids, with coral highlighting the part being added.
[build.py](../../tools/magnetic-float-guide/build.py) runs the same page renderer
as the rotator guide, checks layout overflow, binds the 16 pages with bookmarks,
and creates the cover and `.pdf.json` sidecar.

[guide-inputs.json](guide-inputs.json) records geometry/project hashes.
[art/manifest.json](art/manifest.json) records the illustrated geometry hash,
scene captions and colors. The
[recipe source record](../../tools/magnetic-float-guide/build-recipe-sources.json)
distinguishes manufacturer specifications from selected shop procedures.
