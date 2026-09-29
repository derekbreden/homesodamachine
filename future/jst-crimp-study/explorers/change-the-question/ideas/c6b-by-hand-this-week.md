# c6b — By hand this week: a lever pre-former, a snap block, and a flag seat on the SN-2549

Branch of [c6](c6-pre-form-the-contact.md): the same pre-form step with no
motor and no microcontroller, built around the tools already on the bench.
It combines c6 with terminal-supply's box-keyed clip (C4 in
[`../../../exchange/terminal-supply--on--change-the-question.md`](../../../exchange/terminal-supply--on--change-the-question.md)),
hand-tool-as-press's flag seat
([`flag-seat.svg`](../../hand-tool-as-press/sketches/flag-seat.svg), from its
[a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md)) and
into-the-housing's [i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md)
sensing nest. Its sibling [a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md)
lets the SN-2549 make the pre-form itself, closes the tool by foot, and wires
every stop to an ESP32. Sketches:
[`../sketches/c6-shapes.svg`](../sketches/c6-shapes.svg) (the pre-forms and
what the final stroke does to them) and
[`../sketches/c6b-bench.svg`](../sketches/c6b-bench.svg) (the bench and the
seat; schematic). Numbers: [`../calc/wave2.out.txt`](../calc/wave2.out.txt)
[w2 §n], [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [w3b §n],
[`../calc/on_into_the_housing_w3.out.txt`](../calc/on_into_the_housing_w3.out.txt) [w3 §n],
hand-tool-as-press's [`exchange_ctq_w3.out.txt`](../../hand-tool-as-press/calc/exchange_ctq_w3.out.txt) [htq §n].

## Picture it

On one printed baseplate, left to right, three stations and an insertion
nest. Each splits off one part of today's single juggling act (hold the tool
one click shut, hold the contact captive, feed a floppy conductor into it).

**1. The pre-former (no wire anywhere near).**
- c6's steel nest, mandrel and jaws, closed by a push-pull toggle clamp
  (POWERTEC 305CM, Prime-confirmed, $18.25 a pair, 605 ratings
  [sourcing/amazon-prime.md]) through a short printed lever. The jaws need
  ~10–80 N [w2 §3]; the clamp's own stop sets how far they close.
- The nest is a steel box slot with a lance relief and a front stop, or a cut
  kit XHP housing used as a box pocket (into-the-housing's
  [i2d](../../into-the-housing/ideas/i2d-locator-the-lance-never-touches.md)
  stub). "Fixed" is the nest block.
- The mandrel is chosen once, from the jacket OD Derek measures on five split
  conductors: bore 0.08–0.12 mm under it, e.g. a 1.56–1.57 mm pin for a
  1.70 mm jacket [w3b §3]. Two mandrels are possible:
  - a **round pin** makes c6's keyhole (1.96–2.14 mm wide, 1.3–1.7 mm tall);
  - a **flat blade** 1.5–1.6 × ~2.5 mm makes a tall keyhole (~1.9–2.05 mm
    wide, ~2.5–2.9 mm tall), whose tips the SN-2549's own stroke will finish
    into a B.
  Which one depends on how wide the SN-2549 opens (station 3) and on whether
  the keyhole's O-shaped final crimp qualifies (c6, "What the final crimp does").
- Derek drops a kit contact barrels-up into the nest (the lance relief lets it
  sit only one way), slides the mandrel in with a knob, throws the clamp,
  releases, pulls the mandrel, and pushes the contact out forward with a
  plunger into a **stick** clipped to the nest's exit.
- Sticks are printed channels with a lance groove, one per housing and
  labelled: four contacts for a T4 end, nine for J1, five plus a blank spacer
  at position 3 for J2. A unit is ten sticks, 53 contacts, ~5–9 minutes at the
  lever while a print runs [estimate].

**2. The snap block.**
- A printed block with one pocket: a box slot with a lance groove, a steel
  floor under both barrels, and a hardened front stop for the box's mating
  face. A printed tip stop sits at the strip length Derek's own crimp tests
  settle on (JST says 2.4 mm; the KONNRA clone spec 1.6–2.1 mm [digest]).
- A window under the pocket with a white LED shows the stripped tip against
  the light before it disappears: no stray strands, the whole bundle over the
  U.
- Derek pushes the next contact from the stick into the pocket, lays one
  stripped conductor over it with its cut tip at the stop, and presses a
  printed **thumb tool**: a fork whose rear tine sits on the jacket over the
  insulation barrel and whose front tine sits on the strands over the
  conductor barrel. The jacket snaps in (~0.3–30 N, a few newtons at central
  values [w2 §4]); the strands go into the U; the steel floor takes the push,
  the lance none of it.
- He lifts the conductor. The contact comes with it: a **flag**, at the right
  axial position and roll, held along the wire by ~0.1–3.5 N [w3b §3].

**3. The crimp: the SN-2549 with a flag seat.**
- The SN-2549 sits in a simple printed cradle with its lower handle clamped,
  so one hand squeezes and the other guides the flag (hand-tool-as-press's
  [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md) cradle, without
  the motor). The seat mounts on the lower jaw's M4 screw, lengthened to
  20 mm (the mount published SN-2549 positioners use [source via
  hand-tool-as-press]). "Fixed" is the lower jaw.
- **The seat** carries the flag level, clear of the anvil, so its lance never
  drags across the jaw's edge:
  - on the jaw's rear face, a printed U guide that takes the jacket;
  - on the front face, an open-topped slot keyed to the box and its lance,
    with a thin spring-steel strip in its floor. The slot can be a cut kit
    XHP-2 on a small vertical flexure (i2d's stub), molded at product
    tolerance, squaring roll to ±1.2–6.5° [w3 §4];
  - both guide and slot at one height *h* = 1.1–1.7 mm above the anvil, on
    1–3 N springs. *h* clears the lance on entry (lance + 0.2 = 0.8–1.1 mm)
    and gives the 1.0–1.7 mm lift a crimped lance needs before it is drawn
    back [htq §4].
- **The stop** is an insulated spring-steel leaf across the slot's front,
  preloaded to 10–30 N.
- **The lamp.** A coin cell and an LED are wired between the floor strip and
  the leaf. The box sits on the strip; when its face touches the leaf it
  bridges the two and the LED lights. No far-end wiring, no microcontroller.
- Derek lays the jacket in the rear U and slides the flag box-first through
  the open jaws **until the lamp lights, and stops pushing**. He squeezes: the
  punch meets the wings, pushes the contact down onto the anvil against the
  1–3 N springs (the wings need tens of newtons to curl), curls and coins; the
  ratchet completes. When the tool opens, the springs lift the crimp back to
  *h* and he draws it out through the nest.

**4. Insertion and test.** into-the-housing's i5 nest: the housing plugged
onto a real XH header whose posts are microcontroller inputs; Derek starts
each contact into its lit cavity, a spring-limited lever seats it, and the
post that closes names the cavity. Or by hand as today, then a wafer test.

**What locates what.**

| Pair | Located by | Reference for fixed |
|---|---|---|
| Contact in the pre-former | box in the nest, face on the stop | nest block |
| Conductor tip to contact | tip stop and box stop in the snap pocket; then the snap's grip | snap block |
| Flag to the die, axially | box face on the leaf (lamp) | lower jaw, through the seat |
| Flag laterally and in roll | keyed slot on box and lance; rear U on the jacket | lower jaw |
| Flag vertically | sprung supports at *h*, then the punch presses it onto the anvil | anvil |
| Crimp height | the SN-2549's dies and ratchet, as today | the tool |

**What drives and carries the force.** The toggle clamp (10–80 N) at the
pre-former, a thumb (0.3–30 N) at the snap, and Derek's grip on the SN-2549
(150–300 N through the tool's leverage [xh-facts §4]) at the crimp, closing
jaw to jaw inside the tool's head as today.

**How it knows.**
- The stick carries the loom's order; a missing contact is a visible gap.
- The backlit pocket shows the tip before it disappears into the barrel.
- The lamp says the box is at its stop.
- A light tug on the flag before the crimp (it should not slide at ~0.1 N).
- Crimp height by caliper on a sample, a pull on a sample with the bench
  scale, and the header nest at insertion.

**What the person does.** Everything, still, but each act has one part and
one stop: pre-form in bulk (no wire, no crimp tool); snap (a tip stop and a
box stop); crimp (slide to the lamp, squeeze); insert against a lit, sensing
nest. Estimated 20–32 s per contact against ~25 s today [estimate; the close
sibling a6b is 22–34 s, htq §8]. What it buys is consistency and a check at
each stop, not minutes.

**Steps covered:** pre-form, place (snap, by hand against two stops), crimp
(by hand against a box stop), insert (sensing nest). **Hands back:** every
motion to the person, each made simpler.

## What grows from it

| Hand piece | What a motor or another explorer's machine replaces it with |
|---|---|
| Toggle-clamp pre-former | c6's servo pre-former fed from terminal-supply's rail, post or plate, or from strip; or the SN-2549's own click ([a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md), [a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md)) |
| Sticks in loom order | the same sticks feeding a pallet loader ([c1c](c1c-crimp-in-the-row.md)), or stood over hand-tool-as-press [a2b](../../hand-tool-as-press/ideas/a2b-gravity-tool-flat.md)'s nest as its chute |
| Snap block, one pocket | c1c's pallet: a half-row of pockets and a presser comb snapping 2–5 at once |
| Flag seat and lamp on the SN-2549 | a6b's wired seat on a foot treadle, with the far end as an electrode array; force-and-form [f1](../../force-and-form/ideas/f1-motorised-ratchet-crimper.md) or hand-tool-as-press [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md) cradles; force-and-form [f9](../../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md)'s keyed steel nest |
| i5 nest | into-the-housing's insertion machines |

## Problems worked through

1. **It is more steps than today.** Three where today has one, each shorter
   and each with a stop. The step that needs skill today, holding a captive
   contact while threading 60 fine strands into it, is gone.
2. **A flag pushed box-first on the anvil drags its lance.** The lance
   (0.6–0.9 mm proud, tip rearward) meets the lower jaw's rear edge and folds
   at 1–5 N, above the flag's 0.1–3.5 N grip; the contact would stop and the
   jacket keep moving, losing the strip position with no sign [htq §4]. The
   seat carries the flag at *h*, clear of the anvil, and the punch seats it.
3. **The grip is too light to feel the stop by hand.** Pushing the jacket
   against the leaf, the contact slides back along the jacket before any
   resistance is felt. The lamp ends the push at first touch. A tighter bore
   (0.15–0.2 mm under the jacket) raises the grip toward ~5 N at the price of
   a harder snap [w2 §4].
4. **A rigid stop at the box nose blocks the conductor barrel's growth.**
   Coining pushes the barrel's front 0.03–0.11 mm toward the box with up to
   80–520 N; against a rigid stop the transition bows ~0.07–0.19 mm [w3 §3]. The leaf is preloaded to 10–30 N: far above what the
   person can push through the jacket, well below what the growth pushes, so
   it gives way to the growth. A PA6 stub face would dent instead; the stub
   keys X, Z and roll, and the leaf holds Y.
5. **The flag's roll is held only by friction on the jacket.** The keyed slot
   squares it; the slot's own friction (0.1–0.5 N) is inside the grip.
6. **Why not snap an open contact?** An open clone insulation barrel
   (2.46–3.25 mm) holds nothing: the 1.7 mm jacket drops in and lifts out.

## Contribution

- A first build for the priority step that is useful by itself, with no motor
  and no electronics beyond a coin cell, on the tools already owned, whose
  pieces are the interfaces of the automated versions.
- It takes the contact out of the crimp tool's juggling: by the time the tool
  closes, contact and conductor are already one part.

## Major unresolved problems

- **Whether the SN-2549 opens wide enough at the XH nest** to pass a flag
  carried at *h*: 3.5–4.3 mm with the keyhole, 3.6–4.9 mm with the tall
  keyhole [htq §4]. Unmeasured. If it does not, the seat does not fit, and
  dragging the flag on the anvil loses the strip position. The way out is a
  tool that opens further: Engineer's PA-09 non-ratchet plier (Prime-confirmed,
  $38.99, 1,719 ratings [sourcing/amazon-prime.md]; hand-tool-as-press
  [a5](../../hand-tool-as-press/ideas/a5-two-squeeze-plier.md)), which crimps
  the conductor and insulation barrels in separate squeezes [mfr S18].
- **Everything c6 leaves:** the final crimp over a pre-formed barrel (O-shaped
  over a keyhole, a B over a tall keyhole), snap force and grip on real kit
  contacts, springback scatter, the jacket's OD along a spool.
- **Strip length** for the tip stop: 2.4 mm (JST) against 1.6–2.1 mm (KONNRA
  clone spec).
- **Whether three simple steps are quicker in total** than today's one is
  unmeasured; the case is consistency.

## What rests on assumptions

- The pre-forming, snap and grip estimates of c6 [w2 §3–4; w3b §2–3].
- The seat's heights and the SN-2549's opening [htq §4, estimate].
- The SN-2549 clip mount on the lower jaw's M4 screw [source via
  hand-tool-as-press: Chief Delphi and Printables positioners].
- That a tin-plated box bridging a floor strip and a leaf lights an LED
  reliably at a few newtons [assumption; a thin oxide may need 1–2 N].
