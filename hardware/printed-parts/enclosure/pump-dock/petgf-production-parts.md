# PET-GF pump-dock production parts

The dry dock is five PET-GF parts: the four flat keepers and the one return block. All five go on one plate with the shared [`petgf.3mf`](../../petgf.3mf) recipe. Their manufacturing STLs already contain the print pose; `turns=x:0` preserves it. This is a manual preparation command; it does not start a printer.

All five use six walls and 100% object infill; the [print regions](../enclosure/heat-set-review/print-regions.json) name each part whole. The block lies on its top face, the plane that bears on the front-top's tray foot: its stepped underside faces up, its slot walls stand vertical and each seat's arcs stay within 22 degrees of vertical, so it needs no support.

The recipe uses 0.20 mm first layers and 0.24 mm body layers, ordinary and auxiliary cooling at zero, and localized overhang/bridge cooling at 70% above the 50% unsupported threshold. The rigid PET-GF does not flex during assembly; the TPU returns flex through each channel's slot.

Run from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf --slice --review
```

The separate eight one-object TPU projects are in the [wet-part preparation](print-preparation/2026-10-18-asymmetric-wet-siraya85a-mark1/README.md). Saved settings and geometric fit do not establish snap force, pressure capacity, creep, leakage or lifetime.
