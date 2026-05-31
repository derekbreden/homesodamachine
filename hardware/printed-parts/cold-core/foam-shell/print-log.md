# foam-shell print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis — analysis lives in the conversation, decisions land in the geometry.

Geometry: the full cold-core foam shell, one object `foam-shell.step` from [`foam_shell.py`](foam_shell.py). Outer footprint 283 × 181 mm, 213.4 mm tall, 2 mm walls/floor. README is the geometry source-of-truth.

## Print attempt 1 (settings per [`foam-shell-8mm-high-flow.3mf`](foam-shell-8mm-high-flow.3mf))

First full foam-shell print. Used the part-proving foam shell for the reservoir watertight test (held water with gaskets — see [`../reservoir/print-log.md`](../reservoir/print-log.md) attempt 3).

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

## What's about to be tried — corner gussets (geometry change, settings unchanged)

Reprint the **gusseted** geometry (commit `99c607df`: four diagonal floor-up ribs tying each reservoir-pocket far-corner to the outer-shell corner boss — see README `corner_gussets` and [`../_corner_gussets.py`](../_corner_gussets.py)) at the **same stock settings above**, deliberately **without a brim** (the gussets are the structural alternative to a cut-off brim).

The `foam-shell.step` changed with the gusset commit, so the part needs a fresh slice before this attempt; the committed 3mf above is the pre-gusset slice and is kept as the attempt-1 settings record.

Open: does the corner gusset prevent the floor-corner lift on the next print, or are first-layer-squish / bed-temp / ambient-stability changes still needed.
