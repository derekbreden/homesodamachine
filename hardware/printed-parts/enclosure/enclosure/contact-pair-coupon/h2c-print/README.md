# H2C contact-seat trial

One male and one female coupon, using the [production-derived geometry and
physical checks](../README.md). The reviewed native slice has **zero support
paths**, uses the left hardened 0.4 mm nozzle and black PET-GF, and estimates
22 minutes 14 seconds. The requested H2C Z trim is **+0.18 mm**; textured-plate
compensation emits `G29.1 Z0.16`.

H2C accepted this pair as task **1302534665** through Bambu Connect, with no
reported print error. [launch.json](launch.json) records the printer receipt,
archive and imported-copy hashes, settings, startup state and spacing evidence.

The coupons retain their production print poses. The male's cropped bed matches
front-top's layer phase; the female prints on the clamp's real crown. The first
layer is 0.20 mm and ordinary layers are 0.24 mm. Elephant-foot compensation is
zero to preserve the first-layer footprint. There is no brim.

The shared automatic tree recipe creates three support bodies and five interface
islands at the male pocket roof, female pocket roof and crown grooves, including
a small model-rooted body. [automatic-support-audit.json](automatic-support-audit.json)
records those paths. Coupon-only facet blockers remove that support for the
requested unsupported trial. The mesh geometry and shared support settings are
unchanged; [unsupported-support-audit.json](unsupported-support-audit.json)
confirms no support bodies remain.

[preflight.json](preflight.json) binds the frozen STL hashes to the native archive,
records the Z commands and locates the roofs in the toolpaths. The longest roof
bridge paths are 23.216 mm on the male coupon and 22.882 mm on the female. The
pocket depth is the bridge's width; the physical check assesses sag across its
long span.

Second-layer outer walls have at least 64.2% bead-area overlap with the first-layer
footprint on the male and 98.1% on the female. Three short female inner-wall
corner segments have lower individual overlap. They are 0.032–0.185 mm long and
join longer anchored inner-wall paths; their exact coordinates and widths are
retained in the preflight record.

Print options are Timelapse On, Bed Leveling On, Flow Dynamic Calibration Auto,
and Nozzle Offset Calibration Auto. [preparation.json](preparation.json) records
the project settings and bed placement. Bambu Connect submission uses the
existing background accessibility sender. A printer receipt and new task ID
are required before recording a launch.

[connect-readiness.json](connect-readiness.json) records a successful background
dry run with Send enabled, the external PET-CF-labelled PET-GF spool selected,
and those four options confirmed. The dialog was cancelled without submission.
[prestart-status.json](prestart-status.json) records H2C's finished grip insert and
Mark2's running back-bottom immediately before submission. The user's start
request confirms the bed is clear, following the
[printer instructions](../../../../../../tools/bambu-printers.md#what-ready-looks-like-from-software).
[queue.json](queue.json) records the prepared order: these contact coupons,
followed by the funnel's receiver/cradle trial after this bed is cleared again.

To prepare fresh automatic and unsupported slices, then review them:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/h2c-print/prepare.py --revision 3
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/h2c-print/prepare.py --revision 4 --unsupported
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/h2c-print/verify.py --revision 4 --automatic-revision 3
```

Each revision uses a separate directory in `.cache/prints/`. Reusing a reviewed
input is refused. The export generator is bound to its recorded Git revision;
README-only generator amendments are checked separately from its geometry code.

The print authorizes the local fit, unsupported-roof and wire-passage trial. The
M1.4 installation check awaits the specified inserts and screws. Hand mating
checks polarity and continuity; it does not reproduce the installed face gap.

## Bench check

This trial selects the seat clearance, unsupported-roof treatment and wire
passage before printing the large production parts. Use the delivered connector
pair, the recorded NEIKO digital caliper and AstroAI continuity meter, and the
intended 22 AWG leads. Keep the pair unpowered for continuity readings.

Seat each half by hand against its ear-plate datum, then remove it again and
check for binding or roof witness marks. Measure the pocket's vertical clearance
at the centre of the span with the caliper's inside jaws; check the mouth and
the back of the body pocket, retaining the smaller reading. It must be at least
4.08 mm. The drawn 4.55 mm seat therefore permits at most 0.47 mm of roof sag.
Leave the roof as printed for this check.

With the connector seated, use the caliper's step-measuring faces between the
coupon face beside the mouth and the connector's plastic mating face, clear of
the projecting pins. Check near both ends. Each plastic face must finish within
±0.1 mm of the coupon face. The nominal installed compression and the limit of
hand mating are explained in the coupon's physical-check document.

Route the soldered leads through the male teardrop or the female crown slot and
grooves, then repeat seating and removal. The leads must clear without holding
the half off its datum or projecting above the female crown. Finally, mate the
pair in its attracting orientation and probe the tails: each male contact must
connect to exactly one corresponding female contact, with no connection to the
other three. This checks continuity and wiring isolation; it does not measure
contact resistance or qualify operating life.
