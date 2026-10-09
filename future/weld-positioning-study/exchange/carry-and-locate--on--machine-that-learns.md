# carry-and-locate on machine-that-learns (wave 2)

My view: carrying and locating are different jobs. For each idea I ask what
carries each load, what establishes where the dot is, and whether a drive's load
keeps one sign. I worked on **B, the RCM gun carriage** (with A, the most
developed) and **C, the hexapod with a software pivot** (the roughest), plus
short notes on D, A and the observation layer.

All numbers are at the scene's opening pose (grip 45, hole dial 30, vertical
−15) with main.js's 35° hole-dial offset, the same convention their
`pose_points.py` uses. Scripts: `explorers/carry-and-locate/calc/mtl_b_float.py`,
`mtl_c_preload.py`, `mtl_sketches.py`. Sketches:
`explorers/carry-and-locate/sketches/X-mtl-B-float-and-open-ring.svg`,
`X-mtl-C-preloaded-hexapod.svg`.

---

## 1. B — gun carriage: X, Y, Z stages, a hole-axis arc and a grip-axis yoke

### Difficulty B1: gravity rides the whole chain, and the roll drive's load changes sign

**Variant:** B as drawn — about 3 kg of gun, shell and yoke on the yoke's two
grip-axis bearings, hung from an arc carriage (R 285, plane 40 mm outboard),
hung from the Y carriage (I read it as ~330 mm toward −Y and ~420 mm above the
dot, 536 mm from it), with a worm on the roll and a belt on the arc.

**Assumption behind it:** "During the weld nothing moves, so constant loads
make deflection constant; deflection that changes between poses can be
measured and mapped."

Over B's workspace (roll 20–70, hole dial 5–55, X and Z ±50 mm) the CoM moves
~40 × 130 × 160 mm and gravity does this **[Calc, mtl_b_float.py; 3 kg and the
CoM are B's and my assumptions]**:

| | arc (hole-axis) drive | roll (grip-axis) drive | moment at the Y carriage |
|---|---|---|---|
| no float | +1.9 … +5.7 N·m | **−0.8 … +3.2 N·m** | 4.1 … 8.5 N·m |
| float at the CoM, 1.5 m line | −0.10 … +0.44 | −0.05 … +0.09 | 0 … 0.67 |
| float at 90 %, attached ~40 mm off the CoM | +0.55 … +1.70 | +0.60 … +1.46 | 0.67 … 1.84 |

Three consequences the "constant during the weld" argument does not cover:

- **The roll worm's load changes sign inside the workspace.** Worm backlash sits
  on one side at some poses and on the other at others. The camera sees a roll
  angle that depends on the pose *and on the direction it was approached from*.
  A map indexed by pose alone will not capture it.
- **The stages are upstream of the remote centre.** A tilt of the Y carriage
  turns the whole arc and yoke about the Y carriage, not about the dot. With an
  assumed 0.1 mrad per N·m of carriage tilt, the 4.4 N·m spread moves the dot up
  to ~0.24 mm between poses. B's RCM argument protects the dot from the arc and
  roll drives, not from the stages.
- **The arc carriage's wheels carry the full weight radially.** That is B's
  own POM-creep worry.

**Repair B1 — a float that carries, set so every drive stays loaded one way.**
A constant-force spring balancer (or a counterweight over a pulley) hangs from
the ceiling on a line of at least 1.2 m. It carries ~90 % of gun + shell + yoke
and hooks onto the shell ~40 mm from the CoM, at (36, −13, −38) mm in the gun's
frame (a search result, not an optimum).

- Result: both rotary drives stay loaded one way everywhere (+0.55…+1.70 and
  +0.60…+1.46 N·m). Z carries a steady ~3 N downward, so its screw backlash
  also stays on one side. The spread of the Y-carriage moment halves
  (2.4 N·m, ~0.13 mm at the dot with the same assumed carriage).
- Floating 100 % at the CoM removes more load (≤ 0.44 N·m, ≤ 0.67 N·m at the Y
  carriage, ~0.04 mm), but a drive with no load has no chosen side. That is why
  the float is deliberately short of 100 % and offset from the CoM.
- **What "fixed" is fixed to:** the float's anchor can be a ceiling joist or a
  pegboard boom. It carries only; it is outside the position loop (column →
  stages → arc → yoke → shell → dot).
- **What it leaves:**
  - When X or Z move ±50 mm, the line tilts and puts ≤ 2.3 N sideways on the
    chain (1.5 m line). A free trolley on an overhead rail, dragged along by the
    line, removes most of that.
  - The line must clear the column and camera sightlines.
  - Nothing may touch the float between the last dry lap and the weld.
- **Parts:** the QWORK-class balancer from my sourcing comes in 1.5–3 kg for a
  3 kg load (the 0.5–1.5 kg 2-pack is $16.97 Prime; the other ranges are listed
  on the same Prime search page).

### Difficulty B2: the umbilical — a closed ring, and a fixed saddle while everything moves

**Variant:** "a ring bearing around the cable exit at the grip butt (the
umbilical and wire conduit pass through its bore)", "hanger saddle is a
swivel" on the rear post.

**Assumptions:** the cable can pass through a closed ring, and its pull at the
butt stays roughly constant.

- A closed ring cannot be threaded without unplugging the QBH at the gun (see
  the digest).
- With the first support fixed on the rear post, the butt moves relative to it
  by X ±50–75, Z ±50, Y ±32 mm, and by tilt: 47 mm per 10°, so up to ~±117 mm
  over ±25°. So the cable's pull on the butt changes with pose, ~280 mm from the
  dot.
- Roll twists the cable at the exit by ~0.87× the roll if the cable leaves
  along the grip's rake, as the proxy draws it; by almost nothing if it leaves
  along the grip axis. Only the scan will tell which.

**Repair B2.**

- **Open C-ring roll bearing.** Three V-rollers on the yoke in a 120° sector
  run on a printed ring of ≥ 190° for ±25° of roll. That leaves a ~170° gap, so
  the umbilical and wire conduit drop in sideways. It is Derek's "openable loop
  around the umbilical and wire feed" made precise, sitting on the grip axis
  where his base loop wanted to be.
- **The cable's first support rides the arc carriage**: after the tilt, before
  the roll. X, Y, Z and tilt then carry the cable along with the gun. Only roll
  changes the free span, and roll keeps the butt still. The cable's weight on
  the arc carriage is constant and becomes part of the float's bias.
- If the scan confirms a 30° exit, a guide on the shell can bend the cable onto
  the grip axis. At R ≥ 350 mm that guide is ~180 mm long with a 47 mm offset.
  Roll then becomes pure twist, spread over the span to the next swivel.
- **Remains:** how much twist the fiber tolerates, per metre, is not stated in
  the manual beyond "strictly forbidden".

### What B has that my arrangements lack

- Each commanded motion is one welding variable, and the same knob is later a
  motor. My wire-located suspension holds the dot mechanically as B's arc and
  yoke do, but its three angle wires do not map one-to-one onto Derek's axes.
  B's decomposition is the better one for experiments.
- Drive compliance becomes angle error, not dot error: the same reason I put
  three wire lines through the dot. B had it first as a motor argument.

---

## 2. C — hexapod with its pivot set in software

### Difficulty C1: the legs do not keep one sign, so leg play is two-sided

**Variant:** their proposal geometry (`hexapod_check.py`): platform on the
shell's outboard face, base 190 mm further out, 207.5 mm legs on M5 rod ends,
Tr8×8 integrated-screw motors. My check uses 2 kg of gun + shell at my assumed
CoM.

**Assumptions behind it:** "gravity already loads the legs one way in this
hanging pose; add springs across the rod ends", and "lead screws do not
back-drive easily".

- **Gravity alone** puts three legs in tension and three in compression:
  +20, −12, −2, +6.5, −3, +4 N. **[Calc, mtl_c_preload.py]**
- **Across ±7° about the dot**, with 5 N trigger, 5 N cable and 3 N wire-drag
  disturbances, legs 3, 4, 5 and 6 change sign. Nut, motor-bearing and rod-end
  play is taken up on whichever side the load happens to be. So their
  0.12 mm / 0.20 mm (median / 95th percentile) dot scatter is the realistic
  open-loop figure. It is also hysteretic, which slows "command, look, correct".
- **Tr8×8 is a 4-start, 8 mm lead** (lead angle ~20°, tan ≈ 0.36, above the
  ~0.15–0.2 friction of a brass nut on steel), so it back-drives. Printer Z
  axes on Tr8×8 drop when the drivers release. Under any preload the legs creep
  when the motors release.

**Repair C1 — an internal preload that keeps all six legs in tension.** A gas
spring on the hexapod's axis, from base ring to platform, pushes them apart.
The six legs hold them together, so every leg is in tension. The smallest push
that keeps every leg one-signed over ±7° and the disturbance set
**[Calc]**:

| Case | Central push needed | Leg force range |
|---|---|---|
| gun weight on the legs, all disturbances | 185 N | 0–85 N |
| trigger closed in the shell, cable carried (1 N residual), 3 N wire drag | 170 N | 0–74 N |
| the same, gun also floated at its CoM | 110 N | 0–39 N |

- **What it changes:** each leg's play becomes a constant offset. The camera
  calibrates it out once, and a closed loop settles in one correction with no
  dead band.
- **What it costs:**
  - More constant load on the rod ends and printed rings (constant deflection,
    calibrated).
  - A little motor torque: 33 N axial on Tr8×2 is ~0.04 N·m.
- **Parts:**
  - Farwind 150 N cabinet gas strut, 270/180 mm, $7.99 Prime, in stock. It fits
    only if base-to-platform spacing is raised from 190 to ~225 mm; at 190 it
    sits 10 mm from bottoming and the axial swing of ±7° would hit the end.
  - Ball studs (Prime, 400+ bought per month).
  - Legs: NEMA 17 with an integrated Tr8×2 single-start screw and
    anti-backlash nut ($27.99 Prime, in stock, 240 mm). It self-locks and is 4×
    slower, which does not matter at dry-run speeds.
- **Remains:** real gun mass and CoM, the real cable pull. The required push
  scales with them.

### Difficulty C2: range from a remote pivot

**Variant:** rigid legs, platform ~200 mm from the dot; ±10° needs ~38 mm of
leg change each way.

**Assumption:** the pivot must come from rigid legs around a platform.

**Branch C-w — my six-wire layout as the software-pivot hexapod.** Three wires
whose lines meet at the dot, three angle wires, and two bungees (~38 N from the
grip butt, ~36 N from a shell arm over the rim), with every anchor on a
motorised slide. **[Calc, mtl_c_preload.py Part 2]**

- For ±10° about any of Derek's axes, the three concurrent wires change only
  0.1–1.2 mm (second order). The dot is held mechanically while W4–W6 turn the
  gun, so B's RCM argument comes free: angle-wire drive error becomes angle
  error.
- Rotations need 16 mm (roll) to 41 mm (hole tilt) on W4–W6: the same order as
  the rigid legs. But wire anchors can ride 300–400 mm T8 screws or small
  winches, so range is limited by tension, not stroke.
- Every wire stayed ≥ 1.1 N taut across ±10° and ±10 mm translations with the
  disturbance set, least margin at −10° about the vertical axis. A vertical-axis
  turn is B's Y translation anyway.
- Wires have no play. Anchor-nut play is always taken up on the same side,
  because tension always pulls the same way.
- **Costs:**
  - A triangulated anchor frame tied to the rotator's frame.
  - Wires around the cable exit.
  - Per-pose tension checks.

### What C has that my arrangements lack

- The pivot is an argument: it lets the machine find which axes deserve
  hardware. My wire layout hard-codes a pivot by concurrency.
- With every anchor motorised, C-w keeps C's freedom and keeps the concurrency
  as the default.

---

## 3. Short notes

**D — watch-first seat.**

- **Difficulty:** the seat carries the gun at 52° off vertical, hence ~100 N of
  magnet, and sits ~180 mm from the dot. By my tip-off formula (balls 60 mm
  apart, r ≈ 35 mm), 100 N holds ~12 N at a 150 mm trigger lever. A 20 N hand
  press is past that.
- **Repair (my float-and-dock):**
  - A balancer at the CoM takes the weight, so the magnet only fights
    disturbances and the seat's orientation stops mattering.
  - A tongue near the barrel puts the seat 60–100 mm from the dot instead of
    ~180 mm, cutting the lever amplification of seat scatter roughly in half.
  - A cable saddle ahead of the gun.
  - Their Bowden lever in the shell already removes the trigger.

**A — still gun, moving tube.** Carrying and locating separate most naturally
here: the gun's loads are constant, and gravity keeps the Z-bed screws loaded
one way. One carry note: the heavy work lead clamped on the copper shoe (and the
purge hose) ride the X stage. Hang the work lead from above so its weight does
not side-load the stage by a different amount at each X.

**Observation layer ↔ carrying and locating.**

- **Observation changes what the locator must provide.** When the camera
  measures the dot on the last dry lap, the locator no longer needs long-term
  accuracy. It needs:
  - no change between that lap and the weld;
  - stiffness against the loads that appear only when the weld starts. From my
    inventory: trigger (zero if closed in the shell), wire push and drag 1–3 N,
    wobble reaction (µm-level on the gun's mass), argon flow (small). At
    20 N/mm that is 0.05–0.15 mm; at 100 N/mm, 0.01–0.03 mm.
- **Motors change what the carrier must provide.**
  - Force must stay constant as axes move: a spring balancer or a counterweight,
    not a bungee (0.06–0.12 N/mm × 50 mm of travel = 3–6 N that changes with
    pose).
  - Each drive's load should be biased to one side, so preload turns play into
    an offset.
  - Nobody touches the carrier after the last dry lap.
- **Preload and a closed loop need each other.** The camera loop is how a cheap
  mechanism reaches tenths; preload is what makes that loop converge in one
  step and stay there.
- **The camera measures what my arrangements only assume:**
  - reseat scatter of a dock;
  - creep of a bungee-carried float;
  - dot motion when the umbilical is pushed;
  - wire-length memory after unhook and rehook in my wire-located suspension;
  - calibration of the concurrency point: roll with the dot on the cap and fit
    the arc — B's method applies unchanged.
