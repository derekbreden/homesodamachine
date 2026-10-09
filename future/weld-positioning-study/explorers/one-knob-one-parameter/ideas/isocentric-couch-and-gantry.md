# Isocentric couch and gantry

**Picture it (current state, after waves 2–3).**
- **Common baseplate.** One plate carries two things: the work side and a Z
  column that stands outside the rotator's footprint.
- **Work side.** The existing rotator is unchanged. It sits on three slides:
  - a radial X micrometer slide, which places the dot on the corner;
  - a Y slide along the tangent, which is the **yaw knob** (1.08 mm per degree,
    with the X correction) and also the loading drawer, returning to a
    kinematic stop;
  - Z, carried at the column.
- **Gun side.** The Z column's bracket holds a 4-inch rotary table standing on
  its side just outboard of the tube. Its axis is the radial line through the
  dot, so turning it changes the **hole angle** and nothing else. A 300 mm arm
  runs from the table's face back along the grip axis to two hinged clamshell
  rings. They clamp a printed sleeve on the shell's butt; the sleeve turns in
  them for **roll**, set by a gravity-loaded micrometer lever. A rail on the
  roll body, parallel to the barrel, sets **standoff**. The gun lies in its
  full-length shell with the nozzle ~5 mm above the rim.
- **Wire.** The wire guide sits on the roll body on its own XYZ micrometer
  stage.
- **Cables.** The umbilical and wire conduit leave behind the butt to a
  balancer.
- **What carries and what locates.** The gun's weight goes down through the
  roll rings, arm, table and column. Every rotation axis passes through the dot,
  so angle knobs cannot move it; translations sit nearer ground. "Fixed" is the
  baseplate.
- **Readings.** A dot camera on the rotator base reads where the dot sits on
  this tube's corner.
- The original couch rotary table is kept as a labelled option.

Sketches (opening pose 45/30/−15, the −15° set by the Y slide):
`../sketches/isocentric-side.svg`, `../sketches/isocentric-plan.svg`;
principle: `../sketches/chain-principle.svg`.

**Major unresolved problems.**
- Locked tilt stiffness and lock shift of cheap 4-inch rotary tables.
- Creep of the printed roll sleeve under the clamshell rings.
- Which contact the conductance interlock senses.
- The real gun envelope and mass (scan).
- The dot sits ~120 mm higher than on the bare rotator.

Sketches: `../sketches/isocentric-side.svg`, `../sketches/isocentric-plan.svg`,
`../sketches/chain-principle.svg`. Numbers come from `../geometry.py` (a
port of the scene's `pose.js`) and `../stiffness.py`. The gun is the scene's
illustrative proxy **[Agent]** until Derek's scan replaces it.

## The idea

Make the dot a physical **isocentre**: a point in space through which every
rotation axis of the station passes, and on which the beam is calibrated to
land. Then turning any angle knob cannot move the dot, because nothing on the
path from that knob to the beam offsets it. The dot's *place* on the corner is
changed only by translations, and every translation sits nearer ground than
every rotation on its side of the chain, so it carries the rotations with it
rather than knocking the beam off their centre.

The split between the two sides follows gravity. Knobs whose axis is vertical,
and translations, do not change the puddle's relation to gravity, so they go
under the **work** (the "couch"): a rotary table whose axis is the vertical
line through the dot turns the whole rotator, and slides move it radially and
along the tangent. Knobs that tilt the beam relative to gravity cannot go
under the work without also tilting the puddle, so they stay on the **gun**
(the "gantry"): a rotary table on the radial line through the dot for the
hole angle, and a bearing on the grip axis for the roll. Radiotherapy machines
are built this way: patient translations and couch rotation below, gantry and
collimator rotations above. Their daily "isocentre walk" QA test transfers
almost directly to this station (below).

## The chain: what carries what, and what each knob changes

Work side (baseplate → tube):

| Knob | Parameter it changes | Mechanism | Read | Lock / preload |
|---|---|---|---|---|
| Couch φ | Derek's **vertical-axis** angle (gun vs local tangent) | 4-inch rotary table, horizontal, axis on the dot's vertical; rotator on a plate on top | table dial (36:1 → 10°/turn, 10′ divisions) + AS5600 on the handwheel shaft | table lock levers; approach from one direction |
| Couch X | dot's radial place: onto cap ↔ onto wall | two MGN12 rails, radial; micrometer head as the stop | micrometer 0.01 mm; the dot camera is the truth | spring holds carriage on the spindle, then 2 clamp screws |
| Couch Y | the vertical-axis angle again: sliding the work s along the tangent turns the approach by s/R (0.93° per mm) and leaves the corner by only s²/2R | long drawer slide ending on a kinematic stop (ball in vee, magnet-held) so it returns to microns | — | used to load and unload; its return must repeat like a knob setting, since 0.1 mm is 0.09° |

Gun side (baseplate → Z column → gun):

| Knob | Parameter | Mechanism | Read | Lock / preload |
|---|---|---|---|---|
| Z | dot's height: up the wall ↔ down on the cap | column outside the couch sweep, T8 lead screw, MGN rails, bracket to the hole table | handwheel dial (2 mm lead, 100 div → 0.02 mm) | screw is self-locking; gravity loads it one way; clamp |
| Hole | Derek's **hole-axis** angle = grip-axis elevation | 4-inch rotary table mounted vertically, axis on the radial X line through the dot, face ~40 mm outboard of the dot | table dial + AS5600; the Klein gauge on the arm reads it from gravity | table lock; the gun's weight always loads the worm the same way |
| Roll | Derek's **grip-axis** roll (wall/cap split) | preloaded bearing pair on the grip axis just behind the grip base (~300 mm from the dot), on the end of a spoke from the hole table | worm dial + AS5600 on the worm | worm self-locks; roll body clamp |
| Standoff | focus position vs the joint (beam line unchanged) | MGN12 on the roll body parallel to the barrel; micrometer stop | micrometer | gravity (≈10–12 N along the barrel **[assumed 1.7 kg]**) holds the carriage on the stop |
| Nozzle extension | nozzle clearance at fixed focus | the gun's own graduated tube, if the shell grips a barrel section that does not move with it **[Unknown]** | its scale | its lock |
| Wire tip | wire tip vs dot: lead, height, lateral | LD40 XYZ micrometer stage on the roll body, carrying the wire guide | 3 micrometers | stage locks |
| Wire angle | approach elevation in the gun frame | swappable printed guide inserts (or a small arc) | insert number | — |

Machine settings (power, wobble, wire speed, pullback, ramps) stay on the
HMI and the rotator console: they are already one-knob-one-parameter. The
station adds only the requirement that they be recorded with the rest.

Three kinds of adjustment are kept physically different
(`chain-principle.svg`): **knobs** (above), **calibration screws** that make
axes meet the dot and are then painted over, and **motions to a stop** (the
standoff retract, the Y drawer, the wire-guide flip, the camera flip) that
leave and return to a stop set by a knob, so getting out of the way never
changes a setting.

## Geometry around the actual gun and joint

- The dot is 232 mm above the bench on the bare rotator. The couch adds about
  120 mm: 80 mm table, 12 mm plate and two slides. That puts the dot about 352 mm
  above the baseplate: 1.08 m above the floor with the VEVOR bench at its
  lowest 28 in, which suits standing work. **[Agent: bench range]**
- At the opening pose (roll 45, hole 30; φ lives in the couch) the proxy's
  nozzle tip is about 5 mm above the rim and 7 mm inboard of the bore. The grip
  base is 279 mm up the grip axis at 30° elevation, about 140 mm above the rim
  and well outside the tube in plan. At roll 45 the gun's back leans in over
  the bore, so the gun occupies x ≤ dot + 17 mm for every roll ≥ 0.
- The **hole table** sits outboard on +X with its axis on the X line at joint
  height. The tube's farthest +X point moves outward as the couch turns:
  63.5 + 61.85(1 − cos φ) from the tube axis. With the table face about 40 mm
  outboard of the dot, the couch can turn about ±50° before the tube comes
  within 10 mm of the table.
- The **spoke** (arm plate) runs in a plane about 30–40 mm outboard of the dot:
  outside the tube's radius at every height, and outboard of the gun for every
  roll ≥ 0. At its end a bracket steps inboard to hold the roll bearing
  coaxial with the grip axis.
- The **Z column** must stand outside the rotator's sweep, since the rotator
  base reaches about 260 mm from the dot when the couch turns ±45°. A bracket
  reaches in to the table's base about 86 mm below joint height, which is
  roughly 110 mm above the top of the rotator base. The dot sits on the rotator's free +Y side, which keeps the
  NEMA 23 at 90° from the gantry; it never comes under the table within ±90°
  of couch travel.
- The rotator is unchanged. It clamps through its four Ø10 bench holes to the
  drawer instead of the bench.

## How it is used

**QA (start of a session, ~10 min): the isocentre walk test.** A printed
*corner phantom* sits in the nest in place of a tube: a short ring with
the Ø123.70 bore, a cap face at the real recess depth and a matte white
insert at the corner. With the red dot on, turn each rotary knob through its
working range while the dot camera watches. The trace each knob draws is that
knob's coupling to dot position, measured in millimetres. Adjust calibration
screws until the traces shrink, then record them. The station's quality is
then a number: for example, "hole walk 0.03 mm over 20–45°", not a hope.

**Per tube.** Y drawer out → load and indicate the tube (≤ 0.25 mm radial TIR
per the existing procedure) → seat the cap (tacked by hand as now, or in the
station, below) → drawer back to its latch.
Next, standoff back down onto its micrometer stop and the wire guide back to its
stop; feed the wire and cut it at the stick-out gauge. Set the recipe knobs,
each approached from the same side and then locked. Trim couch X and Z until
the camera shows the dot at the recipe's measured offset from *this* tube's
corner. The micrometer is the actuator; the camera image is the parameter. The
tacks can be made here too, at the recipe pose: the rotator's degree
readout indexes the eight 45° stations, so the tack pattern becomes part of
the record instead of a hand operation. The Y drawer needs about 150 mm of
travel: the gun, lifted 40 mm up its barrel line, clears the rim by about
30 mm while the tube slides out along +Y, away from the gun.

**Dry lap.** Pedal one full revolution with the red dot only. The camera logs
the dot-to-corner offset around the lap. That is the tube's runout map at the
weld, in the same load state as the weld: the gun is static in both, and so
are its supports and cables. Only the wire's push into the puddle and heat are
missing.

**Weld.** Trigger by a Bowden cable to a printed lever on the shell (below),
with the pedal as now. Nothing touches the gun.

**Lift-off / stuck wire.** Release trigger (the HMI's wire pullback runs),
then pedal. The head is locked where it was, which is what the current
procedure asks for, so a stuck wire is snipped from the open side of the tube
opposite the gun. The camera mount flips away on a kinematic seat to make room.

**Unload.** Wire guide flips up to its stop; standoff lever lifts the gun up
the barrel line about 40 mm and latches; Y drawer out. No knob is touched.
The drawer's return stop is a kinematic seat, not a cam latch, because a
tangent offset is an angle (0.93° per mm).

**Second closure.** The tube is inverted in the same nest and the rim height
is unchanged. Its purge hose leaves under the rotator between the feet and runs
along the drawer; couch rotation of ±45° only flexes it. X and Z are trimmed
by camera for the second cap's actual recess.

**Second person.** The recipe is a card of numbers plus a camera reference
image. They set the knobs from one side, lock them, and compare the live image
with the reference. The station shows them whether they got it right.

## Loads, freedoms, and when precision is needed

- **During the weld the gun is static and the work turns.** The loads on the
  gun side are then constant except for three things. The wire's push into
  the puddle (**[Unknown]**, a few N assumed) goes through the wire stage into
  the roll body, not through the shell. The wobble motor's vibration is small
  and at 80 Hz. Radiant heat is small 250 mm away. So precision is needed as
  *static stability for ~50 s* and as *repeatability between setting and
  resetting*, not as stiffness against moving loads. The dry run measures
  almost exactly the weld's static state.
- **Gravity moments keep one sign**, so worm and screw backlash is taken up the
  same way every time:
  - Hole table: the load's centre is always on the −Y side of the X line.
  - Z: the load always hangs downward.
  - Standoff: gravity pulls the carriage down the barrel onto its stop.
  - Roll: for roll ≳ 10° the centre of mass swings inboard, so the moment
    keeps one sign. Near roll 0 it passes over the axis and flips, so a light
    torsion spring preloads the worm there.
- **Arm sag hardly reaches the dot.** The gun folds back along the spoke, so
  the nozzle sits near the spoke's root. For a 300 mm spoke carrying 2.5 kg
  **[assumed]**, the nozzle's gravity-induced motion changes by only about
  0.002 mm (4040 extrusion), 0.005 mm (printed 60 × 60 PET-GF box with 4 mm
  walls) or 0.027 mm (2020 extrusion) as the hole angle goes from 20° to 45°
  (`stiffness.py`). The unknown compliances are in the *joints*: tilt of the
  rotary tables and roll bearing, the shell-to-gun contact, and the rails. The
  walk test measures exactly those.
- **"Fixed" is the baseplate**, a common plate under both the couch table and
  the Z column (aluminium tooling plate, a welded steel frame, or two extrusion
  rails). A flexing wooden bench top between the two halves would put the
  bench into the chain.

## Trying to break it

1. **The couch axis misses the dot by e.** Then φ moves the dot by about e·φ:
   a 1 mm miss and 15° give 0.26 mm. *Repair:* two calibration screws position
   the couch table on the baseplate; the walk test drives e down. *Left:* the
   tube's own runout still moves the corner ±0.125 mm in a lap. That belongs
   to the workpiece, not the station, and the dry-lap map records it.
2. **Couch tilt.** The corner stands about 280 mm above the table face, so
   0.01° of tilt moves it 0.05 mm. A table has a little tilt clearance
   unlocked. *Repair:* rule — adjust unlocked, then lock; the lock pulls the
   table onto its face, so the locked tilt is set by flat contact. *Left:* the
   lock-induced shift is unmeasured. The camera shows it (dot before and after
   locking) as part of QA.
3. **Tube-to-tube variation.** Bore, cap recess and seating differ per tube,
   so a micrometer reading does not reproduce a dot place across tubes.
   *Repair:* the parameter is defined as the camera-measured dot offset from
   *this* tube's corner. Micrometers only drive it. *Left:* the camera's
   calibration (pixel scale, viewing angle) becomes part of the record.
4. **The roll bearing cannot be threaded over a captive umbilical.** The
   QBH/umbilical leaves the grip butt and its other end is at the laser unit.
   A closed ring on the grip axis must either pass over the gun nose-first or
   be open-sided. *Repair A:* size the bearing bore so the gun passes nose-first
   (6816, 80 mm bore — the scan decides whether that clears the body and grip).
   The pair then lives permanently on the roll body, and the roll body's outer
   housing on the spoke is a hinged split clamp, so the gun and roll body lift
   out together. *Repair B:* an open C-shaped roll track (rollers on a printed
   or cut arc around the grip axis) that the gun drops into from the side.
   *Left:* whether 80 mm clears the real gun. *(Wave 3: Repair A fails on the
   proxy. The gun reaches 130 mm from the grip axis and needs a ≥ 130–145 mm
   clear circle to pass a ring. The replacement is branch R2 under
   "Wave-3 revisions".)*
5. **The wire guide sits below the rim and blocks unloading.** The stage's
   ±6.5 mm cannot lift it out. *Repair:* the stage mounts on a flip hinge with a
   kinematic return stop (a motion to a stop), and the feeder's retract button
   pulls the wire back into the guide first.
6. **The conductance interlock.** The laser emits only when the gun and the
   work-clipped workpiece form a circuit (manual 3.6.2). Moving the wire guide
   off the gun's own bracket, and holding the gun in a plastic shell, could
   break the path by which contact is sensed. *Repair:* a braided jumper keeps
   the wire guide electrically common with the gun body. Nothing metal in the
   station may also connect the gun to the tube, or the interlock would be
   satisfied permanently. *Left:* **[Unknown]** which contact the X1 Pro
   senses — nozzle, wire, or body. That needs Derek's observation.
7. **The operator's hand on the trigger pushes the gun.** *Repair:* a printed
   lever on the shell presses the trigger. A bicycle-brake Bowden cable pulls
   it, with the housing stop also on the shell, so the pull reacts inside the
   shell and puts no net force on the gun. The hand lever sits on the bench;
   the housing runs through the roll bearing with the umbilical. *Left:* the
   trigger force and travel **[Unknown]**.
8. **Umbilical drag changes between settings.** At a given setting it is
   static. *Repair:* clamp the umbilical to the roll body (not the gun) just
   behind the grip base, and hang its span from a spring balancer so its pull
   changes little with the hole angle. Roll twists the bundle about its own
   axis over the free span (±30° over about 1 m **[estimate]**). That is a
   distributed twist, not the tight coiling the manual forbids, but it is
   worth a look.
9. **Collisions over the ranges.** The nozzle is 5 mm above the rim and the
   grip base 140 mm above it. With hole below ~20° the proxy's barrel
   comes within 5 mm of the bore wall (`geometry.py`: hole 20 → 5.3 mm gap),
   so a hard stop on the hole table sets the lower limit. The wire guide and
   nozzle are both near the dot; at large roll the nozzle swings toward the
   guide. The real limits come from the scan.
10. **Stack height and access.** The +X side belongs to the gantry. The
    operator works from −X/+Y, which is also the side for snipping wire and for
    the camera.

## Branches

### Wire mount — which relation each choice holds constant

| Wire guide mounted on | Gun angle change | Standoff change | Couch X/Z change | Keeps Derek's "wire with umbilical" |
|---|---|---|---|---|
| the gun's own bracket (as by hand) | wire angle rotates with gun; tip stays at the isocentre if it starts there | **tip moves off the dot** | wire moves with the beam | yes |
| **the roll body (main proposal)** | as above | tip stays | wire moves with the beam | yes, conduit through the roll bearing |
| the spoke, outside the roll | hole rotates the wire, roll does not | tip stays | wire moves with the beam | partly |
| its own small isocentric mount on the Z carriage | wire angle unchanged | tip stays | wire moves with the beam | no, the conduit runs separately |
| the rotator base (work side) | unchanged | unchanged | **beam moves relative to the wire** | no |

No row is "correct"; each decides which experiment is one-parameter. Derek's
scene rolls the wire with the gun (row 2 matches it).

### Motorised: the knobs become software, with no kinematics in between

Each handwheel takes a NEMA 17 on a belt, and each micrometer becomes a small
lead-screw stage. Because every motor already equals one parameter, the
software is a list of named axes. No inverse kinematics, and a calibration
error in one axis cannot leak into another. The dot camera closes the loop. An
AI dry-run experiment ("sweep roll 30→60 in 2° steps, three tubes") is a
product of axis lists. The trigger stays human, and dry runs never fire. This
is where Derek's "AI conducting repeated laser-dot dry runs" lands most simply.
A general-purpose arm could take the same poses, but it would need a solver
between every "knob" and its joints.

### Weld-language axes (the "collimator ring")

Derek's three axes were chosen for cable geometry: roll about the dot–grip-base
line keeps the cable exit still. In weld terms they are three-parameter
knobs. At the opening pose (`geometry.py`, assuming the wobble sweeps along
the gun's local X as the scene draws it):

| per 1° of | work angle | travel angle | wobble-crossing angle |
|---|---:|---:|---:|
| roll | −0.49° | −0.08° | −0.53° |
| hole | +0.59° | +0.82° | −0.60° |
| vertical (couch φ) | +0.54° | −0.54° | −0.78° |

A pure +1° of work angle is roll −1.12°, hole +0.26°, φ +0.56°. The isocentre
makes such a combination safe, because the dot does not move, but it is three
turns. The alternative puts the innermost bearing **around the barrel** (a
ring on the turned barrel section, coaxial with the beam): roll then changes
only the wobble line's orientation and the wire's clock position. The barrel
is also the best datum for gripping the gun. The cost is that the cable exit
swings on a ~118 mm radius about the barrel, which is exactly what Derek's axis
avoids. So the station can decouple the cable or decouple the weld angles, and
the choice belongs to Derek. A lookup table ("to change work angle alone, turn
…") serves either way.

### Hole axis as an arc

A carriage on an R 300 arc centred on the dot, instead of a table on the axis:
it is readable straight off the arc and supports the gun close in. It is
developed in `c-arm-on-the-gun.md`.

## Wave-3 revisions (after borrowed-ecosystems' objections)

The original arrangement above stays as it was. These are labelled branches
and corrections. Source: `../../../exchange/borrowed-ecosystems--on--one-knob-one-parameter.md`.

**R1 — Y is a yaw knob the camera cannot see.** Agreed. A tangential offset s
leaves the dot on the corner (s²/2R) and turns the approach s/R, 0.93° per mm.
Three changes follow:
- The drawer's return is a kinematic seat, already changed above.
- Derek's dial indicator on the drawer end becomes a yaw witness in the walk
  test (five out-and-in cycles).
- **Branch B-Y, no couch table.** A micrometer stop on Y makes Y the yaw knob:
  ±3° is one knob to within 0.085 mm of radial error, which the per-tube camera
  trim of X absorbs.
  - For larger yaw, X follows Y through a printed cam, X = R − √(R² − Y²).
    Equivalently, the couch runs on a parallelogram with 61.85 mm cranks, so the
    work translates round a circle about the dot without turning.
  - This removes the 4-inch couch table, about 80 mm of stack, the ~5 N·m
    eccentric load, and the swinging of motor, purge hose, ground lead and
    camera.
  - *What it costs:* for large changes yaw stops being one dial (a cam or a
    lookup), and the cam's profile error becomes an X error, left for the camera.
  - *Left uncertain:* whether the rotary table's large range is ever needed.
    That depends on the process window Derek finds.
  - I prefer B-Y as the default and the table as the option.

**R2 — The roll bearing cannot pass the gun.** Agreed and checked: in my own
geometry the proxy gun reaches 130 mm from the grip axis. Its silhouette along
the barrel needs at least a 132 mm circle, so 6816 (80 mm) and 32011 (55 mm)
cannot pass nose-first.
- **Branch R-C (borrowed-ecosystems' repair).** The shell continues behind the
  butt as a printed sleeve coaxial with the grip axis, split in halves around
  the cable and aluminium-lined where it is clamped.
  - Two hinged clamshell rings, ~95 mm apart on the spoke's end bracket, close
    around it, so nothing threads.
  - Three PTFE-tipped screws per ring are the calibration screws that put the
    sleeve on the grip axis, found by the walk test.
  - **The roll knob** is a 100 mm lever on the sleeve resting on a micrometer
    head, loaded by the one-signed gravity torque (0.2–1.2 N·m, i.e. 1–12 N at
    the tip) and locked by tightening the rings. 0.01 mm is 0.006° of roll.
  - Their estimate is 0.02–0.08 mm of dot motion per 2 N at the nozzle. It is
    larger than the preloaded bearing pair I had hoped for, but the pair cannot
    be installed.
  - *Left:* the rings clamp a printed sleeve, so its creep under ring pressure
    is the new unknown. Keep the rings snug for setting and tight for the weld,
    and re-check with the walk test.
- **Branch R-O**, the open roll track, stays as the second route.

**R3 — Hole angle as a gravity-loaded sine arm (borrowed-ecosystems' branch
B-S).**
- A preloaded bearing pair on the hole axis, with a hardened ball on the spoke
  at L = 200 mm resting on a gauge-block stack. The gun's weight (1.0–3.3 N·m at
  the corrected pose, one sign) holds it down.
- sin(e − e₀) = Δh/L. The stack is both the setting and the record, and returning
  is re-stacking: a minute, exact, no gear, no backlash.
- Through my view this is a knob paired with its *reference standard*. The table
  or a micrometer push-rod does the sweeping; the stack checks the sweep's zero
  and is the return to baseline.
- *What it changes:* a joint whose lock shift is unmeasured is replaced by one
  whose setting is a certified artefact.
- *Left:* upward cable tugs lift the ball unless a light hold-down spring is
  added. It is slow for AI sweeps, which is why it stays the reference, not the
  sweeper.

**R4 — The work locates X (borrowed-ecosystems §5).** Spring-load the couch X
slide so the tube's OD rests on a fixed wheel pair straddling the dot (±30°,
25 mm below it).
- X then reads "offset from this tube's OD", and tube-to-tube variation drops
  out mechanically. During the weld the whole couch floats on its X slide and
  follows the OD's runout: ≤ 0.017 mm radial error at the procedure's runout
  limit, by their estimate.
- *Where I differ:* the wheel reads the OD, but the weld is at the bore corner.
  Wall-thickness variation around the circumference (0.065 in wall;
  tolerance unrecorded) enters directly.
- The floating couch now carries ~8 kg on the slide, so preload must beat slide
  friction and the rotator's reaction torque.
- *Left uncertain:* wall-thickness variation. One indicator reading on the OD
  and one on the bore of a tube would settle it.

**R5 — Carry the weight, but keep gravity's one sign.** My wave-2 note proposed
floating the gun on a CG balancer to unload the tables and bearings. Their
objection holds: a balancer that fully floats the gun removes the one-signed
torque that the worms, sine arms and roll lever rely on.
- Revised: relieve the gun's weight only down to a few newtons of preload.
- Or hang the umbilical alone, which is the larger varying force.

**On "five to seven precision joints, each with unmeasured lock shift".** That
is fair: every joint's lock shift is an unknown until the walk test measures
it. The branches above replace two joints with artefacts (gauge stack, clamped
rings). `knob-wired-suspension.md` is the joint-free form of the same knob set.

## Parts

Printed: couch plate adapter (or aluminium), rotator clamp blocks, spoke
plate (PET-GF box or aluminium plate), roll body with split outer housing,
shell (full length, gripping the gun's barrel sections as the datum, trigger
lever, Bowden stop), wire-guide inserts and flip mount, stick-out gauge,
corner phantom, camera arm with kinematic seat.

Bought (evidence in `../../../sourcing/one-knob-one-parameter.md`): two 4-inch
rotary tables ($99–$160, Prime), micrometer heads ($16), MGN12 rails ($18),
6816 or 32011 bearing pairs ($15–$17), module-1 worm ($24), LD40 XYZ stage
($117), AS5600 modules ($8 for 3), Klein angle gauge ($33), spring balancer
($20), T8 lead screw, baseplate. Nothing here needs a quote or a lead time
beyond a few days.

## What it contributes, what is open

**Contribution.** It shows that "change one thing" can be a *mechanical*
property, not a procedure. Rotations cannot move the dot, translations
cannot change angles, the numbers on the dials are the record, and the
coupling left over is a measured millimetre figure from the walk test.

**Major open problems.**
- Whether 4-inch rotary tables are stiff and repeatable enough when locked
  under an eccentric 10 kg couch or a 300 mm spoke. It is plausible for cast
  iron, but unmeasured.
- Roll bearing size against the real gun (nose-first pass), or the open-arc
  alternative.
- The interlock path.
- How the station looks and works with the whole stack raising the dot 120 mm.

**Rests on assumptions:** gun mass ~1.2 kg, umbilical and wire forces of a
few N, the wobble's direction (only the weld-angle table uses it), and the
proxy's grip-base location.

**Questions for Derek:**
1. What does the gun weigh, and where does it balance?
2. Does the interlock sense contact through the nozzle, the wire or the body?
3. What trigger force and travel does it need?
4. Which barrel sections stay fixed when the graduated tube is turned?
5. Does the red dot sweep when wobble is on in red-light mode? If so, the
   camera can read the wall/cap split directly.
6. Is the umbilical's QBH end ever disconnected at the gun?
