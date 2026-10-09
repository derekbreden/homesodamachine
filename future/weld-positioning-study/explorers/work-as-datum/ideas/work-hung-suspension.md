# D. Work-hung suspension — Derek's tip loop hung from the endcap

Status: wave 3, developed. Sketch: `../sketches/work-hung-suspension.svg`
(from `make_suspension_sketch.py`). Numbers: `../suspension_calcs.py`. Scene
opening pose throughout (grip 45°, hole dial 30°, vertical −15°, dial offset
applied).

## Picture it (as it stands after wave 5)

Derek's two loops and a third ring, with one change: **the loop at the tip of
the gun hangs from the end plate being welded instead of from the ceiling.**

- **The plate hanger.** It rides the plate: port seat + centre pin in a GE8
  spherical bearing, three stainless wheels on the plate face, an internal
  clamp spring, a tether for azimuth. The rotator turns the plate under its
  wheels.
- **The nose.** A short stalk rises from the hanger to an openable,
  knife-edged V-loop around a grooved collar on the shell's nose, 46 mm from
  the dot. That makes a ball joint on the work (the dot's three
  translations).
- **The room.**
  - The base loop around the shell's rear collar and the third ring at the
    housing back hang from lines that set the three angles.
  - A spring balancer carries the weight; a saddle carries the umbilical.
- **After carry-and-locate's critique (wave 5):**
  - **D1-p.** The loop's upper half is a sprung jaw (~25 N), so the collar is
    held by an internal preload rather than by weight. Each room line has its
    own bungee, and the lines are anchored on a post from the rotator's frame.
  - **D4.** The V-loop is replaced by a **cup centred on the laser dot** (the
    shell's balls held between inner and sprung outer pads). Setting the
    angles then no longer moves the dot, and room errors don't reach it to
    first order.
- **Park state.** Between tubes, Derek's arrangement as stated carries the
  gun from room lines alone.

**Sketches:**
- `../sketches/work-hung-suspension.svg` (D1, true opening pose);
- `../sketches/work-hung-suspension-D4.svg` (D4, true opening pose);
- carry-and-locate's `../../carry-and-locate/sketches/F-nose-and-tail.svg`
  (their nose-and-tail built on D1).

**Major unresolved problems:**
- D1 as first written fails. The nose carries only ~4 N once the third ring
  is present, and the groove is at its limit, so a stuck wire or a hand
  unseats it. D1-p and D4 repair this, but untested.
- Gun mass and centre of mass.
- Heat at the nose collar or cup, 26–43 mm above the rim.
- Nipples under the clamp load.
- Clutter around the nozzle (cup pads, wire guide, camera view).
- A stiff post from the rotator frame for the room lines.

## Derek's example, as he gave it

> Imagine if you will:
>
> - One of those metal rubber coated hooks on pegboard walls in garages everywhere
> - Imagine that hook being a complete (openable) loop
> - Imagine that hook hanging from a wire to be held in Z, and suspended from bungees or something stretching in either the X or Y axis, so just two bungees, holding one axis steadyish
> - Imagine one hook around the tip of the gun, and a second hook around the base of the gun (around the umbilical and wire feed)
>   - Can you see how the arm might "grip" (keeping in mind, that "grip" means a complete shell we print with whatever attachments we want to attach to our robot arm anywhere we like on that shell) this in several ways and get entirely different results?
>   - Can you see how a 3rd ring a number of places might reduce the range of motion (or increase the force needed to exercise that range) but at the same time reduce weight further?

carry-and-locate developed this as stated, with everything anchored to the
room (`../../carry-and-locate/ideas/suspension-original.md`,
`wire-located-suspension.md`). I build on these of its findings:

- bungees belong on the radial axis X, and the tangent Y can be left as the
  free swing;
- the tip loop on the graduated tube carries 56–68% of the gun;
- the third ring belongs high at the housing back;
- a loop around the bare umbilical lets it turn (rolling twists it ~0.87×);
- the umbilical needs a large saddle, not a hook;
- **the float alone does not hold a dot**, so every usable form has a stiff
  locator somewhere.

## What changes through my view: one move

**The tip loop's anchor moves from the ceiling to the endcap.** The rest
starts as he described it: two loops, wires in Z, bungees on one axis, a
third ring, a printed shell with attachments anywhere. The loop at the tip is
the one element whose position the dot inherits almost one-to-one, and the
corner under it moves (±3.2 mm tube length, runout, face tilt, inversion). So
it is the one element that should be referenced to the corner. The loops at
the base and the back keep their room anchors and their job of carrying.

### D0 — literal: the tip loop's wire and bungees anchored on a work-borne gallows

The tip loop hangs by its Z wire from a small gallows standing on the plate
(the plate hanger below), and its two X bungees anchor on the same gallows.

- **What it gains.** The tip's *rest position* follows the work. Tube length,
  runout and the inverted closure move the gallows, so the float settles
  where this tube's corner is, not where the last tube's was.
- **What it doesn't gain.** Stiffness. A bungee pair gives ~0.1 N/mm
  [carry-and-locate estimate], so 1 N at the tip moves it ~10 mm wherever
  the anchor is. The work sets where the float settles, not how firmly.
- **Useful as:** the setup state, where the float drifts to a work-correct
  neighbourhood. It could be frozen by locking the tip node to the gallows
  (their A-r4, but locked to the work instead of the room). Kept as the
  literal form.

### D1 — change the contact, not only the anchor

Derek stresses that the loop-to-shell contact decides what the loop locates.
At the tip:

| Contact | Locates at the nose | Leaves free | Verdict |
|---|---|---|---|
| Round loop on round collar, loose (his hook) | vertical support at the loop's low point; weak lateral self-centring (T/gap) | slide along the barrel, all rotations | carries, barely locates |
| V-bottom loop, plain collar | two in-plane translations | slide along the barrel, so the dot slides along the beam and focus changes | not enough |
| **V-bottom loop on a grooved collar** | **two in-plane translations (V flanks) + along the barrel (groove on a knife-edge loop)** | all three rotations | a ball joint at the nose, seated by gravity |
| Ball on the shell in a cup | the same three translations | rotations | equivalent; the ball can't surround the wire guide |
| Loop clamped on the collar | all six | none | fights the room loops; no |

So the tip loop becomes:
- a knife-edged ring whose lower inside is a 90° V;
- engaging a groove in a nose collar that is part of the printed shell
  (enclosing the barrel and the wire guide);
- still a complete, openable loop. Its upper half clears the collar by a
  few millimetres and closes with a stainless ball-lock pin, so the collar is
  captive but not clamped.

The nose is then a ball joint referenced to the plate. The room loops set the
three rotations about it.

**Where the collar sits** (`suspension_calcs.py`):

| Barrel position | Point | From the dot | Above the rim |
|---|---|---|---|
| z = 30 (chosen) | (41, −25, 33) | 46 mm | 26 mm |
| z = 10 | (50, −14, 18.5) | 26 mm | 12 mm |

The z = 10 position is closer to the dot but hotter and more crowded.

**Seating:**
- The barrel lies along (−0.45, −0.54, +0.71), so gravity splits 0.70 into
  the ring's plane and 0.71 along the barrel, where the groove takes it.
- *(Wave 5 correction: with the third ring present, statics puts only ~4.1 N
  on the nose. See "Wave 5" below.)* With a nose share of 7–10 N, the V is
  seated by 4.9–7 N. It holds about
  that much sideways before the collar starts to climb a flank, and the
  groove carries 5–7 N.

**Interlock.** The loop is at work potential, because it is carried by the
plate through the nipples. It touches only the printed collar, never the
gun's metal, so the gun-to-work conduction interlock (manual p.32) keeps its
meaning. A metal-to-metal nose contact would make the fixture close that
circuit permanently.

### The plate hanger (what the tip loop hangs from)

After workspace-as-structure's paddle and my compass seat:

- **Seat.** Two 316 hex nipples, wrench-snug in the tapped ports; a seat bar
  over them; a centre pin at the port-pair midpoint. The pin runs in a GE8
  spherical bearing in the hub, which sets x and y and leaves tilt and axial
  free.
- **Wheels.** Three stainless 695 wheels roll tangentially on the plate face:
  - P1 (36, 0) and P2 (−40, 0) on the dot's radius. The scene's hole axis
    is this line.
  - P4 (0, −38), under the stalk, on the gun's side but outside the barrel's
    descent sector (−10° to −75° at z 20–70) and outside the nipples' sweep
    (r 11–27).
  - They set height and both tilts from the plate face itself.
- **Clamp.** A ~25 N spring on the pin pulls the hub onto the wheels. The
  nose load sits 21 mm outside the P1–P4 edge, so the clamp must exceed
  0.8 × the nose load (6–10 N); 25 N gives ~3×. The clamp force is internal
  and nets to zero on the tube.
- **Azimuth.** A tether line with a bungee runs to a room post on the +Y
  side. It is one-sided, taking the stuck-wire torque of 0.19–0.31 N·m.
  Azimuth itself is the harmless freedom.
- **What the tube carries.** *(Two-support split; ~4 N with the third ring,
  see Wave 5.)* The nose share (7.7–9.6 N for a 1.6 kg gun +
  shell, estimate) plus a ~3 N hanger, applied at r ≈ 48. That is
  ~0.4–0.5 N·m against the 0.9–2.5 N·m that lifts the loose tube in its
  nest: margin 2–5×. This is what the compass lacked. The hanger carries the
  nose, not the gun.
- **Stalk.** From the hub (z ≈ 20) out under the collar to the loop's V. It
  stays below the barrel and clear of the wire, which crosses z = 20 at r 54,
  azimuth −22°, inside the collar's footprint.
- **Camera.** It can ride on the hanger's +Y side and see the dot in plate
  coordinates.

### The base loop, the third ring, and the cable (room)

- **Base loop.** Derek's openable loop, round the shell's rear collar just
  behind the grip butt, carrying 39–51% of the gun.
  - **Z:** his wire, with a grow-light rope ratchet. The ratchet is also the
    per-tube pitch trim.
  - **X, the finding that forces a change:** his bungee pair alone lets 1 N
    at the base move the dot 0.9–1.7 mm. The nose-to-dot lever is 0.09–0.17
    of the base's motion, but 0.1 N/mm is too soft. A line in X (1/16 in
    stainless rope ~100 N/mm, or 2 mm polyester ~13 N/mm over 500 mm), with
    his bungee as its preload, brings that to 0.001–0.013 mm per N. This is
    carry-and-locate's A-r3, needed only at the base, because the nose is on
    the work.
  - **Y:** not needed. With the nose fixed in 3D and the base fixed in X
    and Z, the base's Y is determined (it lies on a sphere about the nose).
- **Third ring.** High at the housing back, on a Z wire from the room. It
  sets roll about the nose–base line, against a 0.6–0.8 N·m gravity roll
  moment from the centre of mass 39–52 mm off that line (estimate).
- **Constraint count:** 3 (nose, work) + 2 (base X, Z, room) + 1 (third
  ring, room) = 6.
- **Derek's third-ring trade, made concrete.** The more weight the third
  ring takes, the less the nose carries. That lowers the load on the plate,
  but also lowers the V's seating, which sets how much sideways push the nose
  resists. The floor is ~5 N left on the nose, so the third ring may carry
  weight but must not unload the tip.
- **Cable.** Umbilical and conduit leave the grip butt nearly horizontally
  toward −Y and go onto a room saddle (R ≥ 350 mm, emitting) right behind
  the base loop. The base loop grips the shell collar, not the cable, so
  the cable can still turn where it leaves the butt. The tip sees none of the
  cable.

### What happens as the tube turns under it

- **Motion at the hub.** The plate turns under three rolling wheels; seat
  and nipples turn with it; the pin turns in the spherical bearing. Nothing
  slides on the workpiece.
- **Runout** (±0.125 mm at the plate centre). The hub and nose follow it.
  With the base fixed in the room, the dot follows to 83–91%: 0.01–0.02 mm
  of error.
- **Face tilt.** The three wheels set the plane. The nose follows the plate
  face's plane at a point 30 mm from the dot, on the same face.
- **Tube length.** The nose moves δ with the plate; the base doesn't. The
  dot misses by 0.09–0.17 δ (0.28–0.53 mm at the full ±3.2 mm) and the gun
  pitches 0.6°. Raising the base ratchet by δ removes both. The same tube
  uses the same mark for its second closure.
- The gun and cables do not move in the room during a weld, apart from the
  runout's hundredths.

### Setup, dry run, weld, lift-off, stuck wire, second closure

- **Park = Derek's original.** Between tubes the gun hangs from room lines
  only: his tip wire (now a park/lift line with a ratchet), the base loop,
  the third ring. His arrangement as stated is kept whole, as the carrying
  state.
- **Setup per tube.**
  1. Tube, plate, tacks.
  2. Nipples in, seat bar on.
  3. Drop the plate hanger on; spring nut on the pin.
  4. Slacken the park line until the nose collar drops into the V; push in
     the ball-lock pin.
  5. Base ratchet to this tube's mark. Red-dot check.
- **Dry run.** Pedal one lap. The hanger's camera sees the dot against the
  corner in plate coordinates.
- **Weld.** A shell-mounted presser (Bowden or solenoid) is preferred. A hand
  on the trigger is tolerable ("force-sensible"): the grip is near the base
  loop, whose X line takes the push. 5–15 N there moves the dot
  ~0.01–0.03 mm with a stainless base line, up to ~0.2 mm with polyester.
- **Lift-off.**
  1. Retract wire.
  2. Pull the ball-lock pin and take up the park line: the nose rises out of
     the V and the gun hangs from the room.
  3. Lift the hanger off the plate (it weighs ~0.3 kg).
- **Stuck wire.**
  - The drag is 3–5 N along the tangent at the dot. It reaches the V
    (capacity 5–7 N), then the hub, then the one-sided tether and the base
    lines. The gun stays within hundredths to a tenth, depending on the tether line; snip.
  - If the drag exceeds the V's seating, the collar climbs a flank into the
    loop's upper clearance: a captive breakaway, not a fall.
  - It reseats when released. Check the dot before restarting.
- **Second closure.** Invert the vessel, put the hanger on the new top plate,
  use the same base mark. The float rod is inside and nothing changes above
  the plate.
- **Second person.** Hanger on, lower the gun, pin in, ratchet to the mark.
- **Calibration puck.** The hanger fits a puck, but the base lines are in
  the room. The puck must stand where the tube stands, within ±1 mm, to keep
  base mismatch under ~0.17 mm at the dot. A puck on the rotator's nest (a
  short tube stub with a plate) does that.

### Fit with Derek's automated-setup vision

- **Dot knobs on the work.** A small XZ stage in the stalk moves the loop
  relative to the hub, and so the dot relative to the corner, nearly 1:1.
  Micrometer heads first, micro steppers later.
- **Angle knobs in the room.** Winches or anchor slides on the base X line,
  the base Z line and the third-ring line turn the gun about the nose. They
  leak 0.09–0.17 of their motion into the dot, which the dot stage and the
  camera take back.
- That is a cable robot for the angles (carry-and-locate's six-wire idea,
  reduced to three lines) and a work-referenced micro-stage for the dot. The
  learned setpoints transfer across tubes because the dot stage rides the
  tube.

## Branches kept beside D1

- **D2 — both front contacts on the work.** A second loop around the barrel's
  back end, on a post from a paddle arm (workspace-as-structure's paddle),
  would make the whole barrel line work-referenced. The base would then only
  set roll about the barrel, so Derek's bungees could stay soft there. The cost
  is the gun's weight moment back on a paddle, with its room foot P3.
- **D3 — three concurrent wires anchored on the work.** carry-and-locate's
  virtual ball joint at the dot, with its three anchors on a cage carried by
  the plate. Base errors then vanish to first order, not just 0.09–0.17×.
  A cage around the gun, riding a Ø123 plate, is the problem; I don't lead
  with it.

## What stays open

- Gun mass and centre of mass: the nose share, the third-ring force and the
  clamp margin all scale with them.
- Nose-collar heat at 46 mm from the dot, and whether a printed groove keeps
  its shape.
- Wrench-snug nipples under the 25 N clamp. Centring was estimated at
  ±0.07 mm unloaded.
- The V's sideways capacity against a hard stuck wire. The breakaway is
  designed in; its reseating accuracy is not measured.
- Stiffness of the room frame for the base X line (the dot sees 0.09–0.17 of
  it).
- Registering the calibration puck to the room.

## Parts (representative)

- **Nipples:** 316 hex nipples (mine, Prime, next day).
- **Hub bearing:** GE8 spherical bearing (workspace-as-structure observed,
  Prime, stock thin; standard ISO size).
- **Wheels:** stainless S695ZZ (workspace-as-structure observed, Prime, 18
  left).
- **Room lines:** grow-light rope ratchets, 1/16 in 7×7 stainless rope and
  3/16 in shock cord (carry-and-locate observed, Prime, high volume).
- **Loop latch:** stainless T-handle ball-lock pin, 6 mm (observed this
  wave, Prime, same day).
- **Printed:** shell with a grooved nose collar round barrel and wire guide;
  rear collar; third-ring boss; knife-edge V-loop halves; plate hanger with
  stalk.

---

## Wave 5 — carry-and-locate's critique, and the dot-centred cup in place of the nose loop

Source: `../../../exchange/carry-and-locate--on--work-as-datum-w4.md`, and
their combination `../../carry-and-locate/ideas/nose-and-tail.md`. D0 and D1
above stay as written.

### What they found — accepted

1. **The nose carries ~4.1 N, not 7–10 N.**
   - My 7–10 N came from a two-support split (nose and base) made before I
     added the third ring. With the ring at the housing back taking 7.2 N and
     the base Z wire 4.4 N, the nose is already below my own ~5 N floor.
   - The third ring's position decides the split, which the text had not
     checked.
2. **A 90° groove holds along the barrel only up to the seating force.**
   - Gravity splits the nose load 0.70 into the V and 0.71 along the barrel,
     so under gravity alone the groove sits at its limit (2.9 N against
     2.9 N).
   - In their load table, a 5 N stuck-wire drag toward +Y unseats the nose,
     a 10 N hand on the trigger unseats it and slackens the base, and a 5 N
     cable lift at the grip slackens the base Z wire.
   - The pattern they name is right: **the nose's ability to locate was
     borrowed from the weight it carries.** Anything that unloads it (third
     ring, cable, hand, float) weakens it.
3. **The room lines are locators, not carriers.** They reach the dot at
   46/278 = 0.165. A 0.5 mm lean on a pegboard anchor is 0.08 mm at the dot.
4. **The order is fixed: angles first, then the dot** (0.8 mm per degree
   about the nose), with the stalk stage as the dot knob.

### Branch D1-p (theirs, adopted)

- **Sprung jaw.** The loop's upper half is a jaw pressing the collar into the
  V with ~25 N, closing inside the loop. Every case in their table holds
  except a 10 N hand, which fails at the base, not at the nose.
- **Room lines with their own preload.** The base Z line is paired with a
  bungee (10–15 N), and the third ring's line too. The lines are anchored on
  a post standing on the rotator's base or common plate, not the ceiling.
- **Weight off the work.** The weight then comes off the plate entirely, onto
  a balancer, and Derek's third-ring trade stops being a trade: seating no
  longer comes from weight.
- **What it costs:**
  - rotational friction at the jaw (~0.06 N·m, some stick-slip in fine angle
    moves);
  - a spring near the hot zone;
  - the stuck-wire breakaway moves up to ~25 N, above the wire's own 3–5 N
    yield.

### Branch D4 (mine): the nose loop becomes a cup centred on the dot

This is the change I planned in wave 4. It still makes sense after the
critique; in fact the critique makes it more attractive, because both of the
difficulties it raises come from the nose being 46 mm from the dot.

- **The cup.** Three hardened 8 mm balls on the shell ring the barrel ~41 mm
  up from the dot, on a 57 mm circle. Each is held between two pads on
  concentric spheres centred on the laser dot:
  - an inner pad at radius ~46 mm, rigid on the plate hanger's stalks;
  - an outer pad at ~54 mm on a spring (~8 N per ball, ~25 N in total).

  All contact normals pass through the dot, so the cup fixes the dot's three
  translations and leaves every rotation about it free. The preload closes
  inside the cup, as in D1-p. It is the same cup as `guided-hand.md`, with
  outer pads added.
  - Geometry: ball heights 19–49 mm above the plate face, ≥ 11 mm clearance
    to the lip and plate (`../guided_hand_calcs.py`).
- **What that does to the critique's points:**

| Critique point | D1 / D1-p (nose ball joint 46 mm from the dot) | D4 (virtual ball joint at the dot) |
|---|---|---|
| Room-line motion reaching the dot | 0.165× | 0 to first order; second order through the pad centre's offset from the dot |
| Setting an angle moves the dot | 0.8 mm per degree, so angles first, then the dot | No; angles and dot are independent knobs |
| Tube length (±3.2 mm) | Dot misses by 0.53 mm and the gun pitches 0.66°, so a per-tube base mark | Dot stays; the gun pitches 0.66° (0.21°/mm), and a base mark is optional |
| Stuck wire (3–5 N at the dot) | Torque about the nose, taken by the jaw | Force through the cup's centre, no torque on the gun; the internal loop tube → wire → gun → cup → hanger → plate |
| Seating from weight | Removed by the jaw | Removed by the outer pads |

- **What D4 costs:**
  - **Friction against angle moves.** It acts at both pads of each ball:
    about 2μ × 25 N × 50 mm = 0.15–0.5 N·m (μ 0.1–0.2), or 0.5–1.8 N at the
    base loop's 278 mm. The room lines can overcome it, but fine angle moves
    will stick-slip.
    - *Branch D4-r:* let the balls roll between the two spherical bands in a
      cage, making a large spherical rolling bearing centred on the dot. Lower
      friction, more parts.
  - **Clutter and heat.** Six pads and their stalks around the nose, 13–49 mm
    above the rim, beside the wire guide and in the camera's view. Metal
    pads, springs outside the hottest zone.
  - **The cup's centre must be on the dot.** It needs calibrating: rock the
    gun with the red dot on and shim until the dot stays. A printed cup
    starts at ±0.1–0.2 mm.
- **Unchanged from D1-p:**
  - the plate hanger and its clamp (nipples, spherical bearing, wheels);
  - a balancer carrying the weight;
  - room lines with their own bungees on a rotator-frame post;
  - the trigger presser in the shell;
  - the park state, which is Derek's lines as stated.

### Where I differ from carry-and-locate's nose-and-tail (F)

F keeps D1-p's nose 46 mm from the dot and takes the angles at a tail table
with screws and a lockable link, with the order fixed as angles, then dot.
- With D4's cup, F's table screws would stop moving the dot at all (their
  table: 0.17 mm per mm of height, 0.83 mm per mm of cross-tilt, 0.13 mm per
  mm of slide). F's tail table and D4's cup combine directly: cup at the
  nose, their table at the tail.
- Their generalised rule applies to D4 as well: lock at the tail only what
  the cup does not set, i.e. the rotations, never a translation of the gun.

**Still uncertain:**
- the gun's mass and centre of mass (the float's hook point);
- heat at the pads;
- the cup's printed accuracy;
- whether the nipples keep their centring under the 25 N clamp and the cup's
  reactions.
