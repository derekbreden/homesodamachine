# Reservoir overlap candidate

The current reservoir trial uses **50% Infill/Wall overlap**, five Arachne
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
Engineering Plate recipe is **Infill/Wall overlap: 30% to 50%**. Its process
label identifies 50%. All model geometry, placement and other archive entries
are byte-identical to that source. The editable candidate is
`.cache/reservoir-overlap50-20261026/candidate.3mf`; the submitted print records
and the root 265/270 °C reference project retain their own settings. The
frozen matching lid uses the earlier port geometry; the current flush-grip
lid is a separate revision.

Bambu Studio 02.08.02.61 uses this setting when expanding the
[Arachne solid-fill boundary](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PerimeterGenerator.cpp#L1444).
It therefore addresses the reported floor-fill/wall junction. **50% is an
engineering trial selection**, with no demonstrated sealing result. A saved
percentage does not establish deposited fusion or water holding. Increasing
overlap can also leave excess material at the junction; the next article's
surface and leakage observations determine whether the selection is useful.

The left body and matching lid are running as **Mark1 task 1377101665**.
[Print record](../../prints/2026-10-26-mark1-left-engineering-flow105-overlap50-temp260-left08-z000/README.md)
retains the native slice review, successful Send and fresh startup. Studio
estimates **5 h 42 min 25 s and 444.89 g**, with 833 layers. Startup is
RUNNING at layer 0/833 with no error/HMS; physical water holding is unassessed.
