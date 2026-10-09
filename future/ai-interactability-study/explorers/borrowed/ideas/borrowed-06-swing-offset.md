# borrowed-06-swing-offset: the gun already has a fine axis across the seam

Origin: swarm (found by reading the manual for what the product already does). Maturity: developed. Scene: `scenes/borrowed-06-swing-offset/index.html`.

## Picture it

Zoomed on the corner: the gun's beam does not sit still, it sweeps a couple of millimetres along a line that crosses from the plate onto the wall. A control shifts the middle of that sweep left or right. With the gun held a millimetre off, software slides the centre back until the sweep straddles the corner again, and the gun never moved.

## The proposal

The gun contains a motor that swings the beam (item 5 in the parts drawing, [manual p. 17]; the recorded practice settings use 80 Hz by 2 mm [repo pressure-vessel.md]; the manual's own welding note gives 10 Hz by 2 mm [manual p. 13]). The settings screen has a "red light alignment" page: "When the red light is not in the centre of the nozzle, you can adjust the red light to the centre of the nozzle by pressing the left and right buttons" [manual pp. 25, 38 to 39]. If the swing centre can be shifted by software, the head is a one-axis fine actuator across the seam, in the direction that matters most for a bead, for free. The manual also documents an RS232 port for "PC-based supervisory software" (pins 2 RXD, 3 TXD, 5 GND) and a DB25 port "for PLC integration by customers" [manual p. 16]; it documents no protocol.

## What carries loads, establishes position, is free or driven

Nothing new carries anything. The offset moves the spot along the gun's local X, across the seam when the barrel is tangent. Position reference: the sweep line crossing the corner; the seam is where the plate meets the wall.

## Software: command, observe, manual

- Could command (if the head accepts it): swing centre offset, swing width; rotator speed (existing).
- Could observe: nothing from the gun. The spot position along the corner path needs a camera; the scene shows what a nulling loop would do with a biased reading.
- Stays manual: setting the red-light alignment once on the screen; carrying and aiming the gun.

## What was tried to break it

1. **What does an offset move?** In the scene at the opening pose one millimetre of centre offset moves the spot 1.8 mm along the corner path (down the plate, up the wall); the slope changes with the three dials (change them and read the slope line). Assumption: one millimetre of offset is one millimetre at the seam. It is not. Change: the loop divides by the measured slope (the guide-star calibration in borrowed-05 finds it by nudging).
2. **Range.** The offset moves the centre, not the width. When the centre goes far enough the sweep straddles the corner unevenly and then leaves the wall. The range slider stands in for what the head allows; the loop stops at it with a LIMIT badge. Left standing: the real range may be a fraction of a millimetre.
3. **It is one axis.** Hand or rotator drift has two components across the corner; an offset along one line corrects the component along the corner path and leaves the other as a standoff error. Fine for seam position, useless for focus.
4. **Trusting the sensor.** The loop nulls what it sees; a sensor bias becomes a bead offset (the bias slider). With drift of 1.2 mm radial and 0.6 mm vertical the loop drives the spot to 0.00 mm along the path in a second or two (scene test).
5. **Which motor is it?** Assumption: the "motor" in the drawing and the red-light adjustment are the same swing actuator. Not established. The manual says the laser head contains a vibration motor and to handle it gently [manual p. 20].

## Branches and combinations

- Combines with borrowed-05-guide-star (calibrate the slope; the guide loop with one axis) and with any arrangement that leaves a residual of tenths of a millimetre across the seam.
- Transferable: use the process head's own scanner as the fine axis.

## Unresolved problems and questions that need Derek

For Derek to observe:
- Does the red-light alignment screen shift the actual beam spot (put a piece of scrap under the gun with a low power dot, or the red light only) or only the pilot? By how many millimetres at each end of its range, at the working standoff?
- Does the swing keep its shape and width while shifted?
- Does the head or the laser unit accept the shift or the swing setting over RS232 or the DB25 port? A USB-to-RS232 adapter with an FTDI chip is $12.99 on Prime (sourcing/borrowed.md); the manual gives no command set, so this may need the manufacturer's supervisory software or a serial capture of it.
- Does the shift change focus or standoff?

## Assumptions

- Swing shape: a straight line along local X through the dot, width from a slider (2 mm from the repo's recorded settings [repo]); range of shift: slider, [unknown]; sweep landing by rays from the nozzle tip to points on that line, first hit on the drawn tube or plate: geometry only, no energy or melt claim; gun proxy from the manual envelope; dials illustrative.

## Sourcing pointers

sourcing/borrowed.md: FTDI USB-to-RS232 adapter (Prime, $12.99, 2K+ bought). The manual pages are in the repo's manual folder given in the study context.

## Scene

`borrowed-06-swing-offset`
