# eyes — notebook (Seeing first)

Framing: begin from what can be observed about the dot, the seam, the gun's pose, the tube and the wire (cameras, markers, light, touch, electrical continuity, sound, inertial sensors); what can be seen from where; what the rim, the gun and the glare hide; which measurements are direct and which inferred; how the arrangement changes once it is known how the gun will be seen.

Source tags as in `context/shared-context.md`: **[Derek] [repo] [manual] [derived] [unknown]**. Numbers I introduce carry `illustrative` or the calc script that produced them (`calc/`). Nothing is ranked or scored.

---

### 0. Arrangements held (kept current here; a separate summary.md was refused by the tool in this session)

| id | what it is | scene | maturity | origin |
|---|---|---|---|---|
| eyes-01-gun-borne-eye | camera + line laser on the shell measure the seam against the dot in the gun frame; loose support, small two-axis trim stage | `eyes-01-gun-borne-eye` | deep | swarm |
| eyes-02-where-can-an-eye-stand | dome of camera positions tested against wall, rim, gun; sensitivity and kink maps; station presets | `eyes-02-where-can-an-eye-stand` | developed | swarm |
| eyes-02b-sensor-crown | ring of fixed eyes round the tube | preset in eyes-02 | sketch | branch |
| eyes-03-marker-cube | fiducial cube on the shell, fixed cameras see tags not the dot; lever-arm error budget | `eyes-03-marker-cube` | developed | swarm |
| eyes-04-proximity-skin | capacitive pads / eddy coils around the nozzle; no light; error map; model error becomes bias | `eyes-04-proximity-skin` | developed | swarm |
| eyes-05-touch-off-interlock | stylus or nozzle touch-off; the laser's work-contact circuit as a touch sensor | none | sketch | swarm |
| eyes-06-dot-as-probe | sweep the dot across the corner; the image path changes speed or direction there | `eyes-06-dot-as-probe` | developed | swarm |
| eyes-06b-corner-mirror | the plate bounces the dot onto the wall; the two spots merge on the corner | mode of the eyes-06 scene | sketch to developed | branch |
| eyes-07-sectioned-tube | half-tube phantom: a tangent camera sees the true L-section; calibrates every inferred sensor | `eyes-07-sectioned-tube` | developed | swarm |
| eyes-09-scan-then-weld | dry-turn seam map played back by a slow axis; look-ahead camera; comparison of what each leaves | `eyes-09-scan-then-weld` | rough | swarm |
| eyes-10-under-the-workpiece | first closure only: slip-gap light and thermal underside through the service bore | none | sketch (broken on a number) | swarm |
| eyes-11-what-each-eye-sees | six gun coordinates against nine sensors; IMU + microphone observe without moving | `eyes-11-what-each-eye-sees` | developed | swarm |
| eyes-11b-umbilical-eyes | stripe and beads on the umbilical give twist and bend radius | none | sketch | branch |
| eyes-12-dot-lattice | software moves in a scripted grid, video and a person observe afterwards; or software observes and a person moves | none | sketch | swarm |
| eyes-13-cords-see-a-spot | a spot on a surface is a line's end: room-06's calibration loses the position along the beam; a nozzle-height camera (room-05's B) brings it back | `eyes-13-cords-see-a-spot` | developed | combination (room-06 + room-05) |
| eyes-14-wall-as-window | the wall port's outside end is a clean place for scales and a load cell; the rod's bending, not the ball's play, is the large term for a thin rod | `eyes-14-wall-as-window` | developed | branch of room-03 |
| eyes-15-what-the-holder-hides | one dome, five holders (none, hand, monitor arm, table opening, rings): what each hides from the observers | `eyes-15-what-the-holder-hides` | developed | branch (Derek's examples, room-08) |
| eyes-16-measure-the-tube-first | plate depth from a low look across the bore; a PTZ camera's aim cancels because both features share a frame; the scale needs a ruler | `eyes-16-measure-the-tube-first` | developed | branch of room-01 / room-09, Derek's PTZ vision |
| eyes-17-lit-bar-brake-wall | the coach loop with the hand pushing the gun through a two-slide stage; an LED bar on the shell and a passive brake wall driven by the gun-borne eye; the override is data | `eyes-17-lit-bar-brake-wall` | deep | wave 3 new direction (use-06 + eyes-01) |
| eyes-18-what-the-estimate-owes | lens: seven ways of telling or holding a hand against five estimate faults | `eyes-18-what-the-estimate-owes` | developed | wave 3 new direction (freedom-14 + borrowed-19 + eyes-01) |
| eyes-19-touch-cue | a three-contact stylus on the shell as a hand-held cue or the trigger of a real wall | none | sketch | wave 3 new direction (eyes-05 / freedom-12) |

Idea files: `ideas/<id>.md`. Numbers: `calc/` (wave 3: `line-laser-pose.mjs`, `pad-selectivity.mjs`, `umbilical-gauge.mjs`, `feedback-budget.mjs`, and `_audit.mjs`, `_shotel.mjs` for opening scenes as a stranger would; wave 2: `cords-spot-*.mjs`, `wall-window.mjs`; `_check.mjs`, `_eval.mjs` are copies of the coordinator's checker with longer timeouts and a script runner, made because the machine load average reached 55 and the stock 20 s page timeout failed every scene). Parts: `../../sourcing/eyes.md`. Exchange: `../../exchange/eyes--on--room-w2.md`. Arrangements are also listed in `index.md`.

---

## Wave 1

### 1. First look: the geometry of looking (before any idea)

Facts that shaped every idea, each from shared-context or arithmetic on it:

- The dot sits in a canyon: joint circle r = 61.85 mm, 6.35 mm below the rim, wall 1.65 mm, plate face the floor. **[repo]**
- The dot is at the wall. Every line from the dot that goes outward (+X) runs into the wall at once, so the dot can only be seen from the bore side, above the plate. **[derived]**
- The rim is less of an obstacle than it looks: a camera across the bore at rim height or above sees the dot from 2.9 degrees elevation (6.35 mm over 125.35 mm). What is lost across the bore is angle: at 5 degrees the plate's radial direction is compressed about 11 times while the wall's vertical direction is seen at full scale. **[derived]** (calc/view-sensitivity.mjs)
- The seam moves slowly relative to a fixed gun: at most 0.016 mm/s radial and 0.019 mm/s face at 8 mm/s (0.030 / 0.036 at 15 mm/s) from the rig's runout limits. Bandwidth is not the observer's problem; accuracy and bias are. **[derived]** (calc/runout-rates.mjs)
- In the gun frame the dot is fixed and the seam moves; in the tube frame the seam is fixed and the dot moves. A camera on the gun measures the seam in the gun frame; a bench camera needs both frames.
- The laser's own work-contact circuit and its three status LEDs (Ready / Laser on / Alarm) are signals that already exist. **[manual]** pp.15, 19, 32. What closes the circuit at the gun end is **[unknown]**.
- The RS232 port is standard TXD/RXD/GND with no protocol given; the DB25 "PLC integration" port has no pinout in the manual. **[manual]** p.16

### 2. Arrangements written first (one line each, before development)

Ids are the scene/idea ids used later.

- eyes-01 Gun-borne eye: camera and line laser on the shell see the dot and corner; error measured in the gun frame; loose support plus a small trim stage.
- eyes-02 Where can an eye stand: dome of viewpoints tested against wall, rim, gun, wire, weighted by sensitivity; leads to station presets.
- eyes-02b Crown of fixed eyes: ring of cameras on posts, gun through a gap.
- eyes-03 Marker cube: tags on the shell, fixed cameras see tags not the dot; lever arm.
- eyes-04 Proximity skin: capacitive pads or eddy-current coils around the nozzle; no light; blind to the dot.
- eyes-05 Touch-off through the interlock: stylus or nozzle touches rim and plate; the laser's work-contact circuit as the touch sensor.
- eyes-06 The dot as the probe: sweep the dot across the corner; the image path changes speed or direction there.
- eyes-06b The corner is a mirror: the plate bounces the dot onto the wall; the two spots merge on the corner.
- eyes-07 Sectioned calibration tube: half a tube, a tangent camera sees the true L-section: ground truth.
- eyes-09 Scan first, weld second: dry-turn seam map, slow correction played back; look-ahead camera.
- eyes-10 Under the workpiece: first closure only, the open bottom as a window: slip-gap light, thermal underside.
- eyes-11 What each eye sees (and blind but listening): six coordinates against nine sensors; IMU plus microphone observing without moving.
- eyes-11b Umbilical's own eyes: stripe and beads for twist and bend radius.
- eyes-12 The dot lattice: software moves in a scripted grid, a person or a video observes afterwards; or software observes and a person moves.

### 3. What I took deep and how it went

I took **eyes-01** and **eyes-02** deepest (several rounds each, with numbers and scenes), **eyes-03**, **eyes-04**, **eyes-06/06b** and **eyes-07** to developed scenes, **eyes-09** and **eyes-11** to working sketches with a scene, and wrote idea files for the rest, breaking **eyes-10** on a number and leaving **eyes-05** and **eyes-12** as sketches.

#### eyes-02 (dome): rounds

1. Built it expecting the gun to block a large share of the views. Ran the numbers in the scene (`window.__domeStats`): 42.0 % of the upper hemisphere sees the dot, 55.5 % is blocked by the tube, **2.6 % by the gun**, and the visible share changes by 0.1 percentage point over the whole grip-axis roll range. The wall, not the gun, decides where fixed eyes stand. (I had assumed the opposite.)
2. First fixed-eye test returned 0 of 2 for the far-side pair. Debugged: the camera bodies' own lens glass (role `work`) was an occluder for their own line of sight. Fixed by making helpers non-occluding. (A kit note: `P.camera` includes a `work`-role mesh that counts as an occluder.)
3. Added "seam seen" (dot, corner 8 mm either side, wall 3 mm above) because seeing the dot is not seeing the corner.
4. Found the look-ahead station's flaw by calculation (calc/look-ahead-geometry.mjs): both eyes see all four points, but the wall face is 0.05 of square-on. Added plate / wall face-on modes. One eye per surface.
5. Scanned the 1080 cells for a sweet spot: both sensitivities >= 0.92, direction-change score 0.99, whole seam in view, at 100-110 degrees round the tube, 17-23 degrees up. Built the "Beside" preset (130 degree pair).
6. Noticed my kink score counts direction change only; the sweep of eyes-06 also works by speed change. Wrote that into both places.

#### eyes-01 (gun-borne eye): rounds

1. First drawing: camera on the housing top. The scene said "corner blocked by gun". Cause: looking within about 10-15 degrees of the beam axis, the nozzle tip sits in front of the dot. The working window on a 27 mm stalk is 30-130 mm behind the tip (poses A and C). My first text had said the housing view was clear; it was wrong and I corrected it.
2. Line laser "blocked by the gun" was a grazing-ray artefact of my test point (the dot sits on the curved wall); moved the test point 1.5 mm into the bore. Recorded so nobody trusts the early red badge.
3. Pose B breaks parts of the mounting (laser blocked at clock 0 and 60; corner lost at 60 and 120 for some z). One mounting does not serve all poses.
4. Closed the loop on a biased sensor: estimate goes to zero, truth goes to minus the bias (0.27 / -0.19 mm for 0.30 / -0.20). The loop cannot see its own bias. That produced eyes-07.
5. Turned the tube with runout exaggerated 20x and the loop closed: 0.10 mm rms against 1.41 open; scaling by rate the real runout would be about twenty times smaller.
6. Consequence for the support: with a 4 Hz loop and gain 0.6, a disturbance of 0.1 mm/s is followed to about 0.04 mm (rate / (gain x rate of loop) = 0.1 / 2.4); the runout (0.02 mm/s) and any creep below that are absorbed. What the support must then supply is only a working neighbourhood within the trim range (+/-6 mm illustrative) and drift slower than about a tenth of a millimetre per second. **[derived]**

#### eyes-03 (marker cube): rounds

1. Predicted a trade between line of sight (the wall hides a cube near the nozzle) and lever arm. Ran it: the barrel is above the rim within a few centimetres, so a cube 40-80 mm back is visible from almost everywhere on the bore side, at the side and even over the wall (the camera pair placed at 0, 60, ..., 300 degrees azimuth and 10, 35, 60 degrees elevation gives both cameras a tag everywhere except on the gun's grip side at low elevation, where one camera drops out). The predicted trade is largely absent; the real constraints are that the cube has to fit (collides with the rim at clock -90 near the nozzle) and heat/spatter (unresolved).
2. First error model let "two cameras" mean 90 degrees regardless of separation. Replaced with summed information matrices; the position part falls from 0.29 mm at 5 degrees between rays to 0.04 mm at 40 degrees, but the total at the dot barely changes past 20 degrees because the lever-arm term dominates. My assumption that 10 degrees would lose most of the benefit was wrong.
3. Result: 0.14-0.21 mm at the dot for a cube 40-80 mm back with 25 mm faces and two cameras at 500 mm; 0.52 mm from the housing (230 mm back). The floor is an assumed 0.10 mm cube-to-dot calibration.

#### eyes-04 (proximity skin): rounds

1. Pads on the barrel far from the dot are useless: 0.9 mm capacitive resolution at a 30 mm gap (calc/proximity-model.mjs).
2. Pad facets matter: at 0 degrees off the beam axis each pad sees plate and wall together (ill-conditioned); at about 40 degrees they separate. The shell's shape is part of the sensor.
3. The map has a fold: a diagonal where different offsets give the same four readings. Marked as a blind line.
4. A 3-5 % gain error or a nearby conductor biases the solve by tenths of a millimetre and nothing in the four numbers says so. Same lesson as eyes-01: the sensor cannot see its own model error.

#### eyes-06 (dot as probe / mirror), eyes-07, eyes-09, eyes-10: what came out

- Sweep: the corner's speed contrast means even a low in-plane camera finds it (K 0.90 at 5 degrees) but the kink vanishes at about 58 degrees elevation in the section plane (K 0.00). Bounce: 19x radial sensitivity for a camera at 5 degrees; depends on a plate finish nobody has looked at. Cheapest test in the study: does Derek see a second spot on the wall?
- Sectioned tube: the direct view is one number along the L (where the beam lands) plus the nozzle pose; ten random samples find a 0.30 / -0.20 hidden bias to about 0.02 mm.
- Scan then weld: with distortion 0.12 and bias 0.10 the leftover radial rms is 0.195 (scan or look-ahead) against 0.105 (eye at the dot): distortion and bias, not runout, are what is left.
- Under the workpiece: the slip gap is a 6.35 mm deep, 0.127 mm wide slot; it passes light only within +-1.15 degrees of the axis, so the ring of light is invisible to any camera nearer than about 3 m without telecentric optics. Broken on a number; the thermal underside view survives as a post-hoc record (10 s lag, about 80 mm of arc).

### 4. Cross-idea observations (the framing's question: how the arrangement changes once it is known how the gun will be seen)

1. **Where the eye can be decides what is possible.** The wall forces every eye onto the bore side. The good places are beside the tube, slightly above the rim (about 105 degrees round), and across the bore; the tangent view that shows the true section is blocked by the wall. One eye per surface (wall face-on from across the bore, plate face-on from above).
2. **An eye that rides with the gun keeps its view for free** (eyes-01), and it turns two world-frame measurements and a subtraction into one gun-frame measurement. It costs a spatter-exposed camera and gives a bias no loop can see.
3. **Every inferred sensor has a bias the loop cannot see** (eyes-01, eyes-04, eyes-03). One direct view (eyes-07) is the single most reusable piece: it calibrates all the others.
4. **The dot can be the sensor** (eyes-06): sweeping it across the corner needs no calibration; the corner is found in actuator units.
5. **Observation can be time-multiplexed** (eyes-09) because the seam is slow: look where nothing is in the way, weld later; but the thing that moves during the bead (distortion) is only seen at the dot.
6. **Gravity sees two of the three rotations, the turn is the one it cannot see** (eyes-11).
7. The rotator already observes along-seam position; the circle makes it matter little.

### 5. Kit notes (for the coordinator)

- `P.camera()` includes a mesh with role `work` (the lens glass); scenes that add a `P.camera` with `scene.add` get a line-of-sight occluder at their own lens. Use `app.addHelper(cam)` or set `userData.occludes = false` on it.
- `app.legend(customList)` is overwritten at the next render whenever `app.add` (or `addHelper`) has been called since (the kit sets `legendDirty`). Workaround: `app.onReady(() => { app.legend(); app.legend(custom); })`, and call `app.legend(); app.legend(custom)` again after later adds.
- `markVisibility` at its default 4 mm end tolerance ignores a blocker within 4 mm of the target; for sub-4 mm features the target must be chosen a millimetre or two into free space (grazing rays on the curved wall report false blocks).
- `app.inset.add({up})` clones the up vector; a camera rigidly mounted on a rolled gun needs the inset re-created when the gun's pose changes (I did this on variant changes).
- Custom-stage scenes report content 0 % in `check-scene` (no canvas); this is only a warning-less pass, not a failure.

---

## Wave 2

### 6. The exchange with room (my partner this wave)

I opened all seven of room's scenes and read every idea file and their notebook. Five ideas took my attention: room-06 and room-03 (deep, stressed), room-05 (developed), room-08 and room-09 (sketches worth developing). The exchange file is `exchange/eyes--on--room-w2.md`; four new scenes came out of it (eyes-13 to eyes-16). What changed my mind, in order:

1. **A camera sees where a line ends, not where a point is.** room-06's fit is fed a 3-D dot position. The red dot is a spot on a surface. I expected a stepped board or the tube's own corner to give the missing direction back; the numbers say no. Slide the gun along its own beam: the spot does not move. One board 0.19 / 0.23 / 0.31 mm (radial, tangent, vertical, linearised, N = 40, 0.1 mm noise) against 0.043 / 0.036 / 0.036 for a 3-D dot; a stepped board and the tube's corner the same. Adding the nozzle tip's height (a low camera, 0.2 mm) brings it to 0.057 / 0.051 / 0.054. A Monte Carlo of the real nonlinear fit (25 seeds) agrees in kind: 0.10 against about 0.5. (`calc/cords-spot-cov.mjs`, `cords-spot-grid.mjs`, `cords-spot-observer.mjs`.) My first Monte Carlo runs disagreed with each other by a factor of three because Gauss-Newton got stuck in local minima; the linearised covariance was the honest way to compare observation types.
2. **The wall is a window, and the rod bends more than the ball plays.** I came to room-03 expecting to talk about sensing the ball's play from outside. Writing the beam model (`calc/wall-window.mjs`) showed the moment through the ball (about 5 N m) bends both the inside segment and the tail: for a Ø20 × 2 mm aluminium tube the dot ends 2.4 mm off the commanded line, thirty times the ball's play. My first idea, extending the line of two outside scales into the cabinet, is no better than step counts for a thin rod; reading the moment with a load cell at the tail actuators and subtracting a beam model gets to 0.13 mm.
3. **A kit default made room-05's camera B look blocked.** `markVisibility` on a point on the nozzle's axis with the default eps reads blocked by the nozzle's own skin (eps 3 reads seen). The digest treats it as a changed reading. From rim height at 330 mm the tip is seen from 28 of 36 azimuths and the dot from 7.
4. **The hand does not take the good stations.** I expected the operator's forearm to kill one of the two beside eyes for room-08's frame. It does not, for any operator side (15 degree sweep); it takes a band of 0 to 10 points elsewhere in the dome. The one holder that stands in the sight lines is the ring around the gun's tip (freedom-01): 15 mm behind the nozzle costs 9 points, 130 mm costs 1.
5. **The number room-09 waits for can be read from a picture.** A look across the bore, a little above the rim, sees the rim edge and the plate-wall corner in one frame: about 0.03 mm at 4K with a 9 degree lens (0.06 at 20 degrees). room-01's side camera at its default rim + 16 mm already sees the corner in the drawn geometry (threshold about rim + 13 mm at 300 mm); its I/O row says blind.

### 7. Derek's examples, in the eyes framing

Derek's monitor arm, table opening and rings, and his automated-setup vision (motors, PTZ cameras, an AI iterating), asked from where the observers stand and what each hides. Recorded again in the return under examplesTreatment; what I saw that the explorers who began with the examples did not:

- **The holders hide little; the wall hides almost everything.** With eyes-02's dome (bare gun 42 % of the upper hemisphere sees the dot; wall 55 %, gun 3 %), the holders add 0 to 10 points: monitor arm 0 to 3 (it stands above the dome), table opening 0.4 (the slab is at the rim plane; the bridge is outside the wall), rings 4 to 9 depending on how far behind the nozzle the tip ring sits, hand 0 to 10 depending on the operator's side. The examples were drawn for their loads; for observation the constraint is the tube.
- **What each example changes for the observers is where a camera can be mounted, not what it can see.** The table gives a flat plane at rim height (cameras on 20 mm posts across the bore at the far-side low station); the monitor arm gives a carrier that follows the gun (a gun-borne eye, eyes-01); rings give nothing to mount on and put a ring in the sight lines; a hand gives a moving occluder.
- **PTZ cameras: the aim cannot be part of the measurement.** 0.1 degree is 0.86 mm at the far wall, 24 pixels at 4K and 9 degrees: 17 times a 0.05 mm dot correction. An AI iterating for days needs a picture that carries its own reference (two features in one frame, the tube's diameter as the ruler); the PTZ is a moving window. The AI's independent judge (trials-05, eyes-07) must not be the camera closing the loop, or the loop's bias is invisible to it (eyes-01 finding 4).
- **The automated setup's first measurement is not of the gun.** Measure the tube, gun-free, at loading (eyes-16): the plate seat depth is what every motor stage in Derek's vision is waiting for.

### 8. Borrowed

- room-06's self-calibration machinery (`cdpr-core.mjs`, the ridge prior, the fit) reused unchanged to compare observation types (eyes-13).
- room-05's A/B camera pair as the spot camera and the nozzle-height camera (eyes-13).
- room-03's geometry, numbers and its (1 + d/Lt) play formula, extended with the beam bend (eyes-14).
- freedom-02's monitor-arm geometry, freedom-01's ring and bungee positions, room-01's table (slab, bridge at x = 100, post and arm) as occluders (eyes-15).
- trials-03: the spot's size gives standoff, another along-the-beam cue (weaker than a nozzle-height camera).
- use-03's presetter as the place the tube measurement happens (eyes-16); trials-05's calibration board as the surface in the spot experiment; datum-05's tags for the plate's lateral offset (second look).
- room-07's roll-up: an observer-noise row belongs in it.

### 9. Kit notes for the coordinator

- `markVisibility` with the default eps on a point on the axis of a thin part (the nozzle tip) reads blocked by the part's own skin. room-05's camera B is one: eps 3 reads seen. Consider a note beside room-05's I/O row.
- A long `transferable` chip does not wrap: at 390 px width a chip of 55 characters or more widens the whole header and the page scrolls sideways. Four of mine did (eyes-09 in wave 1); all chips are now under 40 characters. The checker's phone warning is the way to find it.
- `app.ui.enable(id, false)` is the right way to say a control applies only to one branch of a radio; the checker then skips its no-visible-effect warning (used in eyes-15).
- Under machine load the checker's 20 s page timeout fails every scene; `explorers/eyes/calc/_check.mjs` is a copy with 300 s.

---

## Wave 3

### 10. The reply to freedom (`exchange/eyes--reply-to-freedom-w3.md`)

Freedom's exchange asked one question of each of my ideas: what is holding each of the gun's six motions while it is taken, and what pushes on each. I opened `freedom-11`, `-12`, `-13`, `-14`, read `calc/eye-support.js` and reproduced its per-newton figures before using them. What changed, in order of how much it moved me:

1. **The support I drew was a symbol.** One elastic at 13° above horizontal carries the gun's weight only at about 53 N of tension, and one line to one lug is a ball joint. Fixing the drawing (vertical elastics from an overhead arm; a swing arm and guide rod) forced the real question, which is what holds the beam's turn, and that showed the eye's two numbers are held while the beam turns 1.3° per newton (elastic) or 0.02° (rigid base). The scene now has the pull slider and three supports.
2. **One fan leaves one turn blind, always.** Their question (do the two slopes give pitch and roll?) turned into a count: a straight corner lets a camera observe five numbers of the pose, one fan gives four, the spot adds nothing about the turns. Which turn is blind depends on the fan's roll (at 0 it is the turn about the radial axis); gravity (0.3°) or a crossed second fan (all five to about 0.1°) closes it. Their 0.35 mm / 7 px per degree was 6 times too large for this geometry (the camera sees the line obliquely: 0.2° of image angle per degree of tilt): it is fit precision, not shift, that makes 0.15° readable. My first calc runs showed NaN and a wrong "blind" for the vertical-axis turn until I wrote the Fisher matrix in (mm, degree) units and used an eigen-decomposition; the marginal sigma from a naive inverse of a near-singular matrix had hidden it.
3. **My own scene had a control that did not behave.** The fan plane was recomputed from world +X each pose, so it followed the gun's rotation. It only came out when I added a tilt. Fixed: fixed in the gun frame.
4. **A dry turn taken idle does not contain a step.** The scene now has a bead-start step, a dry-turn state and a mismatch slider (idle: rms 0.41 with a 0.6 mm step; weld state: 0.05). Making the eye at the dot a real loop with a lag changed the "at the dot" numbers only slightly (0.10 rms).
5. **Span from a nudge, zero from a contact** (eyes-04): the nudge works in principle and at the scene's noise needs a 3 to 6 mm step and about 16 repeats; a zero error is worse than a gain error (1.5 fF, three times the chip's noise, is 1 mm); the plate-only pair has no radial information at all (not a fold). My first noisy calibration run gave 20 to 40 mm errors because it fitted one gain per pad and the small-slope pads blew up: pooled gains for the wall pair and the plate pair fixed it.
6. **The stick-slip sweep** (eyes-06): a new stick slider and a stop-and-look switch (stick 0.8 mm: break error +0.22 mm continuous, +0.01 mm paired with the axis's real position).

### 11. The new direction: the hand supplies the motion, software supplies feedback or resistance

What I tried and where it went. The region already had freedom-14 (a force on the gun through a soft anchor), borrowed-19 (a knob whose torque is a program) and use-06 and borrowed-03 (advice on a screen or a tone). From my framing the gap was not another actuator; it was **what the sensor has to know, how fresh, and what a wrong estimate does**, channel by channel. Three things came out.

1. **The estimate a wall or cue needs is the seam in the gun frame, not the gun in the world.** An encoded arm knows where the gun is to about 15 mm with cheap magnetic encoders (borrowed-03's own number); tags or draw-wires give 0.06 to 0.21 mm at the dot. Only the eye at the dot (0.02 to 0.05 mm) can serve a 0.1 mm band; the arm's or slide's encoders supply only the direction of motion.
2. **A brake is a different kind of assist from a pull.** A passive wall cannot push the gun the wrong way; a wrong estimate can stop a good move but not throw the gun off the seam. Its refusal is unmistakable (a stop, 2 N to get through) where a gentle wrong pull (30 mN for a 0.3 mm bias at 0.15 N/mm) is too small to feel on a held gun and too small to veto. And a channel that resists lets the hand disagree, so **the override is data**: the mean disagreement is the eye's bias (if the hand aims at the true seam), to 0.1/√n mm; about 4 pushes show a 0.1 mm bias. What it cannot do is tell the eye's bias from the hand's.
3. **Every channel has to degrade to no channel.** Frozen, a bar looks live, a spring keeps pulling, and a brake becomes a one-way valve (the scene reproduces it: moves toward the frozen value are free, away refused, forever). Blind, a cue must go dark with a mark (not silent, not the last value), and the physical ones must fail toward free. Latency is millimetres crossed (speed × delay): at 3 mm/s a brake with 78 ms crosses 0.24 mm (more than the 0.1 mm band), a light 0.75 mm (mostly the operator's own 200 ms).

The scene of eyes-17 is 3D because the arrangement matters: where the bar sits on the shell against the operator's line of sight (from 150° to 210° round the tube, 250 mm above the rim, the operator sees the dot and the bar at 3° to 13° of each other; from the gun's own side the wall hides the dot), and where the camera stands decides when the layer goes blind. The lens eyes-18 is 2D because it is arithmetic. What failed: my first eyes-17 view was unreadable (three insets, badges, a stage and a friction arm in an 850 × 480 stage); I moved the view, shrank the insets, enlarged the LEDs and put the wall's geometry into a small SVG panel at the scale of the error (0.1 mm is sub-pixel in a 1 m scene, so a 3D picture cannot show it). I tried a per-joint brake on the encoded arm and left it undrawn: a joint's brake resists the radial and the tangential motion the joint makes at the dot, and a redundant arm lets the hand's force find another path.

### 12. The scenes as Derek will meet them (Part C)

I opened all twelve with `calc/_audit.mjs` (meta, controls with their kinds, sections, a desktop and a 390 px screenshot each) and looked at each as a stranger. Fixed: scenes that are lenses now say so in their tags (eyes-02, 09, 11, 13, 14, 15, 16, 18); eyes-11 opened on a close-up whose table covered the drawing and now opens on a view with the tube to the right; eyes-04 opened on a map with almost no good region (6 mm pads 20 mm back) and now opens on the closest pads the shell allows; controls that had no visible effect in the opening state are greyed by `app.ui.enable` (eyes-09's mismatch, eyes-17's bias, eyes-18's fault-specific sliders); chips longer than 40 characters widened the phone page (eyes-01, 18: fixed). Left as they are: eyes-03 has only scene-edit controls (moving the cube and the cameras is the mechanism); eyes-13 opens on a close-up of the gun (the dashed beam line and both cameras are in it).

### 13. Kit notes for the coordinator (wave 3)

- `WK.svg(tag, attrs, ...kids)` takes Nodes only as children: a string child throws `parameter 1 is not of type 'Node'` (use the `text` attribute).
- A panel id (`app.ui.panel({id})`) and a control id both become `data-wk-id` / `data-wk-panel` attributes; a panel id equal to a control id ('pose') made my own DOM queries pick the wrong element. Panels are `[data-wk-panel=id]`.
- `app.ui.reset` is looked up when the Reset button is clicked, so a scene with state that is not a control (the gun's position after a brake blocked it) can wrap it: `const base = app.ui.reset; app.ui.reset = function () { ...; base(); }`.
- `check-scene` compares frames pixel-wise: a millimetre-scale change in a metre-scale 3D scene is sub-pixel and reads as "no visible effect"; giving the affected part a role change (a pad turning red while it slips) or greying a control that has no effect in the current state (`app.ui.enable`) fixes the warning honestly.
- Per-LED colours: a `THREE.MeshBasicMaterial` per LED (not the shared `WK.mat`) with `.color.copy(WK.color(hex))`.
- Element screenshots of a panel inside the controls column come out wrong when the column scrolls; float the panel with `position: fixed` before shooting.
- Operator/observer insets can be placed with `position: () => Vector3`; `markVisibility` then answers "can this eye see the bar" for a moving station.

## Open threads

- **For Derek's eyes (each cheap):** (1) a second red spot on the wall when the dot is a few mm short of it (eyes-06b); (2) the dot seen along the tangent on a sawn half-tube (eyes-07); (3) whether the corner line shows to a phone at 10 cm from the nozzle past the wire, and whether a green line looks like a kink to his own eye from where he stands (eyes-01, eyes-17); (4) whether the yellow Ready LED changes when the nozzle touches the tube with the laser off (eyes-05); (5) what the gun-end of the work-contact circuit is; (6) plate seat depth on a dozen tubes (rooms 01, 05, 09, eyes-16); (7) a phone photo from across the bore at 10 to 15 degrees above the rim: is the plate-wall corner a clean edge on stainless (eyes-16); (8) with the trigger held, does the red dot stay on (eyes-14, room-08); (9) a photo of the dot on the plate at 30 cm: how big is the spot, does it centroid (eyes-13); (10) which side does he stand and which hand holds the gun (eyes-15, room-08, eyes-17); (11) a phone flash beside the lens looking into the corner: is there a bright band on the plate next to the wall; (12) **new:** the umbilical's pull along and across its exit at three poses with a spring scale, and whether the support or shell moves when the wire jogs, the gas opens or emitting starts (a dial gauge on the shell, laser disabled): the numbers every support scene has as a slider (eyes-01, eyes-09, eyes-11b); (13) **new:** how far a relaxed hand yields per newton at the grip; whether his hand slows or stops when the gun resists; which eyewear he wears and whether it passes a green or an amber LED near the nozzle; a phone video of the dot against the corner during a real hand-held bead (speed, tremor, how it steers) (eyes-17, eyes-18); (14) **new:** whether a steel ball at a fraction of a newton marks the inside of a 316L bore (eyes-05, freedom-12).
- **Not built, with reasons:** (a) a scene on glare and coaxial light in the corner (waits for item 11; what the picture looks like depends on how specular the stainless is); (b) a per-joint brake on the encoded arm (borrowed-03) for eyes-17: needs the Jacobian from joint angles to the eye's error, which could be learned by nudging each joint and reading the eye, and a redundant arm lets the hand's force find another path; (c) tags in place of draw-wire encoders on the pose logger (freedom-09), named, not drawn: neither is fine enough for a 0.1 mm band; (d) a hand model for eyes-17 and eyes-18: the hand is a slider and a set of illustrative numbers because no hand of Derek's has been measured (freedom-14 has one, made up).
- **Other thin regions I touched but did not fill:** calibrating the observation itself (eyes-16 covers PTZ pointing and zoom scale, not camera drift or time synchronisation); a printed ruler in every frame as a standing part of every station; tone and buzz perception (the lens eyes-18 has them as rows with delays, no perception model); the line laser as the operator's guide (a green kink the eye sees as well as the camera, only a question for Derek so far).
- **Ideas whose maturity is low and worth a critic in wave 4 or 5:** eyes-19 (touch cue), eyes-10, eyes-12, the claim in eyes-14 that the moment through the ball is readable from outside, and the override-as-bias-probe of eyes-17 (its assumption is that the hand's own eye is unbiased; a critic who knows how a welder's eye through a shield actually sees a dot against a corner could break it).
- **Numbers worth another look:** the one-fan/two-fan numbers of eyes-01 assume a line found without bias and a calibrated fan plane; a hobby cross-hair's fan angles are two more unknowns. eyes-14 puts the load at the dot end of a straight cantilever. The 12-15 degree nozzle-shadow limit (wave 1) still depends on the proxy nozzle. eyes-17's clamp latency and capacity are guesses (5 N solenoid through a lever).
- **Sourcing gaps:** a narrow red band-pass at hobby prices (still unresolved); PTZ pan/tilt and zoom repeatability (no listing gives it); a data-output linear scale at hobby prices; a magnetic-particle brake or small friction clutch at hobby price on Prime (none found: spring-applied brakes are $211 and up); the brightness of an LED bar against the bead through eyewear.
- **Combination candidates for wave 4 (mine, not scored):** eyes-17's brake wall with travel-05b's soft-drive-hard-lock (a lock that is also a wall); eyes-17 with the coach loop's advice rounding (use-06); eyes-18's channel table with room-14's trigger path (a hand fires, software can only stop: the same refuse-only property); eyes-14 + borrowed-03's encoded arm (reading a hand-moved or wall-borne structure from the clean side); eyes-13 + trials-05's calibration board; eyes-15's operator-side result + use-08's flight recorder.
- **For the answer to my critics in wave 4:** read `exchange/<critic>--on--eyes-w4.md` when it appears; eyes-17, eyes-18 and eyes-19 are new and have had no critic.
