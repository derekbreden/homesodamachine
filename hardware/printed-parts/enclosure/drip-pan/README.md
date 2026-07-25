# Drip pan

Printed catch basin for the service bay — it rides a pair of printed rails on
the cold core's foam-cap top, under the ASSE 1022 chain's atmospheric-vent tip.
The Shutao moisture probe lies flat in it; any vent drip, condensate, or
overflow pools in the basin and wets the probe, tripping the moisture alarm.

Two parts print here: the **basin** and the **rail pair** it slides on.

| | basin | rails |
|---|---|---|
| type | printed PETG, open-top watertight | printed PETG, mirrored L-pair |
| outer | [100](PAN_LEN) × [48](PAN_DEPTH) × [14](PAN_HEIGHT) mm | [124.6](RAIL_SPAN) mm across the pair |
| section | [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR) mm floor | [3](RAIL_RAIL_T) mm rail |
| capacity | [44.9](PAN_CAPACITY) mL to the rim | — |

Rounded vertical corners (r[6](PAN_CORNER_R)) and a filleted floor-to-wall cove
(r[3](PAN_COVE_R)). No drain — the basin holds drips and is emptied on service.

Frame: +X long axis, +Y depth, +Z up; origin at the basin's lower-front-left
outer corner of the walls, and `rail_offset()` carries that origin to the rail
pair's. Open top.

## The vent's column

The vent tip and the foam-cap top bound the basin's column. Under the tip,
[4](PAN_VENT_GAP) mm of splash-and-service air; then the basin; then
[13.6](PAN_LIFT) mm of open deck down to the cap — the aft strip's routing lane.

`_contents.drip_pan_seat()` re-derives that lift from the *placed* vent tip and
raises when the printed rail no longer stands at it. The basin is not posed by
hand either: `_contents` centres it on the vent column, so the chain's pose
carries the pan.

Depth is the aft strip — the run between the SeaFlo's back face and the foam
cap's rear edge, less a standoff off the pump.

## Carried at the floor plane, drawn out the back

The floor slab runs [5](PAN_FLANGE) mm past each wall — [110](PAN_ACROSS) mm
across the flanges — and that overhang rides the rails. The basin's interior
carries no mounting feature.

The rails are a mirrored L-pair: a foot for the VHB, a web that fences the basin
in X, a shelf the flanges ride, and a home stop at the forward end that the
basin's front wall butts. They are bonded to the printed foam-cap lid with 3M
VHB 4941 ([1.1](RAIL_VHB) mm) under foot and web together; nothing fastens to
the cap and nothing fastens the basin. The fit is [0.3](RAIL_SLIP) mm of slip
per side.

Service is one motion — **draw the basin aft** along the rails, in +Y, out
through the back of the cabinet. It rises at no point in that travel.

The rear-panel slot that motion runs through is not cut yet — see the
enclosure's open items. Until it is, the basin draws aft off the rails and
lifts clear inside the cabinet.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/drip-pan/drip_pan.py`
