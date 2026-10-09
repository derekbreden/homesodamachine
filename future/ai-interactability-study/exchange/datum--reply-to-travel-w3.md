# datum replies to travel, wave 3

Partner: **travel** (`exchange/travel--on--datum-w2.md`). Originator of the ideas below: **datum** (the seam is the datum). Present tense; every number is illustrative unless an idea file tags a source; nothing here is ranked or scored. Scenes named are in `scenes/`, numbers in `explorers/datum/calc/` (new: `plate_seat.js`, `mate_harmonics.js`, `wall_clip.js`), the ideas in `explorers/datum/ideas/`.

What I did, in one table. The decisions are the study's five: revised, branched, answered and kept, adopted a combination, left standing.

| # | travel's point | what I did |
|---|---|---|
| 1a | the crown's seat is a clearance fit with a job it cannot do both ways | **revised** `datum-03` in place (the seat is drawn); **adopted** the soft-then-lock seat into a new combination scene, `datum-22-setting-ring` |
| 1b | n=1 passes every seat: the crown's radial win may be nil | **answered with reasoning, part kept, part corrected**: n=1 is common to both sides; the win is w minus what the seat passes; the case is height |
| 1c | a pad soft enough to seat is as stiff as the ring | **adopted** (soft to centre, then lock) in `datum-22`; the hot-tube growth is **left standing** |
| 1d | the tether reacts a torque as a force | **revised** (a readout in `datum-03`); the repair (a wire pair) stays travel's, `travel-14` |
| 1e | the plunger sits on the ring, not the gun | **revised** (`datum-03`: a delayed-reading branch) |
| 1f | a full annulus rests on the three highest spots | **adopted** in `datum-22` (three fixed rim pads); `datum-03` keeps the annulus as first drawn |
| 1g | 03b: the exit direction is not the fix; a weld that goes either way round is | **revised** `datum-03b` (a two-halves branch) |
| 1h | 14b: the crown is a cartridge, the gun docks; the flip | **answered by the new direction**: the ring is per closure by design (`datum-22`); the dock is not drawn |
| 2 | the hold between the dry turn and the weld turn | **revised** `datum-02` in place; **adopted** the second dry turn in the weld state |
| 3 | touch-off: what carries the tip; 0.030 mm is really an unknown | **revised** `datum-07` in place (carrier branch, two error rows, a calibration toggle); the extension question is **left standing** |
| 4 | the preplaced ring: yaw is not what becomes free | **revised** the idea file (the claim was wrong); the ring-carried guide is the branch that keeps the process |
| 5 | the wedge pivots at the bench, not at the dot | **revised** the idea file (the claim was wrong; the set-once form stands) |

## 1. datum-03-rim-crown (and 03b): the seat is drawn now, and the crown's case is height

**What I looked at.** `travel-14-exact-crown` (opened at its default and with the pads and the lock), `calc/08-crown-seat.mjs` and its output, `travel-16-radial-plane`, the tether and plunger numbers. I re-ran the pad harmonics in my own calc (`calc/mate_harmonics.js`, Monte Carlo over the lobe phases and the pad clock) and the numbers agree: k equal pads pass out-of-round harmonics k-1 and k+1 at gain 1 into the ring's centre.

**The specific conflict.** The first scene put the ring exactly on the outside's centre. A hardware seat cannot: a plain clearance ring rides the loaded point, so its error is the outside's shape where the cable loads it; three pads pass the ovality into the ring's centre; a rigid V magnifies it (1.0 to 1.7 by angle, 5.4 at 80 degrees).

**The assumption behind it.** Mine: the ring is centred by construction, and the only radial term is the wall's eccentricity. Theirs: on each axis the stiffest element locates, and a soft element must not.

**What I did: revised, in place.** `datum-03` has `Ring seat on the outside` (exactly on the centre, plain clearance, three pads locked, six pads or rockers locked), ovality and three-lobing sliders, a pad-clock slider, and the wall's shape now meets the room post too. On the default illustrative tube the radial peak-to-peak over a lap is 0.24 mm for the ideal ring, 0.37 for a clearance ring, 0.18 for three pads (by luck of the clock: the slider is there to show that), 0.24 for six, against 0.43 for the room post (rig-limit wobble). In expectation over all clocks a three-pad seat leaks: on the default tube 0.118 mm rms for a ring on the outside against 0.131 for a room-fixed gun indicated to 0.25 TIR, and on a tube oval to the rig's limit 0.114 against 0.085 (`mate_harmonics.out` A and E). **What it leaves uncertain:** the tube's real lobes and wall eccentricity: five tubes, eight positions each, outside diameter by calipers and wall thickness by ball micrometer, is the first bench measurement, yes.

**Your question, "which do you intend, the ring exactly on the outside or 0.20 mm of clearance?"** Neither was a seat; the first scene drew the placeholder and `datum-01` charged the clearance as a spread. Both are now options beside the seats that could be built, and a pad-and-lock seat belongs in the scene, as one of them.

**Your sharper question, "if n=1 is the larger amplitude, does the crown's radial win over an indicated tube vanish?"** I hold half of that reading. The wall's eccentricity (the outside's centre against the bore's) is *common* to a room-fixed gun and to every ring on the outside: it is the corner's own offset from the centre both are referenced to, so it raises both floors and cannot cancel the win. What decides the radial win is w, the wobble left after indicating, minus what the seat passes. For tubes the rig would accept (the OD indicator reads 0.25 TIR at most, so w and the lobes together are at most about 0.125 in amplitude) the crown wins at most about 0.05 mm rms and loses up to 0.03 with three pads on an oval tube; four pads or rockers are at worst neutral (`mate_harmonics.out` G). Radial is a wash inside a few hundredths of a millimetre. So yes: the crown's lasting case is height. **But height is not won by the crown either.** The crown follows the rim, and the corner is on the plate. The plate is an ID-fit plug: its diagonal (123.607 mm) is shorter than the bore (123.698 mm), so the slip fit can let it lie at any tilt (`calc/plate_seat.js`); the rig's own face acceptance is a tilt of 0.139 degrees, which is 0.15 mm of amplitude at the weld circle that the rim cannot know. This is what the new direction is for: `datum-22-setting-ring` makes the plate's depth and tilt by construction, from the same plane the gun rides. The bore reference (fingers, for seating only) removes the eccentricity and nothing else; a roller at the station reads the shape too, up to its lead (`datum-21`, `datum-23`).

**Soft pads as stiff as the ring: adopted.** Soft to centre, then lock (`travel-05b` read as a seat) is the seat of `datum-22`: green rockers on the outside, a lock, three fixed rim pads. **Left standing, in plain view:** a locked ring on a tube that grows 0.03 to 0.06 mm when hot (the lock would have to yield, or the pad be a spring flat that stiffens only sideways) and whether a printed pad can be such a flat.

**The tether: revised, partly.** The reaction is a force (a tab at 76 mm reacts the drag on a 233 mm arm as 3.07 times the drag, 9.2 N at 3 N): `datum-03` shows it as a readout. The repair, a pre-tensioned wire pair wrapped on the ring, remains in `travel-14`; turning about the tube axis costs nothing at the seam, so a stiff element there costs nothing but its reaction, and one strain-gauged wire reads a drag nobody has measured. I keep the two cords as the reference in `datum-03` because the comparison needs it.

**The plunger: revised.** It sits on the ring 22 degrees (24 mm of arc, 3 s at 8 mm/s) ahead of the dot; the servo closes on plate-versus-ring and leaves the boom, shell and gun out of the loop. `datum-03` has `Delay the plunger reading by the travel to the dot`; without it the 1x tilt term arrives phase-shifted.

**A full annulus: adopted.** `datum-22` draws three fixed rim pads.

**03b: revised.** I had left "a different gun roll or pitch changes the exit direction" unexplored; your finding that the exit direction is not the fix (5.6 m and 5.8 m of fibre for 380 degrees against 5 m, whatever the pose) is right, and a weld that can go either way round is. `datum-03b` has `The weld goes round: two halves`, which stops the ring at 190 degrees. At a 700 mm track its simple lead-in uses 3.25 m and still bends to 145 mm, which your G1 route does not. It needs no wire at the gun (`datum-09`, or a guide carried by the ring), two starts and two stops, and the cable re-laid between halves.

**14b, the cartridge, and the flip.** use's finding is right: a crown that stays on its tube serves one closure. `datum-22` takes that as a design rule: the ring's job is to set that closure's plate, so it goes on the other rim for the second closure, its rockers settle and lock again (a fresh draw of everything above), and the same plug hangs plate 2. The first plate becomes the base; the float rod stands up from it and stops 1 mm short of plate 2's register, so the plug is the depth stop and the rod cannot hold the plate proud. Your trunnion dock (pins in V-notches, an amplifier: 20 micron at a pin is 0.1 mm at the dot by tilt over a 40 mm span) is not drawn; the gun would sit on the ring's ledge instead, which is a plane and not a kinematic seat.

## 2. datum-02-seam-signature: the hold is a control, and the second dry turn is the first step

**What I looked at.** `travel-18-signature-parity`, `calc/06` and `calc/10`, the scene's own numbers.

**The specific conflict and the assumption.** The replay applies the dry turn's constant term to a gun that must be in the same place in the weld turn; I wrote "the hold is not addressed". The feeder starts and its conduit pulls on the bracket, the gas hose pressurises, the hand leaves, the fibre emits: each is a change of force, and the gun moves by force times the compliance of the chain to the room. My assumption was that nothing moves between the turns.

**What I did: revised, in place, adopting your repair.** `datum-02` has `What holds the gun between the two turns` (a 20 mm steel post at 6 micron per newton, a 12 mm steel rod at 44, a 12 mm aluminium rod at 128; the change of force in newtons), a warning when the parity term exceeds 0.02 mm, and a toggle that records the dry turn in the weld's mechanical state (feeder jogging at weld speed, gas on, laser off; `use-10-wire-first` as a check). With the rod and 1 N the term is 0.044 mm, twice the fit residual; with the aluminium rod and 2 N the replay leaves 0.28 mm rms in the scene against 0.07 once the dry turn is taken in the weld state. **Yes, I would accept a second dry turn in the weld state as the first thing the routine does.**

**Which holds the gun.** The friction arm, the hand and the crown do not have the same parity term and the 0.022 mm was quoted for all of them; the scene no longer quotes it for all. The hand is not a spring and is not modelled; the crown's boom is much softer than a post (`datum-16` uses 0.3 mm per newton for a rigid grip), which is why its cable pull is trimmed by a radial trim once and not replayed.

**Which axis the replay drives in the crown branch.** Height only: the crown has no radial slide. I had listed "the crown's Z stage as the vertical axis" and left the radial one unsaid. The radial 1x is what the nest screws, the seat, or the head's own beam-centre adjustment would take (if the laser lets software command it: `datum-13`, unknown). Your assignment of the fitted terms (`calc/10`: the constants are two thirds of the 0.29 mm rms; a static trim leaves 0.146, nest screws taking 90 percent of the radial 1x leave 0.114, a Z follow taking the vertical 1x leaves 0.043; a replay stage earns its place below a window of about 0.2 mm, vertical first) is recorded in the idea file. **Left uncertain:** what only an emitting head does, the real change of force, hot drift, the real window.

## 3. datum-07-touch-off: the biggest term was two assumptions

**What I looked at.** `travel-15-touch-stack`, `calc/03` and `calc/06`, the scene's budget bars.

**The specific conflict and the assumption.** (a) A fine stage carrying the gun and the stylus sits on the gun side, where the umbilical pulls, and its compliance is in the touch. (b) The largest term, the tip-to-dot swap error, is not a swap error. Assumption: the tip is the dot, and the tip moves.

**Your question, "where does 0.030 mm come from?"** From an assumption, and from two assumptions folded into one number: 0.030 mm is how well I supposed the stylus's thread and seat put it back after a swap (repeatability, illustrative); the other, which the first scene took to be zero, is the vector between the tip and the dot, because the stylus is at the dot only if the red pilot sits on the nozzle axis 16 mm out, and the manual documents an alignment screen precisely because it does not always (pp. 25 and 39). So the true term is unknown, better touching does not reduce it, and the dot sweep on a coupon is how it is measured.

**What I did: revised, in place, adopting your combination.** `datum-07` has `What carries and moves the tip` (a stage in the shell, about 94 micron per newton in the chain, or the gun and stylus locked on a holder at 44 with the tube stack moving: `travel-15`), a block diagram under the drawing that shows which moves and which is locked, two separate rows (`tip swap and seat repeatability`, and `tip-to-dot vector`, systematic and unknown), touch force times carrier compliance as a row, and a `Calibrated against the dot on a coupon` toggle (touch a coupon's corner with the stylus and sweep the dot across the same corner, both in stage units: the floor is the calibration's accuracy, 0.05 mm here, and the dot is still not the melt). The budget goes from 0.274 mm rms uncalibrated to 0.067 to 0.080 calibrated, so nearly all of it was the vector. The scene also opens with a finished run: a cold reader saw an empty chart. **Left standing:** the graduated tube sets the nozzle extension, which moves the dot along the beam, so a stylus is the right length for one extension only, and I have not fixed the extension the stylus is measured at (a question for Derek).

## 4. datum-09-preplaced-filler-ring: the claim was wrong

**What I looked at.** `travel-16-radial-plane` and its calc (`calc/09`): 15 degrees of yaw moves the in-section beam tilt from 32.5 to 9.9 degrees.

**The specific conflict.** "The gun's yaw about the vertical becomes free" is not what becomes free; yaw still turns the beam. **The assumption:** the wire is the only reason for the tangent attitude, and yaw is what it frees. **What I did: revised, in the idea file.** What the wire ties the gun to is the wire bracket's arrival; what becomes free is a family of attitudes in which the barrel stands in the radial plane over the bore, and the direction of the bead and of the end-of-bead departure. **Your question, which constraint did I want removed?** I wanted two different things and named one: a visible, self-seating line to track (only a preplaced ring gives it) and freedom from the wire's arrival direction (a guide carried by the ring gives it with nothing preplaced and no fusion question). I take your branch as the one that keeps the process. **The smallest coupon test I would accept for fusing a ring:** a scrap L in the laser (a 1/4 in plate on a tube offcut with a recessed corner), a 0.035 in ring laid in the corner, the recorded power and wobble with no wire feed, three passes, then a section. **Left standing:** fusion (0.62 mm^2 for a 0.035 in ring against the 0.684 mm^2 the recorded fillet needs), two starts and two stops, the proxy's real cable exit, grip-up, and the wire feeder's bracket on the ring.

## 5. datum-12-work-side-tilt: the wedge pivots at the bench

**What I looked at.** `calc/11-wedge-abbe.mjs`. I re-ran it: the seam stands 232.05 mm above the feet [derived], and 232.05 tan(1 degree) is 4.05 mm, so 1 degree of tilt moves the seam 4.05 mm, 20 mm at 5 degrees. **The specific conflict and the assumption.** I said a wedge under the base tilts the rotator about a line through the dot and the tube axis, "so the dot stays where it is"; it cannot. **What I did: revised, in the idea file.** Your question, "did you mean the ridge at the base or a pivot at the dot?": the ridge at the base, and the dot claim was wrong. What stands is the set-once form with the gun placed after the tilt; a wedge changed between trials needs the gun or a stack to follow, and only an arc keeps the dot fixed (`travel-03b`). Your two additions (the station azimuth against the lean chooses which rotation the tilt supplies; a Risley pair makes the tilt adjustable, 0 to 2a in any direction with a reduction of about 11 to 1) are recorded as read, not built. **Left uncertain:** what mean inclination Derek actually uses (the reference scene's own note says the dial reads 35 degrees at the mounting inclination), and the printed race under 5 to 17 percent of the weight sideways.

## Combinations you named

- Crown seat + soft-drive-hard-lock: adopted, in the new `datum-22-setting-ring`.
- Crown + cartridge + trunnion dock: the flip is answered there (per closure); the dock is not drawn.
- Touch-off + tube-travels stack: adopted, in `datum-07`.
- Signature + second dry turn + cascade: adopted, in `datum-02`.
- Preplaced ring or ring-carried guide + crown + orbiting crown: adopted as the two-halves branch of `datum-03b`.
- Work-side wedge + dot-centred arcs: recorded, not built.
- datum-04 follower + the stack's Y stage: recorded in the idea file, not drawn. `datum-23-wall-clip` is the follower with a body.
- datum-13, `travel-12` and `borrowed-06` are one idea: agreed; one two-minute look at the touch screen serves all three (is the head's left/right red-light alignment a run-time axis?).
- datum-11 witness pass + `travel-13`: the dot-to-melt vector from a coupon is a constant added to the setup pose; agreed.

## What I could not repair

- **The wall's eccentricity** passes every ring on the outside and every room-fixed gun; only a bore reference or a measurement removes it. A bore-finger seat removes it (`datum-21`) but its fingers stand in the beam and must retract.
- **What only an emitting head does** to the parity term.
- **The dot is not the melt.**
- **The unmeasured numbers everything here hangs on:** the gun's mass and balance point, the umbilical's pull, the tubes' out-of-round and eccentricity, rim flatness, the tack term, the plates' depth and tilt as found.

## Questions that need Derek's observation (repeated in the idea files)

Five tubes, eight positions each: outside diameter by calipers, wall thickness by ball micrometer; rim flatness on a plate with a feeler gauge; a fingernail on the bore for a longitudinal weld seam. **How is the plate held at its recess today, before it is tacked** (the rig doc says a spacer or depth-stop on the rim). The indicator on the plate face at three azimuths before and after the eight tacks on a plate you weld today (ten minutes; it sizes the tack term). Plate depth from the rim over ten plates. The gun weighed and its balance point found; the umbilical's pull at the exit. Does the wire feeder push or pull on the gun's bracket when it runs, and does anything shift when the gas starts? Can the nozzle come off, and its thread; which nozzle extension. How does the laser's work circuit close? Is the head's red-light alignment a run-time axis?

## Scenes drawn or changed

New: `scenes/datum-21-mates-on-the-tube` (a lens), `scenes/datum-22-setting-ring` (deep), `scenes/datum-23-wall-clip`. Changed: `datum-03`, `datum-03b`, `datum-02`, `datum-07`, `datum-01` (a seating control and the lens tag); tags and links only in `datum-04`, `05`, `14`, `15`, `16`, `17`, `19`, `20`. Idea files: `datum-21`, `datum-22`, `datum-23` new; wave 3 sections added to `datum-01`, `02`, `03`, `03b`, `04`, `07`, `09`, `12`, `16`.
