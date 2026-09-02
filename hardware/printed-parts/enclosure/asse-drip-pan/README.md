# ASSE drip pan

Printed catch pan for the service bay, standing under the ASSE 1022 chain's
atmospheric-vent tip. The Shutao moisture probe lies flat in it; any vent drip,
condensate, or overflow pools in the pan and wets the probe, tripping the
moisture alarm. The probe's leads never leave the pan: they run inside it to a
magnetic pogo dock in the pan's east wall, and the pan's own travel mates that
dock with its other half in the sleeve's backstop.

One part prints here: the **pan**. It carries one bought part, the female half of the
[JHYOSSTHI 2-pin magnetic pogo pair](/hardware/reference/jhyossthi-pogo-dock/).

| | pan |
|---|---|
| type | printed PETG, open-top watertight |
| outer | [51](PAN_LEN) × [76](PAN_DEPTH) × [15](PAN_HEIGHT) mm at the walls |
| over the rim | [59](PAN_RIM_LEN) × [84](PAN_RIM_DEPTH) mm at the flange |
| section | [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR) mm floor |
| capacity | [39.2](PAN_CAPACITY) mL to the rim |
| dock | [14.5](DOCK_PILL_L) × [4](DOCK_PILL_W) mm pill in the east wall, pads flush in its outer face, [9](DOCK_Z_MM) mm up |

One plan outline at r[6](PAN_CORNER_R), and everything is that outline at its own
offset — floor slab and walls on the outline itself, the flange on the outline
plus [4](PAN_FLANGE) mm, the cavity on the outline less one wall. A corner is the
same corner at every height. Inside, a filleted floor-to-wall cove
(r[2](PAN_COVE_R)). No drain — the pan holds drips and is emptied on service.

Frame: +X across the strip — the withdrawal axis — +Y depth, +Z up; origin at
the pan's lower-front-left outer corner of the walls, the flange reaching one
flange width outboard of it on both plan axes. Open top.

The pan is narrow across and deep down. X is the loft's contested axis: east of
the sleeve the west column's crossing ladder climbs rung over rung, and the
sleeve's backstop is that ladder's lid. Y is the axis with room to spare — the run
between the SeaFlo's back face and the foam cap's rear edge is deeper than the
pan needs.

## The chain's column

The column reads DOWN from the chain, and the pan follows it rather than
bounding it. `enclosure_assembly.build_asse` stands the chain on the panel deck's
own storey — the storey its union crosses the +Y wall of back-top on — and
[4](PAN_VENT_GAP) mm of splash-and-service air hangs under its underside. What
takes station there is the **sleeve's lid**, the topmost thing in this column;
`enclosure_assembly.pan_rim_z` then puts the rim one lid and one slip below it and
`enclosure_assembly.pan_floor` hangs the floor one pan height under that. The chain
is rolled about its own flow axis, so its underside is a body corner and the vent
stub's tip stands above it, leaning aft.

That column stands the whole pan high over the SeaFlo's **bracket**, whose feet are
the widest section the casting has. What the sleeve meets at its own height is the head
block, and `enclosure_assembly.FOOT_CLEAR` is what it keeps off it.

The plan station is not posed by hand either.
In X the pan hangs off the **wall it comes out through** — `enclosure_assembly.pan_west_x`
puts its west lip one `PAN_PROUD` outside the −X wall's own outer face — and the sleeve's
backstop takes what the rim leaves, which `enclosure_assembly.check_pan_lane` measures
against the pump's casting. In Y the pump's discharge bounds it and the vent does not:
`enclosure_assembly.pan_front_y` strikes the **sleeve's** forward face on the barb's own aft
edge, by what a hose leaving that barb needs. The vent then falls where the
chain's own standoff from the +Y wall of back-top leaves it.

## What the floor carries, and how high the walls stand

The moisture plate lies flat down the pan's **depth** — its long edge along
the withdrawal axis, the axis the strip has to give — and the floor's flat area
inside the coves is what it lands on: [54](PLATE_LEN) × [40](PLATE_DEPTH) mm
of plate with [1](PLATE_SLIP_MM) mm of slip a side. `check_plate()` measures that
at every build and hands back the `plate-lies-flat` bound the machine's scorecard
renders as a gate row, because a plate wider than the flat rides up on the coves
instead of lying down and the water has to stand that much deeper before it
reads. That requirement is what sets the pan's Y, and what the SeaFlo's
station forward of it makes room for.

The **height** answers to the trip the pan makes full. The probe reads a pool a
millimetre deep, so the alarm is out long before the pan is; what
[15](PAN_HEIGHT) mm stands is [12](PAN_WATER_DEPTH) mm of wall over the water while the pan
is drawn west down its slot, clear of the wall, and carried away to be poured out. It hangs
DOWN from a rim the chain fixes, into the strip of air over the SeaFlo's casting.

## The carry is a sleeve

The pan is a drawer and the **sleeve** is its carcase: one solid block of the
enclosure's own material, printed into the **back-top piece** and rooted on the −X
wall's inner face over the whole of its west end. It runs the pan's rim plus one
`asse_drip_pan.PAN_SLIP` and one wall section every way, so its floor, its two flanks
and its lid are each one flat unbroken surface.

`enclosure_assembly.pan_sleeve` states it as that block and the cuts that take the
**berth** back out of it, and `enclosure._pan_sleeve` fuses then cuts. The berth is
the pan's own section, and the pan's section is two rectangles: the pan's body
below the flange, and the rim standing [4](PAN_FLANGE) mm out either side of it at
the top. Between the floor and the flange the wall's outside is a single vertical
face — the pan is a plain box and the berth is a plain slot.

**The floor carries it.** The pan lies on the block's floor across its whole
footprint, so nothing bears on the rim and nothing hangs off the wall. What the
lid does is close back over the flange, [3.70](PAN_LAP) mm of it a side
(`lap_w()`), which is what makes this a **mount** rather than a shelf: the pan
cannot lift out of its berth. Over the pan's mouth that lid is open, so the
drip falls straight through it.

**The backstop is the block.** East of where the pan's own outline ends, the
sleeve is solid floor to lid, so how far the pan goes in is a face of that full
section. The pan's east wall meets it below the flange and the east rim meets it
above, each one slip off its own.

Service is one motion — **draw the pan west**, out through the slot in that same
wall (`enclosure_assembly.west_wall_ports`, cut on the same two rectangles as the
berth). The pan's west end stands `enclosure_assembly.PAN_PROUD` outside the
machine's skin. That exposed end is one full-height chamfered pull face over the
pan's [84](PAN_RIM_DEPTH) mm rim width and [15](PAN_HEIGHT) mm height. It reaches
[5.7](PULL_FACE_DEPTH) mm back from the outer plane, leaving one running-fit slip
to the enclosure skin, so the face masks the two-level wall slot without becoming
the insertion stop. Its [2.5](PULL_FACE_CHAMFER) mm corners rise at 45 degrees from
the print bed. Thumb on the flange's top, fingertip under the floor, and it comes.

## The dock

The plate's two leads run inside the pan — along the floor and up the east wall — to
the **female half** of the magnetic pogo pair, potted in the east wall with its two pads
flush in the wall's outer face, [9](DOCK_Z_MM) mm up from the floor's underside on the
pan's centreline. Its window is cut through the outer [1](DOCK_NOSE_T) mm of wall on the
nose's own outline, and its flange sits in a pocket through the rest of the wall and one
[1.5](DOCK_BOSS_MM) mm boss stood into the cavity behind it, [17.7](DOCK_BOSS_RUN) mm
along the wall; each section is one [0.1](DOCK_SLIP_MM) mm slip larger than the pill.
The step between window and pocket is the nose's shoulder, so the wall's own material is
what the magnets pull the pill against. The pill goes in from the cavity, nose first,
until those shoulders stop it; its two tails then stand [1.5](DOCK_TAIL_L) mm proud of the
boss on the pins' [2.5](DOCK_PIN_PITCH) mm pitch, the leads solder to them there, and the
pocket's mouth is potted over the joints.

The **male half** stands in the sleeve's backstop looking west at the pads
(`enclosure_assembly.build_dock`, `enclosure_assembly.pan_sleeve`), its nose one slip
behind the face the pan rests on, so the backstop and not the connector is what the pan
comes to rest against. Sliding the pan home brings the pads onto the pins, and the
pair's magnets hold the pan on the backstop from then on. Drawing the pan west parts
them. The pan leaves the machine with its plate, its leads and its dock aboard, and
nothing trails it out; the plate is tethered to the wall by its own leads and comes back
in the pan it left in.

The boss stands **over** the plate's east edge and never on it: its underside is a 45°
chamfer off the wall, and `check_dock_clears_plate()` measures that chamfer against the
plate's top east edge with the plate slid its whole slip east — [0.92](DOCK_PLATE_CLEAR_MM) mm
here, against a floor of [0.5](DOCK_PLATE_CLEAR_MIN). The height is bounded from above
too: the male's pocket in the backstop keeps [1.10](DOCK_ROOF_MM) mm of block under the rim
rebate's floor, against a floor of [1](DOCK_ROOF_MIN) (`check_dock_roof()`). Both are gate
rows on the machine's scorecard beside `plate-lies-flat`.

Below the pocket's sill the pan is the watertight box it was: [3.9](DOCK_SILL) mm of water
over the floor, [12.7](DOCK_SILL_ML) mL, before the pool reaches the potting — four times
the millimetre the plate trips on. Above the sill it is the potting and not the wall that
holds the water, up to the [39.2](PAN_CAPACITY) mL the rim stands over.

What the dock does not read: a pan drawn out parts the pads from the pins, and open pads
read the same as a dry plate. The machine sees a dry pan whether the pan is in or out.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/asse-drip-pan/asse_drip_pan.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/asse-drip-pan/asse_drip_pan.py`
