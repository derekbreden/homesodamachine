# machine-that-learns — notebook

Framing: the arrangement is the first stage of a station that software can move
and observe, where an AI eventually runs laser-dot dry-run experiments across
tubes for hours. So: which motions to actuate first, which stay manual, what
partial arrangement is useful by hand today and grows, what cheap high-volume
motion/camera ecosystems give, and how observation closes the loop.

## Wave 1 — 2026-09-28

### Read

shared-context, working-method, weld-position.md, pose.js (and main.js for the
proxy shape and the 35° hole-dial offset), weld-rotation-rig.md, rotator README
and generator constants (tower positions), rotator firmware README, manual
pages 12, 17, 20. Ledger lines for the ELP camera (68° lens, IMX298) and the
Hgnova protective lenses.

### Files

- `ideas/observation-layer.md` — shared cameras, readouts, control stack, safety
  boundary, dry-run experiment catalogue. Not an arrangement; all four use it.
- `ideas/d-watch-first-seat.md` — no new motors: gun hangs on a magnet-preloaded
  kinematic seat under a bridge with two hand-wheel stages; cameras + screen.
- `ideas/a-still-gun-moving-tube.md` — gun, fiber, wire, camera never move; X
  (first new motor), Z and optional tilt are under the rotator. Branch A-tilt
  (differential Z vs trunnion through the dot).
- `ideas/b-rcm-gun-carriage.md` — X/Y/Z stages + hole-axis arc + grip-axis yoke,
  both rotations about the dot; every axis a knob first. Branch B2: purchased
  geared head with software re-centring.
- `ideas/c-hexapod-software-pivot.md` — six identical printer Z motors as a
  hexapod; pivot and axes are numbers; small range.
- `calc/` — pose port (`pose_points.py`), numbers (`arrangement_numbers.py`),
  tube-change clearance, hexapod check, sketch generators (all sketches are
  generated from the scene proxy so the gun is where pose.js puts it).
- `sketches/` — a-still-gun-side/front, b-rcm-carriage-side/front,
  c-hexapod-side, d-watch-first-side, observation-plan, observation-camera-view.

### Findings that changed how I see it

1. **Plan angle is a translation.** The joint is a circle, so turning the gun
   about the vertical line through the dot is identical, point for point, to
   translating it by 2R·sin(ψ/2) (−15° = 16.1 mm along the tangent + 2.1 mm
   inward; verified numerically to 1e-14 mm against the pose.js port). Any
   carrier needs X, Y, Z plus only two rotations; the "vertical axis" never
   needs a bearing, and a 0.1 mm tangent error is 0.09° of plan angle.
2. **In a remote-centre mechanism, drive compliance becomes angle error, not dot
   error.** Backlash or belt stretch in a rotation about the dot leaves the dot
   in place to first order. In an off-centre head the same compliance moves the
   dot by the lever (4.4 mm per degree at 250 mm). That is the real argument for
   building axes through the dot, beyond hand convenience.
3. **The gun's own red beam plus one camera is a triangulation rangefinder.** A
   camera on the free +Y side, mirror of the gun, sits ~69° off the beam: 0.1 mm
   of standoff moves the dot image ~3 px at 100 mm with the ELP already owned.
   If the idle reference beam is swept by the wobble, the line's wall/cap share
   is a measured version of the split Derek rolls the gun for.
4. **Actuation order** (from what each motion lets the machine learn): θ exists
   → X (corner finding, runout follow at 10–30 µm/s, tube-change retract) → Z
   (standoff, face runout) → roll/work angle → hole tilt → Y (plan angle,
   rarely changed). Manual first, forever: the kinematic seat, pose blocks, knobs.
5. **One interface on the gun, many carriers.** A kinematic seat on the shell
   (three balls, three steel-pin grooves, magnet preload) lets the same gun move
   from a hand-hung seat (D) to a fixed portal (A) to stages (B) to a hexapod
   (C) without changing the shell; every reseat is measurable by the camera.
6. **Tube change needs only ~50 mm.** Moving the tube (or the gun) ~50–60 mm
   radially puts every part of the gun proxy outside the tube's plan footprint
   (closest point 67.7 mm from the axis vs 63.5 mm OD at 50 mm), so the tube
   lifts straight out; drop Z ~10 mm first because the rim is ~5 mm below the
   nozzle tip.
7. The rotator's "pedal is the whole of the control" is the one current-design
   assumption a learning station collides with: dry runs need software to turn
   the table. Proposal: software motion only with the laser disabled; pedal stays
   the deadman whenever the laser is armed. Recorded, not changed.

### Tried and broke (details in the idea files)

- D: gravity-only seat fails in this orientation (seat normal 52° off vertical,
  cable tugs roll balls out) → magnet preload ~100 N. Bench-top wood between
  rotator and bridge → clamp both through the rotator base's holes or a common
  frame. Pose-block creep → measured overnight; aluminium drop if needed.
- A: X alone cancels eccentricity (tangential part just slides along the joint);
  face runout needs Z. Thermal growth during the weld (~0.1 mm on the radius for
  100 K, rough) is invisible to dry runs → learn from post-weld bead photos or
  seam-track later. Printer-style Z bed under 6–7 kg at 320 mm below the dot:
  rocking is 5.6 mm per degree at the dot → rails, or keep Z manual at first.
- B: five stages in series; constant loads during the weld make deflection
  constant, varying loads between poses must be measured. RCM centre drifts off
  the surface when standoff changes → software correction or a focus slide. Real
  cable exit is 30° off the grip axis in the proxy → ring bore and wire path need
  the scan.
- C: ±10° about the dot needs ~38 mm of leg change each way (edge of a 100 mm
  screw); ±0.05 mm leg play → 0.12 mm median / 0.20 mm 95th-pct dot error open
  loop → camera closes the loop for static poses.

### Sourcing highlights

SFU1605 ball-screw stages are a Prime commodity (7+ near-identical listings,
$54–74 with NEMA 17; a double-rail 150 mm-wide one $130.80 rated 120 kg); a
hand-wheel version with a revolution counter exists ($85.99, low stock). Klipper
controller (Octopus Pro $64.99, 50+/month). Closed-loop NEMA 17 boards $26 but
thin per-listing evidence. Photographic 3-way geared heads are a mature Prime
category ($147–250, one "100+ bought in past month"). No usable Prime 650 nm
band-pass filter; a Tiffen Red 25 + the camera's IR-cut is the cheap stand-in.

### Open questions

- For Derek: does the idle red beam sweep with the wobble? Trigger force and what
  the process switch does. Gun mass/CoM; how hard the umbilical pulls near the
  grip. Does the wire feeder have a jog button? Bench height in use.
- For me next: stiffness numbers for B's chain; A-tilt trunnion geometry drawn
  against the real rotator footprint; whether the grip axis can clear the real
  cable exit once a scan exists; verify SERVO42D encoder readout with coils off;
  Klipper extra-axis/rotary support for coordinated θ.

## Wave 2 — 2026-09-28 (exchange with carry-and-locate)

Read `context/examples-and-history.md`, `context/digest-wave1.md`, and
carry-and-locate's four ideas, notebook and calcs (as corrected for the 35°
hole-dial offset at 05:28 — their pose module now matches mine to 0.1 mm; a
few other explorers' ports still passed the dial value straight to posePoint
when I looked at 05:30: who-moves-what, sequence-of-use).

Wrote `../../exchange/machine-that-learns--on--carry-and-locate.md`; calcs in
`calc/exchange/` (`servoed_float.py`, `wire_robot_workspace.py`,
`sketch_follower.py`); sketch `sketches/exchange-follower-section.svg`.

What I found:
- **A camera cannot make a soft float hold a dot during the weld.** 1-DOF model
  of the tip node (1.5 kg, 0.1 N/mm, 30 fps, 60 ms): undamped, no stable gain;
  with ζ = 0.5 damping, slow creep is nulled to < 0.1 mm but the 2 N wire-push
  onset still makes a 17 mm transient and a 5 N trigger step 50 mm. Softness +
  camera = placer and drift canceller; the hold must be mechanical (~40 N/mm
  at the dot for 2 N → 0.05 mm). Branch A-r4c: place soft (motorised anchors,
  damper), lock stiff (clamp a shell node to a 16 mm ground rod, ~240 N/mm),
  learn the lock's bias with the camera.
- **Their six-wire layout as a cable robot**: roll ±10° is W6 alone; hole
  −10…+5°; rotating −10° about the vertical slackens a wire, but plan angle
  done as a tangent translation keeps all taut to ±15°. Dot stiffness ~31 µm
  per 5 N. Better than my rod hexapod on play (none), heat (actuators 400 mm
  away) and lift-off (free). I would retire C in favour of this as the
  "everything actuated" option.
- **Rim carriage → D-s, sense don't carry**: a 0.5–1 N ceramic stylus on the
  OD at the dot's angle, read by a caliper-beam scale, gives a weld-time radial
  reference (runout, ovality, thermal growth) that dry-run camera maps cannot;
  it drives my X stages. Wall-thickness variation is the unobserved residue,
  calibrated per tube against the camera map.
- Their load inventory and carrier/locator split would fix my B's main weakness
  (the serial chain carries the whole gun): add a balancer at the CoM and a
  saddle before the grip.

Derek's examples, through my view:
- **Automated-setup vision** lists exactly five motors — XY, Z, grip roll and
  "the opposite axis of roll" — and no vertical-axis motor. That is B's five
  motions, and consistent with plan angle being a Y translation. His PTZ
  cameras upgrade my fixed-camera layer: a 20× optical-zoom PTZ (~$450, Prime,
  100+/month) at ~1 m sees the corner at ~15–20 µm/px out of the spatter and
  can re-aim between dot, wire tip and whole station.
- **Table opening with the rotator beneath**: the most natural home for that
  vision. XY gantry at countertop height carries the gun (and the two rolls),
  the shelf carries Z under the table (also the tube-change move, ~70 mm down);
  the countertop around the opening is a large flat datum for fiducials and
  camera mounts. It is B with Z moved to the work side. Strongest candidate for
  my wave-3 development.
- **Suspension**: good placer, not a holder (numbers above); with a lock and a
  camera learning the lock, it becomes a legitimate automated positioner.
- **Monitor arm**: a carrier; with AS5600s on its joints it becomes a teach arm
  that records Derek's hand poses — the "teach by hand, then lock or replay"
  direction nobody has taken far.

Pose convention check (coordinator, wave 2): `calc/pose_points.py` has always
taken the hole **dial** and subtracted 35 before the pose.js math; every
sketch, the tube-change clearance, the camera angle and the hexapod check call
it with (45, 30, −15) as dial values. Verified: housing back (−60.1, −144.3) in
plan, 423.6 mm above the bench; grip base (−0.7, −233.5), 371.6 mm — the
coordinator's numbers. Nothing from wave 1 changes.

## Wave 3 — 2026-09-28 (objections to my ideas; Derek's table example)

Read `exchange/carry-and-locate--on--machine-that-learns.md`,
workspace-as-structure's `table-opening-gantry.md` and `drop-in-collar.md`,
and the work-as-datum ↔ workspace-as-structure exchanges (centre plunger W1/W1b,
paddle compass).

Objections worked (idea files carry labelled wave-3 sections; originals kept):
- **B.** Their roll-worm sign change came from moving the CoM ±50 mm while
  holding the grip axis fixed. With the axis moving with the gun (as B's
  stages move it), their own function gives +0.37…+1.77 N·m, one-signed. I
  disagree with the sign change, but a bias is still the robust answer because
  the CoM is unknown. Their stages-upstream point stands: 536 mm, 4.5–8.1 N·m at
  the Y carriage. Adopted B-f (90 % float offset 40 mm from the CoM) and B-o
  (open C-ring roll, first cable support on the arc carriage). Added B-t: move
  Z to the work side and make X/Y a low gantry under the gun body. The nearest
  stage then drops to 212 mm and 0.3–1.6 N·m. That is idea E.
- **C.** Legs change sign under gravity; Tr8×8 back-drives (my "lead screws do
  not back-drive easily" was wrong). Adopted C-p (gas-spring internal preload,
  Tr8×2 self-locking legs, spacing 225 mm) and put C-w (their six wires,
  driven) beside it in a comparison table. C-w wins on play, heat and lift-off;
  C-p stays as the compact frame-free module.
- **D.** A 100 N magnet seat 180 mm from the dot is unseated by a ~12 N hand
  trigger → D-b (balancer, tongue near the barrel, Bowden required).
- **A.** Hang the work lead; per-tube height by camera or plunger; stylus
  on the portal.

New idea: `ideas/e-table-opening-station.md` — Derek's table opening as the
home of his automated vision. His five motors (XY, Z, roll, "opposite roll")
are B's five, split as gun-side X/Y gantry + head and work-side Z shelf. Order
here: Z first (per-tube height and LOAD/WELD buttons; the largest error is
tube length), X second (stylus-driven runout follow), Y third, the two rolls
last. Height is measured by camera (E-h1) or referenced by work-as-datum's
plunger (E-h2), both driving the same Z motor. The stylus reaches down the
11.5–16.5 mm gap between tube OD and opening and must lift before LOAD.
Cameras: the table plane is 6.35 mm above the joint, so everything looks down.
A front PTZ across the bore sees the wall face-on; a +Y-end PTZ inboard sees
dot, wire and nozzle; the fixed joint camera measures; tags on the collar
register PTZ frames. Calcs: `calc/table_station.py`; sketches:
`sketches/e-table-station-plan.svg`, `e-table-station-side.svg`.

Biggest open problem: the roll/tilt head at countertop height (table top,
umbilical at 133 mm, wire path, camera sightline), which needs the gun scan.
Second: whether camera-triangulated cap height is good to ~0.05 mm on brushed
316L — the first thing an E0 station should measure.

## Wave 4 — 2026-09-28 (exchange with workspace-as-structure; the wire as an instrument)

Housekeeping: `calc/exchange/wire_robot_workspace.py` now imports a snapshot
copy of carry-and-locate's pose module (`calc/exchange/cl_pose_snapshot.py`)
instead of their live file.

**Exchange** (`../../exchange/machine-that-learns--on--workspace-as-structure-w4.md`)
on their cart station:
- Heat: their "2500 W power dissipation" sits under the manual's electrical
  parameters next to 35 % efficiency, so I read it as maximum draw. That gives
  ~1.3 kW of heat at full power and ~0.8 kW at 60 %, for about a minute per
  closure; the idle draw is unknown. Repair H1: make the loop's growth
  common-mode (matching height materials, short plate distances), put four
  printer thermistors on the loop via the Octopus's inputs, and fit dot drift
  against temperature with the joint camera, then compensate with X or prompt
  a re-trim.
- A constant cable shape stays constant only if the gun stays still. Branch M
  ("A on the cart") puts a ZBX150-class X stage under the rotator on the
  module, so the dot rises to ~1.06 m. Its ~50–60 mm retract replaces the gun
  park for loading. Umbilical, conduit, gun and joint camera never move.
  Cameras and fiducials ride the module; the controller goes on the side
  panel; an IMU logs bumps (no caster brakes).

**New idea F** (`ideas/f-wire-and-interlock-instruments.md`, sketch
`sketches/f-wire-path-side.svg`, calc `calc/wire_path.py`):
- Known from the manual:
  - interlock = clip on the work plus a complete circuit clip↔gun (p.19);
  - unconducted alarm (p.32);
  - key switch (p.31);
  - feeder on a 6-pin connector with Feed/Retract buttons (p.18–19);
  - pullback length after trigger release (p.23);
  - RS232 for supervisory software, DB25 for PLC (p.16).
- Inferred: in a wire-fed weld the wire makes the interlock contact.
- Nothing connects to or alters the welder. No injected touch circuit (the wire
  is in the welder's interlock circuit); every sensor is optical or mechanical,
  or a camera reading the unit's own indicators.
- Arrangement: fixed feeder behind the gun's tail; one-bend conduit in a
  printed trough (feed-force ratio ×1.2–1.5 vs ×4–11 hanging); a straightener;
  the gun's own bracket stays the guide; a SwitchBot/servo finger on the
  feeder's buttons; a 5.5 mm endoscope wire camera on the shell.
- Instruments: stick-out gauge; aim/cast gauge; optical touch-off by stage
  motion (0.13 N per pixel of stick-out bend at 12 mm; 0.01–0.05 mm
  overtravel; feeder jogs would overshoot 0.5–1.1 mm and bend the wire); corner
  by touch cross-checking the red-beam fit; the welder's own conduction
  indicator read by camera, if it shows without the trigger.
- New load case: pullback on a stuck wire pushes the gun's bracket toward the
  bead.
- Biggest open problem: whether the unit shows gun-to-work conduction with the
  trigger released (key off first). That decides whether an electrical touch
  sensor exists for free.
- Consequence: wire experiments want a still gun and a fixed feeder, another
  argument for motion on the work side (A, the cart station's branch M).

## Wave 5 — 2026-09-28 (final pass)

- Worked workspace-as-structure's critique of E into labelled branches in
  `ideas/e-table-opening-station.md`:
  - **E-y**, adopted: the stuck wire goes into tension and drags a belt Y
    silently, so a 20–30 N detent wired as a Klipper endstop. Any Y drive needs
    it, a ball screw included.
  - **E-c**, adopted: the first hard umbilical clamp ≥ 700 mm away, with a
    loose ring at the butt.
  - **Stylus:** use live reading − dry-lap map.
  - **Azimuth/height budget** on the +Y side.
  - **E-s**, their split mount: kept beside E. E for range, E-s for
    exactness; not a disagreement.
- Readability pass: every idea file now opens with "Picture it", sketch paths
  and major unresolved problems. Originals and break/repair records are kept
  below.
- The summary for the report was returned to the coordinator as text (the
  harness does not let this agent write a summary file).
