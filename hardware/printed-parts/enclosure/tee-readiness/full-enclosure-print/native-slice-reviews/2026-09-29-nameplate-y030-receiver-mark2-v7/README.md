# Nameplate receiver Y-clearance test

Mark2 accepted task **1295207560** at 2026-09-30T04:36:07.816244+00:00.
The receiver-only native estimate is **43 min 6 sec**, **20.09 g**. Use the same
flat 3.36 mm nameplate from the v5 pair.

The Y slot is **1.98 mm** thick for the existing **1.68 mm** wing, giving
**0.30 mm total clearance** above the seated wing. The Y=0 seating floor stays
fixed. Wing tips have 0.25 mm X gaps at center, with a 0.10 mm minimum at full
body X float. The Z gaps remain 0.15 mm at the ordinary end and 0.40 mm at the
print-down rough end. Retention overlap is at least 2.10 mm, with 1.00 mm of
flat bearing width. The flat retaining lip is 1.38 mm thick, and its entry
bevel leaves 0.98 mm at the mouth.

[Geometry comparison](geometry-delta.json) confines all removed material to the
two Y slot roofs and their entry bevels, with zero additions. It verifies the
same nameplate STL, fixed seating floor and all six pure-axis motion boundaries.
This is a local test of thickness pinching. The
[preceding physical result](../2026-09-29-nameplate-tip025-receiver-mark2-v6/physical-result.json)
shows bowing when engaged and flatness when disengaged, without establishing
which wing surfaces interfere. Z-end contact remains a possible cause.

The receiver prints in the enclosure back-top orientation with the shared
PET-GF tree supports: 0.40 mm support XY, 0.45 mm upper Z and 0.30 mm lower Z.
Every support bead clears both wing slots and entry bevels. The job uses black
PET-GF on the left 0.4 mm nozzle, +0.04 mm trim, a 0.20 mm first layer and
0.24 mm above it, normal speeds and wall order. The usual startup settings
apply, including Auto Nozzle Offset Calibration.

[Verification](verification.json) checks source hashes, archive integrity,
192 model layers, support settings and emitted slot paths. Geometry lint has
zero unanswered findings; the ideal 101-position insertion envelope passes.
These checks do not qualify physical flatness, force or retention. The
[launch receipt](launch.json) records printer acceptance, spool mapping and
more than three minutes of spacing after H2C's start.

[Physical result](physical-result.json): the user accepts this nameplate fit for
now. Residual bow and insertion force are not quantified.
