# travel on datum, wave 2

Critic: **travel** (split the travel: which body moves, which stays, what range and resolution each stage needs, which stage's error shows up as which error at the dot). Originator: **datum** (the seam is the datum). Nothing of datum's is edited; the eight scenes were run through `tools/check-scene.mjs --shot --exercise` and their per-control shots read, and each was opened at states the shots do not show (datum-01 with the ring-on-OD reference, datum-03 with the drag and tether sliders at their limits). Everything below is present tense, illustrative unless tagged, and ranks nothing.

## What datum's set looks like from here

Three of datum's ideas are allocations of motion in disguise. datum-03 (crown) says **the work carries the gun**, so the runout is not seen and no follow stage exists; datum-02 (signature) says **learn the work, then replay it into a small stage**, which is my `travel-02` with the stage in the gun's shell; datum-07 (touch-off) says **probe the work with the tool**. The framing's habit is to ask of each: what element locates on each axis, what carries, what is free, and where does the compliance sit. The five sections ask that. Each ends with a question for datum.

| # | datum idea | depth | the difficulty, in its variant | what I drew |
|---|---|---|---|---|
| 1 | datum-03 rim crown (with 03b) | deep, stressed | the seat is a clearance fit with a job it cannot do both ways: pads soft enough to seat are as stiff as the ring; three pads pass ovality at gain 1; the cable is modelled as torque only | `travel-14-exact-crown` (branch); `travel-14b-crown-cartridge` (sketch) |
| 2 | datum-02 seam signature | deep, stressed | the hold between the dry turn and the weld turn is "not addressed" and its change of force times compliance is as large as the fit residual | `travel-18-signature-parity` (combination) |
| 3 | datum-07 touch-off | rough, developed | "what carries and moves the tip" is open; the largest term is a swap error that is really an unknown | `travel-15-touch-stack` (combination) |
| 4 | datum-09 preplaced filler ring | sketch, developed | "the yaw becomes free" is not what becomes free; what it frees is worth more and changes 03 and 03b | `travel-16-radial-plane` (combination) |
| 5 | datum-12 work-side tilt | sketch, developed | a wedge under the base pivots 232 mm below the dot | `travel-17-risley-wedges` (calc and idea only) |

---

## 1. datum-03-rim-crown (and 03b): the seat is a clearance fit with a job it cannot do both ways

**What the crown is, allocated.** The tube turns; the ring on its outside and rim turns with it; the gun rides an upper ring on balls. Runout and tube length never reach the gun; a plunger and a vertical stage take seat depth; a counterweight and two soft cords keep the upper assembly level and from wandering. Per tube nothing is trimmed radially: the boom is hand-set once. So the crown assigns **radial and vertical position to the ring's seat on the work**, and the seat is everything.

**The difficulty, in this variant.** The scene draws the lower ring as a skirt with 0.4 mm of radial clearance on the outside (63.9 mm against 63.5) and models the ring as sitting *exactly* on the outside's centre: the radial error is the OD-to-bore offset (0.08 mm) and nothing else. datum-01 charges the same contact as a 0.20 mm clearance, +-0.10 mm. Neither is a seat. Four things follow, from `calc/08-crown-seat.mjs` and the scene `travel-14-exact-crown`:

1. **A plain clearance ring is a one-point follower.** With a steady sideways pull it rides the tube at the loaded point, so the radial error is the whole local out-of-round (n=1 and n per revolution), and a reversal of the pull moves it by the whole clearance.
2. **Pads that centre it pass the out-of-round.** k equal spring pads pass lobe harmonics k-1 and k+1 at gain 1 (checked numerically) and reject the rest: three pads pass ovality (n=2) at unity; four reject it and pass three-lobing; six reject n=2 to 4. A rigid V magnifies ovality, 1.0 to 1.7 by angle and 5.4 at 80 degrees. With illustrative numbers (ovality 0.10 mm, OD-to-bore offset 0.08) a three-pad ring gives 0.33 mm peak-to-peak radial error against 0.25 for a room-fixed gun on an indicated tube (the rig doc's 0.25 mm TIR, half as amplitude); three rockers of two pads at +-45 degrees give 0.16, because that seat rejects n=2 and 3. The n=1 offset (wall thickness) passes every seat at gain 1: **no seat removes it; only a measurement does** (datum-04's feeler at the station, datum-07's touch, the eddy scan).
3. **A pad soft enough to seat is as stiff as the ring.** A pad must stay between about 2 and 20 N over an outside-diameter spread of about 0.36 mm (+-0.127 mm tolerance, illustrative, plus 0.10 out-of-round): 50 N/mm at most. Three of them are 75 N/mm; 3 N sideways moves the ring 0.04 mm and 1 N of *change* 0.013 mm; the scene's default 40 N/mm pads give 60 N/mm and 0.017 mm per newton; a cord-class 1 N/mm pad 0.67 mm per newton. The scene models the cable only as **torque** (3 N at a 233 mm arm, 0.7 N.m); the same 3 N is a force on the seat. What matters is the change between the dry setup and the weld (the parity term of section 2), because the steady part is trimmed by the hand-set radial position.
4. **The tether reacts a torque as a force.** Two cords or a rod to one tab at 76 mm reacts the 233 mm-arm drag as a net force 3.07 times the drag into the seat (9.2 N at the default 3 N). The ring turns 3.5 degrees at 1 N/mm cords (3.7 mm of seam) and 17 degrees at 0.2 N/mm (18.7 mm).

Two more, smaller. **The plunger sits on the ring, not the gun**, 22 degrees from the dot (23.8 mm of arc, 3.0 s at 8 mm/s): the servo closes on plate-versus-ring and excludes the boom and shell, and the 1x tilt term arrives phase-shifted (0.038 mm of a 0.10 mm term) unless the table is delayed 3 s. **The rim is a full annulus**: it rests on the three highest spots it finds and, with a fourth, has two stable seatings; the once-per-revolution vertical error is up to about the rim flatness f (unknown).

**The assumption behind it.** Mine: on each axis the stiffest element locates, and a soft element may carry but must not locate. Theirs (as drawn): the ring is centred by the outside as if by construction, and the tether only has to stop wandering because rotation about the axis is free.

**Repair, drawn: `travel-14-exact-crown` (branch of your scene).**
- **Soft to centre, then lock** (`travel-05b-soft-drive-hard-lock` read as a seat): rockers or six pads settle the ring on the averaged centre and a cam or three set screws lock them. Stiffness becomes the contact's (0.004 mm for 3 N at an assumed 500 N/mm per pad).
- **Three fixed pads on the rim** instead of a full annulus: one repeatable plane per tube.
- **The free axis is where a stiff element costs nothing.** Turning about the tube axis does not move the dot, so the tether can be stiff: a pre-tensioned steel wire pair wrapped on the ring (two equal and opposite tangential pulls) is a pure couple, about 900 times stiffer than 1 N/mm cords (0.00 degrees at 3 N), and one strain-gauged wire reads the drag torque nobody has measured. Ring azimuth is then known by construction.
- **What it changes:** the radial error is n=1 (unknowable) plus the n=4,5 residue of a rocker seat, not n=2; the change-of-pull term falls from 0.017 to about 0.001 mm per newton; the tether's force into the seat goes to zero.
- **What it leaves standing, in plain view:** n=1; the tube's real out-of-round (unknown); a locked ring on a tube that grows 0.03 to 0.06 mm when hot; whether a printed pad can be a flat that only stiffens sideways; wire pretension over a lap; off-the-shelf detent plungers are light springs (12 N end force class, `sourcing/travel.md` 19) and are not the 40 to 50 N/mm the calc asks for.

**A combination I name and draw only as a sketch, `travel-14b-crown-cartridge`.** datum-03 has to come off the tube for every swap and be seated again, and every seating is a fresh draw of everything above. Split it as use-03 splits the tube and its nest: what varies per tube (the ring seat, the locked pads, a shim carrying this tube's seat depth from a depth gauge at a plinth) stays on the tube as a cartridge; what is constant (the gun's beam angle) stays with the gun, which docks on a kinematic seat, two trunnion pins in two V-notches, an axial stop and a pitch stop. That removes the plunger from the pocket, makes the seat's repeatability a one-time acceptance test per crown, and makes the end-of-bead lift-off the dock's own motion (lift straight out of the notches). The dock is an amplifier: the proxy housing is 34 mm wide, so pins on its sides span about 40 mm and 20 micron at a pin is about 0.1 mm at the dot by tilt (200 mm lever); outriggers to a 100 mm span give about 0.04 mm.

**03b, briefly.** The orbiting crown's cable problem is worked in section 4, where the finding is that the exit direction is not the fix and a weld that can go either way round is.

**Question for datum.** The crown scene puts the ring exactly on the outside; datum-01 charges 0.20 mm of clearance. Which do you intend, and would a pad-and-lock seat belong in the crown scene? And a sharper one: if the outside's centre offset from the bore (n=1) is the larger of the two amplitudes, no seat choice matters and the crown's radial win over an indicated tube is nil, so its case is vertical (face wobble, tube length, race float) alone. Do you hold that reading, and would a five-tube survey (OD out-of-round and wall thickness at eight positions each) be your first bench measurement?

---

## 2. datum-02-seam-signature: the hold between the dry turn and the weld turn

**What the signature is, allocated.** One dry turn measures dot-versus-seam per table angle; a small harmonic fit (constant, 1x, 2x) is replayed against the rotator's step count into a two-axis fine stage carried in the gun's shell. The constant is the setup offset, "a free by-product". The scene's fit leaves 0.022 mm rms; the stage needs 0.029 mm/s and +-0.37 mm. Right: the axis is not the hard part.

**The difficulty, in this variant.** The idea says the hold is "not addressed: a passive arm or the hand holds the gun; the fine stage rides in the shell". The replay applies the dry turn's constant term, so it is only as good as the gun being in the *same place* in the weld turn. It is not: between the two turns the wire feeder starts and its conduit pulls on the bracket, the gas hose pressurises, the hand leaves the gun, the fibre emits. Each is a change of force; the error is the change times the compliance of the chain from gun to room (`calc/06`, `calc/10`):

- 12 mm steel rod, 300 mm: 44 micron per newton, so a 1 N change is 0.044 mm, twice the fit residual and the same sign every lap. 20 mm steel: 6. 12 mm aluminium: 128. A friction joint is not a spring: 0.02 degree of creep at 250 mm is 0.087 mm.
- A stage in the shell is in series: 20 N/mm adds 0.05 mm per newton. Keeping the parity term under 0.02 mm at a 1 N change needs a chain stiffer than 50 N/mm, stage included.
- Backlash on the radial (horizontal) stage: the replay reverses at the peaks, so b/2 remains either side once the mean is trimmed (0.025 mm at 0.05 mm); a vertical axis is loaded one way by weight and does not see it.

**Assumption behind it.** Theirs: the seam does not move once the weld starts and the gun does not move between turns. Mine (from `travel-02` round 4): **the stage belongs where the cable does not pull**; a stage in the gun's shell has to be stiff, and a follow stage under the work is out of that chain.

**Repair, drawn: `travel-18-signature-parity`.**
- **Measure the parity term instead of assuming it.** A second dry turn in the weld's mechanical state (feeder jogging at weld speed, gas on, laser off; `use-10-wire-first`'s wire-inclusive dry run, applied as a check): the two turns' constants differ by exactly the parity term, and the replay uses the second turn's fit. The scene's warning shows when the term exceeds 0.02 mm and goes away with the second turn.
- **Assign the fitted terms to the cheapest stage that can carry them.** From your default tube (constants 0.20 and -0.15, 1x 0.13 and 0.15, 2x 0.05 and 0.03): the constants are two thirds of the 0.29 mm rms; a **static trim** (one number per axis per tube) leaves 0.146 rms with peaks 0.18 mm, inside a +-0.30 mm window everywhere; **nest screws** taking 90 percent of the radial 1x (`travel-06`) leave 0.114; a **Z follow under the work** taking the vertical 1x leaves 0.043. A replay stage earns its place below a window of about 0.2 mm, vertical first (no screw in the nest touches the face wobble).
- **What it changes:** the replay's floor becomes the fit plus what the second turn does not see, not the fit alone; the stage count can drop from two axes to one or to none, depending on the window.
- **What it leaves uncertain:** what only an emitting head does (the head's vibration motor, heat), the real change of force, the real window, hot drift (nothing observes it in the weld turn).

**Question for datum.** What holds the gun in datum-02: the friction arm, the hand, or the crown? The 0.022 mm is quoted for all of them and the parity term is not the same for any two. In the crown branch you list "the crown's Z stage as the vertical axis": which axis does the replay drive radially, since the crown has no radial slide, and would you accept a second dry turn in the weld state as the first thing the routine does?

---

## 3. datum-07-touch-off: let the corner come to the tool

**What touch-off is, allocated.** A stylus (or wire tip, or nozzle) is driven into the wall and then the plate by two small software-driven axes; a one-bit contact and the step count are the sensor. Per-tube autonomy, no line of sight. datum-07's own unresolved: *what carries the gun and moves the tip by a few millimetres at 0.01 mm resolution*.

**The difficulty, in this variant.** Two, both numbers in your own scene. (a) The moving side: a fine stage carrying the gun (and a stylus with a touch force) sits on the gun side, where the umbilical pulls, and its compliance is in the touch. (b) The largest term in your budget is the tip-to-dot swap error (0.030 stylus, 0.15 wire, 0.30 nozzle), and it is not a swap error: the stylus is at the dot "by construction" only if the red pilot sits on the nozzle axis 16 mm out, and the manual documents an alignment screen precisely because it does not always (pp. 25 and 39; a third-party explainer says the software offset moves the pilot only). Better touching does not reduce it: it is a vector between two different things, one mechanical, one optical.

**Assumption behind it.** Theirs: the tip is the dot; the tip moves. Mine (`travel-01`): move the work, and let the axes that touch be the axes that apply.

**Repair, drawn: `travel-15-touch-stack` (combination with travel-01, using eyes-06 and trials-14).**
- **The work comes to the stylus.** The gun and stylus sit on a locked holder that never moves; the stack under the rotator drives the wall (X) and the plate (Z) into the ball, fast, back 0.5 mm, slow, one bit. Touch force goes into a holder that is stiff by design (0.3 N times 44 micron per newton is 13 micron, the same at every angle, so it lands in the constant), with no soft stage and no cable on the moving side.
- **A null measurement.** A touch made with the stage that then applies it cancels straightness and tilt of the guides and the Abbe error of my own stack (0.05 degree of layer tilt is 0.2 mm at the dot): they are in the touch and the weld alike.
- **A signature by contact.** The same touches at N angles (8: 2.2 minutes at 14 s per angle; 24: 6.0) give datum-02's fit with no camera; replay is the stack following the fit. That is the sensor datum-02 lacks: dry, cold, static, no fume, no glare.
- **The stylus is calibrated against the dot with the same yardstick.** Touch a coupon's corner with the stylus and sweep the dot across the same corner (eyes-06: the image path breaks at the corner); read both in stack units; the difference is the offset, no camera calibration. In the scene the offset defaults to 0.30 mm (unknown); calibration to an optical 0.05 mm class leaves the floor at the calibration's own accuracy, and the dot is still not the melt.
- **What it changes:** the tool-carrying stage question is answered by hardware already proposed; the biggest term becomes a measured vector with a defined procedure; datum-02 gains a contact sensor.
- **What it leaves uncertain:** the contact bit (the laser's work circuit if readable, or a separate low-voltage sense; trials-14's two-minute lamp test), the stack's own backlash and stick-slip, whether a 1 mm ball rides the 0.13 mm plate slip gap, tacks (a touch at a tack reads the tack), and whether touching the corner about to be welded is acceptable.

**Question for datum.** Where does 0.030 mm come from: the repeatability of the stylus's thread and seat, or an assumption that the dot is on the nozzle axis? If the first, the calibration above is not needed; if the second the true term is unknown and the dot-sweep on a coupon is how it is measured. And: the graduated tube sets the nozzle extension, which moves the dot along the beam, so a stylus is the right length for one extension only. Have you got the extension that the stylus is meant to be measured at?

---

## 4. datum-09-preplaced-filler-ring: what the missing wire frees (and does not)

**What the idea is, allocated.** A split ring of filler lies in the corner; the wire feeder disappears from the sequence and "the gun's yaw about the vertical axis becomes free" because the wire no longer needs the tangent. Your file holds it as a sketch and asks Derek only whether the route is acceptable.

**The difficulty, in this variant.** The claim is not the one that holds. With everything else held, yaw about the vertical still turns the beam: 15 degrees of yaw moves the in-section beam tilt (the heat split between wall and plate) from 32.5 to 9.9 degrees (`calc/09`, kit proxy). What the wire actually ties the gun to is the **wire bracket's arrival**, and what becomes free is a **whole family of attitudes** in which the barrel stands in the radial plane over the bore, plus the direction of the bead and of the end-of-bead departure. Rotation about the beam axis is free for the beam but twists the fibre 0.91 degree per degree (the kit's cable exit leaves along the dot-to-grip line, 25 degrees from anti-parallel to the beam), so it is not free in practice.

**The consequences that make it worth developing** (`travel-16-radial-plane`, kit proxy):
- **Balance.** The gun's centre of mass is 118 mm from the axis in the opening pose, 50 mm in the radial-plane attitude B (the far end of the reference scene's own 'vertical' dial), 14 mm in B2 (grip up, over the axis). datum-03's round 3 needs a counterweight as heavy as the gun; B does not (39 mm for the assembly against the 66 mm ball ring). **The upper ring needs no gap** for the barrel, which is over the bore.
- **Holding.** A yoke of two legs from the ring to trunnion pins on the housing sides holds the gun near its centre of mass and its pivot sets the in-section beam angle; a bipod is stiffer than a boom 118 mm out.
- **The umbilical.** B2 hangs the fibre straight up near the axis: the crown's drag arm is 38 mm instead of 234. In your 03b **the exit direction is not the fix**: A and B both leave radially outward and need a 142 to 155 degree turn before the fibre can run round the tube at the 350 mm bend radius; a G1-continuous route gives 5.6 m (A; your own 5.6 m at 700 mm) and 5.8 m (B) for 380 degrees against a 5 m fibre. (A quarter turn does not end tangent to a concentric track; the route needs the longer turn. The scene and `calc/09` carry the construction.) **What the missing wire does buy is a weld that can go either way round**: two halves of 190 degrees from the first tack, 3.25 m to 3.4 m, inside the fibre, every bend at 350 mm by construction.
- **Lift-off and swap.** No wire, no wire break-off: the head may leave in any direction at the end of the bead.

**A branch that keeps the process.** The wire bracket is what ties the gun to the tangent, not the wire. **Carry the guide on the ring** (the scene draws it, about 30 mm of arm because the reference guide already sits just above the ring): the wire arrives as before while the gun stands in the radial plane. Nothing is preplaced and no fusion question arises. Costs: the conduit's drag now loads the ring (the parity term again), the wire-to-dot alignment is a hand trim on the ring, and the manual's wire-feeding bracket is a gun-mounted part whose adaptation is unresolved.

**Assumption behind it.** Theirs: the wire is the only reason for the tangent, and the gun's yaw is what it frees. Mine: read what a constraint ties to (the bracket, not the wire), and count degrees of freedom by what the *beam* sees, not by the dials.

**What it leaves standing.** Fusion of a preplaced ring (your section; 0.62 mm^2 for a 0.035 in ring against the 0.684 mm^2 the recorded fillet needs, ER316L .035 in is a common Prime spool, `sourcing/travel.md` 22); two starts and two stops for a two-part bead, and a mirror re-lay of the cable between halves; the proxy's cable exit (unknown); whether the head tolerates grip-up (gas, lens drawer, cooling); the wire-feeder's bracket.

**Question for datum.** Which constraint did you want removed, the wire's presence or its arrival direction? If only the second, the ring-carried guide gets it with no preplaced ring; if the first, what is the smallest coupon test you would accept for fusing a ring (a scrap L in the laser, section 11's witness pass)?

---

## 5. datum-12-work-side-tilt: a wedge pivots at the bench, not at the dot

**What it is, allocated.** One of the three rotations is done on the work by a wedge under the base, ridge from the axis to the station; the gun needs one rotation fewer. Set once.

**The difficulty, in this variant.** The dot does not stay where it is: the ridge is at the bench and the seam stands 232.05 mm above the feet **[derived]**, so 1 degree of tilt moves the seam point 4.05 mm sideways (20 mm at 5 degrees, 40 at 10) and drops it 3.5 mm at 10 degrees; keeping the station where it is instead moves the seam 15.5 mm radially at 10 degrees (`calc/11-wedge-abbe.mjs`). For a wedge set once and the gun placed afterwards this does not matter; for one that changes between experiments it moves the seam 4 mm per degree.

**Assumption behind it.** Theirs: rotating about "a line through the dot and the tube axis" is what a wedge under the base does. Mine (`travel-03`): a tilt about a bench-level line has the Abbe lever of everything above it.

**Branch: `travel-17-risley-wedges` (sketch, calc only).** (i) The station azimuth relative to the lean chooses *which* rotation the tilt supplies: alpha cos(psi) in the radial section (the beam-versus-plate angle) and alpha sin(psi) along the tangent (pitch), so one fixed wedge plus the choice of where the gun stands gives any mix, not just the hole-axis roll. (ii) Two stacked wedge rings on a 12 in bearing (a Risley pair) make the tilt vector adjustable, 0 to 2a in any direction (0 to 10 degrees for 5-degree wedges), with a built-in reduction of about 11 to 1, so two rotary axes give two orientations. (iii) Cost: the seam displacement must be followed, and the printed race sees sin(alpha) of the weight sideways (5 to 17 percent at 3 to 10 degrees).

**Question for datum.** Did you mean the ridge at the base or a pivot at the dot? A set-once wedge does not need the dot; a wedge Derek changes between weld trials does, and then the arc of `travel-03b` or the Risley pair with a following gun is the shape. What mean inclination does he actually use?

---

## Combinations named (drawn or not)

- **Crown seat + soft-drive-hard-lock** (`travel-14-exact-crown`, drawn): soft to centre, lock to hold; a wire pair for the free axis.
- **Crown + preset cartridge + trunnion dock** (`travel-14b-crown-cartridge`, sketch): use-03, trials-02 and travel-04 in one arrangement.
- **Touch-off + tube-travels stack** (`travel-15-touch-stack`, drawn), with eyes-06 (dot sweep) and trials-14 (contact bit).
- **Signature + second dry turn + cascade** (`travel-18-signature-parity`, drawn), with use-10.
- **Preplaced ring or ring-carried wire guide + crown + orbiting crown** (`travel-16-radial-plane`, drawn).
- **Work-side wedge + dot-centred arcs** (`travel-17-risley-wedges`, calc).
- **datum-04 corner follower + the stack's Y stage** (named, not drawn): the follower's two-lead yaw estimate (0.13 to 0.18 degree at 0.02 mm noise in your scene and idea file) can be nulled by tangent travel of the work, which is a plan-angle stage with a 1/r reduction (1.08 mm of Y per degree, `travel-01`), so the feeler gets an actuator for its second output.
- **datum-13, my `travel-12` and borrowed-06 are one idea** (the head's own lateral trim): three explorers reached it, all held with the same open question, and one two-minute look at the touch screen serves all three.
- **datum-11 witness pass + `travel-13-print-to-adjust`**: the dot-to-melt vector from a coupon is a constant added to the setup pose, a shim or a printed spacer's job once measured.

## What I could not repair

- **n=1**, the outside's offset from the bore, passes every ring seat: only a measurement removes it (section 1).
- **What only an emitting head does** to the parity term (vibration, heat) (section 2).
- **The dot is not the melt.** Every touch, sweep and mark ends at the dot; only a witness pass touches the last term (sections 2 and 3).
- **Whether a preplaced ring can be fused** at the speeds and power in use (section 4).
- **The unmeasured numbers everything here hangs on:** the gun's mass and balance point, the umbilical's pull and direction at the exit, the tubes' out-of-round and rim flatness.

## Questions that need Derek's observation (repeated in the idea files)

Five tubes, eight positions each: OD by calipers, wall thickness by ball micrometer; rim flatness on a plate with a feeler gauge. The gun weighed and its balance point found; the umbilical's pull at the exit and the direction it leaves the grip base. Does the wire feeder push or pull on the gun's bracket when it runs, and does anything shift when the gas starts? Can the nozzle come off, and its thread? How does the laser's work circuit close? How far and which way does the head travel at the end of the bead today?

## Scenes drawn

`scenes/travel-14-exact-crown`, `travel-15-touch-stack`, `travel-16-radial-plane`, `travel-18-signature-parity` (each names its parent in `branchOf` or `combines`). Idea files: `explorers/travel/ideas/travel-14-exact-crown.md`, `travel-14b-crown-cartridge.md`, `travel-15-touch-stack.md`, `travel-16-radial-plane.md`, `travel-17-risley-wedges.md`, `travel-18-signature-parity.md`. Numbers: `explorers/travel/calc/08` to `11`.
