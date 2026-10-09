# work-as-datum — notebook

## Wave 1 (2026-09-28)

### The framing I worked from

The pose that matters is gun-to-corner, and the corner moves: it turns
(wanted), runs out, is reseated, is a different tube next time, and is upside
down for the second closure. The fillet is a flat circle on the end plate's
perimeter. Two things follow from that shape:

1. **Rotation about the circle's own axis is the one freedom that doesn't
   matter.** Turning the gun about the plate's axis only moves the dot along
   the seam. So a support that takes five freedoms from the work can leave the
   sixth loose (or give it to the cables).
2. **The corner's best datum is the plate, not the tube or the rotator.** The
   plate is thick, flat, stiff, mostly cold, and it is literally one side of
   the fillet. Its centre is findable through its two tapped ports (on one
   diameter, ±19.05 mm [Repo]). The tube's rim is a saw cut; the rotator axis
   is one step removed; the room is two steps removed.

The datum ladder, with what each rung leaves as residual:

| "Fixed" fixed to | Absorbs | Leaves in the pose |
|---|---|---|
| room / bench | nothing | bench flex, rotator placement, runout, tube length, inversion |
| rotator axis (one sub-plate) | bench, rotator placement | runout (indicate each tube), tube length (per-tube height set) |
| axis + tailstock on the plate centre | + radial runout, tube tilt; clamps the loose tube | face tilt; height set once per tube |
| the plate itself (floating gun) | + height, tilt, inversion, reseating | laser-cut and slip-fit radial (~±0.19 RSS est.), and every force on the gun |
| the tube wall at the weld | + local ovality | lip compliance, rim waviness, heat |

### What I found that changes the problem

- **Tube length is the biggest pose error nobody has been counting.**
  OnlineMetals states ±0.125 in cut tolerance [Obs]. The tube stands on its
  far rim in the nest, so corner height = tube length − 6.35. At the scene's
  opening pose, a corner 1 mm low puts the dot 1 mm up the wall and the
  focus 1.05 mm off; 1 mm high puts it 0.34 mm onto the plate
  (`datum_budget.py` §1). Runout acceptance is ±0.15 face / ±0.125 radial by
  comparison. Any gun fixed to the room or the axis needs a per-tube height
  set; the same tube gives the same height for both closures.
- ~~At the opening pose the gun's body sits over the tube axis~~ **Wrong —
  corrected in wave 2.** The wave-1 script omitted the scene's 35° hole-dial
  offset. At the true opening pose the housing is ~112 mm off the axis toward
  −Y, the axis column is clear, and the barrel descends through the sector
  −10° to −75° at r ≈ 47–55 (see wave 2 below).
- **The lip is soft to a push** (~30 µm/N order estimate, `datum_budget.py`
  §2). Anything that rides the tube should pinch the lip or load the tube
  axially, not push it radially.
- **A floating gun must be force-quiet.** A hand on the trigger makes
  0.6–1.8 N·m (1.2–3.5 N·m with the corrected pose: grip base 234 mm out)
  about the tube axis; a lightly preloaded seat on the plate holds
  0.09–0.35 N·m and the loose tube in its nest lifts at 0.9–2.5 N·m
  (`datum_budget.py` §4–5). This single number set is what splits idea A from
  idea B.
- The X1 Pro's interlock needs a closed circuit gun-to-work [Manual 3.6.2,
  unconducted alarm p.32]; the rotator's copper shoe already provides the work
  side. Contact datums on the plate don't interfere with it.

### Ideas

- `ideas/endcap-compass.md` — **A.** The gun frame sits on the plate being
  welded: two 316 hex nipples in the ports carry a seat bar that turns with
  the plate; a centre pin/live centre at the port-pair midpoint gives x, y;
  three stainless ball transfers on the plate face give height and tilt; a
  fork to the rotator base holds azimuth loosely; a balancer carries the
  weight. Removes tube length, runout, reseating and inversion from the pose;
  drops per-tube indicating; the pose becomes a transferable part. Broken on:
  force-quietness (trigger, cables), radial precision no better than an
  indicated axis, plate hold before tacking. Includes the **calibration
  puck** (a replica joint the frame parks on — dry runs off the rotator) and
  the **pose block** (a printed part generated from the scene's pose
  transform). Developed furthest.
- `ideas/between-centres.md` — **B.** Rotator and a gun mast on one
  sub-plate; a tailstock live centre drops onto the same port seat and forces
  the plate centre onto a fixed line while holding the loose tube down; the
  gun stays rigid, its height set from the quill reading (B1) or riding the
  plate face on a two-ball rocker (B2). B0 (mast only, dial-plunger height
  set) kept as the simplest step. Same datum as A, opposite choice of which
  body is compliant; tolerates a hand on the trigger.
- `ideas/lip-collar-track.md` — **C.** Riding the tube at the weld. C0:
  rim roller plus a lip pinch pair 25° ahead (original, kept). C1: a collar
  clamped below the plate by a stock 5 in exhaust band clamp, turning with the
  tube, giving the carriage a clean track at the weld azimuth. The
  port-independent member of the family; heat at the collar undecided.

Sketches: `sketches/endcap-compass.svg`, `sketches/between-centres.svg`,
`sketches/lip-collar-track.svg` (generated by `sketches/make_sketches.py` from
the repo dimensions and the scene proxy). Numbers: `pose_geometry.py`,
`datum_budget.py`.

### Considered and set aside for now

- **Gun fixed, whole rotator floating against a gun-mounted roller.** The
  nest is deliberately loose, so pushing the tube moves the tube in its nest,
  not the rotator; the useful part of this became B (force the plate centre,
  not the rotator).
- **Rollers on the lip bore pushing outward**: lip compliance (above).
- **Orbiting the gun round a fixed tube**: one fiber twist per revolution;
  the manual forbids twisting.

### Open problems (wave 1)

1. Loop force of umbilical + wire conduit at the grip, in Derek's routing —
   decides whether A can work with a light seat.
2. How the plate stays at its recess before tacking — both A and B load the
   plate and must go on after tacks unless the spacer tool also holds it.
3. Port chamfer size and hand-tight nipple centring repeatability.
4. Actual tube length spread and end squareness.
5. Collar temperature for C1.
6. Radial precision of the plate-centre datum (~±0.19 mm RSS estimate)
   versus what the process needs (unknown window).

### Questions for Derek's observation

- Mass of the gun (and with its shell); where it balances.
- Force at the grip from the cables when the gun is moved ±5 mm in its usual
  place (a luggage scale on the grip would show it); trigger force.
- How the plate is held at depth before the first tack.
- Tube lengths and end squareness of the tubes cut so far; whether they are
  OnlineMetals cuts or halves of a 12 in length.
- Diameter of the 82° chamfer on the ports' outside face.
- Whether something may be threaded into the ports during welding (hollow
  316 nipples) — thread contamination, marking, anything else.
- Is there overhead structure above the bench for a balancer?

### Notes for later waves

- A and B share one component (the port-nipple seat). A camera on A's ring
  or B's C-arm sees the dot in plate coordinates; a motorized radial/height
  fine stage in either is where a learning loop would attach.
- The calibration puck is useful to any arrangement, not only A.

## Wave 2 (2026-09-28) — exchange with workspace-as-structure

### Correction

My `pose_geometry.py` passed the hole dial straight to `posePoint`; the scene
subtracts 35° first (`main.js`). Fixed in `pose_geometry.py`,
`datum_budget.py`, both idea files and the sketches. Consequences:
- nozzle 5.0 mm above the rim (not 8.8);
- housing ~112 mm off the axis toward −Y, so the axis column is clear at the
  opening pose; the barrel's descent sector (−10° to −75°) is the region to
  avoid;
- the compass ring becomes a C open over that sector, with the balls at
  50/170/280°, r = 40;
- trigger moment 1.2–3.5 N·m (grip base 234 mm out), and the gun's own
  weight makes ~1.3–1.7 N·m unless balanced at its centre of mass. The
  compass's force problem is worse than I said;
- between centres: the tailstock can come straight down the axis for hole
  dials up to ~30–40°.

### What I worked on (`exchange/work-as-datum--on--workspace-as-structure.md`)

- **Table-opening gantry.**
  - Difficulty: its side-load payoff repeats the nest height, not the corner
    (tube length ±3.2 mm, runout, face tilt).
  - Repair W1: a spring-plunger centre hung from the collar's free +Y edge,
    ball in a countersink on the port seat. Crank the shelf to "dial zero":
    tube length and radial runout are absorbed, the tube is clamped, and
    side loading still clears by 21 mm.
  - Branch W1b: a sprung shelf against a rigid centre.
- **Lidded mouth.**
  - Difficulty: a collar-hung lid must clear the worst tube, and its nose
    ring is room-referenced while the corner moves.
  - Repair L1: the lid rides the plate (my compass seat) 3 mm above the rim
    regardless of tube, parks on the collar when the shelf drops, and
    carries the camera, gas port and nose ring.
  - L1a: nose on the work, tail on the workspace. Work motion reaches the
    dot as ~0.12×.
- Short notes: countertop sled (its plane could live on the lid, but that
  brings back the moment problem), fixed-gun-moving-shelf (their active X
  correction for the residual after W1), drop-in collar (it is the structure
  my between-centres idea lacked).

### How Derek's examples strike me through this view

- **Suspension (rings, wires, bungees).** The natural partner for work
  as datum. His "one hook around the tip of the gun" is L1a's nose ring. If
  that loop hangs from the work (a lid or seat riding the plate) instead of
  from a wire, the loop sets position where it matters. The "second hook
  around the base", on a wire and bungees, can stay soft, because the lever
  from nose to dot attenuates it about eightfold. Suspension then doesn't
  need to be precise anywhere except at one loop, and that loop's reference
  is the joint itself. **This is the one I'll develop seriously in wave 3:**
  what each loop carries and constrains, the contact at the tip loop (split
  ring on the nozzle cone vs a shell boss), the bungee axis, setup vs weld vs
  lift-off, and the stuck wire.
- **Monitor arm.** A good carrier with no reference; its compliance lets the
  work pull the gun into registration. Arm carries, plate seat or nose ring
  locates. It is the soft-carrier-plus-seat family, but with the seat on the
  work rather than on the rotator base.
- **Table opening with the rotator beneath.** It shrinks the XYZ problem as
  he says, except tube length, which it cannot shrink unless the work sets
  the height (W1). The rim-height structure is where small work-referenced
  elements can live.
- **Automated setup (XY, Z, two rolls, PTZ cameras, AI iterating across
  tubes).** Across tubes, what changes is the work. Motors in a
  work-referenced frame (or on a collar the work is forced to) make learned
  setpoints transfer between tubes. The calibration puck lets the AI iterate
  for hours without a tube in the rotator.

### Open after wave 2

- Nose-ring contact on the copper nozzle: heat, interlock path, split-ring
  design.
- Whether W1's ball-in-cone centring holds under the ground shoe's side
  load and the wire's drag. The shoe pushes the tube OD with 0.75–1.5 mm of
  leaf preload [Repo]; that force was not quantified here.
- Face tilt remains in W1; one plate-face indicator reading per tube.

## Wave 3 (2026-09-28) — objections worked, and Derek's suspension through this view

### Objections from workspace-as-structure (`exchange/workspace-as-structure--on--work-as-datum.md`)

- **Pose correction:** they found it independently. Already fixed in wave 2.
- **Compass ring vs nozzle:** accepted. They also found the one I missed: the
  nipples' hex sweeps r 11–27, so 1 in ball transfers at r 40 get struck.
  The plate contacts become 695 stainless wheels.
- **Support triangle too small for the grip's lever:** accepted; this was the
  decisive objection. Two branches added to `endcap-compass.md`:
  - **A3, their paddle compass**, adopted. What I add: P3's height *is* the
    hole-axis dial (0.23°/mm, dot fixed to first order), and the vertical
    axis is a Y slide on the paddle.
  - **A4**: the hub carries only the nose, and the room carries the rest.
    That is the suspension below.
- **Follower 25° ahead** leaves 43% of runout and 85% of ovality: accepted.
  Their cold-map-then-replay branch goes into `lip-collar-track.md` as C2.
  After a plate-centre datum the map only has ±0.1–0.2 mm left to replay.
- **Tailstock straight down the axis** to hole dial ~40: accepted, as B3 in
  their table station.
  - Disagreement on unloading order: a spring quill needn't be lifted before
    the shelf drops (the ball parts; 51 mm to spare).

### Derek's suspension, work-referenced (`ideas/work-hung-suspension.md`)

- **One move:** the tip loop's anchor goes from the ceiling to the endcap. His
  arrangement as stated is kept whole as the *park* state (tip wire becomes
  the park/lift line).
- **D0 (literal: wire and bungees on a work gallows):** the float's rest
  position follows the work, but it is no stiffer.
- **D1:** the contact changes to a knife-edge V-loop on a grooved shell
  collar, which makes a gravity-seated ball joint at the nose (46 mm from the
  dot).
  - It hangs from a plate hanger: port seat, centre pin in a GE8, three
    stainless wheels, a 25 N clamp spring, and an azimuth tether.
  - The plate sees ~0.4–0.5 N·m instead of the compass's 1.2–3.5.
  - Base loop and third ring stay on the room.
- **Key numbers:**
  - Base motion reaches the dot at 0.09–0.17×.
  - With his bungees alone at the base, 1 N at the base moves the dot
    0.9–1.7 mm, so the base's X needs a line with the bungee as preload
    (0.001–0.013 mm/N).
  - Tube length becomes a per-tube base-ratchet mark.
- **Biggest open problem:** the gun's mass and centre of mass set the nose
  share. That share is at once the V's seating force (its sideways capacity
  against wire drag) and the load on the loose tube. The third ring trades
  one against the other, with a floor of ~5 N on the nose.
- **Interlock:** the loop is at work potential, so it must touch only the
  printed collar; metal-to-metal would close the conduction interlock
  permanently.
- **Automation fit:** dot knobs on the work (a stage in the stalk), angle
  knobs in the room (winches on three lines).

### Combinations across explorers

- **carry-and-locate's A-r3** (wire + bungee preload) is exactly what the base
  loop needs. Their D3-style concurrent wires are the limit case (branch D3).
- **workspace-as-structure's paddle** and my plate hanger are one component
  at two sizes: the paddle carries the gun, the hanger carries the nose.
- **one-knob-one-parameter's wire-per-angle** (as the coordinator described
  it; I haven't read it yet) and my "angle knobs in the room" should meet. The room lines are the angle knobs, and the dot stays on the
  work.

## Wave 4 (2026-09-28) — exchange with carry-and-locate; the hand stays the actuator

### On their switch-locked skate (`exchange/work-as-datum--on--carry-and-locate-w4.md`)

- **Difficulty.** The skate sits at the nose (61 mm / 53 mm from the dot)
  on a room plate, so it is the dot's reference.
  - Everything between the room and the corner reaches the dot, amplified:
    debris ×~2.2, switch twist 1.06 mm per degree, tube length at full scale
    until the height screw is reset, runout straight through.
  - The stops remember a room pose, while the variation is in the work.
    Their "second person without knowing anything" fails at the per-tube
    height step.
- **Repair R-A: skate the tail, let the work hold the dot.**
  - A dot-centred cup on the plate hanger at the nose.
  - Their MagJig shoe at the grip base, with the tail ball in a round
    vertical bore.
  - Debris becomes ~0.01° about the dot, switch twist nothing (the bore is
    round), lock shift 0.0006°, tube length an angle of 0.66° at full
    tolerance. The height screw is gone.
- **Lighter branches:** R-B (their skate plate carried by the hanger), R-C
  (a plate-face dial for the height step).
- **What theirs gives mine:** a lock state (my contacts had none), memory in
  stops, and the named principle "float through the switch".

### Guided hand (`ideas/guided-hand.md`)

- **The template idea:** the hand supplies preload, one freedom (roll about
  the grip axis), trigger and presence. A work-referenced **cup centred on the
  dot** supplies position. A tail bore supplies two angles.
  - The cup: three shell balls on a sphere R 50 centred on the dot, pads on
    the plate hanger.
  - 1° of hand roll turns the beam 0.42° and does not move the dot.
- **Honest limits.** A hand can't hold position for 50 s, can hold a push
  and one angle, and shouldn't carry the weight or the roll torque (balancer).
- **Biggest open problem:** the hand is the preload, and its push can also
  tip the loose tube. A push straight down the barrel gives 1.24 N·m at
  10 N and 1.85 N·m at 15 N against 1.6–2.4 N·m restoring. So the push must
  be light, and "light but never zero" is the skill left. The seat light and
  the balancer's residual weight bound it. How hard people actually push is
  unmeasured.
- **Records:** IMU roll trace, seat events (floating circuit, never on the
  interlock), pedal and trigger times, camera.
- **Test order:** C-h (sequence-of-use), then H0, then H1.

### Connections

- The dot-centred cup is carry-and-locate's virtual ball joint (B) made as one
  part, and their E-dome shrunk and moved onto the work.
- It could replace the nose V-loop in my work-hung suspension D1. Base errors
  would then vanish at the dot to first order instead of passing 0.09–0.17×.
  To try next wave.
- Guided hand H2 and repair R-A are the same machine at two ends: the hand
  keeps roll, the skate keeps the angles, the work keeps the dot.

## Wave 5 (2026-09-28) — final pass

- **carry-and-locate's critique of D1** (`exchange/carry-and-locate--on--work-as-datum-w4.md`):
  - Accepted in full:
    - with the third ring present the nose carries ~4.1 N, not 7–10 N (my
      split predated the ring);
    - the 90° groove is at its axial limit under gravity, so a stuck wire or
      a hand unseats it;
    - the room lines leak 0.165× into the dot and belong on the rotator
      frame;
    - the order is angles, then dot.
  - Their D1-p (sprung jaw, bungee-paired lines, float) is recorded as a
    branch.
- **D4, mine:** the nose loop is replaced by the dot-centred cup with sprung
  outer pads.
  - Room lines no longer reach the dot to first order, angles and dot become
    independent knobs, and a stuck wire passes through the cup centre.
  - Cost: 0.15–0.5 N·m of friction against angle moves (rolling variant D4-r
    noted), plus clutter and heat.
  - Sketch: `sketches/work-hung-suspension-D4.svg` (from `make_d4_sketch.py`).
  - It combines directly with their nose-and-tail F: their tail table, my
    cup.
- **Guided hand H1-p:** the same outer pads free the hand from being the
  preload. It keeps roll and the trigger, and the tube-tipping risk from the
  push goes away.
- **Readability:** a "Picture it", sketch list and open problems now sit at
  the top of all five idea files.
- **Summary file.** The harness refused `summary.md` as a report file ("return
  findings as text"). Its content went to the coordinator in the final reply
  instead.
