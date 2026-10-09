# work-as-datum — summary entries

The view: the pose that matters is gun-to-corner, and the corner moves. It turns,
runs out, is reseated, changes from tube to tube (OnlineMetals states a ±3.2 mm
cut tolerance) and is inverted for the second closure. So these arrangements let
the corner's own parts set the dot — above all the end plate's face and the
centre of its two tapped ports — while the room carries weight and cables and
sets the forgiving freedoms.

This explorer started without Derek's examples:
- Entries 1–3 came from beyond them.
- Entry 4 develops his suspension example.
- Entry 5 takes up the hand as the actuator, and his "I become the bottleneck"
  concern.
- Entries 6–8 are branches contributed to other explorers' ideas.

All geometry is at the scene's opening pose (grip 45°, hole dial 30°,
vertical −15°) with the 35° dial offset applied.

## 1. Endcap compass (A2), paddle compass (A3), nose-only frame (A4)

**Idea.** A frame sits on the end plate being welded.
- Two 316 hex nipples go finger-tight into the plate's tapped ports.
- A seat bar over them turns with the plate, and a centre pin at the port-pair
  midpoint gives the frame the plate's own centre.
- In A2, a C-shaped ring rests on the plate face on three stainless rolling
  contacts.
- A fork on the rotator base holds azimuth — the one freedom that doesn't move
  the gun relative to the corner.
- A short leg carries the gun's shell, and a balancer carries its weight.

**What sets what.** Height, tilt and radius come from the plate; azimuth and
weight from the room. Tube length, runout, reseating and inversion drop out of the
pose, and so does indicating each tube.

**Break and repair.**
- **Pose correction:** the gun sits off toward −Y, not over the axis.
- **Collisions** (workspace-as-structure): the ring hit the nozzle, and 1 in ball
  transfers would be struck by the turning nipples. The contacts became small
  695 wheels.
- **The decisive break:** a hand on the trigger makes 1.2–3.5 N·m against a seat
  that holds 0.09–0.35 N·m, and the loose tube lifts in its nest at 0.9–2.5 N·m.
- **Repair A3** (workspace-as-structure's paddle): two rollers on the dot's radius
  plus a foot on a room plane under the grip. The foot's height becomes the
  hole-axis dial (0.23° per mm, dot fixed to first order).
- **Repair A4:** carry only the nose (entry 4).

**Parts.**
- 316 hex nipples, $16.13 for 5, Prime, next day; a standard fitting from at
  least 8 sellers.
- KangTeer all-stainless ball transfers, $16.69 for 4, Prime, next day.
- MT2 live centres, $16–19, Prime, same day, 50–100+ bought per month.
- QWORK balancer, $16.97 for 2, Prime.
- Printed: seat bar, ring, leg, pose block.

**Contribution:** the plate-centre datum and the calibration puck.

**Open:**
- Radial precision is about ±0.19 mm (estimate).
- Whether the nipples may stay in the ports while welding.
- How the plate is held before tacking.
- The gun's mass and centre of mass.

**Files:** `ideas/endcap-compass.md`; `sketches/endcap-compass.svg`,
`../workspace-as-structure/sketches/paddle-compass.svg`.

## 2. Between centres (B0–B3)

**Idea.** The opposite choice of which body gives way: the gun stays rigid and the
work is forced onto it.
- The gun is on a mast (B0–B2) or on a bridge over the free +Y edge of a
  rim-height collar (B3, in workspace-as-structure's table station).
- A spring quill with a live centre or ball comes straight down the tube axis,
  which is open up to hole dial ~40, into a countersink on the same port seat.
- The vessel spins between the nest and the centre. Its top plate's centre is
  forced onto a fixed line, and the loose tube is clamped with 30–50 N.

**What sets what.**
- Radius comes from the forced centre.
- Height comes from the quill's reading, set once per tube (B1), or from a
  two-ball rocker riding the plate face (B2).
- B0 is a mast with an indicated tube and a dial plunger.
- "Fixed" is the sub-plate or collar, so the hand trigger and cables load rigid
  structure, not the work.

**Break and repair.**
- If the quill is 0.2 mm off the rotator axis, the nest rocks 0.08 mm per
  revolution.
- B1 doesn't follow face tilt.
- After the pose correction the C-arm became a straight quill
  (workspace-as-structure).
- The quill need not be lifted before the shelf drops: the ball simply parts,
  with 51 mm to spare (a small disagreement with workspace-as-structure).

**Parts.**
- MGN12 rail, $17.99, Prime, next day; a standard profile with about 10 Prime
  listings.
- LMK12UU bushings, $13.39 for 2, Prime (19 left; 10+ interchangeable listings).
- WEN 1 in dial indicator, $14.06, Prime, 300+ bought per month.

**Open:** the ground shoe's side load; face tilt; the rotator base becomes part of
the structural chain.

**Files:** `ideas/between-centres.md`; `sketches/between-centres.svg`,
`sketches/xw-collar-centre-and-lid.svg` (top panel).

## 3. Riding the tube at the weld (C0, C1, C2)

**Idea.** Take the datum from the tube wall near the weld. This is the one
arrangement that needs no ports.
- **C0:** a stationary carriage with a rim roller and a pinch pair on the top
  2 mm of the lip, 25° ahead on the cold side.
- **C1:** a collar (two half-rings closed by a stock 5 in exhaust lap-joint band
  clamp) turns with the tube below the plate and gives a clean track.

**Break and repair.**
- The lip is soft to a push (~30 µm/N, estimate), hence "pinch, don't push".
- The rim is not the plate face.
- A follower 25° ahead leaves 43% of the runout and 85% of the ovality error
  (workspace-as-structure).
- Their C2 maps the wall cold at the dot's own azimuth and replays it by moving
  the work. After a plate-centre datum, only ±0.1–0.2 mm is left to replay.

**Parts.** Stainless rollers; the band clamp at $29.99 for 4, Prime, 400+ bought
per month.

**Open:** collar heat, which decides its material; rim waviness; C2 needs a live
table-angle stream.

**Files:** `ideas/lip-collar-track.md`; `sketches/lip-collar-track.svg`.

## 4. Work-hung suspension (D0, D1, D1-p, D4) *(Derek's suspension example)*

His example is quoted verbatim in the file, and his arrangement is kept whole as
the park state.

**One move:** the tip loop's anchor goes from the ceiling to the end plate.
- **D0 (literal):** the float's rest position follows the work, but it is no
  stiffer.
- **D1:** a light plate hanger on the plate, with a stalk to an openable V-loop
  46 mm from the dot.
  - The hanger is the port seat, a pin in a GE8 spherical bearing, three stainless
    wheels, an internal clamp spring and a tether.
  - The V-loop is knife-edged and grips a grooved collar on the shell, making a
    ball joint on the work.
  - The base loop and the third ring hang from room lines that set the angles.
- The file compares contact conditions: round loop, V, V with groove, ball in cup,
  clamp.
- The loop touches only the printed collar, so the welder's gun-to-work interlock
  keeps its meaning.

**Break and repair.**
- carry-and-locate found:
  - the nose carries only ~4 N once the third ring is present;
  - the 90° groove is at its axial limit, so a stuck wire or a hand unseats the
    nose;
  - the room lines leak 0.165× into the dot.
- Their D1-p: a ~25 N sprung jaw, bungee-paired lines on the rotator frame, weight
  on a balancer.
- D4 replaces the loop with a cup centred on the dot, the shell's balls held
  between inner and sprung outer pads.
  - The room lines then don't reach the dot to first order.
  - Angles and dot become independent knobs, and a stuck wire passes through the
    cup's centre.
  - The cost is 0.15–0.5 N·m of friction against angle moves (a rolling variant is
    noted), plus clutter and heat.
- carry-and-locate built nose-and-tail (their F) on D1. The D4 cup combines with
  it directly and would make its tail-table screws stop moving the dot; that
  combination is not yet written.

**Parts.**
- GE8 bearing and stainless S695 wheels (observed by workspace-as-structure:
  Prime, thin stock, ISO sizes).
- Grow-light ratchets, 1/16 in stainless rope and shock cord (observed by
  carry-and-locate: Prime, 50–800+ bought per month).
- Stainless ball-lock pin, $15.29 for 2, Prime, same day.

**Open:** gun mass and centre of mass; heat at the nose; the nipples under the
clamp load; calibrating the cup.

**Files:** `ideas/work-hung-suspension.md`; `sketches/work-hung-suspension.svg`,
`sketches/work-hung-suspension-D4.svg`.

## 5. Guided hand (H0, H1, H1-p, H2)

**Idea.** A router template for a turning corner: Derek holds the grip and pulls
the trigger, and the guides give the pose.
- At the nose, three balls on the shell sit in a cup centred on the laser dot,
  carried by the plate hanger. The dot is fixed and every rotation about it stays
  free.
- At the tail, a ball at the grip base in a round vertical bore sets hole and
  plan angle.
- The hand holds only roll about Derek's grip axis. One degree of roll turns the
  beam 0.42° and leaves the dot where it is.
- A balancer takes the weight.

**Stuck wire:** the drag passes through the cup's centre; let go, then snip.

**Second person:** balls seated (a light shows it), pointer on the mark, pedal,
trigger.

**Recorded:** an IMU roll trace; seat events on a floating circuit, never on the
interlock; pedal and trigger times; camera.

**Break and repair.**
- In H0 and H1 the hand is the preload. A push above ~10 N nears the tube's lift
  point (1.24 N·m at 10 N against 1.6–2.4 N·m restoring), and a fading push
  unseats the balls.
- H1-p: sprung outer pads close the preload inside the cup, so the hand only holds
  roll and pulls the trigger.
- H2: the tail sits in carry-and-locate's switch-locked skate.
- sequence-of-use's hand saddle C-h is the nearest neighbour and the cheapest
  first test.

**Parts.** BNO085 IMU, $20.49, Prime, same day, 100+ bought per month; 440C balls;
an ESP32.

**Open:** how hard people actually push; whether roll wander matters to the bead.

**Files:** `ideas/guided-hand.md`; `sketches/guided-hand.svg`.

## 6. W1 — collar-hung centre in the table-opening gantry

A branch of Derek's table example, as developed by workspace-as-structure.

**The difficulty.** Their side-loading payoff (the gun never moves between tubes)
repeats the nest's height, not the corner's. Tube length, runout and face tilt
still move the dot.

**Repair.**
- A spring plunger hangs from the collar's free +Y edge, ball tip into a
  countersink on the port seat.
- Crank the shelf until the plunger's dial reads zero, then lock it.
- Tube length and runout are absorbed and the tube is clamped. The shelf and posts
  drop out of the radial loop, and side loading still clears by 21 mm.
- Branch W1b: a sprung shelf pushed against a rigid centre.
- workspace-as-structure adopted the per-tube plate reading (their T-W1) and put a
  plunger on the axis (B3).

**Left:** face tilt; ±0.19 mm of plate-edge eccentricity (estimate).

**Files:** `../../exchange/work-as-datum--on--workspace-as-structure.md`;
`sketches/xw-collar-centre-and-lid.svg` (top panel).

## 7. L1 — a lid that rides the plate and parks on the collar

A branch of workspace-as-structure's lidded mouth seed.

**The difficulty.** Their seed lid hangs from the collar, so it must clear the
worst tube, and its nose ring is fixed to the room while the corner moves.

**Repair.**
- L1 rides the plate on the port seat and three contacts, 3 mm above the rim
  whatever the tube length.
- It is notched from −35° to +10° for nozzle, beam and wire.
- Lugs let it park on the collar when the shelf drops, and be picked up again as
  it rises.
- L1a: the gun's nose ring rides on the lid and its tail on a workspace cradle, so
  work motion reaches the dot at 0.12×.
- The camera and gas port become work-referenced too.

**Left:** heat and spatter; a nose ring on copper.

**Files:** the same exchange file as entry 6;
`sketches/xw-collar-centre-and-lid.svg` (bottom panel).

## 8. R-A — skate the tail, let the work hold the dot

A branch of carry-and-locate's switch-locked skate.

**The difficulty.** Their skate (a MagJig 95 shoe on a room plate, 61 mm beside and
53 mm above the dot) is the dot's reference.
- Debris under a ball reaches the dot at about 2.2×.
- The switch's twist costs 1.06 mm per degree.
- Tube length arrives in full.
- The stops remember a pose in the room, so "a second person needs to know
  nothing" fails at the height step.

**Repair.**
- Their hardware moves to the grip base, 279 mm from the dot, with a round
  vertical bore in the shoe for the tail ball, and the dot-centred cup goes at the
  nose.
- Debris becomes ~0.01° of angle; the twist moves nothing; the ~3 µm lock shift is
  0.0006°; tube length becomes a 0.66° angle change; the height screw is gone.
- Lighter branches: R-B puts their skate plate on the hanger; R-C adds a
  plate-face dial for the height step.
- carry-and-locate adopted R-A as their lead form (E-RA).

**Parts:** MagJig 95, $46, Prime (carry-and-locate's observation).

**Files:** `../../exchange/work-as-datum--on--carry-and-locate-w4.md`;
`../carry-and-locate/sketches/E-RA-cup-and-tail.svg`.

## Transferable pieces

- **Port seat:** two 316 nipples, a seat bar and a centre pin or countersink at
  the port-pair midpoint. It is the plate's own centre in seconds, and the hollow
  nipples keep the purge venting.
- **Plate hanger:** a pin in a GE8, three stainless wheels on the plate face, an
  internal clamp spring and a tether. It is a light stationary frame referenced to
  the plate's face and centre, and handles ~10 N at about 0.4–0.5 N·m on the tube.
- **Dot-centred cup:** balls between pads on spheres centred on the laser dot. It
  is a one-part virtual ball joint at the dot, and lets anything at the tail set
  angles without moving the dot.
- **Calibration puck:** a short ring of the same tube with a spare plate at its
  recess. Any plate-referenced frame parks on it, and dot calibration and AI dry
  runs can happen off the rotator.
- **Findings:**
  - Rotation about the plate's axis is the harmless freedom; it is the same fact
    as the tangent slide being the vertical-axis turn.
  - Tube length (±3.2 mm) is the largest per-tube error. At the opening pose,
    1 mm moves the dot 1 mm up the wall or 0.64 mm onto the plate, and focus by
    about 1.4 mm. Both closures of one tube share it.
  - The Z reference is the plate face, not the saw-cut rim.
  - The loose tube lifts in its nest at 0.9–2.5 N·m.
  - The lip moves ~30 µm per newton of push, so pinch it rather than push it.
  - Anything at work potential must touch only printed parts of the gun.
  - Put a lock where its errors are divided, not multiplied.
  - carry-and-locate's rule: a lock away from the work-referenced point may fix
    only what that point doesn't.

## Questions only Derek's observation can answer

1. Gun mass and centre of mass, alone and in its shell.
2. Umbilical and conduit pull at the grip in his usual routing, and the trigger
   force.
3. May 316 fittings sit in the ports while welding? What is the port chamfer
   diameter?
4. How is the plate held at its recess before the first tack?
5. Tube length spread and end squareness: are these OnlineMetals cuts, or his own
   halves of a 12 in length?
6. Which part of the gun carries the interlock contact in wire-fed welding, and
   does the welder show it live?
7. How hot does the region 25–45 mm from the puddle and 10–50 mm above the rim get
   during a lap?
8. Is there room for a post on the rotator frame, and overhead structure for a
   balancer?
9. How much roll or angle wander changes the bead? That is for logged experiments
   to answer.
