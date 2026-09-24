# Tee carrier

One PET-GF plate, `enclosure-tee-carrier-plate`, carries Y-C, Y-D, Y-F and Y-G across the front
column. It is [215 mm](LENGTH) long, flank face to flank face, so neither end stands past the
enclosure. Two window covers close the flank openings aft of it.

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

Each column's end face is flush with its flank and is show face. All four of its edges, and the
column's four edges running inboard to it, roll over on the enclosure's [6 mm](SHOW_EDGE_R)
shoulder, the radius of the enclosure's own side edges, so each corner closes as one blend the
way the enclosure's front corners do. The plate joins each column at the column's inboard face;
the plate's back is flush with the column's and its underside stands just over the column's, so
the plate's square bottom-aft corner stands out past the column's rounded one there. Each end
face is smooth within its rounded edges.

The plate prints lying on its back, troughs open upward; the columns stand out in the plane of
the bed, and their aft shoulders rise off it.

The plate prints without supports. Its visible end rounds use 0.08 mm layers through their
full height, including the first layer, and the remaining height uses 0.24 mm. The completed
Mark2 v11 print has a clean upper curve and localized curling on the lower curve around
layers 20–30, with recovery while still at 0.08 mm. The v12 fan-off configuration, at the
same 265°C first layer, 280°C subsequent layers and 80°C bed, is rejected: Derek reports
markedly worse results. The [physical record](physical-acceptance.json) and
[v11 photos](physical-observations/2026-09-24-v11/README.md) identify the trials.
The lower curve's finish and failure mechanism remain under evaluation.

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
[27 mm](SPRING_FREE) free and about [7 mm](SPRING_SOLID) solid. Each runs in
[6.5 mm](SPRING_BORE_D) tunnels on both sides of the [2.15 mm](SPRING_GAP) gap between the column
and the tee wall: a blind bore [14.204 mm](SPRING_BORE_DEPTH) deep in the column's fore face, and a
pocket [3.846 mm](SPRING_POCKET_DEPTH) deep in the tee wall's aft face, teardropped over its crown
for front-top's mouth-down print.

The column's bore is as deep as keeps a free spring's tip [12.796 mm](SPRING_STAGED_REACH) out of
it, no further fore of the staged column than the branch noses; the pocket takes the rest of the
spring's [20.2 mm](SPRING_CONNECTED) connected length. Each bore keeps [3 mm](SPRING_SIDE_WALL) of
column inboard of it; outboard, a [1.4 mm](SPRING_LAND) land of flat fore face stands between its mouth
and the end face's shoulder, and the round thickens the wall from there. The two in a column
stand [21.2 mm](SPRING_SPREAD) apart, one either side of the tees' run axis, the lower's mouth the same
land clear of the column's rounded bottom edge.

Connected, each spring is [20.2 mm](SPRING_CONNECTED) long,
[6.8 mm](SPRING_CONNECTED_COMPRESSION) short of free; with every collet pressed home it is
[18.2 mm](SPRING_RELEASE) long, [8.8 mm](SPRING_RELEASE_COMPRESSION) short of free.

## Window covers

Aft of the seated carrier each window stands open [12.146 mm](WINDOW_AFT) to its aft face. A
window cover closes that from inside the flank: `enclosure-window-cover-west` and
`enclosure-window-cover-east`, mirror images, each a PET-GF slab [6 mm](COVER_T) thick with its
outboard face on the flank's inner face.

Front-top carries a post for each on the flank's inner face at the window's aft face,
[6 mm](POST_W) across, [12 mm](POST_D) aft and [43.996 mm](POST_H) tall. It stands from where the flank's own face begins
over the seam channel up to the window's roof, and its underside is a 45° corbel on the same
plane as the flank's underside below it. Its top half is slotted against the flank,
[3 mm](SLOT_W) wide and [21.998 mm](SLOT_H) deep, so a finger as wide stands inboard of the
slot.

The cover's [2.85 mm](TONGUE_T) tongue drops into the slot and hangs
[0.25 mm](TONGUE_AIR) over its floor: the slip, and [0.1 mm](LAYER_TRANSITION) more for the
floor's rounded turn up into the slot's walls. The slab stands on the window's floor, which is
front-bottom's seam rail where the window cuts it, and its face lies on the flank; a
[0.15 mm](SLIP) slip stands between the cover and the post everywhere else. Fore of the post the
slab reaches [11.846 mm](COVER_FORE), to a slip aft of the seated carrier's back, and stands the
window's full height, [60.122 mm](COVER_H). Aft of the post it reaches
[12 mm](COVER_AFT) at the post's height, so post and cover stand [24 mm](STRUCTURE_AFT) aft of the
window. The finger stands between the two, so a cover lifts off
only straight up.

Each cover prints lying on its outboard face.

## Assembly

The carrier goes in before both valve rows: its staged pass crosses the coils of V-C, V-D, V-G
and V-J, and the +X column's crossing the bodies of V-E, V-F, V-H and V-I.

1. Tie the four bare tees into the troughs, branches fore. No tube is in any tee.
2. Enter the plate through the −X flank opening [10.896 mm](STAGED_DY) aft of its seat, where
   every branch nose passes [0.25 mm](AIR) behind the tee wall's aft face.
3. With a spring in each of the four column bores, slide the plate fore
   [10.896 mm](STAGED_DY). Each branch enters its journal in the tee wall, and each spring's tip
   enters its pocket and bottoms there.
4. After V-G and V-J and before V-F and V-I, lower each window cover onto its post, tongue into
   the slot.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py`
