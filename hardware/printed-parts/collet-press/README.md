# Collet press

The one-piece PET-GF hand tool that releases a 1/4-inch John Guest
push-to-connect fitting. Its U-jaw slips around the tube and its single flat
face pushes the release sleeve squarely into the fitting. There is no stepped
lip, moving part, insert, screw, or second jaw.

## Working head

The constant-width U-slot is [6.55 mm](JAW_GAP) across. That leaves
[0.20 mm](TUBE_CLEARANCE) diametral clearance around the nominal
[6.35 mm](TUBE_D) tube: close enough to center the tool without asking the
printed slot to snap over the tube.

With the tube seated in the semicircular bottom, the straight portion of the U
is [8.06 mm](JAW_DEPTH) deep. Its inner lands continue through the collet's
forward outside edge, then [2.0 mm](TIP_R) corner radii form the noses without
leaving sharp 90-degree tips. That extra [1.61 mm](STRAIGHT_OVERRUN) beyond the
tube's forward tangent keeps every part of the annular release face reachable
by the two arms under their straight section.

The source fitting's release sleeve is [9.57 mm](COLLET_D) OD with a
[6.69 mm](COLLET_BORE) bore and a [1.44 mm](COLLET_WALL) annular wall. The
tool therefore gives each straight jaw [1.51 mm per side](JAW_COVER) of radial
land: enough to span the sleeve wall while leaving the tube free. The two arms
and rounded root load the collet broadly and symmetrically. Its measured
release stroke is [1.335 mm](COLLET_TRAVEL).

The head is [20 mm](HEAD_W) wide and [6.00 mm](HEAD_T) thick. Each arm is
[6.725 mm](ARM_W) wide before its rounded tip. Both arms are parts of the same
slab; the entire unobstructed jaw face is the pressing surface.

## Handle and print orientation

The handle gives [96 mm](HANDLE_L) of bottom bed edge, is
[20 mm](HANDLE_W) wide, and is [6.00 mm](HANDLE_T) thick. Its front is cut on
the head's same [45°](HEAD_ANGLE) underside plane, so no horizontal nose or
shelf projects past the bend. Head and handle are one constant-width,
constant-thickness strip with square side edges through that crease; there is
no shoulder or corner rounding at the transition. The opposite end of the
handle uses the same [2.0 mm](TIP_R) corner radius as the fork tips. Only
[6.725 mm](HEAD_BACK_LAND)—one arm width—of angled material remains behind
the bottom of the U. The root sits [4.24 mm](ROOT_BURY) into the handle,
stopping before the tube path. This gives the angled reach at the fitting,
keeps the rising underside self-supporting, and puts the collet load across the
horizontal layer stack instead of directly along it.

Print the exported orientation without supports. The bounding envelope is
[109.6 mm](TOOL_X) by [20.0 mm](TOOL_Y) by [17.9 mm](TOOL_Z), containing
[13.1 cm³](TOOL_VOLUME) of material. PET-GF through a 0.4 mm nozzle at
0.24 mm layers is the primary print: use at least six walls and a dense core.
A 0.2 mm nozzle at 0.12 mm layers uses the same solid. The handle's complete
underside is the bed face; add a brim only if the printer needs one.

## Use

Drop the slot sideways over the tube, bring the jaw face flat against the
collet, and push the handle toward the fitting while pulling the tube free.
Depressurize the line before disconnecting it.

## Regenerate

```sh
tools/cad-venv/bin/python hardware/printed-parts/collet-press/collet_press.py
```

This writes `collet-press.step`, `collet-press.stl`, and the generated figure
values in this README. The measured release geometry comes from
[`reference/jg-pp0408w`](/hardware/reference/jg-pp0408w/jg_pp0408w.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/collet-press/collet_press.py`
