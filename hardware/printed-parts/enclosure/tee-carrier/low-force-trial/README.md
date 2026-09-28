# Tee-carrier low-force sliding trial

One complete carrier for the existing front-top enclosure. Each column's upper surface
is 0.75 mm lower, with the R6 edge blends retained. Nominal roof clearance is 1.25 mm;
floor clearance is 0.25 mm. The spring bores, tee troughs, tie slots, plate, lower column
surfaces and release travel retain their current positions.

The current front-top STL is byte-identical to the input for H2C job 1277245499
(`2026-09-23-enclosure-front-top-h2c-v13`). Its carrier opening is unchanged.
[Geometry checks](geometry-check.json) bind the trial to that mesh and verify the
opening, spring stations, release travel and valid print solid.

This tests **low-force clearance for rough overhang surfaces involved** at the carrier's
upper sliding contact. The supported front-top roof's physical finish determines the
usable space. Check free sliding and spring return with the existing front-top, with
the tees and springs installed, and assess unwanted play.

H2C prints black PET-GF on the left 0.4 mm hotend, with requested +0.18 mm bed trim.
The carrier lies on its back. Both complete R6 bands use 0.08 mm layers; the bottom
band alone uses six walls. Other layers use 0.24 mm and two walls. Supports are off;
saved speeds, wall-first order and 15% overlap are retained. No window covers or
other parts share the plate.

`low_force_trial.py` generates the geometry; `prepare_print.py` prepares and natively
slices the H2C job. Physical fit is pending.
