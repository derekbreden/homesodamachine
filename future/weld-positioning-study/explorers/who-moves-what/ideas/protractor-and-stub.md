# Protractor + stub: the two gun rotations as physical joints through the dot

## Picture it (as it now stands)

**Two physical joints through the dot.** Both of the gun's rotations are real
joints whose axes pass through the dot by construction:
- **Hole-axis tilt:** a carriage on a laser-cut aluminium arc plate of radius
  ~345 mm, centred on the hole axis. The plate stands beside the tube on the −Y
  side. It spans from dot height (hole dial 0) to 60° up, and sits ~60 mm toward
  −X of the station's tangent plane so the fiber, which leaves the butt along
  −Y, misses the rollers.
- **Grip roll:** the carriage holds a short **stub**, a rigid arm of the shell
  running out along the grip axis ~65 mm behind the butt, turning in two small
  bearings.

**What carries and what adjusts.** A balancer at the gun's centre of mass
carries the weight, so the joints only locate. Yaw is a Y slide (tube symmetry),
and X and Z are set on the work or on the arc's base. Every angle change is one
dial and leaves the dot where it was, once three shell adjustments put the dot
on both axes. The umbilical clamp is released and re-set around each angle
change (sequence-of-use).

**"Fixed"** is the arc's column on the common base.

**Sketch:** `../sketches/s3-protractor-and-stub.svg`, at the true opening pose,
seen from +X, with ghosts at hole dials 0 and 60. The −X offset of the arc is
out of the page in that view.

**Major unresolved problems:**
- Stub stiffness 345 mm from the dot, with and without the balancer.
- Routing the stub arm and the arc past the real fiber exit (scan needed).
- The arc's low end against the rotator's motor and ground towers.
- Re-calibration every time the focus or nozzle changes.
- No lift-off of its own: the work must drop, or the arc's base must lift.

## The original (wave 1), with the wave-2 pose correction

**Allocation in one line:** the scene's hole-axis tilt and grip-axis roll each
become one physical joint whose axis passes through the dot P by construction.
The vertical-axis yaw goes to a Y slide (tube symmetry). X and Z go to
whatever carries the arc's base or the work. Weight goes to a balancer, not to
the joints.

Sketch: `../sketches/s3-protractor-and-stub.svg`. Numbers: `../allocation_calcs.py`
section 2, `../geometry.py`. Poses are the scene's dials: main.js hands posePoint
hole dial − 35, so Derek's opening pose is grip 45 / hole dial 30 / vertical −15.

## The geometric fact that makes it simple

Take the gun at room yaw 0 and any grip roll, and sweep the hole-axis tilt. The
grip base (QBH cable exit) stays in the vertical plane tangent to the tube at P,
and stays **279.2 mm from P**. It traces a circle centred on P, sitting as many
degrees above the −Y horizontal as the hole dial reads. At dial 0 it is level with
the dot, 279 mm out along −Y. At the opening dial 30 it is 30° up, 242 mm out
along −Y and 372 mm above the bench. At dial 60 it is 60° up. This was computed
from the `pose.js` port, calc 2. The grip axis always lies in that plane, and roll
about it never moves the QBH. So:

- **Hole tilt = a carriage running on a circular arc centred on the hole axis.**
  The arc can lie in any plane perpendicular to that axis. The tangent plane
  (x = 61.85 mm) is the natural one, but see the fiber repair below.
- **Grip roll = a bearing on that carriage whose axis is the arc's radius**,
  pointing at P, because the grip axis *is* the radius through the QBH.

Both joints sit at one place, behind the gun's butt, far from heat and spatter.
Neither moves the dot.

## Physical arrangement

- **Stub.** The scan-fit shell grows a rigid arm from the butt region that runs
  out along the grip axis beyond the QBH and ends in a shaft on that axis at
  s ≈ 345 mm from P, about 65 mm past the butt. The fiber leaves the butt 35° off
  the grip axis (the grip rakes 30°, drawing-scaled), and at 51 mm past the butt
  it is ~29 mm off-axis. So the arm leaves the butt on the side away from the
  fiber and rejoins the axis at the bearings. Two bearings sit ~60 mm apart on
  the axis (608 or 6802 class). The stub is a small closed bearing that nothing
  threads through, which the umbilical requires (see notebook: any ring around
  the cable must open).
- **Carriage.** It carries the stub housing and runs on the arc plate on four
  V-rollers (V625-class). It has a clamp and a vernier against a degree scale on
  the plate. At R = 345 mm, 1° of tilt is 6.0 mm of travel, so 0.1° reads as
  0.6 mm, which is easy.
- **Arc plate.** R ≈ 345 mm, spanning about −5° to 65° above the −Y
  horizontal. From hole dial 0 to dial 60 the stub runs from y = −345 mm at dot
  height (232 mm above the bench) to y = −173 mm at 531 mm; at dial 30 it is at
  y = −299 mm, 405 mm above the bench (heights from the current rotator feet). The
  arc stands beside the tube on the −Y side and comes down to dot height about
  280 mm beyond the tube's OD, outside the 300 × 250 rotator base. The motor and
  ground towers' real positions still need checking against it. Laser-cut 6061
  (SendCutSend lists ±0.005 in cut tolerance and up to 0.750 in plate) or printed
  PET-GF for the first version.
- **Fiber repair: move the arc ~60 mm to −X.** At the opening dial the fiber
  leaves the butt nearly horizontally along −Y with a +X component (direction
  0.41, −0.91, 0.06 at room yaw 0). It crosses the arc's radius 79 mm from the
  grip base, 32 mm on the +X side of the tangent plane and ~30 mm below the stub:
  right where the carriage rollers are. Because any plane perpendicular to the
  hole axis works, put the arc plate at x ≈ 0, which is ~60 mm toward −X and away
  from the fiber's +X heading. The stub then reaches it on a 60 mm bracket along
  X. Check the bracket against the body on the real scan.
- **Roll dial and lock.** A printed dial on the stub (a 100 mm radius gives
  1.75 mm per degree) with a friction lock, or a worm or sector gear.
- **Balancer.** A 0.5–1.5 kg tool balancer from overhead, clipped to the shell
  near the gun's centre of mass, carries the weight. The stub and arc only
  locate.
- **Base.** The arc plate's foot is a column at y ≈ −380 mm, beyond the arc's
  low end. X, Z and yaw
  come from either (a) the work on the cross-slide (`still-gun-moving-work.md`,
  so the arc's foot is bench-fixed and P is a room point) or (b) Derek's gantry,
  which carries the arc's foot (branch 2c).

## Operation

Set the recipe's tilt on the arc and its roll on the dial, then lock both. Yaw is
the Y dial (1.08 mm per degree). A one-variable experiment is one dial moved, with
the dot staying put. That is the property repeatability experiments want: change
roll by 2°, keep everything else, and the dot does not wander, so no re-zeroing
confounds the result.

## Calibration (the price of an isocentre)

Both axes must pass through the dot. The dot is optical: it depends on the
graduated-tube (focus) setting and the red-light alignment, not on the copper
nozzle. So the arrangement needs adjustments, used once per gun installation or
nozzle/focus change:

- the shell-to-stub-arm joint gets a small 3-axis adjustment: two directions
  across the grip axis (puts the dot on the roll axis) and one along it (puts
  the dot at the arc's radius);
- the stub housing on the carriage gets two tilt screws (makes the roll axis
  point exactly at the arc centre).

Procedure: roll ±20° and watch the dot in the camera. It traces a circle of
radius e, where e is the dot's offset from the roll axis; adjust until it holds
still. Then tilt ±20° and trim the axial adjustment and the housing screws. The
error budget (calc in `geometry.py`): an axis missing the dot by e moves it
2e·sin(θ/2). For e = 0.5 mm that is 0.04 mm on a 5° experiment step and 0.26 mm
on a 30° move. This loop is exactly the kind an AI can run on the reference beam
for hours.

## Break it

- **Stiffness, one support 345 mm away.** Whatever load reaches the stub
  appears at the dot multiplied by the lever. Without the balancer, the full gun
  weight (15–25 N, estimate) at ~150 mm from the stub puts ~3 N·m on bearings
  60 mm apart, about 50 N of couple. A printed housing compliance of a few µm then
  becomes ~1 mm at the dot, and **that sag changes with roll and tilt** because
  gravity's direction in the gun frame changes. Repair: the balancer takes the
  weight, leaving the stub only the balancer's mismatch (~±2 N, estimate); an
  aluminium housing; and a dot re-check after large angle changes. Unresolved:
  the actual residual, which needs the gun mass and a built stub.
- **Cable forces** enter at the QBH, ~65 mm from the stub, so their moment on
  the stub is small. What they do instead is load the carriage along the arc (a
  clamp holds it) and roll the stub (the roll lock holds it).
- **Roll drags the umbilical.** Rolling about the grip axis swings the fiber exit
  on a 35° cone: 25° of swing and ~37° of twist at the exit for a 45° roll
  (calc 5). Tilting from dial 0 to 60 carries the QBH ~280 mm along the arc. Repair: the first
  ~1 m of umbilical and wire conduit hangs in a free loop (≥350 mm radius) from
  an overhead swivel clamp above the arc's middle. The swivel lets the twist
  relax along the length instead of concentrating at the exit. The manual's
  "twisting is strictly forbidden" makes this a real limit: large rolls should be
  set slowly with the loop free, not clamped.
- **Lift-off and loading are not this idea's motions.** Moving the carriage
  along the arc never lifts the dot out of the corner. Lift and loading go to the
  work (drawer with drop) or to a Z on the arc's foot.
- **Stuck wire.** Nothing moves; snip.
- **Inverted closure.** The same rim height; no change.
- **The arc and the camera.** At the opening dial the arc is low, beside the
  tube on the −Y side, and moved ~60 mm toward −X for the fiber. The camera looks
  in from +X or +Y, clear of it.
- **Wire aim** rolls with the gun, as in the scene. The wire guide on the shell
  keeps aiming at the dot because the dot is on the roll axis.

## Branches

- **2a — trunnion on the hole axis.** A bearing outside the tube on the radial
  line through P, at dot height (x ≈ 90–120 mm), with a frame rising over the
  rim. It is compact, but sits 30–60 mm from the heated wall, in the spatter
  zone, and among the ground and motor towers. Kept as an alternative, not
  developed.
- **2b — open ring around the butt instead of the stub.** An open C-ring
  concentric with the grip axis runs on V-rollers around the grip base. It puts
  the roll bearing right where cable loads enter. It must be open (C-shaped),
  because the fiber cannot be threaded through a closed ring without unplugging
  the QBH at the gun (inference; see notebook). A closed 6820 thin-section
  bearing (100 × 125 mm, Prime, $17.99) therefore does *not* fit this role.
- **2c — on Derek's gantry.** The arc's foot rides the gantry carriage. The
  gantry's X/Y then own radial position and yaw (Y is yaw), and the shelf under
  the table opening owns Z. This keeps Derek's table and gantry arrangement and
  gives its two remaining rotations physical axes through P. His original fixed
  shell is kept as he described it.

## Motorized future

Two motors match Derek's automated vision: "a motor controlling the roll … another
motor controlling the opposite axis of roll." A GT2 belt laid along the arc's
outer edge with a NEMA 17 pinion on the carriage (a belt-rack) drives tilt. A
small worm on the stub drives roll. Because both axes pass through P, the AI's
angle sweeps need no compensating translations, and the calibration loop itself
can be automated.

## Contribution / unresolved / assumptions

- **Contribution:** a concrete mechanism in which the scene's two gun rotations
  are literal joints about the dot, located behind the gun, with the yaw given to
  a slide. It shows that the grip-axis endpoint lies on the hole-tilt arc, which
  collapses both joints onto one carriage.
- **Unresolved:** stub stiffness with and without the balancer; routing the stub
  arm past the fiber exit, and the arc's x offset past the fiber, on the real scan;
  the arc's low end against the motor and ground towers; how much the dot moves when focus is
  changed (re-calibration frequency).
- **Rests on:** pose.js proxy geometry (QBH at 237/−118 mm in the gun frame,
  60° pitch, 16 mm clearance). The real scan moves the QBH point and so the arc
  radius, but not the principle: at room yaw 0, any grip-axis endpoint sweeps a
  circle centred on P in the tangent plane. The first wave-1 numbers here were
  computed at hole dial 65 (posePoint given 30 directly). There the arc ran
  35°–100° up, and the fiber left upward and away from it. At the true opening
  dial 30 the arc sits lower and the fiber heads toward it, hence the −X offset.

---

## Wave 3 note (from sequence-of-use)

**The umbilical clamp belongs to the sequence.** Every roll or tilt change swings
the fiber exit (calc 5), so the cable load on the gun becomes a different
constant. The procedure for an angle change is: unclamp the umbilical, change
the angle, re-clamp at the new shape, then re-check the dot. With that step, one
dial is still one variable. Agreed.
