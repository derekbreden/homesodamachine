# p2 Still ribbon, tools come to it

Sketch: [`../sketches/p2-turret.svg`](../sketches/p2-turret.svg) (schematic side
view). Numbers: the first calcs in [`../calc/`](../calc/) by name,
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) and
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) (cited as [calc wave2 §n] and
[calc wave3 §n]).

The ribbon end is clamped once and never let go until its housing is on. It is
never re-gripped, carried or handed over. Every tool comes to it: a trim blade,
a web splitter, strip jaws, a crimp head carrying its own contacts, a camera and
an insertion gripper. The order is **per conductor, straight through**:
conductor 1 is stripped, crimped, looked at and inserted before conductor 2 is
touched. The machine is one datum with many small motions around it.

## Picture it: J2, two 3Ps into an XHP-6 with cavity 3 empty

**Loading (person, ~1 minute).**
- The person lays both 3Ps edge to edge in the **work clamp**, 3P-a against the
  datum, tips loose, web unpeeled.
- The clamp is on a **y carriage** (a lead-screw slide across the wire axis),
  which also carries a **housing nest** and a small **drop stage** under it.
- The far end's cut face goes into a pogo block on the y carriage
  (ribbon-as-pallet a6), so every conductor is a wire to the controller.
- The person drops an XHP-6 into the nest, presses start and leaves.

**What moves.**
- **y**, the carriage: which conductor, or which housing cavity, is on the work
  line.
- **A drum turret** on an **x** slide in front of the clamp, with six tool
  stations. The tool at 9 o'clock faces the ribbon, and x brings it along the
  wire axis.
- **A selector** under the row: a finger that lifts the active conductor above
  the others by the height its crimp head needs.
- **The drop stage** lowers the housing ~10 mm below the row so tools pass over
  it, and raises it for insertion.

**Sequence for J2** (the program comes from the loom name the person selects):
1. **Trim.** A blade crosses the tips at a line fixed to the clamp.
2. **Split.** Five razor blades pressed through the two webs over ~30 mm, then a
   fan comb on the clamp steers the six conductors to 2.5 mm. (Or
   [p7](p7-strip-before-split.md)'s whole-end strip first, then the split from
   the slug's gap.)
3. **Conductor 3 of 3P-a.** The selector lifts it; the trim tool cuts it back to
   the split point. The program skips cavity 3 from here on.
4. **Conductor 1:**
   - **Lift once.** The selector lifts it, and every tool acts on it in that
     pose ([p1c](p1c-lift-once-tip-down-module.md)'s rule), so the waiting
     conductors keep no set.
   - **Strip jaws** come in along x, close 2.4 mm from the tip, and retreat 3 mm
     with the slug.
   - **The crimp head** comes in along x and crimps (its three forms are below).
     At the end of the wing curl the head's steel reads which far-end conductor
     is in the contact.
   - **Camera**: brush, bellmouth, window. The head's force curve and bottom were
     already logged.
   - **Insertion gripper**, a two-jaw pinch on the insulation 2–3 mm behind the
     insulation barrel: the drop stage raises the housing to the row; the gripper
     takes the contact back ~7.4 mm while the conductor between gripper and comb
     bows ~10 mm upward under a guide finger [calc selector_and_bow §3]; it aligns
     the contact with cavity 1, pushes, and pulls back 5–10 N (seated if nothing
     moves [prior-art §5]).
   - The housing drops out of the way again, taking conductor 1 with it.
5. Conductors 2, 4, 5, 6 the same, into cavities 2, 4, 5, 6. Cavity 3 stays empty
   because nothing was ever crimped for it.
6. The clamp opens. The person takes the loom out with its housing on.

**The crimp head's three forms.** Each makes an upright crimp, floor down, lance
toward the housing's window face, and each closes its force inside itself.

*Head C, a strip-fed C-frame.* A fixed anvil and a punch on its own NEMA 17,
lead screw and toggle, a stop at the bottom, and a load cell; a coil of 100–200
contacts on cut strip, and a pawl that pre-feeds one onto the anvil before each
approach. The lifted conductor enters the open barrels axially from the rear,
through a V lead-in on the head, the insulation riding on the carrier (the
carrier is flat, in the barrel floor plane, as in any side-feed applicator), until
x puts the insulation edge in the window. The tab shears in the stroke.
- **The crimp's way out.** Withdrawing along +x would drag the crimped box
  (1.95 × 2.4 mm) back through the lead-in's 1.7 mm throat. So the lead-in is two
  printed halves that a small servo parts after the stroke; the punch rises, the
  halves open, and the head withdraws past the crimp.
- **The head's depth.** Its body below the conductor axis must stay above the
  row: at 8 mm of lift, ≤ ~5.3 mm including anvil, base, strip track and pawl. An
  applicator's lower tooling is deeper, so head C's lower half is built thin, or
  the lift grows.

*Head T, a hand-tool module* ([p1c](p1c-lift-once-tip-down-module.md)): the
SN-2549 on its side, jaws closing vertically, anvil half underneath, its pusher
bolted to its own handle, ~0.8 kg. It picks a cut-free contact from a post
revolver on the drum's spare station, closing only until the upper jaw's flare
touches the wing tips so the insulation bore stays open, with a1's blade in the
neck. The selector lifts *k* by *a* + 2.7 = 8.7–14.7 mm [calc wave3 §1], which
wants a 30–35 mm split. After the crimp the jaws open and the module moves off
sideways through its mouth.

*Head F, a fin from below* ([p1d](p1d-lift-once-fin-from-below.md)): a small
steel C whose throat faces the clamp, its upper arm above the row with a knee and
a narrow stepped crimper, its lower arm under the cantilevered tips with a fin
sliding vertically in it. x brings the C in until the crimper is over the lifted
conductor; the fin rises through *k*'s empty slot; the knee crimps; the fin drops
before the C withdraws. The selector lifts *k* only 3.5 mm; the contact goes onto
*k* from a post on the y carriage before the fin rises.

**Knowing it worked.** Per conductor: identity at the end of the curl, the force
curve and bottom, the camera frame, and the insertion's force-before-distance
check. Nothing is inserted until it has passed. A header on the drop stage reads
pin to pin through the far-end pogo block before unloading.

**What the person does.** Per housing: lay the ribbon(s) in, drop a housing into
the nest, take the finished loom out and label it. The machine calls every
~14 minutes [calc person_timeline], ten times a unit. Cutting to length stays
with the person.

## What locates what

| Moment | Located | Against | Held to |
|---|---|---|---|
| Whole run | ribbon | work clamp datum (on the y carriage) | fixed for the whole end |
| Trim | tips | trim tool's blade, turret at a detent | ±0.05–0.1 mm [estimate] |
| Crimp | conductor into contact | the head's own lead-in (C), nest (T) or crimper flare over the fin (F); the x position | the head's own ±0.05 mm; x repeat |
| Crimp height | dies | inside each head: stop (C), the SN's jaws (T), knee at straight (F) | the head's own |
| Insert | contact to cavity | gripper jaws; housing nest on the drop stage | ±0.1 mm [estimate] |

"Fixed" is the clamp for the ribbon and each tool's own frame for its work. The
turret only brings a tool within its capture; the x slide sets depth.

## What drives the crimp and carries its force

Each head carries its own drive and closes its own loop: C's NEMA 17 and toggle
inside its C-frame; T's NEMA 17 on the SN's own handle; F's NEMA 17 on a knee
inside the steel C. The turret, the slides and the clamp carry positioning loads
only.

## Steps it covers, and what it hands back

- **Automated:** trim, split, strip, place the contact on the conductor, crimp,
  look, identity, insert (per conductor, including crossings and the skip),
  pin-to-pin test.
- **Handed back:** cutting to length; laying each housing's ribbon(s) into the
  clamp with a housing in the nest (ten calls a unit); unloading; labelling.

## Printed and bought

- **Printed:** drum turret, tool carriers, strip-jaw carriers, V lead-in halves,
  fan comb, selector, guide finger, housing nest, head covers and strip track.
- **Bought** (Prime rows observed 2026-09-28): four to six small steppers
  [Prime: NEMA 17 with integrated T8×2 lead screw, $27.99] on two BTT SKR Pico
  boards [Prime: $35.99 each]; for head C a thin anvil and punch set; for head T a
  dedicated SN-2549 [Prime: $22.29]; for head F p1d's steel; a load cell [Prime:
  bar load cell with HX711, $9.99]; contacts on cut strip [xh-facts §6]; P75 pogo
  pins [Prime: $6.49].

## Problems, and what answers each

1. **Per-conductor insertion with a clamped ribbon is geometrically hard.** A
   seated contact sits where its unseated self was, so each contact comes from
   ~7.4 mm behind its seat and its conductor bows ~8–11 mm out of the row [calc
   selector_and_bow §3]. The guide finger makes the bow go up, not sideways.
   - **Branch p2′:** keep straight-through strip, crimp and look, then raise the
     housing and slide it onto every contact at once (gang). No bow, no gripper,
     and crossings out of reach.
2. **The housing is in the tools' way.** The drop stage lowers it with its
   inserted conductors; they are neighbours, and neighbours belong below the row
   anyway.
3. **The turret carries a heavy head.** A ~1–2 kg head on a drum turns slowly; a
   pin into a hardened bush, set by a small solenoid, holds position; the head's
   own lead-in, not the detent, locates the conductor [calc transfer_capture §1].
4. **Crossings (J4, J7).** The gripper carries a conductor over already-inserted
   neighbours to any cavity, in an order the program plans (the crossing
   conductor last). This is the one arrangement here where the machine, not the
   person, makes the crossing.
5. **Recovery.** A bad crimp at *k* stops the end with *k*−1 contacts inserted.
   The machine pulls the housing off, cuts the whole end back ~6 mm, splits a
   further 6 mm and starts again [calc recovery_length §1]. Checking per
   conductor finds a fault after ~0.7 wasted crimps on a 5-conductor end, against
   ~1.1 when checked at the end [calc recovery_length §5].

## Contribution

- **"Never re-grip"** removes a class of errors: where a contact sits in a
  gripper after handling [prior-art §0, Cellios].
- **"Per conductor, straight through"** is the only order in which the machine
  alone makes J4's and J7's crossings and J2's skip by program.
- **The turret is a slot for tools**: a different strip method or a different
  crimp head is a different tool on the drum, and nothing else changes.

## Major unresolved problems

- **The number of axes.** At least six motions around one point; each simple,
  together a clearance problem.
- **The head:** C's exit and depth; T's lift (*a*, a 30–35 mm split); F's made
  steel.
- **Bow-and-push insertion on soft silicone** is not demonstrated anywhere found;
  the Sogang ribbon inserter's failures came mostly from moving floppy cable
  [prior-art].
- **Per-housing loading**: ten calls a unit. A magazine of work clamps makes it
  p1 by another name, which is a reasonable way for the two to meet.
- **Stripping and splitting** as everywhere.

## What rests on assumptions

- Bow heights assume a ~30 mm split behind the comb and a 6.4 mm contact.
- The call interval assumes ~145 s per conductor including tool changes
  [estimate].
- Axial entry into open barrels assumes the lead-in lines the conductor up to
  ±0.3 mm; hand tools with locators feed wires this way [prior-art §3], a moving
  head is untested.
