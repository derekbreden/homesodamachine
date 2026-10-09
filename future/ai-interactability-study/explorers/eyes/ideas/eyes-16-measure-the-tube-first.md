# eyes-16 Measure the tube first (branch of room-01 and room-09; Derek's PTZ vision)

Scene: `scenes/eyes-16-measure-the-tube-first/`. Origin: exchange with room (wave 2), and Derek's automated-setup vision (PTZ cameras). Maturity: developed.

**Picture it.** The tube is loaded and no gun is anywhere near it. A camera on the table looks across the bore, a little above the rim, at the far wall. In one picture: the rim's edge at the top and the corner where the plate meets the wall at the bottom. The pixel gap, times a scale, is 6.35 mm plus how deep this plate sits.

## The proposal

Plate seat depth is the number room-09's shelf, room-05's Z stage and every fine stage waits for, and it is **[unknown]** in the repo. Do not assume it and do not find it with the gun: read it from a picture, once per tube, before loading the gun, with the laser off and nobody near the interlock.

The camera can be one of Derek's PTZ units. A PTZ camera is a pointing device with a pointing error of its own: 0.1 degree is 0.86 mm at the far wall and 24 pixels at 9 degrees, seventeen times a 0.05 mm dot correction. It stops mattering because both features are in one frame: the aim moves the whole picture, and the difference between the rim and the corner is unchanged. What does not cancel is the scale.

## What carries loads, what establishes position, what is free or restrained

Not addressed: the camera stands on the table or a post. What establishes the measurement is the rim edge and the corner in one frame, and the tube's own inner diameter (123.7 mm, edge to edge across the bore) as the ruler.

## What software could command, observe, and what stays manual

- **Command:** the camera's pan, tilt and zoom to a preset (a moving window); later, a shelf or stage height from the number.
- **Observe:** two edge rows on the far wall, the bore's width in the same frame, whether the corner is visible over the near rim.
- **Not observed:** the plate's lateral offset in the tube (about 0.13 mm of slip), its tilt, tube lean.
- **Manual:** placing the camera; checking the corner edge is the plate and not a tack or burr.

## What was tried to break it

1. **The near rim hides the corner if the camera is too low.** Visible from about 3 degrees (line to the far rim) at nominal seat depth; more when the plate is deeper. The scene marks it.
2. **A PTZ camera as the measuring instrument.** Comparing where one thing sits between visits fails at 0.86 mm per 0.1 degree. Change: compare two things in one frame.
3. **The scale.** With the bore in the frame (a picture at least 130 mm wide at the wall) the ruler is 0.13 % (illustrative wall and OD tolerances); zoomed to 92 mm (6 degrees) the ruler is out of frame and the scale is the lens's (1 % is typical of a zoom, illustrative): 1 % of an 8 mm span is 0.085 mm. Options: a printed scale in the frame, a wide look then a narrow one, or stay at the widest zoom that holds the bore (4K: 0.036 mm per pixel).
4. **Result:** at 3840 px, 9 degrees (bore just in frame), 0.5 px edges: 0.028 mm (0.015 with 0.25 px edges); 20 degrees 0.059; 6 degrees, ruler out of frame, 0.085 (the scale term); 1280 px across at 9 degrees 0.079. Comparable to a caliper on a dozen tubes, with nobody holding a caliper in the bore.

## Branches and combinations

- room-09 (a recipe height per tube from a number) and room-01 (the side camera: see below).
- use-03's presetter: measure at the presetter while the last tube is on the rotator.
- eyes-07's sectioned tube: ground truth for the corner edge on real stainless.
- Second look from above at the two ports (38.1 mm apart) or 90 degrees round for the lateral offset.
- room-01's table-level side camera at its default rim + 16 mm already sees the corner in the drawn geometry (threshold about rim + 13 mm at 300 mm out); its I/O row calls that view blind.

## Unresolved problems, questions for Derek

- Does the plate-wall corner give a clean edge on stainless (glare, slip gap 0.127 mm wide, burr, tack)? A phone photo from across the bore at 10 to 15 degrees above the rim answers it, and gives a first number.
- PTZ pointing and zoom repeatability are not on the listing read for this study (NexiGo 10X: 255 presets, VISCA, no repeatability figure).
- Tube lean (face runout up to 0.30 mm TIR) changes the vertical scale by a hair; not modelled.

## Assumptions

Camera 1280, 1920 or 3840 px across, 16:9. Edge noise 0.1 to 3 px; ruler = tube ID to 0.13 %; zoom repeat 1 % when the ruler is out of frame; pointing error applied as pan and tilt **[illustrative]**.

## Sourcing pointers

`sourcing/eyes.md` wave 2: NexiGo 10X PTZ (B0DQCFX9WN, $242.99, 5,521 ratings, VISCA, 255 presets); other Prime PTZ units $200 to $300.

## Scene

`eyes-16-measure-the-tube-first`. Scene edits: seat depth; camera azimuth, elevation, distance, zoom, pixels; pointing error, edge noise, zoom repeat.
