# A3 — The tool travels: a self-closing crimper on a light gantry, over a ribbon that never moves

## Picture it

**Where things start.**
- The ribbon end is clamped once in a printed **loom fixture** that stands **on
  edge**: the ribbon's plane is vertical.
  - The web is clamped 25–35 mm back from the end.
  - The split conductors lie in a comb whose slots are stacked vertically at
    **2.5 mm**, the XHP cavity pitch. The splay to housing pitch is done here:
    a 5P's outer conductor moves 1.6 mm [xh-facts §7].
  - The stripped tips stand ~8 mm proud of the comb's front face.
  - For a pair (J1, J2, J4, J7), both ribbons lie edge to edge in one clamp.
  - The person lays J4's and J7's crossing conductors in the comb at
    clamping.
- The far end goes into the far-end block, as in [a1](a1-squeezer-cradle.md).
- On the fixture sit a **front plate**, a **rear clamp** and a **housing
  slide** with its own NEMA 17 screw and load cell.
- Beside the fixture, a **post column** holds contacts: 0.64 mm square pins
  cut from a male header, each carrying one contact on its box, and each pin
  wired to the ESP32.
- A fixed camera looks across the fixture at the tip of whichever conductor is
  pulled out, against a backlight.

**What moves.** An open X–Y gantry with a small Z axis carries the **crimp
module**. The belt frame of a diode-laser engraver is the class.
- **The module:**
  - the SN-2549, hung **tip-down**, its jaws closing in X, horizontally and
    normal to the ribbon's plane;
  - a NEMA 17 Tr8×2 pusher bolted to a bracket on the tool's lower handle,
    with the load cell between pusher and upper handle;
  - a1's locator plate and insulated blade, the flap on a hobby servo.
- **A side-puller** on the fixture draws the working conductor out of the
  ribbon's plane in X.

**What locates what.** "Fixed" is the loom fixture on the bench. The module
touches off electrically on a datum pin in the fixture.
- Each conductor's position is its comb slot; the side-puller holds the working
  one out of the plane; the tip picture corrects X and Z to the tip's real
  axis before the slide-on.
- The contact is located in the tool by the nest, blade and front stop, as in
  a1, except that the tool carries it.

**What drives and carries the crimp force.**
- **The crimp:** the pusher on the tool's own lower handle. The force loop is
  pusher → upper handle → linkage → dies → lower handle → bracket → pusher,
  closed inside the module as it is in a hand. The gantry feels none of it;
  it only positions a ~0.8 kg module slowly.
- **The gang push:** the fixture's own housing slide. The gantry does not
  carry it.

**How it knows it worked.**
- The tip picture before each slide-on.
- The module's force curve, run whole on the station ESP32.
- Amber and green on conductor *k* through the far-end block, and on nothing
  else.
- The post that goes open when its contact leaves.
- The fixed camera's frame of the pulled-out, crimped conductor.
- The housing slide's force trace.

**What the person does.**
- Clamps a split, stripped ribbon end in the fixture, laying crossings.
- Plugs contacts onto the post column, or pushes a strip onto it and gang-cuts
  the tabs.
- Drops a housing into the slide's holder, takes the finished end out and
  labels it.

Sketch: [`../sketches/a3-tool-travels.svg`](../sketches/a3-tool-travels.svg)
(the on-edge fixture); the jaw law in
[`../sketches/jaw-law-and-c-frame.svg`](../sketches/jaw-law-and-c-frame.svg).

## Steps it covers and what it hands back

**Covers:** splay to housing pitch (the comb), placing the contact (the tool
is the gripper), placing the conductor (slide-on), the crimp, identity and pin
order, squaring, gang insertion, and the latch pull-back as a sum.

**Hands back:** cut and split; strip, unless a strip module is added; loading
the post column; clamping the end and laying J4's and J7's crossings; dropping
the housing; unloading and labelling.

## How it relates

- The squeezer is [a1](a1-squeezer-cradle.md)'s, moved to the wire.
- The on-edge fixture, the front plate and late rear clamp, and the gang push
  on the fixture come from into-the-housing's reading (its a3-e and C1, in its
  [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md)) and
  its [i3](../../into-the-housing/ideas/i3-converging-shuttles-gang-push.md).
- The tip picture is machine-that-sees-and-learns'
  [v1](../../machine-that-sees-and-learns/ideas/v1-watched-nest.md) look before
  the irreversible act (W5 in its
  [exchange](../../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md)).
- The other head: [a4b](a4b-c-frame-one-nest-head.md), one SN nest on a
  C-frame arm, on the same gantry.
- change-the-question's [c5](../../change-the-question/ideas/c5-ends-as-stock.md)
  T4 ends give a3 one configuration (no pairs, no crossings) [htq, K4].
- Converges with force-and-form's f4 and borrowed-machines' b3 (a force loop
  closed in a travelling head).

## Major unresolved problems

- **How far each conductor is pulled.** The depth *a* of the SN jaw half that
  faces the fixture, ~6–12 mm assumed. With crimped neighbours the pull is
  *a* + 2.7 mm, 8.7–14.7 mm [calc w3 §2], and it sets the copper.
- **Slide-on capture.** The open conductor barrel captures a gathered 0.72 mm
  bundle within ±0.48–0.59 mm, but a splayed 1.0–1.2 mm bundle only within
  ±0.24–0.45 mm [sl w3 §10]. A tip 8 mm proud of a comb whose exit is 2–3° off
  sits 0.28–0.42 mm aside, and spool curl adds up to 0.55 mm: 0.28–0.69 mm in
  all [sl w3 §10; ribbon-as-pallet calc P §6]. The tip picture and a twist
  step are the repair; how often this ribbon's tips splay after the Klein is
  unknown.
- **Contact pull-off from a 0.64 mm post** is not public (0.2–1.6 N
  estimated [terminal-supply]). A thin blade carries only the low end of it.
- **The latch check in a gang push** is a sum (as in
  [a2d](a2d-batch-then-gang-push.md)).
- **A ~0.8 kg module and its cables on a light gantry.** The Prime laser
  engraver found does not state its head payload.
- **The slack behind the housing** that the front plate stores.

## The orientation, and why the fixture stands on edge

**The side-entry jaw law** [calc w2 §3]:
- An SN tool's nest axis is normal to its jaw plane. With the conductor along
  Y, the jaw plane is XZ.
- **Upright crimps.** Closing normal to the ribbon's plane gives upright
  crimps, and puts the jaw's long axis along the row. The working conductor
  must then stand out of the plane by the depth of the jaw half facing the
  ribbon, plus clearance.
- **Rolled crimps.** Closing along the row needs only the nest-to-tip distance,
  but rolls every crimp 90°: the barrels open along the row, every lance
  points along the row, no XHP can be pushed onto that row, and twisting each
  conductor back 90° over 20–35 mm strains the strands 2.3–4× past torsional
  yield [ith ex §8]. A flat fixture with the tool closing along the row is
  set aside for that reason.

**The on-edge fixture** keeps the module tip-down and closing in X, and turns
the fixture 90° about Y:
- The ribbon's plane is vertical, and the comb stacks the conductors in Z.
- The jaws, still closing in X, close **normal to the ribbon's plane**. The
  barrels open away from the plane, the same way for every conductor, which is
  the insertion orientation.
- **The side-puller** draws conductor *k* out in X by *a* + 2.7 mm, where *a*
  is measured from the nest floor to the back face of the jaw half facing the
  fixture.
  - Choose the anvil half to face the fixture; it is the shallower one when
    the jaws are open [assumption].
  - The locator plate stays inside that half's depth on the fixture's side,
    or it adds to *a* ([a2](a2-ribbon-to-fixed-tool.md)).
  - Every other conductor stays in the plane, behind the jaw.
- **The tip** still points down, so the crimp leaves through the mouth as the
  module rises.

**What the pull costs** [calc w3 §2]:
- At *a* = 6–12 mm the pull is 8.7–14.7 mm. On a 20–35 mm free length that is
  a root radius of 9–47 mm, below the ~67–78 mm at which annealed strands
  yield.
- The tip pulls back 1.3–6.5 mm while out. The crimp is right, because the
  touch-off happens in that state.
- Back in the comb, each conductor sits short by some fraction of that and
  carries a kink.
- **Squaring** after the last crimp:
  1. the front plate pushes every nose back to one line ~2 mm behind nominal,
     the excess going into the split as slack;
  2. the rear clamp closes 1–2 mm behind each insulation crimp;
  3. the plate withdraws.

  The fronts are then set by the plate, not by strip length or pull history.

## The cycle, one conductor

1. **Pick.**
   - The module goes to the post column's next contact with the jaws open and
     the flap up.
   - It moves +Y so the contact passes through the jaw from the front face
     side, **with the anvil held ≥ 1 mm off the contact's floor**. Then it
     steps 1 mm in X to set the floor on the anvil. The lance never meets the
     anvil face.
   - The flap drops, and the pusher closes to hold.
   - The module moves −Y, and the contact slides off its post. The post's
     input goes open, which confirms the pick. The pull-off goes into the
     blade and the hold's friction.
2. **Pull out and look.** The side-puller draws conductor *k* out of the plane
   by *a* + 2.7 mm. The fixed camera takes the backlit tip: splay, a strand
   standing out, strip length, the torn edge. The gantry corrects X and Z to
   the tip's real axis. A splayed tip goes to a twist (a small pinch that
   rolls the bundle) or to a question.
3. **Slide on.** The module goes to *k*, nest on its corrected axis, ~2 mm in
   front of the tip, and moves −Y. The conductor stays still while the contact
   slides over it, until amber and then green on *k*.
4. **Crimp.** The pusher runs the full stroke.
5. **Release.** The tool opens to its limiter, and the flap lifts. The module
   steps ~1.5 mm in X, lifting the crimp off the anvil, then rises +Z, so the
   crimp leaves through the tip-down mouth. It never moves rearward low in the
   nest.
6. **Lay it back.** The side-puller returns conductor *k* to its slot.

There is no proof pull in the tool, since neither the blade nor re-closed dies
can carry an honest one ([a1](a1-squeezer-cradle.md)). It is done after the
gang push, as the latch pull-back through the housing slide. Per crimp this is
the same order of time as a2 (~90–100 s) [calc §10].

## The row, and the gang push that belongs to the fixture

After the last conductor, the fixture holds every crimped contact in its comb
slot, in the housing's cavity order, in the insertion orientation.
1. **Square:** the front plate, the rear clamp, and the plate withdraws.
2. **Guide:** a sprung guide comb (into-the-housing's i3) holds each nose
   square until the cavity lead-ins take over. The housing's approach presses
   it down and back.
3. **Push:** the fixture's housing slide drives the XHP onto the whole row
   through its load cell, with a NEMA 17 on a 2 mm screw (~280 N against J1's
   27–225 N [ith ex §12]). The gantry brings the housing holder to the slide,
   or does not touch the housing at all.
4. **Pull-back:** the slide backs the housing off at a limited force, with the
   rear clamp still closed. Force before distance says the latches hold, as a
   sum.

a3 crimps every contact where it will finally sit relative to the web. With
the fronts squared it needs zero stored feed.

**Buckling.** As clamped at the comb, 4.1–4.8 mm of conductor is free behind
each contact. That buckles at 8–15 N with the nose free [ith ex §7]. The rear
clamp leaves 1–2 mm, or the guide comb holds the nose square.

**Pin order is physical once laid.** A crossing conductor lies over its
neighbours behind the comb. The far-end touch-off catches a wrong crossing at
the slide-on, when the conductor that reads differs from the pin map, before
anything is crimped.

## The post column

- **What a post does.** The XH box is built to take a □0.64 mm post and grip
  it [xh-facts §3]. On a pin cut from a male header, a contact is held by its
  own spring, lying square, and oriented if the bar under the post has a keyed
  rest for the barrel floor.
- **Wired posts.** Each post is an ESP32 input. Continuity through the grounded
  tool shows which contact was taken and when its box left the post.
- **The cost.** Each contact gets one extra mating cycle, as on i5's header.
- **Loading:**
  - **loose kit contacts,** plugged on by hand away from the wire;
  - **strip,** pushed onto the column at the strip's pitch, then a blade drawn
    down the column's rear cuts every tab at once.
- **The grip.** Pull-off grip is estimated at 0.2–1.6 N [terminal-supply a4,
  from a Molex KK figure]. A 0.10 mm blade tine sees ~960 MPa at 1.6 N;
  0.15 mm sees ~430 MPa [calc w2 §2 method]. A 0.60 mm pin lowers the grip.

## Why the tool moves and the wire stays

- **The floppy thing never travels.** Sogang's printed ribbon inserter lost
  most of its failures moving the cable (transfer 43/50, insertion 49/50)
  [prior-art]. Here the ribbon is clamped once per end.
- **The crimp force never enters the motion system.** A laser-engraver gantry
  is enough because the tool closes on itself.
- **The tool is the gripper.** The contact is held by the same nest that
  crimps it, so nothing hands it over between handling and crimping. That
  handover is what Cellios measures with two cameras after every handling in
  its robot cell [prior-art §0].

## Tool changer

- **The mount.** The module hangs from the gantry on a kinematic mount: three
  balls in three V-grooves (6 mm chrome steel balls, $6.65 [prime:
  B07L8MLK2N]), held by magnets (N52 10 × 3 mm, $23.99 [prime: B0GF7RLFXR]),
  with pogo pins for the stepper, load cell, servo and ground.
- **Any closed tool is a module:** the SN-2549, or a4b's C-frame head; the
  Klein 11063W, as in [a2c](a2c-one-baseplate-strip-crimp-insert.md); KATA
  flush cutters, for trims.
- **The housing** stays on the fixture's slide.

## Parts

- **Gantry.** An open-frame diode-laser engraver's X–Y belt frame with an
  added Z (a Tr8 stepper axis): LONGER Ray5 10 W, 400 × 400 mm, $268.99, 176
  ratings, head payload not stated [prime: B0G13BBN9L]. A secondhand printer
  gantry is the other route.
- **Module:** SN-2549 ($22.29 [prime: B01N4L8QMW]); NEMA 17 Tr8×2 external
  linear stepper ($27.78 [prime: B07TB7FPPP]); load cell and HX711; hobby
  servo.
- **Fixture:** printed on-edge body, web clamp and comb; side-puller fingers;
  front plate and rear clamp on servos; housing slide with NEMA 17 Tr8×2 and a
  bar cell; post column of header pins (2.54 mm headers, $7.99 for 20 strips,
  pin section not stated [prime: B01MQ48T2V]); a backlight and camera for the
  tip.
- **On hand:** ESP32 stack, ELP camera.

## Rests on

- **[assumption]** The SN-2549 works hung tip-down, the crimp leaving through
  the mouth.
- **[assumption]** The open jaw passes a contact end-first with 1 mm of
  clearance under its floor.
- **[assumption]** A laser-engraver gantry carries ~0.8 kg slowly without
  skipping.
- **[assumption]** The anvil half is the shallower jaw half when open.
- **[estimate]** Capture windows and comb-exit angles from [sl w3 §10].

---

Citation keys: **[calc §n]** is [`../calc/hand_tool_press.out.txt`](../calc/hand_tool_press.out.txt);
**[calc w2 §n]** is [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[sl w3 §n]** is machine-that-sees-and-learns'
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[htq, K4]** is a combination in
[`hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
