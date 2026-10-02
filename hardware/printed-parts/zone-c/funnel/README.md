# Funnel and sliding frame

The removable silicone funnel holds nominally [300 mL](FUNNEL_CAP). Its PET-GF
frame slides into front-top; closing front-top onto back-top captures the rear
rails. The frame uses the enclosure's production rail section and its running
clearances. Both flavors share this filling interface.

## Silicone

The collar center stays at world X0, Y182.5. Its brim underside is Z349 and its
6 mm brim finishes flush with the Z355 enclosure roof. The collar is
165 × 81.783 mm with R20 corners; the mouth is 153 × 69.783 mm with R14 corners;
the brim is 179 × 95.783 mm with R27 corners. The collar wall and ramp's normal
wall are 6 mm. The ramp falls toward X1.85, Y182.5.

The integral silicone plug is a [36 × 44.1 mm](FUNNEL_PLUG) rounded rectangle with
[R1](FUNNEL_PLUG_CORNER) corners, centred on the outlet, 15 mm high, with its bottom at Z302.9.
Two notches along its X sides, open at its underside, house the elbow cradle's hooks and end
[1 mm](FUNNEL_PLUG_WALL) short of its +Y end. Its lower bore has an 8.4 mm entrance,
1.8 mm lead-in and 6.7 mm relief. A nominal 6 mm bore forms the upper 3 mm
sealing land. This geometry describes the proposed push-on seal; its wet and
dry retention and sealing performance have not been physically qualified.

The intended cleaning motion is lifting the whole silicone funnel out by hand.
Its sealing land slides off the drain stub, which stays standing in the drain
elbow's collet under the frame. The existing mold tooling and its slice records
do not qualify this plug.

## PET-GF frame

The frame is 207 mm wide and 106.383 mm long. Its entire underside is flat at
Z299.9, leaving 3 mm below the silicone plug. An [11.25 mm](FRAME_HOLE) hole at
X1.85, Y182.5 passes the drain elbow's collet, and the web round it bears on the
elbow's nose. The plug socket is a [36.6 × 44.7 mm](FRAME_SOCKET) rounded rectangle
centred on that hole, with a 1 mm lead-in at its mouth. Two straight
[5.18 × 32.8 mm](FRAME_SLOTS) slots through the web, one each side of the hole,
take the elbow cradle's wings.

Both end corbels are 30° from vertical, across the complete X width, including
the rail wings. The lower footprint runs from Y155 to Y210. The body widens
upward to Y129.308 and Y235.692. The rail datum is Z306.9 and its top is Z321.7.
The broad body fills the stock between its bowl clearance and rails.
The funnel's brim bears on the enclosure's recessed roof ledge around its collar.

The frame prints on its underside. The exported individual STEP and STL place
that face at Z0 and the funnel's plan center at X0, Y0. Functional rail catches
retain their square bearing faces and accessible supports. Use the enclosure's
PET-GF support-removal strategy; physical surface and fit qualification remain
separate from geometric checks.

## Elbow cradle

The PET-GF cradle holds the scanned [PP0308E elbow](/hardware/reference/jg-pp0308e-elbow/README.md)
under the frame's drain hole, its vertical leg up the hole and its horizontal leg aft toward V-B.
The cradle is the block under the elbow less the elbow's upward shadow grown by
[0.15 mm](CRADLE_SLIP), so the elbow drops straight in and every pocket face opens upward. The
block's top is the underside of the vertical leg's collar: the pocket wraps the root band about
78% of the way round, and the collar, rung and nose stand free above it. The [drain stub](/hardware/reference/funnel-drain-stub/funnel_drain_stub.py)
stands in the elbow's upper collet and up into the plug's land, and `fluid-4` leaves the elbow's
aft collet for V-B.

Both X sides of the block carry on up the body's full [31.8 mm](CRADLE_LENGTH) length as
[1.3 mm](CRADLE_WING_T) wings, [11.24 mm](CRADLE_WING_H) above the body, through the frame's
slots. Each ends in a flat hook reaching [3.1 mm](CRADLE_HOOK) outward,
[2.6 mm](CRADLE_OVERLAP) past its slot's outer edge and [0.4 mm](CRADLE_CATCH) over the web,
to within [0.15 mm](CRADLE_TIP_GAP) of the counterbore's X wall, in a notch in the plug's side.
That reach sets the cradle's [30.1 mm](CRADLE_WIDTH) width and leaves
[4.75 mm](CRADLE_WEB) of web between each slot and the drain hole. Pushed up, each wing bends [2.42 mm](CRADLE_BEND) inward at its
hook into a [3.38 mm](CRADLE_LANE) lane inboard of it. A tip-loaded cantilever estimate puts the
root strain near [5.5%](CRADLE_STRAIN). The [cradle trial](cradle-trial/README.md) tests the snap.

The cradle prints on its bottom. The hooks' flat undersides are retention bearings and take
accessible supports.

## Regenerate

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/funnel.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/funnel_frame.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/elbow_cradle.py
```

The assembly places all three parts through
[`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py).
The shell uses `funnel_frame.receivers` and `funnel_frame.shell_clearance` for
its matching enclosure features.

## Integration checks

[`integration-review/rail-motion-check.json`](integration-review/rail-motion-check.json)
records sampled insertion of the exported frame through both actual upper shells,
their closing motion, and capture against 2 mm translations on all three axes.
Run `integration-review/check_fit.py` from the CAD environment to refresh it.

The current frame requires its own native slice and physical support-removal and fit review.
The stored native slice uses a 0.20 mm first layer, 0.24 mm subsequent layers,
and six walls through the 44.499 mm corbel band. Its four support bodies reach
only the four rail bearing regions; none start on the model. The
[`support audit`](integration-review/frame-support-audit.json) includes unlabelled
support bodies. These records describe the slice, not a physical fit test.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/funnel/elbow_cradle.py`
- `/hardware/printed-parts/zone-c/funnel/funnel.py`
- `/hardware/printed-parts/zone-c/funnel/funnel_frame.py`
