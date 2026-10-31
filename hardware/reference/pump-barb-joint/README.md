# Pump barb joint

The joint on each of the G Ganen pump's two barbs, from three bought parts:

| Part | Source | Use |
|---|---|---|
| neoPure PVCR-0610 reinforced clear PVC, 3/8 in ID × 0.594 in OD | FWS, [purchases.md](../../ledger/purchases.md) | A short piece pushed over the barb to its root |
| John Guest PP061208W reducer, 3/8 in stem × 1/4 in push-to-connect | FWS, [purchases.md](../../ledger/purchases.md), [reference](../jg-pp061208w/jg_pp061208w.py) | Its stem trimmed to 10 mm and pushed into the tube's other end up to the shoulder |
| YDS butterfly SS W2 hose clamp, 10–16 mm, 9 mm band | [B07C33VLQ6](https://www.amazon.com/dp/B07C33VLQ6) | Two: one on the tube over the barb, one over the stem |

The trimmed stem's tip meets the barb's tip inside the tube, so the tube is the barb's length plus
the stem's: 23.39 mm on the suction barb and 23.14 mm on the discharge barb. Each band is centred on
the length of fitting the tube covers. The reducer's 1/4 in collet carries the line on.

[`pump_barb_joint.py`](pump_barb_joint.py) draws the tube installed: its bore follows the barb's
scanned profile and the stem, and its outside opens to keep the tube's section. Each band closes on
the tube's widest outside under it. Its frame has +X on the port's outward axis and the barb's tip
at X = 0.

A joint can be drawn bent down. The reducer and its clamp turn about the lowest point of the barb's
tip, where the stem's tip bears on it, and the barb and its clamp stay as they are. The tube runs
straight on each and creases on the plane halfway between them.

| From the barb's tip, mm | Suction | Discharge |
|---|---:|---:|
| Tube's end, at the barb's root | −13.39 | −13.14 |
| Barb clamp's band centre, and the diameter it closes on | −6.69, d15.51 | −6.57, d15.59 |
| Stem clamp's band centre, and the diameter it closes on | 5.00, d15.09 | 5.00, d15.09 |
| Tube's end, at the stem's shoulder | 10.00 | 10.00 |
| The reducer's 1/4 in collet mouth | 34.10 | 34.10 |

Both bands close inside the clamp's 10–16 mm range.

Taken from Derek's photograph, not measured:

- the stem's 10 mm trim, read against the reducer's 17.3 mm mouth collar;
- the clamp's housing, screw end and key, read against its 9 mm band. The key turns with the screw,
  so it is drawn flat in the band's plane, and a placement picks which side it runs to.

```sh
tools/cad-venv/bin/python hardware/reference/pump-barb-joint/pump_barb_joint.py
```
