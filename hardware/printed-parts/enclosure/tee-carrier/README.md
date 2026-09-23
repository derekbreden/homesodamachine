# Tee carrier

One PET-GF plate, `enclosure-tee-carrier-plate`, carries Y-C, Y-D, Y-F and Y-G across the front
column. It is [215 mm](LENGTH) long, flank face to flank face, so neither end stands past the
enclosure.

## Plate

The plate is [11.5 mm](PLATE_T) thick and [39.2 mm](PLATE_H) tall, the tee's
[39.2 mm](RUN_SPAN_PRESSED) run span with both sleeves pressed, so the plate ends where a
pressed run collet's face does. At each end, from the outer tee's trough edge out through the
flank, it is a column [16.9 mm](COLUMN_X) wide and [59.372 mm](COLUMN_H) tall that slides on the
opening's floor and roof, and [21.054 mm](COLUMN_Y) deep: it reaches [9.554 mm](COLUMN_FORE) fore of the plate, so that with
every collet pressed home it stands [0.15 mm](SLIP) off the tee wall's aft face.

Each tee's run axis lies on the plate's fore face, and its barrel sits half inset in a vertical
[17 mm](TROUGH_D) trough: the [16.5 mm](BARREL_D) collar envelope with
[0.25 mm](AIR) radial air. [3 mm](BACKING) of plate stands behind every trough; the troughs
and the tie slots are all that break the plate's section.

Two ties hold each tee, one at each tie band [8.35 mm](TIE_BAND) above and below its run axis,
round the run roots either side of the branch. Each band has a
[2 mm](TIE_SLOT_X) × [3.5 mm](TIE_SLOT_Z) slot through the plate at each edge of the trough, its
outboard wall on the trough's edge. The tie closes round the tee's front, drops past the run
root into the slot on each side and crosses the plate's back. Its
[1 mm](STRAP_T) strap across the back is inside the flank openings.

Each column's end face is flush with its flank and is show face. All four of its edges roll over
on the enclosure's [6 mm](SHOW_EDGE_R) shoulder, the radius of the enclosure's own side edges.
The exporter strikes the enclosure's flute field on the face at the connected pose, so its
grooves register with the flank's and fade short of the face's edges the same way.

The plate prints lying on its back, troughs open upward; the columns stand out in the plane of
the bed, and each end face's aft shoulder rises off the bed.

## Openings and travel

Each front flank carries a window [35.35 mm](OPENING_Y) in Y by [60.122 mm](OPENING_Z) in Z
through front-top's [9 mm](FLANK_T) flank section and front-bottom's seam rail under it. Its
fore face is the tee wall's aft face; its aft face is the staged plate's strapped back plus
[0.25 mm](AIR). Its floor stands [0.25 mm](AIR) under the tees' extended run span and the
columns. Its roof is the root of the fore valve tray's corbel on the tee wall's aft face; it
prints facing down over support in front-top, so it stands [0.5 mm](ROOF_AIR) over the columns: the running air and a
supported face's [0.25 mm](SUPPORTED).

Between the flanks the same cutter is the tees' sweep, [43 mm](TEE_SWEEP_Z) tall across the
window's depth, and the +X column's crossing at the staged plate, floor to roof. Inside the
column it cuts only front-bottom's seam rail.

The assembly shows the tees connected: each branch collet extended, its nose
[0.5 mm](NOSE_GAP) off the tee wall's release face. Pressing every collet home takes the plate
[2 mm](RELEASE_TRAVEL) fore, that air and the [1.5 mm](COLLET_STROKE) stroke; the windows
leave the columns [2.15 mm](FORE_ROOM) fore.

## Springs

Four return springs, two in each column, push the carrier aft off the tee wall. Each is a
uxcell 304 stainless spring, [0.8 mm](SPRING_WIRE) wire, measured at [6 mm](SPRING_OD) OD,
[27 mm](SPRING_FREE) free and about [7 mm](SPRING_SOLID) solid. Each stands in a blind
[6.5 mm](SPRING_BORE_D) bore [18.054 mm](SPRING_BORE_DEPTH) deep in the column's fore face,
centred in the width the fore face keeps square inboard of its shoulder, with
[2.2 mm](SPRING_SIDE_WALL) of column either side at the mouth and [3 mm](BACKING) behind its
floor, and bears on the tee wall's aft face. The two in a column stand
[30 mm](SPRING_SPREAD) apart, one either side of the tees' run axis, the lower over a
[3 mm](BACKING) floor.

Connected, each spring is [20.204 mm](SPRING_CONNECTED) long,
[6.796 mm](SPRING_CONNECTED_COMPRESSION) short of free; with every collet pressed home it is
[18.204 mm](SPRING_RELEASE) long, [8.796 mm](SPRING_RELEASE_COMPRESSION) short of free.

## Assembly

The carrier goes in before both valve rows: its staged pass crosses the coils of V-C, V-D, V-G
and V-J, and the +X column's crossing the bodies of V-E, V-F, V-H and V-I.

1. Tie the four bare tees into the troughs, branches fore. No tube is in any tee.
2. Enter the plate through the −X flank opening [10.896 mm](STAGED_DY) aft of its seat, where
   every branch nose passes [0.25 mm](AIR) behind the tee wall's aft face.
3. With a spring in each of the four bores, slide the plate fore [10.896 mm](STAGED_DY). Each
   branch enters its journal in the tee wall, and each spring meets the tee wall's aft face.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py`
