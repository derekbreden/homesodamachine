# Drip pan

Printed catch basin for the service bay, standing under the ASSE 1022 chain's
atmospheric-vent tip. The Shutao moisture probe lies flat in it; any vent drip,
condensate, or overflow pools in the basin and wets the probe, tripping the
moisture alarm.

One part prints here: the **basin**.

| | basin |
|---|---|
| type | printed PETG, open-top watertight |
| outer | [51](PAN_LEN) × [76](PAN_DEPTH) × [15](PAN_HEIGHT) mm at the walls |
| over the rim | [59](PAN_RIM_LEN) × [84](PAN_RIM_DEPTH) mm at the flange |
| section | [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR) mm floor |
| capacity | [39.2](PAN_CAPACITY) mL to the rim |

One plan outline at r[6](PAN_CORNER_R), and everything is that outline at its own
offset — floor slab and walls on the outline itself, the flange on the outline
plus [4](PAN_FLANGE) mm, the cavity on the outline less one wall. A corner is the
same corner at every height. Inside, a filleted floor-to-wall cove
(r[2](PAN_COVE_R)). No drain — the basin holds drips and is emptied on service.

Frame: +X across the strip — the withdrawal axis — +Y depth, +Z up; origin at
the basin's lower-front-left outer corner of the walls, the flange reaching one
flange width outboard of it on both plan axes. Open top.

The basin is narrow across and deep down. X is the loft's contested axis: east of
the sleeve the west column's crossing ladder climbs rung over rung, and the
sleeve's backstop is that ladder's lid. Y is the axis with room to spare — the run
between the SeaFlo's back face and the foam cap's rear edge is deeper than the
basin needs.

## The chain's column

The column reads DOWN from the chain, and the basin follows it rather than
bounding it. `enclosure_assembly.build_asse` stands the chain on the panel deck's
own storey — the storey its union crosses the back wall on — and
[4](PAN_VENT_GAP) mm of splash-and-service air hangs under its underside. What
takes station there is the **sleeve's lid**, the topmost thing in this column;
`enclosure_assembly.pan_rim_z` then puts the rim one lid and one slip below it and
`enclosure_assembly.pan_floor` hangs the floor one basin height under that. The chain
is rolled about its own flow axis, so its underside is a body corner and the vent
stub's tip stands above it, leaning aft.

That column stands the whole tray high over the SeaFlo's **bracket**, whose feet are
the widest section the casting has. What the sleeve meets at its own height is the head
block, and `enclosure_assembly.FOOT_CLEAR` is what it keeps off it.

The plan station is not posed by hand either.
In X the tray hangs off the **wall it comes out through** — `enclosure_assembly.pan_west_x`
puts its west lip one `PAN_PROUD` outside the −X wall's own outer face — and the sleeve's
backstop takes what the rim leaves, which `enclosure_assembly.check_pan_lane` measures
against the pump's casting. In Y the pump's discharge bounds it and the vent does not:
`enclosure_assembly.pan_front_y` strikes the **sleeve's** forward face on the barb's own aft
edge, by what a hose leaving that barb needs. The vent then falls where the
chain's own standoff from the back wall leaves it, and
`enclosure_assembly.check_vent_lands` reads its tip back against the floor those two leave,
reporting where the drip lands as the `vent-lands` gate row.

## What the floor carries, and how high the walls stand

The moisture plate lies flat down the basin's **depth** — its long edge along
the withdrawal axis, the axis the strip has to give — and the floor's flat area
inside the coves is what it lands on: [54](PLATE_LEN) × [40](PLATE_DEPTH) mm
of plate with [1](PLATE_SLIP_MM) mm of slip a side. `check_plate()` measures that
at every build and hands back the `plate-lies-flat` bound the machine's scorecard
renders as a gate row, because a plate wider than the flat rides up on the coves
instead of lying down and the water has to stand that much deeper before it
reads. That requirement is what sets the basin's Y, and what the SeaFlo's
station forward of it makes room for.

The **height** answers to the trip the basin makes full. The probe reads a pool a
millimetre deep, so the alarm is out long before the basin is; what
[15](PAN_HEIGHT) mm stands is [12](PAN_WATER_DEPTH) mm of wall over the water while the tray
is drawn west down its slot, clear of the wall, and carried away to be poured out. It hangs
DOWN from a rim the chain fixes, into the strip of air over the SeaFlo's casting.

## The carry is a sleeve

The tray is a drawer and the **sleeve** is its carcase: one solid block of the
enclosure's own material, printed into the **back-top piece** and rooted on the −X
wall's inner face over the whole of its west end. It runs the tray's rim plus one
`drip_pan.PAN_SLIP` and one wall section every way, so its floor, its two flanks
and its lid are each one flat unbroken surface.

`enclosure_assembly.pan_sleeve` states it as that block and the cuts that take the
**berth** back out of it, and `enclosure._pan_sleeve` fuses then cuts. The berth is
the tray's own section, and the tray's section is two rectangles: the basin's body
below the flange, and the rim standing [4](PAN_FLANGE) mm out either side of it at
the top. Between the floor and the flange the wall's outside is a single vertical
face — the basin is a plain box and the berth is a plain slot.

**The floor carries it.** The basin lies on the block's floor across its whole
footprint, so nothing bears on the rim and nothing hangs off the wall. What the
lid does is close back over the flange, [3.70](PAN_LAP) mm of it a side
(`lap_w()`), which is what makes this a **mount** rather than a shelf: the tray
cannot lift out of its berth. Over the basin's mouth that lid is open, so the
drip falls straight through it.

**The backstop is the block.** East of where the tray's own outline ends, the
sleeve is solid floor to lid, so how far the tray goes in is a face of that full
section. The basin's east wall meets it below the flange and the east rim meets it
above, each one slip off its own.

Service is one motion — **draw the tray west**, out through the slot in that same
wall (`enclosure_assembly.west_wall_ports`, cut on the same two rectangles as the
berth). The tray's west end stands `enclosure_assembly.PAN_PROUD` outside the
machine's skin: thumb on the flange's top, fingertip under the floor, and it comes.

The probe's two leads rise from their holes in the open basin and turn west through
the sleeve's **open-top wall notch**. The notch is on the holes' Y station and crosses
only the withdrawal wall; the basin mouth is already open everywhere inboard of it.
The tray can therefore be drawn without pinching a lead under the lid or dragging a
solder joint across an edge. The sleeve keeps nearly all of its flange lap, and the
basin itself remains uncut and watertight.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/drip-pan/drip_pan.py`
