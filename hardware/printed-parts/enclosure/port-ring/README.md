# Port ring

A flat printed annulus in a pocket of the back wall's port field, under a through-wall
fitting's own flange. The fitting's nut draws flange, ring and wall together.

| | |
|---|---|
| OD | Ø[33.96](RING_OD) |
| bore | Ø[18](RING_BORE) — the wall's own hole for the same threading |
| thickness | [3](RING_THICK) mm — the pocket's depth, and how far the fitting's flange bears outboard of the wall |
| colour showing past the flange | [5.55](RING_W) mm |
| volume | [1.95](RING_VOL) cm³ |

## Where each one goes

| station | colour |
|---|---|
| `bulkhead-carb` | blue — carbonated water, the umbilical riser |
| `bulkhead-water` | white — tap water, the customer's teed-in supply |

Both are John Guest PP1208E unions, so both wear the same ring. What a colour means on the rear
face is stated in [`../back-panel/_back_panel_dimensions.py`](../back-panel/_back_panel_dimensions.py);
which fitting stands where is [`../back-panel/README.md`](README.md) §"Bulkhead array arrangement".

## Print

Flat on the bed, many to a plate, one colour per ring. PETG, the enclosure's own stock
([`bom.md`](/hardware/ledger/bom.md) §7).

The pocket it drops into is struck by [`enclosure.py`](../enclosure/enclosure.py) from the same
`back_ports` stations that bore the wall, one [3](RING_THICK) mm deep at each marked station in
the port field's crown.

## Files

- `port_ring.py` — the part, and the figures the wall and the drawings read
- `port-ring-union.step` — the PP1208E station's ring

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads the ring
against the fitting it rings.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/port-ring/port_ring.py`
