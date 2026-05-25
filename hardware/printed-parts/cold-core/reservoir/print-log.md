# reservoir print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis.

Geometry: left flavor reservoir + cap, two parts on one plate — `reservoir-left.step` (body) + `reservoir-cap-left.step` (cap). See [`reservoir-left-body-and-cap.3mf`](reservoir-left-body-and-cap.3mf).

## PETG print attempt 1 (2026-05-22, settings per [`reservoir-left-body-and-cap.3mf`](reservoir-left-body-and-cap.3mf))

Hardware: 0.8 mm high-flow nozzle, H2C, textured plate.

Filament: SunTop food-contact-compliant PETG, 1.75 mm × 1 kg, Clear/Transparent — [B0FP34MJ94](https://www.amazon.com/dp/B0FP34MJ94), delivered May 18, 2026 per [purchases.md §13](../../../purchases.md). Raw materials comply with FDA 21 CFR 177.1630. Manufacturer-stated print band: nozzle 220–240 °C, bed 60–80 °C (Amazon listing copy). Loaded in the slice's active filament slot using the stock `Generic PETG @BBL H2C` profile (no separate SunTop profile created; settings overridden per-slot).

Drying (SUNLU S4 dryer chamber RH, the dryer's hygrometer reading — not filament moisture by weight):
- Out of vacuum bag: 35 % RH
- After cycle 1: 30 % RH
- After cycle 2 (at slice time): 14 % RH

Derek said about SunTop's recommended nozzle temp:
- "I have the transparent variety which is not currently on that amazon listing."
- "I see in a screenshot on that listing that they more specifically recommend 235 not the 220-240 range you cited."

Derek said about flow ratio (pre-slice intent):
- "I have found in other testing that over extrusion (flow ratio) helps with air tightness / water tightness."
- "I have found that 'flow ratio 1.00' works well without defects, while 'flow ratio 1.02' results in noticeable bulges."

Derek said about max volumetric speed:
- "I see a 12 mm3 'max volumetric speed' default in here for the generic PETG settings from Bambu."
- "This is a test print, and one of many to come, I wouldn't mind starting riskier, so I've attempted 22 mm3 max volumetric speed."

Derek said about wall loops:
- "Thanks for the reminder on wall loops btw, I've bumped that to 100 as I had intended but forgotten to do."

Settings observed in the saved 3mf for the active filament slot (`Generic PETG @BBL H2C`, slot 0):
- `nozzle_temperature`: 240 °C (Bambu Generic profile default 255 °C; SunTop listing band 220–240 °C; SunTop screenshot point 235 °C)
- `nozzle_temperature_initial_layer`: 240 °C
- `filament_flow_ratio`: 1.00 (Bambu Generic default 0.97)
- `filament_max_volumetric_speed`: 22 mm³/s (Bambu Generic default 12 mm³/s)
- `filament_diameter`: 1.75 mm
- `filament_density`: 1.27 g/cm³
- `hot_plate_temp`: 70 °C
- `fan_max_speed`: 90 %, `fan_min_speed`: 40 %
- `close_fan_the_first_x_layers`: 3

Process settings observed:
- Print profile: `0.40mm Standard @BBL H2C 0.8 nozzle`
- `nozzle_diameter`: 0.8 mm
- `layer_height`: 0.4 mm
- `initial_layer_print_height`: 0.4 mm
- `wall_loops`: 100 (Bambu print-profile default 2)
- `wall_sequence`: inner wall / outer wall
- `top_shell_layers`: 4, `bottom_shell_layers`: 3
- `sparse_infill_density`: 15 %, `sparse_infill_pattern`: grid (with `wall_loops` 100, perimeters fill the entire cross-section of the part walls before any sparse infill is generated)
- `infill_wall_overlap`: 15 %
- `outer_wall_speed`: 200 mm/s
- `inner_wall_speed`: 300 mm/s
- `sparse_infill_speed`: 350 mm/s
- `internal_solid_infill_speed`: 250 mm/s
- `top_surface_speed`: 200 mm/s
- `initial_layer_speed`: 50 mm/s
- All nominal speeds above are bounded by `filament_max_volumetric_speed` 22 mm³/s. At line width 0.8 mm × layer 0.4 mm = 0.32 mm² cross-section, the effective speed ceiling for nominal-width features is 22 ÷ 0.32 ≈ 68.75 mm/s.

Plate composition (per `Metadata/model_settings.config`):
- 2 objects: `reservoir-left.step` (body) + `reservoir-cap-left.step` (cap)
- Both assigned to the active filament slot (slot 0)

Filament-slot project layout (3 slots with named profiles):
- Slot 0 (active in slice): `Generic PETG @BBL H2C` — the SunTop PETG with the per-slot overrides above
- Slot 1: `Bambu PETG Basic @BBL H2C` (loaded in project, not used by the slice)
- Slot 2: `Bambu ABS @BBL H2C 0.8 nozzle` (loaded in project, not used by the slice)

Print started 2026-05-22.

## End of attempt 1

Derek said:
- "The reservoir leaked at the 240 degree printing, in ways that the 255 degree printed bambu PETG had not."
- "I have bumped the temperature despite all we discussed, just to experiment with 'can this PETG actually print leak proof'."

## PETG print attempt 2 (2026-05-25, settings per [`reservoir-left-body-and-cap.3mf`](reservoir-left-body-and-cap.3mf))

Hardware at slice time: 0.6 mm right-side nozzle installed (this was **not** Derek's intent for attempt 2 — see Derek-said block below). Printer/print profile in the 3mf: `@BBL H2C 0.6 nozzle`; `nozzle_diameter` 0.6 mm.

Derek said about the nozzle (after the print was ~10 hours in):
- "Oh strange, the 0.6 mm nozzle switch was not intentional. I even tried to switch it to 0.8 when I noticed it, but I must have failed."
- "I can confirm I see it is printing with 0.6 now, but it has been like 10 hours already so I'll let it finish."
- "Feel free to mark that as an oversight on my part in the print log, not an intentional part of the experiment."

Intended vs. actual variables for attempt 2: only the **nozzle temperature bump (240 → 255 °C)** was deliberate. The 0.6 mm nozzle / 0.3 mm layer height / 0.62 mm line widths / 12 mm³/s volumetric speed all came in via the `@BBL H2C 0.6 nozzle` print profile being active when the slice was saved — they are not part of the temperature experiment. Any leak-tightness result from this print therefore confounds the temperature variable with the nozzle/layer-height/line-width changes.

Filament: same SunTop PETG spool as attempt 1 ([B0FP34MJ94](https://www.amazon.com/dp/B0FP34MJ94)). Loaded in the same active slot using the stock `Generic PETG @BBL H2C` profile with per-slot overrides.

Drying: not re-dried between attempts 1 and 2 (no Derek statement about an additional cycle); SUNLU S4 last reading at attempt-1 slice time was 14 % RH.

Settings deltas observed in the saved 3mf vs attempt 1:

Filament (active slot 0, `Generic PETG @BBL H2C`):
- `nozzle_temperature`: 240 → **255 °C** (matches Bambu Generic profile default; matches the Bambu PETG temp at which prior prints did not leak)
- `nozzle_temperature_initial_layer`: 240 → **255 °C**
- `filament_max_volumetric_speed`: 22 → **12 mm³/s** (back to Bambu Generic default)
- `filament_flow_ratio`: 1.00 (unchanged)
- `hot_plate_temp`: 70 °C (unchanged)
- `fan_max_speed` 90 % / `fan_min_speed` 40 % / `close_fan_the_first_x_layers` 3 (all unchanged)

Process:
- Print profile: `0.40mm Standard @BBL H2C 0.8 nozzle` → **`0.30mm Standard @BBL H2C 0.6 nozzle`**
- `nozzle_diameter`: 0.8 → **0.6 mm**
- `layer_height`: 0.4 → **0.3 mm**
- `initial_layer_print_height`: 0.4 → **0.3 mm**
- `line_width` (and all per-feature line widths: outer wall, inner wall, internal solid infill, sparse infill, initial layer): 0.82 → **0.62 mm**
- `wall_loops`: 100 (unchanged)
- `wall_sequence`: inner wall / outer wall (unchanged)
- `top_shell_layers`: 4, `bottom_shell_layers`: 3 (unchanged)
- `sparse_infill_density`: 15 % grid (unchanged; moot at `wall_loops` 100)
- `infill_wall_overlap`: 15 % (unchanged)
- Speed nominals unchanged: outer 200, inner 300, sparse infill 350, internal solid infill 250, top surface 200, initial layer 50 (all mm/s)
- New volumetric ceiling: at 0.62 mm × 0.3 mm = 0.186 mm² cross-section and 12 mm³/s, the effective speed ceiling for nominal-width features is 12 ÷ 0.186 ≈ 64.5 mm/s (was ~68.75 mm/s in attempt 1).

Plate composition (per `Metadata/model_settings.config`):
- 2 objects: `reservoir-left.step` (body) + `reservoir-cap-left.step` (cap) — unchanged from attempt 1
- Both assigned to the active filament slot (slot 0)

Filament-slot project layout:
- Slot 0 (active in slice): `Generic PETG @BBL H2C` — unchanged identity, SunTop PETG with the per-slot overrides above
- Slot 1: `Bambu PETG Basic @BBL H2C` — unchanged
- Slot 2: `Bambu ABS @BBL H2C 0.8 nozzle` → **`Bambu ABS @BBL H2C 0.6 nozzle`** (inactive in slice; profile rebound to the 0.6-nozzle variant to match the new printer profile)

Print started 2026-05-25.
