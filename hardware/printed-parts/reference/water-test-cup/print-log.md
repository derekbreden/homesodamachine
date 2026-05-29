# water-test-cup print log

Format: facts only, as observed in the committed [`water-test-cup.3mf`](water-test-cup.3mf) snapshot. No interpretation, no hypothesis. Standing watertight-PETG guidance lives in [`../../cold-core/reservoir/watertight-petg.md`](../../cold-core/reservoir/watertight-petg.md); the coupon's purpose is in [`README.md`](README.md).

Geometry: one object, `water-test-cup.step` — the 4 fl oz open-top cup (⌀56 × 63.25 mm outer, ⌀50 interior, 3 mm wall + floor) from [`water_test_cup.py`](water_test_cup.py).

## Slice snapshot (2026-05-29, settings per [`water-test-cup.3mf`](water-test-cup.3mf))

Saved from Bambu Studio `02.07.00.55`. The 3mf is **saved but not fully sliced** — `slice_info.config` carries only a header (no per-plate time/filament estimate) and no G-code member is present.

Printer / nozzle:
- `printer_model`: Bambu Lab H2C, `printer_variant`: 0.6
- `nozzle_diameter`: `[0.6, 0.6]` (dual-nozzle machine; per-nozzle settings below are stored as pairs)
- `printer_settings_id`: `Bambu Lab H2C 0.6 nozzle`
- `print_settings_id`: `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`

Plate / object:
- 1 object: `water-test-cup.step`, assigned to `extruder` 1
- `plate_1.json` `filament_ids` empty, `first_extruder` 0

Filament slots (`filament_settings_id`, 6 slots): `Bambu PETG Water` ×4, `Bambu PET-CF @BBL H2C`, `Bambu TPU 95A HF @BBL H2C`. `filament_type`: PETG ×4, PET-CF, TPU. `filament_ids`: GFG00 ×4, GFT01, GFU00.

Per-nozzle filament values (each filament stores a value per nozzle → arrays are 2× the 6 slots). PETG slots carry the pair (nozzle 0, nozzle 1) = (260 °C, 250 °C):
- `nozzle_temperature` (12): `260, 250, 260, 250, 260, 250, 260, 250, 270, 270, 230, 230`
- `nozzle_temperature_initial_layer` (12): `255, 245, 255, 245, 255, 245, 255, 245, 270, 270, 230, 230`
- `filament_flow_ratio` (12): `1.02, 0.97, 1.02, 0.97, 1.02, 0.97, 1.02, 0.97, 1, 1, 1, 1`
- `filament_max_volumetric_speed` (12): `21, 28, 21, 28, 21, 28, 21, 28, 5, 5, 12, 12`
- `hot_plate_temp` (6): `70, 70, 70, 70, 100, 35`

Cooling (per slot, 6): `fan_min_speed` `10,10,10,10,10,100`; `fan_max_speed` `20,20,20,20,30,100`; `additional_cooling_fan_speed` `0,0,0,0,0,100`; `overhang_fan_speed` `90,90,90,90,40,100`; `overhang_fan_threshold` `10%,10%,10%,10%,0%,95%`; `close_fan_the_first_x_layers` `3,3,3,3,3,1`.

Process settings observed:
- `layer_height`: 0.18 mm; `initial_layer_print_height`: 0.3 mm
- `line_width`: 0.62 mm (outer wall, inner wall, top surface, internal solid infill, initial layer all 0.62)
- `wall_loops`: 100
- `wall_generator`: classic
- `wall_sequence`: inner wall / outer wall; `is_infill_first`: 0
- `detect_thin_wall`: 0
- `top_shell_layers`: 3, `top_shell_thickness`: 0.8 mm
- `bottom_shell_layers`: 3, `bottom_shell_thickness`: 0
- `sparse_infill_density`: 15 %, `sparse_infill_pattern`: grid
- `top_surface_pattern`: monotonicline; `bottom_surface_pattern`: monotonic; `internal_solid_infill_pattern`: zig-zag
- `infill_wall_overlap`: 15 %
- `ironing_type`: no ironing
- `seam_position`: aligned; `seam_gap`: 15 %
- `scarf_joint_seam`, `precise_wall`, `wall_seam_alignment`, `staggered_inner_seams`: not present in the config
- `outer_wall_speed`: 200, `inner_wall_speed`: 300, `internal_solid_infill_speed`: 250, `sparse_infill_speed`: 350, `top_surface_speed`: 200, `initial_layer_speed`: 50 (all mm/s)
- `enable_support`: 0; `brim_type`: auto_brim, `brim_width`: 0
