# workspace-as-structure on work-as-datum (wave 2)

My view: the room's structure is the first positioning stage and carries the
loads. Theirs: the pose that matters is gun-to-corner, and the corner moves.
I worked on the **endcap compass** (developed furthest), **lip-collar-track**
(left rough), and a shorter section on **between-centres**, because at the true
opening pose it fits inside a room-referenced station directly.

Supporting files in my directory:
`explorers/workspace-as-structure/axis_clearance.py`, `wave2_calcs.py`,
`sketches/paddle-compass.svg` (made by `sketches/make_wave2_sketches.py`).
Parts observed for these repairs (stainless S695ZZ rollers, GE8 spherical
bearing, 0.01 mm digital indicator with RS232) are in
`sourcing/workspace-as-structure.md`, wave 2 section.

---

## 0. A geometry correction that affects all three ideas

`work-as-datum/pose_geometry.py` passes the hole angle straight into
`pose_point` (`report(45, 30, -15)`). The scene subtracts an offset first:
`main.js` line 198, `holeRotation = holeDegrees - HOLE_AXIS_OFFSET`, with
`HOLE_AXIS_OFFSET = 35` and default dial 30. So the scene's opening pose uses
hole parameter −5. Their "opening pose" is **dial 65**, a much steeper gun.
My `geom.py` applies the offset, and running both confirms the difference:

| At grip 45, vertical −15 | Scene opening pose (dial 30) | Their script (= dial 65) |
|---|---|---|
| Beam below horizontal | 45.4° | 71.4° |
| Grip base (cable exit) from the tube axis | r 233, 140 mm above the plate, az −90° | r 118, 253 mm up, az −75° |
| Nearest gun surface to the tube axis, z 100–180 mm | 55 mm | 1.4 mm (body over the axis) |
| Nearest gun surface to the axis, z 0–45 | 38.8 mm (nozzle, az −17° to −39°) | 39 mm |
| Corner 1 mm high → dot onto the plate | 0.64 mm radial (+0.75 along the seam), focus 1.40 | 0.34 mm, focus 1.06 |

Consequences for their files (their observations are correct *at dial 65*):

- **The column over the tube axis is open at the opening pose.** Every gun
  surface stays ≥ 38.8 mm from the axis at every height. Across grip 30–60,
  vertical −30…+15 and dial ≤ 40, the nearest surface stays ≥ ~21 mm away.
  It closes only at dial ≥ 50 (`axis_clearance.py`). A post up the axis from
  the hub, or a quill down it from above, is available for the poses Derek
  uses by hand.
- **The compass frame ring at r ≈ 45, z 30–45 hits the nozzle and barrel.**
  At the true pose these sit at r 38.8–40.2, azimuth −17° to −39°, z 15–45.
  The ring has to stay inside r ≈ 30, or open over the gun's quadrant.
- **The grip base is twice as far from the hub (233 mm).** Trigger and cable
  moments about the compass seat are therefore ~2× their estimate: 5–15 N at
  the grip gives 1.2–3.5 N·m, against the A2 seat's 0.09–0.35 N·m limit. The
  force-quiet requirement gets harder, which motivates the repair in §1.
- **Per-tube height matters more on the plate side.** A corner that sits 1 mm
  high puts the dot 0.64 mm onto the plate (not 0.34) and moves focus by
  1.4 mm. A corner 1 mm low is unchanged: the dot lands 1 mm up the wall.

---

## 1. Endcap compass → branch **"paddle compass"**: two contacts on the plate, one on the room

### The difficulty, in their variant A2

Three stainless ball transfers at r = 35 give a support triangle with a
17.5 mm inradius. The gun's weight, the cable exit and the trigger all act
far outside it: the grip base is 233 mm from the hub at the true pose. With
10–20 N of residual weight after the balancer, a ball unloads at
0.09–0.35 N·m. A 1.5 N cable pull or trigger push at the grip is enough to
reach that. The tube underneath stands loose in its nest and lifts at
0.9–2.5 N·m.

### The assumption behind it

All three vertical constraints have to come from the plate. That is what makes
height and both tilts follow the work, but it also means the support polygon
can be no larger than a region of a Ø123 plate inside a crowded recess.

### The repair: take the one rotation that doesn't move the dot, and give it to the room

Put two contacts on the plate **on the dot's radius** (the scene's hole-axis
line), and move the third far out onto a room plane under the grip:

| Contact | Sets | Referenced to |
|---|---|---|
| Centre pin (on their seat bar and nipples) in a spherical bearing in the paddle hub | x, y | plate centre (work) |
| P1 roller at (36, 0), P2 roller at (−40, 0), on the plate face | z at two points on the dot's radius → height at the dot + tilt about Y | plate face (work) |
| P3 ball foot at ≈ (−60…−90, −250) on a room plane at rim height | z far out → rotation about the P1–P2 line | room |
| Fence at P3 | azimuth about the tube axis | room (the freedom that doesn't matter) |

Six contacts, kinematic. **The dot lies on the P1–P2 line**, so the one
rotation the room sets (about that line) doesn't move it. The pivot is at
the roller centres, 5 mm above the face, so 1 mrad of that rotation moves the
dot 5 µm along the seam. Radial and height at the dot stay fully
work-referenced, as in their compass:

- dot height = 1.34 × P1 − 0.34 × P2;
- x and y come from the plate centre, with their ±0.19 mm RSS budget
  unchanged.

The room plane is whatever flat surface the station has at rim height:

- the collar plate of the table opening (`ideas/drop-in-collar.md`);
- the sled's plate (`ideas/countertop-sled.md`);
- a deck standing on the rotator's own base, which needs no hole in any bench.

The gun sits on the paddle in its shell or pose block. The paddle is
Derek's "gripped along its length" shell, lying from the tube mouth onto the
counter. Sketch: `explorers/workspace-as-structure/sketches/paddle-compass.svg`.

### Geometry at the true pose (`axis_clearance.py`)

- **Hub:** 38.8 mm from the nearest gun surface. A spherical bearing plus
  spring on the pin fits.
- **P1 at r = 36:** ~11–12 mm from the nozzle at the opening pose, ~5–8 mm at
  vertical −30°. Use a miniature stainless bearing as a wheel (axle radial,
  rolling tangentially; e.g. a 5 × 13 × 4 mm 695-size) rather than a 1 in
  ball transfer, which would also collide with the nipples' hex (r 11–27).
  Moving P1 to r 30 gives more room at 1.45× instead of 1.34× at the dot.
- **Paddle arm:** leaves the hub toward azimuth −110° to −120°, away from the
  barrel's −17° to −61°. It crosses the rim 8–20 mm above it, then runs over
  the counter under the housing (which starts ≥ 73 mm above the rim) to P3.
- **Paddle underside:** ≥ 25 mm above the plate inside r 32, clear of the
  turning seat bar and the nipples.
- **Wave-4 correction:** the P1 check above was for a point. A roller
  *holder* (r 7, 25 mm tall) at (36, 0) clears the nozzle by only ~4 mm at the
  opening pose and collides at vertical −30°. Put the two plate rollers on a
  line through the dot tilted 30° off the radius toward +Y instead:
  P1 (32.4, 17.0), P2 (−16.1, 45.0), clearing the gun by 15–22 mm. See
  `explorers/workspace-as-structure/ideas/split-mount-station.md` and
  `split_mount.py`.

### Loads (`wave2_calcs.py`; gun + shell + paddle 21 N [assumed])

- **Inradius:** ~33 mm, against 17.5 mm for A2.
- **Where the weight lands:** P3 carries ~10–13 N, the plate the rest. No
  balancer is needed; the weight rests.
- **Trigger:** a hand pressing at the grip adds load near P3 and lifts
  nothing. Their "force-quiet" condition relaxes to "force-sensible".
- **Cable:** an upward pull at the grip base is resisted by the weight about
  the P1–P2 line (2.5 N·m). Up to ~10 N holds; 20 N lifts P3. Anchor the
  umbilical to the room plane just behind P3, as the table station already
  does.
- **The new weak direction is lifting P1.** P1 and P2 share the plate load
  according to the gun's CG, which is unknown. For three CG guesses and P3 at
  x = −15…+30, P1 can go to zero or negative.
  *Repair:* a hold-down spring on the centre pin (thrust washer on the
  paddle hub, nut on the pin), about 20 N. It clamps paddle to plate like a
  C-clamp: the pin pulls the plate up, P1/P2 push it down 38 mm away, and the
  net force on the tube is zero. That adds ~10 N to each of P1 and P2 whatever
  the CG. The nipples carry 20 N of tension in their threads. P3 then goes to
  x ≈ −60…−90 for margin.
- **Stuck wire:** tangential drag at the dot goes into the pin (translation)
  and the fence at P3 (the moment, over a 250 mm lever).
- **Paddle friction and the loose tube:** rolling contacts only (P1, P2 on the
  turning plate; P3 on a ball foot). The pin sees ~0.2 N of rolling drag, far
  below what shifts the loose tube.

### What "fixed" is fixed to, and what the room now leaks in

- **Radial runout at the plate centre** (±0.125): followed by the pin. The
  paddle yaws about P3 by δ/250 (0.03° for 0.125 mm), harmless.
- **Face tilt:** followed about Y (P1 vs P2). About X it comes from the room,
  i.e. the plate's tilt relative to the room plane (≤ ~2.4 mrad at face-runout
  acceptance). That changes the gun's hole-axis angle by ≤ 0.14°, once per
  revolution.
- **Tube length:** becomes an angle instead of a position. A plate 1 mm
  high relative to the room plane rolls the gun 0.23° about the dot's radius;
  at the ±3.2 mm cut tolerance that is ±0.73°. The dot stays in the corner.
  In the table station the per-tube shelf trim (§4) removes even that.

### Workflow changes

- **Calibration puck:** it still works. Put it in a second opening in the same
  room plane. The puck-to-plane height only sets the harmless roll
  (0.23°/mm), so a puck set within a millimetre reproduces the weld geometry.
- **Tacking:** unchanged from their note. The paddle goes on after tacking,
  and its hold-down spring loads the plate internally.

### What remains open

- The CG (to set P3 and the spring).
- Whether hand-tight nipples take 20 N of tension without shifting centre.
  Their ±0.07 mm estimate was for zero load.
- P1's clearance to the nozzle at steep vertical angles.
- Whether nipples may sit in the ports during the weld (Derek).

---

## 2. Lip-collar-track (rough) → branch **"map on a cold lap, hold in the room"**

### The difficulty, in C0 (pinch pair + rim roller 25° ahead of the puddle)

A follower placed ahead of the puddle corrects the dot with the wall
position *at the contact*, not at the dot. For a once-per-revolution
eccentricity e (runout) the residual after following is 2·sin(lead/2)·e. For
ovality a·cos 2φ it is 2·sin(lead)·a. At C0's 25° lead:

| Lead | Runout left (single) | Runout left (symmetric pair ±lead) | Ovality left (single) | Ovality left (pair) |
|---|---|---|---|---|
| 10° | 0.17 | 0.02 | 0.35 | 0.06 |
| **25°** | **0.43** | 0.09 | **0.85** | 0.36 |
| 40° | 0.68 | 0.23 | 1.29 (worse than not following) | 0.83 |

(`wave2_calcs.py` §3.) So C0 removes about half the runout error and about
15% of the ovality error, while keeping contacts on the soft lip.

C1's collar has a separate problem in any room-referenced station with a
counter at rim height. The collar sits 12–30 mm below the plate, which is
inside the counter's opening. It needs an r ≈ 95 opening and a carriage
reaching down into the annulus, in the heat.

### The assumption behind it

Reading the wall *during* the weld, beside the puddle, is close enough to
reading it *at* the puddle. The table shows it isn't at 25°. The lead can't
shrink much, because the nozzle and wire occupy the gun's side of the dot
(barrel at r 39–45, azimuth −17° to −61° at z 0–60 above the plate).

### The repair / branch

Split *reading the work* from *holding the gun*, using the fact that the room
structure is stiff and can carry an actuator.

1. **Cold lap, gun lifted off** (the sled and the paddle both lift off and
   return to pose). Lower a probe from the collar at the dot's own azimuth:
   - their pinch pair in the top 2 mm of the lip, at zero net load;
   - a plate-face skid 12–20 mm inboard of the corner (the plate face, not the
     rim, which is only the saw cut).
   
   Each drives a digital indicator or a cheap linear scale. Pedal one
   revolution and record radial and height against table angle. Lead angle
   0°, so runout and ovality at the dot are captured completely. No heat, no
   bead, no lip contact during the weld.
2. **Weld, gun back in pose, probe up.** Replay the map by moving the *work*:
   - radial on the X stage under the rotator (`ideas/fixed-gun-moving-shelf.md`);
   - height on the shelf's Z.
   
   A pure radial deviation at the dot's azimuth, runout or ovality, is
   cancelled by translating the rotator the same amount, at a 0.02–0.04 Hz
   rate that steppers on hand wheels handle easily. The gun, wire and
   umbilical never move.
3. **What the map can't know: weld-time change.** Thermal growth of the ring
   near the joint is ~50–200 µm radial for 50–200 K, plus any lip distortion.
   A live single contact ahead of the puddle (C0's pinch at 25°) still reads
   that slow, smooth drift well. The lead error applies to the once- and
   twice-per-rev shape, which the map already has. So: **map for shape, live
   contact for drift**. The live correction is (live reading − map value at
   the contact's azimuth). This keeps C0's pinch pair as the drift sensor.

### What stays uncertain

- Replay needs table angle in real time. The rotator reports degrees only as
  a readout, so this needs a firmware stream from the 14,400-pulse count or a
  separate encoder.
- Lap-to-lap repeatability of the tube in the nest.
- Whether 0.1–0.2 mm of thermal growth matters at all against the unknown
  process window.

C1's collar isn't needed in this branch. C1 remains the port-independent
continuous follower, with its heat problem unresolved.

---

## 3. Between-centres inside a room-referenced station (short)

**Difficulty, in B1:** the tailstock is a C-arm that "comes in low
(z ≈ 45–60) from the far side", and its route "has to be chosen per pose
family". It hangs from a mast on a sub-plate that has to be built.

**Assumption:** the column over the axis is blocked by the gun body. That is
true at dial 65, false at the opening pose (§0).

**Repair:** for hole dials ≤ ~40, the tailstock is a **vertical quill straight
down the tube axis** from a short bridge over the +Y (camera) side of the
mouth. Every gun surface stays ≥ 38.8 mm from the axis at the opening pose,
so a Ø20 quill clears it by ~29 mm. It is a
drill-press quill, not a C-arm, and it doesn't depend on the pose family in
that range.

In the table station:

- **The collar is B's sub-plate.** The bridge bolts to the collar; the
  rotator hangs from the collar on the shelf posts.
- **Quill preload stays inside the station.** The 30–50 N runs collar →
  bridge → quill → plate → tube → nest → rotator → shelf → posts → collar,
  with the bench outside it.
- **Tailstock alignment is set once.** Aligning the quill to the rotator axis
  is a collar-internal relationship; the test-indicator base can sit on a
  steel collar.
- **The quill scale is the per-tube height gauge (B1).** It reads the plate
  centre, and the shelf crank brings it to the recorded number (§4).
- **Unloading order:** lift the quill before the shelf drops to unload.

At dial ≥ 50 the column closes, and B's C-arm route is needed again.

---

## 4. What their per-tube height finding does to my table opening

**The finding goes into the table station's routine.** In my table station the
shelf is cranked every tube anyway (drop ~70 mm to slide the tube out). So the
per-tube height set costs nothing extra, but "return to the recorded crank
number" is wrong: it references the far rim, and at ±3.2 mm cut tolerance
that is a 2 mm dot error at the true pose.

**Repair:** return to a reading taken on the plate, not to a crank number:

- B0's spring plunger with a dial, mounted on the collar and touching the plate
  face ~20 mm inboard of the dot; or
- the tailstock quill scale (§3).

Crank until it reads the recorded value, lock, recheck the dot. The same tube
repeats for its second closure.

**Knock-on changes to the table station:**

- **Drop margin:** the unload drop needs ~3–4 mm more travel for the longest
  tubes.
- **Rim height after the trim:** it is constant, because the recess is set by
  spacer. The nozzle-to-rim clearance (~5 mm at the proxy pose) doesn't shrink
  for long tubes once the trim is done.
- **The sled:** the same trim (shelf) or its three foot screws.
- **The paddle:** only the harmless roll (0.23°/mm) is at stake, so a coarse
  trim is enough.

---

## 5. What their ideas do that my arrangements lack, and what transfers

**Theirs, missing from mine:**

- **The corner itself as the reference.** Tube length, runout, reseating and
  inversion leave the pose without a measurement step. My arrangements
  measure-and-trim every tube (Z) and accept runout (≤ 0.25 TIR).
- **The calibration puck.** A replica joint for dry runs and AI experiments
  off the rotator. It transfers directly to the sled (a second fence/stop
  around a puck opening in the collar) and to the paddle (§1).
- **A force budget against the loose tube.** The moment limits (0.9–2.5 N·m
  to lift the tube in its nest) apply to anything that touches the work,
  including my collar-mounted probe (§2) and the tailstock (§3).

**Mine, useful to theirs:**

- **A large, stiff room plane at rim height.** It gives the compass the
  outrigger it lacks (§1), gives B its sub-plate and bridge (§3), and gives
  C's probe a mount (§2).
- **Cable anchoring to structure** close behind the grip. This is what makes
  a work-referenced gun survivable.
- **The corrected pose geometry and the open axis column** (§0).

**Same fact seen from both frames:** their "rotation about the plate's axis
is the one freedom that doesn't matter" and my "a slide along the tangent is
the vertical-axis turn" are one geometric fact. A tangent translation is a
rotation about the tube axis plus a yaw at the dot. In the paddle, the fence
(azimuth) is the room's share of it.

**Can a work-referenced locator live inside a room-referenced structure?**
Yes, in three ways found here:

- as a **partial contact set**: the paddle takes the dot-moving freedoms from
  the work and the rest from the room;
- as a **work-to-room transfer at setup**: the plunger or quill reading drives
  the shelf, after which the gun is room-held;
- as a **map replayed by room actuators** (§2).

The dividing line in each is the same: which freedoms move the dot relative to
the corner (the work should set those), and which only move the gun around the
dot or along the seam (the room can set those and carry the loads).
