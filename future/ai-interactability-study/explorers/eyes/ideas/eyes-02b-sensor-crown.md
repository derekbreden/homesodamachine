# eyes-02b Sensor crown (branch of eyes-02)

Scene: preset "Crown of six" inside `scenes/eyes-02-where-can-an-eye-stand/` (no separate scene). Origin: branch of a swarm idea. Maturity: sketch.

**Picture it.** A ring of six cameras on short posts stands round the tube, a hand's width above the rim and about 190 mm from the axis, all looking at the station. The gun reaches in through the gap where the +X post would be. The tube turns inside the ring; the cameras never move.

## The proposal

Instead of choosing one observer position, surround the seam. Cameras on the bore side see the dot and triangulate it from angles far apart; cameras on the wall side see only the gun and the rim. Tag-based pose (eyes-03) or dot detection (eyes-06) can use whichever eyes have a view. The crown also gives redundancy: an eye lost to the umbilical or the operator's hand is one of several.

## What carries loads, what establishes position, what is free or restrained

The crown is a fixed ring (six posts or a bench-mounted hoop); it carries only cameras. It establishes the tube frame if tags on the turntable and bench are seen by the same cameras (not drawn). Nothing carries the gun.

## What software could command, observe, and what stays manual

- **Command:** nothing new. **Observe:** which eyes see the dot; triangulated dot position in the tube frame if the cameras are calibrated together. **Manual:** building and calibrating the ring; deciding a gap for the gun.

## What was tried to break it

1. **Six equal eyes.** Assumption: a symmetric ring gives symmetric coverage. In the drawn geometry (posts at 190 mm, 70 mm above the rim) 3 of 6 see the dot (the three on the bore side, azimuths 120, 180, 240 degrees), the widest pair are 87 degrees apart. The three on the wall side see the tube wall and the gun's back. What this changes: half the ring is redundant or looks at something else (the rotator, the operator). What it leaves: the +X post would stand where the gun goes.
2. **A better use of the same number of eyes.** The "Beside" preset (two eyes at 108 and 252 degrees, 260 mm out, 17.5 degrees up, the dome's best directions) sees the whole seam with 130 degrees between them; the crown with three times the eyes is worse. What this changes: a crown is the wrong shape; the useful part is two or three eyes placed where the dome says.
3. **A turning ring.** Putting the eyes on the tube (rotating with it) makes the seam stationary in each image and the gun sweep past. But the rig's rule is that no cable turns with the tube (**[repo]** weld-rotation-rig.md). Wireless cameras (battery, wifi, latency of several frames) or a slip ring through the 90 mm service bore would be needed; the second closure's bore is a purge passage, so the slip ring would fight it. Left standing: not developed.

## Branches and combinations

Parent: `eyes-02-where-can-an-eye-stand`. Uses: `eyes-03-marker-cube` (tags need only some eyes), `eyes-06-dot-as-probe` (the sweep needs the eye placed where the kink is strong).

## Unresolved problems, questions for Derek

Bench space and the operator's access; whether posts fit around the rotator base (300 x 250 mm plus feet); how the gun and umbilical pass the ring.

## Assumptions

Ring radius 190 mm, height 70 mm above the rim, six eyes at 60 degree spacing: illustrative. Occlusion by the drawn proxy gun and tube only. Rig dimensions **[repo]**.

## Sourcing pointers

`sourcing/eyes.md`: Logitech C920 (32.7K reviews, "500+ bought in past month" on the page): the eye that makes a ring cheap.

## Scene

Preset in `eyes-02-where-can-an-eye-stand` (Fixed eyes: Crown of six).
