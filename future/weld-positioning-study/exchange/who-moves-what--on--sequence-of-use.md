# who-moves-what on sequence-of-use (wave 2)

My view: every freedom and every phase is owned by some body — gun, shell, lid,
seat, work, rotator, a setup step — at some rate (per session, recipe, tube,
weld). Sequence-of-use's view puts time on the other axis. Together they give
an allocation *per phase*, which neither of us had.

I worked on **A, lid carrier** (their furthest-developed idea) and **D,
gauge-set lock-held** (sketch level), with shorter notes on B and C.

**Pose convention.** main.js hands posePoint *hole dial − 35*, so Derek's
opening pose (grip 45 / hole dial 30 / vertical −15) is posePoint(45, −5, −15).
Their `proxy.pose()` defaults, and my first run, used posePoint hole 30, which is
hole **dial 65**. The results below are recomputed at dial 30; the dial-65
results are kept where they differ, labelled. Hole values in this file are dials.

Their files are unchanged. My checks and sketch are in
`explorers/who-moves-what/`. `wave2_lid_checks.py`, `wave2_lid_checks2.py` and
`wave2_drawer_check.py` use *their* proxy point cloud and collision test,
read-only, so the numbers are comparable with theirs. The points are posed with
this study's own posePoint port (their `pose()` changed to take dials mid-wave).
`sketches/w2-lid-reallocated.svg` shows the result.

---

## 1. Lid carrier (A)

### The difficulty, in this variant

As drawn (`lid-side-view.svg`, `lid_calc.py`), the lid has three things open,
and they interact:

1. **The fine stage is "left to others", yet it sits between the hinge and the
   gun.** The hinge location was proved for one pose (grip 45, hole 30,
   vertical −15). Every recipe change moves the gun relative to the hinge, and
   nothing yet says which recipes still escape.
2. **Per-tube height goes in "a Z slide in the fine stage" (A6).** That moves the
   gun relative to everything else in their own kit that references the rim: the
   H2 hanger's depth, the K4 overlap pointer, the K5 snip window, the camera's
   focus, and the park-gauge stickout.
3. **The seat triangle spans the tube.** The front vee is at x = −150 and
   rim + 70, on the operator's side. H2's stationary arm also has to come in from
   −X at about rim + 50 to reach the tube axis. So the lid's front beam, the
   front vee post and the hanger arm all want the same space.

### The assumptions behind it

(1) yaw is a rotation of the gun, and one pose stands for the recipe range;
(2) the gun side is the only place to take tube length; (3) the closed lid must
be gravity-seated with its centre of mass inside the ball triangle, with the latch
only adding margin.

### Repair: allocate each freedom to a body, by phase and rate

| Freedom | Body | Set in phase | Rate |
|---|---|---|---|
| lift-off, loading, inversion | hinge (theirs, x 200, rim + 60, ∥ Y) | 10 → 1, 11 | per weld/closure |
| location while welding | three balls + latch, **seat behind the station** | 5, 7–9 | every close |
| grip roll, hole tilt | printed recipe block on the lid | 0 | per recipe |
| yaw | **Y slide** on the lid, 1.08 mm per degree (tube symmetry) | 0 | per recipe |
| radial | X slide on the lid | 0 | per recipe (tube ID spread is small) |
| **height (tube length)** | **the work**: three fine screws under the rotator base, one knob | **2** (already hands-on with the indicator) | per tube, shared by both closures |
| spin | rotator | 7–8 | during the weld |
| stickout | their K3 | 0, after every snip | per snip |

**Check against their proxy and hinge** (`wave2_lid_checks*.py`, same point
cloud, same fine-step sweep, hole passed as dial − 35):

- **Their hinge search survives at the true pose.** Re-running their 80
  candidate lines × 2 directions at dials 45 / 30 / −15 leaves 16 of 160
  collision-free. All are parallel to Y, on the +X side, lifting up and back:
  the same family they found at dial 65. Their chosen hinge (x 200, rim + 60)
  still gives lift-clear at 20.5° and full-open at 72.5°. Those two angles are
  set by the wire tip, which starts at the dot in every pose, so they barely move
  with the recipe.
- **Recipe range, yaw by rotation:** every feasible pose with grip 30–60, hole
  dial 15–45 and yaw −30…+5 escapes. At dial 30, yaw ≥ +10 is not a feasible
  pose: the proxy's straight wire already sits in the lip at rest. At dial 65 the
  feasible range reached yaw +15, and every feasible pose there escaped too.
- **Yaw by the Y slide** (the gun keeps its room orientation; the dot lands on the
  seam 1.08 mm per degree away) escapes from **−25° to the +5° feasible limit**
  (−25° to +20° at dial 65). At −30° the wire passes within 1 mm of the lip in the
  first degree of opening. The reason: sliding rotates the *local tangent* away
  from the fixed hinge line, and the escape needs the hinge within ~25° of that
  tangent. That is a real limit on my wave-1 claim that "any X/Y carrier owns the
  yaw". It owns the yaw *for the weld*, but lift-off needs the hinge to follow the
  tangent. Beyond ~25°, use rotation-yaw on the lid, or put the hinge post on a
  turntable about the vertical through the dot.
- **Tube length ±3.2 mm** (the digest's OnlineMetals cut tolerance): it escapes
  whether height is taken by a lid Z slide or by the work. **Untaken, +3.2 mm puts
  the wire into the plate before the lid moves.** So height must be taken per
  tube; the question is only by which body. This is the same at both dials.

**Why height belongs to the work.** Tube length is a property of the work, so
absorb it there. Raise or lower the rotator so the rim returns to nominal, and
every rim-referenced part of their kit stays at its session setting: H2 depth, K4
pointer, K5 window, camera focus, park-gauge stickout, and the lid's own escape
clearance. The mechanism: three M10 × 1 screws replace the four printed feet,
with tips forming a ball-in-cone, ball-in-vee and ball-on-flat so the base stays
located in X/Y. A closed GT2 loop over three 20T pulleys makes one knob a pure Z
(1 mm per turn; a 100-division dial reads 0.01 mm). Representative belt: uxcell
1000-2GT-6 closed loop, Prime, $9.09 for 2, 86 ratings. Spring hold-downs through
the Ø10 clamp holes keep it from lifting without over-constraining it. It is set
in phase 2, when Derek already has the indicator on the tube.

*A rejected alternative:* stainless shims under the tube's rim in the nest
(Prime shim assortments exist). Raising the tube 3 mm leaves only ~1.5 mm of the
nest's 4.5 mm ID pilot engaged, so the shims go under the rotator base, not under
the tube.

**Seat behind the station** (sketch). Front ball pair at x = 170, y = ±110;
rear ball on a short tail at x = 300, behind the hinge; the latch at the rear
ball. The posts stand on the subplate *outside* the 300 × 250 rotator base. They
cannot stand on the base, because the base now rises with the per-tube Z. My first
try (front pair at x = 100) put the posts through the base. At the true pose their
centre-of-mass proxy sits at (−30, −108) mm, off the tube axis on the −Y side (it
was over the tube centre at dial 65). That is 200 mm outside the front pair. The
latch needs ≥ 33 N against gravity plus ~7 N for their 5 N cable tug at 177 mm,
using their 2.2 kg lid + gun estimate. At that latch the front balls carry 17 N
(+Y) and 38 N (−Y), so all three stay loaded. Their 60 N toggle latch gives ~1.5×
(~1.7× at dial 65). What
this buys: nothing of the lid crosses the tube or the −X side when closed. H2's
arm, the operator's hands and the loading column all have that side to
themselves.

**The fine stage on the lid.** For discrete recipes, the stack is lid → X slide
→ Y slide → recipe block → shell. For continuous angles, the protractor + stub
(`ideas/protractor-and-stub.md`) sits *inside* the slides: lid → X → Y → arc →
stub → shell. That order follows the digest's rule that a translation placed
between a rotation and the gun couples angle changes into the dot.

**Left open:** the real centre of mass and umbilical pull (they set the latch);
where the motor and ground towers actually sit relative to the x = 170 posts;
yaw beyond −25° by slide; the hold-down design for a base on three screws.

---

## 2. Gauge-set, lock-held (D)

### The difficulty, in this variant

The gauge sits on the rim round the nozzle and receives the shell. The
single-knob articulated arm is locked with the gauge seated. The lock moves the
arm tip "tenths of a millimetre or more", so the gauge takes that as strain, and
the gun springs back when the gauge comes out. The gauge also surrounds the
nozzle with the wire in the corner, so it has to split to come out past the wire.

### The assumption behind it

One gauge sets **all six** freedoms at once, per tube, and one general holder
must then hold all six in whatever pose it was given.

### Repair: split the pose by how often each part changes

| Part of the pose | Changes | Set by | Held by |
|---|---|---|---|
| roll, hole tilt | per recipe | the printed **recipe block** (D's "the gauge is the recipe", made literal and versioned) | the block itself |
| yaw, radial | per recipe | Y and X dials (yaw is 1.08 mm per degree) | the slides' own lead screws |
| height | **per tube** | a gauge **foot** on the shell | the work's Z screw (§1) |

- **No lock step, so no lock shift.** A lead-screw slide is held by the same
  thread that set it. Stopping turning *is* locking. An anti-backlash nut takes
  the thread slack, and any gib lock pushes perpendicular to the travel, not
  along it. A representative part: a manual linear stage with a 75 mm stroke,
  10 kg load and anti-backlash nut, Prime, $45.77, next-day, though only 15
  ratings. The category is common, the listing thin.
- **The gauge becomes a retractable foot, so it never passes the wire.** It has
  two pads on a 3 mm cam slide on the shell. A Z pad sits on the plate face at
  r ≈ 50 mm, 12 mm inboard of the bore, clear of the ~1.5 mm fillet. An X pad
  sits on the bore 3–4 mm above the plate. Both are on the free +Y side of the
  wire, 8 mm along the seam from the dot. The 0.5 mm curvature offset there is
  designed into the pad.
- **The rotator becomes part of the gauge sequence.** Index the table 22.5°,
  midway between tacks, so the pads land on clean corner. Turn the work's Z knob
  until the Z pad just drags (or a dial on the foot reads zero), and check the X
  pad. Retract the foot and index back to tack 1. Gauging at 22.5° and welding
  from 0° differ by at most 0.39 × eccentricity + 0.77 × ovality, about 0.05 mm
  at the procedure's 0.25 mm TIR if the runout is eccentric.
- **Branch D-m (measuring foot).** Put a dial on the Z pad instead of a hard
  stop and read it at all eight between-tack angles. Set the height to the mean
  (the best fixed setting for a gun that does not follow). The eight numbers are
  that tube's runout map, which is my `tube-carries-the-reference.md` 3b without
  a camera. Record them per tube with their K7.
- **D's original stays**, as the tool that *checks* a pose: drop the rim gauge
  on, see whether the shell mates. It is also a way to set a new recipe block's X
  and Y dials the first time.

**Left open:** calibrating the foot's pads against the dot (a replica-joint
puck, like work-as-datum's calibration puck, fits this). Also whether the wire
touch-off (their K3, if the welder shows conduction live) makes the Z pad
unnecessary. The wire touches along its own line, so it gives one combined X/Z
reading, not both.

---

## 3. Shorter notes

**B, gun stays, work travels.** Their drawer-path check was at dial 65. I
re-ran it at dial 30 in `wave2_drawer_check.py`, posing their point cloud with
this study's posePoint port. It **holds**: arriving from the station side
within ±20°, with a ≥ 10 mm drop and a 60 mm ramp, clears; ±40° does not. A purely
vertical final rise grazes the wire tip, which sits exactly at the bore radius.
Their diagonal ramp keeps the wall outboard of the tip until the last moment, so
the ramp is the right motion, not a convenience. Their `drawer_path.py` result
corrects my
`still-gun-moving-work.md`. I claimed the tube could slide out sideways whenever
the nozzle clears the rim, but the **wire tip sits in the corner**. The tube must
drop ≥ 10 mm and leave toward +X within ±20°. Their ramp-into-seats does exactly
that; my drawer needs it. Allocation from my side: set the three vee seats on a
plate carried by the cross-slide. The cross-slide then holds radial and yaw per
recipe, gib-locked, and the ramps and seats return the carriage to it every
time. Put per-tube Z on three screws between the carriage and the rotator, so
the ramps never change.

**C, rim-riding saddle.** C5 (plate tilt relative to the rim passes straight to
the dot) has a direct repair: move the height contacts from the rim top to the
plate face inside the recess. That is a tripod of ball transfers at r ≈ 47 mm and
r ≈ 30 mm, upstream, clear of fillet, tacks and ports, as in my 3a. The OD contacts
stay. C2 changes at the true pose. At dial 30 the centre of mass is not over the
tube centre but outboard, at (−30, −108) mm, beyond the wall on −Y. And the
scene's wire approaches from −Y, the gun's side. If the wire must be on the
arriving side, as the current per-weld sequence says, the arriving (cold) side is
−Y and the table turns counter-clockwise from above. Their sketch draws cw with
contacts on +Y. The mirror saddle is the one that matches the scene: contacts on
−Y, under the gun's lean, with the balancer taking the outboard weight. **Their C-h hand saddle is a better *first* experiment than
anything I proposed.** Run it on the same tube as my 3b mapped lap: C-h shows
whether contacts can locate the dot, and 3b shows whether following is needed at
all.

---

## 4. What their view does that my arrangements lacked

- **The phase states.** The gun must be *out of the way* (1–4, 11), *located*
  (7–8), *still* (9) and *returnable* (10 → 7). My allocation matrix had rates
  but no phases, and no tacking, plate holding, stickout or snip window at all.
- **The wire-escape constraint.** The wire tip must leave up and inward, so only
  a hinge behind the station, parallel to the tangent, works. My protractor + stub
  has no lift-off of its own (I gave it to a work drop). My still gun's sideways
  exit was wrong without a drop.
- **The wire tip as a second contact** at the moment of seating, stickout as a
  sequence number, and the interlock through the wire.

## 5. What transfers, and how allocation changes between phases

The same freedom has different owners in different phases. For the lid, as
repaired:

| | load / indicate | tacks | dry run / weld | stuck wire | gun away |
|---|---|---|---|---|---|
| dot height | **work Z knob** (set) | work Z (held) | work Z (held) | held | held |
| gun location | hinge (parked) | seat + latch | seat + latch | seat + latch | hinge |
| yaw, radial | slides (held) | held | held | held | held |
| roll, hole | block | block | block | block | block |
| plate depth | H2 / H1 set from rim | H2 | H2 (may stay) | — | — |

In one direction, yaw-by-slide, the seat behind the station and work-Z go to
their A and B. In the other, phase states and the wire-escape constraint come to
my still gun, protractor and rim rider. Combined proposal: **their lid, my
stack, work height set in phase 2, and a measuring foot that maps each tube while
setting its height.**
