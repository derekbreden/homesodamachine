# Touch-Flo mounting plate

Printed PETG disc that supports the harvested Touch-Flo faucet body,
the two flavor tubes that pass alongside it, and (eventually) the
shell that wraps around the assembly. Mates against the countertop
top surface via the TPU mounting gasket below it.

## Geometry

- **Ø [54.35 mm](PLATE_D), [4 mm](PLATE_T) thick disc** — sized so the
  plate's edge sits [5 mm](PLATE_TO_SHELL_GAP) out from the shell
  base's outer cylinder (Ø [44.35 mm](SHELL_OUTER_D) =
  `SHELL_OUTER_R × 2`). [5 mm](PLATE_TO_SHELL_GAP) matches the standard
  wall / margin elsewhere in the shell. The factory plate was Ø 44.5;
  this is bigger.
- Plate spans Z from [-4](PLATE_Z_BOTTOM) to 0 in world coords; top
  face flush with the deck plane (= body bottom in the faucet-assembly).
- **Plate center at world ([3.175 mm](PLATE_X), 0)** — the midpoint of
  the assembly's lateral footprint at Z = 0 with 1/4" flavor tubes:
  - −X edge: body cylindrical base at X = −15.75 mm
  - +X edge: outer wall of the +X flavor tube at X = +22.10 mm
  - midpoint: +[3.175 mm](PLATE_X)

  This puts the body at world (0, 0) shifted −[3.175 mm](PLATE_X) in X
  relative to the plate center, by design. Plate center matches the
  shell's `SHELL_CENTER_X` for concentric stack-up.

## Holes

1. **Shank hole** — Ø [12.6 mm](SHANK_HOLE_D) at world (0, 0). Matches
   the factory mounting plate's clearance for the [11 mm](SHANK_OD)
   threaded shank (~[14.5%](SHANK_CLEARANCE_PCT) diametric clearance).
2. **Flavor-tube pill slot** — at world
   ([18.925 mm](PLATE_FLAVOR_X), 0), oriented along Y. Per-tube Ø
   would be [7.05 mm](FLAVOR_HOLE_D) (= [6.35 mm](FLAVOR_TUBE_OD) OD
   + [0.7 mm](FLAVOR_HOLE_CLEARANCE) clearance applied to the 1/4"
   flavor tubes), but the two tubes are only
   [6.35 mm](TUBE_CENTER_Y) apart center-to-center, so the per-tube
   circles overlap by ~[0.7 mm](TUBE_OVERLAP). We model the combined
   opening as a single pill (rounded-rectangle) slot for cleaner
   printability:
   - Length (Y, end-to-end): [13.4 mm](PLATE_PILL_L)
   - Width (X): [7.05 mm](PLATE_PILL_W)

No plate-to-shell retention or alignment features. The plate is a
clean disc with only the shank hole + pill slot through it; the
shell's bottom face is similarly clean. Earlier revisions tried
screws+heat-set retention and then printed-boss press-fit alignment;
both were abandoned (see the joinery history in `ASSEMBLY.md`). The
plate is held to the shell by gravity during sub-assembly handling
and by the shank-nut clamp (body -> plate -> TPU gasket ->
countertop) once the under-counter install finishes.

## Stack thickness

The plate thickness was initially [5 mm](PREV_PLATE_T); trimmed by
[1 mm](PLATE_TRIM) to the current [4 mm](PLATE_T) to free shank thread
engagement for the under-counter nut once the [2 mm](GASKET_T) TPU
gasket is in the stack.

## Top-outer edge fillet

A [2 mm](TOP_FILLET_R) fillet on the top outer edge softens the
visible ring around the body once the plate is installed.
[2 mm](TOP_FILLET_R) on a [4 mm](PLATE_T) plate
(~[50%](FILLET_RATIO) of thickness — half-bullnose, half-flat side)
reads as an intentional finished edge without eating the flat
landing area the body and shell sit on.

## Regenerate

```
tools/cad-venv/bin/python generate_step_cadquery.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/touch-flo-mounting-plate/generate_step_cadquery.py`
