# Drip pan

Printed catch basin for the service bay, standing under the ASSE 1022 chain's
atmospheric-vent tip. The Shutao moisture probe lies flat in it; any vent drip,
condensate, or overflow pools in the basin and wets the probe, tripping the
moisture alarm.

One part prints here: the **basin**.

| | basin |
|---|---|
| type | printed PETG, open-top watertight |
| outer | [53](PAN_LEN) × [76](PAN_DEPTH) × [10](PAN_HEIGHT) mm at the walls |
| over the rim | [73](PAN_RIM_LEN) × [96](PAN_RIM_DEPTH) mm at the flange |
| section | [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR) mm floor |
| capacity | [23.9](PAN_CAPACITY) mL to the rim |

One plan outline at r[6](PAN_CORNER_R), and everything is that outline at its own
offset — floor slab and walls on the outline itself, the flange on the outline
plus [10](PAN_FLANGE) mm, the cavity on the outline less one wall. A corner is the
same corner at every height. Inside, a filleted floor-to-wall cove
(r[2](PAN_COVE_R)). No drain — the basin holds drips and is emptied on service.

Frame: +X across the strip — the withdrawal axis — +Y depth, +Z up; origin at
the basin's lower-front-left outer corner of the walls, the flange reaching one
flange width outboard of it on both plan axes. Open top.

The basin is narrow across and deep down. X is the loft's contested axis: east of
the basin the west column's crossing ladder climbs rung over rung, and the
basin's east rim is that ladder's lid. Y is the axis with room to spare — the run
between the SeaFlo's back face and the foam cap's rear edge is deeper than the
basin needs.

## The chain's column

The ASSE chain's underside and the SeaFlo's crown bound the basin's column.
Under that underside, [4](PAN_VENT_GAP) mm of splash-and-service air; then the
basin; then the air its own floor keeps over the casting, one `LINE_HUG` of it.
The chain is rolled about its own flow axis, so its underside is a body corner
and the vent stub's tip stands above it, leaning aft.

`_contents.drip_pan_seat()` hangs the basin off that underside and raises when
the casting under it asks for more. The plan station is not posed by hand either.
In X the flange's west edge lands on the −X wall's inner face
(`_contents.drip_pan_west`), the face the tray withdraws through; in Y the vent's
own column centres it, held off the discharge chain's barb by what a hose leaving
that barb needs, and it is the **flange** that arrives at the barb first.
`_contents._pan_room` reads the vent's tip back against the floor those two
leave, and raises when the drip would land outside the basin it is meant for.

## What the floor carries sets the depth

The moisture plate lies flat down the basin's **depth** — its long edge along
the withdrawal axis, the axis the strip has to give — and the floor's flat area
inside the coves is what it lands on: [55.25](PLATE_LEN) × [41](PLATE_DEPTH) mm
of plate with [1](PLATE_SLIP_MM) mm of slip a side. `check_plate()` raises when
it does not fit, because a plate wider than the flat rides up on the coves
instead of lying down and the water has to stand that much deeper before it
reads. That requirement is what sets the basin's Y, and what the SeaFlo's
station forward of it makes room for.

## The carry is the rim

The basin's interior holds no mounting feature, and nothing stands under its
floor. That last part is the constraint: the basin lies over the SeaFlo, so
anything beneath it is height paid twice — once for the casting's own clearance
and again for the carrier's section — and every millimetre of it comes straight
out of the vent gap above.

So the carry is the basin's **own rim**, the way a baking tray's is what the oven
rack holds. The flange turns out [10](PAN_FLANGE) mm all four ways at the top of
the walls, its top face flush with them, so it costs the column nothing. A 45°
haunch fills the corner under it — the tray prints floor-down, and the haunch is
what the flange's first courses grow out of. What is left flat outboard of that
haunch, less the slip, is [6.70](PAN_BEARING) mm of bearing a side, and
`_contents.drip_pan_rails` stands a rail under each.

**One number for two grips**, and the hand sets it: the west lip is hooked with a
fingertip to draw the tray, and a lip a finger pulls on wants ten. The rail takes
what that lip leaves. One rim runs all four sides at the one figure.

The rails are printed into the enclosure's **back-top piece**, rooted on the −X
wall's inner face and running east under the rim — the axis a rail is laid on is
the axis the thing on it travels. Their two inboard arrises take the tray's two
haunches and hold it on its column.

Service is one motion — **draw the tray west**, out through the slot in that same
wall (`_contents.west_wall_ports`). The slot is the tray's own silhouette: rim-wide
above the flange's underside, haunch-wide below it. The step between the two is the
wall the rails stand on.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/drip-pan/drip_pan.py`
