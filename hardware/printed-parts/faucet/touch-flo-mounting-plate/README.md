# Touch-Flo mounting plate

Printed PETG disc that supports the harvested Touch-Flo faucet body
and the two flavor tubes that pass alongside it. Mates against the
countertop top surface via the TPU mounting gasket below it.

## Geometry

- **Ø [54.35 mm](PLATE_D), [4 mm](PLATE_T) thick disc.**
- Plate spans Z from [-4](PLATE_Z_BOTTOM) to 0 in world coords; top
  face flush with the deck plane (= body bottom in the faucet-assembly).
- Plate center at world (0, +[3.175 mm](PLATE_Y)) — offset toward the
  back of the appliance. Body sits at world (0, 0).

## Holes

1. **Shank hole** — Ø [12.6 mm](SHANK_HOLE_D) at world (0, 0). Clears
   the [11 mm](SHANK_OD) threaded shank.
2. **Flavor-tube pill slot** — at world (0, +[18.93 mm](PLATE_FLAVOR_Y)),
   oriented along X. Two 1/4" tubes [6.35 mm](TUBE_CENTER_X) apart
   center-to-center (lateral), combined into a single rounded-rectangle:
   - Length (X, lateral): [13.4 mm](PLATE_PILL_L)
   - Width (Y, depth): [7.05 mm](PLATE_PILL_W)

The plate is held to the shell by gravity during sub-assembly handling
and by the shank-nut clamp (body → plate → TPU gasket → countertop)
once the under-counter install finishes.

## Top-outer edge fillet

[2 mm](TOP_FILLET_R) fillet on the top outer edge.

## Regenerate

```
tools/cad-venv/bin/python touch_flo_mounting_plate.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/touch-flo-mounting-plate/touch_flo_mounting_plate.py`
