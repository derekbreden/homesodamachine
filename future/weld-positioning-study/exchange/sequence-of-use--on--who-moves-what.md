# sequence-of-use on who-moves-what (wave 2)

My view: the procedure is the machine. I walked each of their arrangements through
a full session (load, seat and indicate, plate at recess, eight tacks, aim and dot
dry run, weld, stuck wire, gun away, unload, invert, next tube) and looked for the
phase where it stops working.

Worked on:

1. **Still gun, moving work** (their furthest-developed idea): three difficulties,
   all repaired far enough to be built.
2. **Carrier + seat, branches D1/D2** (Derek's monitor arm and rings, left rough):
   parking, roll, and the moment of docking.
3. Short sequence notes on **3c gauge foot** and **protractor + stub**.

New files in my directory: `calc/exchange_w2.py` (numbers below),
`calc/x2_sketches.py` →
`sketches/x2-plate-hung-from-P.svg` and `sketches/x2-trolley-parked-carrier.svg`.
All geometry is the orientation-scene proxy at the opening pose (grip 45°, hole 30°,
vertical −15°, 16 mm nozzle-to-dot). Masses are estimates.

---

## 1. Still gun, moving work

What it does that none of my arrangements do: it gives yaw and X to a cross-slide
under the work (their tube-symmetry finding), so the seat of a still gun is
*adjustable* in the two freedoms that vary. It also makes the dot a fixed pixel for
a fixed camera. My idea B (gun stays, work travels) had kinematic seats but no X or
yaw setting at all. B should take their cross-slide.

### Difficulty 1.1 — the wire, not the nozzle, blocks the tube leaving, at any standoff

*Variant:* 1a at the proxy's 16 mm standoff, where their calc 8 finds the nozzle tip
8.8 mm above the rim and concludes that "the tube slides out sideways with nothing
lifted".

*Assumption behind it:* the nozzle tip is the lowest point of the gun. It isn't: the
wire runs 16 mm past the nozzle and sits in the corner, 6.35 mm below the rim.

*Numbers* (`exchange_w2.py` §1, tube moved horizontally under the fixed proxy gun):

| Tube moves toward | No drop | 5 mm drop | 10 mm drop |
|---|---|---|---|
| −X (away from the station) | collides at once (wire) | collides | collides |
| ±Y (along the tangent) | collides at once | collides | collides |
| +X (under the gun, from the station side) | collides after 121.5 mm, when the far wall reaches the wire | collides | **clear** |

With the wire retracted **8 mm** along its own line (the wire is 71° above
horizontal, so 7.8 mm lifts the tip 7.35 mm, above the rim), every direction is
clear at this standoff.

*Repairs, as a choice between sequences:*

- **Drop first, then out along +X only.** Their "drop-away drawer" branch is needed
  at every standoff, not only at 5 mm, and the drawer direction is fixed: +X,
  toward and past the station.
- **Retract the wire 8 mm before every drawer move** (the feeder's retract button,
  manual 3.5), then jog it back to touch after the drawer returns. There is no
  mechanism, but each tube gains two steps, and stickout is re-made every time
  (see 1.3 and my session kit K3).
- **Ramps into vees** (next item), which give the drop as a by-product.

### Difficulty 1.2 — "back to a stop" leaves play along the tangent, and their own finding makes it yaw

*Variant:* the loading drawer "out along X, back to a stop" on the cross-slide.

*Assumption:* a hard stop returns the work to where the cross-slide was set. It
returns only the travel axis. Ball-bearing drawer slides and light rails leave
lateral play (0.2–1 mm, my estimate; not measured). By their tube-symmetry finding,
that play is yaw:

| Tangent play | Yaw |
|---|---|
| 0.2 mm | 0.19° |
| 0.5 mm | 0.46° |
| 1.0 mm | 0.93° |

Their dot check re-trims X each tube, but they note that an error along the seam
is invisible to the dot. So every reload carries an unobserved yaw error, which
breaks their own rule that Y is "set by dial, not by chasing the dot".

*Repair: end-of-travel ramps into vees* (my idea B, placed on top of their
cross-slide). The drawer carriage runs 20 mm low on its guide. In the last 60 mm,
three hardened balls under it climb three ramps and settle into three vees fixed to
the cross-slide's top plate. The guide then only guides; the vees locate. Kinematic
reseating is micrometre-class (their Thorlabs figure is 82 µrad max; a dowel-pin vee
seat is probably tens of µm, an estimate), so the cross-slide dials mean the same
thing on every load. The same ramps give the 20 mm drop that 1.1 needs, and the
approach is along X (±20° is fine, `drawer_path.py`). *Cost:* about 30 mm more
stack height, and a push of ~20–25 N for 6–10 kg of work (estimate).

### Difficulty 1.3 — phases 3–6: the plate at its recess and eight tacks, under a gun that never moves

*Variant:* their per-tube procedure is "drawer out, load, indicate, drawer in, dry
run, weld". The end plate and the tacks are not in it.

*Assumption:* tacks and plate seating happen as they do today, by hand. In this
idea the gun cannot go into the hand, and:

- the plate can only go into the tube with the drawer **out**, because the nozzle
  and wire are inside the rim circle at the station. A slip-fit plate then drops
  (first closure: down the bore; second: onto the float rod's tip, deliberately
  1 mm short, where it cocks);
- the tacks must be made **at P by the still gun**, with the table indexing between
  eight angles. Any hanger that bridges the rim crosses P at each index and hits the
  wire.

*Repair: hang the plate from P* (sketch `x2-plate-hung-from-P.svg`). A stationary
head on an arm from the gun stand comes in over the far (−X) rim at rim + 40 mm.

- **Engages the plate:** a bearing housing on the tube axis. Its spindle ends in a
  keyhole fork that catches collars on two 1/4 NPT stainless plugs, finger-threaded
  into the plate's two tapped ports (tapped at step 1, before welding).
- **Sets the plate's plane:** a spring pulls the spindle up and holds the plate
  against three **stationary** ball-transfer pads at r = 40 mm (180°, ±60°). The pads
  sit outside the port circle (13.5–24.6 mm) and well inside the fillet. Their tips
  are set at P height.
- **Holds** plate Z and tilt from the stand. **Leaves free** radial position (the
  bore centres the plate) and spin (the bearing).
- **Rim flag:** the same head carries a flag at P + 6.35 mm, over the far rim.

*What this changes:* the corner's height at the station is P **for any tube
length**, because the plate face is set by the stand, not by the tube.
OnlineMetals' ±3.2 mm cut tolerance (digest) then moves only the lip height. The
per-tube work-Z step becomes mechanical — "raise until the rim touches the flag" —
and needs no camera. The dot check is left to trim X only.

*Clearance* (§2): the closest head-to-gun centre-line distance is 30 mm, at the
barrel 40 mm above the rim (proxy). Subtracting member radii leaves roughly 15 mm.
The head can stay in place through the weld, lifted 2 mm off the plate.

*The session with this repair:*

| Phase | Hands | Machine |
|---|---|---|
| Load | Drawer out. Tube into the nest; indicate as now; drop the plate in; thread both plugs finger-tight | Gun stands free: trim stickout at the gauge |
| Seat | Push the drawer in | Ramps lift the work into the vees |
| Recess | Raise work Z until the rim touches the flag. Lower the head, turn the free fork onto the collars, lever up | Plate face held at P |
| Tacks | Pedal to each indexed angle (console degrees), one trigger pulse each | The tack pattern becomes a fixture operation, as repeatable as the bead |
| Weld | Lever down (pads lift 2 mm). Dot dry run, then weld | — |
| Stuck wire | Snip, then retract the wire | Nothing moves before the snip |
| Unload | Drawer out: ramps drop first. Unthread plugs; invert or change tube | — |

*Breaking the repair:*

- **Table face wobble while indexing between tacks.** Once tack 1 is in, the plate
  is tied to the tube. The turntable's axial runout at that tack's angle then pushes
  against pads held by the stand. Keep the spring pull modest (~20–30 N) so the tube
  and nest yield first. If the face readings show strain, release after the first
  two opposite tacks. *Leaves:* the turntable's real face runout (not measured).
- **Second closure:** the plate sits cocked on the rod tip. The fork turns freely on
  its spindle, so it can be rotated by hand to find the collars before the lever
  pulls the plate level. The rod-register clocking is done by hand when the plate
  goes in, as now.
- **Plugs in the ports** stay through the weld (work-as-datum asked the same
  question: may 316 fittings sit in the ports while welding?). In the second closure
  they stop the top ports venting, so purge leaves through the open lower port, as
  the repo intends.
- **Pad marks** land on the plate's outside face, outside the pressure boundary.
  Stainless ball transfers: their own sourcing (TOVOT CY-15A) or work-as-datum's
  KangTeer 1 in units.

*Transfers:* this head fits my B, work-as-datum's between-centres idea, and any
arrangement where the gun stays in place during tacks.

---

## 2. Carrier + seat (D1 monitor arm, D2 Derek's rings)

What it does that mine lacks: a seat on a post from the **rotator base**, the same
printed datum as the race and nest. That is a shorter chain than my lid's frame post
on a subplate; my lid's vees could move there. D2's observation that Derek's two
loops already lie nearly on the grip axis is a real find. The monitor arm gives
"park anywhere"; my lid has one fixed park.

### Difficulty 2.1 — parking a balancer-hung gun, and where the umbilical's peak goes

*Variant:* D2, two rings hung from two tool balancers anchored overhead, above the
tube.

*Assumption:* balancers carry the gun anywhere, so "swing aside for loading" is
free.

*Break:*

- **The lines are pendulums** (§4). Pulled 300 mm aside to open the loading column,
  a 15–20 N gun on 0.8–1.2 m lines is pulled back toward the tube with 4–8 N and must
  be hooked.
- **Two anchors yaw the gun.** They sit at different points, so the two lines lean
  at different angles as the gun moves, and the gun yaws and drags the umbilical
  sideways.
- **The umbilical changes shape.** The digest's umbilical needs a support near its
  peak (~680 mm above the bench). If that support stays put while the gun parks and
  returns, the gun-to-peak section takes a different shape each time. The cable
  force on the seat then depends on how the gun came back, and the dock position
  moves with it.

*Repair: one trolley carries everything that hangs* (sketch
`x2-trolley-parked-carrier.svg`).

- **Rail:** a 2040 V-slot rail about 1.25 m above the bench, with an assembled
  gantry plate on POM wheels (Prime, $16.89, observed).
- **What the trolley carries:** both balancers and the umbilical saddle (arc R ≥ 350).
- **Park:** lift ~30 mm (the wire tip clears the rim after ~8 mm; weightless on the
  balancers), then roll ~420 mm to a detent. The lines stay vertical at both ends of
  the rail.
- **Dock:** the gun-to-saddle umbilical has one shape at every dock, so its force on
  the seat is one constant.
- **Rail loads:** the rail carries only ~30–40 N and locates nothing, so ceiling
  joists or two posts on the bench will do.

### Difficulty 2.2 — the rings' roll hinge is not free while hanging

*Variant:* D2's rings, made into journals concentric with the grip axis, "a gun
that floats weightless and rolls about the grip axis".

*Assumption:* concentric journals make roll a neutral hinge.

*Break* (§3): the proxy centre of mass (housing centre) sits **85 mm off the grip
axis**, which is inclined 65°. With roll free, gravity gives **0.28–0.49 N·m** about
the grip axis for 0.8–1.4 kg of gun and shell. The hanging gun rolls until its
centre of mass is under the axis, not to the recipe's 45°. Every trip from park to
dock ends with a hand rolling it back against that torque.

*Repair / branch:*

- **Roll lock on ring B,** released only for a deliberate roll change at setup.
  This matches their recipe-block view: roll is a setup adjustment.
- **Or give Derek's third ring the job.** A third ring hung from its own balancer,
  off the grip axis, supplies a counter-torque: F₃ · r₃ ≈ W · 85 mm makes the gun
  hang at the recipe roll. This is exactly his "increase the force needed to
  exercise that range", and it is a trim, not a lock. Constant-force balancers
  balance it at one roll only.

### Difficulty 2.3 — docking is also the moment the wire meets the corner

The balls drop vertically into the vees, and the wire tip reaches the corner at the
same instant. The proxy tip touches the wall, so a vertical last approach drags it
down the lip's inner face. A tip 1 mm long bends, or holds the shell off the seat.

*Repair:* stickout set ~1 mm short and the tip 0.5 mm in from the wall at the
recipe, then jog to touch after docking (my A3 and K3). *Leaves:* whether the
welder's start tolerates the gap (question for Derek).

### Transfer from my lid

A stiff carrier (a monitor arm's friction joints) docked into a seat
over-constrains the gun unless it goes soft at the dock. My lid solves this with
hinge pins in slots, so the closed lid hangs only from its three balls. For D1, the
equivalent is a compliant link between the arm's VESA plate and the shell: a few mm
of float held by springs, so the arm carries and the seat locates.

---

## 3. Short notes

- **3c gauge foot** (the same family as my D, gauge-set lock-held):
  - A single touch sets the corner at one table angle, not the mean. Touch at 3–4
    angles and set to the mean; that is 3b's map, taken with a feeler.
  - Tacks sit in the corner every 45°, so the foot must touch between them (22.5°
    off). Index back to tack 1 afterwards.
  - The foot's retract cam must close its force loop inside the shell, or retracting
    disturbs the lock.
- **Protractor + stub:** every roll or tilt change swings the fiber exit (their
  calc 5). The umbilical clamp therefore belongs to the sequence: unclamp, change the
  angle, re-clamp at the new shape, then re-check the dot, because the cable load is
  now a different constant. With the clamp in the sequence, the isocentre keeps one
  dial as one variable.

## Combination worth carrying forward

Still gun + ramps into vees on the cross-slide + plate hung from P + stickout gauge
used with the drawer out. The human actions per tube become: load, thread two plugs,
push the drawer in, raise to the flag, pull the lever, pedal-and-pulse eight tacks,
dry run, weld. Each step is either a mechanical stop or a number on a dial, which is
the transfer-to-another-person goal. The umbilical never moves, so their static
cable route stands, and my trolley is not needed there.

---

## Wave-3 correction: pose convention

My wave-2 numbers above were computed at scene hole **dial 65**. My proxy passed the
dial straight into `posePoint`; the scene subtracts 35. At Derek's opening pose (dial
30), re-run in `explorers/sequence-of-use/calc/exchange_w2.py` and `head_w3.py`:

- **Tube leaving a still gun.** Same pattern: only toward +X, and only after a
  ≥ 10 mm drop. The wire retract that frees every direction is **14 mm**, not 8 mm,
  because the wire rises at 38°, not 71°.
- **Stand-hung plate head.** The "30 mm" clearance was dial 65. At dial 30 the
  180° / ±60° pad layout at rim + 40 **intersects the barrel** (6 mm centre-line).
  The layout becomes pads at 45° / 150° / 255°, frame at rim + 15, arm from −X:
  38.8 mm centre-line (sketch `x2-plate-hung-from-P.svg` redrawn).
- **D2 roll torque.** The CG is still 85 mm off the grip axis, but the axis is
  inclined 30°, not 65°, so the free-roll torque is **0.58–1.01 N·m** for 0.8–1.4 kg
  (0.28–0.49 at dial 65). The case for a roll lock on ring B is stronger.
- **Pendulum and drawer-play numbers** do not depend on pose and are unchanged.
