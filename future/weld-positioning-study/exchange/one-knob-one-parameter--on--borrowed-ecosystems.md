# one-knob-one-parameter on borrowed-ecosystems

My view: the station is an apparatus for controlled experiments. A knob
should change one weld quantity, and what is left over should be a measured
number. I worked on **A1** (their furthest-developed arrangement) and **C**
(medium depth, the one my view changes most), with shorter notes on A2 and B.
Calculations: `explorers/one-knob-one-parameter/exchange_calcs.py`. Sketches:
`explorers/one-knob-one-parameter/sketches/a1g-isocentric-rider.svg` and
`.../c-g2-vertical-angle.svg`.

## 0. First, a geometry correction that runs through their numbers

`pose.js` receives the hole rotation as **dial − 35**; the scene's opening pose
is roll 45, dial 30, vertical −15. Derek set exactly those defaults in commit
`eda643038`, after the re-zero in `ed6519414`. That makes the hole rotation −5°.
`borrowed-ecosystems/geometry.py` passes `hole=30` straight in as the rotation,
which puts the gun at **scene dial 65**. So does the geometry code of
who-moves-what, work-as-datum, sequence-of-use and carry-and-locate. Only
workspace-as-structure, machine-that-learns and I apply the offset.

| At roll 45, vertical −15 | dial 30 (the scene's pose) | dial 65 (their code) |
|---|---|---|
| barrel elevation | 45° | 71° |
| nozzle tip vs rim | +5.0 mm | +8.8 mm |
| grip base | 140 mm above the dot, plan (−1, −234) | 253 mm above, plan (31, −114) |
| their CG proxy | plan (−23, −127), 140 above | plan (5, −24), 197 above |
| gravity torque about the hole axis, 1 / 2 kg | 1.42 / 2.84 N·m | 0.38 / 0.75 N·m |
| about the grip axis | 0.41 / 0.83 N·m | 0.20 / 0.40 N·m |
| umbilical exit elevation, loop apex above the bench | 29°, **~416 mm** | 64°, ~682 mm |

Things that change at the real pose:
- A1's remark that the trigger and grip base sit "almost directly above the
  stations". The grip base is actually 180 mm behind station 2, toward −Y.
- B's rotator bending moment and hole torque, both roughly 3–4× larger.
- The digest's "umbilical rises to ~680 mm" and "gun body almost over the tube
  axis". At dial 30 the gun leans back along −Y, and its body sits beside the
  tube, not over its axis.

None of the ideas depends on the wrong pose, but the loads and clearances
should be re-run.

## 1. A1 — the arm carries, the tube locates

**What it does that my arrangements lack.**
- The locating reference is the joint's own neighbourhood. Runout, reseating,
  the nest and the bench drop out of the dot, where my stations can only
  measure them.
- The weight never enters the locating chain. The arm or balancer carries it
  through a soft hook at the CG, so everything that locates carries only
  preload and disturbance: a few newtons. In my isocentric station the rotary
  tables and roll bearing carry the full weight, and their joint compliance is
  my largest unknown.

**The difficulty.** Consider A1 exactly as written. Angles are "baked into the
rider/shell geometry (printed wedges); changing a recipe angle is a swap", with
fine XYZ screws between rider and shell, and the wire guide on the gun.

A wedge swap rotates the gun about the wedge's own seat, not about the dot. The
dot then moves by roughly (seat-to-dot distance) × Δθ: 9–17 mm for 5° at
100–200 mm. Three XYZ screws must bring it back, and each new wedge brings its
own print error into all three angles.

The wire rides along with every swap. A guide on the gun moves 6.5 mm (tangent
axis), 8.7 mm (hole axis) or 7.3 mm (vertical axis) per 5° about the dot.

So one angle change is a part swap plus three screw moves plus a wire
re-set, and whether the *other* angles held depends on print accuracy.

**The assumption behind it.** Angles are recipe constants that rarely change.
All fine work is translation.

**Repair / branch A1-G, the isocentric rider** (sketch
`a1g-isocentric-rider.svg`). The chain on the rider runs:

> rider → XYZ micrometer stage → { wire-guide mount ; work-angle arc → shell → gun }

- **Where the arc sits.** A printed arc of radius 70 mm, centred on the seam
  tangent through the dot. It lies in the plane y = −40, between the two rim
  stations, and spans 0–60° from horizontal-outboard to above the corner.
  Against the proxy at the real pose, the arc clears the gun by 47–65 mm and the
  OD below the rim by 63–85 mm. A micrometer tangent screw drives it and a clamp
  locks it.
- **What each knob now changes.**
  - The XYZ stage moves the arc centre, the gun and the wire together, so it
    changes only the dot's place. The rotations are carried with it, which is
    the chain rule: translations nearer ground than rotations.
  - The arc turns the gun about the dot and nothing else. The wire stays put,
    because it sits on the XYZ carriage, not the gun.
  - The wedges become coarse recipe angles for the gun only.
  - Wire micrometers on its mount set the wire tip against the dot.
  That makes four groups, each one parameter.
- **Why it works here and not in my stations.**
  - Load: move the rim preload to ballast on the rider, as A1 already suggests,
    and balance the gun fully at the hook. The arc and stage then see only
    disturbances (conduit, umbilical residual, about 1–2 N), which a printed
    arc or a 60 mm optics stage can hold.
  - Radius: B's weak link was a compliant rotation 300 mm from the dot. A
    compliant rotation at this carriage moves the dot by δθ × 70 mm. The same
    compliance costs about a quarter of the dot motion.
- **Why the work angle gets the arc.** It is the direct lever on the wall/cap
  split, and it is the axis that fits.
  - Derek's grip roll would disturb a gun-mounted wire least: 1.8 mm per 5°,
    because the guide sits near his axis. That is a real merit of his choice,
    which my wave-1 "his knobs are three-parameter" framing understated.
  - But 60 mm from the dot his axis runs 22 mm above the rim with the barrel
    28 mm above it, so no dot-near arc fits around it. Grip roll stays a wedge,
    or goes to a bearing at the butt.
- **The rider's Y screw.** Per the tangent finding, sliding along Y is the
  vertical-axis angle (0.93° per mm) plus a drift off the corner of s²/2R. So a
  straight Y screw is two parameters. The repair is a printed *curved* Y slide,
  concentric with the tube (R 61.85 at the dot). It is then an exact
  vertical-angle knob, the same idea as the G2 arc below.
- **Station 1.** At the real pose the proxy passes 11 mm above the rim near
  θ −20…−40, and station 1 at −30° has proxy metal 17 mm away. Moving the
  stations to −40/−70 clears the proxy. The cost is A1's worst-case
  once-per-rev extrapolation error, which rises from 0.033/0.040 mm to
  0.052/0.062 mm (radial/height) with their method. Alternatively, keep −30
  with the wheel axle cantilevered from outboard, where the scan decides.

**What remains.**
- The wire conduit now runs to the rider, not with the umbilical, so Derek's
  "keep them together" is given up in this branch.
- An interlock jumper is needed from the wire guide to the gun body.
- The nozzle and wire guide may collide at large arc angles; the scan decides.
- The arc sits 30 mm outboard of a hot OD for the overlap. Print it in PET-GF
  and keep its metal pins away from the rim.
- A1's own open problem, rim versus corner shape, is untouched. The dot camera
  on a dry lap measures it.

## 2. C — engraver gantry

**What it does that my arrangements lack.** It is motorised, homed and
G-code driven, with camera-alignment software, bought as one high-volume
product. My knobs need building before an AI can turn them. The gantry is
already the platform for Derek's "let an AI iterate dry runs".

**The difficulty.** Consider C with "two small roll stages between the Z module
and the shell, whose axes are not through the dot, compensated in software",
and with X/Y treated as free positioning axes. Two things fail.

1. **Y is not a position axis near the corner.** Moving along the tangent turns
   the approach 0.93° per mm. For the same angle change, the straight move
   leaves the dot 0.23 mm off the corner at 5°, 0.93 mm at 10° and 2.04 mm at
   15°. A search that "walks Y to find the corner" is changing an angle.
2. **A software pivot is only as single as its calibration.** If a roll stage's
   axis is mislocated by d, each step moves the dot by d × Δθ: 0.5 mm and 10°
   give 0.087 mm, 1 mm gives 0.175 mm. Also, every compensation move shifts the
   hanging payload's CG under POM wheels. The carriage tilt then changes by an
   amount the model does not contain, and possibly with hysteresis.

**The assumption behind it.** A computer makes inverse kinematics free, so
mechanical isocentricity is unnecessary.

**Repairs.**
- **The vertical angle is a G2/G3 arc about the tube axis** (sketch
  `c-g2-vertical-angle.svg`). Translating the gun so the dot travels round the
  corner circle changes its approach relative to the local tangent by exactly
  the arc angle, and the dot never leaves the corner. It is one command, one
  parameter and exact, and the engraver ecosystem does arcs natively. The tube
  axis in machine coordinates is found once by fitting the corner circle with
  the dot camera at three points.
- **The radial dot place** is a G1 move along the radial at the current arc
  angle. **Height** is Z.
- **The most-swept rotation goes on a physical axis through the dot.** Grip
  roll becomes a preloaded bearing pair on the grip axis, hung from the Z
  carriage just behind the grip base. At the real pose that is 234 mm back
  along −Y and 140 mm above the dot. The gun cantilevers forward from it, so a
  roll step needs no compensation. The hole angle stays as a cassette or as the
  one software pivot.
- **Calibrate that pivot with the walk test.** Put a corner phantom in the nest,
  sweep the stage, and let the camera fit the axis location and report the
  residual. Store the pivot coordinates as locked calibration, like a work
  offset, not as something a recipe edits.
- **Stiffness.** An MGN carriage (their own repair) and a counter-spring cut the
  CG-dependent tilt. The walk test shows what is left.
- **What stays true in G-code.**
  - Knobs are named macros, one per parameter: radial, height, vertical-as-G2,
    roll, standoff.
  - Calibration is the pivot coordinates and the tube-axis fit.
  - Motions to a stop are homing and park moves.
  - A recipe is a file plus a cassette number.

**What remains.**
- Carriage stiffness under a 2–3 kg hanging payload.
- The legs and rotator share only the bench. A common plate would take the
  wood top out of the loop.
- At dial 30 the gun reaches 440 mm above the bench (not 487 mm) and 235 mm
  back along −Y. The 400 × 400 frame still contains that footprint plus a
  ±15° G2 range.

## 3. Shorter notes

**A2, the arm into a kinematic dock.** The dock repeats the gun against the
post to microns. The corner, however, moves per tube by up to millimetres:
tube length ±3.2 mm moves the corner height, and so does the cap recess. So the
dock is a *motion to a stop*, and the XYZ stage under the receiver holds the
real knobs, re-set per tube by the camera. Their chain already has the right
order (post → XYZ → receiver). My recipe cartridges are A2 with the angles in
the block. Toolchanger hardware transfers directly to my shell interface:
magnets, printed funnels, and an unseat alarm through two balls.

**B, the nodal head.** It is essentially my isocentric gantry; the
panorama-head "no-parallax point" is a better name for the isocentre than mine.
- **Their grip-roll weak link.** A printed arc at 300 mm gives mm-scale dot
  motion. A lightly preloaded 6816 pair 30 mm apart, with an assumed radial
  stiffness of 5 × 10⁴ N/mm per bearing, has a tilt stiffness of about
  2 × 10⁴ N·m/rad. 2 N at the nozzle then moves the dot about 7 µm, so the
  housing dominates.
- **The QBH problem.** The 80 mm bore lets the gun pass through nose-first,
  which avoids unplugging the QBH, if the scan allows.
- **The column foot on an arc about the dot's vertical** is my couch rotation
  done on the gun side.

## 4. What transfers

**From them to me.**
- Carry the weight separately. A balancer hook at the gun's CG would unload my
  hole table and roll bearing, so their compliance stops mattering as much.
- Following the rim is an alternative to measuring runout and leaving it in.
- The engraver/G-code ecosystem is the cheap way to motorise my knobs.
- Toolchanger docks suit the shell-to-station interface.

**From me to them.**
- Isocentre and chain order: translations nearer ground than rotations.
- Mount the wire on the translation carriage, so angles leave it alone.
- The vertical angle as a curved slide or G2.
- The walk test as a QA number.
- The dial-30 correction.

**Together.** A1-G is the combination: a rim rider whose locating chain is an
isocentric knob set, with the weight carried elsewhere.
