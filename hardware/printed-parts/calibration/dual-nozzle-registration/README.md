# Mark2 two-nozzle registration

This coupon measures the remaining XY displacement between Mark2's left black
and right white PET-GF paths, using its two 0.4 mm hotends. The black reference
and white candidate tops are coplanar at 1.44 mm, so their alignment can be read
without comparing a raised white top to a recessed black opening.

Each row has indices 0–14. Choose the index where the black line and its white
continuation line up. Read **X and Y independently**; report both indices if
adjacent candidates tie. Each step is 0.05 mm:

    X white correction (mm) = -1.05 + 0.05 × selected index
    Y white correction (mm) = +0.35 + 0.05 × selected index

With X above Y and the indices increasing left to right, the top row tests
−1.05 through −0.35 mm in X and the bottom row +0.35 through +1.05 mm in Y.
The selected displacement is the correction to apply to white;
the measured relative error has the opposite sign. Do not extrapolate beyond
the coupon. A photograph perpendicular to the surface can document the reading.

`registration.py` builds the two-colour reference. `prepare_print.py` packages
it with the saved PET-GF profiles. `verify_print.py` checks all 60 emitted
candidate displacements across both rows and both raised layers. It also checks
the native checksum, source hashes, filament mapping, layer planes and no support.
The plate uses 0.20 mm first, 0.28 mm second, then 0.24 mm layers, with the normal
saved speeds and wall order. Mark2's requested +0.04 mm trim emits +0.02 mm for
the textured plate.

The coupon uses the usual **Auto** nozzle-offset startup option. Its line pairs
are inspected afterward. Validation and product prints use the same usual launch
options; no touchscreen-managed high-precision calibration is part of this procedure.

`mark2-registration.json` holds the selected correction: **white X −0.50 mm,
Y +0.70 mm**. The user's choices are the twelfth and eighth positions from the
left (zero-based indices 11 and 7). “Fourth from the right” of 15 confirms the
top-row numbering. The Y choice is tentative because slight oozing makes its
neighbouring candidates difficult to distinguish.

The correction belongs to Mark2's current nozzle pair. The nominal CAD artwork
and black cavity meshes remain aligned. Bambu Studio's native `extruder_offset`
is `0x0` for left/black and `0.5x-0.7` for right/white. Its
[`point_to_gcode` implementation](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/GCode.cpp)
subtracts that configured offset from model coordinates. `verify_correction.py`
checks the actual emitted model paths against the uncorrected native slice;
the maximum normalized path difference is 0.000691 mm, within export rounding.
The native purge-tower entry movements are checked separately.

The [raised-artwork nameplate](../../enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-flat-wings-mark2-v3/README.md)
is the physical validation print. Its colour alignment and QR scanning remain
pending before applying the correction to TAP and FLAVOR rings. Recheck after
changing a hotend or calibration condition.

The current native review and launch receipt are retained in
[`2026-09-29-registration-mark2-v3`](../../enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-registration-mark2-v3/README.md).
