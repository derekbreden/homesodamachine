# b5 — A desktop arm as the operator of the other stations

Kurabo's harness robot "sets the wire into an ordinary terminal crimping
machine": the press is stock, and the robot is the operator [prior-art Start
here]. The borrowed-machine version uses a mass-produced desktop arm as the
person who walks between one-step stations: a laser or rip station
([b4](b4-laser-slits-and-scores.md), [b6](b6-pierce-at-the-root-pull-to-the-tip.md)),
a crimp cell ([b1b](b1b-applicator-in-slow-crank-press.md) or
[b2](b2-hand-crimper-in-a-frame.md)), an insertion jig and a tester. At the
cheap tier it moves cassettes, not conductors. At the precise tier it can be
the hand that places contacts and presents conductors.

**Related:** machine-that-sees-and-learns
[v2](../../machine-that-sees-and-learns/ideas/v2-arm-taught-by-hand.md) gives the teaching route and
cost; terminal-supply's [a6 post head](../../terminal-supply/ideas/a6-post-is-the-gripper.md)
is the end effector of the precise tier, a pairing terminal-supply proposed.

Sketch: [`../sketches/b5-arm-stations.svg`](../sketches/b5-arm-stations.svg).

Labels: [calc cycle_and_arm §n] is this explorer's
[`cycle_and_arm.out.txt`](../calc/cycle_and_arm.out.txt); [procedure calc §n] is
procedure-is-the-machine's
[`exchange_borrowed.out.txt`](../../procedure-is-the-machine/calc/exchange_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28).

## Picture it

**Where things start.** A ring of stations on one plate, each with a kinematic
dock (two cones and a vee, a magnet, a hall sensor that says "seated"):
- a rack of loaded cassettes;
- b6's rip board, or a laser dock;
- the pinch-pull and brush station;
- the crimp cell, with its own shuttle;
- an insertion jig;
- a continuity tester made from an XH header on an ESP32.

In the middle stands a desktop arm.

**What moves.** The arm:
1. picks a cassette from the rack by a handle and docks it at the rip or laser
   station;
2. flips it, if a laser needs the second face;
3. carries it to the pinch station;
4. docks it in the crimp cell and waits;
5. takes it to the insertion jig;
6. takes it to the tester;
7. returns it to the rack.

It approaches **every dock the same way**: from above, descending, with the
same payload. Each station does its own precise work against the cassette's
datum.

**What locates what; the reference for "fixed."** Each dock. The arm only has to
arrive inside the dock's lead-in; the cone-and-vee seat pulls the cassette into
place, repeatably to well under 0.1 mm [estimate, kinematic seats]. The cassette
carries its datum from station to station.

**What drives and carries the crimp force.** The stations. The arm carries a
~50–150 g cassette plus the loom's loose tail [estimate]. The slug pull
(24–65 N for a whole 5P tip) is too much for a small arm's wrist, so the pinch
station has its own lever and the arm only docks.

**How it knows it worked.** The dock sensors confirm each seating; each station
reports its own checks (camera, force curve, pull-back, continuity).

**What the person does.** Loads ribbon ends into cassettes at the rack, still
the largest share of person time here, and takes finished looms off. The arm
runs a unit's 14 ends unattended, in an afternoon.

## Steps it covers and what it hands back

- **Cheap tier:** none of the procedure's steps directly. It automates the
  carrying between steps, and the flips.
- **Precise tier:** place the contact and present the conductor (below).
- **Hands back:** loading ribbon ends into cassettes, unless the arm learns it;
  taking finished looms off; teaching and correcting the arm.

## Two tiers of borrowed arm

| Arm | Price | Precision | What it can do here |
|---|---|---|---|
| **SO-101 (LeRobot)** | follower electronics kit with STS3215 servos, $184.99 (1 rating); SO-ARM101 Pro servo kit, leader and follower, $360 (9 ratings, 50+ bought last month); Hiwonder assembled kit with printed parts, $269.99–459.99 [Prime]. $220–240 kit ([CNX](https://www.cnx-software.com/2025/05/02/so-arm101-open-source-dual-robotic-arm-kit-works-with-hugging-faces-lerobot/)); BOM $229.88 leader plus follower [machine-that-sees-and-learns, source] | STS3215 backlash **0.87°**, repeatability **0.17°** per joint ([Robonine](https://robonine.com/testing-of-feetech-sts3215-servomotor-backlash-repeatability-and-torque/)). At the tool, ~6 mm RSS from backlash if approaches vary; **~1.2 mm RSS (2.2 mm worst) if every dock is approached the same way**, so taught waypoints absorb the backlash; a flip reverses gravity on the wrist only, 0.15–1.2 mm [calc cycle_and_arm §2; procedure calc §13] | Dock-to-dock carrying with ≥5 mm lead-ins; flips. It cannot present a stripped conductor (0.72 mm strands into a 1.7–1.9 mm barrel) or find a 2 mm housing cavity unaided |
| **Dobot MG400** | $2,890 ([RobotSourced](https://robotsourced.com/robots/educational/dobot-mg400/)) to $3,495 ([Pololu](https://www.pololu.com/product/5400), in stock, backorders allowed); no Amazon route checked | **±0.05 mm**, 440 mm reach, 500–750 g payload, 16 digital I/O, air port [Pololu] | Everything above, plus the precise tier |

## The precise tier: the arm with a post head

The MG400 carries terminal-supply's post head: a 0.64 mm header pin in a
floating holder, with a stripper sleeve.
1. The arm spears a loose kit contact in a pocket plate over a backlight, lifts
   it, and measures in silhouette the distance from the holder face (the box
   front) to the conductor barrel's rear edge [terminal-supply calc wave2 §5].
2. It sets the contact on an open knife-set anvil, or carries it barrels first
   into the open SN-2549 jaws of [b2](b2-hand-crimper-in-a-frame.md), correcting
   by the measured offset. The crimper closes to captive; the sleeve strips the
   contact off the post.
3. It changes grip, picks up the cassette (or a work clamp holding the ribbon
   end), and presents each conductor to the captive contact along its axis.
4. The crimper closes.

That is Kurabo's pattern with the post as the only custom end effector. It
replaces a shuttle, a strip feeder and a fork with one bought arm, for a few
thousand dollars against a second-hand printer's axes.

## Where the arm's minutes are, and are not

**Carrying is the step that costs the person least.** The person's largest steps
in every arrangement here are loading, folding and splitting. Each of the
cheap-tier arm's own reasons has another route:

| Reason | Another route |
|---|---|
| Flips for the laser | two heads at the station, [b4b](b4b-diode-heads-at-the-station.md) |
| A rack of many cassettes | a magazine on one slide (procedure-is-the-machine p1) |
| The loose loom tail | the spool as carrier: no tail until the cut ([b8](b8-spool-fed-borrowed-line.md), [b8b](b8b-flat-spool-line-over-a-crown.md), procedure p3) |

**Where an arm could still earn its place** is the dexterous loading itself:
laying a cut ribbon end into a cassette channel, closing the clamp, lifting a
finished loom off with its tail. That is imitation learning on a deformable
object, outside the precision path. machine-that-sees-and-learns v2 gives the
teaching cost: LeRobot advises at least 50 demonstrations per task, ~4–6 h of
Derek's time for five subtasks [source, via v2]. With the SO-101's leader arm,
Derek teaches "lay this end in this channel" by doing it. It is untested on
silicone ribbon, and the precision still lives in the channel and the clamp,
not in the arm.

## Teaching it

- **Scripted waypoints.** Docks are fixed, so plain waypoints recorded once are
  enough for carrying, approached from one direction.
- **Imitation learning** for the untidy parts: lifting a cassette whose tail is
  tangled, laying the tail aside, recovering a cassette that did not seat, and,
  if it works, loading.
- **Not in the precision path** at the cheap tier; the stations provide it.

## Problems and their repairs, as they stand

- **A linear rail between stations does the carrying better.** Mostly true: a
  printer-axis rail carrying one cassette past the stations is cheaper and more
  precise. The arm earns its place only where a rail cannot reach: loading, the
  loose tail, and at the MG400 tier the placing and presenting itself.
- **The H2C's laser is enclosed and interlocked** [assumption], so an arm does
  not load it; the laser is a separate open-frame station in its own enclosure,
  or b4b's heads.
- **5 mm lead-ins against 6 mm of backlash** hold only because every approach is
  the same (~1.2 mm RSS, 2.2 mm worst). The loom tail's varying weight
  (≤15–20 g against a 50–150 g cassette [estimate]) is what remains.
- **The servos drop into overload protection.** The STS3215 can fall to ~20 %
  torque under prolonged load [Robonine]; the arm carries briefly and parks
  unloaded.

## Contribution

- A frame for turning separate one-step machines into an unattended afternoon
  run.
- The judgement that precision belongs in the docks and the cassette, not in a
  cheap arm, and the same-direction approach that makes cheap servos dock
  reliably.
- At the MG400 tier, a route to Kurabo's pattern with one custom end effector,
  the post.

## Major unresolved problems

- **Loom tail.** How the tail is managed through docks.
- **Loading by imitation.** Whether a learned policy lays silicone ribbon into a
  channel reliably. Untested.
- **Two purchases that differ tenfold.** Whether a $185–460 arm with docks, or a
  ~$3k arm that places contacts and presents conductors, fits Derek's idea of a
  machine worth building.
- **The post on the MG400.** Whether the arm's ±0.05 mm, a floating post and a
  silhouette correction reach the ~±0.1 mm axial placement the barrels want.
- **Person time.** Unless the arm learns loading, loading stays the person's job
  at every tier.

## What rests on what

- **Derek:** he likes building things; unattended running while the printers
  run is the premise.
- **Facts:** arm prices and specifications [Prime; sources above].
- **Calculations:** tool-tip stack-up [calc cycle_and_arm §2; procedure calc
  §13]; post capture and silhouette [terminal-supply calc wave2 §5].
- **Estimates:** cassette and tail weights; kinematic dock repeatability.
- **Assumptions:** printed cones and steel balls repeat to <0.1 mm; the H2C's door
  interlocks its laser.
