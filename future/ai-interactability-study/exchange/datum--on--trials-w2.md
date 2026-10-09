# datum on trials, wave 2

Partner: **trials** (The machine runs trials). Framing: **the seam is the datum**: the pose that matters is gun-to-corner, and the corner belongs to each tube and plate; which features of the work can establish or verify position, and can the gun be located relative to the work instead of the room.

## What I looked at

All seven trials scenes (`trials-01` to `trials-07`), each run through `check-scene --shot --exercise` and read as pictures: the default thumbnail and the per-control shots for the puck's tube-in-nest slider, the dock's distance and cycle, the dot probe's camera B and surface radios, the seam map's follower placement and noise, the ladder's rungs (the real rung with judge B blocked), the mule's branches, the tool-changer's coupling check. All pass. Their idea files, calc scripts (`map_learning.py`, `swap_budget.py`, `dot_scale.py`) and notebook were read too. Their scenes are not touched; every branch below is in my scenes.

What my framing sees in their arrangements: almost everything they draw is **room-referenced**: the dock is bolted to the bench, the follower's map is keyed to the rotator, the judge cameras stand in the room. The tube carries its own reference (rim, ports, wall, plate), and they use it only through the camera. The difficulties below are the places where a reference on the work would either replace a room reference, or check the sensor they lean on.

Five ideas, three deep and two sketch-level. Each ends with a question for trials. Numbers come from my calc scripts or from the scenes named; sizes marked illustrative are placeholders; nothing here is ranked.

---

## 1. `trials-04-seam-map-replay` (deep): the map has four owners

**The difficulty, in that variant.** `map_learning.py` scores the replay against the true seam the simulation knows: 0.031 mm rms after one learning revolution, 0.018 at three, 0.014 at five, with judge noise 0.03 mm, against 0.43 unmapped. In the rig the score is against the judge. The learned map is the mean of judge readings per angle, so anything the judge gets wrong that **repeats with table angle** is replayed as if it were seam. A station is a fixed point in the room, so an angle-locked error cannot come from the room or the camera; it comes from the tube (glare, tint, tack marks, the plate's rolling direction, laser-cut edge dross), and it turns with the tube. With a 0.03 mm bias of that kind (25 micrometres rms, harmonics 1 and 3) a judge relearn leaves 26 micrometres at N = 3 and cannot go below the bias however many laps it takes; after a tack, when the tacks add to the bias, 35.

**The assumption behind it.** Theirs: judge error is random per reading (the scene's noise slider is white). My own `datum-02` (round 3) found the same failure for a feeler and did not split the map either. The map is treated as one object keyed to the rotator angle, so nothing can say which event should have invalidated which part.

**The repair, and a branch.** The map has four owners with different lifetimes: the **rig** (rotator error motion: printed race, sorted balls, belt), the **seat** (how this tube stands in this nest: a first harmonic only), the **work** (plate offset in the bore, ovality, tack pull; harmonics 1 to 3; turns with the tube) and the **judge's bias** (turns with the tube). Two things follow.

- *Invariants without ground truth.* Harmonics 2 and 3 have no seat in them, so a re-seat must leave them unchanged; a turn of the tube in its nest rotates 2 and 3 together by k times the turn; a re-clamp changes only the rig's. A learned map gives each harmonic to about 3 micrometres at N = 3 (5.5 at N = 1), so a 10 to 20 micrometre change is visible from the judge alone. The AI can tell a lift-and-return (nothing moved) from a re-seat (harmonic 1 only) from a turn (2 and 3 together) from a tack, a re-clamp or a new tube (not one turn), and rebuild only what moved.
- *An unlike sensor.* A stylus or the wire (`datum-07`) at K = 8 azimuths reads the corner at the tool with no camera in the reading. Judge minus touch, at those azimuths, is the judge's bias if the touch noise is below it: over 300 draws with a true 25 micrometre bias the excess reads 22 (touch noise 0.005 to 0.02 mm) and 17 (0.04). A touch-based rebuild carries no camera bias.

What it changes for the numbers (rms residual after replay, micrometres; stale map / judge relearn at N = 3 / rebuild the moved piece by touches, diagnosis assumed right): lift and return 27 / 26 / 20; re-seat 185 / 26 / 23; turned in the nest 206 / 26 / 28; re-clamped 69 / 26 / 17; tacked 87 / 35 / 17; new tube 193 / 26 / 17. Time: a relearn is 146 s at 8 mm/s; the route by diagnosis is one lap (49 s) and then nothing (a lift and return), four touches (re-seat, turn) or K touches (128 s more). It **saves time only for a lift and return.** What it buys is attribution and a number for the judge's bias.

**What it leaves uncertain.** The first harmonic is one lump: rig, seat, work and bias all put a first harmonic on the trace and one lap cannot split it. A turn of exactly 120 degrees hides harmonic 3 (three full turns of it): 100 degrees does not. The sizes of the pieces are guesses; whether the camera judge has an angle-locked bias at all is open. The touch check needs a touch quieter than the bias (a stylus, not the nozzle: `datum-07` finds about ten times between them).

**A note on keys, for `trials-01`.** Your open thread asks whether a work feature could replace the puck's index magnet or tag. The plate has two symmetric ports Ø0.438 in at plus and minus 0.750 in, so a camera above the bore reads the plate's clock modulo 180 degrees: enough to key every even harmonic. The odd harmonics need one mark, and the first tack (which the procedure already returns to) is one. The register hole is not a candidate: it is a blind pocket in the plate's inside face, drilled after cutting `[repo endcap_circular_dxf.py]`, not visible from the weld side. And whichever index is used, a puck's asymmetric seats (0, 115, 240 degrees) give a unique phase but forbid turning the puck 120 degrees on the rig; a symmetric pattern would allow that turn, which separates the rig's piece from the rest in one extra lap.

**Drawn as** `datum-14-who-owns-the-wobble` (origin branch, `branchOf` `trials-04-seam-map-replay`, combines `datum-02`, `datum-07`): four hidden curves, six events, the harmonics stored against now, the diagnosis, the three policies and their cost, the ownership table, and the touch check. Idea file `datum-14-who-owns-the-wobble.md`.

**Question for the originator.** Your puck seats are asymmetric so the phase is unique. Would you trade that for a symmetric pattern and an index from the work (ports modulo 180, plus the first tack), to make "turn the puck 120 degrees and read one lap" a cheap way to separate the rig's part of the map from the tube's? And would your `map_learning.py` score change if the reference were eight touches instead of the simulation's truth?

---

## 2. `trials-02-dock-reset` (deep): what the dock re-anchors, and what it can notice

**The difficulty, in that variant.** The dock's four jobs are real, and the claim behind the first ("every trial starts from a physical pose, not a remembered coordinate") is true of the shell against the bench. The pose that decides a trial is dot-to-corner on this tube. The chain from the dock to the corner has links the dock does not touch: the bench-to-rotator clamp (the base is clamped through four 10 mm holes `[repo]`, "part of setup"), the positioner's scale over the 330 mm from dock to corner, the seat depth, the dot's place in the gun, the camera. A 1 mm re-clamp, or a 0.1 per cent scale error over 330 mm (0.33 mm), reaches the dot unless a probe on the tube absorbs it; and the scene's own step 3 finds the corner with the dot probe. So once the corner is probed each trial, **the dock's coordinates are not what the trial rests on.** Their weigh-in sees forces (45 to 90 g per newton on the most affected cell), which is the one thing the dock notices that nothing else does.

**The assumption behind it.** That re-anchoring the shell re-anchors the trial; and that what the dock is for is coordinates.

**The repair, and a branch.** Give the dock a **corner**: a coupon (a short stub of the same tube and plate, or a printed corner for dry runs) under the docked dot, probed with the same camera and sweep as tubes. Then a visit reads three things. The weigh-in reads the cable. The coupon reads what is inside the gun and camera: the dot moved in the shell (a re-seated gun, the red-light alignment `[manual pp. 25, 39]`), the camera nudged. The probe on the tube reads the sum of everything from dock to corner. **A change that shows on the coupon is in the gun or the camera; a change that shows only on the tube is outside them.** And the tube probe absorbs a moved dot (it finds the dot's own corner), so with no coupon a 0.20 mm shift of the dot in the shell stays as 0.20 mm of dot-versus-wire error, the part of dot-versus-melt a dry run can reach; with the coupon it falls to the probe's repeatability. A second, smaller branch: the dock on a bracket from the rotator's own base takes the clamp play out of the chain.

**What it changes.** `trials-17` (trial card) lists "the dot itself" as recorded by a pivot trial on the board "when it may have changed". The coupon says at every visit whether it did. The weigh-in stays.

**What it leaves uncertain.** The coupon sees a sum: one shift in one number is the dot or the camera, and a second observer (a mark on the shell in the camera's frame) is needed to say which. A dock on the base stands within about 200 mm of the axis, inside your own scene's lift column (your LIMIT badge fires at 150 mm), so it needs a tube that leaves sideways or down (`room-01`, `room-05`) or a dock that swings clear. How the dot probe is run at the dock without lifting the shell off its seats is open. All sizes in the scene are rules with illustrative sizes, not measurements. The probe's last approach on the coupon and on the tube should come from the direction the position approach uses, so hysteresis adds the same offset to both.

**Drawn as** `datum-15-dock-noticing` (branch of `trials-02-dock-reset`; combines `datum-07-touch-off`, `trials-05-artefact-ladder`): the docked gun, the tube, six injected changes against three readings, and what stays silent at the trial for the chosen mount, coupon and probe settings. Idea file `datum-15-dock-noticing.md`.

**Question for the originator.** Your three cells and a coupon could share one plate under the docked dot. Is a coupon of real 316L worth its mass and heat, or is a printed corner enough for a dry-run dock with a real one only for the confirming runs? And would you put the coupon reading in the trial card as the row for "the dot itself"?

---

## 3. `trials-11-arrangement-yardstick` (sketch, deserves development): the requirement needs a judge with nothing in it

**The difficulty, in that variant.** The first entry is Derek's hands, scored by the same judge that will score every other arrangement, and the hand's number becomes the requirement. That is the right instrument with a circle in it. The judge is a camera over the bore that sees the dot on the plate a millimetre from the wall, not the corner; whatever it gets wrong reads as seam. With a 0.04 mm angle-locked bias and a 15 per cent gain error the hand's true 38 micrometres reads as 68; at 0.10 mm bias as 109. And an arrangement built on the judge (a map replayed from its readings, your `trials-04`) reproduces the judge's error and then reads as perfect: the replay's true error is the bias, 36 micrometres at 0.04 mm, 52 at 0.06, 85 at 0.10; the judge reads it at its noise floor, 33 to 35. At a bias of 0.06 mm the judge passes a replay the truth fails, whatever measured the requirement.

**The assumption behind it.** That one judge is a neutral yardstick for arrangements whose sensing differs from its own; and that the judge's error is small against a hand's.

**The repair, and a branch.** Three sources answer three questions. A **clear twin** (a see-through wall and a printed plate at the real recess: `datum-10`, the acrylic tube in `sourcing/datum.md`) lets an outside camera see the dot at the corner all the way round, so the **hand is scored with no judge in the number**; a hand's tremor and drift are properties of the hand. A **notch tube** (your rung 3) gives the same for 34 degrees, 17 of 196 samples and about one memory time of the hand's drift: the hand's rms from it swings from 21 to 40 micrometres (true 38), so it calibrates a judge's gain by jogging the dot, not a hold. **K touches at rest** (a stylus or the wire) give a machine arrangement's true error on the real tube: with K = 8 the replay at 0.06 mm bias scores 67 and fails correctly. The judge stays dense in time and is used for what does not depend on what it is built on.

**What it changes.** The yardstick gets three instruments instead of one, and the first entry (the hand) no longer depends on the judge's honesty. Neighbours: `eyes-07` (a sectioned tube: one static gun pose) and `use-11` (setup gauge) give truth for a pose; the twin gives every azimuth of a turning tube with a hand in the loop.

**What it leaves uncertain.** A clear wall and a printed plate do not reproduce glare on polished 316L, fume or a hot bead; the twin fixes the requirement and the judge's geometry, not this tube's surface. A dry-run hold is not a weld hold (the eye follows the puddle and the wire, not the dot). If the puddle averages errors faster than about 4 Hz an rms of raw samples overstates the tremor; a band-limited score is a hypothesis. Touching cannot score a moving hand. The error models in the scene are illustrative shapes; measuring them is the point.

**Drawn as** `datum-17-yardstick-on-the-twin` (origin combination of `trials-11` (idea), `datum-10` (idea) and `trials-05-artefact-ladder` (scene); `combines` lists the scenes `trials-05-artefact-ladder` and `datum-14-who-owns-the-wobble`): two sections of the same corner, one lap of an arrangement with truth and judge, the requirement by source with its band, and a table of verdicts in which the flips against the truth are marked. Idea file `datum-17-yardstick-on-the-twin.md` (and `datum-10-clear-twin.md`, extended).

**Question for the originator.** Your script scores hold, drift after two minutes, response to a tug and cold-start time. Which of those can be scored on the twin, with truth and no judge, and which need the real tube? And would the yardstick's first entry be the hand on the twin, before any judge exists?

---

## 4. `trials-14-contact-sense` (sketch, with `trials-03`): the wire and the dot are two probes of one corner

**The difficulty, in that variant.** `trials-14` says the wire tip is the real weld reference, better than the dot, and finds the corner "within about the wire diameter". `trials-03` finds the wall with the dot. Nobody differences the two. On the same corner in the same dry run, the wall found by the dot's knee and the wall found by the wire tip give the **vector from the dot to the wire tip**, which is the part of dot-versus-melt a dry run can reach without emitting (and `datum-01` shows dot-versus-melt is a floor under every datum). The geometry has three facts that neither idea file has. **First**, a straight wire lying along the tangent runs into a wall that curves away at 61.85 mm radius (the wall's inner surface is y squared over 2R further out at tangent offset y): a stick-out L needs an outward lean of about L/2R over cos(elevation); for the drawn geometry (35 degrees elevation, tip 3 mm upstream, 0.3 mm miss) the minimum is 4.8 degrees, and at zero lean the body is 0.77 mm inside the wall. **Second**, the tip moves along the wire's line, not along the seam: per millimetre of feed, 0.57 mm in height, 0.09 mm radially, 0.81 mm along the seam. One millimetre of stick-out is about 0.6 mm of tip height, and each weld ends with the wire cut or retracted `[repo]`, so the vector must be re-measured every start. **Third**, the wall touch is the tip's, at the tip's own tangent position, 0.05 mm further out at 2.4 mm upstream.

**The assumption behind it.** That a wire touch is a point probe at the dot's place; and that touching gives the corner "within a wire diameter" without saying which corner feature it touched.

**The repair, and a branch.** Read the two probes together and keep the vector: the radial part from the two wall touches (knee and wire), the vertical part from the wire's plate touch and the dot's focus (the focus is the weaker reading, since the spot-size curve is flat near it; a stylus touch in the same run, `datum-07`, reads it better). The dock coupon (section 2) can carry the same two probes on a known corner at every visit, so a change in the guide or the head shows as a change in the vector; the mule (`trials-06`) could carry a 0.76 mm wire stub with its own contact sense so the vector is found in its shell first.

**What it changes.** The dot-versus-wire relation becomes a number the AI can hold and check, beside your pivot trial (where the dot is in the gun's frame). `use-10` already puts the wire in the dry lap and draws it landing at the dot by construction; the vector says by how much it does not.

**What it leaves uncertain.** Whether contact changes anything the laser box shows (your own cheap test: clip on, laser disabled, touch the tube; watch the lamps); whether the feeder can be driven by software; that the tip is where the wire is, not where the melt is (the puddle is a couple of millimetres long and the wire enters at its leading edge); a 0.76 mm wire bends when pushed (the scene lets a fraction of a 0.1 mm bend into the readings). No interlock is defeated in any of this.

**Drawn as** `datum-20-dot-and-wire` (origin combination; `branchOf` `trials-03-dot-touch-probe`; combines `use-10-wire-first`, `datum-07-touch-off`): section and plan at the station, the wire's lean checked against the curved wall (LIMIT badge with the least lean that clears), the tip's offset from the dot per millimetre of feed, the radial and height sweeps with the AI's conclusion beside the truth. Idea file `datum-20-dot-and-wire.md`.

**Question for the originator.** Your mule has a switch in the nozzle tip. Could it carry a wire stub with its own contact sense, so the dot-to-wire vector is measured first on a stand-in that can run all night, and which sweep would you run first?

---

## 5. `trials-16-tube-moves-gun-hangs` and `trials-04b-follower-under-tube` (sketches): the passive support has to be stiff on two axes, and the crown is one

**The difficulty, in that variant.** The gun hangs from a passive support and the stage under the tube follows the seam by camera. The follower is sized for the tube's wobble (0.03 mm/s, a stroke of tenths of a millimetre to a few millimetres for seating). The passive support's own wander is not in that budget: `freedom-01` finds that with only bungees and wires holding the gun, 1 N of umbilical pull moves the dot about 40 mm radially, thirty times the follower's 1.2 mm radial stroke in your scene and far outside the loop's range (the dot knee gives a signal only within about half a millimetre of the seam). A stage under the tube can absorb what belongs to the tube, not the gun's static offset from a soft support. Your own open question ("how far does a gun on a passive support wander in ten minutes?") has a floor: the cable's pull divided by the support's stiffness.

**The assumption behind it.** That the gun can hang from anything, and the passive support's only cost is bandwidth.

**The repair, and a branch.** Let the passive support be the one that is stiff on radial and vertical, soft on the tangent, and standing on the work: a **crown** on the rim (`datum-03`). It follows the runout mechanically at any speed (0.125 mm radial and 0.15 mm face at the station, real size), so the stage under the tube is left with the slow part only: seat depth, a constant per tube, and the plate's tilt against the rim (0.10 mm at the station, illustrative). A lift under the tube set once from a touch removes the constant; the tilt stays (a crown stage servoed to a plunger removes both). A frequency split: the crown fast, the tube-side stage slow. The gun's weight is then the crown's problem, and Derek's loops are the answer to that: two soft wires from an overhead gallows carry 85 per cent of it, with the split between them set to take the weight's moment as well. With no loops, the crown's load acts 67 mm from the axis, at the edge of a ring on the rim (66 mm), and needs about 0.8 kg of counterweight to keep contact all round; with the loops and their split set for the weights it acts 22 mm out and needs none. The cable's pull is the load that remains: 1.5 N at an exit 0.13 m above the rim is 0.2 N m, and at 6 N the crown tips unless the split is retuned for the pull (software reading the two wire tensions) or the crown is heavier.

**What it changes.** `trials-16`'s loop closes on the dot error at a bandwidth of a few tenths of a hertz instead of chasing runout; the tube-side stage may be big, slow and a shim in the limit (`travel-13`). The dock weigh-in of `trials-02` and the two wire tensions here are the same measurement seen from the gun and from the wires.

**What it leaves uncertain.** A stiff vertical support anchored in the room and attached to a gun that rides the rim **fights the rim**: the force is the stiffness times the face wobble, 0.003 N for a 0.02 N/mm balancer, 30 N for a 200 N/mm wire against 7.4 N of crown: the wire lifts the crown off and the gun stops following. The supports must be forces. Three supports on one printed shell (two soft loops and a lug) without over-constraining it; the loops' own lateral stiffness; every gun mass, centre of mass and cable pull here is `[unknown]`. (A correction to my own `datum-03` claim: "a counterweight as heavy as the gun" centres the assembly on the axis; stopping a tip needs about 0.23 kg and contact all round about 0.7, illustrative. Its scene now reports all three.)

**Drawn as** `datum-16-loops-carry-rim-locates` (origin branch of `freedom-01-ring-bungee`, combines `datum-03-rim-crown`): the tube with the crown, the gallows, two loops with wires and a spring symbol each, the boom to the shell on a crown or on a room post, sliders for the loops' share, the stiffness of the vertical support, the cable's pull, the boom's compliance and a radial trim, the seat-trim options, and the statics readouts. This is also Derek's suspension example in my framing (below). Idea file `datum-16-loops-carry-rim-locates.md`.

**Question for the originator.** What stroke do you assume for the tube-side stage: the seating error, or the gun's static offset under the cable's pull? If the latter, the passive support needs to be stiff on two axes before the follower has anything to follow.

---

## Combinations named (the originals stay as they are)

- `trials-04` + `datum-02` + `datum-07`: a touch-checked map (`datum-14`).
- `trials-02` + `datum-07` + `trials-05` rung 2: a dock with a corner (`datum-15`).
- `trials-11` + `datum-10` + `trials-05`: a yardstick with truth (`datum-17`).
- `trials-03` + `trials-14` + `use-10` + `datum-07`: dot and wire on one corner (`datum-20`).
- `trials-16` / `trials-04b` + `datum-03` + `freedom-01`: a crown as the passive support, a slow stage under the tube (`datum-16`).
- `trials-01` puck + a work index (ports modulo 180 degrees, first tack): the index magnet and tag lose one job; see section 1.
- `trials-17` (trial card) + `datum-15`: a "dock coupon reading" row for the dot itself.
- `trials-06` mule + `datum-20`: a wire stub with its own contact sense.
- `trials-03` camera A + `datum-19`: the plate as a calibration target. The rim edge is the sharp feature and the corner is 6.35 mm below it, so a camera that reads the dot against the rim edge is wrong by 6.35 times the tangent of its line of sight to the axis (1.3 mm at 300 mm on the axis, 2.8 at 150); the rim circles and the two ports give the camera's pose in every frame. Your camera A, "far above, looking straight down", has this parallax.

## What in my framing the trials scenes helped correct

The dock weigh-in and the trial card gave `datum-14` and `datum-15` their events; the puck's kinematic seats give the lift-and-return case. The judge separated from the controller (your notebook's stated contribution) is what `datum-17` extends: a judge that is neither the controller nor the requirement's source.
