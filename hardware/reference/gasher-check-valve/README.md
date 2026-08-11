# GASHER 1/4" NPT inline check valve

Nickel-plated copper hex-barrel check valve, soft seat, 150 psi: a **female**
1/4" NPT socket on the inlet end and a **male** 1/4" NPT stub on the outlet
end. The casting's flow arrow runs female → male, so an upstream male threads
into the socket and the stub threads into a downstream female. Two are packed
in the enclosure:

- **gasher-water** — the SeaFlo pump's discharge check, riding the pump top on
  the carb-water riser path.
- **gasher-co2** — the CO2 inlet check on the ABU44 → WR1110 chain.

Fluid roles are in `hardware/topology/fluid-topology.md`.

## Model

External envelope only — a hex barrel with a socket boss one end and a male NPT
stub the other. The internal spring + poppet is not modeled, and the NPT
threads are plain cylinders at the nominal major Ø.

| dimension | value | note |
|---|---|---|
| flow-axis length | 40 mm | off the manufacturer's dimensioned drawing |
| hex across corners | 17 mm | circumdiameter |
| hex across flats | 14.72 mm | 17 · √3/2 |
| hex barrel length | 18 mm | |
| female socket boss | Ø15.5 × 11 mm | inlet end, the depth a male threads in |
| male NPT stub | Ø13.7 × 11 mm | outlet end, 1/4" NPT major Ø, simplified |

Frame: **+Y = flow axis** (matches the enclosure placement), the female inlet
at −Y and the male outlet at +Y, centered on X/Z, +Z up.

Terminals: `inlet()` (socket mouth) and `outlet()` (stub end), each
`(position, outward axis)`.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/gasher-check-valve/gasher_check_valve.py
```
