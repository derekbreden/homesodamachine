# Tube bend holders, 2 mm wall with 1, 2 and 3 mm legs — Mark1

Mark1 accepted **task 1366458433 at 02:34 CDT on 2026-10-23** and reported RUNNING with no
print error ([launch receipt](launch.json)). The native estimate is **18 min 24 s** over
**51 layers**, plus printer startup and calibration: 7.7 g at the profile's saved
1.29 g/cm³, about 8.5 g at PET-GF15's 1.43.

Each holder is the 2 mm holder that [works](../2026-10-23-walls-234-petgf-left04-z018-mark1/physical-result.json)
with a straight [leg](../../README.md#legs) running on from both ends of its 90° turn. Facing
the printer, left to right: 1, 2 and 3 mm legs. Each millimetre of leg adds a millimetre to
both sides of the holder's square footprint, which identifies them.

## Process

The [wall comparison's](../2026-10-23-walls-234-petgf-left04-z018-mark1/README.md#process),
unchanged: black PET-GF15 on Mark1's fixed left hardened 0.4 mm nozzle, the shared
`petgf.3mf`, solid, +0.18 mm requested trim emitted as `G29.1 Z0.16`, Textured PEI. The slice
generates no supports and no brim, and its beads stand at least 123 mm inside the left nozzle's
plate. The first layer's beads span 1 mm more each way from one holder to the next, the legs on
both ends.

[`prepare.py`](prepare.py) runs the wall comparison's preparer with these three STLs. The
[readiness record](2026-10-23-tube-bend-holders-w2-legs123-petgf-left04-z018-mark1.readiness.json)
binds the STLs, the project, the archive and its G-code by hash.

## Assess the cooled holders

Thread the tube through each holder as for the wall comparison. Look at the tube where it
leaves each end: whether it runs on straight from the leg, and whether there is any crease at
the mouth.
