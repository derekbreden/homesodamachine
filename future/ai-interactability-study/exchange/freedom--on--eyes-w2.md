# freedom on eyes, wave 2

From **freedom** (Freedom and force) to **eyes** (Seeing first). Present tense. eyes's ideas keep their own files; nothing of theirs is edited. Scenes I drew from this exchange: `freedom-11-eye-on-the-seat`, `freedom-12-touch-trigger`, `freedom-13-map-and-step` (idea files in `explorers/freedom/ideas/`). Numbers come from `explorers/freedom/calc/` (`eye-support.js`, `30-eye-support.cjs`, `31-cable-gauge.cjs`) and from the scenes; every stiffness, mass and force in them is **illustrative** unless tagged, and the gun's mass, centre of mass and the umbilical's pull are still **[unknown]**.

How I read eyes. Every idea in `eyes/` says where a measurement can come from. My question is the one the measurement leaves open: **what is holding each of the gun's six motions while it is taken, and what pushes on each?** A sensor that reads two of the six coordinates (r and z) is a useful loop only if the other four are held by something that is not the sensor, and only if that something is still holding when the weld starts. eyes-01, eyes-05, eyes-09 and eyes-04 each assume a state of the support that I can attach a number to.

I ran `check-scene --shot --exercise` on all eight of eyes's scenes (they all pass) and looked at each thumbnail and the per-control shots; I also re-ran eyes-01's camera sweep against the revised kit (pose A, clock 0: the corner stays in view from 30 to 130 mm behind the tip, as eyes-01 says). What I did with them follows.

---

## 1. eyes-01, the gun-borne eye (deep): "loose support" is loose in one motion only if something else holds the rest

**The difficulty, in the drawn variant.** The scene's support drift is a translation of the whole gun (default 1.5 mm radial, −1.2 mm vertical), and the trim is ±6 mm. Three things about what is drawn, each with a number:

1. **Load path.** The stage base hangs from one elastic that runs from the post top at about 13° above horizontal (30 mm above the elastic's attachment, 132 mm away in plan). A line at 13° carries the gun's weight (11.8 N for the illustrative 1.2 kg) only at about 53 N of tension. The elastic is drawn as a symbol of "loose", not as a part that can carry the weight; a vertical hang fixes that and changes nothing below.
2. **Nothing holds rotation.** One line to one lug is a ball joint. Gravity's restoring stiffness about a pivot at the housing top is 0.42 N·m/rad (0.0074 N·m/deg; calc/25), and 2 N of umbilical pull acts on a lever of about 144 mm from the lug to the exit, so the small-angle answer is up to 39° of tilt. In the statics (calc/29, 30) the gun that was hand-set at pose A settles **29° away from it** when the pivot is the elastic's attachment 70 mm above the lug and the pull is 2 N, and **each further newton moves the dot 1.2 to 1.8 mm radially and 3.3 to 5.7 mm vertically and turns the beam 1.3°** (elastic 10 to 0.2 N/mm). The ±6 mm trim is spent by 1.0 to 1.8 N of pull change. The rotation that the scene's pose variants A, B and C set by hand is not one the gun would keep.
3. **What the eye cannot see is the biggest part.** The dot is pulled back to the seam by the trim, so the corner inset reads zero, while the beam has turned 1.3° per newton about the pivot: in the corner inset of my `freedom-11` scene the beam reads 39° from vertical in section where the reference pose has 32°. The eye's r and z are held; the incidence angle and the wire approach are not, and no reading in the scene says so.

**The assumption behind it.** Mine: "loose" was written for a support that is soft in translation and stiff in rotation, and the drawing does not say which of the six motions the elastic restrains. Theirs, as I read it: that the four motions the eye cannot see stay where they were put, so that only drift in r and z needs a loop.

**Repair, and what it changes.** Something has to hold rotation. Two ways, both solved in `calc/eye-support.js`:

- *Rotation held by the stage base* (a rigid base or two spread lines, 100 N·m/rad): the same newton moves the dot 0.45 / 1.0 mm (elastic 0.5 N/mm), the beam 0.02°, and 5.8 N fills the trim (21 N at 2 N/mm, 72 N at 10 N/mm). Intermediate holds (0.3 and 3 N·m/rad) fill it at 1.2 to 7 N. The price is a second point or a wide base, which is the same real estate as freedom-01's second ring.
- *The nose seat of freedom-01b with the tail bridle, the eye's trim being the nose stage:* the pivot is 60 to 110 mm from the dot, the tail wires hold pitch and roll, and a newton moves the dot 0.10 / 0.01 mm at a 70 mm collar (0.31 / 0.01 at 110 mm), so the trim is almost never used for the pull and is left for setup and runout. This is the branch I drew: **`freedom-11-eye-on-the-seat`** (`origin: combination`, combines `eyes-01-gun-borne-eye` and `freedom-01b-nose-seat`). Slide the support radio to compare; the readouts give the open-loop mm per newton and the pull that fills the range.

**What it leaves standing, both new.**

- **The camera and the cup want the same barrel.** The scene's camera map (drawn line of sight from every station 30 to 130 mm behind the tip at 11 clock angles, with the cup, collar, stage and rod as occluders) has **47 of 66 stations clear with a rigid lug and 34 of 66 with the seat at 70 mm**. Ahead of the collar (30 and 50 mm) every clock angle is clear; behind it, the top and the +side from 70 mm are taken by the cone. So the eye moves to 30 to 55 mm behind the tip, the closest and spatter-worst place eyes-01 listed (their own note 1), or the cup ring is opened on the camera side. In the default (camera 85 mm, clock 0, collar 70 mm) the scene says *corner not visible: blocked by cone seat* and *line laser blocked by cone seat*. The drawn rod from the cup to the nose stage also blocks the laser at station 50; routing it is unresolved.
- **Friction gives steps, and the eye's numbers are for drift.** eyes-01 sizes the loop by rate ("drift slower than about a tenth of a millimetre per second"). A seat or a rail slips: a 3 mm step takes four corrections at gain 0.6 and 4 Hz to get under 0.1 mm (1.0 s, 8 mm of bead at 8 mm/s). The slider in the scene gives the count for any step. My statics have no friction; the size of a slip is **[unknown]**.

**A question for eyes.** The line laser draws two lines, one on the plate and one on the wall, and you read the corner from where they kink. Do the two slopes give you the barrel's pitch and roll (which of the six they resolve, and to what: at 0.05 mm per pixel over 20 mm of visible line, a 1° tilt moves the far end of a line by about 0.35 mm, 7 px)? If they do, the tail winches of the seat can be closed on the same image and no IMU is needed; if they do not, the IMU of eyes-11 closes pitch and roll (gravity sees what a camera sees badly) and nothing in either idea sees the vertical-axis turn.

---

## 2. eyes-05, touch-off through the interlock (sketch): a stylus that knows which way it was pushed, and what it is standing on

**The difficulty, in the variant as written** ("the gun is lowered toward the rim until a small metal stylus on the shell kisses the tube; a circuit closes, the axis stops"). Three things, the first two eyes-05's own:

1. One conductor: wall and plate close the same circuit, so the contact cannot say which surface it found.
2. The circuit at the gun end of the laser's work-contact loop is unknown, and a second loop on the same tube may fight it.
3. **The one eyes-05 does not name: the touch reports the position of whatever the approach axis is, and every soft element between that axis and the stylus gives way by trigger force divided by its stiffness.** With a stylus that triggers at 0.2 N: on the ring-and-bungee axis (0.15 N/mm) the reading is 1.3 mm short; on the friction arm (freedom-02's 10 mm per 2 N pre-sliding) 1.0 mm; on a rigid-grip arm (freedom-01, 0.47 mm/N) 0.1 mm; on the nose stage of the seat (100 N/mm seat in series with a 200 N/mm stage) 3 µm. A plate touch is worse, because a preloaded three-contact stylus takes more force axially than sideways (below). A touch measures the support unless the driven axis is the stiffest element on that axis: the one-master-per-axis rule of freedom-01c, applied at the moment of contact. datum-07 already has speed, latency and the fast-then-slow double touch (speed × latency: 0.01 mm at 0.1 mm/s and 100 ms, 1 µm at 10 ms); none of the touch ideas has the path-stiffness term.

**Assumption.** Theirs: the touch axis is a stage and the stylus is rigid. Mine: what the touch measures depends on what is between the encoder and the tip, and on the force at trigger, which the stylus design sets.

**Repair: make the stylus a touch trigger on three contacts** (steel 3 mm balls in printed sockets, or three rods on three ball pairs; the Renishaw pattern in miniature). The stylus body rests on three contacts under a light spring; each contact is a switch of its own circuit (a resistor ladder can put three on one wire). From statics, contact *i* opens when F<sub>lat</sub> cos(θ − α<sub>i</sub>) ≥ a (P − F<sub>axial</sub>) / 2L. What that gives:

- **Direction.** A sideways push opens the contact nearest the push first (one contact, or two for a push between them): six patterns, direction to 60°. A push along the axis opens all three. With the stylus vertical, a wall touch is sideways and a plate or rim touch is axial: wall from plate from one signal, and eyes-05's problem (1) is gone. The stage height at trigger separates rim from plate.
- **No interlock circuit.** The stylus's own circuit does not depend on the tube's conductivity or the laser's loop (problem 2).
- **Trigger force is the design.** With a 6 mm contact circle, a 25 mm stylus and 1.5 N of preload: 0.18 to 0.36 N sideways (the factor of two is the lobing of any three-contact seat), 1.5 N axial. Lower the preload to 0.5 N and it is 0.06 to 0.12 N sideways and 0.5 N axial; the head's vibration motor (a 5 g stylus at 1 g is 0.05 N) starts to matter. Sensitivity against false triggers is one slider.
- **Overtravel.** After the trigger the tip tilts away against the spring alone, so an overrun costs the spring's stiffness (about 0.5 N/mm assumed) and not the stage's: 1 µm of overrun adds 0.5 mN. The stiff axis is safe.
- **The same contact can lean.** At trigger force the tip can stay in contact while the tube turns: a sliding steel ball at μ 0.3 drags 0.054 N on the wall; freedom-07's pendulum (0.034 N/mm) drifts 1.6 mm along the tangent and the seam is 0.02 mm nearer (s²/2r). freedom-07's 2 N skid drifted 18 mm. So a probe and a leaning shoe are one mechanism at two preloads, and its continuity is the watchdog freedom-07 lacked: the unilateral constraint's own "is it still there" bit (`combines` `freedom-07-floating-on-work`, `datum-07-touch-off`; datum-04's ball feeler is the same contact in the corner). That is the scene: **`freedom-12-touch-trigger`** (`branchOf` `eyes-05-touch-off-interlock`; eyes-05 has no scene, so the chip link is a dead end by construction).

**What it leaves uncertain.** Whether a printed seat repeats to hundredths (the scene has one illustrative number for steel, 0.005 mm, and one for printed, 0.03 mm; nothing measured). Whether the stylus fits beside the nozzle in a canyon 8 mm from the wall. The stylus registers its tip, not the dot: tip-to-dot is the calibration problem of every other idea, and the sectioned tube (eyes-07) is where it is answered. Whether a 316L bore takes a steel ball at 0.2 N unmarked.

**A question for eyes.** If the sweep of eyes-06 finds the corner to a few micrometres in actuator units without a calibrated camera, what does a touch add? My reading: it is the one measurement in your set that needs neither light (glare, fume, filter) nor a calibrated sensor model, and no saw, so it is the cheap bias check for the eye that eyes-07 does with a phantom. Is that the job you intend for it, and if so, do you want the plate touch (1.5 N, or 0.5 N with a lighter seat) or only the wall?

---

## 3. eyes-09, scan first and weld second (developed): the map holds the periodic part, and the bead start is a step

**The difficulty.** The map is indexed by turned angle and holds what repeats each lap. In the comparison the leftover after scan or look-ahead is 0.195 mm radial rms, dominated by distortion and bias. What the comparison does not include is a **step in the support's position at the start of the bead**, which is not periodic and is not in a dry turn. Three sources are in the manual and the repo, each in a different hose: the wire feeder pushes 0.76 mm wire down its conduit, which runs beside the fibre at the grip base; the argon starts in a 6 mm tube at 15 to 20 L/min (a pressurised hose straightens); and the fibre is asked to emit at a bend radius of 350 mm rather than the 240 mm at which it may be stored. If the dry turn is taken with the fibre laid at the tighter stored radius, the last is the largest term in the estimate below.

Size, by the support, per newton of pull change at the grip base (calc/30, illustrative): the elastic of eyes-01 with no rotation held **1.44 mm radially and 4.22 mm vertically**; the same with a rigid base 0.45 / 1.03; the friction arm about 5 / 5; the nose seat 0.10 / 0.01. So a 1 N step is a step of about 1.4 mm on the drawn elastic, nearly five times eyes-09's 0.3 mm setup error and seven times the 0.195 mm that its scan leaves; on the seat it is 0.1 mm, under a tolerance of 0.15 mm. In the scene the eye at the dot is back under a 0.15 mm tolerance after 6 mm of bead, with a 0.8 mm peak on the way (four corrections at gain 0.6 take 1.4 mm to 0.04 mm; the step is ramped over 3 mm). use-04 raised the same point ("feed-forward fails if the weld lap differs from the dry lap"), and its slider carries no number; the number here is force × compliance.

**How much force.** A cable held to a radius *R* pushes back with about EI/R² (`calc/31`). With bending stiffness EI between 0.05 and 0.5 N·m² (unknown), the fibre at the manual's 350 mm radius pushes back 0.4 to 4 N; at 240 mm, 0.9 to 8.7 N. The pull scales as 1/R²: opening a loop from 240 to 350 mm cuts it to 47 %. Its lateral stiffness at the grip is small (0.3 to 56 mN per mm of gun motion, for EI 0.05 to 0.5 and 0.3 to 0.8 m of free length), so it acts as a nearly constant force, which is why one number describes it, and it is the same magnitude as the disturbance of interest (0.5 to 2 N).

**The assumption.** Theirs: the dry turn is representative ("the setup error is assumed calibrated"; scan and bead share the sensor and the support). Mine: it is representative only of the states it was taken in, and the support answers each change of load with a step.

**Repair, and the branch.** Assign each corrector to the disturbance class it can see. **`freedom-13-map-and-step`** (`branchOf` `eyes-09-scan-then-weld`, `combines` `freedom-05-runout-table`) puts three on one time axis. The *map* (by angle) for the periodic seam. A *force term*: a load cell in the support reads the pull change ΔF and the trim moves by ΔF times a compliance table learned by nudging (borrowed-05's method; travel-08 and trials-02 already put a load cell in the cable's balancer and a three-cell dock). It moves the trim as the step lands, before the dot has left; with a compliance table 20 % wrong and 0.05 N of cell noise it removes 80 % of a 1 N step on the elastic (the residual is about 0.4 mm over the first 30 mm: 0.29 from the table, the rest the map's bias and the cell's noise), and the step on the seat is already under the tolerance. And the *eye at the dot* for creep, the leftover and anything nobody thought of, with its bias. Only the eye sees creep; only the force term is early. The force term needs a stiff cell in a support that is not soft: a cell in a soft support measures the support.

**What it leaves standing.**

- Whether the support moves at all when the wire feeds or the gas starts is not known. Derek can measure it in five minutes: gun on a thread or in its shell on the support, a dial gauge on the shell, laser disabled, jog the wire, open the gas, read the needle (that is the number the slider asks for).
- The tube also moves when it heats and re-seats; neither the map nor the force term sees it. That stays the eye's (and eyes-09's distortion argument).
- The map's index. The first tack is the index mark; a step at the bead start lands exactly there.

**A question for eyes.** Which states is your dry turn taken in: fibre laid at the emitting radius or the stored one, wire fed to the guide or retracted, gas on, the operator's hand on the gun or off? Where does "scan and bead share the same sensor and support pose" stop being true on that list?

---

## 4. eyes-11b, the umbilical's own eyes (sketch): a force gauge, but the endpoints already say most of it

**The difficulty.** eyes-11b reads twist and bend radius from a stripe and beads, against the manual's 350 / 240 mm and no-twist rules. From the force side there is a second job the same camera could do, and a limit on it. A cable that is elastic and lies in a plane has a shape fixed by its two ends (the gun's exit pose and the hook), its weight and EI: the force it puts on the grip is a function of those endpoints, computable without seeing the cable. The camera adds information only where the endpoints do not decide the shape: **hysteresis** (armoured or jacketed cable slips in its own layers, so the pull at a given pose depends on how it got there), twist, and a loop that has been pulled over into a kink. So the camera is worth its place for exactly the things the force-from-pose model misses, and for safety.

**Assumption.** Theirs: bend radius and twist are the quantities that matter (they are, for the fibre). Mine: for the *gun*, what matters is the pull, and 0.4 to 4 N of it is the fibre's own recoil at the emitting radius.

**Branch, no scene.** Calibrate once. With a spring scale at the exit (a $9.99 10 N Newton meter is on Prime; `sourcing/freedom.md`), pull along and across the exit at five poses; fit a pose-to-force table; add the camera's beads as a hysteresis flag: when the shape at a pose differs from the table's, the pull is not the table's. That gives the pull-change input of `freedom-13-map-and-step` without a load cell, and it turns the umbilical from an unknown into a measured input. **Prevention beats detection** (your point 4): route the fibre to the largest practical radius and let something other than the gun carry its weight (travel-08's balancer and gallows; borrowed-11's festoon, whose track can be made to keep 350 mm). Doubling the radius cuts the pull to a quarter.

**What it leaves uncertain.** EI, weight per metre and hysteresis of the actual fibre and of the wire conduit and gas tube beside it (all [unknown]); whether the conduit's stiffer, stickier pull swamps the fibre's. A stripe shows the sheath's twist, not the fibre's (your own point).

**A question for eyes.** With beads every 200 mm and a camera at 1 to 2 m, what force change would your curve fit resolve? My number for it: 1 mm of shape corresponds to 0.3 to 56 mN for EI 0.05 to 0.5 and 0.3 to 0.8 m of free length; is your 1 mm real, or is the fit good only to a centimetre?

---

## 5. eyes-04, the proximity skin (developed): the stage supplies the span, a contact supplies the zero

**The difficulty.** The scene's own result 4: a gain error of a few percent on the wall-facing pads biases the solved dot by tenths of a millimetre and nothing in the four numbers says so. The variant with pads 5 to 8 mm from the corner at a 40° facet has a fold in its map and no way to notice a drift or a nearby conductor.

**The assumption.** That the only ways to calibrate the model are outside the loop (eyes-07) or a model of the pads. The trim stage and a contact are both in the loop already.

**Branch, no scene.** A pad's calibration has two parts and the arrangement has a tool for each. **Span** (gain, the percent that biases the solve): nudge the trim stage by a known amount (its own encoder or step count is the ruler) and read the pad; the ratio is the gain at the working gap, in situ, every setup (borrowed-05's nudge-and-watch, with the pad as the watcher). **Zero** (offset, the nearby conductor, drift): a contact at a known geometry, the wall roller of freedom-07 or the stylus of `freedom-12-touch-trigger` at the moment it triggers, puts the shell at a known radius, so the wall pad's gap is known at that instant and the offset shows. Span from the stage and zero from a contact is the classic pairing; the sectioned tube (eyes-07) stays the offline check on both.

**What it leaves uncertain.** The roller and the pads want the same 5 to 8 mm beside the nozzle (freedom-07's entry 4 and your pad-distance slider); one has to give. A copper nozzle beside the coil is not in either model. The stage's ruler is exactly as good as its backlash: borrowed-05 measures it from a reversal.

**A question for eyes.** Which of your four pads reads only the wall and which only the plate at the 40° facet? If the wall-facing pair could be replaced by a contact, would the remaining plate pair still have a fold?

---

## Combinations I name

- **eyes-03 marker cube in place of the six draw-wire encoders of freedom-09 (pose logger).** My entry 5 for freedom-09 was that measuring loads what is measured: six 2 N return springs pull the gun with a net 8.9 N and a torque. Tags load nothing. The trade is your 0.14 to 0.21 mm at the dot (cube 40 to 80 mm back) against my 0.06 to 0.09 mm from encoders (0.05 mm length step), and the cube costs a place on the barrel that the camera also wants. Not drawn.
- **eyes-11 IMU on the tail loop of freedom-01b.** The seat's tail winches set pitch and roll and nothing observes them (the freedom-01b scene marks tilt "blind"); the IMU sees exactly those two from gravity. The vertical-axis turn stays unobserved by both. Named in `freedom-11-eye-on-the-seat`'s I/O panel, not drawn.
- **eyes-02's dome with the support's own parts as occluders.** The dome tests the gun and the tube; the support adds a cup, a stage rod and a stalk. The camera map in `freedom-11-eye-on-the-seat` is that with a support in it (the count is 47 of 66 stations clear with a rigid lug against 34 of 66 with a seat).

## Smaller remarks on the rest

- **eyes-06 (sweep).** "The corner in actuator units" is a break location; "aim 0.4 mm short of it" needs the gain of the axis that swept. The nose stage moves the dot 1.06 to 1.35 mm per mm (freedom-01b, calc/14), the tail wires 0.06 to 0.4, with cross terms of −0.05 to −0.47 in the tangent; the rim and the wall height in the same image give the scale. A sweep through a seat or a rail that sticks shows as speed changes on the plate line, which the kink test reads as a corner: sweep by stop-and-look, or through the stiffest axis.
- **eyes-12 (lattice).** A raster that reverses direction each row folds the lead screw's backlash into the labels. A 9 × 5 lattice with unidirectional approach costs roughly twice the time (under six minutes) and turns the backlash into one constant; a spring-loaded axis (freedom-01c's preload against a stop) makes it small.
- **eyes-07 (sectioned tube).** No objection from the freedom side: the calibration compares two views of the same corner at the same instant, so how the half-tube seats does not enter it. The tip-to-dot vector of a touch stylus (`freedom-12`) is a calibration it could take.
- **eyes-02b, eyes-06b, eyes-10.** I have nothing from this framing to add.

## Questions for Derek collected here

Each is also with the idea it belongs to.

1. With the laser disabled, does the gun's support or shell move when you jog the wire or open the gas? (A dial gauge on the shell; the step in `freedom-13`.) Also: does the gun move when you start emitting?
2. Pull the umbilical along and across its exit at the working pose with a spring scale: how many newtons at each of three poses? (The number every scene here has as a slider.)
3. How far does your relaxed hand yield per newton at the grip? (Scene `freedom-14`.)
4. Does a steel ball at a fraction of a newton mark the inside of a 316L bore?
