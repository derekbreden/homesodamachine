# Funnel and sliding frame

The removable silicone funnel holds nominally [600 mL](FUNNEL_CAP). Its PET-GF
frame slides into front-top; closing front-top onto back-top captures the rear
rails. The frame uses the enclosure's production rail section and its running
clearances. Both flavors share this filling interface.

## Silicone

The collar center stays at world X0, Y182.5. Its brim underside is Z349 and its
6 mm brim finishes flush with the Z355 enclosure roof. The collar is
165 × 151 mm with R20 corners; the mouth is 153 × 139 mm with R14 corners;
the brim is 179 × 165 mm with R27 corners. The collar wall and ramp's normal
wall are 6 mm. The ramp falls toward X1.85, Y182.5.

The integral silicone plug is [36 mm](FUNNEL_SPOUT_OD) in diameter and 15 mm
high, with its bottom at Z302.9. Its lower bore has an 8.4 mm entrance,
1.8 mm lead-in and 6.7 mm relief. A nominal 6 mm bore forms the upper 3 mm
sealing land. This geometry describes the proposed push-on seal; its wet and
dry retention and sealing performance have not been physically qualified.

The intended cleaning motion is lifting the whole silicone funnel out by hand.
Tube retention and the final connection to V-B remain unresolved. The assembly
shows the plain frame hole and carries that open requirement on its scorecard.
The existing mold tooling and its slice records do not qualify this plug.

## PET-GF frame

The frame is 207 mm wide and 111.697 mm long. Its entire underside is flat at
Z299.9, leaving 3 mm below the silicone plug. A plain 6.85 mm through hole sits
at X1.85, Y182.5. The plug socket is 36.6 mm in diameter.

Both end corbels are 30° from vertical, across the complete X width, including
the rail wings. The lower footprint runs from Y155 to Y210. The body widens
upward to Y126.652 and Y238.348. The rail datum is Z306.9 and its top is Z321.7.
The broad body fills the stock between its bowl clearance and rails.
The funnel's brim bears on the enclosure's recessed roof ledge around its collar.

The frame prints on its underside. The exported individual STEP and STL place
that face at Z0 and the funnel's plan center at X0, Y0. Functional rail catches
retain their square bearing faces and accessible supports. Use the enclosure's
PET-GF support-removal strategy; physical surface and fit qualification remain
separate from geometric checks.

## Regenerate

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/funnel.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/funnel_frame.py
```

The assembly places both parts through
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
- `/hardware/printed-parts/zone-c/funnel/funnel.py`
