# work-as-datum on carry-and-locate — the switch-locked skate (wave 4)

Their idea: `explorers/carry-and-locate/ideas/switch-lock-skate.md` (idea E).
My numbers: `explorers/work-as-datum/guided_hand_calcs.py` (the cup and tail
geometry is shared with my wave-4 idea `ideas/guided-hand.md`). Scene opening
pose, dial offset applied.

## What I take as given from theirs

The lock taxonomy is right and useful beyond this idea. A switch that only
raises the preload on contacts that already touch (switchable magnet, vacuum,
ball feet) shifts the pose by micrometres. Gap-closing locks shift it by
hundredths to tenths. A float that carries the load through the switch
removes "load changing hands".

In the skate itself (MagJig 95 shoe on three 10 mm balls, on a steel plate
~53 mm above the rim beside the dot), the numbers that matter are:
- 24–39 N sideways holding against 1–5 N in-weld loads;
- ~3 µm of lock shift;
- the plate's X/Y slide as the radial and plan-angle controls (the tangent
  slide equivalence);
- magnetic stops as memory.

---

## 1. The difficulty, in the variant they wrote down

The main arrangement: shoe on a steel plate carried by a post from the
rotator's frame, the pose remembered by magnetic stops on that plate, the
height set "for this tube (height screw against a rim gauge or the camera)".
Their session step 6 says: "A second person does step 5 without knowing
anything about the pose."

The shoe sits **61 mm from the dot horizontally and 53 mm above it**. Because
the dot is carried by the skate at that short distance, the skate is the
dot's reference. So everything that moves the plate or the shoe relative to
the corner reaches the dot, amplified:

| What moves | Where it enters | At the dot (their geometry) |
|---|---|---|
| Debris 0.01 / 0.05 / 0.10 mm under a ball | shoe tilt | 0.02 / 0.11 / 0.22 mm (their calc) |
| Switch twist (knob torque before grip) | shoe yaw | 1° of yaw = 1.06 mm at the dot (their calc) |
| Tube length ±3.2 mm | corner vs room plate | up to 3.2 mm up the wall or 2 mm onto the plate, plus 4.5 mm of focus, until the height screw is reset |
| Radial runout ±0.125 mm, face ±0.15 mm | corner vs a locked room plate | passes straight through during the lap |
| Reseating and inversion | corner vs room | a new offset each time |

The stops remember a pose **in the room**. The things that change from tube
to tube are **in the work**. So the second person's return to the stops
gives the right gun-to-room pose and a wrong gun-to-corner pose. The per-tube
height screw (set by rim gauge or camera) is the step that needs knowing,
which is the step their own claim wanted to remove.

## 2. The assumption behind it

The skate is placed at the nose because that is where hand motions map most
directly onto the dot: X on the plate is the dot's radius, Y is plan angle.
The assumption is that **the room plate can stand in for the corner**. But
the plate is the room, and the corner moves per tube, per revolution and per
reseat. The skate's two strong properties (tiny lock shift, memory in stops)
are spent on the one location where every room error arrives at full scale.

## 3. Repair R-A: skate the tail, and let the work hold the dot

Keep their hardware; move it.

- **At the nose — a cup on the work.**
  - Three hardened 8 mm balls on the shell ring the barrel ~41 mm up from
    the dot, on a 57 mm circle.
  - They sit in a concave spherical band of radius 50 mm **centred on the
    dot**. The band is carried by my plate hanger: port seat + centre pin,
    three stainless wheels on the plate face, a clamp spring, from
    `ideas/work-hung-suspension.md`.
  - The contact normals at the three balls all pass through the dot, so the
    cup fixes the dot's three translations and leaves all three rotations
    about it free. It is a single-part version of their own
    wire-located suspension's virtual ball joint (idea B), carried by the
    tube.
  - At the true pose the balls sit at z 19–49 above the plate, with ≥ 11 mm
    clearance to the lip and plate.
- **At the tail — their skate.**
  - A ball boss on the shell at the grip base (the cable exit, on Derek's
    grip axis, 279 mm from the dot) drops into a **round vertical bore** in
    the MagJig shoe. The ball is free to slide up and down in the bore.
  - The shoe skates on a steel plate on a post from the rotator frame,
    exactly as they built it, with balancer, stops and switch.
  - The shoe's X and Y place the tail horizontally, and the tail's height
    follows from the sphere about the dot. So **the skate sets hole angle
    and plan angle, 0.21° per mm of slide**, and the dot does not move while
    it slides.
- **Roll** about the dot–tail line (Derek's grip axis) is left over. Their
  pose block, a gravity-preloaded roll stop, or the hand (my wave-4
  guided-hand idea) sets it.

What each weak point becomes:

| Their weak point | In R-A |
|---|---|
| Debris 0.1 mm under a ball | Tilts the shoe ~0.15°; the tail ball ~20 mm up the bore shifts ~0.05 mm; the gun turns ~0.01° **about the dot**; the dot doesn't move to first order |
| Switch twist | The bore is round, so shoe yaw moves nothing |
| Lock shift ~3 µm | 0.0006° at 279 mm |
| Tube length ±3.2 mm | The dot rides the cup; the angles change 0.66° at full tolerance (re-slide or accept); the per-tube height screw is gone, since the tail's height is free in the bore |
| Runout, reseat, inversion | The dot follows the plate; angles change ≤ 0.03° per 0.125 mm |
| Plate flatness | Waviness under the tail shoe tilts angles by hundredths of a degree |
| Stuck wire (3–5 N along the tangent at the dot) | The force passes through the cup's centre, so it puts no torque on the gun. The cup holds it with ≥ 4–7 N of seating preload (contact angle 35°: capacity 0.70 × preload). The tail shoe sees nothing |
| "A second person without knowing anything" | Now true at the joint: hanger on the plate, balls into the cup, tail into the bore, magnet on |

Loads and carry:
- **The balancer** hangs at the gun's centre of mass as in their E. Set it to
  leave 7–10 N resting on the cup, which is the cup's preload. The tail bore
  takes no weight, only horizontal location.
- **The plate** then carries ~7–10 N at r ≈ 45–60 mm, about 0.4–0.5 N·m
  against the loose tube's 0.9–2.5 N·m, with the hanger clamp internal.
  That is the same budget as my work-hung suspension.
- **Trigger** by their shell presser. A hand press is tolerable too: its force
  mostly goes into the tail bore and the magnet's 24–39 N of friction.

Teach and memory:
- Slide the tail on its plate until the angles are right (camera or
  protractor), switch on, set the stops.
- The stops now hold **angles**, and angles are forgiving (0.21°/mm, so a
  0.05 mm return error is 0.01°).
- **Position** lives on the work, fixed by the cup's centre. A fine radial
  and height stage between the hanger and the cup (two micrometer heads)
  trims the dot relative to the corner once per recipe.

What R-A leaves uncertain:
- whether printed or machined cup pads hold their spherical centre on the dot
  to ~0.1 mm (calibrate like their E-dome: rotate the gun and shim until the
  dot stops wandering);
- heat on the cup pads and balls, ~40 mm from the puddle and 13–43 mm above
  the rim;
- the plate hanger's ports-and-nipples dependence (Derek hasn't said whether
  nipples may sit in the ports while welding);
- clutter around the nose: cup pads, wire guide and the camera's view.

## 4. Two lighter branches (their arrangement kept closer)

- **R-B: the skate plate rides the work.** Their shoe stays at the nose, but
  its steel plate is carried by the plate hanger instead of a room post.
  - An arm leaves the hub over the free +Y side and curves outside the rim to
    the shoe's place beside the dot, ~50 mm up, staying out of the plume
    above the puddle.
  - The magnet preload is internal between shoe and plate, so the hanger
    carries only in-weld loads: 1–5 N at r ≈ 120 is 0.12–0.6 N·m on the tube,
    with a 25–40 N clamp.
  - Tube length, runout and reseat drop out, and the stops remember a pose in
    plate coordinates.
  - The stops travel with the hanger between tubes, but debris and switch
    twist still reach the dot at their full amplification.
- **R-C: keep everything, change only the height step.** Replace "height screw
  against a rim gauge or the camera" with a spring plunger and dial touching
  the **plate face** (my W1 transfer). The second person cranks to zero. That
  removes the skill step and the rim's waviness from Z. Runout and reseating
  still pass through.

## 5. What their idea does that mine lack, and what transfers

**Theirs, missing from mine:**
- **Teach-by-hand in seconds, then lock with micrometres of shift.** My plate
  hanger, V-loop and cup have no lock state at all. They are gravity- or
  hand-preloaded contacts, the "preload-increasing" class without a switch.
  Their switchable magnet is the missing lock.
- **Memory as physical stops** a second person can use, with the numbers
  added by scales or a camera.
- **The float through the switch.** Nothing changes hands, which I relied on
  implicitly (balancer at the centre of mass) without naming it.

**Mine, useful to theirs:**
- **Where the reference for the dot should live.** Put the skate where its
  errors are divided by 279 mm, not multiplied by ~2.
- **The dot-centred cup** turns their E-dome (R ≈ 250 mm above the housing,
  room-referenced, hard to make) into a small band (R ≈ 50 mm) around the
  nose, carried by the tube. That is the same geometry with the reference
  moved to the work.

**The split, in one line:** the work holds the dot (three translations), the
skate holds two angles (taught, locked, remembered), and roll goes to a stop,
a block or the hand. Each element is used where its errors cost least.
