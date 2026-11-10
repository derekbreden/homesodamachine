# Collet press

The one-piece PET-GF hand tool that releases a 1/4-inch John Guest
push-to-connect fitting. Its U-jaw slips around the tube and its single flat
face pushes the release sleeve squarely into the fitting. There is no stepped
lip, moving part, insert, screw, or second jaw.

## Working head

The constant-width U-slot is across. That leaves
 diametral clearance around the nominal
 tube: close enough to center the tool without asking the
printed slot to snap over the tube.

With the tube seated in the semicircular bottom, the straight portion of the U
is deep. Its inner lands continue through the collet's
forward outside edge, then corner radii form the noses without
leaving sharp 90-degree tips. That extra beyond the
tube's forward tangent keeps every part of the annular release face reachable
by the two arms under their straight section.

The source fitting's release sleeve is OD with a
 bore and a annular wall. The
tool therefore gives each straight jaw of radial
land: enough to span the sleeve wall while leaving the tube free. The two arms
and rounded root load the collet broadly and symmetrically. Its measured
release stroke is.

The head is wide and thick. Each arm is
 wide before its rounded tip. Both arms are parts of the same
slab; the entire unobstructed jaw face is the pressing surface.

## Handle and print orientation

The handle gives of bottom bed edge, is
 wide, and is thick. Its front is cut on
the head's same underside plane, so no horizontal nose or
shelf projects past the bend. Head and handle are one constant-width,
constant-thickness strip with square side edges through that crease; there is
no shoulder or corner rounding at the transition. The opposite end of the
handle uses the same corner radius as the fork tips. Only
—one arm width—of angled material remains behind
the bottom of the U. The root sits into the handle,
stopping before the tube path. This gives the angled reach at the fitting,
keeps the rising underside self-supporting, and puts the collet load across the
horizontal layer stack instead of directly along it.

Print the exported orientation without supports. The bounding envelope is
 by by, containing
 of material. PET-GF through a 0.4 mm nozzle at
0.24 mm layers is the primary print: use at least six walls and a dense core.
A 0.2 mm nozzle at 0.12 mm layers uses the same solid. The handle's complete
underside is the bed face; add a brim only if the printer needs one.

## Use

Drop the slot sideways over the tube, bring the jaw face flat against the
collet, and push the handle toward the fitting while pulling the tube free.
Depressurize the line before disconnecting it.

In [`/3d`](https://homesodamachine.com/3d), arm **Select → Component** and
select any modeled 1/4-inch LLDPE tube. Its component panel offers **Open
collet-press**, preserving the assembly in the breadcrumb while it opens this
tool's STEP. The relation excludes the 3/8-inch faucet tube, refrigerant copper,
foam, and the atmospheric PRV vent because this jaw does not fit them.

## Regenerate

```sh
tools/run -- cargo run --release --manifest-path tools/hsm/collet-press/Cargo.toml
```

This writes `collet-press.step`, its payload and model, and `collet-press.stl`.
[`numbers.rs`](numbers.rs) holds the press's dimensions and the PP0408W figures it is shaped
round, measured off the part in hand ([`reference/jg-pp0408w`](/hardware/reference/jg-pp0408w/)).
