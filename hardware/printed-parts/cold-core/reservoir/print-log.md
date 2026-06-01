# reservoir print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis.

Standing, filament-agnostic print guidance lives in [`watertight-petg.md`](watertight-petg.md); this file is the per-attempt record.

Geometry: the left flavor reservoir — `reservoir-left.step` (body) + `reservoir-cap-left.step` (cap). Plate composition and settings are recorded per attempt below.

## PETG print attempt 3 (2026-05-30, settings per [`reservoir.3mf`](reservoir.3mf))

First print of the watertight recipe (developed on the [`../../reference/water-test-cup`](../../reference/water-test-cup/) coupon, which held water) carried onto the actual reservoir body. First reservoir print to carry supports for the slanted floor.

Geometry: one object, `reservoir-left.step` (body only; no cap on the plate). Printed mouth-up; the floor underside sits raised over the open bag-pocket space, so supports rise from the plate to the floor underside. Plate bbox ≈ 90 × 145 mm; `first_layer_time` ≈ 393 s.

Printer / nozzle: Bambu Lab H2C, `printer_variant` 0.6, `nozzle_diameter` `[0.6, 0.6]`. `print_settings_id` `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`. Textured plate. Active PETG slot `Bambu PETG Water`, nozzle pair (260 °C, 250 °C), `filament_flow_ratio` (1.02, 0.97), `filament_max_volumetric_speed` (21, 28). The 3mf is saved + printed-from; `slice_info.config` header-only (no per-plate estimate written).

Support settings (this print's purpose):
- `enable_support`: 1
- `support_type`: normal(auto)
- `support_threshold_angle`: 30
- `support_top_z_distance`: 0.25 mm
- `support_bottom_z_distance`: 0.18 mm
- `support_on_build_plate_only`: 1
- `support_interface_top_layers`: 2 (Derek chose to keep the default 2 rather than reduce it; reasons not recorded)
- `support_interface_bottom_layers`: 2
- `support_interface_spacing`: 0.5 mm
- `support_style`: default; `support_object_xy_distance`: 0.35 mm; `support_line_width`: 0.6 mm

Cooling (PETG slot): `fan_min_speed` 10 %, `fan_max_speed` 20 %, `overhang_fan_speed` 90 % at `overhang_fan_threshold` 10 %, `additional_cooling_fan_speed` 0, `close_fan_the_first_x_layers` 3.

Watertight recipe carried over from the coupon:
- `wall_generator`: arachne; `wall_loops`: 6; `line_width`: 0.60 mm (3.0 mm wall ÷ 0.60 = 5 lines)
- `sparse_infill_density`: 100 %
- `top_surface_pattern` / `bottom_surface_pattern`: zig-zag
- `ironing_type`: top
- `seam_position`: random; `seam_slope_type`: all (scarf on all walls)
- `layer_height`: 0.18 mm; `initial_layer_print_height`: 0.3 mm

Print started 2026-05-30.

### Result — SUCCESS (2026-05-30)

Derek said:
- "It did work. None of the floor pulled off."
- "It did allow me to test with that foam shell print. It's holding water for a few hours now. First successfully done so, and done so with gaskets and all."

First watertight reservoir. The slanted-floor supports (normal(auto), 0.25 mm top z-gap, interface top layers 2) released cleanly — no tear-out of the floor underside. Assembled into the printed foam shell with the bulkhead + TPU gaskets and held water for several hours with no weep. Leak-tightness gate (per [`watertight-petg.md`](watertight-petg.md)) passed at fill-and-hold; this is the first reservoir to pass.
