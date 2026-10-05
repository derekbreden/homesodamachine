# Frame and fit plate

The [input project](2026-10-04-rc62-valve-frame-fit-mark2-v2-input.3mf)
contains one flush-ceiling funnel frame, seventeen labeled open RC62 pockets
and five upright four-socket valve panels. The
[snapshot](snapshot.json) binds the input, native archive and every review by
SHA-256. The [launch receipt](../mark2-v2-launch.json) records the accepted job.

The frame retains four bed-rooted rail supports. Its roof-side expansion has
six walls and no support contacts. The fit objects retain two walls, 15% infill,
the production 0.9555 flow ratio and zero XY compensation; their supports are
disabled individually. This plate contains no insertion pause.

[Native review](emitted-path-review.json) passes source binding, first-layer
continuity, full-bead bed margins, object separation, frame component coverage,
wall placement, left-nozzle use and the emitted +0.02 mm Textured PEI trim. All
four support bodies have an outward X removal route clear of the native frame
stock at their supported layers. Release the interface contacts and cut
sacrificial branch junctions before pushing a support outward.

The [independent fit review](../../../../fixtures/valve-socket-fit/tighter-trial-v2/combined-mark2-native-check.json)
passes all seventeen RC62 mouths and curved seats, all twenty valve socket
sections and blind floors, and the absence of fit-object support roads.

The native estimate is 9 h 37 m 50 s and 357.43 g. Emitted paths do not establish
physical adhesion, support-removal effort, friction fit, magnetic retention or
strength. The frozen preparation and slice reports retain their preparation
phase fields, including `submitted: false` and
`native_slice_awaiting_emitted_review`. The emitted review records its pass;
the [launch receipt](../mark2-v2-launch.json) carries current printer acceptance
for task **1310076386**.
