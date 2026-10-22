# reservoir print log

Format: facts only. Direct quotes from Derek where applicable. Settings observed in committed `.3mf` snapshots. No interpretation, no hypothesis.

The current recipe and result are in [watertight-petg.md](watertight-petg.md) and
[reservoir.3mf](reservoir.3mf). This file records historical settings and observations. [Water-hold acceptance](water-hold-acceptance.json) identifies the tested articles and reported results.

Geometry: the left flavor reservoir — `reservoir-left.step` (body) + `reservoir-cap-left.step` (cap). Plate composition and settings are recorded per attempt below.

## PETG print attempt 1 (2026-05-22, settings per history-only `git:8c9128a94:hardware/printed-parts/cold-core/reservoir/reservoir-left-body-and-cap.3mf`)

SunTop PETG, left body and cap, 0.8 mm High Flow nozzle. The active Generic
PETG slot carried `nozzle_temperature` **240 °C** (initial 240),
`layer_height` **0.40 mm** (initial 0.40), flow 1.00 and a 22 mm³/s
volumetric limit. The process requested 100 walls and 15% grid infill.
Normal cooling was 40–90%.

### Result — leaked

The May 25 attempt-2 record reports that attempt 1 leaked. Its original
settings and observations are retained in Git at the source above.

## PETG print attempt 2 (2026-05-25, settings per history-only `git:f0b560736:hardware/printed-parts/cold-core/reservoir/reservoir-left-body-and-cap.3mf`)

SunTop PETG, left body and cap, 0.6 mm nozzle. The active slot carried
`nozzle_temperature` **255 °C** (initial 255), `layer_height` **0.30 mm**
(initial 0.30), flow 1.00 and a 12 mm³/s volumetric limit. The process
requested 100 walls, 0.62 mm lines and 15% grid infill. Normal cooling was
40–90%.

### Result — not recorded

The record documents the print start and saved settings, without a water-hold outcome.

## PETG print attempt 3 (2026-05-30, settings per history-only `git:f25975cd045cc835eccf1a207cb12fe48dc63ada:hardware/printed-parts/cold-core/reservoir/reservoir.3mf`)

First print of the watertight recipe (developed on the water-test-cup coupon, which held water; the cup, its print log and its `.3mf` stand at the `archive-water-test-cup` tag) carried onto the actual reservoir body. First reservoir print to carry supports for the slanted floor.

Geometry: one object, `reservoir-left.step` (body only; no cap on the plate). Printed mouth-up; the floor underside sits raised over the open bag-pocket space, so supports rise from the plate to the floor underside. Plate bbox ≈ 90 × 145 mm; `first_layer_time` ≈ 393 s.

Printer / nozzle: Bambu Lab H2C, `printer_variant` 0.6, `nozzle_diameter` `[0.6, 0.6]`. `print_settings_id` `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`. Textured plate. Active PETG slot `Bambu PETG Water`, nozzle pair (260 °C, 250 °C), `filament_flow_ratio` (1.02, 0.97), `filament_max_volumetric_speed` (21, 28). The 3mf is saved + printed-from; `slice_info.config` header-only (no per-plate estimate written).

Actual filament: **Bambu PETG clear**, confirmed by Derek on 2026-10-05.
The saved custom preset carries PETG Basic's `GFG00` identity. The active
left nozzle uses 255 °C initially, 260 °C subsequently, flow 1.02 and a
21 mm³/s volumetric limit. The paired right-nozzle values do not describe
this print's extrusion.

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

First watertight reservoir. The slanted-floor supports (normal(auto), 0.25 mm top z-gap, interface top layers 2) released cleanly — no tear-out of the floor underside. Assembled into the printed foam shell with the bulkhead + TPU gaskets and held water for several hours with no weep. The reported fill-and-hold result passed; this was the first reservoir reported to hold water.

## Saved project dated 2026-05-31 (settings per history-only `git:7ba87d399:hardware/printed-parts/cold-core/reservoir/reservoir.3mf`)

PETG Translucent preset, 0.6 mm nozzle, `layer_height` **0.18 mm**
(initial 0.30), `nozzle_temperature` **245 °C** (initial 250), flow 0.97
and a 16 mm³/s volumetric limit. Normal cooling was 20–60%. The saved project
used tree supports with a 0.18 mm top gap.

### Result — not recorded

This saved recipe differs from the May 30 water-holding recipe. No physical
water-hold outcome is recorded for this saved project.

## PETG print attempt 4 (2026-06-10, settings per history-only `git:7436a1c92:hardware/printed-parts/cold-core/reservoir/reservoir.3mf`)

Full plate carrying both flavor reservoirs and both caps — four objects, four cut records. Bodies `reservoir-left.step` + `reservoir-right.step` placed mouth-up; caps `reservoir-cap-left.step` + `reservoir-cap-right.step` laid flat. Plate bbox ≈ 262 × 231 mm; `first_layer_time` ≈ 1107 s; `slice_info.config` header-only (no per-plate estimate written). Sliced with BambuStudio 02.07.01.57.

Printer / nozzle: Bambu Lab H2C, `printer_variant` 0.6, `nozzle_diameter` `[0.6, 0.6]`. `print_settings_id` `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`. Textured plate. Active PETG slot `Bambu PETG Translucent @BBL H2C`, nozzle pair (245 °C, 245 °C), `filament_flow_ratio` (0.97, 0.97), `filament_max_volumetric_speed` (16, 16).

Support settings:
- `enable_support`: 1
- `support_type`: tree(auto)
- `support_threshold_angle`: 30
- `support_top_z_distance`: 0.18 mm
- `support_bottom_z_distance`: 0.18 mm
- `support_on_build_plate_only`: 1
- `support_interface_top_layers`: 2
- `support_interface_bottom_layers`: 2
- `support_interface_spacing`: 0.5 mm
- `support_style`: default; `support_object_xy_distance`: 0.35 mm; `support_line_width`: 0.6 mm

Cooling (PETG slot): `fan_min_speed` 20 %, `fan_max_speed` 60 %, `overhang_fan_speed` 90 % at `overhang_fan_threshold` 10 %.

Watertight recipe (carried from attempt 3):
- `wall_generator`: arachne; `wall_loops`: 6; `line_width`: 0.60 mm
- `sparse_infill_density`: 100 %
- `top_surface_pattern` / `bottom_surface_pattern`: zig-zag
- `ironing_type`: top
- `seam_position`: random; `seam_slope_type`: all
- `layer_height`: 0.18 mm; `initial_layer_print_height`: 0.3 mm

### Result — not yet recorded (slice committed 2026-06-10)

## PETG print attempt 5 (2026-06-14, settings per history-only `git:8ace13398:hardware/printed-parts/cold-core/reservoir/reservoir.3mf`)

Full plate carrying both flavor reservoirs and both caps — four objects (`reservoir-left.step`, `reservoir-right.step`, `reservoir-cap-left.step`, `reservoir-cap-right.step`). Plate bbox ≈ 262 × 231 mm; `first_layer_time` ≈ 1097 s; `slice_info.config` header-only (no per-plate estimate written). Sliced with BambuStudio 02.07.01.57.

Geometry change from attempt 4: `ROD_POSITION_X` moved 100 → 104 (the level-sensing float-guide rod), so the 27.75 mm measured donor donut rides against the cavity far wall; both `reservoir-left.step` and `reservoir-right.step` re-exported. Rationale in [`level-sensing.md`](level-sensing.md).

Printer / nozzle: Bambu Lab H2C, `printer_variant` 0.6, `nozzle_diameter` `[0.6, 0.6]`. `print_settings_id` `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`. Textured plate. Active PETG slot `Bambu PETG Translucent @BBL H2C`, nozzle pair (245 °C, 245 °C), `filament_flow_ratio` (0.97, 0.97), `filament_max_volumetric_speed` (16, 16).

Support settings:
- `enable_support`: 1
- `support_type`: tree(auto)
- `support_threshold_angle`: 30
- `support_top_z_distance`: 0.18 mm
- `support_bottom_z_distance`: 0.18 mm
- `support_on_build_plate_only`: 1
- `support_interface_top_layers`: 2
- `support_interface_bottom_layers`: 2
- `support_interface_spacing`: 0.5 mm
- `support_style`: default; `support_object_xy_distance`: 0.35 mm; `support_line_width`: 0.6 mm

Cooling (PETG slot): `fan_min_speed` 20 %, `fan_max_speed` 60 %, `overhang_fan_speed` 90 % at `overhang_fan_threshold` 10 %, `additional_cooling_fan_speed` 0, `close_fan_the_first_x_layers` 3.

Watertight recipe (carried from attempt 4):
- `wall_generator`: arachne; `wall_loops`: 6; `line_width`: 0.60 mm
- `sparse_infill_density`: 100 %
- `top_surface_pattern` / `bottom_surface_pattern`: zig-zag
- `ironing_type`: top
- `seam_position`: aligned (attempt 4 was random); `seam_slope_type`: all
- `layer_height`: 0.18 mm; `initial_layer_print_height`: 0.3 mm

### Result — not yet recorded (slice committed 2026-06-14)

## PETG seal trial prepared (2026-09-04, settings per history-only `git:67994c7efaed7589ff26db350b90eea089fbd3e8:hardware/printed-parts/cold-core/reservoir/reservoir-08-seal-trial.3mf`)

One September reference left reservoir body, mouth up, and matching left cap, exterior face down
and gasket rim up. H2C, 0.8 mm nozzle, PETG Translucent.
Bambu Studio 02.08.02.61. Estimated 26 h 12 min, 417.16 g, 984 layers.

- Printer: 0.8 mm Standard, +0.04 mm over stock Z trim; the archived trial bundle also contained a +0.18 mm preset.
- `nozzle_temperature` **255 °C** (initial 255)
- `layer_height` **0.18 mm** (initial 0.30)
- Arachne, six requested wall loops, 0.80 mm wall width.
- Wall and fill speed requested: 30 mm/s; volumetric limit 6 mm³/s.
- Filament flow ratio: 0.97. Normal part fan: 20%; overhang override: 90%; auxiliary fan off.
- Aligned scarf seams, inner walls included, conditional scarf disabled, seam gap 0%.
- Top and bottom shells: 12 layers / 2 mm; 100% infill; top-surface ironing.

[Settings and toolpath inspection](history/seal-trial.md).

### Result — held water (reported 2026-10-05)

Derek said: "The September slower recipes did hold water (both of them) literally, so at least we have something usable there, even if a bit slow."

The recovered Mark2 file is `reservoir-08-seal-trial.gcode.3mf`, printer file
timestamp `20260907175322`. Its complete project settings match the saved
0.18 mm project. The printer slice estimates 26 h 8 min and 416.86 g.
Its timelapse thumbnail shows a full-height reservoir body and separate cap.
The [acceptance record](water-hold-acceptance.json) identifies the archive and
G-code hashes. The reported water hold has no specified duration, temperature
or fill height.

## PETG 0.24 mm seal trial prepared (2026-09-04, settings per history-only `git:67994c7efaed7589ff26db350b90eea089fbd3e8:hardware/printed-parts/cold-core/reservoir/reservoir-08-seal-trial-024.3mf`)

One September reference left reservoir body and matching left cap. Body mouth up; cap exterior
face down and gasket rim up. H2C, 0.8 mm nozzle, PETG Translucent.
Bambu Studio 02.08.02.61. Estimated 20 h 8 min, 414.76 g, 738 layers.

- Printer: 0.8 mm Standard, +0.04 mm over stock Z trim; the archived trial bundle also contained a +0.18 mm preset.
- `nozzle_temperature` **255 °C** (initial 255)
- `layer_height` **0.24 mm** (initial 0.30)
- Other physical machine, filament and process settings match the September 0.18 mm recipe. The saved 0.18 mm project received a later mesh/placement refresh; it is not geometrically identical to this 0.24 mm project.
- Inspection basis: both object meshes and their placement match the September 4 0.18 mm reference slice.

### Result — held water (reported 2026-10-05)

Derek's statement above applies to this 0.24 mm recipe as well.
The recovered Mark2 file is `reservoir-08-seal-trial-024.gcode.3mf`, printer
file timestamp `20260905022656`. Its complete project settings match the
saved 0.24 mm project. The printer slice estimates 20 h 7 min and 414.76 g.
Its timelapse thumbnail shows a full-height reservoir body and separate cap.
The [acceptance record](water-hold-acceptance.json) identifies the archive and
G-code hashes. The reported water hold has no specified duration, temperature
or fill height.


## Flat-square ironing calibration (2026-10-06, Mark2 task 1314288755)

Nine 35 × 35 mm flat squares compared 15/30/60 mm/s ironing speed and
10/20/30% flow at 0.15 mm spacing, alongside one OFF square. All used clear
Bambu PETG, the left 0.8 mm Standard hotend, 255 °C nozzle, 70 °C bed and
0.30/0.24 mm layers. [Launch and completion](ironing-study/prints/2026-10-06-mark2-squares-v1/launch.json).

Derek said:

> the "OFF" one is the best result by a long shot, smoothest and feels best.

He tentatively preferred the entire 30% flow column among the ironed squares.
The 60/30 square felt more papery than 15/30 and 30/30; no ranking between
15/30 and 30/30 was reported. [Physical observation](ironing-study/prints/2026-10-06-mark2-squares-v1/physical-result.json).
This was a flat-finish assessment, with no water-hold or gasket-seal result.

## Left reservoir and cap, ironing off (2026-10-06, Mark2 task 1314692596)

One current left reservoir body, mouth up, and matching cap, exterior face
down, used the September 0.24 mm baseline with model and support ironing
disabled. The left 0.8 mm Standard hotend used Bambu PETG Translucent Clear
from A4, +0.04 mm user Z trim (emitted `G29.1 Z0.02`), 255 °C nozzle and
70 °C bed. The native model/support/brim footprint had an 80.5 mm minimum
bed-edge inset. The native estimate was 419.09 g, 19 h 23 min and 740 layers.

[Launch record](prints/2026-10-06-mark2-no-ironing-v1/launch.json) records the
new job accepted without errors. Finished-part and water-hold outcomes are
unassessed.


## Right reservoir and cap, ironing off (2026-10-07, Mark2 task 1317261284)

The right body and matching right cap use plate 2 of the frozen October 6
reservoir project with identical reviewed native G-code and settings. Mark2
accepted one foreground Send at **09:34:45 CDT**, 233.39 seconds after Mark1
accepted its matching funnel core. Both printers were freshly read before Send;
Mark2 was idle without faults.

Clear PETG starts from A4 through the left 0.8 mm Standard nozzle,
Textured PEI, +0.04 requested / +0.02 emitted trim, 255 °C nozzle and
70 °C bed. Model and support ironing are Off. Timelapse and bed leveling
are On; flow dynamic and nozzle offset calibration use Auto. Probing clump
checks remain Off. Native estimates are **19 h 23 min, 419.13 g and 740 layers**.

[Project binding, preflight and accepted launch](prints/2026-10-07-mark2-right-no-ironing-v1/README.md).
Finished-part, gasket seal and water-hold results are unassessed.

At 09:50:35 CDT, the right pair is RUNNING at layer 1/740 without faults.
Runtime timelapse is enabled; the read-only card inventory contains 97 clips.
[Timelapse observation](prints/2026-10-07-mark2-right-no-ironing-v1/timelapse-review.json).

## Left reservoir and cap, Mark1 right 0.8 mm (2026-10-21, task 1359853920)

Mark1 accepted the current flat-floor left body and matching top-fill/top-draw cap
at **00:02:36 CDT** through one Bambu Connect Send. The right 0.8 mm Standard-flow
hotend starts on **A4**, with automatic refill choosing subsequent spools. Derek
requests **A2 for the next print start**.

The September 0.24 mm baseline uses ironing Off, 255 °C nozzle, 70 °C Textured PEI
bed and Mark1's +0.18 mm user trim, emitted as `G29.1 Z0.16`. Native estimates are
**19 h 21 min, 410.28 g and 833 layers**. Timelapse and bed leveling are On; flow
dynamic and nozzle offset calibration use Auto. The printer acknowledges SUCCESS
and reports the new job in PREPARE without faults. Finished-part and water-hold
results are unassessed.

[Native review, preflight, packaging and launch](prints/2026-10-20-mark1-right08/README.md).

### Result — stopped after first-layer non-adherence (2026-10-21)

Derek said:

> Oh interesting,  we do have a failure on the current print, one of the inner Wall layers did not adhere and got lifted up at some point. I've stopped the print.

[Photographs taken before removal](prints/2026-10-20-mark1-right08/physical-result/physical-result.json)
show a lifted cap perimeter strand and separated first-layer lines. Derek
removed the failed material and reports the bed clear for a retry with the
+0.18 mm user Z trim removed. A separate
[earlier corner-lifting report and timelapse review](corner-lifting/README.md)
has no established onset layer.

## Left reservoir and cap, zero-user-trim PETG retry (2026-10-21, Mark1 task 1359909015)

Mark1 accepted one Send at **00:40:29 CDT**, starting on **A2** with
automatic refill through the right 0.8 mm Standard nozzle. The added user Z
trim is **0.00 mm**, with stock Textured PEI compensation emitted as
**`G29.1 Z-0.02`**. All other executable native commands match the failed A4
job: 255 °C nozzle, 70 °C bed, 0.30/0.24 mm layers, flow 0.97, 6 mm³/s ceiling,
no ironing and the same supports/cooling/deposition. The printer acknowledged
SUCCESS and entered PREPARE without faults.

[Native verification, preflight, packaging and launch](prints/2026-10-21-mark1-right08-z000/README.md).

### Result — stopped; corner curl and water leakage (2026-10-21)

Derek supplied two finished-article photographs and said:

> It leaked many places. It is from the most recent print i just stopped.

The [physical result](prints/2026-10-21-mark1-right08-z000/physical-result/physical-result.json)
records reported corner curling and the failed water hold for this zero-trim
article. Leak locations, fill height, hold duration and stop layer are not
specified. A2 automatically refilled from A1 during the print.

The last live UI observation was layer 526 at **14:13:18 CDT / 19:13:18 UTC**.
Only exposed body/cap edges were assessable; no complete attached baseline or
lift onset was established. At **14:41:56 CDT / 19:41:56 UTC**, this exact
retained task reported FAILED, heaters targeted off and HMS empty. Terminal
layer 0 is a reset status, not the stop layer. Bambu Studio displayed
"The task was canceled." The final camera preview was unavailable. The
[terminal observation](prints/2026-10-21-mark1-right08-z000/terminal-observation.json)
records these limits and the paused monitor.

## Left reservoir and cap, May Water adapted to 0.8 mm (2026-10-21, Mark1 task 1362179138)

Derek said:

> Let's try the May Water recipe adapted to the 0.8 nozzle, with 1.02 flow, no brim, zero added Z trim, and ironing off. Mark1 is clear; go ahead and start the next reservoir print.

Mark1 accepted one foreground Bambu Connect Send at **16:42:02 CDT** and acknowledged
SUCCESS, entering PREPARE without print errors or HMS alerts. A1 feeds the right
0.8 mm Standard nozzle with automatic refill. A2 is empty. The native recipe uses
255/260 °C nozzle, 70 °C bed, flow 1.02, 21 mm³/s ceiling, 0.30/0.24 mm layers and
0.80 mm lines. Requested outer/inner wall speeds are 200/300 mm/s; solid/top are
250/200 mm/s. Six requested Arachne walls, 100% zig-zag fill, 15% overlap, random
conditional scarf and 15% seam gap match the recovered May controls. Cooling is
10–20%, off for the first three layers, with 90% overhang override and auxiliary off.

No brim or ironing is emitted. Zero added user trim retains stock Textured PEI
`G29.1 Z-0.02`. Current Tree(auto)/Default bed-only supports retain 0.18 mm gaps.
Native plate-1 estimates: **5 h 42 min, 431.04 g, 833 layers**; no plate warnings.
Send options for timelapse/bed leveling are On; flow dynamic/nozzle offset calibration are Auto.
[Adaptation, native review and accepted job](prints/2026-10-21-mark1-may-water-right08-z000/README.md).
The 16:48:41 CDT startup check found layer 0/833, no print error/HMS, bed 70 °C
and the mounted right 0.8 mm nozzle. Live camera frames showed the empty plate
during startup; runtime timelapse activation at deposition is unassessed.
Finished-article corner contact and water hold are unassessed.


### Result — May-adapted article leaks at the floor-fill/perimeter boundary (2026-10-21)

Derek said: **“Leaks between infill and wall.”** Five underside photographs show
multiple droplets along that boundary. The retained task 1362179138 reports
FINISH at 833/833 with no print error/HMS; fill height and hold duration are
unreported. [Physical result](prints/2026-10-21-mark1-may-water-right08-z000/physical-result/physical-result.json).
The saved May mesh has a sloped floor with sampled 3 mm vertical material thickness;
the geometry comparison does not establish the cause of different sealing.

## Left reservoir and cap, walls-only May Water (2026-10-21, Mark1 task 1362982574)

Derek said:

> I think I'd rather continue the walls forever, as we did in the sphere pressure vessel test. Another agent suggested at some point infill works better, but I haven't seen that.

> Mark1 bed is clear and ready for walls only. I think there is still filament on A4 that is unused please use that first.

> Do you understand what I meant about the spool order? That we want to use up the spools that are most empty first ...

Mark1 accepted one foreground Send at **23:25:22 CDT October 21 / 04:25:22 UTC
October 22** and acknowledged SUCCESS with no print error/HMS. The Send dialog
selected **A4 PETG R** and right **0.8 mm Standard**. Matching-spool automatic
refill is retained; preferred depletion order is **A4 → A1 → A3**, with automatic
backup priority unverified. A1 reports 57%, A3 100%, A4 unknown; A2 is empty.

**999 requested walls**, **0% sparse fill**, zero top/bottom shell fill. Native
model features contain only walls, including the floor. Other May controls,
geometry, placement, zero user Z trim, no brim, ironing Off and Tree/Default
supports are retained. Native estimate: **5 h 46 min, 430.66 g, 833 layers**.
No physical adhesion, corner-flatness or water-hold result is established.
[Adaptation, native review and launch](prints/2026-10-21-mark1-walls-only-right08-z000-a4/README.md).


### Result — walls-only article leaks along the seam (2026-10-22)

Derek said: **“Leaks along the seam”**. The underside photograph shows droplets
along a branching junction across the concentric floor paths and at lower
corners. The retained task 1362982574 reports FINISH at 833/833, with no print
error/HMS; those status fields do not establish sealing. This article fails
its reported water hold. Fill height, duration and complete internal flow path
are unreported. [Physical result](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json).

The pictured junction qualitatively resembles the native medial-junction pockets
recorded before launch. Native comparisons retain walls-only and flow 1.02 and
separately examine seam gap and Arachne's junction controls. A saved setting or
bead-envelope comparison is not a physical sealing result.
