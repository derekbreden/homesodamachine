# use on travel, wave 2

From **use** (The day of use) to **travel** (Split the travel). travel's ideas keep their own files; nothing of theirs is edited. Present tense. Numbers come from `explorers/use/calc/` (`w2_t1_states.mjs`, `w2_handover.mjs`, `w2_yoke.mjs`, `w2_presetter.mjs`, `w2_angle_key.mjs`) and from the scenes; every stiffness, duration, shift and force in them is **illustrative** unless tagged **[repo]**, **[manual]**, **[derived]** or **[Derek]**, and the gun's mass, the umbilical's pull, the shoe's force and the size of a clamp's shift are still **[unknown]**. Nothing is ranked or scored.

How I read travel. Every idea in `travel/` says which body moves and what range and resolution each stage needs. My question is the one that comes after: **in what order does the closure use those stages, who holds the gun in each state, what changes hands at each handover, and is the last look taken after the last thing that shifts?** A stage that is right for its job is still wrong if the sequence asks it for a second job, or if a handover shifts the gun after the last measurement.

What I did with their set. I ran `tools/check-scene.mjs --shot --exercise` on all thirteen of travel's scenes (01, 02, 03, 04, 05, 05b, 06, 07, 08-force-path, 14, 15, 16, 18; all pass) and read the thumbnails and the per-control shots; I drove `travel-01` by hand at states no shot shows (the fine-Z and shuttle sliders together: section 1). travel's set grew while I worked (idea files 14, 14b, 15, 16, 17, 18 and their `index.md` appeared); I read the versions in place at about 03:00 and revised what follows against them. Five scenes come out of this exchange, and my own `use-01`, `use-03` (scenes) and `use-02` (idea file) are revised (section "Scenes drawn").

**A source problem first, because several sections stand on it.** The coordinator's shared context says that at the end of a bead "the trigger stays held while the operator lifts the head straight away, and the gun's retract cycle breaks the wire in air", and cites `hardware/weld-rotator-guide/46-the-per-weld-sequence.html`. The guide's text (and `weld-rotation-rig.md` steps 6 and 7) says only "carry the bead about 20 degrees past the first tack ... Release the trigger, then the pedal", and then the snip of a stuck wire. The words *lift*, *retract* and *in the air* do not occur in guide 46 or in `pressure-vessel.md` (searched). The lift-away may come from Derek's earlier accounts; it is repeated as [repo] in travel-04, room-01, use-01, use-02 and other files. In this exchange every use of an "escape" is conditional on it, the scenes take the distance as a slider whose 0 is the sequence as written, and I have corrected my own attribution in `use-01-day-lanes` and `use-02-swing-head`.

| # | travel idea | depth | the difficulty, in its variant | what I drew |
|---|---|---|---|---|
| 1 | travel-01 tube travels | deep, stressed | the fine Z is bigger than the swap margin, an end-of-bead escape has no owner, one closure needs two approaches, and a fused wire is a state | `use-13-work-states` (branch) |
| 2 | travel-05b soft drive, hard lock | sketch, developed | the clamp closing is the last handover and nothing looks after it; Derek's bungees fail at the weld once the arm lets go | `use-14-handover-shift` (combination) |
| 3 | travel-14b crown cartridge (with 14 and 16) | sketch, developed | the crown stays on its tube for one closure, not two; the dock is a hand action; the pivot at its stop has a 200 mm lever | `use-16-yoke-escape` (combination) |
| 4 | travel-06 nest driver | developed | the driver centres with the shoe off; the rotator has no jog-to-angle; presetting frees the station and a driver frees the hand | `use-17-driven-presetter` (combination) |

Derek's examples, as days, are `use-15-examples-as-days` (branch of freedom-01, freedom-02 and room-01; it also answers travel-07's request to see states as columns). Smaller notes on travel-02 and travel-18, travel-15, travel-04, travel-07, travel-10 and travel-13 follow the four sections.

---

## 1. travel-01-tube-travels (deep): one Z axis is asked for three jobs, and the closure approaches twice

### The difficulty, in this variant

travel-01 assigns the per-tube trim to a stack under the rotator and the swap to a shuttle with the gun locked. Followed through the states of a closure, four things ask more of the stack than the drawing does.

1. **Z's range is bigger than the swap margin.** In the kit's proxy pose the nozzle tip is 5.0 mm above the rim plane [derived]; the fine Z runs ±6 mm. In travel-01's own scene, with the shuttle at 20 mm and Z moved by hand, the rim badge is off at Z = +1 and red from Z = +2 (the barrel behind the tip is nearer the rim ring than the tip is). So 8 mm of the 12 mm of fine range are safe for a swap, and a weld that ends with the axis trimmed high (a shallow plate, or a tube whose seam sits low) drives the barrel into the rim on the next shuttle. Nothing in the drawing stops it. The shuttle needs an interlock (no shuttle unless the barrel is clear), which forces a fine-axis move before every swap.
2. **The end of a bead has no owner.** If the head must leave the puddle with the trigger held (the shared-context sentence above; unconfirmed), the gun cannot: it is locked in a holder. The work must drop. With the beam's vertical component 0.712 in this pose, 20 mm of standoff growth along the beam is **28.1 mm of Z**, in 0.47 s at 60 mm/s while the tube is still turning (3.7 mm of seam at 8 mm/s). The whole fine range (12 mm) gives at most 8.5 mm along the beam, and it is a micron-step, stiff-by-design axis. room-01 names the shelf drop as the escape and room-15's scene puts numbers on it (26 mm at 60 mm/s, which is 18.5 mm along the beam in this pose).
3. **A return axis's tilt is face runout.** Every return to a hard stop leaves the stack tilted by the stop's repeatability; the seam is 232 mm above the rotator feet (travel's own figure), and a tilted seam circle at r = 61.85 mm moves up and down under the fixed gun by 61.85 tan δ once per revolution: 0.02° is 0.022 mm, 0.05° is 0.054 mm (0.11 mm peak to peak), 0.1° is 0.108 mm, against a 0.30 mm TIR acceptance [repo]. The fine axes cannot trim a tilt, only the position it causes; the follow stage of travel-02 would have to follow it, afresh after every approach.
4. **Two approaches per closure.** Guide 46's order is: indicate; seat and tack the plate; verify the face TIR ≤ 0.30 mm; engage the shoe; dry revolution; set the speed, return the index, place the wire; weld. The tacks are fired with the gun at the seam; the dial reads the plate face at the weld circle. With the gun fixed and the dial needing the recess, the tube goes in for the tacks, out for the dial, and in for the weld: two hard-stop landings, each with its own return error, and the last trim has to come after the second. A fused wire is one more state: the head stays where it stopped and a hand cuts it, and with the gun fixed a shuttle or a drop before the cut drags the wire through the seam, so every axis is inhibited until a hand says the wire is cut.

### The assumption behind it

Theirs, as I read it: Z exists to trim, the swap is rare and slow, and the gun's fixity is the reason nothing else has to move. Mine: that the sequence gives Z (and the shuttle) more than one job and that a fixed gun leaves the work as the only thing that can leave.

### Repair or branch: `use-13-work-states`

travel's own stack rule is *long axes at the bottom with hard stops, the fine axes on top* (their round 3). Applied to Z it gives **a drop tier under the fine tier**: 30 to 40 mm, hard stops up and down, commanded as states. The approach becomes drop, shuttle in, rise to the top stop, then the fine trim. The swap clearance and the escape become one commanded motion (the same finding my plunge made in use-02, and room-12 made for the shelf). The scene follows the closure through eleven states (load and indicate out at the loading position, seat the plate, approach 1, trim and tack, face check out, approach 2, trim and dry lap, weld, escape, hold, unload), draws the hand marker and a lane card for each, and compares the two Z branches and the two escape owners (the work drops, or the gun plunges back) with the drop distance, the return error, the tube length and the plate depth as sliders. The fused-wire toggle raises the hold badge on any move after the fusing. What it changes: one more axis, and the top stop's repeatability and tilt join the chain; the escape leaves the fine axis. What it leaves uncertain, and stands: the real nozzle margin (the 5.0 mm is the kit's proxy), what tilt repeatability a printed or lab-jack tier has, how fast a drop may be with a fused wire (force limit), whether a lift is needed at all (slider 0 removes it), and the cables on a shuttling body (motor lead, pedal, shoe, purge hose), which travel-01 lists and which the scene does not draw.

The alternative, drawn as a radio in the same scene because room drew it first (`room-12-one-axis-head`, "the tube clears"): the gun escapes on a short slide along its own beam and the work keeps only the shuttle and the trim. Z stays a pure trim axis; the price is 20 mm of umbilical motion on the gun side, and a force-limited plunge that stops after 4 mm on a fused wire (use-02's rule: the retract must never be the thing that breaks a fused wire), which the scene shows as a badge.

What drawing the states exposed that thinking had not: the hand and the gun meet only at the trigger and the snip in this arrangement (the tube states are 200 mm away), which makes it the arrangement with the fewest hand-on-gun minutes I have drawn; and the second approach is a consequence of the written order, not a choice.

### Question for travel

The ±6 mm on Z came from the trim. Was the swap or the end of a bead in mind for that axis, and if a return tier goes under it, what tilt repeatability at its top stop would you accept, given that 0.05° is 0.054 mm of face runout on every approach?

---

## 2. travel-05b-soft-drive-hard-lock (sketch): the clamp is the last handover, and a look has to come after it

### The difficulty, in this variant

The idea file lists the right item under "leaves standing": the clamp moves the gun as it closes and software does not see it. What the sequence adds is *where it sits*. In `travel-05b` the order is: soft anchor drive to a neighbourhood, camera trim through the springs, close the clamp, weld. The camera's last look is before the clamp. So the size of the clamp's shift is the size of the error.

`explorers/use/calc/w2_handover.mjs` (2000 closures, the scene's defaults: hand ±1.0 mm, springs 0.10 and 0.40 N/mm, dead band ±0.30 mm from 0.15 N of friction, camera 0.05 mm, step 0.01 mm, clamp 1-sigma shift 0.05 mm, window ±0.10 mm, load change 1 N, clamp 50 N/mm):

- no camera look after the clamp: **81 %** of closures end inside the window; with a look after it (unlock, trim, relock, until the reading is inside half the window): **95 %**;
- the friction dead band costs **rounds, not accuracy**: the loop winds the anchor until the gun breaks out and lands on the band's edge, so the median closure trims in two rounds and ends 0.035 mm from the seam, while 15 % of closures use five or six rounds (10 % use all six); 0.02 N of friction gives 96 % (the drawn 0.15 N gives 95 %);
- a clamp that always pushes the same way (mean shift 0.08 mm): 49 % with no look, 82 % with a look, **81 % with no look at all once the mean is learned and removed** from logged closures. A mean can be learned by an AI that runs the closure many times; a scatter needs a look afterwards.

### The assumption behind it

Theirs: a clamp is a reduction of compliance and its closing is a footnote. Mine: that the shift at a handover is the requirement, and that its size is unmeasured and may have a mean.

### Repair or branch: `use-14-handover-shift`

The same one-axis chain drawn for four arrangements, state by state: **A** an arm that grips and stays (freedom-01 with a rigid grip), **B** travel-05b, **C** Derek's rings and bungees once the arm lets go, **F** a three-ball seat (use-02) for comparison. Each state is a column with the shift it adds; the distribution over 2000 closures and the RMS move at each state sit beneath. Two rules fall out and both are drawn:

1. *The last look comes after the last handover.* For B it is the relock loop above. For A the last handover is the grip; the arm's own load change at the weld (1 N on a 5 N/mm arm and 0.15 N/mm of bungee: 0.19 mm) is after the last look: 1 % of closures inside the window; with the dry state carrying the weld loads (room-13's repair: gas on, wire jogged, trigger path loaded, laser off) only a fifth of it is left: 93 %; a 20 N/mm arm: 87 %. travel-18's "second dry turn in the weld state" is the same rule applied to the signature.
2. *An arm may let go of a soft support only at zero arm force, and a soft support cannot hold the weld.* In C the release shift is 0.77 mm RMS; nulling the arm force first by moving the bungee anchors (freedom-01's auto-null) cuts it to 0.11 mm, but a soft spring cannot be nulled better than force noise over stiffness: 0.05 N over 0.15 N/mm is 0.33 mm. Then a 1 N load change moves a 0.15 N/mm support 6.7 mm; 3 N/mm brings it to 0.33 mm, at which point the bungees are an arm. Derek's rings carry, shed weight and hold a neighbourhood; the last stiff element at the weld has to be something else.

What it changes: the state machine around a soft drive gains a *relock* loop and a bias table; travel-14's "soft to centre, locked to hold" pads inherit the same missing shift (its `lock` toggle adds stiffness and no closing shift). What it leaves uncertain: every number (the shift, its mean, the load change, the window are all unmeasured); heat (a locked ring on a tube that grows 0.03 to 0.06 mm); nothing observes the gun between the last look and the weld.

### Question for travel

What do you expect a clamp to do to the dot as it closes: a wedge or cam that pushes toward a known side (a bias the AI can learn) or a jaw that pinches (a scatter it can only look at afterwards)? Which would you build first, and would you rather measure the closing shift with the indicator you already own before choosing?

---

## 3. travel-14b-crown-cartridge (sketch, with travel-14 and travel-16): the crown's day, the dock, and the pivot at its stop

### The difficulty, in this variant

travel-14b splits the crown the way use-03 splits the tube: what varies per tube (ring seat, locked pads, a shim from a depth gauge) stays with the tube on a presetter; what is constant (beam angle, by a pitch stop) stays with the gun; the gun lifts out of one yoke and drops into the next by two trunnion pins in V-notches. Read as a day:

| state | who holds the gun | the hand | the eye | software |
|---|---|---|---|---|
| presetter: seat the crown, pads settle, lock, depth gauge, shim | the tube's crown | works | dial and gauge | reads the gauge; could log the shim |
| carry the cartridge to the rotator, drop it in the nest | the crown, no gun | works | rim seated | none |
| dock the gun (pins into notches, stop screw) | hand, then the dock | holds the gun, one hand, fibre trailing | judges | reads three contacts |
| trim (one-time radial, per tube: the n = 1 term and seat depth) | the dock | works on the boom | a camera, if one can see the dot | the crown "sees nothing" |
| tack, dry lap, weld | the dock | trigger | guards | rotator only |
| lift the gun out (the escape) | hand | holds and lifts | judges | none |

Four difficulties sit in that table.

1. **The crown stays on its tube for one closure, not two.** The repo's second closure inverts the tube (first plate down, ports through the Ø90 mm service bore) [repo]. The crown sits on the rim being closed, so for the second closure it is on the wrong end: a second crown, or seat, lock, gauge and shim again. The presetter step is per closure, not per tube, and a crown per closure doubles the printed count.
2. **The dock is a hand action, so there is no state for software to command.** travel-14b's software list is the rotator and three contacts. The AI cannot run repeat-dock experiments (the point of the study's goal) with the docking, the pad lock and the lift-out all by hand. The swing head (use-02) commands *seat* and *retract*; a dock does not.
3. **The pivot at its stop has a long lever.** In attitude B the trunnion axis is 185 mm from the nozzle and 202 mm from the dot (kit proxy, `calc/w2_yoke.mjs`). A stop repeatable to 0.02° is 0.07 mm at the dot, 0.05° is 0.18 mm, 0.1° is 0.35 mm. travel-14b's own figure (20 µm on a 40 mm pin span is about 0.1 mm at the dot) has the same shape; outriggers to 100 mm give 0.04 mm.
4. **The last look must come after the dock.** The pads lock at the presetter (cold, off the station, shoe off); the dock closes at the station. The last handover is the dock, and the shim from the depth gauge cannot see it. travel-14 says "nothing sees the dot" and puts a one-time hand trim on the boom, so the trim's eye has to look after the dock, once per tube, not once per crown.

### The assumption behind it

Theirs: the gun is a constant and moves between cartridges as an object the person already carries. Mine: a hand-run dock is a sequence with three hand-on-gun states per closure and none the AI can drive, and the pivot at the dock's stop is a lever, not a hinge.

### Repair or branch: `use-16-yoke-escape`

The trunnion pins in V-notches are already a pivot with a pitch stop. Rotate the gun about them and the same axis is (a) the beam-angle setter, (b) the dock's pitch seat, and (c), if a bead must end with the head leaving a wire, an escape that never unseats the pins. The scene is a radial section of the kit's proxy gun in attitude B: 10° of pivot puts the tip 26 mm above the rim, 37 mm from the puddle point (from 16, so 21 mm of standoff) and swings it 27 mm outward over the wall; 5° gives 7 mm. A motorised pivot (a small geared stepper on the trunnion, or a spring-return with a latch) is a *commandable* seated/escaped state, which is what makes unattended dry-run repeatability experiments possible; the stop at 120 mm from the trunnion with 20 µm contacts is 0.034 mm at the dot, and a stop further from the trunnion is better. What it changes: docking stays by hand once per cartridge, but the escape and re-seat between beads become a command. What it leaves uncertain: whether the housing takes trunnions there; travel-16 and travel-04 note that with no wire at the gun the reason to lift disappears, so for that variant the pivot is only the dock's axis and the angle setter; the pivot's own play and printed creep; the preload against cable pull.

### Question for travel

Who is meant to dock the gun, a hand or a machine? And for the second closure, is the crown moved to the other rim or duplicated? If duplicated, is the presetter's depth gauge per closure?

---

## 4. travel-06-nest-driver (developed): the driver's last pass belongs with the shoe on, and it needs an interface the rotator does not have

### The difficulty, in this variant

The routine nulls the tube's eccentricity by turning the three nest screws round to a stationary driver while a probe reads the tube wall, down to 0.024 mm TIR in three passes. Three steps of the written sequence and one fact about the controller bear on it.

1. **The shoe.** Guide 46 indicates the tube first (step 2), tacks and verifies the face (step 3) and only then "scuff and engage the copper shoe" and proves continuity on a dry revolution (step 4). The shoe wipes the tube on one side. The tube is held by three screw tips within 0.20 mm of radial clearance [repo]; a sideways shoe force F moves it by F over the contact stiffness. With placeholders of 1 N and 5 to 50 N/mm that is 0.2 to 0.02 mm, which is the size of the routine's whole result. So a centring done shoe-off is not the weld state's centring.
2. **The rotator has one input, the pedal.** Held, the table turns at the stored speed; released, it stops and, ten seconds later, the driver lets the motor go so the table turns by hand; the console is serviced only while the table is stopped; the degrees are "a readout for the operator" [repo firmware README]. A driver that presents a screw to a bit needs *go to an angle and hold*: firmware that does not exist yet (it is Derek's own code and small, but it is a change).
3. **Station or hand.** The routine occupies the station for the passes (their scene: 260 s at 15 mm/s for three passes). use-03's finding was the mirror: a presetter frees the station and not the hand. At the drawn defaults (`use-17`) a driver on the station cuts the hand from 12.0 to 7.5 minutes per tube and leaves the station at 13.7; a presetter with an advisor takes the station from 16.0 to 10.3 and leaves the hand at 10.0; a driver *on a presetter* gives 8.0 and 10.3. The station is the binding resource in all four rows at these numbers. If the presetter also seats the plate (which needs no rotator) the station drops by another three minutes and the *person* becomes the binding resource in the two presetter rows. Every duration here is a slider and a placeholder.
4. **The register.** A cartridge moved from a presetter to the station arrives with a register error, and a shoe-off centring has the shoe error; both land in the weld unless a verify pass with the shoe on follows.

### The assumption behind it

Theirs: once centred the tube stays where the routine left it, and the routine's place in the day is wherever indicating is today. Mine: that the state the routine measures must be the state the weld sees, and the guide's order puts the shoe after indicating.

### Repair or branch: `use-17-driven-presetter`

Four rows (hand on the station; use-03's presetter and advisor; travel-06's driver on the station; the driver on a presetter with a station verify pass), each with person, presetter and station minutes and the error left at the weld from three terms: the centring residual (0.06 hand and dial, 0.05 advisor, 0.024 driver), the register error (0.03) and the shoe shift (0.05). At the defaults the errors are 0.078, 0.071, 0.055 and 0.055 mm; with every last pass made with the shoe engaged they are 0.060, 0.050, 0.024 and 0.024. The repair is an ordering rule: **run the driver after the shoe is engaged and treat the presetter's result as a starting point**, with a station verify pass (one lap at measuring speed, shoe on). What it changes: the routine moves later in the closure; the driver needs go-to-angle-and-hold; the presetter rows need a second rotary (a lazy Susan with an encoder and a hall pulse is a few dollars: `sourcing/use.md`, wave 2 additions). What it leaves uncertain: the shoe's force and whether it moves the tube at all (an indicator on the tube with the shoe engaged and disengaged says in a minute); a jog speed above the weld range is not documented; the probe is still the missing part (no Prime-listed indicator with a documented data output found; the caliper-style clock and data route is unchecked).

### Question for travel

When the driver runs, is the pedal held (a deadman) or does the controller take a hold command? And would you run the routine after "engage the shoe", so that the tube it centres is the tube that will be welded?

---

## Also noticed (not full sections)

- **travel-02 and travel-18: the replay's zero.** travel-18 is right that the dry turn must be in the weld's mechanical state; in the guide's order that is the turn *after* step 5 (speed set, index returned, shielding, wire placed), not the step-4 continuity revolution. A follow table keyed by angle needs an angle zero that survives: the controller lets the motor go ten seconds after the pedal is released and its degrees are a readout. The tolerance is generous: a phase error φ on a 0.125 mm first harmonic leaves 2 × 0.125 × sin(φ/2), which is 0.022 mm at 10°; counting the first three harmonics (0.125, 0.03, 0.01 mm) the table stays inside 0.02 mm to about 5° and inside 0.05 mm to about 13° (`calc/w2_angle_key.mjs`). The guide already returns the table to an index mark by eye, good to about 1° (1 mm of arc), so the zero is the index mark; a once-per-revolution hall pulse (a 5-pack is $5.99 on Prime, `sourcing/use.md`) makes it readable by software. All three harmonics are safe at the 1° the eye gives.
- **travel-15 touch stack: state count.** The touch routine follows the tacks (guide step 3) and the shoe, and a tack under the ball is read as a tack (they note it). What the lanes add: the stylus stands where the nozzle was, so a per-tube routine is a hand-on-gun swap in and a swap out (two states) unless the stylus has its own slide to the dot.
- **travel-04 return seat, beside use-02.** Same seat, different carrier. Two things each has that the other lacks: the lid needs no plunge axis and no post, and a motor that lifts it has to supply the gun's weight torque (1.2 kg at 230 mm is 2.7 N·m, illustrative) plus the magnets' preload, where use-02's plunge along the barrel needs only the preload and a float; travel-04's hinge line about x lifts the nozzle straight up with no radial motion (measured in their scene at swing 12°: 54 mm up, 1.5 mm along the tangent, where their text says about 45 mm), which is fine for lift-and-slide. The unresolved cable is the same in both.
- **travel-07 allocation matrix.** Its only state axis is setup versus weld. The matrix has columns for motions; the states have columns too. `use-15-examples-as-days` is the same question with eleven state columns for Derek's three examples (rings and arm, monitor arm, table opening), including PARK (the recess must be open for seating the plate), ESCAPE and SNIP. Adding a park column to travel-07 would fill three cells its blanks mark as "not named": parking is free in the table opening (the hand works under the table), a swing held by friction on the monitor arm, and a lift of the whole hanging assembly in the suspension.
- **travel-10 (person is the eye) and trials-10 (human-labelled jog) are the same idea, found independently.** The eye is needed in one state (TRIM), not in the dry lap or the weld, and the real recess denies it a view. use-11's gauge tube with a wall window gives a person's eye the corner once per campaign; each tube then brings its correction by cartridge (use-03). "Narrate a dozen tubes" becomes one gauge session plus corrections. Not drawn: use-11 already draws the gauge.
- **travel-13 print to adjust: the printer as the coarse stage.** What the AI has that a person does not is hundreds of logged closures. If the per-tube trim is N(0.8, 0.3) mm and the fine range is ±0.5 mm, 16 % of tubes fit; a shim that recentres the mean puts 90 % inside (illustrative). That is a state-level use of the 20-minute loop: it runs while the hand is busy with the next tube, its lag is a two-tube delay, and its input is the same mean-learning as the clamp's bias in section 2.

## Combinations named (drawn or not)

- travel-01 × travel-01's own stack rule × room-12: drop tier under the fine Z, or the gun escapes and the work swaps: `use-13-work-states` (drawn; room-12 drew the second).
- travel-05b × freedom-01c × freedom-01 × room-13 × use-06: the last look after the last handover, the rings' release at zero force, the dry state that carries the weld loads: `use-14-handover-shift` (drawn).
- travel-14b × travel-16 × travel-04 (× use-02): the pivot with a stop as dock axis, angle setter and escape: `use-16-yoke-escape` (drawn as a section).
- travel-06 × use-03 × room-09 (a commanded height from the cartridge record): the driver on a presetter, the plate at the presetter, the station verify pass with the shoe on: `use-17-driven-presetter` (drawn as a budget).
- travel-07 × use-01 (× freedom-01, -02, room-01): state columns for Derek's examples: `use-15-examples-as-days` (drawn).
- travel-10 × use-11 × trials-10 × use-03: a gauge session for the eye, cartridges for the tubes (named, not drawn).
- travel-13 × use-14's bias table: the printer recentres the coarse stage from logged closures (named, not drawn).
- travel-18 × room-13: the second dry turn is the load-matched dry state (both name it).

## What I could not repair

The real size and mean of a clamp's closing shift (nobody has measured it); the shoe's force and whether it moves the tube; whether the head must lift at the end of a bead at all and how far; the cables on a shuttling stack (motor lead, pedal, shoe, hose); the crown's second closure (a second crown is a fix, not a repair of the cost); printed-groove creep at any seat; the missing micron-class probe (still not on Prime); the trigger's real path from a hand that is not gripping (room-14 draws one). Each stays visible in its section.

## Questions that need Derek's observation (collected)

- How do you end a bead today, how far does the head go before the wire is free, and does it lift at all?
- Read the indicator at the weld circle before and after you engage the copper shoe: does the tube move, and by how much?
- What does a clamp, cam or magic-arm knob do to a dot when it is tightened (indicator on the gun's shell, tighten, read)?
- Can the dial stand opposite the gun for the face-runout check after tacking?
- Weigh the gun and its shell; pull the umbilical with a spring scale at the grip base, before and after the wire feed starts and the gas comes on.
- The rotator's fastest safe jog, and whether the console accepts a command while the pedal is held.

## Scenes drawn

| id | origin | branchOf / combines | what it is |
|---|---|---|---|
| `use-13-work-states` | branch | travel-01 | the tube travels through eleven states; one fine Z or a drop tier under it; who escapes (the work or the gun); the two approaches; the hold |
| `use-14-handover-shift` | combination | branchOf travel-05b, freedom-01; combines travel-05b, freedom-01c | where the millimetres go at each handover, four arrangements, 2000 closures |
| `use-15-examples-as-days` | branch | freedom-01, freedom-02, room-01 | Derek's three examples through eleven states side by side; minutes at the tube, holding, firing, free |
| `use-16-yoke-escape` | combination | branchOf travel-16; combines travel-16, travel-04 | a radial section of the yoke pivot: escape, dock axis, stop and its lever |
| `use-17-driven-presetter` | combination | branchOf travel-06; combines travel-06, use-03 | minutes for the person, presetter and station, and the error left at the weld, for four ways of centring |

Revisions of my own: `use-01-day-lanes` and `use-02-swing-head` (the lift-away attribution), `use-03-preset-cartridge` (the verify pass belongs with the shoe on, borrowed from travel-06's order problem), and `sourcing/use.md` (wave 2 additions: a hall-effect index sensor).

## What this changes for me

The rule "the last adjustment must come after the last thing that shifts" (use-06) was about a lock; travel-05b and travel-14b show it is about every handover, and `use-14` puts a number on the cost of ignoring it. My use-01 gate list needs a *hold* state for a fused wire and a *shoe engaged* state before any centring or verify; my use-02 plunge keeps its seating and clearance jobs whether or not the sequence has a lift. My earlier finding that presetting frees the station and not the hand has a partner: a driver frees the hand and not the station, and only one of them is scarce at a time. The three examples take the hand off the gun and none takes it off the tube; that is where the day is. And the largest uncertainty across all four sections is not a mechanism: it is one sentence about the end of a bead that two explorers' scenes and three of mine quote as [repo] and that the repo does not say.
