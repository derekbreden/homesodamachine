# Notebook — sequence-of-use

Framing: the procedure is the machine. Walk one session phase by phase and ask
what each element (gun, wire, umbilical, table, plate, trigger, operator's hands
and eyes, the record) must be in that phase — free, parked, located, still — and
design arrangements whose states change between phases.

## Wave 1 (2026-09-28)

### Sources read

`context/shared-context.md`, `context/working-method.md`,
`hardware/assembly/weld-position.md`, `web/public/js/weld-position/pose.js` (and
the gun proxy in `main.js`), `hardware/assembly/weld-rotation-rig.md` (incl. the
per-weld sequence), `hardware/printed-parts/fixtures/weld-rotator/README.md`,
`hardware/assembly/pressure-vessel.md` steps 1–5, X1 Pro manual pages 12, 17, 20
and the other extracted pages for the trigger, interlock, wire feeder and
sequence settings (13, 16, 18, 19, 22–24, 30–32, 36, 40).

### The session, phase by phase

Chart: `sketches/session-states.svg`.

0 open session → 1 load tube → 2 seat + indicate → 3 plate at recess →
4 shoe + continuity → 5 eight tacks → 6 hanger off, index to tack 1 →
7 aim + dot dry run → 8 weld 380° → 9 stop / stuck wire → 10 gun away →
11 unload / invert → 12 next tube.

What the gun support has to be, reading across: **completely out of the way**
(1–4, 11), **precisely and stiffly located** (7–8), **perfectly still** (9), and
**able to return to a remembered pose** (10 → 7). Only 5 is ambiguous (tacks).

### Findings from walking it (these shaped every idea)

1. **The only lid hinge that works is behind the station.** Swept 80 horizontal
   hinge lines about the posed proxy (`calc/lid_swing2.py`). The wire tip sits in an
   inside corner, so it must leave up *and inward*. Only axes parallel to the tangent,
   on the +X side, rotating the gun up and back, avoid the 6.35 mm lip. (A first
   coarse sweep with 1° steps falsely passed others — the tip jumped through the
   wall between samples; fine steps fixed it.)
2. **A tube can only slide in under a fixed gun from the weld-station side.** For a
   straight approach at angle φ from +X, the wire tip is inside the bore only in the
   last 123.6·cos φ mm; along the tangent it never is (`calc/drawer_path.py`).
3. **Tacks collide with any stored-pose gun.** A plate hanger that bridges the rim
   crosses the station whenever the table indexes between tacks. Either the gun
   retracts between tacks, tacks stay a hand operation, or the plate is held by a
   *stationary* swivel hanger from the far side (kit K1-H2), which also makes the
   tack pattern a fixture operation.
4. **The trigger force goes through the aim chain** if a finger presses the gun in a
   fixture. Close the loop in the shell (Bowden lever, solenoid) or remove it (DB25
   external start, if it exists). A two-stage pedal would *enforce* the per-weld
   order but contradicts the rig's explicit "pedal never commands the laser" rule.
5. **The interlock needs gun-to-work conduction** (manual 3.6.2): the wire touching
   the joint is part of starting. That makes the wire a touch probe (per-tube zero,
   stickout check) if the welder shows conduction live, and it makes stickout a
   sequence-critical number — after every snip it must be re-set (kit K3).
6. **The wire tip is a second contact** at the moment a stored pose seats (A3, B3):
   set stickout ~1 mm short, jog to touch after seating.
7. **The fiber's 350 mm emitting bend radius is the biggest dimension** in any
   carrier. Clamp the umbilical to whatever carries the gun so the gun-to-clamp
   section keeps one shape; cross hinges in a plane perpendicular to the axis.
8. **Per-tube joint height** follows each tube's cut length in any frame-referenced
   arrangement (A, B); rim-referenced ones (C, D) absorb it.
9. The welder's own sequence settings (pullback length/speed, fall time, gas
   post-flow, turn-on/off delay) are part of the machine; pullback is the first
   lever on stuck wire.
10. The overlap is judged at an index mark while watching the puddle: two places.
    A pointer beside the station puts them in one view (K4).

### Ideas

- `ideas/lid-carrier.md` — **A**, developed furthest. Hinged lid behind the station,
  closes onto a three-ball kinematic seat (hinge slotted so it carries nothing when
  closed), over-centre open at ~80°, latch preload, Bowden trigger on the handle.
  Sketch `sketches/lid-side-view.svg` from the proxy.
- `ideas/gun-stays-work-travels.md` — **B**. Gun, umbilical, aim and camera fixed
  for a session; rotator on a carriage that travels 20 mm low and climbs end ramps
  into kinematic seats. Removes umbilical force variation entirely. Biggest problem:
  holding the plate through travel and tacks. Sketch `sketches/drawer-lift.svg`.
- `ideas/rim-riding-saddle.md` — **C**. Contacts on the rim and OD on the arriving
  (cold) side locate the gun only while loaded; balancer + tangential tether carry
  weight and drag. Branch **C-h**: the same saddle held by hand — the cheapest test
  of whether the rim can locate the dot. Sketch `sketches/rim-saddle.svg`.
- `ideas/gauge-set-lock-held.md` — **D**, sketch level. Pose stored in a printed
  rim gauge; a general lockable holder holds; gauge removed before the weld.
- `ideas/session-kit.md` — cross-cutting pieces the sequence forces on every
  arrangement: plate hangers (K1), trigger paths (K2), stickout gauge and touch-off
  (K3), overlap pointer (K4), snip window (K5), umbilical rule (K6), record (K7),
  welder sequence settings (K8).

### Unequal depth

A got geometry, loads, preload and eight breaks. B got the approach-direction
proof, mass/push estimate and seven breaks. C got contact layout, the CG tipping
problem and a hand branch. D is a sketch with its main breaks named.

### Assumptions in play

Proxy gun geometry and the scene's opening pose; gun 1.0 kg at the housing centre;
shell + stage 0.4 kg; lid 0.8 kg; rotator + tube 5–7 kg; operator on −X/−Y (A, C)
or +X (B); table cw for the saddle's arriving side.

### Questions that need Derek's observation

1. What holds the end plate at the 6.35 mm recess while tacking today?
2. Does the welder's monitoring screen show gun-to-work conduction live (touch-off)?
3. Trigger force and travel; which switch is the laser trigger in practice; what
   the process switch does; can it be left covered?
4. Is the red reference beam on without the trigger (for the dry run), and does it
   coincide with the working beam?
5. DB25 pinout: is there an external start input?
6. Measured spread of tube cut length and end squareness across the batch.
7. Gun mass and centre of mass; how hard the umbilical and conduit pull when the gun
   is held still in the welding pose.
8. Are tacks made with wire or autogenous?
9. Where Derek stands now, which hand holds the gun, and which side the grip faces
   relative to the table direction.
10. Wire pullback / patch length settings in use, and whether stuck wires happen at
    the bead end or at tacks.

### Next

Compare with other explorers' mechanisms in wave 2: A/B/C need a fine-aim stage I
did not design; my contribution is where it sits in the sequence and which settings
are per-recipe vs per-tube. Worth taking further: H2 hanger geometry against the
real gun; C-h as a first physical experiment; A's hinge with the scanned gun.

## Wave 2 (2026-09-28) — exchange with who-moves-what; Derek's examples

Read `context/examples-and-history.md`, `context/digest-wave1.md`, and all of
who-moves-what (notebook, four ideas, `allocation_calcs.py`, sketches).
Wrote `exchange/sequence-of-use--on--who-moves-what.md`; calcs
`calc/exchange_w2.py`, sketches `sketches/x2-plate-hung-from-P.svg`,
`sketches/x2-trolley-parked-carrier.svg`.

### What the exchange produced

- **The wire, not the nozzle, sets how a tube leaves a still gun.** Toward −X or
  along the tangent it collides immediately; toward +X it collides after ~121 mm
  unless the work drops ≥10 mm; an 8 mm wire retract frees every direction
  (proxy, 16 mm standoff).
- **Drawer play is yaw** (their 1.08 mm/°): ramps-into-vees on top of their
  cross-slide fix both the play and the drop. My idea B should in turn take their
  cross-slide (B had no X or yaw setting).
- **Plate hung from P**: a stationary head from the gun stand (spindle fork on two
  port plugs, spring pull against three stationary pads at P height, rim flag at
  P + 6.35). Corner height becomes P for any tube length; per-tube Z becomes a
  mechanical rim stop; tacks become fixture pulses. Applies to my B and to any
  still-gun station.
- **Balancer-hung carriers need a trolley**: pendulum pull-back 4–8 N at 300 mm;
  two anchors yaw the gun; the umbilical peak must travel with the gun or the
  dock force changes. One trolley on a 2040 rail carries both balancers and the
  umbilical saddle.
- **D2's free roll isn't free**: proxy CG 85 mm off the grip axis → 0.28–0.49 N·m.
  Roll lock on ring B, or Derek's third ring as a roll trim.

### Derek's examples through the sequence view (for wave 3)

- **Monitor arm.** A carrier whose natural state is "anywhere, weightless". In a
  session that is exactly the tack phase (hand-guided, weightless, the gun can go
  anywhere around a rim-bridge hanger) and the park phase; paired with a seat, it
  also docks for the weld. It answers the question my lid could not: how to keep
  hand tacks when the weld pose is stored. The arm's friction joints must go soft
  at the dock (compliant VESA link). **Strongest candidate for my wave-3 work**:
  arm-carried gun, three states (hand-guided / parked / docked), with the session
  kit.
- **Table opening, rotator beneath.** The table top becomes the stand: the gun
  tip at countertop height, the plate-from-P head and the rim flag mount flush on
  the table around the opening, the overlap pointer too. The shelf drop is the
  loading motion; the side opening is the drawer. Eyes at countertop level look
  straight down onto the joint. Plate insertion and indicating happen below the
  table — worth walking phase by phase.
- **Suspension (rings, wire, bungees).** Reads as a carrier with states: the
  loops must open (a loading phase for the gun itself), the gun hangs weightless
  for hand tacks, and something else locates for the weld. Which bungee axis is
  stiff could change by phase (a bungee clipped to a different anchor for setup vs
  weld). The pendulum/park and roll-torque findings above apply directly.
- **Automated setup.** The session chart is the spec for automation: phases 7
  (aim, dry run) and 8 are the ones software can own; 1–4 and the plate/plug
  steps remain hands-on. The AI's "hours of dry runs" is phase 7 repeated on a
  seated tube, which needs a stored pose (seat, still gun) far more than a
  following one.

## Wave 3 (2026-09-28) — pose fix, objections, Derek's monitor arm

### 0. Pose convention

`main.js` hands `posePoint` hole **dial − 35**; my `calc/proxy.py` passed the dial
straight in, so every wave-1/2 number was at dial 65. `pose()` now takes the dial
and subtracts 35 (default dial 30 = Derek's opening pose); `pose(p, 45, 65, -15)`
reproduces the old numbers. Verified: barrel 45.4°, body back (−60, −144) at 424,
grip base (−1, −234) at 372 — matching the digest.

What changed / what did not (all re-run):

- **Lid hinge sweep:** unchanged. Same 16/160 lines; the chosen hinge gives
  lift-clear 20.5° and column-clear 72.5°; the wire tip sets both.
- **Lid statics:** changed. CG over-centre at 71.5° (was 58°), so park at 88° (was
  80°); closing moment 4.05 N·m; the wave-1 seat never contained the CG.
- **Drawer approach:** unchanged (±20°, ≥ 10 mm drop). The nozzle clears the rim by
  5.0 mm (was 8.8). Wire-retract alternative 14 mm (was 8), because the wire rises
  at 38°.
- **Plate-head clearance:** the wave-2 layout collides at dial 30 (6 mm). New pads at
  45° / 150° / 255°, frame at rim + 15: 38.8 mm (`calc/head_w3.py`).
- **D2 ring roll torque:** 0.58–1.01 N·m (was 0.28–0.49); the grip axis is at 30°.
- **Saddle:** the scene's wire comes from −Y, so the table runs ccw and the contacts
  go on −Y. The CG is now outboard and beyond the contacts (C2 inverted). Balancer at
  the CG plus a small separate preload.
- **Sketches regenerated:** lid-side-view (park 88°, seat behind station),
  drawer-lift, rim-saddle (ccw, CG marked), x2-plate-hung-from-P (new pads),
  x2-trolley (torque note).

### 1. Objections from who-moves-what, and what I did with them

- **A:** their A-r taken whole: seat behind the station, recipe stack on the lid,
  height on the work, yaw-by-slide limited to −25…+5°. Three sequence additions:
  - unlatching dips the gun (CG outside the triangle; tip drop 3.6 × slot clearance)
    → squeeze-to-release, tight slot, stickout short;
  - phase 2 needs a rim flag, not just the indicator;
  - a stuck wire can pop the three-screw base's vee foot (~35 N against plausible
    30–50 N preload) → stiffer hold-down, pedal first, re-check.
- **B:** their B-r taken (seats on a cross-slide plate; Z between carriage and
  rotator). Height is set with the carriage seated, against the portal's rim flag.
- **C:** mirrored to ccw; C2 recomputed; their plate-face tripod kept as branch C-p,
  placed at −40…−70° because the wire descends low on −Y.
- **D:** their D-r (split by rate) and D-m (measuring foot) taken; the pads' +Y side
  is free at the true pose; gauging becomes index 22.5° → touch → index back.
- **No real disagreements.** The additions are about *when* each of their pieces is
  used, and what the sequence does to it.

### 2. Derek's monitor arm → `ideas/monitor-arm-session.md` (idea E)

- Stated as he gave it; borrowed-ecosystems' A0/A1/A2 findings credited (zero-rate
  spring, 2 kg minimum, friction swivels, CG hook, dock).
- **What it becomes:** the arm carries in every state; a park cradle (nozzle cap +
  stickout gauge + positive stop) holds in PARK; a kinematic dock under the gun body
  holds in DOCK; the hand holds in HAND.
  - A **bail at the CG** on a swivel hook serves all three states: weightless and
    freely orientable in the hand, vertical-force-only to the dock.
  - A **fixed umbilical saddle** gives the same cable shape at every dock.
  - A **dock-contact solenoid** fires the trigger only when seated.
- **Main gain:** hand tacks survive alongside a stored weld pose.
- **Biggest open problem:** the free gimbal against the unbalanced umbilical
  (~0.65 N·m for 5 N at the 129 mm cable-exit lever) in the move from hand to dock.
- **Branches:**
  - M2 — pole-mount arm plus balancer: Derek's two examples joined, no 2 kg minimum;
  - M3 — AS5600 joint logging as a record of the hand;
  - M0 — weight relief only.

### Questions added for Derek

- How much does the umbilical twist the gun about its own balance point when he lets
  go of it on a balancer?
- Where are the motor and ground towers around the tube? This decides the dock post
  and the seat posts.
- Would he accept a trigger fired by a dock-gated solenoid?

## Wave 4 (2026-09-28) — exchange with borrowed-ecosystems; teach, record, replay

### Exchange: `exchange/sequence-of-use--on--borrowed-ecosystems-w4.md`

Their E (film-grip carrier) walked through a session
(`sketches/w4-film-grip-session.svg`, `calc/w4_calcs.py` §1):

- **The gimbal's attitude off the tube is set by the umbilical.** A 1–5 N pull at
  the exit, 129 mm from the CG, gives 130–640 N·mm, against 0.9–2 N·mm/° of their
  2–5 mm pendulosity, so the lifted gun flips to the cable's equilibrium.
  - *Repair E-s (carry pins):* M8 pull-ring plungers lock the two non-vertical
    gimbal axes at the recipe attitude whenever the gun is off the tube; a printed
    indexing ring per recipe.
  - *Branch E-p:* 60–100 mm pendulosity. It is acceptable on the rider but not
    against a 5 N pull.
- **Landing and wire-in-corner are one event.** Two hard stops on the rider's Z:
  LAND (tip ~10 mm back along the barrel), then WELD. Lift-off reverses.
- **Tacks with a rider:** a rim-bridge hanger hits its ±60° wheels, so use the
  stand-hung plate head (no conflict with the rider) and fixture tacks.
- **Stuck wire:** take their pedal-loop breakaway (a rig change, Derek's call);
  then slide back, re-seat, and re-trim stickout at a gauge in their docking cup.
- **Back to me:** their arm replaces my monitor arm in idea E (branch E-f), and my
  E1 friction brake becomes carry pins.

### Uncovered direction: `ideas/teach-record-replay.md` (idea F)

- The hand finds the pose on a weightless carrier. Tags plus cameras, the joint
  camera, an IMU, the console and a trigger switch record it, on one clock, in the
  joint frame.
- The recipe is a file plus a printed block. The sweep scripts become the recipe
  validator (taught poses must dock and escape).
- Replay has four physical meanings:
  - R1: dials and a printed block, then dock;
  - R2: a guided hand with live error bars;
  - R2b: holding-magnet joint locks (weakest);
  - R3: motors plus a runout map.
- **Biggest open problem:** the pose-to-dial model (needs the scan and the
  dot-to-shell relation). Until then R1 replays by iteration against the recorded
  dot image.
- **Branches:**
  - F0: record today's hand practice with no carrier (the cheapest baseline in the
    study);
  - F-d: passive digitizer linkage with 14-bit encoders;
  - F-j: carrier-joint encoders (CG position only).

### Questions added for Derek

- Would he spend one session welding exactly as now with a tag plate and IMU on
  the gun (F0)?
- Does the welder's screen or LED expose trigger state for logging, or should a
  microswitch read the presser?

## Wave 5 (2026-09-28) — final pass

- **borrowed-ecosystems' critique of idea E, all accepted into the idea file,
  labelled:**
  - the saddle at the natural apex (~420–450 mm; 680 was dial 65). New
    consequence: at the true pose that is past the bench edge on −Y, so the
    operator works from −X;
  - trim, drag and friction on the bail, complementary to my carry pins: pins for
    carrying and docking, trim and drag for the hand's feel;
  - the solenoid overheats: the Bowden is the main route, with my safety note that
    an unpowered servo may hold the trigger, so any servo goes on the dock side and
    hit-and-hold is the fail-safe electrical option;
  - M2 needs bearing hinges or becomes E-f.
- **Readability pass:** every idea file now opens with "Picture it", its sketch
  paths and its major unresolved problems. The originals are kept below, marked.
  New `sketches/d-gauge-foot.svg` (D at the true pose); `w3-monitor-arm-session.svg`
  updated (saddle, operator).
- **`summary.md` was not written.** The file tool refused it as a report file.
  The summary (entries A–F, contributed branches G–J, transferable pieces, Derek
  questions) went to the coordinator in the wave-5 reply, for them to place.
