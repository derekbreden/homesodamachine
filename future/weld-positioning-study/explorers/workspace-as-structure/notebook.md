# Notebook — workspace-as-structure

Way of seeing: the workspace (tables, openings, frames, plates, shelves, the
rotator's own mounting) is the first positioning stage. Arrange structure so
the nominal pose is built in and the residual adjustment is small, and so the
motions that must be easy are easy and the ones that must not happen can't.

## Wave 1 (2026-09-28)

### What I did

- Ported the scene's `posePoint` and proxy housing to Python (`geom.py`) to
  find where the gun body, grip base and cable exit sit relative to the rim and
  the bench for several poses. That fixed most layout decisions.
- Rough numbers in `loop_calcs.py`: how Z errors map onto the dot, a wood-top
  lean, post stiffness, sled contact sensitivities, tube thermal growth.
- Sketches generated to scale from the proxy: `sketches/make_sketches.py`
  → five SVGs.
- Sourcing in Derek's Chrome (own tab, read only): bench specs, rails, lead
  screws, extrusion, aluminium tube, SendCutSend MIC-6/steel, granite plate,
  cross-slides, micrometer heads, steel balls, switch magnet, lab jack. Home
  Depot showed a bot-protection page; not bypassed.

### Ideas (files in `ideas/`)

1. `table-opening-gantry.md` — Derek's branch as described, developed: gantry
   beside (not over) the opening, gun resting on it at countertop height, Y
   rails either side, four-screw shelf, side unloading by shelf drop so the
   gun never moves between tubes. Edge version kept as a branch. **Deepest.**
2. `drop-in-collar.md` — repair for the break in (1): one laser-cut plate
   carries rails above and posts below; the wood only supports it. Adds a
   magnetic-base datum beside the mouth.
3. `countertop-sled.md` — the plate at rim height is the stage: three ball feet
   (Z + two tilts), fence (X + heading), stop (Y), spring preload = 3-2-1
   kinematic mount; the gun lifts off and returns to its pose. Motorized form:
   six stationary actuators at the six contacts; branch with a light pusher
   gantry; branch "the rotator grows a deck" (no hole in any bench).
   **Deep.**
4. `fixed-gun-moving-shelf.md` — the gun bolted to structure, XY + Z under the
   rotator; cables never move; live runout following by moving the work.
   **Medium.**
5. `lidded-mouth.md` — seed only: a stationary lid over the rim carrying gun,
   camera and gas ports.

### Findings that cut across arrangements

- **Where the gun is** (scene proxy, opening pose, rim flush with a surface):
  body 70–200 mm above the rim plane, entirely on the −Y side of the mouth and
  over the tube's centre line in X; grip base ~133 mm up and ~233 mm along −Y;
  the grip axis leaves at 30° elevation, 15° off the tangent. Only the barrel
  and nozzle cross the mouth; **the nozzle tip is ~5 mm above the rim** (≈1 mm
  at hole dial 10°). So an opening only needs to pass the tube (Ø150–160), and
  anything that holds the gun can sit on solid surface beside the mouth.
- **Tangent slide = vertical-axis turn.** Sliding gun or work dy along the
  tangent at fixed heading lands the dot where the local tangent is turned
  atan(dy/R) = 0.93°/mm; radial error dy²/2R (8 µm at 1 mm). The vertical-axis
  control can be a straight slide, and the tangent is the forgiving axis —
  the right direction for retracting, for a breakaway, and for stops that
  don't need to be precise.
- **Z moves the dot along the beam.** At the opening pose the beam runs 45°
  down and 50° off the radial; 1 mm of cap height moves the dot 0.64 mm across
  and 0.75 mm along the seam. Less grip roll → Z matters less across the seam.
- **A stuck wire pulls along the tangent** (the tube surface carries it).
  Whatever holds the gun along Y is what a stuck wire loads.
- **Operator/camera view.** The recessed corner (6.35 mm deep across a 124 mm
  bore) is visible from nearly any point on the near side a few degrees above
  the rim plane. Put the dot on the far wall from the operator; put a camera
  on the +Y side, opposite the gun. From the front the nozzle tip can hide the
  dot (it sits 7 mm in front and 11 mm above).
- **Trigger force belongs inside the shell.** A hand on the trigger of a
  supported gun loads the support during the weld and unloads it at release.
  An actuator reacting against the shell itself keeps the force internal.
- **Guidance and lift are separate parts.** Four Tr8 screws as posts:
  ~70 N/mm sideways; four 1 in × 1/8 in aluminium tubes: ~2,900 N/mm.
- **Loop through wood:** a 200 N lean on a 30 mm hardwood top → ~0.1–0.5 mm
  gun-vs-tube motion when gun and tube hang from the same top. A single
  collar plate (or a deck on the rotator's own base) removes the wood from the
  loop.
- **Tube length and cap seat** move the dot in Z in every arrangement that
  seats the tube by its far end; a per-tube Z trim or a top-rim touch-off is
  part of the process.
- **Thermal growth** of the ring near the joint: 50–200 µm radially for
  50–200 K (316L). No structure prevents that; flagged for measurement
  explorers.
- **Purge hose:** a shelf open underneath (Derek: no shelf beneath it) lets the
  argon hose come straight up through the shelf hole and the rotator's Ø90
  passage for both closures, and lets side loading connect the hose after the
  tube is in.

### Open problems

- Angle experiments: the table/fixed-gun branches hold grip-axis and hole-axis
  angles in named printed saddles (discrete). The sled's six-actuator form can
  compose small rotations; big sweeps need an arc guide or a stage from another
  explorer.
- Contact cleanliness and spatter near a sled plate at rim height.
- Wobble-motor vibration vs. a gravity-held sled — unknown.
- Whether the tube lifts cleanly off the nest with the shelf dropped (OD guide
  height, copper-shoe preload).

### Questions that need Derek's observation

1. Where are the VEVOR 72 in top's crossbars? Is there room for a Ø160 opening
   ~650 mm from the −Y end, near the front edge — or would he rather not cut a
   top (deck or free-standing collar)?
2. Gun mass and roughly where it balances; how stiff the umbilical + wire
   conduit loop is (does it push a 2 kg object across a table?).
3. Trigger force, and whether a lever/servo on the trigger is acceptable.
4. Where the cart parks relative to the bench today, and the wire conduit
   length.
5. Is a countertop-height mouth (look down into it) better for him than the
   current chest-height joint?

### For the coordinator

- The tangent-slide equivalence and the "nozzle 5 mm above the rim / body over
  solid surface" geometry are useful to every explorer; `geom.py` reproduces
  the scene's pose math for anyone who needs positions.
- The sled's 3-2-1 motorized form overlaps with any explorer doing
  hexapods/stages; the pusher-gantry branch overlaps with suspension (the plane
  as the weight-carrying support, the pusher as the positioner).

## Wave 2 (2026-09-28) — exchange with work-as-datum

File: `../../exchange/workspace-as-structure--on--work-as-datum.md`. New files
here: `axis_clearance.py`, `wave2_calcs.py`, `sketches/make_wave2_sketches.py`
→ `sketches/paddle-compass.svg`.

- **Found:** work-as-datum's `pose_geometry.py` passes the hole angle to
  `pose_point` without the scene's −35° offset (main.js line 198), so its
  "opening pose" is dial 65. At the true opening pose (dial 30) the column
  over the tube axis is open (every gun surface ≥ 38.8 mm from the axis; ≥ ~21 mm
  across dial ≤ 40), the grip base is 233 mm from the axis (not 118), and a
  1 mm-high corner moves the dot 0.64 mm onto the plate (not 0.34). The
  digest's "gun body sits almost over the tube axis" holds only for steep
  hole dials (≥ 50).
- **Paddle compass** (branch of their endcap compass): centre pin (x, y) +
  two rollers on the plate on the dot's radius (height, tilt about Y) + one
  foot and fence on a room plane under the grip (roll about the dot's radius,
  azimuth). The dot lies on the roller line, so the room-set rotation doesn't
  move it. Inradius ~33 mm vs 17.5; weight, trigger and cable loads land on
  the room. A 20 N hold-down spring on the centre pin clamps paddle to plate
  with zero net force on the loose tube. Tube length becomes 0.23°/mm of
  harmless roll.
- **Lip-collar-track:** a follower 25° ahead leaves 43% of runout error and
  85% of ovality error. Branch: map the wall at the dot's own azimuth on a
  cold lap with the gun lifted off, and replay by moving the work (X stage,
  shelf Z). Keep a live contact only for weld-time drift (map for shape, live
  for drift).
- **Between-centres:** at dial ≤ 40 the tailstock is a vertical quill down the
  axis from a bridge on the collar; the collar is B's sub-plate; the quill
  reading is the per-tube height gauge for the shelf.
- **Their per-tube height finding changes my table opening's routine:** return
  the shelf to a *plate reading* (plunger or quill on the collar), not to a
  crank number; add 3–4 mm of drop travel.
- **For my own ideas next wave:** the sled and gantry should borrow the puck
  (second opening, second fence/stop), and every room-referenced arrangement
  needs the per-tube plate reading built into the collar.

## Wave 3 (2026-09-28) — objections worked, new direction

### Objections from work-as-datum, worked into my files

Source: `../../exchange/work-as-datum--on--workspace-as-structure.md`.

- **Table opening: "the crank repeats the nest, not the corner."** Accepted.
  The payoff line overstated what was repeated by construction.
  - Adopted their collar centre as branch **T-W1**: a spring plunger on a +Y
    collar arm drops into a countersink on a port seat; crank the shelf to the
    dial's zero and lock. Length and radial runout leave the pose; face tilt
    stays as one per-tube reading.
  - Added: let the plunger rotate in its ball bushing; the arm clears the gun
    at the true pose; crank-to-zero with a NEMA 17 plus an RS232 dial is the
    automated per-tube height set.
  - Their sprung shelf (**T-W1b**) is recorded but not preferred: it puts the
    rotator on springs, and a motorized crank removes its main advantage.
- **Lidded mouth.** Adopted L1 (the lid rides the plate, parks on the collar)
  and L1a (nose ring on the lid, tail on the collar, 0.12d residual).
  - Found: the ring load (6–8 N, estimate) lands ~40 mm outside the lid's
    ball triangle and tips it. Repair **L1h**: a ~30 N hold-down through the
    centre pin, zero net force on the tube.
  - Branch **L1p**: paddle contacts on the lid give exact dot geometry and
    nothing on the copper nozzle.
- **Sled, moving shelf, collar:** short wave-3 notes added.
  - Sled: stays on the collar with T-W1; the puck gets a second opening.
  - Moving shelf: W1 and rotator-X following are exclusive on one axis.
  - Collar: point the indicator at the plate face near the corner.

### New direction: `ideas/cart-station.md`

The station built on the Weldpro cart around the cable system.

- **Layout:** weld module (rotator + gun support on one plate, three hard feet)
  on the upper tray; the X1 Pro on the bottom tray with the middle tray
  removed; feeder on the module; argon at the rear with a purge line straight
  up through a tray hole.
- **Cable:** a rear mast saddle gives the umbilical one fixed R 375 bend. The
  excess ~3 m is stored as an S of opposite turns (no net twist) on the side
  panel.
- **What it makes easy:**
  - the cable force is a constant, measurable once;
  - short fixed conduit and gas lines;
  - counter-height mouth without cutting a bench;
  - mobile and transferable as one piece.
- **What it makes hard:**
  - up to 2.5 kW of unit heat below the module;
  - sideways tipping (~180 N·m margin vs a 200 N lean at 1 m);
  - space (531 × 330 tray: paddle, sled or bridge, not a gantry);
  - excess umbilical storage.
- **Principle found:** park or lift the gun by rotating about an axis through
  the cable exit, perpendicular to the cable's bending plane. The cable only
  bends in its own plane. Rolling about the grip axis is the motion that
  twists it.
- **Branches:**
  - cart docked to a bench station (fixed cable shape for the table opening);
  - the cart mast as a travelling overhead anchor for other explorers'
    balancers.
- **Drill press, from its manual:** 2 in stroke, 8 in swing, 1.75 in column.
  The whole press can't straddle the rotator (its column would sit inside the
  base footprint). Its quill is a ready-made W1 or W1b centre if transplanted,
  but it's a production tool.
- **Pegboard:** storage and cable hooks only.
- **Ceiling rails:** others developed them; the cart mast is the portable
  version.

New files: `cable_path.py`, `sketches/cart-station.svg` (in
`make_wave2_sketches.py`).

### Questions for Derek (added)

- Tray heights on the Weldpro, and where the unit, feeder and cylinder sit now.
- Where the umbilical and the unit's cooling air leave the X1 Pro unit.
- Wire feeder size and conduit length.
- Would he move the unit to the bottom tray (middle tray removed)?

## Wave 4 (2026-09-28) — exchange with machine-that-learns; one combination

### Exchange on E, the motorised table station

File: `../../exchange/workspace-as-structure--on--machine-that-learns-w4.md`.

1. **Stuck wire vs motorised Y.** In the rig's direction (wire on the arriving
   side, from −Y) the surface drags the wire *away* from the gun. After the
   stick-out bends over, that is tension, bounded by the rotator (~140 N)
   before the wire (~250–320 N, estimate). A belt-driven Y holds ~60 N and
   would slip silently: a plan-angle error of 0.9° per mm.
   *Repair:* a 20–30 N ball-detent breakaway between the belt clamp and the Y
   carriage, with a switch as a Klipper endstop, halt, then re-home.
2. **E's head at countertop height (its open problem).** Branch E-s: the tilt's
   remote centre comes from two rollers on the plate on a line through the dot,
   and the tilt motor is a lead screw lifting the room foot P3 under the
   collar. The head shrinks to the roll yoke.
3. **Umbilical first clamp before the head.** Roll twists ~0.87× roll into
   ~100–150 mm (~90–130°/m).
   *Repair:* loose ring near the butt, first hard clamp at a fixed saddle
   ≥ 700 mm away.
4. **Stylus heat checked.** ~50–100 K peak 9 mm below the corner (thin-plate
   Rosenthal, worst case). Warm, reads the real thermal bulge. The tube seam and
   wall thickness are subtracted with the dry-lap map.
5. **The +Y side is shared** by camera, W1 arm, PTZ, lid and rollers: needs an
   azimuth/height budget.

### Combination: `ideas/split-mount-station.md`

Sources, credited and left intact:

- work-as-datum: port seat, compass, L1 park, puck;
- machine-that-learns: E's motor order, observation layer, dry-run rule;
- carry-and-locate: open C-ring roll;
- one-knob-one-parameter: tilt on the gun, work vertical;
- mine: collar, table opening, sled, paddle.

The station:

- **Hub pin:** x, y from the plate centre.
- **Rollers P1/P2 on a carrier:** on a line through the dot, 30° off the
  radius toward +Y. They give dot height and tilt across the line.
- **P3 on a motorised lift on the collar:** exact rotation about that line.
- **Fence:** azimuth.
- **Magnets:** Derek's RC62 rings on a 430 disc as an internal hold-down.
- **Micro-slides:** X/Y between paddle and carrier (the rollers ride with the
  gun, so the dot stays on the line).
- **Sensing:** an inclinometer for both rotations; the camera for the dot.

**Found:** rollers on the radius don't fit. A holder at (36, 0) is 4 mm from
the nozzle and collides at vertical −30°; the nipples sweep r ≤ 27 on the
other side. My wave-2 paddle was checked only as a point. The 30° line clears
by 15–22 mm; dot height = 1.61·P1 − 0.61·P2; P3 lift 4.9 mm/°.

**Costs:**

- Y trim only −4.6° … +2.3° around a built-in nominal, so bigger plan-angle
  changes are carrier changes;
- the hold-down is required (a roller unloads without it);
- spatter under a roller shows up as a spike at the dot.

**Biggest open:** the scan-based clearance through the tilt range, and whether
a 30°-mixed tilt axis suits Derek's experiments.

New files: `split_mount.py`, `sketches/split-mount-station.svg`. Correction
appended to the wave-2 exchange (P1 on the radius collides).

## Wave 5 (2026-09-28) — final pass

- **Cart station vs machine-that-learns' critique.** Recorded in
  `ideas/cart-station.md` (wave 5 section).
  - Accepted their reading of the manual's 2500 W as maximum electrical draw:
    ~0.8 kW of heat while firing at 60 %, for about a minute per closure; idle
    draw unknown.
  - Adopted their H1: common-mode layout, thermistors, a drift model fitted by
    the camera.
  - Branch M (X stage under the rotator on the cart). Two notes: the retract
    needs the cable-exit park (~5° nose-up, ~22 mm) first; M and a work-riding
    gun support are alternatives on the cart.
  - Partial disagreement: gun-side motion doesn't spend the constant cable
    shape if the cable force is a repeatable function of pose. Hysteresis on
    the saddle is what would. Test by approaching a pose from both sides.
- **Readability pass.** Every idea file now opens with Picture it, sketch
  paths and major unresolved problems.
- **summary.md.** The harness refused to let this subagent write a summary
  file. The summary was returned inline to the coordinator instead.
