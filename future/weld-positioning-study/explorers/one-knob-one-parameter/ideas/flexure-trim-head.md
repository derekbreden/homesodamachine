# Flexure trim head: printed fine knobs with no backlash, stick-slip or lock shift

**Picture it.**
- **Host.** On who-moves-what's tilt cradle (T-b1) the work and gun are tilted
  32.5° together. The carriage drops down the vertical escape rail onto a
  gravity-seated hard stop 62–84 mm from the dot.
- **The head.** Between the carriage and the recipe block, a printed PET-GF
  body holds three flexure stages with clamped spring-steel leaves:
  - A, a parallelogram moving the gun horizontally across the corner;
  - W, a remote-centre pivot whose two leaves aim at the seam tangent through
    the dot (the work angle);
  - S, a parallelogram along the beam (standoff).
- **Drive and reading.** Each stage is pushed by a micrometer through a printed
  5:1 notch-hinge lever and kept in contact by a steel spring. A and S also
  carry digital indicators; the dot camera and a Klein gauge on the shell read
  W.
- **Above the head.** The recipe block (coarse hole and roll), then the shell
  and gun at the opening pose, lying in the vertical tangent plane.
- **Carrying and locating.** The carriage and rail carry the weight. The
  flexures only locate, with their leaves along the weight where possible.
- **Fixed** is the cradle (carriage → column → cradle floor → rotator).

Sketch: `../sketches/flexure-trim-head.svg` (section at τ* with the proxy gun at
the opening pose 45/30/−15, plus a stage in detail). Numbers: `../flexures.py`
(all material values labelled; estimates where marked).

**Major unresolved problems.**
- Whether ±1–3° and ±2–4 mm of range covers the fine tuning the process needs.
  The process window is unmeasured.
- Thermal growth of printed loops over a session.
- Relaxation of the printed clamps holding the steel leaves.

## The idea

Every knob in my stations so far has joints: worm and table, micrometer and
slide, bearing and clamp. Each joint has play, stick-slip and a lock that
shifts the setting when tightened; borrowed-ecosystems counted "five to seven
precision joints, each with unmeasured lock shift". A flexure has none of these.

- It moves by bending, so it has no clearance to take up and no friction to
  stick, and nothing to lock: the micrometer that sets it also holds it.
- Derek prints, and a printed flexure is one part.
- Its weakness is range, so flexures are the **fine** knobs around a coarse,
  seated pose:
  - **coarse:** a recipe block, a dock, a rail stop, the cradle τ;
  - **fine:** a few printed flexure stages, each driven by a micrometer through
    a flexure lever.

**The stage set** (on the host's carrier, from the carrier outward):

| Stage | Flexure | Changes only | Range (estimate) | Drive and reading |
|---|---|---|---|---|
| **A**, across the corner | parallelogram, motion perpendicular to both the beam and the seam | dot between wall and cap | ±1.5–4 mm | micrometer on a 5:1 flexure lever: 2 µm per division; RS232 digital indicator on the platform for the log |
| **W**, work angle | remote-centre pivot: two leaves whose lines meet at the **seam tangent through the dot**, D ≈ 70–90 mm | the beam's tilt between wall and cap, with the dot fixed | ±3° (steel leaves L 40) to ±13° (L 80) | micrometer on a lever at ~40 mm drive arm: ~0.001° per division; the camera and a Klein gauge on the shell read the angle |
| **S**, standoff | parallelogram along the beam | focus only | ±2–4 mm | micrometer + lever; digital indicator |

Order follows my chain rule: the translation A is nearer ground than the
rotation W. S runs along the beam, so it may sit inside W.

## Host: who-moves-what's tilt cradle, branch T-b1

It fits best there (see `../../../exchange/one-knob-one-parameter--on--who-moves-what-w4.md`):

- **Coarse** settings come from the cradle and carriage:
  - the rail's hard stop seats the carriage (gravity, ball in vee);
  - the recipe block holds coarse hole and roll;
  - the Y slide sets yaw;
  - the cradle sets τ (gravity).
- **Fine** settings come from the flexure head between the carriage and the
  recipe block: A, W, S. They are exactly the two stages that were missing
  there (S and A), plus a work-angle pivot on the same line as the cradle's
  axis (their branch T-g).
- **Why the host suits flexures.**
  - The carriage sits 62–84 mm from the dot, so a remote centre at the dot is
    only D ≈ 70–90 mm away. Remote-centre drift grows with D (below).
  - At τ* the rail is vertical and the gun's weight is purely along it, so the
    head can be laid out with its leaves along the weight: axial load, no
    bending creep.

**Other hosts:**
- **The A1-G rider** (wave 2): the rider's printed arc becomes a W flexure at
  D ≈ 40–70, with no rollers and no play. The rider already carries only preload.
- **My C-0 / couch station:** a W stage mounted on a bracket that reaches to
  within ~80 mm of the dot, rather than at the 300 mm spoke end.
- **The knob-wired suspension:** each angle wire's anchor driven by a flexure
  lever and micrometer instead of a lead screw.

## Range against stiffness

At 0.25 mm spring steel against 1.2 mm printed leaves, L 40, width 20:

| Parallelogram | Range | Drive | Out-of-plane | Tilt stiffness |
|---|---:|---:|---:|---:|
| PETG leaves | ±2.1 mm | 1.8 N/mm | 500 N/mm | 1,250 N·m/rad |
| PET-GF leaves | ±1.3 mm | 3.8 N/mm | 1,050 N/mm | 2,600 N·m/rad |
| 1095 shim leaves in PET-GF blocks | ±4.2 mm | 2.0 N/mm | 12,800 N/mm | 32,000 N·m/rad |

- The drive direction is soft on purpose. What holds a setting is the steel
  micrometer through its lever, preloaded by a steel spring.
- The other five directions matter for precision, and there spring steel is
  10–25× stiffer than printed leaves.
- Under the gun's full weight moment (1.5 kg at 150 mm, 2.2 N·m) a PETG
  parallelogram tilts enough to move a point 150 mm away by 0.26 mm; PET-GF
  0.13 mm; steel leaves 0.01 mm. Relieved to 0.3 N·m: 0.04 / 0.02 / 0.001 mm.

**Rule:** in the gun's load path, use steel leaves or relieve the weight.
Printed leaves are fine in lightly loaded places: levers, the rider, wire anchors.

## Can the remote centre sit at the dot?

Yes. It is a remote-centre compliance (RCC) layout, the device robot wrists use
to put a compliance centre at a peg's tip: two leaves whose extended lines meet
at the dot, forming a four-bar whose instant centre is there.

- **Range** is the price of the distance, because the leaves' ends travel D·θ:

  | Leaves | L | D 70 | D 150 | D 250 |
  |---|---:|---:|---:|---:|
  | PETG 1.2 | 40 | ±1.7° | ±0.8° | ±0.5° |
  | PETG 1.2 | 80 | ±7.0° | ±3.3° | ±2.0° |
  | 1095 0.25 | 40 | ±3.4° | ±1.6° | ±1.0° |
  | 1095 0.25 | 80 | ±13.6° | ±6.4° | ±3.8° |

- **Drift.** The centre is exact only at the design angle and wanders roughly
  with the square of the rotation (pseudo-rigid four-bar):

  | D | at 0.5° | at 1° | at 2° |
  |---|---:|---:|---:|
  | 70 mm | 6–11 µm | 24–42 µm | 96–170 µm |
  | 150 mm | 19–32 µm | 75–126 µm | 300–500 µm |
  | 250 mm | 45–80 µm | 180–320 µm | 0.7–1.3 mm |

  - The drift is deterministic, so the camera maps it once and stage A cancels
    it with a small lookup. Alternatively, keep W to ±1° around a recipe block
    at D ≈ 70.
  - It sets the placement rule: **flexure pivots belong within ~100 mm of the
    dot.** That is where the tilt cradle's carriage, the A1-G rider and the
    suspension's outrigger already are, and where my gantry's 300 mm roll
    bearing is not.
- **Stiffness about the dot** from the leaves alone is low (1–10 N·m/rad at
  D 70). The micrometer holds the angle; the leaves' axial and out-of-plane
  stiffness holds the other five directions.

## Creep, relaxation, temperature

- **Displacement-held versus load-held.** A stage set by a micrometer is held
  at constant displacement. Its leaves *relax* (stress falls) rather than
  creep, and the position stays where the steel spindle put it. Only the
  restoring force drops, so a steel spring in parallel supplies the contact
  force and the printed flexure only guides.
  - Leaves that carry the gun's weight in bending creep in *position*. My
    estimate for amorphous PET/PETG at 10–20 % of strength is +30–60 %
    compliance over ~1000 h, so 0.02 mm of gravity tilt becomes 0.03 mm over
    months.
  - Hence: weight along the leaves (axial, 0.3 MPa: negligible), steel leaves,
    or a balancer.
- **Clamped steel leaves** do not creep, but their printed clamp blocks can.
  Steel screws in heat-set inserts, with the clamp face backed by a steel
  washer strip; re-check with the walk test monthly.
- **Temperature.**
  - The pool itself is a tiny radiator: ~1 W total, ~30 W/m² at 70 mm.
  - The hot lip and fresh bead give perhaps 2 W, ~70 W/m² at 70 mm. Neither
    heats a printed part appreciably.
  - Spatter reaches 70 mm, so a stainless shield plate goes on the head's
    dot-facing side.
  - The real heat source is the gun body, which warms from its optics; the
    manual's lens alarm sits at ambient +15–20 °C. It conducts into the shell
    and head.
  - PETG's Tg is ~80 °C and PET-GF holds better. At a gun-side 35–45 °C
    neither softens meaningfully **[estimate]**.
- **Thermal growth is the bigger thermal effect.** 120 mm of printed loop
  warming by 5–15 K grows 39–117 µm (PETG), 21–63 µm (PET-GF) or 10–31 µm
  (aluminium-framed with steel leaves).
  - What matters is the change between the dry run and the end of the weld,
    so run the dry run at thermal steady state, immediately before the weld.
  - A 50 s weld plausibly adds 1–3 K **[estimate]**, a few µm with PET-GF.
  - Keep the printed length in the loop short, and let the frame be metal where
    it is long.

## Reading, returning, recording

- **Reading.**
  - A and S: micrometer thimbles, plus 0.01 mm digital indicators with RS232
    output on the moving platforms. The indicators bypass lever nonlinearity
    and log themselves.
  - W: the dot camera (the dot must stay put while the wall/cap split changes)
    plus a Klein gauge on the shell.
- **Returning.** Set the thimbles. No backlash, so the approach direction does
  not matter, and no lock, so there is no lock shift.
- **Baseline.** Three thimble readings plus the coarse block's name.
- **Motorised.** A small stepper on each micrometer, or a voice-coil/stepper
  pushing the lever directly. The flexure has no dead band, so an AI's dry-run
  sweep of ±1° work angle in 0.05° steps is clean. That is Derek's automated
  vision at the finest scale.

## Breaking it

1. **Range is small.** It is fine trim only: ±1–3° and ±2–4 mm. Everything
   coarse must already be right (block, dock, stop, τ). If the process window
   turns out wider than the flexure range, the flexures are unnecessary; if
   narrower, they are the only knobs fine enough. That is unknown until the
   first coupons.
2. **Printed leaves under load creep.** Use steel leaves in the load path,
   printed leaves elsewhere.
3. **Remote-centre drift beyond ±1°:** mapped and cancelled by A, or avoided.
4. **Clamp-block relaxation** can shift a steel leaf's effective length (and
   the centre). The monthly walk test catches it.
5. **Fatigue** is not an issue at these strains and cycle counts: settings
   change a few times a day, and the wobble's 80 Hz vibration is µm-level.
6. **Heat and spatter:** shield plate; short printed loop; dry run at steady
   state.
7. **Out-of-plane stiffness of printed leaves** (500 N/mm) is comparable to the
   wires' dot stiffness. Printed-leaf stages therefore belong in light-duty
   places, steel-leaf stages in the gun's path.

## Parts

- **Bought:**
  - 1095 blue-tempered spring-steel shim assortment (Precision Brand, AMS 5122;
    sourcing file);
  - micrometer heads ($16–$100);
  - steel compression springs;
  - RS232 0.01 mm digital indicators (workspace-as-structure's sourcing);
  - M3 screws and heat-set inserts.
- **Printed:** PET-GF blocks, levers with notch hinges, the head body; PETG
  where a printed leaf is wanted.

## Contribution and open problems

It makes the fine knobs free of every joint defect, printable, and cheap. It
supplies exactly the standoff and across-the-corner stages the tilt cradle
lacked, and a work-angle pivot on the cradle's own axis. It also turns the
wave-2 rule ("put the pivot hardware close to the dot") into a number: drift
∝ D.

**Biggest open problem:** whether its range (±1–3°, ±2–4 mm) covers the
fine-tuning the weld needs. That depends on a process window nobody has
measured. Second: the thermal growth of printed loops during a session.

**Questions for Derek:** does the gun body warm noticeably during a run of
welds, and by how much? A $10 thermocouple on the barrel answers it.
