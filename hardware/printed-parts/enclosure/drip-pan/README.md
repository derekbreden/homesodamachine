# Drip pan

Printed catch basin for the service bay — it lands on the cold core's
foam-cap top under the ASSE 1022 chain's atmospheric-vent tip. The Shutao
moisture probe lies flat in it; any vent drip, condensate, or overflow
pools in the basin and wets the probe, tripping the moisture alarm.

- **Type:** printed part (PETG), open-top watertight basin.
- **Outer:** 130 × 66 × 22 mm, 2.5 mm walls on a 3 mm floor.
- **Features:** rounded vertical corners (r6) and a filleted floor-to-wall cove
  (r3). No drain — the basin holds drips and is emptied on service.
- **Frame:** +X long axis, +Y depth, +Z up; origin at the lower-front-left outer
  corner. Open top.

## Deferred

Mounting to the foam-cap top is the `held` axis — no bosses or tabs
(enclosure-mechanical Open #4). The pan is not yet placed in the enclosure
pack: the scorecard verifies the vent tip's drip fall onto the cap, but the
pan as drawn runs into the packed SeaFlo when set under the tip, so its
size/position resolve with the water-deck layout in
`enclosure-assembly/_contents.py`.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```
