# trials on borrowed, wave 2

From **trials** ("The machine runs trials") to **borrowed** ("Borrowed from elsewhere"). Five of borrowed's ideas, one section each: the difficulty in the specific variant, the assumption behind it, a repair or branch and what it changes and leaves uncertain, and a question for the originator. Where the branch has a definite shape it is drawn as a scene of mine; borrowed's own files and scenes are untouched.

How I read the set. The station is an instrument for many repeated dry-run experiments conducted by software. So I ask of each idea: what does the AI do with it a hundred times overnight; what resets between trials and what does not; what does it teach the AI about the rig; and what does it cost when it goes wrong at three in the morning (the tube, the rim, the fibre). Everything is illustrative unless tagged **[repo]**, **[manual]**, **[derived]** or **[unknown]**. Scripts behind the numbers are in `explorers/trials/calc/`.

| section | borrowed idea | depth | what I did | scene of mine |
|---|---|---|---|---|
| 1 | borrowed-03 encoded arm | deep (stressed) | the arm calibrates itself against a dot board | `trials-19-fixed-point-cal` |
| 2 | borrowed-02 gimbal on gantry | deep (stressed) | the formula's silent term, the same trial for it, power loss | `trials-19-fixed-point-cal` (gimbal branch) |
| 3 | borrowed-10 gun-free dot | sketch (developed) | the pointer becomes a steerable ground truth; borrowed-06 is its real-gun twin | `trials-18-steerable-mule` |
| 4 | borrowed-05 guide star | developed | half a dot at the seam: guide on the fraction, not the centroid | `trials-20-guide-at-the-knee` |
| 5 | borrowed-07 tonearm | rough | the rim is not the seam; break-even parallelism; a stylus in the corner | `trials-21-rim-vs-seam` |

---

## 1. borrowed-03-encoded-arm: the coach speaks to two decimals of a number that carries a millimetre

**The difficulty, in this variant.** The scene's coach prints "move the dot 0.8 mm toward the tube axis and 1.3 mm down" from six joint readings. At the scene's defaults (12 bit, 0.2 degrees of linearity error, 0.3 degrees of zero offset) the estimate is 1.57 mm off; at the datasheet maximum of 1 degree the corner inset reads 11.8 mm. The idea file concludes that a cheap magnetic encoder makes "a coarse pose logger, not a fine aligner, unless its per-turn error is mapped by a calibration nobody has designed". I take that sentence as the brief.

The number that matters is not the worst-case absolute error at one pose. It is what the arm still gets wrong across the poses a hand actually uses, after the one touch-off the idea already has. Rerunning borrowed's arm model (`calc/arm_touch_cal.py`, the arm of `borrowed/calc/encoder_error.py`, truth drawn with random link errors of up to 2 mm and per-joint phases): with the dials varied over plus or minus 15 degrees about the opening pose and 1 degree of linearity error, the error against a dot held at one point, constant removed, is **1.3 to 1.6 mm rms** (0.5 to 0.7 mm at plus or minus 5 degrees, 2.6 to 2.7 mm at plus or minus 25). That is ten times the resolution the coach prints.

**The assumption.** That an encoder's per-turn error is a property of the part that nothing can remove. Over a working window it is not: a joint that moves 15 degrees sees a smooth stretch of a sine, which a fit absorbs as an offset and a gain. The arm's *repeatable* error is calibratable; what stays is the part that is not repeatable. The second, quieter assumption is that the only reference for the zeros is a touch-off at datums through the interlock circuit. A dot on a board is a better datum: the camera reads where it fell, so the hand does not have to be exact.

**A repair, drawn: `trials-19-fixed-point-cal`.** The hand takes about 40 assigned orientations (a list shown on a screen) with the red dot near one printed cross on a board at plate-face height (rung 1 of the artefact ladder, `trials-05`); camera A reads the dot's board xy for each; software records the six joints. Because the dot is at one point every time, the arm's own forward kinematics must return one point. A least-squares fit of 28 numbers (per-joint zero and one cosine and one sine of linearity error, two link lengths, the wrist offset, where the beam leaves the gun and its tilt, the camera-to-arm shift, the board height) removes what repeats. It is the pivot calibration of `trials-13` with the arm's pose in place of a tilt about a supposed pivot. The score is on fresh poses that were never fitted.

What it changes (100 touches, 200 fresh poses, mean of several draws):

| joints | unread play per joint | uncalibrated | after the fit |
|---|---|---|---|
| 16 bit | none | 1.5 mm | **0.03 mm** |
| 16 bit | 0.02 degrees | 1.6 | 0.32 |
| 16 bit | 0.05 degrees | 1.7 | 0.79 |
| 14 bit | 0.02 degrees | 1.6 | 0.33 |
| 12 bit (AS5600 class) | 0.01 degrees | 1.6 | 0.28 |

Forty touches are enough (0.34 mm against 0.32 at a hundred, 16 bit, 0.02 degrees of play; twenty give 0.43). Unmodelled second and third harmonics (up to the same size as the first) and a post that leans 0.3 degrees change the result by at most 0.06 mm in the same window.

**What it leaves standing.**
- The floor is set by two things the fit cannot see. Quantisation: 0.088 degrees per count at 12 bit is about 0.28 mm at this arm's lever arms. Play beyond the encoders (bearing slop, arm bend under the umbilical): 0.02 degrees of random play is 0.3 mm. The dashed line in the scene's chart is what a perfect fit would still leave. Nobody knows the play of a monitor-arm joint **[unknown]**.
- Calibrating over a small window and using a larger one costs: fit at plus or minus 10 degrees and test at plus or minus 25 leaves 1.2 mm (2.6 mm uncalibrated); fit at plus or minus 25 leaves 0.34. The touches must span what the hand will do.
- The model is matched to the truth: the near-perfect 0.03 mm is the best case, not a prediction of any part.
- The calibration belongs to a session. Joints settle and a bumped arm changes its zeros; a kinematic seat that the arm returns to (`trials-02`) is the cheap check that the zeros have not moved.
- It is a laser-off, dot-on-a-board result. It says nothing about where the melt is, or about deflection under a laser-on hand.
- 14-bit modules (AS5047P, AS5048A) exist with Prime delivery at $11.99 to $14.99; their sales evidence is thin (single-digit ratings). The 12-bit AS5600 modules in borrowed's sourcing carry the volume.

**Combinations.** With `trials-11` (the yardstick): the first entry of the yardstick is Derek's hands; the arm records the pose while the judge records the dot-to-seam error, and together they give the map from pose to error that the coach should use instead of forward kinematics alone. With `trials-04` (the seam map): the coach can be told where the seam is at each rotator angle rather than one number. With `trials-17`: the calibration's session id is a "recorded" row on the trial card.

**Question for borrowed.** What does the recorder need from the arm: the dot's *position* (the coach), or only the three orientation angles a skilled hand uses (the "useful travel" your open threads want)? If only orientation, a shell IMU (`trials-06`: pitch and roll from gravity) plus one yaw encoder does it and the arm's position error stops mattering; if position, would you accept a fixed-point trial as part of setting up the arm, and what unread play would you expect from the joints of the 2 kg-and-up arm you found?

---

## 2. borrowed-02-gimbal-on-gantry: the formula carries a term the error sliders do not show

**The difficulty, in this variant.** The gantry moves the gimbal centre C to `J + t g(v, h)`. That formula assumes C sits exactly at distance t from the dot along the roll line **in the gun's own frame**. In the drawn build C is where a printed cradle and a hand-balanced gun put it. The scene's "what the hardware fails to do" group holds a gimbal angle error (0.17 mm per 0.05 degrees at t = 200) and a gantry error, and no cradle error. A cradle error is three numbers. One millimetre of it, in a random direction, costs (`calc/gimbal_fixed_point.py`, touch-off at the home pose removed):

| swing (yaw, hole and roll each plus or minus) | rms dot error | worst |
|---|---|---|
| 10 degrees | 0.19 mm | 0.35 mm |
| 20 degrees | 0.37 | 0.70 |
| 30 degrees | 0.54 | 1.0 |

Three times the angle-error term the scene shows, at the swing the scene's own travel readout (193 x 122 x 173 mm at plus or minus 30 degrees) is built for. It grows with the swing because the error is a fixed vector in the gun's frame that the rotation moves.

A second difficulty is a step of the sequence, not a number in the formula. With **Motor power on** switched off (default pose, direct drive) the gun sags to the hole-axis stop at dial minus 25 degrees, the dot goes 185 mm off scale, and the cable badge reads **LIMIT: minimum bend radius 73 mm against the 240 mm stored minimum** (illustrative cable path; the scene with Motor power on switched off). The tube is not touched; the fibre is kinked. A station that runs all night sees power dips.

**The assumption.** That the cradle is a rigid, exactly-known extension of the gun ("t is set once at build time, not commanded"), and that the power stays on.

**A repair, drawn: the gimbal branch of `trials-19-fixed-point-cal`.** The compensating gantry is itself the pivot. Software runs 20 to 40 orientations with the beam on the same board cross, the camera reads where each landed, and a fit of the cradle offset (3), the gimbal's angle zeros (3), the board height and the frame shift recovers the error. Numbers (cradle error of (1.0, minus 0.8, 0.6) mm, camera noise 0.05 mm, plus or minus 20 degrees, 20 poses): the two components **across the beam** come back to 0.05 mm, and the error of where the beam meets the board on fresh poses falls from 0.43 mm to 0.018 mm. At camera noise 0.15 mm, 40 poses give 0.11 mm on the components.

What it cannot see: the component **along the beam**. It moves the nozzle along its own beam, so the spot does not move and a board's xy cannot register it (the fit leaves it at zero; the scene says so). That component is the standoff, and spot size (`trials-03`) is its sensor. It matters for the wire and the focus, not for where the beam meets the seam.

Two further branches for the same problem:
- **Make the error repeatable.** A three-ball seat between the shell and the cradle (the class of seat in `trials-01`/`trials-02` and `use-02`) turns "the cradle error" from a property of each mounting into a constant of the shell-and-cradle pair. The gun comes off the gimbal whenever Derek welds by hand; without a seat every remount is a new calibration.
- **Fail into the dock.** Bias the balance so the unpowered rest is the dock's ramp (`trials-02`), not the hole-axis stop. The price is a constant holding torque, m g e: borrowed's own numbers give 0.35 N m for 1.2 kg at 30 mm (`gimbal_geometry.py`), which is more than a small gimbal motor holds continuously as I understand them **[unknown]**. Better: the first hundred hours of unattended running use the mule (`trials-06`), which has no fibre to kink and takes the crash; the real gun and its fibre only come out for confirming runs.

**What it leaves standing.** The three gimbal axes are only concurrent to what the gimbal maker built; each adds columns to the same fit (nine more numbers) but their identifiability from one board has not been tried. Pose-dependent flex of the yoke under gravity. Gantry lost steps (the dock re-homes them). Board flatness: a free board-height term is fitted, and a board that is tilted is not.

**Question for borrowed.** Is C meant to be defined by the gimbal (its mechanical centre) or by the cradle? Which of the three offsets would you constrain by construction (a keyed, seated cradle) and which leave to the trial? And is there a stock gimbal you know that holds its pose unpowered, or is the worm-geared head the only candidate for anything that runs without watching?

---

## 3. borrowed-10-gun-free-dot: a pointer that is not a stand-in for the gun but a ground truth for the eye

**The difficulty, in this variant.** The idea file is a sketch: a $15 pan/tilt pointer where the nozzle would be, for camera work that can run all night. Two numbers in it do not survive the mule's geometry. It states the resolution at 100 mm ("0.1 degree is 0.17 mm"). With the beam at 32 degrees to the plate and the dot 16 mm ahead of the nozzle, a pivot 100 mm behind the dot moves the dot **2.07 mm per degree** (0.21 mm per 0.1-degree servo step), coarser than the 0.05 mm labels a ground truth needs. The same servo turning a **mirror at the nose** (16 mm from the dot) moves the dot 0.68 mm per degree of mirror tilt (the beam turns twice the mirror): 0.068 mm per step, at the price of reach: plus or minus 8 degrees of mirror reaches minus 5.6 to plus 5.9 mm against minus 16 to plus 4 for the pan/tilt (numbers from the scene's table). Resolution and reach trade against each other and the pivot's distance from the dot sets the exchange rate.

And the nose does not have room: the proxy nozzle tapers to 2.2 mm radius **[illustrative kit proxy, manual envelope]**. A servo does not fit there; a mirror might.

**The assumption.** That the pointer is a cheap substitute for the gun so the vision chain can be rehearsed without one. That is true and worth keeping. It undersells the idea. The pointer is the only thing in the station that can put a dot at a chosen place on the corner *with no arrangement moving and no mass*, so it is a **steerable ground truth**.

**A development, drawn: `trials-18-steerable-mule`** (combines the mule of `trials-06`, the knee of `trials-03` and the swing offset of `borrowed-06`). The mule carries the pointer. A sweep across the corner finds the seam **in the pointer's own units**: the plate part of the dot disappears at the seam, so the command where half of it is visible is the command that puts the dot's centre on the seam (coarse sweep, then a fine one through the transition, a line fitted through it). After that every command is a labelled offset: 1.0 mm short, 0.5 mm short, on the corner. In the scene, with 0.02 fraction noise, 0.1 degree steps and 0.2 degrees of lash, the labels come out 0.02 to 0.03 mm from the truth for the pan/tilt and 0.06 mm for the mirror; the swing-offset type, which has no servo lash, comes out 0.002 mm. Two details carry the numbers:
- **The lash cancels only if labels are approached from the side the sweep used.** The sweep goes upward, so the knee sits half a lash later than the true seam in command units, and any label approached upward carries the same half lash. From the other side it is the wrong sign (the scene's "labels approached from" radio shows it). It is the unidirectional final approach of `trials-02` again.
- **The scale needs the pivot's height above the plate.** A far pivot barely notices 0.5 mm of shell height (0.6 per cent of scale) and a near one does (3.7 per cent): 0.055 mm error on a 1.5 mm label. The shell's placement error is a slider.

What it is used for, all laser-off and unattended: thousands of labelled frames for the judge (at 3 s a label about 1200 an hour); a camera-to-gun-frame calibration for free, because the pointer's axes are in the shell's frame (borrowed-05's nudge-and-watch does the 2x2 without moving the arrangement); a golden dot: the same command repeated every ten minutes shows camera drift and, stepped or blinked, latency; and a rehearsal bench for any fine-axis loop. The third steering type is exactly `borrowed-06`: the gun's own swing offset, if it can be commanded, would present the same command and the same sweep. The mule lets the AI build the loop, with a range slider standing in for the unknown range, before Derek learns whether the real head accepts a shift. If it turns out the gun's red light alone can be lit (your open thread), the pointer is redundant for a *fixed* dot and not for a *moving* one.

**What it leaves standing.** The pointer is not the gun's dot: the listed 5 mW modules are 17 times brighter than 0.3 mW **[manual p.12]**; a class 2, under 1 mW module with an APC driver is $15.99 on Prime and 79 ratings (`sourcing/trials.md`), nearer. Eye safety of an unattended red laser is Derek's call. A hobby servo's lash and drift over hours are not measured (a 28BYJ-48 stepper, 0.088 degrees per half-step, 400+ bought a month, is the finer option; its gear backlash is unchecked). Nothing here says where an infrared beam would melt; the dot finds the seam, not the melt. Whether a galvo mirror ($109.99, Prime, 25 ratings: thin) or a servo-turned mirror fits in a 5 mm nose is untested.

**Question for borrowed.** The scan of the nozzle region decides which type can be built: how small can the printed nose be at the tip, and can it hold a mirror of a few millimetres? Given that, which would you build first? And since the third type is your own swing-offset idea: do you want the pointer's command designed to be the same one, so the mule rehearses borrowed-06 before Derek finds out what the head accepts?

---

## 4. borrowed-05-guide-star: half a dot is not a star

**The difficulty, in this variant.** The simulated guide camera draws the dot as a whole red circle at the seam target however far into the wall it is, and the seam pixel as the target of the centroid. From above, the wall covers the part of the dot that lies on it (the wall spot is edge-on; `trials-03`). For a 0.5 mm dot at 32 degrees the footprint is 0.59 mm along r, and the centroid of the visible part moves at slope **1** while the dot is wholly on the plate, **one half** while it straddles the seam, **zero** once it has gone. Two consequences:
- The loop's target, the seam pixel, is unreachable: a centroid of zero needs a dot of zero visible width. In `trials-20` the loop parks the dot **0.26 mm into the wall** on average (rms 0.26 mm, out of sight 6 to 11 per cent of the time in the scene and in `calc/guide_at_knee.py`, hunting at the edge of visibility). That is half a spot.
- The nudge calibration measures the wrong plant when it starts near the seam. Started with the dot 0.3 mm short of the seam it measures a slope of **0.53** (0.73 at 0.5 mm short; at 0.15 mm short the star is lost while nudging and the calibration fails). The guide divides by that slope, so a gain of 0.6 becomes about 1.1 on the plate side.

**The assumption.** That the dot is a star: visible everywhere near the target, with a centroid that moves linearly with the axis.

**A repair, drawn: `trials-20-guide-at-the-knee`** (branch of borrowed-05, with the visible fraction of `trials-03`). Guide on the **visible fraction** with a target of 50 per cent. Half of the dot is visible exactly when its centre is on the seam, for any dot size, so the target does not need the dot's width, which changes with height. The centroid does the approach from the plate side, and the loop switches to the fraction as it drops below 97 per cent. In the scene (same noise, same drift) the fraction loop holds the dot centre at **0.005 to 0.009 mm** from the seam on average, rms 0.009 to 0.011 mm (scene and calc). That figure is the ideal-edge model's; it says the target can be reached, not that the real one is that clean. The calibration is done on the plate side (the button and the axis slider let you do it across the seam and see the failure).

**What it leaves standing.**
- The real dot is a round spot with soft tails, and the wall seen at a small angle is not a sharp line. The fraction curve is softer than drawn; for a symmetric spot the 50 per cent point stays at the centre.
- The fraction needs the dot's full brightness on the plate at the same standoff, measured once on the plate side; brightness changes with height and incidence.
- The scale bar of the idea (the wall's 1.65 mm) is the rim top, 6.35 mm above the seam. A camera off the axis by an angle sees the seam foot and the rim's inner edge 6.35 tan(angle) apart in the image: 2.1 mm at 18 degrees. The target and the scale must come from the seam foot, not from the strip.
- The wall side: camera B sees the wall spot, so a two-camera version could hold the 50 per cent point from both sides.

**Question for borrowed.** Does the guide camera of your drawing look straight down the bore, or from the far rim, where the wall face is visible and the wall part of the dot is seen at a grazing angle? And would you accept the guide's target being defined by the knee found in a sweep (`trials-03`, or the pointer of `trials-18`) rather than by a pixel?

---

## 5. borrowed-07-tonearm: the rim is not the seam

**The difficulty, in this variant.** The scene lifts the dot's vertical error from 1.43 mm to 0.005 mm at 20 times exaggeration by riding the rim. That result uses one number for the rim-to-plate distance, the "plate depth error below the rim" slider, held constant round the circle. The distance is a function of angle: the rim's tilt against the plate face's tilt. A rim that is off square to the plate by a small angle e gives a differential of 63.5 tan(e) mm at the weld station of the follower: 0.11 mm for 0.1 degrees, 0.33 mm for 0.3, 0.55 mm for 0.5 degrees. The face runout the rig accepts is 0.30 mm TIR, 0.15 mm amplitude **[repo]**. The follower removes what the rim and the plate share (the turntable and nest wobble) and adds what they do not share. It helps only where the rim and the plate face are parallel to within about **0.135 degrees** (atan of 0.15 over 63.5); above that it makes the vertical error worse than a locked gun. `weld-rotation-rig.md` already lists the tube's end squareness among the causes of face runout ("square the tube end or correct the end-cap seat") **[repo]**, so this is a known variable and nobody has its size **[unknown]**. The tube is a commodity 316L tube **[repo]**; whether its ends arrive square is unknown, and how each plate's recess is set (from the rim with a gauge, from the far plate through the rod, or by feel) decides whether the plate follows the rim at all.

**The assumption.** That rim height tracks seam height. It is the assumption the idea file names ("the rim is a good reference for the seam. It is not, if the plate's depth varies") and then models as a constant.

**A measurement and a branch (the differential and its break-even are drawn: `trials-21-rim-vs-seam`; the corner arm is not).**
- *Measure.* The arm's own angle encoder is a free rim-height trace (borrowed says so); a second indicator on the plate face gives the seam's, and their difference over one revolution on three tubes is the differential. It is a job for the indicator Derek already owns and a magnetic base, with the laser off. If the differential is under 0.1 degrees the tonearm is worth building; if not, the seam map of `trials-04` learns the *differential*, which the follower leaves.
- *Move the stylus into the corner.* A phonograph stylus rides a V-groove and follows both flanks. The inside corner is a groove: `datum-04-corner-follower` puts a ball of 1 to 2 mm in it and reads both the radial and the vertical position. A tonearm has two pivots, a vertical and a horizontal, so a corner ball on an arm with both follows radius and height together, with no dependence on the rim. The ball would lead the dot by 6 mm or more (datum-04's wire-corridor numbers), ride over tacks (they show as bumps, which is the tack count the guide asks for), and take a diagonal preload of about 2 N, with the counterweight as the vertical part. The arm's two encoders then record the seam's position at each rotator angle by touch, with no camera: an independent truth for the judge on the real 316L tube, which the notch tube (`trials-05`) gives only on a modified tube.

**What it leaves standing.** The ball on 316L wears and marks; a ceramic or PTFE ball is a guess. The corner also holds the wire corridor (datum-04's clearance at a 6 mm lead is 0.08 mm at a 30-degree wire). The follower's friction drag (about 0.6 N at 2 N and a friction coefficient of 0.3, illustrative) pulls the arm sideways. And the mass of the gun on the arm has not been resolved: the scene carries the gun on the arm; your notebook proposes only the follower riding on it.

**Question for borrowed.** Is the tonearm meant to carry the gun, as the scene draws, or to follow and be pressed against the gun's carrier, as the notebook proposes? And if the foot moves from the rim to the corner, does the tonearm's second pivot do most of what `datum-04` needs its own arm for?

---

## Combinations named

- **Fixed-point trial across arrangements** (borrowed-03 and borrowed-02 with the board of `trials-05` and the pivot of `trials-13`): drawn, `trials-19-fixed-point-cal`. Any arrangement that reports its own pose can be calibrated this way; the along-beam component is invisible to a board.
- **Steerable mule** (borrowed-10, borrowed-06, `trials-06`, `trials-03`): drawn, `trials-18-steerable-mule`.
- **Guide loop on the knee** (borrowed-05, `trials-03`): drawn, `trials-20-guide-at-the-knee`.
- **Encoded arm as the yardstick's first entry** (borrowed-03, `trials-11`, `trials-04`): not drawn; the arm records pose, the judge records error, the map from one to the other is what the coach uses.
- **Tonearm with a corner stylus** (borrowed-07, `datum-04`): the rim-versus-seam differential and the ball's trace are drawn, `trials-21-rim-vs-seam`; the arm with two pivots is not drawn, and the decision depends on two indicator readings nobody has.
- **Gimbal with a fail-safe dock** (borrowed-02, `trials-02`, `trials-06`): not drawn; the number that decides it is the holding torque of an intentionally unbalanced gun.

## Questions that need Derek's observation (collected)

- Weigh the gun and find its centre of mass (borrowed-02, borrowed-03 spring rating, `trials-02` dock cells).
- Two indicators on a tube over one revolution, one on the rim and one on the plate face, on three tubes (borrowed-07; also sizes the seam map of `trials-04`): does the rim track the plate?
- How the 6.35 mm recess is set: gauge from the rim, the rod, or by feel (borrowed-07).
- Whether the gun's red light alone can be lit and blinked (borrowed-10, borrowed-06, `trials-03`).
- The play in a monitor-arm joint under a 1 kg load at a 500 mm lever (borrowed-03): push at the wrist with a dial gauge on the far side of the joint.
- The nozzle region of the scan: how thin can the printed nose be at the tip (borrowed-10's mirror).

## What this exchange changes for me

- The pointer of borrowed-10 is the piece `trials-06` lacked: a mule whose dot moves. The mule becomes an instrument for the judge's own calibration as well as a stand-in.
- The fixed-point trial is the general form of `trials-13`; the pivot trial on a board is one instance of it.
- The guide loop needs the knee, and the knee needs a sweep: `trials-03` and borrowed-05 are one idea seen from two ends.
