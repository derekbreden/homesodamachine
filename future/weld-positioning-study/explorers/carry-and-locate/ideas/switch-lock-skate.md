# E — Supports that switch state: the switch-locked skate, and its relatives

**Picture it.** Two forms are kept.

- **E-RA** (work-as-datum's repair R-A, plus my roll pad, wave 5):
  - **The dot.** A small hanger on the endcap being welded carries a cup: a
    spherical band centred on the dot. Three balls on the shell's nose sit in
    it, so the dot is held by the work and the gun can turn freely about it.
  - **The tail.** At the grip butt, a ball on the shell drops into a round
    vertical bore in a switchable-magnet shoe. The shoe skates on a steel plate
    on a post from the rotator frame. Sliding it turns the gun about the dot:
    hole tilt and plan angle.
  - **Roll.** A second ball, 40 mm off the grip axis, rests on a screw pad on
    the same shoe.
  - **Lock and memory.** One twist locks everything; magnetic stops on the
    plate remember the angles.
  - **Carry.** A balancer carries the gun and a saddle the cable.
- **E, the original.** The same switchable-magnet shoe on three ball feet, but
  at the end of a tongue from the nose, skating on a plate beside the tube. The
  plate is then the dot's reference.

In both, the float carries through the switch so nothing changes hands.

**Sketches:**
- `../sketches/E-RA-cup-and-tail.svg` (E-RA, true opening pose);
- `../sketches/E-switch-lock-skate.svg` (original E, true opening pose).

**Major unresolved problems:**
- **Original E:** it makes the room the dot's reference. Debris, switch twist,
  tube length and runout all reach the dot at full or amplified scale
  (work-as-datum's critique, accepted below).
- **E-RA:**
  - the cup's centre must be the dot (calibrate by turning the gun and
    shimming);
  - the cup pads sit ~40 mm from the puddle;
  - the hanger depends on nipples in the ports;
  - the cup must be seated by a spring, not by weight.
- **Both:** the MagJig's real force across the ball stand-off, and its knob
  twist, are unmeasured.

Sketch: `../sketches/E-switch-lock-skate.svg`. Numbers: `../calc/skate.py`.
Pose: the scene's opening pose with the 35° hole-dial offset.

A support that switches state is a carrier in one state and a locator in the
other. What matters about such a support:

- what it does to the pose at the moment it switches (**lock shift**);
- which contacts carry which loads in each state.

The rest of this file is about those two things.

## Lock shift, in general

Three different things can move the gun when a lock engages:

1. **Load changing hands.** If a hand (or a spring, or a motor) was carrying
   part of the gun when the lock closed, letting go moves that load onto the
   lock, and the lock deflects by load / stiffness. A float that keeps carrying
   the gun through the switch removes this almost entirely. This is the main
   reason to pair any lock with a carrier.
2. **Gap-closing locks.** Split clamps on rods, collets, set screws, ball-head
   clamps and central-lock arms all close a clearance. The part moves by some
   share of that clearance, in a direction set by where the clamp squeezes
   first. Typical scale: hundredths to tenths of a millimetre per joint, and
   joints in series add up. Machine-that-learns' A-r4c rod clamps and every
   articulated arm are in this class.
3. **Preload-increasing locks.** Contacts are already touching, and the lock
   only presses them harder: a switchable magnet or a vacuum pad pulling three
   ball feet onto a flat. The shift is the change in Hertzian contact approach,
   a few micrometres, plus anything the switching action itself pushes (a knob's
   twist).

So the best-behaved lock presses contacts that already touch, while a float
carries the load across the switch.

The alternative is no lock step at all. A lead-screw slide is held by the same
screw that moves it, so it has no switch and no switch shift (noted in the
who-moves-what / sequence-of-use exchange). Borrowed-ecosystems classes ball
heads and magic arms as "parking and support only": one lock frees several
axes at once. Switching supports earn their place where a pose is set by hand
in seconds and must then hold without a screw per axis.

## The original arrangement (E): a switchable-magnet shoe skating on a steel plate beside the tube

**Physical idea.** A metal tongue on the shell leaves near the barrel (70 mm
up from the nozzle), reaches out over the rim on the +X side and ends in a
**shoe**:

- a Magswitch MagJig 95 (0.1 kg, 55.8 × 33 × 45.7 mm) in a small body;
- three 10 mm chrome balls as feet.

The shoe stands on a horizontal **steel plate** ~53 mm above the rim, beside
the tube, carried by a steel post from the frame that carries the rotator.

- **Carry:** a spring balancer at the gun's centre of mass carries ~95–100 % of
  the gun and shell. A saddle carries the umbilical before it reaches the gun.
- **Locate:** three balls on a flat fix Z and the two tilts. Switch the magnet
  on and friction also fixes X, Y and yaw.

**What the plane gives the hand.** The shoe sits 61 mm from the dot
horizontally and 53 mm above it. Sliding it on the plate moves the gun in X, Y
and yaw, and relative to the joint those three motions are:

- **X** — the dot across the corner (radial);
- **plan angle** — Y along the tangent is 0.93° per mm; yaw is equivalent;
- **a slide along the joint that does not matter.**

So the hand has three freedoms, two of which matter, with no screw in the way.

**Height** is the plate's height: a screw or wedge under the plate, or a shim.

**Hole tilt and roll** come from a pose block between shell and tongue (as in
one-knob-one-parameter's and machine-that-learns' pose blocks), or from the
spherical branch E-dome below.

**Memory.** Once the pose is taught, two small magnetic stops are set against
the shoe's side pins and switched on: a V-stop against one pin, a flat stop
against another. The stops are the taught pose. This is the machinist's "part
on a magnetic chuck against stop blocks".

### States, and what carries what

| State | Gun weight | Cable | Wire push / drag | Hand or trigger | Pose held by |
|---|---|---|---|---|---|
| Unlocked, sliding | balancer (95–100 %) | saddle | — | the hand slides the shoe (friction ~0.6 N at 3 N residual) | nothing: equilibrium plus friction |
| Locked | balancer (unchanged) | saddle, residual into the shoe | shoe friction and ball contacts | trigger closed inside the shell | three balls on the plate plus magnet friction |
| Lifted (tube change) | balancer | saddle | — | a finger lifts 15–20 mm, or a parking hook | nothing; the stops keep the memory |
| Returned | balancer | saddle | — | push the shoe into the stops, switch on | balls + stops, then magnet |

### Numbers **[Calc, skate.py; estimates labelled]**

- **Magnet [Magswitch spec]:** 43 kg normal breakaway, 4 kg shear working
  load at 2:1, so ~78 N shear breakaway (μ ≈ 0.19).
- **With ball feet** the poles stand ~0.2–0.3 mm off the plate. I assume 30–50 %
  of full force survives that gap (not measured), giving 130–210 N of preload.
- **Holding:** the shoe slips at ~24–39 N sideways. A ball unloads at ~30–50 N
  applied sideways at the dot. The in-weld loads are 1–3 N of wire push or drag
  (and a stuck wire yields at 3–5 N), so the margin is about 10×.
- **Lock shift from the contacts:** ball approach goes from 0.2 µm (3 N
  residual) to ~2.5–3.5 µm (locked). Contact stiffness ~26–30 N/µm per ball.
- **Stiffness at the dot:**
  - a 25 mm steel post 200 mm tall is ~1400 N/mm;
  - an aluminium tongue 15 × 25 × 70 mm is ~11,800 N/mm;
  - with an assumed 500 N/mm for the plate, shoe and shell-to-gun fit, the
    total is ~360 N/mm, so 2 N of wire push moves the dot ~6 µm.
  The printed shell's grip on the gun is the unknown that decides this.
- **Debris:** a 0.01 / 0.05 / 0.10 mm particle under one ball moves the dot
  ~0.02 / 0.11 / 0.22 mm. This is the lock's worst enemy.
- **Float pull while unlocked:** on a 1.2 m balancer line, sliding the shoe
  40 mm gives ~0.5 N of sideways pull, below the ~0.6 N static friction. The
  gun stays where it is slid.

### Breaking it

- **The switch itself twists the shoe.** The MagJig is turned by a knob. As the
  field comes on, the knob's reaction goes into the shoe body, while only ~0.6 N
  of friction holds it: the shoe can yaw before it grips.
  - **Repair:** switch it with a printed two-arm key, one arm on the knob and
    one braced on the shoe body, so the twist stays inside the shoe. Or a lever
    on a Bowden cable reacting on the shoe. Or an electro-permanent magnet
    (switched by a current pulse, no twist; not sourced).
  - **Leaves:** a hand on the key still pushes the shoe unless the key is
    thumb-and-finger. Measure: lock twenty times, watch the dot.
- **Debris and spatter.** The plate sits 53 mm above the rim, 60–80 mm from
  the puddle. Spatter lands on it, and a magnet attracts ferrous grit.
  - **Repair:** a spatter shield on the tongue, a wipe before every return, and
    the balls kept to three small contacts.
  - **Check:** the dot on the corner after every lock (eye, dial indicator on
    the shell, or the camera).
- **Plate flatness.** Hot-rolled A36 plate is not flat to hundredths.
  - Sliding the shoe changes tilt as the balls ride the plate's waviness. The
    first lock at a new place needs a look; returns to the same stops repeat
    the same waviness.
  - Two precision-ground O1 bars side by side make a better plane (1/4 × 2 ×
    12 in, Prime, thin stock).
- **Lift and return.** Magnet off, lift on the float 15–20 mm (the nozzle then
  clears the rim by 20–25 mm), change the tube, set the shoe down, push it into
  the stops, magnet on.
  - Return repeatability is that of a pin in a V plus a pin on a flat: with
    printed pins ~0.01–0.05 mm (estimate), better with hardened dowels.
  - The stops' own lock shift matters once, when they are set.
- **Stuck wire.** Locked, the shoe holds 24–39 N sideways, far above the
  3–5 N at which the stick-out bends, so the gun stays put for the snip. If
  something pulls harder, the shoe slips on the plate instead of bending the
  tongue or the post: a fuse, like the rim carriage's free spin.
- **Height and tube length.** Tube length varies (±3.2 mm published cut
  tolerance, per the digest). The plate's height screw is the per-tube Z, the
  same for both closures of one tube.
- **Heat on the magnet.** NdFeB inside the MagJig loses strength above
  ~80 °C. At 60–80 mm from the puddle, radiant heat over a 50 s bead is
  probably modest (not measured). Shield it.
- **Interlock.** The shoe is steel on steel through the post and frame. If the
  frame is bonded to the work lead, the gun's shell could become an electrical
  path to the work. The feet or the tongue need an insulating layer until
  Derek decides what the interlock should see.

### How it is used across a session

1. **Morning.** The plate and stops are where the last recipe left them. Hang
   the gun on the balancer and set the shoe against the stops. Switch on.
2. **Tube 1, first closure.** Set the plate height for this tube (height screw
   against a rim gauge or the camera). Dry revolution with the red dot.
   - If the dot is off: switch off, nudge (fingertips, or two push screws
     against the shoe), switch on, check.
   - Move the stops only when the change is meant to be kept.
3. **Weld.** Pedal, trigger by the presser in the shell, release, release.
4. **Stuck wire.** Snip; the gun has not moved.
5. **Tube change or second closure.** Switch off, lift, change, set down against
   the stops, switch on, one dry look.
6. **A second person** does step 5 without knowing anything about the pose.
7. **A new recipe** (new angle): change the pose block, teach X and plan angle
   by sliding, reset the stops, record their position (scribed marks, a photo,
   or scales printed on the plate).

**What it lacks:** numbers. Teach-by-hand stations remember positions, not
values; scales on the plate, AS5600 or camera readings, or pose gauges have to
add the values.

## Branch E-dome: rotations about the dot by skating on a sphere

A shoe on three balls, riding a spherical surface centred on the dot, can move
over that surface in three freedoms, and every one of them is a rotation about
the sphere's centre. If the centre is the dot, the hand turns the gun about the
dot in roll, hole tilt and plan angle while the dot stays put, and one switch
locks all three.

- **Where:** at the opening pose, the direction from the dot to the housing
  centre points up, inward and toward −Y. A patch of a sphere of R ≈ 250 mm
  there lies above the housing and short of the grip butt. It is ~130 × 130 mm
  for ±15° in two directions. The shoe sits on the housing top and presses up
  against the patch's underside.
- **Lock:** a large steel spherical patch is not a Prime item (only small
  stainless hemispheres and foam ones were found), and 304 stainless is not
  magnetic. So:
  - print the patch in PET-GF, seal it smooth, and lock by **vacuum**: a
    50–60 mm suction pad in the shoe, with its lip pre-compressed so the three
    balls touch first. The sag of a 60 mm chord at R 250 is 1.8 mm, within a
    rubber lip's range;
  - or bond thin steel to the print and accept a weaker magnet.
- **Accuracy:** an error in the patch's radius or shape moves the dot by about
  the same amount. A printed patch at ±0.1–0.2 mm means each aim change is
  followed by a small X/Y re-slide on the flat skate. The dome is then a fast,
  lockable, one-hand aim, and the flat skate cleans up the dot.
- **Calibration:** as in machine-that-learns' B. Rotate with the dot on the
  flat cap and fit the arc; shim the shoe until the dot stops wandering.
- **Carry state matters more here:** with the gun hanging under the patch, the
  float must carry slightly more than 100 % so the shoe stays against the patch
  while unlocked, or a weak always-on magnet provides a glide preload.
- **Unresolved:** what the umbilical does when the gun is rolled under the
  patch; the patch's support stiffness.

## Other supports that switch state (capabilities checked where they matter)

| Support | Unlocked | Locked | Lock-shift class | Real capability found | Where it fits |
|---|---|---|---|---|---|
| Switchable-magnet shoe on steel (this file) | slides on 3 balls | friction + contact | preload-increasing | MagJig 95: 43 kg normal, 4 kg working shear at 2:1, 0.1 kg, $46 Prime **[spec page]** | the main arrangement |
| Vacuum pad on smooth surface | glides | atmospheric preload | preload-increasing if balls touch first | hand-pump glass lifters (8–10 in, Prime) too big; small pads + pump needed (not sourced) | E-dome on a printed sphere |
| Central-lock articulated arm (machinist, gauging) | all joints free | one knob locks all | gap-closing at 3+ joints in series | Noga MG61003: 317 mm total arm, 800 N magnet, $144.77 Prime, 50+/month **[Noga, Amazon]**; HHIP 4401-0528 "most rigid", 20 in reach, $141.99 Prime; FISSO Strato µ-Line 130–330 mm arms hold **30–56 N** at the tip **[distributor]**. No stiffness published. | locator only, with a float carrying the gun: 30–56 N exceeds the in-weld loads, but lock shift is untested (sequence-of-use expects tenths). Lock a fine stage last, or learn the bias (A-r4c) |
| Split clamps on steel rods (machine-that-learns A-r4c) | float places | clamp at node | gap-closing | Ø16 rod cantilever ~240 N/mm at 200 mm (their calc) | the suspension's lock |
| Granular jamming cradle | beads flow round the shell | vacuum jams them | phase change: the bed compacts 1–3 % (estimate), so 0.3–1 mm at 30 mm depth | yield ~30–50 kPa at 80 kPa vacuum (estimate: μ × p) | "teach any pose" seat. Needs a thin bed (few mm) or learned shift; creeps under steady load |
| Electromagnetic power-off brakes on printed joints (teach arm) | back-drivable arm | spring-applied brake | gap-closing (brake spline/backlash) | not found as a Prime commodity in a useful size in this pass | teach-by-hand arm; float again does the carrying |
| Low-melt alloy cup (pin in Field's-metal-type alloy, heater) | melt: pin free | solid | phase change (small volume change) | not sourced; used industrially for holding odd parts | a "cast" lock; slow to switch |
| Lockable gooseneck (Loc-Line, snake arms) | bends | friction | — | far too soft for the gun | camera or light holder only |

## Contribution

- A way to hold the gun that is set by hand in seconds, switches from free to
  locked with a few micrometres of shift, holds ~10× the in-weld loads, and lets
  go when something pulls far harder.
- Plan angle comes free: the plate's Y slide is the vertical-axis turn, by the
  joint's symmetry.
- Memory lives in magnetic stops a second person can use without knowing the
  numbers.
- The float makes it work: nothing changes hands at the switch.

## Open problems

- The switch's own twist.
- Debris under the feet.
- Plate flatness.
- The magnet's real force across the ball stand-off.
- Hole and roll need a pose block or E-dome.
- The printed shell's grip on the gun sets the real stiffness.
- All untested; each is a measurement (lock 20 times, watch the dot).


## Wave 5: work-as-datum's critique, and the branches it produced

Source: `../../../exchange/work-as-datum--on--carry-and-locate-w4.md`.

### The critique, which I accept for the original E

The shoe sits 61 mm from the dot horizontally and 53 mm above it, so the room
plate is the dot's reference, and every error of the plate or shoe reaches the
dot amplified:

- debris 0.1 mm → 0.22 mm;
- switch twist 1.06 mm per degree of shoe yaw;
- tube length ±3.2 mm → up to 3.2 mm on the wall, until the height screw is
  reset;
- runout and face runout pass straight through the lap;
- every reseat or inversion gives a new offset.

The stops remember a pose **in the room**, while what changes per tube is **in
the work**. So "a second person, knowing nothing" is true only within one
tube, for example between its two closures, where the length is the same. For
a new tube, the per-tube height step needs knowing.

One point of accuracy, not a disagreement: the original file already made the
per-tube height a step (session step 2). The critique is right that this is
exactly the skilled step the stops were meant to remove.

### Their repair R-A — the work holds the dot, the skate holds the tail (kept as the lead form)

- **Cup.** Three hardened 8 mm balls ring the barrel ~41 mm from the dot on a
  57 mm circle. They sit in a concave spherical band (R 50 mm) centred on the
  dot, carried by work-as-datum's plate hanger. Every contact normal passes
  through the dot: the dot's translations are held by the work, and all
  rotations stay free.
- **Tail.** A ball on the shell at the grip base drops into a round vertical
  bore in my MagJig shoe, which skates on its plate on a post from the rotator
  frame. X and Y slide set hole tilt and plan angle, 0.21° per mm, with the dot
  fixed. The ball's height is free in the bore.

Their table of what each weak point becomes is right:
- debris under the shoe gives ~0.01° about the dot, not a dot move;
- shoe yaw moves nothing, because the bore is round;
- tube length changes the angles by 0.66° at full tolerance instead of moving
  the dot;
- the stops now hold angles, which forgive (0.05 mm = 0.01°).

**By my own rule from nose-and-tail it is also determinate.** Cup 3 + bore 2 +
roll 1 = 6. The shoe's lock is over-constrained only on the shoe itself (its
yaw), which the round bore hides from the gun. So the dot can follow runout
while the tail is locked: the ball slides up and down in the bore. This is
exactly "lock at the non-referenced point only what the referenced point
doesn't set".

**Two additions of mine (branch E-RA+).**

1. **Roll on the same shoe.** R-A leaves roll to a stop, a block or the hand. A
   second shell ball, 40 mm off the grip axis, resting on a screw pad on the
   same shoe, makes roll a screw (~1.4° per mm) held by the same switch. The
   float's bias presses the ball onto the pad. A hand on the trigger could lift
   it, which is one more reason for the in-shell presser.
2. **Seat the cup with a spring, not with weight.** R-A leaves 7–10 N of weight
   on the cup as its preload: capacity 0.70 × preload, so 5–7 N against a
   3–5 N stuck-wire drag. That is the same "locating borrowed from carried
   weight" I found in their D1 (wave-4 exchange).
   - **Repair:** a spring clip or small magnet pulling the ball ring into the
     band, internal to the cup, 20–30 N.
   - The balancer can then take all the weight. The tube carries only
     disturbances, and seating no longer depends on pose.
   - **Cost:** rotation friction μ·F·r ≈ 0.2 × 25 N × 50 mm ≈ 0.25 N·m about
     the dot. That is ~0.9 N at the tail shoe, well under the shoe's sliding
     feel once unlocked, and irrelevant once locked.

**Still uncertain (theirs and mine):**
- the cup's spherical centre on the dot to ~0.1 mm (the same calibration as
  E-dome, but on a 50 mm band instead of a 250 mm patch);
- heat on the cup pads 13–43 mm above the rim;
- nipples in the ports while welding;
- clutter of cup, wire guide and camera;
- the bore's clearance, which sets the angle play (0.02 mm ≈ 0.004°).

### R-B and R-C (lighter branches, recorded)

- **R-B:** the skate's plate rides the plate hanger instead of a room post.
  Tube length, runout and reseat drop out, but debris and switch twist still
  reach the dot at 2.2× and 1.06 mm/°. Kept as a record; E-RA supersedes it
  for accuracy.
- **R-C:** keep E, and set height by a dial touching the plate face instead of
  a rim gauge. It removes the skill step and the rim's waviness from Z; runout
  and reseating still pass through. This is the quickest improvement to the
  original if E is built first as a teach-by-hand test.

### How R-A relates to nose-and-tail (F)

Same division of work — the work holds the dot, a table beside the rotator
holds the angles, a float carries — reached from two directions in the same
wave.

| | F (nose-and-tail) | E-RA |
|---|---|---|
| Pivot | 46 mm from the dot | at the dot |
| Angles | table screws (numbers, slow) | hand slide plus switch (fast, taught) |
| Nose element | small V-loop collar | larger, hotter cup band |
| After an angle change | dot re-centred at the stalk | nothing |

- A merged form is natural: E-RA's cup at the nose, F's two-screw table (or
  E-RA+'s pad shoe) at the tail.
- The choice between screws and a switch is between numbers you can dial and a
  pose you can teach.
