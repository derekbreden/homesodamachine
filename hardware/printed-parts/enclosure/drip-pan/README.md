# Drip pan

Printed catch basin for the service bay — it rides a pair of printed rails on
the cold core's foam-cap top, under the ASSE 1022 chain's atmospheric-vent tip.
The Shutao moisture probe lies flat in it; any vent drip, condensate, or
overflow pools in the basin and wets the probe, tripping the moisture alarm.

Two parts print here: the **basin** and the **rail pair** it slides on.

| | basin | rails |
|---|---|---|
| type | printed PETG, open-top watertight | printed PETG, mirrored L-pair |
| outer | [64](PAN_LEN) × [76](PAN_DEPTH) × [15](PAN_HEIGHT) mm | [70.6](RAIL_SPAN) mm across the pair |
| section | [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR) mm floor | [3](RAIL_RAIL_T) mm rail |
| capacity | [50.3](PAN_CAPACITY) mL to the rim | — |

Rounded vertical corners (r[6](PAN_CORNER_R)) and a filleted floor-to-wall cove
(r[2](PAN_COVE_R)). No drain — the basin holds drips and is emptied on service.

Frame: +X across the strip, +Y depth — the withdrawal axis — +Z up; origin at
the basin's lower-front-left outer corner of the walls, and `rail_offset()`
carries that origin to the rail pair's. Open top.

The basin is narrow across and deep down. X is the aft strip's contested axis:
the controller board stands in the same strip, west of the basin, and every
millimetre the basin gives back there is a millimetre of the board's connector
lanes. Y is the axis with room to spare — the run between the SeaFlo's back face
and the foam cap's rear edge is deeper than the basin needs.

## The chain's column

The ASSE chain's underside and the foam-cap top bound the basin's column. Under
that underside, [4](PAN_VENT_GAP) mm of splash-and-service air; then the basin;
then [17.7](PAN_LIFT) mm of open deck down to the cap — the aft strip's routing
lane. The chain is rolled about its own flow axis, so its underside is a body
corner and the vent stub's tip stands above it, leaning aft.

`_contents.drip_pan_seat()` measures the air the printed rail leaves and raises
outside the band. The basin is not posed by hand either: `_contents` hangs it
east of the vent column, the tip landing a stated inset inside its west outer
face, and lands its back face on the cap's rear edge. The tip's X is fixed by
the chain's own length along its flow axis and does not move with the roll; the
inset is what absorbs a re-roll's swing in Y.

## What the floor carries sets the depth

The moisture plate lies flat down the basin's **depth** — its long edge along
the withdrawal axis, the axis the strip has to give — and the floor's flat area
inside the coves is what it lands on: [55.25](PLATE_LEN) × [41](PLATE_DEPTH) mm
of plate with [1](PLATE_SLIP_MM) mm of slip a side. `check_plate()` raises when
it does not fit, because a plate wider than the flat rides up on the coves
instead of lying down and the water has to stand that much deeper before it
reads. That requirement is what sets the basin's Y, and what the SeaFlo's
station forward of it makes room for.

## Carried on its floor edge, drawn out the back

The basin is carried on its own floor edge and its interior holds no mounting
feature. The rails are a mirrored L-pair: a web, with a foot and a shelf both
turning inboard off it at opposite ends of its height — the foot lying on the
cap under the basin, the shelf carrying the basin — plus a home stop at the
forward end that the basin's front wall butts. Nothing reaches outboard, so the
pair spans [70.6](RAIL_SPAN) mm, the basin plus its two webs: the strip's east
end belongs to V-K and the umbilical cluster, and its west end to the board.

They are bonded to the printed foam-cap lid with 3M VHB 4941
([1.1](RAIL_VHB) mm) under foot and web together; nothing fastens to the cap and
nothing fastens the basin. The fit is [0.3](RAIL_SLIP) mm of slip per side.

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
