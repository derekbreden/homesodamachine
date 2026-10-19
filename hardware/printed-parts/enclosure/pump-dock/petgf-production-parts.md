# PET-GF pump-dock production parts

The twelve station-specific parts use six walls and 100% object infill. Their manufacturing STLs already contain the flat print pose; `turns=x:0` preserves it. Each command prepares one station using the shared [`petgf.3mf`](../petgf.3mf) recipe. These are manual preparation commands; they do not start a printer. Native placement, emitted supports and the existing preparation review establish whether each three-part station fits its plate.

The recipe uses 0.20 mm first layers and 0.24 mm body layers, ordinary and auxiliary cooling at zero, and localized overhang/bridge cooling at 70% above the 50% unsupported threshold. The rigid PET-GF parts do not flex during assembly; local strain belongs to the TPU keys.

Run from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-receiver-keeper-west-outer.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cradle-west-outer.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cover-west-outer.stl,quantity=1,turns=x:0,walls=6,infill=100

tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-receiver-keeper-west-inner.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cradle-west-inner.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cover-west-inner.stl,quantity=1,turns=x:0,walls=6,infill=100

tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-receiver-keeper-east-inner.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cradle-east-inner.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cover-east-inner.stl,quantity=1,turns=x:0,walls=6,infill=100

tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-receiver-keeper-east-outer.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cradle-east-outer.stl,quantity=1,turns=x:0,walls=6,infill=100 \
  --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-return-cover-east-outer.stl,quantity=1,turns=x:0,walls=6,infill=100
```

These twelve PET-GF preparations remain a manufacturing handoff. The separate eight one-object TPU projects and their actual native estimates are in the [wet-part preparation](print-preparation/2026-10-18-asymmetric-wet-siraya85a-mark1/README.md). Saved settings and geometric fit do not establish snap force, pressure capacity, creep, leakage or lifetime.
