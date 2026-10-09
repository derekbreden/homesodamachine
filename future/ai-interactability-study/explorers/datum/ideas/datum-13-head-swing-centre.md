# datum-13-head-swing-centre: the head's own beam-centre adjustment as a free fine axis

No scene (sketch; used inside datum-02 as a possible radial axis). Depth: sketch. Origin: swarm.

## Picture it

The X1 Pro's head already moves its beam sideways: it sweeps 2 mm wide at 80 Hz in the practice settings [repo], and the settings screen has a "red light alignment" step where the operator nudges the red light left or right to centre it on the nozzle [manual pp. 25, 39]. If that lateral offset can be commanded at run time it is a fine axis with no mechanism at all, and it is exactly the direction across the seam.

## The proposal

Lateral in the gun's frame, at zero yaw and roll, is the radial horizontal direction: moving the beam sideways moves the dot across the corner, between the plate side and the wall side. That is the radial error the seam signature (datum-02) wants to cancel (0.125 mm amplitude at the rig's radial limit [repo]). The laser unit exposes an RS232 port for "PC-based supervisory software" and a DB25 port for "PLC integration by customers" [manual p. 16]. Whether either can move the swing centre while running, over what range and in what steps, is not documented in the pages I have.

## What carries the loads, what establishes position, what is free or restrained

Nothing: the head's own scanner. Position is set by a commanded offset added to whatever the gun's support does.

## What software could command, observe, and what stays manual

Command: a lateral beam-centre offset (unknown range and resolution), if reachable. Observe: nothing about the result; the sensor from datum-02 or -04 does that. Manual: everything else.

## What was tried to break it

1. **It may be a setup step, not a run-time control.** *Conflict:* the manual documents the alignment as a touch-screen adjustment for a red light that is off-centre, not a live control. *Uncertain:* everything.
2. **Off-centre swing changes the melt too.** *Conflict:* moving the beam centre may not move the red light with it, so the dot stops marking the melt. *Left standing.*
3. **Only one axis.** It cannot supply height; that needs a stage (datum-03) or a mechanism.

## Branches and combinations

The radial axis for datum-02; a cheap partner to datum-03's vertical stage; a natural target for datum-04's estimate.

## Unresolved problems and questions for Derek

Can the swing centre be moved from the RS232 or DB25 port, by how much, in what steps, and does the red light move with it? Does the laser unit's vendor document the serial protocol?

## Assumptions

Wobble 80 Hz x 2 mm [repo pressure-vessel practice]; red light alignment [manual pp. 25, 39]; ports [manual p. 16]; the rest is inference.

## Sourcing pointers

None.

## Scene id

None (mentioned in `datum-02-seam-signature`).
