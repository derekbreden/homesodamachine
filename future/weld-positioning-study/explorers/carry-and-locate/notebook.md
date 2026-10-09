# carry-and-locate — notebook

## The view

Carrying and locating are different jobs. For every arrangement I ask: what
carries each load (gun weight, its moment, umbilical, wire conduit, hands,
trigger, wobble, wire push, a stuck wire), what establishes where the dot,
wire tip and angles are, where each acts on the shell, and what "fixed" is
fixed to. Working vocabulary:

- **Carrier**: soft, nearly constant force (pendulum wire, bungee, spring
  balancer, cable saddle). Its drift δ through stiffness k_c puts only k_c·δ
  on the locator. The softer, the less it disturbs.
- **Locator**: stiff where it acts. Dot error ≈ (unknown force)/k_locator.
- **Preload**: a soft force that keeps a stiff contact or wire engaged (a
  bungee pulling a wire taut, a magnet or residual weight in a seat).
- **Position loop**: the chain of parts from the joint to the dot. Carriers
  should be outside it.
- **The don't-care DOF**: the joint is a circle. Moving the gun along the
  tangent, or turning a tube-riding carriage about the tube axis, slides the
  dot along the joint. Radial error from a tangent shift s is s²/2R
  (0.03 mm at 2 mm); the plan angle to the local tangent changes s/R
  (0.9°/mm). Soft directions belong there.

## Wave 1 (2026-09-28)

### What I did

- Ported the scene's pose code (`calc/pose.py`) to place loops, seats and
  wires on the real proxy geometry at the opening pose (grip 45 / hole 30 /
  vertical −15), with the scene's 35° hole-dial offset applied (see the wave-2
  correction). At that pose the barrel rises at 45°, the nozzle is ~5 mm above
  the rim, the housing sits beside the tube toward −Y (centre 112 mm off the
  axis, 330–430 mm above the bench), the grip butt is 372 mm above the bench
  and 233 mm off the axis, and the umbilical leaves it nearly horizontally
  along −Y.
- Load estimates (`calc/loads.py`), third-ring shares (`calc/three_ring.py`),
  wire virtual-pivot drift (`calc/wire_rcm.py`), wire tension feasibility
  (`calc/wire_tensions.py`, `calc/wire_layout_search.py`), wire compliance
  (`calc/wire_stiffness.py`), dock tip-off and rim loads
  (`calc/dock_and_rim.py`), ovality leakage (`calc/ovality.py`).
- Four sketches generated from 3D points in three views (`calc/sketches.py`
  → `sketches/*.svg`).
- Sourcing in Derek's Chrome: `../../sourcing/carry-and-locate.md`.

### Arrangements

- **A — Suspension, Derek's original, developed** (`ideas/suspension-original.md`).
  Findings: put the bungees on X (radial) and leave the pendulum free on Y
  (tangent, the forgiving direction). Two loops on wires leave roll about the
  loop line free; at this pose that line is 9° off Derek's grip axis, and a
  shell trunnion on the grip axis makes the free roll exactly the grip-axis
  roll. The tip loop carries 56–68 % of the gun, the base loop the rest plus
  cable; 0.39–0.54 N·m/kg of roll must come from the arm or a third ring, which
  belongs at the housing back (at the front it would need a pushing wire).
  Five grip modes for the arm (tip, CoM, base-with-fulcrum, roll lever,
  trigger). Breaks: float alone gives ~10–100 mm under plausible forces; the
  base loop must be a large saddle, and must not clamp the cable because
  grip-axis roll twists the umbilical at ~0.87× the roll; a stuck wire drags a
  bare float along Y. Five repairs/branches kept beside the original.
- **B — Wire-located suspension** (`ideas/wire-located-suspension.md`).
  Three wires whose lines meet at the dot form a virtual ball joint there;
  three more set the angles; two soft bungees preload. Decoupled: dot by
  three lengths, angles by three lengths. Drift 0.02–0.05 mm at 2°. The first
  layout failed (wires would have had to push); a search found layouts
  with all six taut and ≥ 6.8 N margin under ±5 N pushes and a trigger push,
  but only with two preloads (the preload lines must miss the rotating tube).
  Wires cannot push, so lift-off and return to the same pose are free.
- **C — Float and dock** (`ideas/float-and-dock.md`). Balancer + cable saddle
  carry; a magnet-preloaded three-ball/three-groove seat on an adjustment
  stack locates. Tip-off numbers show a hand on the trigger would unseat a
  modest seat; a shell-mounted presser makes the trigger force internal. The
  umbilical's residual is a real share of the seat's margin.
- **D — Rim carriage** (`ideas/rim-carriage.md`). The tube carries a C-ring
  on rollers; the gun hangs from it; a float sets the rim preload; a soft
  tether holds the don't-care spin. Pinch pairs at ±30° put no radial load on
  the tube and leak only 0.42e of ovality (±60° would leak 2e). Branch D2: a
  local shoe on cap face + bore at the joint. A stuck wire rotates ring and gun
  with the tube instead of bending anything.

### Load inventory (whole station)

| Load / action | Magnitude | Character | Where it belongs |
|---|---|---|---|
| Gun weight | 6–15 N (mass not in manual; 0.6–1.5 kg assumed) | static | carrier |
| Gun's moment about the dot | 0.75–2.3 N·m at the opening pose (CoM ~120–145 mm above the dot, 127–155 mm off it horizontally) | static, pose-dependent | carrier or known preload |
| Umbilical weight, spring-back | unknown; R ≥ 350 mm emitting | static + creep, pose-dependent | saddle before the gun |
| Umbilical twist | ≈ 0.87 × grip-axis roll at the butt | set at setup | loose loop / long free run |
| Wire conduit | unknown | static | with the umbilical |
| Wire push into puddle | 1–3 N assumed | steady during the bead | locator |
| Stuck wire | 3–5 N bends the stick-out; rotator can pull ~140 N | event | fuse: wire bends, breakaway seat, or don't-care DOF |
| Trigger | 3–8 N assumed | start/stop | internal to the shell (presser) |
| Wobble reaction | 0.1–2 N at 80 Hz assumed → 0.4–8 µm on a free 1 kg gun | continuous | mass; keep locator modes off 80/160 Hz |
| Hands in setup | 5–30 N | setup | soft carrier, locator engaged after |
| Cutters when snipping | a few N | after the bead | locator |

### Things that surprised me

- The joint's circular symmetry gives one free direction at the dot (the
  tangent) and one free rotation for anything riding the tube (spin about the
  tube axis). Both are natural places for compliance.
- The umbilical is a locating hazard mainly through twist and bend radius, not
  weight. The manual's "twisting is strictly forbidden" turns the loop around
  the cable into a rotating bearing, not a clamp.
- In a tension-only system, lift-off costs nothing and return is automatic.

### Open questions needing Derek's observation

1. Gun mass and CoM: luggage scale (hang the gun with a few cm of cable
   supported), and balance points on a rod edge in two orientations.
2. Umbilical: outside diameter, weight per metre, and the pull at the grip
   (luggage scale at the grip, cable in its usual route) as the gun moves
   10–20 mm in each direction.
3. Trigger: force and travel; is there any latch/lock-on mode?
4. In current practice, does the copper nozzle touch the work, or only the
   wire? (Vendor page: "Laser only fires when the gun touches metal.")
5. What the "laser gun holder" in the box looks like and where it grips.
6. Room: ceiling height and joists above the rotator's bench; where the
   pegboard is relative to the rotator.
7. The tube rim: faced/squared and deburred, or band-saw finish?
8. Nozzle kit contents (inside-corner types?).
9. The wire conduit: outside diameter, stiffness, and its route from the cart.

### For later waves

- Combine B and C: wires that locate plus a seat that makes lift-off/return
  exact even if a wire is unhooked.
- Run the load layout at other poses with the pose script.
- Put a number on anchor-frame stiffness for B.
- Compare C's stack options against Derek's three rotations about the dot.

## Wave 2 (2026-09-28) — exchange with machine-that-learns

### Pose correction

My wave-1 `calc/pose.py` passed the hole dial straight into `posePoint`; the
scene subtracts 35°. Wave-1 numbers were therefore at hole dial 65. Fixed in
`pose.py` (dial convention now explicit) and every pose-dependent number
recomputed at the true opening pose; the dial-65 results are kept, labelled, in
"Pose note" sections of the two suspension files. What changed at the true
pose: barrel 45° (not 71°); gun body off to −Y beside the tube (not over its
axis); grip butt 372 mm above the bench, 233 mm off axis; umbilical leaves
nearly horizontally along −Y; tip loop 272 mm / base loop 377 mm above the
bench; tip share 56–68 % (was 80–95 %); roll moment 0.39–0.54 N·m/kg (was
0.33–0.45); wire layout needs ~38 + ~36 N of preload with ≥ 6.8 N margin (was
24 + 35 N, ≥ 10 N); one preload alone falls 4.5 N short (was 0.6 N); trigger
push moves the dot 0.03–0.08 mm (was 0.015–0.04); gun's moment about the dot
0.75–2.3 N·m (was 0.3–1). Unchanged: the tip–base line's relation to the grip
axis, third ring at the housing back and its shares, bungees on X with the
tangent free, the 0.87× twist, two preloads needed, second-order concurrency
drift.

### What I did on their ideas

`../../exchange/carry-and-locate--on--machine-that-learns.md`, with
`calc/mtl_b_float.py`, `calc/mtl_c_preload.py`, `calc/mtl_sketches.py`,
`sketches/X-mtl-B-float-and-open-ring.svg`, `sketches/X-mtl-C-preloaded-hexapod.svg`.

- **B (RCM carriage).** Unfloated, the roll worm's gravity load changes sign
  inside the workspace (−0.8…+3.2 N·m), so backlash flips; the Y carriage sees
  4.1–8.5 N·m and it sits upstream of the remote centre (536 mm lever). Repair:
  a balancer at 90 % on a ≥ 1.2 m line hooked ~40 mm off the CoM keeps every
  drive one-signed (arc +0.55…+1.70, roll +0.60…+1.46 N·m, Z 3 N down).
  Open C-ring roll bearing (≥ 190° ring, rollers in 120°) so the cable drops
  in; first cable support on the arc carriage so only roll changes the span.
- **C (hexapod).** At their geometry gravity puts three legs in compression;
  across ±7° with small disturbances four legs change sign, so leg play is
  two-sided. A gas spring on the hexapod axis (110–185 N, internal preload)
  keeps all six in tension; Tr8×8 back-drives, Tr8×2 self-locks. Branch C-w:
  my six wires as their software-pivot hexapod — concurrent wires change
  ≤ 1.2 mm over ±10°, angle wires 16–41 mm, all taut ≥ 1.1 N.

### What changed in how I see my own ideas

- A soft carrier under motors must be constant-force (balancer, counterweight),
  and should bias each drive to one side rather than cancel its load exactly:
  float slightly less than 100 %, offset from the CoM.
- Preload is what turns cheap play into a calibratable offset; the camera loop
  is what then reaches tenths. They need each other.
- My wire-located suspension is a cable hexapod; the first motor would be the
  W6 anchor (grip-axis roll alone).
- With the camera measuring the last dry lap, a locator only has to hold
  through weld-onset loads (1–3 N of wire push/drag if the trigger closes in
  the shell).

## Wave 3 (2026-09-28) — objections, and supports that switch state

### Objections worked (machine-that-learns on my ideas)

- **Suspension.** Their servo model says a camera and motorised anchors
  cannot hold a soft float through the weld-start push: undamped, no stable
  loop; damped (ζ 0.5), drift is nulled but 2 N gives a 17 mm transient. I
  agree: the float places and cancels drift; a mechanical lock holds.
  - Added A-r4c (theirs: rod clamps, learned lock bias).
  - Added A-r4d (mine): the X bungee seats a V-shoe on a vertical steel rod
    (the bungee's first locating job), and a switchable magnet in the V locks
    it. The lock only adds preload.
  - Damper: an eddy-current vane from the C110 stock.
- **Wire-located suspension.** Accepted: plan angle as tangent translation
  keeps the layout taut (±15°, ≥ 1.3 N) where vertical rotation slackens it;
  roll is W6 alone; camera keep-out and spoke shielding; bungee preloads drift
  4 N over 40 mm, so balancers or a seventh wire.
  - New: answered one-knob-one-parameter's question. A strictly diagonal map
    is impossible (at one attachment point all three rotations move it in the
    same 2-D plane), but a practical one exists: W4 = hole (4.74 mm/°), W6 =
    roll (1.05 mm/°), W5 holds vertical, W1–W3 = dot. Taut ≥ 12.9 N with
    ~47 + 56 N preloads.
- **Rim carriage.** Added D-s (theirs): stylus senses, a stage acts,
  something else carries. Noted where the stylus must stand (on the gun's
  carrier), and that with a locked support D-s becomes the weld-time runout log.

### New direction: supports that switch state (`ideas/switch-lock-skate.md`)

- Lock shift sorted into three causes:
  - load changing hands (the float removes it);
  - gap-closing locks (clamps, collets, arms: hundredths to tenths);
  - preload-increasing locks (magnet or vacuum on contacts already touching:
    micrometres).
- Arrangement E: a MagJig 95 shoe on three balls skates on a steel plate beside
  the tube. The plane gives X and plan angle by hand (Y slide = vertical-axis
  turn), plus a don't-care slide. One switch locks it; magnetic stops remember
  the pose.
  - Holds ~24–39 N sideways (≈10× the in-weld loads).
  - Contact shift ~3 µm; ~360 N/mm estimated at the dot.
  - Enemies: the knob's twist, debris (0.05 mm speck → 0.1 mm at the dot),
    plate flatness.
- Branch E-dome: skate on a sphere centred on the dot for all three rotations;
  printed patch, vacuum lock; profile error ≈ dot error, cleaned up by the flat
  skate.
- Table of the other switch-state supports with real capabilities: Noga and
  HHIP central-lock arms publish no tip stiffness; FISSO Strato µ publishes
  30–56 N holding force. With a float carrying, 30–56 N is ample; lock shift is
  the question.

### Questions this adds for Derek

- Whether a steel post and plate beside the tube may be bonded to the work
  lead (interlock path through the shell).
- The real MagJig force across a 0.2–0.3 mm stand-off and its knob torque (one
  bathroom-scale test).

## Wave 4 (2026-09-28) — exchange with work-as-datum; a combination

### On work-as-datum's work-hung suspension (`../../exchange/carry-and-locate--on--work-as-datum-w4.md`, `calc/wad_nose.py`)

- **Nose share.** With nose, base Z wire and third ring all present, statics
  put only ~4.1 N on the nose (ring 7.2, base 4.4), not the 7–10 N of a
  two-support split.
- **Groove at its limit.** Gravity splits the nose load 0.70 into the V and
  0.71 along the barrel, so a 90° groove sits at its limit under gravity alone.
- **What unseats it.** A +Y stuck-wire drag of 5 N or a 10 N hand unseats the
  nose. A 5 N cable lift slackens the base Z wire.
- **The pattern:** the nose's locating is borrowed from the weight it carries.
- **Repair D1-p:**
  - a sprung jaw (~25 N) closing inside the loop;
  - a base Z pair (wire plus bungee);
  - then the weight can go to a float, the tube carries ~nothing, and the
    third-ring trade disappears.
- **Room lines:** the base lines reach the dot at 0.165, so anchor them on the
  rotator frame.

### Combination (`ideas/nose-and-tail.md`, sketch `F-nose-and-tail.svg`, `calc/nose_tail.py`)

- Nose on the work (their D1 hanger plus my jaw) for the dot's translations.
- Tail on a table beside the rotator for the angles:
  - height screw = hole 0.23°/mm;
  - cross-tilt screw = mostly roll;
  - one ball-ended link to a magnet-braked carriage = plan angle.
- Float and saddle carry.
- **Key break:** my switch-lock shoe locked at the tail made the constraint
  count 9, so the work-following nose would fight it every revolution
  (~6–25 N cycling, estimate). **Repair:** rolling ball transfers plus one
  lockable DOF, giving 6.
- **General rule:** a lock at a point not referenced to the work may lock only
  what the work-referenced point doesn't set.
- Tube length: +1 mm tips hole 0.23° and the dot misses by 0.18 mm; raising the
  table 1 mm cancels it exactly.
- Float hooked ~85 mm off the centre of mass at 77 % keeps both tail balls
  seated.

### Correction noted

My first reading of their D1 (nose 7–10 N) was their number; mine (4.1 N) uses
all three supports. If the third ring moves nearer the nose–base line, the nose
share rises. That is their choice to make.

## Wave 5 (2026-09-28) — final pass

- **Work-as-datum's critique of E accepted.** The room plate at the nose
  becomes the dot's reference: debris ×2.2, switch twist 1.06 mm/°, and tube
  length and runout pass through.
  - Recorded their R-A (cup centred on the dot on the plate hanger, plus my
    shoe with a round bore at the tail), R-B and R-C in
    `ideas/switch-lock-skate.md`.
  - E-RA is now the lead form. My additions (E-RA+): roll on a screw pad on
    the same shoe, and the cup seated by a spring rather than weight (the same
    finding as D1-p).
  - E-RA is determinate by the nose-and-tail rule.
  - New sketch: `sketches/E-RA-cup-and-tail.svg`.
- **Readability pass.** Every idea file now opens with "Picture it", its
  sketch(es) and its major unresolved problems. All sketches are regenerated at
  the true opening pose (A–D after the wave-2 dial fix; E, E-RA, F, X-mtl-B and
  X-mtl-C drawn at the true pose).
- **Summary.** The harness refused a separate `summary.md` for this subagent,
  so the summary entries went back to the coordinator in the final reply.
