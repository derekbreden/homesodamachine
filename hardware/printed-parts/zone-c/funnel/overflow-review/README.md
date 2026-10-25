# Funnel overflow and roof runoff

The customer can keep pouring after the funnel is full. The removable silicone
funnel therefore includes a continuous apron across the exposed frame/roof
joints to the enclosure's exterior sides. Its broad, flat underside rests
on the roof outside the frame opening.
The funnel, apron and rib are one casting and lift out together for cleaning.

![Integral silicone funnel and roof apron](assembly.png)

| Datum | Native design |
| --- | --- |
| Frame-bearing underside | Z349 mm |
| Rigid roof | Z355 mm |
| Mouth rim and cover seat | Z358 mm |
| Highest point with cover | Z361 mm |
| Apron plan | 215 × 190.392 mm, Y87.0–277.392 |
| Apron sheet | 3 mm |
| Flat apron underside | Z355 mm |
| Capacity to the mouth rim | 698.21 mL |
| Finished casting volume | Approximately 331.0 mL |

The apron has one roof-bearing plane. The brim's 6 mm underside shoulder
fits the recessed frame. The surrounding apron can bend while the brim and outlet block bear on
their existing frame/cradle seats. The drain stub, collar, frame and shell
fits use their existing datums. Fit the silicone after closing the upper
shell screws; lift the apron for screw access and wipe both faces when cleaning.

[The native review](native-review.json) binds the source and finished STEP
files. It records roof and frame fit, cover clearance and sampled vertical
extraction clearance. The [frame review](../drop-in-review/native-review.json)
records the removable frame, original drain snap web and J10 tool passages. The
[cover review](../../funnel-cover/geometry-check.json) checks its assembled
placement, neighboring hardware and removal.

The two-piece [mold](../../funnel-mold/README.md) forms the complete apron and
rib with the same straight stock outlet rod. Its [design record](../../funnel-mold/design.json)
records closure, core lift, rod withdrawal and nominal casting equality.
The [chamber review](../../funnel-mold/chamber-check.json) includes M4 closure
hardware and the dry-side breather drill paths. Current tooling needs its
own production slice; dated print receipts apply to their identified artifacts.

The [post-publication mesh review](mold-mesh-review.json) identifies the retained
tool-entry notches, flat clamp bearings and 0.30 mm finishing pocket.

The review can run with `--geometry-only` to read the individual current exports.
Its aggregate refresh mode replaces only the named funnel and cover members. Every
other original STEP entity record remains unchanged; named native geometry,
colors and viewer arrays are also checked. The refresh scripts are manual
review tools and are not called by a generator or build.

Physical overpour and roof-runoff exclusion have no recorded cast-part result.
No sealing-force or lifetime qualification is inferred from the CAD checks.
