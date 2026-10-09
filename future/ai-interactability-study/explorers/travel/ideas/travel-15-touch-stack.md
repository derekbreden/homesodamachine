# travel-15-touch-stack: touch-off, the work comes to the stylus

Scene: `scenes/travel-15-touch-stack`. Origin: combination of `datum-07-touch-off` and my `travel-01-tube-travels` (exchange wave 2, section 3), with `eyes-06-dot-as-probe` and `trials-14-contact-sense`. Depth: developed. Framing: split the travel: which body moves, which error shows up as which error at the dot.

## Picture it

A ball stylus, 1 mm in radius, stands where the nozzle was, at the dot. The gun sits on a holder that is locked and never moves. Under the rotator a stack of two stages does the moving: X pushes the wall toward the ball, a fast approach, a half-millimetre back, a slow approach until one bit flips; Z lifts the plate into the ball the same way. The two stack positions are this tube's corner at the pose the stack will weld in. The rotator indexes to the next angle and the touches repeat: eight angles, about two minutes, and there is a seam signature with no camera. A second, one-time routine touches a coupon's corner with the stylus and sweeps the dot across the same corner: the difference, read in stack units, is where the dot is relative to the stylus.

## The proposal

datum-07 finds the corner by driving a stylus into it and leaves open what carries and moves the tip a few millimetres at 0.01 mm. The stack of travel-01 is that mover, with the moving side inverted:

- **The touch force goes into a holder that is stiff by design.** Nothing soft sits on the gun side and no cable is on the moving side. Force times compliance is a systematic offset (0.3 N times 44 micron per newton, `calc/06`: 13 micron), the same at every angle, so it lands in the constant term.
- **A touch made with the stage that then applies it is a null measurement.** Straightness and tilt of the guides, and the Abbe error of `travel-01` (0.05 degree of layer tilt is 0.2 mm at the dot), are in the touch and in the weld alike and cancel. Only what changes between the two matters, and no stage moves between them.
- **The same touches at N angles are a signature by contact.** Dry, cold and static: no line of sight, no fume, no camera calibration. datum-02's harmonic fit runs on it unchanged (the scene fits constant, 1x and 2x). Replay: the stack follows the fit by rotator angle, which is the follow stage of `travel-02` with its own sensor.
- **The stylus is not the dot.** datum-07's largest error term is the tip-to-dot swap (0.030 mm for the stylus, 0.15 wire, 0.30 nozzle) and assumes the dot is where the tip is by construction. The dot is the red pilot, aligned by a screen the manual documents (pp. 25, 39); how it sits on the nozzle axis 16 mm out is unknown. Touch a coupon corner with the stylus and sweep the dot across the same corner (`eyes-06`, image break at the corner): both are read in stack units, so no camera calibration and no model. The scene has the unknown offset as a slider (0.30 mm) and the calibration as a toggle with an optical accuracy (0.05 mm). After calibration the error at the dot is the calibration's own accuracy; the dot is still not the melt.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** a locked holder (post and two-link arm) carries gun and stylus; the stack carries rotator and tube; the umbilical and wire conduit hang from a fixed gallows.
- **Establishes position:** the tube's own wall and plate face, by contact, at each angle; the stack's step counts are the coordinates.
- **Free / restrained / driven:** X and Z driven, the rotator indexed; gun fixed; the tangent position free (redundant).

## What software could command, observe, and what stays manual

- **Command:** X and Z (fast, retract, slow), rotator index, replay of the fit.
- **Observe:** one contact bit (its source is unresolved: the laser's work circuit if readable, or a separate low-voltage sense, `trials-14`), step counts. Blind: the dot, the melt.
- **Manual:** swapping the stylus for the nozzle and back; hand-aiming so the ball starts inside the bore and above the plate (the scene's default is 3 mm each); cleaning the corner; the coupon.

## What was tried to break it

1. **The stack's own backlash and stick-slip.** *Assumption:* the stack repeats at the slow approach speed. *What the scene shows:* the repeatability slider (0.010 mm) is the whole per-touch noise; N=8 fits five parameters per axis. *Leaves:* unmeasured; borrowed-05 (nudge and watch) is the way to find it.
2. **The stylus offset.** See above. *Leaves:* the dot-sweep's accuracy (a few hundredths at best), and whether the pilot moves when the wobble is on.
3. **Time.** About 14 s per angle at 2 and 0.1 mm/s plus indexing at 15 mm/s: 8 angles 2.2 minutes, 24 angles 6.0 (scene readouts). *Leaves:* whether a dry routine of that length is acceptable per tube.
4. **A tack under the ball.** A touch at a tack reads the tack. *Leaves:* the tack angles are known from the first-tack procedure [repo]; skip or flag them.
5. **The plate slip gap and debris.** A 1 mm ball rides over a 0.13 mm gap; debris is datum-07's median-of-repeats. *Leaves:* nobody has looked.
6. **Touching the corner about to be welded.** A fraction of a newton on a polished vessel. *Leaves:* Derek's call.

**Wave 3 entry, from use's exchange ("Also noticed").** **The touch routine adds two hand-on-gun states (use).** *Conflict:* the routine follows the tacks (guide step 3) and the shoe, and a tack under the ball is read as a tack (noted); the stylus stands where the nozzle was, so a per-tube routine is a hand swap in and a swap out unless the stylus has its own slide to the dot. *Assumption behind it:* the stylus is fitted once. *What the change alters:* recorded; a stylus on a small slide beside the nozzle is the unbuilt variant, and with an arm (`travel-20`) the arm can fetch it. *What it leaves uncertain:* the nozzle thread and the stylus length at the graduated extension.

## Branches and combinations

- With `datum-02-seam-signature`: the touch signature is a sensor for it that needs no line of sight; the parity question of `travel-18-signature-parity` applies to it as to any dry turn.
- With `datum-04-corner-follower`: the follower's two-lead yaw estimate can be nulled by the stack's Y stage, which is a plan-angle stage with a 1/r reduction (1.08 mm of Y per degree, `travel-01`).
- With `travel-06-nest-driver`: the touch signature's radial 1x is what the nest screws would take out at its source.
- With `trials-13-pivot-calibration` and `eyes-06`: the alternative and the partner ways to find the stylus-to-dot vector.

## Unresolved problems and questions for Derek

- Can the copper nozzle come off, and what is its thread; does the graduated tube (nozzle extension) move the dot along the beam, so the stylus length is right only for one extension?
- How does the laser's work circuit close (nozzle, wire or body), and is it readable over RS232 or DB25?
- The plate seat depth and tube length spread: the stack ranges (+-12 mm here) only need the coarse aim, not those.

## Assumptions

- Stack ranges and step, repeatability 0.010 mm, fast 2 and slow 0.1 mm/s, latency 5 ms (datum-07's numbers), ball radius 1.0 mm, holder compliance 44 micron/N, touch force 0.3 N, runout 0.25 / 0.30 mm TIR **[repo]** as acceptance numbers, ovality 0.03 mm, seat error 0.5 mm, stylus-to-dot offset 0.30 mm and calibration accuracy 0.05 mm: **illustrative** (the offset is **[unknown]**).

## Sourcing pointers

`sourcing/travel.md`: stage entries 1 to 6 as for travel-01; datum's `sourcing/datum.md` for the CR Touch and ruby styli.

## Scene id

`travel-15-touch-stack`
