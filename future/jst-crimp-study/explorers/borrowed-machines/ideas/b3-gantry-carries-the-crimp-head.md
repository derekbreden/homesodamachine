# b3 — A cheap printer gantry carries a narrow crimp head to a fanned ribbon

**The arrangement.** The other applicator arrangements bring the wire to a
fixed press. This one takes the crimp to the wire:
- the ribbon end lies still on a printer bed, fanned out like a circuit board
  on a pick-and-place machine;
- a small crimp head on the printer's carriage picks a contact from a strip
  feeder, carries it to each conductor and crimps it there;
- a converging comb then brings the crimped row to housing pitch, and the
  housing is pushed onto the whole row.

**What is borrowed:**
- an Ender-3-class bed-slinger as the gantry;
- the tooling from a second OTP applicator, for narrow dies;
- pick-and-place practice: a feeder at the frame side, vision for finding each
  tip (OpenPnP-style), the part carried to the board;
- an applicator's own feed-finger principle for the strip.

**Related:** hand-tool-as-press a3, force-and-form
[f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md) and this idea
reached "the force stays inside a travelling head" independently [digest].
into-the-housing's i3 supplies the gang push; procedure-is-the-machine's p2 and
p3 the per-conductor order and the still ribbon from the spool (below). b3's
V-fork on the head's rear face is carried into
[b8b](b8b-flat-spool-line-over-a-crown.md).

Sketch: [`../sketches/b3-gantry-head.svg`](../sketches/b3-gantry-head.svg).

Labels: [calc geometry §n], [calc presses §n], [calc wave3 §n] are this
explorer's [`geometry.out.txt`](../calc/geometry.out.txt),
[`presses.out.txt`](../calc/presses.out.txt) and [`wave3.out.txt`](../calc/wave3.out.txt);
[TS §n] is terminal-supply's
[`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt);
[procedure calc §n] is procedure-is-the-machine's
[`exchange_borrowed.out.txt`](../../procedure-is-the-machine/calc/exchange_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**The machine.** An Ender-3-class printer with its hot end removed (Ender 3 V3
SE, $186.14–219.00 [Prime]). The bed moves along the wire; the carriage moves
across the conductors; Z sets height.

**The ribbon end, prepared flat.** Before it ever reaches the fixture, the end
is flush-cut, split from a placed root to the strip line, and stripped while
it is still flat and one piece: [b6](b6-pierce-at-the-root-pull-to-the-tip.md)'s
rip and whole-tip slug, or [b4](b4-laser-slits-and-scores.md)'s scores, or
procedure-is-the-machine's [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md)
(the whole end stripped while webbed, then split). Every
conductor's tip and strip line then sit the same along-conductor distance from
the root.

**The fan fixture.** A printed fixture screwed to the bed:
- the webbed part of the ribbon clamped at the back;
- the split, stripped conductors lying in grooves that spread them from 1.7 mm
  to ~4–5 mm pitch, held by a clamp bar;
- each conductor's last ~8 mm (the bare strands and ~5 mm of insulation)
  sticking out past the fixture's front edge, level, like fingers over a cliff.
  The outer tips stand a little further back than the middle ones, because
  their path is diagonal; the camera finds each.

**Beside the bed.** A strip feeder presents the lead contact of an SXH strip at
the end of a flat steel track, box pointing toward the bed. A pawl pushes the
strip one pitch per pick and a tapered pin in a neighbouring pilot hole fixes
it there.

**On the carriage.**
- **The crimp head:**
  - a small steel C-frame with a fixed lower arm carrying an anvil;
  - a sliding punch holder carrying a conductor punch and an insulation punch,
    thin blades a few millimetres wide taken from a second OTP XH applicator;
  - a NEMA 17 with a planetary gearbox and a 3 mm crank inside the head,
    closing the punches;
  - a drop blade beside the anvil's rear edge, which is the fixed shear edge at
    the tab root;
  - **a neck blade**: a thin steel leaf on a small servo that drops into the gap
    between the conductor barrel and the box once the contact is captive, to
    hold it axially and stop the strands;
  - **a V-fork** on the head's rear face that closes on the conductor's
    insulation ~3 mm behind the strip line as the bed brings the conductor in.
- **The housing tool:** a printed nest holding an XHP-n housing, mating face
  away from the fixture, and the **converging comb**: slanted slots that slide
  forward from the root and close the crimped row from fan pitch to 2.5 mm.
- **The camera:** the ELP looks down.

**Cycle, per conductor.**
1. The camera maps every conductor tip in X, Y and height.
2. The head goes to the feeder with its punches open and its anvil slid under
   the lead contact.
3. It closes to the captive position, pinching the barrels. The drop blade
   pushes the carrier down past the anvil's rear edge and shears the tab at its
   root; the pinch across the barrels sits right beside the tab, so the shear
   has almost no lever through the contact. The neck blade drops in.
4. Carrying the captive contact, the head moves in front of conductor *i*, at
   the height where the conductor's axis meets the barrel centres.
5. The bed moves toward the head. The V-fork closes on the insulation and takes
   over from the camera map, so the 8 mm cantilever's wander of 0.2–1 mm under a
   light touch no longer matters
   [procedure-is-the-machine's exchange on borrowed-machines]. The conductor slides
   lengthwise into the contact's open barrels, led by the insulation barrel's
   2.5–3.0 mm mouth, until the strands touch the neck blade. The camera confirms
   the insulation edge sits in the window.
6. The head's motor turns its crank through bottom dead centre: the crimp.
7. The head opens fully, the neck blade lifts, the V-fork opens, and the bed
   draws the conductor back out, the box passing through the open punches.
8. Repeat for the next conductor.

**Insertion, once the row is crimped.**
1. The converging comb slides forward from the root and closes the row from fan
   pitch to 2.5 mm, the crimped contacts as its handles. From 4.35 mm pitch the
   outermost 4P contact moves 2.8 mm and the outermost 5P contact 3.7 mm [TS
   §2].
2. A spring guide comb squares the contacts' noses.
3. The housing nest drives onto the whole row at once through a load cell; the
   housing moves, not the conductors, so nothing buckles or drags sideways
   (into-the-housing i3's gang push).
4. Each contact is pulled back ~5 N in turn: force before distance means it is
   latched.

**What locates what; the reference for "fixed."** The printer frame, with the
camera calibrated to it.

| What | Set by | Reference |
|---|---|---|
| Strip at the feeder | tapered pin in a neighbouring pilot hole | feeder track, on the printer frame |
| Contact in the head | the head's own anvil and punches, as in an applicator; held axially by the neck blade | head |
| Conductor | fixture groove, then the V-fork on the head; the camera map is a coarse guide | head |
| Conductor depth | strands against the neck blade; every tip is the same along-conductor distance from the root | head |
| Bed and carriage | the printer's steppers: ~0.01 mm resolution, ~0.05 mm repeatability [estimate] | printer frame |
| Fronts at insertion | equal along-conductor distances from the root, so the outermost front lands short only by the housing fan's own amount | housing nest |

At b3's ~20 mm free length the outermost front lands short by 0.04 mm (4P),
0.06 (5P), 0.14 (J4) and 0.25 mm (J1), all inside the ~±0.3 mm a gang push
wants [calc wave3 §7; TS §2]. The fan pitch at the crimp drops out.

**What drives the crimp and carries its force.** The head's own motor and crank,
closing inside the C-frame.
- **Force.** A NEMA 17 with 10:1 gives ~3.8 kN at 0.1 mm above bottom; with
  50:1, ~17 kN [calc presses §5]. The Prime 26.85:1 NEMA 17 (StepperOnline,
  $41.91, 3 N·m permissible [Prime]) sits between them.
- **Gantry load.** The gantry carries only the head's weight, ~1 kg
  [estimate].
- **Frame.** The C-frame's stiffness sets the scatter: ±30 µm at 10 kN/mm, ±8 µm
  at 40 kN/mm [calc presses §5], so the C is laser-cut thick steel.

**How it knows it worked.**
- The camera before the crimp (depth) and after (brush, wings).
- A BF350 strain gauge ($6.99 [Prime]) on the C-frame gives an HX711 force
  curve through the slow crank, as in [b1b](b1b-applicator-in-slow-crank-press.md).
- At insertion: the load cell sees each lance fold and snap; the pull-back
  proves each latch.

**What the person does.**
- Lays each split, stripped end into the fan fixture and clamps it, 60–90 s.
- Drops a housing into the nest.
- Starts; unloads.
- Loads strip into the feeder.

## Steps it covers and what it hands back

- **Covers:** supply contacts (strip feeder, cut in the head), place the contact
  on the conductor (captive pinch, neck blade, V-fork, axial slide-in), crimp
  (head-internal crank), verify the crimp (pictures, C-frame force curve),
  insert (converging comb and gang push) and verify insertion (trace and
  pull-back).
- **Hands back:** laying ends into the fixture; splitting and stripping unless
  b6 or b4 feed it; housings; strip; unloading.

## Why the conductors fan wider here

The head's dies must fit between the target and its neighbours where their last
~6 mm overlap the die plates.
- **Fan pitch** must be at least half the die width plus half a conductor plus
  0.5 mm [calc geometry §2]:
  - 4.5 mm-wide dies need 3.6 mm;
  - 6 mm dies need 4.35 mm;
  - 10 mm dies need 6.35 mm.
- **5P fan.** At 4.35 mm pitch a 5P end is 17.4 mm wide, and its outer conductor
  moves 5.3 mm, 15° over a 20 mm split.
- **The SN-2549's jaws** are tens of millimetres across; no fan clears them. A
  second OTP applicator at $125–165 is the cheapest source of hardened,
  correctly profiled XH blades [Sanao, eBay pricing in b1]; neither it nor a
  bare knife set has a Prime listing [Prime].
- **The head cuts the contact free before it arrives**, which is why a fan works
  here at all. A fan over a strip still attached would put the second and third
  neighbours on the next contacts' open wings
[procedure-is-the-machine's exchange on borrowed-machines, §A].

## Alternatives inside b3

- **Per-conductor insertion by the same gantry.** After each crimp the housing
  nest visits the contact and the bed pushes it in. With the ribbon clamped at
  the back, each insertion drags the already-inserted conductors sideways by up
  to 6–10 mm on a 5P [calc geometry §2]; the fixture's clamp must release each
  conductor after insertion (cam-lifted "piano key" fingers), and a second clamp
  bar must come within ~1 mm of the crimp so an 8 mm column does not buckle. The
  crossing conductor (J4's GND, J7's GND) goes in last, so it lands on top.
- **Per-conductor order, strip to insert** (procedure-is-the-machine p2): the
  head strips, crimps, looks and inserts one conductor before the next. A strip
  head on the carriage would be [b7](b7-borrowed-strip-head-one-conductor.md)'s
  die-hole blades or ribbon-as-pallet's a8b spindle. Stripping one conductor at a
  time after the fan puts the strip line back on each conductor's own tip, which
  still keeps the along-conductor distances equal.
- **A still ribbon from the spool** (procedure-is-the-machine p3): the end is
  held at a work clamp fed from the spool instead of being laid into grooves. It
  removes the person's slowest step here, but the fan then has to be formed at
  the clamp, by combs that close on the split conductors
  ([b8b](b8b-flat-spool-line-over-a-crown.md)'s comb, entered from the tips).

## Problems and their repairs, as they stand

- **The conductor buckles when pushed into the housing.** Per conductor, an 8 mm
  free column buckles at a few newtons. Gang insertion moves the housing onto a
  row that stays put, and the converging comb holds each conductor close behind
  its crimp.
- **The captive contact slides forward when the strands catch the barrel's rear
  edge.** The neck blade holds it axially; the captive pinch only holds it down.
- **Strands splay when slid lengthwise into the barrel.** Sixty loose 0.08 mm
  strands can catch on the wing tips. A light twist when stripping (b7), the
  insulation barrel's wide mouth and the V-fork's axis help; the camera sees a
  stray strand before crimping, and the machine backs out and retries.
- **Trimming to a stepped edge after stripping** would move each insulation edge
  forward by the trim: 0.54 mm on a 4P at 4.35 mm pitch, 1.06 mm on a 5P,
  2.27 mm on J4, and into the jacket on J1, putting insulation under the
  conductor barrel [TS §2]. The flat strip line before the fan removes the trim.
- **A printer carriage and a 1 kg head.** An Ender-class carriage carries a
  direct-drive extruder and hot end, ~0.3–0.5 kg [estimate]; at slow speed 1 kg
  is a matter of stepper torque and wheel preload. Steel V-wheels or an MGN12
  carriage conversion are printer-ecosystem parts.
- **A wrapped sprocket** would bend the carrier plastically below ~25 mm radius
  [TS §9]; the pawl on a flat run avoids it.
- **Why not the H2C?** The H2Cs print ~100 h per unit [repo].

## Printed and bought

- **Printed.** Fan fixture with grooves and clamp bar; feeder track body; housing
  nest; converging and guide combs; V-fork jaws; camera mount.
- **Bought.**
  - An Ender 3 V3 SE ($186.14–219.00 [Prime]), or a used Ender 3.
  - A second OTP XH applicator, for its punches and anvil (eBay or
    Made-in-China).
  - A NEMA 17 with a planetary: the 26.85:1 above, or 10:1–50:1.
  - Laser-cut steel C-frame and punch slide (SendCutSend, 12.7 mm max, 2–4 days,
    [SendCutSend](https://sendcutsend.com/materials/mild-steel/)).
  - A small stepper or servo for the pawl; two MG90S servos; a 5 kg bar load cell
    with HX711 [Prime].
  - SKR Pico ($35.99 [Prime]) or the printer's own board running Klipper.
- **On hand:** camera.

## Contribution

- The "crimp head goes to the wire" arrangement is geometrically open once the
  contact is cut free before it arrives and the conductors are fanned wider than
  the dies.
- Place, crimp and insert on one cheap gantry, with the printer doing the
  positioning and the force closed inside a hand-sized C-frame.
- A strip line cut while the ribbon is flat makes a fan crimp compatible with a
  gang insertion, with no per-loom trim geometry.

## Major unresolved problems

- **Dies.** Harvesting an OTP applicator's punches and anvil: their shapes,
  mounting and heat treatment are unknown until one is in hand. A sliding punch
  holder that keeps them aligned to ~0.02 mm in a 1 kg head is real precision
  work.
- **The converging comb.** Whether it closes crimped contacts (boxes 1.95 mm,
  gaps 0.55 mm at 2.5 mm pitch) from 4.35 mm pitch without snagging, and how
  much set the fan leaves for it to straighten.
- **Fixture loading.** Laying five split conductors into fan grooves is the
  person's slowest task here, 60–90 s per end.
- **Captive position** for a contact whose wing height varies from reel to reel
  [assumption].
- **Head stiffness** at ~1 kg total mass.
- **Insertion force** is unmeasured [facts Unresolved 4].

## What rests on what

- **Derek:** the H2Cs are busy printing [repo]; he likes building and printing
  things.
- **Facts:** contact barrel mouths, box width, insertion force unpublished
  [facts §1, §3].
- **Calculations:** fan pitch and drag [calc geometry §2]; head force and frame
  scatter [calc presses §5]; fronts and trim losses [TS §2, calc wave3 §7];
  sprocket strain [TS §9].
- **Estimates:** printer repeatability ~0.05 mm; head mass; carriage payload.
- **Assumptions:** applicator punches are usable outside their applicator; the
  V-fork holds an 8 mm cantilever to ~0.1 mm at the barrel mouth; insertion
  force is a few newtons per contact.
