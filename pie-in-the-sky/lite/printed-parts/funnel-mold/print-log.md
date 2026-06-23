# funnel-mold print log

Format: facts only, as observed in the committed [`funnel-mold.3mf`](funnel-mold.3mf)
snapshot. No interpretation, no hypothesis. Geometry + standing design notes live
in [`README.md`](README.md); this file is the per-attempt record.

Geometry: the lite hopper-funnel silicone mold — `funnel-mold-cavity.step` (cavity
half) + `funnel-mold-core.step` (core half) from
[`funnel_mold.py`](funnel_mold.py). Plate composition and settings per attempt below.

## Slice snapshot (2026-06-23, settings per [`funnel-mold.3mf`](funnel-mold.3mf))

Saved from Bambu Studio `02.07.01.62`. The 3mf is **saved but not fully sliced** —
`slice_info.config` carries only a header (no per-plate time/filament estimate) and
no G-code member.

Printer / nozzle:
- `printer_model`: Bambu Lab H2C, `printer_variant`: 0.4
- `nozzle_diameter`: `[0.4, 0.4]`
- `printer_settings_id`: `Bambu Lab H2C 0.4 nozzle`
- `print_settings_id`: `0.08mm High Quality @BBL H2C`
- Textured plate.

Plate / object:
- 1 object: `funnel-mold-cavity.step` — the **cavity half only**; the core is not on
  this plate. `source_offset_z` 49.5, identity matrix (printed as modeled, opening up).
- Plate bbox ≈ 119 × 179 mm; `first_layer_time` ≈ 281 s.

Filament (active slot):
- `Bambu PETG Translucent @BBL H2C 0.4 nozzle`, `filament_type` PETG.
- `nozzle_temperature` 245 (`nozzle_temperature_initial_layer` 250); `hot_plate_temp`
  / `textured_plate_temp` 70.
- `filament_flow_ratio` 0.97; `filament_max_volumetric_speed` 6.

Process:
- `layer_height` 0.08; `initial_layer_print_height` 0.2.
- `line_width` 0.42 (`outer_wall_line_width` 0.42, `inner_wall_line_width` 0.45).
- `wall_loops` 2; `wall_generator` classic; `wall_sequence` inner wall/outer wall;
  `detect_thin_wall` 0.
- `sparse_infill_density` 100 %; `sparse_infill_pattern` zig-zag;
  `internal_solid_infill_pattern` zig-zag.
- `top_shell_layers` 9 (`top_shell_thickness` 1 mm); `bottom_shell_layers` 7
  (`bottom_shell_thickness` 0 — by layer count).
- `top_surface_pattern` / `bottom_surface_pattern` zig-zag; `ironing_type` no ironing.
- `seam_position` aligned; `seam_gap` 15 %; `seam_slope_type` none (no scarf).
- `infill_wall_overlap` 15 %.

Cooling:
- `fan_min_speed` 10, `fan_max_speed` 30; `overhang_fan_speed` 90 at
  `overhang_fan_threshold` 10 %; `additional_cooling_fan_speed` 0;
  `close_fan_the_first_x_layers` 3.

Supports:
- `enable_support` 1; `support_type` tree(auto); `support_threshold_angle` 15;
  `support_on_build_plate_only` 0; `support_top_z_distance` 0.08; `support_filament` 0.
- `support_interface_top_layers` / `_bottom_layers` 2 / 2; `support_interface_spacing`
  0.5; `support_object_xy_distance` 0.35; `support_style` default; `support_base_pattern`
  default.

Speeds (mm/s):
- `outer_wall_speed` 60; `inner_wall_speed` 120; `internal_solid_infill_speed` 120;
  `sparse_infill_speed` 100; `top_surface_speed` 120; `initial_layer_speed` 40;
  `support_speed` 150; `support_interface_speed` 80.

Brim: `brim_type` auto_brim; `brim_width` 5.

Derek: "we're still at nearly 3 days for both pieces at 0.08 layers."

### Result — not yet recorded (slice saved 2026-06-23)
