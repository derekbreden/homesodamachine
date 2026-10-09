# Split-mount station: the plate places the dot, the collar tilts the gun about it

## Picture it

- **Structure:** the table opening with its collar, and the rotator on the
  four-post shelf below (shelf Z only for LOAD/WELD).
- **Three bodies above the mouth:**
  - A **hub** rides the plate's centre. A spherical bearing sits on a pin on
    work-as-datum's port seat, and RC62 magnets hold it down on a 430 disc.
  - A **paddle** runs from the hub, ~250 mm along −Y under the grip, to a ball
    foot (P3). The foot stands on a motorised lift in the collar, beside a
    fence.
  - A **carrier** sits on X/Y micro-slides on the paddle. It holds two
    stainless rollers on the plate face on a line through the dot (30° off the
    radius, away from the gun), the roll yoke, and the gun in its shell.
- **What the plate locates:** the dot's x, y (pin) and height (rollers).
- **What the collar locates:** the rotation about the roller line (P3 lift).
  The dot sits on that line, so that tilt leaves it in place. The collar also
  holds azimuth (fence).
- **What carries:** weight, trigger and cable loads land mostly on P3 and the
  collar.
- **Gun and wire:** the gun stays tangent. The wire comes from its bracket
  along the tangent.
- **"Fixed" is fixed to:** the plate for position, and the collar for the
  tilt.

**Sketch:** `../sketches/split-mount-station.svg`.

**Major unresolved problems:**

- Clearance through the tilt range needs the gun scan.
- The tilt axis is a 30° mix of hole-axis tilt and lean. Is that acceptable?
- The plan-angle trim is only −4.6° … +2.3° around a built-in nominal.
- Spatter under a roller.
- Nipples in the ports at weld time.
- Magnet pull on 430 through PTFE.


Wave 4 combination. Sketch: `../sketches/split-mount-station.svg`
(`../sketches/make_wave2_sketches.py`). Numbers: `../split_mount.py`,
`../axis_clearance.py`.

## Where it comes from (credited; the sources stay as they are)

- **work-as-datum, endcap compass** (`../../work-as-datum/ideas/endcap-compass.md`):
  - the port seat (two 316 hex nipples in the plate's tapped ports, a seat bar,
    a centre pin at the port-pair midpoint);
  - the insight that turning about the plate's own axis is the one freedom
    that doesn't matter;
  - the calibration puck;
  - from their exchange on my ideas: the lid that rides the plate and parks on
    the collar (L1), and the collar centre (W1).
- **machine-that-learns, E, the motorised table station**
  (`../../machine-that-learns/ideas/e-table-opening-station.md`):
  - Derek's five motors and the order to motorise them (Z first, as LOAD/WELD);
  - the observation layer: joint camera on the +Y side, collar fiducials, dry
    runs where software turns the table only with the laser disabled and never
    fires it.
- **carry-and-locate:** the open C-ring on three V-rollers for the grip-axis
  roll, which lets the cable drop in sideways.
- **one-knob-one-parameter:** the rule that knobs keeping the puddle's relation
  to gravity go under the work and tilts stay on the gun. Here the tube stays
  vertical and only the gun tilts.
- **Mine:**
  - the table opening, collar and countertop sled (3-2-1 on a room plane, with
    actuators at the contacts);
  - the wave-2 paddle, two work contacts plus one room contact, which this
    corrects;
  - the cart dock for a fixed cable shape.

## The idea

A 3-2-1 kinematic mount has six contacts. The sled puts all six on the room;
the compass puts five on the work. Here each contact goes to the side that
should own the freedom it controls:

| Contact | Controls | Owner | Why |
|---|---|---|---|
| Centre pin (hub, on the plate's port seat) | dot x, y | work | the corner moves with runout and reseating |
| Rollers P1, P2 on the plate face, **on a line through the dot** | dot height, and tilt across that line | work | tube length, seat depth and face tilt move the corner |
| Foot P3 on the collar, far out under the grip | rotation about the P1–P2 line | room | this rotation doesn't move the dot, because the dot is on the line |
| Fence at P3 | azimuth about the tube axis | room | only moves the dot along the seam |

**What the split does:** P3 is on the room side and it controls a pure rotation
about an axis through the dot. So **P3 is the tilt actuator.** A lead screw
under the collar lifting P3's pad turns the gun about a line through the dot,
exactly. The remote centre comes from where two contacts sit on the work. No
arc, no linkage, nothing big near the countertop.

**What it changes in the two families it joins:**

- **Riding the work:** normally only follows position. Here its contact line
  also defines the tilt axis.
- **Rotations about the dot:** normally needs a remote-centre mechanism. Here
  it becomes one linear actuator in the workspace.

## The station

**Structure (unchanged from my table branch):**

- a collar plate flush with the rim in a bench opening, or on its own legs;
- the rotator on the four-post shelf below;
- shelf Z on four belt-linked Tr8×2 screws with a NEMA 17 (E's first motor):
  LOAD/WELD only, bringing the plate into the paddle's range.

**Three bodies ride the plate:**

- **Hub part.**
  - A GE8 spherical bearing takes the centre pin: x, y located; tilt and axial
    motion free.
  - Hold-down: two of Derek's K&J RC62 N42 rings, listed at 38 N each on thick
    steel at contact. They bear through a PTFE washer on a 430 (magnetic)
    stainless disc on the seat bar. That is contact, not a gap, so the force
    doesn't depend on the seat's thread height. The 430 disc gives less than
    thick mild steel, so allow ~20–40 N total.
  - It clamps the paddle to the plate internally: the magnet pulls the seat up,
    the rollers press the plate down, and there is no net force on the loose
    tube.
- **Paddle.** Rigid from the hub to the P3 foot (a ball foot on a hardened pad)
  and fence contact, ~250 mm along −Y under the grip. It carries the X/Y
  micro-slides.
- **Carrier.** It sits on the slides and holds:
  - the two rollers P1, P2 (stainless 695 bearings, axles radial, rolling
    tangentially on the turning plate);
  - the roll yoke with the open C-ring near the grip butt;
  - the gun in its shell and pose block.

**Why the rollers ride on the carrier:** they move with the gun. The dot then
stays on the roller line at any X/Y slide setting, and the tilt stays exact.
With a gun-only Y slide, a 5° plan-angle trim leaves the dot 5.4 mm off the
line, and a 10° tilt then moves it 1.0 mm in height; at 15°, 2.9 mm
(`split_mount.py` §2).

**Motors (Derek's five, plus LOAD):**

| Motor | Where | What |
|---|---|---|
| P3 lift (NEMA 17 + T8 under the collar) | room | rotation about the line through the dot: 4.9 mm per degree; ±10° is ±50 mm; 0.6 µm per microstep |
| Roll (yoke on the carrier, C-ring) | carrier | grip-axis roll, the wall/cap split |
| X micro-slide | paddle → carrier | dot across the seam (−2 … +6 mm range) |
| Y micro-slide | paddle → carrier | plan-angle trim, 0.93° per mm (−4.6° … +2.3° around the nominal) |
| Shelf Z | room | LOAD/WELD; the dot's height needs nothing from it |

**Feedback:**

- **Inclinometer on the shell** (WitMotion-class, listed at 0.05° XY): reads
  both rotations against gravity, which is square to the tube (vertical within
  its runout acceptance).
- **Slide positions:** step counts, with an index switch on each.
- **Joint camera:** where E puts it, on +Y, verifying dot vs corner.

## Geometry at the true opening pose (`split_mount.py`, `axis_clearance.py`)

**Why not the radius.** A line through the dot along the radius is the obvious
choice, and it doesn't fit. A roller holder at (36, 0) comes within 4.3 mm of
the nozzle at the opening pose and collides at vertical −30°. On the other side
the nipples turn with the plate, and their hex sweeps r ≤ 27. My wave-2 paddle
put its rollers there; that was checked as a point, not a holder, and was
wrong.

**The line used.** Tilt the line 30° off the radius toward +Y, away from the
gun:

- P1 = dot + 34 mm → (32.4, 17.0), r 36.6;
- P2 = dot + 90 mm → (−16.1, 45.0), r 47.8.

The P1 holder (r 7, 25 mm tall) then clears every gun surface by 15–22 mm over
six poses (grip 30–60, hole dial 20–40, vertical −30…0).

**Dot height** = 1.61 × P1 − 0.61 × P2.

**The tilt axis is that line**, so P3's rotation is a known mix of hole-axis
tilt (cos 30°) and lean across the tangent (sin 30°). With the grip-axis roll,
the two motors still span Derek's two rolls. The inclinometer reports the
resulting attitude directly.

**Slide ranges while both rollers stay on clean plate** (outside the nipples'
sweep, inside the fillet toe):

- Y −5.0 … +2.5 mm;
- X −2 … +6 mm.

The nominal plan angle, e.g. −15°, is built into the carrier's pose block; the
slide trims around it.

**P3:** 282 mm from the tilt line.

**Loads** (`split_mount.py` §3; paddle + carrier + motors 32–35 N [assumed],
three CoM guesses):

- Without hold-down, P2 can go to −6 N; the mount lifts a roller.
- With 30 N of hold-down: P1 19–37 N, P2 7–18 N, P3 21–25 N, all positive.
- The plate sees ~20–25 N net (the hold-down is internal), which also seats
  the loose tube.

**Tilt range vs the table:** at −10° the grip end drops ~40–50 mm. The grip
base stays ~85–90 mm above the collar, the housing ~45 mm.

## How it is used

**Recipe setup (once):**

1. Choose the carrier pose block (nominal roll, hole and plan angles).
2. The P3 lift and roll motor bring the inclinometer to the recipe attitude.
3. X finds the corner with the dot (camera).
4. Y trims the plan angle.
5. Record six numbers.

**Each tube:**

1. **LOAD.** The shelf drops. The plate leaves the rollers and pin, and the
   paddle parks on lugs over the collar (work-as-datum's L1 park). Slide the
   old tube out of the open face; its seat bar and nipples come off it.
2. Put the nipples and seat in the new plate after tacking. Slide it in.
3. **WELD.** The shelf rises. The pin enters the hub's chamfered bore
   (±0.5 mm lead-in covers runout and park play). The rollers land and the
   magnets seat. The shelf stops a few mm higher, where the paddle has lifted
   off its park lugs.
   - The dot's position no longer depends on the shelf, on the tube length or
     on runout; the gun rides the plate.
   - The P3 lift re-servos to the recipe attitude on the inclinometer, because
     tube length changes the plate height relative to P3.

**Dry runs and AI sweeps:**

- tilt, roll, X and Y each change one variable around a fixed dot;
- the camera measures;
- software turns the table only with the laser disabled (E's rule);
- the calibration puck in a second collar opening allows sweeps with no tube.

**Weld:** pedal as the deadman, Bowden or servo trigger inside the shell.
Nothing moves except the tube.

**Stuck wire:** the drag along +Y goes into the Y micro-slide and the fence.

- The Y slide's nut couples through a 20–30 N ball detent with a switch (the
  repair from my exchange on E).
- The paddle stays seated: the drag acts almost on the roller line (at the
  dot, a few millimetres above the plate), so it makes little moment about it
  against 20–40 N of hold-down and weight.

**Second closure:** invert, seat on the new plate, WELD. The same recipe
numbers apply.

**Second person:** LOAD, nipples, WELD; the screen says when the attitude and
dot are in tolerance.

## Breaking it

1. **Spatter or a burr under a roller.** A 0.1 mm bead under P1 is 0.16 mm at
   the dot, as a once-per-revolution spike.
   *Repair:* a small stainless brush wiper ahead of each roller (the plate turns
   under them). The dry lap's camera trace shows any spike before the weld.
   Rollers run 15–25 mm inboard of the fillet on the plate face, which the
   procedure keeps clean.
2. **Hold-down by magnets on the work.** A 430 disc on the seat bar next to a
   316L weld: no free iron touches the plate, because the disc sits on the
   nipples. RC62s are rated to 80 °C, and the hub is ~40 mm above the plate
   centre, where the mean vessel rise is 6–22 K (work-as-datum's estimate).
   *Alternative:* a spring and nut on the pin (manual, one extra step).
3. **The plan-angle range is small (≈ 7°).** Larger plan-angle changes are
   carrier changes: a second pose block, or a second roller-bracket position
   on the carrier. E's gantry Y had tens of degrees; this station trades range
   for exactness.
4. **Motors ride the work.** Three small motors and their cables (X, Y, roll)
   are on the paddle and carrier. Their cable forces and the umbilical's go
   mostly into P3 and the fence (room), not the rollers.
   - The umbilical's first hard clamp is on the collar well behind the grip,
     with a loose ring near the butt (my exchange on E, §3).
   - With the cart dock the cable shape repeats every session.
5. **Inclinometer vs the 80 Hz wobble motor.** Angles are set at setup with
   the wobble off and filtered. During the weld nothing is commanded. The
   inclinometer reads the gun's attitude, which is what matters. Its 0.05°
   listing is the seller's; E0-style measurement with the camera checks it.
6. **The pin's pick-up.** If the hub bore catches instead of centring, the
   paddle lifts on one side as the shelf rises.
   *Repair:*
   - a 45° chamfer with 2 mm lead-in;
   - the shelf's WELD move slows for its last 5 mm;
   - a Hall sensor in the hub confirms the magnets have seated before the
     recipe runs.
7. **Tilt range vs clearances.** Checked only at the proxy's poses. A ±10°
   sweep about the 30° line moves the nozzle a little (it is near the line),
   and the grip end ±40–50 mm. The real scan must confirm the nose against P1
   and the grip against the collar.
8. **Nipples in the ports during the weld** (Derek's call), and the plate held
   before tacking (the seat goes on after tacks). Both come from the compass.

## Contribution

- A remote centre for one rotation made from contact placement, with the motor
  in the workspace. E's open problem (the head at countertop height) shrinks to
  the roll yoke alone.
- Position is passive and work-referenced: tube length, runout, reseating and
  inversion don't reach the dot. The motors spend their range on the
  experiments (angles, wall/cap offset, plan-angle trim), not on chasing the
  work.
- Joins the 3-2-1 family (sled, paddle, compass) into one rule: put each
  contact on the side that should own its freedom, and put the motors at the
  room contacts where you can.

## Unresolved / rests on

- **The gun scan:** nose and P1, grip and collar through the tilt range.
- **Gun CoM and umbilical force:** set the hold-down, P3's position and the
  P2 margin.
- **Whether a 30°-mixed tilt axis suits Derek's experiments,** vs a pure
  hole-axis tilt that would need rollers on the radius (which doesn't fit this
  gun at this pose).
- **Magnet pull on a 430 disc through PTFE:** measure; K&J's 38 N is for thick
  mild steel at contact.
- **Spatter frequency on the plate face with wire feed:** unknown.
