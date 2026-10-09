# C — Float and dock: carried from above, located by a seat

**Picture it.**
- **Carry.** A spring balancer above the gun carries its weight. A saddle
  carries the umbilical and wire conduit before they reach the grip.
- **Seat.** A metal tongue on the shell leaves near the barrel just above the
  rim and reaches over the rim on the +X side. Its three balls drop into three
  V-grooves (pairs of hardened rods) on a seat beside the tube, and a
  switchable magnet pulls them home.
- **Stack.** The seat stands on an adjustment stack on a post from the rotator
  frame ("fixed"). The stack holds the pose; the seat makes lift-off and return
  repeatable.
- **Trigger.** Pressed by a presser inside the shell.

**Sketch:** `../sketches/C-float-and-dock.svg` (true opening pose).

**Major unresolved problems:**
- Which stack gives Derek's three rotations about the dot without re-trimming
  the dot.
- The tongue's stiffness.
- The umbilical's residual pull on the seat.
- The seat is room-referenced near the nose, so tube length, runout and
  reseating reach the dot at full scale. This is the same critique
  work-as-datum made of E; E-RA in `switch-lock-skate.md` shows the reference
  moved to the work.

Sketch: `../sketches/C-float-and-dock.svg`. Numbers: `../calc/dock_and_rim.py`.

## The physical idea

Two different structures touch the gun's shell, and they never trade jobs:

- **Carriers** (soft, nearly constant force): a spring balancer hung above the
  gun's centre of mass takes almost all of the gun's weight; a large saddle
  (R ≥ 350 mm) takes the umbilical and the wire conduit *before* they reach the
  gun, so only a short, slack run reaches the grip butt.
- **Locator** (stiff, only where it touches): three balls on a stiff tongue of
  the shell drop into three V-seats (Maxwell three-groove coupling). A
  switchable magnet under the seats pulls a steel plate on the tongue down into
  them. The seats sit on an adjustment stack on a post that stands on the same
  frame as the rotator.

The balancer and saddle handle everything heavy and slow; the seat handles
everything that matters to the dot; the adjustment stack under the seat holds
the settings and only ever sees the magnet's preload and the disturbances.

## Geometry around the actual gun (opening pose)

- The tongue leaves the shell at the graduated-tube region (~70 mm up the
  barrel from the nozzle, just above the rim) and reaches out over the rim on
  the +X side to a seat plane ~50–80 mm above the rim and ~55 mm outside the
  tube wall. The seat is therefore close to the dot (~60–100 mm) — short levers
  from the seat to the dot and the wire tip.
- The post comes up outside the tube on the +X side, beside the rotator base
  (or from the base itself, which puts the whole position loop inside the
  rotator's frame: seat → stack → post → base → race → turntable → nest →
  tube → cap → dot).
- The balancer hangs above the housing (at this pose the CoM is beside the
  tube toward −Y, ~130 mm off the tube axis and ~370 mm above the bench), from
  a ceiling hook or a pegboard boom. Where it hangs does not matter to
  position.
- The umbilical saddle hangs above and behind the grip butt.

## How it is used

1. **Setup (once per recipe).** Dock the gun (magnet on). With the reference
   beam, turn the tube slowly on the pedal and set the dot, then the angles,
   on the adjustment stack. Lock the stack. The pose now lives in the stack.
2. **Per tube.** Magnet off → the balancer lifts the gun a few cm → change the
   tube → lower the gun into the seats → magnet on. One slow dry revolution
   with the reference beam confirms the dot against the new tube's runout.
3. **Weld.** Wire placed; pedal; trigger pressed by a shell-mounted presser
   (below). Nothing but the seat touches the gun's position.
4. **Stuck wire.** Snip while docked. If the rotator drags hard before the
   pedal is released, the seat is the fuse: it pops out rather than the wire
   guide or the stack yielding; re-dock and re-check the dot.
5. **Second closure** (inverted, float rod inside, purge from below): the
   dock does not see the difference.
6. **Second person.** "Magnet off, lift, change, lower, magnet on" — the
   recipe is in hardware.

## Loads, position, freedoms

| Load | Where it goes |
|---|---|
| Gun weight (mass unknown, 0.6–1.5 kg assumed) | balancer at CoM; set so the residual is small and known |
| Umbilical + wire conduit weight and spring-back | saddle, then a short slack run; residual into the seat |
| Magnet preload (chosen, ~40–100 N) | through the balls into the seats and the stack — internal to the dock |
| Wire push, wobble reaction, trigger (if pressed by hand) | through the seat into the stack |
| Stuck-wire drag | seat, up to breakaway |

Seat freedoms: none while preloaded. Every DOF of the gun is set by the three
ball-groove contacts; the stack sets where the seats are.

**Tip-off (breakaway) threshold** F = F_p·r/(2h) for preload F_p, seat radius
r, disturbing force at lever h from the seat:

- 40 N preload, r = 50 mm: ~17 N at the wire tip ~60 mm away, but only ~5 N at
  the trigger ~200 mm away.
- 80 N, r = 80 mm: ~53 N at the wire tip, ~16 N at the trigger.
- A hand on the trigger (3–8 N assumed) needs F_p·r ≳ 3200 N·mm. A
  shell-mounted presser (servo on the shell, or a Bowden cable whose housing
  ends on the shell) puts **no net force** on the seat, because the pressing
  force and its reaction are both inside the shell.
- The umbilical's residual matters: 2 N at 250 mm is 0.5 N·m against the
  seat's 1 N·m restoring moment at 40 N / 50 mm. Carrying the cable before it
  reaches the gun is not optional here. **[Calc]**

## Breaking it

- **Seat surfaces.** Balls against printed grooves creep and wear; soft
  stainless dowels dent. Hardened 8 mm chrome rods in pairs make each groove;
  balls are bonded into a metal insert on the tongue.
- **Tongue stiffness.** An 80 mm printed PET-GF tongue, 10 × 20 mm, is
  roughly 200–250 N/mm in bending (E ~6 GPa assumed) — the weakest link
  between the seat and the gun. A deeper section, a metal core, or the seat
  placed closer to the barrel.
- **Shell-to-gun fit.** The seat locates the shell; the gun must not move in
  the shell. The scan-fitted shell has to clamp the gun along its length.
- **Magnet near a welding cell.** Attracts ferrous spatter and filings into
  kinematic contacts, which hate debris. Cover the seat, wipe before docking,
  put the magnet between the balls rather than at the edge.
- **Balancer force.** Spring balancers are not perfectly constant and have
  hysteresis. If the residual weight is part of the seat preload, it varies.
  Setting the balancer to carry the full weight makes the magnet the only
  preload, independent of pose.
- **Heat and spatter at the seat.** 50–80 mm above the rim, outside the tube:
  radiant heat and spatter from the puddle. A shield plate on the tongue.
- **Reach of the stack.** The dock must allow Derek's rotations about the dot.
  If the stack's rotations are not centred on the dot, every angle change
  moves the dot and needs a dot re-trim; stacks with remote centres
  (goniometer pairs) or the "six-screw" option below avoid that.

## Variants

- **C-v1 Six-screw seat.** Each of the three grooves sits on a small two-axis
  carriage (up/down and sideways); six screws set all six DOF of the gun,
  hexapod-like, with no separate stack. The dock and the adjuster become one
  printed part.
- **C-v2 On the rotator.** The post is the ground tower or a new tower on the
  rotator base: the position loop never leaves the rotator.
- **C-v3 First joint of the future arm.** Motorise the stack (or the six
  screws). The gun can still be lifted off by hand and re-docked to the same
  motorised setting.
- **C-v4 Toggle-clamp preload.** A toggle clamp pushing the tongue into the
  seats through a spring instead of a magnet: no field, no filings, but a
  hand on the clamp near the gun.

## Parts (see `../../../sourcing/carry-and-locate.md`)

- QWORK 0.5–1.5 kg spring balancer (Prime, in stock, 2-pack $16.97).
- Magswitch MagJig 95 switchable magnet (Prime, $46, in stock) or pot magnets.
- 10 mm G10 chrome balls (Prime, $6.29/20) and 8 mm hardened chrome rods
  (Prime, $9.99/5).
- MG90S micro servo for a shell-mounted trigger presser (Prime, 900+/month).
- Printed: shell with tongue, ball insert and steel plate seat; groove blocks;
  umbilical saddle.

## Contribution and open problems

- The cleanest separation of carrying from locating in this study so far:
  nothing heavy touches the locator; nothing that locates carries weight.
- Lift-off and return are a switch and a lift; repeatability is the seat's.
- Open: what stack under the seat gives Derek's three rotations about the dot
  without re-trimming the dot; tongue and post stiffness; the real residual
  force of the umbilical; whether the trigger can be pressed by a small servo.
