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

## Hardware / setup observations across all PET-CF attempts

Derek said:
- "I have not been running the E2 for any of this ... it has been 23 hours since the E2 was last ran and the last 8 hours of trial and error have nothing to do with 'E2 at 70'"
- "I have been switching through my 3 different 0.4 nozzles throughout this. So they may all be contaminated in ways I cannot see, but they all look fine to me."
- On clumping detection (probing): "it has been on for all prints so far"
- "Well ... I don't see any purging during prints"

PET-CF surface quality, when it printed:
- "I don't see layer lines like I have on everything else — if they're there, they are invisible to my eyes. It really does look great, a whole different ballgame than everything else we've been printing with (ABS, PETG, PLA)"

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

## Evidence that `enable_wrapping_detection` might be probe detection in the UI

- Wiki language for the feature: "the nozzle is detected to be wrapped by filament" — "wrapping" describes what clumping is physically ([Bambu Wiki: Nozzle Clumping Detection by Probing](https://wiki.bambulab.com/en/software/bambu-studio/nozzle-clumping-detection-by-probing))
- Behavior match in the gcode: `wrapping_detection_gcode` in the 3mf moves the toolhead to the back of the bed and runs `G39` (probe) at `layer_num` 3, 10, 19 — matching the wiki's "probes at layers 4, 11, 20" (same triggers, 0- vs 1-indexed)
- Trigger-layer alignment: 4 / 11 / 20 layers in the wiki match the gcode's 3 / 10 / 19 (zero-indexed)
