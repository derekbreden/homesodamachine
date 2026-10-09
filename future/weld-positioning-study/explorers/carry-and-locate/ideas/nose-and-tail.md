# F — Nose on the work, tail on a table, weight on a float

**Picture it.**
- **Nose (on the work).** A small hanger sits on the endcap being welded:
  nipples in its two ports, a centre pin, three stainless wheels on its face.
  It carries a V-loop with a sprung jaw that grips a grooved collar on the
  shell's nose, 46 mm from the dot. That fixes a point near the dot to the
  work.
- **Tail (on a table).** At the grip butt, the shell's rear collar rests on two
  ball transfers rolling on a steel table beside the rotator:
  - the table's height screw sets hole tilt;
  - its cross-tilt screw sets roll;
  - one ball-ended link to a magnet-braked carriage sets and locks plan angle.
- **Carry.** A balancer and a saddle carry the gun and cable, so neither nose
  nor tail carries weight.
- **Adjust the dot.** A micro-stage in the hanger's stalk re-centres the dot
  after angles change.
- **Camera** on the hanger.
- **"Fixed."** The work for the dot's translations; the rotator frame for the
  angles.

**Sketch:** `../sketches/F-nose-and-tail.svg` (true opening pose).

**Major unresolved problems:**
- The printed nose collar's heat and groove wear, 26 mm above the rim.
- The real centre of mass, which sets where the float hooks.
- The cable path past the tail.
- Nipples in the ports while welding (Derek's call).
- The pivot is 46 mm from the dot, so every angle change needs a dot re-trim.
  Work-as-datum's cup (E-RA) removes that.

Sketch: `../sketches/F-nose-and-tail.svg`. Numbers: `../calc/nose_tail.py`,
`../calc/wad_nose.py`. Pose: the scene's opening pose (hole dial − 35).

## Where it comes from (credit), and what is new

A combination that grew out of the wave-3 and wave-4 exchanges. The source
ideas stay as their owners wrote them.

- **work-as-datum**, `work-hung-suspension.md` (D1): Derek's tip loop hung
  from the endcap being welded.
  - A knife-edged V-loop seats a grooved nose collar on the shell, 46 mm from
    the dot.
  - The loop is carried by a plate hanger: 316 nipples in the ports, a centre
    pin in a spherical bearing, three stainless wheels on the plate face, a
    clamp spring, an azimuth tether.
  - An XZ micro-stage in the hanger's stalk is the dot knob.
- **work-as-datum / workspace-as-structure**, `endcap-compass.md` A3 (paddle
  compass): a foot on a room plane whose height is the hole dial (0.23°/mm).
- **machine-that-learns**: the camera sets and verifies (from the hanger's +Y
  side it sees the dot in plate coordinates) and learns lock biases. Plan angle
  done as a translation.
- **Mine:**
  - the float and saddle that carry;
  - the preloaded nose jaw (wave-4 exchange);
  - switch-state locks and the lock-shift classes (`switch-lock-skate.md`);
  - the determinacy check below, which decides how the tail may be locked.

**What is new is the division of work.** Derek's two loops each get exactly
one job:
- the tip loop locates the dot's translations, from the work;
- the base loop locates the three angles, from a table beside the rotator;
- neither carries weight or cable — a float and a saddle do.

## The station

- **Nose (work).** D1's plate hanger and stalk, with a V-loop whose upper half
  is a sprung jaw (~25 N, closing inside the loop), seating the shell's grooved
  collar at barrel z = 30. This makes a ball joint 46 mm from the dot,
  referenced to the plate being welded. The collar is printed, and the loop at
  work potential never touches the gun's metal (their interlock reasoning).
- **Tail (table).** At the base-loop position (40 mm beyond the grip butt along
  the grip axis, 278 mm from the nose, 4° off the grip axis), the shell's rear
  collar carries two ball transfers 120 mm apart, across the nose–tail line.
  They roll on a horizontal steel **tail table** standing on a post from the
  rotator's frame.
  - Under the table: a **height screw** (hole tilt) and a **cross-tilt screw**
    (roll).
  - Beside it: a steel rail carrying a carriage with a switchable magnet
    (MagJig class). One **ball-ended link** runs from the tail to the carriage,
    across the nose–tail line: plan angle, lockable.
- **Float.** A spring balancer carries ~77 % of gun and shell, hooked on a
  shell lug ~85 mm off the centre of mass. That offset keeps both tail balls at
  ~3 N and leaves the nose almost unloaded **[Calc]**. A saddle carries the
  umbilical just behind the tail.
- **Trigger** by a presser inside the shell.

**Constraint count:** 3 (nose) + 2 (ball heights) + 1 (link) = 6, exactly
determined.

### What each knob does (per unit, at the opening pose) **[Calc, nose_tail.py]**

| Knob | Where | Turns the gun | Dot moves |
|---|---|---|---|
| table height, 1 mm | room | 0.23°, almost pure hole tilt | 0.17 mm |
| table cross-tilt, 1 mm (60 mm ball spacing; ~half with 120 mm) | room | 2.1°: roll 2.1°, plus hole 0.4° and vertical 1.0° | 0.83 mm |
| tail slide on the link, 1 mm | room | 0.23° about the vertical through the nose (plan angle) | 0.13 mm |
| stalk X, Z | work | none | ~1:1 |

- Angles are turned about the nose, so the dot shifts by about 0.8 mm per
  degree. The order is **angles at the table, then the dot at the stalk**.
  The stalk does not disturb the angles, and the angles are set by screws that
  hold themselves.
- Plan angle can also come from the hanger's azimuth tether: rotating the
  hanger about the tube axis slides the nose along the joint, which is the same
  thing by the circle's symmetry.

## Break and repair

**1. The first form over-constrained itself.**

- **First form:** a two-ball shoe with a switchable magnet (my
  `switch-lock-skate.md` shoe), locked to the tail table.
- **Problem:** locked friction at two balls adds four constraints, so 3 + 2 +
  4 = 9. The nose follows the plate's runout (±0.125 mm) once per revolution,
  while the locked tail cannot let the gun turn about it. Each revolution the
  gun would be strained between them. With an estimated 50–200 N/mm between
  nose and tail, that is ~6–25 N of cycling load, against a 25 N jaw and
  24–39 N of tail friction. The result would be fretting, and a stick-slip jump
  of the dot when one of them lets go.
- **Repair:** balls that roll (ball transfers), plus one lockable degree of
  freedom (the link). Six constraints, nothing fights, and the gun follows the
  nose by rotating slightly about the tail. The dot follows the corner to
  83–91 %, as in D1.
- **Generalisation:** a lock at a point that is not the work-referenced point
  must lock only the freedoms that the work-referenced point does not set.

**2. Tube length.**

- A 1 mm longer tube lifts the nose 1 mm while the tail stays. The gun turns
  0.23° in hole tilt and the dot misses the moved corner by 0.18 mm
  (0.56 mm at the published ±3.2 mm) **[Calc]**.
- **Repair:** raise the table by the same 1 mm, which is exactly the 0.23°
  back. Measure each tube once; both closures of a tube share the mark (their
  observation). The camera confirms.

**3. Room movement reaches the dot at 46/278 = 0.165.**

- A 0.5 mm lean on the bench puts ~0.08 mm on the dot if the table stands on
  the bench top.
- **Repair:** the table's post stands on the rotator's own base or its common
  plate. The float's anchor can be anywhere.

**4. Unlocked, the float must keep the balls seated.**

- With the float at 90 % hooked at the centre of mass, one ball lifts (the
  centre of mass rolls the gun about the nose–tail line). Hooked ~85 mm off
  the centre of mass at 77 %, both balls carry ~2.9 N, and 1 N cable pushes
  leave ≥ 2.4 N.
- That residual is the only thing holding roll before the weld starts.
  Disturbances during the weld go to the ball heights (stiff in compression)
  and the nose jaw. A lift at the tail of more than ~3 N would unseat a ball,
  so the cable must be carried before the tail.

**5. The nose's own holding** (see the exchange file).

- Gravity-seated, D1's V holds only ~3 N in each direction and unseats under a
  5 N stuck-wire drag or a hand.
- With the float carrying the weight, the nose load is nearly zero, so the
  sprung jaw is required, not optional. With the jaw, every disturbance in the
  inventory short of a 10 N hand holds.

**6. The lock itself.**

- The carriage magnet is a preload-increasing lock: the carriage already rests
  on its rail. Its knob twist is reacted in the carriage body.
- The link's two ball ends have play. The float's line, anchored ~50 mm
  across, gives the link a steady ~0.5 N one-way pull, so the play sits on one
  side.
- Since the link carries only the plan-angle moment (a 5 N stuck-wire drag at
  the dot gives ~0.5 N in the link), its stiffness matters far less than a
  full holder's.

**7. What the tube carries.**

- Almost no weight: the float carries it and the jaw's preload closes inside
  the loop.
- Sideways disturbances at the nose act ~185 mm above the nest.
  - A stuck-wire drag is internal (tube → wire → gun → nose → plate → tube).
  - External pushes (cable, hand) reach the tube at ~0.19 N·m per newton,
    against 0.9–2.5 N·m to lift it. One more reason for the in-shell presser.

**8. Heat, spatter, interlock.**

- The nose collar is printed, 26 mm above the rim; its jaw spring is outside
  the hot zone (work-as-datum's open question stands).
- The tail is ~300 mm from the weld.
- The ball transfers and the tail table must not bond the shell to the work
  lead through the frame; the shoe's printed body insulates.

## How it is used across a session

1. **Per tube:**
   1. Tube in the nest; plate and tacks as the procedure says.
   2. Nipples and seat bar on; drop the plate hanger on, spring nut.
   3. Lower the gun on the float until the collar drops into the V; close the
      jaw.
   4. Set the table height to this tube's mark. The tail's balls rest on the
      table, and the link's carriage is already locked from the last tube.
2. **Dry run.** Pedal one slow lap. The camera on the hanger shows the dot
   against the corner. Trim with the stalk's X/Z. Angles are untouched.
3. **Weld.** Pedal, presser, release, release.
4. **Stuck wire.** Snip. The drag goes round inside the tube–gun–hanger loop;
   the jaw (25 N) and the ball heights hold.
5. **Lift-off.** Open the jaw, lift the gun on the float ~20 mm (the tail
   balls lift off the table; nothing on the table moves), lift the hanger off.
6. **Second closure.** Invert, hanger on the new plate, same table mark. Lower,
   close the jaw.
7. **New recipe.** Height and cross-tilt screws for hole and roll, the link's
   carriage for plan angle; relock; the camera checks. The three table settings
   are numbers: screw turns, a scale on the rail.
8. **Second person.** Hanger on, lower the gun, close the jaw, table to the
   mark. They need know nothing else.

## Toward Derek's automated setup

- Three small actuators at the table (height, cross-tilt, carriage) are the
  angle axes. Each sits ~300 mm from the weld, on the room side, and carries
  only preload.
- The stalk's X/Z on the work is the dot axis. It could be micro-steppers, as
  work-as-datum suggests.
- The camera on the hanger reads the dot in plate coordinates, so learned
  setpoints transfer across tubes: the dot knobs ride the tube, and the angle
  knobs are nearly tube-independent apart from the per-tube height mark.

## Parts (see `../../../sourcing/carry-and-locate.md`)

- **Theirs:** 316 hex nipples, GE8 spherical bearing, stainless 695 wheels,
  ball-lock pin.
- **Tail:** stainless ball transfers (TOVOT 5/8 in, 304 housing, Prime, thin
  stock; many carbon-steel equivalents); a steel table (ground O1 bars or A36
  plate); two fine screws.
- **Plan-angle lock:** a MagJig 95 carriage on a steel rail; ball-ended link
  from M5 rod ends (Prime).
- **Float:** a QWORK-class balancer and a saddle.
- **Nose jaw spring:** a small stainless compression or leaf spring (not
  sourced).

## Contribution and open problems

- **What it adds:** a room-anchored angle set and a work-anchored dot, each
  determinate, with no weight on either. The table screws are the three angles
  almost one-to-one (A3's hole dial generalised to roll and plan). The rule
  from break 1 (lock at a non-referenced point only what the referenced point
  doesn't set) applies to any combination of a work-riding element with a
  room-side lock.
- **Open:**
  - the nose collar's heat and groove wear;
  - whether ball transfers leave the tail smooth enough at hundredths;
  - the real centre of mass (which sets the float hook);
  - the cable path past the tail;
  - the hanger's nipples under load (work-as-datum's open question);
  - the cross-tilt screw's coupling into vertical angle (1.0° per 2.1° of
    roll), which a rotated screw axis could reduce.
