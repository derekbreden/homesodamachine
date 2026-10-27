---
title: Four core junctions stand behind V-B’s wall
lede: The WAGO wells share a flat wall top 1.25 mm below the funnel frame. V-B and the two reservoir-A under-valve runs sit 1 mm lower, using the fore snap and aft tied seat.
date: 2026-10-27T00:26:10-05:00
commit: 451531391826bf29baf7f8eda58ec2856119771d f08e10128
model: manifold-layout/enclosure-assembly.step
---
The four WAGO junctions occupy two rows on the PCB-facing back of V-B’s
mounting wall. Their levers open west; the sensor and V12 ports face fore,
and the reed and GND ports face aft. The integral wells retain 3 mm stock.
The fore-facing connectors enter before the valve’s inlet plumbing.

Derek suggested: “On the back side of the valve b mount wall might be an option too”.

V-B, its attached stem elbows and return union are 1 mm lower. The inlet
uses an R19.98 minimum S-offset and the return uses its crowned R28.66
minimum curve. The V-A feed follows the freed low west lane between its
selected fitting endpoints.

The reservoir-A tubes pass below V-B at Z258.5 through the fore snap,
then rise to Z259.5 before the curved aft seat. Their modeled spans are
at most 177 mm for fill and 139 mm for draw. The fore cap retains its local
geometry; two shallow lid pockets clear its spring feet and retain
4.75 mm of backing. The frame and front fitting stations keep their
selected datums.

The native assembly has no volume clashes. The scoped tube clearances,
snap insertion reading and matching lid slice are recorded in the
[wall-routing review](https://github.com/derekbreden/homesodamachine/blob/main/hardware/printed-parts/cold-core/foam-cap/wago-wall-review/README.md).
The slice is prepared for Mark2’s left 0.4 mm Standard nozzle in PET-GF15;
the preparation launches no print.
