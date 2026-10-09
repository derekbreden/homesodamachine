# trials-13-pivot-calibration: where is the dot in the gun's own frame?

Shown in `scenes/trials-05-artefact-ladder` (board rung; the "pivot trial" controls). Calc: `explorers/trials/calc/pivot_cal.py`.

## Picture it

The gun's dot rests on a printed board. The software tilts the gun about the place it believes the dot is. If the belief is right, the dot does not move. If it is wrong by d millimetres along the beam, the dot wanders about d times the tilt in radians. Read the wander on the board's printed coordinates and you have d.

## The proposal

A tool-centre-point calibration for a red dot, borrowed from tracked surgical tools. Tilt about two horizontal axes through several angles (±12°, in both axes), record the dot's board coordinates at each, and fit the offset by least squares. The dot's place in the shell's frame is what every other coordinate in the study depends on: the position of the mule's module, the software's kinematics, the dot probe's standoff. Standoff, the lens position and the laser's "red light alignment" **[manual p.25, 39]** all move it, so the trial is cheap enough to repeat.

## Carries, locates, free

No support is proposed; any positioner that can tilt about a known axis. The board (trials-05, rung 1) supplies the reference.

## Software

Command: tilt about two axes. Observe: the dot on the board (camera A). Manual: fitting the board at plate-face height.

## Tried to break it

1. **Small tilts.** With ±2° the offset estimate scatters by 0.42 mm (sd) at 0.05 mm board noise; with ±12° by 0.06 mm (`pivot_cal.py`). Repair: use the larger tilts. Leaves: large tilts may leave the camera's field or the board.
2. **The tilt axis is itself imperfect.** Repair: two directions and a consistency check. Leaves: not drawn.
3. **Board height.** A board that is not exactly at plate-face height shifts the dot by tan(β) per mm (0.62 mm at 32°). Leaves: how the board is set to height.
4. **Dot on paper is not the dot on steel.** The size and brightness differ. Leaves: unchecked.

## Combinations

`trials-05` (the rung), `trials-06` (places the mule's module), `trials-03` (standoff).

## Wave 2

The method generalises: `trials-19-fixed-point-cal` puts the beam on one cross from many orientations and fits whatever the arrangement reports (encoded-arm joints, or the gimbal-and-gantry formula's cradle offset), and finds the two components across the beam; the component along the beam moves nothing on a board and needs spot size (`trials-03`). The tilt-about-a-pivot trial on the board is one instance of it.

## Unresolved

Whether the real dot is nearer or farther than the nozzle's nominal clearance **[unknown]**.

## Assumptions

Tilt range, board noise, offsets **[illustrative]**; technique standard.
