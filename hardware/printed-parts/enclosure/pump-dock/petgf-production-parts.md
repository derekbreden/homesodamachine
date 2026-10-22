# PET-GF pump-dock production parts

The dock's PET-GF parts are the four tee caps, one part (`enclosure-tee-cap`) printed four times, and the factory's tube setting jig (`enclosure-pump-tube-setting-jig`). The tee anchors, the collet plate and the magnet bosses are front-top's own material.

The tee cap's manufacturing STL contains its print pose, standing on its fore end with the section on the bed; `turns=x:0` preserves it. The cap is one section its whole length, so every layer is the whole section, no face looks down and each wing bends along its own extrusion lines.

Use the shared [petgf.3mf](../../petgf.3mf) with six walls and 100% object infill, so each cap is solid through both wings and lips. Retain 0.20 mm first layers and 0.24 mm body layers, ordinary/auxiliary cooling off, and localized overhang/bridge cooling at 70% above the 50% unsupported threshold. Supports keep the shared Tree (auto)/Default decisions. Keep the 0.65 mm gaps between the half pipe and the wings open; they let the wings spring. The [anchor caps](../anchor-cap/README.md) share the snap interface and the recipe and can print on the same plate.

The tube setting jig prints alone on the `factory-tools` plate, as exported, with the shared recipe.

Manual offline preparation, without starting a printer:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf --slice --review
```

Bind any production project and emitted paths to the current manufacturing meshes. No native project or print is bound to the tee cap; its snap, its retention in the anchor and its fit round the branch collar are unmeasured.
