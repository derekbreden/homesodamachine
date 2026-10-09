# datum: the seam is the datum

Framing: the pose that matters is gun-to-corner, and the corner belongs to each tube and plate. Which features of the work (rim, OD, bore, plate face, ports, register hole, tacks, the joint itself) can establish or verify position; can the gun be located relative to the work instead of the room; what does a reference on the work make unnecessary.

Source tags: **[Derek] [repo] [manual] [derived] [unknown]** as in `context/shared-context.md`. A number with none of those is **illustrative**.

## Wave 1: first look (written before developing anything)

Twelve arrangements the framing suggests. Silly ones are in on purpose.

1. **Datum chain.** Draw the dimension chain bench, rotator, nest, tube length, rim, seat depth, plate face, corner, and let the reader pick which link the gun is referenced to (room / nest / rim / plate face / seam directly). Shows which unknown each reference makes unnecessary. Nothing moves; it is a way of seeing.
2. **Seam signature by dry rotation.** Park the gun with the dot on, turn the tube once, log dot-to-seam offset against table angle, fit a small model (centre, tilt, seat height, ovality), replay it as feed-forward to a fine axis. Software observes in the dry run, moves in the weld run.
3. **Rim crown.** A slewing ring seats on the tube rim (spigot in the bore, face on the rim). Its non-rotating half carries a boom and the gun. The gun is carried by the work, so the runout the room-fixed gun sees is not seen. Tether prevents circling; counterweight balances.
4. **Port-pin mast (branch of 3).** Two pins in the plate's ports carry a mast and hub: a datum at plate centre, plate clock and plate face, not the rim. Silly first (the plate is only tacked, the ports are the purge path); the useful form is the depth stylus.
5. **Corner follower.** A ball feeler rides in the corner itself, ahead of the dot. Its two deflections are the corner position, and the tacks announce themselves as bumps. Two leads give offset and yaw.
6. **Fiducial collar.** A printed ring on the OD near the rim carries tags. A camera on the gun shell reads them: the tube's pose in the gun's frame, runout included. Software observes and moves nothing: a seam-frame flight recorder for the hand-held weld, or LED cues to the hand.
7. **Through-the-wall eddy sensing.** A coil outside the OD at the weld azimuth sees the plate step behind the 1.65 mm wall: plate-face height from outside, no line of sight. Depends on skin depth versus wall.
8. **The stylus is already there.** The wire tip is aimed at the dot; the nozzle is removable. Touch the wall and plate with the wire (or a stylus threaded in place of the nozzle) in a dry run, detect by continuity, and the dot is zeroed to this tube's corner mechanically.
9. **Preplaced filler ring.** A split ring of filler wire lies in the corner. It is a visible, self-seating line to track, and it removes the wire-approach constraint (the gun need not lie tangent). Flawed first (fusion of a preplaced ring, a ring that will not stay put); kept for what it does to the geometry.
10. **Clear twin.** A see-through replica of the corner (clear tube, printed plate) lets an outside camera see the true dot-to-corner offset, to calibrate a cheaper estimator that is then used on the real tubes.
11. **The laser writes its own datum.** A low-power scribe pass leaves a ring of ticks and a witness line on each plate. The marks give an along-seam angle datum for that tube and a witness of where the beam really lands compared with the dot.
12. **Tilt the work about the dot.** The three rotations about the dot done on the work side (a cradle whose centre is the dot) instead of the gun side. Silly (the rotator is heavy); useful form is a fixed wedge or a hole-axis tilt set by hand.

Also written down while looking: the head's own left/right red-light alignment (manual pp. 25, 39) is documented only as a touch-screen alignment step, but it means the head has a lateral beam-centre adjustment. If it can be commanded at run time it is a fine axis with no mechanism at all. **[unknown]**: range, resolution, whether the RS232 port exposes it (manual p. 16).

What the twelve share, and one thing the framing shows that the physical reading hides: the joint is a circle, so **rotation of the gun about the tube axis does not change the gun-to-corner pose.** One of the six degrees of freedom is free by symmetry. A tether only needs to keep the gun from circling to a bad azimuth; it does not need to be stiff. This is also why the tube-turns and gun-orbits versions of the same hardware are the same problem for pose and different for cables.


## Wave 1: what I chose to develop, and why

Deep (several rounds, in the idea files): **datum-02 seam signature** and **datum-03 rim crown** (with branch datum-03b orbiting crown). Developed: datum-01 chain, datum-04 follower, datum-05 collar. Rough scenes: datum-06 eddy, datum-07 touch-off. Sketches without scenes: 08 to 13. I picked the two deep ones because they answer the framing from opposite ends: 02 says "don't hold the gun to the tube, learn the tube"; 03 says "hold the gun to the tube, mechanically". The datum-01 scene came first because drawing the chain was the quickest way to ask what a reference on the work makes unnecessary, and the answer set the order of the rest.

## Log of what changed my mind

Numbers that moved something (scripts in `calc/`, outputs beside them):

- **Symmetry.** The joint is a circle, so rotating the gun about the tube axis leaves gun-to-corner pose unchanged. That made the crown's tether easy (soft cords, only to stop wandering) and made "tube turns" versus "gun orbits" the same problem for pose. I did not expect it to matter for the cable until I built datum-03b.
- **Seam signature (calc/seam_signature.py).** At the rig's own runout limits plus a 0.20 mm setup offset the uncompensated dot is 0.22 mm RMS off; a 24-sample dry rotation with 0.05 mm noise leaves 0.022 mm. The stage demand is tiny: 0.029 mm/s peak at 8 mm/s and +/-0.37 mm stroke. I had expected the axis to be the hard part. It is not; a sensor bias that repeats with the table angle is (0.05 mm of it takes 0.007 mm to 0.036 mm RMS), and so is hot drift (0.10 mm over the lap leaves 0.061 mm).
- **Crown statics (calc/rim_crown.py).** In the reference opening pose the nozzle tip is 5.0 mm above the rim and 55 mm from the axis, and the gun's centre of mass is about 118 mm out. The first ring (a spigot in the bore) sweeps through the beam; the fix is to locate on the outside of the tube. The counterweight has to weigh about as much as the gun. Rim pressure (about 0.05 MPa) is not the problem; tipping is.
- **Orbiting cable (scene datum-03b).** The gun's cable exit points away from the axis, so a hook on the axis needs a U-turn (bend radius about 16 mm against the fibre's 350 mm emitting limit), and a wrap on a laid-flat ring track needs about a metre of radius and about 8 m of cable for 380 degrees, against a 5 m fibre. I had assumed a track a bit bigger than the tube would do.
- **Eddy (calc/eddy_skin.py).** My first estimator (steepest-edge search) failed in 82% of simulated scans; my first Python kernel was truncated and gave a falsely good 0.5 mm RMS. Fitting a template of the whole response works (0.13 mm RMS at 15% blur error) and puts the whole problem into calibration.
- **Fiducials (calc/tag_lever.py).** Tags on the vertical outer wall are seen 70-78 degrees off-normal from a camera above the rim and are tiny; tags on the top face of a flange are seen at about 30 degrees. The lever arm from tag to seam, times tilt error, is the accuracy.
- **Follower (calc/follower_leads.py).** The curvature term s^2/2r is big (0.81 mm at 10 mm) but known; the killer is lead times yaw (0.175 mm at 10 mm and 1 degree). Two leading feelers solve it at 1.4 to 2.2 times the noise; a symmetric pair does not help because the trailing one rides the bead. And the wire is ahead of the feeler on the same side: the clearance test in the side view shows negative room at 20 degrees elevation and a 6 mm lead.
- **Touch-off (calc/touch_off.py).** A stylus is about ten times better than the nozzle at the same repeatability, because the nozzle is 16 mm short of the dot.
- **Datum chain (calc/datum_chain.py).** With illustrative spreads the rim reference leaves 0.85 mm worst case in height (seat depth dominates) against 0.23 for the plate face. Shrinking the two unknown spreads to 0.10 mm keeps the order and shrinks the gaps: the honest message is "measure those two before deciding".

## Sourcing highlights (details in `sourcing/datum.md`)

- Creality CR Touch probe: Prime confirmed, $34.99, 1.7K ratings, "200+ bought in past month", rank #128 in 3D Printer Accessories. A switch-type probe in real volume; fit and force on a gun shell unchecked.
- Arducam 100 fps mono global-shutter USB camera (OV9281): Prime confirmed, $49.99, 100+ bought in past month, rank #110 in Webcams.
- Mini linear stage with NEMA 11: Prime cards from about $49 to $60; sales evidence moderate (34 ratings on the first card).
- Inductive switch LJ12A3-4-Z/BX: Prime confirmed, $6.99, 386 ratings; an LDC1612 coil board has no Prime route I saw (about $16 at Digi-Key by search snippet, stock unchecked).
- Ruby-ball CMM stylus: $21-27, weak sales evidence (2-8 ratings): a niche part.
- 6 in lazy Susan turntable: $6.95, 1.1K ratings, 300+ bought in past month; not a drop-in for a crown (ball circle and no central opening, unchecked).
- Clear acrylic tube 125 mm ID x 130 mm OD, 6 in: $15.99, 76 ratings; not the steel tube's bore or wall.
- Where nothing was found: an LDC1612 module on Prime; digital indicators with data output were not looked up.

## Kit issues found (also in the return)

- `WK.app` gives no public before-render hook. The scenes that re-pose the gun each frame use `app.onFrame`, which runs before render and returns false when idle: fine, but it needs care that a slider handler pose the scene itself.
- Custom-stage scenes have no built-in legend and stage badges overlap the SVG's top-centre (I left the top 60 px of the SVG clear).
- `app.inset.markVisibility` recolours the inset frame and writes the caption for one target; for many targets I set the frame and caption myself (class toggles on `ins.el`).
- `check-scene.mjs --exercise` flags controls whose only effect is a readout or an animation speed (time-lapse, mass sliders); I left those.
- `gun.dotOffset` can be wrapped to add scene terms (seat depth, tilt); the corner inset follows it. This is undocumented and worked well; a documented hook would help.
- Puppeteer console errors for negative `<rect>` widths stop the checker: clamp rect sizes in SVG scenes.

## Wave 2: exchange with trials, the examples, and what I borrowed

### The exchange (partner: trials)

Read all seven trials scenes (exercised, per-control shots looked at) and their idea files. Their arrangements are almost all room-referenced (dock on the bench, map keyed to the rotator, judge cameras in the room); the tube's own rim, ports, wall and plate are used only through the camera. Five ideas taken up: `trials-04` (deep), `trials-02` (deep), `trials-11` (sketch), `trials-14` with `trials-03` (sketch), `trials-16` / `trials-04b` (sketch). The write-up is `exchange/datum--on--trials-w2.md`; the scenes that came out of it are `datum-14`, `datum-15`, `datum-17`, `datum-20` and (with the examples) `datum-16`.

What moved my mind in the exchange:

- **A station is a fixed point in the room.** So anything that varies with table angle in a judge's reading has to come from the tube, and turns with the tube. That is what makes a judge's bias separable from the room's, and what makes turning the tube in its nest a test.
- **The judge cannot score what it is built on.** A map replayed from judge readings reproduces the judge's bias and the judge then reads it at its noise floor (`calc/owners_model.js`, and the yardstick scene). At a bias of 0.06 mm the judge passes a replay that truth fails.
- **The ownership route saves almost no time.** I expected the split (rig, seat, work, bias) to make relearning cheaper. In the model it saves time only for a lift and return; the value is attribution and an unbiased number. (146 s for a relearn at N = 3, against 49 s for one diagnostic lap and then 0, 64 or 128 s of touches.)
- **Dock coordinates stop carrying a trial once the corner is probed each time.** What the dock can still do is notice; a corner in the dock (a coupon) separates gun and camera from the rest.
- **The "counterweight as heavy as the gun" in `datum-03` centres the assembly on the axis.** Stopping a tip needs about 0.23 kg and contact all round about 0.7 (illustrative masses). I had written the first number as if it were the requirement. Corrected in `datum-03`'s scene and idea file.
- **The register hole is not visible from the weld side.** It is a blind pocket in the plate's inside face, drilled after cutting (`hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py`). The ports are, but they are symmetric, so the plate's clock is known modulo 180 degrees from above: enough for every even harmonic.
- **The wire has to lean outward to clear a curved wall.** Lean of about L/2R over cos(elevation); 4.8 degrees for the drawn geometry. `use-10` draws the wire at the dot by construction and never meets the wall.
- **A camera over the bore sees the corner displaced from the rim edge by 6.35 x tan(line of sight to the axis).** 1.3 mm from 300 mm above the axis. Every observation idea that reads "dot against rim edge" carries it.

### Derek's examples, in this framing

Suspension: Derek's loops carry from the room; the arm that holds the shell has a base, and the base can stand on the tube. `datum-16-loops-carry-rim-locates` puts the loops on a gallows and the boom on the crown. The rest follows from the statics: the weight's moment goes to the loops through the split of the two wires, the crown keeps only the cable's pull, and a stiff vertical support fights the rim (stiffness times the face wobble). Table opening: `datum-18-flush-to-the-table` reads the tabletop as a surface plate, makes the shelf a servo on a flush touch, and finds the tube in a loose hole by three wall touches. The monitor arm follows the suspension case: an arm-class support whose base is on the crown is the same statics with a friction window in place of loops. `examplesTreatment` in the return records what the framing saw that the explorers who began with the examples did not.

### Borrowed

- **From trials:** the puck's kinematic seats and their lift-and-return repeatability (10 to 20 micrometres at the seam) as the "nothing moved" case in `datum-14`; the dock's weigh-in (45 to 90 g per newton) and the swap interlock as the readings in `datum-15`; the dot probe's knee and focus signals (`trials-03`) as the probe run on the coupon and in `datum-20`; the notch tube's 34 degree window (`trials-05`) and the judge-separated-from-the-controller principle as the yardstick's sources of truth; `trials-17`'s nuisance-factor table as the lifetimes in `datum-14`; `swap_budget.py`'s lap and swap times.
- **From freedom:** the stiffness set for vertical supports (balancer 0.02, long bungee 0.2, wire 200 N/mm), the auto-null idea (read the arm's force, retune the supports) and the 0.3 to 0.9 mm/N rigid-grip compliance in `datum-16`; the 40 mm/N wander of a soft-hung gun in section 5 of the exchange.
- **From room:** the table opening's geometry, "the table plane is the rim plane", the loose Ø160 hole (16.5 mm each way) and finding 6 (nothing detects a plate deeper or shallower than expected) in `datum-18`.
- **From borrowed and travel:** the festoon as the remedy for the cable's moment on the crown (`borrowed-11`); `travel-13` (print to adjust) as the limit of a slow tube-side stage.
- **From use and eyes:** `use-10-wire-first` for the wire in the dry lap (`datum-20`); `eyes-07` (sectioned tube) as the static neighbour of the twin.

### Kit issues found in wave 2

- `WK.app({stage:'custom', minWidth})` makes the whole page scroll sideways at phone width (390 px): the header text is cut off, because the stage's min-width widens the page grid. The stage itself is readable. The 3D scenes overflow the same way in the header at 390 px (wave 1 scenes included).
- `check-scene.mjs` uses a 20 s load and 15 s ready timeout; under machine load (load average 35 to 50 while eight explorers ran) most trials scenes timed out on the first run. I used a copy with longer timeouts kept in my scratchpad; the tool itself is unchanged.
- A `noVisual` radio that only changes readouts (`datum-16`'s split-tuning choice) reads as "no visible effect" until marked; readouts and badges are not counted as output by the checker.
- The shared scratchpad holds other explorers' files; my helper scripts are in `scratchpad/datum/`.

## Wave 3: travel's critique, and a new region (shells, seats and interfaces formed by the work)

### What travel found, and what I did (details in `exchange/datum--reply-to-travel-w3.md`)

Five of my ideas were run through travel's framing. The crown's seat was drawn, not built (a ring exactly on the outside's centre); the signature ignored the hold between its two turns; touch-off folded two assumptions into one number; two sketches had wrong claims (the preplaced ring frees the wire's arrival, not the yaw; a wedge under the base pivots at the bench, not the dot). I revised `datum-03`, `03b`, `02`, `07` in place, corrected the idea files for 09 and 12, adopted the soft-then-lock seat and the per-closure ring into a new combination scene (`datum-22`), and held one point back: **the wall's eccentricity is common to a room-fixed gun and to every ring on the outside, so it cannot cancel the crown's radial win; what decides it is the wobble left after indicating minus what the pads pass** (`calc/mate_harmonics.js`).

### The new direction: what I tried

- **Started from what the tube's own features let a part do.** Listed the mates: rim (plane), outside (cylinder), bore (cylinder), plate face (plane), ports (two holes with 82 degree countersinks and a 1/4 NPT thread), the plate's slip fit, the blind register (not visible from the weld side), the float rod, the wall at the station, plate 1's ports from below (closure 2 only). Counted the freedoms each fixes.
- **Found the organising fact: motion versus shape.** A part on the whole circle follows the tube's rigid motion and none of its shape (ovality, lobing, wall eccentricity); the pads or fingers that centre it pass harmonics k-1 and k+1 at gain 1 into its own centre. A mate at the station reads the shape too, up to the phase its lead costs: 2 sin(n s / 2R). This is `datum-21`, a lens.
- **Found the second fact in the repo's own numbers: the slip fit does not square the plate.** The plate's diagonal is 123.607 mm and the bore is 123.698 mm; it can lie at any tilt without touching the wall on both sides. Seat depth and tilt were the two links left under the rim reference; they are how the plate was held, not properties of the tube. `calc/plate_seat.js`.
- **Made it into an arrangement (`datum-22`, deep).** The ring is the crown's ring; its ledge is at once the seat of a temporary plug and the race of the upper ring. The plug hangs the plate by its two ports (cone collars in the countersinks, one pin in a slot, a T-head under the plate; the thread is never touched) and three set-screw feet set its depth; the plate's mate is exactly six constraints. Arms at 22.5, 157.5 and 292.5 degrees stand 22.5 degrees from every tack. The tack pull is the residual (constant plus a first harmonic about half the spread between tacks); the feet clamp the plate while the tacks cool. The flip: the ring is per closure by construction. The plug is the depth stop in the second closure, so the float rod (1 mm short of the register) cannot hold the plate proud.
- **Drew the local alternative (`datum-23`).** A hook on the gun's nose straddles the wall a few millimetres ahead of the dot, a roller on the bore, a wheel on the rim, a spring pad on the outside on one radial line (a squeeze, not a bend: contact half-width 7 micrometres at 8 N). The weight hangs from a balancer wire. On the default tube 0.03 mm rms radial against 0.10 to 0.13 for the others; the cost is the lead (2 sin(n s / 2R)), the cable's pull against the preload, heat, and a weld seam on the bore if there is one. The plate is not known to it.
- **Tried and failed, kept as rows of the atlas:** a mast on the ports as a gun carrier (the plate face gives height and tilt, but the slip gap is the radial term and a mast on the axis needs a long boom); threaded studs in the ports (galling; the ports are used again for the elbows); plate 1's ports from below (it centres the tube's bottom end, not its working end 146 mm up); a nose skid on the rim (a dry skid drags 1.25 N at 5 N; a wheel is a row of the hook).
- **Sketched only:** an index ring (a printed slit ring or a ring of magnets on the rim, read by a fixed sensor) giving the tube's own angle at the gun, so a replay is keyed to the work; the open question is whether the tube slips in the nest at all.

### What moved my mind in wave 3

- The repo already describes a rim-referenced depth-stop for the plate ("a 1/4 in spacer / depth-stop on the rim"); the new idea is to keep it, make it hold the plate, and share its plane with the gun.
- The travel critique was right on four of five and half right on the fifth (n=1); the half that is mine is that the crown's lasting case is height, and height is not won by the rim either.
- A bore-finger seat removes exactly the wall eccentricity and nothing else, and it stands in the beam corridor (the scene's clash test fires at the station): fingers are for seating, then retract.
- A 10 mm bearing roller (MR105ZZ) is too big for the gap beside the wire; the drawn roller is 5 mm.

### Kit issues found in wave 3

- `gun.addRing` and `gun.addShell` are enough to attach a bracket and a collar to the nozzle; a public hook for `gun.dotOffset` (wrapping it was undocumented in wave 1) would help every scene that adds terms.
- The Chrome tab group is shared: another session's clean-up closed my first tab and its group; I opened a second and closed it at the end. Reading Amazon result pages by same-origin `fetch` in a page script is faster than clicking.
- `WK.app({stage:'custom'})` scenes centre their SVG in the stage, leaving a 100 to 190 px empty band at the top in several of my older scenes (reserved for badges, which are now a strip above the stage); not changed.
- `check-scene --exercise` flags controls whose effect depends on another control's state (step, branch) as "no visible effect"; I marked them `noVisual` with the reason in the help text.

## Open threads

- **Ask Derek (short, in priority order):** (1) **how is the plate held at its 1/4 in recess today, before it is tacked** (the rig doc names a spacer or depth-stop on the rim; what keeps the plate there is not recorded); (2) the ten-minute test that would size the tack term: an indicator on the plate face at three azimuths before and after the eight tacks, on a plate you weld today; (3) five tubes, eight positions each: outside diameter (calipers), wall thickness (ball micrometer), rim flatness (feeler gauge on a plate), and a fingernail on the bore for a longitudinal weld seam (`datum-21`, `datum-23`); (4) plate depth from the rim over ten plates (depth gauge); (5) what accuracy the dot needs against the corner (every window slider in the set is a placeholder); (6) gun mass, centre of mass, the umbilical's pull at the exit; (7) whether the nozzle comes off and its thread, which extension the dot is set at, how the laser's work circuit closes, whether the head's left/right red-light alignment is a run-time axis; (8) the turn-in-the-nest indicator test that would replace every amplitude in `datum-14`; (9) a phone photograph of the bore from 300 mm and 150 mm above (`datum-19`); (10) whether anything may touch the rim, bore or outside of a finished tube (`datum-16`, `datum-18`, `datum-22`, `datum-23`).
- **Bench tests that would replace assumption with data:** the tack indicator test above; the five-tube survey; probing one coupon and one tube ten times each after re-seating the gun in its shell and after moving the camera 0.3 mm (`datum-15`); the turn-in-the-nest test (`datum-14`); a coil board and a scrap tube (`datum-06`); the scrap-L test for fusing a preplaced ring (`datum-09`).
- **Combinations still to build:** the setting ring with bore fingers (a ring centred on the bore, then locked: the plate's gap round its edge even, the wall eccentricity gone); the wall clip on the setting ring's ledge (the clip supplies the radial reading, the ring the plate); the wall clip as `datum-04`'s follower with an actuator behind it that delays the reading by s / v; the crown's lower ring carrying the ports' clock and an angle scale for `datum-14`; the touch probe on the crown's Z stage.
- **Directions not developed:** the index ring above; the work in another orientation (a horizontal tube axis: a saddle on the top is a gravity-seated crown); a bought positioner judged by repeatability over one lap and stiffness in two axes; a second observer that separates the dot from the camera on the coupon; lift-away at the end of the bead as the ring's or the plug's second job (a plug that lifts out is already a straight lift).
- **Standing problems that no idea here solves:** the dot-versus-melt term beyond what the wire vector reaches; hot drift during the weld; heat and spatter on anything in the pocket (a roller or wheel within 20 mm of the pool: steel only); fume and glint for any camera; whether a dry-run hold and a dry-run judge say anything about a weld; what only an emitting head does to the parity term; the tack term; a locked ring on a tube that grows 0.03 to 0.06 mm when hot.
