# A. Lid carrier — the gun lives on a hinged lid that closes onto a stored pose

Sketch: `../sketches/lid-side-view.svg` (built from the orientation-scene proxy).
Calculations: `../calc/lid_swing2.py` (which hinges work), `../calc/lid_calc.py` (positions, moments).

> **Pose note (wave 3).** Numbers in the wave-1 text below were computed at scene hole **dial 65** (my proxy passed the dial straight into `posePoint`; the scene subtracts 35). Derek's opening pose is dial 30. The corrected numbers and the repaired branches are in the *Wave 3* sections at the end; dial-65 values are kept where they describe that reachable orientation.

## Picture it (as it now stands: branch A-r, true opening pose)

The gun sits in a printed shell on a light lid frame. The frame is hinged on a
horizontal axis parallel to the seam's tangent, 200 mm outboard of the tube axis
on the weld-station side and 60 mm above the rim. Between frame and shell sit an X
slide, a Y slide (yaw, 1.08 mm per degree) and a printed recipe block (roll and
hole angle).

- **Closed.** The lid does not rest on its hinge: the pins sit in tight slots. It
  rests on three steel balls in three vees on posts behind the station (a pair at
  x = 170, y = ±110; one at x = 300), pulled down by a latch at the rear ball. The
  gun's centre of mass lies outside that triangle, so the latch carries load.
- **Opened.** Lifting the handle swings the gun up and back along the tangent side,
  the only direction in which the wire tip leaves the corner without touching the
  lip. The lid goes over-centre at 71.5° and rests open at 88°.
- **Per-tube height.** The work takes it: three screws under the rotator, one knob,
  set against a rim flag on a seat post.
- **Umbilical and wire.** Clamped to the lid 300–400 mm from the butt; they cross
  the hinge in a plane perpendicular to its axis, so opening bends and never
  twists them.
- **Fixed to.** One subplate carrying the rotator and the seat posts.

Sketch: `../sketches/lid-side-view.svg` (true pose, parked at 88°, seats behind the
station).

## Major unresolved problems

1. **Real CG and umbilical pull.** They set the latch force, and the unlatching dip
   (tip drop = 3.6 × slot clearance).
2. **Tacking.** Hand tacks need the gun out of its shell mount. Fixture tacks need
   the stand-hung plate head.
3. **Stuck wire vs the three-screw base.** A yank can pull the vee foot out of its
   seat.
4. **Yaw by slide** escapes only from −25° to the +5° feasibility limit.
5. **Motor and ground towers** vs the seat posts (their positions are unknown).

## The physical idea

The session needs the gun in two conditions and almost nothing in between:
completely out of the way (loading, indicating, plate seating, unloading) and
precisely where it was last time (dry run, weld, stuck-wire snip). A chop-saw /
waffle-iron lid gives exactly those two states with one hand motion.

- A printed shell grips the gun along its length (Derek's established capability).
  The shell mounts to the lid through a small fine-aim stage. The stage holds the
  **recipe** (the pose about the dot); it is set rarely, locked, and every axis has a
  printed scale and a witness mark.
- The lid is a light frame (printed nodes + 2020 extrusion or printed beams) that
  pivots on a hinge **behind the weld station**: axis parallel to the tangent (±Y),
  200 mm from the tube axis on the +X side, 60 mm above the rim (298 mm above the
  bench on the current feet).
- Closed, the lid does **not** rest on its hinge. The hinge pins sit in short vertical
  slots; the lid's weight goes onto three hardened balls under the lid that land in
  three vee seats on the frame (Maxwell coupling: three vees at ~120°). The seat is
  what "closed" means. The hinge only guides the swing.
- Open, the lid swings up and back to ~80° and rests against a stop. Its centre of
  mass passes over the hinge at ~58°, so it stays open by gravity and closes by
  gravity once pushed back past 58°. A soft-close damper or small gas strut keeps the
  landing gentle (the manual: the head contains a vibration motor, handle it gently).

## Why the hinge must be where it is (geometry result)

I swept the proxy gun (opening pose: grip 45°, hole 30°, vertical −15°) about 80
candidate horizontal hinge lines with fine angular steps and checked every proxy
point against the tube wall, lip and plate (`lid_swing2.py`).

- **Only hinges parallel to the tangent, on the weld-station (+X) side, turning the
  gun up and back, are collision-free.** Every radial-axis hinge and every hinge on
  the far (−X) side drags the wire tip or nozzle into the 6.35 mm lip in the first
  degree or two. The wire tip sits in the corner; it must first move up and
  *inward*, and only a hinge behind and above the station gives that.
- Chosen hinge (x = 200 mm from axis, rim + 60): the wire tip's first motion is
  ~65° above horizontal, inward; the whole gun clears a lifted tube (r < 95 mm up
  to rim + 45) at **20.5°** and clears the full loading column (r < 95 mm up to
  rim + 320) at **72.5°**. A lower or farther hinge opens sooner (x = 250, rim + 20:
  column clear at 44°) at the cost of a longer lid.
- Parked at 80°: nozzle ~125 mm outboard of the axis and 430 mm above the bench,
  housing out over the +X side. The operator works the tube from the −X / −Y sides.

This is proxy geometry. The real gun scan and Derek's real pose move the numbers;
the conclusion "hinge behind the station, parallel to the tangent" follows from the
wire tip sitting in an inside corner and should survive.

## Operating it, phase by phase

| Phase | Lid | Hands / eyes |
|---|---|---|
| Open session | Parked. Stickout trimmed at the park gauge (session kit K3). | Gauge, welder screen |
| Load, indicate, plate, shoe | Parked; column open | Both hands on tube / indicator / hanger |
| Tacks | Either lid closed with the stationary swivel hanger (fixture tacks, kit K1-H2), or gun lifted out of its shell mount for hand tacks (second kinematic interface) | Tack angle on the console |
| Aim | Close lid (one motion). Per-tube Z: dial the measured tube length on the Z slide, or lower until the wire touches (kit K3 touch-off). | Camera / eye on dot vs corner |
| Dot dry run | Seated. Pedal, one revolution, laser disabled. | Dot track (camera on the lid) |
| Weld | Seated; trigger via the Bowden lever on the lid handle (kit K2) | Puddle and the 20° pointer (kit K4) |
| Stuck wire | Lid stays seated; snip through the snip window (kit K5) | Wire at the bead |
| Gun away | Lift the handle; lid rides to 80° | — |
| Unload / invert / next | Parked | Tube |

The second closure is the same pose: the joint is the same height above the nest
because both ends seat on the same rim datum and both plates sit 6.35 mm down. The
purge hose goes down the Ø90 passage and does not interact with the lid.

## Loads, what is fixed to what

Reference chain during the weld: gun → shell → fine stage → lid → three balls/vees
→ frame post → **common subplate** → rotator base (through its four Ø10 bench-clamp
holes) → ball race → turntable → nest → tube → plate. The subplate matters: if the
post and rotator clamp separately to the wooden VEVOR top, the top's flex and
creep sit inside the aim loop.

The loop needs to be *stable* more than stiff. During a weld nothing pushes on the
gun except the umbilical (constant, see below) and the trigger (routed off the
chain, kit K2).

Seat loads (masses assumed: gun 1.0 kg, shell + stage 0.4 kg, lid 0.8 kg; balls at
x = −150 front, x = +150 rear pair ±100 in y, seat plane ~rim + 70):

- Gravity alone: front ball ~8 N, rear balls ~7 N each.
- A 5 N sideways tug on the umbilical at the grip base (177 mm above the seat plane)
  shifts ball loads by ~±4 N. Gravity alone is marginal: a rear ball can unload.
- **Repair:** a toggle latch (or magnets) pulling ~60 N down near the triangle's
  centroid raises every ball to ~20–28 N. The latch is part of "close the lid":
  close, flip latch. It also stops a stuck wire on a turning tube from dragging the
  lid off its seat.

## Wire and umbilical

- The fiber's minimum bend radius while emitting is 350 mm (manual); stored 240 mm;
  twisting forbidden. That radius is the largest dimension in this whole arrangement.
- Clamp the umbilical and the wire conduit together to the lid ~300–400 mm from the
  grip butt. The gun-to-clamp section then moves with the lid as one rigid body and
  pulls on the gun with the **same** force every time the lid is seated. Only the
  section beyond the clamp flexes.
- Beyond the clamp, the bundle crosses the hinge region **in a plane perpendicular
  to the hinge axis** and hangs in a loop to the cart. Opening the lid then bends
  that loop (the grip base swings ~320 mm on a 250 mm radius about the hinge) and
  never twists it. Loop radius ≥ 350 mm in the closed state, ≥ 240 mm anywhere.
- The wire leaves the conduit through the gun's bracket; stickout is set at the park
  gauge (kit K3) so the tip lands ~1 mm short of the corner when the lid seats (see
  break A3).

## Trying to break it

**A1 — hinge and seat fight (over-constraint).** A hinge that also locates the
closed lid makes the pose depend on how it was closed. *Repair:* hinge pins in ~3 mm
vertical slots so the closed lid hangs only from the three balls. *Leaves:* the last
few mm of closing are unguided; the vees' flanks must capture a ball that arrives a
few mm off.

**A2 — preload.** See loads above: gravity alone lets a rear ball lift under a
modest cable tug. *Repair:* latch. *Leaves:* the real umbilical force is unmeasured.

**A3 — the wire tip is a second contact.** The tip arrives in the corner at the same
instant the balls arrive in their vees. Stickout 1 mm long means the wire hits the
plate first, bends, and can hold the lid off its seat; the closing path near the end
is down and outward at ~65°, so it also drags across the plate face. *Repair:* the
park gauge sets the tip ~1 mm short; after seating, jog the feeder forward until
conduction shows (kit K3), or let the weld start feed it in. *Leaves:* whether the
welder's start tolerates a 1 mm gap depends on its wire-feed delay and interlock
behaviour (question for Derek).

**A4 — closing shock.** A 2 kg lid falling 58° lands hard on a gun with a vibration
motor. *Repair:* damper; ball-and-vee seating is quiet if the lid arrives slowly.

**A5 — rim-bridge hanger vs closed lid.** A plate hanger that bridges the rim collides
with the seated gun as soon as the table indexes between tacks. *Repair:* the
stationary swivel hanger (kit K1-H2), or hand tacks with the gun lifted out of its
shell mount. *Leaves:* H2 needs its own depth reference to the rim.

**A6 — per-tube joint height.** The seat stores a pose relative to the frame; the
joint height moves with each tube's cut length (and end squareness). *Repair:* a
single Z slide in the fine stage, dialled to the measured length; or a wire
touch-off. *Leaves:* how much tube length actually varies (unmeasured).

**A7 — a second person grabs the wrong thing.** Lifting by the gun or by the stage
disturbs the recipe. *Repair:* a dedicated handle on the lid frame at the −X side
(which also carries the trigger lever); stage screws locked with witness paint.

**A8 — stuck wire with a free table.** The driver releases 10 s after a stop and the
table then turns by hand. A stuck wire ties the tube to the gun; a bump on the tube
pulls the wire. *Repair:* the latch holds the lid; snip immediately; optionally the
firmware keeps the driver enabled until the operator acknowledges (a proposal, not
a change).

## Parts (representative; see `sourcing/sequence-of-use.md`)

- Three 1/2 in chrome balls (PGN G25, Prime, 946 reviews) and six 6 × 30 mm
  stainless dowel pins as vee pairs in printed blocks.
- Toggle latch 4001, 304 stainless (Prime, 400+ bought/month).
- 50 N 10 in gas struts (Prime, $8.99/2) or any soft-close damper.
- Shimano brake cable and housing set (Prime, 1K+/month) + any bicycle brake lever for
  the trigger (kit K2).
- Printed: shell, stage, lid nodes, vee blocks, hinge slots, park gauge, handle.

## Contribution, open problems, assumptions

Contribution: a one-motion two-state carrier whose weld pose is stored mechanically,
with a proved-out (for the proxy) hinge location and a clear rule for the umbilical.
Open: fine-stage mechanism (left to others), per-tube Z method, tack method, real
masses and cable forces. Assumptions: proxy geometry; masses; the operator works
from −X/−Y.

---

## Wave 3 — the numbers at the true opening pose (hole dial 30)

Re-run with the corrected proxy (`calc/lid_swing2.py 30`, `calc/lid_calc.py`):

- **The hinge result stands.** The same 16 of 160 candidate lines are
  collision-free, all parallel to the tangent on the +X side, lifting up and back.
  The chosen hinge (x 200, rim + 60) still gives lift-clear at 20.5° and column-clear
  at 72.5°: both are set by the wire tip, which starts at the dot in every pose.
  who-moves-what's independent re-run agrees.
- **The gun body lies toward −Y, not over the axis.** CG proxy at (−30, −108) mm,
  375 mm above the bench (dial 65: (−2, −6), 423 mm). Body back at (−60, −144),
  424 mm. Grip base at (−1, −234), 372 mm.
- **Over-centre moves from 58° to 71.5°,** so the park angle goes from 80° to
  **88°**; 80° would hold open by only 8°. The closing moment is 4.05 N·m (masses
  assumed). The grip base swings 297 mm between closed and parked.
- **The wire rises at 38°, not 71°,** from the tip toward −Y. The closing path still
  ends down-and-outward into the corner, so A3 (the tip as a second contact) stands.
- **The wave-1 seat was wrong at this pose too.** With balls at x = −150 and
  x = +150, y ±100, the CG at (−30, −108) lies outside the triangle on the −Y side.
  The latch carries load in every layout.

## Wave 3 — branch A-r: freedoms reallocated by phase (from who-moves-what)

who-moves-what (`exchange/who-moves-what--on--sequence-of-use.md`) found three open
things interacting in A — the fine stage between the hinge and the gun, per-tube
height in that stage, and a seat triangle spanning the tube — and repaired them by
assigning each freedom to one body per phase:

- **Seat behind the station.** Ball pair at x = 170, y = ±110; rear ball at x = 300
  behind the hinge; latch at the rear ball. Posts stand on the subplate outside the
  rotator base. Their loads: the latch needs ≥ 33 N against gravity plus ~7 N for a
  5 N cable tug; with the 60 N toggle the front balls carry 17 / 38 N.
- **Recipe on the lid:** lid → X slide → Y slide (yaw, 1.08 mm/°) → recipe block →
  shell.
- **Per-tube height on the work:** three M10 × 1 ball-tipped screws (cone / vee /
  flat) replace the rotator's feet, tied by one GT2 loop to one knob (1 mm per turn).
  The rim returns to nominal, so every rim-referenced item in my kit keeps its
  session setting.
- **Yaw by slide escapes only from −25° to the +5° feasible limit** (−25…+20° at
  dial 65). Lift-off needs the hinge within ~25° of the *local* tangent.

**What I take:** all four. The seat behind the station frees −X for the H2 / plate
head arm and the operator. Height on the work is the right owner, because tube
length belongs to the tube.

**What the sequence adds to A-r (new):**

1. **Unlatching dips the gun into the work.** The CG is ~200 mm outside the ball
   triangle, so a closed, unlatched lid rotates about the front pair (x = 170). The
   hinge pin, 30 mm behind that line, rises into its slot; the wire tip, 108 mm in
   front, drops 3.6 × the slot clearance. *Repairs, together:*
   - squeeze-to-release: the latch is released by the same handle that lifts, so
     the hand takes the moment before the latch lets go;
   - slot clearance ≤ 0.2 mm above the seated pin (tip dip ≤ 0.7 mm);
   - stickout 1 mm short (A3), which covers what remains.

   *Sub-branch A-r2:* a gravity-stable triangle with one ball under the gun, e.g. at
   (−120, −160). The latch then only adds margin, but that post stands in the
   operator's and the hanger arm's space.
2. **Phase 2 needs a height reference, not just the indicator.** The indicator reads
   runout, not rim height relative to the station. Add a rim flag on one of the seat
   posts, reaching over the rim at a non-station angle (e.g. +45°). The step becomes
   "turn the knob until the rim touches the flag".
3. **A stuck wire loads the three-screw base.** Rough estimate:
   - A wire stuck while the table is still turning can pull ~140 N at the bead
     (digest), ≈ 8.7 N·m about the axis.
   - On a cone / vee / flat base, that torque is resisted where the vee foot's
     ball meets the vee flanks, at maybe 250 mm from the cone: ~35 N tangential.
   - That is comparable to a plausible 30–50 N of weight plus hold-down on that
     foot, so the ball could climb out of its vee.

   *Repair:* a stiffer hold-down at the vee foot, plus the existing rule to release
   the pedal first. After any stuck wire, the first indicator reading tells whether
   the base re-seated. *Leaves:* real preload at the feet.

**Uncertain after A-r:** real CG and umbilical pull (they set the latch); where the
motor and ground towers sit relative to the x = 170 posts; yaw beyond −25° (needs
rotation-yaw or a hinge post that turns about the vertical through the dot).
