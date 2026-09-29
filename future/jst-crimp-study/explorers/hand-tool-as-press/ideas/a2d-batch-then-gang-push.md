# A2d — Strip all, crimp all, lay the row into a squaring comb, push the housing onto it

## Picture it

**Where things start.**
- [a2c](a2c-one-baseplate-strip-crimp-insert.md)'s baseplate: the Klein
  squeezer, [a1](a1-squeezer-cradle.md)'s crimp squeezer with
  [a2](a2-ribbon-to-fixed-tool.md)'s stub magazine, rear-face shear and pull
  slot. In place of a2c's housing nest, two new things:
  - **Squaring comb.** A steel-faced comb with 2.5 mm slots, each a
    2.0 × 2.45 mm pocket for the crimped contact body with a 1.7 mm channel
    behind it for the wire. A printed **front plate** slides in and out across
    the noses, and a **rear clamp** with TPU-lined half-round grooves closes
    1–2 mm behind the insulation crimps.
  - **Housing press.** A slide carrying a keyed XHP holder, in line with the
    comb, driven by a NEMA 17 on a Tr8×2 screw (~280 N) through a 20 kg bar
    load cell. A sprung guide comb (into-the-housing's i3) stands in front of
    the row.
- The person clamps the ribbon end, or both ribbons of a pair edge to edge,
  in the head, drops the housing into the holder, and picks the loom.

**What moves.**
1. **Strip all** (a2c step 1).
2. **Crimp all** (a2's cycle), with a proof pull at the pull slot.
3. **Lay down, in pin-map order.**
   - The fork carries each crimped conductor to its slot *c(k)* and presses
     the contact into its pocket.
   - A conductor that crosses others is laid **last, over the top**.
     - J4: the 3P's GND goes to slot 2 over the 4P conductors already in 3, 4
       and 5.
     - J7: the 5P's GND goes to slot 7 over CLO and CHI [ith; repo:
       `pcba.tsx`, `cable-assemblies.md`].
   - The crossing lies between the head's comb and the squaring comb, behind
     where the rear clamp will close.
   - J2's trimmed conductor 3 is laid aside; it was cut short at the end jig.
4. **Square.**
   - The front plate slides across and pushes every nose back to one line,
     ~2 mm behind nominal. The extra length goes into the split as slack.
   - The rear clamp closes 1–2 mm behind each insulation crimp.
   - The front plate withdraws.
5. **Push.**
   - The guide comb holds each nose square until the cavity lead-ins take
     over, then the housing's approach presses it down and back.
   - The slide advances the housing onto all contacts at once, at a crawl,
     through the load cell.
   - No conductor needs stored length, because the housing moves, not the
     contacts [into-the-housing handover].
6. **Release.** The rear clamp opens, and the head unclamps the web.

**What locates what.**
- **Stripping and crimping:** as in a2 and a2c.
- **The row.** Each crimped contact's roll and lateral position are set by its
  comb pocket. Its axial position is set by the front plate, not by its strip
  length or by how much copper set it kept from the crimp's stand-out.
- **The housing:** the keyed holder, on the slide, on the baseplate. "Fixed"
  is the baseplate.

**What drives and carries the force.**
- **Crimp:** as in a1, inside the tool head.
- **Push:** the housing slide's screw pushes the housing onto the row. The row
  reacts into the rear clamp and the comb, so the force loop is baseplate to
  slide to housing to contacts to clamp to baseplate. The head carries none of
  it.
- **Size of the push:** J1's nine contacts take 27–225 N at 3–25 N each
  [ith ex §12], within the ~280 N screw.

**How it knows it worked.**
- a2's per-crimp checks, and the far-end block's identity at every lay-down.
- A camera frame of the squared row before the push: noses on one line, roll
  in the pockets, J2's slot 3 empty.
- The push's force against slide travel, logged: each lance's fold and snap
  as a sum.
- The latch check is an open problem (below).

**What the person does.**
- Cuts and splits the ends; loads stubs.
- Clamps the ribbon end, or both of a pair.
- Drops a housing into the holder, takes the finished end out and labels it.

Sketch: [`../sketches/a2d-squaring.svg`](../sketches/a2d-squaring.svg)
(schematic plan); the strip and crimp stations are a2's
([`../sketches/a2-ribbon-to-fixed-tool.svg`](../sketches/a2-ribbon-to-fixed-tool.svg)).

## Steps it covers and what it hands back

**Covers:** stripping; placing each contact and conductor; crimping, tab cut
and proof pull; pin order, including J4's and J7's crossings and J2's gap;
squaring the row; gang insertion.

**Hands back:** cutting and splitting the ends; loading stubs; clamping ends
and dropping housings in; unloading and labelling; the latch check, unless one
of the three routes below is built.

## How it relates

- Branch of [a2c](a2c-one-baseplate-strip-crimp-insert.md): no one-at-a-time
  insertion and no hump. After crimping, the head lays every crimped conductor
  into the squaring comb in pin-map order, and a fixed housing press drives the
  housing onto the row.
- A combination with into-the-housing's
  [i3](../../into-the-housing/ideas/i3-converging-shuttles-gang-push.md): its
  housing press, zero-feed gang push and sprung guide comb (proposed as C2 in
  its [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md)).
- change-the-question's [c5](../../change-the-question/ideas/c5-ends-as-stock.md)
  T4 ends (4P into XHP-4, 38 % of crimps, no pairs or crossings) give a2d one
  configuration, and the unspooled remainder on a slip ring is the far-end
  electrode array before any loom is cut [htq, K4].

## Major unresolved problems

- **The latch check.** A summed force trace hides one contact that did not
  latch. Three routes, each with a cost:
  - **A camera on the free mating face.** It sees each lance in its window,
    and J2's cavity 3 empty (i3).
  - **The housing on a wired header during the push** (into-the-housing's
    C6). Each contact's arrival on post *n* is timed electrically and paired
    with conductor *k* through the far-end block. The costs: an extra mating
    cycle, the post force added to the push, and the mating face hidden.
  - **A staggered row** (i3b). The squaring comb's pockets are stepped
    0.3–1 mm, so the contacts seat one after another. That gives up the
    single front line.
- **Slack behind the housing.** Pushing the noses ~2 mm back stores slack in
  the split. Whether that bow looks acceptable on a finished loom is Derek's
  question.
- **Laying a crossing over the top** without dislodging the contacts already
  in their pockets. The pockets hold them only by a light press fit, or a
  sprung cover.
- **Jam recovery** in a nine-contact push.
- **Pairs.** Two ribbons edge to edge in one head need a wider clamp. A
  600 mm loom tail from each ribbon has to hang clear of the carriage.
- **The crimp station's stand-out** (*a* + 2.7 mm, 8.7–14.7 mm [calc w3 §2])
  is what the front plate undoes; how evenly set copper squares is untested.

## Why this branch exists

- **Nothing is tied to a housing until the last move.** In a2c the first
  latch ties the ribbon to the housing.
- **No conductor needs a hump or a lift.** This is the only way the head can
  insert without storing feed length.
- **The machine makes J4's and J7's crossings.** i3 and every other gang push
  hand them to the person; here the fork routes conductor *k* to slot *c(k)*.
- **The set copper from a2's stand-out is undone at one place,** the front
  plate, instead of being a property of each conductor.
- **Free conductor behind each contact.** With the rear clamp 1–2 mm behind the
  insulation crimp, that is 1–2 mm, inside even the free-nose buckling limit
  of 1.6–3.5 mm at 14.7 N [ith ex §7; ith calc §1].

## Parts beyond a2c

- **Squaring comb.** Laminated stencil stainless (JLCPCB 304 from $3
  [source]) on a printed body.
- **Front plate and rear clamp.** Printed, TPU-lined grooves; two hobby
  servos.
- **Housing press.** NEMA 17 Tr8×2 linear stepper (Iverntech, integrated
  240 mm screw with anti-backlash nut, $27.99 [prime: B094CRRSRQ]), a bar
  load cell with HX711, printed keyed holders for XHP-4/5/6/7/9 (into-the-housing
  i3), and a sprung guide comb.
- **Optional:** a B*n*B-XH-A header board (B4B-XH-A 171,802 at Newark,
  B9B-XH-A 44,226 at Digi-Key [source via into-the-housing]); the CQRobot kit
  also carries B2B/B3B/B4B-XH-A headers [prime: B0731NHS9R].

## Rests on

- **[source, analog]** XHP insertion 3–25 N per contact (Molex Mini-SPOX
  analog, clone spec ≤ 9.8 N); not public for XH.
- **[assumption]** A crimped contact sits in a 2.0 × 2.45 mm pocket with roll
  within a few degrees.
- **[assumption]** The lance faces the window side [xh-facts §3].

---

Citation keys: **[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[ith calc §n]** is its [`insertion_geometry.out.txt`](../../into-the-housing/calc/insertion_geometry.out.txt);
**[htq, K4]** is a combination in
[`hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
