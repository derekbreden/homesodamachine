# Still gun, moving work

## Picture it (as it now stands, after waves 2–3)

**Upright tube, fixed gun.** The tube stays upright, and the gun never moves
after setup.

**The work stack**, from the bench up (one rigid base plate under both it and the
gun stand):
- a cast-iron **cross-slide**: X is radial, Y along the tangent, which is the
  relative yaw at 1.08 mm per degree;
- a **drawer** whose carriage climbs end ramps and drops into three **vee seats**
  on the cross-slide's top plate. This is branch 1d, from sequence-of-use; the
  vees, not the drawer guide, return the work, so the dials mean the same thing
  every load;
- the rotator on three fine Z screws.

**The gun side.** The scan-fit shell hangs from a bench-fixed stand through a
printed **recipe block** (roll and hole). The umbilical and wire conduit follow
one static route to the cart. A camera on the stand sees the dot as a fixed
pixel.

**The plate.** A stationary head from the stand holds it at P (sequence-of-use):
port plugs, three stainless pads at r = 40 mm clocked 30° / 150° / 250° to clear
the barrel, and a rim flag at P + 6.35 mm.

**Per tube, and per weld.** Raise Z until the rim touches the flag. Tacks are
indexed pulses. Loading is drop-then-out toward +X, which the ramps provide,
because the wire tip sits in the corner.

**What carries, locates and is fixed.** The stand carries the gun, and the
seats, dials and flag locate the work. "Fixed" is the common base plate.

**Sketches:**
- `../sketches/s2-still-gun-moving-work.svg` (station, true opening pose; drawn
  before 1d, so the drawer is shown without ramps or the plate head);
- `../sketches/s1-plan-yaw-by-work-slide.svg` (why Y is yaw, true pose).

**Major unresolved problems:**
- Runout during the weld is not followed. Whether that matters depends on the
  unmeasured process window.
- The turntable's face runout pushes against the stationary pads while indexing
  between tacks.
- Whether 316 plugs may sit in the ports while welding.
- About 150–180 mm of stack height.
- The purge hose and leads riding a moving base.

## The original (wave 1), with later corrections marked

**Allocation in one line:** after setup, the gun, its shell, the umbilical and the
wire conduit never move. The work takes every motion that does not change the
puddle's relation to gravity: radial X, the seam-tangent Y (which *is* the
vertical-axis yaw), Z, spin, lift-off and loading.

Sketches: `../sketches/s2-still-gun-moving-work.svg` (station, side view) and
`../sketches/s1-plan-yaw-by-work-slide.svg` (why Y is yaw).
Numbers: `../geometry.py`, `../allocation_calcs.py`.

## What makes it different

Every arrangement Derek has described moves the gun: an arm, a gantry, or hooks.
This one inverts the allocation. Three facts make the inversion unusually cheap
for this joint:

1. **Tube symmetry turns a slide into yaw.** The seam is a circle on the tube
   axis, so rotating the work about that axis changes nothing. Sliding the work
   along the tangent by r·sin φ, and toward the station by r·(1 − cos φ), keeps
   the seam through the fixed station point P and turns the local tangent by φ
   under a gun that never turns. That is **1.08 mm per degree**; ±15° takes
   ±16.0 mm of slide and 2.1 mm of correction (calc 1). A plain X/Y cross-slide
   under the rotator therefore realizes radial position *and* the scene's
   vertical-axis rotation. No yaw bearing exists anywhere.
2. **Yaw and translation are gravity-neutral.** Moving the work in X, Y, Z or
   spinning it leaves the plate horizontal and the weld downhand. Only grip roll
   and hole tilt change the gun's attitude, and those stay with the gun.
3. **Cables are the gun's worst load, and here they are static.** The fiber
   (35 cm minimum bend while emitting; "twisting is strictly forbidden"), gas line,
   signal and wire conduit hang in one route for a whole session. A constant
   force gives a constant, calibratable sag. A moving gun instead drags a varying
   cable force through every axis.

## The station (whole-station view)

```
         overhead anchor ── umbilical + wire conduit (static route to cart)
                   \
   stand ──bracket──[recipe block]──shell──gun   camera (on stand)
   (bench-fixed)                         \          :
                                          \ nozzle  :
                                           P (dot)  <- fixed point in the room
                                     ┌─────tube─────┐
                                     │   rotator    │  spin (existing, pedal)
                                     ├──────────────┤  3 fine screws: Z + trim tilt
                                     │ drawer rails │  loading: out & back to a stop
                                     ├──────────────┤
                                     │ cross-slide  │  X radial, Y = yaw (1.08 mm/deg)
   ─────────────bench (lowered ~150 mm to keep the joint height)──────────────
```

| Motion | Body that realizes it | When set |
|---|---|---|
| Grip-axis roll, hole-axis tilt | printed recipe block between stand bracket and shell (1a), or the protractor + stub on the stand (1b → `protractor-and-stub.md`) | per session / recipe |
| Vertical-axis yaw | cross-slide Y (tube symmetry) | per recipe; re-checked per tube |
| Radial X | cross-slide X | per tube (dot check) |
| Z / standoff | three fine screws under the rotator base (also give trim tilt of the work) | per tube |
| Tangential position of the dot | none: that is the symmetry | — |
| Spin | existing rotator, pedal | during the weld |
| Lift-off | the drawer's first motion is a ≥10 mm drop (the wire tip sits in the corner, below the rim) | per weld |
| Loading, inversion | drop, then drawer out toward +X (the station side, within ±20°), tube swapped or inverted, back in and up onto seats | per closure |
| Trigger | lever or servo on the fixed shell (the gun never moves, so any rigid linkage works) | during the weld |
| Stuck wire | nothing moves; snip | — |

## How it is used

- **Session:** mount the recipe block. Put a calibration piece in the nest: a
  tube offcut with a plate tacked 6.35 mm deep. Mark P in the stand camera's
  image where the dot lands. The camera is on the stand, so **the dot never moves
  in its image**. Only the work moves under it. That suits a vision loop.
- **Per tube:** drawer out, load, indicate runout as now, drawer in to the stop.
  Dry-run the reference beam at a few table angles. Trim X on the cross-slide and
  Z on the screws until the dot sits in the corner at P. Y is dialled from the
  recipe (yaw), not used to chase the dot.
- **Weld:** pedal, then trigger, as in the current sequence. **End:** release
  the trigger, and the feeder's pullback retracts the wire (manual, fig. 17
  "Pullback length"). Release the pedal.
- **Second closure:** the same station. The nest seats the welded end, and the
  rim height is unchanged. The lower-plate purge hose through the Ø90 passage
  needs slack for the drawer stroke.

## Break it

- **What is "fixed" fixed to.** P is defined by the stand. The work reaches P
  through bench → cross-slide → drawer → screws → rotator base → balls → nest →
  tube. If the stand and cross-slide sit on the VEVOR wooden top separately,
  top flex and caster creep become relative motion. Repair: both sit on one rigid
  plate, which is then clamped to the bench.
- **Cross-slide backlash and gibs.** Trapezoidal screws have backlash (estimate
  0.1–0.2 mm; not read on the listing). The table is set per tube, always
  approached from the same direction, and gib-locked for the weld. During the
  weld it carries only the static load and the rotator's drag reaction, so
  backlash does not matter while locked.
- **Y is not free.** Because Y is yaw, an unintended 1 mm Y error is a 0.93°
  yaw error. An error along the seam is invisible to the dot check and visible
  only as yaw. Use the dial, not the dot, to set Y.
- **Yaw and X couple** (2.1 mm at 15°). Keep a two-column chart (φ → X, Y), or
  set φ in firmware if motorized.
- **Recipe-block swap moves the dot.** Blocks are computed from `pose.js` so
  each recipe rotates the gun about P. Printed faces carry error: 0.1 mm over a
  100 mm base is 0.06°, which moves the dot 0.25 mm at a 250 mm lever (calc 4).
  So the angles are good to about 0.1°, and the dot is re-zeroed with X and Z
  after a swap, a one-minute camera step. A 0.25 mm residual along the seam
  shifts yaw by 0.23°.
- **Runout during the weld is not followed.** The corner wanders through the
  procedure limits (≤0.25 mm radial TIR, ≤0.30 mm face TIR) under a fixed gun,
  exactly as under a steady hand. Whether that matters is the unmeasured process
  window. If it does, following goes to the work, not the gun: a motorized X/Z
  under the rotator replays a runout map recorded on a dry-run lap (see
  `tube-carries-the-reference.md`, branch 3b). The work is heavy (~8–10 kg,
  estimate), but the motion is ≤0.3 mm at once per 48.6 s.
- **Loading needs a drop first, whatever the nozzle does** (wave 2, from
  sequence-of-use's `calc/drawer_path.py`). At the opening pose (hole dial 30)
  the nozzle tip sits +5.0 mm above the rim at the proxy's 16 mm standoff, +0.8 mm
  at 10 mm and −2.8 mm at 5 mm (calc 8). At hole dial 65 those were +8.8, +3.1 and
  −1.6 mm.
  But the **wire tip sits in the corner, 6.35 mm below the rim**, so no purely
  horizontal tube motion gets it out. The tube must drop ≥ 10 mm and leave toward
  +X, the station side, within about ±20°. Repair: the drawer's first motion is
  the drop. Sequence-of-use's ramps-into-vee-seats (their idea B) does exactly
  this, and the vee seats sit on a plate carried by this cross-slide, so the
  recipe's X and yaw are kept by the seats. The earlier line here, "slides out
  sideways with nothing lifted", was wrong.
- **Height.** The stack adds ~150 mm (estimate: table ~100–110 mm, drawer
  ~40 mm). The VEVOR benches adjust 28–39.5 in (agent figure), so the joint can
  be put back where Derek is used to it.
- **Stuck wire.** Nothing moves; the tube stops with the pedal. The backdrivable
  belt still yields. Snip as now.
- **Second person.** The settings are a recipe-block ID plus the cross-slide
  dials, the drawer stop and the screw marks. Nothing hand-held, nothing
  cable-heavy to wrestle.
- **Moving the work has costs.** Hoses (purge), the ground-shoe lead, the pedal
  lead and the rotator's power ride on the drawer. The purge hose through the
  base is the most constrained, needing a stroke's worth of slack.

## Branches

- **1a — recipe blocks (drawn).** The angles are printed objects. Changing
  recipe means swapping a block. This is very transferable, and fun to make:
  a block per 5° step is an overnight print.
- **1b — protractor + stub on the stand.** Continuous angles with both axes
  through P. See `protractor-and-stub.md`.
- **1c — Derek's table opening, reallocated.** The rotator sits on a shelf
  under the table opening, and the gun is fixed on the table top above. The
  shelf's cross-slide owns X/Y(yaw) and the shelf height owns Z. The opening's
  side face is the drawer. Derek's original, with the gantry carrying X/Y above,
  stays as he described it. Under this reading, his gantry's Y already owns the
  yaw, and his "not tangent" concern becomes a Y-position setting.

## Motorized future

Replace the two cross-slide handwheels with NEMA 23s and the Z screws with a
motorized wedge or three small steppers. The AI iterates by moving the work
under a fixed gun and a fixed camera. No motor carries cable drag. Roll and tilt
stay manual (blocks) unless 1b is used, which adds the two "roll" motors of
Derek's automated vision.

## Contribution / unresolved / assumptions

- **Contribution:** shows that the vertical-axis rotation costs no hardware for
  a tube joint, that cables can be made static, and that a fixed gun makes the
  dot a fixed pixel for vision.
- **Unresolved:** the drop-then-out drawer mechanism (the wire tip sits below the rim); cross-slide
  backlash and lock behaviour (not observed); whether the process window
  tolerates un-followed runout; the purge-hose route on a moving base.
- **Rests on:** the pose.js proxy gun (60° pitch, 16 mm clearance); the capsule
  gun model scaled from the manual drawing; stack heights estimated.

---

## Wave 3: sequence-of-use's objections, and the repaired variant (branch 1d)

Source: `../../../exchange/sequence-of-use--on--who-moves-what.md` (written at hole
dial 65). Pose-dependent numbers are re-checked here at the true opening pose
(dial 30) in `../wave3_objection_checks.py`. The original arrangement above stays
as written. Branch 1d is the repaired variant.

| Objection | Verdict | At the true pose |
|---|---|---|
| **1.1 The wire, not the nozzle, blocks slide-out** at any standoff | Agree (already corrected above in wave 2) | Their drawer result holds at dial 30 (`../wave2_drawer_check.py`): arriving from the station side within ±20°, a ≥ 10 mm drop and a diagonal ramp clear; a purely vertical final rise grazes the tip. Retracting the wire instead needs **12 mm** along the wire (it is 37.8° above horizontal at dial 30), not their 8 mm (71° at dial 65) |
| **1.2 Drawer lateral play is yaw** (1.08 mm per degree), invisible to the dot check | Agree; it is a direct consequence of my own tube-symmetry finding and I missed it | Pose-independent |
| **1.3 The plate and eight tacks are missing** from my sequence | Agree | Their plate head from P works, but their pad clocking (180°, ±60°) puts the −60° stem **2.2 mm into the barrel** at dial 30. Pads at **30° / 150° / 250°** clear by ≥ 24 mm (stems) and ≥ 28 mm (spider arms). The clocking is recipe-dependent: at dial 65 the 30° pad would have only 11 mm |

**Branch 1d — still gun, ramps into vees, plate hung from P.**

- **Seats.** Three hardened balls under the drawer carriage climb end ramps
  into three vees fixed to the **cross-slide's top plate**. The vees, not the
  drawer guide, return the work. So the cross-slide dials (X radial, Y = yaw)
  mean the same thing on every load, and the ramps give the ≥ 10 mm drop and the
  +X exit the wire requires.
- **Plate.** The plate is held from P by a stationary head on the gun stand:
  port plugs, a spring-up spindle, three ball-transfer pads at r = 40 mm
  (re-clocked 30° / 150° / 250°), and a rim flag at P + 6.35.
- **Per-tube height.** Raise the work Z until the rim touches the flag. The
  corner is then at P for any tube length, and the flag is the reference (my
  three screws stay as the actuator). This replaces my "trim Z with the camera"
  step.
- **Tacks** become fixture pulses at indexed table angles.
- **Stickout** is trimmed at a gauge with the drawer out (their K3).

**What it changes.** Every per-tube step is now a stop or a dial. Yaw can no
longer drift on reload. Tube length drops out of the corner height. The
arrangement now covers phases 3–6, which it previously ignored.

**What it leaves uncertain.**
- The turntable's face runout pushes against the stationary pads while indexing
  between tacks; their answer is a modest spring and releasing after two tacks.
- Whether 316 plugs may stay in the ports during the weld (question for Derek).
- The ramp push (~20–25 N) and ~30 mm of extra stack height.
- The pad clocking must be checked against each recipe's barrel path.

**One disagreement, a small one.** They list "retract the wire before every
drawer move" as an alternative to the drop. At the true pose it needs 12 mm of
retraction and a re-touch every tube, and the ramps give the drop for free. I
would keep only the ramps.

**See also** `tilt-cradle-escape-rail.md`. There a straight rail along the
corner's escape direction replaces the drawer's drop: the gun leaves the work,
rather than the work leaving the gun.
