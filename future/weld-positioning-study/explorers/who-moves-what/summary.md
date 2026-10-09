# who-moves-what — summary entries

**View.** Every relative motion between gun and corner, and every phase of use, is
owned by some body — gun, shell, support, fixture, tube and rotator, or a setup
step — at some rate: per session, per recipe, per tube, per weld.

**Pose convention.** Poses are the scene's dials. The opening pose is grip 45 /
hole dial 30 / vertical −15, which `main.js` passes to `posePoint` as hole −5.

**Sourcing.** Details are in `../../sourcing/who-moves-what.md`.

## 1. Still gun, moving work *(beyond Derek's examples)*

`ideas/still-gun-moving-work.md` · `sketches/s2-still-gun-moving-work.svg`,
`sketches/s1-plan-yaw-by-work-slide.svg`

**Idea.** After setup the gun, shell, umbilical and wire conduit never move. The
work takes every motion that doesn't change the puddle's relation to gravity. The
tube's symmetry is what makes this cheap: sliding the work along the tangent *is*
the vertical-axis yaw, at 1.08 mm per degree plus an X correction of r(1 − cos φ).
A plain cross-slide therefore owns both radial position and yaw, with no rotary
joint.

**Loads, position, fixed.**
- A bench stand carries the gun through a printed recipe block (roll and hole).
- The rotator sits on three fine Z screws, on a drawer whose carriage climbs end
  ramps into three vees on the cross-slide's top plate (branch 1d, from
  sequence-of-use).
- A stationary plate head (sequence-of-use) holds the plate at the dot's position P:
  port plugs, three pads re-clocked to 30°/150°/250° to clear the barrel at the true
  pose, and a rim flag at P + 6.35 mm. Tube length drops out.
- "Fixed" is one base plate under both the stand and the cross-slide.

**Breaks and repairs.**
- The wire tip in the corner blocks a sideways exit (sequence-of-use). The tube must
  drop at least 10 mm and leave toward +X on a diagonal ramp; re-checked at dial 30.
- Lateral drawer play is a yaw the dot camera can't see (sequence-of-use). The vees
  remove it.
- The plate and tacks were missing from the sequence. The plate head covers them,
  and the tacks become indexed pulses.
- Runout during the weld is not followed. The 3b replay under the work covers it
  (entry 3).

**Parts** (observed on Prime).
- VEVOR compound table, $135.90: X 210 / Y 110 mm travel, 66 lb, 50+ bought/month.
- HGR15 rail kit, $48.99.
- Printed: recipe blocks, ramps, pad carriers.

**Contribution.** A fixed pixel for vision, static cables, and yaw with no hardware.

**Open.**
- Whether un-followed runout matters (the process window).
- Face runout against the stationary pads while indexing.
- Plugs in the ports while welding.
- 150–180 mm of extra stack height (estimate).

**Branch 1c** re-reads Derek's table-opening example with X/Y moved to the shelf.

## 2. Protractor and stub *(beyond Derek's examples)*

`ideas/protractor-and-stub.md` · `sketches/s3-protractor-and-stub.svg`

**Idea.** Both gun rotations become joints through the dot. At room yaw 0 the grip
base stays 279.2 mm from the dot, in the vertical tangent plane, at every hole tilt.
- A carriage on an arc centred on the hole axis gives hole tilt.
- A bearing on that carriage, its axis pointing at the dot, gives grip roll. That
  bearing is a stub: a rigid shell arm along the grip axis, about 65 mm behind the
  butt, turning in two small bearings.
- A balancer at the centre of mass carries the gun; the joints only locate.
- Adjustments: a vernier on the arc (6 mm per degree at R 345), a roll dial, a Y
  slide for yaw, and X/Z on the work.
- "Fixed" is the arc's column.
- Calibration: three shell adjustments and two tilt screws on the stub housing put
  the dot on both axes. A dot that misses an axis by e traces a circle of radius e
  when that axis turns.

**Breaks and repairs.**
- The stub sits 345 mm from the dot, so it needs the balancer; the residual sag
  isn't estimated yet.
- Roll swings the fiber: 45° of roll gives 25° of swing and about 37° of twist at
  the exit. Repair: a free loop, a swivel anchor, and releasing and re-setting the
  umbilical clamp around every angle change (sequence-of-use).
- At the true pose the fiber heads for the carriage 79 mm out. Repair: move the arc
  about 60 mm toward −X.
- It has no lift-off of its own.

**Branches.**
- 2a: a trunnion on the hole axis outside the tube.
- 2b: an open C-ring around the butt. A closed 6820 is ruled out because the fiber
  can't be threaded through it.
- 2c: the arc on Derek's gantry.

**Parts.** SendCutSend 6061 plate, ±0.005 in cut tolerance observed, lead time not
read. V625 V-groove rollers, $8.81 on Prime (thin listing). borrowed-ecosystems' F
reuses the stub.

## 3. The tube carries the reference: 3a rider, 3b map and replay, 3c gauge foot *(beyond Derek's examples)*

`ideas/tube-carries-the-reference.md` · `sketches/s4-rim-rider-section.svg`
(a schematic section, pose-independent)

**Idea.** The rotating tube sets the gun's radial position and height, so there is
no per-tube setup.

- **3a — rider.** A carriage hung from a balancer, located by exactly six
  constraints: a tripod of ball transfers on the plate face (height and both tilts),
  two rollers on the OD (radial and yaw), and a soft tether for travel around the
  tube. The tube's symmetry makes the tether harmless. The first version also had
  an X–Z rail float, was over-constrained, and was repaired.
- **3b — map and replay.** One dry lap maps the corner against table angle. A small
  X–Z stage replays the map, clocked by the rotator's 14,400 pulses per revolution.
- **3c — gauge foot.** A retractable foot touches the plate at 3–4 angles between
  tacks, and the gun is set to the mean (sequence-of-use). The foot then lifts clear.

**Breaks.**
- A contact placed φ from the dot passes 2 sin(φ/2) × the eccentricity and 2 sin φ ×
  the ovality: 0.35 and 0.68 at 20°. Whether riding helps at all depends on the
  tube's harmonic content.
- At the true pose the barrel descends through −9° to −80°, on the arriving side.
  Plate-face pads at −10° to −40° interfere by 7–14 mm, and they clear only from
  −60°, where riding is no better than a fixed gun. So 3a's plate-face form doesn't
  fit.
- Unaffected: sequence-of-use's rim-top saddle, 3b and 3c.

**Parts.** Stainless CY-15A ball transfers, $9.99 for 4 on Prime (thin listing;
standard size).

**Contribution.** The runout-transfer arithmetic, and 3b as the cheapest experiment
to decide whether following matters.

**Open.** The runout harmonics; contact temperatures.

## 4. Carrier and seat: Derek's monitor arm and suspension *(Derek's examples)*

`ideas/carrier-and-seat.md` · `sketches/s5-carrier-and-seat.svg`

**Idea.** Derek's arm and loops are carriers: they take weight, cable load and every
large motion. Something small and stiff locates, and only while docked.

**Variants.**
- **D1:** a gas-spring monitor arm docks into a kinematic seat on a post from the
  rotator base, which is the same datum as the nest.
- **D1-r:** the arm, with a few mm of spring float (sequence-of-use's lid transfer),
  hands the shell onto a short escape rail leaning 32.5° toward the tube's centre.
  The gun slides onto a stop under 0.84 of its weight, so the wire tip arrives along
  the escape direction instead of being dragged down the lip.
- **D2:** Derek's two loops already lie nearly on his grip axis (7.5 mm off at the
  nozzle tip). Made into journals concentric with it, they form a roll hinge.
- **D3 (sequence-of-use):** one V-slot trolley carries both balancers and the cable
  saddle.

**Breaks and repairs.**
- **Seat preload:** it must exceed 2FL/b against the cable pull F at lever L across
  ball span b. That calls for a 150–200 mm span; the Thorlabs KB75/M's 29 N magnets
  are too weak at 75 mm.
- **Docking shock on the gun's motor:** a cam latch, not snap magnets.
- **D2's roll is not free** (sequence-of-use). At the true pose gravity puts
  0.41–0.72 N·m on it. Repair: a lock on ring B, with the third ring as trim.
- **Vertical lifts drag the wire up the lip:** lift along the escape direction.

**Parts** (observed).
- HUANUO monitor arm, $39.99 Prime, 16.5k ratings, 500+/month, rated 4.4–19.8 lb, so
  its minimum load may exceed the gun.
- QWORK balancer 2-pack, $16.97, 50+/month.
- Thorlabs KB75/M, $117.27, with 21 µrad mean and 82 µrad max reseat.

**Open.** Gun mass and centre of mass; cable pull at the grip; how well a rail stop
repeats.

## 5. Tilt cradle and escape rail *(beyond Derek's examples)*

`ideas/tilt-cradle-escape-rail.md` · `sketches/s6-tilt-cradle-escape-rail.svg`

**Idea.** Incline the work axis. An isocentric cradle pivots on the station tangent
through the dot and carries the gun, rotator and plate head together, so the tilt τ
changes only gravity. τ = 0 is today's geometry.

**At τ\* ≈ 32.5°:**
- the gun lies flat in a vertical plane;
- the fillet bisector is 12.5° from vertical, nearly a flat fillet (1F);
- the corner's escape direction is vertical, and a straight lift along it clears the
  gun for 32 of 32 feasible recipes after 43 mm, upright or tilted.

**Tilts in terms of Derek's dials:**
- 1° about the tangent = grip +1.11°, hole −0.26°, vertical −0.55°.
- 1° about the radial ≈ hole +0.97°.

Weight runs down the rail to a stop. A quadrant and pin set τ and carry no
precision. "Fixed" is the cradle.

**Breaks and repairs** (one-knob-one-parameter, adopted).
- **T-b1:** the stop moved standoff 1.185 mm and yaw 0.59° per mm. It becomes a fixed
  ball-in-vee stop, with S (along the beam) and A (across the corner) flexure stages
  from their flexure trim head.
- **T-g:** a work-angle pivot coaxial with the cradle axis, so gravity and work angle
  become two factors.
- **Tipping:** the unclamped first-closure tube tips at about 30.5° and slides from
  about 17°; the turntable lifts at 30–40°. Repairs: a band clamp to the turntable, a
  preloaded catch, a sprung seat, and a two-inclinometer tilt walk test.
- **Gas:** buoyancy matters over the lip, not at the pool, which suggests a tilt ×
  flow experiment read by heat tint.
- One point of emphasis here: the coupling comes from using the stop as a knob, not
  from the rail itself.

**This is a process change.** A Bond number of 0.09–0.34 for 1.5–3 mm pools
(estimate). Argon spills from the recess beyond 2.9° of tilt. The float stays clear
only while τ < 90°.

**Branches.** T-a (the rail fixed in the room), T-c (the work takes the angles), T-d
(beam vertical, seam sloped 27°), T-e (tube horizontal), T-f (VEVOR HD-10
positioner: $254.90 Prime, 1–12 rpm so it can't reach 5 mm/s, 25 ratings).

**Parts.** XIKE UCP204 pillow blocks, $26.99, 234 ratings. Klein 935DAG angle gauge,
$32.97, 5K+/month. An HGR15 rail.

## 6. Gravity in the gun's plane *(a combination that draws on Derek's suspension)*

`ideas/gravity-in-the-gun-plane.md` · `sketches/s7-gravity-in-the-gun-plane.svg`

**Idea.** At the tilt, gravity's torque about the grip axis falls from 0.77 to
0.13 N·m for a 1.5 kg gun, reaching zero near 38°. About the vertical axis it is
always zero, so the hole axis carries all of it (1.3 N·m). One of Derek's angles is
loaded; two are nearly weightless.

**What it joins.**
- work-as-datum's plate hanger and dot-centred sprung cup: the work fixes the dot,
  and every rotation stays free.
- one-knob-one-parameter's hole wire from Derek's base loop, and their plane rule,
  so each support is one knob.
- Derek's loops as roll journals, with a friction lock.
- A pin in a vertical slot for yaw.
- sequence-of-use's trigger, stickout and umbilical rules.
- The tilt.

**Loads, fixed, use.**
- Gravity carries the gun: about 8 N into the cup, and 6.8 N in the wire (16.6 N
  with a 1 kg weight on the loop, which adds nothing to the cup).
- The umbilical's free loop leaves its clamp vertically, so it acts as ± ballast.
- "Fixed" is the plate for the dot, and the cradle column for the angles.
- Docking is a straight drop; lifting releases everything.
- The tilt knob measures the real gun's centre-of-mass plane: step τ until the hung
  gun stops turning.

**Breaks and repairs.**
- A cable pulling along its natural exit pushes the cup sideways. Repair: a vertical
  free loop and sprung outer pads.
- Attaching the wire nearer the dot drives the cup load negative, so keep it at the
  grip base.
- It runs at 32.5–38°, above the ~30.5° at which the unclamped tube tips, and the cup
  adds about 0.6 N·m on the downhill side. The clamp and catch are mandatory.
- The cup protects the dot's position, not the angles.
- At this tilt, work-as-datum's and carry-and-locate's cups would face much smaller
  preload problems. Not yet written up.

**Parts.** Tr8×2 lead screws, $12.99 Prime, 91 ratings. A 1 kg hooked weight, $28.09
(thin listing; any steel will do).

## 7. Branches contributed to others

**sequence-of-use's lid carrier**
(`../../exchange/who-moves-what--on--sequence-of-use.md`,
`sketches/w2-lid-reallocated.svg`). Each freedom goes to one body, by phase and rate:
- the seat moves behind the station, on posts outside the rotator base (latch
  ≥ 33 + 7 N, so their 60 N gives 1.5×);
- the recipe block, yaw slide and radial slide go on the lid;
- tube length goes on the work, via three belt-linked screws (uxcell 2GT belt loop,
  $9.09).

Checked with their proxy at the true pose:
- their hinge family survives (16 of 160);
- every feasible recipe escapes with yaw done by rotation;
- yaw done by slide escapes only from −25° to +5°;
- 3.2 mm of tube length, if not taken up, puts the wire into the plate.

**Their gauge-set, lock-held.** Split by rate: a recipe block, lead-screw dials (no
lock step, so no lock shift), and a retractable measuring foot that touches between
tacks and maps runout.

**Their rim-riding saddle.** Plate-face contacts were suggested in wave 2. At the
true pose they interfere with the barrel's descent sector, so the rim-top form is
the one that fits (caveat added to the exchange file).

**one-knob-one-parameter's wired suspension**
(`../../exchange/who-moves-what--on--one-knob-one-parameter-w4.md`).
- Freeing the sixth wire anywhere in its plane raised feasibility from 2 to 12 of
  40,000 layouts, and the margin from 5.95 to 18.5 N, with knobs still single.
- Yaw on a couch Y slide is exact and needs no wire.
- Load cases taken from the session sequence barely helped: the margin problem is
  geometric.

## Transferable pieces

- **Yaw by slide.** Tangent travel is the relative yaw: 1.08 mm per degree, with an X
  correction of r(1 − cos φ). A Y error is a yaw error. It serves the weld, but a
  fixed hinge's escape tolerates only about ±25° of it.
- **The escape direction.** (−0.537, 0, 0.844) in the tube frame: 32.5° from the tube
  axis toward the centre, 12.5° from the fillet bisector. A straight lift along it
  clears every feasible recipe after 43 mm. It works as a rail, as a dock's last
  approach, or as the vertical once tilted. Other explorers' docks have not yet been
  checked against it.
- **Separate weight from location.** Soft carriers carry; stiff, lightly loaded
  locators locate.
- **Gravity-neutral vs gravity-changing motions.** X, Y, Z, spin and yaw can go to
  the work. A tilt about the tangent is mostly grip roll; about the radial, mostly
  hole.
- **The umbilical.** Rings around it must open (the fiber can't be threaded without
  unplugging the QBH). It leaves about 30–35° off the grip axis on the proxy, so roll
  swings and twists it.
- **The spin belongs to the tube.** A gun orbiting a still tube would twist the fiber
  about 380° per weld.
- **Tube length** is taken on the work, against a rim flag.
- **The wire tip in the corner** blocks any horizontal exit: drop first, then leave
  toward +X on a diagonal ramp.
- **The barrel's descent sector** at the true pose (−9° to −80°) is on the arriving
  side; anything riding the plate there has to avoid it.
- **Recipe blocks** can be computed about the dot, so swapping one leaves the dot in
  place.
- **The one-knob plane rule,** plus placement freedom within each wire's plane.

## Questions only Derek's observation can answer

1. The real nozzle-to-dot standoff, stickout and wire pullback. Does the wire retract
   clear of the 6.35 mm recess?
2. Does the HMI's red-light centring also move the process beam, and in which
   direction?
3. Gun mass and centre of mass (with shell); umbilical and conduit pull at the grip;
   trigger force and travel.
4. Is the QBH ever unplugged at the gun?
5. One indicator lap on a seated tube: is the runout mostly eccentric or oval?
6. Which table direction is used, and which side does the wire arrive from?
7. Is the tube clamped in the nest for the first closure, and would a band clamp on
   the OD near the nest be acceptable?
8. May 316 plugs or nipples sit in the ports while welding?
9. Is a tilted (non-downhand) trial worth running, 0° against 32.5°?
