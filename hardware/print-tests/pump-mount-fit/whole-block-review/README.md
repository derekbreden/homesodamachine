# Whole pump block review

This review candidate carves the whole lower mount from one broad blank. One
straight central channel clears the rigid casing and cable cover. Two flat
bearing strips carry the fixed rails, with integral stopping faces at both
ends of both rails. A single plane across the fore end clears the head lugs.
The production 54.5 mm upper clip and its hook-bearing datums are retained.

The flanks extend 3 mm farther outward on both sides. The rail bearing strips
are 3.419 and 3.329 mm wide, backed by continuous solid stock. The central
channel is 49.62 mm wide. Its floor retains 0.25 mm nominal air below the
corrected rigid cable-cover datum. The upper clip retains its 3.1 mm spring arch.

Both comparison models include the same 7.4 mm lid section.

| Geometry | Current mount | Carved block |
| --- | ---: | ---: |
| Base faces | 44 | 37 |
| Base edges | 120 | 102 |
| Base and clip edges | 176 | 158 |
| Solid volume, including common lid section | 110,662.90 mm³ | 118,110.22 mm³ |

The complete base has 18 fewer edges and 7.447 cm³ more solid stock. Both
bases are single valid native solids with watertight printable meshes.
Native seated overlap with the complete bare pump and the upper clip is zero.
[solid-block-report.json](solid-block-report.json) binds the measured source
and geometry. Its source reading was made from commit `27f1cd5be`.

The raised mount clears all nine surrounding mechanical parts included in the
local payload reading. The reservoir air tube has 1.054 mm of clearance.
[neighbors.json](neighbors.json) records the source parent payload and exact
query results. That reading clips the mount at the existing Z253.4 lid face:
the common rectangular comparison plate is a lid section, and the production
lid retains its existing air-line penetration. Wires and Wagos do not constrain
this mechanical proposal.

This is review geometry. The production mount and the launched fit trial retain
their selected design. Printed seating, axial play, spring force, release access
and running vibration of this candidate remain physical observations to make.

Run `build.py` explicitly through `python3 tools/run.py --cad -- <CAD Python>`
to regenerate the native comparison and print meshes. It starts no print and
changes no production geometry. The source is a reproduction of the measured
construction with its checkout and output paths resolved beside this review.
