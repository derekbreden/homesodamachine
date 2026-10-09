# Carrier + seat: Derek's monitor arm and suspension, read as allocations

## Picture it (as it now stands)

**The idea.** Derek's monitor arm and his suspension are *carriers*: they take
weight, cable load and every large motion. A small locator takes position, and
only while docked.

- **D1-r (current form):**
  - The carrier is a gas-spring monitor arm, with a few millimetres of
    spring-held float between its plate and the shell.
  - It hands the shell onto a short **escape rail** on a post from the rotator
    base. The rail leans 32.5° from vertical, toward the tube's centre, in the
    radial plane at the station.
  - The gun slides down by 0.84 of its weight onto an adjustable stop, and the
    wire tip arrives along the corner's escape direction.
  - A recipe block sets roll and hole.
- **D2 and D3:**
  - Derek's two loops, made into openable journals centred on the grip axis,
    hang from two balancers carried by **one V-slot trolley**, which also carries
    the umbilical saddle (sequence-of-use).
  - The loops' roll hinge is **locked on ring B**: upright, gravity puts
    0.41–0.72 N·m on it.
  - The trolley parks the gun 420 mm away; it docks into D1's seat or rail.
- **"Fixed"** is the rotator base, the same datum as the nest.

**Sketches:**
- `../sketches/s5-carrier-and-seat.svg` (true opening pose; drawn with D2's
  rings and a three-ball seat);
- the escape-rail geometry is in `../sketches/s6-tilt-cradle-escape-rail.svg`,
  where the rail is vertical; upright it leans 32.5°.

**Major unresolved problems:**
- The gun's mass and centre of mass (the arm's minimum load is 2 kg).
- The umbilical's pull at the grip (it sets seat preload).
- Whether a rail stop repeats as well as a ball-and-vee seat.
- Heat and spatter on ring A (44 mm above the rim at the true pose).

## The original (wave 1)

**Allocation in one line:** a soft *carrier* takes weight, cable load and every
large motion: lift-off, swing-away for loading, gross placement. A small, stiff
*seat* on the rotator base takes location, and only while docked. Precision is
needed continuously only during the dry run and weld, and the seat provides it
exactly then.

Sketch: `../sketches/s5-carrier-and-seat.svg` (drawn with branch D2's rings and
balancers; D1 swaps them for a monitor arm). Numbers: `../allocation_calcs.py`
sections 3 and 6.

## Derek's originals, kept as he gave them

- **Monitor arm** (from "Repeat"): "arms designed to hold monitors in a
  position on a desk".
- **Suspension** (verbatim in `context/examples-and-history.md`): a
  rubber-coated pegboard hook closed into an openable loop, hung from a wire for
  Z, steadied by two bungees in one horizontal axis. One loop is round the tip of
  the gun and one round its base (round the umbilical and wire feed). A third
  ring reduces range of motion or raises its force while reducing weight further.

Read as allocations:

| | monitor arm | suspension (as given) |
|---|---|---|
| weight | gas spring (roughly constant force across its tuned range) | wire tension |
| Z | arm joints plus spring | wire length (stiff in tension) |
| horizontal | arm joints, friction-held | one axis bungee equilibrium (soft); the other a pendulum (softer) |
| orientation | VESA head tilt/swivel/rotate, friction-held | what each loop's contact allows; a loop on a round section allows roll about that section and sliding along it |
| location precision | none claimed | none claimed |
| lift-off, loading | move the arm | lift or swing by hand |

Both are **carriers**. The criticism "too flexible" or "it will sway" assumes
the carrier must also *locate*. Give location to something else and the
carrier's softness becomes an asset: the gun is weightless and easy to move, and
the locator carries almost no load. The pendulum numbers show how soft
suspension is. A 15–25 N gun on a 0.5–1.5 m wire has a lateral stiffness of only
0.010–0.050 N/mm, so a 1 N side pull moves it 20–100 mm (calc 6). The locator
must therefore resist the cable forces, not the carrier.

## D1 — monitor arm + kinematic seat

- **Carrier.** A gas-spring monitor arm (HUANUO class: 4.4–19.8 lb, 39.6 cm
  lift, 16.5k ratings, Prime), clamped to the bench on the −Y side. It holds the
  scan-fit shell by a printed VESA plate. The umbilical and wire conduit clip
  along the arm, so the arm carries their weight too. **Minimum-load catch:** if
  gun + shell is under ~2 kg, the arm floats up; add ballast to the plate, or
  let the float be the *lift-off* and hold the gun down on the seat with a latch.
- **Seat.** Three 12.7 mm steel balls bonded into the shell's underside, on a
  150–200 mm triangle. Three V's (pairs of dowel pins, or printed V's lined with
  steel) sit on a post screwed to the **rotator base**, the same printed datum
  as the ball race and the nest. The gun-to-tube chain is then short: shell →
  seat → post → base → balls → turntable → nest → tube. At the opening pose
  (hole dial 30) the gun lies out along −Y: the grip runs from about y = −150 to
  y = −234 mm, 347–372 mm above the bench, and the fiber leaves nearly
  horizontally along −Y. So the post stands at the base's −Y edge (y ≈ −140 mm),
  ~290 mm tall, with the V-plate under the grip, ≥150 mm from the weld and below
  the fiber's exit line.
- **Preload** against cable pull. Tipping needs P > 2FL/b (calc 3). With a
  150 mm span and 10 N at 150 mm, that is 20 N; at 250 mm it is 33 N. The arm's
  residual weight plus pot magnets or a cam latch supplies 30–50 N. A commercial
  75 mm magnetic base (Thorlabs KB75/M, 29 N magnets, 21 µrad mean / 82 µrad max
  reseat repeatability, observed) would need 40–67 N at those loads. That is why
  the DIY seat is drawn larger. Its repeatability is still excellent: 82 µrad at
  250 mm is 0.02 mm at the dot.
- **Recipe.** A printed recipe block between the post and the V-plate (roll,
  hole tilt), plus a small X/Y adjustment of the V-plate on the post. Y is yaw
  (1.08 mm per degree), X is radial. Z comes from shims under the V's or three
  fine screws.
- **Use.** Undocked: the arm holds the gun anywhere, and loading is trivial
  because the gun leaves the tube entirely. Docked: lower the shell, the balls
  find the V's, and the latch closes. Dry-run the dot, weld, unlatch, lift,
  swing. Stuck wire: stay docked and snip.

### Break it

- **Docking shock.** Magnets snap, and the gun "contains a vibration motor;
  handle it gently" (manual). Repair: let the balls seat under the arm's slow
  gas-spring descent, then engage a cam latch. No snap magnets on the gun side.
- **The arm's force changes with height.** A gas-spring arm balances at its
  tuned position. Docked, the arm always sits at the same height, so its residual
  force on the seat is constant, and constant loads calibrate out.
- **Cable forces go through the arm, not the seat,** if the umbilical is
  clipped along the arm and has a free loop between the last clip and the shell.
- **Per-tube variation is not followed.** The seat fixes the gun to the rotator
  base, not to the plate. Per-tube X/Z still needs the dot check and the V-plate
  adjustment, or the gauge foot of `tube-carries-the-reference.md` (3c).
- **Where "fixed" is fixed.** The post on the PET-GF base makes the base a
  structural member for the seat. Base flex under the post's moment moves the
  seat relative to the race. The loads are small because the arm carries the
  weight. Check with the indicator on the motor lamination (the repo's
  indicating datum).
- **Second person.** Dock, check dot, weld: the lowest-skill station of all
  four ideas.

## D2 — Derek's two rings, centred on the grip axis (a hinge while hanging)

Derek's loops sit "around the tip" and "around the base (around the umbilical
and wire feed)". The line from the grip base (cable exit) to the dot is the grip
axis. It passes 7.5 mm below the barrel's centreline at the nozzle tip and 17 mm
below at 20 mm back (pose.js proxy). So a loop round the tip and a loop round
the base are already almost on the grip axis. Make each loop's *contact* a
journal on the shell that is concentric with the grip axis, and the two loops
become **a physical hinge for grip-axis roll**, with the dot and cable exit fixed.
That is exactly Derek's rotation.

- **Ring A** round the barrel region at s ≈ 100 mm from the dot along the axis:
  36 mm from the gun surface. At the opening pose (hole dial 30) it is 44 mm
  above the rim and 92 mm from the tube axis, just outside the wall on the −Y
  side (computed). At dial 65 it would be 84 mm above the rim. The journal is
  an eccentric printed band on the shell, concentric with the axis, not with the
  barrel. The ring is openable (Derek's "openable loop") and PTFE-lined or
  3-roller.
- **Ring B** behind the butt at s ≈ 330 mm, on a short shell arm on the axis,
  clear of the fiber (the stub of `protractor-and-stub.md`). It is openable too,
  because the umbilical is there and cannot be threaded.
- **Hanging.** Each ring hangs from a 0.5–1.5 kg tool balancer (QWORK 2-pack,
  Prime, $16.97): constant force, so Z is weightless rather than wire-stiff.
  Bungees in one horizontal axis, as Derek had them.
- **What it gives:** a gun that floats weightless and rolls about the grip axis
  without the dot or cable exit moving. A shoulder on journal B stops sliding
  along the axis. Lock roll by clamping ring B.
- **What it lacks:** location. It is pendulum-soft in two translations and
  about the vertical. Pair it with the D1 seat (dock the hanging gun), with the
  rim rider (`tube-carries-the-reference.md`, which wants exactly a weightless
  gun), or with Derek's own hands. **Hand-guided but weightless** is itself useful
  now: it keeps his current practice and removes the weight and cable drag from
  his wrist.
- **Third ring** (Derek's): a third balancer-hung ring near the gun's centre of
  mass takes weight off A and B. It adds no constraint if its journal is also
  concentric with the grip axis. If it is not concentric, it resists roll, which
  is Derek's "increase the force needed to exercise that range".
- **Break:** ring A is 44 mm above the rim at the opening pose, just outside the
  wall, near spatter and reflected 1080 nm light. Use a metal hoop and a PTFE liner, and never a printed part in the beam
  path. Two balancer wires above the tube interior must stay out of the camera's
  view.

## Contribution / unresolved / assumptions

- **Contribution:** takes both of Derek's examples seriously as the *carrier*
  half of a split, and shows that his two-loop suspension already nearly
  coincides with his grip axis. It gives a concrete locating seat with its
  preload arithmetic, and it is the only idea where loading is trivial (the gun
  leaves entirely).
- **Unresolved:** gun + shell mass (sets arm choice and balancer class);
  umbilical stiffness at the grip base (sets seat preload); docking repeatability
  of a printed shell carrying steel balls (not measured); seat-post stiffness on
  the PET-GF base.
- **Rests on:** proxy geometry for the ring positions; estimated cable pulls
  (5–10 N) and masses (15–25 N).

---

## Wave 3: sequence-of-use's objections, and repaired branches

Source: `../../../exchange/sequence-of-use--on--who-moves-what.md` (their numbers
at hole dial 65). Re-checked at the true pose (dial 30) in
`../wave3_objection_checks.py`. D1 and D2 above stay as written; the branches
below repair them.

| Objection | Verdict | At the true pose / my addition |
|---|---|---|
| **2.1 Parking a balancer-hung gun**: pendulum pull-back of 4–8 N, two anchors that yaw the gun, and an umbilical shape that differs at every dock | Agree | Their repair, one V-slot trolley carrying both balancers and the cable saddle, becomes **branch D3**. Addition: their "lift ~30 mm, then roll" must start *along the escape direction* (below). A vertical lift in the upright tube drags the wire tip up the lip |
| **2.2 D2's roll is not free** (centre of mass 85 mm off the grip axis) | Agree, and it is **stronger at the true pose** | The grip axis is 30° above horizontal at dial 30 (65° at dial 65), so gravity's torque about it is **0.41–0.72 N·m** for 0.8–1.4 kg (0.20–0.35 at dial 65 in my model). A **roll lock on ring B** is required; roll becomes a setup adjustment. Derek's third ring as a counter-torque trims at one roll only (constant-force balancers) |
| **2.3 Docking is also the wire touch-down** | Agree | Stickout 1 mm short, then jog to touch (their K3). Addition: dock *along* the escape direction (branch D1-r) |
| **Stiff carrier into a seat over-constrains** (their lid's slotted hinge) | Agree | D1 needs a few mm of spring-held float between the VESA plate and the shell, so the arm only carries |

**Branch D1-r — arm carries, a short escape rail docks.**

- The seat post (on the rotator base, as in D1) carries a 60–80 mm **escape
  rail** along d = (−0.537, 0, 0.844) in the tube frame: 32.5° from vertical,
  leaning toward the tube's centre in the radial plane at the station. The rail
  ends in an adjustable stop; the recipe block sits between the carriage and the
  shell.
- The monitor arm, through its spring-float link, hands the shell onto the
  carriage at the top of the rail. The gun then slides down to the stop under
  0.84 of its weight.
- The wire tip therefore meets the corner *along* the escape direction, never
  dragged down the lip.
- A straight lift along d clears every feasible recipe tested (32 of 32;
  `../tilt_calcs.py`). After 43 mm the gun is outside the tube's cylinder or
  above rim + 30.
- The rail's stop replaces the three-ball seat as the locator. An HGR15 carriage
  is preloaded, so it has no play along its rail's normals, and the stop sets
  travel. That keeps location to one dial (the stop screw) plus the recipe block.
- *Leaves:*
  - whether a rail carriage plus stop is as repeatable as a ball-and-vee seat
    (both are micrometre-class in their catalogues; unmeasured here);
  - the column's position beside the tube: it must not stand inside the tube's
    cylinder, so its foot goes on the −Y side;
  - the arm's float link design.

**Branch D3 — one trolley (sequence-of-use's repair, adopted).**

- A 2040 V-slot rail ~1.25 m above the bench carries one trolley with both
  balancers and the umbilical saddle (arc R ≥ 350 mm). Parking lifts ~15 mm
  along d (the D1-r rail, or by hand along the barrel), then rolls ~420 mm to a
  detent. The lines are vertical at both ends of the rail, so the gun does not
  yaw, and the umbilical has one shape at every dock.
- *Leaves:* the rail's mounting (ceiling joists or two posts) and heat and
  spatter on ring A. At the true pose ring A is 44 mm above the rim, just
  outside the wall.

**What these change overall.** Derek's two carriers (arm, rings) stay as carriers
and gain a sequence that works: carry → hand onto the escape rail → slide to the
stop → lock roll → weld → lift along the rail → carry away. D2's "free roll while
hanging" becomes "roll set once and locked"; the hinge is still useful for
setting it.
