# GASHER 1/4" NPT inline check valve

Owned SKU B0FV2D2FFX has a female 1/4-inch NPT inlet and male 1/4-inch NPT
outlet in the nominal dimensional drawing. It is not part of the appliance.
Both of the machine's check valves, the CO2 check downstream of the PISCO
secondary and the pump-discharge water check, are the push-connect
[neoFit ACHV44-E](../neofit-achv44-check/README.md).

The owned valve's exact body and seat materials are not established by the
source drawing. Stainless/PTFE and nickel-plated-copper/soft-seat descriptions
in the source record conflict. Its pressure rating, CO2/carbonated-water
suitability, cracking pressure and reverse sealing are unconfirmed.

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

Frame: **+Y = flow axis**, the female inlet
at −Y and the male outlet at +Y, centered on X/Z, +Z up.

Terminals: `inlet()` (socket mouth) and `outlet()` (stub end), each
`(position, outward axis)`.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/gasher-check-valve/gasher_check_valve.py
```
