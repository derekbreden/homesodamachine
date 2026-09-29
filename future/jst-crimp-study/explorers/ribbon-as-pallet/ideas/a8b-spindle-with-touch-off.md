# a8b Spindle with touch-off: one conductor at a time into a small turning head that finds its tip, scores a ring, twists the stub and keeps the slug

## Picture it

A branch of [a8](a8-rolling-ring-scorer.md). The blades turn around one
conductor instead of the row turning under fixed blades, and each conductor's
own tip is found electrically before its score is placed. Sketch:
[`../sketches/a8b-spindle-with-touch-off.svg`](../sketches/a8b-spindle-with-touch-off.svg)
(schematic).

**The head.**
- A hollow printed spindle runs in two 6700 bearings (10 × 15 × 4 mm), turned
  through a GT2 belt by an N20 gearmotor at about a turn a second.
- At the front, a **snout** no wider than 7.8 mm reaching at least 6 mm ahead of
  the bearing section [P3 §8]. The bore opens as a 4 mm funnel and narrows to a
  1.9 mm guide.
- Behind the guide, two razor-sliver tips face each other on printed flexure
  arms. A non-rotating collar, moved by a hobby servo, pushes a cone that closes
  both arms onto screw stops set for a score radius of 0.55–0.60 mm, gauged with
  a 1.1–1.2 mm pin laid in the bore.
- At the back of the bore, one strip length behind the blade plane, a steel
  **tip stop**: a rod through the hollow spindle, not rotating, isolated and
  wired. A phosphor-bronze brush connects both blades to a second input.

**One conductor.**
1. **Touch-off.** The stage lines conductor k up with the funnel (the fan block
   has it to ±0.1 mm; the funnel captures ±1 mm) and moves it in. The instant its
   copper face touches the stop, the far-end port ([a6](a6-housing-as-last-comb.md))
   reads conductor k continuous to the stop. The stage stops and records where.
2. **Score.** The spindle turns and the collar closes the blades. Closing
   together, they push the conductor to the axis from both sides, so the ring is
   concentric with the jacket. Three turns.
3. **Pull and twist.** The spindle stops with the blades closed; the stage draws
   back 1.2 mm and the slug tears at the score and slides halfway off. The
   spindle turns a quarter to half a turn, twisting the 60 strands to a lay of
   5–10 mm (outer strands at 13–25°) through the slug's grip, as the Schleuniger
   RotaryStrip does [prior-art §2]. The stage draws back the rest of the way.
4. **Clear.** The blades open, the tip stop pushes forward, the slug drops out.
5. **Look.** A backlit frame of the stub, as a8.

**Neighbours.** At 5 mm pitch the neighbours' jacket edges are 4.15 mm from
conductor k's axis, so without the snout their flush-cut tips would butt the
head's 15 mm face as k is fed in, and touch-off would read k against the stop and
a bent neighbour against the face [P3 §8]. At housing pitch (2.5 mm) a snout
would have to be under 2.8 mm; there conductor k is lifted ~9 mm into a
full-size head instead, and laid back (procedure-is-the-machine's lift-once,
[p1c](../../procedure-is-the-machine/ideas/p1c-lift-once-tip-down-module.md)).
At an 8 mm lift k is left 0.3–5.6 mm high over 20–25 mm free [procedure-is-the-machine
calc wave2 §1(b)], and a flat sole presses it level
([a1c](a1c-crimp-upstream-first-park-after.md)'s).

**What locates what, and the reference for fixed.** "Fixed" is the tip stop.
Axially, the conductor's own tip, found electrically, with the blade plane a
fixed distance from the stop; radially, the two closing blades; laterally, the
funnel and bore.

**Force.** No crimp force. Scoring torque is under 0.4 N·mm; tear-off is 2–8 N
at a 0.55–0.60 mm score radius [calc W2 §4], taken by the clamp at the split
root.

**How it knows.** Touch-off before; the blades' own circuit during (a nick
closes conductor k to the blades and stops the spindle); the backlit frame after.

**What the person does.** Nothing at a station on a stage. **By hand:** the same
head on a bench block, turned by a knob, the blades closed by a lever; the
person feeds one conductor in until an LED shows touch-off, turns three times,
pulls half, twists, pulls off.

## Steps it covers and what it hands back

Covers the strip of each conductor, touch-off of each tip (order C of
[a5](a5-part-fan-strip-in-the-pallet.md)), strand twist, nick detection and stub
inspection. Hands back nothing at a station on a stage.

## What it adds over a8

- **Each tip is found, not assumed:** a conductor that crept in the fan block is
  stripped correctly anyway, and its crimp Y can be set from the same record.
- **A deeper score:** two blades closing together centre the conductor to about
  ±0.02 mm, allowing 0.55–0.60 mm against a8's 0.58–0.63 mm [calc W2 §4].
- **A twisted stub:** a quarter turn through the slug gathers 60 untwisted
  0.08 mm strands without touching them.
- **A captive slug** that leaves by one route.

## What it costs against a8

- One conductor at a time, about 20–30 s each, 20–25 min for a unit's 53
  [estimate].
- A rotating head with a closing mechanism, a brush and a hollow stop, now inside
  a 7.8 mm snout.
- The conductor has to reach the head along its own axis, with the neighbours
  fanned wide, or lifted.

## Major unresolved problems

- **The closing mechanism at snout scale:** two flexure arms, a cone and a thrust
  ring inside 7.8 mm, set to ±0.02 mm. A machined brass cone may be the first
  version.
- **The brush** on a turning spindle as a clean nick signal.
- **Everything a8 leaves open:** the tear on this silicone, bundle eccentricity,
  strand twist.

## Related ideas

- Parent: [a8](a8-rolling-ring-scorer.md). Module: [a5](a5-part-fan-strip-in-the-pallet.md).
- Where it fits: [a4](a4-spool-as-magazine.md) and
  [a1c](a1c-crimp-upstream-first-park-after.md) at 5 mm with the snout; other
  explorers' single-conductor stations (borrowed-machines
  [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md),
  procedure-is-the-machine [p4](../../procedure-is-the-machine/ideas/p4-person-presents-machine-takes.md),
  [p1c](../../procedure-is-the-machine/ideas/p1c-lift-once-tip-down-module.md)).

## What rests on assumptions

- Touch-off contact force and reliability through tinned strand ends
  [assumption]; twin-blade centring to ±0.02 mm [estimate].

## Labels

As [a1](a1-pallet-tour.md#labels).
