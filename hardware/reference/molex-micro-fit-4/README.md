# Molex Micro-Fit 3.0 four-circuit pump connector

The pump connector is a black Molex Micro-Fit 3.0 wire-to-wire pair. The fixed
`43020-0400` plug housing snaps into the ridge wall behind the enclosure display;
the pump cartridge carries the mating `43025-0400` receptacle. The user pushes the
receptacle home until its integral latch clicks, and presses that downward-facing latch
through the empty pump bay to remove it.

| | Fixed enclosure side | Removable cartridge side |
|---|---|---|
| Housing | Molex `43020-0400` | Molex `43025-0400` |
| Contact | male `43031-0001` | female `43030-0001` |
| Cable | J13 → 22 AWG 4P | 22 AWG 4P → four pump Fastons |
| Mount | integral panel ears | free-hanging, integral mating latch |
| Colour | black | black |

Molex specifies both housings as polarized and positively locked. Its current product
specification accepts 22 AWG stranded copper through **1.85 mm maximum insulation OD**;
the bought BNTECHGO ribbon is 1.7 mm per conductor. The four-circuit run carries one
motor conductor per contact, about 0.8 A on a pump that is running, rather than summing
the two pumps through one contact. Conservatively applying Molex's fully-loaded six-circuit
wire-to-wire table to this four-circuit pair gives **4 A per contact at 22 AWG** for a 30 °C
maximum rise. That covers both the 0.8 A running load and the DRV8870 driver's 3.6 A peak
capability; the 43020 housing's agency table is 5 A per circuit.

## Printed panel

The fixed housing's panel ears are designed for 1.40–2.54 mm panel stock. The enclosure's
3 mm ridge wall is relieved on its cavity face to leave a **2.00 mm local panel**. The
cut-out follows Molex customer drawing `SD-43020-006`:

| Drawing feature | Nominal |
|---|---:|
| four-circuit body width `C` | 7.21 mm |
| panel-ear width `D` | 10.90 mm |
| main height | 7.11 mm |
| keyed overall height | 8.71 mm |
| lower ear band | 4.06 mm |
| upper key width | 1.98 mm |

`molex_micro_fit_4.panel_cut()` adds 0.15 mm FDM slip per cut edge and cuts the
cavity-side thinning pocket. The bought nylon ears provide the flex and retention;
the printed PET-GF wall remains rigid.

## Service envelope

Molex's `43025` drawing gives the removable body as 6.85 × 8.28 × 14.00 mm and the
complete mated pair as 24.77 mm long. Against the fixed housing's 16.89 mm body, the two
halves nest by **6.12 mm**. The assembly's service path therefore pulls the cartridge half
**7.12 mm** toward the user — the complete nesting distance plus 1 mm of true air — before
lowering it into the empty pump bay.

The enclosure installs the keyed/latching side downward. `enclosure_assembly.py` sweeps a
conservative envelope of the complete body and latch through that pull-and-drop motion and
checks it against the live front-top and display solids. It also requires at least 12 mm
between the latch and the pump-bay lintel for a fingertip.

## Contact order

On the bench, hold the fixed housing with its key up and view its mating face. Its moulded
circuit numbers control the harness: `1 AM2`, `2 AM1`, `3 BM2`, `4 BM1`. The enclosure
installs that key down; the numbers, not the installed visual order, remain authoritative.
The same circuit number must read through the mated pair at the cartridge. Continuity-test
the completed pair against J13; do not infer contact order from wire position after the
ribbon is dressed.

## Sources

- [Amazon B078Q7B7PG — black four-circuit Micro-Fit plug + receptacle, terminals included, two sets](https://www.amazon.com/dp/B078Q7B7PG). Incoming inspection verifies the moulded Molex part numbers and the fixed half's panel ears before crimping.
- [Molex 43020 series](https://www.molex.com/en-us/products/series-chart/43020) — `43020-0400`, black, four circuits, panel-mount ears.
- [Molex 43025 series](https://www.molex.com/en-us/products/series-chart/43025) — `43025-0400`, black, four circuits, mating lock and polarization.
- [Molex Micro-Fit 3.0 product specification PS-43045](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/430/43045/PS-43045-001.pdf) — wire range, insulation OD, electrical and mechanical ratings.
- [Molex 43020 customer drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/430/43020/430200601_sd.pdf?inline=) — housing envelope, panel range and recommended keyed cut-out.
- [Molex 43025 customer drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/430/43025/430250600_sd.pdf?inline=) — removable-housing envelope and complete mated-pair length.

Regenerate the reference STEP with:

```sh
tools/cad-venv/bin/python hardware/reference/molex-micro-fit-4/molex_micro_fit_4.py
```
