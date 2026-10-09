# Table opening + countertop gantry (Derek's branch, developed as he described it)

## Picture it (as it now stands)

**Derek's original:** a hole in a bench top; the rotator below on a shelf held
at four corners; a gantry at countertop height above; the gun in a fitted
shell, tangent to the circle.

**As developed here:**

- **The opening.** A Ø150–160 hole in a 72 in VEVOR bench, ~650 mm from its
  −Y end near the front edge. In the repaired variant, a drop-in collar plate
  sits in a larger hole.
- **Below the top.** Four posts hang from the top (or collar) and carry a
  shelf on four belt-linked Tr8×2 screws, with a lock.
  - The existing rotator is bolted to the shelf, so the tube's rim is flush
    with the table surface and the joint sits 6.35 mm below it.
  - The box's front face is open.
  - Nothing is under the shelf, so the purge hose rises straight up.
- **Above the top.**
  - Two MGN12 rails run along Y either side of the hole.
  - A beam along X rides them 20–40 mm above the table, beside the hole
    (y ≈ −190).
  - An X carriage on the beam holds a printed pose saddle, and the saddle holds
    the gun's shell.
  - The gun body sits 70–200 mm above the table on the −Y side. Only the barrel
    and nozzle cross the mouth; the nozzle is ~5 mm above the rim.
- **Cables.** The umbilical and wire conduit leave the grip butt ~133 mm up,
  heading −Y at 30°. They clamp to the carriage and bend at R ≥ 350 off the
  bench end to the cart.
- **Motions.**
  - X (carriage) sets the dot across the seam.
  - Y (gantry) is the plan angle, 0.93° per mm.
  - Z is the shelf.
  - The two rolls live in the saddle.
- **Loads.** Gun weight goes to the carriage and beam; the tube and rotator go
  to the shelf and posts.
- **"Fixed" is fixed to:** the bench top in the original; the collar plate in
  the repaired variant.
- **Tube change:** drop the shelf ~70 mm and slide the tube out the open face;
  the gun never moves.
- **Branch T-W1 (work-as-datum):** a spring plunger on a collar arm drops into
  a countersink on a port seat. The shelf is cranked to the dial's zero, which
  takes tube length and runout out of the pose.

**Sketches:** `../sketches/table-opening-gantry.svg` (plan and elevation, gun
proxy at the true opening pose). The collar is in `../sketches/drop-in-collar.svg`.

**Major unresolved problems:**

- The loop runs through the wood in the original; the collar repairs it.
- Per-tube corner height: the crank repeats the nest, not the corner. T-W1 or
  a camera fixes it, but needs nipples in the ports at weld time (Derek).
- Angles are discrete: named printed saddles.
- Stuck-wire drag along Y.
- The bench's crossbars under the opening.
- Gun mass and cable force.


Sketch: `../sketches/table-opening-gantry.svg` (plan + elevation, gun proxy
projected from the scene's opening pose). Geometry script: `../geom.py`.
Rough numbers: `../loop_calcs.py`.

## The idea as Derek put it (kept intact)

A hole in a bench top. Under it, "something screwed into the bottom of the
table, maybe metal, maybe motorized, maybe manually height adjusted", an
upside-down box open on at least one face for loading, carrying the existing
rotator on a height-adjustable shelf held at **four corners**, with **no second
shelf beneath it**. Above the hole a **gantry at countertop height**: the whole
gantry slides in one horizontal axis on rails on both sides of the hole; the gun
slides along the gantry in the other. The gun sits in a **fitted printed shell,
gripped along its length**, its tip near countertop height, and **tangent to the
circle**. Derek's reason: it doesn't solve XYZ, it shrinks the distance from a
built-in starting point to the fine-tuned pose.

Everything below develops that; branches are labelled as branches.

## Where the gun actually is when the rim is at the table surface

From the scene proxy at the opening pose (grip 45°, hole dial 30°, vertical
−15°) [Agent proxy of the manual drawing; ±10–20 mm]:

| Part | Relative to the dot (x radial, y tangent, z up) | Above the table (rim flush) |
|---|---|---|
| Nozzle tip | x −7, y −9, z +11 | **~5 mm above the rim**, inside the bore in plan |
| Lowest gun point outside the bore | — | ~69 mm (lens section) |
| Housing | x −143…−40, y −161…−55, z 79…208 | 73–201 mm |
| Grip | x −95…−42, y −236…−111, z 104…160 | 98–153 mm |
| Grip base (cable exit) | x −63, y −234, z +140 | ~133 mm, ~233 mm out along −Y |
| Grip axis (dot → cable exit) | 279 mm long, 30° elevation, 15° off the tangent in plan | |

What that means for the workspace:

- With the rim flush with the top, **the whole gun body sits over solid table**,
  on the −Y side of the opening, 70–200 mm above it. Only the barrel and nozzle
  cross the mouth. So the opening only needs to pass the tube: **Ø150–160 mm**
  is enough. The gantry beam doesn't have to span the hole at all — it can run
  along X beside the hole at y ≈ −190, directly under the gun body, with the
  Y rails on either side of the hole (x ≈ ±205). That is the countertop-height
  gantry, with the gun sitting on it rather than hanging from it.
- Roll 45° swings the housing inward over the tube's centre line (world x from
  −81 to +22): the gun body is *above the middle of the tube*, displaced along
  −Y, not beside the far wall.
- Tube OD rim at x = ±63.5; the nozzle tip is 5 mm above the rim plane. A
  purely horizontal move of the gun along −Y can pull the nozzle out over the
  rim with ~5 mm clearance at this pose, ~1 mm at hole dial 10°. Lower the shelf
  a few mm first.

## What each motion does at the dot

Three findings that hold for every arrangement in this study (they come from the
tangent pose, not from the gantry):

1. **X (along the gantry) is across the seam.** It moves the dot between wall
   and cap 1:1. This is the axis that deserves fine resolution and stiffness.
2. **Y (the gantry on its rails) is along the tangent, and is equivalent to a
   vertical-axis turn.** Sliding the gun (or the work) dy along the tangent at
   fixed heading lands the dot at a point of the circle whose tangent is rotated
   atan(dy/R) = **0.93° per mm** (R = 61.85 mm bore radius); the radial error is
   only dy²/2R (1 mm → 8 µm; 5 mm → 0.2 mm; 16 mm → 2.1 mm, which X corrects).
   Because the tube turns anyway, *where* on the circle the dot lands does not
   matter. So a Y slide plus a small X correction **is** the vertical-axis
   control, with no rotary joint through the dot. It is also the axis whose
   errors hurt least — the natural retract axis.
3. **Z (the shelf) moves the dot along the beam.** In the opening pose the beam
   runs 45° down and 50° off the radial in plan, so raising the cap face 1 mm
   moves the dot 0.64 mm across the seam and 0.75 mm along it (toward the
   nozzle), and changes standoff. Z matters about two-thirds as much as X for
   the across-seam position in this pose; with less grip roll it matters less.

So the gantry's two axes are not equal: **X precise, Y coarse with a
repeatable stop**, Z fine on the shelf.

## The arrangement, concretely (one representative build)

**Above the top (the gantry):**
- Two MGN12 rails (400 mm) along Y at x ≈ ±205, screwed to the top (or to the
  collar — see `drop-in-collar.md`).
- A beam along X across them (2040 V-slot, or a 1 in aluminium square tube with
  a third MGN12 on its top), 20–40 mm above the table.
- X carriage on the beam, driven by a Tr8×2 screw with a dial knob (2 mm/turn,
  a 50-division printed dial = 0.04 mm/div) or a 0–25 mm micrometer head
  pushing against a spring. Clamp after setting.
- Y: push by hand to a hard stop (a screw stop with a lock nut on each rail), and
  a rail clamp. A second "retract" stop 150–200 mm back along −Y.
- On the carriage, a **pose saddle**: a printed block whose top surface holds
  the shell at one set of grip/hole angles. Angles are set by which saddle is
  on the carriage (a labelled family: "G45-H30", "G60-H30" …) and trimmed by
  shims. This is where the grip-axis and hole-axis rotations live in this
  branch. A continuous version is an arc guide centred on the dot; that belongs
  to the mechanism explorers and can drop onto the same carriage.
- The shell grips the gun along its length and carries: the saddle interface
  under the housing/grip, the cable clamp just beyond the grip butt (so cable
  tug goes into the carriage, not the aim), the wire-guide bracket, and a
  **trigger actuator that reacts against the shell itself** (a lever or servo
  pressing the trigger with its reaction inside the shell, so the trigger force
  never loads the gantry — a hand pressing the trigger of a supported gun
  pushes it off its pose, then lets it spring back at release).

**Below the top (the box):**
- Four posts at the corners of a ~320 × 370 mm rectangle, hanging from the top
  (or the collar), shelf ~12 mm aluminium or plywood with a Ø100 hole under the
  rotator's Ø90 purge passage. The rotator bolts to the shelf through its four
  Ø10 clamp holes, with the shelf top 238 mm below the table surface so the rim
  sits flush (rotator rim 238.4 mm above its feet).
- Height: four Tr8×2 screws, one per corner, tied by a closed GT2 belt to one
  crank (2 mm/turn, self-locking) — the 3D-printer "four-Z" layout. The posts
  guide; the screws only lift. Rough stiffness: four 1 in × 1/8 in aluminium
  tube posts, 300 mm, fixed at the top and guided at the shelf: ~2,900 N/mm
  sideways (10 N → 3 µm). Four bare Tr8 screws as posts: ~70 N/mm
  (10 N → 0.14 mm). Guidance and drive must be separate parts.
- A shelf lock (four clamp screws against the posts) makes the shelf's position
  a clamped state rather than a screw-thread state. Precision is needed at the
  moment of locking; recheck the dot after locking.
- The open face of the box faces the operator. The rotator is turned so its
  motor tower and ground tower sit on the sides, clear of that face.

**Cables and wire:**
- The umbilical and wire conduit leave the grip butt along the grip axis:
  heading −Y, 30° up, 133 mm above the top. Continue them straight ~250 mm,
  clamp them to the carriage (or collar), then one ≥ 350 mm-radius bend (the
  fiber's emitting minimum) off the −Y end of the bench down to the cart parked
  there. The opening therefore sits ~650 mm or more from the −Y end of the
  72 in bench, near the front edge for reach.
- A printed saddle with a 350 mm radius at the bench end makes that bend a
  fixed shape rather than a hanging loop.

## How it is used

**Setup (once per pose):** shelf to the recorded height; pose saddle on; gun in
shell on the saddle; Y to its stop; X by dial until the reference dot sits in
the corner; lock; check the dot through one dry revolution. Record X, Y, Z,
saddle name.

**Tube change without touching the gun (the payoff):** crank the shelf down
~70 mm so the rim clears the underside of the top (30 mm top + ~20 mm lift off
the nest + margin), lift the tube off the nest, slide it out of the open face.
Reverse with the new tube; crank up to the recorded number; lock. The gun,
wire and umbilical never move between tubes, so the pose is repeated by
construction, and Z is repeated by a screw approached from one direction.

**Indicating runout:** the OD near the working end is inside the table
opening, where the procedure's indicator can't reach it. Two options: indicate
with the shelf dropped (tube in the box, magnetic base on the NEMA 23 as now),
then raise — the tube does not move in the nest when the shelf moves slowly; or
indicate the **bore lip from above** with the indicator base on a steel collar
(`drop-in-collar.md`), which measures the actual weld surface in the gun's own
frame.

**Purge, both closures:** the shelf is open air below (no second shelf), so the
argon hose comes straight up through the shelf hole and the rotator's Ø90
passage — to the open held end for the first closure, to a lower-plate port for
the second. With side loading, connect the hose after the tube is in (reach up
through the shelf hole); the hose never has to be threaded through the rotator
bore while the tube slides sideways.

**Inverted second closure:** same rim height (the nest seats the rim either
way). The float rod is captive inside and nothing stands above the top plate
([Repo] pressure-vessel.md step 5), so nothing crosses the gun's path.

**Tacking:** the 8 tacks could be placed with the gun in the saddle, indexing
the table 45° at a time by the console's degree readout.

**Stuck wire:** the head stays put (it's on the carriage); the snip goes in from
above through the mouth, which is at countertop height — easy to reach.

**Second person:** they see the gun already posed, a crank with LOAD and WELD
marks, and the pedal. Loading needs no touch of the gun. This is where the
arrangement is strongest for transfer.

## Breaking it

1. **The loop runs through the wood.** Gun → saddle → carriage → beam → Y rails
   → **30 mm rubberwood top** → posts → shelf → rotator → tube. A 200 N lean on
   the top near the opening, on a 600 mm span of 30 mm hardwood, gives an
   end-slope ~0.7 mrad; with ~400 mm between where the gun is held and the
   rotator base, that is ~0.27 mm of relative motion (range 0.1–0.5 mm with the
   opening weakening the strip) [Agent estimate]. Wood also swells and creeps.
   Repair: close the loop in one stiff frame that rests on the top —
   `drop-in-collar.md`. Leaning then tilts gun and tube together.
2. **The gantry is only loaded by static weight.** Nothing moves during a weld
   except the tube, so sag of beam, wheels or rails is present at setup and
   seen by the dot; it doesn't need to be tiny, only unchanging. What changes
   during a weld: trigger force (repair: actuator reacting inside the shell),
   cable drag (repair: clamp at the carriage, fixed saddle at the bench end),
   wobble-motor vibration (unknown amplitude; stiffer is better), a person
   touching the gantry (collar).
3. **Stuck wire drags along the tangent.** A wire frozen in the puddle is carried
   by the tube surface along ±Y. Pulled away from the gun (+Y), it drags the wire
   guide and gun along Y — which is the carriage's Y rail. A plain stop only
   holds one direction. Branch A: clamp Y hard (the wire kinks or the rotator's
   backdrivable belt yields, which the rig already relies on). Branch B: make Y
   a **breakaway detent** (ball-and-spring or magnet at the stop, releasing at
   ~20–30 N) so the gun slides along the insensitive axis and reseats on the
   stop afterwards. The tangent pose puts the drag on the axis that tolerates it.
4. **Top loading vs. side loading.** Top loading keeps today's procedure but
   needs the gun to leave: slide Y back 150–200 mm to a retract stop. Returning
   to the stop repeats heading to ~0.05° per 0.05 mm and the across-seam
   position to microns, because Y is the insensitive axis. Side loading keeps
   the gun untouched but needs ~70 mm of shelf travel per tube change (35 turns
   of a 2 mm-lead crank; faster with a motor or a 4-start Tr8×8 plus a lock).
   Both stay open.
5. **Tube length varies, and the shelf references the bottom rim.** The nest
   seats the tube's far end, so a tube 0.5 mm long puts the dot 0.5 mm high —
   0.32 mm across the seam in the opening pose. Either record the dot per tube
   and trim Z with the crank (fast, since Z is only a screw), or touch the top
   rim against a stop on the collar and back off a fixed amount (a drill-press
   depth-stop habit). The cap's seat depth varies too; only the dot sees both.
6. **The nozzle is 5 mm above the rim.** Radial runout (≤0.25 mm TIR accepted)
   and face runout (≤0.30 mm) don't reach it. A bent lip or a proud tack
   could; the shelf can drop a few mm for a dry revolution check.
7. **Operator's view:** from the front, the nozzle tip sits 7 mm in front of and
   11 mm above the dot, slightly to the gun side; it can hide the dot. The
   corner itself is visible from almost anywhere on the near side (the recess is
   6.35 mm deep across a 124 mm bore — the line of sight only has to clear the
   near rim, 3° above horizontal). A camera from the +Y side, opposite the gun,
   sees the dot clearly.
8. **Heat:** the top is at the rim, 6 mm above a weld. A wood or printed edge at
   the opening needs to stay back from the tube (a 15–20 mm gap on the Ø160
   opening) or be lined with sheet metal.

## Branch kept beside the original: the edge version

Derek: with a one-sided support "we might as well just do all this on the edge
of the table". The collar can overhang the bench edge as a notch instead of a
hole: four posts still at four corners, two of them hanging from the part of
the collar plate that projects past the edge. The tube then slides out through
the notch without dropping below the top (it only has to clear the nest), and
three sides are open for access and cameras. The cost is a cantilevered collar
(its stiffness now matters) and the gun body sitting over the notch side.

## Contribution

- Tube changes and both closures without touching the gun, if loading is by
  shelf drop. That is the strongest repeatability property found so far.
- A clear allocation: X precise on the gantry, Y coarse (it *is* the
  vertical-axis angle), Z on the shelf, angles in a named printed saddle.
- Countertop ergonomics: mouth at bench height, snip and view from above.

## Unresolved / rests on

- Gun mass, CG and umbilical stiffness [Unknown] set how much a trigger press or
  cable change moves anything.
- Whether the VEVOR top's crossbars leave room for a Ø160 opening ~650 mm from
  the end near the front edge [Derek to look].
- Whether the tube lifts off the nest cleanly with the shelf lowered (the OD
  guide height, the ground shoe's preload) — needs the real nest.
- Angles are discrete in this branch (saddle family). A continuous angle sweep
  for the automated-setup vision needs an arc guide or a different stage.

---

## Wave 3: work-as-datum's objections, and the branches they produce

Source: `../../../exchange/work-as-datum--on--workspace-as-structure.md` §1.
The arrangement above (Derek's branch as developed in wave 1) is left as it
was; the branches below change it.

### The objection: the crank repeats the nest, not the corner (accepted)

The payoff line above, "the pose is repeated by construction, and Z is
repeated by a screw", is true for the **nest**. Three things between the nest
and the corner are not repeated:

- **Height:** corner = nest + tube length − 6.35 mm (plus the plate's seating).
  - OnlineMetals' cut tolerance is ±3.2 mm.
  - At the opening pose, a corner 1 mm high puts the dot 0.64 mm onto the
    plate and moves focus 1.4 mm; 1 mm low puts the dot 1 mm up the wall.
- **Radius:** the rotator axis plus the tube's runout on it.
- **Tilt:** the plate face's tilt relative to the spin axis.

Break 5 above named the length but proposed re-finding the dot per tube, so
the pose was being repeated by measurement, not by construction. The branch
below makes the line true at the plate.

### Branch T-W1 (work-as-datum's W1, adopted): a centre on the plate, hung from the collar

**What it is:**

- **On the work:** two 316 hex nipples go finger-tight into the plate's two
  ports, and a seat bar over them carries a 90° countersink at the port-pair
  midpoint.
- **On the collar:** an arm comes from the collar's free +Y edge to the tube
  axis, 40–60 mm above the plate. It carries a vertical spring plunger: Ø12
  shaft in a flanged LM12 bushing, spring, 1/2 in hardened ball, and a dial
  reading the shaft.
- **Per tube:** crank the shelf up until the ball seats and the dial reads
  zero, then lock the four post clamps.

**What it changes here:**

- **Tube length and the shelf's crank position drop out of the height.**
- **Radial runout drops out.** The ball-in-cone forces the plate centre onto
  the plunger axis, which is fixed to the collar. The tube pivots in its nest,
  with the M3 adjusters backed off.
- **The loose tube is clamped** into the nest by the 30–50 N preload.
- **Unloading is unchanged.** Side loading still works: the ball parts from the
  seat as the shelf drops, with ~21 mm to spare (their check).
- **Per-tube routine:** load, crank to the dial's zero, lock, one face-tilt
  reading. The indicator run for radial runout leaves the weld path.

**Additions from this side:**

1. **Let the plunger turn with the seat.** A linear ball bushing allows
   rotation, so the ball rides round with the countersink instead of sliding
   in it under 30–50 N. The dial then reads a rotating shaft end, which is
   fine for a flat anvil.
2. **The arm fits.** At the true opening pose the column over the axis is open:
   every gun surface is ≥ 38.8 mm from the axis. At 40–60 mm above the plate,
   the gun's nearest surfaces are at r 39–45, azimuth −17° to −61° (the gun's
   quadrant). An arm arriving from +Y crosses nothing. The camera, also on +Y,
   goes toward +X so its sight line to the dot doesn't cross the arm.
3. **Crank-to-zero is a closed loop a motor can run.** Use a NEMA 17 on the
   shelf's belt loop plus a 0.01 mm digital indicator with a data port (RS232,
   ~$24 Prime). That is the automated per-tube height set Derek's vision wants.
4. **What remains:**
   - **Face tilt:** point the collar's magnetic-base indicator at the plate
     face ~10–15 mm inboard of the corner for one reading per tube.
   - **Plate-centre accuracy:** the port-pair centre vs the plate edge
     (±0.19 mm RSS, their estimate) stays as a once-per-revolution sinusoid,
     which the camera sees.

**Uncertain:**

- whether nipples may sit in the ports during the weld (Derek);
- how the plate is held at depth before tacking (the seat goes on after
  tacks);
- whether the tube pivots cleanly within the nest's pilot/guide clearances
  under 30–50 N;
- whether the copper shoe's side preload on the OD (a few N) matters once the
  top is held.

### Branch T-W1b (their sprung shelf against a rigid centre): recorded, not preferred

**What it is:** the plunger becomes a rigid stop. The shelf carries the rotator
on soft springs (~4.7 N/mm total, ~30 mm precompression, 30–60 N preload
across the whole length range). The crank always goes to one WELD mark.

**Gain:** Z and radius stay referenced to the collar *during* the weld, not
just at setup, and no per-tube crank is needed.

**Why I prefer T-W1:**

- **The rotator is no longer on anything rigid.** Belt reaction, the copper
  shoe's preload, the pedal-driven start and a hand on the machine all act on
  a spring-mounted body. It needs vertical guidance and a torque restraint,
  both new parts in the loop.
- **Its main gain disappears with a motor.** With the motorized crank-to-zero
  above, the no-crank advantage goes away, and T-W1 keeps the rotator on four
  stiff posts.

**Where W1b still wins:** a purely manual station where cranking every tube is
the burden.

### Also usable here

The paddle compass (my wave-2 branch of their compass,
`../../../exchange/workspace-as-structure--on--work-as-datum.md` §1) puts its
room foot P3 and fence on this collar. The gun then rides the plate at the
dot's radius while its weight, trigger and cable loads land on the collar.
With T-W1 also fitted, the paddle's residual roll (0.23° per mm of tube
length) disappears too.
