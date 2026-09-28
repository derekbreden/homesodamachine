# Machine display retention receiver · H2C

H2C task **1289537122** reports RUNNING at layer 0/252 at 2026-09-28T07:13:16.919764+00:00.
Derek confirms clearing the extrusion overload and pressing Resume using the
[cut–unload–remove–reload sequence](startup-recovery.json). The print-error field
is 0; the overload HMS remains listed. The exact resume time is unknown, so its
shared-circuit spacing cannot be verified. The agent issued no resume command.

One receiver in black PET-GF on the left 0.4 mm Standard nozzle.
Native estimate: 173.1 minutes, 72.4 g using the saved profile density, 252 layers.

The symmetric cover has 3.6 mm hook projection, centered 75 mm leaves, 0.9 mm inset
per side, 0.5 mm extra axial reach, 0.98 mm nominal bearing clearance and R0.8 inner
root fillets. Nominal catch overlap is 3.1 mm per side, at least 2.8 mm at full lateral
float. The matching receiver has open flex lanes and 0.5 mm slot clearance at each end.
The cover's visible bezel and window retain their production dimensions.

Display plane at 30 degrees, matching front-top. Both use 0.24 mm layers, a 0.20 mm first layer, two walls,
saved speeds and wall order, 15% infill overlap, and the printer's standing Z trim.
Open underside and back, inside the cheeks, before inserting the cover or display. All emitted support paths, including unlabelled contacts,
span both functional bearings. Removal effort and printed contact finish remain untested.

The geometry reading covers symmetry, root stock, clear seating and rigid insertion
envelopes. It does not measure bending strain, insertion force or shake retention.
The physical test is for both leaves to return outward, both hooks to catch fully,
the bezel to relax flat, and the cover to stay engaged when shaken.

[Manifest](manifest.json), [geometry](geometry-check.json), [native verification](verification.json),
[support review](support-removal-review.json) and [slice preview](preview.png).
