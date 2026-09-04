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

The source fitting's release sleeve is [9.57 mm](COLLET_D) OD with a
[6.69 mm](COLLET_BORE) bore and a [1.44 mm](COLLET_WALL) annular wall. The
tool therefore gives each straight jaw [1.51 mm per side](JAW_COVER) of radial
land: enough to span the sleeve wall while leaving the tube free. The two arms
and rounded root load the collet broadly and symmetrically. Its measured
release stroke is [1.335 mm](COLLET_TRAVEL).

The head is [38 mm](HEAD_W) wide and [9.60 mm](HEAD_T) thick. Both fork arms
are parts of that same slab; the entire unobstructed jaw face is the pressing
surface.

## Handle and print orientation

The [104 mm](HANDLE_L) long by [24 mm](HANDLE_W) wide handle lies flat on the
print bed and is [9.60 mm](HANDLE_T) thick. The head rises from its buried,
full-width root at [45°](HEAD_ANGLE). That gives the angled reach at the
fitting, keeps the rising underside self-supporting, and puts the collet load
across the horizontal layer stack instead of directly along it.

Print the exported orientation without supports. The bounding envelope is
[134.9 mm](TOOL_X) by [38.0 mm](TOOL_Y) by [53.5 mm](TOOL_Z), containing
[40.3 cm³](TOOL_VOLUME) of material. PET-GF through a 0.4 mm nozzle at
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
