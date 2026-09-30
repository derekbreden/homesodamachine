# Tee carrier — 0.50 mm low-force addition

Native slice verified; **not sent**. H2C estimate: **1 h 45 min 40 s**, **55.82 g**,
140 layers. The carrier is the only object on the plate. Black PET-GF uses the left
0.4 mm hotend, with requested +0.18 mm trim and emitted textured-plate +0.16 mm.

The upper gap is **1.00 mm**: 0.25 mm sliding, 0.25 mm for the rough enclosure roof
and 0.50 mm for low-force motion. The lower gap is **0.25 mm**; total vertical travel
is 1.25 mm. The front-top opening, spring bores, tee stations and release travel retain
their geometry. [Geometry checks](geometry-check.json) verify the stated gaps and
compatibility with the printed opening.

The additive bottom chamfer/taper uses a 0.20 mm first layer and 0.24 mm layers above,
with six walls through print Z 6.1 mm. The complete top R6 uses 0.08 mm. Two walls
apply above the bottom band. Speeds, wall-first order and 15% overlap use the saved
settings. Supports, brim and elephant-foot compensation are off.

[Native verification](verification.json) checks source hashes, first/second-layer
bead overlap, complete transition bands, wall counts and absence of supports.
[Manifest](manifest.json) binds the exact archive and geometry. Lint has no unanswered
findings. The chamfer/taper surface has an accepted physical reference on job
1292379739; this gap requires its own sliding and spring-return test.
