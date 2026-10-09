# borrowed-ecosystems — summary entries

The view: somebody already mass-produces most of this for another purpose, so
each station is built from that parts bin plus printed parts fitted to the gun.
Geometry is at the true opening pose (grip 45, hole dial 30, vertical −15).
Prices were observed on Prime product pages on 2026-09-28; details are in
`../../sourcing/borrowed-ecosystems.md`.

## A0 — Derek's monitor arm, as proposed *(Derek's example)*

**Idea:** a gas-spring desk monitor arm, clamped behind the rotator, holds the
scan-fitted shell through a printed VESA adapter. Derek aims by hand and lets go.

**Carry, locate, fixed:**
- The arm carries everything and nothing locates.
- Height is held only by friction; the gas spring's rate is close to zero.
- Every swivel turns about a vertical axis on friction, so umbilical and conduit
  forces move it with nothing to bring it back.
- Fixed = the bench top at the clamp.

**Real capability:** HUANUO FlowLift, $35.99, Prime same-day, 4K+ bought/month,
16,507 ratings, rated 2.0–9.0 kg. Gun plus shell (estimated 1.2–2.5 kg) needs
ballast; reviewers report light loads creeping to the top.

**Break and repair:** it can't hold the dot through a 48.6 s lap. Near repairs
are a pole-mount arm with Z locked by a collar, and clamped swivels (joint play
unmeasured).

**Contribution:** its real roles are weight relief while hand-aiming, and parking.
Those grew into A1, A2 and E here, and into sequence-of-use's monitor-arm session.

**Open:** joint play, friction band, gun mass.

**Files:** `ideas/a0-monitor-arm-holds-gun.md`, `sketches/a0-arm-holds-the-gun.svg`.

## A1 — The arm carries, the tube locates *(from Derek's monitor-arm and suspension examples)*

**Idea:** the shell is fixed through small stages to a printed rider that holds
the tube's working end from outside:
- two wheels on the outside diameter straddle the dot at ±30°, 25 mm below it
  (radial position);
- a low outside wheel stops tilt;
- V-groove wheels on the rim at ±60° set height;
- a soft tether with a magnetic breakaway, wired as a switch in the pedal loop,
  holds the tangent.

The gun's weight hangs on a soft spring through its centre of mass, so the carrier
can't fight the rider.

**Fixed:** the tube's own working end. Bench, arm, nest, runout, reseating and tube
length all drop out of the dot's position.

**Break and repair:**
- Worst radial following error is 0.017 mm at the procedure's 0.25 mm runout
  limit; ovality leaks through at half strength.
- The wave-1 rim stations clashed with the wire at the true pose (4 mm gap) and
  exaggerated ovality 1.8×. They are kept as the original.
- one-knob-one-parameter showed printed angle wedges pivot about their seat,
  moving the dot 9–17 mm per 5°. Their A1-G branch (XYZ stage, then an arc about
  the dot, wire on the stage) is adopted, with a bought optics goniometer added
  as the arc.
- Also: A1-Y (a Y slide curved around the tube axis) and A1-B (balancers as the
  carrier).

**Parts:** V624 V-groove bearings, $9.71 for 20, 334 ratings. Huanyu 65 mm
goniometer, ±10°, 0.05° steps, $299, 4 ratings; low volume, and its
rotation-centre height isn't published.

**Open:** rim and outside-diameter shape vs the corner; contacts on warm metal
behind the weld; the pedal-circuit change.

**Files:** `ideas/a1-arm-carries-tube-locates.md`,
`sketches/a1-arm-carries-tube-locates.svg`,
`../one-knob-one-parameter/sketches/a1g-isocentric-rider.svg`.

## A2 — The arm carries, a toolchanger dock locates *(from Derek's monitor arm)*

**Idea:** three balls on the shell drop into three vees on a fine XYZ stage on a
bench post, held by magnets or a latch. A soft carrier floats the weight.

**Locate:** the dock fixes all six freedoms against the bench. Runout is not
followed.

**Break and repair:** a 5 µm seating difference becomes about 12 µm at the dot.
The carrier must hang the gun on a soft link or it fights the dock.
one-knob-one-parameter: the dock is a return-to-stop, and the per-tube
adjustments are the XYZ stage under it, set by camera.

**Open:** the hand-to-dock transition with the umbilical attached; preload against
umbilical tugs; where the post goes relative to the towers.

**Files:** `ideas/a2-arm-into-kinematic-dock.md`, `sketches/a2-arm-into-dock.svg`.

## B — Nodal head *(beyond Derek's examples: camera panorama heads and machinist tools)*

**Idea:**
- A rotator's axis is the hole axis itself, at the dot's height, 30 mm outside
  the tube.
- A spoke runs back along −Y at 30° to a roll element behind the butt.
- Both rotations pivot on the dot, like a panorama head's no-parallax point.
- A cast-iron cross-slide moves the tube in X and Y, and a column gives Z. The
  gun and cables stay still.

**Loads:** gravity torque about the hole axis is 1.0–3.3 N·m and always one sign.
Fixed = a common plate.

**Breaks:**
- The roll element is the weak link: a printed arc about 300 mm from the dot moves
  the dot about 1.5 mm for 2 N at the nozzle.
- A closed roll bearing needs a 145 mm bore to fit over the gun.
- Branches: B0–B3 roll options, and B-G, an upside-down lens gimbal head as the
  hole joint.
- It converges with one-knob-one-parameter's isocentric gantry and
  who-moves-what's protractor-and-stub.

**Parts:**
- VEVOR cast-iron cross-slide, $135.90, 50+ bought/month, 210/110 mm travel.
- Sunwayfoto indexing rotator, $54.95.
- 4 in rotary tables at $134.99 (generic) and $469.08 (Vertex; reviewers report
  minimal backlash and a vernier read with parallax).
- NEEWER GM101 gimbal head, $129.99, 605 ratings.

**Open:** roll stiffness vs fit around the umbilical; lock shift; runout left in.

**Files:** `ideas/b-nodal-head.md`, `sketches/b-nodal-head.svg`.

## C — Engraver gantry *(C-T is Derek's table-hole example; the legged frame goes beyond it)*

**Idea:** an open-frame diode-laser engraver (400 × 400 mm, belts, GRBL-class
controller) with its laser removed, on about 500 mm legs over the rotator. A
ball-screw Z module hangs the shell from the carriage, and a USB camera watches
the dot.

**Locate:** belts and steppers in X/Y (about 120–190 N/mm, estimated), ball screw
in Z.

**Breaks:**
- one-knob-one-parameter showed Y is really an angle, and a software pivot is only
  as good as its calibration. Their C-G2 branch is adopted: the vertical angle
  becomes a G2/G3 arc about the tube axis fitted by camera.
- The ball-screw Z back-drives when unpowered.
- A stuck wire costs steps.

**Parts:** LONGER Ray5, $168.28, 176 ratings, delivery Oct 1, no published
carriage payload; SFU1605 100 mm Z module, $73.80.

**Open:** carriage tilt and creep on plastic wheels with 2–3 kg hanging.

**Files:** `ideas/c-engraver-gantry.md`, `sketches/c-engraver-gantry.svg`,
`../one-knob-one-parameter/sketches/c-g2-vertical-angle.svg`.

## E — Film-grip carrier *(film gear, beyond Derek's examples; plays his monitor arm's role)*

**Idea:** a Steadicam-type spring arm on bearing hinges, on a stainless C-stand. A
printed yoke at the centre of mass takes the arm's post, and the umbilical saddle
rides the same stand's boom.

**Carry:** near-constant lift and no pull-back sideways. A balancer line pulls
back 6–9 N when parked 300 mm aside; this arm doesn't. The rider or a dock locates.

**Breaks:**
- sequence-of-use: the umbilical sets the lifted gun's attitude. Adopted from
  them: carry pins (E-s), lower centre of mass (E-p), LAND/WELD stops (E-z), their
  plate head, a stickout gauge in the docking cup.
- Mine: pulling the pins hands the cable torque to the rider's wheels (up to about
  11 N of contact change against 5–10 N of preload), so trim the pivot position
  and put the saddle at the cable's natural apex. The remaining disagreement is
  only the lever (71 mm to the cable's line of pull vs sequence-of-use's 129 mm);
  the conclusion is the same.

**Parts:**
- FLYCAM Galaxy, $448, 249 ratings, 2–5 kg or 5–10 kg springs.
- FLYCAM Comfort, $209, 314 ratings; reviewers report bounce.
- NEEWER stainless C-stand, $184.99, 2,476 ratings.

sequence-of-use adopted E into their own monitor-arm session as branch E-f.

**Open:** the real cable pull; the arm's vertical spring rate and hinge friction;
yoke clearance around the gun.

**Files:** `ideas/e-film-grip-carrier.md`, `sketches/e-film-grip-carrier.svg`.

## F — Hand-steered isocentre *(a combination, beyond Derek's examples)*

**Credits:** one-knob-one-parameter (rotations about the dot, the walk test),
who-moves-what (the roll stub shaft), sequence-of-use (the hand state),
machine-that-learns (the dot camera).

**Idea:** hole and roll joints both pass through the dot, and each is:
- weightless at every angle: both gravity torques follow exact sine curves, so a
  spring arranged like an Anglepoise lamp's, or a counterweight, cancels them
  everywhere;
- damped with lens grease;
- locked by a bicycle disc brake;
- read by an encoder.

Derek steers the angles by hand on handles while the camera shows the dot staying
put. The work only translates.

**Modes:** explore, freeze, weld on a recipe, or steer roll during a bead while
the encoders log it.

**Breaks:**
- Leftover imbalance needs trim plus a little friction.
- Hand force at the nozzle is about 0.006 mm.
- Tremor is cut about 5×.
- A single-piston brake shifts the dot about 0.03 mm when it clamps, so use a
  dual-piston caliper.
- Hard stops in case a spring fails.

**Parts:** Farbetter disc-brake kit, $25.99, 627 ratings; helical damping grease,
$29.99, 177 ratings.

**Open:** gun mass and balance point; grease viscosity; whether steering mid-bead
teaches anything.

**Files:** `ideas/f-hand-steered-isocentre.md`, `sketches/f-hand-steered-isocentre.svg`.

## Contributed to one-knob-one-parameter (wave-2 exchange)

**Problems:**
- Their Y drawer turns the approach angle 0.93° per mm and the camera can't see it.
- Their nose-first 6816 roll bearing can't pass the gun.
- Their C-arm's overhead yaw table is redundant.

**Repairs:**
- For Y: a kinematic drawer end, or Y read as the yaw knob, which makes the couch
  table optional.
- For roll: hinged clamshell rings, with a micrometer under a lever the gun's
  weight holds down.
- For the C-arm: delete the yaw joint.
- For the hole angle: a sine arm resting on gauge blocks (WEN 81-piece set,
  $104.88, 182 ratings).
- For recipe cartridges: hardened angle blocks.

**Files:** `../../exchange/borrowed-ecosystems--on--one-knob-one-parameter.md`,
`sketches/x-okop-gravity-sine-arms.svg`.

## Contributed to sequence-of-use (wave-4 exchange)

**Problems:**
- The 680 mm saddle (a dial-65 figure) forces a bending moment at the butt of
  0.3–1.4 N·m.
- The solenoid overheats over a weld's ~54 s hold.
- The pole-mount arm's swivel friction leans the balancer line 3–18°.

**Repairs:**
- Saddle at the natural apex.
- Offset the pivot pins 12–43 mm on a screw, like a car-engine hoist's load
  leveler, then add drag and a little friction.
- A dock-gated servo (four for $18.99, 1,346 ratings).
- Bearing hinges.

**File:** `../../exchange/borrowed-ecosystems--on--sequence-of-use-w4.md`.

## Not yet written down elsewhere

The rider's outside-diameter wheels could serve as the X stop in the isocentric
stations, removing the per-tube camera trim.

## Transferable pieces

- **Carry at the centre of mass, locate elsewhere.** Lock the carrier's pivots
  whenever the gun is off its locator.
- **Gravity about any axis through the dot is a sine.** Springs or counterweights
  cancel it at every angle, and a one-signed torque preloads stops for free.
- **Balance, then drag, then friction**, in that order.
- **Circle symmetry:** sliding along the tangent is the vertical-axis rotation
  (0.93°/mm), so a rotary joint for that angle is optional.
- **Rider error formulas:** a symmetric pair follows runout to A(1 − cos α);
  ovality leaks at (1 − cos 2α).
- **Rings around the grip axis** must clear about 145 mm of gun.
- **The umbilical's natural apex** is about 420–450 mm above the bench.
- **Triggers:** use a servo or Bowden cable, not a held solenoid.
- **Bought hardware:** gauge and angle blocks as recipe records; bicycle disc
  brakes as locks; lens grease as drag; optics goniometers as bought arcs about a
  remote centre.

## Questions only Derek's observation can answer

1. Gun mass and balance point, and trigger force and travel.
2. The umbilical's pull and stiffness at the butt (a hang test).
3. The real cable exit direction, and the fibre's clearance from the grip axis
   (from the scan).
4. Runout and ovality at the rim and outside diameter vs at the plate level; how
   far the rim moves after a lap; the tube's seam bead.
5. Which part of the gun makes the conduction contact during a wire-fed weld.
6. Where the motor and ground towers sit around the tube.
7. Whether a breakaway switch in the pedal loop is acceptable.
8. Whether the QBH may be disconnected once to fit a closed bearing.
9. Whether he wants to steer an angle mid-bead as an experiment, or only set and
   lock.
