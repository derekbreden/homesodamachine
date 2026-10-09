# B — Gun carriage: X, Y, Z stages plus two rotations about the dot, every axis a knob first

## Picture it

**Work side.** The tube turns on the bench as today.

**Gun side, a chain from a 4040 column behind the gun.**
1. Z, X and Y ball-screw stages.
2. A printed arc (R ≈ 285) centred on the radial line through the dot: tilt
   about the hole axis.
3. A yoke with two bearings on the grip axis: roll.

Both rotations pass through the dot, so drive slack becomes angle error, not
dot error. Plan angle is the Y stage, by the circle's symmetry. Every axis is a
dual-shaft NEMA 17 with a hand knob. "Fixed" is the column's footing on the
bench.

**Wave-3 branches:**
- **B-f** (carry-and-locate): a balancer biased to carry ~90 % of gun and yoke,
  so every drive stays loaded one way.
- **B-o** (carry-and-locate): an open C-ring roll bearing; the cable's first
  support rides the arc carriage.
- **B-t** (mine): Z moves under the work and X/Y become a low gantry. That is
  idea E.

Sketches: [`../sketches/b-rcm-carriage-side.svg`](../sketches/b-rcm-carriage-side.svg),
[`../sketches/b-rcm-carriage-front.svg`](../sketches/b-rcm-carriage-front.svg);
carry-and-locate's `explorers/carry-and-locate/sketches/X-mtl-B-float-and-open-ring.svg`.

**Major unresolved:**
- The stages sit upstream of the remote centre: the Y carriage is 536 mm from
  the dot and carries 4.5–8.1 N·m.
- The grip-axis bearings versus the real cable exit and wire path (needs the
  scan).
- Creep in the arc's wheels.
- Whether the closed-loop boards read a hand-turned shaft.

---

Sketches: [`../sketches/b-rcm-carriage-side.svg`](../sketches/b-rcm-carriage-side.svg),
[`../sketches/b-rcm-carriage-front.svg`](../sketches/b-rcm-carriage-front.svg).
Numbers: [`../calc/arrangement_numbers.py`](../calc/arrangement_numbers.py).
Cameras and control: [`observation-layer.md`](observation-layer.md).

## The idea

The tube stays on the bench, turning under the gun as today. The gun is carried
by a chain whose motions each mean one welding thing, so an experiment can change
one variable and nothing else:

| Motion | Physical joint | Welding meaning | Range (proposal) |
|---|---|---|---|
| X | ball-screw stage, radial | dot across the joint (cap ↔ wall); runout follow; retract | 100–150 mm |
| Y | ball-screw stage, tangent | **plan angle** (vertical-axis rotation), by the circle's symmetry | ±32 mm = ±30° |
| Z | ball-screw stage, vertical | height / standoff (with X: along the beam) | 100 mm |
| hole-axis tilt | printed arc, R ≈ 285 mm, centred on the radial line through the dot | tilts the whole gun and grip axis (travel lean) | ±25° |
| grip-axis roll | two bearings on the dot–grip-base line | wall/cap split | ±25° |

Two of Derek's three rotations are real bearings whose axes pass through the dot
(a remote centre of motion). The third, the vertical axis, is not a joint at
all: because the joint is a circle, turning the gun about the vertical line
through the dot is identical — for every point of the gun — to translating it
by 2R·sin(ψ/2) (16.1 mm for 15°; `calc`, section 1). The Y stage *is* the
vertical-axis control, and a 0.1 mm Y error is only 0.09° of plan angle.

**Every axis starts as a knob.** Each is a dual-shaft NEMA 17 ($20.38 Prime)
with a hand knob on its back shaft and a closed-loop board (MKS SERVO42D,
$25.99 Prime) behind it. Before any firmware exists, the axes are turned by
hand and the station is D with more freedoms. The boards' magnetic encoders are
meant to report the shaft angle even when a hand turned it (**not verified** —
if they do not, an AS5600 on the knob shaft does the same job for $4). When
motors are enabled, the same knob is a jog wheel. Manual and automatic are the
same mechanism.

## How it is carried

column (4040, standing at y ≈ −450 mm behind the gun) → Z carriage → X
carriage → Y carriage → **arc track** → arc carriage → **yoke** → rear ring
bearing + front stub bearing → shell → gun.

- **Arc track.** A printed arc (or several bolted segments) in the vertical
  plane x = +40 mm — 40 mm outboard of the dot, beside the tube — centred on the
  radial line through the dot. Its centreline radius ~285 mm, spanning 4°–60°
  of elevation on the −Y side (the grip base sits at 31° elevation, 273 mm from
  the hole axis). The low end is 20 mm above the dot but 280 mm along −Y, far
  from the tube. The carriage rides on V-groove wheels on the track's edges and
  is driven by a GT2 belt fixed at both ends of the arc (omega drive). A 20T
  pulley at 1/16 step moves the carriage 12.5 µm, 13 arcsec at this radius.
- **Yoke.** From the arc carriage an arm reaches ~100 mm inboard over the gun's
  outboard face to two bearings on the **grip axis** (the dot–grip-base line):
  - a ring bearing around the cable exit at the grip butt (the umbilical and
    wire conduit pass through its bore);
  - a stub bearing ~125 mm ahead of it, on the same line. The grip axis passes
    ~62 mm below the barrel at the body front, through the space in front of the
    grip where the hand would be. The shell fills part of that space with a web
    carrying the stub; the wire's path (offset to one side of the axis in the
    scene) passes beside it.
  The roll is driven by a printed worm on a sector on the rear ring (self-locking).
- **Camera.** Either on the frame (as in A) or on the Y carriage. On the frame,
  the dot stays at a fixed pixel only while X/Y/Z stay put.

## Why the remote centre matters to a learning machine

- **Drive compliance becomes angle error, not dot error.** If the arc's belt
  stretches or the roll worm has backlash, the gun turns slightly about the dot;
  the dot does not move to first order. On an off-centre head (branch B2) the
  same compliance moves the dot by the lever arm: 1° about a pivot 250 mm away
  is 4.4 mm (`calc`, section 5). Bearing and structural compliance still move
  the dot in either case.
- **One variable at a time is mechanical.** Sweeping roll changes the wall/cap
  split and nothing else — the dot stays on the corner, the cable exit stays
  put. For hand use: turn the roll knob and watch the red line tip between wall
  and cap, without losing the dot.
- **The cable exit stays still on the axis that changes most often.** Rolling
  about the grip axis moves the grip base 0 mm; 10° about the tangent line would
  move it 27 mm, about the hole axis 47 mm (`calc`, section 4).

## How it is used

- **Setup:** knobs or software bring the dot to the corner with X/Z, choose plan
  angle with Y, tilt and roll to the recorded pose. The RCM centre is calibrated
  once: roll ±10° with the red dot on the flat cap; the dot traces a small arc
  whose radius is the offset between the dot and the bearing axis; shim the
  shell seat (or record the offset and let X/Y/Z correct it).
- **Dry run:** software sweeps any axis with the table turning; the camera logs.
- **Weld:** pedal + Bowden trigger (no hand is on the gun). X/Z follow the stored
  runout map at µm/s. Release, release.
- **Stuck wire:** hold everything; snip; then the lift-off is a programmed move
  (for example 3 mm back along the beam, then Z up) — the same every time, which
  turns one of the hand skills Derek wants out of the process into a line of code.
- **Tube change:** X +60 mm (outboard) takes every part of the gun proxy with
  |y| < 66 mm outside the tube's plan footprint (mirror of A's retract), then the
  tube lifts out.
- **Second closure:** same geometry; the joint is at the top in both.
- **Second person:** loads a named pose; knobs still work.

## What I tried to break

**Five stages in series, cantilevered.** Column → three stages → arc → yoke →
gun is a long serial path, and the umbilical, wire conduit and gravity load it
differently at each pose. Where precision is needed matters: *during* the weld,
nothing moves but X/Z by micrometres, so what counts is that deflection under
constant loads is constant. Worm drives and ball screws hold without power;
the arc belt is backed by a clamp screw. What remains is structural sag that
changes between poses — the station can measure it (hang a known weight on the
gun, watch the dot) and either stiffen or map it.

**Gravity on the arc.** Gun + shell + yoke assumed ~3 kg, centre of mass
~180 mm from the hole axis: ~5 N·m, ~18 N on the belt at R = 285. Belt stretch
under that is an angle error (see above), not a dot error. The carriage wheels,
though, carry the load radially; POM wheels creep and their eccentric preload
sets the dot error. **Repair options:** steel-rod races pressed into the printed
arc under steel V-bearings; or a shorter, stiffer aluminium arc plate cut by a
fast-turn service.

**The RCM centre must be the dot, but the dot moves along the beam when standoff
changes.** If X/Y/Z move the gun 2 mm back along its beam, the bearing axes now
cross 2 mm in front of the surface; a 10° roll then moves the dot ~0.35 mm.
Either software corrects it with X/Y/Z, or a short focus slide inside the yoke
moves the gun along its own beam so the axes stay on the surface. The slide
shifts the cable exit off the roll axis by a few mm, which is harmless.

**The cable exit is not on the roll axis in reality.** The scene draws the
umbilical continuing along the grip axis; the grip direction at the opening pose
is 30° off that axis. Rolling ±10° swings the cable's exit direction by roughly
±5° around a cone. The ring bore must pass the QBH, the cable and the wire
conduit at that angle. **Needs the scan.**

**Heat and light near the joint.** Nothing in B's chain comes within ~60 mm of
the weld except the nozzle and the stub fork (~60–70 mm above the dot). A small
metal shield on the fork's underside; the printed arc is ~280 mm away.

**Axes through the dot must be built, then verified.** Printed parts will not
put two bearing axes through one point to 0.1 mm by construction. The camera
calibration (roll and tilt with the dot on the cap, fit the arcs) finds the
residual; small errors are corrected by X/Y/Z in software. A true RCM makes the
correction small; it does not make calibration unnecessary.

## Branch B2 — a purchased geared head instead of the arc and yoke

A K&F GD-3W PRO 3-way geared head ($159.99 Prime, "100+ bought in past month",
6 kg rated, 0.1° micro-adjust, three angle scales) on the Y carriage, the
shell's kinematic seat on its clamp. Three worm-driven, graduated, lockable
rotations arrive tomorrow. Their axes cross inside the head, ~150–250 mm from
the dot, so each degree moves the dot 2.6–4.4 mm, and the X/Y/Z stages (knobs
guided by the screen, or software) bring the dot back. Consequences: drive
backlash in the head becomes dot error multiplied by that lever; hand use means
"turn angle, then re-find the dot"; motorising the head's knobs is untested.
What it keeps: fastest path to adjustable, graduated angles, and a clean
comparison against the printed RCM on the same stages.

## Parts

Printed: shell (scan), yoke, arc segments, carriage, worm and sector, knobs,
camera mounts. Bought (sourcing file): three SFU1605 stages, five dual-shaft
NEMA 17, five SERVO42D boards, V-wheels, GT2 belt and pulleys, a thin-section or
printed ring bearing for the rear of the grip axis, small bearing for the stub,
Octopus Pro, 4040 column, balls/pins/magnets for the seat.

## Contribution, open problems, assumptions

Contribution: each commanded motion is one welding variable; roll and tilt keep
the dot mechanically; plan angle needs no joint; the same knob serves the hand
and the motor, so the station is useful from the day the stages arrive.

Open: stiffness of the serial chain; whether the grip axis can pass the real
cable exit and the wire path (needs the scan); arc bearing design; whether the
closed-loop boards read hand-turned shafts.

Rests on: the scene's grip-base location and pose (proxy); assumed masses; the
circle-symmetry result (exact).

---

## Wave 3 — objections from carry-and-locate, and the branches they produce

The original above stays as written. Source of the objections:
`exchange/carry-and-locate--on--machine-that-learns.md` (their scripts
`explorers/carry-and-locate/calc/mtl_b_float.py`, sketch
`explorers/carry-and-locate/sketches/X-mtl-B-float-and-open-ring.svg`).

### Objection B1 — gravity rides the whole chain

Their three points, and where I land on each:

1. **"The roll worm's load changes sign inside the workspace" (−0.8…+3.2 N·m).**
   *I disagree with the sign change, not with the concern.* Their script moves
   the centre of mass ±50 mm in X and Z but keeps the grip axis and the dot
   fixed. In B the X and Z stages carry the whole gun, so the grip axis moves
   with it and the torque about it cannot depend on X or Z. Rerunning their
   own function with the axis moving with the gun (3 kg, their CoM, roll
   20–70, hole dial 5–55): the roll load is **+0.37…+1.77 N·m, one-signed**.
   (`calc/table_station.py` §3 finds the same with 2 kg: +0.25…+1.18 N·m.) The
   arc drive's range is unchanged (+1.9…+5.7 N·m, one-signed).
   **What remains uncertain:** the CoM is assumed. A real CoM on the other side
   of the grip axis could put the sign change back. A deliberate bias (below)
   guarantees one sign whatever the scan and scale show.
2. **"The stages are upstream of the remote centre."** Agreed, and it is the
   serious one. The Y carriage sits ~536 mm from the dot. The gravity moment
   there spans 4.5–8.1 N·m across the workspace (their script, axes moving
   correctly; theirs said 4.1–8.5). With their assumed 0.1 mrad per N·m of
   carriage tilt, that is up to ~0.2 mm at the dot between poses. The RCM
   protects the dot from the arc and roll drives, not from the stages
   underneath them.
3. **The arc carriage's wheels carry the full weight radially.** Agreed; it is
   my own POM-creep worry, and it gets worse the longer the arc.

### Branch B-f — a float that carries, biased so every drive stays one-signed (carry-and-locate's repair)

- **What it is.** A constant-force spring balancer on a ≥1.2 m line from the
  ceiling or a boom. It carries ~90 % of gun + shell + yoke and is hooked ~40 mm
  off the CoM (at gun-local (36, −13, −38) mm, their search result).
- **What it changes.**
  - Both rotary drives stay loaded one way everywhere (+0.55…+1.70 and
    +0.60…+1.46 N·m).
  - The Z screw carries a steady ~3 N down.
  - The Y-carriage moment spread halves, to ~2.4 N·m.
  - For my view this matters because the camera's deflection map becomes
    small and single-valued: the same pose gives the same deflection whichever
    way it was approached. That is what makes "measure it and map it" honest.
- **What it leaves.** The line tilts as X/Z move and side-loads the chain by up
  to ~2 N (a free overhead trolley removes most of it). Nothing may touch the
  float between the last dry lap and the weld. The line must clear the column
  and camera sightlines.

### Branch B-o — open C-ring roll bearing; the cable's first support rides the arc carriage (carry-and-locate's repair)

- **What it is.** It replaces my closed ring around the cable exit, which could
  not be threaded without unplugging the QBH. Three V-rollers on the yoke run
  on a printed ring sector of ≥190°, so the umbilical and conduit drop in
  sideways through the ~170° gap.
- **Where the cable is carried.** The first cable support moves to the arc
  carriage, so X, Y, Z and tilt carry the cable along with the gun. Only roll
  changes the free span, and roll keeps the butt still.
- **What it changes.** The cable's pull on the gun no longer varies with X,
  Y, Z or tilt; it becomes a constant load on the arc carriage, folded into the
  float's bias.
- **What it leaves.** The fiber's tolerable twist per metre (the manual only
  says "strictly forbidden"). The real exit direction still needs the scan: at a
  30° exit, roll is ~0.87× twist at the butt; along the grip axis, almost none.

### Branch B-t — take Z (and the stages' lever) away from the gun (mine)

Point 2 above says a stage stack upstream of the remote centre undoes part of
the RCM's benefit, in proportion to its distance from the dot and the moment
on it. The same masses (gun + shell 2 kg, head 1 kg) and the same
roll/tilt range give (`calc/table_station.py` §2):

| Nearest gun-side stage | Distance from the dot | Gravity moment on it |
|---|---|---|
| B as drawn: Y carriage high behind the gun | 536 mm | 4.9–5.7 N·m |
| Low X carriage at countertop height, under the gun body (y ≈ −190) | 212 mm | 0.3–1.6 N·m |

So:
- move Z to the work side (a shelf under the tube, as in A and Derek's table
  opening);
- run X and Y as a low gantry just under the gun's body;
- mount the tilt arc and roll yoke on the X carriage.

The lever and the moment both drop by roughly 3–5×, before any float.
This is developed as idea E ([`e-table-opening-station.md`](e-table-opening-station.md)),
which is Derek's own table example.

**Still open for every B branch:** real gun mass and CoM; carriage tilt
stiffness (the 0.1 mrad/N·m is an assumption, which the camera can measure
with a hung weight).
