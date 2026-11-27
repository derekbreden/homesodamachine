# WAGO pocket fit and support removal

## Selected Mark2 openings

Three recessed bars identify this plate. Hold each coupon with the dots up and the opening facing you. X is the short dimension between the cheeks and Y runs from the floor to the roof.

| Dots | Connector | Requested X × Y | Clear X × Y in the G-code |
| --- | --- | --- | --- |
| 1 | 10-way, 221-420 | 15.70 × 30.10 mm | 15.70 × 29.94 mm |
| 2 | 5-way, 221-415 | 8.10 × 30.10 mm | 8.10 × 29.94 mm |
| 3 | 3-way, 221-413 | 8.20 × 18.70 mm | 8.20 × 18.66 mm |

Each coupon has one removable tree rooted on its pocket floor. The long dimension in the slice runs from the deposited floor to the underside of the first bridge bead on the production layer schedule. The 10-way opening repeats the clear span of the original one-dot support-removal coupon. [Measured toolpaths](prints/2026-11-27-fit-c-mark2/fit-toolpaths.json) · [Mark2 print record](prints/2026-11-27-fit-c-mark2/print-job.json)

## Three-size fit comparison

In the incremental comparison, one recessed bar identifies the Mark1 set and two bars identify the Mark2 set. Each plate carries one separate coupon for each connector.

| Dots | Connector | Mark1 X × Y | Mark2 X × Y | Insertion depth |
| --- | --- | --- | --- | --- |
| 1 | 10-way, 221-420 | 15.70 × 30.20 mm | 15.70 × 30.40 mm | 8.70 mm |
| 2 | 5-way, 221-415 | 8.00 × 30.00 mm | 7.80 × 29.80 mm | 8.70 mm |
| 3 | 3-way, 221-413 | 8.30 × 18.70 mm | 8.10 × 18.50 mm | 9.45 mm |

The table gives the designed openings. The 0.20 mm increment applies to the entire opening. Both earlier 3-way pockets felt loose, so the three-way comparison coupons share the smaller tested opening, 8.70 × 19.10 mm, as their reference. All six use the same floor-rooted removable tree and pry stock as the first comparison. The `--fit` option on the coupon source generates the three sets for the `wago-fit-a`, `wago-fit-b` and `wago-fit-c` plate recipes.

On the production 0.24 mm layer schedule, each 0.20 mm change in the designed long dimension moved the underside of the first bridge by a full layer. The measured opening from the top of the floor to the underside of the first roof bead is 30.18, 29.94 and 18.66 mm on Mark1, and 30.42, 29.70 and 18.42 mm on Mark2, in 10-, 5- and 3-way order. [Mark1 toolpaths](prints/2026-11-27-fit-a-mark1/fit-toolpaths.json) · [Mark2 toolpaths](prints/2026-11-27-fit-b-mark2/fit-toolpaths.json)

The [one-bar Mark1 job](prints/2026-11-27-fit-a-mark1/print-job.json) and [two-bar Mark2 job](prints/2026-11-27-fit-b-mark2/print-job.json) identify the exact files sent to each printer.

## Original support-removal coupons

Each coupon has one blind production pocket and one removable tree. The tree sits over the pocket floor and flares into a three-course crown beneath the transverse roof bridge. The 8 mm side cheeks and blind back, 7.16 mm floor and 6 mm roof give a screwdriver a solid edge to bear against. The dots recessed into the top of the blind back identify the specimen after removal from the plate.

| Dots | Printer | Production pocket | Sites | Width × height × depth |
| --- | --- | --- | ---: | --- |
| 1 | Mark1 | Front top, MAN-A, WAGO 221-420 | 1 | 15.70 × 30.00 × 8.70 mm |
| 2 | Mark1 | Front top, MAN-B, WAGO 221-415 | 1 | 8.20 × 30.20 × 8.70 mm |
| 3 | Mark2 | Back top, WAGO 221-413, three mains and three west-wall junctions | 6 | 8.70 × 19.35 × 9.45 mm |
| 4 | Mark2 | Cold-core lid, WAGO 221-413, both banks | 4 | 8.70 × 19.10 × 9.45 mm |

![Sections through the four sliced coupons, with one floor-rooted tree and its contact cap in each well](coupon-sections.png)

The coupons use the production [removable tree](../../printed-parts/enclosure/enclosure/back-top/print_supports.rs). Its crown extends 0.24 mm past the mouth to back the outside perimeter. In the emitted toolpaths each 3.34 mm foot sits entirely over the pocket floor. The longest unbacked section of either mouth-wall road measures 0.017 mm in all four slices. Both plates use black Fiberon PET-GF15 with smooth timelapse and a cooling tower. The shortest commanded deposition time spent away from a coupon between pocket layers ranges from 28.01 to 29.28 seconds. [Mark1 front plate toolpaths](prints/2026-11-27-front-mark1/coupon-toolpaths.json) · [Mark2 rear and lid plate toolpaths](prints/2026-11-27-rear-lid-mark2/coupon-toolpaths.json)

The [coupon source](coupon.rs) produces the four STLs and their support records. The `front-wago-pry` and `rear-lid-wago-pry` entries in the [plate recipes](../../printed-parts/enclosure/trial-preparation/pieces.json) prepare the Mark1 and Mark2 projects.

The [Mark1 job](prints/2026-11-27-front-mark1/print-job.json) carried the one- and two-dot coupons. The [Mark2 job](prints/2026-11-27-rear-lid-mark2/print-job.json) carried the three- and four-dot coupons. Derek removed the trees on the bench. The 10-way felt right on its short side and barely tight on its long side. The 5-way felt barely loose on both sides. Both 3-way openings felt loose in both directions. [Front coupon observations](prints/2026-11-27-front-mark1/physical-result.json) · [Rear and lid coupon observations](prints/2026-11-27-rear-lid-mark2/physical-result.json)
