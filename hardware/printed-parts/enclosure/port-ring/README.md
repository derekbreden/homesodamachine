# Port ring

A flat printed annulus in a pocket of the back wall's port field, under a through-wall
fitting's own flange. The fitting's nut draws flange, ring and wall together.

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
| thickness | [2](RING_THICK) mm — the pocket's depth, and how far the fitting's flange bears outboard of the wall |
| colour showing past the flange | [4.05](RING_W) mm |

## Where each one goes

| station | ring | colour |
|---|---|---|
| `bulkhead-carb` | union | blue — carbonated water, the umbilical riser |
| `bulkhead-water` | union | white — tap water, the customer's teed-in supply |
| `co2-inlet` | CO2 | red — the customer's regulator tether |

What a colour means on the rear face is stated in
[`../back-panel/_back_panel_dimensions.py`](../back-panel/_back_panel_dimensions.py); which
fitting stands where is [`../back-panel/README.md`](README.md) §"Bulkhead array arrangement".

The two flavour unions wear none. A customer pushes black into either black and the manifold
sorts them, so the field is solid around their bores and their flanges bear on its crown.

## Print

Flat on the bed, many to a plate, one colour per ring. PETG, the enclosure's own stock
([`bom.md`](/hardware/ledger/bom.md) §7).

The pocket it drops into is struck by [`enclosure.py`](../enclosure/enclosure.py) from the same
`back_ports` stations that bore the wall, one [2](RING_THICK) mm deep at each marked station in
the port field's crown.

## Files

- `port_ring.py` — the part, and the figures the wall and the drawings read
- `port-ring-union.step` — the PP1208E station's ring
- `port-ring-neofit.step` — the ABU44 station's ring

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads each ring
against the fitting it rings.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/port-ring/port_ring.py`
