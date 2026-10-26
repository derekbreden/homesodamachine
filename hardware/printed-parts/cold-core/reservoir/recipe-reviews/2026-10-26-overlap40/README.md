# Reservoir overlap candidate

The next reservoir candidate uses **40% Infill/Wall overlap**, five Arachne
walls, flow **1.05**, **255/260 °C** first/subsequent nozzle temperatures,
**70 °C** bed, the glued Engineering Plate and the left **0.8 mm Standard**
hotend. Layers remain 0.30/0.24 mm, with 100% solid zig-zag floor/cap fill,
zero added/effective Z trim, no brim and ironing Off.

[Complete settings](settings.json) · [Source and exact setting changes](adaptation.json) ·
[Verification](verification.json).

The customer outcome is a reservoir that retains liquid without seepage.
Derek reports a small amount of water after **two hours** on the most recent
reservoir, at the line between wall and infill. The
[physical record and two base photographs](../../water-hold-evidence/2026-10-26-two-hour-leak/physical-result.json)
retain that observation. Small droplets and wet marks are visible beside the
base; the photographs do not expose the internal path. The report does not
explicitly identify a task or side. Earlier task-specific water-hold observations
retain their recorded scope.

The candidate's only physical setting change from the latest recorded left
Engineering Plate recipe is **Infill/Wall overlap: 30% to 40%**. Its process
label identifies 40%. All model geometry, placement and other archive entries
are byte-identical to that source. The editable candidate is
`.cache/reservoir-overlap40-20261026/candidate.3mf`; the submitted print records
and the root 265/270 °C reference project retain their own settings.

Bambu Studio 02.08.02.61 uses this setting when expanding the
[Arachne solid-fill boundary](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PerimeterGenerator.cpp#L1444).
It therefore addresses the reported floor-fill/wall junction. **40% is an
engineering trial selection**, with no demonstrated sealing result. A saved
percentage does not establish deposited fusion or water holding. Increasing
overlap can also leave excess material at the junction; the next article's
surface and leakage observations determine whether the selection is useful.

No printer job is submitted. Settings and unchanged geometry are verified;
native slicing remains pending because the local Studio CLI exits with signal
11 before producing a slice. A future print requires native slicing of this
candidate, rather than reuse of the 30% G-code.
