# borrowed-ecosystems — notebook

Viewpoint: somebody already mass-produces most of this for another purpose;
design whole stations from that parts bin plus printed parts fitted to the gun.

## Wave 1 — 2026-09-28

### Read
shared-context, working-method, examples-and-history; `weld-position.md`,
`pose.js`, `weld-rotation-rig.md`, rotator README; manual pages 12, 17, 18, 20,
21, 32; the XLaserlab product page; skimmed "Welding arm 3" for gun-mass and
umbilical assumptions (agent estimates, not used as requirements).

### Tools made
- `geometry.py` — Python copy of `pose.js` with landmark points of the gun proxy
  (nozzle, drawer, body, wire bracket, trigger, grip base, a CG proxy).
- `calcs.py` — gravity torques about the three dot axes, rider following error,
  hook-spring coupling, balancer pendulum, belt-gantry stiffness, umbilical loop,
  hole-rotator loads.
- `sketches/svgkit.py`, `sketches/make_sketches.py` — sketches drawn from the
  proxy pose, so gun/wire/cable positions are the scene's, supports schematic.

### Things found that matter beyond my view (flag to coordinator)
*Items 2–5 were computed with the hole dial passed straight into the pose math
(i.e. at hole dial 65, a reachable but not the opening orientation). They stay
below, labelled; the corrected values at the true opening pose are in the
wave-2 section.*
1. **The laser only fires with conduction between gun and work** [Manual p.32:
   "Unconducted Alarm" — safety clip on the work *and* contact between torch and
   workpiece; XLaserlab page: fires only when the gun touches metal]. With wire
   feed the wire touching the work presumably supplies it. So in every
   arrangement the wire is a mechanical contact between gun and joint during the
   weld, and a wire that lifts off stops the laser. [Inference: which part of the
   gun makes contact is not stated.]
2. **[Wrong: my own mis-drawn grip; see wave 2]** **Grip-axis roll twists the cable.** In the scene proxy the cable leaves the
   grip butt within 1.3° of the grip axis (dot → cable exit). Rolling about that
   axis therefore rotates the cable about its own length at the exit — twist, not
   swing. Small exploration ranges spread along metres of cable; ±45° is not
   small. [Proxy geometry; the real gun's grip direction needs the scan.]
3. **[Valid at hole dial 65, not at the opening pose]** **At the opening pose the gun stands nearly upright over the dot**
   (barrel 71° elevation, body over the tube's centre, grip base ~253 mm above
   the dot). Gravity torques about the dot axes are small: hole 0.4–0.75 N·m,
   grip 0.2–0.4 N·m for 1–2 kg gun + shell; zero about the vertical.
4. **[Valid at hole dial 65 only]** **Umbilical loop** (R 350 mm while emitting): exits 485 mm above the bench at
   64° elevation heading −Y; apex ≈ 680 mm above the bench; ≈ 665 mm of
   horizontal run before it hangs vertically. Every arrangement needs a support
   near that apex.
5. **[Hole dial 65]** Nozzle tip at the opening pose is ~9 mm *above* the rim, inside the bore by
   ~5 mm; only the wire (and beam) go below the rim.

### Arrangements developed
| File | One line | Depth |
|---|---|---|
| `ideas/a0-monitor-arm-holds-gun.md` | Derek's original, as proposed; broken honestly; its strong roles (weight relief, parking, carrier) | medium |
| `ideas/a1-arm-carries-tube-locates.md` | Arm (or balancers) floats the weight through a soft hook at the CG; the shell rides the rim ahead of the puddle on V-groove bearings; tube locates 5 DOF, a breakaway tether the 6th | deepest |
| `ideas/a2-arm-into-kinematic-dock.md` | Arm carries; a 3D-printer-toolchanger ball/groove dock on a bench post locates; gun lifts off and returns exactly | light |
| `ideas/b-nodal-head.md` | Panorama-head / machinist parts arranged so hole and grip rolls pivot on the dot; cast-iron cross-slide moves the tube in X/Y; Z at a column | deep |
| `ideas/c-engraver-gantry.md` | Diode-engraver XY frame on legs over the rotator with a ball-screw Z carrying the shell; G-code + camera for dry-run search | medium |

### What developed most
- A0 → A1: the monitor arm is a zero-rate carrier with friction; it fails as a
  locator but is excellent at carrying and parking. Coupling it through a single
  soft hook at the CG (Derek's loop) stops its friction joints fighting whatever
  locates. Letting the rim locate removes runout/reseating from the dot: two
  contacts ahead at −30/−60° leave ~0.03–0.04 mm worst-case against the
  procedure's runout limits; a ±30° symmetric OD pair ~0.02 mm.
- B: the photography "no-parallax point" framing. The hole rotator must sit at
  the dot's height, just outboard of the OD, axis radial. The grip roll is the
  weak link: any single rotary element at the grip base is ~300 mm from the dot,
  so a compliant arc gives mm-scale dot motion for a 2 N nozzle force. Branches
  B0–B3 (wedges / clamp after setting / rotisserie rings / closed bearing
  threaded once over the cable).

### Neighbours looked at and left as roles, not arrangements
- Electric tapping arm (parallelogram keeps tool orientation, gas-spring
  float): right idea for "orientation fixed, XYZ free", but $350–1,999 with
  single-digit ratings per listing.
- Camera magic arms (2K+/month, $20): friction lock; good for the camera,
  umbilical saddle, conduit guide, not the gun.
- Three-axis motorised camera gimbals: axes meet near the payload CG, not
  ~200 mm away at the dot; would need to hold ~2 N·m continuously.
- Hand-drill press stands (lever Z with depth stop): the right function for
  lift-off/return, but low volume and known-sloppy; a ball-screw module does Z.
- Drill press itself as column: an 8 in drill press (WEN 4208T) has roughly a
  4 in throat, less than the rotator base's 125 mm half-width (estimate).
- Film-grip C-stands: floor reference puts the floor and bench legs in the loop.
- Geared heads (3-way): precise, but their axes are in the head, not at the dot;
  every angle change needs re-centring (software pivot).

### Questions for Derek's observation
1. Gun mass and CG (with and without the first metre of umbilical); trigger force.
2. Bore runout and ovality at the rim vs at the plate level on a tacked assembly.
3. Rim/lip movement near the start after one lap.
4. ID seam bead at the rim edge?
5. Where the motor tower and ground tower sit around the tube.
6. Would he disconnect the QBH once to thread a closed bearing around the cable?
7. Which part of the gun makes the conduction contact during a wire-fed weld?

### Notes on process
- Chrome: one own tab per session, closed at the end. Amazon: Prime-filtered
  searches; only product pages that showed a Prime badge were recorded.
- The shared scratchpad lists other explorers' render filenames; I did not open
  them.

## Wave 2 — 2026-09-28 (exchange with one-knob-one-parameter)

### Pose correction (my error, now fixed)
`main.js` passes `holeDial − 35` to `posePoint`; my `geometry.py` passed the
dial straight in, so every wave-1 pose number was at hole dial 65. Fixed in
`geometry.py` (pose_point now takes the dial value), the sketch kit now draws the
scene's own proxy (barrel sections, 34 × 34 × 135 housing, grip box raked
(−25,172)→(−111,232)), and the cable follows the scene: along the rake, onto the
grip axis within 70 mm, then R 350.

At the true opening pose (grip 45 / dial 30 / vertical −15):
- barrel 45° elevation, heading inward-back (plan az −130°); housing back at
  (−60, −144), 424 mm above the bench; grip base (−1, −234), 372 mm above the
  bench; nozzle ~5 mm above the rim, ~7 mm inside the bore; the gun lies back
  over the arriving (−Y) side and mostly outside the tube in plan;
- gravity torque about the hole axis 1.35–2.7 N·m (1–2 kg), up to 3.3 N·m over
  dial 15–45; about the grip axis 0.4–0.9 N·m (0.2–1.2 over roll 10–75°); both
  one-signed; zero about the vertical;
- umbilical apex ~420–450 mm above the bench (416 by one-knob-one-parameter's
  cable model, 453 by mine, which starts the R 350 bend 70 mm out), ~0.5 m of run
  back along −Y;
- the scene grip rakes 30° off the grip axis, so my wave-1 "1.3°" was an
  artefact of my own proxy.

What changed in my conclusions:
- **A1:** the wire crosses the arriving-side rim low (−15 to −30°); a rim wheel at
  −30° would sit 4 mm from it. The wave-1 rim stations are kept as the original;
  the arrangement now leads with OD wheels straddling the dot at ±30° 25 mm
  below it (radial) and rim wheels at ±60° (height), bracket rising at −75°. The
  CG is now ~150 mm from the rider, so the CG hook carries nearly everything.
- **B:** the hole arm runs back along −Y at 30° (the same spoke layout as
  one-knob-one-parameter); rotator torques are 2–4× larger; tube change is by
  sliding the tube along +Y, away from the gun.
- **C:** the gun top is ~430 mm, not ~487, so legs ~500 mm; the umbilical passes
  under the rear rail.
- **A0/A2:** geometry only; conclusions unchanged.
- **Sketches:** all regenerated at the corrected pose.

### Exchange work (file: `../../exchange/borrowed-ecosystems--on--one-knob-one-parameter.md`)
- Isocentric couch and gantry:
  - The Y drawer is a 0.93°/mm yaw knob the dot camera cannot see. Repairs: a
    kinematic drawer end, or a read Y knob that makes the couch table optional
    (circle symmetry).
  - The 6816 nose-first roll bearing cannot pass the proxy gun (145 mm
    silhouette along the grip axis). Repair: hinged clamshell rings (lens-collar
    or tube-ring class) around a printed sleeve on the grip axis behind the butt,
    with the roll set by a micrometer under a gravity-loaded lever.
  - Branch: the hole angle as a sine arm on a gauge-block stack.
  - Sketch `sketches/x-okop-gravity-sine-arms.svg`; numbers `calcs_exchange.py`.
- C-arm: the overhead yaw joint is redundant with the work's X/Y (circle
  symmetry). Deleting it removes the hanging-table problem and 4–6 kg overhead;
  optional printed X-from-Y cam for yaw purity. The C-arm then converges with
  the couch station minus its table.
- Recipe cartridges: hardened angle blocks / sine bar take the angle out of the
  print.
- Transfer back: my B should adopt their walk test and knob vocabulary. A1-S's OD
  wheels could be their X stop, removing per-tube camera trim.

### Open, added this wave
- Hinged lens collars that open: none of the Prime listings states it.
- Pivot preload and lock shift for a sine-arm pivot; stack hold-down vs umbilical
  tug.
- Whether Derek would take yaw as a read Y knob.

## Wave 3 — 2026-09-28 (objections worked through; new ecosystem)

### Objections from one-knob-one-parameter (`exchange/one-knob-one-parameter--on--borrowed-ecosystems.md`)
Their text was written against my dial-65 geometry; its geometry section is the
same correction I made in wave 2.
- **A1: wedge swaps pivot about the seat.** Agreed: 3.5–7 mm per 2°,
  8.7–17.5 mm per 5° at 100–200 mm. Wedges demoted to coarse recipe angles.
- **A1-G (their isocentric rider) adopted as a branch.** Chain: rider → XYZ →
  {wire mount; arc about the seam tangent through the dot}. My addition: a
  bought optics goniometer (Huanyu 65 mm, ±10°, worm, 0.05°) as the fine arc on
  a printed coarse wedge, centre found by the walk test (0.5 mm off = 0.09 mm over
  10°). The wire-on-carriage choice splits the conduit from the umbilical; both
  wire mounts kept as options.
- **A1-Y (curved Y concentric with the tube) adopted.** The rider already
  references the OD, so a printed concentric slide is accurate.
- **Stations.** Their −40/−70 proposal is superseded by my wave-2 OD straddle
  (±30° below the rim, 0.017 mm). The A1-G arc sits above the dot and does not
  meet those wheels.
- **C: "Y is an angle" and "a software pivot is only as single as its
  calibration" agreed.** C-G2 adopted: the vertical angle as a G2/G3 arc about the
  fitted tube axis (native to GRBL). Their closed grip-roll bearing pair cannot
  be fitted (145 mm silhouette), so my hinged-ring sleeve hangs from the Z module
  instead.
- **A2: the dock is a motion to a stop; the knobs are the XYZ under the
  receiver.** Agreed, noted in the file.
- **B: 6816 pair stiffness fine (~7 µm), fitting not.** Hinged rings carried
  into B; B and their gantry are one family, and the walk test is B's QA.

### New direction: film grip and stabilizers → `ideas/e-film-grip-carrier.md`
- Surveyed with Prime-filtered searches:
  - Industrial torque-reaction and zero-G tool arms: not buyable at volume.
  - Power-off EM brakes for a lock-by-release teach arm: only integrated brake
    steppers, ~1 rating.
  - Camera jibs: $500–750, ≤13 ratings.
  - C-stands and grip heads: 2,476 and 491 ratings, next-day.
  - Steadicam-type iso-elastic arms: FLYCAM Comfort 314 ratings ($209), Galaxy
    249 ($448, 2–5 / 5–10 kg springs).
- **E.** An iso-elastic stabilizer arm on a C-stand, a yoke-and-trunnion gimbal
  at the gun's CG, and the umbilical/conduit saddle on the same stand's boom.
  - Carrier only: horizontally neutral (a balancer line pulls back 6–9 N at
    300 mm aside), near-constant lift, no moments.
  - The tube rider (A1-S + A1-G) or a dock locates.
  - Rolling the stand parks carrier and cable together, so the umbilical keeps
    its shape.
  - Reviewers' main complaint is bounce (low damping), which is benign here;
    set-down may need a damper.
- **Sketch:** `sketches/e-film-grip-carrier.svg`; numbers `calcs_wave3.py`.

### Leads noticed, not developed
- **Welding fixture tables** (5/8 in / 16 mm hole-grid tables and their
  articulating arm rests, stops and pins) are a high-volume ecosystem that could
  be the common baseplate several explorers need, with every accessory pinned
  back into the same hole. Not sourced; for workspace-as-structure.
- **Video fluid heads.** Their tilt counterbalance spring gives torque ∝ sin
  (tilt from head-level). Mounted so the gun's CG lies on the head's "up" line,
  it would balance the hole-axis gravity torque at every hole angle, with fluid
  drag for hand steering. A branch for B / the isocentric hole axis; not sourced.
- **Engine load leveler** (automotive). A screw that moves the lift point along
  a bar sets a hanging load's attitude: a trim for balancer-hung carriers. Not
  sourced.

### Open, added this wave
- A real iso-elastic arm's vertical rate, hinge friction and mid-stroke range
  with ~2.5 kg.
- Goniometer centre height (unpublished) and whether ±10° fine range is enough.
- Gimbal-yoke clearance around the real gun.

## Wave 4 — 2026-09-28 (second exchange; one combination)

### Exchange with sequence-of-use → `../../exchange/borrowed-ecosystems--on--sequence-of-use-w4.md`
Subject: their monitor-arm session (park / hand / dock, CG bail, fixed saddle,
dock-gated solenoid, M2 pole arm + balancer).
- **E1/E2 (hand to dock).**
  - Their saddle at "~680 mm" is my wave-1 dial-65 figure. At the true pose the
    free apex is ~420–450 mm.
  - Forcing the cable up to 680 costs a butt bending moment EI/R = 0.3–1.4 N·m
    (EI 0.1–0.5 assumed), as large as their whole 0.65 N·m estimate.
  - Repair: the film operator's recipe of balance, then drag, then friction:
    saddle at the natural apex; bail pins offset 12–43 mm on a screw (an engine
    load leveler) to trim the cable torque; helical-grease drag plus ~0.1 N·m of
    friction; their lead-ins.
- **Solenoid.** The listing itself says the coil overheats in prolonged
  operation, and a weld holds the trigger ~54 s. Repair: an MG996R servo gated
  by the dock (47–78 N at a 15–25 mm horn), or hit-and-hold PWM, or their Bowden.
- **M2.** Monitor-arm swivel friction makes the balancer line lean 3–18° (30–200 mm
  on 0.6 m) before the anchor follows. Repair: bearing hinges (a mod, or my film
  arm E).
- **Transfer to me.** E gets their cradle, their dock-gated trigger and the
  positive-stop rule; my gimbal yoke needs the same trim and drag.

### Combination → `ideas/f-hand-steered-isocentre.md`
- **What it joins.**
  - one-knob-one-parameter's isocentre and walk test.
  - who-moves-what's protractor geometry and roll stub (a bearing around a shaft
    on the grip axis, the fibre off-axis).
  - sequence-of-use's hand state.
  - machine-that-learns' dot camera and wobble line.
  - Film/lamp counterbalance: zero-length spring or counterweight, drag, a
    bicycle disc-brake lock.
- **What it is.** Hole and roll joints through the dot, each weightless at every
  angle (both gravity torques follow exact sines: the hole torque is m g r sin α
  with α = 75° − dial; roll is 0.90 sin(roll) N·m at 1.5 kg), damped, lockable
  and read, steered by hand on tillers while the camera shows the dot staying put.
- **Modes.** Explore by hand; freeze with a brake (or a block); weld on a recipe;
  and a new "steer roll during a bead while the encoders log it" learning mode.
- **Breaks worked.** Balance residual (trim plus friction, since drag alone
  drifts); hand force (~0.006 mm); tremor (corner ~2 Hz at 1 N·m·s/rad); lock
  shift of a single-piston caliper (~0.03 mm; use dual-piston); hard stops;
  near-rim rotor; umbilical twist.
- **Biggest open problem.** Whether steering during a weld teaches anything, and
  the real mass and CG for the balancers.
- **Sketch:** `sketches/f-hand-steered-isocentre.svg`; numbers `calcs_wave4.py`.

### Housekeeping
No other explorer's code is imported. My geometry and calcs use my own
`geometry.py`; others' results are quoted with credit.

## Wave 5 — 2026-09-28 (final pass)

- **E vs sequence-of-use's critique** (`../../exchange/sequence-of-use--on--borrowed-ecosystems-w4.md`).
  Agreed: the umbilical, not pendulosity, sets a free gimbal's attitude off the
  tube (70–640 N·mm against 1–2 N·mm per degree).
  - Adopted: carry pins (E-s), a lower CG (E-p), LAND/WELD stops (E-z), their
    stand-hung plate head, and a stickout gauge in the docking cup.
  - Added: pulling the pins hands the cable torque to the rider (up to ~11 N of
    contact change against 5–10 N of preload), so trim the trunnions and put the
    saddle at the natural apex.
  - Minor difference: my lever is 71 mm to the cable's line of pull, theirs
    129 mm to the exit; the conclusion is the same.
- **Readability pass.** Every idea file now opens with Picture it, its sketches
  and its major unresolved problems. All sketches are at the true opening pose;
  E's sketch is labelled with the wave-5 branches.
- **Summary entries.** The per-arrangement summary could not be saved as a file
  here (the harness returns summaries as text); it went to the coordinator in the
  wave-5 reply.
