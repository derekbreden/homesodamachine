# Face-up raised TAP and FLAVOR rings

One TAP ring and two FLAVOR rings print face up with 0.48 mm raised lettering.
The existing 2.0 mm fitting seat, bores and outlines remain the mounting
interface. The raised letters clear the fitting flanges by at least 1.20 mm
in the lettering band.

TAP has a white body and black letters. Both FLAVOR rings have black bodies and
white letters. Mark2's left nozzle is black PET-GF; its right nozzle is white
PET-GF. The measured alignment correction belongs to that nozzle pair and must
follow the white nozzle's paths, including TAP's body.

The native geometry-review plate takes **26 min 37 s**, using **8.25 g** at the
saved profile density. It has no supports, a 0.20 mm first layer, normal 0.24 mm
layers and a 0.12 mm closing layer at the 2.0 mm fitting face. Every raised
letter has two full 0.24 mm layers above that face. Speeds, wall order and
15% overlap follow the saved PET-GF settings.

**This uncorrected review slice is held.** Printing depends on the measured
Mark2 registration result and physical acceptance of the nameplate. The
calibration state is recorded in
[`../../../calibration/dual-nozzle-registration/mark2-registration.json`](../../../calibration/dual-nozzle-registration/mark2-registration.json).
No unmeasured correction is included in this plate.

`raised_rings.py` generates the trial CAD. Publish it before running geometry
lint. `prepare_print.py` creates the native geometry-review archive, and
`verify_print.py` verifies its source hashes, seating/letter layer planes and
the filament used by each raised word. Production ring geometry is separate
from this fit and finish trial.
