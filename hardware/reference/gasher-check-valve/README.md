# GASHER 1/4" NPT inline check valve

Owned SKU B0FV2D2FFX has a female 1/4-inch NPT inlet and male 1/4-inch NPT
outlet in the nominal dimensional drawing. Verify the supplied body's arrow
runs female → male. The two roles are:

- **gasher-water** — the SeaFlo discharge check in the MAACFLOW → GASHER →
  PP450822E chain.
- **gasher-co2** — the check downstream of WR1110, before the cold core's
  plain bottom gas port. Its female inlet takes PI010822S; its male outlet
  takes a 316 FNPT coupling and a second PI010822S.

The owned valve's exact body and seat materials are not established by the
source drawing. Stainless/PTFE and nickel-plated-copper/soft-seat descriptions
in the source record conflict. Confirm the supplier specification, pressure
rating, CO2/carbonated-water suitability, cracking pressure and reverse sealing
before qualifying the part for either duty. The gas-check placement must
include the adapters and coupling, as specified in
[internal plumbing](/hardware/assembly/internal-plumbing.md).

Fluid roles are in [fluid topology](/hardware/topology/fluid-topology.md).

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
