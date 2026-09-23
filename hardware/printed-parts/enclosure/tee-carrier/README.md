# Tee carrier

Two PET-GF parts carry Y-C, Y-D, Y-F and Y-G across the front column.
`enclosure-tee-carrier-plate` is the plate and the −X handle; `enclosure-tee-carrier-grip` is
the +X handle alone. Neither stands past the enclosure's flanks: the plate is
[215 mm](LENGTH) long, flank face to flank face.

## Plate

The plate is [11.5 mm](PLATE_T) thick and [39.2 mm](PLATE_H) tall, the tee's
[39.2 mm](RUN_SPAN_PRESSED) run span with both sleeves pressed, so the plate ends where a
pressed run collet's face does.

Each tee's run axis lies on the plate's fore face, and its barrel sits half inset in a vertical
[17 mm](TROUGH_D) trough: the [16.5 mm](BARREL_D) collar envelope with
[0.25 mm](AIR) radial air. [3 mm](BACKING) of plate stands behind every trough; the troughs
and the tie slots are all that break the plate's section.

Two ties hold each tee, one at each tie band [8.35 mm](TIE_BAND) above and below its run axis,
round the run roots either side of the branch. Each band has a
[2 mm](TIE_SLOT_X) × [3.5 mm](TIE_SLOT_Z) slot through the plate on each side of the trough,
[3 mm](BACKING) out from the trough's edge. The tie passes through one slot, crosses the plate's
back, returns through the other and closes round the tee's front. Its
[1 mm](STRAP_T) strap across the back is inside the flank openings.

## Openings and handles

Both front flanks carry the same opening, [35.35 mm](OPENING_Y) in Y by
[45.7 mm](OPENING_Z) in Z, cut straight across the column through front-top's
[9 mm](FLANK_T) flank section and front-bottom's seam rail under it. Its fore face is the tee
wall's aft face; its aft face is the staged plate's strapped back plus [0.25 mm](AIR).

The −X handle fills its flank section from [11.454 mm](HANDLE_FORE) fore of the plate to the
plate's back, [3 mm](GRIP_WALL) above and below the plate. The [11.896 mm](SLIDE_ROOM) of
opening behind it is the slide room. The grip fills the whole +X opening less its air; the
plate's section passes through it line to line and ends flush with the flank.

## Assembly

The carrier goes in before the aft valves: its staged pass crosses the coils of V-C, V-D, V-G
and V-J.

1. Tie the four bare tees into the troughs, branches fore. No tube is in any tee.
2. Enter the plate through the −X flank opening [10.896 mm](STAGED_DY) aft of its seat, where
   every branch nose passes [0.25 mm](AIR) behind the tee wall's aft face.
3. With the handle in its flank, slide the plate fore [10.896 mm](STAGED_DY). Each branch
   enters its journal in the tee wall.
4. Push the grip over the plate's end in the +X flank until it is flush.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py`
