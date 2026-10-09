# sequence-of-use — summary entries

**The view.** The procedure is the machine. A session runs:
1. load
2. seat and indicate
3. plate at recess
4. eight tacks
5. aim and dot dry run
6. weld
7. stuck wire
8. gun away
9. unload or invert
10. next tube

Across these phases the gun must be out of the way, then precisely located, then
perfectly still, then able to return to a remembered pose. Chart:
`sketches/session-states.svg`.

This explorer started without Derek's examples. A–D and F come from beyond them;
E is his monitor arm. All geometry uses the proxy gun at the true opening pose
(grip 45, hole dial 30, vertical −15); older dial-65 values are labelled where
kept.

## A. Lid carrier

The shell rides a lid frame through X/Y slides and a printed recipe block.
- **Hinge:** parallel to the tangent, 200 mm outboard on the station side, 60 mm
  above the rim. A sweep of 80 candidate hinges showed this family is the only
  one where the wire tip leaves the corner up and inward without touching the
  lip. It holds at both dials.
- **Closed:** three balls sit in vees on posts behind the station, with a latch
  (who-moves-what's branch A-r). The hinge pins float in slots.
- **Open:** the lid goes over-centre at 71.5° and rests at 88°.
- **Height and cable:** per-tube height is set on the work with one knob against a
  rim flag. The umbilical is clamped to the lid.
- **Breaks and repairs:**
  - hinge fighting the seat → slots;
  - cable tugs → latch;
  - wire tip as a second contact → stickout 1 mm short;
  - unlatching dips the tip by 3.6 × slot clearance, because the centre of mass
    lies outside the ball triangle → release by the lifting handle, tight slots;
  - a stuck wire can unseat the three-screw base → stiffer hold-down.
- **Parts:** PGN 1/2 in balls $9.45 (946 reviews); 6 × 30 dowel pins $6.99; 4001
  toggle latch $8.35 (400+/month); 50 N gas struts $8.99. All Prime, observed.
- **Unresolved:** real centre of mass and cable pull; tack method; tower
  positions; yaw by slide limited to −25…+5°.
- **Files:** `ideas/lid-carrier.md`, `sketches/lid-side-view.svg`.

## B. Gun stays, work travels

The gun, umbilical, conduit and camera are fixed on a portal for the session. The
rotator's carriage runs 20 mm low and climbs 60 mm ramps into three vees on a
cross-slide plate (branch B-r).
- **Exit rule:** the tube can leave only along X from the station side, within
  ±20°, after dropping at least 10 mm or retracting the wire 14 mm.
- **Height:** screws between the carriage and the rotator, set against a rim flag
  on the portal.
- **Plate:** held by the stand-hung plate head (entry H).
- **Why:** the umbilical force becomes a session constant, and aim is verified
  rather than set per tube.
- **Parts:** LONTAN drawer slides $22.99, only 16 left (as a guide only).
- **Unresolved:** plate-head spring against face wobble; ~600 × 350 mm footprint;
  operator on +X; purge hose on the carriage.
- **Files:** `ideas/gun-stays-work-travels.md`, `sketches/drawer-lift.svg`,
  `sketches/x2-plate-hung-from-P.svg`.

## C. Rim-riding saddle

Five stainless rollers ride the cold arriving side, which is −Y at the true pose
with the table turning counter-clockwise.
- **Contacts:** two on the rim top, two on the outside wall, one lower on the
  wall. The saddle stays under ~35 mm above the rim to clear the wire and barrel.
- **Load:** a balancer at the gun's centre of mass, which sits outboard at
  (−30, −108), plus a separate small preload. A tether takes the rolling drag.
- **Branches:** C-h, the saddle held by hand, is the cheapest test. C-p
  (who-moves-what) takes height from the plate face with ball transfers at
  −40…−70°.
- **Parts:** 440C S608 bearings $9.99 for 10; QWORK balancer $16.97, 50+/month.
- **Unresolved:** real forces against preload; residuals the contacts cannot see;
  heat; whether following is needed at all.
- **Files:** `ideas/rim-riding-saddle.md`, `sketches/rim-saddle.svg`.

## D. Gauge-set, lock-held

A printed rim gauge sets the pose and a lockable holder keeps it.
- **Breaks:** the holder's tip shifts when locked; the gauge must pass the wire;
  the Noga DG61003 ($110) is built for grams, not the gun.
- **D-r (who-moves-what):** a printed block for the angles, lead-screw slides for
  yaw and radius, a retractable foot for per-tube height on the free +Y side.
- **D-m:** the foot read at the eight between-tack angles gives a runout map.
- **Sequence addition:** index 22.5°, touch, retract, index back to tack 1. The
  original gauge stays as a pose checker.
- **Files:** `ideas/gauge-set-lock-held.md`, `sketches/d-gauge-foot.svg`.

## E. Derek's monitor arm, carry–park–dock *(Derek's example)*

His words: "arms designed to hold monitors in a position on a desk."
borrowed-ecosystems' A0 shows it floats rather than holds: zero-rate spring,
friction swivels, 2 kg minimum.
- **States:** the arm carries in every state and never locates.
  - Park: a cradle with a nozzle cap and stickout gauge.
  - Hand: a bail at the centre of mass makes the gun weightless, so hand tacks
    stay possible.
  - Dock: vees, a latch, a rim flag, the recipe stack and a Bowden lever.
- **Umbilical:** a saddle at the natural apex (~420–450 mm above the bench), which
  at the true pose sits past the bench's front edge on −Y, so the operator works
  from −X.
- **Repairs:**
  - carry pins;
  - trim, drag and friction on the bail (borrowed-ecosystems);
  - saddle height corrected from the dial-65 figure;
  - Bowden as the main trigger. An unpowered servo can stay where it stopped with
    the trigger pressed, so a servo belongs on the dock post, where undocking
    frees the trigger.
- **Open disagreement (mild):** carry pins vs trim for docking a gun hung at its
  centre of mass. Trim is exact at only one attitude, so here the pins do the
  docking and trim sets hand feel.
- **Branches:** M0 (weight relief only); M2 (pole arm plus balancer, needs bearing
  hinges or becomes the film arm); M3 (joint encoders); E-f (the film arm).
- **Parts:** HUANUO FlowLift Pro $29.99, 4K+/month; Shimano cable set $15.49,
  1K+/month; M8 plungers $8.99 for 6.
- **Unresolved:** the hand-to-dock transition; the arm's friction band; the dock
  post against the towers.
- **Files:** `ideas/monitor-arm-session.md`, `sketches/w3-monitor-arm-session.svg`.

## F. Teach by hand, record, replay

The hand finds the pose on the weightless carrier. The record runs on one clock,
in the joint frame: tags plus IMU on the shell, the joint camera, console degrees
and a trigger switch.
- **Recipe:** a file plus a printed block. The wire-escape sweeps validate a
  taught pose before printing.
- **Replay:**
  - R1: dials and block, then dock;
  - R2: a guided hand with live error bars;
  - R2b: magnet locks on the joints (weakest);
  - R3: motors.
- **Resolution (estimates):** tags ~0.1 mm and 0.1–0.3°; dot 10–20 µm; IMU
  0.2–0.5°; digitizer arm ~0.3 mm with 14-bit encoders.
- **Parts:** BNO085 $20.49, 100+/month; AS5048A $14.24; uxcell 100 N holding magnet
  $9.99.
- **Unresolved:** the pose-to-dial model; tags under weld light; how steady a
  guided hand is.
- **F0:** record today's hand practice with a tag plate and IMU, no carrier.
- **Relation:** borrowed-ecosystems' F (hand-steered isocentre) is the isocentric
  cousin of R2.
- **Files:** `ideas/teach-record-replay.md`, `sketches/w4-teach-record-replay.svg`.

## G. Branch contributed to who-moves-what's still gun

Drawer play is yaw: 0.5 mm of slide play is 0.46°, unobserved. The wire, not the
nozzle, sets the exit. Repair: ramps into vees on their cross-slide, which also
supplies the drop. `../../exchange/sequence-of-use--on--who-moves-what.md`.

## H. Stand-hung plate head

Fixes tacking for every stored-pose arrangement.
- **Mechanism:** a stationary arm over the far rim carries a spindle fork that
  catches collars on two 1/4 NPT plugs in the plate's ports. A spring pulls the
  plate against three pads set at the dot's height; a rim flag sets the lip.
- **Result:** the corner sits at the dot's height for any tube length, and the
  eight tacks become fixture pulses.
- **Pose fix:** pads at 45°/150°/255°, frame 15 mm above the rim, 38.8 mm
  centre-line clearance to the barrel. The wave-2 layout hit the barrel at dial
  30; who-moves-what independently re-clocked it to 30°/150°/250°.
- **Parts:** Joywayus 1/4 NPT plugs $8.99, 100+/month.
- **Unresolved:** face wobble against the pads; whether plugs may stay in the
  ports while welding.

## I. Branch contributed to who-moves-what's D2 (Derek's rings)

Balancer lines are pendulums (4–8 N pull-back at 300 mm), and two anchors yaw the
gun.
- **Repair:** one trolley on a 2040 rail carries both balancers and the umbilical
  saddle (gantry plate $16.89, 109 reviews).
- **Roll:** roll isn't free; the centre of mass is 85 mm off the grip axis, giving
  0.58–1.01 N·m. Use a roll lock, or give Derek's third ring the job of roll trim.
- **Sketch:** `sketches/x2-trolley-parked-carrier.svg`.

## J. Branch contributed to borrowed-ecosystems' film-grip carrier

A 1–5 N cable pull (130–640 N·mm) beats the gimbal's 2–5 mm pendulosity, so the
gun flips when lifted.
- **Repairs:**
  - carry pins with a printed indexing ring;
  - two hard stops on the rider's Z (LAND, WELD);
  - plate-head fixture tacks;
  - a stickout gauge in their docking cup.
- **E-p:** 60–100 mm pendulosity. Acceptable on the rider, not against a 5 N pull.
- **Files:** `sketches/w4-film-grip-session.svg`,
  `../../exchange/sequence-of-use--on--borrowed-ecosystems-w4.md`.

## Transferable pieces

- the session-states chart;
- the wire-escape rule, and its sweep as a pose validator;
- ramps into vees;
- the stand-hung plate head;
- the rim flag;
- stickout as a sequence number: gauge at park, set 1 mm short, snip first, a
  clear side for the cutters;
- trigger force closed inside the shell, releasing on power loss;
- carry pins and a two-stop Z;
- the umbilical rule: clamp to the carrier, saddle at the natural apex, the same
  shape at the dock, bend not twist;
- the unlatch dip;
- the overlap pointer;
- teach → print;
- the hole dial − 35 convention.

## Questions only Derek's observation can answer

1. How is the plate held at its recess when tacking? Are tacks made with wire?
   Where do wires stick?
2. Gun mass and centre of mass, and the umbilical's pull at the butt (a
   kitchen-scale hang test answers both).
3. Trigger force and travel; the process switch's role; the DB25 pinout.
4. Does the welder show gun-to-work contact live?
5. Is the red beam on without the trigger, does it coincide with the process beam,
   and does it sweep with the wobble?
6. The spread in tube length; is runout eccentric or oval?
7. The real nozzle standoff.
8. Where the rotator's motor and ground towers sit, where he stands, and where the
   cable hangs.
9. Would he accept plugs in the ports while welding, a trigger actuator that works
   only when docked, and a breakaway contact in the pedal loop?
10. Would he record one session with a tag plate and IMU (F0)?
