# Drip pan

Printed catch basin for the service bay, standing under the ASSE 1022 chain's
atmospheric-vent tip. The Shutao moisture probe lies flat in it; any vent drip,
condensate, or overflow pools in the basin and wets the probe, tripping the
moisture alarm.

One part prints here: the **basin**.

| | basin |
|---|---|
| type | printed PETG, open-top watertight |
| outer | [53](PAN_LEN) × [76](PAN_DEPTH) × [10](PAN_HEIGHT) mm |
| section | [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR) mm floor |
| capacity | [23.9](PAN_CAPACITY) mL to the rim |

Rounded vertical corners (r[6](PAN_CORNER_R)) and a filleted floor-to-wall cove
(r[2](PAN_COVE_R)). No drain — the basin holds drips and is emptied on service.

Frame: +X across the strip, +Y depth — the withdrawal axis — +Z up; origin at
the basin's lower-front-left outer corner of the walls. Open top.

The basin is narrow across and deep down. X is the aft strip's contested axis:
the controller board stands in the same strip, west of the basin, and every
millimetre the basin gives back there is a millimetre of the board's connector
lanes. Y is the axis with room to spare — the run between the SeaFlo's back face
and the foam cap's rear edge is deeper than the basin needs.

## The chain's column

The ASSE chain's underside and the SeaFlo's crown bound the basin's column.
Under that underside, [4](PAN_VENT_GAP) mm of splash-and-service air; then the
basin; then the air its own floor keeps over the casting, one `LINE_HUG` of it.
The chain is rolled about its own flow axis, so its underside is a body corner
and the vent stub's tip stands above it, leaning aft.

`_contents.drip_pan_seat()` hangs the basin off that underside and raises when
the casting under it asks for more. The basin is not posed by hand either: `_contents` hangs it
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

## The carry is open, and it belongs on the flange

The basin's interior holds no mounting feature, and nothing stands under its
floor. That last part is the constraint: the basin lies over the SeaFlo, so
anything beneath it is height paid twice — once for the casting's own clearance
and again for the carrier's section — and every millimetre of it comes straight
out of the vent gap above.

So the carry belongs on the basin's **own flange**, the way a baking tray's rim
is what the oven rack holds. `FLANGE_W` (now [0](PAN_FLANGE)) grows off the wall
at a plane up the basin's height; rails stand outboard of the basin at that
plane and it hangs between them. What the pair may spend in X is the wall's
footprint and a slip fit — the strip's east end belongs to V-K and the umbilical
cluster, and its west end to the board.

Service is one motion — **draw the basin aft**, in +Y, out through the back of
the cabinet.

The rear-panel slot that motion runs through is not cut yet — see the
enclosure's open items. Until it is, the basin lifts clear inside the cabinet.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/drip-pan/drip_pan.py`
