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

`mark2-registration.json` holds the measurement state. No software correction is
qualified yet. A measured correction belongs to this printer and nozzle pair,
must preserve the CAD artwork and black cavity geometry, and requires an audit
of the emitted white coordinates plus a second physical alignment check before
use on a nameplate. Numerical zero in the uncorrected coupon is not evidence of
calibration. Recheck after changing a hotend or calibration condition.

The current native review and launch receipt are retained in
[`2026-09-29-registration-mark2-v3`](../../enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-registration-mark2-v3/README.md).
