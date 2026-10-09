# Knob-wired suspension: one wire per angle, three wires meeting at the dot

**Picture it (current state, wave 5).**
- **Wires and cage.** The gun in its shell hangs in six taut 1/16 in stainless
  wires running to an anchor cage (~0.9 m) around the rotator, on the same
  baseplate. Two downward preloads (Derek's bungees, or constant-force
  balancers) keep every wire taut; they set no position.
- **The pivot.** Three calibration wires, fixed and painted, aim along lines
  through the dot from a printed outrigger that reaches over the rim. Together
  they make the dot a virtual pivot.
- **Hole knob.** A wire from Derek's base loop, an openable ring around a
  collar on the shell's butt sleeve, pulls up in the vertical plane of the grip
  axis.
- **Roll knob.** A wire from the outrigger pulls up in the vertical radial plane
  through the dot.
- **The sixth wire.** It lies in the plane of the grip and hole axes.
  - Original: a vertical-angle knob from the base loop.
  - Wave-5 branch after who-moves-what: a fixed wire from a shell boss 112 mm
    along the grip axis. The vertical angle is then set by the couch Y slide
    instead.
- **Work side.** The dot's place is set by X/Z slides under the rotator.
- **Anchors.** Each angle wire ends on a Tr8×2 lead-screw anchor with a dial.
  Tension always loads the nut one way, so there is no backlash.
- **Load path.** The wires both carry and locate.
- **Moving it.** Unhooking the preloads and the horizontal wires frees the gun.
  Re-hooking restores the six lengths and so the pose.
- **Fixed** is the anchor cage.

Sketch (opening pose 45/30/−15): `../sketches/knob-wired-suspension.svg`.

**Major unresolved problems.**
- Tension margin. It was 5.9 N in the original layout; who-moves-what's
  in-plane sixth wire (R1) lifts it to 18.5 N, still on an assumed 1.5 kg gun
  and CoM.
- Exactness is first-order only: the dot drifts ~θ² × 25–65 mm.
- A ~0.9 m cage.
- Clutter near the dot: outrigger, nozzle, wire guide, camera.

Sketch: `../sketches/knob-wired-suspension.svg`. Numbers: `../diagonal_wires.py`
(layout search, knob matrix, finite moves, stiffness; output saved in
`../diagonal_wires.out.txt` and the layout in `../diagonal_wires_layout.json`)
and `../diagonal_wires_checks.py` (vibration modes, plane tolerance, anchor
loads). The gun is the scene's illustrative proxy at the opening pose (roll 45,
hole dial 30, vertical −15). Gun + shell mass 1.5 kg, with borrowed-ecosystems'
CG proxy **[assumed]**.

## Derek's example, as he gave it

> Imagine if you will:
>
> - One of those metal rubber coated hooks on pegboard walls in garages everywhere
> - Imagine that hook being a complete (openable) loop
> - Imagine that hook hanging from a wire to be held in Z, and suspended from bungees or something stretching in either the X or Y axis, so just two bungees, holding one axis steadyish
> - Imagine one hook around the tip of the gun, and a second hook around the base of the gun (around the umbilical and wire feed)
>   - Can you see how the arm might "grip" (keeping in mind, that "grip" means a complete shell we print with whatever attachments we want to attach to our robot arm anywhere we like on that shell) this in several ways and get entirely different results?
>   - Can you see how a 3rd ring a number of places might reduce the range of motion (or increase the force needed to exercise that range) but at the same time reduce weight further?

The original stays as the reference. Others have already taken it seriously:

- **carry-and-locate** developed it as stated (`../../carry-and-locate/ideas/suspension-original.md`):
  - weight shares between the two loops;
  - bungees on the radial axis, with the tangent left as the free swing;
  - a shell trunnion that makes the two-loop free roll equal Derek's grip roll;
  - the third ring high at the back.
- They also found **six taut wires, three of whose lines meet at the dot**, which make a virtual ball joint there, with bungees kept only as preloads (`wire-located-suspension.md`). This file builds directly on that.
- **machine-that-learns** ran that layout as a cable robot (`../../../exchange/machine-that-learns--on--carry-and-locate.md`). Grip roll came out almost a one-wire axis (W6 alone). The vertical-axis angle is better done as a tangent translation than as a rotation.
- **work-as-datum** is developing a form referenced to the work.

My question from wave 2: **can the wires be arranged so that each turnbuckle
sets exactly one weld parameter?**

## The rule that makes a wire a knob

Take the three wires through the dot as fixed: to first order the dot cannot
move. Now change one of the other three wire lengths and hold the rest. The
gun must turn about an axis ω for which the two held rotation wires do not
change length: m·ω = 0 for each, where m is the wire's moment about the dot.

For that ω to be exactly one of Derek's axes, the two held wires must have zero
moment about it. A line has zero moment about an axis through the dot when the
line meets that axis (or runs parallel to it). A line that meets two axes
without passing through their common point lies in the plane of those two axes.
Hence:

| Knob | Its wire lies in the plane of… | Realised as |
|---|---|---|
| **Hole angle** | grip axis + vertical axis (the vertical plane of the grip axis) | a wire from the **grip-base loop**, pulling up in that plane |
| **Vertical-axis angle** | grip axis + hole axis | a wire from the **same loop**, pulling along the hole-axis direction |
| **Grip roll** | hole axis + vertical axis (the vertical radial plane through the dot) | a wire from an **outrigger** over the rim, pulling up in that plane |

This is Derek's example, with its lines placed:

- **His base loop, hung on a wire in Z with a bungee in X, is the hole knob plus
  the vertical knob.** The only change is that the "X" pull becomes a stiff wire
  along the hole-axis direction (15° off X at this pose), with the soft bungee
  opposing it as its preload.
- The loop wants to be exactly what he said: **complete and openable**, closed
  around a round collar on the shell's butt sleeve so the gun can roll inside it.
  Then the loop passes force through the grip axis whatever points its wires
  are tied to. That is precisely the "meets the grip axis" condition, and roll
  stays free for the third knob.
- **His tip loop is the virtual ball joint**, but only if its lines pass
  through the dot. A plain vertical wire from a loop 56 mm up the barrel misses
  the dot by ~40 mm horizontally, so every angle change would also move the
  dot. The loop becomes an outrigger whose three wires aim at the dot.
- **His third ring is the roll knob.** It has to sit in the vertical radial
  plane through the dot. As he said, it also carries weight: 8.6 N here.

**What cannot be made one-knob with wires.** A fully diagonal six-wire layout does
not exist here.
- Every wire is sensitive to translation along itself, so no wire can be a pure
  rotation knob in a basis that includes all three translations.
- In the weld-language basis, the only wire that changes the vertical-axis angle
  alone lies on the horizontal line through the *tube axis* at cap height, which
  passes through the tube wall.

So the dot's *place* is best moved **at the work**: couch X/Z slides under the
rotator, as in `isocentric-couch-and-gantry.md`. The three dot wires then stay
fixed as calibration, and their only job is to make the dot the pivot. That is
my chain rule again (translations nearer ground than rotations), here made of
wires. Branch W-A below keeps the dot wires as knobs and states their leak.

## The layout (from a search, not hand-placed)

The search kept the rotation wires inside their planes and the dot wires on
lines through the dot:
- the X wire horizontal, within ±30° of radial;
- the Y wire along the tangent;
- the Z wire in the tangent plane.

It chose two downward preloads whose lines miss the tube. It maximised the
worst-case minimum tension and ranked layouts by dot stiffness. The load cases
were gravity, the preloads, ±5 N at the dot on every axis, a 5 N trigger push
and 5 N umbilical pulls at the grip base. Anchors sit 400 mm from their
attachments. Only 4 of 40,000 candidates kept every wire ≥ 5 N, so feasibility
is tight.

| Wire | Attach (scene mm) | Pulls toward | Tension at rest |
|---|---|---|---|
| W_x (dot, calibration) | (117, 28, 146) outrigger foot, dot height, outboard | horizontal, az 27° | 11.5 N |
| W_y (dot, calibration) | (62, 62, 146) outrigger foot, beside the OD | +Y (tangent) | 14.4 N |
| W_z (dot, calibration) | (62, −27, 183) outrigger, tangent plane | up-back, el 54° | 13.9 N |
| **W_grip** | (114, −14, 218) outrigger, radial plane | up, el 67° | 8.6 N |
| **W_hole** | grip-base loop (−1, −234, 286) | up, el 69° | 37.9 N |
| **W_vert** | grip-base loop | along the hole-axis direction | 17.7 N |
| preload 1 (bungee/balancer) | grip-base loop | down-inboard, el −48° | 24 N |
| preload 2 | outrigger (132, −25, 206) | down, el −73°, outboard of the OD | 21 N |

The outrigger is one printed part. It runs from the shell's nozzle end over the
rim to a small plate at the dot's height, 25–55 mm outside the OD, with a riser
for the Z and roll eyes.

## How independent the knobs really are

**First order** (1 mm on one wire, the others held):

| Wire | X mm | Z mm | seam ° | vertical ° | hole ° | grip ° |
|---|---:|---:|---:|---:|---:|---:|
| W_grip | 0 | 0 | 0 | 0 | 0 | **+0.84** |
| W_hole | 0 | 0 | 0 | 0 | **−0.33** | 0 |
| W_vert | 0 | 0 | 0 | **+0.24** | 0 | 0 |
| W_x | **+1.12** | 0 | 0 | −0.27 | −0.03 | +0.36 |
| W_z | 0 | **+1.24** | 0 | +0.03 | +0.38 | −0.96 |
| W_y | −0.50 | +0.73 | +0.93 | −0.77 | +0.13 | −0.82 |

The three angle knobs are exactly single to first order. The dot wires move the
dot cleanly (W_x along X only, W_z along Z only) but leak 0.3–1.0° of angle per
mm, which is why they are left as calibration. W_y is a calibration screw only.

**Finite moves** (exact wire geometry, the other five held):

| Knob turned for | dot moves (X, Z, Y) mm | other angles move ° |
|---|---|---|
| grip 2° / 5° / 10° | 0.03, 0.02, 0.01 / 0.16, 0.11, 0.08 / 0.61, 0.43, 0.34 | ≤ 0.01 / ≤ 0.03 / ≤ 0.12 |
| hole 2° / 5° / 10° | 0.00, 0.07, 0.04 / 0.01, 0.49, 0.29 / 0.11, 2.6, 1.4 | ≤ 0.03 / ≤ 0.18 / ≤ 0.99 |
| vertical 2° / 5° / 10° | 0.03, 0.05, 0.05 / 0.18, 0.30, 0.30 / 0.78, 1.3, 1.3 | ≤ 0.04 / ≤ 0.26 / ≤ 1.1 |

- The pivot is exact only to first order. The dot drifts with roughly the square
  of the angle: under 0.08 mm for a 2° step, up to 0.5 mm at 5°.
- The knob's own gain also bends: 10° of hole asked gives 12.3°.
- **In steps of ±2° around a recipe this is a one-knob machine.** For bigger
  changes the camera shows the dot's drift, and the couch X/Z (clean) returns it.
- For a new neighbourhood (±10° away), re-place the anchors on their slotted
  mounts so the planes hold at the new pose. carry-and-locate and
  machine-that-learns reached the same "layout per neighbourhood" rule.

**Build tolerance.** A rotation wire 2 mm out of its plane makes the *other two*
angle knobs leak into its rotation by 0.002–0.027° per degree. The planes need
millimetre care, not precision.

## Reading, recording, returning

- **Each angle wire ends on a lead-screw anchor slide** (Tr8×2: 2 mm per turn,
  dial of 100 divisions = 0.02 mm), aligned with the wire.
  - Resolution per division: grip 0.017°, hole 0.0066°, vertical 0.0048°.
  - Range over 50 mm of screw: grip ~42°, hole ~16°, vertical ~12°.
  - An AS5600 on each screw writes the record.
  - A wire only ever pulls, so the nut is always loaded the same way. Backlash
    never enters, and "approach from one side" is automatic.
- **Turnbuckles** (Derek's) do the coarse length when a new neighbourhood is set
  up. After that they are painted.
- **The dot** is read by the dot camera on the rotator base, and moved by the
  couch X/Z micrometers.
- **Walk test** each session: sweep each angle screw ±2° with the red dot on the
  corner phantom. The dot's trace measures the triad's concurrency, and the
  triad's anchors carry two perpendicular calibration screws to null it.
- **Baseline** is three dial numbers and two couch micrometer numbers. Returning
  is setting them; the tension-loaded nuts take up their own backlash.
- **A second person** reads a card of five numbers and compares the camera image.

## Carrying, cable and use

- **Carrying.** The wires carry everything. The vertical components of W_hole,
  W_z and W_grip balance the gun's 15 N plus the preloads' downward pull
  (about 38 N). There is no separate carrier: C&L's "the load path is the
  locator".
- **Umbilical.** It leaves the butt through the shell's sleeve, inside the base
  loop, then runs to its own saddle or balancer (bend radius ≥ 350 mm).
  - A 5 N residual pull at the grip base moves the dot 14 µm.
  - Rolling still twists the cable at the butt (~0.87× the roll, as C&L
    measured). The loop does not change that.
- **Welding wire.** The guide is on the gun, as in Derek's scene. The grip-roll
  knob moves the guide end only 1.8 mm per 5°, against 6.5–8.7 mm for hole or
  vertical changes (wave 2). Stick-out is reset with a gauge after a snip.
- **Setup.**
  1. Lower the gun into the loops with the preloads unhooked (a soft float).
  2. Hook the preloads. Every wire comes taut and the pose is the six lengths.
  3. Set the dot on the corner with the couch X/Z and the camera.
  4. Set the angles with the three screws.
- **Dry run and weld.** The gun is static on stiff wires.
  - Stiffness at the dot (1/16 in stainless rope, rigid frame assumed): 5 N
    moves it 25 µm in X, 21 µm in Y, 34 µm in Z.
  - Natural frequencies are 31, 50, 116, 191, 213 and 252 Hz. The 80 Hz wobble
    falls between modes: an assumed 1 N wobble reaction gives ~4 µm of dot
    vibration.
  - A wobble-frequency sweep through ~116 Hz meets a mode (~10 µm per N at
    ζ 0.02). **The wobble-frequency setting can therefore couple into dot
    vibration**, a one-knob concern peculiar to lightly damped supports.
    Viscoelastic inserts at the anchors would damp it.
- **Stuck wire.** 3–5 N of tangential drag moves the dot ~20 µm, and the stick-out
  bends first, so the head stays put for the snip.
- **Lift-off and tube change.** Unhook both preloads, and the up-pulling wires go
  slack as the gun is lifted. The three horizontal wires (W_x, W_y, W_vert)
  would stretch if the gun rose. Lifting 60 mm against a 400 mm horizontal wire
  needs ~4.5 mm of stretch, so they end in hooks that seat in printed V-notches
  and are unhooked first. Park the gun on a hook. On return, hook, preload, and
  the six lengths restore the pose. The hook seats are the repeatability (C&L).
- **Second closure** (inverted): nothing above the rim changes.
- **What "fixed" is fixed to.** The anchor cage, about 900 × 900 × 750 mm
  around the rotator, on the same baseplate as the couch. Anchors sit at the
  dot's height on +X and +Y, above the tube and behind it on −Y. The wires give
  ~150–350 N/mm at the dot, so the cage must be several times stiffer or it
  dominates. Triangulated extrusion or welded steel tube.

## Branches

- **W-A, dot wires as knobs.** Leave the couch out; W_x and W_z become the
  X/Z knobs. The dot moves cleanly along X or Z, but each mm leaks 0.3–1.0° into
  the angles (table above). For per-tube trims of 0.1–0.3 mm that is 0.03–0.3°,
  and the camera cannot see it. Acceptable only if the angle process window
  proves wide.
- **W-M, motorised (Derek's automated vision).**
  - Three NEMA 17s on the three angle screws give three motors for three of
    Derek's angles, with no inverse kinematics.
  - Two couch motors move the dot. The AI's dry-run grid is a product of five
    axis lists.
  - The drift (about θ² × 25–65 mm) becomes a known model term that a camera
    calibration fits: the standard cable-robot calibration machine-that-learns
    described.
- **W-C, constant-force preloads.** Bungees change force as the angles change the
  preload geometry (MTL: ~4 N over a 40 mm move against margins of a few N).
  Constant-force springs or spring balancers keep the margins. The SUS301
  constant-force spring on Prime is a low-volume listing; balancers are the
  volume part.

## Wave-5 branches (after who-moves-what's re-run)

Source: `../../../exchange/who-moves-what--on--one-knob-one-parameter-w4.md`.
They vendored my search unchanged, reproduced my result (2 of 40,000 feasible,
5.95 N), then relaxed one assumption at a time. The original layout above
stays as it was.

**W-R1 — the sixth wire anywhere in its own plane.**
- *Their finding.* My rule only requires the vertical-angle wire to lie in the
  (grip axis, hole axis) plane. My search needlessly tied it to the grip-base
  loop and to within ±35° of the hole-axis direction. Freeing it within the
  plane (attached on the grip axis at 60–330 mm, any in-plane direction) gives:

  | | Feasible of 40,000 | Worst-case margin |
  |---|---:|---:|
  | Original search (my load box) | 2 | 5.95 N |
  | W-R1, my load box | 12 | 18.5 N |
  | W-R1, their sequence-of-use loads | 25 | 13.9 N |

  Grip and hole stay exactly single (W_grip: G only, +0.581°/mm; W_hole: H
  only, −0.283°/mm).
- *The best layout.* The wire hangs from a shell boss 112 mm along the grip
  axis, in the air under the barrel, pulling almost horizontally toward −X over
  the tube to an anchor on the far side.
- *I agree.* It is the correct reading of my own rule, and it removes the thin
  margin that was my break 1.
- *What it changes, beyond their note:*
  - The wire runs **over the open tube**, about 50 mm above the rim. It crosses
    the side I had reserved for snipping a stuck wire and for the dot camera.
    It needs a hook and V-notch (as they say), plus a camera sightline check.
  - It also sits in the rising plume. Stainless rope warming 10–30 K over part
    of 400 mm grows 0.05–0.15 mm **[estimate]**. The boss is 112 mm along the
    grip axis rather than 279 mm, so this wire's gain is about 0.6° of yaw per
    mm (moment arm ~94 mm about the vertical axis), and the growth is 0.03–0.09°
    during a weld. Small, but it is the first thermal term in this idea, and
    under W-R2 the Y slide can trim it.
  - Keeping W_y and W_z on the cold (−Y) side is an unrun constrained search
    (theirs to note, mine to run).

**W-R2 — move the vertical angle to the couch Y slide.**
- *Their allocation.* With the Y slide (1.08 mm per degree, with the X
  correction R(1 − cos φ) applied by the couch X), the sixth wire becomes fixed
  calibration.
- *Gains:*
  - Yaw becomes exact, not first-order: nothing leaks into grip or hole.
  - Its range is ±23° on 25 mm, against ±6° per neighbourhood by wire.
  - A yaw change moves nothing above the rim: wires, cables and gun stay put.
- *I agree, with one nuance.* A yaw change is then *two* couch moves (Y, plus
  the analytic X correction), or one with a printed cam, or a parallelogram
  couch, exactly as in my isocentric branch B-Y. The side-effect is analytic and
  camera-visible, where W_vert's was a θ² drift partly invisible to the camera.
  So W-R2 is better, and I make it the default.
- *Knob count after W-R1 + W-R2:*
  - two angle wires (grip, hole);
  - three couch axes (X, Z, Y = vertical angle);
  - four wires fixed and painted.
  Five weld parameters on five knobs; the sixth, position along the seam, does
  not matter.

**Tried by them and not adopted** (honest negatives, kept visible):
- **W-R3, sequence-of-use load cases** (the trigger closes in the shell; real
  umbilical exit direction; stuck-wire drag in +Y only): 3 layouts, 6.0 N. The
  margin problem is geometric, not an artefact of my load box.
- **W-R4, every wire leaning up the corner's escape direction,** so a lift
  slackens all six and no hooks are needed: 1 layout, 5.9 N, 3–5× softer. The
  hooks and V-notches stay.

**The combination they built from this rule:**
`../../who-moves-what/ideas/gravity-in-the-gun-plane.md`.
- *Their finding.* With the work and gun tilted to τ* ≈ 32.5° about the
  tangent, the gun, beam, grip axis and CoM lie in one vertical plane. Gravity's
  moment about the grip axis falls from 0.77 to 0.13 N·m and about the vertical
  axis is zero, so **only the hole wire carries gravity, tensioned by it.** One
  hanging wire from Derek's base loop sets the hole angle; grip and yaw need
  only light locks.
- *Through my view.*
  - It is the plane rule at its most economical: one loaded wire, two nearly
    weightless angles.
  - It inherits the tilt's own couplings, which I raised in wave 4. The
    first-closure tube tips in its nest near 30.5°, so it must be clamped, and
    the tilt changes the gas behaviour as well as the pool.
  - Its preloads are gravity and ballast, which is what finally removes the
    tension-margin fight.
- *Uncertain:* the process effect of the tilt, and the real gun's plane at τ*
  (the scan).

## Trying to break it

1. **Tension margin is thin.** Only 5.9 N worst case, from 4 feasible layouts in
   40,000. The real gun mass, CG and umbilical force can erase it.
   *Repair:* raise the preloads (margins scale with preload, at the cost of
   anchor loads) or add a seventh wire, as machine-that-learns suggests; tension
   then becomes commanded. *Left:* needs the measured gun.
2. **The outrigger lives on the hot side.** The search put W_x and W_y on the +Y
   (departing) side at the dot's height, 25–55 mm outside an OD that has just
   been welded. *Repair:* metal eyes and a stainless heat shield on the
   outrigger foot, or constrain the search to the −Y side (it found less margin
   there). *Left:* temperatures unmeasured.
3. **Clutter near the dot.** The outrigger, the nozzle and the wire guide all
   live within ~60 mm of the dot, and the camera needs a sightline. The camera
   keep-out belongs in the search (MTL's point).
4. **Large moves leave the planes.** Beyond ±5°, re-place anchors (above).
5. **Frame and hooks.** The pose is only as good as the anchor cage and the
   hook seats. Both are measured by the walk test, and a push test while the
   camera watches.

## What it contributes

Derek's own suspension picture turns out to contain the rule for a one-knob
machine:
- hang the base loop on a vertical wire and it is the hole knob;
- pull it along the hole axis and it is the vertical knob;
- put the third ring in the radial plane and it is the roll knob;
- aim the tip's lines at the dot and they make it the pivot.

It has no joints to lock, shift or wear, lift-off and return are free, and the
parts are rope, turnbuckles, lead screws and printing.

**Biggest open problem:** it is exact only to first order, with thin tension
margins that depend on the real gun. It needs the gun's mass and CG, and one
physical prototype with the walk test, before the numbers mean much.

## Questions for Derek

1. Gun mass and CG, and umbilical pull at the butt. These set whether the
   layout stays taut.
2. Is a ~0.9 m anchor cage around the rotator acceptable in the shop?
3. Is ±2° per neighbourhood enough range for exploring? (Beyond that, anchors
   move.)
