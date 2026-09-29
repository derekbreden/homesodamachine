# into-the-housing on terminal-supply (wave 3)

into-the-housing treats insertion as the dexterous step: what matters about a
crimp is where it sits, how it is held and how much wire it carries when it
reaches the housing. terminal-supply holds that the contact's arrival form
decides everything downstream. This file reads
[terminal-supply](../explorers/terminal-supply/summary.md)'s idea files, most
closely the ones new or changed in wave 2
([a2d](../explorers/terminal-supply/ideas/a2d-skip-pitch-crown.md),
[a4b](../explorers/terminal-supply/ideas/a4b-through-cavity-post.md),
[a5](../explorers/terminal-supply/ideas/a5-housing-as-fixture.md),
[a6](../explorers/terminal-supply/ideas/a6-post-is-the-gripper.md),
[a7](../explorers/terminal-supply/ideas/a7-if-the-contacts-switch-to-strip.md),
[x1](../explorers/terminal-supply/ideas/x1-post-feeds-the-hand-tool.md)), its
[wave-2 calc](../explorers/terminal-supply/calc/wave2.out.txt), and the wave-2
critique
([machine-that-sees-and-learns on terminal-supply](machine-that-sees-and-learns--on--terminal-supply.md)).
What that critique already raised (a2's neighbours on fresh contacts, the
vane, the drop-shear kink, a2b's tag pull, a3b's punch axis, a5's pivot, the
nozzle that cannot load a post) is not repeated.

**Citations.**
- **[w3 §X]** are numbers in
  [`../explorers/into-the-housing/calc/exchange_terminal_supply_w3.py`](../explorers/into-the-housing/calc/exchange_terminal_supply_w3.py),
  output in
  [`exchange_terminal_supply_w3.out.txt`](../explorers/into-the-housing/calc/exchange_terminal_supply_w3.out.txt).
- **[ith w2 §X]** are my wave-2 numbers
  ([`wave2.out.txt`](../explorers/into-the-housing/calc/wave2.out.txt)).
- **[TS calc §n]** are terminal-supply's own
  ([`terminal_supply.out.txt`](../explorers/terminal-supply/calc/terminal_supply.out.txt),
  [`wave2.out.txt`](../explorers/terminal-supply/calc/wave2.out.txt)).
- Prime rows are from [`../sourcing/amazon-prime.md`](../sourcing/amazon-prime.md),
  observed 2026-09-28.

**Coordinates.** Y along the contact, +Y toward the box nose and the mating
face; X across the row; Z up, barrels open up, lance hanging below the floor.

---

## 1. Combinations

### T1 — Crown station, then sort and push: one web clamp from reel to latched housing (a2d + i6, with a6's post head as the sorting hand)

a2d crimps a whole ribbon end while the ribbon lies flat, fanned at 3–3.5 mm,
and hands back insertion and pin order. My
[i6](../explorers/into-the-housing/ideas/i6-sort-then-push.md) needs exactly
that as its input ("the crimp step must leave the end in a staging plane") and
has no contact supply and no grip on a crimped contact that controls roll.
a6's post head is that grip.

**Picture it.**

- **The bench.** A base about 450 × 250 mm.
  - Along the back, an MGN12 rail carries the **ribbon carriage**: an X
    carriage with a short Y slide, driven through a 5 kg bar cell. On the
    carriage are the **web clamp** (one under-width channel that takes a
    single ribbon or a pair edge to edge) and, 10–25 mm in front of it, a
    printed **fan comb** at 3.5 mm pitch.
  - **Station A, on the left, is a2d as drawn.**
    - A reel of SXH-001T-P0.6 hangs below the bench. The strip rises past
      the thinning punch and wraps a steel crown block of R 25–30 mm.
    - A knife-set anvil sits at the crest, with a drop plate on the downstream
      half and radial pins in the removed contacts' holes at ±7.1 mm.
    - A fence stepper sits behind the crown.
    - Above is a 1 t arbor press whose lever a NEMA 17 lead screw pulls onto
      a hard stop on the crown block, with disc springs for overtravel.
    - The ELP camera looks down, and a level view crosses the station to a
      backlight tile downstream.
    - Added here: a slotted steel **pull fork** on a servo, which drops onto
      the land behind the station contact's insulation barrel.
  - **Station B, about 200 mm to the right, is i6 with a different hand.**
    - Two dock pins for the carriage.
    - A printed **target comb** of 1.5–1.6 mm U-slots at 2.50 mm, 6–10 mm
      below the fan plane.
    - A **housing nest** on a Y slide, driven by a NEMA 17 on a T8 screw
      through a bar cell.
    - A slotted stencil-steel **backing blade** on a servo.
    - The camera above.
    - a6's **post head** on a small X–Y–Z stage. Its parts:
      - a 0.64 mm pin standing 1.5–1.8 mm out of a steel holder ≤ 2 mm wide;
      - a stripper;
      - the ±0.2 mm float;
      - its backstop blade, cut here as a **fork** that straddles the wire.
- **What the person does.**
  - Lays a split, stripped ribbon end (or a pair) into the web clamp and
    presses its conductors into the fan comb.
  - Picks the loom's recipe.
  - Drops the housing into the nest.
  - Later lifts the finished end out and labels it (J4 and J7 share a
    housing).
  - Mounts the reel once. At a2d's skip-2, 0.89 of one 8,000 reel covers the
    program [TS calc wave2 §7].
  - Empties the thinning, reject and scrap cups.
- **At station A, for each conductor in web order** (a2d's cycle, one step
  added):
  1. The ribbon is drawn back and the strip indexes two pitches. The pins go
     in, the camera measures the station contact, and the fence corrects it.
  2. The carriage presents conductor k over the crest, steered by its
     insulation edge as seen, and the level gate looks across the station.
  3. The press closes to its stop and the drop plate shears the tab.
  4. **Proof pull.** The pull fork drops behind conductor k's insulation
     barrel. The carriage's Y pulls the whole web back at 20 N through its
     cell, and the camera watches k's insulation edge for slip.
     - Only k is blocked by the fork. The other conductors' contacts are free
       and simply move.
     - This is the force ladder's place, before insertion [ith w2 key
       findings].
  5. The fork lifts, and the carriage lifts k and draws back.
  6. A contact that fails its look is sheared with no wire, as in a2d. A crimp
     that fails stops the end and queues a cut-back.
- **Carry.** After the last conductor the carriage runs to station B and
  docks on its pins. The crimped contacts now stick out of the fan comb, lance
  down, at 3.5 mm pitch in the fan plane: i6's staging plane.
- **At station B, lower layer first, centre outward** (i6's order, [ith w2
  A, C]):
  1. The camera finds contact k's box front.
  2. The head's fork drops behind k's insulation barrel. Between neighbours at
     3.5 mm there is 1.8 mm between insulation surfaces.
  3. The pin spears the box from the front at 0.2–2 N, reacted by the fork.
     The head's cell shows a rise, then the wall.
  4. The head carries the contact down 6–10 mm and across (at most 8.5 mm, on
     J4 [w3 §H]) to slot k. The holder face sets the box front on the
     placement line.
  5. Lowering also presses the wire into the U-slot through the fork's
     crotch.
  6. The stripper releases the box and the head rises.
  7. The upper-layer conductors go last and lie over the placed ones: J4's
     3V3 and GND, J7's GND.
- **Push and check.**
  - The backing blade drops behind every insulation barrel, and the nest
    drives −Y onto the row.
  - The cell trace shows the lance events. At the KONNRA clone figure the sum
    is ≤ 7 × 9.8 N on J4 and 9 × 9.8 N on J1.
  - The blade lifts. The carriage pulls the web back at 5 N × n while the
    camera watches each wire at the rear face: a contact that moves more than
    0.2 mm has not latched.
- **How it knows.**
  - a2d's five signals at A, plus the proof-pull trace.
  - At B: the spear trace (rise, then wall), the placement photo (order, roll,
    fronts), the push trace and the pull-back.

**What locates what.**

| Moment | Reference | Located part |
|---|---|---|
| Contact at the die | crown block: pins in the removed contacts' holes, fence per contact, anvil land, stop | the contact [TS a2d] |
| Conductor at the die | its own insulation edge, as seen | conductor k (carriage X and Y) |
| Proof pull | pull fork on the crown land | insulation barrel's rear edge |
| A to B | two dock pins | the web clamp and the fan comb, so the whole end |
| Pick at B | the head's holder face and pin | box front and roll (pin flats against the leaves) |
| Row | target comb (wire), placement line (box fronts), backing blade (rears at the push) | each contact |
| Push | keyed nest on its Y slide | cavities |

**What drives and carries force.**
- **The crimp.** 0.8–2.6 kN closes through the crown block and its stop, as in
  a2d; the arbor press frame only pushes.
- **The proof pull.** 20 N goes through the fork into the crown block.
- **The spear.** 0.2–2 N goes into the head's fork.
- **The push.** It goes through the backing blade into the base.

**What each contributes, and what neither does alone.**
- **a2d:**
  - supply from a reel;
  - a located contact;
  - a flat ribbon at any width, so J1's 5P + 4P goes through as one
    nine-conductor end;
  - a level line of sight;
  - reject without a wire.
- **a6:** a hand that holds a crimped contact by its own socket, with roll set
  by flats and the front on a face. This is my i6's first open problem
  ("gripping a 0.043 g crimped contact by its barrels and releasing without
  roll"), and it answers it without fingers at 2.5 mm pitch.
- **i6:**
  - J4's and J7's crossings;
  - the pairs;
  - J2's empty cavity;
  - the backing blade;
  - a gang push that stores no feed;
  - the latch check.
- **Together:** a reel and a ribbon end become a latched, tested housing with
  one datum (the web clamp) from first crimp to push.

**Numbers.**
- **Fan split at A** [w3 §H]:
  - 3P 11 mm, 4P 13 mm, 5P 16 mm;
  - the J4 and J7 pairs ~23 mm;
  - J1 ~26 mm at 3.5 mm pitch;
  - 1–5.5 mm less at 3.0 mm pitch.
- **Staging height at B.** At 3.0–3.5 mm staging pitch J4 needs ≥ 5.5–6.1 mm
  and J7 ≥ 2.6–3.2 mm. J1 and the straight looms have no crossing [w3 §H].
  6–10 mm covers the unit.
- **Machine time.** 2.7–3.1 h per unit: a2d's 94 min, plus 60–87 min of sort,
  pull and push, plus the carriage moves [w3 §L]. It is unattended between
  loads.

**Problems, as they stand, and branches.**
- **The spear needs the fork.**
  - A crimped contact on 20–30 mm of free conductor buckles the conductor at
    0.17–0.39 N [w3 §H, scaled from the digest].
  - The spear takes 0.2–2 N, so the fork behind the insulation barrel is part
    of the head, not an option.
  - Its tines must be ≤ 0.4 mm and bear on a crimped insulation barrel about
    1.8–2.0 mm wide.
- **Capture at the box entry is ±0.1–0.25 mm, not ±0.4/0.6** (§3 item 1).
  - The staged fronts are found by the camera. A roll left by the crimp is
    squared by the pin's flats, which twist the conductor slightly.
  - Whether a staged contact's roll exceeds what the entry accepts is
    unknown.
- **Fronts on a line, rears scattered.** The holder face aligns fronts, so the
  rears differ by the contacts' length spread: ±0.05 mm within a lot
  [estimate], up to ±0.25 mm between brands [source S19–S22]. During the push
  each contact slides back in its slot (1–11 N of slot grip [ith w2 D]) onto
  the blade before its lance folds, which staggers the events in the trace.
  That is useful rather than harmful, and it is unmeasured.
- **Strip-bound.** T1 cannot use the kit contacts except as hand-repair stock:
  a2d needs strip, genuine or clone reel. a7's supply decision reaches T1
  directly.
- **The finished loom's split.** 11–26 mm of split, plus the i6 set step of
  6–10 mm and bows up to ~2.9 mm on J4 [ith w2 B]. Whether that is
  acceptable behind the housing is still Derek's question.
- **Trimmed conductors.** J7's third 3P conductor and J2's cavity-3 conductor
  are cut back at the fan root by the person, or by a snip at A. The carriage
  skips that position.
- **a2d's own open problems carry over unchanged:**
  - real SXH pitch and carrier temper;
  - knife-set blade width and protrusion;
  - seating the anvil into the crown;
  - the die outside its applicator.
- **Branch T1b: i6b's post bed at B.**
  - Identity is proven before the latch.
  - The a6 head cannot thread onto a bed post, because both want the box
    front. T1b uses i6's barrel fingers and gives up the post head.
  - The bed push is 13–14.5 mm [w3 §A].
- **Branch T1c: a2b's tag as the handle at B.**
  - At A, the carrier is cut either side of the pilot hole instead of at the
    tab. At B, the head grips by the hole plus a finger on the crimp.
  - Tags 2.3 mm wide cannot enter 1.5–1.6 mm U-slots, so each rear stands
    3.8–4.2 mm ahead of the comb face. The blade then bears on the tag's rear
    edge: 0.46 mm², 54 MPa at 25 N.
  - After the push the tags are bent off beside the housing (a2b's open stub
    question). a2b's calc §4 puts the carrier edge between 0.05 mm inside and
    0.9 mm outside the rear face at full seat, so in the worst case the tag
    stops the seat.

**Parts with Prime rows.**
- **Press:** VEVOR AP-1 1 t arbor press, $61.90, 150 mm opening, 81 mm throat.
- **Drives and rails:**
  - Iverntech NEMA 17 with integrated Tr8×2 screw, $27.99 (thin);
  - MGN12 and MGN9 rails;
  - MG90S and DS3218 servos.
- **Sensing:** ShangHJ 5 kg bar cell with HX711, $9.99. That covers A's 20 N
  pull. B's J1 push of up to ~90–180 N wants a 20 kg cell, which is listed in
  my `sourcing-requests.md`, Wave 3.
- **Crown and springs:**
  - Accusize pin gauges, which include 1.448 mm, for the crown's pins;
  - Hilitchi Belleville assortment, light duty, per its caveat.
- **Posts:** 2.54 mm header strips for pins, cross-section unstated.

The knife set has no Prime listing (eBay/AliExpress titles only [TS a2]).
Contacts come from the Digi-Key or LCSC reel [xh-facts §6].

### T2 — a5's staging with i2b's single push: stage, crimp, leave, then push them all

a5 stages a bare contact into its own cavity with a post, crimps it at the
mouth and pushes it home, one cavity at a time. My
[i2b](../explorers/into-the-housing/ideas/i2b-preload-the-whole-housing.md)
preloads every cavity by hand in two passes, crimps each in place and pushes
all home at once. Combined, the machine does the staging and nothing is
pushed until every contact is crimped. That removes the per-conductor stored
feed that one-at-a-time seating forces (§2, a5 item 1).

**Picture it.**
- **One X stage** carries the housing nest and the web clamp with a 2.5 mm fan
  comb. The web must ride with the housing: §2, a4b item 3.
  - The nest is located only in Y. It floats ±0.2 mm in X and Z on a printed
    parallelogram flexure (i2's floating nest).
  - A Y drive between web and nest runs through a 20 kg cell.
- **The fixed station:**
  - a5's staging post, which enters through the front post opening from under
    the mating face, with a light behind it for the lit square;
  - a **lance-grooved** shuttle nest (§2, a6 item 1), fed by a nozzle or by
    hand;
  - my narrow stepped crimper (3.1 mm conductor step with 0.8 mm walls, 2.5–2.7
    mm insulation step) on a knee in a fist-sized steel C, over an anvil
    whose shoulders below the floor catch the crimper walls (i2, force-and-form
    f8);
  - one lift finger;
  - a side camera.
- **Staging.** With the web drawn back so no stripped tip lies on the
  shuttle's path, the machine stages bare contacts at 1.5 mm into every other
  cavity, centre outward. For each, the post spears the contact from the
  grooved shuttle and draws it in; a side look and the lit square follow.
- **Odd pass.** The web advances. For a one-layer loom every odd conductor
  lands in its staged contact's barrels at once, fanned at 2.5 mm, and the
  even conductors lie flat behind their empty cavities. Each conductor's Y is then
  trimmed by pressing a saddle hump, because the tip moves 1.7–3 × the press
  (f&f §12), so the web is set slightly long. Each staged contact is crimped.
  The waiting even conductors lie flat beside the die at ±2.5 mm and clear it:
  +0.10 mm at the conductor step, +0.30–0.40 at the insulation step [w3 §C].
- **Even pass.**
  1. The finger lifts even conductor k about 4 mm.
  2. The shuttle stages its contact beneath. The open wings clear the crimped
     neighbours' insulation barrels by +0.03 to +0.30 mm.
  3. The finger lays the conductor into the barrels, and the contact is
     crimped between crimped neighbours: +0.20 at the conductor step,
     +0.17–0.28 at the insulation step [w3 §C].
  4. After each crimp the post withdraws out the front, and the crimped
     contact stays staged by mouth friction and its own conductor.
- **Crossings.** J4 and J7's upper-layer conductors (3V3 and GND; GND) wait
  lifted by the finger until their cavities come last. Those cavities lie at
  an end of the housing [ith w2 A], so the lower layer is complete beside
  them.
- **Proof pull.** A slotted blade behind every insulation barrel; each wire is
  pulled 20 N, in turn, by a clamp on the lift finger. Pulling the web pulls
  all of them and leaves each wire's share unknown.
- **Push.** The nest drives −Y by 5.25–5.45 mm onto all the contacts at once
  [w3 §A]. The cell shows the lance events, and the lit squares go dark.
- **What the person does.** Loads the housing and the split, stripped end, and
  keeps the shuttle's supply filled.

**What each contributes.**
- **a5:** machine staging of rigid bare contacts into the product's own
  cavities, the lit square and a per-cavity look.
- **i2b:** the single push with zero stored feed.
- **i2:** the floating nest, the stepped dies bottoming on anvil shoulders, and
  the lance condition.
- **i6:** layer order, so crossings need only one lift finger.

**What it leaves uncertain.**
- **Die making.** A 3.1 mm step with 0.8 mm walls, cut to ±0.05 mm, is my own
  open problem.
- **The lance condition.** About half the clone-drawing range needs a lance
  slot in the anvil [w3 §D].
- **Staged, crimped contacts must stay put** at 1.5 mm with the post gone,
  while their neighbours are crimped. Mouth friction is unmeasured.
- **The web's Y** sets every conductor's reach at once. Tear scatter per
  conductor needs the hump press, and the hump press can only shorten.
- **J1.** 9 cavities means 5 odd and 4 even stagings.

### Others, briefly

- **T3 — the stub pen (x1 + i2d).** x1's post pen and my
  [i2d](../explorers/into-the-housing/ideas/i2d-locator-the-lance-never-touches.md)
  reference the same datum, the box front.
  - **The build.** A cut XHP stub (front wall plus 1.0–1.5 mm of cavity) is
    bonded to the pen's steel face, so the pen's pin passes through the stub's
    own post opening. The contact is speared into the stub.
  - **What each part does.**
    - The stub's walls add roll (±1.5–4.4°) and X–Z [ith w2 H] to the pin's
      grip.
    - The pin adds grip and stripping to the stub.
    - x1's jaw fence takes the pen face, so i2d's flexure is not needed: the
      pen leaves after the click.
  - **Wired.** The pin wired to an ESP32 input, with the far end in a
    terminal block, is i2d″: "this conductor is in this contact" before the
    squeeze.
  - **Uncertain.** Stub depth against the lance root (0.74–1.74 mm allowed
    [ith w2 H]), and the lot's box-to-barrel spread, which both references
    share.
- **T4 — a3's hanging pose fills i2b by gravity.**
  - a3 delivers a contact box-down. A housing lying rear face up under the
    rail's escapement takes it box-first. The contact slides until its lance
    tip meets the rear face, about 2.4 mm deep, which is i2b's first stop.
  - Odd cavities go first, because clone wings collide at 2.5 mm pitch; then
    the odds are crimped, then the evens are filled. This removes i2b's two
    hand passes.
  - **Uncertain:**
    - the escapement's landing in a 1.9–2.1 mm mouth (a3's own
      landing-accuracy question);
    - which way the U faces relative to the cavity's window side, which a3's
      turn pocket settles.
- **T5 — a2d's crown under my i2 strip branch and K2.** Skip-2 at R 25–30
  drops the kept neighbour's box top 1.2–2.0 mm below the housing's underside,
  with a 3.3–3.9 mm floor drop [w3 §I]. i2's strip feed then needs no plastic
  crown (§3 item 4).
- **T6 — the lit square after a gang push.** a4b's and v6's light under the
  mating face is a per-cavity seat check for i3's and i6's pushes before the
  pull-back: a seated box darkens its post opening. One flashlight photo also
  answers i6b's premise.
- **T7 — a6's silhouette on the post as i4's contact pick.** The gantry hand
  in [i4](../explorers/into-the-housing/ideas/i4-gantry-hand-with-eyes.md)
  picks bare contacts with fingers at 2.5 mm pitch, which is its open grip
  problem.
  - A post tool picks and measures the bare contact instead, to a few µm.
  - The fingers are kept for the crimped contact on its way into the cavity.
  - a6's float (±0.2 mm sideways, 0.3 mm up, light preload) is a working
    specification for the lockable wrist i4 lacks.

---

## 2. What still breaks in their revised and new ideas

### a4b — the post through the cavity

1. **The crimped contact is ~14 mm short of its seat, and one web holds every
   conductor.**
   - The box sits on a post tip 9 mm out of the rear face, so its front is
     7.2–7.5 mm outside the housing. Seated, it is 6.75–6.95 mm inside. The
     push is therefore 13.95–14.45 mm [w3 §A].
   - With square-cut ends and each contact seated taut, conductor k needs
     that much extra length at the moment of its crimp.
   - That is an **11–15 mm hump** between the web and the post tip over a
     25–40 mm split [w3 §B]. It rises where the press stands above the post
     and over the flat neighbours. At a tightest radius of 2.6–3.5 mm it
     yields, so it holds its shape. The push draws it straight with a few
     hundredths of a newton [w3 §B].
   - If the housing moves onto the contact instead, the seated neighbours
     carry the same bow.
   - The file does not say where the length comes from.
   - **Repairs:**
     - a saddle or hump presser behind the post line (my i1 and i2);
     - a5's short post, which gives a 6–8 mm hump, at the cost of the
       neighbour sweep growing from 2–4° to 17–30°;
     - every post at once with one push, which is my i6b: nothing is stored.
   - **Uncertain:** where the hump can stand with a punch holder above the
     post tip.
2. **The waiting conductors lie in the die's path.**
   - TS calc §8 counts only the seated side.
   - Conductor k+1's tip reaches the same Y as k's. At web pitch it lies
     inside any punch: −0.50 to −1.15 mm.
   - Fanned to 2.5 mm it clears a 2.7 mm punch (+0.30) and my 3.1 mm step
     (+0.10), and meets 3.5–4.0 mm punches by 0.10–0.35 mm [w3 §C].
   - **Repair:** lift the waiting side (a finger or a loft), or fan it to
     2.5 mm and use narrow dies.
3. **The web clamp must ride the housing's X stage.** Once the first contact
   latches, the ribbon is tied to the housing. If the housing steps 2.5 mm per
   cavity under a fixed web, the seated conductors are dragged sideways by up
   to (n−1) × 2.5 mm: 20 mm on J1. The station (post slide, dies, camera)
   must be the part that stays fixed.
4. **Pin order "through the stage index."**
   - That holds for the eight one-layer looms.
   - On J4 the conductor for cavity 1 (3V3) sits third in the 4P, and GND
     crosses 6.7 mm [ith w2 B].
   - The stage must visit cavities in layer order. The picker takes each
     conductor from its web position, and the upper-layer conductors wait
     lifted until last [ith w2 A, C].
5. **The seat pull.** 10 N is 68 % of the 14.7 N Molex-analog retention and
   51 % of KONNRA's 19.6 N [w3 §K]. 5 N keeps the force ladder's margin.
   Before the post withdraws, the pull also includes its 0.2–2 N grip.
6. **The shuttle nest needs a lance groove** (a6 item 1 below).

### a5 — the housing as fixture

1. **Stored feed.**
   - The push after the crimp is **5.25–5.45 mm**, not ~4.5 [w3 §A; §3 item 2].
   - Conductor k therefore stands in a **6–8 mm hump** during its crimp
     [w3 §B], beside the die and over the swept, seated wires.
   - **Repairs:** a hump presser, or branch T2 (stage, crimp, leave, one push).
2. **The lance window, from a5's own numbers.**
   - Staging at 1.5 mm puts the lance tip 0.94 mm outside the face (tip 2.44
     from the front). The conductor barrel starts 1.1 mm behind the face
     (2.6 from the front).
   - The anvil's front edge must therefore sit between 1.04 and 1.10 mm behind
     the face: **0.06 mm of window** [w3 §D].
   - Across the clone ranges (tip 2.24–2.64, transition 0.4–0.6) the margin
     runs from −0.34 to +0.26 mm.
   - "Every crimp die already has this relief" is the assumption that closes
     it. With a relief, up to 0.34 mm of the conductor barrel's front rides
     on the slot's two shoulders instead of a full anvil, 1 mm from the
     housing face.
   - **Uncertain** until one kit contact is photographed side-on.
3. **The waiting side** is the mirror of a5's own sweep calc.
   - Conductor k+1, fanned to 2.5 mm behind its empty cavity, meets the 3.5 mm
     punch by 0.10 mm and the 4.0 mm insulation punch by 0.35 mm [w3 §C].
   - **Repair:** a second finger sweeping or lifting the waiting side, or the
     narrow stepped dies, which clear it.
4. **The wedge is one way to match anvil and cavity; floating the housing is
   another.**
   - The seated wires resist a ±0.2 mm float by 0.01–0.09 N [w3 §G].
   - A nest located only in Y lets a fixed anvil lift the staged box and drag
     the housing to its own line, with no per-cavity floor measurement and no
     wedge travel.
   - The wedge keeps a use: setting the fixed anvil or the stop once.
5. **A proof pull at the mouth is possible,** and a5 does not use it.
   - A slotted fork behind the insulation barrel's rear edge (~4.5 mm behind
     the face at 1.5 mm staging), with conductor k pulled −Y at 20 N, loads
     the crimp while the contact is staged and unlatched.
   - This is my backing blade used as a fork. The critique's "no crimp proof
     pull once seated" applies only after the push.
6. **"Cavity index is conductor index."** This holds for one-layer looms and
   fails for J4 and J7 (a4b item 4).

### a6 — the post as gripper (and x1's pen and spear block)

1. **A barrels-up contact does not lie flat on a channel floor with no lance
   groove.**
   - The lance stands 0.6–0.9 mm proud of the floor side, 2.24–2.64 mm behind
     the front [xh-facts §1]. The estimated centre of mass is 2.75 mm behind
     the front [w3 §E], right beside the lance tip, so either rest occurs:
     - nose-up by 8–16°, with the box front floor 0.9–1.7 mm above the
       channel floor;
     - or nose-down by 13–22°.
   - A pin approaching along the channel axis at the flat-lying height meets
     the box face, not the entry.
   - v4b's pocket had a lance relief at one end. a6's channels are "open at
     both ends" so the box may be at either end, and they carry no relief.
   - **Repair:** a groove 0.8–1.0 mm wide and ≥ 1 mm deep along the whole
     channel floor, with the box and barrels spanning it (as i2's lance-grooved
     channel plate).
   - The same groove belongs in x1's spear block, a4's loading nest, and
     a4b's and a5's shuttle nests.
   - **Uncertain:** how far a spring lance flexes under the contact's own
     0.4 mN, which is negligible. One side photo of a contact on a card shows
     the rest.
2. **Capture.**
   - The ±0.41 mm / ±0.58 mm figures come from the box's inside
     (1.45 × 1.80 mm). The post enters through the box's formed entry,
     0.60–0.70 mm [xh-facts §1, S19, S21].
   - With a 0.2 mm chamfer that is ±0.18–0.23 mm, and ±0.08–0.13 mm with a
     0.1 mm chamfer [w3 §F].
   - Laterally the 2.05 mm channel holds the box to ±0.05–0.10 mm, which is
     enough. Vertically, item 1 decides.
3. **The float goes up only.**
   - The float is "±0.2 mm sideways and ~0.3 mm up". At the SN-2549's nest
     (x1), or an anvil that seats the floor lower than the head's taught Z,
     the closing die drives the contact down and the holder cannot follow.
     The pin then bends the box against the transition.
   - **Repair:** ±0.2 mm in Z too, with the preload from above.

### x1 — the post feeds the hand tool

- Everything in a6 items 1–2 applies to the spear block and to the machine
  form.
- **The pen shares my i2d stub's exposure.** Both place the barrels from the
  box front, so both depend on the lot's box-to-barrel spread: ±0.05 mm within
  a lot [estimate], ±0.25 mm between clone brands.
  - a6's per-contact silhouette removes that in a machine.
  - For the pen, one light-pad photo of twenty kit contacts measures the lot's
    spread once.
- **The lance condition** [w3 §D] applies to the SN-2549's own XH anvil. The
  tool crimps kit contacts today, so either their transition is long enough
  or the anvil has a relief. That is one look at the jaw, my open question.

### a2d — skip-pitch strip over a crowned anvil

- **The punch-holder rule counts the wrong neighbour.**
  - It counts a conductor (half-width 0.85 mm). The neighbour at ±p is a
    crimped contact whose box, 1.95 mm wide, lies at the station's Y.
  - So p ≥ blade/2 + 0.98 + 0.3: about 0.13 mm more, 2.5–2.8 mm for a
    2.5–3.0 mm blade.
  - 3.5 mm pitch still clears.
- **No proof pull.** The pull fork and carriage pull of T1 fit a2d as drawn.
  The fork sits on the crown land, the camera already watches the insulation
  edge, and the carriage already has a driven Y.
- **The fan stays in the loom.** 11–26 mm of split at 3.5 mm pitch [w3 §H]
  stays in the finished loom unless insertion re-closes the fan. T1's i6 does
  that at the housing, and the split remains behind it.
- Otherwise a2d stands as drawn. Its open problems (pitch, temper, knife set,
  anvil in the crown) are its own.

### a2b — the carrier kept as a handle

- **The tag cannot enter any comb built for wires.** It is 2.3 mm wide against
  my 1.5–1.6 mm U-slots, i3's shuttle clamps, and i6b's post bed. Carried into
  a gang push, the tag and not the insulation barrel is what the backing blade
  bears on (T1c).
- **At full seat** the tag is either inside the rear face by 0.05 mm (blocking)
  or outside by up to 0.9 mm [TS calc §4]. So a gang push with tags on needs
  them bent off after a partial push: two push phases. Otherwise the tag's
  datum is used for the sort only and cut before the push.

### a7 — the supply map

- **Genuine narrow wings let every cavity be preloaded,** as a7 says for i2b,
  but they do not let every cavity be crimped in one pass. The 3.1 mm
  conductor step clears an open neighbour's conductor barrel (clone 1.68–1.90
  mm) by only 0.00–0.11 mm [w3 §J]. The odd/even order stays unless genuine
  conductor barrels are narrower than the clone drawings.
- **The classification of my arrangements** is in §3 item 5.

---

## 3. Consistency

1. **Post capture at the box front.**
   - [a6](../explorers/terminal-supply/ideas/a6-post-is-the-gripper.md)
     ("±0.4 mm sideways and ±0.6 mm vertically"), TS calc wave2 §5 and the TS
     summary's key findings compute capture from the box inside
     (~1.45 × 1.80 mm).
   - [xh-facts §1](../context/xh-facts.md) gives the box entry as 0.60–0.70 mm
     [S19, S21]. My [i6b](../explorers/into-the-housing/ideas/i6b-post-bed-through-the-housing.md)
     uses ±0.2 mm from it.
   - The entry figure is document-backed and is the one a post passes. Capture
     is ±0.1–0.25 mm, depending on chamfer [w3 §F].
2. **Push travel after a crimp at or outside the housing.**
   - a5's "the last ~4.5 mm" is a seat with the contact's rear flush to the
     rear face.
   - TS calc §4's own seat geometry (rear 0.25–0.85 mm inside, front wall
     0.8–1.0 mm) gives 5.25–5.45 mm from 1.5 mm staging. The calc is the more
     careful figure.
   - a4b states no travel; from its 9 mm post it is ~14 mm.
   - The same geometry sets my i6b's housing travel at 13–14.5 mm [w3 §A],
     the figure its file carries.
   - All of these rest on the front-wall thickness, which is unmeasured.
3. **The lance and the anvil.**
   - a5 places the lance tip "~0.1 mm ahead of the conductor barrel's start"
     and relies on "every crimp die already has this relief". That is a flat
     anvil with margin 0 by construction.
   - The transition estimates disagree:
     - TS calc wave2 §5 reads 0.4–0.6 mm off the clone drawings;
     - my wave-2 exchange with hand-tool-as-press used 0.2–0.5 mm [estimate].
   - With xh-facts' lance tip at 2.24–2.64 mm, the flat-anvil margin is −0.34
     to +0.26 mm on TS's reading [w3 §D], and worse on mine.
   - Neither can be called right. One side photo of a kit contact settles the
     transition, and one of the SN-2549 jaw settles the relief.
4. **Crowns.**
   - My [i2](../explorers/into-the-housing/ideas/i2-crimp-in-the-cavity.md)
     strip branch and K2 in i3 (from force-and-form §10) use R 6.3–12.5 mm,
     plastic and one-way, to "drop the neighbours 3.6–4.0 mm".
   - a2d rejects plastic crowns. Its table uses the wing tip against the crest
     plane; i2 uses the floor drop. Both are computed consistently: [w3 §I]
     reproduces 3.59 mm at R 6.3 / 7.1 mm and 3.44 mm at R 12.5 / 9.5 mm.
   - Where they differ is usability, and a2d is right about my i2.
     - A perforated carrier wrapped past yield does not take a smooth radius.
       The slots localise the hinge (critique calc §6).
     - The station contact's roll then depends on two hinge angles.
   - With skip-2 at R 25–30, i2 gets its floor drop elastically (3.3–3.9 mm)
     and the kept neighbour's box top 1.2–2.0 mm below the housing's underside
     [w3 §I].
   - R 12.5 with every contact kept at 7.1 mm pitch leaves the box top at
     −0.02 mm, against a housing underside at about −0.4 mm [assumption].
5. **a7's table, for my arrangements.**
   - i4 is marked "loose". It is either: a tray, or f3's strip, per i4.
   - Not listed:
     - i6 and i6b: — (they handle crimped contacts only);
     - k6: strip (f4's dispenser);
     - i2d: loose, or strip contacts cut first;
     - i2c: either.
   - a7 notes that it read wave-1 summaries.
6. **The 1 t arbor press.**
   - a2 and a2d use Harbor Freight 59766: $79.99, 139.7 mm opening, 20:1
     lever.
   - The Prime pass confirmed the VEVOR AP-1: $61.90, 150 mm opening, 81 mm
     throat.
   - Both are too short for an OTP applicator (166–176 mm) and both fit a
     knife-set block. The conclusion is unchanged.
   - a2's "~150 N at the lever gives ~3 kN" is Harbor Freight's 20:1; the
     VEVOR page does not state a ratio.
   - The 81 mm throat bounds how far the crown's crest may sit from the
     column.
7. **The seat pull against the force ladder** (a4b's 5–10 N): see §2, a4b
   item 5.
8. **Checked and consistent:**
   - post stiffness: a4b's 0.85–1.7 N/mm at 17 mm, a5's ~24 N/mm at 7 mm, and
     my 16.4 N/mm at 8 mm are all 3EI/L³ with E 200/100 GPa;
   - a2d's program costs ($36 and $71) against xh-facts §6 prices;
   - TS's 3,556 crimps, which is 3,233 plus 10 % spares;
   - lifted-conductor set [TS calc wave2 §4] against the digest's 67 mm yield
     radius.

---

## 4. Transfers

**From into-the-housing to terminal-supply**

- **The feed-length rule.**
  - One-at-a-time seating after a crimp stores the travel as conductor length:
    6–8 mm humps in a5, 11–15 mm in a4b.
  - A single push after all crimps stores none (T2, i6b).
  - This decides where a4b's and a5's dies can stand.
- **Wait high, place low; pin maps as layers.**
  - Only J4 and J7 need a second layer, and it lands at a housing end.
  - This answers a4b's and a5's "two-ribbon housings" and turns "cavity index
    is conductor index" into a visiting order.
- **The web clamp as the single datum, riding with the housing** once the
  first contact latches (a4b item 3).
- **The floating nest,** located in Y only, instead of a5's per-cavity wedge
  and floor measurement [w3 §G].
- **The lance condition,** t ≥ tip + 0.1 − 2.0, for every anvil that holds
  the box with the lance free: a5, a6's knife-set anvil, x1's SN-2549 [w3 §D].
- **The lance-grooved channel** for every bare-contact pocket: a6, x1, a4,
  a4b, a5.
- **The backing blade as a proof-pull fork** behind the insulation barrel.
  - It gives a2d and a6 a proof pull.
  - It gives a5 one at the mouth, before the push.
  - Force ladder: 5 N latch test < 14.7–19.6 N retention < ~20 N proof pull
    < 39.2 N pull-out.
- **Narrow stepped dies** (3.1 mm with 0.8 mm walls, 2.5–2.7 mm insulation
  step) clear waiting conductors fanned at 2.5 mm and crimped neighbours
  [w3 §C]. a5's knife-set punches do neither.
- **The housing stub** (i2d) as the molded twin of x1's pen face (T3).

**From terminal-supply to into-the-housing**

- **a6's post head is the grip i6 lacked** for crimped contacts. Roll comes
  from the pin flats, the front from the holder face, and release from the
  stripper (T1).
  - It needs a fork behind the insulation barrel [w3 §H].
  - It cannot thread onto i6b's posts.
- **a2d's skip-pitch elastic crown** replaces my i2 strip branch's plastic
  crown (T5, §3 item 4).
- **a2d's flat ribbon at any width** is the crimp stage that leaves i6's
  staging plane (T1). J1 goes through as one nine-conductor end.
- **a5's staging post and lit square** machine-load i2b's cavities (T2). The
  lit square is also a seat check for i3 and i6 (T6).
- **a5's self-locking 2–3° wedge** sets i2d's stub floor to the SN-2549 anvil
  once. That is i2d's "stub floor to anvil height match". It gives
  35–52 µm per mm of travel and holds 3 kN [TS calc wave2 §8].
- **a6's silhouette on the post and its float** for i4's bare-contact pick and
  wrist (T7).
- **"Cut the carrier before the wire exists," and a2c's pinch cutter** for my
  i2 strip branch. Its tab shear otherwise pulls the rear down with only the
  cavity walls holding the box.
- **a3's box-down hanging pose** is the pose a rear-face-up housing takes by
  gravity, which fills i2b (T4).
- **a7's supply map.**
  - T1, k6 and i2's strip branch are strip-bound.
  - i2b, i2d and T2 run on the kit contacts.
  - Genuine wings change i2b's loading but not its crimp order [w3 §J].

---

## Questions for Derek this exchange adds

- One kit contact laid barrels-up on a card and photographed side-on: does it
  rock on its lance, nose up or nose down? That decides whether every
  bare-contact pocket needs a lance groove (a6, x1, a4, a4b, a5, T2).
- One kit contact latched in a kit housing: how far inside the rear face is
  the box front, or how thick is the front wall? That sets the push after the
  crimp in a4b, a5 and T2, and the housing travel in i6b and T1b.
