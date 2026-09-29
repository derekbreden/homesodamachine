# a7b Plough station: floating razor blades cut along each valley

## Picture it

A branch of [a7](a7-zip-station.md). The web is cut, not torn. Each blade rides
its own valley on a V-nose and floats sideways on a flexure. It needs no thin
neck, only a valley deep enough to steer a nose. Sketch: panel P1 of
[`../sketches/a5-part-fan-strip.svg`](../sketches/a5-part-fan-strip.svg) names it;
a7's sketch shows the same pallet and clamp.

- **Where things start.** As a7: one ribbon end in a pallet or a reel clamp, the
  clamp face at the split root, the end roughly square, on a covered floor.
- **The plough.** N−1 **ploughshares** in a printed carrier above a steel floor
  plate. Each is a sliver of double-edge razor (0.10 mm) bonded into a printed
  shoe: a V-nose on top rides the valley in the ribbon's top face; the blade's
  tip runs in a 0.3 mm slot in the floor plate, so it passes right through the
  web; a flexure lets the shoe float ±0.3 mm in X and presses the nose into the
  valley with ~1 N.
- **What moves.** The pallet drives the tip end into the plough in +Y. The
  blades enter at the valley lines, the noses drop into the valley notches, and
  the pallet stops with the blade tips 1 mm short of the clamp face.
- **What locates what, and the reference for fixed.** "Fixed" is the clamp face,
  which the stage stop is set from. Each nose finds its own valley; the ribbon's
  pitch stack across the width does not enter, because each blade floats
  independently [calc W2 §1].
- **Force.** A sharp blade drawn along a 0.25–0.7 mm web costs well under the
  tear force, around a newton per web [assumption]. No crimp force.
- **How it knows.** The same silhouette check as a7. The blades are isolated
  and wired, so a blade that leaves its valley and touches strands shows on the
  far-end port as continuity on that conductor.
- **What the person does.** Nothing at a station on a stage; slides the pallet
  by hand in the bench version.

## Steps it covers and what it hands back

Covers the split to the root and its verification; J2/J7 trims as a7. Hands
back nothing at the station.

## What the numbers say

0.98 mm of silicone lies between two bundles on the mid-plane, 0.49 mm each side
of the valley plane [calc W2 §1].

| Blade | Keeps ≥0.25 mm of flank wall while its offset is under | Reaches strands at an offset of |
|---|---|---|
| double-edge sliver, 0.10 mm | 0.19 mm | 0.40 mm |
| single-edge razor, 0.23 mm | 0.12 mm | 0.34 mm |

A **fixed gang** of 0.23 mm blades on a 5P, from a centred datum, carries up to
0.32 mm of lateral error (RSS 0.09) [calc W2 §1], which at worst comes within
about 0.1 mm of the outer strands. A **floating** 0.10 mm blade on its own
V-nose carries about ±0.07 mm [estimate] and keeps at least 0.25 mm of wall on
both flanks. That is why the blades float and are thin.

## Against a7

| | a7 zip (tear) | a7b plough (cut) |
|---|---|---|
| Depends on | a neck clearly thinner than the 0.49 mm wall | a valley deep enough to steer a V-nose |
| Kerf | none | 0.05 mm off each flank with a 0.10 mm blade |
| When the ribbon disagrees | the tear wanders into a jacket | the nose climbs out of a shallow valley and the blade cuts a flank |
| Tool | blunt tines, also the fan | sharp slivers, fan made separately |
| Cutting edges near copper | none | N−1 |

## Major unresolved problems

- **Valley depth.** A ribbon with nearly flat faces gives a V-nose nothing to
  follow. The cross-section photograph that settles a7's neck settles this.
- **Slivers in printed shoes:** snapping a 0.10 mm blade to a clean sliver and
  bonding it square is handwork; sliver life on silicone is unknown.
- **The floor slot:** a 0.3 mm slot at every valley position, per ribbon width,
  is a laser-cut or EDM part; a printed floor wears.
- **Web flash:** a cut leaves a flat face on each flank where the web was;
  whether it matters under an insulation wing tip is unknown.

## Related ideas

Parent [a7](a7-zip-station.md); module [a5](a5-part-fan-strip-in-the-pallet.md)
(P1).

## What rests on assumptions

Cutting force [assumption]; valley-following accuracy ±0.05–0.07 mm [estimate].

## Labels

As [a1](a1-pallet-tour.md#labels).
