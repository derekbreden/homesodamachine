# foam-shell print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis — analysis lives in the conversation, decisions land in the geometry.

Geometry: the full cold-core foam shell, from [`foam_shell.py`](/hardware/printed-parts/cold-core/foam-shell/foam_shell.py). The smooth casing is 282.4 × 180.4 mm, 213.4 mm tall, with ordinary 2.38 mm standing walls and a 2 mm floor. README is the geometry source-of-truth.

The launch record binds the exact `foam-shell.stl` embedded in the sliced project. The current shell, caps and lid edges have smooth surfaces. Historical fluted projects remain identified with their own attempts below.

## Production preparation — round copper exits / A2 seam

The full shell is prepared for Mark2 with two 7.5 mm copper holes, continuous
2.38 mm walls, the selected faucet A2 scarf treatment and wiping off. The
scarf starts on the plain long-wall span at native X60, Y−90.2. Outer walls
request 100 mm/s / 1,500 mm/s²; inner walls 150 mm/s / 3,000 mm/s².

The [production record](prints/2026-10-26-mark2-round-ports-a2/README.md)
binds the editable project, sliced archive, exact source hashes, emitted paths
and preserved fits. Native estimate: **31 h 37 min**, **1,449.9 g**. Tree(auto)
Default remains enabled and generates no supports. Prepared only; no launch
or physical result is recorded for this article.

## Stock

The recorded smooth-shell job uses **Polymaker Fiberon PET-GF15, black, on Mark2's
fixed left hardened 0.4 mm Standard hotend**. Its left-nozzle envelope is
325 × 320 × 320 mm. The [job record](prints/2026-10-25-mark2-left04-smooth238-z004/README.md)
binds the archive and printer mapping.

The plate uses 0.20 mm first and 0.24 mm ordinary layers, 0.42 mm outer and
0.45 mm inner lines, three classic wall loops and 15% gyroid in thick regions.
Emitted outer walls request 200 mm/s and 5,000 mm/s² acceleration.
It takes the filament settings from the shared
[`petgf.3mf`](../../petgf.3mf):

| | Value |
|---|---|
| Filament preset | `Polymaker PET-GF @BBL H2C` |
| `nozzle_temperature` / initial layer | 280 / 265 °C |
| `hot_plate_temp` / `textured_plate_temp` | 80 °C |
| `chamber_temperatures` | 0 °C (unheated) |
| `filament_flow_ratio` | 0.9555 |
| `filament_max_volumetric_speed` | 18 mm³/s |
| Fan min / max / bridge-overhang | 0 / 0 / 70%; 50% unsupported-width threshold |
| `filament_retraction_length` | nil |

Drying is per spool, not per build: 100 °C × 10 h in the SUNLU E2 only if the spool has taken
on moisture, and a 3 kg spool feeds the print from a PolyDryer Box XL rather than the E2
([tools.md](/hardware/ledger/tools.md) "What dries where").

Attempts 1 and 2 below use `Bambu PETG Basic`. The smooth PET-GF shell's reported
physical result and digital audit are recorded with its launch below.

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


## Smooth 2.38 mm casing, Mark2 0.4 mm (2026-10-25)

Derek: "Please start a print of this new cold core shell on mark2 when you are ready."

Mark2 accepted task **1375153599** at **16:26:12 CDT / 21:26:12 UTC**.
The shell uses the smooth 282.4 × 180.4 mm casing and fixed reservoir cavities.
Classic with three loops gives six perimeter lines across sampled ordinary
2.38 mm walls. The 0.4 mm Standard left nozzle prints black PET-GF15 at
0.20/0.24 mm layers, 265/280 °C, an 80 °C textured PEI bed, unheated chamber,
ordinary cooling off and localized 70% bridge/overhang cooling. Thick regions
use 15% gyroid. Supports are off; minimum native bed margin is 21.183 mm.
Native estimate: **23 h 4 min 46 s**. Requested user Z trim +0.04 mm emits
G29.1 Z0.02. Timelapse and bed leveling On; flow and nozzle-offset Auto.

The [job record](prints/2026-10-25-mark2-left04-smooth238-z004/README.md)
binds geometry, settings, emitted paths and the accepted launch.
Derek supplied seven photographs and reported: "Well, this turned out pretty
awful here, at least in these parts that I've photographed for you here."
The photographs show a rippled, locally porous patch at an upper long-wall
corner and rough, porous vertical slot edges. The
[sent-file audit](prints/2026-10-25-mark2-left04-smooth238-z004/post-print-audit/README.md)
binds the supplied photographs by hash and checks the launch archive,
embedded model and emitted paths. The exterior finish is a failed result.
Fit, leak and load results were not supplied for this shell.

First-layer readback at 16:48:22 CDT: RUNNING, 1/889, 265/80 °C,
print error 0. Dirty nozzle-camera warning 0C00010000020017 may affect AI
monitoring; the print continues and Derek was notified. This is printer
progress, not physical surface acceptance.
