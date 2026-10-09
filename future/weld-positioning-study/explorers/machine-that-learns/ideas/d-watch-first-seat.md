# D — Watch first: the gun hangs on a kinematic seat, the station measures and shows

## Picture it

**No new motors.** A small 2040 bridge on the bench carries:
- two hand-wheel ball-screw stages with counters (Z, then X);
- a printed pose block;
- a kinematic seat: three steel-pin grooves with a pot-magnet preload, into
  which the shell's three balls snap.

The rotator sits on the bench unchanged, turned by its pedal. The joint camera
and a screen show dot-to-corner distance, wall/cap share, standoff and table
angle.

**What the hand does.** It only seats the gun, turns two wheels to the screen's
numbers, and fires.

**What "fixed" is.** The wooden bench top, which is a weakness.

**Branch D-b** (from carry-and-locate): a balancer carries the gun, the seat
moves nearer the barrel, and the Bowden trigger becomes required.

Sketch: [`../sketches/d-watch-first-side.svg`](../sketches/d-watch-first-side.svg).

**Major unresolved:**
- A hand press on the trigger unseats a 100 N magnet seat at a 150 mm lever
  (~12 N), so the Bowden trigger is required.
- Wood in the position loop.
- Creep of the printed pose block.
- Gun mass and umbilical pull, which size the magnet.

---

Sketch: [`../sketches/d-watch-first-side.svg`](../sketches/d-watch-first-side.svg).
Shared cameras and software: [`observation-layer.md`](observation-layer.md).

## The idea

The smallest station that already learns has no new motors. The gun, in its
scanned shell, hangs on a **magnet-preloaded kinematic seat** (three steel balls
on the shell, three steel-pin V-grooves on the carrier) under a small bridge. Two
hand-wheel ball-screw stages with revolution counters sit between the bridge and
a printed **pose block**: Z (vertical) and X (radial). The rotator stays on the
bench exactly as today, pedal and all. The joint camera and station camera
watch; a screen shows dot-to-corner distance, wall/cap share, standoff and table
angle while the human turns the wheels.

What makes it different from hand welding: the hand no longer holds the pose.
It seats the gun (the magnet snaps it home), dials two wheels to numbers on a
screen, and fires. What makes it the first stage of a learning machine: every
revolution is logged against a pose that can be reproduced exactly — the pose
block is a file and a part, the wheels are counts, the seat returns the gun to
the same place.

This is also the seed of everything else here: the shell, the seat, the pose
block, the cameras and the software carry over unchanged when motors arrive,
whether on the gun side (B) or the tube side (A).

## How it is carried and what is fixed to what

bench → bridge (2040 portal) → hand-wheel Z → hand-wheel X → pose block →
**seat** → shell → gun. The umbilical and wire conduit leave the grip butt
heading along −Y (the grip points almost exactly along the tangent at the
opening pose: direction (0.10, −0.99, 0.13) from `calc/pose_points.py`) to a
swivel saddle on the rear post, then fall to the cart in a bend of at least
350 mm radius. The wire conduit is bundled with the umbilical up to the saddle
and runs to the wire bracket under the barrel.

The seat sits on the body's outboard face (the gun's local +x side, which at the
opening pose faces up and outward: normal (0.78, 0.16, 0.61)). A seat there is
reached from above and outside the tube, so the bridge never crosses the open
top of the tube.

"Fixed" is the bench top. The rotator is clamped to it, and so is the bridge.
That is the first weakness (below).

## How it is used

- **Setup:** load and seat the tube as today. Hang the gun on its seat. Turn the
  table once with the pedal: the camera measures the corner position and
  standoff all the way round. The screen shows the runout at the dot itself,
  which is where it matters; the three M3 nest adjusters can be set against that
  reading instead of against the dial indicator on the OD.
- **Dry run:** dial X and Z until the screen shows the target (say, dot centre
  0.1 mm onto the cap, standoff at the recorded value). Pedal once more; the log
  records the residual.
- **Weld:** pedal, then trigger — by hand on the grip, or by a Bowden cable from
  a second pedal to a lever in the shell (see the safety boundary in the
  observation layer). Release trigger, then pedal, as today.
- **Stuck wire:** the gun stays on its seat; snip between nozzle and bead as the
  procedure says.
- **Lift-off / tube change:** peel the gun off the magnet, park it on a hook,
  swap tubes, reseat. The wheels keep their counts; the seat puts the gun back.
- **Second closure (inverted):** identical; the joint is at the top both times.
- **Second person:** seat the gun, read the screen, turn two wheels, pedal. The
  pose they are using is the part in their hand, with its numbers printed on it.

## Loads, freedoms, and what I tried to break

**The seat must not lift or rock.** Loads on it, all assumptions: gun + shell
15–25 N (gun mass not in the manual; 1.0–1.5 kg assumed, shell 0.4–0.6 kg);
trigger push 5–20 N if pressed by hand; umbilical pull at the grip butt 0–10 N,
direction depending on how it hangs. A seat held only by gravity in this
orientation fails: its normal is 52° off vertical, so gravity has a large
component along the seat plane, and a cable tug can roll a ball out of its
groove. **Repair:** preload with pot magnets (~100 N total) pulling a steel
plate on the carrier. With the preload five times the largest disturbance, the
coupling stays closed in any orientation and its stiffness is set by the
ball-on-pin contacts and the printed body behind the pins. **Left uncertain:**
how much the printed groove body deflects when the trigger is pressed. The
camera can measure it directly: laser disabled, press the trigger, watch the
dot.

**Reseat repeatability.** DIY kinematic couplings with hardened pins and balls
typically repeat to a few micrometres; with pins pressed into PET-GF I would
expect 5–20 µm at the seat (assumption). With ~60 mm between balls and ~180 mm
from the seat to the dot, 10 µm at the seat becomes roughly 30–40 µm at the dot.
This is one of the first numbers the station should measure (reseat 20 times,
record the dot).

**What "fixed" is fixed to.** The rotator and bridge are clamped to a wooden
bench top. Leaning on the bench, a heavy tool set down, or wood creep can move
one relative to the other. **Repair:** feet of the bridge clamped through the
rotator base's own bench-clamp holes (both share one clamp stack), or both on a
common extrusion frame as in A. The camera quantifies the problem before
anything is built: lean on the bench, watch the dot.

**Bridge sag.** A 2040 crossbar spanning ~560 mm with ~6 kg (stages + gun) at
mid-span deflects ~0.07 mm (plain beam formula, I ≈ 4.7 cm⁴ assumed for 2040's
strong axis). It is static and constant, so it moves the pose once, not during
a weld.

**Printed pose block creep.** PET-GF under a steady bending moment creeps. The
overnight drift experiment in the observation layer measures it; if it
matters, the block becomes an aluminium plate with printed angle wedges.

**Changing the pose.** A new pose means a new block (an hour or two on the H2C).
That is slow for exploring angles but ideal for fixing a proven pose. Branch
**D-hinge**: a pose block with one lockable hinge on the grip axis and an
AS5600 on it, so the roll can be swept by hand and logged. Its axis would not
pass through the dot unless the hinge sits on the grip-axis line; if it does
not, the X/Z wheels re-find the dot after each roll, guided by the screen.

**Runout is not compensated** during a weld: nothing moves but the table. D
measures it and lets the human decide (re-indicate, or accept). That measurement
is what tells whether A's or B's X-follow is worth building.

## Parts

Printed: shell from the MINI 2 scan (with the three ball sockets, magnet
pockets, trigger lever, and a window at the protective-lens drawer), seat body
with pressed dowel-pin grooves, pose block, camera hood and mounts, cable
saddle, index ring for the turntable.

Bought (see [`sourcing/machine-that-learns.md`](../../../sourcing/machine-that-learns.md)):
two hand-wheel SFU1605 stages with counters (YRJM, $85.99 Prime, only 4 in
stock — the motorised SFU1605 stage is the fallback and the upgrade), 12 mm
G25 balls (search level, $7.69/30), hardened dowel pins, pot magnets, 2040
extrusion, a second ELP camera, a Tiffen Red 25 filter, AS5600 boards for the
two wheels.

## Contribution, open problems, assumptions

Contribution: turns today's hand welding into a reproducible, logged setup
without any automation risk; measures the things (runout at the dot, reseat
scatter, trigger push, bench flex, drift) that decide how much motion is worth
building; every part is reused later.

Open: the gun's mass and the umbilical's pull (sets the magnet size); trigger
force; whether the seat location on the scanned body leaves the protective-lens
drawer, LEDs and wire bracket accessible; whether the wooden bench is stable
enough.

---

## Wave 3 — note from carry-and-locate's exchange

**Objection.** The seat carries the gun at 52° off vertical, 180 mm from the
dot, which is why it needs ~100 N of magnet. By their tip-off formula (balls
60 mm apart), 100 N resists only ~12 N at a 150 mm trigger lever, so a 20 N
hand press would unseat it. I had assumed 5–20 N of hand trigger force as
tolerable; it is not at the top of that range.

**Branch D-b (their float-and-dock applied to D).**
- A spring balancer at the CoM takes the weight. The magnet then only fights
  disturbances, so the seat's orientation stops mattering.
- A tongue near the barrel puts the seat 60–100 mm from the dot, which roughly
  halves the lever amplification of seat scatter.
- A cable saddle takes the cable before it reaches the gun.
- The Bowden trigger lever in the shell, already in D's safety boundary,
  becomes required, not optional.

**What stays uncertain.** Whether a tongue near the barrel can dodge the wire
guide and the joint camera's sightline; the real trigger force.
