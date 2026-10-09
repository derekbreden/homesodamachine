# trials — "The machine runs trials" — notebook

Framing: the station is an instrument for many repeated dry-run experiments run by software (an AI iterating for hours or days across tubes, judging by cameras and the laser dot). Questions I keep asking: what does software command and see; what resets between trials (above all the tube swap); what makes trial N comparable to trial N+1; what does the AI learn about the rig; which partial versions exist.

Tags in numbers: [Derek] [repo] [manual] [derived] [unknown] as in `context/shared-context.md`; anything else is **illustrative**.

---

## Wave 1

### 1. The wide list (written before developing anything)

One line each. Several are deliberately silly or flawed; the flawed ones are here to be taken far enough to find their useful form. No budget screens anything.

1. **Loader-tended cell.** Everything the vision lists is motorised (XY, Z, two rolls, PTZ cameras) [Derek]; the tube swap stays a person's job. Software asks ("load tube 7"), verifies the seat, runs, asks again. The honest baseline: the trial is cheap, the swap is expensive.
2. **Pucks.** Nest + tube live together on a kinematic coupling (3 balls in 3 grooves, magnet preload, one asymmetric pair so phase is unambiguous). The swap becomes lifting one puck and dropping another; nest indicating moves to a prep stand off the rig; the puck carries an ID tag and the tube's measured seam map.
3. **The dock.** Between trials the gun-in-shell returns to a kinematic cradle. The dock is the physical "home" (re-anchors drift, hysteresis, missed steps), clears the tube for the swap, closes a contact circuit ("seated"), and — with three load cells under the seats — weighs the gun+shell+umbilical every visit, so a changed cable drag shows up as a changed reading.
4. **The dot as a touch probe.** One axis and one camera: sweep the dot across the corner and read where its image stops moving (the knee) — that is the wall's position in axis coordinates, found with light. The plate's own mirror reflection may throw a second dot up the wall that acts as a ruler.
5. **Seam map + angle-indexed replay.** Revolution 1 records the seam's r(θ) and z(θ) with the judge; later revolutions replay the map as feed-forward on a small follower axis keyed to the rotator angle. If the follower is under the tube (a tiny XY stage) the gun side needs no actuator at all. Consequence: tube seating becomes a range requirement, not a precision one, and the manual indicating step could go.
6. **Artefact ladder.** Swap the workpiece, not the machine: calibration board -> corner coupon -> notch tube (a band-sawed scrap with a window in the wall) -> printed "zoo" tube with designed errors -> real 316L tube. Each rung isolates one difficulty and has a different ground truth.
7. **Mule gun.** A printed dummy in the scanned shell: same envelope, ballast to the real mass, a 650 nm laser module at the real dot position, an IMU, a switch-tipped nozzle, a dummy umbilical. The AI can run overnight, crash, and touch surfaces with it; the real gun only comes out to confirm.
8. **Tube zoo.** A population of printed corner analogues with dimensional errors put in on purpose (plate depth, plate offset, ovality, tilt) so the AI learns the rig against known ground truth, including cases worse than a real tube. Blind to glare, so it tests geometry, not vision.
9. **Human-labelled jog.** Command only, no judge: motors move the dot; Derek watches the dot and taps a keypad (good / +/- nudge). The taps become labels; a camera judge is trained against them, then takes over with occasional human spot checks.
10. **A yardstick for any support.** Observe-only: the station judges whatever holds the gun — hand, monitor arm, rings on bungees, gantry — with the same tube, camera and dot log, so different arrangements can be compared by the same instrument.
11. **Encoded manual axes.** Hand-driven stages with digital scales or magnetic encoders; software commands nothing but reads every knob, and the AI coaches ("up 0.3 mm") and logs. Partial version: observe the hands.
12. **Tool-changing gantry swaps the tubes.** The same positioner that carries the gun parks it in the dock, picks up a gripper, exchanges pucks from a rack, and picks the gun up again. Enables unattended overnight runs. Heavy; take it far enough to see what is real.
13. **Pivot calibration of the dot.** Tilt the gun about a supposed pivot while its dot sits on a board; the wander of the dot on the board says where the dot really is in the shell frame (tool-centre calibration as used for tracked surgical tools).
14. **Wire-touch / contact sense.** The gun's interlock circuit and the wire could be used as a touch probe (continuity to the tube). The manual gives the RS232 pins but not the protocol or the DB25 map [manual p.16], so what the laser box exposes is [unknown].
15. (silly) **Trials without repeating anything.** Run the AI on one loaded tube for hundreds of poses and never swap: the swap noise is then a separate experiment (re-seat the same tube ten times and see what the judge says).
16. (silly) **The tube moves, the gun hangs.** Rotator on a small XY stage; the gun on a passive support; the software steers the tube under the dot. Same fine positioning, all the actuators on the workpiece side.

### 2. What I chose to develop (and why these)

Depth, several rounds: **2 Pucks**, **3 The dock**, **4 The dot as a touch probe**, **5 Seam map + replay** (they connect: the puck carries the map, the dock re-homes, the probe finds the seam, the map replays).
Developed, one or two rounds and a scene: **6 Artefact ladder**, **7 Mule gun**, **12 Tool-changing gantry**.
Idea files without a scene yet (short): 1, 8, 9, 10/11, 13, 14.

(Everything after this line is the log of the work, appended as it happens.)

### 3. Ids for the wide list

1 -> trials-08-loader-tended-cell · 2 -> trials-01-puck-swap (+ 01b nest-as-puck) · 3 -> trials-02-dock-reset · 4 -> trials-03-dot-touch-probe · 5 -> trials-04-seam-map-replay (+ 04b follower-under-tube) · 6 -> trials-05-artefact-ladder · 7 -> trials-06-mule-gun · 8 -> trials-09-tube-zoo · 9 -> trials-10-human-labelled-jog · 10 -> trials-11-arrangement-yardstick · 11 -> trials-12-encoded-manual-axes · 12 -> trials-07-toolchange-swap · 13 -> trials-13-pivot-calibration · 14 -> trials-14-contact-sense · 15 -> trials-15-one-tube-many-poses · 16 -> trials-16-tube-moves-gun-hangs · plus trials-17-trial-card (the table that answers "what makes trial N comparable to N+1").

Scenes built (all pass `check-scene --shot --exercise`; 390 px phone width checked for 02 and 03): trials-01-puck-swap (3D), trials-02-dock-reset (plan + elevation SVG), trials-03-dot-touch-probe (2D section SVG with two proposed camera views and sweep plots), trials-04-seam-map-replay (strip charts and a polar view), trials-05-artefact-ladder (3D with two judge insets), trials-06-mule-gun (3D exploded instruments), trials-07-toolchange-swap (plan with a coupling-load check). They differ in representation: three are 3D scenes with different jobs (a swap, a family of workpieces, an exploded instrument set), four are 2D (section geometry, time series, plan and elevation, plan and a load bar).

### 4. Rounds, in the order they happened

**Dot as touch probe (deepest geometry).** Round 1: sweep the gun radially, watch the dot cross the seam. First error of mine, caught in the code and then in the numbers: I first assumed a beam from outside the bore and wrote a rim-shadow condition for it. Redoing the geometry with the reference scene's inset (beam from inside, over the plate) removed the shadow from the primary beam and moved it to the *outside* case: beyond 14.6 degrees from vertical the corner cannot be reached from outside at all (1.65 wall, 6.35 recess: derived). Round 2: the knee I estimated (0.71 mm) was not the truth I compared against (1.20 mm): the knee depends on height by tan(beta) per mm, so radius and height are confounded on the plate. That produced the second signal (spot size, height alone) and the combined two-sweep estimate. Round 3: the plate as a mirror throws the dot up the wall at a cot(beta): a one-frame ruler, but only while the dot is within 3.97 mm of the seam and only if camera B can see past the gun body. The scene now lets the reader move camera B and watch it get blocked.

**Puck and swap.** Round 1: kinematic seats, prep stand. Round 2: I computed utilisation and found my own first claim (the puck buys throughput) was weak: with 20 trials per load the swap is a small fraction. The honest reasons are population coverage (many different tubes), repeatability as a measurement, and the puck carrying the index, the phase and the identity. Round 3: the coupling does not fix the tube in the nest; the scene has a slider for that. Round 4: derived rotating mass from the tube geometry (0.79 kg tube plus 0.61 kg plate = 1.40 kg) and it matched the rig doc: those masses are exactly the tube and plates. Round 5: the rotator has no index sensor (turned-so-far degrees only), so the puck's magnet plus a Hall sensor supplies a zero, which the seam map needs. Round 6: a smaller branch (01b) keeps the present nest and only replaces its screws.

**Dock.** Round 1: a cradle. Round 2: the shell's body lies over the bore at the working pose, so a nearby dock puts it in the tube's lift column at the swap step; the scene draws the collision (LIMIT badge). Round 3: a weigh-in on three cells sees a sideways umbilical pull as a change in shares while the total stays constant; a single scale is blind to it (dock_scale.py). Round 4: one-sided final approach turns two friction clusters into one calibratable offset. Round 5: three docks are three known points (07).

**Seam map.** Round 1: learn per-angle wobble, replay. Round 2: the demand on the follower is tiny (0.03 mm/s at 1x for 0.125 mm amplitude at 15 mm/s), so it is a small slow axis; the tricky part is the map, not the motion. Round 3: only radial and vertical matter; tangential slides. Round 4: a tube-side X slide follows radial only, so the height error stays; the scene's radio shows it. Round 5 (map_learning.py): more than about four learning revolutions buys little; the judge's noise sets the floor. Round 6: maps do not survive a re-seat; the puck's tag carries the key.

**Artefact ladder, mule, toolchanger** got a round or two each; see their idea files. Notable: the IMU sees two of the three rotations (checked by setting the vertical-axis dial and reading pitch and roll: unchanged); the moment check shows magnets alone do not hold a 1.5 kg gun on a 200 mm lever.

### 5. Things that changed my mind

- The swap does not need to be fast to matter; it needs to be repeatable and to carry context. (swap_budget.py)
- The gun's real requirement can come from Derek's hands: measure a competent hold with the judge and compare arrangements with the same instrument (trials-11). That avoids inheriting tolerances.
- The dot has more than one signal (position, visible fraction, size, reflection). Most of what the AI needs from the corner may be in those.
- The manual gives RS232 pins but not a protocol; whether the dot can be blinked is open, and the mule can do it by construction.

### 6. Convergence warnings for the coordinator

- Judge cameras and line of sight to the dot: `eyes`, `datum` will draw similar cameras. My contribution is the *judge separated from the controller* and the notch tube as ground truth.
- Homing/dock and kinematic seats: `use`, `room`, `borrowed` may propose a dock or a zero-point plate. Mine differs by the weigh-in and the swap interlock, and it uses the shell's attitude at the working pose.
- Seam following: `travel`, `datum` may propose following the rim or plate. Mine keys a map to the rotator angle and only follows r and z.
- A tube-side stage (04b, 16) overlaps `travel`.

### 7. Kit issues

- The kit's `app.badge` shows at the top centre of a custom stage and overlaps custom content; scenes that use it (02) have overlapping captions at times.
- `check-scene` warns "no visible effect" for controls that matter only in one state (zoo sliders on the real rung; the swap "who" radio at rest); I disabled or made them visible.
- `WK.inset.markVisibility` ignores hits within 4 mm of the target by default: a dot on a wall looks visible from outside. I pass `{eps: 0.8}` in the ladder scene. That default deserves a note in kit/README.
- `THREE.LatheGeometry` angles after the kit's `rotateX(pi/2)` are offset by 90 degrees from +X; my notch tube depends on it.
- The scratchpad directory is shared between explorers: another explorer overwrote my helper script once. I moved mine to `scratchpad/trials/`.
- `summary.md` could not be written by the tool in this session (the harness refuses files named as reports); the inventory is in section 8 of this notebook and in the structured return.

### 8. Arrangements held (the summary the coordinator asked for, kept here)

Deep: 01 puck-swap, 02 dock-reset, 03 dot-touch-probe, 04 seam-map-replay. Developed: 05 artefact-ladder, 06 mule-gun. Rough: 07 toolchange-swap. Notes: 01b nest-as-puck, 04b follower-under-tube, 08 loader-tended-cell, 09 tube-zoo, 10 human-labelled-jog, 11 arrangement-yardstick, 12 encoded-manual-axes, 13 pivot-calibration, 14 contact-sense, 15 one-tube-many-poses, 16 tube-moves-gun-hangs, 17 trial-card. Files: `ideas/<id>.md`; calc scripts `calc/dot_probe.py`, `seam_rates.py`, `swap_budget.py`, `dock_scale.py`, `pivot_cal.py`, `map_learning.py`; sourcing `sourcing/trials.md`.

## Open threads (after wave 1)

1. **Derek's observations that would change many things at once** (one afternoon): weigh the gun and find its centre of gravity; photograph the dot on the plate at three heights and see if a second spot appears on the wall; touch the nozzle and wire to the tube with the clip on and the laser disabled and watch the lamps; lift and re-seat one tube ten times with the indicator; note how long a swap plus indicating takes.
2. **The requirement itself.** How far off the seam can the dot be, and at what angle, and still make a good weld? Trials-11 proposes measuring a good hand instead of guessing.
3. **Judge camera position** that sees the dot at the corner past the gun body for every pose: unresolved in 03 and 05; `eyes` should take it.
4. **Weld-time use of the seam map**: thermal distortion, wire and gas geometry with a following dot.
5. **Real tube-to-tube variation** (length, plate seat depth, out-of-round): ten measurements would size the zoo and the follower's stroke.
6. **The laser box's RS232/DB25 interface**: can the dot be blinked, can the ready state be read?
7. **Turntable design for the seats** (01, 01b): load path through the printed turntable to the ball race.
8. **Pair candidates for wave 2**: with `eyes` (judge cameras, line of sight, the dot's signals), with `use` (the cycle steps and handovers, whose steps I drew), with `travel` (tube-side follower vs gun-side), with `datum` (a reference on the work that replaces the index magnet or the tag: the plate register hole).
9. **Wave 2 idea for me**: take a partner's arrangement (a suspension or a gantry) and run it through the yardstick, the dock and the seam map: what the trial rig would say about it.


---

## Wave 2 (observed 2026-09-29)

Partner: **borrowed**. My work on their ideas is `exchange/trials--on--borrowed-w2.md`; **datum** works on mine and leaves a file for wave 3. The machine was heavily loaded at the start (load average above 50) so `tools/check-scene.mjs` timed out at its 20 s navigation limit; I ran a copy with longer timeouts from the scratchpad (`scratchpad/trials/check-slow.mjs`, same code) and a small screenshot script that sets controls and clicks buttons (`shots.mjs`).

### 1. What I read

The digest, the kit README (1.1.0), borrowed's notebook, index, twelve idea files and eight scenes (each run through the checker, per-control shots looked at, and the states no shot shows set by script: borrowed-02 with power off, borrowed-05 after the code was read). The kit changes I use: `eps` 0.8 on visibility tests, `app.ui.panel`, `app.stageOverlay`, the persistent legend, `noVisual`.

### 2. What I chose from borrowed, and why

Five ideas: borrowed-03 (deep, stressed), borrowed-02 (deep, stressed), borrowed-10 (sketch, developed), borrowed-05 (developed) and borrowed-07 (rough). The framing asks what repeats, what resets, what the AI learns and what goes wrong overnight; each choice is where one of those questions had a number.

### 3. Things that changed my mind

- **A cheap encoder is not "a coarse pose logger" once it can be calibrated over a window.** Borrowed's conclusion (1 degree of linearity error is about 15 mm) is an absolute worst-case number at one pose. After the one touch-off the idea already has, the error across a plus or minus 15 degree hand window is 1.3 to 1.6 mm, and a fixed-point fit on 40 touches takes it to the floor set by quantisation and unread play (0.03 to 0.8 mm). I had expected the calibration to disappoint; it disappoints only through play, which nobody has measured. (calc/arm_touch_cal.py)
- **The gimbal formula's biggest error is not on its sliders.** A cradle error of 1 mm costs 0.54 mm rms at plus or minus 30 degrees, three times the angle-error term. And a fixed-point trial cannot see the component along the beam: it moves the nozzle along its own beam. I had first written the fit as recovering all three components (0.6 mm stuck in the results until I saw that the missing 0.6 was exactly the along-beam component of the drawn error). (calc/gimbal_fixed_point.py)
- **A pointer 16 mm from the dot is 12 times finer than the same servo 100 mm away** (0.068 against 0.21 mm per 0.1 degree step, with reach as the price). Borrowed-10 quotes the resolution at 100 mm because the pointer sits where a person would mount it; the mule's geometry puts the nose at 16 mm.
- **A sweep step coarser than the dot is not a sweep.** My first scene's 61-point sweep had 0.55 mm between points, about the dot's footprint, and found the knee 0.3 mm off. Coarse then fine is what the software does; the scene now does it.
- **The lash cancels only from one side.** I had computed the knee error as an error; it is a constant the labels share when they are approached the same way the sweep went. That is the unidirectional final approach of trials-02 showing up in a new place.
- **The centroid at the seam pixel is unreachable.** Borrowed-05's guide target needs a visible width of zero; the loop parks half a spot into the wall (0.26 mm) or hunts at the edge. I would not have seen it without drawing the clipped dot.
- **The tonearm's answer depends on a number the scene fixes.** The recess is one slider; it is a function of angle. Break-even is 0.135 degrees of rim-to-plate parallelism.

### 4. Borrowed

Pieces I use from the digest, and where.

- **datum-05 fiducial collar (tags on the work read by a camera):** a ring of sixteen tags on the puck flange, read by the judge camera, replaces the Hall sensor and the NFC reader for phase and identity in trials-01 (a radio in the scene). Its own lever-arm rule limits it: the ring is 147 mm below the seam, good for angle and name, not for position.
- **use-02 swing head (a float that hands over the load; seat amplification):** in trials-02, the float answers my open item about kinematic seats on soft load cells, and the amplification (about 5 times at a 30 mm contact circle and a dot 130 mm away) sizes a dock's repeatability at the dot.
- **eyes-06b corner mirror (the dot and its reflection merge on the corner):** a null-type criterion for the knee, in trials-03.
- **datum-04 corner follower (a ball in the corner):** an independent touch truth on the real tube for the mule (trials-06), and the stylus of a tonearm with two pivots (exchange section 5).
- **room-05 drawer cell:** the tube swap as a drawer, in trials-08.
- **use-12 golden tube:** a row in the trial card (trials-17), next to two new rows (camera drift, calibration id).
- **borrowed-05 guide star and borrowed-06 swing offset:** the loop of trials-20, and the third steering type of trials-18 (the mule rehearses the interface before the real head's range is known).
- **borrowed-02's `dot = C - t g` and borrowed-03's arm:** the two arrangements trials-19 calibrates; **borrowed-10's pointer** is the actuator of trials-18.
- **eyes-12 dot lattice:** trials-18's pointer is the lattice positioner with no mass.
- Not used, considered: freedom-05, datum-02, travel-02 (the same map-replay as trials-04; I keep mine); use-11 setup gauge (the same as the notch tube).

Scenes revised with a borrowed piece: `trials-01-puck-swap` (tag ring option).

### 5. My own ideas this wave

The digest lists thin regions; I worked in two. **Calibrating the observation itself** (hand-eye calibration, camera drift, the judge's own error): trials-18 (a steerable ground truth: labelled offsets at the real corner in the real light, a golden dot for drift, camera-to-gun-frame for free) and trials-19 (calibrating the pose-reporting arrangement with the same board). **The hand supplying motion while software supplies guidance** appears in trials-19's arm branch: the hand takes an assigned list of orientations. I did not add variants of the crowded regions (map replay, touch and probe, docks); trials-20 is a repair to another explorer's loop, not a new region.

New: **trials-18-steerable-mule**, **trials-19-fixed-point-cal**, **trials-20-guide-at-the-knee** and, smaller, **trials-21-rim-vs-seam** (the tonearm's break-even, a rough scene); scenes for each; calc scripts `arm_touch_cal.py`, `gimbal_fixed_point.py`, `guide_at_knee.py`; sourcing (pan/tilt kits, micro servos, a class 2 red module, a galvo set, 14-bit encoders, steppers).

### 6. Kit and tooling issues

- `tools/check-scene.mjs` navigation timeout (20 s) and ready timeout (15 s) fail when the machine is loaded (load average above 50); a copy with 120 s and 90 s works. Worth an environment variable.
- `app.badge` on a custom stage covers custom content at the top (as noted in wave 1); the reach badge in trials-18 uses it sparingly.
- SVG panels drawn with a fixed viewBox scale their text with the column width: a 520-wide viewBox in an 810 px column has 1.5 times the text size. I used per-panel viewBox widths (800 for the wide panels).
- `window.__setControl` on a `select` control takes the option value; the checker's DOM pass also clicks every option, so a fit or heavy computation behind a control must be debounced (trials-19 debounces 260 ms) or the exercise queues them.
- The Chrome `find` tool fails on a very large Amazon results page (a prompt-length error); `get_page_text` works but is mostly boilerplate.
- The kit's `app.inset.add` can be added and removed at run time (`.remove()`); trials-01 does it for the tag-ring judge camera.

## Wave 3 (observed 2026-09-29)

Partner: **datum**, whose critique of my ideas is `exchange/datum--on--trials-w2.md`; my answer is `exchange/trials--reply-to-datum-w3.md`. The new direction the coordinator named for me: calibrating the observation itself.

### 1. What I read

The datum exchange; datum's five scenes that name mine (`datum-14` seam owners, `datum-15` dock noticing, `datum-17` yardstick on the twin, `datum-19` plate as target, `datum-20` dot and wire) and `datum-16` (the crown), with their idea files; the wave 2 digest; kit 1.1.0; my own notes and all eleven of my scenes, each opened as someone who has not read the notes (checker, screenshots, control kinds, a NaN and error scan of every control at its extremes, a phone-width pass).

### 2. Answering the critique (what I did)

Details are in the reply file. In one line each:
- **`trials-04`:** revised in place. The scene scored its replay against the simulation's truth, which a rig never has; it now shows the true error beside what the judge reads, with a bias slider, a touch check (K azimuths), a map-source radio and a passive-support radio with the follower's travel. `calc/map_bias_touch.py`.
- **`trials-01`:** the keys question answered with a seat-pattern radio and a brute-force (`calc/seat_sets.py`): ports modulo 180 still separate three symmetric seatings; 120 degrees hides harmonic 3; two groove sets 70 degrees apart beat both.
- **`trials-02`:** revised the claim (the dock re-anchors the shell, not the trial), adopted the coupon (a toggle), moved the better coupon to a puck at the trial's station.
- **`trials-11`:** adopted the combination: the twin and the notch are pucks; the hand on the twin is the first entry.
- **`trials-14`, `trials-03`:** the wire and dot vector is `datum-20`'s; answered and kept. Camera A's line of sight revised in `trials-03` (`calc/knee_view_angle.py`): the knee is parallax-free, the rim edge is not.
- **`trials-16`, `trials-04b`:** revised through the support radio; a crown is the stiff support.
- **`trials-17`:** rows added. **`trials-06`:** the mule's wire stub recorded as an option.

### 3. The new direction

Three ideas, one physical, two lenses. **`trials-22-reference-pucks`** (deep, 3D): the artefact ladder made into pucks on the same kinematic seats as any tube, so the board's frame is the tube's frame, its rim ring and ports let the same fit run on the board and a tube, and a board-derived camera pose turns the next tube's rim edge into a seat-depth gauge. **`trials-23-frame-clock`** (developed): time as a calibration. **`trials-24-calibration-graph`** (developed): the ledger of calibrations as a graph of what leans on what, with four arrangements from other explorers.

What I tried and where it went thin. I looked for a physical arrangement for time (a slate in the frame) and found it fits only a wide camera; the close-up has no room, so the useful ones are a step test and an axis-triggered exposure. I expected the board to matter most for the camera's pose and found it matters for the seat depth of a far camera (0.26 to 0.07 mm at 450 mm) and hardly at all for a near one (0.03 mm alone at 150 mm). I expected a flat board to fail at focal length and found it does not, for the point that matters.

### 4. Things that changed my mind

- **The knee needs no calibration of the eye's pose; the error of a comparison grows with the separation of what is compared** (scale 1 per cent: 3 micrometres on the knee, 23 on the rim edge, 190 on the ports, 620 against the room; pointing costs nothing in a comparison made in one picture and 0.5 mm against the room). That came from datum's parallax point, and it is the sharpest sentence of the wave.
- **My scene of the seam map was not a scene of what the rig could know.** Scoring against the simulation's truth is the kit's own named anti-pattern; datum found it in mine. The judge reads 18 micrometres however wrong the map is.
- **Eight touches alias.** A touch check is clean only for a smooth seam (harmonics 5 and 6 fold onto 3 and 2); with tack marks in the seam the touch map is worse than the judge's until the bias is large. The hybrid is never much worse than either.
- **Lash and latency are the same shape.** Both flip sign with direction, so one sweep pair cancels both and two speeds separate them. The unidirectional approach of `trials-02` and the labels of `trials-18` were already half of this.
- **Datum's plate-as-target treats a port as a point.** A port is an 11.1 mm circle; fitted from eight edge points it makes the pose-free seat depth three times better at the same pixel noise (my Fisher model reproduces datum's 0.335 mm with ports as points).
- **My first graph made a new tube make the judge suspect.** Drawing the dependency edges showed that the geometry and the dot were fitted on the matte board, where the tube's surface does not enter; the tube's bias lives in the seam node. Fixed in the scene and the calc.

### 5. Borrowed

- `datum-15` (the coupon): the dock coupon toggle; the coupon puck. `datum-17` and `datum-10` (the clear twin): a puck. `datum-19` (rim and ports fit): the fit that runs in `trials-22` and the seam foot's image position for `trials-03`. `datum-14` (owners, touch check): `trials-04`'s judge-bias rows. `datum-20`: the vector, in `trials-14`. `datum-16` (the crown): the support radio. `eyes-13` and `trials-19`: the cage and arm numbers in `trials-24`. `borrowed-13`: the hexapod row. `room-01`/`room-15`: the gantry row.

### 6. Kit and tooling issues

- `transferable` chips in the scene header do not wrap: a long chip made the whole page scroll sideways at 390 px width (scenes 01, 22, 23, 24) until I shortened them. The kit could wrap them.
- `app.ui.panel` cards are appended after the control groups whatever the order of creation; key numbers I want beside the picture go in `app.stageOverlay` instead.
- A camera inset looking straight down needs an explicit `up` (the default +Z is degenerate): `app.inset.add({ up: V(0,1,0) })`.
- A custom stage's `minWidth: 820` scrolls sideways inside the stage on a phone: fine, but a chart with a fixed viewBox is small until then.
- `WK.lineOfSight` on a hundred and sixty points is fast enough to run on every control change; used in trials-22 to count the fiducials the gun hides.
- One batch of scripted control changes on `trials-04` printed NaN in its table and could not be reproduced afterwards (the same sequences ran clean twice, and a NaN scan of every control at its extremes is clean); the cause was not found. Recorded in case it returns.
- The Chrome group already held another explorer's tab; I worked in my own and closed it.

### 7. Arrangements held

Deep: 01, 02, 03, 04, 22. Developed: 05, 06, 18, 19, 20, 23, 24. Rough: 07, 21 (with a section sketch now). Notes and lenses: 01b, 04b, 08 to 17. See `index.md`.

## Open threads

1. **Derek's afternoon, all waves:** weigh the gun and find its centre of mass; a phone photograph of the bore from 300 and 150 mm above (are the rim circles and ports sharp, does the wall show a strip: trials-22, trials-03, and datum-19's question); the dot at the corner one millimetre short and on the seam (trials-20); does the laser box blink its dot, and what do the lamps do on touching the nozzle and wire with the clip on and the laser disabled (trials-14, trials-06); ten lifts and re-seats of a puck-shaped print with the indicator on the flange (trials-01, trials-22); indicate a tube, turn it 100 degrees in its nest, indicate again (trials-04, trials-01); two indicators on a tube over one revolution (borrowed-07, trials-21); a printed sheet against calipers (trials-22); a phone at 240 fps on a display and the camera preview (trials-23); the play of an arm joint (trials-19); the nozzle region of the scan (trials-18).
2. **Does the camera judge have an angle-locked bias?** Everything in `trials-04`, `datum-14` and `datum-17` is conditional on it. The indicator turn-in-the-nest test and a few touches would put a number on it.
3. **Whether printed seats hold 10 micrometres per landing over hundreds of swaps.** The reference pucks and the map keys both stand on it.
4. **The requirement itself** (how far off the seam the dot can be and still weld well) and the weld-time use of any of this: the eye is blind while the laser is on, so what the eye calibrated must be held by the arrangement through that interval. Not a dry-run quantity.
5. **What a suspect calibration is trusted for.** `trials-24` marks stale and suspect; the thresholds that make a check pass and Derek's rule for a weld on a suspect calibration are unset.
6. **A camera with a trigger input, and the rotator ESP32's timing.** `trials-23` prefers an axis-triggered exposure; the listed OV9281 module claims a trigger in its title and nothing is checked.
7. **The along-beam component** (standoff) still cannot be seen by a board; spot size is its sensor and `trials-03` has only an illustrative model. The four arrangements in `trials-24` each carry it.
8. **Pair candidates for wave 4:** eyes for the judge's real noise and bias on stainless and the seam foot's image position (trials-03, trials-22); use for the states of an unattended cycle with reference pucks in it (trials-22, trials-24); freedom for the gun's static offset under the cable and the crown's statics behind the support radio (trials-04); travel for what a tube-side follower's stroke must be.
9. **What I owe the others:** if a partner names a reading or a calibration in my ledger that leans on something I missed, the graph's edges are one reading and are meant to be redrawn.
