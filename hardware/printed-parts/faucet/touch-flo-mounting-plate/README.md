# Touch-Flo mounting plate

Printed PET-CF plate that supports the harvested Touch-Flo faucet body and
the two flavor tubes beside it, and carries the three screw bosses that
bolt up into the shell. Mates against the countertop top surface via the
TPU mounting gasket below it.

## Footprint

Matches the shell foot exactly — the foot circle plus the two lateral
teardrop pods and the front D-pod — so the plate edge runs flush under the
shell with no ledge. Built by reusing the shell's own outline geometry.

- [4 mm](PLATE_T) thick; spans Z from [-4](PLATE_Z_BOTTOM) to 0, top face
  flush with the deck plane (= body bottom in the faucet-assembly).
- Centered at world (0, +[3.175 mm](PLATE_Y)); body axis at world (0, 0).

## Screw bosses

One at each pod center (both laterals + the front), so the plate clamps to
the shell through all three pods. Each boss is a [12.15 mm](BOSS_D) ⌀
cylinder rising [7 mm](BOSS_H) from the plate top into the shell's boss
hole — shy of the hole floor (the gap absorbs the hole ceiling's bridge
sag, insert squeeze-out, and layer-1 lips) so the plate seats on the foot,
not the boss. A [0.6 mm](BOSS_CHAMFER) × 45° lead-in chamfer rings each top
rim, easing all three pins into their holes at once. Each is bored for an
M3×12 stainless SHCS:

- [6.15 mm](CBORE_D) ⌀ counterbore through the full plate. The head bears on
  the boss base and stays recessed clear of the gasket.
- [3.9 mm](SHANK_D) ⌀ shank clearance up through the boss to the shell's
  ruthex heat-set insert.

## Holes

1. **Shank hole** — Ø [12.6 mm](SHANK_HOLE_D) at world (0, 0). Clears the
   [11 mm](SHANK_OD) threaded shank.
2. **Flavor-tube pill slot** — at world (0, +[18.93 mm](PLATE_FLAVOR_Y)),
   oriented along X. Two 1/4" tubes [6.35 mm](TUBE_CENTER_X) apart
   center-to-center (lateral), combined into a single rounded-rectangle:
   - Length (X, lateral): [13.4 mm](PLATE_PILL_L)
   - Width (Y, depth): [7.05 mm](PLATE_PILL_W)

The plate is held to the shell by the three pod screws, and to the
countertop by the shank-nut clamp (body → plate → TPU gasket → countertop)
once the under-counter install finishes.

## Regenerate

```
tools/cad-venv/bin/python touch_flo_mounting_plate.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/touch-flo-mounting-plate/touch_flo_mounting_plate.py`
