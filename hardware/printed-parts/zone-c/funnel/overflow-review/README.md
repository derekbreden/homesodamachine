# Funnel overflow and roof runoff

The customer can keep pouring after the funnel is full. The removable silicone
funnel therefore includes a continuous apron across the exposed frame/roof
joints to the enclosure's exterior sides. An integral underside rib contacts
the roof outside the frame opening, opposing runoff beneath the apron.
The funnel, apron and rib are one casting and lift out together for cleaning.

![Integral silicone apron covering the frame joints, highlighted in gold](assembly.png)

| Datum | Native design |
| --- | --- |
| Frame-bearing underside | Z349 mm |
| Rigid roof | Z355 mm |
| Mouth rim and cover seat | Z358 mm |
| Highest point with cover | Z361 mm |
| Apron plan | 215 × 155.392 mm, Y87.0–242.392 |
| Apron sheet | 2.5 mm |
| Rib's bottom contact band | 1.5 mm wide, Z354.7 mm |
| Nominal flat-roof seating interference | 0.3 mm |
| Capacity to the mouth rim | 530.54 mL |
| Finished casting volume | Approximately 274.9 mL |

The rib is a local cast-silicone sealing feature. Its nominal interference
allows seating; it does not establish sealing force or water exclusion.
The surrounding apron can bend while the brim and outlet block bear on
their existing frame/cradle seats. The drain stub, collar, frame and shell
fits use their existing datums. Fit the silicone after closing the upper
shell screws; lift the apron for screw access and wipe both faces when cleaning.

[The native review](native-review.json) binds the source and finished STEP
files. It records intended contact only within the underside rib, the cover's
four silicone pads, and sampled vertical extraction clearance. The
[cover review](../../funnel-cover/geometry-check.json) checks its assembled
placement, neighboring hardware and removal.

The two-piece [mold](../../funnel-mold/README.md) forms the complete apron and
rib with the same straight stock outlet rod. Its [design record](../../funnel-mold/design.json)
records closure, core lift, rod withdrawal and nominal casting equality.
The [chamber review](../../funnel-mold/chamber-check.json) includes M4 closure
hardware and the dry-side breather drill paths. Current tooling needs its
own production slice; dated print receipts apply to their identified artifacts.

The native aggregate refresh replaces only the named front-top, funnel and
cover members. The front-top uses its continuous display backing wall. Every
other original STEP entity record remains unchanged; named native geometry,
colors and viewer arrays are also checked. The refresh scripts are manual
review tools and are not called by a generator or build.

Physical overpour and roof-runoff exclusion have no recorded cast-part result.
No sealing-force or lifetime qualification is inferred from the CAD checks.
