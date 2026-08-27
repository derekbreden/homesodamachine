# foam-shell print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis — analysis lives in the conversation, decisions land in the geometry.

Geometry: the full cold-core foam shell, from [`foam_shell.py`](/hardware/printed-parts/cold-core/foam-shell/foam_shell.py). Outer footprint 283 × 181 mm, 213.4 mm tall; the four standing walls are 3.2 mm on a 2 mm floor. README is the geometry source-of-truth.

**Slice `foam-shell.stl`, not `foam-shell.step`.** The standing walls carry a fluted show skin that lives in the MESH and not in the solid, so the STEP beside it is a smooth prism — a plate sliced off it prints a part this machine does not have. The two foam caps are the same: `foam-cap-top.stl` and `foam-cap-bottom.stl`. Everywhere else on the machine the STEP is the whole of the part; on these three it is not. See README §The show skin.

## Stock

**Polymaker Fiberon PET-GF15, black, on a 0.8 mm tungsten carbide nozzle, left hotend.** The
shell and all four foam caps and lids ship on it ([bom.md §7](/hardware/ledger/bom.md)) — the
same spool the enclosure's exterior runs, on the big nozzle instead of the exterior's 0.4
([tools.md](/hardware/ledger/tools.md) "Which hotends fit an H2C"). Every abrasive nozzle runs
left, and the left nozzle is also the one whose 325 × 320 × 320 mm envelope holds a part this
size, so the abrasive path and the big-part path are one path.

The plate keeps its own figures — 0.4 layer, `line_width` 0.82, `wall_loops` 2 classic, 15 %
grid — and takes the stock's from the slot the exterior is sliced on
([enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md) "The
PET-GF15 exterior"):

| | Value |
|---|---|
| Filament preset | `Polymaker PET-GF @BBL H2C` |
| `nozzle_temperature` | 290 °C |
| `hot_plate_temp` / `textured_plate_temp` | 100 °C |
| `chamber_temperatures` | 50 °C |
| `filament_flow_ratio` | 0.9555 |
| `filament_max_volumetric_speed` | 18 mm³/s |
| Fan min / max / overhang | 0 / 0 / 0 % |
| `filament_retraction_length` | nil |

Drying is per spool, not per build: 100 °C × 10 h in the SUNLU E2 only if the spool has taken
on moisture, and a 3 kg spool feeds the print from a PolyDryer Box XL rather than the E2
([tools.md](/hardware/ledger/tools.md) "What dries where").

**No PET-GF plate of this part has been sliced.** Both attempts below ran `Bambu PETG Basic`,
and the hours [machine-time.md](/hardware/ledger/machine-time.md) §1 carries for this group are
attempt 2's carried across the stock rather than measured on it. Slicing one closes that.

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

`foam-shell.step` at geometry commit `7cd49702`: rounded outer corners (12 mm), cylindrical bosses tangent to the exterior wall with teardrop corner-fill webs, four corner gussets (z 2–42). Cap + gasket pads share the boss shape. Geometry in [`README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md); construction in [`../_outer_shell.py`](/hardware/printed-parts/cold-core/_outer_shell.py); the four corner gussets were defined in `_corner_gussets.py` at that commit.

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
