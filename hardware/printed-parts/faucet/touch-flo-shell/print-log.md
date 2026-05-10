# touch-flo-shell print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis.

## Pre-PET-CF test print (PETG with PLA supports)

Derek said:
- "Getting support material out of the dispense tube is going to be tough"
- "The zone 4.5 to zone 5 transition is the structural weak point and snaps easier than I would like, even though this was PETG and we will be printing in PET-CF"

## PET-CF print attempt 1

Derek said:
- "While printing, I have now twice in the first 2 hours gotten alerts 'please check the filament is still pushed in', and it was, and each time it then asked 'is it now extruding?' and it was."
- "The first time I got the alert, it immediately went back to that alert several times in a row after starting to print just a few mm, but then eventually it started going again and was fine for like 30 minutes until I got the next alert."
- "I went ahead and pushed the PTFE tube way further into the Sunlu E2"
- "Ended up printing nothing after I tapped 'it was visible now' when it apparently was not — got tired of monitoring it. Found it clogged above the hot end, had to take things apart there to get it all out."

## PET-CF print attempt 2

Derek said:
- "Got it reloaded now, starting attempt #2 .... redid all the PTFE and feeding of it entirely, checked all connections, used a shorter PTFE run."
- "Well attempt #2 failed as well same thing, got a clog, I had to take more things apart to clean it this time"

## PET-CF print attempt 3 (calibration phase)

Derek said:
- "tried #3 I am now getting 'nozzle offset calibration' failed over and over"
- Error code reported: `0300-4010 180102`
- "Alright .... finally got a couple good calibrations."

## PET-CF print attempt 4 (after calibration restored)

Derek said:
- "At about layer 20 I peaked at the print and saw that somewhere around layer 15 we started printing air. At first I saw some threading sticking up"
- "I hit unload and it unloaded just fine. I hit load and it loaded just fine. No clog."

## PET-CF print attempt 5 (clean slate, settings per commit `df00c36`)

Derek said:
- "We made it to layer 33 and no air print yet — furthest it has gotten so far I think."
- "I need to switch the 'add support' angle to add more supports — I think I might have had it at the default 35, but I'd been bumping it to 45 at least on most prints and had forgotten here perhaps"
- "I see some very stupid things happening that seem like they are going to crash the print, but they haven't exploded yet"

Observed in `df00c36` 3mf:
- `support_threshold_angle`: 25 (Derek's recollection of the default was 35; observed value is 25)
- `support_angle`: 0
- `support_critical_regions_only`: 0

TODO for next slice: bump `support_threshold_angle` per Derek's "at least 45" practice for prints with significant overhangs. Reminder to self if the print crashes mid-air later: insufficient supports were a known concern at layer 33 of attempt 5.

Derek observed during the print:
- "I see a few places where it is an entirely solid array, think like dozens of walls, and within that, there are a few stray strands curling up, like it printed air for a micro second, or perhaps it printed too thinly of a line momentarily, or perhaps it printed fine and just something else is wrong that is causing a single 1 mm strand to break off and curl upward in the middle of an otherwise solid print."
- "In some cases I have sent it print over these things just fine and the next layer at least has the 'short curly threads' in different spots"

Action: at layer 40 of this print, Derek turned the E2 back on to 60°C (it had been off; last run 23+ hours before the print started).

Environmental readings during attempt 5 (Sunday May 3rd 2:48 AM, layer 44):
- Basement EcoBee: 64 °F
- Upstairs EcoBee: 70 °F, 38% humidity
- Garage Shelly: 61 °F, 34% humidity
- Deck Shelly: 55 °F, 41% humidity
- Upstairs Bathroom Shelly: 18 °C, 40% humidity
- Master Bathroom Shelly: 64 °F, 39% humidity
- Downstairs Bathroom Shelly: 64 °F, 42% humidity

Two sensors nearest the 3D printer:
- Basement EcoBee: 64 °F
- Downstairs Bathroom Shelly: 64 °F, 42% humidity

## End of attempt 5 (print finished)

Derek observed:
- More air gaps in the finished print
- Some places: "many layers in a row [of air gaps] before starting again"
- Some places: air gaps consistently start "either at the end or at the beginning of a layer only"
- Base plate (printed simultaneously, "walls only" mode):
  - "the center of the base plate, the innermost 90% is solid"
  - "the outermost portion of it (whatever printed last or first) there is a 'wobble' of air gaps where some layers printed more of that, some printed more air, of that outermost 10%"

Derek observed on the prime tower (after tearing it apart):
- "the first 10 layers on the PET-CF look fine"
- "from there on up we what might be described best as 'stringing' (filament not fused to what is next to it or below it or above it, i.e. raw 'strings' of filament)"
- "The ABS side looks solid and well fused throughout"

## PET-CF print attempt 6 (settings per commit `0081e8f`)

Pre-print actions:
- Filament re-dried for 12 hours at 85°C
- E2 set to 60°C continuous during print (active maintenance drying)
- Bambu wiki confirms 85°C for PET-CF; the filament's box also specifies 85°C

Stated intent prior to slicing:
- Derek had said: "Next print: base plate only, no supports"
- Derek had said: "I have seen evidence of moisture being a problem since even when it was most recently dried"

Settings changes observed in `0081e8f` 3mf (vs `df00c36`):
- `nozzle_temperature` PET-CF (and initial layer): 270 → 280
- `chamber_temperatures`: PET-CF 50 + ABS 65 → both 50 (effective max 50)
- `layer_height`: 0.16 → 0.12
- `inner_wall_speed`: 150 → 120
- `sparse_infill_speed`: 180 → 100
- `fan_max_speed` PET-CF: 30 → 0 (PET-CF cooling fan off entirely)
- `fan_min_speed` PET-CF: 10 → 0
- `support_threshold_angle`: 25 → 45
- `filament_retraction_length` PET-CF: nil → 0.4 (now explicit)
- Filament profiles: now custom copies ("Bambu PET-CF/ABS @BBL H2C ... - Copy")

Settings unchanged from `df00c36`:
- `filament_max_volumetric_speed` PET-CF: 5
- `enable_wrapping_detection`: 0 (off)
- `enable_pressure_advance`: 0 (off)
- `outer_wall_speed`: 60
- `close_fan_the_first_x_layers`: 3
- `enable_support`: 1 (slice still has supports enabled; differs from Derek's earlier "no supports" plan)
- `support_filament`: ABS

Start-of-print events:
- Derek said: "the AMS HT for the ABS hit some clogs and breaks in the PTFE feed before getting started on the first layer"
- Derek said: "I cut a long length off of both ABS spools and confirmed both loaded successfully now"
- Derek said: "First layer of PET-CF printed fine btw, before I had to scrape it off"
- Print restarted Sunday May 4th at 11:50 AM
- E2 stayed at 60°C continuously through the delay

## PET-CF print attempt 7 (0.6 mm DUROZZLE TC nozzle + same-material supports)

Hardware change before this print:
- L-side nozzle swapped to 0.6 mm tungsten carbide DUROZZLE off-brand hotend (Amazon B0GWDDKG47, $37.43 delivered Sat May 9; see [hardware/purchases.md](../../purchases.md) §13). First L-side 0.6 mm nozzle on hand for the H2C; replaces the 0.4 mm hotends used in attempts 1–6.

Derek said:
- "The most recent PET-CF print worked beautifully."
- "We finally got a 0.6 tungsten nozzle (off brand)."
- "We did same material supports and they broke away cleanly." — supports printed in PET-CF (model material), broke away without contamination or fusion problems.

Settings changes observed in `touch-flo-shell-4-pieces.3mf` (vs `0081e8f`):
- Printer profile: `Bambu Lab H2C` 0.4-nozzle → `Bambu Lab H2C 0.6 nozzle` (`printer_variant`: 0.4 → 0.6)
- Print profile: → `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`
- `nozzle_diameter` (both extruders): 0.4 → 0.6
- `layer_height`: 0.12 → 0.18
- `initial_layer_print_height`: 0.3
- `line_width`: 0.62
- PET-CF `nozzle_temperature` + initial layer: 280 → 270
- PET-CF `filament_retraction_length`: 0.4 → nil (no override; uses printer default `retraction_length` 1.4 mm)
- PET-CF `fan_max_speed`: 0 → 30 % (cooling fan back ON)
- PET-CF `fan_min_speed`: 0 → 10 %
- `outer_wall_speed`: 60 → 200 mm/s
- `inner_wall_speed`: 120 → 300 mm/s
- `sparse_infill_speed`: 100 → 350 mm/s
- `support_filament`: 1 (ABS) → 0 (PET-CF, same material as model)
- `support_interface_filament`: 1 (ABS) → 0 (PET-CF, same material as model)
- Filament profile: `Bambu PET-CF @BBL H2C - Copy` → stock `Bambu PET-CF @BBL H2C` (no "- Copy")

Settings unchanged from `0081e8f`:
- PET-CF `filament_max_volumetric_speed`: 5 mm³/s
- PET-CF `chamber_temperatures`: 50 °C
- PET-CF `overhang_fan_speed`: 40 %
- `close_fan_the_first_x_layers`: 3
- `support_threshold_angle`: 45
- `enable_support`: 1
- `enable_pressure_advance`: 0
- `enable_prime_tower`: 1
- `enable_wrapping_detection`: 0

Plate composition (per `Metadata/plate_1.json`):
- 4 objects: `touch-flo-shell-base.step`, `touch-flo-shell-tube-half-neg-y.step`, `touch-flo-shell-tube-half-pos-y.step`, `touch-flo-mounting-plate.step`
- All objects assigned to `extruder=1` (left), `filament_maps` all = 1 (left nozzle), `first_extruder`: 0 (PET-CF slot)
- Bed: textured plate

## PET-CF print attempt 8 (failed: support tower fell over, joined faucet peak)

Hardware: same as attempt 7 (0.6 mm DUROZZLE TC L-side hotend).

Geometry change before this print: shell consolidated from 3 separate STEPs (base + 2 tube halves) into a single integrated `touch-flo-shell.step` per commit `41316ce` ("collapse back to a single piece, 3 mm wall throughout"), followed by `be92d9b` (drop zone-4.5 lid height to 3 mm on the back side) and `d7aa674` (heat-set retention geometry on shell + mounting plate). Plate now contains 2 objects instead of 4: `touch-flo-shell.step` (whole) + `touch-flo-mounting-plate.step`.

Derek said:
- "Most recent print failed in an interesting way, the support tower fell over[;] it finally joined up with the peak of the faucet."

Failure mode (Derek's description): a tall thin support structure for the faucet bend overhang lacked stability, leaned/drifted during the print, and eventually contacted and fused into the highest point of the faucet — i.e., the support didn't sever cleanly because it had grown into the part rather than alongside it.

No `.3mf` saved for attempt 8 in isolation; the in-flight slice was re-saved with the brim-fix changes for attempt 9 (settings deltas captured below).

## PET-CF print attempt 9 (support brim + on-build-plate-only)

Hardware: same (0.6 mm DUROZZLE TC L-side hotend).

Geometry: same as attempt 8 (`touch-flo-shell.step` whole + `touch-flo-mounting-plate.step`).

Derek said:
- "I added a brim to it (this is 'initial layer expansion' in the interface, no idea how you will find it in 3mf)."

What that maps to in the 3mf (vs attempt 7 / attempt 8 baseline):
- `raft_first_layer_expansion`: -1 (default/disabled) → 20 (mm) — this is the key the Bambu Studio UI labels "Initial layer expansion". With supports enabled, this expands the first layer of each support tower outward by 20 mm, giving the tower a much wider footprint at the bed and dramatically increasing its tip-over resistance.
- `support_on_build_plate_only`: 0 → 1 — supports are now forced to root in the build plate; they cannot grow on top of the model surface. Combined with the 20 mm expansion, this means every support tower has a wide skirt at z=0 and nothing floating mid-print.

Two related observations:
- The standalone `brim_type: auto_brim`, `brim_width: 5 mm`, and `elefant_foot_compensation: 0.15 mm` were already on for attempt 7 and were not changed for attempt 9 — those are the part brim, not the support-tower brim.
- All other settings — printer profile (`Bambu Lab H2C 0.6 nozzle`), print profile (`0.18mm Balanced Quality @BBL H2C 0.6 nozzle`), PET-CF temps (270 °C), wall/infill speeds (200 / 300 / 350 mm/s), same-material PET-CF supports (`support_filament: 0`, `support_interface_filament: 0`), `support_threshold_angle: 45`, fan settings (30 / 10 / 40 %), `line_width: 0.62`, `wall_loops: 50`, `layer_height: 0.18` — are unchanged from attempt 7.

Plate composition (per `Metadata/plate_1.json`):
- 2 objects: `touch-flo-shell.step`, `touch-flo-mounting-plate.step`
- Both objects assigned to `extruder=1` (left), `filament_maps` all = 1, `first_extruder`: 0 (PET-CF slot)
- Bed: textured plate

## End of attempt 9 (print succeeded)

Derek said:
- "The last print is beautiful! Actual success, and I was able to remove all the supports even those from inside of the tube."
- "Beautiful everywhere except where the supports were, and there it seems like we have some roughness and layer lines. Nearly stringing, but still part of the solid body. Like it is visibly a string, but still fused well so not the sort of stringing that makes a spaghetti explosion."

Observed in the attempt-9 settings:
- `support_top_z_distance`: 0.3 mm with `layer_height`: 0.18 mm = 1.67 layers (not a clean multiple of layer height; the slicer rounds the z-gap to alternating 1- and 2-layer offsets across the interface footprint).

## Hardware / setup observations across all PET-CF attempts

Derek said:
- "I have not been running the E2 for any of this ... it has been 23 hours since the E2 was last ran and the last 8 hours of trial and error have nothing to do with 'E2 at 70'"
- "I have been switching through my 3 different 0.4 nozzles throughout this. So they may all be contaminated in ways I cannot see, but they all look fine to me."
- On clumping detection (probing): "it has been on for all prints so far"
- "Well ... I don't see any purging during prints"

PET-CF surface quality, when it printed:
- "I don't see layer lines like I have on everything else — if they're there, they are invisible to my eyes. It really does look great, a whole different ballgame than everything else we've been printing with (ABS, PETG, PLA)"

## H2C right-side dual extruder unit — clog access procedure

How to reach a clog in the dual extruder unit (gear-driven filament feed assembly above the right hot end) without damaging the Vortek pincers or flex cable. Source: Derek's hands-on procedure after damaging the right Induction Heating Assembly during attempt 6 troubleshooting; the working sequence is what he arrived at AFTER the breakage.

1. Remove the back fan (needed to reach the flat ribbon cable connection point)
2. Disconnect the flat ribbon cable for the hotend assembly
3. Unscrew the power lines for the hotend assembly (reachable without the back fan removed for some unholy reason)
4. Then, and only then, begin unscrewing the mounting screws for the hotend assembly
5. With that removed, the front plate in front of the motors and the clog can be removed, and from there the clog can now be reached

Do NOT use a probe (drill bit, paperclip wire, etc.) from below to push the clog upward — this approach damaged the right Induction Heating Assembly's Vortek pincer mechanism and severed its flex cable during attempt 6.

## 3mf snapshots committed

### Commit `145a852` — saved during in-flight print

Filament slots in project: PET-CF (slot 0), ABS, ABS, ABS, PETG, PETG, PETG, PET-CF, PLA
Active in slice: PET-CF (left) + ABS (right, supports)
Support filament: ABS
Support interface filament: ABS

PET-CF settings:
- `nozzle_temperature`: 280°C
- `filament_flow_ratio`: 0.94
- `filament_retraction_length`: 1.2 mm (override)
- `filament_retract_before_wipe`: 70% (override)
- `filament_max_volumetric_speed`: 5 mm³/s
- `chamber_temperatures`: 50°C

ABS settings:
- `chamber_temperatures`: 65°C
- Effective chamber for slice: 65°C (max wins)

Process settings:
- `layer_height`: 0.24 mm
- `outer_wall_speed`: 200 mm/s
- `inner_wall_speed`: 300 mm/s
- `sparse_infill_speed`: 350 mm/s
- `enable_pressure_advance`: 0
- `enable_prime_tower`: 1
- `enable_wrapping_detection`: 1 (clumping detection by probing enabled)
- `wrapping_detection_layers`: 20 (probes triggered at layer_num 3, 10, 19 per gcode)

### Commit `e0752d9` — resaved during in-flight print
Same settings as `145a852`. File-byte delta only. `enable_wrapping_detection`: 1.

### Commit `df00c36` — clean slate

Filament slots in project: PET-CF (slot 0), ABS (slot 1)
Active in slice: PET-CF (left) + ABS (right, supports)
Support filament: ABS
Support interface filament: ABS

PET-CF settings:
- `nozzle_temperature`: 270°C
- `filament_flow_ratio`: 1.0
- `filament_retraction_length`: nil (no override; uses printer default)
- `filament_retract_before_wipe`: nil (no override)
- `filament_max_volumetric_speed`: 5 mm³/s
- `chamber_temperatures`: 50°C

ABS settings:
- `chamber_temperatures`: 65°C
- Effective chamber for slice: 65°C (max wins)

Process settings:
- `layer_height`: 0.16 mm
- `outer_wall_speed`: 60 mm/s
- `inner_wall_speed`: 150 mm/s
- `sparse_infill_speed`: 180 mm/s
- `enable_pressure_advance`: 0
- `enable_prime_tower`: 1
- `enable_wrapping_detection`: 0 (clumping detection by probing disabled)
- `wrapping_detection_layers`: 20 (gcode unchanged; would trigger at layer_num 3, 10, 19 if enabled)

### Commit `0081e8f` — attempt 6 (multi-lever fusion attack)

Filament profiles: custom copies created — `Bambu PET-CF @BBL H2C 0.4 nozzle - Copy`, `Bambu ABS @BBL H2C - Copy`
Filament slots in project: PET-CF (slot 0), ABS (slot 1)
Active in slice: PET-CF + ABS
Support filament: ABS
Support interface filament: ABS

PET-CF settings:
- `nozzle_temperature`: 280°C
- `nozzle_temperature_initial_layer`: 280°C
- `filament_flow_ratio`: 1.0
- `filament_retraction_length`: 0.4 mm (now explicit override)
- `filament_retract_before_wipe`: nil
- `filament_max_volumetric_speed`: 5 mm³/s
- `chamber_temperatures`: 50°C
- `fan_max_speed`: 0%
- `fan_min_speed`: 0%
- `overhang_fan_speed`: 40%

ABS settings:
- `chamber_temperatures`: 50°C (lowered from default 65°C)
- `fan_max_speed`: 60%
- Effective chamber for slice: 50°C

Process settings:
- `layer_height`: 0.12 mm
- `outer_wall_speed`: 60 mm/s
- `inner_wall_speed`: 120 mm/s
- `sparse_infill_speed`: 100 mm/s
- `support_threshold_angle`: 45 (from 25)
- `enable_support`: 1
- `enable_pressure_advance`: 0
- `enable_prime_tower`: 1
- `enable_wrapping_detection`: 0 (clumping detection still disabled)
- `close_fan_the_first_x_layers`: 3

### `touch-flo-shell-4-pieces.3mf` — attempt 7

Filament profiles: stock `Bambu PET-CF @BBL H2C` (no "- Copy")
Filament slots in project: PET-CF (slot 0), PLA, PET-CF, ABS, ABS, PETG, PETG, PETG (8 slots; only slot 0 active in slice)
Active in slice: PET-CF (left, slot 0)
Support filament: PET-CF (slot 0 — same material as model)
Support interface filament: PET-CF (slot 0 — same material as model)
Printer profile: `Bambu Lab H2C 0.6 nozzle` (`printer_variant`: 0.6)
Print profile: `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`

PET-CF settings (slot 0, left nozzle):
- `nozzle_temperature`: 270 °C
- `nozzle_temperature_initial_layer`: 270 °C
- `filament_flow_ratio`: 1.0
- `filament_retraction_length`: nil (no override; uses printer default)
- `filament_retract_before_wipe`: nil
- `filament_max_volumetric_speed`: 5 mm³/s
- `chamber_temperatures`: 50 °C
- `fan_max_speed`: 30 %, `fan_min_speed`: 10 %, `overhang_fan_speed`: 40 %
- `close_fan_the_first_x_layers`: 3

Process settings:
- `nozzle_diameter`: 0.6 mm
- `layer_height`: 0.18 mm
- `initial_layer_print_height`: 0.3 mm
- `line_width`: 0.62 mm
- `wall_loops`: 50
- `top_shell_layers`: 3, `bottom_shell_layers`: 3
- `sparse_infill_density`: 15 %, `sparse_infill_pattern`: grid
- `outer_wall_speed`: 200 mm/s
- `inner_wall_speed`: 300 mm/s
- `sparse_infill_speed`: 350 mm/s
- `internal_solid_infill_speed`: 250 mm/s
- `top_surface_speed`: 200 mm/s
- `support_speed`: 150 mm/s
- `support_interface_speed`: 80 mm/s
- `initial_layer_speed`: 50 mm/s
- `initial_layer_infill_speed`: 105 mm/s
- `outer_wall_jerk` / `inner_wall_jerk` / `infill_jerk`: 9
- `retraction_length` (printer-side): 1.4 mm; `wipe`: on; `retract_when_changing_layer`: on

Supports:
- `enable_support`: 1
- `support_filament`: 0 (PET-CF — same material)
- `support_interface_filament`: 0 (PET-CF — same material)
- `support_threshold_angle`: 45
- `support_angle`: 0
- `support_critical_regions_only`: 0
- `support_top_z_distance`: 0.3
- `support_base_pattern`: default
- `support_interface_top_layers`: 2
- `support_interface_pattern`: auto
- `support_style`: default
- `tree_support_branch_distance`: 5

Other:
- `enable_pressure_advance`: 0
- `enable_prime_tower`: 1
- `enable_wrapping_detection`: 0
- `wrapping_detection_layers`: 20

### `touch-flo-shell-2-pieces.3mf` — attempt 9

Filament profiles: stock `Bambu PET-CF @BBL H2C` (no "- Copy")
Filament slots in project: PET-CF (slot 0), PLA, PET-CF, ABS, ABS, PETG, PETG, PETG (only slot 0 active in slice)
Active in slice: PET-CF (left, slot 0)
Support filament: PET-CF (slot 0 — same material)
Support interface filament: PET-CF (slot 0 — same material)
Printer profile: `Bambu Lab H2C 0.6 nozzle` (`printer_variant`: 0.6)
Print profile: `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`

Plate composition (per `Metadata/plate_1.json`):
- 2 objects: `touch-flo-shell.step` (whole, single integrated piece per commit `41316ce` + `be92d9b` + `d7aa674`), `touch-flo-mounting-plate.step`
- Both on `extruder=1` (left), `filament_maps` all = 1, `first_extruder`: 0
- Bed: textured plate

Settings deltas vs `touch-flo-shell-4-pieces.3mf` (attempt 7):
- `raft_first_layer_expansion`: -1 → 20 mm — Bambu Studio UI label "Initial layer expansion"; widens first layer of each support tower 20 mm outward at the bed
- `support_on_build_plate_only`: 0 → 1 — supports root from the bed only; cannot grow on the model surface

Settings unchanged from attempt 7 (selected — full list in the attempt-7 snapshot above):
- PET-CF: `nozzle_temperature` 270 °C, `filament_flow_ratio` 1.0, `filament_retraction_length` nil, `filament_max_volumetric_speed` 5 mm³/s, `chamber_temperatures` 50 °C, `fan_max_speed` 30 % / `fan_min_speed` 10 % / `overhang_fan_speed` 40 %, `close_fan_the_first_x_layers` 3
- Process: `nozzle_diameter` 0.6 mm, `layer_height` 0.18 mm, `initial_layer_print_height` 0.3 mm, `line_width` 0.62 mm, `wall_loops` 50, `top_shell_layers` / `bottom_shell_layers` 3, `sparse_infill_density` 15 %, `sparse_infill_pattern` grid
- Speeds: `outer_wall_speed` 200, `inner_wall_speed` 300, `sparse_infill_speed` 350, `internal_solid_infill_speed` 250, `top_surface_speed` 200, `support_speed` 150, `support_interface_speed` 80, `initial_layer_speed` 50, `initial_layer_infill_speed` 105 (all mm/s); jerk 9
- Supports: `enable_support` 1, `support_filament` 0 (PET-CF), `support_interface_filament` 0 (PET-CF), `support_threshold_angle` 45, `support_top_z_distance` 0.3, `support_object_xy_distance` 0.35, `support_object_first_layer_gap` 0.2, `tree_support_branch_diameter` 2, `tree_support_branch_angle` 45, `support_interface_top_layers` 2
- Part brim (already on for attempt 7, unchanged here): `brim_type` auto_brim, `brim_width` 5 mm, `brim_object_gap` 0.1 mm, `elefant_foot_compensation` 0.15 mm
- Other: `enable_pressure_advance` 0, `enable_prime_tower` 1, `enable_wrapping_detection` 0

## Evidence that `enable_wrapping_detection` might be probe detection in the UI

- Wiki language for the feature: "the nozzle is detected to be wrapped by filament" — "wrapping" describes what clumping is physically ([Bambu Wiki: Nozzle Clumping Detection by Probing](https://wiki.bambulab.com/en/software/bambu-studio/nozzle-clumping-detection-by-probing))
- Behavior match in the gcode: `wrapping_detection_gcode` in the 3mf moves the toolhead to the back of the bed and runs `G39` (probe) at `layer_num` 3, 10, 19 — matching the wiki's "probes at layers 4, 11, 20" (same triggers, 0- vs 1-indexed)
- Trigger-layer alignment: 4 / 11 / 20 layers in the wiki match the gcode's 3 / 10 / 19 (zero-indexed)
