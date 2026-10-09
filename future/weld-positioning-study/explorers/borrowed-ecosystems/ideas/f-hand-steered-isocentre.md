# F — Hand-steered isocentre: balanced, damped, lockable joints about the dot

## Picture it

**The work side.** Translations only: an X micrometer, Y read as the yaw knob,
Z set per tube.

**The gun side.** On +X at the dot's height, a preloaded bearing pair on the
radial line through the dot carries a spoke. The spoke runs back along −Y to a
roll stub on the grip axis behind the butt (who-moves-what's stub), which
carries the shell and gun. The wire guide rides the roll body.

**What each joint gets.**
- Weightless at every angle: a zero-length spring or counterweight cancels
  gravity's exact sine.
- Damped by a grease film.
- Locked by a bicycle disc brake.
- Read by an encoder.

**How it is used.** Derek steers the angles by hand on tillers well away from
the dot, and the camera shows the dot staying on the corner. "Fixed" is a common
plate under the work translations and the gun-side column.

It is a **combination beyond Derek's examples**, crediting one-knob-one-parameter,
who-moves-what, sequence-of-use and machine-that-learns.

**Sketch:** `../sketches/f-hand-steered-isocentre.svg` (true pose).

**Major unresolved problems.**
- Gun mass and CG, which size the balancers.
- The umbilical trim.
- The grease's viscosity.
- Lock shift.
- The stub's clearance from the fibre.
- Whether steering during a weld teaches anything.

Sketch: `../sketches/f-hand-steered-isocentre.svg`. Numbers:
`../calcs_wave4.py` §6–9. Corrected opening pose (grip 45, hole dial 30,
vertical −15). A combination across explorers; the source ideas stay as they are.

## Where it comes from (credits)

- **one-knob-one-parameter, `isocentric-couch-and-gantry.md`.** The dot as an
  isocentre: every gun-side rotation axis passes through it, translations sit
  nearer ground, the work carries X and Y (Y is really the vertical-axis angle),
  and the walk test measures what is left.
- **who-moves-what, `protractor-and-stub.md`.**
  - As the hole angle sweeps, the grip base travels on a 279 mm circle about the
    dot.
  - Roll can sit on a **stub shaft on the grip axis** ~65 mm past the butt. The
    fibre, leaving along the grip's rake, is ~29 mm off-axis there, so a bearing
    goes around a shaft and never around the cable.
  - Yaw is a Y slide.
- **sequence-of-use, `monitor-arm-session.md`.** The **hand state**: the gun
  weightless in Derek's hand for tacks and exploration, with positive stops for
  every rest state.
- **machine-that-learns, `observation-layer.md`.** A dot camera ~69° off the beam
  on the free +Y side reads dot versus corner and standoff. If the idle red beam
  sweeps with the wobble, it shows the wall/cap split directly.
- **Mine.** The counterbalance and drag of video fluid heads and Anglepoise lamps,
  and the telescope equatorial mount's clutch and slow-motion practice. The
  mass-market parts: a bicycle disc brake as the lock, camera helical grease as
  the drag, a hobby servo or Bowden for the trigger.

## The idea in one paragraph

The isocentric stations make every angle a *knob*: a worm, a micrometer, a gauge
stack. That is right for returning to a recipe and slow for finding one; Derek
finds things with his hands and eyes. The hand state is the opposite: fast and
intuitive, but the dot goes wherever the hand goes. Joining them:

- Keep the joints whose axes pass through the dot, so **no hand motion on them
  can move the dot**.
- Make each joint **weightless** (gravity torque cancelled at every angle),
  **damped** (viscous drag filters tremor), **lockable** (a brake) and **read**
  (encoder plus camera).
- Steer them by hand on a tiller away from the dot.

The hand then explores angles directly while the camera shows the dot staying on
the corner and, if the beam sweeps, the wall/cap split changing. Lock, read,
record. It is a telescope mount pointed at the dot.

## The physical arrangement

- **Work side**, from the isocentric/still-gun families: X micrometer (radial dot
  place), Y read as the yaw knob (0.93°/mm), Z set per tube by the camera. The
  rotator unchanged, on a common plate with the gun side.
- **Hole joint.**
  - A preloaded deep-groove bearing pair on the X line through the dot, ~40 mm
    outboard of the OD (where the partner's table sits), on a Z carriage. A spoke
    runs back along −Y at the grip axis' elevation to the roll stub.
  - **Balance.** Gravity about this axis follows an exact sine: at 1.5 kg the CG
    sits 195 mm from the axis, and the torque is m g r sin α with α = 75° − dial
    (2.49 N·m at dial 15, 1.44 at dial 45). Either of two classic balancers cancels
    it at *every* angle:
    - a **zero-length spring** (a spring behind a pulley; Anglepoise and video
      fluid heads) from an anchor b above the pivot to a point a along the CG
      line, with k·a·b = m·g·r. That is k ≈ 0.29 N/mm at a = b = 100 mm, or
      0.13 N/mm at 150 mm, and the anchor height b is the trim knob;
    - a **counterweight** on the +Y side, diametrically opposite the CG about the
      axis (telescope mounts): exact at all angles with no spring, at the cost of
      doubling inertia and bearing load.
  - **Drag.** A camera helical-grease film between a printed hub and housing:
    c ≈ 1 N·m·s/rad with a 30 mm radius, 20 mm length and 0.2 mm gap if the
    grease is ~60 Pa·s (unmeasured).
  - **Lock.** A 160 mm bicycle disc rotor on the hinge with a cable caliper;
    17–34 N·m of holding against 1–3.3 N·m needed. Use a **dual-piston** caliper:
    a single-piston caliper pushes the rotor sideways and tilts the hinge (below).
  - **Read.** An AS5600 on the hinge (0.09°, or 0.02° with a 1:5 belt), the camera
    as the truth.
- **Roll joint.** who-moves-what's stub. A rigid arm leaves the butt on the side
  away from the fibre and carries a short shaft *on* the grip axis ~65 mm past the
  butt, in a bearing pair on the spoke's end. Gravity about the grip axis also
  follows a sine (0.90 sin(roll) N·m at 1.5 kg), so it gets its own small
  zero-length spring or counterweight, drag, a small disc lock and a roll tiller.
  (If the scan shows the fibre too close to the axis, fall back to my hinged rings
  around a sleeve.)
- **Tiller.** A handle on the spoke 250+ mm from the dot, up and back, carrying
  the brake lever (Bowden to the caliper) and the trigger lever (Bowden to the
  shell's presser, reacting inside the shell). The hand never touches the gun,
  and its force goes into the spoke far from the nozzle.
- **Wire.** On the roll body (the partner's main mount), so it turns with the gun
  as Derek's scene draws it.
- **Umbilical.** Clamped to the roll stub's body. The saddle sits at the cable's
  natural apex behind (~420–450 mm above the bench, not 680).
- **Camera and readout.** machine-that-learns' dot camera on +Y. A small display
  shows hole, roll and the dot's offset from the corner.

## How it is used

1. **Explore (red beam only).**
   - Release both brakes. The gun floats in hole and roll, with drag.
   - Steer on the tillers and watch the display: the dot stays on the corner (the
     walk test is always running), and the split changes.
   - Stop, squeeze the brake levers, and record the encoder angles and a camera
     frame.
   - This replaces a sweep of knob settings with a minute of steering.
2. **Freeze.** Lock both brakes; optionally fit a gauge-stack stop or a
   recipe-cartridge seat at the found angles for exact return. That is
   one-knob-one-parameter's "knobs find, blocks freeze", with the hand as the
   knob.
3. **Weld (recipe).** Brakes locked; pedal; trigger lever. Nothing moves but the
   tube and the wobble.
4. **Weld while steering (a new learning mode).** Brakes off and drag on; Derek
   steers roll slowly during a bead while the encoders log angle against time and
   table degrees. Position is removed as a variable mechanically; only the angle
   trajectory, which is recorded, is his. It is the controlled half-way house
   between hand welding and a fixed recipe.
5. **Lift-off / stuck wire / tube change.** A Z-carriage lift (a motion to a stop),
   the Y drawer on a kinematic end, the tube out along +Y (the partner's sequence).
6. **Second person.** The recipe is two angles, three work-side readings and a
   camera reference image. They steer to the numbers with the display, lock, and
   compare.

## Breaking it

1. **Balance is exact for one mass and CG.**
   - A 10% mass error leaves 0.10–0.22 N·m about the hole axis, and roll moves
     the CG so the hole torque changes ±10% over roll 0–75°.
   - *Repair:* the anchor-height trim (or sliding counterweight) set per session
     with the umbilical attached, plus light Coulomb friction (~0.1–0.2 N·m).
   - Drag alone cannot hold a residual: 0.2 N·m would drift ~10°/s at
     1 N·m·s/rad. The fluid-head recipe is balance, then drag, then friction.
2. **Hand force leaking into the dot.**
   - A 10 N push on the tiller of a 4040 spoke moves the nozzle ~0.006 mm (it sits
     near the spoke's root, one-knob-one-parameter's `stiffness.py` result). The bearing
     pair's radial compliance adds microns.
   - The tiller must be on the spoke, not the gun: the shell's grip on the gun is
     the unknown compliance.
3. **Tremor.** With I ≈ 0.07 kg·m² about the hole axis and 1 N·m·s/rad of drag,
   the corner is ~2 Hz: 10 Hz tremor is cut ~5×, and steering at 10°/s needs
   0.7 N at a 250 mm tiller. At 2 N·m·s/rad it is 1.4 N and a 2× cut. Tune by
   grease grade (the #10–#3000 range exists).
4. **Lock-induced shift.** A single-piston cable caliper pushes the rotor against
   the fixed pad. The ~300 N axial load at 70 mm makes ~21 N·m on the bearing pair,
   of order 0.5 mrad of tilt for an assumed 4 × 10⁴ N·m/rad pair: ~0.03 mm at
   the dot. *Repair:* a dual-piston caliper (opposed pads, no net axial force),
   and include "lock/unlock ×5" in the walk test.
5. **Steering while welding breaks one-knob purity by design.** The encoders make
   it an *observed* variable instead of an uncontrolled one. Whether it is useful
   depends on whether roll changes mid-bead produce readable effects; it is an
   experiment, not a recipe.
6. **Spring failure or a dropped counterweight** lets the gun swing about the dot.
   *Repair:* hard stops on both joints (hole dial ~15–60, roll ~10–70), so the
   nozzle swings about the dot and cannot reach the lip.
7. **Near-rim hardware.** The hinge, rotor and drag housing sit at the dot's height
   just outboard of the OD. The rotor's lower edge (~80 mm below the dot) must
   clear the ground shoe and motor tower at their azimuths; a 140 mm rotor gives
   more room.
8. **Umbilical.** Roll swings the fibre ~29 mm around the stub axis and twists it
   by the roll angle over its free span. With the saddle at the natural apex, the
   residual cable torque becomes part of the trim.

## What it contributes, and what it connects

- The rotations-about-the-dot family gains a **way to explore** that needs no
  knob-turning, while keeping the dot mechanically fixed. The hand-state family
  gains a **held dot**. The digest's unexplored directions — "the hand kept as
  the actuator with a guide making it repeatable" and "teach by hand then lock
  or replay" — become one mechanism.
- The same joints motorise later (a belt and stepper on each hinge, the brake as
  a holding brake), so F is also the manual form of Derek's AI dry-run station:
  the hand teaches, the encoders record, and motors replay.

## Parts (see `../../../sourcing/borrowed-ecosystems.md`, wave 4)

- Farbetter cable disc-brake kit (two calipers and two 160 mm rotors, $25.99, 627
  ratings); a dual-piston cable caliper from the same Prime search.
- Japan Hobby Tool helical grease (#10–#3000 grades, $29.99, 177 ratings).
- AS5600 encoders and MG996R servo (if the trigger is servo-driven).
- 6000-series bearings, extension springs, 4040 spoke.
- Printed hubs, pulleys, tillers and stops.

## Unresolved

- Gun mass and CG (sets springs or counterweights), umbilical EI and tension (sets
  the trim).
- The grease's real viscosity.
- Whether steering during a weld teaches anything.
- Whether the stub's fibre clearance holds for the real gun (scan).
