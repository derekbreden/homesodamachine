# trials-03-dot-touch-probe: the red dot as a touch probe

Scene: `scenes/trials-03-dot-touch-probe/index.html` (developed). Calc: `explorers/trials/calc/dot_probe.py`. Sourcing: `sourcing/trials.md` (cameras).

## Picture it

The gun is stepped a few millimetres, one axis at a time, while the red dot sits in the recessed corner and a camera above the bore watches it. The dot slides across the plate toward the wall; when it reaches the seam the plate part of it disappears from above and the rest climbs the wall. The axis value where half the dot is gone is the wall's position in the software's own coordinates. A second spot may also appear on the wall, thrown there by the plate, and its height above the seam says how far the dot still has to go.

## The proposal

Treat the dot as a **non-contact touch probe**. From above (camera A) the dot's image is the part of it lying on the plate; the wall spot is seen edge-on and is invisible. So the visible fraction goes from 100 % to 0 % as the gun moves the dot across the seam; half-drop is where the dot centre is on the seam. That is a measurement of "where is the seam in axis coordinates" made with one axis and one camera, with no absolute camera calibration.

Three more signals ride on the same dot:

- **Spot size** is smallest at focus (assumed, unmeasured), so a height sweep finds the plate height in axis coordinates: a standoff meter.
- **The dot's own reflection.** A mirror-like plate throws the dot up the wall: a dot on the plate a mm short of the wall appears on the wall at a·cot(β) above the seam (about 1.6 a at 32°), and only while a is less than 6.35·tan(β) (3.97 mm at 32°). Camera B on the far rim, looking across the bore, reads that height: a **ruler in one frame**, no sweep.
- **Height and radius are confounded on the plate.** Raising the gun by z moves the dot along the plate by z·tan(β), so the knee alone gives one combination of wall position and height. The focus sweep gives height alone; together they solve both (the scene does it and reports the error).

The beam approaches from **inside** the bore over the plate, as in the reference corner inset. From outside it is not possible: a beam arriving over the rim from outside cannot reach the corner once it is steeper than atan(1.65/6.35) = 14.6° from vertical (rim shadow; `dot_probe.py`, [derived] from the 1.65 mm wall and 6.35 mm recess).

## What carries the loads, what establishes position, what stays free

Nothing about carrying is modelled: any positioner that steps 0.05 mm along the radial direction will do; the tangent slide costs almost nothing (0.008 mm per mm at r = 61.85 mm, `seam_rates.py`). Position is established by the corner itself: the wall is a hard edge for the dot. Free: everything else; the sweep needs one axis (a second for the focus sweep).

## What software could command, observe, and what stays manual

- Command: the radial axis (and height axis), start/stop a sweep. Whether the dot can be switched or blinked is **[unknown]**: the manual gives RS232 pins but not a protocol **[manual p.16]**; the mule (trials-06) has a switchable dot by construction, which would allow frame-subtraction against glare.
- Observe: centroid and visible fraction (camera A); spot size; reflected-spot height (camera B, if the plate is specular); the knee.
- Manual: rough setup so the dot starts on the plate, 2 to 8 mm short of the wall; confirming with a phone photo that the real plate reflects the dot.

## Tried to break it

1. **Outside beam and rim shadow.** Conflict: from outside the corner is unreachable at a steeper angle. Assumption: the gun can stand over the bore. Change: the inside approach; the scene draws it. Leaves: the inside approach puts the barrel across the bore, which conflicts with any arrangement whose gun body cannot be over the tube.
2. **Height looks like radius.** Conflict: tan(β) mixing on the plate. Repair: spot size (depends on height alone) and the second sweep. Leaves: near focus the size curve is flat (sign ambiguity), so the software has to dither in height and compare; the combined estimate in the scene is the loosest of its signals (about 0.1 to 0.2 mm error at 0.04 mm image noise).
3. **The wall spot is invisible from above.** Repair: camera B, or the reflection. Leaves: both depend on things unchecked (a camera line of sight past the gun body, a specular plate).
4. **Camera B blocked.** With B low on the far rim the gun body blocks the sight line (scene slider). Assumption: B has a clear view across the bore. Leaves: the position that sees the wall spot while clearing the gun for every pose has not been found.
5. **The dot may not look like this on 316L.** Size at focus, brightness under shop light and specularity are **[unknown]** (0.3 mW red **[manual p.12]**). The scene's Rayleigh-style size model is illustrative.
6. **The dot is not the melt.** The IR focus is elsewhere by an amount the "red light alignment" setting changes **[manual p.25, 39]**. The probe finds the dot, not the melt; a witness mark would relate them.

7. **Camera A "straight down" is not where a camera over the bore stands (from datum's exchange, wave 2, combinations list: "the plate as a calibration target").** *Conflict, in this variant:* the scene drew camera A "far above, looking straight down" and read only the plate part of the dot, with the wall spot edge-on. A camera 300 mm over the bore centre looks at the station wall at atan(61.85 / 300) = 11.6 degrees (22 at 150 mm), so it sees the wall face in a strip 6.35 tan(psi) wide beyond the seam foot (1.30 mm at 11.6 degrees), and the wall part of the dot shows in it, foreshortened by tan(psi). Reading the dot against the *rim edge* is then wrong by that 6.35 tan(psi) (1.3 mm at 300 mm, 2.6 at 150). *Assumption behind it:* the wall is edge-on to the camera. *What the change alters* (`calc/knee_view_angle.py`): the knee itself is unchanged because it needs no rim: the plate side of the seam foot still falls to 50 per cent when the dot's centre is on the seam, for any psi; but the total visible fraction stays near 100 per cent through the crossing, so the software has to know where the seam foot is in the picture (from the rim and ports fit, `datum-19`, or a camera over the station), and without that line the centroid of everything visible bends from slope 1 to 0.33 over about 0.7 mm and the knee is hard to call. The scene has a line-of-sight slider (default 11.6 degrees) and panel A draws the wall-face strip, the rim edge and the foreshortened wall part. *What it leaves uncertain:* the seam foot's image position from a real frame; the dot's brightness on the wall face at grazing view.

## Branches and combinations

- Feeds `trials-04-seam-map-replay` (the map needs the dot on the seam within the follower's range before it can learn).
- Uses the artefact ladder (`trials-05`): the board calibrates the camera-to-axis mapping; the notch tube gives ground truth for the knee.
- Transferable: dot as touch-off probe; dot size as standoff meter; specular ruler.
- `trials-14-contact-sense` is the electrical version of the same idea (gun and wire as a continuity probe).

- **Wave 2, borrowed from `eyes-06b-corner-mirror`:** the dot and its plate reflection merge exactly when the dot is on the corner; that is a second, null-type criterion for the knee that does not need the visible fraction's noise floor (a null is easier to call than a slope) but does need a specular plate (Scotch-Brite prep may spoil it, see eyes-06b). The reflection ruler above is the same geometry read as a distance instead of a merge.
- **Wave 3:** `trials-22-reference-pucks` gives camera A its calibration (the board puck's pose and scale); `trials-23-frame-clock` says a sweep reads the knee late by speed times latency and how to cancel it (sweep both ways, at two speeds); `trials-24-calibration-graph` says the knee is the one reading that leans on neither the lens nor the camera's pose.
- **Wave 2, the knee as the seam in another unit:** `trials-18-steerable-mule` finds the knee with a steerable pointer, coarse then fine, and writes labels from it; `trials-20-guide-at-the-knee` closes a loop on the 50 per cent point instead of the centroid.

## Unresolved, and questions for Derek

- Q: Photograph the dot on the plate face at three heights (nozzle at 10, 16, 22 mm): how big, how bright, does a second spot appear on the wall?
- Q: Can the laser box be told to blink the dot (RS232 or DB25)? What does the manual not say?
- The beam angle used (32°) is the reference scene's; the real working angle may differ.

## Assumptions

Wall 1.65 mm and recess 6.35 mm **[repo]**; beam 32° from vertical and 16 mm nozzle-to-dot **[illustrative]**; spot-size model, camera noise, mirror/satin/matte behaviour **[illustrative]**; camera positions **[illustrative]**.
