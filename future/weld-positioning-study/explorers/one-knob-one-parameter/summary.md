# one-knob-one-parameter — summary entries

The view: the station is an apparatus for controlled experiments. Each
weld-relevant quantity should be settable, readable, lockable, recordable and
returnable on its own, so that "change one thing" physically changes one thing.

This explorer started without Derek's examples. Everything below uses the scene's
proxy gun at the opening pose, hole dial 30 (rotation −5°). Gun mass and centre of
mass (CoM) are assumed throughout (1–2 kg).

## 1. Isocentric couch and gantry *(beyond Derek's examples)*

**The idea.** Make the dot an isocentre. Every rotation axis passes through it, so
angle knobs cannot move it. Translations sit nearer ground than rotations, so they
carry the rotations with them. Knobs that keep the puddle's relation to gravity go
under the work; knobs that tilt the beam stay on the gun. Radiotherapy machines are
built this way, and their daily isocentre QA test transfers directly.

**Current state.**

Work side:
- the existing rotator on a radial X micrometer slide (dot place);
- a tangent Y slide as the yaw knob (1.08 mm per degree plus an X correction), which
  is also the loading drawer and returns to a kinematic stop;
- Z at a column.

Gun side:
- a 4-inch rotary table on its side, axis on the radial line through the dot (hole
  angle);
- a 300 mm arm to hinged clamshell rings around a printed butt sleeve (roll, set by a
  gravity-loaded micrometer lever);
- a rail parallel to the barrel (standoff);
- the wire guide on its own XYZ stage.

Gun weight goes down through the rings, arm, table and column. "Fixed" is the
common baseplate. A dot camera on the rotator base reads the dot's place on this
tube's corner.

**Breaks and repairs.**
- **Arm sag (own check):** barely reaches the dot, because the gun folds back along
  the arm: ≤ 0.005 mm for 4040 extrusion.
- **Y drawer (borrowed-ecosystems):** it is a yaw knob the camera can't see. It now
  returns to a kinematic stop, and the Y slide becomes the yaw knob (branch B-Y), so
  the couch rotary table becomes optional.
- **Roll bearing (borrowed-ecosystems):** a closed 6816 cannot pass the gun, which
  needs a ≥ 130–145 mm circle. Replaced by their clamshell rings (R-C).
- **Other branches:**
  - R3: the hole angle on a gravity-loaded sine arm with gauge blocks
    (borrowed-ecosystems).
  - R4: the tube's own OD as the X stop (borrowed-ecosystems; wall-thickness caveat
    added here).
  - R5: relieve weight only down to a few newtons, so gravity keeps loading the
    worms one way.

**Parts.**
- Printed: roll body and sleeve, clamp rings, wire-guide flip mount, corner phantom,
  camera arm.
- 4-inch rotary tables:
  - HHIP, $159.80 (1 left, Oct 1);
  - generic 36:1, $99 (5 left, Sep 30);
  - ≥ 10 Prime sellers, so the volume evidence is category-level.
- Micrometer head $15.99; MGN12 rail $17.99; AS5600 encoders, 3-pack $7.99
  (100+/month); Klein angle gauge $32.97 (5K+/month).

**Contribution.** Decoupling becomes a mechanical property, and the leftover
coupling becomes a measured number from the walk test.

**Unresolved.**
- Locked stiffness and lock shift of cheap tables.
- Sleeve creep under the rings.
- Which contact the conductance interlock senses.
- The real gun envelope.

**Files.** `ideas/isocentric-couch-and-gantry.md`; `sketches/isocentric-side.svg`,
`sketches/isocentric-plan.svg`, `sketches/chain-principle.svg`.

## 2. C-arm on the gun, and branch C-0 *(beyond Derek's examples)*

**The idea.** The scene's three dials become three physical axes, nested exactly as
`pose.js` nests them.
- An overhead yaw table sits on the dot's vertical and carries an R 300 arc centred
  on the dot. The carriage's place on the arc is the hole dial, read straight off
  the arc.
- The carriage carries roll on the grip axis, then standoff, then the gun.
- The work only translates, so the purge hose, ground lead, camera and the
  operator's view never move for an angle change.
- Weight hangs from the yaw table on a goalpost frame. "Fixed" is the goalpost plus
  the baseplate.

**Breaks and repairs.**
- **Own checks:**
  - An off-axis CoM makes the isocentre walk with yaw; a counterweight fixes it.
  - A hanging rotary table's retention is uncertain.
  - The arc is a curved cantilever; repaired with a strut and cut 6061 plate
    (SendCutSend states delivery in days).
- **borrowed-ecosystems:** the yaw joint is redundant for a circular seam. Branch C-0
  deletes it, hanging the arc from a fixed goalpost and taking yaw on the work's Y
  slide. C-0 then converges with entry 1. The only fork left is an arc versus a
  rotary table for the hole axis; the arc supports the gun close in.

**Unresolved.** Arc and carriage compliance; overhead mass and space (C-0 removes
most of it).

**Files.** `ideas/c-arm-on-the-gun.md`; `sketches/c-arm-side.svg`.

## 3. Recipe cartridges, and branch S *(beyond Derek's examples; converges with others' docks)*

**The idea.** The gun's angles are held by a printed pose block on kinematic seats.
- Three G25 balls on the shell sit in the block's vees.
- Three balls under the block sit in dowel-pin vees on a stand outboard on −Y.
- The block is generated from the pose math, so its file and commit are the record.
  Reseating repeats to microns.
- Dot place and yaw stay as knobs at the work, set per tube with the camera.
- Weight goes through the block to the stand; "fixed" is the stand's baseplate.
- Lifting the shell off frees the gun for hand work, and it returns exactly.

**Breaks and repairs.**
- **Own checks:**
  - Print error of 0.1–0.3 mm over 200 mm (estimate) is fixed, so it gets measured.
  - Tip/tilt trim screws would pivot off the dot, so they are rejected.
  - Sweeps are slow at one print per step.
- **borrowed-ecosystems, branch S:** hardened angle blocks set the angle and printing
  only locates (WEN 12-piece $41.74; Accusize ±30″ $42, from their sourcing). The
  addition here: the hinge on the stack must pivot on the dot.

**Parts.** G25 balls $6.95 per 100 (100+/month); dowel pins $6.49 per 24.

**Contribution.** The baseline becomes a physical object; transferring the recipe
means handing over a part.

**Unresolved.** PET-GF creep under point loads; cable routing through a block whose
shape changes per pose.

**Files.** `ideas/recipe-cartridges.md`; `sketches/recipe-cartridge-pose.svg`,
`sketches/recipe-cartridge.svg`.

## 4. Knob-wired suspension *(Derek's suspension example, developed)*

Derek's example is kept verbatim in the file. It builds on carry-and-locate's
six-wire located form, where three wires meet at the dot and act as a pivot there,
and on machine-that-learns' cable-robot run.

**The plane rule.** With the three dot wires fixed, a wire changes exactly one angle
if and only if it lies in the plane of the other two rotation axes. That maps onto
Derek's picture:
- a vertical wire on the base loop = the hole knob;
- the base loop pulled along the hole-axis direction = the vertical-angle knob;
- the third ring in the vertical radial plane through the dot = the roll knob;
- tip lines aimed at the dot = the pivot;
- his "complete, openable loop" around a round collar lets the gun roll inside it
  while the loop's force passes through the grip axis.

A fully diagonal six-wire layout is impossible here: the pure vertical-angle wire
would pass through the tube wall. So dot X and Z move at the work.

**Search results.**
- The angle knobs are exactly single to first order. In 2° steps the dot drifts
  < 0.08 mm; at 5°, up to 0.5 mm.
- Stiffness at the dot: 21–34 µm per 5 N.
- Modes at 31–252 Hz. The 80 Hz wobble sits between them (~4 µm per N); a
  wobble-frequency sweep through ~116 Hz meets one.
- The tension margin was thin: 5.9 N.

**Repairs from who-moves-what, adopted.**
- **W-R1:** freeing the sixth wire anywhere within its plane gives 12 feasible layouts
  and an 18.5 N margin. Caveat recorded here: their best layout's wire crosses the
  open tube, blocking the snip side and the camera, and sits in the plume.
- **W-R2:** yaw on the couch Y slide is exact over ±23°, leaving five knobs for five
  parameters.
- **What didn't help:** sequence-of-use loads and escape-lean wires.
- **Their combination:** `../who-moves-what/ideas/gravity-in-the-gun-plane.md`, in
  which only the hole wire carries gravity at the tilt τ* and is tensioned by it.

**Carrying, fixed and return.** The wires both carry and locate. "Fixed" is a
~0.9 m anchor cage. Readouts are Tr8×2 lead-screw anchors with dials; tension
removes backlash. Unhook the preloads and horizontal wires, re-hook, and the pose
returns.

**Parts.**
- Tr8×2 lead screw $7.49 (185 reviews); thimbles $6.99 (100+/month).
- Stainless rope and turnbuckles: carry-and-locate's sourcing.
- Constant-force spring $39.99 (weak volume, no reviews); spring balancers are the
  volume alternative.

**Unresolved.** The margin rests on the assumed gun mass and CoM; exactness is
first-order only; cage size and clutter near the dot.

**Files.** `ideas/knob-wired-suspension.md`; `sketches/knob-wired-suspension.svg`;
`diagonal_wires.py`.

## 5. Flexure trim head *(a direction nobody else developed)*

**The idea.** Fine knobs as printed flexures, which have no backlash, stick-slip or
lock shift, around a seated coarse pose. The primary host is who-moves-what's tilt
cradle with branch T-b1. Three stages sit between the carriage and the recipe
block:
- **A:** a parallelogram moving the gun across the corner, between wall and cap.
- **W:** a remote-centre pivot whose two spring-steel leaves aim at the seam tangent
  through the dot (work angle).
- **S:** a parallelogram along the beam (standoff).

Each stage is set by a micrometer on a 5:1 printed notch lever and preloaded by a
steel spring. Weight goes through the carriage and rail, with leaves along the
weight where possible. "Fixed" is the cradle.

**Estimates (`flexures.py`).**
- Parallelograms: ±2 mm with PETG leaves, ±4 mm with 1095 shim.
- W: ±3–13° at 70 mm from the dot.
- Remote-centre drift is proportional to distance from the dot: 24–42 µm at ±1° for
  70 mm, three times that at 150 mm. Hence the rule: **flexure pivots within
  ~100 mm of the dot**.
- Printed leaves carrying the gun's weight tilt 0.13–0.26 mm at 150 mm, so steel
  leaves belong in the load path.
- Micrometer-held stages relax rather than creep.
- Thermal growth of printed loops (20–120 µm for 5–15 K) is the bigger heat term;
  dry-run at steady temperature.

**Parts.** 1095 shim assortment $53.39 (48 reviews, 2 left), with alternatives from
$28.92. PETG Basic's 75 MPa bending strength observed on Bambu's page. The PET-GF15
datasheet link was found but its PDF not read, so those values are estimates.

**Unresolved.** Whether ±1–3° and ±2–4 mm cover the needed fine tuning (the process
window is unknown); thermal growth over a session; clamp relaxation.

**Unwritten connection.** The flexure pivots and the escape rail could replace the
isocentric station's drawer, retract lever and roll rings.

**Files.** `ideas/flexure-trim-head.md`; `sketches/flexure-trim-head.svg`.

## 6. Branches contributed to others' ideas

**A1-G, isocentric rider** (on borrowed-ecosystems' A1 rim rider).
- On the rider, an XYZ stage carries both the wire guide and a printed R 70 arc
  about the seam tangent through the dot; the shell hangs on the arc.
- XYZ moves beam and wire together, changing only the dot place. The arc turns only
  the gun; the wire stays.
- This works because the arm carries the weight, so the locating chain sees only
  newtons, and a 70 mm radius costs about a quarter of the dot motion of a 300 mm
  arc.
- The rider's straight Y screw should be curved, concentric with the tube, to be an
  exact yaw knob.
- Cost: the wire conduit no longer runs with the umbilical, and an interlock jumper
  is needed.
- Files: `../../exchange/one-knob-one-parameter--on--borrowed-ecosystems.md`;
  `sketches/a1g-isocentric-rider.svg`.

**Engraver gantry** (on borrowed-ecosystems' C).
- The vertical angle becomes a G2/G3 arc about the tube axis: exact, one command.
- Grip roll goes on a physical axis through the dot.
- The one remaining software pivot is calibrated by the walk test.
- Sketch: `sketches/c-g2-vertical-angle.svg`.

**T-b1 and T-g** (on who-moves-what's tilt cradle).
- **T-b1:** the rail stop was really two knobs, adding 1.18 mm of standoff and 0.59°
  of yaw per mm. It becomes a fixed seat, with one beam-parallel stage and one
  across-the-corner stage.
- **T-g:** a work-angle pivot on the cradle's own axis separates work angle from
  gravity.
- **Tipping:** the first-closure tube tips in its nest at about 30.5°, so it needs a
  band clamp.
- **Tilt walk test:** with two inclinometers.
- **Gas:** the argon jet's Richardson number is ≪ 1 at the pool but 0.03–1.5 over the
  lip, so tilt changes gas coverage there. Read the heat tint, and run tilt against
  flow as two factors.
- File: `../../exchange/one-knob-one-parameter--on--who-moves-what-w4.md`.

**Dial-convention correction.** Five explorers' geometry used hole dial 65 as the
opening pose. At the real pose:
- the barrel is at 45°;
- the grip base is 140 mm above the dot;
- the umbilical apex is ~416 mm above the bench;
- hole-axis torque is ~3.7× larger.

## Transferable pieces

- **Isocentre.** Rotation axes pass through the dot, and translations sit nearer
  ground than rotations. A translation inside a rotation couples angle changes into
  the dot, by roughly trim × angle.
- **Three classes of adjustment.**
  - A knob is a parameter.
  - A calibration screw is set during QA, then painted over.
  - A motion to a stop moves things out of the way without ever changing a setting.
- **The parameter is what's measured at the dot.** The camera on the work side is the
  truth; the micrometer is only the actuator.
- **Walk test.** Sweep each knob with the red dot on a corner phantom; the trace is
  that knob's coupling in mm. The tilt version adds two inclinometers.
- **Plane rule.** A support is a single knob iff its line lies in the plane of the
  other two rotation axes.
- **Circle symmetry.** Tangent motion is yaw (0.93° per mm); G2 arcs or curved
  slides make it exact.
- **One-signed gravity** takes up backlash consistently.
- **Flexure placement.** Pivot hardware within ~100 mm of the dot. Flexures guide,
  steel sets, steel springs preload.
- **Carry and locate separately,** so locating chains can be light.
- **Mount the wire guide on the translation carriage** to decouple it from angle
  changes.

## Questions only Derek's observation can answer

- Gun mass and CoM; umbilical pull at the butt; trigger force.
- Which contact the interlock senses: nozzle, wire or body.
- Which barrel sections stay fixed when the graduated tube turns.
- Whether the red dot sweeps with wobble on in red-light mode.
- The nozzle's exit bore and gas flow.
- Whether the gun body warms over a run of welds, and by how much.
- Whether the first-closure tube is clamped or only indicated in the nest.
- Tube length spread, and runout at the rim versus at the plate.
- Whether he would accept a ~0.9 m anchor cage, or yaw as a Y slide instead of a
  dial.
