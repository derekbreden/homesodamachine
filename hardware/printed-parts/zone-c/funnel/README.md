# Funnel and sliding frame

The removable silicone funnel holds nominally [455 mL](FUNNEL_CAP). Its PET-GF
frame slides into front-top; closing front-top onto back-top captures the rear
rails. The frame uses the enclosure's production rail section and its running
clearances. Both flavors share this filling interface.

The [lift-off cover](../funnel-cover/README.md) closes the mouth between fills.
Remove it before pouring or lifting the silicone out, and reseat it after filling.

## Silicone

The collar center is world X0, Y164.55. Its brim underside is Z349 and its
6 mm brim finishes flush with the Z355 enclosure roof. The collar is
165 × 117.683 mm with R20 corners; the mouth is 153 × 105.683 mm with R14 corners;
the brim is 179 × 131.683 mm with R27 corners. The collar wall and ramp's normal
wall are 6 mm. The ramp falls toward X1.85, Y164.55, centred in Y.

The native cavity holds 455.437 mL to the brim. The brim pocket keeps a 3.114 mm
roof landing behind the display facet's arris, including its 0.25 mm running air.
The drain exits at X1.85, Y164.55, Z306.05. Geometry and clearances are recorded in
[`integration-review/forward-expansion-check.json`](integration-review/forward-expansion-check.json).

The integral silicone plug is a [36 × 41.0 mm](FUNNEL_PLUG) rectangle with square corners,
centred on the outlet, 12.85 mm tall with its flat bottom at Z306.05 resting on the cradle's
hook tops. Its walls run up into the bowl's underside, so none of its top shows. Its lower bore has an
8.4 mm entrance,
1.8 mm lead-in and 6.7 mm relief. A nominal 6 mm bore forms the upper 3 mm
sealing land. This geometry describes the proposed push-on seal; its wet and
dry retention and sealing performance have not been physically qualified.

The intended cleaning motion is lifting the whole silicone funnel out by hand.
Its sealing land slides off the raw 1/4-inch LLDPE drain stub, which stays standing in the drain
elbow's collet under the frame. To refit, press the plug into the frame's socket
until its flat bottom bears on the cradle's hook tops and the brim seats on the roof ledge.
The [mold shells and contoured mandrel](../funnel-mold/README.md) form the complete
plug and staged bore. Their native geometry and slice checks do not establish
the finished silicone's wet seal, dry retention or removal force.

## PET-GF frame

The frame is 207 mm wide and 142.283 mm long. Its entire underside is flat at
Z299.9. Its socket floor is Z302.9, with a 3 mm web beneath it and 3.15 mm air to the
silicone block's lower face between the hook tops. An [11.25 mm](FRAME_HOLE) hole at
X1.85, Y164.55 passes the drain elbow's collet. Its fixed nose face stands 0.65 mm
below the frame's underside in the released pose. The plug socket is a
[36.6 × 41.6 mm](FRAME_SOCKET) rectangle centred on that
hole, its corners rounded by the plug's gap, with a 1 mm lead-in at its mouth. Its ±Y walls stand
on the far ends of two straight
[5.49 × 32.3 mm](FRAME_SLOTS) slots through the web, one each side of the hole, that take
the elbow cradle's wings, so no strip of web stands between a slot and a wall.

Both end corbels are 30° from vertical, across the complete X width, including
the rail wings. The lower footprint runs from Y119.1 to Y210. The body widens
upward to Y93.408 and Y235.692. The rail datum is Z306.9 and its top is Z321.7.
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
block's top stands 1 mm under the top of the vertical leg's root band: the pocket wraps the band
about 78% of the way round, and the collar, rung and nose stand free above it. The [drain stub](/hardware/reference/funnel-drain-stub/funnel_drain_stub.py)
stands in the elbow's upper collet and up into the plug's land, and `fluid-4` leaves the elbow's
aft collet for V-B.

Both X sides of the block carry on up the body's full [31.8 mm](CRADLE_LENGTH) length as
[1.3 mm](CRADLE_WING_T) wings, [15.64 mm](CRADLE_WING_H) above the body, through the frame's
slots. Each ends in a flat hook reaching [3.1 mm](CRADLE_HOOK) outward,
[2.6 mm](CRADLE_OVERLAP) past its slot's outer edge, to within
[0.15 mm](CRADLE_TIP_GAP) of the counterbore's X wall. The cradle releases
[0.65 mm](CRADLE_CATCH) from its insertion datum until the hook undersides bear on the web.
The 3.15 mm thick hooks' flat tops at Z306.05 then bear beneath the silicone block over
269.895 mm² in the native geometry.
That reach sets the cradle's [30.1 mm](CRADLE_WIDTH) width and leaves
[4.44 mm](CRADLE_WEB) of web between each slot and the drain hole. Pushed up, each wing bends [2.53 mm](CRADLE_BEND) inward at its
hook into a [3.69 mm](CRADLE_LANE) lane inboard of it. A tip-loaded cantilever estimate puts the
root strain near [3.2%](CRADLE_STRAIN). The [cradle trial](cradle-trial/README.md) tests the snap.
The accepted v4 trial applies to its frozen meshes; the current hook thickness, slots and
block bearing need a separate physical trial.

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
