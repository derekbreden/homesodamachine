# Machine display retention receiver · H2C

H2C task **1289537122** reports RUNNING at startup, layer 0, at 07:11:33 UTC.
Its print-error field is 0, but the **0300-801E extrusion-motor overload** HMS is still
listed. No agent resume command was issued. The exact cause and time of return to
RUNNING are unobserved, so spacing of that resume cannot be verified.
The reviewed job was accepted at 2026-09-28 07:00:01 UTC.
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
