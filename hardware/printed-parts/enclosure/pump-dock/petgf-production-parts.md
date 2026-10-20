# PET-GF pump-dock production parts

The dry dock has three separate PET-GF parts: two outer keepers and one inner-pair keeper. The four fixed-body elbow seats are integral with front-top. The keeper manufacturing STLs contain their flat print pose; `turns=x:0` preserves it.

Use the shared [petgf.3mf](../../petgf.3mf), six walls and 100% object infill. Retain 0.20 mm first layers and 0.24 mm body layers, ordinary/auxiliary cooling off, and localized overhang/bridge cooling at 70% above the 50% unsupported threshold. The plain U openings face down in service and slide over the junction necks without snapping.

Manual offline preparation, without starting a printer:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf --slice --review
```

Bind any production project and emitted paths to the current manufacturing meshes. The [elbow integration review](elbow-review/README.md) records geometry, not physical fit or lifetime. The [October 18 wet projects](print-preparation/2026-10-18-asymmetric-wet-siraya85a-mark1/README.md) apply only to their saved geometry.
