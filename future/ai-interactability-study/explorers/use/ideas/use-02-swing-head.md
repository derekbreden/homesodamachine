# use-02-swing-head: the arm brings, the seat locates

Scene: `scenes/use-02-swing-head/index.html`. Origin: swarm (framing: the day of use). Maturity: deep.

## Picture it

The X1 Pro sits in a printed sleeve clamped to a short rail behind the gun, on the end of an arm that swings about a post beside the rotator. Halfway down the barrel a flange carries three steel balls. When the arm has brought the gun beside a fixed fork with three grooves, a small plunge along the barrel axis drops the balls into the grooves and the fork takes the gun's weight; the arm and its spring-loaded carriage let go. To change a tube, the plunge lifts the balls out, the arm swings the gun about 100 mm out over the tube wall (illustrative), and the tube can be lifted out of the nest. A hand still fires the trigger.

## The proposal

Software commands **states**, not positions: approach, seat, retract, park. Two axes do it: a **swing** (rotary about a vertical post, or a short slide in the limiting case of a distant post) that only moves the head between "over the seat" and "clear of the tube", and a **plunge** along the gun's own barrel axis (about 46 mm of stroke: retract 40 mm, seat, and a few millimetres of float). Precision is geometric and lives in a three-ball, three-groove kinematic seat at the collar; the arm, bearing and rail are allowed to be sloppy so long as they bring the balls within the fork's capture range. The fine pose (the gun's position and tilt relative to the shell) is set once per campaign by three adjuster screws, guided by the dry-run camera, and is manual.

The plunge axis is the "lift the head straight away" that the end of every bead is said to need (the coordinator's shared context, attributed there to guide 46; the guide's own text says only "release the trigger, then the pedal", so the lift-away is unconfirmed, wave 2): it is also the retract, the seating stroke and clearance over the rim, in one motion. If no lift is needed the plunge keeps the other two jobs.

## What carries the loads, what establishes position, what is free or restrained

- **Travelling** (parked, approaching, retracting): gun, shell, back plate, tie-rods and nuts (which pull it back), or the float spring (which pushes it forward), carriage, rail, arm, swing bearing, post, bench.
- **Seated**: gun, shell, flange, three balls, fork, seat arm, post, bench. The carriage keeps pressing through the float spring and the tie-rod nuts lift off; the arm and rail no longer set the pose. The scene draws both paths and switches the amber load path when the plunge goes past zero.
- **Position** comes from the six ball-to-groove contacts (a Maxwell coupling). The dot's position relative to the seam is that seat plus the gun-to-shell trim plus the tube's own runout.
- **Free**: arm position within the capture range (slop is a slider; capture 3 mm is illustrative). **Restrained**: all six degrees of freedom at the seat once seated; the arm swings only about the post and the carriage moves only along the barrel axis.
- **Driven**: swing and plunge. **Manual**: the fine trim, the tube, the trigger, snipping.
- **The umbilical** is carried by its own hook, not by the gun; see the cable entry below.

## What software could command, observe, and what stays manual

- **Command** (proposed): swing to park / to the seat side; plunge to retract / to seat; the existing rotator (speed, direction, degrees) to run the dry lap. Never the laser [repo: pedal is a deadman that never commands the laser].
- **Observe**: two end-stop switches on the plunge rail; continuity through the three ball/groove pairs (says *seated*, not *where*); a timeout on the retract switch (how a fused wire would show); a camera on the dot and the seam, which sees the dot only when the head is in; rotator degrees. The scene shows what a camera *could* report (an illustrative bias on an exact value) next to the exact corner inset and never presents the exact value as a measurement.
- **The experiment this enables**: with the tube left in place and a person away (policy questions in `use-05-gates`), the AI can run park, approach, seat, dry lap, retract, park many times and log the seat-to-seat spread of the dot. The scatter panel shows what that log would look like from the contact repeatability and arm slop you set.
- **Manual or unresolved**: loading and indicating the tube, the campaign trim, the trigger and pedal, snipping a fused wire, and the wire's landing point relative to the dot (nothing observes it).

## What was tried to break it

1. **A hinge about a horizontal axis.**
   *Conflict:* in the kit proxy at the opening pose the nozzle tip sits at (54.6, -8.6, 157.4), 5 mm above the rim (z 152.4), just inside the bore; a horizontal-axis hinge behind the tube moves it up and *inward* over the bore (`calc/swing_path.mjs`). *Assumption:* the retract should clear the tube. *Change:* a vertical-axis swing about a post 300 to 400 mm behind, moving the head outward (clockwise from above), leaves over the near wall and clears an illustrative swap volume (radius 95 mm, top 217 mm) after 10 to 30 degrees for posts 260 to 380 mm from the nozzle, about 65 to 150 mm of arc. *Leaves:* which side the operator stands on and which direction the rotator turns decide where the post can go; the family "swing" and "short slide" are one design with the post at different distances.
2. **Is the plunge needed at all?**
   *Conflict:* a horizontal swing at seat height clears the rim by about 3 mm with no collision in the proxy. *Assumption:* the proxy nozzle, standoff and pitch are right; they are the kit's and unmeasured. *Change:* keep the plunge; each mm of plunge along the barrel axis adds about 0.7 mm over the rim (0.712 is the axis's vertical component), so 20 mm gives about 18 mm of margin, and the plunge is already the retract and the seating stroke. Software rule: no swing until the plunge is at least 20 mm out; the geometry alone forbids it below 8 mm. *Leaves:* the real margin.
3. **What locates the dot: the arm or the seat?**
   *Conflict:* bearing slop, a printed stop, rail play and the dot being about 280 mm from a grip pivot [derived] would all sit in the error chain. *Assumption:* precision has to come from the moving part. *Change:* let the arm only bring the gun within capture and let a kinematic seat locate it, with a float so the arm lets go when the seat takes over. `calc/seat_amplification.mjs`: a 30 mm contact circle and a dot about 130 mm from the seat centre amplify a contact error about 5 times (5 microns at each contact moves the dot roughly 25 to 30 microns RMS); a wider circle (60 mm) gives about 3 times. Hardened balls in hardened grooves repeat to a few microns in the literature summaries [sourcing/use.md]. *Leaves:* what a printed groove does under 20 to 50 N over hundreds of cycles (creep, wear, spatter and fume on the seat), which nobody has measured; a 20-cycle test with the 0.0005 in indicator would say.
4. **The fixed fork versus the tube-swap volume.**
   *Conflict:* the fork plane is normal to the barrel axis, tilted 45 degrees, so its low corner dips into the volume where the tube has to lift out: at 116 mm behind the nozzle it clears by 2 mm, at 100 mm it intrudes 6 to 13 mm depending on the contact circle (`calc/fork_clearance.mjs`). *Assumption:* the seat can sit anywhere along the barrel. *Change:* move the seat back (130 mm clears by 12 mm) at the cost of a slightly longer lever (amplification 5.1 to 5.6). A slider in the scene does this and reports the intrusion. *Leaves:* stiffness of a cantilevered fork and seat arm under preload; not analysed.
5. **The umbilical.**
   *Conflict:* the fibre must not bend tighter than 240 mm stored or 350 mm emitting and must not twist [manual p.20]. It leaves the grip base along the dot-to-grip line, up and back. A Bezier stand-in from that exit to a hook drops below 200 mm at any hook closer than about 0.4 m (`calc/cable_swing.mjs`). A hook fixed on a mast makes the swing bend it (a 150 mm sideways miss over 450 mm gives 326 mm: fine for the stored swing, under the emitting figure); a hook that rides on the arm changes only with the 40 mm plunge (above 1100 mm at 450 mm). *Assumption:* the cable can be routed after the head is designed. *Change:* the cable rides where the gun moves least, and the run from the grip is nearly straight for about half a metre. *Leaves:* the drawn Bezier has no stiffness, weight or twist; twist is the manual's forbidden failure and a swing about a vertical axis with a fixed cable end is exactly what could induce it unless the run is long and free.
6. **A wire fused into the bead.**
   *Conflict:* the retract cannot complete. A 0.030 in wire is 0.456 mm^2; at the roughly 590 MPa spec-sheet figure for deposited ER316L that is about 270 N to break [derived from a search summary, spool-wire strength unchecked]. The rotator is backdrivable and a small lead screw can push more than that. *Assumption:* the retract can break a fused wire. *Change:* the retract is force-limited and is never the thing that breaks a wire; a timeout on the retract switch puts the machine in a HOLD state and a hand snips, as the repo already requires with the head left where it stopped. The scene shows the stop at 4 mm and the HOLD badge. *Leaves:* what force the tube and rotator will tolerate before something moves.

## Branches and combinations

- `use-07-two-stations`: the same head as a carriage that translates between two rotators; branch id given there.
- `use-05-gates`: the sequence and policy around this head (what may run alone).
- `use-03-preset-cartridge`: what removes the tube-to-tube change so the gun is never re-aimed; the two combine directly (the swing-head column of `use-01-day-lanes` and its preset column).
- Compare, not combine: `use-06-coach-loop` (a supported gun with no seat) has the same locked-arm hand and pays for it in re-aiming after every swap.

## Unresolved problems and questions for Derek

- Gun mass, centre of mass, umbilical stiffness and trigger force are [unknown]; they decide arm stiffness, seat preload and whether a lazy-Susan bearing is enough. Weighing the gun on a kitchen scale would help most.
- Which way the rotator turns for the qualified wire approach [Derek]; the post, fork slot and cable hook are drawn for one hand of the gun.
- Preload: what holds the seat against umbilical pull and the trigger hand (magnets, spring, plunge force)? The scene's arithmetic (5 N pull at 250 mm lever with a 30 mm circle needs about 40 N) uses a made-up pull.
- Whether the operator's access to the nest, the indicator and the shoe survives an arm, a post and a fork on the +X side.

## Assumptions

- **[repo]** tube, plate and joint geometry; rotator dimensions and rim height 238.4 mm; retract-before-release sequence; snip with head where it stopped; pedal never commands the laser.
- **[manual]** fibre bend radii 350 emitting / 240 stored, twisting forbidden (p.20); interlock clip needed for emission (p.19).
- **[derived]** gun-side lever about 279 mm (1 degree = 4.9 mm at the dot); 0.712 vertical component of the barrel axis at the opening pose; 0.456 mm^2 wire section.
- **[unknown]** gun mass, umbilical stiffness, real nozzle geometry, seat wear, capture range of a printed fork.
- Illustrative (the scene labels them): the kit's gun proxy and opening pose, the swap volume, 3 mm capture, 1 mm arm slop, contact repeatability, trim offsets, plunge stroke, flange position, the hook distance.

## Sourcing pointers

`sourcing/use.md`: NEMA 17 with T8 lead screw (plunge), 12 V actuator with built-in limit switch (with the force caveat), 27:1 planetary NEMA 17 (swing), 6 inch lazy-Susan bearing, 6 mm G25 balls, 2020 extrusion post. All Prime, prices and evidence recorded there.

Scene id: `use-02-swing-head`. Numbers: `explorers/use/calc/swing_path.mjs`, `cable_swing.mjs`, `seat_amplification.mjs`, `fork_clearance.mjs`, `pose.mjs`.
