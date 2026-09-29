# v2 — An arm taught by Derek's hands carries the work between stations; docks and cameras do the precision

Explorer: machine-that-sees-and-learns.

Sketch: [`../sketches/v2-arm-docks.svg`](../sketches/v2-arm-docks.svg) (schematic).
Numbers: [`../calc/arm_and_feeder.out.txt`](../calc/arm_and_feeder.out.txt) §1–2
(**[calc: arm_and_feeder §n]**); ribbon-as-pallet's
[`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt)
(**[rap P §n]**); borrowed-machines'
[`cycle_and_arm.out.txt`](../../borrowed-machines/calc/cycle_and_arm.out.txt)
(**[bm arm §n]**). **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.

Related: the same topology (an arm as the operator walking between fixed
stations) is borrowed-machines'
[b5](../../borrowed-machines/ideas/b5-desktop-arm-as-operator.md) and Kurabo's
robot that "sets the wire into an ordinary terminal crimping machine"
[prior-art Start here]. The stations are [v6](v6-patient-cell.md)'s; the
queue is [v7](v7-the-run.md)'s.

## Picture it

**Where things start.**
- An **SO-101 follower arm** is clamped to the bench with its **leader arm**
  beside it.
  - The pair's bill of materials is $229.88, or $121.94 for a follower alone
    ([SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100),
    2026-09-28). On Prime: the follower electronics kit with six 12 V STS3215
    servos, $184.99 (thin listing); the SO-ARM101 Pro servo kit for leader and
    follower, $360.00; a Hiwonder SO-ARM101 kit assembled with printed parts,
    from $269.99 [Prime].
  - The joints are Feetech STS3215 serial servos with a 4096-count position
    sensor ([Waveshare wiki](https://www.waveshare.com/wiki/ST3215_Servo)).
- Around the arm, inside its reach, sit fixed stations: split and strip
  ([v6](v6-patient-cell.md)); the watched nest and press
  ([v1](v1-watched-nest.md)) or [v8](v8-tack-look-crimp.md)'s tack and crimp
  stations; the inspection booth ([v5](v5-inspection-booth.md)); a housing
  nest; a tray of finished looms.
- Cameras: one on the arm's wrist and one overhead, feeding the learned policy
  at 640 × 480 [source: LeRobot docs' examples]; and each station's own camera,
  for judging.
- The ribbon end is clamped in a **pallet**, or carries ribbon-as-pallet's
  snap-on backshell (branch below). Under the pallet, three **steel balls**; on
  top, a handle shaped for the SO-101's gripper.
- **Every dock:** three pairs of hardened dowel pins pressed into a printed
  body, which catch the balls; a magnet to pull the pallet home; a chamfered
  funnel with at least 5 mm of lead-in (borrowed-machines' b5).

**What moves.** The arm, and only coarsely.
1. It picks a pallet from the loading shelf.
2. It carries it into a dock's funnel and lets go; the magnet pulls the pallet
   onto its three contacts.
3. The station does its work and signals done.
4. The arm lifts the pallet and carries it to the next station.

**What locates what.**
- **Arm to dock:** the funnel and the magnet.
- **Pallet to dock:** the balls in the dowel pairs. Only steel touches steel, at
  877–1,658 MPa of Hertz peak, fine for hardened pins [rap P §7]; a ball on
  printed PETG flanks would peak at 67–126 MPa under 10–30 N of magnet, above
  PETG's ~50 MPa yield, and bed in. Seat repeatability [estimate: a few µm]; a
  dial indicator over 50 seatings measures it.
- **Pallet to contact:** the station's own small stage and camera, doing v1's
  hover-and-correct over the last few tenths of a millimetre.
- **Contact to die:** the nest.
- **The reference for "fixed"** is each dock's pins; the arm's own tip is
  never trusted for anything finer than "inside the funnel":
  - with every dock approached the same way, as taught waypoints give, the
    STS3215's backlash drops out and its 0.17° repeatability (Robonine test)
    gives ~1.2 mm RSS of tip wander, 2.2 mm worst; when approaches vary, its
    0.87° backlash gives ~6 mm RSS, 11.2 mm worst [bm arm §2];
  - published SO-101 repeatability is ±2–4 mm;
  - one encoder count alone is 0.38–0.54 mm at the tip [calc: arm_and_feeder §1].

  Placing a conductor over an open barrel (±0.15–0.5 mm) or a contact into a
  cavity (±0.2 mm) is an order of magnitude finer than the arm, and the ≥5 mm
  funnels take either figure.

**What drives the crimp and carries its force.** The station's press. The arm
lifts at most a pallet [assumption: SO-101 payload not stated in the README;
borrowed-machines notes its servos drop into overload protection under sustained
load].

**How it knows it worked.** Two separate judges: the **policy** decides when a
move is finished, from its own cameras; the **station camera** decides whether
the result is right (pallet seated, confirmed by a hall sensor or contact in the
dock; conductor laid in; contact latched). A station that says no sends the arm
back one step, or files an ask in [v7](v7-the-run.md)'s queue.

**What the person does.**
- **Once:** teaches. With the leader arm in hand and the cameras recording,
  Derek performs each subtask about 50 times ("pallet from shelf to strip dock",
  "strip dock to press dock"). LeRobot's guidance is at least 50 episodes a task
  ([LeRobot imitation-learning docs](https://huggingface.co/docs/lerobot/il_robots)).
  Four or five subtasks are ~4–6 hours at the leader arm
  [calc: arm_and_feeder §2]. Training an ACT policy takes "several hours" per
  policy, unattended, and LeRobot trains on Apple silicon
  (`--policy.device=mps`).
- **Per unit:** loads pallets onto the shelf and answers when a station asks.
- **When a station asks:** takes the leader arm and finishes the move;
  LeRobot's `dagger` rollout records the correction for the next training run.

**Steps it covers:** transfers between every station, flips and racking, and
possibly splitting the web by peel. **What it hands back:** every precise act
(to the stations); loading pallets, or snapping backshells in the branch;
teaching and retraining; answering the arm's asks.

## What the arm is for, since it is not for precision

- **Carrying pallets between docks.** 14 ribbon ends × 4–5 stations is ~56–70
  transfers a unit, 15–35 minutes of arm time [calc: arm_and_feeder §2].
- **A rigid object, not a floppy tail.** With the XH end made first, the tail is
  a bare cut end coiled in a cup on the pallet, its cut face in a pogo block;
  with the spool as the pallet ([v6](v6-patient-cell.md)'s branch) there is no
  tail at all. The Sogang system's lost cycles came from transferring a floppy
  cable with a finished end [prior-art Start here], the case this order of the
  ends removes.
- **Flips and racks.** Turning a pallet over for a second laser pass
  (borrowed-machines' b4), shelving and unshelving. A plain rail cannot.
- **Peeling, if the web zips** (repo Open item 5, untested). The pallet's clamp
  face is the tear stop. The arm grips one conductor near the tip and pulls
  sideways, and the pallet sets the parted length; the wrist camera watches the
  tear front.
- **Passive pallets.** Every pallet mechanism (lid, keys, pitch changer) is
  worked by the station, not the arm. The arm only carries, the task where 50
  demonstrations are most likely to suffice.

## Branch, not in its own file: the arm carries backshells

ribbon-as-pallet's [a3](../../ribbon-as-pallet/ideas/a3-backshell-that-ships.md)
snaps a 1–2 g printed clip onto each ribbon end: the datum, the recipe code, the
embossed label and, in the product, the strain relief.
- **What changes:** the arm picks looms from a tray by their backshells and
  docks each backshell in station holders; palleting, the person's largest share
  of time, becomes snapping 14 clips on; the holder's funnel takes out the arm's
  wander, and the holder, not the arm, seats the datum faces.
- **Uncertain:** whether a ~12 mm clip holds the ribbon against split, strip and
  insertion loads (tens of newtons on silicone); whether stations can fan and
  crimp with the ribbon held only there; whether a part on every loom suits the
  product (Derek's call).

## Problems, and what answers them

- **The arm is an order of magnitude too coarse for the XH steps.** It never does
  them. Every precise act belongs to a station with a dock, a small stage and a
  camera, which also makes the arm replaceable by a person carrying pallets.
- **A plain linear rail between stations is cheaper and more precise**
  (borrowed-machines' b5). True for a line of stations; the arm earns its place
  only for flips, racks and varied handling. For a straight line, a rail or
  [v1b](v1b-printer-as-stage.md)'s stage does the carrying.
- **Learned policies are brittle to lighting and camera bumps.** Fixed lighting
  under a hood; rigid camera mounts; demonstrations across small variations; a
  station's picture check catches failures, so brittleness costs time, not bad
  crimps.
- **Servo wear and drift over 60 units.** The docks absorb drift up to their
  capture range; retraining on fresh demonstrations is an evening.
- **A precise desktop arm instead.** A Dobot MG400 (±0.05 mm, $2,890–3,495
  [borrowed-machines, source]) could present conductors to an unmodified press,
  as Kurabo's does. It would not remove the need for pictures: curl and seat
  still have to be seen.

## Contribution

- It automates the least precise, most varied handling (carrying, flipping,
  racking, perhaps peeling), which the other arrangements hand back as "move it
  along".
- The arm is cheap and printable, and teaching it is the part someone who likes
  building things may enjoy [Derek, in the weld-study brief].

## Major unresolved problems

- **Teaching cost.** ~4–6 hours of demonstrations plus training, repeated when
  stations move; that is the harness labour of 5–8 units, spent once. Whether
  policies stay good across the program is unknown.
- **Success rates.** Published fine-manipulation policies reach 80–90 % on tasks
  like zip-tie threading (ALOHA) [prior-art §7]. At 90 % per transfer and ~60
  transfers a unit the arm would ask ~6 times a unit; wide funnels may do better.
- **Sustained load** in a flip, against the servos' overload protection.
- **Peel.** Wholly untested; it depends on the web.

## What rests on assumptions

- The arm's tip wander, from borrowed-machines' servo test and published figures.
- Seat repeatability until measured.
- The SO-101's payload margin with a pallet.
- Success rates borrowed from other tasks.
- That the web peels at all.
