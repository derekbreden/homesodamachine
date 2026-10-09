# trials-05-artefact-ladder: swap the workpiece, not the machine

Scene: `scenes/trials-05-artefact-ladder/index.html` (developed). Calc: `explorers/trials/calc/pivot_cal.py` (the board's pivot trial). Sourcing: cameras in `sourcing/trials.md`.

## Picture it

Five things can stand on the rotator, in order of increasing realism: a flat printed calibration board at plate-face height, a short corner coupon, a scrap tube with the top of its wall sawn away at the station (the notch tube), a printed tube with errors put in on purpose, and the real 316L tube. They sit in a rack behind the rotator, one ring marks the one on the rotator, and two proposed judge cameras look at the dot: A straight down the bore, B from outside at the height of the corner. Each rung turns the cameras' frames green, red or amber, and each carries a different ground truth.

## The proposal

Nobody has to learn everything on the real tube. Give the AI a ladder:

1. **Calibration board.** A printed disc (checker, fiducials, the 61.85 mm seam ring, the port pattern) on a pedestal so its surface is at plate-face height. No wall, glare or occlusion. The dot lands on coordinates the printer wrote. This is where the AI learns how commands move the dot and, by a **pivot trial**, where the dot really is in the gun's frame.
2. **Corner coupon.** A short ring of tube and a plate at the real recess on a pedestal: the corner is exact and cheap to make in bulk; nothing tall to hide the dot from a camera.
3. **Notch tube.** A scrap tube (band saw **[repo]**) with the wall above the plate cut away over about 34°. Camera B, outside, now sees the dot against the plate edge: the only rung with a direct ground-truth view of where the dot is at the corner.
4. **Printed zoo** (`trials-09-tube-zoo`). Printed tubes with dimensional errors put in on purpose: a known population, including cases worse than a real tube. Blind to glare.
5. **Real 316L tube.** Glare, real variation, the real corner; truth unknown without a measuring machine.

## The pivot trial (on the board)

The software rotates the gun about where it *believes* the dot is. If the real dot is d mm off along the beam, it wanders by about d times the tilt in radians. Read the wander on the board: d = wander / tilt. With 0.05 mm board noise, a ±12° tilt set gives the offset to about 0.06 mm (one standard deviation over 50 simulated runs); at 0.1 mm noise the estimate is off by about 0.13 mm; a ±2° set gives 0.42 mm and is too small (`pivot_cal.py`). Standoff, lens position and the laser's "red light alignment" **[manual p.25, 39]** all move the dot, so the trial repeats whenever any of them changes. It is the tool-centre-point calibration used for tracked surgical tools, applied to a dot.

## What carries the loads, what establishes position, what stays free

Nothing in the scene carries the gun (it floats as in the reference scene); each artefact sits on the existing turntable. Position: each artefact carries its own truth (printed coordinates, cut geometry, designed errors). The pedestal puts the board and coupon at plate-face height.

## What software could command, observe, and what stays manual

- Command: rotator speed (existing); gun tilt about the assumed dot (any positioner that can tilt).
- Observe: dot visible to A and B (drawn line of sight, not a measurement); dot position on the board's printed coordinates; wander during the pivot trial; on the zoo, the designed error at each angle.
- Manual: fitting the artefacts, making the notch and zoo tubes, flatness and centring of the board.

## Tried to break it

1. **The board says nothing about the corner.** Repair: it is only the first rung. Leaves: whether a matte paper dot resembles the dot on polished 316L.
2. **The notch tube shows a grazing view of 6.35 mm.** Conflict: the window is the wall above the plate; the view is nearly edge-on. Repair: it is a ground-truth instrument, not a production view. Leaves: it changes the tube (no wall to hit), so the dot lands on the plate edge, not in a corner.
3. **The zoo is blind to glare.** Any vision method that works on it may fail on 316L. Repair: glare-only questions live on rung 5. Leaves: how much of the real variation the zoo covers **[unknown]** (nobody has measured real tube variation).
4. **Judge B on the real tube is red (blocked).** Assumption: an outside camera can see the dot. The wall says no. This is why rung 3 exists.
5. **The pivot trial needs a well-known tilt axis.** If the software's tilt axis is itself off, the wander mixes both. Repair: do two tilt directions and check consistency (a scale bias shows up as a difference). Leaves: not drawn.

## Branches and combinations

- `trials-09-tube-zoo` (idea file) and `trials-13-pivot-calibration` (idea file) are the two pieces with their own files.
- Uses `trials-03` (camera A and the knee), feeds `trials-06` (where to put the mule's dot).
- Transferable: calibration board at seam height; notch tube; the ladder as a way of ordering difficulty.

- **Wave 3:** `trials-22-reference-pucks` puts each rung on a puck (the same three kinematic seats as any tube), so the board's frame is the tube's frame; its board carries a rim ring and the two ports so the same fit runs on it and on a tube; the coupon at the trial's own station is `datum-15`'s dock coupon done where it also sees the bench clamp and the positioner's scale; the clear twin (`datum-10`, `datum-17`) is a puck. Derek's coupon and notch rungs are unchanged.
- **Wave 2:** `trials-18-steerable-mule` gives the corner coupon and the notch tube a partner: a steerable dot with known offsets, whose knee (found by the sweep) the notch tube's direct view checks. `trials-19-fixed-point-cal` uses rung 1, the board with one printed cross, to calibrate an encoded arm or a gimbal formula.

## Unresolved, and questions for Derek

- Q: Is a printed 127 mm tube with an inserted plate a job for the Bambu printers (height 152 mm, one piece)? Which material would hold a plate press fit?
- Q: Are there scrap tube ends to make a notch tube from?
- The board's flatness and centring on the axis.

## Assumptions

Tube, plate, recess **[repo]**; gun proxy, opening pose, 16 mm clearance **[illustrative]**; camera poses **[illustrative]**; the zoo's drawn errors are exaggerated by the chosen factor, the numbers are exact; wander readings are exact scene numbers.
