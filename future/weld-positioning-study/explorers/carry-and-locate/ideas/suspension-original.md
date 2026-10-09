# A — Suspension, in Derek's original form, and what it becomes

**Picture it.**
- **Loops.** The gun, in a printed shell, hangs above the tube from two
  openable loops:
  - a **tip loop** on the graduated tube, 56 mm from the dot and ~34 mm above
    the rim;
  - a **base loop** just behind the grip butt, around the shell's rear collar
    and the cable, ~377 mm above the bench.
- **Wires and bungees.** Each loop hangs on a wire from an overhead bar ~950 mm
  up (ceiling, or a boom off the bench pegboard). A pair of opposed bungees
  centres it radially (X). Along the tangent (Y) it swings freely as a
  pendulum, because the joint forgives that direction.
- **Third ring.** An optional third ring high at the housing back takes weight
  and roll.
- **Cable and wire.** The umbilical leaves the grip butt along −Y onto a large
  saddle (bend radius ≥ 350 mm). The wire guide rides the barrel and reaches
  the dot through the tube's open top.
- **The tube** turns under it on the unchanged rotator.
- **Carry and locate.** Loops, wires and bungees carry. In Derek's form an arm
  gripping the shell locates; in the branches a lock at each loop does.
- **"Fixed."** The overhead bar for the loops (a carrier only); the rotator's
  frame for the arm or locks.

**Sketch:** `../sketches/A-suspension-original.svg` (true opening pose).

**Major unresolved problems:**
- The float alone does not hold a dot during the weld. A camera and motorised
  anchors cannot hold it through the weld-start push either
  (machine-that-learns), so a damper and a lock (A-r4c, A-r4d) or an arm are
  needed.
- Gun mass and centre of mass are unmeasured.
- The umbilical's saddle is large, and rolling the gun twists the cable (~0.87×
  the roll).

Sketch: `../sketches/A-suspension-original.svg` (plan and two elevations, drawn
from the scene's opening pose). Numbers: `../calc/loads.py`, `../calc/three_ring.py`.

## The original, kept as stated [Derek]

- A pegboard-style rubber-coated hook, made into a complete, openable loop.
- Each loop hangs from a wire that holds it in Z, and is held "steadyish" in
  one horizontal axis by two bungees (X or Y), so each loop has three lines on
  it: one up, two opposed sideways.
- One loop around the tip of the gun; one around the base of the gun, around
  the umbilical and wire feed.
- An arm "grips" the gun, where "grip" means a full printed shell with
  attachments anywhere on it, and gripping it in different places gives
  entirely different results.
- A third ring in various places reduces the range of motion (or raises the
  force to use it) while taking more weight.

Everything below develops that. The variants (A-r1 … A-r5) change it and are
kept separate; the original stays the reference.

## Placed around the actual gun and joint

At the scene's opening pose (grip 45°, hole 30°, vertical −15°), using the
scene's proxy gun **[Agent proxy of Manual drawing]**:

- The barrel rises at 45°, leaning back toward −Y and inward. The nozzle tip
  is ~5 mm above the rim; the beam (and the wire) enter the tube and reach the
  dot 6.35 mm below the rim. The housing sits beside the tube toward −Y (its
  centre 112 mm off the tube axis, 330–430 mm above the bench); the grip butt
  is 372 mm above the bench and 233 mm off the axis along −Y, and the
  umbilical leaves it nearly horizontally along −Y. **[Calc, pose.py, with the
  scene's 35° hole-dial offset]**
- **Tip loop** on the graduated tube, 56 mm from the dot, ~272 mm above the
  bench (~34 mm above the rim).
- **Base loop** 40 mm beyond the grip butt around the umbilical + wire
  conduit, ~377 mm above the bench, 314 mm from the dot.
- **Overhead**: wires rise ~570–680 mm to a bar ~950 mm above the bench. The
  bar can hang from the ceiling or be a boom off the VEVOR bench pegboard: it
  only carries (see "what fixed is fixed to").
- **Bungees**: two per loop, opposed, anchored to posts left and right.

### Which horizontal axis the bungees should hold

Derek left X or Y open. Around this joint the choice is not symmetric:

- The joint is a circle. A shift of the gun along the **tangent (Y)** slides
  the dot along the joint. It leaves the circle only by s²/2R: 0.008 mm for
  1 mm, 0.03 mm for 2 mm, 0.2 mm for 5 mm (R = 61.85 mm). It does turn the gun
  relative to the local tangent by s/R: 0.9° per mm. **[Calc]**
- A shift along the **radius (X)** moves the dot straight into the wall or
  away from it — the wall/cap split Derek's grip-axis roll exists to control.

So: **bungees on X, pendulum free on Y.** The soft direction lands on the
direction the joint forgives. That is a property of this joint and this
arrangement, not of suspension in general.

## What each element actually holds

| Element | Holds | Stiffness (estimate) | Free / soft |
|---|---|---|---|
| Wire in Z (per loop) | height of that loop | axial EA/L: ~13 N/mm (2 mm polyester grow-light rope, 500 mm), ~100–260 N/mm (1/16 in stainless rope) | horizontal: pendulum T/L ≈ 0.01 N/mm (5 N on 500 mm) |
| Bungee pair (per loop) | X centring | ~0.1 N/mm (two 3/16 in cords, assumed 15 N at 100 % on 250 mm) | nothing else |
| Round loop on round barrel | vertical support at the loop's low point; lateral self-centring T/gap (0.5–2.5 N/mm for 2–10 mm clearance at 5 N) | — | slides along the barrel; rolls about the barrel axis |
| Loop around bare umbilical + wire | the cable, not the gun | gun sees only the short cable segment's bending stiffness | cable can turn in the loop (important, see twist) |
| Loop around a shell collar at the cable exit | the gun, through the shell | as the loop | — |

Two points held on vertical wires leave the gun free to **roll about the line
through the two loop contacts**. At this pose that line is 9.4° from Derek's
grip axis, passes 32 mm from the dot and 14 mm from the grip butt **[Calc]**.
With a shell trunnion placed on the grip-axis line near the nozzle, the free
roll becomes exactly the grip-axis roll: the suspension then leaves free the
one rotation Derek wants to set separately (branch A-r2).

**Weight shares at this pose** (vertical wires only, gun 1.0 kg assumed, CoM
cases in the notes): the tip loop carries 56–68 % of the gun, the base loop
32–44 % plus whatever cable it holds. The CoM sits 40–55 mm off the tip–base
line in plan, so **0.39–0.54 N·m per kg of gun** must come from somewhere other
than the two wires: the arm, or the third ring. **[Calc]**

**The third ring**: three vertical wires set height, pitch and roll by their
three lengths. Placed at the housing back, the shares stay positive (tip
~3.0 N, base 0.7–2.2 N, third 4.7–6.7 N for a 1 kg gun). Placed at the housing
front top, the tip wire would have to push (−3.9 to −5.6 N): the gun tips.
At this pose the third ring belongs high at the back. With three rings
the vertical DOF are wire-stiff; X, Y and yaw remain pendulum/bungee-soft.
That is the "less range, more force, less weight each" trade Derek described,
now with a location for it. **[Calc, three_ring.py]**

## The arm gripping the shell in different ways

With the loops carrying, the arm's job and its best attachment change:

- **A1 near the tip** (just above the tip loop). The arm holds the dot through
  a ~40–60 mm lever: dot stiffness ≈ arm stiffness. Orientation changes swing
  the heavy rear of the gun in the loops' soft directions, which costs little
  force. The arm sees gravity only as the loops' spring forces times travel
  (≈ 0.1 N/mm × 20 mm = 2 N).
- **A2 at the CoM**. Loops carry; the arm sets pose; the arm sees almost no
  static moment. Dot stiffness is arm stiffness divided by lever effects —
  worse than A1 for the dot, better for orientation.
- **A3 at the base**. The tip loop's wire is a vertical fulcrum 56 mm from the
  dot. Raising A3 by 1 mm drops the dot ~0.2 mm and tips the gun ~0.2° — a
  built-in 5:1 reduction in Z and pitch. But horizontally the tip loop is soft,
  so A3 cannot hold the dot in X or Y; the gun would pivot about A3. Useful
  only for the vertical DOF, or with the tension-stiffened tip node (A-r3).
- **A4 on the housing top, ~85 mm off the grip axis**. With two loops holding
  the loop line, the arm sets only roll about it: the smallest possible arm (a
  lever and a screw).
- **At the trigger**: the arm's attachment can also be the actuator that
  presses the trigger, so the pressing force is internal to arm + shell.

## Breaking it

**Free motions.** Y pendulum at ~0.7 Hz (500 mm wire); X on bungees; yaw; the
roll about the loop line with two loops.

**What pushes on it** (magnitudes are estimates; see the notebook table):

- *Finger on the trigger* (3–8 N assumed) on the float alone: tens of
  millimetres. With A1 at 20 N/mm: ~0.25 mm. With a shell-mounted presser: zero
  net force.
- *Wire push and conduit spring* (1–3 N assumed): 10–40 mm on the float alone,
  0.1 mm on a 20 N/mm arm.
- *Umbilical.* The fiber must stay at R ≥ 350 mm while emitting **[Manual]**.
  A pegboard loop around the cable is a point support the cable bends over;
  what carries the umbilical has to be a large saddle, not a hook. And
  **rolling the gun about the grip axis twists the cable at the butt by ~0.87×
  the roll** (the exit is 30° off the grip axis): 45° of roll is ~39° of
  twist. A loop that clamped the cable 50 mm from the butt would put that into
  50 mm of cable (~780°/m); spread over a metre it is ~39°/m. "Twisting is
  strictly forbidden" **[Manual]**. A *loose, openable loop* lets the cable
  turn inside it — a reason for the loop to stay a loop, not become a clamp.
- *Stuck wire.* Bending a 0.030 in ER316L stick-out plastically at 10 mm takes
  ~3–5 N; the rotator can pull up to ~140 N at the bead (holding-torque bound,
  backdrivable belt). On the float alone the gun is dragged along Y, its
  pendulum direction, for as long as the pedal is held (~4 mm in 0.5 s at
  8 mm/s). The procedure's "snip while the head stays put" then no longer
  holds: the head has swung. With A1 the wire bends instead.
- *Wobble at 80 Hz.* A 0.1–2 N reaction on a free 1 kg gun moves it 0.4–8 µm.
  A ~1 Hz float isolates it; a stiff but undamped arm with a mode near 80 or
  160 Hz is the thing to worry about, not the float.

**Setup / dry run / weld / lift-off.**

- Setup: the float is excellent. The gun can be moved with fingertips and
  stays near where the float's equilibrium puts it. It returns to that
  equilibrium, not to where it was left; "stays where I put it" needs the arm
  or a lock.
- Dry run and weld: position accuracy is (force uncertainty)/(stiffness).
  With 0.1 N of unknown force and 0.1 N/mm, that is 1 mm. The float alone does
  not hold a dot; something stiff has to.
- Lift-off and tube change: the float makes these easy — lift the gun a few
  centimetres and hang its shell on a parking hook; the loops stay on it.
- Second closure (inverted, heavier, float rod inside): nothing changes above
  the rim.
- Second person: a bump swings the gun and it settles back near equilibrium,
  within friction and bungee hysteresis — not to within tenths.

## Repairs and branches (the original stays above)

- **A-r1 Float + arm (carry soft, locate stiff).** Loops carry gun and cable;
  an arm at A1 (or A2) locates. Dot error ≈ ΔF/k_arm + k_float·δ/k_arm. Soft
  loops help: a 5 mm drift of the float's anchor through 0.1 N/mm adds only
  0.5 N to the arm. The arm can then be light and printed; its stiffness at the
  dot sets precision (20 N/mm → 0.1–0.25 mm; 200 N/mm → 0.01–0.03 mm for the
  disturbances above). Open: which arm; its mode relative to 80 Hz.
- **A-r2 Grip-axis hang.** Tip loop replaced by a shell trunnion on the grip
  axis near the nozzle; base loop around a shell collar at the cable exit
  (also on the grip axis). Roll about the grip axis is then the loops' free
  motion. Two ways to set it: (a) leave the CoM 64–85 mm off the axis, so
  gravity presses the housing against one adjustable roll stop with ~2–4 N per
  kg — a gravity-preloaded single-contact locator for roll; (b) add ~0.5–0.7×
  the gun's mass as counterweight on the far side to make roll neutral, then
  lock it with a brake on a printed arc. (a) is lighter; its stop can be
  lifted off by a hand on the trigger (internal trigger needed).
- **A-r3 Tension-stiffened loops.** Each bungee pair becomes one stiff wire +
  one bungee pulling the other way: the wire locates, the bungee preloads. Tip
  and base nodes each stiff in X and Z, third ring stiff in Z: five stiff
  constraints, with only the tangent Y left free — the DOF the joint forgives.
  Add a soft Y centring and stops. This branch continues in
  `wire-located-suspension.md` (idea B).
- **A-r4 Soft for setup, locked for the weld.** Grow-light ratchets lock Z.
  Locking a bungee does not stiffen it, so lock the node instead: a printed
  clamp near each loop that grips a vertical rod on the frame. The float is
  used to place; the clamps make it a frame for the weld.
- **A-r5 Different contact at the tip.** A hanging V-block under the barrel
  instead of a round loop: the barrel sits in the V under its own weight
  share, located sideways up to that preload × the V's geometry. The contact
  condition (ring around a cylinder vs cylinder in a V vs trunnion in a notch)
  decides what the loop locates and what it merely carries.

## Parts that matter (see `../../../sourcing/carry-and-locate.md`)

- 1/8 in grow-light rope ratchet hangers (AC Infinity, Prime, in stock) — the
  Z line with one-hand length lock. Carrier only (polypropylene, creeps).
- 1/16 in 7x7 stainless wire rope + M4 turnbuckles (Prime, high volume) — when
  a line has to locate (A-r3).
- 3/16 in shock cord (Prime) — bungees / preload.
- Pegboard hooks (Prime; Derek's benches have pegboard) — parking and first
  experiments.
- Printed: the shell with loop seats (trunnion on the grip axis, collar at the
  cable exit, V-notches for hooks), a large umbilical saddle (R ≥ 350 mm).

## Contribution

- The suspension's soft directions can be matched to the joint: X held,
  tangent Y free, and the two-loop free roll aligned to Derek's grip axis.
- It separates the jobs cleanly: loops and saddle carry gun weight and cable;
  something else — arm, lock, tensioned wire, or seat — locates. Soft carriers
  disturb a stiff locator very little.
- It gives Derek's future motorised arm a light job: position a floating gun,
  not hold up a gun and a 5 m cable.

## Unresolved, and what rests on assumptions

- Gun mass, CoM, trigger force, umbilical weight/stiffness: all assumed.
  The loop shares and roll moments scale with them.
- At other poses, the tip/base shares and where the third ring
  belongs change; recompute with the pose script.
- The float alone does not hold a dot to tenths; every usable form here has
  a stiff locator somewhere. What the locator is stays open in A-r1.
- The umbilical saddle's size (R ≥ 350 mm) makes the overhead structure large.

## Pose note: the same arrangement at hole dial 65

The numbers above use the scene's opening pose with main.js's 35° hole-dial
offset (grip 45, hole dial 30, vertical −15). The first version of this file
passed 30 straight into `posePoint`, which is hole dial 65 — a steeper,
reachable orientation. At hole dial 65 the barrel rises at 71°, the housing
sits almost over the tube axis 360–490 mm above the bench, the grip butt is
485 mm up and 118 mm off the axis, and the umbilical leaves upward. There the
tip loop carries 80–95 % of the gun, the CoM sits 33–46 mm off the tip–base
line, and the roll moment is 0.33–0.45 N·m per kg. What does not depend on the
dial: the tip–base line's 9.4° angle to the grip axis (32 mm from the dot,
14 mm from the grip butt), the third ring's shares and its place at the housing
back, the X-bungee / free-tangent choice, and the ~0.87× cable twist.

## Wave 3: the exchange's objections, and two more branches

Machine-that-learns tested whether a camera plus motorised anchors could make
the soft float *hold* a dot, not just place it
(`../../../exchange/machine-that-learns--on--carry-and-locate.md`,
`servoed_float.py`).

- **Undamped** (as built, ζ ≈ 0.03): no stable loop exists with 30 fps and
  ~77 ms of delay.
- **With damping** (ζ ≈ 0.5): slow drift is nulled to < 0.1 mm, but the 2 N
  wire push at bead start still makes a 17 mm transient and a 5 N trigger a
  50 mm one.

**I agree, and it sharpens A-r1 and A-r4.** The float is a placer and a drift
canceller; something mechanical must hold during the weld. The float also
needs real damping before any servo is closed. The shop already holds one: an
**eddy-current damper** made from a copper vane on the tip node moving between
NdFeB magnets. The C110 bar the ground shoe was cut from is the vane stock. An
oil dashpot is the other option. Not sized here.

A feed-forward move at the trigger (the wire push starts at a known moment)
could in principle pre-empt part of the transient. Its size is unknown and
varies, so it is noted, not pursued.

### A-r4c (machine-that-learns): place soft, lock stiff, learn the lock

Their branch, summarised; the full text is in their exchange file.

- Winches on the Z wires and slides on the X bungee anchors, a damper on the
  tip node; the camera drives the float's equilibrium to the target.
- A split clamp at each node, closing on a vertical Ø16 mm steel rod on the
  rotator base (~240 N/mm at 200 mm).
- Every lock is measured, and the bias is learned so the float is placed at
  "target minus bias".
- Locked, the 2 N push moves the dot ~0.01–0.02 mm.

What my view adds, from `switch-lock-skate.md`:

- A split clamp is a **gap-closing** lock: it moves the node by part of its
  clearance, toward wherever it squeezes first. Learning the bias works if the
  scatter is small. That has to be measured.
- The float keeps carrying through the lock, so no load changes hands at the
  switch; that part of the shift is already gone.

### A-r4d: the bungee pushes a V-shoe onto the rod, a magnet locks it (a preload-increasing lock)

A variant of A-r4c that keeps Derek's X bungees in a new job.

- Each node carries a small V-shoe facing a vertical steel rod. The X bungee
  presses the V onto the rod: the rod now locates the node in X and Y, while Z
  still hangs on the wire and slides freely along the rod.
- A switchable magnet in the V-shoe (MagJig 95 class; its maker says it holds
  round steel) then locks Z by friction and stiffens the V contact.
- Because the V already touches before the switch, the lock only adds
  preload. The shift is micrometres of contact approach, not a share of a
  clamp's clearance.

Unlocked, each node can still be moved along its rod and around it. The
bungee's pull keeps the V seated, so the node's position across the rod is set
by the rod itself. This gives the suspension:

- carrying by wires and saddle;
- pre-location by bungee-seated V-shoes (the bungee's first real locating job
  in this study);
- locking by one switch per node.

**Left open:** the rods must avoid the table's indexing path during tacking; a
V on a round rod is a line contact (debris-sensitive); a magnet near the weld
needs a shield.
