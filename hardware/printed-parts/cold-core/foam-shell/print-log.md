# foam-shell print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis — analysis lives in the conversation, decisions land in the geometry.

Geometry: the full cold-core foam shell, one object `foam-shell.step` from [`foam_shell.py`](/hardware/printed-parts/cold-core/foam-shell/foam_shell.py). Outer footprint 283 × 181 mm, 213.4 mm tall, 2 mm walls/floor. README is the geometry source-of-truth.

## Print attempt 1 (settings per [`foam-shell-8mm-high-flow.3mf`](foam-shell-8mm-high-flow.3mf))

First full foam-shell print. Used the part-proving foam shell for the reservoir watertight test (held water with gaskets — see [`../reservoir/print-log.md`](/hardware/printed-parts/cold-core/reservoir/print-log.md) attempt 3).

Settings — **stock Bambu defaults** for the hotend + filament, no anti-warp tuning:
- Printer: Bambu Lab H2C, 0.8 mm nozzle; profile `0.40mm Standard @BBL H2C 0.8 nozzle`
- Filament: `Bambu PETG Basic @BBL H2C`, **black**
- `layer_height` 0.4 mm (initial 0.4); `line_width` 0.82 mm
- `wall_loops` 2 (classic); top/bottom shells 4/3; `sparse_infill_density` 15 % grid
- `nozzle_temperature` 250 °C (initial 245); `hot_plate_temp` 70 °C, textured PEI; `chamber_temperatures` 0 (passive)
- `filament_flow_ratio` 0.97; `filament_max_volumetric_speed` 21 mm³/s
- Fan min/max 20/40 %, overhang 90 % at ≥10 %, fan off first 3 layers
- `brim_type` auto_brim, `brim_width` 5 mm, `brim_object_gap` 0.1 mm

The 3mf is a saved project (not sliced — no G-code member). Auto-brim is the profile default; whether it generated a brim is not captured in the saved project, and no brim was observed on the printed part.

### Result — corner warp

Derek said:
- The corners raised up over the course of the print and are raised now.
- From the timelapse (not watched live; black PETG + shadows make it hard to read): the corners *appear* to start raising somewhere around layer 50–100, raise over several layers, then hold at that raised amount for the rest of the print. Estimates may be off; the corners may have raised instantly.

Otherwise "nearly everything was perfect."

## Print attempt 2 (sliced, settings per [`foam-shell-8mm-high-flow.3mf`](foam-shell-8mm-high-flow.3mf))

`foam-shell.step` at geometry commit `9a417017`: rounded outer corners (12 mm), cylindrical bosses tangent to the exterior wall with teardrop corner-fill webs, four corner gussets (z 2–42). Cap + gasket pads share the boss shape. Geometry in [`README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md); construction in [`../_outer_shell.py`](/hardware/printed-parts/cold-core/_outer_shell.py); the four corner gussets were defined in `_corner_gussets.py` at that commit.

Settings observed (same stock profile as attempt 1):
- Profile `0.40mm Standard @BBL H2C 0.8 nozzle`, dual 0.8 mm nozzle; `Bambu PETG Basic`, black
- `layer_height` 0.4 / initial 0.4; `line_width` 0.82; `wall_loops` 2 classic; top/bottom shells 4/3; `sparse_infill_density` 15 % grid
- `nozzle_temperature` 250 °C (initial 245); `hot_plate_temp` 70 °C, textured PEI; `chamber_temperatures` 0
- `filament_flow_ratio` 0.97; `filament_max_volumetric_speed` 21 mm³/s (28 second slot)
- Fan min/max 20/40 %, overhang 90 % at ≥10 %, fan off first 3 layers
- `brim_type` auto_brim, `brim_width` 5 mm, `brim_object_gap` 0.1 mm; `enable_support` 0

Sliced (Bambu Studio): 379.99 m / 1142.47 g, 14h22m, single PETG on the left nozzle.

### Result — success

Derek said:
- The print is almost finished; "we do have success."
- The four diagonal corner gussets do not reach the reservoir pocket wall — each rib's pocket-side end stops short of the pocket outer wall.
