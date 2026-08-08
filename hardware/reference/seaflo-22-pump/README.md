# SEAFLO 22-Series diaphragm pump

SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand diaphragm pump, model
SFDP1-013-100-22 ([B0166UBJX4](https://www.amazon.com/dp/B0166UBJX4)), the
appliance's `seaflo-pump` — transfers tap water against CO2 back-pressure into
the carbonator. 3/8" hose-barb inlet + outlet on the head (plumbing in
`hardware/assembly/internal-plumbing.md`).

## Ports

Both ports are **3/8" hose barbs molded into the pump head** — fixed, not
fittings. There is no port thread and nothing unscrews: SEAFLO's own catalog
warns that its 90° barbed accessory fitting (21F001) "will NOT fit standard 3/8"
barb pump models," and sells an alternative **O-Ring Style Pump Outlet** as a
different factory head (109.60 mm across, Ø9.90 ports) for anyone who wants a
removable elbow. The barb head and the O-ring head are ordering options, not
field-swappable parts. A hose over the barb with a clamp is the only connection
this pump offers.

## Model

External envelope: a motor can bolted straight onto the pump head, the head
carrying the two barb ports and the pressure switch, on a mounting bracket whose
four rubber feet splay wider than any of it. The internal diaphragm mechanism is
not modeled.

The head is a narrow block and the barbs are short stubs off it — that pair, not
the head alone, is what makes the pump 80 mm wide across the ports. The feet, at
98 mm, are the widest thing on the pump.

The pump's 72 mm is the **motor can's own crown**. Its axis lies on the head's
mid-height and the can is Ø54, so the can's top, the head block's top and the
pressure switch's top all come out on that one plane. Below the head's port end
hangs a 30 mm boss, the lowest casting on the body, and the head block's own
underside stands clear above it.

| feature | size |
|---|---|
| overall | 187 (L) × 98 (W over the feet) × 72 (H) mm |
| across the barb tips | 80 |
| motor can | Ø54, bolted to the head's flange; its crown IS the pump's 72 |
| pump head | 54 wide at the ports, 70 at the flange band by the motor; 56 tall, its underside 16 above the mounting plane, over a 30 mm boss reaching down to 13 |
| ports | 2 × 3/8" hose barb (Ø10.4), 13 long, on the head's ±Y side faces, each pointing straight out along its ±Y axis, at Z 53 |
| pressure switch | the upper part of the head's -X end face, opposite the motor |
| mounting | Ø5.0 holes on a 57 × 79 pattern, feet 98 apart |

Frame: **+X = motor axis** (head at -X), foot underside at Z = 0, centered on Y.
The two 3/8" barbs leave the head's ±Y side faces; the -X end face carries the
pressure switch. `suction()` and `discharge()` return `(position, outward axis)`
with the position at the barb **tip**: suction at (-36.6, -40.0, 53.0) out -Y,
discharge at (-36.6, +40.0, 53.0) out +Y.

## Sources

Every labeled figure above comes from SEAFLO's dimensioned drawing for the 22
Series — Marine & RV catalog p.15, reproduced as an image on the Amazon listing.
Labeled there: 187 long, 72 tall, 80 across the barb tips, 98 across the feet,
Ø10.40 barbs, Ø5.00 holes on 57 × 79. Everything else is scaled off that
drawing's linework, calibrated on its 57 mm hole pitch.

Two cautions the drawing itself raises. Its linework, at that calibration,
scales to 178.5 mm long rather than the labeled 187 — the model carries the 8.5
mm difference in the pressure-switch block, the least-constrained feature. And
its linework puts the barb tips ~83 mm apart rather than the labeled 80, so
leave a couple of millimetres of margin outboard of each port.

Amazon's "Product Dimensions 7.35 × 4.31 × 2.83 in" quotes the width of the
**O-Ring** head (4.31 in = 109.60 mm), which this pump does not have.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/seaflo-22-pump/seaflo_22_pump.py
```
