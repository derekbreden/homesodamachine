# ASA Aero magnetic float build guide

[Open the illustrated build guide](magnetic-float-guide.pdf), published on
[the drawings shelf](https://homesodamachine.com/drawings).

Thirteen Letter pages cover the one-piece ASA Aero float, external dry-feed
setup, native slice review, RC62 insertion at the pause, roof closure, inspection,
installation and liquid reed calibration. The cobalt, white and ice palette
matches the website and owner guides. CAD illustrations show the current
36 × 28 mm body and ring magnet.

The [float record](../printed-parts/cold-core/magnetic-float/all-aero/README.md),
[physical evidence](../printed-parts/cold-core/magnetic-float/all-aero/physical-observations.json)
and [installation specification](../printed-parts/cold-core/magnetic-float/all-aero/installation.md)
hold the engineering detail. The guide identifies the accepted insertion evidence
and the properties still requiring qualification. The current v2 geometry needs
a fresh native slice review before its expected insertion layers can be used.

## Print files

- [Current float STL](../printed-parts/cold-core/magnetic-float/all-aero/float-aero.stl).
- [Design and process record](../printed-parts/cold-core/magnetic-float/all-aero/design.json).
- [Native slice preparation](../printed-parts/cold-core/magnetic-float/all-aero/prepare_print.py).

The preparation script writes a separate current-revision project. It does not
submit a print. The retained `all-aero-float.3mf` is identified v1 print evidence;
its reviewed pause layers apply to that identified project.

## Authoring and rebuilding

This booklet is rebuilt by hand. Its HTML leaves, artwork, PDF, cover and document
sidecar live together here. `out/` holds ignored page renders. The committed PDF,
cover and sidecar deploy through `render.yaml`; the sidecar lists the guide on
the drawings shelf.

```sh
tools/cad-venv/bin/python tools/magnetic-float-guide/author.py
tools/cad-venv/bin/python tools/magnetic-float-guide/float_art.py
tools/cad-venv/bin/python tools/magnetic-float-guide/build.py
```

[author.py](../../tools/magnetic-float-guide/author.py) reads the current design,
integration, installation and physical records.
[float_art.py](../../tools/magnetic-float-guide/float_art.py) renders native
CadQuery solids, with coral motion cues and the same current CAD revision.
[build.py](../../tools/magnetic-float-guide/build.py) verifies input and image
hashes, checks layout overflow, binds the pages with bookmarks and writes the
cover and `.pdf.json` sidecar.

[guide-inputs.json](guide-inputs.json) binds the text to its sources.
[art/manifest.json](art/manifest.json) binds every illustration to its generator,
geometry and image bytes. The
[recipe source record](../../tools/magnetic-float-guide/build-recipe-sources.json)
separates manufacturer specifications, selected shop procedures and observed
print evidence.
