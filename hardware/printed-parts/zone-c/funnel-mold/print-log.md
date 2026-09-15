# Funnel mold print log

## 0.40 mm support trial — 2026-09-14 (settings per `funnel-mold-h2c-040.gcode.3mf`)

- `layer_height` **0.40 mm** (initial 0.40)
- `nozzle_temperature` **245 °C** (initial 250)

The User Process is **Funnel mold shell - 0.8 nozzle - 0.40 mm gentle supports**.
The cavity is 199 layers, estimated at 20 h 43 min and 745.57 g. The separate
core plate is 113 layers, estimated at 11 h 48 min and 484.64 g. The cavity's
estimate is 10 h 47 min shorter than the 0.24 mm gentle-support slice.
[layer-height-review.json](layer-height-review.json) records the comparison,
checksums, actual support and travel motion, and cavity support footprint.
The modeled geometry, support speed limits, reinforced trees and Z trim match
the gentle-support trial. Forming slopes require sanding and finishing.

Derek confirmed the bed clear and authorized starting the print. Bambu Connect
submitted plate 1 to **H2C**, serial **31B8AP612000452**, with AMS A3 PETG
Translucent (96% remaining before submission), the left 0.8 mm High Flow nozzle
and Textured PEI. Timelapse is off, bed leveling on, and flow/nozzle-offset
calibration Auto. At 21:14:54 UTC the printer reports RUNNING, 199 layers and
no print error or HMS entry, with its nozzle warming at 165 °C. The core was
not submitted. Derek reports: “It printed, but there's gaps.” His picked
location is X=86.800, Y=−69.368, Z=71.112 mm. The submitted cavity's STEP
and STL both have through-wall openings beneath the brim and at the ramp joins.

## Gentle support motion file — 2026-09-14

The saved User Process is **Funnel mold shell - 0.8 nozzle - gentle supports**.
The checked cavity file is `funnel-mold-h2c-gentle-supports.gcode.3mf`, with
331 layers, a 31 h 29 min estimate and 786.73 g including supports. It has
not been submitted. Derek has not cleared the bed and requested a 3MF only.

Supports are capped at 40 mm/s, interfaces at 30 mm/s and travel at 150 mm/s.
Normal printing and travel acceleration are 1,500 mm/s². Trees have two wall
loops and 4 mm initial branch diameter; support walls participate in travel
detours. Initial layer expansion is 8 mm. The +0.18 trim, Textured PEI,
left 0.8 mm High Flow nozzle and Bambu filament operating settings are retained.
[support-motion-review.json](support-motion-review.json) records the emitted
commands and settings comparison. Physical stability is untested.

## Cavity support feet — 2026-09-14

Derek reports this job failed. The supports bond early and remain stable;
later, fast movement on and between the tall supports knocks some over.
The failed print remains on the bed. The exact failure layer is unknown.

H2C accepted `funnel-mold-h2c-support-feet.gcode.3mf` through Bambu Connect.
At 15:34 UTC it reports RUNNING, 331 layers and no print error or HMS entry;
Connect shows toolhead homing and left-nozzle heating. The job uses AMS A3
Bambu PETG Translucent, reported full before submission. A2 reported 59%
remaining against the 653 g estimate. Bed leveling is on; timelapse is off;
flow and nozzle-offset calibration use Auto.

The saved User Process is **Funnel mold shell - 0.8 nozzle - 8mm support feet**.
Support → Initial layer expansion is 8 mm, initial layer density is 90%,
and raft layers are zero. The +0.18 mm trim emits `G29.1 Z0.16` on Textured
PEI. The left 0.8 mm High Flow nozzle, stock PETG temperatures and flow limit,
0.40 mm first layer and 0.24 mm later layers are retained.

The emitted first-layer support contact area is approximately 30,305 mm²,
compared with 10,677 mm² in the failed job. The sliced paths remain inside
the printable area. The estimate is 18 h 31 min and 653 g, adding about
9 minutes and 10 g. [support-foot-review.json](support-foot-review.json)
records the path comparison and startup-command check;
[print-jobs.json](print-jobs.json) records submission hashes and printer state.
The editable project's meshes and placements are byte-identical to its
preceding saved version. The initial support bonding is reported above;
completed-part quality is unobserved.

## Cavity trial — 2026-09-14

Derek reports this job failed. His photograph shows tall tree supports detached
from the Textured PEI plate and lying beside the cavity, with loose extrusion
around the flange. The exact detachment layer is unknown. H2C reported FAILED
at 15:16 UTC, with no active print error or HMS entry. Derek cleared the plate
and confirmed it ready for a retry. The retry process uses 8 mm Support →
Initial layer expansion and retains the +0.18 mm trim.

H2C accepted plate 1 of `funnel-mold-h2c.gcode.3mf` through Bambu Connect.
The job uses AMS A2 PETG Translucent, the left 0.8 mm High Flow nozzle,
Textured PEI, +0.18 trim, stock filament operating settings and a 0.40 mm
first layer. Bed leveling is enabled. The cavity has 331 layers; its slicer
estimate is 18 h 22 min and 643 g. At 06:26 UTC the printer reports RUNNING
at layer 1, with no print error or HMS entry. Its nozzle is 250 °C and its
bed is 70 °C. [print-jobs.json](print-jobs.json) holds the submitted file
and G-code hashes, settings and printer observation.

## Tree-support detachment — 2026-09-14

Derek reports two stopped attempts on the printer named H2C, using Textured
PEI and +0.18 mm trim. Several supports lifted in the first attempt before
reaching the model; one support fell in the second. The failed job bytes,
detachment heights and first-layer photographs were not captured here.
The +0.04 and +0.18 trims come from dozens of PET-GF calibration prints;
their transfer to PETG has not been established.

The saved project selected Engineering Plate. Its PETG Translucent profile
used 255 °C for both first and subsequent layers, and 18 mm³/s for High Flow.
The installed Bambu H2C 0.8 PETG Translucent defaults are 250 °C first layer,
245 °C afterward and 16 mm³/s for both nozzle types. The mold's 0.32 mm first
layer also differs from the stock process's 0.40 mm. The saved bed temperature,
cooling, support speed and tree branch settings match the stock presets.
These differences do not establish which condition detached the supports.

## Rod fit — 2026-09-13

Derek reports that the steel rod was nearly impossible to press into the
recently printed core. He could not establish whether it reached its seat;
the rod interfered with closing the core and cavity. The exact printed source
revision and the measured socket, rod and insertion dimensions were not
identified. No measurement establishes which surfaces made contact.

## Dry fit — 2026-09-12

Derek reports that the recently printed cavity and core fit tightly before
finishing. He is skeptical that sanding will provide a clean fit with room
for primer. He also reports a small departure from flatness, with the bodies
too stiff for his available clamps to pull together. The exact source revision
of this pair was not identified. No coated fit or casting result was reported.

## Solid cavity — 2026-09-10

Mark2 reported `Funnel_mold_-_solid_cavity_and_core`, 304 layers, 18 h 59 min 7 s
and 1,315.70 g. The reference project is `solid/solid-mold.3mf` at Git revision
`46295bf93`, SHA-256
`8019a34f5062a185253bfe8ae5b906343ed8e454f589b75de5106e647a5e1a50`.
The device's title, layer count, time and mass match that archive; the printer's
job bytes were not downloaded for comparison.

At layer 178 the device showed 255 °C nozzle, 70 °C bed and 100% speed. The camera
showed uneven bands and loose strands on the visible outer wall. Derek supplied
`IMG_7779.jpeg`, `IMG_7778.jpeg` and `IMG_7777.jpeg` from the opposite side. Those
photos show a substantial clump of tangled extrusion at an outer corner, long
loose strands below it and strings across the forming cavity. The adjacent broad
wall is comparatively regular. Adhesion and the condition of the hidden wall
were not established by the camera view.

At Z 44.8 mm the archived G-code begins its exterior perimeter at printer XY
(68.731, 77.753), on a rounded corner. That perimeter commands 55–60 mm/s and 90%
part cooling. The photos are not registered to printer XY, so their relationship
to this seam is an inference. Neither the photos nor the path reading establishes
a single cause for the failure.

At layer 185 Mark2 still reported 100% speed. Selecting Bambu Studio's speed
control did not open a selector or change that reading. No runtime speed change,
pause, stop or replacement print was sent.

On 2026-09-11 Derek reported that the defect was confined to the observed layers
and that the print recovered higher up. He judged the important surfaces good
enough to sand and use. Sanding, coating, vacuum cycling and casting results have
not been reported. He also reported starting the next piece; its exact project
and plate were not identified in that message.
