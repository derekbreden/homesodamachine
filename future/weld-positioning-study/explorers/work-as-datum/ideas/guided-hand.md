# H. Guided hand — the hand stays the actuator, the work holds the dot

Status: wave 4, developed. Sketch: `../sketches/guided-hand.svg` (from
`make_guided_hand_sketch.py`). Numbers: `../guided_hand_calcs.py`. Scene
opening pose, dial offset applied.

## Picture it (as it stands after wave 5)

Derek, or a second person, holds the gun by its grip as today and pulls the
trigger, but the gun rests in two guides.

- **Nose.** Three hardened balls on the printed shell sit in a cup whose pads
  lie on a sphere centred on the laser dot. The cup is carried by the plate
  hanger riding the end plate (port seat, centre pin, three wheels). The dot
  is fixed to this plate's corner, and every rotation about the dot stays
  free.
- **Tail.** A ball on the shell at the grip base drops into a round vertical
  bore on a post from the rotator frame, which sets hole angle and plan
  angle.
- **Hand.** It holds the one remaining freedom, roll about Derek's grip
  axis, and presses lightly into the cup.
- **Support and record.** A balancer takes the weight. An IMU and three
  seat contacts record what the hand did.
- The rotator turns the plate under the hanger, and nothing slides on the
  work.
- **Branch H1-p (wave 5).** Sprung outer pads close the cup's preload
  internally, so the hand no longer has to be the preload. It holds roll and
  the trigger only.

**Sketch:** `../sketches/guided-hand.svg` (H1, true opening pose). The cup
with sprung outer pads is drawn in `../sketches/work-hung-suspension-D4.svg`.

**Major unresolved problems:**
- In H0 and H1 the hand is the preload: a fading push unseats the balls, and
  a push over ~10 N nears the loose tube's lift point. H1-p is the repair.
- The cup centre must be calibrated onto the dot.
- Heat and clutter at the nose.
- How hard people actually push, and how much roll wander matters to the
  weld; unmeasured.

Neighbours and credit:
- **sequence-of-use's hand saddle C-h**
  (`../../sequence-of-use/ideas/rim-riding-saddle.md`): the hand presses a
  saddle onto the rim, and the rollers position. It is the cheapest test of
  "contacts can locate the dot".
- **carry-and-locate's wire-located suspension (B)** and **E-dome**: the
  virtual ball joint at the dot.
- **My own plate hanger** (`work-hung-suspension.md`).

## The idea: a router template for a turning corner

A router template holds the cut's path; the hand only pushes the router
against it and steers. Here the joint moves itself (the rotator), so the hand
does not feed. Its jobs are to press the gun into a guide, keep one forgiving
freedom on its mark, pull the trigger, and be there: react, stop, lift, snip.
The guide carries the pose.

The split is chosen by what a hand can and cannot hold for a ~50 s revolution
(about 51 s including the 20° overlap). The figures are estimates, not
measured on Derek:

| Quantity | A hand over ~50 s | Needed (agent proposals, not requirements) | So |
|---|---|---|---|
| Position in free air | tremor 8–12 Hz, ~0.1–0.5 mm; drift of millimetres over tens of seconds | ~0.1–0.3 mm at the dot | the guide holds it |
| Angles by eye, with a pointer | ±2–3° | a few degrees? (unknown) | the hand can hold one of them |
| A steady push | 5–15 N for a minute is easy; its direction wanders | a preload that never reaches zero | the hand is the preload |
| Weight 1.2–1.6 kg + roll torque 0.6–0.8 N·m | today's practice, tiring over many tubes | — | cup, fork and balancer carry it |
| Attention | foot on pedal, eye on puddle and index mark, finger on trigger | — | fewer jobs is better |

The guide takes position, the hand's worst skill. A fork takes two angles.
The hand keeps **roll about Derek's grip axis**. The dot sits on that axis,
and the beam is only 25° off it, so 1° of roll turns the beam 0.42° and
doesn't move the dot. That is the freedom a hand can hold with the least
consequence.

## What the guide touches: a cup centred on the dot

- **On the shell.** Three hardened 8 mm balls on stubs ring the barrel
  ~41 mm up from the dot, on a 57 mm circle.
- **On the work.** Three pads lie on a sphere of radius 50 mm **whose centre
  is the laser dot**. Each pad's normal passes through the dot, so the three
  contacts fix the dot's three translations and leave all rotations about it
  free. It is a ball joint whose centre is in the corner, where no hardware
  can go.
- **What carries the pads.** Stalks from the plate hanger: port seat, centre
  pin in a GE8, three stainless wheels on the plate face, clamp spring. The
  cup's centre is therefore fixed to this plate's face and centre, whatever
  the tube's length, runout, seating or inversion.
- **Geometry.** Ball heights 19–49 mm above the plate face, ≥ 11 mm clearance
  to the lip and plate. The wire guide passes inside the ball circle.
  - A smaller cup (R 40, 30°) fits too, with 7.4 mm of clearance and a
    weaker hold (lateral capacity 0.58 × preload instead of 0.70 ×).
- **Trimming the centre onto the corner.** Two micrometer heads between
  hanger and cup, radial and height, set once per recipe.
  - Calibrate on the calibration puck: rock the gun in the cup with the red
    dot on. If the dot wanders, the pad sphere's centre is not on the dot;
    shim until it stays.
- **Interlock.** The balls sit in the printed shell, insulated from the gun's
  metal. The pads are isolated inserts. The welder's gun-to-work conduction
  interlock is untouched.

## What the hand does, and what stays free

**H1 (the main form).**
- **Tail.** A ball boss on the shell at the grip base (the cable exit,
  279 mm from the dot, on the grip axis) drops into a **round vertical bore**
  on a room post or the rotator frame. The ball can slide up and down in the
  bore. The bore's horizontal position sets the hole angle and plan angle
  (0.21° per mm) and never moves the dot.
- **The hand** holds the grip as now, index finger on the trigger. It presses
  gently along the barrel into the cup (5–10 N), and keeps a roll pointer (or
  an IMU readout) on its mark.
- **Weight.** Cup and bore carry it. A balancer at the centre of mass removes
  the 0.6–0.8 N·m gravity roll torque from the wrist and leaves ~7–10 N
  seating the cup when the hand lets go.
- **Free:** roll, which the hand holds. Nothing else.

**H0 (no fork).** The hand holds all three angles about the dot. The dot
still doesn't move. It is the simplest build (hanger + cup only) and the one
that shows most directly what a hand does to the angles.

**H2 (fixture end of the spectrum).** The tail bore sits in carry-and-locate's
switch-locked skate. Angles are taught by sliding the tail and locked with
micrometres of shift, and remembered by magnetic stops. The hand keeps roll,
preload and trigger. See `../../../exchange/work-as-datum--on--carry-and-locate-w4.md`
(repair R-A).

## The trigger

The squeeze is internal to the hand (palm on grip, finger on trigger), so it
puts no net force on the gun. Any push the arm adds while squeezing goes along
the barrel into the cup, which raises the preload. This is the one
arrangement in the study where a hand trigger is the right answer rather than
a problem.

## As the tube turns under a hand-held, guided gun

- **At the hanger.** The plate turns under the hanger's wheels, and the seat
  and pin turn with it. The hanger's azimuth is held through the cup by the
  gun, and through the gun by the tail bore.
- **Nothing slides on the work.** The balls rest still in the cup unless the
  hand rolls.
- **What the hand feels.** Runout (±0.125 mm at the plate centre) and face
  tilt carry the cup, and the gun with it, by tenths of a millimetre. The
  tail bore lets the angles follow by ≤ 0.03°.
- **The overlap.** The 20° past the first tack is judged at the index mark as
  now. The console's degrees can be read aloud, or shown on the seat-light
  unit, because the eyes are freer.
- **Keeping it seated.** If the hand's push fades toward zero, the balls can
  lift and the dot is free. The seat light (below) shows it at once. The
  balancer's residual weight is the floor under the hand.

## The stuck wire

- The drag (3–5 N along the tangent at the dot) passes through the cup's
  centre, so it puts **no torque on the gun**.
- The cup holds it while the seating preload is ≥ 4.3–7.1 N (contact angle
  35°): the hand's push plus the residual weight.
- Release the pedal. The gun rests in cup and bore without the hand. The
  procedure's "one hand keeps the head where it stopped, the other cuts"
  becomes "let go, then cut with either hand".
- Reset the stick-out before the next weld.

## How a second person reproduces it

1. Tacks done. Nipples in, hanger on, clamp nut.
2. Tail ball into the bore; nose balls into the cup until the seat light is
   green.
3. Roll pointer to the recipe mark.
4. Pedal; trigger once rotation is steady; release at the overlap mark,
   trigger then pedal.

The skill left is keeping ~5–10 N of push and a pointer on a mark for 50 s.
That is teachable in minutes, unlike holding a pose in the air.

## What gets recorded

- **Recipe (per pose).** The cup's two micrometer readings (the dot relative
  to the corner), the tail bore's position on scaled rails (hole and plan
  angle), and the roll target.
- **Per weld (the hand's freedom, instrumented rather than trusted):**
  - roll, and the two fixed angles as a check, from a BNO085 IMU on the shell
    at 50–100 Hz;
  - seat events: each shell ball is an isolated contact and each pad an
    isolated insert, read by a small floating circuit (an ESP32 like the
    project's others) that is never connected to the welder's interlock.
    Any unseat is time-stamped;
  - pedal and trigger times, the console's degrees at release, and camera
    video of the dot and puddle.
- **Why record.** If roll wander turns out to matter, the record shows it,
  and the roll becomes a stop or a block (the H2 direction). If it doesn't,
  the hand stays.

## Breaking it

1. **The push can lift the loose tube.** The worst case is a hand pushing
   straight down the barrel with the cup taking all of it
   (`guided_hand_calcs.py`). The horizontal part of that push, ~30 mm above the
   plate and ~176 mm above the nest seat, gives:

   | Push | Tipping | Restoring |
   |---|---|---|
   | 5 N | 0.62 N·m | 1.6–2.0 N·m |
   | 10 N | 1.24 N·m | 1.8–2.2 N·m |
   | 15 N | 1.85 N·m | 2.06 (first closure) – 2.44 (second) N·m |

   It holds, with a thin margin at 15 N in the first closure. The tail bore
   shares the push in practice. *Keep the push light (≤ 10 N).* Or add a
   hold-down: a tie through the rotator's Ø90 passage into a lower-plate port
   works for the second closure but not the first, whose lower end is open.
   *Uncertain:* how hard a person actually pushes.
2. **The push fades.** The balls lift and the dot is free. The seat light
   and the residual weight are the defence. A magnet in each pad would add a
   floor that doesn't depend on the hand, but NdFeB weakens above ~80 °C,
   ~40 mm from the puddle.
3. **Cup centre not on the corner.** A printing or assembly error of
   ±0.1–0.2 mm becomes a fixed dot offset. Find it on the puck with the red
   dot; take it out with the micrometers.
4. **Heat and spatter on the pads and balls,** 13–43 mm above the rim, ~40 mm
   from the puddle. Metal pads, a shield, unmeasured.
5. **Clutter at the nose.** Pads, stalks, wire guide and the camera's view
   from +Y. It needs a CAD check around the real scan.
6. **Both directions of rotation.** The cup is symmetric, so there is no
   mirror part; C-h needs one per direction.
7. **The hand as the only preload during a long session.** Fatigue lowers
   the push. The balancer floor and the seat light cover it; the record shows
   the trend.

## Against sequence-of-use's C-h

| | C-h (their hand saddle) | H1 |
|---|---|---|
| Guide | Rollers on the rim and OD, 22–52° ahead of the puddle, moving with the tube under a stationary saddle | Stationary cup on a hanger riding the plate face and port-pair centre |
| Hand | Preload and tether | Preload, roll and trigger |
| Angle wander | Moves the dot | Doesn't, to first order (the pivot is the dot) |
| Error it carries | Lead-angle error (43% of runout, 85% of ovality at 25°) and rim waviness | Nipples in the ports, a tail post and more parts |
| Cost | One print and a few bearings | More, as above |

Suggested order: **C-h first**, since it is the cheapest proof that contacts
can locate the dot. Then **H0** (hanger and cup, the hand holds all angles,
with the IMU recording them). Then **H1** with the tail bore.

## Parts (representative)

- **Plate hanger:** as in `work-hung-suspension.md` (316 nipples, GE8
  spherical bearing, stainless S695 wheels, clamp spring).
- **Balls:** 8 mm 440C stainless (commodity).
- **Trim:** two micrometer heads (sourced by other explorers).
- **IMU:** BNO085 module (observed this wave, Prime, same day, 100+ bought per
  month).
- **Seat logger:** ESP32, as already used in the project.
- **Printed:** shell with ball stubs and tail boss, pads/stalks, tail bore on
  a post.

---

## Wave 5 — H1-p: stop borrowing the preload from the hand

carry-and-locate's critique of my suspension nose, that its locating capacity
was "borrowed from the weight it carries"
(`../../../exchange/carry-and-locate--on--work-as-datum-w4.md`), applies here
with the hand in place of the weight. In H0 and H1 the cup locates only while
the hand pushes (≥ 4.3–7.1 N for a stuck wire). A push that fades unseats the
balls, and a push over ~10 N nears the first-closure tube's lift point.

**H1-p (branch).** Add the sprung outer pads of `work-hung-suspension.md` D4:
each shell ball is held between a rigid inner pad and a sprung outer pad on
spheres centred on the dot, ~25 N in total, closing inside the cup.
- The hand no longer has to push. The cup's hold is independent of it, and
  the tipping risk from the hand's push disappears.
- The hand holds roll and pulls the trigger. Rolling against the pads'
  friction costs 0.15–0.5 N·m, easy for a wrist.
- Lifting off needs the outer pads opened: one cam lever flicks all three.
  So "presence" (lift away instantly) becomes one motion slower than before.
- The hand-guided character is kept where it matters: the hand holds the
  forgiving freedom and triggers; the guide holds the rest.

H0 and H1 (hand as preload) stay as the simpler first builds. Their seat light
and IMU record show how much the hand's push actually varies, and that record
decides whether H1-p is needed.
