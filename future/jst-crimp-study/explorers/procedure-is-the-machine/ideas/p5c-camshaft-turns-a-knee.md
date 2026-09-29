# p5c The camshaft turns a knee: one motor, one turn per conductor, crimp height from geometry

Sketch: [`../sketches/p5c-knee-cam-timing.svg`](../sketches/p5c-knee-cam-timing.svg)
(schematic timing and layout). Numbers: [`../calc/wave3.out.txt`](../calc/wave3.out.txt)
(cited as [calc wave3 §n]), [`../calc/wave2.out.txt`](../calc/wave2.out.txt) (cited as
[calc wave2 §n]), force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
§8 (cited as [calc FP §n]).

**A branch of [p5](p5-camshaft-one-revolution-per-conductor.md), and a
combination.** It keeps p5's one motor turning one shaft once per conductor,
the cassette on a rail with its printed rack as the escapement, and the skip and
end bumps as the program. Its tooling is [p1d](p1d-lift-once-fin-from-below.md)'s
station: *k* lifted 3.5 mm, the contact slid onto *k* from a post, a fin rising
from below through *k*'s empty slot, and a knee in a small steel C that drives
a narrow crimper to its straight position. The pairing is force-and-form's (its
FP2, from its f3 knee press); the steel is its f7 and f8.

What it drops from p5: the eccentric, the stop blocks, the presser that sets
every waiting conductor, and the tall free-standing fin. What it drops from
[p5b](p5b-camshaft-squeezes-the-hand-tool.md): the hand tool, its ratchet, and
the 8.7–14.7 mm lift.

## Picture it: J1 in its cassette on the rail

**Where things start.**
- J1's cassette sits on the carriage rail, loaded as in p1 with a root comb and a
  tip comb 5–7 mm behind the tip line. The webbed end was stripped whole with
  [p7](p7-strip-before-split.md)'s lever before the person peeled it, so every
  conductor arrives trimmed and stripped. The far end is in the pogo block.
- A two-tier **post bar** on the cassette's carriage holds J1's nine contacts in
  key order, odd keys on one tier and even keys 8 mm further forward (p1d).
- **The steel C** stands at the station line, spine ahead of the tips, throat
  toward the cassette: upper arm with the knee and the stepped crimper on two
  ground pins, lower arm with the fin in its slot and a gate wedge under the
  fin's foot, a 0.001 mm indicator across crimper and lower arm, foil gauges on
  the spine.

**The shaft.** Printed side plates carry a 10–12 mm steel shaft on two
bearings. A 12 V self-locking worm gearmotor, 40 kg·cm (3.9 N·m) at 10 rpm
[Prime: Greartisan, $26.99], turns it through a ~5:1 GT2 belt (a 20-tooth pulley
[Prime: GT2 pulley, 20T, $5.99] driving a printed 100-tooth one): ~2 rpm, one
turn in ~30 s plus the stops. An AS5600 on the shaft gives its angle [Prime:
AS5600, $7.99 for three]. On the shaft sit an index cam and pawl, a lift cam, a
post-bar Y cam, a fin cam (fin up, then gate in), the **knee lobe**, a pull cam
with its spring and switch, a lay-back and squaring cam, and a switch cam.

**One turn, 40–60 s** (schematic; the sketch):

| Degrees | What happens | Driven by |
|---|---|---|
| 0–25 | escapement advances the cassette one key (2.5 mm) | index cam + pawl |
| 25–50 | lift finger raises *k* 3.5 mm | lift cam |
| 50–60 | camera frame: bare length, brush | switch cam |
| 60–110 | post bar −Y: contact *k* slides onto *k* to the cam's depth | Y cam |
| 110–130 | fin up ~4.8 mm through *k*'s slot; gate wedge in | fin cam |
| 130–150 | knee lobe: wing curl; **the shaft stops at 150°** and the C reads *k* through the contact | knee lobe; controller |
| 150–200 | knee lobe drives the knee **through** straight to a stop just past it | knee lobe |
| 200–215 | lobe backs the knee off, re-touches at ~10 N; indicator reads height | knee lobe |
| 215–240 | knee open; gate out; fin down; post bar +Y off the box | lobe, fin and Y cams |
| 240–275 | hook drops into the neck and pulls 20 N through a spring; switch | pull cam |
| 275–320 | lift lowers *k*; squaring presser tidies the crimp into the row | lift and presser cams |
| 320–360 | switch cam: go, or stop before the next index | switch cam |

**The knee lobe goes through straight.** The crimper's lowest point is at the
knee's straight position, so the lobe's printed profile error does not reach
the crimp height, as a crank's does not at bottom dead centre. 0.2–0.5 mm short
of straight is 1–17 µm on 15–30 mm links [calc wave3 §3], and the lobe carries
the joint past straight onto a stop, where it cannot fall short at all.

**The one departure from "one motor, no software".** The shaft stops at 150°
while the C reads identity, and stops before the index if the switch cam's
checks fail. A self-locking gearmotor with an angle sensor stops wherever it is
told; so does a stepper.

**Key 3.** The skip bump lifts a lever that holds the post-bar Y follower and
the fin follower off their cams for one turn; J2's post for key 3 is empty
anyway. **End.** The end bump stops the shaft at 0°.

**Depth.** The Y cam's dwell fixes the depth for every key. The terms are the
strip-length tear (±0.2 mm, the largest), the Y dwell and the contact's own
reference: ±0.21 mm RSS [calc wave2 §3]. On top sits a systematic term: after
p7's straight strip line, the fan pulls the outer conductors' fronts back
0.05–0.16 mm for a single 4P or 5P, so each ribbon of a pair is stripped on its
own [calc wave2 §7]. The camera frame at 50° sees every bare length but a cam
cannot act on it. A small stepper on the post bar instead of the Y cam takes the
camera's correction (±0.07–0.09 mm) and is the branch **p5c-Y**; it is the only
departure from one motor besides the stops.

## What locates what

| Moment | Located | Against |
|---|---|---|
| Index | cassette | its own rack tooth and the escapement |
| Lift | *k*'s height | lift finger (frame) |
| Beside the fin | *k*±1 | the cassette's tip comb |
| Place | insulation edge in the window | post bar's Y dwell (or the p5c-Y stepper) |
| First die touch | contact on the fin | crimper's flare; post bar soft sideways |
| Crimp height | crimper to fin | knee at straight + gate wedge, inside the steel C |
| Timing | every motion | shaft angle |

"Fixed" for position is the printed frame and the shaft; for crimp height, the
steel C alone.

## What drives the crimp and carries its force

- The knee lobe pushes the knee joint sideways. Shaft torque follows from the
  crimp's work, 0.13–0.44 J over a 40–60° lobe: 0.12–0.63 N·m average and
  ~0.25–1.9 N·m peak, plus 0.1–0.3 N·m for the knee's friction and return spring
  [calc FP §8; profile factor an estimate]. p5b's lobe needs 2.1–3.2 N·m to
  squeeze an SN handle.
- The force loop is crimper → knee → upper arm → spine → lower arm → gate → fin
  → contact, inside the C (100–200 kN/mm [estimate]; ±1.5–6 µm of height scatter
  [calc wave3 §3]). The printed cam frame carries only the knee's 60–160 N
  input.
- The ~5:1 belt from the 10 rpm gearmotor gives ~19 N·m available at the shaft,
  far over the need; a NEMA 17 with a 26.85:1 planetary, 3 N·m permissible, not
  self-locking [Prime: STEPPERONLINE 17HS19-1684S-PG27, $41.91], also covers it.

## How it knows it worked

Identity at 150° through the C; the force curve from the spine's gauges against
shaft angle; the re-touched height every crimp; the camera frame at 50° and
again at 320°; the pull switch. The log keeps the cassette ID and key.

## Steps it covers, and what it hands back

- **Covered:** index, lift, look, place the contact on the conductor, crimp,
  measure height, proof pull, identity, square, skip and end, per conductor.
- **Handed back:** cut; strip the webbed end with p7's lever; peel; load the
  cassette (crossings in the loft); load the post bar in key order; insert (or
  bench C); label.
- **Minutes:** J1 takes 6–9 minutes of shaft time, a unit 35–53 minutes [calc
  wave3 §6]; the person's minutes are p1d's, ~40–44 a unit on the same task
  library [calc wave3 §6; estimate].

## Printed and bought

- **Printed:** side plates, face cams (PET-CF), follower levers, post bar, lift
  finger, squaring presser, cassettes with racks and bumps.
- **Steel:** p1d's C, knee links, stepped crimper and fin (f7's routes).
- **Bought** (Prime rows observed 2026-09-28): the gearmotor ($26.99) or the
  planetary stepper ($41.91), AS5600 ($7.99), GT2 pulleys ($5.99), a 10 mm
  ground shaft [Prime: $17.99 for four], 608-class bearings, roller micro
  switches ($5.99), BF350 gauges ($6.99), HX711 ($11.50), the 0.001 mm
  indicator ($52.99).

## Contribution

- **The camshaft machine with an upright crimp and a kinematic bottom.** Crimp
  height is a property of the knee's links and the gate wedge; the cams only
  have to carry the joint past straight.
- **The smallest motor of any camshaft here**, because the knee, not the shaft,
  multiplies force, and the crimp's work is under half a joule.
- **The program stays physical**: the rack's bumps, the blanked key and the empty
  post.

## Major unresolved problems

- **Everything p1d leaves open:** the steel, the contact's neck *n*, tip wander
  against 0.56–1.42 mm of fin clearance, the insulation crimp at a fixed step,
  wear of the gate and fin slide.
- **Fixed depth** at ±0.21 mm unless the Y cam gives way to a stepper.
- **Retiming means reprinting cams.**
- **The knee lobe's contact stress** on a printed cam: the knee's 60–160 N is
  far below p5b's 220–275 N, but a steel wear strip is still the safe side
  [calc wave2 §5 for the p5b case].
- **The proof-pull reaction** through the cassette clamp.

## What rests on assumptions

- The lobe's profile factor (2–3× average) and the knee's friction.
- The 40–60 s turn and the minutes.
- The C's stiffness, 100–200 kN/mm.
