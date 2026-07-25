# Drip pan

Printed catch basin for the service bay — it lands on the cold core's
foam-cap top under the ASSE 1022 chain's atmospheric-vent tip. The Shutao
moisture probe lies flat in it; any vent drip, condensate, or overflow
pools in the basin and wets the probe, tripping the moisture alarm.

Two parts print here: the **basin** and the **cradle** it drops into.

| | basin | cradle |
|---|---|---|
| type | printed PETG, open-top watertight | printed PETG, floorless fence |
| outer | 100 × 30 × 22 mm | 106.4 × 36.4 × 7 mm |
| section | 2.5 mm walls on a 3 mm floor | 3 mm rail |
| capacity | 45.1 mL to the rim | — |

Rounded vertical corners (r6) and a filleted floor-to-wall cove (r3). No
drain — the basin holds drips and is emptied on service.

Frame: +X long axis, +Y depth, +Z up; origin at the basin's lower-front-left
outer corner, and `cradle_offset()` carries that origin to the cradle's. Open
top.

## The shape is the strip

The aft strip of the service bay is 55 mm wide — the SeaFlo's back face at
y = 326 to the rear wall at y = 381 — and the vent tip hangs over it at
(134.0, 345.5, 285.0), pointing straight down. The basin is **centred on that
column**, so the drip lands in the middle of the floor, on the moisture plate:
100 long because the plate lies flat down its length, 30 deep because that is
what the strip gives once the pump keeps its clearance on one side and the pan
keeps off the rear wall on the other. The enclosure does not place the pan by
hand — `_contents` reads the vent tip and subtracts half the basin, so a change
in the ASSE chain's pose carries the pan with it.

Seated at x[84, 184] y[330.5, 360.5] z[253.4, 275.4]: 4.50 mm to the SeaFlo,
12.10 mm to V-K, 12.33 mm to the ASSE chain, resting on the cap. The drip's
Ø6.35 column falls 9.6 mm of free air from the tip to the rim plane and 28.60
mm in all, landing at (134.00, 345.50, 256.40) — 9.3 mm from the nearest
interior wall.

## Held by the cradle

The cradle is one closed rail loop, bonded to the printed foam-cap lid with
3M VHB 4941 (1.1 mm) on its 3 mm underside — ~800 mm² of bond under a part
that weighs 26 g dry. It has no floor, so the basin drops through it and seats
on the cap itself; the rail takes the basin in X and Y with a 0.2 mm slip per
side and stands 7 mm up its outside. Nothing fastens to the cap, and nothing
fastens the basin: it lifts off the rail by hand.

Service is two motions, both in verified-clear air: **lift 8 mm, draw 84 mm
west** along the deck (the swept box x[0, 184] y[330.5, 360.5] z[261.4, 283.4]
is clear of every packed body), which walks the basin out from under the ASSE
chain to the strip's west end. There the west two thirds of its rim stands
under an open shaft — a Ø3 cast up from the rim finds nothing in 120 mm — and
the east end has 34.46 mm of free lift under the chain's inlet fittings, which
is the room to tilt it up and out.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```
