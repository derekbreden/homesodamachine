# Tilt cradle + escape rail: incline the work axis, let the gun ride one straight rail

## Picture it (as it now stands, after waves 3–5)

**What sits on the cradle.** The existing rotator stands on a U-shaped cradle
that pivots on two pillow-block trunnions. The pivot line is the station's
tangent through the laser dot. On the cradle, besides the rotator:
- the tube, **band-clamped to the turntable** (wave 5);
- the plate head, with its rim flag;
- a column rising from the cradle's −Y side plate, on the station side.

**What moves.** A quadrant and pin set the tilt τ, read by an inclinometer:
- **τ = 0** is today's upright tube;
- **τ ≈ 32.5°** makes the fillet nearly flat and lays the gun flat in the
  vertical plane through the tangent.

Because gun and work tilt together, the tilt changes gravity's direction
relative to the joint and nothing else. The rotator spins the tube as today.

**The escape rail.** It runs up the column along the corner's escape direction,
and is vertical at 32.5°. Its carriage drops by its own weight (plus a spring)
onto a **fixed** ball-in-vee stop. Lifting it 43 mm clears the gun from the tube
for every feasible recipe.

**Recipe settings, each changing one thing** (branch T-b1, one-knob-one-parameter):
- **S:** a small stage along the beam (standoff only);
- **A:** a stage horizontal and radial (moves the dot between wall and cap);
- an optional work-angle pivot about the cradle's own axis (T-g);
- a recipe block for coarse roll and hole;
- yaw on the column's Y slide.

S, A and the pivot are one-knob-one-parameter's printed flexure head.

**Where the gun and wire sit.** The gun lies on its side on a vertical plate,
the wire guide under the barrel, and the umbilical leaves horizontally in the
gun's plane.

**What carries and what fixes.** The weight goes down the rail to the stop, and
the cable goes to a trolley or loop above. "Fixed" is the cradle: every
locating chain closes on it, and the trunnions carry no precision.

**Sketches:**
- `../sketches/s6-tilt-cradle-escape-rail.svg` (true opening pose at τ = 32.5°:
  view along the tangent, and view from +X; drawn before T-b1, so it shows the
  stop but not the S/A stages);
- the flexure head: `../../one-knob-one-parameter/sketches/flexure-trim-head.svg`.

**Major unresolved problems:**
- **The tilted weld process.** The pool attitude, the lip and trailing shielding
  (buoyancy matters there, not at the pool) and the back purge are all
  unmeasured. Only τ = 0 has qualified-practice history.
- **Staying clean under tilt.** The unclamped first-closure tube tips at about
  30.5° and slides from about 17°, and the turntable lifts at 30–40°. The band
  clamp and a preloaded catch are the repairs. A two-gauge tilt walk test
  measures what remains.
- **The real gun's mass and centre of mass**, and the rotator's real centre of
  mass.
- **Heat at a column** 62 mm from the weld.

## The original (wave 3), kept as written

**Allocation in one line:** a new work-side freedom, tilting the tube axis,
goes to an isocentric cradle that pivots on the station's tangent line through
the dot. Tilt is a **process knob**: it changes only gravity, because the gun
rides on the cradle too. Lift-off, loading and docking go to **one straight rail
fixed to the work along the corner's escape direction**. At a tilt of about 32°
that rail is vertical, the gun lies flat in a vertical plane, and its own weight
seats it on its stop.

Sketch: `../sketches/s6-tilt-cradle-escape-rail.svg` (left: view along the
tangent; right: view from +X). Numbers: `../tilt_calcs.py` (poses are scene
dials; opening pose grip 45 / hole dial 30 / vertical −15).

**This is a weld-process change as well as a positioning one.** Tilting moves
the puddle from today's horizontal fillet (2F) toward a flat fillet (1F). What is
known and unknown about that is set out in "Process" below. τ = 0 is exactly
today's geometry, so today's process stays one setting of the knob.

## What tilting does (tube-frame recipe fixed; the work and gun rotate together)

Tilt τ about the station tangent (Y through the dot); + tips the tube's open end
toward the station side:

| τ | fillet bisector from vertical (0 = 1F flat, 45 = 2F) | beam from vertical | beam out of the vertical tangent plane | pistol's side vs that plane |
|---:|---:|---:|---:|---:|
| 0 (today) | 45 | 44.6 | −26.9 | 39.2 |
| 20 | 25 | 34.5 | −10.5 | 20.4 |
| 30 | 15 | 32.5 | −2.1 | 12.3 |
| **32.5 (τ\*)** | **12.5** | **32.4** | **0.0** | **10.8** |
| 45 | 0 | 34.5 | +10.5 | 11.3 |
| 90 | 45 (2F, wall as floor) | 63.1 | +45.4 | 52.2 |

At **τ\* = 32.5°**, three things line up at once:

- **The gun lies nearly flat in the vertical plane through the station
  tangent.** The beam is exactly in it. The nozzle, body front, body back and
  centre of mass all sit at x ≈ 0; the grip base is 22 mm out; the pistol's side
  is 11° from the plane.
- **The fillet is nearly flat.** Its bisector is 12.5° from vertical.
- **"Straight up" is the corner's escape direction** (within 12.5° of the
  bisector). In the upright tube, vertical is parallel to the wall and scrapes
  the wire tip up the lip. That is why the upright arrangements need a hinge
  behind the station or a retreat back along the tangent.

The fiber leaves the grip base horizontally along −Y (0.16, −0.99, −0.03), in
the gun's plane. The station becomes the **lowest point of the rim** (+5.4 mm
above the dot); the far rim rises 72 mm above it, on the far side.

## The escape rail (holds with or without tilt)

A rail fixed to the work along d = (−0.537, 0, 0.844) in the tube frame lies
32.5° from the tube axis, toward the tube's centre, in the radial plane at the
station. A straight lift along it **clears for every feasible recipe tested:
32 of 32** (grip 30–60, hole dial 15–45, yaw −30…+5; 4 more grid points are
infeasible at rest because the proxy's straight wire already sits in the lip).
The whole gun is outside the tube's cylinder, or above rim + 30 mm, after
**43 mm** of travel. This uses the vendored proxy point cloud (straight wire
included) at a fine step.

This holds in the **upright** tube too, as a rail inclined 32.5° from vertical,
and there the gun's weight still seats it on its stop (0.84 W along the rail).
Tilting to τ\* makes the rail vertical, so the weight is purely axial, and it
moves the column out from over the tube.

## The arrangement (whole station on the cradle, branch T-b; drawn)

| Element | What it does | Rate |
|---|---|---|
| Cradle | U-frame: floor under the rotator, side plates at y = ±175 mm, pivoting on two **UCP204 pillow blocks** on posts at y = ±190 mm, **axis = station tangent through the dot** | — |
| Tilt lock | printed or aluminium quadrant with pin holes at 0°, 20°, 25°, 32.5°, …; set with a digital angle gauge on the cradle floor | per session / per closure |
| Rotator | existing, on three fine Z screws on the cradle floor. The screws move it along its own axis, so tube length puts the corner back onto the trunnion axis | per tube |
| Plate head from P (sequence-of-use) | on the cradle; pads re-clocked to 30° / 150° / 250° at the true pose (their 180° / ±60° put the −60° stem 2 mm into the barrel; `wave3_objection_checks.py`); rim flag at P + 6.35 | per tube |
| Column + rail | upper extension of the −Y cradle side plate, at x = +62…+84 mm from the dot on the station side; HGR15 rail along d | — |
| Carriage + vertical plate | carriage on the rail; a plate at x ≈ +28 mm carries the shell flat on its side through a **recipe block** (roll, hole); **stop screw** at the bottom of travel sets the seated position | per recipe |
| Yaw | Y slide under the column foot (1.08 mm per degree; tube symmetry). The tilt axis *is* the tangent, so this still holds when tilted | per recipe |
| Camera | on the cradle, looking down the rail into the V (both fillet legs seen symmetrically) | — |
| Umbilical + wire conduit | leave in the gun's plane along −Y, to a loop or trolley above; they move ~160 mm when τ changes by 32.5° (the QBH is 280 mm from the dot) | — |
| Trigger | closes inside the shell (Bowden or solenoid, their K2) | per weld |

**Why everything rides the cradle:** the trunnions and lock then set only
gravity's direction. Their play or compliance tilts gun and work *together*, so
it never reaches the relative pose. The tilt mechanism can be a plain quadrant
and pin; no precision needed. The structural loop (gun → rail → side plate →
floor → rotator base → nest → tube) is short and never passes through the
trunnions.

**Balance** (estimates): the rotator + tube, 8–10 kg with its centre of mass
~130 mm below and 62 mm inboard of the axis, pulls back toward τ < 0 with
5–6 N·m at 0° and 10–12 N·m at 32.5°. The gun + column (~4.5 kg on the station
side) pushes the other way with ~5 N·m at 0° and ~8 N·m at 32.5°. The net is a few
N·m, so the cradle is easy to tilt by hand and a pin holds it.

## A closure, phase by phase

| Phase | Motion |
|---|---|
| Session | set τ with the pin; recipe block on the plate; stickout at the park gauge (their K3) |
| Load | gun up the rail to its park detent (≥ 50 mm); cradle to 0°; tube in, indicate (or indicate at τ, see break 2); plate in; plugs; plate head lever up; raise the Z screws until the rim touches the flag |
| Tilt | pull the pin, rotate to τ, pin. Nothing relative moves (isocentric, everything on the cradle) |
| Seat | lower the gun down the rail: its weight takes it to the stop. The wire tip arrives along the escape direction, not dragged down the lip. Jog to touch (their K3) |
| Tacks | pedal to each indexed angle, one trigger pulse each (fixture tacks via the plate head) |
| Weld | plate-head pads lift 2 mm; dot dry run; weld |
| Stuck wire | nothing moves; snip. The wire's tangential pull is across the rail, taken by the carriage |
| Away | gun up the rail; cradle to 0°; unload or invert |

## Which of Derek's three angles become work-side motions

Relative to the joint, a work tilt equals a change of dials (`tilt_calcs.py`,
exact at the opening pose):

- **1° about the station tangent** = grip +1.11°, hole −0.26°, vertical −0.55°.
  It is mostly Derek's **grip roll**. (At the true pose the grip axis is 33° from
  the tangent.)
- **1° about the station radial** = grip +0.30°, hole +0.97°, vertical −0.15°.
  It is mostly the **hole axis**.
- **Vertical axis** = the Y slide (tube symmetry), gravity-neutral.

So all three can be work-side: two tilts and a slide. **But** the two tilts
change gravity, so giving them to the work couples every recipe change to a
puddle-attitude change (branch T-c). The drawn arrangement keeps them apart: the
recipe on the gun side, the tilt as a separate process knob with the gun riding
along.

## Process: what is known and unknown (labelled; a process change, not a positioning detail)

- **Puddle size vs gravity.** Bond number Bo = ρgL²/σ with handbook-order
  values for liquid steel (ρ ≈ 7000 kg/m³, σ ≈ 1.8 N/m) is 0.09–0.34 for a
  1.5–3 mm pool, against 1.4 for a 6 mm arc-weld-sized pool. Surface tension should
  dominate gravity at this pool size, so the 2F → 1F change may be smaller for
  wobble laser welding than arc-welding experience suggests. This is an
  estimate, not a measurement; the recorded hand practice is all at 2F.
- **Shielding** *(wave 5: one-knob's Richardson estimate puts the buoyancy effect
  over the lip and trailing bead, not at the pool; see the wave 5 section)*.
  Argon is ~1.38× the density of air. Upright, the 6.35 mm recess
  is a cup that can hold argon. **Tilted more than 2.9°**, the recess spills over
  the rim's low point, which is the station. Whether that helps (gas flows over
  the weld) or hurts (no pool) is unknown.
- **Back purge.** First closure: argon enters the open held end. Tilted, the
  underside of the plate being welded has a high side, the far side, where air
  can pocket. The ports' clocking decides whether they vent it. Unknown.
- **Lip.** The unbacked 6.35 mm lip is heated the same way; its orientation to
  gravity changes. Unknown whether distortion changes.
- **Requalification.** Power, wobble, wire and travel settings would need
  re-running at τ ≠ 0. τ = 0 keeps today's settings valid. The knob lets one
  experiment compare 0° and 32.5° with everything else identical, which is
  exactly the "change one variable" loop Derek described.

## Break it

1. **The existing rotator tips at about τ\*.** Its turntable is
   gravity-seated, with a 1 mm lift catch. With the rotating centre of mass
   100–140 mm above the race (estimate), it starts to lift at 30.5–39.5°.
   *Repairs:* (a) run at 25° (bisector 20°, beam 6° out of the plane, pistol 16°
   off: still nearly planar); (b) preload the spool catch, replacing the 1 mm
   running gap with a PTFE thrust washer and wave spring (the drive's torque
   margin covers the drag); (c) a positioner built to tilt (branch T-f).
   *Leaves:* the real centre of mass.
2. **The tube shifts in the nest under the side load** *(wave 5: worse. An
   unclamped first-closure tube tips at ≈ 30.5°; see the wave 5 section for the
   band clamp)* (0.54 × weight at τ\*).
   The ID pilot has 0.2 mm radial clearance and the OD guide 0.4 mm; the three M3
   adjusters take the load. *Repair:* indicate at the welding tilt; the indicator
   base on the NEMA lamination tilts with the rotator, so the repo's datum still
   works.
3. **Swing clearance.** At τ\* the cradle floor's station end dips ~20 mm below
   its upright height. The posts are ~40 mm taller than the rotator's current
   joint height, and the bench drops to suit (VEVOR 28–39.5 in).
4. **The umbilical moves when τ changes** (the QBH swings ~160 mm). It is
   harmless if τ changes per session. If the cradle goes to 0° for every load,
   the first metre flexes twice per closure. A trolley or loop above the column
   takes it. The cable load at the gun is the same at every seat, because the
   seat is at the same τ each time.
5. **Loading at 0°.** The column then leans 32.5° over the tube; 100 mm above the
   dot it is inside the tube's cylinder. The tube needs only ~30 mm of lift to clear the
   nest, then is tipped out by hand toward −X. With the gun parked ≥ 50 mm up the
   rail, both clear.
6. **Second closure, float inside.** The rod is tacked to the first plate at
   r = 51 mm, and its tip sits in the second plate's register. The donut slides
   to the low end. For any τ < 90° the low end is the first plate, away from the
   weld, so the float stays clear. **Past 90° it slides onto the plate being
   welded** (plastic; melt risk). Keep τ ≤ ~80°.
7. **Stuck wire on a tilted table.** The off-axis rod and float (~45 g at 51 mm,
   estimate) give ~0.01 N·m of imbalance at τ\*, about 0.2 N at the bead. The
   unpowered motor's detent holds it, and the table does not creep when the
   driver releases.
8. **Recipes far from the baseline** take the gun out of the plane. The recipe
   block absorbs it; the rail still clears for every feasible recipe in the grid
   (above).

## Branches

- **T-a — room-fixed rail, tilt per session.** Only the work sits on the
  cradle; the gun's column stands on the bench, vertical, at the chosen τ. The
  cradle is lighter, but changing τ changes the relative pose and needs a new
  recipe block, so τ becomes a session constant, not a knob.
- **T-c — the work takes Derek's angles.** The gun is fixed in the room; grip
  and hole come from two work tilts, yaw from the Y slide. The gun support is
  simplest, but every recipe change is also a gravity change.
- **T-d — beam vertical.** τ\* plus a radial tilt of −33° puts the beam 6.5°
  from vertical (a fixed vertical optic, as in laser cells), but slopes the seam
  27° (uphill/downhill travel) and puts the fillet bisector 28° off vertical.
  Recorded; not preferred.
- **T-e — horizontal tube (τ = 90°), turning-roll style.** The fillet is 2F
  again, with the tube wall as the floor. The beam is 63° from vertical and the
  pistol's side 52° off the plane: no simplification of the gun support. The
  float is friction-held and can slide to the weld plate beyond 90°. Loading
  along the axis, lathe-style, is its one attraction.
- **T-f — commercial tilting positioner** (VEVOR HD-10, Prime, $254.90;
  self-locking worm tilt 0–90°, 1–12 rpm, 3-jaw chuck with 2–58 mm clamping).
  - It would carry a printed arbor holding the tube nest.
  - 1 rpm is 6.5 mm/s at the bead, so the 5 mm/s low end of the rig's window is
    out of reach.
  - Its tilt axis does not pass through the dot, so each tilt change needs a
    re-zero.
  - It would replace the rotator's stepper console (stored speed, degree
    readout) unless its motor is swapped.
  - It has only 25 ratings.

## Contribution / unresolved / assumptions

- **Contribution:**
  - The escape-rail finding: one straight rail along the corner's escape
    direction lifts the gun clear for every feasible recipe, upright or tilted.
  - At τ\* ≈ 32° that rail is vertical, the gun lies flat in one vertical plane
    with its cable, and the fillet is nearly flat.
  - Putting the gun on the cradle turns tilt into a clean process experiment
    with τ = 0 as today.
  - It answers which of Derek's angles a work tilt replaces: the tangent tilt is
    mostly grip roll, the radial tilt mostly hole.
- **Unresolved:**
  - the process effect of the tilt (shielding, purge, puddle);
  - the rotator's real tipping angle;
  - the real gun's plane at τ\* (from the scan);
  - the column's heat exposure 62 mm from the weld.
- **Rests on:** the pose.js proxy gun (60° pitch, 16 mm clearance, straight wire
  guide) at the true opening pose; the capsule and point-cloud gun models;
  estimated masses and centres of mass.

---

## Wave 5: one-knob-one-parameter's critique, and branches T-b1 and T-g

Source: `../../../exchange/one-knob-one-parameter--on--who-moves-what-w4.md`,
with calculations in `explorers/one-knob-one-parameter/tilt_exchange_calcs.py`.
I checked their key numbers with my own geometry.

### 1. The rail stop sets two things. Agreed; branch T-b1 adopted.

Their numbers are exact. In the tube frame, 1 mm along the escape direction
d = (−0.537, 0, 0.844) decomposes as **1.185 mm along the beam plus 0.635 mm
along the seam, and 0 across the corner**: d lies in the plane of the beam and
the seam. So the stop screw moved standoff *and* yaw (0.59° per mm, invisible to
the dot camera). Nothing on the gun side moved the dot between wall and cap.

*Assumption behind my version:* "the stop is where the gun sits" was taken to
be one setting.

**T-b1.**
- The rail stop becomes a fixed, gravity- and spring-seated ball-in-vee, never
  adjusted.
- Two stages are chosen by what they change: **S** along the beam (focus only)
  and **A** horizontal-radial (across the corner only).
- Yaw stays on the Y slide.
- The rotator's Z screws become per-tube calibration against the rim flag.

S and A ride the cradle with the gun, so they stay one-parameter at every τ.
Their printed flexure realisation (steel leaves in PET-GF blocks, micrometer on
a flexure lever) is `explorers/one-knob-one-parameter/ideas/flexure-trim-head.md`,
built on this carriage. The rail is then purely a motion to a stop, which is what
it was best at.

### 2. Branch T-g: a work-angle pivot coaxial with the cradle axis. Adopted as a branch.

A small pivot about the seam tangent through the dot, on the carriage: the
flexure head's W stage, a remote centre at D ≈ 70–90 mm. Then:
- α changes the work angle with gravity fixed;
- τ changes gravity with the work angle fixed;
- α = −τ reproduces T-c.

This is a better answer to "angle or gravity?" than my T-b alone, which could
only change gravity. It fits my wave-3 decomposition: the tangent tilt is mostly
grip roll (+1.11°/°), so W is the weld-language work-angle knob.

### 3. The tube tips before τ\*. Agreed; my break 2 treated only sliding.

The first-closure tube (1.40 kg, centre of mass ~108 mm above the rim it stands
on) tips about that rim at **≈ 30.5°** (atan 62.7/108; my check agrees), and
slides near 17° at µ ≈ 0.3. The second closure tips at ≈ 40°. A tube leaning on
its 0.4 mm guide clearance moves the corner by millimetres.

**Repairs adopted:**
- a 5 in exhaust band clamp around the OD at 70–110 mm, tied to the turntable by
  three printed posts (work-as-datum's C1 band, one-knob's placement);
- the turntable catch preloaded above the tipping moment (~1.6 N·m at 32.5°);
- the carriage seated by a spring beyond gravity, so its seat force does not
  switch between 0.84 W and W;
- **a tilt walk test**: cycle τ 0 → τ\* → 0 with the corner phantom clamped;
  read the dot on the camera, and two inclinometers (shell and rotator base),
  whose difference is the angle change the camera cannot see.

*Stays uncertain:* band-clamp distortion of the 0.065 in wall. Indicate with
the band on and off.

### 4. Gas: buoyancy matters over the lip, not at the pool. Agreed; added to "Process".

By their Richardson-number estimate, the jet dominates near the pool
(Ri < 0.02 at 15–20 L/min), and buoyancy competes only in the slow gas over the
lip, the trailing bead and the recess cup (Ri 0.02–1.5). So τ plausibly changes
pool attitude and trailing/lip shielding, not the pool's own coverage.

**Experiment:** τ × flow as two factors, with heat tint on the lip, the trailing
bead and the root photographed as the readings. Add an optional nozzle skirt as
its own in/out knob if the τ effect depends on flow.

### What changes, and what stays

- **Changes.** The rail stop is no longer a recipe knob. The station gains S, A
  and optionally W. The tube is clamped whenever τ > ~15°, the catch is
  preloaded, and the tilt walk test is part of commissioning. "Tilt changes only
  gravity" becomes a measured claim, not an asserted one.
- **Stays.**
  - The escape direction and its 32 of 32 clearance.
  - The isocentric cradle carrying everything.
  - Yaw on the Y slide.
  - That τ\* ≈ 32.5° lays the gun flat and the fillet near 1F.
- **One small disagreement, about emphasis.** They present the stop's standoff
  and yaw coupling as a defect of the escape rail. It is a defect of using the
  stop as a knob. As a *motion to a fixed stop*, the escape rail is exactly
  one-parameter: its only job is on or off. Their T-b1 is that reading, so we
  agree on the design.
