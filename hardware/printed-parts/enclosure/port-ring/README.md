# Port ring

A flat printed annulus lying in a pad on the back wall's outer face, under a through-wall
fitting's own flange. The fitting's nut draws flange, ring and wall together. One at every
crossing the wall passes a tube through.

The wall passes two families of fitting, so the ring comes in two sizes — each struck on the
flange it hides under and the barrel it passes. `thickness` and `colour showing` are the same
for both.

| | union station | CO2 station |
|---|---|---|
| fitting | John Guest PP1208E | neoFit ABU44 |
| OD | Ø[30.96](RING_OD) | Ø[30.04](CO2_RING_OD) |
| bore | Ø[18](RING_BORE) | Ø[17.86](CO2_RING_BORE) |
| volume | [1.00](RING_VOL) cm³ | [0.92](CO2_RING_VOL) cm³ |

| | |
|---|---|
| thickness | [2](RING_THICK) mm — the depth its rim is cut to, so the two faces come out one plane, and how far the fitting's flange bears outboard of the wall |
| colour showing past the flange | [4.05](RING_W) mm |

## Where each one goes

| station | ring | colour |
|---|---|---|
| `bulkhead-carb` | union | blue — carbonated water, the umbilical riser |
| `bulkhead-water` | union | white — tap water, the customer's teed-in supply |
| `co2-inlet` | CO2 | red — the customer's regulator tether |
| `bulkhead-flavor-a` | union | black |
| `bulkhead-flavor-b` | union | black |

What a colour means on the rear face is stated in
[`../back-panel/_back_panel_dimensions.py`](../back-panel/_back_panel_dimensions.py); which
fitting stands where is [`../back-panel/README.md`](README.md) §"Bulkhead array arrangement".

The two flavour rings print in the wall's own black and identify nothing — a customer pushes
black into either black and the manifold sorts them. What they carry is the rim, so no station
on that face is a different kind of thing from its neighbour.

## Print

Flat on the bed, many to a plate, one colour per spool. PETG, the enclosure's own stock
([`bom.md`](/hardware/ledger/bom.md) §7).

The pad it drops into is struck by [`enclosure.py`](../enclosure/enclosure.py) from the same
`back_ports` stations that bore the wall — a plain cylinder standing off the wall with the ring's
pocket cut [2](RING_THICK) mm through it, which leaves a rim of that width around each ring.

## Files

- `port_ring.py` — the part, and the figures the wall and the drawings read
- `port-ring-union.step` — the PP1208E station's ring
- `port-ring-neofit.step` — the ABU44 station's ring

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads each ring
against the fitting it rings.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/port-ring/port_ring.py`
