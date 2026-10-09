# A0 — A gas-spring monitor arm holds the shell (Derek's example, as proposed)

## Picture it

**The arrangement.** A gas-spring desk monitor arm is clamped to the bench's
back edge behind the rotator, on the −Y side, where the gun leans back and the
umbilical leaves. Its VESA plate bolts through a printed adapter to the
scan-fitted shell around the X1 Pro. Ballast brings the load into the arm's
2–9 kg window.

**What moves.** The rotator turns the tube underneath. Gun, wire guide and
umbilical stay wherever the arm's joints stopped.

**Carrying and locating.** The arm carries everything and nothing locates:
position is held by friction in about five joints — vertical-axis swivels, a
gas-spring lift with near-zero rate, and a friction head. "Fixed" is the bench
top at the clamp. Derek's hand aims the dot.

This is **Derek's example exactly as proposed**. Its strong roles — weight
relief while aiming by hand, and parking — feed A1, A2, E and
sequence-of-use's monitor-arm session.

**Sketch:** `../sketches/a0-arm-holds-the-gun.svg` (true opening pose).

**Major unresolved problems.**
- It cannot hold the dot through a 48.6 s lap against changing umbilical or
  conduit forces, because nothing restores it.
- The real joint play and friction band are unmeasured.
- The gun's mass, which sets the ballast, is unmeasured.

Sketch: `../sketches/a0-arm-holds-the-gun.svg`. Branches that change it:
`a1-arm-carries-tube-locates.md`, `a2-arm-into-kinematic-dock.md`.

## The arrangement

A bench-edge clamp behind the rotator (on the −Y side, where the grip and
umbilical go at the scene's opening pose) carries a single gas-spring monitor
arm of the ordinary kind: a post, a swivel (J1), a spring-lifted parallelogram
upper arm with an elbow swivel (J2/J3), and a head with swivel, tilt and
rotate (J4). The VESA 75/100 plate bolts to a printed adapter on the
scan-fitted shell. Derek swings the gun in, puts the aiming dot on the corner,
lets go, presses the pedal and the trigger.

- **What it carries:** everything — gun, shell, the first span of umbilical and
  conduit.
- **What it locates:** nothing by construction. Position is wherever the joints
  stopped.
- **Where "fixed" is:** the bench top at the clamp, through four or five
  friction joints.
- **What drives it:** Derek's hand.

## Its real capability (representative part: HUANUO FlowLift, 2.0–9.0 kg)

- A gas-spring arm is built to push up with almost the same force across its
  whole height range. Its vertical *rate* is therefore close to zero: height is
  held by seal and joint friction, and any vertical force beyond that friction
  band moves it with nothing to bring it back. Reviewers of the representative
  arm describe exactly this: a light monitor makes the arm creep up, and one
  owner says it always drifts to the top.
- Gun + shell (estimated 1.2–2.5 kg; the gun's mass is not published) sits at or
  below the arm's 2.0 kg minimum. Ballast on the adapter (≈0.5–1 kg of steel)
  brings it into range; the spring's tension screw then trims.
- Every swivel axis is vertical. Horizontal forces — umbilical weight and
  stiffness, the wire conduit's spring, a hand — are resisted only by swivel
  friction, which is set low enough to move a monitor with a fingertip. Lock
  screws add friction; they do not add a positive stop.

## Breaking it

| Phase | What moves, and why |
|---|---|
| Setup | Easy and fast: the gun floats, the hand puts the dot on the corner. The arm "remembers" nothing, so the next setup starts from scratch. |
| Dry run | The table turns under a still gun: fine, provided nothing pushes on the gun. The tube's own runout (≤0.25 radial / ≤0.30 face TIR accepted) is not followed. |
| Weld | The wobble motor vibrates the head; dither lowers effective breakaway friction, so a constant side load (umbilical) can walk a friction joint slowly (plausible, unmeasured). Any change in umbilical or conduit force shifts the gun with no restoring stiffness. |
| Lift-off | Excellent — the gun floats up. |
| Stuck wire | The tube drags the wire; the arm yields instead of the wire guide bending. The gun is pulled off its setting. |
| Inverted second closure | No difference from the gun's side. |
| Second person | Nothing records the pose. |

Conclusion for the original as a locator: it floats in all six directions, so it
cannot by itself hold the dot for a 48.6 s lap against varying forces. That is a
statement about one role, not the family.

## The roles where it is strong

1. **Weight relief while Derek still aims by hand.** This is the industrial
   "zero-gravity tool arm" role (arms that carry grinders so the operator guides
   with fingertips). The skill stays in Derek's hand, but tremor and fatigue from
   holding ~1–1.5 kg at arm's length for 50 s go away. Smallest possible step,
   next-day parts.
2. **Parking.** Swing the gun away for a tube change and back again; the arm
   does this better than anything bolted.
3. **Carrier for something else that locates** — developed in A1 (the tube
   locates) and A2 (a bench dock locates).

## Repairs that stay close to the original

- **Pole-mount "SCARA" arm.** A pole-mounted monitor arm clamps a collar at a
  fixed height on a vertical pole, and its two links swivel about vertical axes.
  That is a manual SCARA: stiff in Z (collar and link bending), compliant in X/Y.
  Z becomes a locked, repeatable setting; X/Y still need a stop or a locator.
  Pairs naturally with an OD-only rider (A1-S).
- **Clamp collars on each swivel.** Printed split collars with thumb screws
  convert friction joints into clamped joints. What remains is joint play
  (bushing clearance, unmeasured) multiplied by link lengths of 250–400 mm.
  Worth one indicator test on a real arm before building anything around it.
- **Derek's third ring / third support.** Letting the shell touch something
  fixed near the nozzle turns the arm into a carrier and the touch point into
  the locator — which is A1/A2.

## Open questions

- Gun mass and CG (kitchen scale, string); shell mass.
- Joint play of a real arm with swivels clamped: indicator at the VESA plate,
  ±5 N push.
- How much Derek's hand-held consistency improves just from weight relief
  (cheap experiment: bead-to-bead variation with and without the arm).
