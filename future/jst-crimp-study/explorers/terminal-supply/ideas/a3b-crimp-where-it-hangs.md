# a3b — Crimp it where it hangs: the rail's end pocket turns the contact to face a sideways punch

Branch of [`a3-hanging-rail.md`](a3-hanging-rail.md). **What it changes:** no
transfer. The contact that reaches the end of the rail is crimped vertically,
still hanging. The conductor comes down from above into the open U, and the
punch moves sideways.

Sketch: [`../sketches/a3b-hanging-crimp.svg`](../sketches/a3b-hanging-crimp.svg)
(schematic, looking along the rail after the pocket's turn).
Numbers: [`../calc/wave2.py`](../calc/wave2.py) §10 [w2 §10].

**Related.** [a5](a5-housing-as-fixture.md)'s gravity variant (a housing rear
face up, the contact standing in its mouth) crimps with this same turned punch,
fixed wall and finger.

## Picture it

- **Where things start.** The rail's last position is a turning pocket: a short
  hardened steel cylinder on a servo, with a slot through it that continues the
  rail's slot. A contact hangs in it box-down, its insulation barrel resting on
  the slot's edges. Hanging in the rail, its U opens fore or aft along the rail,
  because the wings bear on the slot's two edges.
- **The turn.** The camera, looking down the U with a light below, sees which way
  the U opens. The pocket turns 90° or 270° so the U faces across the rail,
  toward the punch. The insulation barrel's height (2.75–3.2 mm from floor to
  wing tips) is more than the 2.4 mm slot, so the contact still hangs after the
  turn: by its floor on one edge and its wing tips on the other. One servo turn
  replaces a3's separate 180° pocket.
- **The fixed wall.** Beside the rail's line, across from the punch, a fixed
  hardened steel wall stands behind the contact's floor. The turning pocket is
  cut away on that side, so the floor meets the wall directly. The punch's first
  touch pushes the contact 0.1–0.2 mm across onto the wall. The rotating pocket
  only locates; the crimp force goes from the floor into the fixed wall, which
  does not stand across the path the contact arrived along.
- **The ribbon hangs above,** clamped with its splayed, stripped conductors
  pointing down. The loom, 100–600 mm long [repo], stands up from the clamp or
  drapes over a guide. Every conductor except k is folded back up along the
  ribbon and clipped there, out of the punch's path and away from the rail's
  waiting contacts.
- **What moves.** The carriage lowers conductor k straight down. The open
  insulation U (2.46–3.0 mm) is its funnel, and the 0.72 mm strands enter the
  conductor U. Because the U now faces sideways and has no wall on the punch
  side, a thin finger swings in from the punch side and presses the insulation
  toward the floor, into the insulation barrel; the strands follow as one stiff
  bundle. The carriage stops at a height referenced to the pocket's top edge,
  the same edge the contact hangs from, and the camera then steers it by the
  insulation edge as seen.
- **The look before the stroke.** From above and in front, on the punch side:
  no strand outside the wing tips, insulation edge in the window. The pocket's
  side walls stop below the conductor barrel, or have a window, so a lateral
  silhouette across the barrels is not blocked.
- **The crimp.** The horizontal punch moves toward the wall and closes the wings
  against the floor, onto a hard stop between the punch holder and the wall's
  block.
- **Leaving.** The finger and punch retract and the carriage lifts the conductor.
  The crimped contact slides up out of the open-topped pocket with it. The pocket
  turns back and the escapement drops the next contact in.
- **What the person does.** Refills the hopper; splays and strips; folds and
  clips the other conductors unless the carriage does; hangs the loom above the
  machine.

## What locates what

| What | Reference | Note |
|---|---|---|
| Contact, along its own axis (vertical) | the insulation barrel's lower edge on the pocket's top | 0.4 mm from the conductor barrel |
| Contact, facing | the pocket's turn (90° or 270°), chosen from the silhouette | — |
| Contact, across (the crimp direction) | the fixed wall behind the floor | the punch's first touch seats it there |
| Conductor depth | carriage height from the pocket's top edge, then the insulation edge as seen | contact and wire referenced to one face |
| Conductor in the U | the finger pressing the insulation toward the floor | — |
| Crimp height | hard stop between punch holder and the wall's block | — |

**The reference for "fixed" is the steel block that carries the wall and the
hard stop.** The turning pocket, the finger and the camera mount to it.

## What drives and carries the crimp force

A horizontal punch driven by a NEMA 17 lead screw or toggle. The loop is punch →
contact → fixed wall → wall block → punch guide. It is a normal crimp turned
90°, 0.8–2.6 kN [xh-facts §4], with the hard stop and spring overtravel of
[a2](a2-strip-indexer.md). The frame must be stiff horizontally, and the stop
local, as in any press.

## How it knows it worked

- Before the crimp: contact present, U facing the punch, insulation edge in the
  window, no strand past the wing tips.
- The punch reaches its hard stop, with a force trace.
- After: did the contact leave with the conductor, or stay in the pocket? Then
  the after-crimp look.

## What changes by hanging

- **Gravity holds the contact in its pocket** until the punch arrives. Nothing has
  to clamp it.
- **Contact and conductor depth share one reference,** the pocket's top.
- **No release mechanism.** The crimp leaves upward with the conductor.
- **Gravity straightens the conductors only weakly,** and copper keeps whatever
  bend it was given [digest]. The carriage's fork guides each one, and the finger
  seats it.

## Problems and repairs

1. **A punch moving along the rail would put either the punch or its wall across
   the contact's arrival path.** Repair: the pocket turns the U to face across
   the rail, so punch and wall sit beside the rail's line. A variant keeps the
   along-rail punch with a steel shuttle anvil that closes behind the contact
   after it enters; its seating repeatability then enters crimp height directly,
   and the hard stop must reference the fixed abutment, not the shuttle.
2. **Nothing holds the conductor inside a sideways U,** so strands can hang past
   the wing tips on the punch side and be closed onto. Repair: the finger presses
   the insulation toward the floor before the punch moves, and the look from the
   punch side checks the strands.
3. **The ribbon's other conductors hang beside the pocket,** over the waiting
   contacts, in the punch's path, or behind the wall, depending on how the
   ribbon's plane is turned. Repair: fold them back up along the ribbon and clip
   them.
4. **Does the punch's first touch lift the contact?** The punch acts across the
   contact's axis, and the insulation barrel rests on the pocket edges. The
   wings' curl has a small axial component, which the pocket's top edges and the
   conductor's friction resist. Open.
5. **The pocket must pass the conductor barrel's full tolerance** (1.55–2.15
   open) yet hold the contact square for the punch. The punch's lead-in centres
   it laterally, as in any die, and the wall takes the floor.
6. **Vertical loom handling.** A 600 mm loom above the machine needs a stand.

## Steps covered, and what it hands back

- **Covers:** loose supply; orientation; placing the contact; holding; placing
  the conductor in it (finger, carriage steered by the picture); crimping;
  release.
- **Hands back:** splay and strip; folding and clipping the other conductors,
  unless the carriage does it; the vertical ribbon presentation; insertion.

## Printed and bought

- **Steel:** the turning pocket (a short hardened pin with a slot cut through it),
  the fixed wall and the punch: the OTP XH anvil profile becomes the wall and the
  crimper the punch, reoriented, in a small horizontal frame.
- **Drive:** a NEMA 17 lead screw (Iverntech Tr8×2, Prime, $27.99) or a toggle.
- **Printed:** the ribbon clamp above, the carriage, the conductor clips and the
  frame around the steel.
- **Servos:** the pocket's turn and the finger (MG90S, Prime, $13.88 4-pack).

## Contribution

A crimp station with no transfer and no clamp: supply, locate and crimp in one
pocket. The contact is referenced by the same edge the conductor's depth is set
from, and one turn of the pocket both orients the U and moves the punch and its
wall out of the contact's path.

## Major unresolved problems

- **A horizontal press frame** stiff enough for ~3 kN with a local hard stop.
- **The first touch:** whether a hanging contact stays square, and whether the
  floor meets the wall squarely.
- **Seeing strands across the barrels** past the pocket's side walls.
- **Handling long looms vertically,** with the other conductors folded and
  clipped.
- **Everything a3 leaves open** about which contacts have a head: genuine JST
  contacts inside their 1.95 mm envelope fall through a 2.4 mm slot [w2 §10].

## What each conclusion rests on

- **Facts [source]:** clone insulation-barrel height and wing widths (S19–S22).
- **Calculations [calc]:** genuine versus clone wings against the slot [w2 §10].
- **Estimates:** crimp force [xh-facts C1]; the 0.1–0.2 mm first-touch shift.
- **Assumptions:** kit contacts hang as the clone drawings suggest; the
  insulation barrel's height catches the slot after the turn; the
  punch-first-touch behaviour.
