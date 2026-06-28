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

### Result — FAILED (2026-06-23)

Derek: "Print failed partway through on first attempt at a funnel mold. The auto
generated supports toppled over."

The tree(auto) supports filling the cavity's open forming-wall relief toppled
over and the print failed partway through, before the part completed.

## Re-slice — support base brim (2026-06-23, settings per [`funnel-mold.3mf`](funnel-mold.3mf))

Same object, plate, filament, and process as the snapshot above; the only
project-setting change targets the toppled supports.

Derek: "I have attempted to add a brim to them with 'initial layer expansion'
that worked for a similar problem another time."

The "similar problem another time" is the
[touch-flo-shell PET-CF attempt 9](/hardware/printed-parts/faucet/touch-flo-shell/print-log.md)
tip-over fix — the same `raft_first_layer_expansion` knob.

What that maps to in the 3mf (vs the snapshot above):
- `raft_first_layer_expansion`: -1 (default/disabled) → 20 (mm) — the key the
  Bambu Studio UI labels "Initial layer expansion". With supports enabled it
  expands the first layer of each support tower outward by 20 mm, giving the
  tower a much wider footprint at the bed and increasing its tip-over resistance.
  Now also listed in `different_settings_to_system`.
- Everything else is unchanged: tree(auto) supports, `support_threshold_angle`
  15, `support_on_build_plate_only` 0, `support_top_z_distance` 0.08; PETG
  Translucent slot; 0.08 mm layers, 100 % infill; `brim_type` auto_brim /
  `brim_width` 5 (the part brim, not the support-tower brim — unchanged).

Realized in the saved plate (`Metadata/plate_1.json`):
- Plate bbox ≈ 155 × 215 mm (was ≈ 119 × 179 — the support bases grew ~18 mm
  outward on every edge).
- `first_layer_time` ≈ 1056 s (was ≈ 281 — the brim adds first-layer area).

Still **saved but not fully sliced** — `slice_info.config` is header-only (no
per-plate time/filament estimate, no G-code member), same as the snapshot above.

### Result — completed, one cruddy mid layer (2026-06-25, per Derek)

The support-base brim held — the towers did not topple, and the print ran to
completion (the prior failure mode did not recur).

Derek: "Last print had a single layer in the middle that turned out cruddy
because the AI monitoring paused for a long time on a 'detected air printing'
that I simply resumed on and could find no trouble with."

One mid-height layer printed cruddy. Derek attributes it to the printer's AI
monitoring auto-pausing for an extended time on a false "detected air printing"
alert; he resumed the print and found no actual fault. That auto-pause is a
printer/cloud setting, not a project setting — it is not captured in the 3mf.

## Re-slice — 0.16 mm profile + build-plate-only supports (2026-06-25, settings per [`funnel-mold.3mf`](funnel-mold.3mf))

Same object, plate, and filament as the snapshots above — cavity half only
(`funnel-mold-cavity.step`, 1 object, identity orientation), PETG Translucent
slot. The print profile and the supports changed.

Derek: "Did a couple other tweaks." Printer-side, the AI-monitoring "detected
air printing" auto-pause was turned off (not captured in the 3mf).

Profile swap — `print_settings_id` 0.08mm High Quality → 0.16mm High Quality:
- `layer_height` 0.08 → 0.16 — roughly halves the layer count (targets the
  standing "nearly 3 days for both pieces at 0.08 layers" note above).
- Shell layer counts drop as the layers thicken (shell thickness held):
  `top_shell_layers` 9 → 6, `bottom_shell_layers` 7 → 4;
  `top_color_penetration_layers` 9 → 6, `bottom_color_penetration_layers` 7 → 4.
- Profile speeds rise (mm/s): `inner_wall_speed` 120 → 150,
  `internal_solid_infill_speed` 120 → 180, `sparse_infill_speed` 100 → 180,
  `top_surface_speed` 120 → 150, `gap_infill_speed` 50 → 250,
  `initial_layer_speed` 40 → 50, `initial_layer_infill_speed` 70 → 105.
- `support_top_z_distance` / `support_bottom_z_distance` 0.08 → 0.16 (one layer,
  tracking layer height).
- `ironing_flow` 8 % → 25 %, `ironing_speed` 30 → 20 — profile defaults only;
  `ironing_type` is still no ironing, so these are inert.

Support changes (now also in `different_settings_to_system`):
- `support_on_build_plate_only` 0 → 1 — supports grow only from the bed, not off
  the part's surfaces.
- `support_threshold_angle` 15 → 45.
- `raft_first_layer_expansion` 20 → 5 — the tower-base brim from the previous
  attempt, dialed back from 20 mm to 5 mm.

Other:
- `extruder_ams_count` extruder-1 entry `4#0` → `4#1` (AMS slot bookkeeping;
  incidental).
- Filament, wall loops, line widths, seam, cooling, and the part brim
  (`brim_type` auto_brim, `brim_width` 5) — all unchanged.

Realized in the saved plate (`Metadata/plate_1.json`):
- 1 object, `funnel-mold-cavity.step` — still the cavity half only; the core is
  not on this plate.
- Plate bbox ≈ 107 × 158 mm (was ≈ 155 × 215 in the brimmed snapshot) — the
  support footprint pulled back in (raft expansion 20 → 5, build-plate-only
  supports, threshold 45).
- `first_layer_time` ≈ 541 s (was ≈ 1056).

Still **saved but not fully sliced** — `slice_info.config` is header-only (no
per-plate time/filament estimate, no G-code member), same as the snapshots above.

### Result — completed (per Derek)

Print ran to completion. Supports held; no tip-over.

## Re-slice — core half, support clearance up (2026-06-27, settings per [`funnel-mold.3mf`](funnel-mold.3mf))

One object change; support z and xy standoff increased; support-tower brim disabled.

Object:
- 1 object: `funnel-mold-core.step` (the **core half only**); cavity is not on this plate.
  `source_offset_z` 54.5, identity matrix (printed as modeled, opening up).

What changed vs the 2026-06-25 snapshot:
- `support_top_z_distance` / `support_bottom_z_distance` 0.16 → 0.24.
- `support_object_xy_distance` 0.35 → 0.42.
- `raft_first_layer_expansion` 5 → -1.

Everything else unchanged: 0.16 mm layers, `support_on_build_plate_only` 1,
`support_threshold_angle` 45, PETG Translucent, 100 % zig-zag infill, `brim_type` auto_brim /
`brim_width` 5.

Realized in the saved plate (`Metadata/plate_1.json`):
- 1 object, `funnel-mold-core.step`.
- Plate bbox ≈ 107 × 170 mm; `first_layer_time` ≈ 752 s.

Still **saved but not fully sliced** — `slice_info.config` is header-only (no per-plate
time/filament estimate, no G-code member), same as prior snapshots.

### Result — completed; mating halves too much clearance (per Derek)

Print completed. Supports removed more cleanly than prior attempts. Fitted against the cavity:
clearance between mating surfaces too large.

## Re-slice — both halves (2026-06-28, settings per [`funnel-mold.3mf`](funnel-mold.3mf))

Both halves on the plate; core geometry from commit `ece85465`; all support settings unchanged
from the 2026-06-27 snapshot.

Objects:
- 2 objects: `funnel-mold-cavity.step` (`source_offset_z` 49.5) and `funnel-mold-core.step`
  (`source_offset_z` 54.5). Both identity matrix.

Support settings (unchanged vs 2026-06-27):
- `support_on_build_plate_only` 1; `support_threshold_angle` 45; `support_type` tree(auto).
- `support_top_z_distance` / `support_bottom_z_distance` 0.24; `support_object_xy_distance` 0.42.
- `raft_first_layer_expansion` -1.

Everything else unchanged: 0.16 mm layers, PETG Translucent, 100 % zig-zag infill,
`brim_type` auto_brim / `brim_width` 5.

Realized in the saved plate (`Metadata/plate_1.json`):
- 2 objects, `funnel-mold-cavity.step` + `funnel-mold-core.step`.
- Plate bbox ≈ 223 × 171 mm; `first_layer_time` ≈ 1170 s.

Still **saved but not fully sliced** — `slice_info.config` is header-only (no per-plate
time/filament estimate, no G-code member), same as prior snapshots.

### Result — not yet recorded (print started 2026-06-28)
