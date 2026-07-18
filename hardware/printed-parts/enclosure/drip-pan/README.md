# Drip pan

Printed catch basin on the compressor top, under the Multiplex atmospheric-vent
barb. The Shutao moisture probe lies flat in it; any vent drip, condensate, or
overflow pools in the basin and wets the probe, tripping the moisture alarm.

- **Type:** printed part (PETG), open-top watertight basin.
- **Outer:** 130 × 66 × 22 mm, 2.5 mm walls on a 3 mm floor.
- **Features:** rounded vertical corners (r6) and a filleted floor-to-wall cove
  (r3) so water sheets to the probe and the print cleans easily. No drain — the
  basin holds drips and is emptied on service.
- **Frame:** +X long axis, +Y depth, +Z up; origin at the lower-front-left outer
  corner. Open top.

## Deferred

Mounting to the compressor top / enclosure is the `held` axis and not yet
modeled — no bosses or tabs (enclosure-mechanical Open #4). The basin currently
rests on the compressor top in the pack.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```
