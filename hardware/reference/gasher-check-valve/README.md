# GASHER 1/4" NPT inline check valve

Brass hex-barrel spring check valve, 1/4" NPT male each end. Two are packed in
the enclosure:

- **gasher-water** — the SeaFlo pump's discharge check, riding the pump top on
  the carb-water riser path.
- **gasher-co2** — the CO2 inlet check on the DERPIPE → WR1110 chain.

Fluid roles are in `hardware/topology/fluid-topology.md`.

## Model

External envelope only — a hex barrel with a male NPT stub each end. The
internal spring + poppet is not modeled, and the NPT threads are plain
cylinders at the nominal major Ø.

| dimension | value | note |
|---|---|---|
| flow-axis length | 40 mm | off the manufacturer's dimensioned drawing |
| hex across corners | 17 mm | circumdiameter |
| hex across flats | 14.72 mm | 17 · √3/2 |
| hex barrel length | 18 mm | |
| NPT stub | Ø13.7 × 11 mm each | 1/4" NPT major Ø, simplified |

Frame: **+Y = flow axis** (matches the enclosure placement), centered on X/Z,
+Z up.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/gasher-check-valve/gasher_check_valve.py
```
