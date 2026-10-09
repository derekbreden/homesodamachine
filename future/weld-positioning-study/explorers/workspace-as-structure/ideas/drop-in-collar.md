# Drop-in collar: one frame closes the gun-to-joint loop (a repair any table arrangement can use)

## Picture it

- **The collar:** one laser-cut plate (1/2 in MIC-6 aluminium, or 3/8 in
  steel), with the Ø160 tube opening and every rail, post and pad hole cut in
  one datum. It rests on three pads in an oversized hole in the bench top, and
  two stops locate it sideways.
- **Above it:** whatever holds the gun — gantry rails, a sled's reference
  plane, a fixed bridge, the collar-centre arm (T-W1), the lid's park lugs, or
  the paddle's room foot.
- **Below it:** four 1 in aluminium tube posts hang from the plate and carry
  the shelf and rotator.
- **The loop:** gun to tube, entirely inside the collar and its posts. The wood
  only holds the collar up.
- **A lean on the bench** tilts the whole collar, gun and tube together.
- **A steel collar** gives the indicator's magnetic base a seat beside the
  mouth. Point it at the plate face near the corner.

**Sketch:** `../sketches/drop-in-collar.svg`.

**Major unresolved problems:**

- Whether Derek will cut a bench top, or wants the collar on its own legs.
- The bench frame's layout under the opening.
- Face tilt remains a per-tube reading even with the collar centre.


Sketch: `../sketches/drop-in-collar.svg`.

## The idea

Treat the station like a kitchen sink: a stiff rim frame drops into a counter
opening and hangs from its own flange. The **collar** is one plate (or a welded
ring) that carries everything with a precision relationship — the gantry rails,
sled plate or fixed bridge above; the four posts and the rotator shelf below.
The bench top only supports the collar's weight on three pads. The structural
loop from gun to joint then runs entirely through the collar:

gun → shell → saddle/carriage → rails → **collar plate** → posts → shelf →
rotator → nest → tube.

What's different from the plain table opening: the reference for "fixed" is the
collar, not the wood. The bench becomes furniture.

## Why it is needed (the break it repairs)

In the plain opening, the loop passes through the 30 mm rubberwood top: a firm
lean near the opening gives ~0.1–0.5 mm of relative gun-to-tube motion
(`../loop_calcs.py` §2, agent estimate), and wood moves with humidity. With the
collar resting on three pads, a lean or bump tilts the collar as one body. Gun
and joint rotate together about a pad; their relative position doesn't change.
The bench's casters, height holes and wooden top drop out of the loop.

## One representative build

- **Plate:** 1/2 in MIC-6 cast aluminium tooling plate, laser-cut with the
  Ø160 opening, the rail-screw holes, post holes and three pad seats in one
  CAD file — SendCutSend lists MIC-6 at 0.250/0.375/0.500 in, ±0.005 in laser
  cut, 2–4 days production, up to 30 × 44 in at instant pricing (observed
  2026-09-28). MIC-6 is cast and stress-relieved, so it stays flat after
  cutting; one plate carries every hole in one datum, the way the rotator's
  one-piece base already does. A ~500 × 700 mm plate weighs ~12 kg. Mild steel
  (3/16–1/2 in HRP&O, same service) is the alternative: heavier, weldable by
  Derek's X1 Pro, and **magnetic** — an indicator base holds on it.
- **Posts:** four 1 in × 1 in × 1/8 in aluminium square tubes (Prime, 48 in
  lengths) bolted up into the plate; ~2,900 N/mm sideways at the shelf for a
  300 mm drop.
- **Rest:** three hard pads under the flange onto the wood (or onto the
  bench's steel frame rails if they line up) — three, so the collar never rocks
  on an uneven top.
- **Lateral location:** the opening in the wood is cut 20–30 mm oversize; the
  collar is located by the three pads plus two stops screwed to the wood, so
  it can be lifted out whole.

## What it adds beyond stiffness

- **A metrology datum next to the mouth.** With a steel collar (or a steel
  insert in an aluminium one), the test-indicator's magnetic base sits beside
  the tube and can read the **bore lip just above the cap** — the actual weld
  surface — through a dry revolution. That measures runout in the gun's own
  frame, rather than relative to the rotator's motor.
- **A laser boundary.** The joint sits 6 mm below the collar surface; a skirt
  or lid on the collar (`lidded-mouth.md`) closes the rest of the mouth.
- **Portability.** The collar with its posts, shelf, rotator and gantry is one
  module. It can move to the other 72 in bench, or stand on four legs of its
  own as a dedicated station, without re-establishing any relationship inside
  it.

## Breaking it

- **Pads on wood:** the collar sits on wood, so the collar's *attitude* follows
  the wood (tilts of a few tenths of a milliradian under a lean). That tilts the
  tube axis and the gun together: harmless to the dot, but the tube is no longer
  exactly vertical. For a downhand fillet, 0.5 mrad is nothing.
- **Plate bending under its own loads:** the gun (~1–2 kg) sits beside the
  opening and the rotator (~8–10 kg with tube) hangs from four posts on either
  side. A 12.7 mm plate across a 400 mm span under ~100 N deflects in the
  hundredths of a millimetre, statically — present at setup and unchanged
  during a weld.
- **Heat:** aluminium at the edge of the opening, 6 mm above a fillet weld,
  ~30 mm from the tube: fine; spatter pits it; a steel liner ring at the
  opening is cheap.
- **Thermal drift of the loop:** aluminium grows 23 µm/m/K; a 400 mm loop
  warming 5 K grows 0.05 mm, slowly, over an hour. The dot check at the start of
  each tube covers it.

## Where it applies

- `table-opening-gantry.md`: rails on the collar instead of the wood.
- `countertop-sled.md`: the collar plate *is* the sled's reference plane.
- `fixed-gun-moving-shelf.md`: the fixed bridge bolts to the collar.
- The edge variant: the collar has a notch instead of a hole and overhangs the
  bench edge; its cantilever becomes the part to check.

## Unresolved

- Whether Derek wants a hole cut in a VEVOR top at all, or prefers the collar on
  its own legs beside the bench (same loop, no cutting).
- Actual rubberwood top and frame layout under the opening [Derek to look].

---

## Wave 3 note (from work-as-datum's exchange)

The collar is where three work-referenced elements attach, all from its free
+Y edge or its surface:

- **The collar centre (T-W1):** an arm with a spring plunger dropping into a
  countersink on the plate's port seat.
- **The lid's park lugs (L1):** the lid rides the plate and parks on the
  collar when the shelf drops.
- **The paddle compass's room foot and fence.**

**Where to point the magnetic-base indicator.** Aim it at the plate face
~10–15 mm inboard of the corner, not the bore lip. Face tilt is the one error
the collar centre doesn't remove, so this reading is the one to keep per tube.
