# Digest after the first pass

Coordinator's map of what the eight explorers developed independently, the
findings that apply across arrangements, and where the pass converged. Read
the idea files themselves for substance; paths are relative to
`future/weld-positioning-study/explorers/`.

Four explorers started with Derek's examples (carry-and-locate,
workspace-as-structure, who-moves-what, borrowed-ecosystems); four started
without them (work-as-datum, one-knob-one-parameter, sequence-of-use,
machine-that-learns). Everyone now has `context/examples-and-history.md`.

## Pose convention (correction during wave 2)

`pose.js` takes the hole rotation as **dial − 35**: `main.js` calls
`posePoint(p, grip, holeDial - 35, vertical)`. Derek's opening pose is
grip 45° / hole dial 30° / vertical −15°, i.e. `posePoint(p, 45, -5, -15)`.
Passing 30 straight into `posePoint` gives hole dial 65. At the true opening
pose: barrel elevation ~45°, back of body ~(−60, −144) mm in plan and ~424 mm
above the bench, grip base ~(−1, −234) mm in plan and ~372 mm above the bench.
At dial 65: barrel ~71°, back of body ~(−24, −8) and ~487 mm, grip base
~(31, −114) and ~485 mm. Results computed at dial 65 remain valid for that
reachable orientation; label them as such.

## Every arrangement so far, grouped by how it assigns the work

Grouping is the coordinator's reading; one idea can sit in several families.

**Suspension and wires**
- `carry-and-locate/ideas/suspension-original.md` — Derek's loops, wires and
  bungees as stated, placed on the real pose; bungees on the radial axis,
  tangent left as the free swing; two-loop free roll aligned to the grip axis
  by a shell trunnion; third ring high at the back; five labelled branches.
- `carry-and-locate/ideas/wire-located-suspension.md` — six taut wires, three of
  whose lines meet at the dot (a virtual ball joint there), three setting the
  angles; bungees only keep wires taut. Lift-off is free, lowering returns the
  pose. Needs a braced anchor frame.

**Soft carrier + stiff seat or dock** (the largest convergence)
- `carry-and-locate/ideas/float-and-dock.md` — balancer and cable saddle carry;
  magnet-held three-ball seat on an adjustment stack locates.
- `who-moves-what/ideas/carrier-and-seat.md` — Derek's monitor arm and
  suspension as carriers docking into a seat on the rotator base; his two loops
  already lie nearly on the grip axis.
- `machine-that-learns/ideas/d-watch-first-seat.md` — seat under a small bridge,
  two hand-wheel ball-screw stages with counters, cameras reading dot vs corner.
- `borrowed-ecosystems/ideas/a2-arm-into-kinematic-dock.md` — 3D-printer
  toolchanger coupling on a bench post; gun off for tacking, back to pose.
- `one-knob-one-parameter/ideas/recipe-cartridges.md` — hole and roll frozen in
  printed pose blocks on kinematic seats; the block is the record.
- `sequence-of-use/ideas/lid-carrier.md` — the gun on a lid hinged behind the
  station; closed, it rests on three balls in vees with hinge pins in slots;
  open, it parks at ~80°; the hinge line was found by sweeping 80 candidates.
- `workspace-as-structure/ideas/countertop-sled.md` — the shell stands on three
  ball feet on a rim-height plate against a fence and stop; lift off, set back;
  motorised form as six actuators at the six contacts.

**The gun stays; the work moves** (six explorers reached a version of this)
- `who-moves-what/ideas/still-gun-moving-work.md` — cross-slide, loading drawer
  and three fine screws under the rotator; printed recipe blocks for the angles.
- `workspace-as-structure/ideas/fixed-gun-moving-shelf.md` — gun on a bridge,
  cross-slide under the rotator; following runout by moving the work.
- `sequence-of-use/ideas/gun-stays-work-travels.md` — the rotator on a carriage
  that runs low, then climbs end ramps into kinematic seats.
- `machine-that-learns/ideas/a-still-gun-moving-tube.md` — rotator on a radial X
  stage, then Z; tilt by differential Z or a trunnion through the dot.
- `borrowed-ecosystems/ideas/b-nodal-head.md` — (also a rotation-about-the-dot
  head) cast-iron cross-slide moves the tube under a fixed gun; column for Z.
- `one-knob-one-parameter/ideas/isocentric-couch-and-gantry.md` — (also below)
  rotary table + radial micrometer slide + tangent drawer under the work.

**Rotations that pivot on the dot** (isocentre / remote centre)
- `one-knob-one-parameter/ideas/isocentric-couch-and-gantry.md` — knobs that
  keep the puddle's relation to gravity go under the work; tilting knobs stay on
  the gun: a rotary table on the radial line through the dot (hole angle), a
  preloaded bearing pair on the grip axis (roll), a barrel rail (standoff).
- `one-knob-one-parameter/ideas/c-arm-on-the-gun.md` — the scene's three dials
  nested as `pose.js` nests them, hanging from an overhead vertical-axis table.
- `who-moves-what/ideas/protractor-and-stub.md` — hole tilt on a dot-centred arc;
  roll on a short bearing on the grip axis behind the butt.
- `machine-that-learns/ideas/b-rcm-gun-carriage.md` — X/Y/Z stages plus a
  hole-axis arc and grip-axis yoke; each a hand knob a motor can later drive;
  branch B2 with a geared camera head and software re-centring.
- `borrowed-ecosystems/ideas/b-nodal-head.md` — panorama-head parts or a rotary
  table placed so both rolls pivot on the dot.
- `machine-that-learns/ideas/c-hexapod-software-pivot.md` — six printer
  lead-screw actuators; pivot set in software; ±7–10° range.

**Riding the work** (five explorers; contact conditions differ)
- `borrowed-ecosystems/ideas/a1-arm-carries-tube-locates.md` — shell rides the
  rim ahead of the puddle on V-groove bearings plus an outside wheel; arm or
  balancers carry through the centre of mass; following error estimated.
- `carry-and-locate/ideas/rim-carriage.md` — ring riding the rim on roller pairs
  pinching the wall at ±30° (0.42× ovality leakage); branch D2, a shoe on the
  cap and bore at the joint.
- `who-moves-what/ideas/tube-carries-the-reference.md` — 3a rides (skids on the
  plate, rollers outside, soft tether); 3b maps the corner on a dry lap and
  replays it; 3c is a gauge foot used only at setup.
- `sequence-of-use/ideas/rim-riding-saddle.md` — five rollers on the cold,
  arriving side; balancer carries; C-h held by hand as the cheapest test.
- `work-as-datum/ideas/lip-collar-track.md` — C0 rollers on the lip (kept); C1 a
  stock 5 in exhaust band clamp as a clean track below the plate.

**Referenced to the endcap itself**
- `work-as-datum/ideas/endcap-compass.md` — the gun frame sits on the plate being
  welded: 316 hex nipples in the two tapped ports, a centre pin between them,
  three ball transfers on the plate face, a fork pin holding rotation about the
  tube axis; a calibration puck (replica joint) and a pose block. Needs a
  force-quiet gun (trigger and cables relieved).
- `work-as-datum/ideas/between-centres.md` — rotator and gun mast on one
  sub-plate; a tailstock live centre on the port seat clamps the loose tube;
  B0 (mast + dial-plunger height set) kept as the simplest step.

**Structure-first**
- `workspace-as-structure/ideas/table-opening-gantry.md` — Derek's branch as he
  described it; the gun body sits over solid table and only the barrel crosses a
  Ø150–160 opening; tube change by dropping the shelf ~70 mm and sliding the tube
  out the open face; edge-of-table version kept as a branch.
- `workspace-as-structure/ideas/drop-in-collar.md` — one cut plate carries rails
  above and posts below, taking the wood top out of the structural loop.
- `workspace-as-structure/ideas/lidded-mouth.md` — seed: a fixed lid above the
  rim with gun, camera and gas ports.
- `borrowed-ecosystems/ideas/c-engraver-gantry.md` — an open-frame diode-engraver
  gantry on legs over the rotator, ball-screw Z module holding the shell.

**Held and used**
- `borrowed-ecosystems/ideas/a0-monitor-arm-holds-gun.md` — Derek's monitor arm
  as proposed: floats in every direction; excellent for carrying while aiming by
  hand and for swinging away; kept as proposed.
- `sequence-of-use/ideas/gauge-set-lock-held.md` — a printed rim gauge sets the
  pose, a lockable holder keeps it, the gauge comes off before the weld.
- `sequence-of-use/ideas/session-kit.md` — plate hangers, trigger paths, stickout
  gauge, wire touch-off, overlap pointer, cutter side, umbilical routing,
  what to record. `sketches/session-states.svg`: 13 phases × element states.
- `machine-that-learns/ideas/observation-layer.md` — camera placement and
  resolution, red beam as a triangulation line, dry-run experiment list, a
  Klipper stack, and software never firing the laser.

## Findings that apply across arrangements

- **A slide along the tangent is the vertical-axis turn.** The joint is a circle:
  moving gun or work along the tangent by s turns the relative approach by s/R
  (0.93° per mm, R = 61.85 mm) and leaves the joint by only s²/2R (0.008 mm at
  1 mm). A −15° plan angle is 16.1 mm along the tangent plus 2.1 mm inward. Any
  X/Y carrier already owns the vertical axis; a Y error is a yaw error.
  (Found independently by four explorers.)
- **Tube length moves the corner.** OnlineMetals' published cut tolerance is
  ±3.2 mm; at the opening pose 1 mm of corner height moves the dot ~0.64–1 mm on
  the wall and focus ~1 mm. Anything referenced to the room or rotator needs a
  per-tube height set (both closures of one tube share it). *work-as-datum,
  workspace-as-structure*
- **The trigger press should close inside the shell** (Bowden lever, solenoid,
  servo presser), or it pushes the aim chain. A two-stage foot switch could
  enforce rotate-then-fire, but the rig's rule is that the pedal never commands
  the laser — Derek's call. *several*
- **Cable twist.** Rolling about the grip axis twists or swings the umbilical at
  the butt depending on the cable's exit direction. The scene's proxy draws the
  cable leaving along the grip's rake (~30° off the grip axis) and bending onto
  the grip axis within 70 mm; explorers who measured the first direction found
  ~0.87× twist per unit roll, one who measured the second found ~1.3°. The real
  exit direction needs the scan. Closed rings or bearings around the cable
  cannot be threaded without unplugging the QBH at the gun; openable loops,
  split bearings, open tracks or a nose-first bore through the gun are the
  alternatives.
- **The fiber's 350 mm emitting bend radius** makes the umbilical rise well above
  the grip before it can hang: ~416 mm above the bench at the opening pose
  (~680 mm at hole dial 65); every arrangement needs a support near that peak.
  *borrowed-ecosystems, corrected by one-knob-one-parameter*
- **Interlock contact.** The manual (p.32) says the laser stops without electrical
  contact between gun and workpiece; with wire feed the wire is presumably that
  contact, so the wire tip is a physical contact at the joint, and stickout must
  be reset after a stuck-wire snip. A plastic shell may affect whatever contact
  the gun senses. Unverified which part carries it. *several*
- **The nozzle clears the rim by only ~5–9 mm** at the proxy pose; whether a tube
  can slide out under a fixed gun depends on the real standoff (at 5 mm standoff
  the nozzle sits below the rim). Tube change needs ~10 mm down and ~50–60 mm
  radial, or ~70 mm down in the table arrangement. Only a hinge/retract that lifts
  up and back along the tangent side gets the wire tip out of the corner without
  touching the lip. *who-moves-what, machine-that-learns, sequence-of-use*
- **Where the gun body sits depends strongly on the hole dial.** At the opening
  pose (dial 30) the barrel is ~45° above horizontal and the grip base is ~234 mm
  off the tube axis on the −Y (tangent) side, ~372 mm above the bench; at dial 65
  the barrel is ~71° and the body sits nearly over the tube axis. The interior
  below the rim is clear within r < 45 mm, z < 45 mm. *work-as-datum, pose
  corrected by the coordinator*
- **Tacking vs a fixed-pose gun.** Plate hangers that bridge the rim cross the
  station whenever the table indexes between tacks; a stationary swivel hanger
  from the far side repairs it. How the plate is held at its recess before tacking
  is not recorded anywhere. *sequence-of-use, work-as-datum*
- **Stuck wire** pulls along the tangent; the backdrivable rotator can pull
  ~140 N at the bead. A floating gun is dragged; a stiff one bends the wire.
- **A stiff arm's sag barely reaches the dot** when the gun folds back along the
  arm with the nozzle near the arm's root (~0.005 mm for 4040 extrusion); joint
  compliances dominate. **Rotations about the dot turn drive slack into angle
  error, not dot error.** A translation placed between a rotation and the gun
  couples angle changes into the dot (~0.09 mm for 0.5 mm × 10°).
  *one-knob-one-parameter, machine-that-learns*
- **Derek's three axes each move several weld angles.** A pure +1° of work angle
  at the opening pose is roll −1.12°, hole +0.26°, vertical +0.56°.
  *one-knob-one-parameter*
- **Camera + red beam measures standoff**: a camera ~69° off the beam on the free
  +Y side sees ~3 px per 0.1 mm of standoff with the ELP already owned. If the
  idle red beam sweeps with the wobble, it can show the wall/cap split directly.
  *machine-that-learns*
- **Thermal growth** during the weld (~0.1 mm on the radius, estimate) is invisible
  in dry runs. **Gravity torques about the three axes** are small at the opening
  pose (0.2–0.75 N·m for 1–2 kg). **The manual's DB25 is labelled "for PLC
  integration"** (p.16); pinout absent. **The red-light centring adjustment** may
  shift the process beam too (unverified).

## Where the pass converged

Seven explorers produced a soft carrier docking into a kinematic seat, six
produced a still gun over a cross-slide or drawer under the rotator, five
produced a rim or tube rider, and four produced rotations about the dot. The
same VEVOR cross-slide, spring balancers and ball-in-vee seats recur. Those
families are real and developed; the next passes develop them as families
rather than eight times over, and spend the freed effort elsewhere.

Directions nobody has taken far yet (not a list to fill): printed compliant and
flexure mechanisms; tilting the work axis so gravity and access change; the
shop's existing machines and the welding cart as structure; the hand kept as
the actuator with a guide making it repeatable; overhead, wall or ceiling
structure and cable booms; the umbilical and wire path as the organising
principle; lockable goosenecks, jamming or hydraulic holding arms; cable-driven
parallel robots beyond the six-wire layout; teach-by-hand then lock or replay.

## Questions for Derek collected so far

Gun mass and centre of mass; trigger force; umbilical and wire-conduit pull and
stiffness at the grip; real nozzle standoff; whether the idle red beam sweeps
with wobble on; whether the red-light centring moves the process beam; which
part of the gun carries interlock contact during a wire-fed weld, and whether
the welder shows gun-to-work contact live; how the plate is held at its recess
before tacking; tube length spread; runout and ovality at the rim vs at the
plate level; whether 316 nipples may sit in the ports while welding; whether the
QBH may be disconnected once to thread a bearing; whether the wire feeder has a
jog; where the motor and ground towers sit around the tube. Individual notebooks
hold the full lists.
