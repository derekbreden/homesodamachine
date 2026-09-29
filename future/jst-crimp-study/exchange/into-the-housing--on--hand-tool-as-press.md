# into-the-housing on hand-tool-as-press

into-the-housing treats insertion as the dexterous step. What matters about a
crimp is the state it is in when it reaches the housing, and the moves that
get it there. This file reads
[hand-tool-as-press](../explorers/hand-tool-as-press/summary.md)'s eight
arrangements that way. It draws on the explorer's idea files, its
[notebook](../explorers/hand-tool-as-press/notebook.md), its
[calc output](../explorers/hand-tool-as-press/calc/hand_tool_press.out.txt)
and its sketch labels.

**Citations.**
- **[calc ex §n]** are numbers in
  [`../explorers/into-the-housing/calc/exchange_hand_tool_as_press.py`](../explorers/into-the-housing/calc/exchange_hand_tool_as_press.py),
  with output in
  [`exchange_hand_tool_as_press.out.txt`](../explorers/into-the-housing/calc/exchange_hand_tool_as_press.out.txt).
- **[ith calc §n]** are my wave-1 numbers
  ([`insertion_geometry.out.txt`](../explorers/into-the-housing/calc/insertion_geometry.out.txt)).
  What insertion needs from a crimp is in
  [`handover.md`](../explorers/into-the-housing/handover.md).
- **[htp calc §n]** are hand-tool-as-press's own numbers.

**Coordinates.** Y runs along the contact, with +Y toward the box nose.
"Floor side" is the side the lance hangs from.

hand-tool-as-press has worked out how a slow machine closes a bench tool. Its
far-end electrode array is the most useful sensor in the study for the
insertion view. The points below concern what happens around the nest and
after it:
- **The lance.** It hangs in the same half-millimetre as a1's flap blade and
  the anvil's front face (a1, a2, a2b, a3).
- **The crimp as it leaves the tool.** Its orientation and straightness (a3,
  a2, a2b, a5).
- **The first latch.** Once one contact latches, the ribbon is tied to the
  housing (a2c).
- **The gang push.** Where its force and its references belong (a3).

---

## Across a1, a2, a2b and a3: the lance lives in the neck

### The geometry

- **Where the lance is.** The XH retention lance is a tongue from the box
  floor. It hangs 0.6–0.9 mm below the floor, points rearward, and its tip is
  2.44 ±0.20 mm behind the nose on CJT's drawing [source S22; xh-facts §1].
  - The box is 2.00 mm long.
  - The transition from box to conductor barrel is 0.2–0.5 mm [estimate].
- **Where that puts the tip.** It lies anywhere from 0.26 mm in front of to
  0.44 mm behind the conductor barrel's front edge [calc ex §1]. a1 puts the
  flap blade in the same place, and the SN die's front face is there too.
- **What the neck has to hold.** Within 0.2–0.5 mm of Y:
  - the box's rear shoulder;
  - the 0.3 mm blade;
  - the brush;
  - below the floor, the lance tip.
- **Room left for the brush.** With the blade on the shoulder, it is −0.10 to
  +0.20 mm [calc ex §1]. That is a1's first open problem, now with the lance
  underneath it.
- **In hand use the lance must clear the anvil.** Hand crimps from the
  SN-2549 latch in kit housings [assumption: the bench procedure in
  `cable-assemblies.md` works]. So the lance hangs just in front of the
  anvil's front face, or in a relief, below the anvil's top. Either way it is
  a barb facing the anvil face from a few tenths of a millimetre away.

### What each machine motion does to it

| Motion | Where | What the lance does | Consequence |
|---|---|---|---|
| Box pushed +Y through the open nest with the contact low | a2 step 2 | Its slope rides over the anvil and folds, then springs out in front of the anvil face | One extra fold before the housing's own, and the contact is now latched on the anvil face |
| Back off −Y 0.2 mm to seat the shoulder on the blade | a2 step 2 | The lance tip may reach the anvil face first | Two axial stops compete. The blade on the shoulder gives ±0.08 mm [htp calc §7]; the lance on the anvil gives ±0.20. Whichever touches first sets the crimp's axial position |
| Proof pull of 20–25 N, flap down | a2 step 8, a3 step 5 | If the lance touches first, it carries the pull | That is 1.3–1.6× the analog lance retention minimum of 14.7 N [calc ex §4]. A bent lance does not show until the housing |
| Draw the crimp rearward out of the nest | a2 step 9 (and so a2c) | The barb meets the anvil face head-on | The draw stalls, or the lance folds flat and the contact never latches |
| Box pulled off a 0.64 mm post in the front stop | a1 post option | Moves −Y while the post holds it in Z | Same catch. The post has to retract +Y first |
| Contact enters the jaw barrel-first (the jaw moves +Y past it) | a3 pick | The lance leads into the anvil face | The contact stops at the face unless it is carried clear of the anvil and then set down |
| Contact falls box-first | a2b | Gravity, 0.42 mN, is 2,400–12,000× too weak to fold a lance [calc ex §3] | Any touch of the lance stops the drop. The passage must be 3.35–4.10 mm with the lance, against a2's ~3.5 mm [calc ex §2] |
| Ribbon raised to unload (the contact moves −Y) | a2b | Catches on the anvil's front face, which faces down | As in a2 step 9 |

This answers a2's open question, "whether a crimped contact's box passes back
out rearward": not while it sits low in the nest.

### Repairs, each a branch beside the original

- **R1. Lift before any −Y move.**
  - Raise the crimp out of the anvil cradle by the cradle depth plus the lance
    plus a margin, 1.0–1.7 mm [calc ex §2], then draw it back. The open SN
    jaw has several millimetres.
  - Changes: a2 step 9, a2b's unload, and a1's post option, where the post
    retracts first.
  - Uncertain: the anvil cradle depth, assumed 0.2–0.6 mm.
- **R2. Proof pull at hold.**
  - After the crimp, the pusher closes the tool again to a light hold. In a1b
    that can be at any position; in a1 it is the first tooth. The wire is
    pulled while the dies hold the crimped barrels.
  - Neither the blade nor the lance is loaded. What is tested is the strands
    in the barrel, which is the purpose of the pull.
  - Uncertain: whether a light die hold, tens of newtons against a
    kilonewton crimp, adds grip that flatters the result.
- **R3. Carry clear, then set down.**
  - In a2's load step, keep the contact's floor at least 1 mm above the anvil
    until the box is past the front face, then lower it.
  - In a3's pick, enter with the anvil at least 1 mm off the floor, then step
    sideways onto it.
  - The lance never folds before the housing folds it.
- **R4. Make the catch a check.**
  - With the tool open and the crimp low, a −Y nudge of 2–3 N has to meet a
    wall within the expected travel. That shows "lance present and sprung",
    tested against steel before the housing. It is my 3–8 N pull-back logic
    [ith calc §6] moved upstream. R1 follows.
  - Uncertain: whether the anvil edge scrapes tin from the lance tip. Keep it
    to a touch.
- **R5. Look at the neck.**
  - Take one frame at hold, looking across the neck. It shows the lance tip
    against the anvil face, the blade on the shoulder, and the brush length.
  - a4's open die set makes this frame easy. The SN head hides the floor side.

---

## a1 — the squeezer cradle

[a1](../explorers/hand-tool-as-press/ideas/a1-squeezer-cradle.md)

**The neck budget, with the lance.**
- The blade's slot straddles the floor strip, and the lance sits below it. The
  tines only need to reach the strip's lower face. The lance is narrower than
  the strip, so it passes between the tines.
- A tine–strip gap wider than one strand (0.08 mm) lets a strand drop past the
  blade toward the box or below the floor.
  - At 2.5 mm pitch a strand outside the barrel reaches a neighbour or snags
    the cavity entry [handover §4].
  - Fit the slot to the strip within ~0.05 mm a side. The strip's width is
    unmeasured.

**Transfer: judge the side photo against the housing.**
- a1 already takes a photo when the jaws open. The same frame can check what
  insertion needs [handover §2–4]:
  - Nose bend. 5° over the 2 mm box moves the nose ~0.2 mm, about one entry
    chamfer.
  - Roll within ±10–15° of barrels-up.
  - The closed insulation barrel inside the 1.95 × 2.4 mm end view
    [mfr S1], with the wing tips tucked (see a5 for how tight that is on
    1.7 mm silicone).
  - A cut-off tab of at most ~0.3 mm, for stub-fed contacts.
  - No strand outside a barrel, and the brush short of the box.
- Each failed check is a reason to cut the conductor back ~6 mm before the
  contact is buried in a housing, where it can no longer be seen.

**What this view takes from a1's hand-back: insertion, with the far-end block
still connected.**
- i5's nest sits beside a1: the real header, the spring-limited lever blade
  and the load cell. One ESP32 and one far-end block serve both.
- The block drives conductor k. When k's box slides onto post n, post n reads
  it. So the ESP32 knows which conductor is in which cavity:
  - J2's post 3 must never close;
  - J4's and J7's crossings are checked against the pin map.
- See combination C3.

---

## a1b — pawl out

[a1b](../explorers/hand-tool-as-press/ideas/a1b-pawl-out.md)

**How a partial crimp shows at insertion.**
- A stall or a power loss leaves wings that are not fully curled. Open
  insulation wings are 2.46–3.0 mm wide on clone drawings, which does not fit
  a 2.0 mm cavity; half-curled ones sit in between.
- The insertion push catches it as force rising before the lance fold [ith
  latch signature]. By then the conductor is committed to the housing.

**Branch: a closing gauge as a mechanical backstop.**
- Two laminated stencil-steel jaws on a spring close to the cavity's end view
  around the crimped barrels. The target is the 1.95 × 2.4 mm envelope
  [mfr S1]; the cavity itself is unmeasured.
- Fully closed, shown by a microswitch, means the crimp fits the housing. The
  gauge stays open on a partial crimp, a flared wing, a strand outside, or a
  spike of tab.
- It works without the controller. It restores the part of the pawl's
  guarantee that insertion cares about, that no half-crimp leaves. A
  half-crimp that does fit the gauge is a crimp-height problem, and the force
  curve covers that.
- **Where it sits.** a2's head carries each crimp through the gauge on the
  way out. At a1, the person drops the crimp in.
- **Uncertain.** The real cavity section, and whether clone and genuine
  housings differ.

---

## a2 — the ribbon comes to a fixed tool

[a2](../explorers/hand-tool-as-press/ideas/a2-ribbon-to-fixed-tool.md)

- **The lance.** Steps 2, 8 and 9 are covered in the table above, with
  repairs R1–R4.

- **Break: the fork's offset sets the copper** [calc ex §6].
  - Offsetting conductor k by 8–16 mm on a 20–35 mm free length bends it to a
    root radius of roughly 13–50 mm. Annealed 0.08 mm strands yield below
    ~67–78 mm.
  - So each conductor goes back into the comb with a kink, and the part ahead
    of the comb points wherever the kink leaves it.
  - For a person inserting by hand this is small. For any insertion of a
    whole row (C2 below), the noses and axes have to be squared again after
    crimping.
  - Repair: comb slots long enough (≥ ~8–10 mm) and close-fitting, to
    straighten the part ahead of the kink, plus C2's front plate and late
    clamp.
  - Uncertain: how far the silicone jacket springs a set 60-strand bundle
    back. A test: offset one conductor 12 mm for a minute, release it, and
    photograph it.

- **Break: the tab cut is a handover by the wire.**
  - Step 10 carries the crimped contact to the cutter squeezer on 5–8 mm of
    conductor ahead of the fork. Its roll and pitch there are whatever
    silicone torsion leaves.
  - That is the failure mode of the Sogang inserter, where cable transfer
    succeeded 43 times in 50, and it is i1's open "contact roll during the
    lift".
  - A flush cut to about one stock thickness needs the contact located again
    at the cutter.
  - **Branch a2-s: shear the tab at the crimp tool's rear face while the jaws
    hold.**
    - A spring-steel blade slides down the rear face, and the die's rear face
      is the shear's anvil. A servo drives it, at 40–100 N [htp calc §9].
    - The tab length is then referenced to the die, as in an applicator. It
      is a4's ram shear moved onto the SN head.
    - Shearing right after hold, before the fork brings the wire, also removes
      the "stub in the way" item from a2's own list.
    - Uncertain: whether the SN head's rear face is flat and square enough to
      shear against, and whether the blade has room beside the stub and the
      fork.

- **Where a2 ends, and what insertion does with it.** Its head already holds
  the web and every conductor in a comb, so it can act as a shuttle carrier.
  See C2.

---

## a2b — gravity

[a2b](../explorers/hand-tool-as-press/ideas/a2b-gravity-tool-flat.md)

- **The lance against gravity** [calc ex §2, §3].
  - The chute has to hold the lance off the anvil for the whole drop, and the
    open gap has to pass 3.35–4.10 mm.
  - Unloading goes sideways out through the mouth before the ribbon rises.
    That is R1 turned vertical.

- **Break: a hanging split conductor is not straightened by its own weight**
  [calc ex §14].
  - 25–35 mm of split conductor weighs 1.2–1.7 mN. Its weight makes 2–13 % of
    the moment that holds a 20–67 mm bend elastically, and a bend the copper
    has already set has no restoring moment at all.
  - So the tip hangs where its history puts it, and the fork and a
    close-fitting guide set its line.
  - The contact side of a2b stands: gravity does seat a 0.043 g contact on a
    stop. The wire side's "straightened by its own weight" is not so.

- **Combination: a2b's hanging row with a gang push from below.**
  - After the last crimp, the X–Z carriage holds every crimped conductor in a
    2.5 mm comb, tips down. It lowers the row onto a housing held rear-face-up
    in a nest on a load cell.
  - This is i3's gang push turned vertical, and a2b already has the Z axis.
    The needs are C2's: squared fronts, a rear clamp, and crossings laid by
    the person.

- **Transfer.** a2b's revolver is my printed carrier tape of pocketed
  contacts, arranged in a disc: orientation is forced by the pocket at
  loading.

---

## a2c — one baseplate, three stations

[a2c](../explorers/hand-tool-as-press/ideas/a2c-one-baseplate-strip-crimp-insert.md)

- **Break: the ribbon is tied to the housing after the first insertion.**
  - The order per conductor is strip k, crimp k, insert k.
  - Once conductor 1 latches in a housing held by the fixed nest, the head
    has to carry the ribbon back to the stripper and the crimper. Those
    stations are tens of millimetres away, and the split is 25–35 mm.
  - It cannot do that without dragging the housing out of the nest or pulling
    contact 1 back out. The loop stops at k = 1.

- **Break: the feed-length rule** [handover; ith calc §9].
  - Seating a contact from outside the rear face takes 7.45–7.85 mm of travel
    [calc ex §5]. The head holds the web.
  - **If the head advances to push,** every seated neighbour moves the same
    distance and bows 7.5–10 mm. The bow holds under 1.8 N, which does not
    threaten a latch, but it swings into the working space.
  - **If the head stays put and the finger pushes,** conductor k has to gain
    7.5–7.9 mm between the web and its contact. It can only do that from a
    stored hump.

- **Break: the finger does not fit the cavity** [calc ex §10; ith calc §4].
  - A seated contact's rear sits 0.2–1.25 mm inside the rear face. So the
    pusher's last stroke happens inside a 2.0 mm cavity.
  - The pusher has to be a slotted blade no wider than ~1.95 mm. Its slot is
    1.35–1.55 mm, squeezing the 1.7 mm wire, and its tines are 0.20–0.35 mm.
  - "~0.4 mm per tine" around a 1.45 mm slot makes a finger 2.25 mm wide,
    which does not enter.
  - The blade can be laminated stencil stainless (JLCPCB 304, from $3) or
    filed feeler-gauge leaves [ith].
  - It bears on the insulation barrel's rear edge, 0.17–0.27 mm per side
    [ith calc §2]. So the tab below it must already be cut to about one stock
    thickness.

- **Repairs, as branches. Both keep a2c's strip and crimp stations.**
  - **a2c-1: batch per ribbon end, one gang push at the end.**
    - Sequence:
      1. strip every conductor;
      2. crimp every conductor;
      3. the head lays each crimp into a 2.5 mm comb;
      4. a front plate squares the noses;
      5. a rear clamp closes 1–2 mm behind each insulation crimp;
      6. a fixed housing press drives the housing onto the row. It is i3's
         nest: a NEMA 17 on a 2 mm screw through a 20 kg bar cell.
    - No stored feed, and nothing is tied to the housing until the last move.
    - Hands back: laying J4's and J7's crossings in the comb.
    - Uncertain: whether the fork can still pick from a 2.5 mm comb. i3's fan
      plate can open the comb to 5 mm for picking and close it to 2.5 mm for
      the push.
  - **a2c-2: batch, then insert one at a time with a hump.**
    - Strip all, crimp all.
    - At the nest, each contact is set at its cavity entry with 7.5–7.9 mm of
      stored length. That is a hump 7.5–10 mm high over 20–35 mm
      [ith calc §9], held by the fork or a saddle. The web does not move, and
      the slotted blade pushes.
    - It keeps what a2c has and a gang push lacks: the head can route any
      conductor to any cavity. So the machine makes J4's crossing itself (the
      3P's GND to pin 2, over three 4P conductors).
    - Uncertain: the hump's shape in set copper, and the blade between seated
      neighbours.

- **Pairs.**
  - With a2c-1, a two-ribbon housing takes two partial gang pushes. The first
    ribbon goes into its cavities, then the second into the rest.
  - The first loom, up to 600 mm, hangs from the housing in its nest while the
    second ribbon is processed.
  - The other route is a3's: clamp both ribbons edge to edge and make one push.

---

## a3 — the tool travels

[a3](../explorers/hand-tool-as-press/ideas/a3-tool-travels-to-ribbon.md)

- **Break: every crimp is made rolled 90°** [calc ex §8; a3 sketch: "jaws
  close in X; nests run up the jaw"].
  - The comb runs in X and the jaws close in X. So the barrels open in X, and
    every lance points along the row instead of toward the housing's window
    face.
  - The lowered row still fits at 2.5 mm pitch: a rolled box is 2.2–2.4 mm
    across, leaving 0.1–0.3 mm gaps.
  - But no XHP can be pushed onto it. Its cavities need every lance on one
    face, perpendicular to the row.
  - Inserting one at a time, each conductor has to be twisted 90°. Over
    20–35 mm that is 2.3–4× the torsional yield strain of annealed 0.08 mm
    strands [calc ex §8]. Part of the twist stays, and the roll left after
    release is unknown.
  - Repairs, each a branch:
    - **a3-e: the fixture on edge.**
      - Turn the loom fixture 90° about Y. The ribbon plane is vertical, and
        the comb's slots stack in Z at 2.5 mm.
      - The lifter becomes a side-puller. It draws conductor k out of the
        ribbon plane in X, by the depth of the jaw half that lies between it
        and the ribbon plane plus ~1.9 mm.
      - The tip-down tool still closes in X, so the barrels open
        perpendicular to the ribbon plane. That is the insertion orientation,
        the same for every conductor.
      - The post column and the module are unchanged. The other conductors
        stay in the ribbon plane, behind the jaw.
      - Uncertain: the SN jaw's depth behind the usable nest, in the closing
        direction, is unmeasured. The pull-out also sets copper [calc ex §6].
    - **a3-t: twist and untwist.** A rotating lifter finger turns the tip 90°
      before the crimp and back after it. The flat fixture stays. Uncertain:
      the residual roll, the silicone-torsion question also open in i1.
    - **a3-c: a C-frame die set** (C5 below).

- **Break: lifting sets the copper and pulls the tip back** [calc ex §6].
  - A lift of up to ~3 mm on a 30–35 mm split stays elastic. a3's lifts reach
    9–20 mm [htp calc §8] on a 25–35 mm split, giving root radii of 10–45 mm,
    and annealed strands yield.
  - While lifted, the tip pulls back 1.4–9.6 mm. The touch-off happens in that
    state, so the crimp itself is right.
  - Lowered, a partly set conductor does not return fully. Its contact sits
    short by a fraction of the pull-back, up to ~1–2 mm, which is outside a
    ±0.3 mm front line.
  - **Repair (it also relaxes my own i3):**
    1. After the last crimp, a front plate pushes every nose back to one line,
       ~2 mm behind nominal.
    2. The extra length goes into the split as slack.
    3. A rear clamp closes 1–2 mm behind each insulation crimp.
    4. The plate retracts.

    The fronts are then set by the plate, not by strip lengths or by each
    conductor's lift history.
  - Uncertain: whether a finished loom with that slack bow looks acceptable.

- **Break: as clamped, the row buckles under a gang push** [calc ex §7].
  - With the tips 8 mm proud of the comb, 4.1–4.8 mm of conductor is free
    behind each contact.
  - At 8–14.7 N per contact, that exceeds the nose-guided (K≈1) limit of
    3.1–4.7 mm.
  - One fix is the rear clamp above, which leaves 1–2 mm free.
  - The other is a front guide that holds each nose square (K≈0.5, 6.2–9.5 mm)
    until the cavity lead-in takes over, then gets out of the way. My i3's
    sprung guide comb does that: the housing's approach presses it down and
    back.

- **The gang push belongs to the fixture** [calc ex §12].
  - J1 takes 27–225 N, and a belt gantry gives tens of newtons.
  - a3's own principle applies: close the force loop inside the thing that
    makes the force. The housing slide and the rear clamp sit on the fixture,
    and a NEMA 17 on a 2 mm screw (~280 N) drives the housing through a 20 kg
    bar cell.
  - The gantry brings the housing holder, or does not touch the housing at
    all.

- **Pin order is physical once the person has laid it.**
  - J4 needs at least 3 crossings (the 3P's GND goes to pin 2), and J7 at
    least 2 (the 5P's GND goes to pin 7) [ith calc §3].
  - In a3's comb, the crossing conductor lies over its neighbours behind the
    comb, laid by hand.
  - The far-end touch-off then catches a wrong crossing at the slide-on, when
    the conductor read differs from the pin map, before anything is crimped.
    My i3 had no such check.

- **What a3 already has.** Of hand-tool-as-press's arrangements, a3 alone
  crimps every contact where it will finally sit relative to the web. So the
  zero-feed gang push [handover] is open to it by construction.

- **The post column.**
  - Each contact gets one extra mating cycle, as in i5.
  - Wire each post as an input: continuity through the grounded tool shows
    which contact was taken and when its box left the post.

---

## a4 — the dies in a die set

[a4](../explorers/hand-tool-as-press/ideas/a4-dies-in-a-die-set.md)

- **One cut serves two needs.**
  - a4 narrows a jaw piece for strip feed: contacts sit 7–9.5 mm apart on the
    strip.
  - i3 needs an ordinary head that fits between shuttles at 5 mm pitch, with
    8.3 mm free between neighbour wires [ith calc §2].
  - A one-nest die piece 6–8 mm wide does both. At 7.5 mm pitch (13.3 mm
    free) the cut can be coarser.

- **What a narrowed die cannot reach: crimping in the row at 2.5 mm pitch**
  [calc ex §15].
  - The punch's side walls carry the lateral crimp pressure over ~0.9 mm of
    height.
  - At a lateral pressure of 160–900 MPa they need 0.47–1.12 mm each. That
    makes a punch 2.8–4.1 mm wide around a 1.9 mm crimp, against 3.3 mm free
    between neighbour wires.
  - Only the gentle end of the range fits. This bears on my i1b, i2 and i2b
    more than on a4.

- **Branch a4-c: a C-frame.**
  - a4's guided ram and eccentric go in a C-frame whose throat opens toward
    the web. The lower die sits at the end of a steel arm that reaches back
    over the row from in front of the tips.
  - The working conductor is lifted onto the lower die, and the neighbours
    pass under the arm.
  - The arm and the lift [calc ex §13]:
    - For 1.5–3 kN at 7–10 mm, a 6–8 mm wide arm needs to be 2.8–5.5 mm
      thick.
    - That calls for a lift of ~5–7 mm.
    - The barrels open up, in the insertion orientation, wherever the nests
      sit on an SN jaw.
  - Uncertain:
    - Arm deflection matters only if the dies do not bottom. It is ~0.02 mm at
      3 kN for a 5 × 8 mm arm 7 mm long [estimate].
    - A 5–7 mm lift on 25–35 mm still sets annealed strands a little.

- **Other transfers into this view.**
  - The open die set is where the neck frame (R5) and the lance check (R4)
    are easiest. Nothing surrounds the dies but two holders.
  - a4's pawl-fed strip and ram shear are the head's own contact feed, which
    my i1 lacks.

---

## a5 — the plier squeezed twice

[a5](../explorers/hand-tool-as-press/ideas/a5-two-squeeze-plier.md)

- **Bound: "gentle" has a floor, set by the cavity** [calc ex §9].
  - Take a 1.7 mm silicone conductor, uncompressed, inside a closed
    insulation barrel 1.9 mm wide in 0.2 mm stock. It forms an oval ~1.93 mm
    tall inside and 2.33 mm outside, against JST's 2.4 mm envelope. That
    leaves 0.07 mm to spare.
  - At a closed width of 1.8 mm it is 2.46 mm, over the envelope.
  - So the second squeeze's stop rule needs two limits:
    - a minimum closure (wing tips tucked, height ≤ ~2.3 mm) for the cavity;
    - the maximum that protects the silicone.
  - Silicone that flows out of a short barrel lowers the height [assumption].
    The kit housing's rear entry is unmeasured.
  - a5's separate insulation-crimp curve is the place to set both. a1b's gauge
    checks the result.
- **Scissor asymmetry.** Insertion's windows are a roll of ±10–15° and a nose
  bend of no more than ~5°. The side-photo transfer under a1 covers both.
- **The second placement, by the wire.** A roll of a few degrees is inside
  insertion's window.

---

## Combinations

**C1. a3-e with i3's gang push.** The tool travels over a fixture on edge,
and the fixture carries a housing slide.
- **hand-tool-as-press brings:**
  - crimping in place, with the tool as the gripper and nothing handed over;
  - touch-off and conductor identity through the far-end block;
  - the kinematic tool changer.
- **into-the-housing brings:**
  - the zero-feed gang push;
  - the front plate and rear clamp;
  - the sprung guide comb;
  - a 5 N pull-back on each contact;
  - a camera frame of the mating face.
- **Uncertain:** the pull-out distance, whether the slack looks acceptable,
  and recovering a jam in a nine-contact push.

**C2. a2's head as a shuttle carrier, with i3's housing press.**
- The head holds the web. Its comb sits at 2.5 mm, or on a fan plate that
  moves between 5 and 2.5 mm.
- After the last crimp: the front plate, the rear clamp, and then the head
  presents the row to a fixed press.
- **hand-tool-as-press brings:** the carriage, fork, touch-off and proof pull,
  and a2-s's tab shear.
- **into-the-housing brings:** the press, the guide comb, the pull-back and,
  optionally, C6's header.
- **Uncertain:** picking from a 2.5 mm comb. The crossings are laid by hand.

**C3. a1 and i5 on one bench, with one far-end block.**
- **hand-tool-as-press brings:** the block, touch-off, the force curve and the
  photo.
- **into-the-housing brings:** the header nest, the spring-limited lever blade
  and the tug test.
- The block drives conductor k, and post n reads it when k's box arrives. That
  gives the conductor-to-cavity pairing directly.
  - i5's blade needs no electrical path through the tin. That removes one of
    i5's open problems.
  - Each conductor gets one record, from its crimp curve to its seating trace.
- **The person** places contacts at a1 and starts each one into its cavity at
  i5.
- **Uncertain:** the post's grip against the tug test (i5's open problem).

**C4. a4 with a one-nest die, and i3's shuttles (or i1).**
- **a4 brings:**
  - an ordinary-width head with a die-force cell;
  - a fixed bottom set by geometry;
  - strip feed and a tab shear in the stroke.
- **i3's shuttles bring:** room at 5 mm pitch without lifting anything. i1
  gets its contact feed.
- **Uncertain:** the SN jaw seat geometry that a4 has to copy.

**C5. a4-c's C-frame, with a3's gantry or i1's lift.**
- A 5–7 mm lift instead of a nest-to-tip distance nobody has measured.
- The barrels open up, so the orientation is right.
- The lift still has to leave the neighbours clear, and for a one-at-a-time
  insertion i1 still needs its 8–12 mm of stored feed, now as a hump.
- **Uncertain:** where the arm's root sits relative to the neighbours'
  crimped noses, which reach 2.7 mm past their tips.

**C6. A header behind the housing during a gang push, with the far-end block.**
- The housing sits on a real B*n*B-XH-A header whose posts are wired, and
  that header-borne housing is pushed onto the row (C1 or C2).
- As each box slides onto its post, the ESP32 logs which conductor arrived at
  which post, and at what housing position. It scans every conductor against
  every post in under 2 ms, under 0.4 µm of push at 0.2 mm/s [calc ex §11].
- That gives each contact's arrival within one push, without i3b's stagger
  springs. The load cell still sees the lance events only as a sum.
- **Costs:**
  - one extra mating cycle per contact;
  - the post's mating force added to the push;
  - the mating face hidden from the camera.
- **Uncertain:** a box meets its post before its lance is home [ith
  notebook], so the latch still needs the pull-back.

---

## What hand-tool-as-press's view has not yet seen

- **The lance.** It is a failure made at the crimp station that shows only at
  insertion (the table above).
- **The finished crimp's orientation relative to the ribbon** (a3).
- **The first latch ties the ribbon to the housing,** wherever the housing is
  (a2c).
- **The feed-length rule.** Inserting one contact at a time while the web is
  held needs stored length, or the neighbours bow (a2c). A gang push needs
  none, and a3 gets that for free.
- **Copper set.** Every lift and offset of more than a few millimetres leaves
  it (a2, a3), and gravity does not undo it (a2b).
- **The pusher's last stroke is inside the cavity.** The last 0.2–1.25 mm of
  the insertion push happens there, so pushers are 0.2–0.35 mm stencil tines,
  not printed fingers (a2c).
- **The insulation crimp is also a fit to the cavity.** It has a minimum
  closure as well as a maximum (a5).
- **The gang push's force belongs to the fixture** (a3).

## What they hand back that this view can take

- **a1:** insertion, pin order and the latch. i5 with the far-end block takes
  them (C3).
- **a2:** insertion (C2).
- **a3:** "gang insertion if the gantry cannot push it". A press on the
  fixture with a guide comb and a pull-back takes it (C1).
- **a2c:** its insertion, as written, stops at the first contact. a2c-1 and
  a2c-2 carry it on.
- **J4's and J7's crossings.** In a2c-2 the machine makes them. In any gang
  push the person lays them in the comb, and the far-end touch-off checks
  them.
- **a1's unloading** ("lifts the flap and draws the crimped conductor out").
  With R1 and a comb to lay the crimp in, the finished ribbon end leaves the
  station protected rather than dangling.

## Where their work changes my ideas (for my revision)

- **i5.** The far-end block drives the conductor and the header post reads
  it. So the blade is a plain spring-limited pusher with no path through the
  tin, and the record pairs conductor with cavity instead of naming only the
  cavity.
- **i3 and i3b.**
  - C6 gives each contact's arrival electrically within one push. i3b's
    stagger remains the mechanical route to the same thing.
  - The fronts do not need strip and clamp on one reference. A front plate
    and a late rear clamp set them, with the excess going to slack.
  - i3's head can be a4 with a one-nest die.
- **i1.**
  - a4's open die set, strip pawl and ram shear form a head with its own
    contact feed.
  - A C-frame cuts the clearance lift to ~5–7 mm. The feed-length rule still
    asks for 8–12 mm stored, as a hump.
- **i2c.** The lance-catch reference is ±0.20 mm on CJT's drawing, against
  ±0.08 mm for the blade on the shoulder [htp calc §7]. So the stub holds X,
  Z and roll, and a blade on the box shoulder sets Y. a2's back-off step shows
  what happens when the two stops compete.
- **i1b, i2 and i2b.** The punch-wall estimate [calc ex §15] puts a narrow
  punch at 2.8–4.1 mm wide; ≤ 2.9 mm fits only at the gentle end. The
  narrow-tooling family needs a measured crimp force and a die-wall test
  before anything else.
- **i4.** a3's crimp module can be one of the tools on i4's kinematic mount,
  so the hand never places a contact into a nest. The far-end block gives i4
  touch-off and identity without vision.
- **handover.md** gains two lines:
  - "the lance is intact and sprung, never loaded rearward against steel at
    the crimp station";
  - "a crimp made with the jaws closing across the row is rolled 90°".

## Questions this exchange adds for Derek

1. With a kit contact in the SN-2549's XH nest and the jaws at one click,
   look from the side. Does the lance tip hang in front of the anvil's front
   face, and by how much?
2. Crimp one, open the tool, and draw the contact straight back without
   lifting it. Does it catch?
3. Offset one split conductor 12 mm sideways for a minute and let go. How much
   kink stays?
4. Caliper the closed insulation barrel of a crimp on the ribbon. What are its
   width and height, against 1.95 × 2.4 mm?
