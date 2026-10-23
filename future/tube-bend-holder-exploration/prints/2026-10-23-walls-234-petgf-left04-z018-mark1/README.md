# Tube bend holders, 2, 3 and 4 mm walls — Mark1

Mark1 accepted **task 1366393391 at 01:53 CDT on 2026-10-23** and reported RUNNING with no
print error ([launch receipt](launch.json)). The native estimate is **22 min 15 s** over
**68 layers**, plus printer startup and calibration: 10.3 g at the profile's saved
1.29 g/cm³, about 11.4 g at PET-GF15's 1.43.

Facing the printer, left to right: the [2, 3 and 4 mm holders](../../README.md), each on its
flat back, identified by size.

## Process

- Polymaker Fiberon PET-GF15, black, on Mark1's fixed left hardened 0.4 mm nozzle from
  external spool 254, which reads PET-CF. Textured PEI.
- The shared [`petgf.3mf`](../../../../hardware/printed-parts/petgf.3mf) with its localized
  cooling; requested +0.18 mm trim, emitted `G29.1 Z0.16`.
- Solid, like the tube-insertion fixture: six walls and 100% zig-zag infill, so the wall
  thickness is the only difference between the three. 0.20 mm first layer, 0.24 mm layers.
- Tree (auto) supports stay on and the slice generates none; no brim is generated. The slicer
  closes each channel's point with a short bridge course just above it.
- The native bead envelope stands at least 122.6 mm inside the left nozzle's plate.
- Timelapse and Bed Leveling On; Flow Dynamics and Nozzle Offset Calibration Auto.

[`prepare.py`](prepare.py) writes the project and slices it with Bambu Studio 02.08.02.61.
The [readiness record](2026-10-23-tube-bend-holders-w234-petgf-left04-z018-mark1.readiness.json)
binds the three STLs, the project, the archive and its G-code by hash.

## Assess the cooled holders

This decides the thinnest wall that holds 1/4" LLDPE at R14, and whether the Ø6.8 channel
threads by hand. Those two set the section for a holder at the enclosure's R14 corners.

Cut about 150 mm of 1/4" LLDPE square. Push its end into one mouth of a holder, round the turn
and out the other, pulling it through once it shows, until it stands well out of both ends.
No other tool is needed.

A holder passes when:

- the tube goes through by hand;
- the bore stays open and round through the turn, with no crease: look along the tube from
  each end, or blow through it;
- the holder shows no crack or whitening along its crown or its sides, and the tube leaves
  both mouths square to them.
