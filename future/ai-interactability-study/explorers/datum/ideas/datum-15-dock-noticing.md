# datum-15-dock-noticing: what a dock visit can notice, and a corner in the dock

Scene: `scenes/datum-15-dock-noticing/index.html`. Depth: developed. Origin: branch of `trials-02-dock-reset`, combining `datum-07-touch-off` and `trials-05-artefact-ladder` (the coupon is its rung 2 placed at the dock). Exchange: `exchange/datum--on--trials-w2.md` section 2.

## Picture it

The gun sits on the dock's three seats. Under the docked dot is a short length of tube and plate: a corner with a known place. Cells under the seats weigh the cable. The elevation shows the bench, the rotator and the tube, the travel from dock to corner, and one highlighted link at a time. Beside it, a table of six kinds of change (rotator re-clamped, dot moved inside the gun, positioner scale off, cable drag changed, a new tube seated deeper, camera nudged) against three readings (the weigh-in, the coupon probe, the tube probe) and the error that stays silent at the trial.

## The proposal

The dock of `trials-02` re-creates the shell's pose against the bench. The pose that decides the weld is dot-to-corner on this tube. If a probe finds the corner at the start of each trial (the dot sweep of `trials-03`, the stylus of `datum-07`) the dock's coordinates are not what the trial rests on. What the dock can still do is notice change between visits and say which link moved. Three readings do different jobs:

- **Weigh-in.** Forces, not positions. It sees the cable's drag (45 to 90 g per newton on the most affected cell `[trials-02]`; 68 used here) and nothing else.
- **A coupon under the docked dot.** The same probe, run on a corner with a known place. It sees what is inside the gun and camera: the dot moved in the shell (a re-seated gun, the red-light alignment `[manual pp. 25, 39]`), the camera nudged. It cannot say which of the two.
- **The probe on the tube.** The sum of every link from the dock to this corner: re-clamp, scale, drag, seat depth, and the dot's own shift.

Where a change shows on the coupon it is in the gun or the camera; where it shows only on the tube it is outside them. The tube probe also absorbs a moved dot (it finds the dot's own corner), so the dot-versus-wire relation, the part of the dot-versus-melt term a dry run can reach, stays wrong unless the coupon sees it.

## What carries the loads, what establishes position, what is free or restrained

The ramp and seats carry the shell when parked (trials-02). The mount is a choice: the bench (a link in the chain from the room), or a bracket from the rotator's own base (the bench-to-rotator clamp drops out). Position: three kinematic seats re-create the shell; a coupon corner is a place on the dock.

## What software could command, observe, and what stays manual

- **Command:** the positioner path (undock, hover, probe the coupon, probe the tube, dock); weigh-in on docking; what to do with a shift (recalibrate, flag, stop).
- **Observe:** three cell shares against baseline; dot against the coupon corner; dot against this tube's corner.
- **Blind:** whether a coupon shift is the dot or the camera; the trial itself; the melt.
- **Manual:** making and placing the coupon; deciding the allowed shift; re-aligning the red light.

## What was tried to break it

Rules with illustrative sizes (nominal: re-clamp 1.0 mm, dot in shell 0.20, scale 0.10 per cent, drag 1.0 N, seat 0.5, camera 0.30), not measurements.

1. **A re-clamp or a scale error passes to the dot unless the tube is probed.** *Assumption in the dock idea:* re-anchoring the shell re-anchors the trial. A 1 mm re-clamp, or 0.1 per cent over 330 mm (0.33 mm), reaches the dot with no probe on the tube; with a probe both are absorbed and the dock's coordinates stop mattering. The rotator is clamped through four 10 mm holes `[repo]`; how far it moves between sessions is `[unknown]`.
2. **A moved dot is silent to the tube probe.** With the tube probe on and no coupon, a 0.20 mm shift of the dot in the shell leaves 0.20 mm of dot-versus-wire error; with the coupon it leaves the probe's repeatability (0.03). The same for a nudged camera: 0.30 mm of judge error without the coupon.
3. **The coupon sees a sum.** One shift in one number cannot be the dot or the camera. *Repair not drawn:* a second observer that sees only one of them (a mark on the shell in the camera's frame). *Left standing:* whether the AI should re-zero the judge or re-align the red light when only the sum is known.
4. **A dock on the rotator base conflicts with the lift column.** It stands within about 200 mm of the axis; `trials-02` draws the gun body in the tube's lift column at 150 mm. It is available where the tube leaves sideways or down (`room-01`, `room-05`), or where the dock swings clear.
5. **The final approach direction.** The probe's last approach on the tube and on the coupon should come from the direction the position approach will use, so backlash and hysteresis add the same offset to both (`trials-02`'s one-sided approach).

## Branches and combinations

- Branch of `trials-02-dock-reset`. `trials-17` (trial card) lists "the dot itself" as recorded by a pivot trial on the board "when it may have changed"; the coupon at the dock says whether it did, at every visit. `trials-13` (pivot calibration) and `trials-05` (board, coupon rung) are the coupon's neighbours; `datum-14` reads the judge's bias with touches, which the coupon can supply at the dock.
- Combines with `datum-07-touch-off` (the probe on both corners).

## Unresolved problems and questions for Derek

- Coupon material: a short stub of the same 316L tube and plate, or a printed corner for dry runs and a real one for confirming runs.
- How the dot probe is run at the dock without lifting the shell off its seats (the positioner sweeps; or the head's own fine axis `datum-13`, if it exists).
- Bench test: probe one coupon and one tube ten times each, after re-seating the gun in its shell and after moving the camera 0.3 mm.

## Assumptions

Sizes above; thresholds 0.05 mm on the probes and 0.2 N on the cells; boom compliance 0.4 mm/N (freedom-01: 0.3 to 0.9 for a rigid grip); all illustrative. Geometry of the docked gun from `trials-02`.

## Sourcing pointers

`sourcing/datum.md`: probe class (CR Touch, ruby-ball styli) as in `datum-07`; nothing new for the cells (`sourcing/trials.md`).

## Scene id

`datum-15-dock-noticing`.
