# machine-that-learns — summary entries

The view: the station as something software can move and observe, where an AI
eventually runs laser-dot dry runs across tubes. Which motions to motorise first,
which stay manual, and how observation closes the loop.

Provenance. This explorer started without Derek's examples. A, B, C, D and the
observation layer come from beyond them. E is Derek's table-opening example. F
takes up a direction nobody had developed.

Conventions and sources:
- All geometry uses the scene's stand-in gun at the opening pose (grip 45, hole
  dial 30, vertical −15, with `main.js`'s 35° offset).
- Gun mass, centre of mass (CoM), umbilical force and trigger force are
  assumptions throughout.
- Sourcing: `../../sourcing/machine-that-learns.md`, observed 2026-09-28 in
  Derek's Chrome, Prime only.

## A — Still gun, moving tube *(beyond Derek's examples; six explorers reached a version of it)*

`ideas/a-still-gun-moving-tube.md` · `sketches/a-still-gun-side.svg`, `sketches/a-still-gun-front.svg`

The fiber, wire and measuring camera never move. The gun sits in its scanned
shell on a kinematic seat under a printed pose block, on a fixed 4040 portal.

Every software motion is under the tube:
- θ from the existing, unchanged rotator.
- A radial X ball-screw stage, the first new motor. It finds the corner, follows
  runout at 10–30 µm/s, and retracts ~50 mm for tube changes.
- A Z bed on three belt-linked screws.

Gravity loads the stack onto its screws one way, and the gun's loads are constant,
so their deflection is a one-time calibration. "Fixed" is one extrusion frame that
carries both the portal and the stack, taking the bench out of the loop.

**Break and repair.**
- X alone cancels eccentricity; face runout needs Z.
- Branch A-tilt for work angle:
  - A-tilt-1: differential Z, 5.6 mm per degree to re-centre.
  - A-tilt-2: a trunnion whose axis is the tangent through the dot.
- From the exchanges:
  - hang the work lead from above (carry-and-locate);
  - take height per tube from the work;
  - mount the stylus on the portal.

**Parts.**
- Printed: shell, seat, pose blocks, index ring.
- ZBX150 double-rail stage, $130.80 Prime, "15 left", 120 kg rated (listing).
- SFU1605 stages, $54–74 across 7+ Prime listings (commodity).
- Octopus Pro, $64.99 Prime, 50+ bought/month.

**Unresolved.**
- Thermal growth during the weld (~0.1 mm on the radius per 100 K, estimate) is
  invisible in dry runs.
- A rocking Z bed.
- A ~1.1 m working height.
- A dry-run mode for the rotator's firmware.

## B — Gun carriage: X/Y/Z plus two rotations about the dot, every axis a knob first *(beyond Derek's examples; matches his five-motor vision)*

`ideas/b-rcm-gun-carriage.md` · `sketches/b-rcm-carriage-side.svg`, `sketches/b-rcm-carriage-front.svg`

A column behind the gun carries, in order:
1. Z, X and Y ball-screw stages;
2. an arc (R ≈ 285) centred on the radial line through the dot, for hole-axis
   tilt;
3. a yoke with bearings on the grip axis, for roll.

Plan angle is the Y stage, because the joint is a circle. Every axis is a
dual-shaft NEMA 17 with a hand knob and a closed-loop board, so it works by hand
before any firmware exists. Remote-centre rotations turn drive slack into angle
error, not dot error.

**Break and repair (carry-and-locate).**
- Stages upstream of the remote centre still move the dot: the Y carriage is
  536 mm from it and carries 4.5–8.1 N·m.
- They found the roll-drive load changing sign. Here, with the axis moving with
  the gun, their own function gives +0.37…+1.77 N·m, one sign. The point stays
  open only because the real CoM is unknown.
- Repairs:
  - **B-f:** a biased balancer carrying ~90 %, so every drive stays one-signed
    (theirs).
  - **B-o:** an open C-ring roll bearing, with the first cable support on the arc
    carriage (theirs).
  - **B-t:** Z under the work and X/Y as a low gantry. The nearest stage is then
    212 mm from the dot with 0.3–1.6 N·m. This became E.
- **B2 branch:** a K&F GD-3W PRO geared head ($159.99 Prime, 100+ bought/month)
  with software re-centring. It is the fastest route to adjustable angles, at
  2.6–4.4 mm of dot motion per degree.

**Parts.**
- Dual-shaft NEMA 17, $20.38 Prime.
- MKS SERVO42D, $25.99 Prime (14 reviews, thin evidence).
- V-wheels and GT2 belt.
- Printed arc and yoke.

**Unresolved.**
- The grip-axis bearings against the real cable exit and wire path (needs the
  scan).
- Creep in the arc's wheels.
- Whether the closed-loop boards read a hand-turned shaft (unverified).

## C — Hexapod with the pivot in software *(beyond Derek's examples; kept beside the wire robot)*

`ideas/c-hexapod-software-pivot.md` · `sketches/c-hexapod-side.svg`

Six identical NEMA 17 integrated-lead-screw legs ($22.99 Prime; a standard printer
Z part) on M5 rod ends ($9.99 per four, Prime). They join a base ring, on a coarse
manual carrier, to a platform that is the shell's kinematic seat, ~200 mm from the
dot. Pivot and axes are arguments — Derek's axes, the tangent line, anything — so
the machine can learn which axes deserve hardware.

**Break.**
- ±10° about the dot needs ~38 mm of leg per direction.
- ±0.05 mm of play per leg gives a dot error of 0.12 mm median, 0.20 mm at the
  95th percentile.
- carry-and-locate: gravity puts legs in both tension and compression, so the play
  is two-sided and hysteretic, and Tr8×8 back-drives.

**Repair C-p (theirs).** A gas strut on the axis preloads all legs in tension
(~170–185 N; a $7.99 Prime strut if the spacing grows to ~225 mm), with Tr8×2
self-locking legs ($27.99 Prime). Play becomes a calibrated offset.

**Comparison with C-w, carry-and-locate's six wires as a cable robot.** C-w wins on
play, heat and free lift-off. C-p is the compact module with no anchor frame and no
wires near the cable exit, and it bolts onto any coarse carrier.

**Unresolved:** range; deflection under cable load; the inverse-kinematics and
calibration software.

## D — Watch first *(beyond Derek's examples; converged with float-and-dock, carrier-and-seat and others)*

`ideas/d-watch-first-seat.md` · `sketches/d-watch-first-side.svg`

No new motors. A bench bridge carries:
- two hand-wheel SFU1605 stages with revolution counters (YRJM, $85.99 Prime,
  "4 left", weak);
- a printed pose block;
- a magnet-preloaded three-ball seat.

The shell snaps into the seat and the rotator stays on its pedal. The joint camera
and a screen show dot-to-corner distance, wall/cap share, standoff and table
angle. The hand only seats the gun, dials two wheels and fires.

**What it measures:** runout at the dot rather than at the OD, reseat scatter,
trigger push, bench flex and drift — the numbers that decide how much motion to
build. Every part carries over when motors arrive.

**Break and repair.**
- A gravity-only seat at 52° off vertical fails, so it gets a ~100 N magnet
  preload.
- carry-and-locate: 100 N still yields to a ~12 N hand on the trigger at a 150 mm
  lever. Repair D-b: a balancer at the CoM, the seat moved nearer the barrel, and
  the Bowden trigger required.
- Wood in the loop: clamp the bridge with the rotator, or use a common frame.

**Parts.**
- Printed: shell, seat body, pose block.
- 12 mm G25 balls (search level, $7.69 for 30).
- Hardened pins, pot magnets.
- AS5600 encoders on the wheels ($7.99 for 2, Prime, 50+ bought/month).

**Unresolved.**
- Gun mass and umbilical pull, which size the magnet.
- Seat location on the real scan.
- Reseat repeatability: estimated 5–20 µm at the seat and ~30–40 µm at the dot,
  not measured.

## E — Derek's table opening as a motorised, observed station *(from Derek's example; built on workspace-as-structure's table and collar)*

`ideas/e-table-opening-station.md` · `sketches/e-table-station-plan.svg`, `sketches/e-table-station-side.svg`

**Derek's branch, kept.**
- The rotator on a four-corner, height-adjustable shelf under a table opening.
- A countertop-height gantry above: Y on rails either side, X along the gantry.
- A fitted shell, with the gun tangent to the circle.
- His vision: X, Y, Z and two roll motors, PTZ cameras, an AI iterating dry runs.

**What it became.**
- His five motors are the five that matter; the vertical axis is his Y rails.
- Z goes on the work side: a shelf on belt-linked Tr8×2 screws, motorised first,
  as LOAD/WELD buttons.
- Per-tube height comes from the work, since tube length (±3.2 mm) is the largest
  error. Two sources:
  - E-h1: camera triangulation;
  - E-h2: work-as-datum's centre plunger with workspace-as-structure's $23.99
    RS232 indicator.
- X/Y is a low gantry under the gun body. It carries the tilt arc and roll yoke,
  and cuts stage moments 3–5× compared with B.

**Sensing.**
- A stylus in the 11.5–16.5 mm gap between tube and opening drives X during the
  weld.
- A front PTZ across the bore sees the wall face-on; a PTZ at the +Y end sees the
  dot and wire.
- The joint camera measures, and collar tags register the PTZ frames.
- Representative PTZ: FoMaKo 20×, $449 Prime, 100+ bought/month. Its 10–24 µm/px
  at the corner is estimated.

**Break and repair (workspace-as-structure).**
- **E-y:** a stuck wire goes into tension and drags a belt Y (~60 N hold against
  the rotator's 140 N), losing steps silently at ~0.9° per mm. Adopted: a 20–30 N
  detent wired as an endstop. Any Y drive needs it, ball screw included.
- **E-c:** the first hard umbilical clamp goes ≥ 700 mm from the butt.
- **Stylus heat:** 50–100 K at the tip, so it reads the real thermal bulge. The
  weld-time signal is the live reading minus the dry-lap map at the same angle.
- **E-s:** their split mount (entry 8 in workspace-as-structure's summary) rides
  the plate, with rollers on a line through the dot and a tilt lead screw under
  the collar. It trades plan-angle range (−4.6…+2.3°) for exact, work-held
  position. Both are kept: E for range, E-s for exactness.
- **+Y side:** needs an azimuth and height budget. The camera, rollers, plunger
  arm and PTZ all want it.

**Unresolved.**
- The tilt/roll head at countertop height (E-s removes it).
- Whether camera-measured cap height is good to ~0.05 mm on brushed 316L.
- The bench cut, the gun scan and its mass.

## F — The wire path as the spine; the wire and interlock as instruments *(beyond Derek's examples)*

`ideas/f-wire-and-interlock-instruments.md` · `sketches/f-wire-path-side.svg`

The station is organised around the filler wire:
- a fixed feeder behind the gun's tail;
- the conduit held in a printed trough with one bend. Feed force is 1.2–1.5× the
  tip force, against 4–11× for a hanging conduit;
- a roller straightener. The cast offsets a 12 mm stick-out by 0.07–0.24 mm;
- the gun's own wire bracket, unchanged;
- a button finger on the feeder's own Feed/Retract buttons (SwitchBot, $25.99
  Prime, 700+ bought/month, 28k reviews);
- a 5.5 mm endoscope camera on the shell watching the wire (Teslong 5 MP
  autofocus, $49.99 Prime).

**Instruments.**
- A stick-out gauge.
- An aim and cast gauge.
- Optical touch-off by slow stage motion: ~0.13 N per pixel of stick-out bend and
  0.01–0.05 mm overtravel. Feeder jogs would overshoot 0.5–1.1 mm and bend the
  wire.
- The corner found by touch, cross-checked against the red-beam fit.
- The welder's own conduction indicator, read by camera, if it shows without the
  trigger.

**Known, inferred, untouched.**
- Known from the manual:
  - the interlock needs a complete clip-to-gun circuit (p.19);
  - the unconducted alarm (p.32);
  - the key switch (p.31);
  - the feeder's 6-pin connector and Feed/Retract buttons (p.18–19);
  - a pullback length after trigger release (p.23);
  - the RS232 and DB25 ports (p.16).
- Inferred: the wire makes the interlock contact during a wire-fed weld.
- Nothing connects to the welder's circuits, and no injected touch circuit is
  proposed.

**New load case:** pullback on a stuck wire pushes the gun's bracket toward the
bead.

**Unresolved.**
- Whether the unit indicates conduction with the trigger released (check with the
  key off first).
- The feeder's size, pull and minimum jog.
- The real bracket geometry.

## Branch on carry-and-locate's suspension *(Derek's example)*: place soft, lock stiff, learn the lock

`../../exchange/machine-that-learns--on--carry-and-locate.md` §1 · `calc/exchange/servoed_float.py`

**Can a camera plus motorised anchors turn Derek's soft loops (~0.1 N/mm at the
tip) into a holder?** A one-axis model (1.5 kg, 30 fps, 60 ms latency) says:
- Undamped, no stable gain exists.
- With ζ = 0.5 of added damping, creep is nulled to below 0.1 mm.
- The 2 N wire-push onset still makes a 17 mm transient, and a 5 N trigger step
  50 mm.
- So softness plus a camera is a good placer and drift canceller, but the hold at
  the weld must be mechanical: ~40 N/mm at the dot to keep 2 N within 0.05 mm.

**Branch A-r4c.** Derek's loops and saddle carry the gun. Motorised winches and
slides, with a damper, place it under the camera — his automated setup in
suspension form. Then a shell node clamps to a 16 mm ground rod (~240 N/mm at
200 mm), and the camera learns each lock's bias and places the gun ahead of it.

**Unresolved:** the node design on the real shell; the lock's scatter; the damper
hardware.

## Branch on carry-and-locate's six-wire suspension: driven as a cable robot

`../../exchange/machine-that-learns--on--carry-and-locate.md` §2 · `calc/exchange/wire_robot_workspace.py`

**Their layout, with anchors fixed and lengths driven.**
- Roll of ±10° moves one wire only (W6).
- Hole tilt covers −10…+5°.
- Rotating −10° about the vertical slackens a wire; the same plan angle done as a
  tangent translation keeps every wire taut out to ±15°.
- 5 N at the dot moves it ~31 µm (rigid frame).

**Repairs.**
- Constant-force balancers or a seventh motorised wire for the preloads.
- A keep-out zone for the joint camera (W1 passes 27 mm from its sightline).
- Anchor slides of ±10 mm (W1–W3), ±45 mm (W4, W5) and ±20 mm (W6).
- Camera self-calibration of the 36 anchor and attachment coordinates.

It beats the rod hexapod on play, heat and lift-off.

**Unresolved:** anchor-frame stiffness; clutter around the cable exit.

## Branch on carry-and-locate's rim carriage: D-s, sense don't carry

`../../exchange/machine-that-learns--on--carry-and-locate.md` §3 · `sketches/exchange-follower-section.svg`

Their carriage rides the thin lip at 10–20 N, references the rim rather than the
joint, and bonds the gun electrically to the work. This branch keeps the following
and drops the carrying:
- A 0.5–1 N ceramic stylus touches the tube's OD at the dot's own angle, ~9 mm
  below the joint.
- An iGaging Absolute Origin caliper with an SPC port is the scale ($47.77 Prime,
  900+ bought/month, 1,886 reviews). Reading its port with an ESP32 is a known
  hack, not verified here.
- It gives a weld-time radial reference for runout, same-angle ovality and thermal
  growth, which dry-run camera maps miss.
- It drives an X stage in A or E. The weld-time signal is the live reading minus
  the dry-lap map at the same azimuth (refined with workspace-as-structure).

**Unresolved:** wall-thickness variation; the seam bump; tip heat (50–100 K,
workspace-as-structure's estimate).

## Branches on workspace-as-structure's cart station

`../../exchange/machine-that-learns--on--workspace-as-structure-w4.md`

**H1 — heat.**
- The manual's "power dissipation 2500 W" sits among the electrical parameters, so
  it is read here as maximum draw. That gives ~1.3 kW of heat at full power and
  ~0.8 kW at 60%, for about a minute per closure; idle draw is unknown.
- Make the loop's thermal growth common-mode, with matching height materials and
  short distances on one plate.
- Add four printer thermistors on the Octopus's inputs, and let the joint camera
  fit dot drift against temperature.

**M — "A on the cart".**
- A ZBX150-class X stage under the rotator on the module; the dot sits at
  ~1.06 m.
- The stage's ~50–60 mm retract replaces the gun park, so the gun, umbilical,
  conduit and joint camera never move and the constant cable shape stays constant.
- A PTZ on a front-corner mast and a station camera on the rear mast.
- Tags on the module, and an IMU logging bumps (the casters have no brakes).

**Open disagreement.** workspace-as-structure holds that a cable force that repeats
with pose is still usable; here, the first gun-side motor undoes the constant
shape. A two-sided approach test with the camera would settle it.

## Transferable pieces

- **Plan angle is a translation.** A turn ψ about the vertical line through the
  dot equals a tangent slide of 2R·sin(ψ/2), 16.1 mm for 15°. It is exact to
  1e-14 mm on the proxy, and four explorers found it independently. No carrier
  needs a vertical-axis bearing, and it keeps cable robots taut.
- **Observation layer** (`ideas/observation-layer.md`):
  - The joint camera goes on the free +Y side, ~69° off the beam. The owned ELP
    16 MP gives ~23 µm/px at 100 mm.
  - The red reference beam plus one camera is a triangulation rangefinder,
    ~3 px per 0.1 mm of standoff.
  - A wobble-swept red line would show the wall/cap split.
  - PTZ cameras are registered by printed tags.
  - A printed index ring gives absolute table angle.
  - Software never fires the laser; the trigger goes through a Bowden pedal.
- **Motor order, by what each motor lets the machine learn.** θ, then X, Z, roll,
  tilt, and Y last. In the table station, Z comes first because tube length
  dominates.
- **Knob-first axes.** A dual-shaft motor with a hand knob and an encoder, so
  manual and automatic use share one mechanism.
- **Preload and camera loops need each other** (with carry-and-locate). A
  one-signed drive load turns play into an offset the camera can calibrate.
- **A soft carrier is a placer, not a holder** (numbers above).
- **Weld-time sensing.** The dot is blind in the glare, so use the stylus or shell
  fiducials.
- **Remote-centre rotations** turn drive slack into angle error, but stages
  upstream of the remote centre still move the dot.
- **Motion on the work side** keeps the cable shape, wire path and camera still —
  the most learnable configuration. Wire experiments need a still gun, which
  constrains every gun-side-motor arrangement.
- **New load cases:** a stuck wire in tension (workspace-as-structure) and pullback
  on a stuck wire. Both belong in carry-and-locate's load inventory.

## Questions only Derek's observation can answer

1. Gun mass and CoM; umbilical and conduit pull at the grip; trigger force.
2. Does the idle red beam sweep with the wobble motor?
3. With the clip on and the trigger never pressed, does the unit's screen or the
   gun's LED show wire-to-work contact? Check with the key off first.
4. The feeder: size, where it sits, the Feed/Retract button feel, the conduit's
   minimum bend, the spool's cast, and the pullback length currently set.
5. The unit's cooling-air path and idle draw.
6. Can the camera see the corner and dot on real brushed 316L? One test frame with
   the owned ELP would show it.
7. The bench height in use, and whether cutting a top is acceptable.
