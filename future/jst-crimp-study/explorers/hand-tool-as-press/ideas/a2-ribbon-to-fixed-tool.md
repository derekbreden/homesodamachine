# A2 — The ribbon comes to a fixed tool: a carriage loads contact and conductor into a1's squeezer

## Picture it

**Where things start.**
- [a1](a1-squeezer-cradle.md)'s squeezer is bolted to a baseplate: the
  SN-2549 on its side, the pusher, the locator with its insulated flap blade.
  A hobby servo lifts the flap.
- Beside it is a vertical magazine of **carrier stubs**. Each stub is one
  SXH-001T-P0.6 contact still joined by its tab to one pitch of carrier strip,
  with that pitch's pilot hole.
- The person clamps one ribbon end into a head on a small three-axis carriage.
  The ribbon is split back 25–35 mm and stripped 2.4 mm, JST's length for the
  genuine contact the stubs carry [mfr S6].
- The ribbon's far end goes into the far-end block wired to the ESP32.
- The person picks the loom on a screen (J1…J13). The controller then knows
  the conductor count and which conductor, if any, is skipped (J2's cavity 3,
  J7's trimmed conductor).

**What moves.**
- **The carriage:** X across the conductors, Y along the nest axis, Z in
  height.
- **On the head:**
  - the ribbon clamp, mounted through a small load cell;
  - a comb that holds the split ends at ~3 mm pitch in slots ≥ 8–10 mm long;
  - a servo **fork** that pulls one conductor out of the comb;
  - a servo **pin** that rises into a stub's pilot hole.
- **Off the head:** a1's pusher closes the tool; a servo-driven **shear blade**
  slides down the die's rear face; a camera looks at each stripped tip from
  above against a backlight.

**What locates what.** The lower jaw is "fixed", as in a1. The carriage
touches off on a grounded datum pin on the locator plate, so its coordinates
are the jaw's coordinates.
- **Contact.** The pin in the pilot hole locates it until the jaws close to
  "hold". From then the nest and the blade hold it.
- **Conductor, sideways and in height:** the fork, 3–8 mm behind the jaw's
  rear face, corrected from the tip picture.
- **Conductor, along the axis,** in one of two ways:
  - the strands reaching the insulated blade (green, as in a1);
  - the tip touched off first on a grounded **tip plate** beside the tool,
    whose Y is known from the datum pin, then fed a set distance. This needs
    nothing in the neck, and the neck frame checks the brush.

**What drives and carries the crimp force.** a1's pusher, through the tool's
own linkage. The crimp force closes inside the tool head. The carriage feels
only:
- the few newtons of carrying a stub into the open nest;
- the light touch of strands on a stop;
- the proof pull, taken at a separate pull slot.

**How it knows it worked.**
- The tip picture before the feed: splay, a strand standing out, the torn
  insulation edge. The tip plate's reading against the picture checks the
  camera's scale and focus on every conductor, and a tip that touches early
  against the picture is a splayed strand, found before the lay-in (W9 in
  machine-that-sees-and-learns'
  [exchange](../../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md)).
- a1's force curve against the taught band, run whole on the station ESP32.
- Continuity on the right conductor, and only that one.
- The neck frame at hold and a side frame with the jaws open, judged against
  what the housing needs (a1).
- A **proof pull** at a backed pull slot on the baseplate, ~20 N on the
  clamp's load cell. A crimp that slips shows as travel without force.

**What the person does.**
- Loads the stub magazine (stubs snipped from cut strip in a batch, or by a
  snipping station).
- Clamps each ribbon end and picks the loom.
- Answers the conductors the machine parks with a question.
- Takes the finished ribbon end out. Each conductor carries a crimped contact
  with its tab cut.
- Inserts the contacts into the housing, or hands the end to
  [a2d](a2d-batch-then-gang-push.md)'s housing press.

Sketch: [`../sketches/a2-ribbon-to-fixed-tool.svg`](../sketches/a2-ribbon-to-fixed-tool.svg);
the stand-out in [`../sketches/jaw-law-and-c-frame.svg`](../sketches/jaw-law-and-c-frame.svg).

## Steps it covers and what it hands back

**Covers:**
- presenting each conductor in turn, with a tip picture first;
- placing the contact (stub);
- placing the conductor in the contact;
- the crimp;
- the tab cut at the die's rear face;
- the proof pull at a pull slot;
- inspection frames;
- conductor identity, and skipping trimmed positions.

This is the step Derek most wants automated, done end to end. The person is at
the start (clamp a ribbon end) and the end (take it out).

**Hands back:**
- cutting ribbon to length;
- splitting the end 25–35 mm;
- stripping (unless [a2c](a2c-one-baseplate-strip-crimp-insert.md));
- loading stubs;
- housing insertion (unless [a2d](a2d-batch-then-gang-push.md));
- the label.

## How it relates

- Base: [a1](a1-squeezer-cradle.md)'s squeezer.
- Branches: [a2b](a2b-gravity-tool-flat.md) (loose contacts dropped into a
  tool lying flat), [a2c](a2c-one-baseplate-strip-crimp-insert.md) (the same
  carriage visits a stripper and a housing too),
  [a2d](a2d-batch-then-gang-push.md) (a2c with a gang push).
- The tip picture comes from machine-that-sees-and-learns'
  [v1](../../machine-that-sees-and-learns/ideas/v1-watched-nest.md) hover look.
- The carriage can be the same bed-slinger printer as
  [v1b](../../machine-that-sees-and-learns/ideas/v1b-printer-as-stage.md)'s
  stage.

## Major unresolved problems

- **The side-entry jaw law.** For an upright crimp (barrels opening normal to
  the ribbon plane) the jaw's long axis lies along the row. So the fork must
  stand the working conductor out of the plane by the depth of the jaw half
  facing the ribbon (*a*, unmeasured, assumed 6–12 mm) plus 2.7 mm once
  neighbours carry crimps: 8.7–14.7 mm [calc w3 §2]. That sets the copper (root
  radius 9–47 mm on a 20–35 mm free length, tip pull-back 1.3–6.5 mm) and
  leaves each conductor kinked.
- **Stub geometry.** Carrier pitch, pilot-hole position and tab length are not
  dimensioned in any document read [xh-facts §1]. The $4.71 Digi-Key strip
  settles them.
- **The lance.** The contact must be carried into the nest with its lance clear
  of the anvil, and lifted before it is drawn out. That takes an open jaw gap
  of ~4.5–5 mm, unmeasured on the SN-2549.
- **The tab stub length** at the rear-face shear depends on where the
  insulation barrel's rear edge sits relative to the die's rear face.
- **The pull slot needs a neck.** A flat 0.3 mm plate on the box's rear walls
  fits only at transitions of ~0.35–0.5 mm; a stepped plate relaxes that if the
  crimped barrel is narrower than the box (a6, [calc w3 §3]).

## The cycle, one conductor

1. **Fetch a stub.** The pin rises into the bottom stub's pilot hole, and the
   head draws the stub out along a slot shaped to its section. This is the
   OpenPnP drag-feeder idea: the head's own motion does the feeding
   [prior-art §3].
2. **Carry it clear, then set it down.**
   - The tool is open, limited to the opening loading needs, with the flap up.
   - The head holds the contact's floor ≥ 1 mm above the anvil and drives Y
     until the box is past the jaw's front face.
   - Then Z lowers it onto the anvil. The lance never touches steel before the
     housing folds it. The open gap must pass 3.35–4.10 mm of
     contact-plus-lance plus that 1 mm [ith ex §2].
   - The flap drops. The blade lands behind the box.
3. **Hold.** The pusher closes until the force rises a few newtons over the
   empty-tool curve: the first tooth, or a position hold in
   [a1b](a1b-pawl-out.md).
4. **Shear the tab at the rear face.**
   - While the jaws hold, a spring-steel blade on a servo slides down the
     die's rear face and pushes the carrier piece down, away from where the
     wire will be.
   - The die's rear face is the shear's anvil, at 40–100 N [calc §9].
   - The pin has already dropped, and the carrier piece falls to a bin.
   - It is an applicator's drop-shear, with the tab length referenced to the
     die (into-the-housing's branch a2-s in its
     [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md)).
   - It also clears the stub out of the fork's way before the wire arrives.
5. **Look at the tip.** The fork picks conductor *k* out of its slot and holds
   it over a backlight in view of the top camera. Splayed tips go to a twist
   (a small rotary pinch) or to a question.
6. **Present the conductor.** The fork stands *k* out of the ribbon plane by
   *a* + 2.7 mm. The head brings it onto the nest axis, corrected from the
   picture, the strands 1–2 mm behind the insulation barrel's mouth. With the
   stub gone, the fork can come to 3–4 mm behind the rear face.
7. **Feed.**
   - Y creeps forward. The controller drives conductor *k*'s far end and
     watches the others.
   - Amber should come at the insulation barrel's mouth and green at the
     blade. In the tip-plate method there is no green: Y stops at the set
     distance, and the neck frame checks the brush.
   - If a different conductor reads, or amber comes early (the tip is on the
     die's rear face), the cycle stops. In a1b the machine can open and retry.
8. **Crimp.** The pusher runs the full stroke, and the force curve is logged.
9. **Open and look.** The pusher retracts to the opening limiter, and the
   camera takes the side frame, including the window between the barrels.
10. **Lift, then draw out.** The flap lifts, Z raises the crimp 1.0–1.7 mm off
    the anvil, then Y draws it back. Optionally, before the lift, a 2–3 N
    rearward nudge meets the anvil face within the expected travel: lance
    present and sprung.
11. **Proof pull at the pull slot.**
    - The head lays the crimp into a slotted steel plate on a printed block
      beside the tool. The plate bears on the box's rear walls above the
      floor, relieved below for the lance (a6's pull jig).
    - Y pulls to ~20 N on the clamp's load cell, holds and relaxes.
    - The box walls see ~16 MPa [calc w2 §2].
12. **Return.** The fork lays conductor *k* back in its comb slot. The slot is
    long and close-fitting, and straightens the part ahead of the kink. The
    head indexes to the next conductor, or skips the one the loom says is
    trimmed.

**When a conductor is in doubt.** The head holds one ribbon end, so a parked
conductor would stall it. Per-conductor state (as in machine-that-sees-and-learns'
[v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md)) lets the recipe
skip it, finish the others and come back once the person has answered.

Per crimp ~90–100 s, ~80–90 min of machine time per unit, ~4 h at three times
slower [calc §10].

## Neighbours: the working conductor has to stand out, and it keeps a kink

**The side-entry jaw law** [calc w2 §3; calc w3 §2].
- The SN-2549's nest axis is normal to its jaw plane. With the conductor along
  Y, the jaw plane is XZ.
- For the barrels to open normal to the ribbon plane (the insertion
  orientation), the jaws close normal to the ribbon plane. The jaw's long
  axis then lies along the row.
- Every interior neighbour is inside the jaw's extent. So the working
  conductor stands out by the depth of the jaw half facing the ribbon (*a*)
  plus the floor-to-axis height (1.05 mm), plus the crimped neighbour's box
  above its own axis (1.35 mm), plus 0.3 mm clearance: *a* + 2.7 mm.
- The crimped neighbours' boxes lie just ahead of the jaw's front face, in the
  plane of the locator plate and flap. So the locator plate stays inside the
  jaw half's depth on the row's side, or it adds to *a*.
- Turning the tool so its jaws close across the row makes the stand-out only
  the nest-to-tip distance. But then every crimp is rolled 90° and no housing
  can be pushed onto the row ([a3](a3-tool-travels-to-ribbon.md)).

**What the stand-out does to the copper.**
- Annealed 0.08 mm strands yield below a bend radius of ~67–78 mm [digest; ith
  ex §6].
- Standing 8.7–14.7 mm out on a 20–35 mm free length gives a root radius of
  9–47 mm. The comb holds 8–10 mm of each conductor, so the free length is
  shorter than the 25–35 mm split. The conductor comes back with a kink.
- While it is out, the tip pulls back 1.3–6.5 mm. The crimp itself is right,
  because the feed happens in that state.
- Back in the comb, the part ahead of the comb points wherever the kink
  leaves it.

**Repairs:**
- **Comb slots ≥ 8–10 mm long and close-fitting,** so the part ahead of the
  kink runs straight.
- **For any insertion of the whole row:** a front plate that pushes every
  nose back to one line ~2 mm behind nominal, the extra length going into the
  split as slack, and then a rear clamp 1–2 mm behind each insulation crimp.
  This is [a2d](a2d-batch-then-gang-push.md)'s station.
- **For a person inserting one at a time,** the kink matters little.

**What it leaves uncertain:** how far the silicone jacket springs a set
60-strand bundle back, and *a* itself.

Derek's test: offset one split conductor 12 mm for a minute, release it, and
photograph it.

## The stub as handle and reference

- **What a stub is.** A side-feed chain contact hangs from its carrier by a
  tab at the rear of the insulation barrel [xh-facts §1]. One pitch of
  carrier (~7.1 mm on Würth's analog drawing [change-the-question]), with its
  Ø1.5 mm pilot hole, is a flat handle.
- **What it does:**
  - a pin can hold it;
  - it lies in the floor plane below the conductor's path;
  - it locates the contact the way an applicator does, by the strip's own
    hole [prior-art §3].
- **Accuracy.** A Ø1.45 pin in a Ø1.50 hole locates to ±0.025 mm. The
  hole-to-barrel distance is fixed by the stamping, assumed ±0.05
  [calc §7]. The Accusize pin-gauge set includes 0.057 in = 1.448 mm ($45.58
  [prime: B00JOLCSF6]).
- **Where stubs come from:**
  - **by hand in a batch:** snip cut strip with the KATA cutters between
    contacts, 53 a unit, onto a printed tray that orients them;
  - **a snipping station:** the pin drags the strip through a guide one pitch
    at a time, and a servo shear snips at the carrier's slot.
- **Strip is sold cut, not on Prime:**
  - Digi-Key: 100, 500 and 1,000 lots at $0.0471–0.0401;
  - LCSC: C140573 at $0.0100 per 1,000 [xh-facts §6].

**Variant: the strip itself, off the jaw tip.** If the usable nest is the one
nearest the jaw's tip, a whole strip can lie behind the rear face with the next
contact beyond the tip. The pin feeds one pitch per crimp. This removes the
snipping and the magazine, if the nest-to-tip distance is under one strip
pitch.

## Parts

**Printed:**
- stub magazine and drag slot;
- head: comb, fork arm, pin guide, clamp;
- tip plate holder, backlight window, pull slot block, shear guide;
- camera hoods.

**Carriage, two routes:**
- **Purpose-built:** three short linear rails with NEMA 17s and GT2 belts or
  Tr8 screws on the bench's ESP32 stack. MGN12 300 mm rail with carriage
  $20.49 [prime: B07ZVFFXQZ]; GT2 20T pulleys $5.99 for five [prime:
  B07CXR7SFL].
- **A bed-slinger printer frame:** Creality Ender-3 V3 SE, $219.00, 2,112
  ratings, 500+ bought in the past month [prime: B0F8J78BN1].
  - Its bed carries a1's cradle along Y, and its head carries the ribbon head
    in X and Z.
  - The crimp force never enters the printer.
  - A 20–25 N pull is within a NEMA 17 on a 20T GT2 pulley (~60 N at
    0.4 N·m) [calc, assumption on motor].

**Servos, four:** flap, fork, pin, shear. DS3218MG 20 kg·cm, $14.99, 5,306
ratings [prime: B076CNKQX4].

**On hand:** the ELP camera, KATA micro flush cutters, the ESP32 stack.

**Load cell:** a 5 kg bar pair with HX711 for the proof pull, $9.99 [prime:
B09K7G3477].

## Tried against it

- **"Strands catch on the insulation-barrel wing tips."** At hold, the
  insulation wings are partly curled by the punch into a converging mouth
  [assumption from how the punch forms the wings, xh-facts §4]. With the stub
  sheared off at step 4, a printed funnel on the rear face has room. Amber
  arriving early says the tip hit steel instead.
- **"Unsupported conductor between fork and jaw."** With the stub gone the
  fork comes to 3–4 mm behind the rear face. The free conductor at a few
  newtons of drag stays under the ~6 N it buckles at over 5 mm [digest].
- **"The proof pull loads the flap arm or the lance."** It is taken at the pull
  slot, relieved for the lance, on the box's rear walls.
- **"Cutting after the crimp risks the crimp."** The cut comes before the
  wire, at hold. The shear pushes the carrier down, away from the barrels, on
  the die's own face.
- **"The copper keeps the offset."** It does (above). The comb, and for gang
  insertion a2d's front plate and rear clamp, are what square it.

## Rests on

- **[assumption]** The usable nest's position and the jaw's extent around it.
- **[estimate]** The carrier stub's dimensions: pitch, hole and tab.
- **[assumption]** The die's rear face is flat and square enough to shear
  against, with room for a blade beside the stub.
- **[assumption]** The open jaw passes ~4.5–5 mm at the opening the limiter
  allows.
- **[assumption]** A NEMA 17 on a printer frame's Y belt pulls 20–25 N without
  skipping. The controller sees skips as a force-position mismatch.
- **[assumption]** A 20–25 N proof pull does not damage a good crimp. JST
  publishes no proof pull; this is a screening load chosen below its minimum.

Measurements that bear on it:
- the nest positions on the jaw and the depth of the jaw half below the
  usable nest, with a caliper;
- one 100-piece Digi-Key strip, measured by caliper or scanner (it also
  answers xh-facts Unresolved 2);
- the offset-and-release photo of one conductor;
- the flush cutters and a rear-face shear on a strip tab under the ELP.

---

Citation keys: **[calc §n]** is [`../calc/hand_tool_press.out.txt`](../calc/hand_tool_press.out.txt);
**[calc w2 §n]** is [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
