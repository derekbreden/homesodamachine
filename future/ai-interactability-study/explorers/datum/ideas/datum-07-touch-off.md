# datum-07-touch-off: the stylus is already at the dot

Scene: `scenes/datum-07-touch-off/index.html`. Depth: rough. Origin: swarm. **Software moves, observes a one-bit contact, and that is enough.**

## Picture it

In a dry run, a ball stylus where the nozzle would be is driven by two small axes toward the wall until a contact bit flips, backed off, driven slowly for a second touch, and then the same downward onto the plate face. The two touches are the corner of this tube. The stylus ball's centre is at the dot by construction, so touching the corner is placing the dot on the corner. A supervising program logs each step; no camera, no line of sight, no model of the tube.

## The proposal

Use the cheapest sensor there is, a switch, and let software do the searching. Three tips: a dedicated ball stylus threaded in place of the nozzle (the manual says the copper nozzle can be removed, p. 20; the nozzle thread is not documented); the 0.76 mm wire fed out of its guide a few millimetres, which is already aimed at the dot; the copper nozzle itself, 16 mm short of the dot. Fast approach, retract, slow second touch (so the late-detection bias is the slow speed times the latency); wall first, then plate. Position at trigger minus tip radius is the surface.

This is something an AI could run by itself on every tube: a self-contained per-tube calibration with a switch and two small axes.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** not addressed; the stage rides on whatever holds the gun (a crown's stage, an arm's wrist, a fixture). Touch force is a fraction of a newton for a probe of this class.
- **Position:** the tube's own wall and plate face, found each time.
- **Free / restrained / driven:** two axes driven by software (proposed), a compliant stylus.

## What software could command, observe, and what stays manual

- **Command:** stage X (radial) and Z (height), speeds, the sequence.
- **Observe:** the contact bit and the stage position from its step count. Nothing else.
- **Manual:** swapping the stylus for the nozzle and back; coarse aim to within a few millimetres of the corner; cleaning the surface.

## What was tried to break it

Numbers from `calc/touch_off.py` (`calc/touch_off.out`); every error source is illustrative except geometry from the repo and manual.

1. **The contact signal is late.** *Assumption:* detection is instant. *What the numbers say:* the recorded position overshoots by speed times latency: 0.10 mm at 1 mm/s and 100 ms, 0.01 mm at 0.1 mm/s. *Change:* the fast-then-slow double touch; the fast touch only finds the neighbourhood. A full touch-off takes about 20 s at 2 and 0.1 mm/s.
2. **The nozzle as the probe.** *Assumption:* the dot is where the nozzle points. *What the numbers say:* the dot is 16 mm beyond a cone-shaped nozzle (kit proxy); 1 degree of beam-direction uncertainty is 0.28 mm; the nozzle branch is about 0.30 mm RMS per axis against 0.035 for the stylus and 0.16 for the wire, at the same contact repeatability. *Change:* the stylus.
3. **The wire is soft.** *What the scene shows:* 0.38 mm tip radius [repo: wire 0.030 in] but a tip that bends and a position uncertain by a few tenths (0.15 mm swap sigma, illustrative).
4. **Debris and oxide.** *What the scene shows:* a bump read as the surface. *Repair:* repeat and take the median; clean and scuff as the sequence already does for the work contact [repo].
5. **The sense signal itself.**
   - *Known:* the laser unit already checks a complete circuit between the work clip and the gun before it emits, and shows an alarm when conduction is lost [manual pp. 19, 32]; the manual describes contact "between the welding torch and workpiece" as a condition.
   - *Unknown:* how the circuit closes (nozzle, wire, or body), whether it is readable through the RS232 or DB25 ports [manual p. 16], and its latency. A separate low-voltage sense to a spare pin would not depend on it but is not designed here, and it must not fight the interlock.

### From travel's exchange (wave 3: `exchange/travel--on--datum-w2.md` section 3; `scenes/travel-15-touch-stack`)

6. **Round 6: what carries and moves the tip.** *Conflict (travel):* a fine stage carrying the gun and a stylus sits on the gun side, where the umbilical pulls, and its compliance is in the touch. *What the change alters:* the scene has `What carries and moves the tip`: gun side (a stage in the shell, about 94 micron per newton in the chain: stage 50 plus holder 44) or work side (the gun and stylus locked on a holder at 44, the tube stack moving: `travel-15`). A touch made with the stage that then applies it is a null measurement: guide straightness, layer tilt and the stack's own Abbe error (0.05 degree of layer tilt is 0.2 mm at the dot) are in the touch and the weld alike. Touch force times compliance lands in the constant (0.3 N x 44 micron per newton is 13 micron). *Leaves uncertain:* the stack's backlash and stick-slip; whether a 1 mm ball rides the plate's 0.13 mm slip gap; a tack under the ball; whether touching the corner about to be welded is acceptable.
7. **Round 7: 0.030 mm was two assumptions.** *Conflict (travel):* the largest term, the tip-to-dot swap error (0.030 stylus, 0.15 wire, 0.30 nozzle), is not a swap error. *Answer:* 0.030 mm is my assumption for the repeatability of the stylus's thread and seat; the other, which the first scene took to be zero, is the vector between the tip and the dot: the stylus is at the dot only if the red pilot sits on the nozzle axis 16 mm out, and the manual documents an alignment screen because it does not always (pp. 25 and 39). Better touching does not reduce it. *What the change alters:* two rows now, repeatability and a systematic vector (0.30 mm, unknown). *Repair, adopted:* touch a coupon's corner with the stylus and sweep the dot across the same corner (`eyes-06`), both in stage units; the difference is the vector, with no camera calibration; the floor is the calibration's accuracy (0.05 mm) and the dot is still not the melt. *Leaves uncertain:* the vector itself.
8. **Round 8: the extension.** *Conflict (travel):* the graduated tube sets the nozzle extension, which moves the dot along the beam, so a stylus is the right length for one extension only. *Left standing:* nobody has fixed the extension the stylus is measured at (a question for Derek: which extension, and does the dot move with it).

## Branches and combinations

- **With the crown** (datum-03): the crown's vertical stage plus a small radial slide is the stage; the plunger there is the same idea for height only.
- **With the seam signature** (datum-02): touch-off supplies the constant term (setup offset) of the signature.
- **With the follower** (datum-04): the follower drags a ball along the corner; touch-off drives a tip into it.

- **Used by.** The touch is the unlike sensor that bounds a judge's bias at K azimuths (`datum-14-who-owns-the-wobble`); the probe run on a known corner in the dock and on the tube (`datum-15-dock-noticing`); the probe on the tabletop, the rim, the plate and the wall in the table opening (`datum-18-flush-to-the-table`); the wire as the second probe on the same corner (`datum-20-dot-and-wire`).

## Unresolved problems and questions for Derek

- Can the copper nozzle be removed and a stylus threaded in? What is the thread?
- Does the laser unit expose its conduction circuit? How does it close today?
- Is touching the corner where a fillet is to be welded acceptable (a fraction of a newton, but nobody has looked)?
- What carries and moves the tip by a few millimetres at 0.01 mm resolution?

## Assumptions

- Ball 1.0 mm radius, nozzle cone 3 mm effective radius: illustrative; wire 0.030 in [repo]. Repeatability (0.010, 0.050, 0.030 mm), tip-to-dot swap (0.030, 0.150, 0.300 mm), backlash, debris, latency, speeds: illustrative. 16 mm nozzle-to-dot is the kit proxy.

## Sourcing pointers

`sourcing/datum.md`: Creality CR Touch (Prime confirmed, $34.99, 1.7K ratings, "200+ bought in past month"), ruby-ball CMM styli (weak sales evidence), mini linear stage. Fit and force unchecked.

## Scene id

`datum-07-touch-off`.
