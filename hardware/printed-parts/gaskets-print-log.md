# gaskets print log

Format: facts only. Direct quotes from Derek where applicable. Settings
observed in committed `.3mf` snapshots. No interpretation, no hypothesis.

[`gaskets.3mf`](gaskets.3mf) is a consolidated TPU plate — it batches the
appliance's flexible seals onto one bed and prints them in a single Bambu
TPU 85A run. Each part's geometry source-of-truth and any per-part print
history stay in that part's own subsystem folder; this plate just groups
them. Several of these parts have prior individual prints (the reservoir
gasket + bulkhead seals were in the 2026-05-30 watertight test — see
[`cold-core/reservoir/print-log.md`](cold-core/reservoir/print-log.md)).

## Plate composition (13 instances, 6 distinct parts)

| Part (STEP) | Source | × | Footprint | CAD material |
| --- | --- | --- | --- | --- |
| `foam-cap-gasket` | [`cold-core/foam-cap/foam_cap.py`](cold-core/foam-cap/foam_cap.py) | 1 | 4480 mm² | TPU 90A |
| `reservoir-gasket` | [`cold-core/reservoir/reservoir.py`](cold-core/reservoir/reservoir.py) | 3 | 2323 mm² | TPU 85A |
| `touch-flo-mounting-gasket` | [`faucet/touch-flo-mounting-gasket/touch_flo_mounting_gasket.py`](faucet/touch-flo-mounting-gasket/touch_flo_mounting_gasket.py) | 2 | 2111 mm² | TPU 90A |
| `reservoir-bulkhead-seal-wet` | [`cold-core/reservoir/reservoir.py`](cold-core/reservoir/reservoir.py) | 2 | 145 mm² | TPU washer |
| `reservoir-bulkhead-seal-dry` | [`cold-core/reservoir/reservoir.py`](cold-core/reservoir/reservoir.py) | 2 | 67.7 mm² | TPU washer |
| `reservoir-retaining-ring` | [`cold-core/reservoir/reservoir.py`](cold-core/reservoir/reservoir.py) | 3 | 77.4 mm² | TPU 90A |

Part roles (geometry authoritative in the sources above):
- **foam-cap-gasket** — compresses between the foam-cap tray and the
  outer-shell mating face during the pour-in-place foam cure.
- **reservoir-gasket** — 2.0 mm flat gasket, 5 mm-wide perimeter ring,
  between the reservoir body wall top and the cap base, clamped by six M3.
- **touch-flo-mounting-gasket** — Ø54.35 mm × 2.0 mm disc between the
  faucet mounting plate and the kitchen countertop; shank hole + flavor-tube
  pill slot.
- **reservoir-bulkhead-seal-wet / -dry** — TPU face-seal washers around the
  PureSec bulkhead, shared Ø16 mm ID × 2.0 mm; wet OD 21.0 mm, dry OD 18.5 mm.
- **reservoir-retaining-ring** — 2.0 mm ring, OD 13.4 / ID 9.0 mm, press-fit
  into the Ø13.2 mm vent-filter pocket (0.1 mm interference/side).

The CAD docstrings spec a mix of hardnesses (reservoir-gasket TPU 85A;
foam-cap-gasket, touch-flo-mounting-gasket, retaining-ring TPU 90A; the two
bulkhead washers unspecified). This plate prints all of them from the single
loaded TPU 85A spool.

## Print attempt 1 (2026-06-06, settings per [`gaskets.3mf`](gaskets.3mf))

First consolidated gaskets plate. All 13 instances on extruder 1 (left),
single TPU 85A spool. `first_layer_time` ≈ 2215 s; plate bbox ≈ 283 × 285 mm.
`slice_info.config` header-only (saved + printed-from, no full slice estimate
embedded). Sliced in Bambu Studio 02.07.01.57.

Settings observed in the 3mf:
- Printer: Bambu Lab H2C, `nozzle_diameter` `[0.6, 0.6]`, `nozzle_volume_type`
  Standard; `print_settings_id` `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`.
  Textured PEI plate.
- Filament: single slot `Bambu TPU 85A @BBL H2C` (black, GFU04), `filament_type`
  TPU. `nozzle_temperature` 225 °C (initial 225), `hot_plate_temp` /
  `textured_plate_temp` 35 °C, `chamber_temperatures` 0, `filament_flow_ratio`
  1.0, `filament_max_volumetric_speed` 2.2 mm³/s, `filament_retraction_length`
  1.0 mm.
- Process: `layer_height` 0.18 mm, `initial_layer_print_height` 0.3 mm,
  `line_width` 0.62 mm (initial 0.62), `wall_generator` arachne, `wall_loops`
  2, `detect_thin_wall` 0, `sparse_infill_density` 100 % zig-zag,
  `top_shell_layers` / `bottom_shell_layers` 3 / 3, `raft_layers` 0,
  `brim_type` auto_brim (`brim_width` 5 mm, `brim_object_gap` 0.1 mm),
  `enable_support` 0, `enable_prime_tower` 1.
- Cooling: `fan_min_speed` / `fan_max_speed` / `overhang_fan_speed` all 100 %.
- Speeds: `outer_wall_speed` 200, `inner_wall_speed` 300, `initial_layer_speed`
  50 mm/s. `enable_pressure_advance` 0 (`pressure_advance` 0.02 dormant).
- `different_settings_to_system`: `wall_generator` + the infill pattern/density
  fields — i.e. arachne + 100 % zig-zag overrides over the stock Balanced
  Quality profile's defaults.

Same TPU 85A profile the touch-flo-tpu-o-ring v3 printed on (H2C 0.6 nozzle,
0.18 mm Balanced Quality, 225 °C, textured plate, flow 1.0, 2.2 mm³/s — see
[`faucet/touch-flo-tpu-o-ring/print-log.md`](faucet/touch-flo-tpu-o-ring/print-log.md)).
The difference is this plate runs solid seals — `wall_loops` 2 / arachne /
100 % infill / 3+3 shells — versus the o-ring's single Arachne wall.

Derek said (2026-06-06):
- "gaskets are going well."

Print outcome not yet fully recorded — this entry captures the committed
slice state.
