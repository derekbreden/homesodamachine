# Sculpted faucet at the machine's Z feed on the glued Engineering Plate, Mark2

The [print plate](sculpted-faucet-machine-z-engineering-black-mark2.gcode.3mf) and
[editable project](sculpted-faucet-machine-z-engineering-black-mark2.3mf) hold the complete black
PET-GF faucet: the Sculpted base, the tip, the display cover, the mounting plate and the lever.
`faucet-plate sculpted --production` prepared them from the checkout at
[`47ab7d77d`](https://github.com/derekbreden/homesodamachine/tree/47ab7d77d9e49efeaabb429c454e58c35ca09e8a),
so the plate is also the Sculpted product plate of that commit. The [package record](package.json)
binds the archive's G-code and the acceleration planner's estimate of its motion.

The plate goes on Mark2's glued Engineering Plate. Its first layer stands the
[plate's selected bed trim](https://github.com/derekbreden/homesodamachine/blob/47ab7d77d9e49efeaabb429c454e58c35ca09e8a/tools/hsm/print-prep/faucet-plate.json)
above Bambu's own plate compensation, which on this plate and nozzle sends nothing but the start
code's clear; the stopped Mark 1 back-top on the same kind of plate sent only that clear.

Beside the [restored plate](../2026-11-14-seven-courses-restored-mark2/README.md) Derek last
printed, this plate carries:

- The base's seven foot courses at the machine's own Z feed, the M203 the plate sends, for every
  move the foundation lays, crosses or hops. Their show lap and rings take the outer wall speed and
  acceleration the slicer gives the base's level layers, and their fill its internal solid infill
  speed and default acceleration, each bead held to the filament's volumetric limit. Where the lap
  climbs or drops the Z feed holds it; where it runs level it reaches the level walls' speed. The
  bridge course over the roof keeps its bridge speed and fan; the half-lift on the descending side
  and the course spacing are as printed.
- The tip's tilted shoulder courses at the machine's Z feed, and one donor course of air between
  the shoulder's interface and its first course, as the base's first course has one course of air
  over its roof. On the restored plate two courses of air stood there.
- The tip's display pocket front corners standing under the cover's front rim, and its flat
  dispense face, which leave the tip's passage without the support column the restored plate laid.

The [verification](verification.json) records the checks the plate passed before it was sent:
its [recipe against the restored plate](recipe-printed-vs-final.txt) and
[against the checkout before these changes](recipe-baseline-vs-final.txt), the head-to-plastic
reading, the cooling stages and the tip-end splice ([receipts](cooling.json)), the first-layer
commands, the support by the tip's new corners, the foot courses' and show lap's planned speeds,
and the tip shoulder's footing. The [foundation record](foundation.json) gives the foot's stack and
the limits it was laid to, the [tip courses' report](tip-courses.json) and [warp](tip-warp.json)
the tip's tilted courses, and the [flow cap](flow-cap.json) the tip moves the volumetric limit
holds.

No print has tested the foot's or the tip's speeds, the tip's one course of air, the Engineering
Plate first layer with its trim, or the tip's new corners.

[Reproduce the plate](REPRODUCE.md).
