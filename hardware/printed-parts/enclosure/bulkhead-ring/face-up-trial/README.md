# Face-up raised TAP and FLAVOR rings

One TAP ring and two FLAVOR rings print face up with 0.48 mm raised lettering,
on the 2.0 mm fitting seat, bores and outlines of [`../bulkhead_ring.py`](../bulkhead_ring.py).
The raised letters clear the fitting flanges by at least 1.20 mm in the
lettering band.

TAP has a white body and black letters. Both FLAVOR rings have black bodies and
white letters. Mark2's left 0.4 mm nozzle uses black PET-GF; its right 0.4 mm
nozzle uses white PET-GF. The accepted nameplate appearance uses a native
white-nozzle correction of X −0.50 mm, Y +0.70 mm. It follows all white paths,
including TAP's body, while nominal CAD stays aligned.

The native plate takes **26 min 37 sec**, using **8.25 g** at the saved profile
density. It has no supports, a 0.20 mm first layer, normal 0.24 mm layers and
a 0.12 mm closing layer at the 2.0 mm fitting face. Every raised letter has
two full 0.24 mm layers above that face. Speeds, wall order and 15% overlap
follow the saved PET-GF settings. The usual Auto nozzle-offset startup option
applies; no touchscreen calibration is required.

The [print review](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-30-bulkhead-raised-mark2-v2/README.md)
records Mark2 task 1295298484 and its exact files. The user
[accepted the finish and excellent, clear lettering](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-30-bulkhead-raised-mark2-v2/physical-result.json).
Mounting fit was not separately reported. The
[registration record](../../../calibration/dual-nozzle-registration/mark2-registration.json)
links the accepted nameplate artwork appearance; residual XY error is unmeasured.

`raised_rings.py` builds the three rings from `../bulkhead_ring.py`.
`prepare_print.py` creates the corrected native archive, and `--uncorrected`
creates its comparison slice. `verify_print.py` checks source hashes, seating
and letter planes, filament assignments, support absence and the correction on
every object/tool/layer.
