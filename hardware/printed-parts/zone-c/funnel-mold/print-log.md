# Funnel mold print log

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
