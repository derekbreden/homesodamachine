# Sculpted faucet mounting plate · above counter

Printed PET-GF15 plate supporting the Westbrass above the countertop.
Three recessed M3 screws clamp it to the faucet shell. The three pedestals
align the parts before the screws are tightened. The above-counter gasket
covers the underside and the fasteners when the faucet ships.

[Finished plate engineering drawing](above-counter-plate-drawing.pdf)
(FCT-PLT-02, Rev A) defines the footprint, passages, pedestal locations and
recessed screw seats after support removal. The sheet includes top and front
views and a 5:1 local section. General linear tolerance is ±0.20 mm;
feature-center coordinates are ±0.10 mm, with individual fit and depth limits
shown on the drawing. Gasket-face free-state gap is 0.20 mm maximum.
[above_counter_plate_drawing.py](above_counter_plate_drawing.py) generates
the sheet from the production part's parameters.

## Footprint and bearing

The oval measures [58 mm](FOOT_WIDTH) across X and [59 mm](FOOT_DEPTH)
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
Ø[7.9 mm](PEDESTAL_D) pedestal stands [2.2 mm](PEDESTAL_H) above the plate,
giving a [3 mm](SEAT_T) bearing section above the head. The screw passes
through a Ø[3.9 mm](SHANK_D) clearance hole and into a ruthex M3 short
insert above the shell socket. All heads sit below the gasket-contact face.

The pedestals' [0.4 mm](PEDESTAL_CHAMFER) lead chamfers guide them into
the shell's blind sockets. The plate seats on the shell's full bottom
face; each pedestal has clearance above its tip.

## Tube openings

The flavor pair and 4 mm drain pass through a [18.15 mm](PLATE_PILL_L) ×
[7.25 mm](PLATE_PILL_W) pill slot centered at
([0 mm](PLATE_FLAVOR_X),+[18.93 mm](PLATE_FLAVOR_Y)), with its long axis along X.
The signal-cable clearance is a 5.0 × 1.8 mm capsule centered at
([0 mm](PLATE_RIBBON_X),+[21.4875 mm](PLATE_RIBBON_Y)), with its long axis along X.
This capsule lies entirely within the pill slot. The ribbon stays flat behind
the flavor/drain row through the counter stack.
The rear bundle is centered on X=0, with the drain between the flavors and
the flat ribbon behind it. The matching steel plate admits the complete row
through its open rear channel. The printed passage connects broadly around
the tubes and ribbon.

Route both flavor tubes, the drain and the signal ribbon before closing this
factory joint.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/above-counter-plate/above_counter_plate.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/above-counter-plate/above_counter_plate.py`
