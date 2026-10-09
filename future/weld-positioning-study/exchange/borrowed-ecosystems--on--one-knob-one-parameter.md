# borrowed-ecosystems on one-knob-one-parameter (wave 2)

Everything here is computed at the **corrected opening pose**: grip 45, hole
*dial* 30, vertical −15, with the scene's 35° dial offset applied (`main.js`
passes dial − 35 to `posePoint`). one-knob-one-parameter's geometry already did
this; mine did not in wave 1 and is corrected (see my notebook). Numbers:
`explorers/borrowed-ecosystems/calcs_exchange.py`. Branch sketch:
`explorers/borrowed-ecosystems/sketches/x-okop-gravity-sine-arms.svg`.
Sourcing evidence for new parts is in `sourcing/borrowed-ecosystems.md`.

I worked on **isocentric-couch-and-gantry** (developed furthest) and
**c-arm-on-the-gun** (left rough), with a shorter note on **recipe-cartridges**.

---

## 1. Isocentric couch and gantry

### 1a. The Y drawer is a yaw knob, treated as a motion to a stop

- **Variant.** The couch Y drawer: "nothing weld-relevant to first order (dot
  slides along the seam)", a long drawer slide with a hard stop and cam latch,
  used to load and unload.
- **Assumption behind it.** That sliding along the seam changes nothing. The
  joint is a circle: a tangential slide *s* leaves the dot on the corner
  (radial change s²/2R, 8 µm at 1 mm) but turns the approach by s/R, i.e.
  **0.93° of vertical-axis angle per mm**. Through the partner's own weld-angle
  table, a drawer that returns 0.3 mm off shifts work +0.15°, travel −0.15° and
  wobble-crossing −0.22°. The dot camera cannot see it, because the dot is still
  on the corner.
- **Real capability of the part.** Ball-bearing drawer slides are carriers, not
  locators: their end stops and lateral play are of order 0.1–0.3 mm (estimate;
  no listing publishes a repeatability). That is a 0.1–0.3° yaw scatter per
  load/unload.

**Repair A — keep the drawer, make its end kinematic.** The slides carry the
rotator's weight over the 150 mm stroke; the last few mm land on three steel
balls in two dowel-pin vees and a flat (parts already in the partner's
sourcing: G25 balls, ground dowel pins), pulled home along the drawer axis by a
spring behind the cam latch so the latch force never sets the position. That is
their own "motion to a stop", with the stop made kinematic. Add Derek's dial
indicator (0.0005 in, owned) on the drawer end as a yaw witness in the walk test:
drawer out/in five times, read Y.

**Repair B — use it: Y becomes the read yaw knob, and the couch table becomes
optional.** Rotating the gun about the dot's vertical by φ is, relative to a
circular joint, the same as translating the work along the chord to the point
at −φ (rotation about the tube axis is a symmetry of the joint): R sin φ along
the tangent and R(1 − cos φ) radially.

| φ | tangent | radial |
|---:|---:|---:|
| 1° | 1.08 mm | 0.009 mm |
| 3° | 3.24 mm | 0.085 mm |
| 5° | 5.39 mm | 0.235 mm |
| 15° | 16.0 mm | 2.11 mm |

With a micrometer stop on Y (as on X), a ±3° yaw trim is one knob to within
0.085 mm, which the per-tube camera trim of X absorbs anyway. Deleting the
4-inch couch table then removes ~80 mm of stack, the eccentric load on it
(rotator + plate + slides ≈ 8–9 kg acting ~62 mm off the table axis, ≈5 N·m,
estimate), and the swinging of motor, purge hose, ground lead and camera that
their C-arm file lists as the couch's cost. **What it costs:** φ stops being a
single dial for large changes (15° needs Y and a 2.1 mm X correction, from a
lookup or a printed cam, below). The couch table buys pure large-range yaw; a
read Y buys a lower, simpler couch. Both keep gravity loads one-signed.

### 1b. The roll bearing cannot reach the grip axis

- **Variant.** Repair A in their file: size a closed bearing (6816, 80 mm bore)
  so the gun passes through it nose-first, then it lives on the roll body.
- **Assumption behind it.** That the bore only has to pass the gun's
  cross-section. Seen *along the grip axis* the proxy gun's silhouette needs a
  **145 mm** circle: the barrel runs ~25° off the grip axis and the housing hangs above it, so it sits
  up to 130 mm from it. 6816 (80 mm) and 32011 (55 mm) cannot pass; a ~150 mm
  bore thin-section bearing would (61830 class, not checked for Prime stock).

**Repair — borrowed from lenses and telescopes: hinged rings around a printed
sleeve.** Extend the shell behind the butt into a printed sleeve coaxial with
the grip axis (the scene's cable is on the grip axis 70 mm out; the sleeve's
bore carries it, printed in halves). Two hinged clamshell rings, ~95 mm apart on
a bracket at the spoke's end, close *around* the sleeve: nothing threads.

- **Tilt stiffness from spacing.** For a 2 N change at the nozzle ~300 mm away,
  two clamped rings 95 mm apart move the dot ~0.02 mm (aluminium, ~2000 N/mm per
  ring) to ~0.08 mm (printed sleeve, ~500 N/mm) — against ~1.5 mm for a single
  printed arc on rollers with contacts 70 mm apart (my own B's weak point; calcs
  §7). The sleeve should be aluminium-lined where the rings clamp.
- **Calibration screws.** Telescope practice uses three PTFE-tipped screws per
  ring: exactly their calibration screws for putting the sleeve axis on the grip
  axis, found by their walk test.
- **The roll knob.** A 100 mm lever on the sleeve rests on a micrometer head
  (their $16 part) and is preloaded by gravity: the grip-axis torque is
  0.2–1.2 N·m over roll 10–75° for 1–2 kg, one sign, i.e. 1–12 N on the tip.
  0.01 mm = 0.006° of roll. Near roll 0 the torque vanishes, as they found; their
  torsion spring applies.
- **Lock.** Tighten the rings: holding 0.9 N·m on an 84 mm sleeve needs about
  70–110 N of clamp normal force (µ 0.2–0.3), easy with a ring knob. Weld with
  them tight; set with them snug.
- **Bought parts, honestly.** Hinged lens collars are sized for zoom lenses
  (FOTGA 84 mm ring, $27.89, 61 ratings, Prime; that it opens is typical of lens
  collars but not stated on the listing). Telescope *guide-scope* rings on Prime
  (Astromania 90 mm ID pair, $28.97, 47 ratings) are **closed** three-screw
  rings, so they fail the threading test just like a bearing; hinged tube-ring
  clamshells exist but were low-volume listings. Printed clamshells with PTFE
  liners are a legitimate fallback, since the metal that matters is the
  micrometer and the clamp screws.

### 1c. Branch: the hole angle as a gravity-preloaded sine arm on gauge blocks

Their hole table relies on gravity to take up worm backlash one way. At the
corrected pose that torque is **1.0–3.3 N·m over dial 15–45 for 1–2 kg**, one
sign throughout (their assumption holds; my wave-1 figure was 2–6× too small).
A machinist's sine bar does the same job without a worm:

- **Mechanism.** A preloaded deep-groove bearing pair on the hole axis, 40 mm
  outboard of the dot (where their table sits). A hardened ball on the spoke at
  L = 200 mm from the axis rests on a **gauge-block stack** standing on an anvil
  fixed to the same Z bracket as the pivot. The gun's weight holds the ball down
  with 7–17 N.
- **Setting, reading, locking, returning.** sin(e − e₀) = (h − h₀)/L. With a
  100 mm reference at dial 30, dial 20 is a 68.40 mm stack and dial 45 a
  141.42 mm stack. A 0.0001 in step is 0.0007°; a block's ±0.25 µm is under
  0.3 arcsec. The stack list *is* the record ("0.1003 + 0.140 + 2 + 1"), return
  to baseline is the same stack, and nothing can drift. The WEN 81-piece set is
  $104.88 on Prime (182 ratings, ASME B89.1.9 certificate, next-day).
- **Breaking it.**
  - It is slow to change (a minute to re-stack), so it is the wrong tool for AI
    sweeps. Repair: a micrometer or a motorised push-rod under the ball does the
    sweeping, and the stack is the calibration artefact that the sweep's zero is
    checked against — a knob and its reference standard.
  - An upward umbilical tug ≥ 7–17 N at the grip end could lift the ball. A light
    spring hold-down (tens of N) fixes it, as in their cartridges.
  - The pivot's play becomes angle error, so the bearing pair must be axially
    preloaded.
  - It does not motorise as neatly as a table handwheel.
- **Versus their table.** The table is continuous, motorisable and has dial and
  lock in one part. Amazon reviewers of the Vertex HV-4 report smooth movement
  and minimal backlash, but also parallax reading its vernier (the vernier ring
  is larger than the main dial) and a zero not aligned to the mounting face. The
  dial therefore wants a witness anyway, which their Klein gauge and AS5600 plan
  supplies; the lock-induced shift remains unmeasured. The sine arm has no gear
  and no backlash, and its setting is a calibrated artefact.

The same idea works for roll (1b): **both gun-side rotations become hinges whose
arms rest by gravity on bought metrology**. Sketch:
`x-okop-gravity-sine-arms.svg`.

### 1d. What their station has that my arrangements lack

- The **isocentre walk test** as a session QA number. My B (nodal head) is the
  same kinematics — hole rotator 30–40 mm outboard at the dot's height, spoke
  running back along the grip axis, roll behind the butt — reached
  independently. Theirs is the better-developed version, and B should simply
  adopt the walk test and the knob vocabulary.
- The **wire-mount table** (which relation each mount holds constant). None of
  my arrangements decided where the wire guide lives.
- **Standoff and nozzle extension as two parameters.** None of mine had a
  standoff knob.
- **"The knob is the actuator; the camera offset is the parameter."** My A1
  rider gets there mechanically for radial and height, but has no knobs for
  angles at all.

---

## 2. C-arm on the gun

### 2a. The outermost joint hangs overhead — and is redundant

- **Variant.** The yaw table hung table-down from a crossbeam ~420 mm above the
  dot, carrying 10–14 kg whose centre of mass moves with hole and roll. They
  flag the hanging-table question, the φ-dependent crossbeam walk (~0.04 mm per
  0.1 mrad) and the head-height mass.
- **Assumption behind it.** That the vertical-axis angle must be a rotation of
  the gun about the dot's vertical to be "the scene's dial".
- **Physics.** For a circular joint that rotation equals a translation of the
  work along the chord (table in 1a). The C-arm's work side already has an X
  micrometer slide and a Y drawer.

**Repair — delete the yaw joint.** The C-arc hangs from a fixed goalpost frame.
There is no overhead bearing, no off-axis centre-of-mass walk, no hanging-table
question, and 4–6 kg less over the operator's head (the yaw frame, table and
counterweight). Yaw becomes the read Y knob plus the camera's X trim. The work
still never *rotates* for yaw, so the C-arm keeps its main advantage: purge
hose, ground lead, camera and the operator's view stay put.

- **What it costs.** "Each dial is the scene's dial" for the vertical axis. A
  small yaw (±3°) is one knob (Y) to 0.085 mm; 15° needs +2.1 mm of X.
- **Keeping purity if Derek wants it.** A printed cam plate that drives X from
  Y (X = R − √(R² − Y²)) makes the Y knob a pure-yaw knob with the dot held — a
  "yaw slide". Unlinking the cam returns X to its own knob.
- **Convergence.** The C-arm without its yaw joint is the couch-and-gantry
  station without the couch table: arc (hole) and roll on the gun, X/Y/Z
  translations at the work. The two ideas meet.

### 2b. The arc itself

- My own number for a *printed* arc on rollers (§7 of calcs_exchange: ~1.5 mm
  at the dot for 2 N at the nozzle) is why their cut 12.7 mm 6061 plate with
  eight rollers is the right call. Commodity rollers exist: 624-size V-groove
  bearings ($9.71 for 20, 334 ratings) as edge rollers on a chamfered plate
  edge, and 608-class bearings as face rollers.
- The hole torque (1–3.3 N·m) always pushes the carriage the same way down the
  arc, so the carriage can rest on a micrometer stop or a gauge stack (1c)
  instead of a belt rack. Keep the belt rack for motorised sweeps and the stack
  for return-to-baseline.
- The arc supports the gun close in, which a single bearing on the hole axis
  (their table, my B) does not. That is a real stiffness advantage worth
  keeping even after the yaw joint goes.

---

## 3. Recipe cartridges (short)

Their first break is print accuracy (0.1–0.3 mm over 200 mm, estimate) and
creep of PET-GF under point loads. The machinist's answer to "an angle that
cannot drift" is **hardened angle gauge blocks**: WEN 12-piece, 1/4°–30°,
$41.74, 167 ratings; Accusize 10-piece, ±30 arcsec, $42, 215 ratings. A sine bar
($61.99, HHIP 5 in) with gauge blocks covers arbitrary angles.

- **Branch.** A cartridge becomes a printed carrier with steel seats plus a
  stack of angle blocks under a hinged pose plate. Printing *locates*; steel
  *sets the angle*. Creep and print error leave the angle and stay only in
  position, which their couch X/Z already trims per tube.
- **Cost.** One tilt per stack direction; compound angles need two stacks at
  90°, or the sine arms of 1c. It loses the one-generated-part-per-recipe
  elegance and the git record, and gains a record in steel.

---

## 4. Can decoupled-knob discipline come from camera, lab and machinist parts?

| Part (ecosystem) | Set | Read | Lock | Return | Verdict |
|---|---|---|---|---|---|
| 4 in rotary table (machinist) | worm | dial + vernier (parallax reported) | lock levers (shift unmeasured) | one-sided approach | knob ✓, motorisable |
| Gauge-block stack under a gravity-loaded arm (machinist) | stack | the stack | gravity + light clamp | exact | knob ✓, slow |
| Micrometer head against a preload (lab/machinist) | thimble | 0.01 mm | its lock / the preload | one-sided | knob ✓, 25 mm travel |
| Indexing pano rotator (camera) | detent clicks | scale | knob | by click | setup knob ✓, coarse steps |
| Arca clamp + scaled rail (camera) | slide | mm scale | clamp | ±~0.1 mm, no stop | calibration screw only |
| Lens collar / tube ring (camera, astro) | loosen and turn | printed scale | knob | ✗ without a lever + micrometer | lock ✓, knob with 1b's lever |
| Worm macro rail (camera) | worm | scale | lock | backlash unless preloaded | knob ✓ if gravity-loaded |
| Ball head, magic arm, gimbal head (camera) | one lock frees several axes | — | friction | ✗ | never a knob: parking and support only |
| Monitor arm, spring balancer (office, assembly line) | — | — | — | — | carriers only |

Where the discipline costs function:

- Sine arms and stacks are slow; detents are fast but coarse; worms are the
  motorisable middle.
- The knob stations put five to seven precision joints in the gun's chain, each
  with unmeasured lock shift and tilt. A tube rider (my A1) has none of those
  and follows runout, but it cannot set an angle at all.

The combination worth drawing next is knobs for angles, with the rider as the
X/Z stop (below).

---

## 5. Transfers the other way

- **Rider as the translation stop.** Their per-tube X/Z camera trim exists
  because bore, recess, seating and tube length vary. A spring-loaded OD wheel
  pair straddling the dot at ±30° 25 mm below it (my A1-S) can be the *stop*
  for couch X, making X "offset from this tube's OD". The same idea with a rim
  wheel at ±60° serves as the Z stop. Tube-to-tube variation then drops out
  mechanically, and the micrometer reads a transferable offset. This keeps
  "translations nearer ground" (the stop is on the work side) and gives the
  radial following error of ≤0.017 mm at the procedure's runout limit.
- **Use gravity rather than cancel it.** Their umbilical balancer is right, but
  a balancer that also floats the gun would remove the one-signed preload their
  worms and my sine arms depend on. If the gun proves heavy (> 2 kg), relieve it
  only down to a few newtons of preload.
- **Circle symmetry** (1a, 2a) — the digest's "a slide along the tangent is the
  vertical-axis turn", found independently by four explorers — is the most useful
  single transfer here: it deletes one bought rotary table from either station,
  or tells them what their Y drawer really is.

## Questions this adds for Derek

- Would he accept yaw as a read Y knob (plus an X lookup) instead of a rotary
  couch or an overhead yaw table?
- Is a one-minute gauge-block re-stack acceptable as the "return to baseline"
  for the hole angle, with a micrometer doing the exploring?
