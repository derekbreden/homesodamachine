# Above-counter plate

Printed PET-GF15 plate supporting the Westbrass above the countertop.
Three recessed M3 screws clamp it to the faucet shell. The three pedestals
align the parts before the screws are tightened. The above-counter gasket
covers the underside and the fasteners when the faucet ships.

## Footprint and bearing

The oval measures [65 mm](FOOT_WIDTH) across X and [66 mm](FOOT_DEPTH)
along Y, centered at world (0, [0 mm](PLATE_Y)). The shell and gasket share
this exact perimeter.

The plate is [4 mm](PLATE_T) thick, from Z=[-4](PLATE_Z_BOTTOM) to 0.
The Westbrass's bottom face lands on the top face around the central
Ø[12.6 mm](SHANK_HOLE_D) shank hole. The captive donor nut clamps the
Westbrass, plate, gasket, countertop and existing stainless under-counter
plate together at installation.

## Factory joint

Three M3×[8 mm](SCREW_LENGTH) socket-head screws enter from below. Each
Ø[6.15 mm](CBORE_D) counterbore is [3.2 mm](CBORE_DEPTH) deep. Its
Ø[9.9 mm](PEDESTAL_D) pedestal stands [2.2 mm](PEDESTAL_H) above the plate,
giving a [3 mm](SEAT_T) bearing section above the head. The screw passes
through a Ø[3.9 mm](SHANK_D) clearance hole and into a ruthex M3 short
insert above the shell socket. All heads sit below the gasket-contact face.

The pedestals' [0.4 mm](PEDESTAL_CHAMFER) lead chamfers guide them into
the shell's blind sockets. The plate seats on the shell's full bottom
face; each pedestal has clearance above its tip.

## Tube openings

The flavor pair passes through a [13.6 mm](PLATE_PILL_L) ×
[7.25 mm](PLATE_PILL_W) pill slot centered at
(0,+[18.93 mm](PLATE_FLAVOR_Y)), with its long axis along X.
The connected signal-cable branch is a 5.0 × 1.8 mm capsule centered at
(9.3,17.0). This places the ribbon inside the existing stainless plate's
open flavor channel and the drilled countertop hole. The passage has a
broad connection to the flavor opening so no thin printed fin separates them.

Route both flavor tubes and the signal ribbon before closing this factory joint.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/above-counter-plate/above_counter_plate.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/above-counter-plate/above_counter_plate.py`
