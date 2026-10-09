# C — Hexapod with its pivot set at the dot: every freedom actuated, small range

## Picture it

**The mechanism.** Six identical NEMA 17 lead-screw legs on rod ends join two
printed parts:
- a base ring, on a manually set arm or portal;
- a platform that is the kinematic seat on the shell's outboard face, ~200 mm
  from the dot.

The pivot and the axes are software. "Fixed" is the coarse arm or portal.

**Branch C-p** (carry-and-locate): a gas strut on the axis preloads all six
legs in tension, and the legs become self-locking Tr8×2.

**Beside it, C-w**: carry-and-locate's six-wire robot, driven, with a comparison
table.

Sketches: [`../sketches/c-hexapod-side.svg`](../sketches/c-hexapod-side.svg);
carry-and-locate's `explorers/carry-and-locate/sketches/X-mtl-C-preloaded-hexapod.svg`
and `B-wire-located-suspension.svg`.

**Major unresolved:**
- Range ±7–10° about the dot.
- Open-loop dot scatter of 0.12–0.20 mm; the preload turns it into an offset.
- Deflection caused by the cable.
- Gun mass.
- The inverse-kinematics and calibration software.

---

Sketch: [`../sketches/c-hexapod-side.svg`](../sketches/c-hexapod-side.svg).
Numbers: [`../calc/hexapod_check.py`](../calc/hexapod_check.py).
Cameras and control: [`observation-layer.md`](observation-layer.md).

## The idea

Instead of choosing which motions to build, build all six at once in a small
parallel mechanism and make every axis — including where the rotations pivot —
a number. Six identical legs (NEMA 17 motors with integrated Tr8×8 lead screws,
~$21–23 each on Prime, a standard 3D-printer Z part) join a printed base ring to
a printed platform through M5 rod ends ($9.99 per four, Prime). The platform is
the kinematic seat on the shell's outboard face. The base ring hangs from a
manually set, lockable carrier — the portal of A/D, or B's column without its
stages. Coarse placement stays manual; the hexapod is the fine, fully actuated
last stage.

What is different: Derek's three rotations about the dot, the tangent-line work
angle, a roll about the beam itself, or any other axis are just different
arguments to one inverse-kinematics function. The station can literally run
"rotate 2° about the grip axis" and "rotate 2° about the tangent line" back to
back and let the camera compare them. For a machine that is meant to explore,
the choice of axes becomes something it learns, not something built in.

## Geometry (proposal)

Platform centre on the shell's outboard face at the opening pose, ~202 mm from
the dot; base ring 190 mm further out along that face's normal, i.e. above and
outboard of the tube — nothing crosses the tube's open top. Platform joints on a
60 mm radius, base joints on 120 mm, the usual paired 6-6 layout; nominal legs
207.5 mm.

The dot is not on the hexapod's own axis: it sits almost sideways from the
platform, ~200 mm away. That is the cost of a remote pivot: every rotation about
the dot is also a large sideways move of the platform.

## What the numbers say

From `hexapod_check.py` (proposal geometry, not optimised):

- ±10° about the dot needs up to **38 mm of leg change each way** (worst case:
  about the tangent line). A 100 mm integrated screw leaves perhaps 70–80 mm of
  usable stroke after nut and joint lengths, so ±10° is at the edge and ±7° is
  comfortable. Translations are cheap: 10 mm costs 5–10 mm of leg.
- Leg errors of ±0.05 mm (a plausible mix of nut backlash, motor-bearing axial
  play and rod-end play, all assumed) give a dot error of **0.12 mm median,
  0.20 mm at the 95th percentile**, open loop. The lever from platform to dot
  amplifies tilt errors.

## How it is used

- Coarse: loosen the carrier, put the gun roughly at the pose by hand (a pose
  block can do this repeatably), lock.
- Fine: the hexapod homes its six legs, the camera finds the corner, and the
  software closes the loop: command, look, correct. Static poses reach whatever
  the camera can resolve, not what the legs can do open loop.
- Weld: the six legs hold (lead screws do not back-drive easily); X-follow of
  runout is a small platform translation, recomputed every 100 ms. Trigger by
  the Bowden pedal.
- Stuck wire, lift-off: programmed moves, same as B.
- Tube change: a programmed retract within the hexapod's range is too small
  (~50 mm of clear radial move is needed); the carrier swings or slides the whole
  hexapod away, and the kinematic seat on the carrier brings it back.

## What I tried to break

**Control.** Klipper has no hexapod kinematics. Two routes: LinuxCNC has a
generic hexapod kinematics module (from my knowledge of it, not verified here);
or, since dry-run moves are quasi-static, a Python host computing leg lengths and
sending absolute positions to six MKS SERVO42D boards over RS485/Modbus (their
listing advertises absolute-position mode). Motion between poses need not be
coordinated; only the end pose matters. During a weld only tiny follow moves
happen, at µm/s.

**Open-loop accuracy is poor; the camera must close the loop.** 0.1–0.2 mm at
the dot from leg play alone, before printed-ring compliance. Repairs: preload
every joint (gravity already loads the legs one way in this hanging pose; add
springs across the rod ends), anti-backlash nuts, and — decisively — use the
camera as the position sensor for static poses. The hexapod is then an actuator
whose errors are measured, not a precision instrument.

**Varying cable load.** Unlike A, the gun moves, so the umbilical's pull changes
with pose. A parallel mechanism is stiffer than a serial chain for the same
parts, but printed rings and rod ends are the weak points. Measure (hang a
weight, watch the dot).

**Range versus pivot distance.** The farther the pivot, the more translation a
rotation costs. Moving the platform closer to the dot (to the barrel near the
body front, ~100 mm from the dot) halves the leg stroke per degree but puts
printed rings and rod ends within ~60–100 mm of the weld: heat, spatter, and
reflected 1080 nm light on plastic. Keeping them ~200 mm away is the trade.

**Singularities and homing.** Six legs must be homed (end switches or stall
detection) and the forward solution is iterative; neither is exotic, both are
work.

## Parts

Printed: base ring, platform/seat, leg end blocks, nut housings. Bought
(sourcing file): six NEMA 17 Tr8×8 integrated-screw motors, twelve M5 rod ends,
six SERVO42D boards (or six TMC2209 channels on the Octopus if LinuxCNC/Klipper
is not used), an RS485 adapter.

## Contribution, open problems, assumptions

Contribution: the most general "machine that learns" carrier — every freedom
actuated from one repeated part, with the pivot and axes defined in software;
it can test which axes are worth building mechanically before building them.

Open: range (±7–10°), open-loop accuracy (0.1–0.2 mm), cable-induced deflection,
and the software work. It depends on the observation layer more than any other
idea here.

Rests on: proposal geometry, assumed leg play, the scene proxy's face normal.

---

## Wave 3 — objections from carry-and-locate, a repaired branch, and the wire robot beside it

The original above stays as written. Sources:
`exchange/carry-and-locate--on--machine-that-learns.md` (§2, script
`explorers/carry-and-locate/calc/mtl_c_preload.py`, sketch
`X-mtl-C-preloaded-hexapod.svg`) and my own exchange on their six-wire
layout (`exchange/machine-that-learns--on--carry-and-locate.md` §2,
`calc/exchange/wire_robot_workspace.py`).

### Objection C1 — the legs do not keep one sign, and Tr8×8 back-drives

Both points are right, and the second corrects something I wrote.

- **Leg forces change sign.** Under gravity alone (2 kg, their CoM) the legs
  carry +20, −12, −2, +6.5, −3 and +4 N: three in tension, three in
  compression. Across ±7° with trigger, cable and wire-drag disturbances, four
  of them change sign. So the play in each leg's nut, motor bearing and rod
  ends is taken up on whichever side the load happens to be. My 0.12 / 0.20 mm
  (median / 95th percentile) open-loop dot scatter is the realistic figure, and
  it is also hysteretic. That makes "command, look, correct" slower: the
  correction itself can flip a leg across its play.
- **"Lead screws do not back-drive easily" was wrong for Tr8×8.** It is a
  4-start, 8 mm lead thread (lead angle ~20°), and it back-drives. Printer Z
  axes built on it drop when the drivers release.

### Branch C-p — gas-spring internal preload, self-locking legs (carry-and-locate's repair)

- **Preload.** A gas strut on the hexapod's axis pushes the base ring and
  platform apart, so all six legs are in tension. Their search: a 185 N push
  keeps every leg one-signed over ±7° with all disturbances. That drops to
  170 N with the trigger closed inside the shell and the cable carried, and to
  110 N if the gun is also floated at its CoM.
- **Parts.** A Farwind 150 N cabinet strut ($7.99 Prime) fits if the
  base-to-platform spacing grows from 190 to ~225 mm. Legs become NEMA 17 with
  an integrated Tr8×2 single-start screw and anti-backlash nut ($27.99 Prime):
  self-locking, and 4× slower, which does not matter at dry-run speeds.
- **What it changes.** Each leg's play becomes a constant offset, which the
  camera calibrates once. The closed loop then converges in one correction
  instead of hunting across a dead band. This is the general rule their view
  and mine meet on: **preload is what lets a camera loop converge; the camera
  is what lets a cheap preloaded mechanism reach tenths.**
- **What it leaves.** A higher constant load on the rod ends and printed
  rings (constant deflection, calibrated). The push needed scales with the
  real gun mass, CoM and cable pull. Range stays ±7–10°, because the pivot is
  still ~200 mm from the platform.

### Beside it: C-w, the six-wire robot (their layout, driven)

| | C-p (rigid legs, gas-spring preload) | C-w (six wires, two preloads, anchors on slides) |
|---|---|---|
| Play | constant offset after preload; still rod ends and nuts | none in the wires; slide play always on one side (tension pulls one way) |
| Dot stiffness | set by printed rings, rod ends, leg screws (not computed) | ~160 N/mm at the dot with a rigid frame (5 N → 31 µm) |
| Range | ±7–10° about the dot; ~38 mm of leg per 10° | roll ±10° (one wire), hole −10…+5°, plan angle ±15° as a tangent translation, dot ±5 mm; all wires stay taut |
| Where the actuators sit | ~200 mm from the dot, above the tube's +X side | ~400 mm away, on a frame |
| Structure needed | none beyond a coarse mount | a triangulated anchor frame tied to the rotator's frame |
| Clutter | compact, one module | wires around the cable exit and the joint camera's side (W1 passed 27 mm from its sightline) |
| Lift-off | a separate seat or retract | free: slacken the preload, lift, set back; the lengths are the memory |

**My position after the exchange.** C-w is the better "everything actuated"
option on play, heat and lift-off. C-p remains the choice where no anchor
frame or wire field around the gun is wanted. It is one compact module that
can bolt onto any coarse carrier (A's portal, B's column, E's gantry carriage),
and it pushes as well as pulls. Both keep what C was for: the pivot and the
axes are software, so the station can test which axes deserve hardware before
building them.
