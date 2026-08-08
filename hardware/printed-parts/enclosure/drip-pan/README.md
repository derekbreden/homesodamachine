# Drip pan

Printed catch basin for the service bay, standing under the ASSE 1022 chain's
atmospheric-vent tip. The Shutao moisture probe lies flat in it; any vent drip,
condensate, or overflow pools in the basin and wets the probe, tripping the
moisture alarm.

One part prints here: the **basin**.

| | basin |
|---|---|
| type | printed PETG, open-top watertight |
| outer | [52](PAN_LEN) × [76](PAN_DEPTH) × [10](PAN_HEIGHT) mm at the walls |
| over the rim | [72](PAN_RIM_LEN) × [96](PAN_RIM_DEPTH) mm at the flange |
| section | [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR) mm floor |
| capacity | [23.4](PAN_CAPACITY) mL to the rim |

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

The column reads UP from the pump, and the chain follows the basin rather than
bounding it. `enclosure_assembly.pan_floor` stands the basin's own floor one
`enclosure_assembly.FOOT_CLEAR` over the SeaFlo's **bracket** — the feet's top face, the
widest section the casting has, and the one the tray rides over rather than
beside — and `enclosure_assembly.build_asse` then hangs the chain's underside one basin
height plus [4](PAN_VENT_GAP) mm of splash-and-service air above that floor, so a
change to either number moves both bodies together. The chain is rolled about its
own flow axis, so its underside is a body corner and the vent stub's tip stands
above it, leaning aft.

The plan station is not posed by hand either.
In X the basin hangs off the pump — `enclosure_assembly.pan_east_x` puts its east rim one
clearance off the casting's west flank at the tray's own height — and the west lip
takes what the lane has left, which `enclosure_assembly.check_pan_lane` measures against
the −X wall's inner face, the face the tray withdraws through. In Y the pump's
discharge bounds it and the vent does not: `enclosure_assembly.pan_front_y` strikes the
forward rim on the barb's own aft edge, by what a hose leaving that barb needs, and
it is the **flange** that arrives at the barb first. The vent then falls where the
chain's own standoff from the back wall leaves it, and
`enclosure_assembly.check_vent_lands` reads its tip back against the floor those two leave,
reporting where the drip lands as the `vent-lands` gate row.

## What the floor carries sets the depth

The moisture plate lies flat down the basin's **depth** — its long edge along
the withdrawal axis, the axis the strip has to give — and the floor's flat area
inside the coves is what it lands on: [54](PLATE_LEN) × [40](PLATE_DEPTH) mm
of plate with [1](PLATE_SLIP_MM) mm of slip a side. `check_plate()` measures that
at every build and hands back the `plate-lies-flat` bound the machine's scorecard
renders as a gate row, because a plate wider than the flat rides up on the coves
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
`enclosure_assembly.pan_rails` stands a rail under each.

**One number for two grips**, and the hand sets it: the west lip is hooked with a
fingertip to draw the tray, and a lip a finger pulls on wants ten. The rail takes
what that lip leaves. One rim runs all four sides at the one figure.

The rails are printed into the enclosure's **back-top piece**, rooted on the −X
wall's inner face and running east under the rim — the axis a rail is laid on is
the axis the thing on it travels. Their two inboard arrises take the tray's two
haunches and hold it on its column.

A **stop bar** closes their east ends — `enclosure_assembly.pan_rails` returns it as the
third of the three members `enclosure._pan_rails` fuses onto the wall — so the three
members are one U and how far the tray goes in is a face and not a judgement. The
bar stands in the pocket the flange overhangs its basin by, at the rails' own
height, so the **rim rides over it** the way it rides the rails and what comes to
rest against it is the **haunch**, one `drip_pan.PAN_SLIP` off the bar's west
flank. The bar runs the rim's whole width because both rails are its only root —
it is fused to the −X wall through them and through nothing else, and a bar short
of them is a solid hanging in air. The plan arcs carry the tray clear of it at
both ends: r[16](PAN_RIM_CORNER_R) rounds the rim and the haunch rounds the
section beneath, so what butts is the straight run between those arcs.

Service is one motion — **draw the tray west**, out through the slot in that same
wall (`enclosure_assembly.west_wall_ports`). The slot is the tray's own silhouette: rim-wide
above the flange's underside, haunch-wide below it. The step between the two is the
wall the rails stand on.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/drip-pan/drip_pan.py`
