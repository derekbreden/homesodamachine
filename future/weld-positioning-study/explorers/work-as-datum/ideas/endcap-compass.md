# A. Endcap compass — the gun rides on the plate it is welding

Status: wave 1, developed furthest. Sketch: `../sketches/endcap-compass.svg`.
Numbers: `../pose_geometry.py`, `../datum_budget.py` (both corrected in wave 2
for the scene's 35° hole-dial offset).

## Picture it (as it stands after wave 5)

A frame sits on the end plate being welded and carries the gun (or, in
later branches, only part of it) over the corner.

- **The datum.** Two 316 hex nipples are screwed finger-tight into the
  plate's two tapped ports. A seat bar drops over them and turns with the
  plate. A centre pin at the port-pair midpoint fixes the frame's x and y to
  the plate's own centre.
- **The original A2.**
  - The frame is a C-shaped ring inside the tube, open over the sector where
    the barrel comes down.
  - It rests on the plate face through three stainless rolling contacts
    (height and both tilts).
  - A pin in a fork on the rotator base holds its azimuth, the one freedom
    that doesn't matter.
  - A short compass leg rises from the ring's end to the gun's printed shell.
  - A spring balancer overhead carries the gun; the cables are
    strain-relieved to the room.
- **What moves.** The rotator turns plate, seat and nipples under the
  stationary frame. The frame follows the plate's runout and face tilt, so
  the gun's pose is fixed to this plate's face and centre, not to the room or
  the rotator.
- **Branches.**
  - **A3** (workspace-as-structure's *paddle compass*): the centre pin plus
    two rollers on the dot's radius, and a third foot on a room plane under
    the grip. The foot's height is the hole-axis dial.
  - **A4:** the frame carries only the gun's nose. That is
    `work-hung-suspension.md`.

**Sketches:**
- `../sketches/endcap-compass.svg` (A2, true opening pose, XZ elevation and
  plan);
- A3: `../../workspace-as-structure/sketches/paddle-compass.svg`;
- A4: `../sketches/work-hung-suspension.svg` and
  `../sketches/work-hung-suspension-D4.svg`.

**Major unresolved problems:**
- A2's light seat can't take the grip's lever: a hand on the trigger makes
  1.2–3.5 N·m against 0.09–0.35 N·m. A3 and A4 are the repairs.
- Radial precision is about ±0.19 mm (estimate), no better than an indicated
  axis.
- Whether 316 nipples may sit in the ports while welding (Derek).
- How the plate is held at its recess before tacking.
- Heat and reflected light on printed parts near the bore.

## The physical idea

The fillet is a flat circle on the end plate's own perimeter. A circle is drawn
most repeatably with a compass: a point fixed at the centre, a pencil at the
radius, and the paper turned under it. Here the rotator turns the paper; the
**point** is the end plate's own centre, found through its two tapped ports;
the **pencil** is the gun. The gun frame sits on the plate being welded and is
free only to spin about the plate's axis, which is the one freedom that does
not change the gun's pose relative to the corner (turning about the circle's
own axis just moves the dot along the seam).

What "fixed" is fixed to, deliberately:

| Freedom of the gun | Fixed to | By |
|---|---|---|
| Height, and tilt about both horizontal axes (3) | the plate's outer face — the fillet's own base | three stainless ball transfers rolling on the face, 35 mm from centre |
| Radial x, y (2) | the plate's centre = midpoint of its two ports | a centre pin on a seat carried by the ports |
| Azimuth about the plate axis (1) | the rotator base, loosely | a pin in a vertical fork slot |
| Weight | the room (overhead) | a spring balancer, leaving 10–20 N on the balls |
| Cable and wire forces | the room | strain relief near the gun, soft slack loop to the grip |

Consequences, if it works: the tube's radial and face runout, its reseating,
its length (OnlineMetals cuts to ±0.125 in = ±3.2 mm [Obs]), the squareness of
its ends, and the inversion for the second closure all drop out of the gun's
pose. The per-tube indicator step becomes unnecessary for the weld path. The
second closure is the same setup as the first. The pose becomes a property of
a part that sits on a plate, so it transfers to a second person, to a
replica plate on the bench (see "Calibration puck"), and to the next tube.

## Geometry around the actual gun and joint

Frame: +Z up, origin on the tube axis at the plate's outer face, dot at
(61.85, 0, 0), rim at z = +6.35.

From `pose_geometry.py` at the scene's opening pose (grip 45°, hole dial 30°,
vertical −15°; the proxy's 60° pitch and 16 mm clearance are illustrative).
*Corrected in wave 2: the wave-1 script passed the hole dial straight into
`posePoint`; the scene subtracts 35° first (`main.js`), so wave 1 placed the
gun 35° too steep and wrongly reported its body over the tube axis.*

- nozzle tip at r = 55.3, z = 11.4 (**5.0 mm above the rim**, 6.5 mm inboard of
  the bore); the beam runs 45° down, leaning toward the wall (radial
  component +0.45) and along the tangent (+0.54);
- the barrel climbs out toward −Y through the sector between azimuth ≈ −10°
  and −75°: r ≈ 49 at z = 26, 47 at z = 40, 55 at z = 68, leaving the bore's
  plan outline near z ≈ 80;
- the housing's centre sits at about (−29, −108, 143): **112 mm off the tube
  axis toward −Y**, outside the tube in plan;
- the grip base (cable exit) is at (−1, −234, 140), 234 mm from the axis.

So the tube interior below the rim is empty except for the beam and the last
few millimetres of wire; the column above the tube axis is clear at this pose
(it becomes crowded at steep hole dials — at dial 55 the barrel's back passes
within ~31 mm of the axis at z ≈ 150). What is **not** clear is the sector the
barrel descends through, −10° to −75°, at r ≈ 35–60 and z ≈ 20–70. The frame
ring (z ≈ 30–45, r ≤ 46) is therefore a **C, open over that sector**, and the
**compass leg** rises from the C's end near −80° to the shell's belly around
z ≈ 50–70 — still the shortest, stiffest link between datum and gun. With the
axis column clear, a second strut can also go straight up the axis to the
shell above the housing.

The gun's own weight now sits far off the hub (housing ~112 mm out). A seat
on the plate cannot carry it as a moment; the balancer must hang at the gun's
centre of mass, or a counterweight on the +Y side of the frame must bring the
combined centre of mass over the hub (§ Breaking it, 1).

The hole axis ("through the dot and both port centres") passes through the
hub. In this frame the hole-axis rotation can be a real hinge on the hub ring,
its pin line aimed at the dot, rather than an arc. The vertical-axis
rotation is the gun's heading relative to the compass radius and needs an arc
or a remote-centre linkage about the dot inside the leg. The grip axis ends at
the grip base, a physical point where a ball joint can sit. None of this has
to be built as literal joints (the pose can be a printed block — below).

### The hub, in two constructions

**A2 (preferred first build): pin centre + rolling plane.**

1. Two 1/4 NPT 316 hex nipples, finger-tight into the two ports (the ports are
   tapped and chamfered before any welding [Repo, step 1]). Each stands
   ~25 mm proud as a hollow Ø13.7 pin. Hollow matters: in the first closure
   the purge fed from below leaves through the top plate's ports; the nipples
   keep that vent open. They are the same alloy as the plate, 37 mm from the
   corner at their nearest.
2. A **seat bar** drops over both nipples — one round hole, one slot along
   the port line — and carries a centre pin (or a 60° centre socket) at the
   midpoint. It turns with the plate. Nothing slides on the workpiece.
3. The stationary **frame ring** (printed PET-GF, r ≈ 45) is centred on that
   pin by a short bronze bushing (plain bearing; x, y only, free in z and in
   small tilt), or by an MT2 live centre whose point sits in the socket —
   a preloaded triple-bearing part with listed 0.0002 in runout [Obs].
4. The ring rests on the plate face through **three stainless ball
   transfers** at r = 40, placed at 50°, 170° and 280° from the dot so none
   sits under the barrel's descent sector (−10° to −75°); the triangle's
   nearest side is 16.9 mm from the hub axis. They roll on the plate in
   circles; they define the plane.
5. A **fork arm** leaves the ring over the far (−X) rim to a vertical slot on
   a post from the rotator base: tangential restraint only.

**A1: rigid seat + moment bearing.** The seat bar is clamped to the nipples,
a vertical shaft at its centre, a preloaded pair of bearings (angular-contact
pair, tapered pair, or the live centre used for its own bearing stack) in the
frame. Tilt then comes from the bearing and the nipples' thread fit, not the
plate face; moments go into the plate. Simpler to picture, but it trades the
plate face (the fillet's own base) for thread and bearing play, and it sends
disturbing moments into a tube that stands loose in its nest (below).

## How it is used across a session

1. Rotator clamped anywhere on the bench — its position no longer sets the
   pose. The frame, gun and cables hang from the balancer, parked on the
   **calibration puck** (below).
2. Load the tube in the nest; seat the plate to its 6.35 mm recess with the
   rim spacer; tack. (Indicating the tube is no longer needed for the weld
   path; only the copper shoe's continuity check remains.)
3. Thread the two nipples in by hand. Lift the frame off the puck, lower it:
   the seat bar lands on the nipples, the pin enters the bushing, the balls
   touch down, the fork pin drops into its slot. Seconds.
4. Dry run: laser disabled, red dot on, pedal one revolution. A camera fixed
   to the frame ring on the free +Y side looks down across the interior at
   the dot, ~100 mm away. What it sees is the dot relative to this plate and
   this bore, not relative to the room.
5. Weld: gas, pedal, trigger once rotation is steady, carry ~20° past the
   first tack, release. The frame does not move in the room except by the
   plate's own runout (tenths of a millimetre).
6. Stuck wire: the gun is held where it stopped without anyone holding it;
   the cutter goes over the lip from the tangential side between the wire
   nozzle and the bead.
7. Lift-off: retract wire (the feeder has a pullback setting [Manual]), lift
   the frame on the balancer, set it on the puck, unscrew the nipples.
8. Second closure: invert, float, top plate, seat, tack, nipples, lower the
   frame. Identical to 3–7; tube length and the inverted seating don't enter.
9. Second person: the seat is symmetric about the port pair, so it cannot be
   put on wrong; the pose lives in the frame, not in anyone's hands.

### Calibration puck

A 25 mm ring cut from the same 5-in tube with a spare SendCutSend end plate
seated 6.35 mm down and tacked (or a printed replica with a real steel plate
insert), on a stand beside the rotator. The frame parks on it between tubes.
Because the frame references only the plate and bore, the puck reproduces the
weld geometry exactly: red-dot alignment, camera calibration, a changed pose
block, or an AI's dry-run series can all be done on the puck at any time,
without a tube in the rotator, and transfer unchanged to every real tube.
It also holds the gun safely between welds.

## Breaking it

**1. The loose tube and the light seat cannot take moments (the serious
one).** The ball seat holds only while the residual load's line stays inside
the ball triangle: with 5–20 N residual and ~17 mm from the hub to the
triangle's nearest side, the seat unloads a ball at **0.09–0.35 N·m**. A hand
pressing the trigger near the grip (grip base ~234 mm from the axis) with
5–15 N makes **1.2–3.5 N·m** [trigger force Unknown]; the gun's own weight,
if not balanced at its centre of mass, makes ~1.3–1.7 N·m (1.2–1.5 kg at
112 mm). The tube itself stands loose in the nest: its rim
lifts at roughly 0.9–2.5 N·m depending on closure and preload
(`datum_budget.py` §4–5). So a hand on the trigger, a cable yank or a stiff
conduit can rock the seat or the tube.
*Repair:* the arrangement demands a **force-quiet gun**. (a) The trigger is
closed inside the shell — a Bowden cable to a foot or hand lever (housing
reacts on the shell, inner pulls the trigger), a solenoid or a servo in the
shell; a bare hand squeeze is also internal, but an arm leaning on it is not.
(b) Umbilical and wire conduit strain-relieved to the room within
~0.3–0.5 m of the grip, with a soft loop respecting the 35 cm emitting bend
radius [Manual]. (c) Residual load raised by ballast on the ring (a 2 kg
steel ring adds ~20 N) if the loop forces turn out large. What stays
uncertain: the loop force at the grip, which nobody has measured.
*Branch:* if the gun cannot be made quiet, see `between-centres.md`, which
keeps the same datum idea but puts the gun on a rigid mast and forces the
work instead.
*Branch (wave 2, from the exchange with workspace-as-structure):* nose on the
work, tail on the workspace. The frame carries only a nose ring ~26 mm from
the dot; the gun's tail, with its weight and trigger reaction, rests on a
cradle on the room or collar ~220 mm back. Work motion reaches the dot as
~0.12× (`../exchange_calcs.py`). See
`../../../exchange/work-as-datum--on--workspace-as-structure.md` (L1a). To be
developed in wave 3 as Derek's suspension, with its tip loop on the work.

**2. Radial precision is not better than an indicated axis.** Estimated RSS
±0.19 mm (`datum_budget.py` §6): port-pair midpoint vs plate edge from the same
laser program (±0.1, estimate), the plate's 0.005 in radial slip seen at the
bore (±0.13), nipple/seat centring (±0.07), frame compliance (±0.05). An
axis-fixed gun on a tube indicated to acceptance sees ±0.125 radial. The
compass wins on height (the whole tube-length error — ±3.2 mm at cut
tolerance — and ±0.15 face runout) and on setup time, not on radius. The
residual radial error is a fixed eccentricity per plate, a once-per-rev
sinusoid; the camera would see it on the dry run. *Possible repair, not
developed:* a motorized radial fine stage in the compass leg, driven from the
camera during the dry run (overlaps a camera/AI explorer's territory).

**3. Heat and light at the hub.** Mean vessel rise after one bead is
~6–22 K (`datum_budget.py` §3); the plate centre lags that. PET-GF on
stainless balls at r = 40 is comfortable. Reflected 1080 nm light inside the
bore will find printed parts; a thin aluminium or stainless cover over the
ring and leg is cheap insurance [Est].

**4. Contact with the workpiece.** Nothing slides: the seat turns with the
plate; stainless balls roll on the face 22 mm inboard of the corner, clear of
the tacks (in the corner) and of the fillet. Iron pickup is avoided by using
all-stainless ball transfers; the procedure keeps pads stainless-only for the
same reason [Repo].

**5. Purge.** Covered by hollow nipples. The frame ring sits above them with
clearance so the vent stays open. The vented argon leaves at the plate's
centre inside the recess and may pool there; whether that helps or disturbs
top shielding is unknown.

**6. Tacking and the plate's hold.** The plate is a slip fit; the procedure
sets its depth with a spacer on the rim. How it stays at depth until tacked
is not recorded. The frame's residual load pushes the plate down, so the
frame goes on **after** tacking. Tacks themselves could be made with the frame
on if the spacer tool also holds the plate. *Needs Derek's practice.*

**7. Pose adjustment inside a small frame.** The compass fixes the reference;
it does not give the three rotations for free. For exploration: radial and
height by fine screws in the leg; hole axis as a hinge on the hub ring;
vertical axis and grip roll by arcs about the dot. For repeat work: a **pose
block** — a printed part that holds the shell at one (grip, hole, vertical)
setting, generated from the same transform the orientation scene uses
(`web/public/js/weld-position/pose.js`). Changing a parameter becomes
printing a block; the puck verifies it. Unresolved: how finely a printed
block reproduces an angle (0.25° at 62 mm is 0.27 mm at the leg).

**8. Stuck wire with the table still turning.** The wire drags the gun
tangentially; the fork resists (rigid in azimuth); the belt is backdrivable
[Repo]. The seat stays down if the drag is below the moment limit in (1);
the pedal release is still the real stop.

**9. Over-constraint.** Kinematic count: 3 (balls) + 2 (pin) + 1 (fork) = 6.
Balancer and cable loop are soft. The fork slot allows the ±0.15 mm runout
motion radially and vertically.

## Printed parts and bought hardware (representative)

Printed: seat bar, frame ring, compass leg / pose block, gun shell, fork arm
and post, calibration-puck stand, light shields' carriers.

Bought (see `../../../sourcing/work-as-datum.md`): 316 hex nipples (Prime,
next day, ~$3 each); all-stainless 1-in ball transfers (Prime, next day,
~$4 each; smaller sizes exist); MT2 live centre ($16–19, Prime, same day,
50–100+ bought/month) or a bronze bushing and dowel pin; spring balancer
1.1–3.3 lb class ($17 for two, Prime, next day — the next size up would be
needed if gun + frame exceed ~1.5 kg); Bowden trigger cable (bicycle brake
cable, commodity). Spare end plate for the puck from the existing SendCutSend
order [Repo].

## Contribution and open problems

Contribution: removes tube length, runout, reseating and inversion from the
gun's pose with a handful of cheap parts and a printed frame; makes the pose a
transferable object; gives a stationary replica target (puck) for dry runs and
AI experiments; drops the per-tube indicating step.

Open: (1) whether the gun can be made force-quiet enough — loop forces
unmeasured; (2) radial precision is only as good as the plate's laser cut and
slip; (3) how the plate is held before tacking; (4) the port chamfer size and
whether hand-tight nipples centre repeatably (±0.07 assumed); (5) gun mass and
CoM for the balancer; (6) whether argon venting at the centre matters.

Questions for Derek's observation: gun mass with shell; force at the grip
from the umbilical + conduit in the current routing (a luggage scale on the
grip while moving it ±5 mm would do); trigger force; how the plate stays at
depth before tacks; measured length spread and end squareness of tubes cut so
far.

---

## Wave 3 — objections from workspace-as-structure, and the branches they produce

Source: `../../../exchange/workspace-as-structure--on--work-as-datum.md`.
The original A2 above stays as written (with its wave-2 pose correction).

### Objection 1: the ring hits the nozzle at the true pose — accepted

At the scene's opening pose the nozzle and barrel pass r 38.8–40.2 from the
axis at azimuth −17° to −39°, z 15–45. My wave-2 correction had already
opened the ring over −5° to −75°. They add a second collision I missed:

- the nipples' hex turns with the plate and sweeps r 11–27 at z 0–7;
- a 1 in ball-transfer housing (Ø ~38) at r = 40 reaches in to r ≈ 21, so
  it would be struck once per revolution.

**Change:** plate contacts are small stainless wheels (695 size, 5 × 13 × 4 mm,
axle radial, rolling tangentially) or 5/8 in transfers, and nothing
stationary may reach inside r ≈ 30 below z ≈ 10.

### Objection 2: the support triangle is too small for the grip's lever — accepted

This is the objection that matters. The grip base is 234 mm from the hub at
the true pose, so trigger and cable moments (1.2–3.5 N·m) are 4–10× what a
three-point seat inside a Ø123 plate can hold (0.09–0.35 N·m). Repairing it
means answering which body carries the gun's weight moments. Two branches do
so.

**Branch A3 — paddle compass (workspace-as-structure's repair, adopted as a
branch):**
- A centre pin on my port seat sets x and y.
- Two rollers on the plate face lie on the dot's radius, P1 at (36, 0) and
  P2 at (−40, 0). They set height at the dot (1.34·P1 − 0.34·P2) and tilt
  about Y.
- One foot (P3) on a room plane at rim height, ~250 mm out under the grip,
  plus a fence, set the remaining rotation and azimuth.
- A ~20 N hold-down spring on the pin clamps the paddle to the plate with
  zero net force on the tube.

Because the roller contacts lie on the scene's hole axis (the radial line
through the dot at the plate face), the one rotation the room sets does not
move the dot. The inradius grows to ~33 mm, the weight rests (P3 takes
10–13 N), and a hand on the trigger adds load near P3 instead of lifting
anything.

What I add to it:
- **P3's height is Derek's hole-axis dial.** Raising P3 by 1 mm turns the gun
  0.23° about the line through the dot. A screw foot at P3 is therefore a
  hole-angle control with the dot fixed to first order: ±10° is ±43 mm of foot
  travel, coarse steps by printed spacers, fine by the screw. Their finding
  that tube length "becomes an angle" (0.23°/mm) is the same fact: a long tube
  turns the hole dial slightly, and the P3 screw takes it back if it matters.
- **The vertical-axis turn is a Y slide on the paddle** (the tangent-slide
  equivalence: 0.93° per mm). Only grip-axis roll needs a real arc or cradle in
  the shell mount.
- **The calibration puck** survives, as they note, in a second opening in the
  same room plane.

What stays uncertain:
- hand-tight nipples under 20 N of tension (my ±0.07 mm centring estimate was
  for no load);
- P1's clearance to the nozzle at steep vertical angles (5–8 mm at −30°);
- the need for a rim-height room plane, which means the table collar, the
  sled plate or a deck on the rotator base. The plain rotator on a bench has
  none.

**Branch A4 — the frame carries only the nose (see `work-hung-suspension.md`).**
The other answer to "who carries the weight moments" is Derek's suspension.
The room carries the gun at its base and back, and the plate-borne hub
carries only the nose loop's share (7–10 N at r ≈ 48). The moments on the hub
fall to 0.3–0.4 N·m about Y and 0.2–0.25 N·m about the dot's radius. A
three-wheel clamped hub (P1, P2 on the dot's radius, P4 at (0, +38) on the
side away from the barrel) holds that with no room plane at all, and the
tube sees ~0.4 N·m against its 0.9–2.5 N·m.

### Where I disagree, or would keep A2

- **The original A2 remains the right form for the calibration puck and for
  dry runs.** There the gun can be held by a balancer at its centre of mass
  and the red dot needs no trigger force.
- **The "force-quiet gun" requirement is not abandoned by A3, only relaxed.**
  A3 still passes cable lift into the P1–P2 line (up to ~10 N at the grip base
  holds, 20 N lifts P3). Their cable anchor behind P3 is part of the repair,
  not optional.
