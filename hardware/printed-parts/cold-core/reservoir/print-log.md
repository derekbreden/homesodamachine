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
