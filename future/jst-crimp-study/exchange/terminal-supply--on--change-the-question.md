# terminal-supply on change-the-question

terminal-supply reads the procedure from the contact's side: how the contact
arrives (bag, strip, reel, on a post, in a cavity) decides what locates it,
what holds it, what can cut it free and who has to touch it. This file reads
[change-the-question](../explorers/change-the-question/summary.md)'s six
arrangements that way: its idea files, its
[notebook](../explorers/change-the-question/notebook.md), its calc outputs
([ctq](../explorers/change-the-question/calc/ctq.out.txt),
[order_search](../explorers/change-the-question/calc/order_search.out.txt))
and its sketch labels.

My numbers for this file are **[calc otq §n]** in
[`../explorers/terminal-supply/calc/on_change_the_question.py`](../explorers/terminal-supply/calc/on_change_the_question.py),
output in
[`on_change_the_question.out.txt`](../explorers/terminal-supply/calc/on_change_the_question.out.txt).
My wave-1 numbers are [ts §n]
([terminal_supply.out.txt](../explorers/terminal-supply/calc/terminal_supply.out.txt));
theirs are [ctq §n].

Where change-the-question hands something back to the person, it is almost
always the contact: "loading loose contacts into pallets" (c1, c1b), "loading
contacts" (c3), "spool changes" with the housings and contacts implied (c5).
Most of what follows is about taking those back, and about the places where a
printed pocket stands in for a reference the contact already carries.

---

## A fact both of us lean on: the Würth contact is not XH-sized

I opened both Würth drawings on 2026-09-28
([646 101 137 22](https://www.we-online.com/components/products/datasheet/64610113722.pdf),
1,000-piece reel, which I cited in wave 1;
[646 001 137 22](https://www.we-online.com/components/products/datasheet/64600113722.pdf),
10,000-piece reel, which c4 cites). They are the same contact on two reel
sizes, so we agree on the part. Section C-C of the drawing gives the box as
**1.45 × 2.00 mm** [mfr-an]. XH's box is 1.85–1.95 × 2.2–2.4 mm, so the Würth
box is 0.40–0.50 mm narrower and 0.20–0.40 mm lower [calc otq §2]. The same
drawing gives:

- contact length 7.0 mm;
- tab 0.80 mm;
- pilot-hole centre 2.30 mm behind the contact's rear;
- lance 0.65 ±0.1 mm proud on the floor side, its tip 2.30 mm behind the
  front.

What follows:
- **c4's table row** for Würth as an "XH-compatible crimp contact" with
  narrower wings describes a contact with a smaller box. It would sit loose in
  an XHP cavity. It is most likely the analog of a smaller 2.5 mm family
  [assumption: JST EH-class, not checked].
- **[ctq §3]'s "Würth 0.20 mm gap at 2.5 mm"** is therefore a property of a
  different connector, not an option for XH.
- **7.10 mm**, the only public carrier pitch either of us has, belongs to
  that smaller contact. JST's SXH pitch is still unknown. Every strip-based
  combination below carries that uncertainty until one Digi-Key 100-piece
  strip is under a caliper.

---

## c1 — half-rows

[c1](../explorers/change-the-question/ideas/c1-half-rows.md)

### Break 1: the punch is fixed on the frame, but the ram carriage steps along the row

- **The conflict.** Step 5 has "a carriage with a vertical ram" under the
  pallet that "steps 3.4 mm to the next carrier", meeting "a fixed punch
  mounted on the frame". The force path is given as frame → fixed punch →
  contact → anvil → ram → screw → frame.
  - One fixed punch sits over one carrier position only. If the carriage
    steps and the pallet does not, the ram rises under carriers 2…n where no
    punch is.
  - If instead the punch rides the carriage, the loop closes through the
    carriage's rail. The hard stop that sets crimp height then sits outside a
    short steel loop, and rail deflection at 3 kN enters crimp height. This is
    the "where the stop sits" disagreement in the digest.
- **Repair (a branch).** Keep ram, punch and stop in one fixed C-frame, a
  press. Put the pallet and the web clamp on one slide that steps 3.4 mm
  under it.
  - The pallet is already referenced to "a datum stop on the clamp frame", so
    clamp and pallet moving together keeps every conductor-to-contact
    relation.
  - The station then becomes the same object as my
    [a2](../explorers/terminal-supply/ideas/a2-strip-indexer.md) station: an
    OTP XH knife set in a guided holder, driven by an arbor press on a lead
    screw, with the stop in the die block. It is also force-and-form's f2/f2b
    frame. The pallet replaces the strip as what presents the contact.
- **What it leaves.** A slide carrying a clamped ribbon with its tail, stepped
  under a press. For the long looms that tail is up to 600 mm, or a spool in
  c5.

### Break 2: between the pushes, row A's wires lie across row B's working zone

- **The conflict.** After push 1, "the holder lifts the housing, with half-row
  A in it, out of the way". Row B is then laid (presser comb from above),
  lifted into the fixed punch above, crimped (ram from below) and spread.
  - The housing is tethered: the free conductor between web root and housing
    rear face is only ~6–9 mm at a 12 mm split, ~9–12 mm at 15 mm and
    ~14–17 mm at 20 mm [calc otq §10].
  - The housing sits in front of the pallet, on the box side. Row A's wires
    run from web-root positions *between* row B's conductors forward to the
    housing, so they cross over or under pallet B's whole length.
  - If they run above, the presser comb's teeth, which go exactly in the gaps
    between row-B conductors, meet them near the root, and the punch meets
    them over the contacts. If they run below, the ram carriage meets them.
- **Consequence.** As written, step 8 cannot lay or crimp row B while row A is
  already in the housing.
- **Repair A: crimp both rows before inserting either.**
  1. Row A is crimped in pallet A. Pallet A, now carrying rigid contacts,
     parks down and back under the clamp nose. That is the same fold c1
     already gives plane B's bare conductors.
  2. Row B comes up and is laid and crimped in pallet B in the working plane.
  3. Pallet B rises above the plane while pallet A returns into it. Their
     wires start 1.7 mm apart at the root and diverge in opposite directions,
     so they do not cross.
  4. Pallet A spreads and pushes row A into cavities 1, 3, 5, then drops away.
     Its pockets are open at the top, so the wires lift out of them.
  5. Pallet B comes down between row A's wires at 5.0 mm (c1's 1.9 mm gaps)
     and pushes.

  The housing never moves except by 2.5 mm between pushes.
- **Repair B: flip.** The web clamp rotates 180° about the ribbon axis
  between rows. Row A and its housing go to the far side of the plane, away
  from the tools, and the tools stay single-sided.
- **What either leaves.**
  - In Repair A, pallet B descends between row-A wires that are still
    converging from 5.0 to 3.4 mm behind it. For T4 that S-bend is 4.5 mm and
    0.8 mm, harmless. For J1 it is 18 mm and 3.2 mm, longer than a pallet, so
    pallet B's carriers would meet the bend [ctq §2b].
  - Repair A needs two pallets. c1's one-pallet branch 5 is incompatible with
    it.

### Break 3: open clone wings make the lift a ±0.07 mm guidance problem

- **The conflict.** At 3.4 mm the gap between open wing tips is 0.15 mm for
  worst-case clone wings (3.25 mm with tolerance) and 0.60 mm at nominal
  2.8 mm [calc otq §4].
  - As carrier k rises 3–4 mm past its neighbours, its flared wing tips slide
    past theirs. Any lateral wander over ±0.07 mm (worst case) catches a wing
    and bends one or both.
  - The carrier is a printed part that also slides on a cam plate for the
    spread. So its vertical guide is a printed slot inside a moving pallet.
- **Repair: tack first, then crimp in the row, with no lift.** This combines
  c1b with c1.
  - A tacked insulation barrel is ~2.0–2.2 mm across [estimate], and the
    open conductor wings are ≤2.15 mm. So the half-room beside a neighbour at
    3.4 mm rises from 1.67 mm to 2.20–2.23 mm.
  - c1's own punch estimate is 1.75–1.9 mm half-width for the conductor
    section and ~1.9–2.0 mm for the insulation section [calc otq §4; ctq §3].
    Both fit beside tacked neighbours with 0.2–0.4 mm to spare. The lift, its
    11–19° conductor bend and the wing-clash risk all go.
  - If the lift is kept anyway, tacked neighbours give 1.2 mm between tips,
    so ±0.6 mm guidance.
- **What it leaves.**
  - The tack's grip (c1b, below).
  - Whether the final die re-forms a tacked insulation barrel cleanly (c1b
    tried 2).
  - The 2.0–2.2 mm tacked width is an estimate. One tacked kit contact under
    the caliper settles it.

### Break 4: bellmouth runs through five printed links

- **The conflict.** Bellmouth needs the contact axially within about
  ±0.1 mm of the punch [xh-facts §5; ts §2]. c1's axial chain is:
  1. punch to frame;
  2. frame to pallet slide;
  3. pallet to carrier guide (a printed carrier that also lifts and spreads);
  4. carrier pocket rear shoulder (printed);
  5. box rear to conductor-barrel rear (the part).

  That is ±0.09–0.18 mm RSS and ±0.19–0.36 mm worst case [calc otq §5,
  estimated link tolerances].
- **Repair: take the reference from the contact's own face at the station.**
  - The pocket is open at the front for insertion. So the station can carry
    a hardened front stop that the box's mating face meets, with the carrier
    sprung lightly forward in its pocket.
  - The chain becomes stop → punch, both on one steel block, plus the part's
    own box-front-to-barrel distance: ±0.05–0.10 mm RSS, ±0.06–0.12 mm worst
    case.
  - A camera re-teach per lot removes the lot offset, as in my a2's re-teach
    per reel.
  - This is the transferable I set out in wave 1: reference the barrels from
    a face of the contact, not through a handle whose length varies.
- **What it leaves.** Whether a sprung carrier can yield forward ~0.2 mm in a
  pocket that must also hold the box square. And whether the box front,
  a folded sheet edge, is flat enough to stop against. One kit contact under
  the ELP camera settles the second.

### Break 5: the pocket has to be drawn around the contact's lance

The contact has features the pocket description does not yet show [mfr-an;
xh-facts §1]:
- **The lance.** It stands 0.65–0.9 mm proud of the floor, and c1's pallet
  holds contacts barrels-up, so it points down. Its tip is 2.3–2.6 mm behind
  the box front, facing rearward.
  - A pocket floor without a slot tilts the contact on its lance.
  - A slot that ends behind the lance tip turns the lance into the pull-test
    stop. The ~20 N proof pull would then load the lance at around its own
    design retention, which is unpublished [xh-facts §3] and could bend it so
    it no longer latches in the housing.
  - Repair: a lance slot ~1.1 mm deep, running out through the open front, so
    the proof pull bears only on the box's rear shoulder.
- **The anvil's front edge.** The lance tip is only a few tenths of a
  millimetre ahead of the conductor barrel. An anvil blade rising through the
  carrier window with poor axial registration can catch it. Break 4's front
  stop takes care of this too.
- **The sprung shoulders.** Step 5 lifts the carrier on shoulders that "go
  slack once the anvil bears".
  - If the pocket floor under the box ends up higher than the anvil top, the
    punch pushes the barrels down onto the anvil while the box is held up.
    That is a bend at the box-to-barrel transition, the "bend-down" the MKS-L
    manual traces to terminal position on the anvil [ts, MKS-L §7-8].
  - Repair: rigid shoulders, with the pocket floor set 0.1–0.2 mm *below* the
    anvil top. The anvil alone then defines the contact's plane, and the box
    overhangs, as in an applicator.
- **The housing's face.** If the lance goes toward the window face
  [assumption, xh-facts §3], a barrels-up pallet needs the housing held
  windows-down. c1's holder should say so. One kit housing and contact
  settles it.

### What c1 hands back that the contact's arrival could take

- **Loading pockets.** This is the step Derek wants off his hands: placing the
  metal bit. c1 hands it back as 53 tweezer placements per unit, ~5–9 min
  [calc otq §1, estimate], into 3.4 mm pockets where open wings clear by
  0.15–0.94 mm. The machine then calls once per housing (10 per unit), or 20
  with branch 5. The combination below (C1) takes it back.
- **Housings in.** One per cycle, and a stick magazine takes it (C2).
- **J2's and J7's empty pockets.** A loader skips them, so the pallet loaded in
  loom order is itself the build list. That is my a4 transferable.
- **J4 and J7 crossings.** From my view, a crossing done *after* the crimp is
  a swap of two rigid parts, not a re-route of two floppy strands.
  - c1's cam pallet cannot swap two carriers.
  - A pick-and-place that holds crimped contacts by the box, or by a carrier
    tag (my [a2b](../explorers/terminal-supply/ideas/a2b-carrier-as-handle.md)),
    could lift one over the other between spread and push.
  - For J7's single crossing (GND over CLO in row A) that is one move. It is
    a branch with its own problems (a gripper at 5.0 mm pitch; the crossed
    wires must lie over or under each other behind the housing) and is not
    developed here.

---

## c1b — tack first

[c1b](../explorers/change-the-question/ideas/c1b-tack-first.md)

### Break 1: the tack comb's teeth go to a knife edge with worst-case clone wings

- **The conflict.** Each tack profile has to catch the open wing tips in its
  flared mouth, so the mouth is as wide as the open wings. At 3.4 mm the
  steel left between neighbouring mouths is:
  - 0.15 mm for 3.25 mm worst-case clone wings;
  - 0.6 mm at nominal;
  - 0.94 mm at 2.46 mm [calc otq §3].

  A 1.2–1.5 mm laser-cut plate cannot hold a 0.15 mm tooth tip: it is about
  one kerf wide.
- **Repair: tack in two passes.** Odd profiles first, then shift the comb
  3.4 mm and do the even ones.
  - The profiles are then 6.8 mm apart, so the teeth are ≥3.5 mm wide.
  - The force per pass halves.
  - With contacts narrower than the worst clone, one pass is enough.
- **What it leaves.** The first pass closes half the barrels. The second pass
  works beside neighbours already tacked, which is exactly the geometry of
  c1 Break 3's repair, and is easier.

### Break 2: the tack's grip is unknown across three orders of magnitude, and the load it must carry decides the downstream

- **The range.** A loose tack squeezes a 0.49 mm silicone wall. Slide grip
  spans ~0.1 N to ~50 N depending on:
  - silicone modulus (1–10 MPa);
  - confinement;
  - squeeze (0.05–0.2 mm);
  - barrel length and friction.

  A middle case gives ~2 N [calc otq §7]. That is c1b's "measure it in an
  afternoon" question, now with the bands that matter.
- **What it has to resist, from my view.**
  - Pushing the flag's box into a keyed slot: 0.1–0.5 N [estimate].
  - Pushing the box onto a 0.64 mm post: 0.2–1.6 N [ts §7].

  So a tack below ~2 N can still go into a slot-type locator. It may slip on
  a post.
- **The branch this gives.** Locate the heavy crimp by a box slot, not a post
  (combination C4). The tack then only has to keep axial position against
  slot friction. Roll is set by the slot on the box.

### Break 3: "put the flag in the SN-2549's nest and squeeze" still needs a stop

- **Box first through the nest.** A flag cannot enter the nest from the front
  face: the loom trails behind it. It enters box-first from the wire side,
  through the insulation section and then the conductor section, with the
  jaws open.
  - Across the jaw opening the box plus lance is 2.8–3.25 mm. That is
    change-the-question's own figure in its f1 critique.
  - So it needs the tool fully open, not "one click", and the contact is not
    captive.
- **Nothing stops the contact axially.** The person pushes until it "looks
  right", and the ±0.1 mm bellmouth window is back in their eye. c1b names
  this ("the locator question moves to the heavy crimp").
- **Repair from my view: a clip on the jaw's front face** with a slot keyed
  to the box (2.0 mm, with the lance notch) and a stop for the box's mating
  face.
  - It is my [a2c](../explorers/terminal-supply/ideas/a2c-strip-locator-for-hand-tool.md)
    clip with its pilot pin replaced by a box key. A flag has no pilot hole.
  - The flag goes in box-first until the box face touches the stop, then the
    person squeezes.
  - Axial, lateral and roll then come from the box, as JST's WC-110 flap does
    it [mfr S6].
- **What it leaves.**
  - Whether the SN-2549's full-open gap passes box and lance (a pin gauge).
  - Whether a clip on the front face leaves the jaws' travel free.

### What c1b opens beyond itself

Tack-first works for any arrangement whose station struggles with force, not
only for half-rows. See C5: my hanging-pocket crimp a3b, whose unresolved
problem is a 3 kN horizontal frame.

---

## c2 — buy the crimp

[c2](../explorers/change-the-question/ideas/c2-buy-the-crimp.md)

- **The reference crimp carries more than crimp height.**
  - The ASXHSXH22K lead's contacts came off JST's reel through JST's
    applicator. Their cut-off tab stub is JST's own stub.
  - That stub is the target for any severing in this study: my a2 drop-shear,
    my a2c bend-off, and the pallet loader in C1, which can place its blade to
    leave 0.20–0.30 mm [calc otq §3].
  - The lead is also the one genuine crimped contact on which to measure XHP
    insertion force and the latch click (xh-facts Unresolved 4) before any
    machine exists.
- **The height transfer is rougher than the area ratio suggests.**
  - UL1007 22 AWG hookup wire is commonly 7- or 17/19-strand [assumption; the
    lead's wire is not stated]. The ribbon is 60 × 0.08 mm.
  - A coarse-strand bundle compacts differently from a fine one at the same
    area, so c2's 0.02–0.04 mm correction is a floor on the uncertainty, not
    the whole of it.
  - What transfers cleanly: crimp width, bellmouth, brush, window, stub, and
    the pull at 39.2 N as a pass line.
- **The far end of "buy".** A custom harness house crimping XH on a
  customer's ribbon would buy the whole XH end, J2's empty cavity and the J4
  and J7 crossings included [assumption: not sourced; no search this wave]. It
  meets Derek's low-lead-time value badly: quote-and-wait, weeks by post. I
  record it as the endpoint of c2's axis, not as a direction.
- **Variant (c), single pre-crimped wires, is the worst supply form for a
  machine.** Loose flying leads in a bag tangle, and each contact's roll about
  its wire is random. A machine inserting them has to singulate floppy parts,
  which is what Sogang's failures came from [prior-art]. That fits c2's own
  reading that (c) reduces the XH job to hand insertion.

---

## c3 — fold and solder

[c3](../explorers/change-the-question/ideas/c3-fold-and-solder.md)

### Break: a printed folding arch is gouged by the wing edges

- **The numbers.** The first contact of a 0.2 mm wing edge (radius
  0.05–0.1 mm) on the arch is a line contact.
  - At 8 N per wing, the plastic-hinge force c3 computes, spread over a
    1.3 mm barrel, peak contact pressure is ~220–310 MPa on PETG and
    ~340–490 MPa on PET-CF.
  - At 40 N it is 485–770 MPa.
  - Against yields of ~48 and ~80 MPa [calc otq §8, Hertz line contact,
    estimate].
- **Consequence.** Every fold dents the profile where the wing tips first
  slide. Over ~3,200 folds the arch's shape wears, and fold height drifts with
  it.
- **Repair.** The profile is steel: laser-cut sheet, the same object as c1b's
  tack comb. c3 already notes the two share hardware, and this makes them the
  same part. Printed parts can carry the steel profile, not be it.

### Transfer: fold and solder on the strip

- **Heat.** The tab neck (0.6–1.0 mm wide, 0.2 mm thick, 0.8 mm long) loses
  only ~1.7–4 W at a 230 K rise [calc otq §8]. That is a thermal choke against
  a 60–70 W iron, so a contact can be folded and soldered while still on its
  carrier, then drop-sheared. The strip gives c3 location, orientation and no
  loose loading.
- **Flux.** The strip can be tilted box-up as a whole. Flux and solder then
  run rearward, toward the carrier and away from the box, which is c3's
  worry 3.
- **What it leaves.** Rearward is also toward the insulation. Box-up tilt
  trades flux in the box for wicking under the silicone (c3's worry 2), and
  only a sectioned sample shows which one is worse.

---

## c4 — parts that mate the wafer

[c4](../explorers/change-the-question/ideas/c4-parts-that-mate-the-wafer.md)

- **The Würth row** is not an XH contact (the section at the top of this
  file). c4's own unresolved item, "whether WR-WTB 2.50 mates XH", now has a
  likely answer from its drawing: its box is too small to be held square by an
  XHP cavity [mfr-an; the cavity width itself is not public].
- **One measurement flips two families in opposite directions.** Open
  insulation-wing width:
  - **Narrow wings**, JST's 1.95 mm envelope if the real part fits it, help
    c1's 3.4 mm pallets, c1b's single-pass tack and the preloaded-housing
    ideas.
  - **Wide wings**, the clones' 2.46–3.25 mm, are what my hanging rail
    (a3, a3b) hangs contacts by. JST's envelope may mean genuine contacts have
    no head to hang from [ts §6].

  So the one caliper reading of a kit contact and a BXH is not "which contact
  is better". It decides which arrangements each contact suits. c4's table
  could carry that column.
- **Supply form as a machine choice.** c4 chooses contacts by shape. The same
  contact also arrives as:
  - a loose bag (BXH);
  - a 100/500/1,000 cut strip (Digi-Key SXH);
  - an 8,000 reel;
  - a clone reel.

  Each sets a refill interval of 1.9, 9.4, 18.9, 151 or 170 units [ts §1] and
  decides what orients the contact: a person, a rail, or the carrier. That is
  the axis my wave 1 explored, and it belongs in c4's table beside shape.
- **The strip cannot gang-load c1's pallet either.**
  - 7.10 mm is 0.30 mm off two half-row pitches (6.8 mm), just as it is
    0.40 mm off three housing pitches [ctq §7].
  - A strip loads a pallet one pocket per index, which C1 below does.
  - If SXH's real pitch turns out to be 6.8 mm, quarter-rows could sit on the
    strip directly. The Digi-Key strip settles that too.

---

## c5 — ends as stock

[c5](../explorers/change-the-question/ideas/c5-ends-as-stock.md)

### Break: an unattended spool run has to be supplied with contacts and housings for the whole run

- **The conflict.** c5 "relies on some termination arrangement working
  unattended for a whole spool". The arrangement it names first, c1, hands
  back both parts on every cycle: pockets loaded by hand, and "drops an empty
  housing in the holder".
  - A long T4 run is 21 ends, 84 contacts and 21 XHP-4 housings.
  - A short run is 38 ends, 152 contacts and 38 housings [calc otq §9].

  Without supply automation, c5's run is attended at every end, and the
  bin-of-ends idea buys scheduling but not the person's time.
- **Repair (C2 below).** Contacts from strip into c1's pallet, and housings
  from a stick magazine: 120–163 mm tall for a long run, 217–294 mm for a
  short one [calc otq §9].
  - A long run's 84 contacts fit inside one 100-piece strip with 16 to spare,
    so **the spool change and the strip change fall on the same visit**.
  - A short run needs 1.5 strips: a 500-piece strip, a reel, or an SMT-style
    splice of two strips (my a2 tried 6).
- **What it leaves.**
  - The kit housings come mixed by size in CQRobot bags. A T4 run's 21–38
    XHP-4 is probably more than one kit's 4-ways [assumption; kit composition
    is a wave-1 question]. XHP-4 is $0.049–0.058 from LCSC or Digi-Key in
    quantity [xh-facts §6].
  - Loose kit contacts can feed a T4 run only through my a3 rail (C5), since
    84–152 have to arrive in one orientation.

### What c5 does for supply

- **Continuous runs** are what a reel wants. 8,000 contacts is ~95 long T4
  runs.
- **One end type per run** removes loom-order loading. A T4 run has no gaps
  and no crossings.
- **The housing-as-fixture ideas shrink.** My
  [a4b](../explorers/terminal-supply/ideas/a4b-through-cavity-post.md) and
  [a5](../explorers/terminal-supply/ideas/a5-housing-as-fixture.md) only
  need an XHP-4 nest with three fixed 2.5 mm steps, no skip and no pair.

---

## Transfers from my view

1. **Sever before the wire arrives.** The five listed steps leave out "cut
   the contact from its carrier", which strip supply adds. It can sit before
   the crimp or after it, and the two orders are different machines. This is
   a change-the-question move in its own right.
   - **After the crimp** (my a2): the carrier holds the contact through the
     crimp, but the wire lies over the tab, so only a drop-shear works and
     only the neighbours' pilot holes are free.
   - **Before the wire** (C1): every pilot hole is free, the station's own
     included. A blade from above cuts at a chosen line, so the stub meets JST's
     1.0–1.5 × stock rule by blade position alone [calc otq §3]. But the
     contact is then loose, and the next fixture (a pocket) must keep its
     orientation.
2. **The contact's faces as references.** The box's mating face, its rear
   shoulder, the barrel floor on the anvil, and the lance slot. c1's pocket
   and c1b's heavy crimp both improve when the station stops on the box face
   rather than on a printed shoulder (c1 Break 4, c1b Break 3).
3. **Pilot pins through loaded holes.** Where a conductor already lies over a
   pilot hole, a tapered pin that stops flush with the carrier's top face
   still centres on the hole's lower edge [calc otq §6]. That makes a
   half-row laid on consecutive strip contacts locatable (C3).
4. **Loom-order magazines.** A loader that leaves J2's cavity-3 pocket and
   J7's trimmed pocket empty makes the loaded pallet the build list.
5. **Load at the wide pitch.** c1's cam plate runs 3.4 ↔ 5.0 mm. Loading at
   5.0 gives 1.75–2.54 mm between open wing tips against 0.15–0.94 at 3.4
   [calc otq §3]. The pallet closes to 3.4 for the lay and reopens for the
   push.

---

## Combinations

### C1 — c1's pallet, loaded from strip

- **What it is.** A strip station beside the pallet's load position:
  1. It pins the strip through the station's own hole and its neighbours.
  2. It shears the tab 0.2–0.3 mm behind the contact's rear.
  3. It pushes the freed contact straight down through a contact-shaped
     window in a die plate into pocket k, barrels up, box forward.

  The cam plate holds the pallet at 5.0 mm while it loads, then closes to
  3.4.
- **What each side contributes.**
  - c1: one-motion placement of a half-row, the pitch change on rigid
    handles, and the two-push fill.
  - Mine: orientation carried from the reel to the pocket, no fine handling
    by the person, stub control, and loom-order skips.
- **Figures.** 10–15 s per contact, so 40–60 s for a T4 end, overlapped with
  crimping [calc otq §3]. Contacts by hand go from 53 to 0 per unit. Calls
  stay at one per housing (the ribbon load) [calc otq §1].
- **What it leaves.**
  - Whether a 0.043 g contact pushed 2–3 mm down a window lands square in a
    printed pocket.
  - The real SXH pitch and tab.
  - c1's own breaks above.

### C2 — c5 + C1 + a housing stick: one visit per T4 spool

- **What it is.** The 4P spool, a 100-piece strip and 21 XHP-4 housings are
  loaded together, and the machine makes 21 long T4 ends in ~3–4 h
  unattended [calc otq §9, estimate at 8–12 min per end].
- **Calls per unit.** ~5.2: one-fifth of a visit for the five T4 ends, plus
  one each for the five other housings if they stay attended [calc otq §1].
  c1 as written is 10 or 20.
- **What each side contributes.**
  - c5: the scope (T4 only), the spool feed and cut, and test-before-loom.
  - c1: the termination.
  - Mine: contact and housing supply sized to the run.
- **What it leaves.** Everything c1 and c5 leave, plus the housing stick's
  escapement into the holder.

### C3 — c1b's tack on the strip itself: no pockets at all

- **What it is.**
  1. A half-row is fanned from 3.4 mm to the strip's 7.1 mm. For T4's pairs
     that is one wedge dropped between the two conductors: 1.85 mm each way
     over ~5 mm, where a whole 4P needs 22 mm [calc otq §6].
  2. The pair is laid onto two consecutive strip contacts.
  3. c1b's tack comb, now at 7.1 mm with teeth ~3.9 mm or wider, tacks both.
  4. The strip and web clamp step together under my a2 station, which
     crimps each contact and drop-shears it.
  5. Pins locate through the free holes beyond the half-row, or flush in the
     loaded ones.
- **What each side contributes.**
  - c1b: the light gang tack that pins wire to contact before anything moves.
  - c1: the two-plane split that makes 3.4 mm in-plane gaps.
  - Mine: the carrier as pallet and datum, and the drop-shear.
- **What it leaves.**
  - The crimped flags come off the strip at 7.1 mm. Insertion then needs
    them converged to 5.0 mm (c1's cam pallet run in reverse) or a
    carrier-tag handle (my a2b).
  - Rows of 3–5 need 10–20 mm of fan.
  - Pitch unknown, as always.

### C4 — c1b flags and a box-keyed locator at the heavy crimp

- **What it is.** The flag goes box-first into a slot keyed to the box and
  lance, with a stop for the box's mating face. The slot is:
  - on a clip on the SN-2549 (my a2c, re-keyed); or
  - on the anvil block of any single-die station.
- **What each side contributes.**
  - c1b: contact-to-wire position fixed in advance.
  - Mine: contact-to-die position from the box, as WC-110 does.
- **What it leaves.** The tack's grip must exceed slot friction, ~0.5 N
  [calc otq §7]. And the SN-2549's full-open gap (c1b Break 3).

### C5 — c1b's tack in my hanging pocket: loose kit contacts without a 3 kN horizontal frame

- **What it is.** My
  [a3b](../explorers/terminal-supply/ideas/a3b-crimp-where-it-hangs.md)
  crimps a kit contact hanging box-down in a steel pocket at the end of the
  rail. Its main unresolved problem is a horizontal frame stiff enough for
  ~3 kN.
  - If that station only *tacks* the insulation barrel, it needs
    33–132 N [ctq §5]: a servo on a lever.
  - The flag leaves on its conductor for C4's heavy crimp.
- **What each side contributes.**
  - c1b: splitting the joint at the insulation barrel.
  - Mine: loose kit contacts singulated and oriented by their wings, with no
    person placing them.
- **What it leaves.**
  - Everything a3 leaves about which contacts have a head.
  - The tack's grip.
  - The ribbon held vertically.

### C6 — tack, then crimp in the row (inside c1 and c1b)

This one is change-the-question's own, surfaced by wing widths: c1 Break 3's
repair. The lift is no longer needed [calc otq §4]. c1b's contribution is the
narrowed neighbours; c1's is the in-row crimp with the housing push after it.

### C7 — fold and solder on the strip

See c3's transfer above. c3 contributes the light fold and the solder joint;
mine contributes the carrier's location and a thermal choke of ~2–4 W. The
flux-versus-wicking trade is left open.

---

## What change-the-question has not yet seen

- **Sever as a sixth step that can move.** Their reorder of splay to after the
  crimp is the same kind of move as moving sever to before the wire. They have
  not used it (Transfer 1).
- **The contact's own references.** In c1, c1b and c3 every contact reference
  runs through a printed pocket or nest. The box face, the lance and the
  barrel floor are free references that cut the bellmouth chain roughly in
  half (c1 Break 4).
- **The lance** in pocket design and pull tests (c1 Break 5).
- **Housing supply**, for c1 per cycle and for c5 per run (c5 Break).
- **The arithmetic of refills against runs.** A 100-piece strip matches one
  long T4 spool run (C2).
- **Which contacts each arrangement suits.** Wing width decides it, and it
  cuts in opposite directions for pallets and for rails (c4).
- **The Würth part's box.** Its drawing shows a smaller contact (top of file).

---

## Where their work changes my own ideas (for my revision)

- **a2 (strip indexer).**
  - c1's two-plane split is the upstream my ribbon carriage lacked. It gives
    1.7 mm gaps between in-plane conductors, so the carriage presents plane
    A's conductors and then plane B's, instead of bending "unused conductors
    up" one at a time.
  - c2's reference lead gives my drop-shear its stub target.
- **a2b "comb" sub-variant.** With half-rows, the split needed to meet the
  strip falls from 22 to ~5 mm for T4, and from 30 to ~10 mm for a 5P (half-rows of 3 and 2)
  [calc otq §6]. The comb goes from a stretch to plausible for T4. C3 is its
  new form.
- **a2c (strip locator clip).** It gains a box-keyed version for tacked flags
  and loose contacts (C4). The clip no longer depends on strip supply.
- **a3 / a3b (hanging rail and pocket).** c1b's tack removes a3b's hardest
  problem, the 3 kN horizontal frame, if the pocket only tacks (C5).
- **a4 (post-held).** c1b Break 2 shows a post needs 0.2–1.6 N of grip that a
  tacked flag may not have. For flags, a slot is the better holder, and the
  post stays with bare contacts.
- **a4b / a5 (housing as fixture).** c5's T4-only scope cuts both down to one
  XHP-4 nest, three steps and no gaps.
- **My facts.** My wave-1 Würth citation stands: it is the 1,000-piece-reel
  number. The drawing confirms what I said then, that it is an analog for the
  strip only, since its box is 1.45 mm. Both explorers' 7.10 mm is that
  smaller contact's pitch, and my strip ideas should say so each time they
  use it.
- **A new idea for my view.** A strip-fed *pallet loader* (C1) is a
  supply-side machine I did not draw in wave 1. It serves any arrangement
  that holds loose contacts in pockets: c1, c1b, c3, and ribbon-as-pallet's
  cassette.
