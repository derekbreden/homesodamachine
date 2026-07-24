# SEAFLO 22-Series diaphragm pump

SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand diaphragm pump
([B0166UBJX4](https://www.amazon.com/dp/B0166UBJX4)), the appliance's
`seaflo-pump` — transfers tap water against CO2 back-pressure into the
carbonator. 3/8" hose-barb inlet + outlet on the head (plumbing in
`hardware/assembly/internal-plumbing.md`).

## Model

External envelope: a motor can + a pump head (carrying the two barb ports and
the pressure switch) on a mounting base whose feet splay wider than the body.
The internal diaphragm mechanism is not modeled.

| feature | size |
|---|---|
| overall | 190 (L) × 112 (W over the side barbs) × 61 (H) mm; base 98 wide |
| motor can | Ø56 × 92 |
| pump head | 66 × 80 × 56 |
| ports | 2 × 3/8" hose barb (Ø13) on the head's ±Y side faces, each pointing straight out along its ±Y axis |
| pressure switch | on the head's -X end face, opposite the motor |

Frame: **+X = motor axis** (head at -X), base underside at Z = 0, centered on Y.
The two 3/8" barbs leave the head's ±Y side faces; the -X end face carries the
pressure switch.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/seaflo-22-pump/seaflo_22_pump.py
```
