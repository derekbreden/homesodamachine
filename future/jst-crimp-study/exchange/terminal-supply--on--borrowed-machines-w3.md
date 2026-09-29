# terminal-supply on borrowed-machines (wave 3)

The reader's view: how the contact arrives decides everything downstream. The
subject's view: somebody already mass-produces most of this, for another
purpose. This file pairs the two, breaks what the supply view can break in
borrowed-machines' wave-2 ideas (b1 revised, b1b, b1c, b2, b2b, b3, b6, b7, b8),
checks their numbers against the facts, and lists what crosses in each
direction.

procedure-is-the-machine's wave-2 critique already covers these, and they are
not repeated here:
- the pre-feed conflict on a fast press;
- the rod stack against a crank's push at bottom dead centre;
- the spring link;
- placing the contact from the front, barrels first;
- the fold as the person's largest step;
- the trim geometry of b1 and b3;
- b3's missing axial holder;
- b4's order;
- b5's backlash.

Numbers are in
[`../explorers/terminal-supply/calc/w3_on_borrowed.py`](../explorers/terminal-supply/calc/w3_on_borrowed.py),
with output in
[`w3_on_borrowed.out.txt`](../explorers/terminal-supply/calc/w3_on_borrowed.out.txt).
They are cited as [calc §n]. [wave2 §n] is this explorer's
[`wave2.out.txt`](../explorers/terminal-supply/calc/wave2.out.txt).
[Prime] means a row in [`../sourcing/amazon-prime.md`](../sourcing/amazon-prime.md),
observed 2026-09-28.

---

## 1. Combinations

### K1. The flat spool line: b8's spool, rip and gang push around a2d's crowned skip-pitch station

**What each side brings.**
- **b8** supplies:
  - the spool as carrier, with test through its inner end on a slip ring;
  - the belt feed whose retraction drives the needle rip, so the split root
    lands on the work clamp's face by geometry;
  - the whole-tip strip while the tip is still webbed;
  - the converging comb and the gang push of an XHP-4 from a tube;
  - cutting last, so a redo costs spool.
- **a2d** ([idea](../explorers/terminal-supply/ideas/a2d-skip-pitch-crown.md))
  supplies:
  - a strip with every other contact removed before the station;
  - a steel crown block (R 25–30 mm) whose crest land is a knife-set anvil;
  - tapered pins in the removed contacts' pilot holes, and a fence corrected
    from a picture of each waiting contact;
  - a one-sided drop-shear;
  - a level gate view across the station to a fixed backlight;
  - a bad contact sheared off with no wire in it.

**What neither does alone.**
- **b8 alone.** Its applicator's strip path is fixed, and fresh contacts
  stand on open wings 7.1 mm upstream. The only open side is behind the
  tooling, so b8:
  - folds all four conductors back into a band;
  - picks each with tines and swings the fork 180°;
  - re-parks it;
  - lays all four forward again for the comb.
- **a2d alone** needs a flat, split, stripped ribbon end presented in its
  crest plane, and gets it from a carriage the person loads.

Together:
- the ribbon never folds;
- the spool line supplies exactly the flat end a2d needs, with its root and
  strip line already in the work clamp's coordinates;
- the crown takes any width flat, so two spools laid edge to edge (p3b) put
  J1's nine conductors through the same station. b8's band leaves pairs
  uncovered.

#### Picture it

- **Where things start.**
  - **Spool.** A 4P spool sits on an axle behind the machine, its inner end in
    a spare XH housing on a 6-circuit capsule slip ring ($9.99 [Prime]). The
    free end is threaded through b8's belt feed, encoder, guillotine, needle
    bar and work clamp, all on one small X/Y stage (MGN12 rails with NEMA 17
    and T8 screws).
  - **Contacts.** Below the bench an SXH reel, or a clone reel, feeds up to
    a2d's crown block. On the rising run a servo punch cuts off every other
    contact. The contact's floor rests on a steel edge while the punch cuts;
    the removed contacts fall into a thinning cup.
  - **Press.** The crown block sits under a 1-ton arbor press: VEVOR AP-1,
    $61.90, 150 mm opening, 81 mm throat [Prime]. The press is turned so its
    column stands on the box side of the station. The feed head then comes in
    from the open side, behind the contacts, which is where a ribbon has to
    come from to slide in over the carrier.
  - **Drive.** A NEMA 17 on a Tr8×2 lead screw pulls the press lever, as in
    [a2](../explorers/terminal-supply/ideas/a2-strip-indexer.md). The punch
    holder lands on a hard stop on the crown block, with a disc stack for
    overtravel.
  - **Pedestal.** The crown block stands on a steel pedestal, so the strip
    arrives and leaves on tangents about ±40° from the crest and clears the
    press's 90 mm plate. Pedestal, crown and punch holder together must fit
    the 150 mm opening [estimate].
- **One T4 end.**
  1. **Feed, pierce, rip, clamp**, as b8 steps 1–4. The belts push the square
     end 14.4 mm past the needles and the needles pierce each web. The belts
     draw back 12 mm while the needles stay put, so the tear runs forward to
     the strip line. The pierce point, which is the root, now sits on the
     clamp face, and the clamp closes.
  2. **Strip.** Crown scores and a pinch pull take the still-webbed tip off
     as one slug (b8 step 5). The scoring blades need the depth limit in §2
     (b8), or b4b's diode heads do the scoring at the clamp.
  3. **Spread.** Nothing folds. A printed spreading comb slides from the clamp
     face toward the tips and stops on insulation short of the strip line. It
     is b8's converging comb run the other way: its slots go from 1.7 mm
     pitch at the root to *p* at the strip line.
     - **The pitch *p*.** The knife-set punch sets it. With the holder clear
       of the conductors, *p* ≥ punch half-width + neighbour half-width +
       0.3 mm, which gives **2.35–2.80 mm** for a 2.4–3.0 mm punch [calc §5,
       punch width an estimate].
     - **Movement.** The outermost 4P conductor moves 1.2–1.65 mm. Its root
       curvature is 1.7–2.3× strand yield, so it takes a partial set toward
       the housing's own fan: 1.2 mm for a 4P [calc §5].
  4. **Present.** The X/Y stage carries the flat, spread end into the crest
     plane. Conductor *k* slides forward over the carrier into the waiting
     contact's open U.
     - **Its neighbours.** They lie flat in the same plane over the crown's
       flanks, which sit 0.09–0.16 mm below the crest at ±*p* [calc §5].
     - **The next kept contact** is 14.2 mm away. It is rotated 32°, with its
       wing tips 1.2 mm below the plane at R 25 [wave2 §2].
     - **Axial position.** The stage steers by the insulation edge in the
       picture, as in a2d.
  5. **Gate.**
     - **Picture.** a2d's level view at wing height across the station.
     - **Continuity.** From the spool's inner end, through conductor *k*, to
       the grounded crown block. This is b8's gate, with the crown block as
       the electrode. It names the conductor and shows the strands touching
       the contact.
  6. **Stroke.** The press lands on its stop; the force trace is logged. The
     drop plate on the downstream half of the crest sinks 0.3–0.5 mm and
     shears the tab against the crown's own edge. The kink lies 11–12 mm
     downstream of the next station tab, in scrap [wave2 §9].
  7. **Proof pull and withdrawal.** The punch lifts, and a thin fork drops
     into the neck behind the box. The stage pulls conductor *k* back 20 N
     against it. This is b1's pull after the punch lifts, which tests the crimp
     and not the tool's grip. It is taken on the neck, not through a width
     slot, because the box is no wider than the crimped insulation barrel
     (§2, b1).
  8. **Index.** The stage draws the whole ribbon back behind the contacts'
     rear edge, because a kept contact's wings sweep through the crest plane
     as it rides up the crown [a2d]. The sprocket then advances two pitches,
     and the stage steps *p* in Y to the next conductor.
  9. **After four.** The stage carries the crimped row to the housing station
     beside the crown. The row is still at pitch *p*, with every contact
     placed on its own conductor.
     - The converging comb takes the row to 2.5 mm. The outermost 4P contact
       moves 0–0.45 mm [calc §5].
     - An XHP-4 from the tube is pushed onto all four at once, and each
       contact gets a 5 N pull-back.
     - The end is tested through the spool, fed out to length and cut
       (b8 steps 8–10).
- **What the person does.** b8's list:
  - load a spool (~5 min per 5–7 units' T4);
  - keep the housing tube full;
  - label, and empty the bins.

  To that it adds mounting the contact reel once and emptying three cups:
  thinning, reject and carrier scrap. At skip-2, all T4 over the program is
  0.30 of an 8,000 reel [calc §5].

#### What locates what; the reference for "fixed"

| What | Set by | Reference |
|---|---|---|
| Contact on the anvil | crest land, pins in the removed contacts' holes at ±7.1 mm, fence moved by each contact's own picture | crown block |
| Ribbon | work clamp; the root is placed on its face by the needle bar's 12 mm offset | X/Y stage |
| Conductor *k*, lateral | stage Y; the open U (clone wings 2.46–3.0 mm) takes ±0.2–0.8 mm [calc §4] | crown block via camera fiducials |
| Conductor *k*, axial | insulation edge steered into the window in the picture | crown block |
| Crimp height | hard stop between punch holder and crown block, optionally on a2's stepper wedge | crown block |
| Contact fronts at the housing | the strip line was scored while the ribbon was flat, so every contact sits the same along-conductor distance from the root | housing nest |

**Fronts do not depend on the crimp pitch.** Each contact is placed on its own
conductor relative to a strip line cut while the ribbon was one piece, so the
fan pitch at the crimp drops out. In the housing the outermost front lands
short by the housing fan's own amount [calc §2]:

| End (12 mm free length) | Outermost front short by |
|---|---:|
| 4P | 0.06 mm |
| 5P | 0.11 mm |
| J4 | 0.24 mm |
| J1 | 0.43 mm |

These are procedure's b1 numbers. J1 alone exceeds the ~±0.3 mm gang window.
A 20 mm free length brings it to 0.26 mm [calc §2]. That is 8 mm more
split, which is Derek's split-length question.

**What drives the crimp and carries its force.**
- The arbor press is rated 1 t, about 9.8 kN, against a 3 kN design crimp
  [digest].
- The force loop is punch holder → stop → crown block, not the press casting
  (a2).
- The crimp height is the stop's.

#### Contribution

- Nothing folds and nothing swings 180°. Each root is bent once, in the
  direction the housing wants.
- In b8 each conductor goes forward and back over the clamp face about four
  times. A residual kink of 5–15° at the root shortens a front by
  0.05–0.41 mm and varies conductor to conductor [calc §10]. That kink does
  not arise here.
- **One reel supplies two stations.** Skip-2 over the T4 program uses 2,400
  strip contacts and drops 1,200 loose ones into the cup. The other looms need
  1,980 crimps, so the cup covers 61 % of them with the same contact [calc §5],
  for a hand station making the rest: b2b stage 1, or
  [x1](../explorers/terminal-supply/ideas/x1-post-feeds-the-hand-tool.md)'s
  post pen. The crimp is qualified on one contact type.
- **Time.** ~10.6 min per T4 end, ~53 min a unit's five, unattended
  [calc §5, estimates].

#### Problems kept beside it

- **The die.** It is a knife set outside its applicator, so punch-to-anvil
  alignment in a guided holder is a2's open problem. The knife set comes only
  from eBay or AliExpress; no Prime listing was found ("OTP XH crimper and
  anvil blade set" [Prime]).
- **The pitch *p*** rests on the punch's outer width and how far it stands
  out of its holder. If the holder does not clear the neighbours, *p* is
  4–6 mm (a2d's rule). The fronts still hold by the table above. The comb then
  moves the outermost 4P contact 2.3–5.3 mm, and the spread sets harder.
- **The applicator's feed, locate and shear become separate mechanisms:**
  thinning punch, pin lever, sprocket, fence, drop plate. See K6 for putting
  them back on one shaft.
- **The spreading comb** must bear on insulation only, stopping before the
  strip line, or it drags stripped strands.
- **J4 and J7 crossings** are not made, as in b8. J2's unused conductor is
  trimmed at the root by recipe (b1's cutter).
- **Tab stub** from the drop on a crown: a2's open question.

### Other combinations, named more briefly

- **K2. b1b/b1c × a1's supply-side gate.**
  - **Look first.** The waiting contact is photographed alone, before the fork
    moves: lance, roll, wings and bellmouth line against the anvil fiducials
    ([a1](../explorers/terminal-supply/ideas/a1-applicator-slow-ram.md)
    point 7).
  - **Reject turn.** A bad contact gets a turn with the fork idle. The crank
    crimps it empty and shears it. An air blow-off in the dwell (after the
    crimpers clear at ~226°, before the feed at ~274°) [calc §6] clears it
    off the anvil into a reject cup. The valve is a TAILONZ 24 V 5/2, $16.99
    [Prime]; the compressor is on hand [repo].
  - **Crimp-height sweep.** A 2–3° stepper wedge under the applicator base
    [wave2 §8] lets the machine sweep crimp height in 0.02 mm steps on the
    production die and then hold it, while the crank still sets bottom dead
    centre.
  - This is also the repair for b1c's back-out break (§2).
- **K3. b2/b2b × x1's post head.**
  - A 0.64 mm post in the box replaces the printed tweezers. The holder face
    is the box-front datum, a stripper sleeve releases the contact, and a
    silhouette on the post corrects each contact's axial position.
  - With loose kit contacts on a6's pocket plate, b2b keeps one contact type
    from stage 1 to stage 5 (see b2b's break below). The post pen is a stage 0
    needing only a header pin and two prints.
  - For strip contacts, a6's strip pick puts the post in the lead box and cuts
    the tab from above against a steel edge before any wire exists [wave2 §6].
- **K4. b1b's jack test × a7's supply question: one jack test, two contacts.**
  - **Two supplies through one die.** Thread the vendor's reel, crimp, section
    and pull. Then thread one Digi-Key 100-piece genuine SXH strip
    (455-1135-100-ND, $4.71 [xh-facts §6]) through the same feed and do the
    same.
  - **What it answers:**
    - which contact the OTP die is cut for;
    - whether genuine carrier pitch fits the feed's pitch screw;
    - whether genuine wings clear the V of b1's ram finger (§2, b1).
  - **Two more looks in the same session:**
    - a side photograph across the anvil at wing height (a1's line-of-sight
      question);
    - where the feed finger stands when the post-feed ends (§2, b1).
- **K5. b5's Dobot MG400 × a6's post head.**
  - The ±0.05 mm arm is the post head's gantry. It picks kit contacts from the
    pocket plate, measures them in silhouette and sets them on an open
    knife-set anvil. The same arm then presents the ribbon.
  - That is Kurabo's pattern with the post as the only custom end effector.
  - What it costs: $2,890–3,495 (b5) against a secondhand printer's axes.
- **K6. b1c's one shaft × a2d's supply motions.**
  - On one shaft: the thinning punch, the pin lever, the two-pitch sprocket
    advance, the drop plate and the press stroke. The contact side is then
    timed the way an applicator's cam times it.
  - The ribbon side stays on steppers, because it steers by picture.
  - It returns to K1 the single-drive order that the applicator gave b8.

---

## 2. What still breaks in their revised and new ideas

### b1 (post-feed with a ram finger)

**The waiting contact is never seen alone, and a mis-feed arrives under a
conductor already on its way down.**
- **The conflict.** In post-feed the anvil is empty at rest. The contact
  slides in on the downstroke, under a conductor held with its centre 4.6 mm
  above the barrel floor. The ram finger then seats the conductor into
  whatever arrived.
  - The before-image shows a conductor over an empty anvil.
  - On the fast press, nothing is seen between feed and crimp.
- **Consequence.** A rolled, doubled or half-fed contact is crimped onto
  conductor *k*. The redo is a whole-end cut-back of ~6 mm. procedure's
  recovery calc puts that at 0.4 to 35 looms scrapped over the program at 2 to
  10 % bad [procedure calc recovery_length].
- **The supply sets the mis-feed rate.**
  - An 8,000 reel from the applicator's vendor is threaded once.
  - Digi-Key cut strips (100 per bag, ~1.9 units each [digest]) are a
    threading event every 1.9 units, and strips kinked in the bag are what a
    feed finger mis-indexes.
- **Repairs.**
  - Run b1 from a reel only.
  - Look one pitch upstream, at the contact waiting on the carrier at rest.
    Whether the strip guides leave its barrels visible is a1's line-of-sight
    question, and it comes with the part.
  - Move to b1b's stoppable crank, where pre-feed shows the contact alone.
- **Uncertain.** The OTP unit's mis-feed rate, and the lines of sight in its
  feed track.

**The ±0.4 mm lateral window is a clone number.**
- **The numbers.** b1's table allows ±0.4 mm for the insulation entering the
  open insulation wings. The clearance per side by supply [calc §4]:
  - clone wings, 2.46–3.0 mm ±0.25: +0.21 to +0.83 mm;
  - Würth analog, 2.30 mm: +0.25 to +0.35 mm;
  - JST's 1.95 mm catalog envelope, if that is the open width (unresolved,
    xh-facts §1): +0.08 to +0.18 mm.
- **Consequence with genuine SXH inside its envelope.** The ram finger's V
  pushes the jacket down onto a wing tip, and the insulation crimper folds
  that wing onto the top of the jacket or cuts it.
- **Repairs.** The vendor's clone reel, which the OTP die is likely cut for
  anyway [a1, assumption]. Or a V whose centring is tighter than ±0.1 mm.
- **Uncertain.** Genuine open-wing width; one Digi-Key strip settles it.

**The catch plate has no width window.** The same plate serves b1, b1b, b1c and
b8.
- **The plate as written.** b1's catch plate is "a slot narrower than the
  1.9 mm box and wider than the crimped barrels".
- **Width.** The box is 1.85–1.95 mm wide and the crimped insulation barrel
  ~1.8–2.0 mm, a margin of −0.15 to +0.15 mm [calc §11; xh-facts §1,
  estimates]. For some contact and wire combinations no slot width exists; for
  the rest the box bears on a sliver of its wall ends.
- **Height** has margin. The box is 2.2–2.4 mm tall and the crimped insulation
  barrel ~1.8 mm (clone spec [digest]), so the box's roof stands 0.4–0.6 mm
  proud.
- **The lance.** It stands 0.6–0.9 mm below the floor, with its tip pointing
  rearward over the neck. A plate reaching below the floor meets it end-on, as
  a housing shoulder does. A 20 N pull there is an unrated retention test on
  the part that must later latch [xh-facts §3].
- **Consequence as written.** The box passes the slot and the pull reads
  nothing, or the pull lands on the lance.
- **Repairs.**
  - A plate whose edge sits ~2.0 mm above the floor, bearing on the roof's
    rear edge.
  - Or a thin fork dropped into the neck. Behind the box the crimped
    conductor barrel is only ~1.5 mm wide and ≤1.1 mm tall, which is a6's
    proof-pull fork. Either stays above the floor.
- **Uncertain.** The real insulation crimp width on this ribbon; the five
  SN-2549 or jack-test crimps give it.

**The feed finger's envelope over the wire path** [assumption; nothing
published shows it].
- **The geometry.** The pilot holes lie on each contact's centreline, under
  the wire's path [digest]. In post-feed the conductor already hangs over that
  line when the finger moves. Near the barrels its underside is ~3.75 mm above
  the floor, and it slopes down toward the root at 14–25°.
- **The risk.** If the finger engages the station contact's own hole, or its
  lever stands more than ~3 mm above the carrier, the finger hits the held
  conductor, or lifts it before the ram finger arrives.
- **Settled by** the jack test (K4), watching the finger's end position with
  a conductor held at 4.6 mm.

### b1c (one shaft)

**The gate's "no" has no safe exit.**
- **The timing** [calc §6]:
  - b1c's table puts the pre-feed advance at ~266–285°. The crank formula
    puts the ram 15–20 mm up at 274–293°.
  - A cam-driven feed lever's position is a function of ram height
    [assumption, WERI-pattern cam]. The finger therefore retracts to the next
    hole on the downstroke at ~67–86°.
  - That falls inside the fork's lay-in (20–80°) and just before the foot
    (80–110°), which are before the gate at 115°.
- **What each response does.** The fork and foot are driven by cams on the
  crank's own shaft, so neither can leave the conductor without the shaft
  turning.
  - **Forward:** the crimp at 145–180°.
  - **Back to 0°** (b1c's "backs the shaft out"): the shaft passes 86→67°
    again. The finger re-advances the strip one pitch under a laid-in,
    footed conductor. That is b1's Break 1, re-created by the back-out.
- **Consequence.** A contact or conductor that fails at 115° is either crimped
  anyway or shoved sideways with a conductor in it. Only the second is
  recoverable, and it may jam the feed finger out of its hole (Mecal's rule
  [prior-art §3]).
- **Repairs**, and each can stand alone:
  - **(a) Latched followers.** Solenoid-latched cam followers on the fork and
    foot levers let them drop to park at the gate. The shaft then goes
    forward as a reject turn (K2): empty crimp, shear, and an air blow-off
    between 226° (crimpers clear) and ~274° (feed).
  - **(b) Gate before the band.** Move lay-in and seating to finish by ~60°,
    with the gate at ~62°, so a back-out never crosses 67–86°. That compresses
    the fork's 180° swing into ~40° of shaft.
  - **(c) Skip pin.** Restore p5's skip pin, which b1c dropped as unneeded for
    trims. It decouples the ram for a turn; the fork cycle then parks the
    conductor untouched. The bad contact still needs (a)'s blow-off on the
    turn after.
- **Uncertain.** Whether the OTP feed lever really follows ram height. Stroke
  the jack slowly downward and watch the finger.

**A bad waiting contact has no disposal path in b1b either.** b1b's gate is at
top dead centre, with the contact and conductor both in view.
- **The problem.** If the contact is the fault, the shuttle's fork can lift
  the conductor away, since it is not cam-bound. The contact can only leave
  the anvil by a stroke, and a stroke with no wire leaves a crushed empty
  contact on the anvil. The pre-feed then pushes the next contact into it:
  Break 1 with no conductor to withdraw.
- **Repair.** K2's blow-off in the dwell, and the look at the contact alone
  before the fork lays in, so no conductor meets a bad contact.

### b2 (hand crimper in a frame, strip-fed)

**The drop-shear cannot be reacted by a gripper on the box.**
- **The load.** b2 shears the tab by dropping the carrier while "the gripper
  is the die", with printed tweezers on the box.
  - The tab needs 48–158 N [xh-facts C1].
  - Its root is 4.8–5.7 mm behind the grip [calc §1, clone lengths].
  - So the grip must resist **230–905 N·mm**.
- **What resists it.**
  - The neck between the box and the conductor barrel has a plastic moment of
    ~4.5–66 N·mm, depending on its width and wall height [calc §1,
    estimates]. The shear moment is 3–200× that.
  - Tweezers squeezing at 1–5 N resist ~0.3–2.7 N·mm by friction.
- **Consequence.** The contact bends at its neck, or turns in the tweezers,
  before the tab shears. The result is a bent contact with its tab still on,
  or a torn tab and a rolled contact.
- **Repairs.**
  - **A steel fixed edge under the insulation barrel's rear.** Its lever to
    the tab root is ~0, with a guided steel drop blade beside it. The printed
    track cannot be the fixed blade [digest: printed parts are not die faces].
  - **The hinge line** of the drop section 2–3 mm upstream of the station tab.
    The 1.5 mm drop's kink then moves into scrap after one index
    [wave2 §9]. The scrap then leaves as a staircase with 1.5 mm steps, which
    needs a free exit.
  - **Or cut from above before the wire exists,** with a post in the box and
    the floor on a flat steel track (a6's strip pick, [wave2 §6]).
- **Uncertain.** The stub length. It is the fixed edge's position relative to
  the contact's rear, set from carrier geometry nobody has measured (one
  strip).

**The "SMT-style" sprocket** (b2's strip track; b3's feeder).
- **The mismatch.** The carrier's pilot holes are Ø1.5 mm, the same as 8 mm
  SMT tape's sprocket holes. Their pitch is ~7.1 mm, not tape's 4.0 mm
  [calc §9; EIA-481 values an assumption].
- **The bend.** A printed sprocket at 7.1 mm with 8 teeth has a 9 mm pitch
  radius. A 0.2 mm carrier wrapped round it runs at 1.1 % strain against
  0.41–0.59 % yield. It needs ≥22 teeth (R ≈ 25 mm) to stay elastic
  [calc §9].
- **Consequence.** A carrier set at every contact arrives at the pick with
  the lead contact rolled. That is the roll problem the carrier-as-datum is
  meant to remove.
- **Repairs.** A pawl on a flat run, which is the applicator's own feed
  finger. Or a large sprocket with the carrier tangent to it and not wrapped.
  A tapered pin in a neighbour's hole at the pick also makes the pick's
  position independent of sprocket backlash (a2's pins).

### b2b (pedal-less hand station)

**The contact changes between build stages.**
- **The change.** Stages 1–2 crimp loose kit contacts from a keyed flap.
  Stages 3–5 crimp SXH from strip.
  - The kit contacts are probably clones: their drawn wings are 2.46–3.0 mm,
    against JST's 1.95 × 2.4 envelope [xh-facts §1; a7].
  - The strip is genuine unless a clone reel is bought.
- **Consequence.**
  - The first-week sections and pulls qualify the SN-2549 on one contact.
    Stage 3 puts a different wing width and barrel length in the same nest,
    and needs a different strip length (§3), so the qualification starts
    again.
  - The b7 nozzle's stop plate changes setting with it.
- **Repairs.**
  - **(a) Clone strip.** A clone reel: LCSC CJT A2501-TP, 665,523 at $0.0079
    [xh-facts §6]. First check whether kit contacts carry tab stubs [a7]. If
    they do, they were cut from a reel, and the same maker's reel is the kit
    contact on strip.
  - **(b) Loose throughout,** with K3's post head in place of the strip
    feeder.
  - **(c) Genuine BXH loose from stage 1:** Digi-Key 137,303 at $0.0444
    [xh-facts §6].

**The actuator the plan counts on is not the one on Prime.**
- **What b2b counts on.** ~500 N at ~15 mm/s, with position feedback for the
  captive stop.
- **What Prime has** [Prime]:
  - Justech: 1,500 N, **7 mm/s loaded**, limit switches, self-locking, **no
    feedback**, $29.99.
  - Progressive Automations PA-01-POT: 750 N with a potentiometer, $155.39,
    no ratings.
- **Consequence with the Justech.**
  - Closing and opening each take ~5.7 s over b2's ~40 mm of handle travel,
    not ~2.7 s. The ~20 s cycle becomes ~26 s, and Derek's ~17 s share waits
    on it.
  - "Captive" needs its own position sensor: an AS5600 on the handle pivot,
    $7.99 [Prime].
- **The PA-01-POT's 750 N** is 1.8× the spring link's 410 N preload at a
  handle ratio of 8, so it carries the link.

### b3 (gantry-borne head)

**The stepped trim is taken off conductors that are already stripped.**
- **The order.** The person lays split, stripped conductors into the fan
  grooves, then trims each tip against its step. The steps are the
  outermost's excess length [procedure calc §6]. At 4.35 mm fan pitch they
  remove:
  - 4P: 0.54 mm;
  - 5P: 1.06 mm;
  - J4: 2.27 mm;
  - J1: 3.80 mm.
- **What that leaves** of a 2.4 mm strip: 1.86, 1.34 and 0.13 mm, and
  nothing for J1 [calc §2].
- **Consequence.** b3 stops the strands at a neck blade, so each trim moves
  the insulation edge forward by the trimmed amount. For 5P and wider, the
  insulation goes under the conductor barrel, a JST fault [xh-facts §5]. For
  J1 the trim cuts into the jacket.
- **Repair.** Flush-cut and strip while the ribbon is flat and still one
  piece: b6's rip then the whole-tip slug, or b4's scores. The neck blade then
  puts every contact the same along-conductor distance from the root, and the
  fan pitch at the crimp drops out.
  - In the housing, the outermost front lands short by the housing fan's own
    amount [calc §2], at b3's 20 mm free length: 4P 0.04, 5P 0.06, J4 0.14,
    J1 0.26 mm. All are inside ±0.3 mm.
  - The steps, the per-loom step geometry and the person's trimming against
    them all go. The fan grooves only fan.
- **What remains.** The converging comb has further to travel from 4.35 to
  2.5 mm pitch: 2.8 mm for the outermost 4P conductor and 3.7 mm for the
  outermost 5P. The fan leaves a set, which the comb straightens.

**The feeder** is §2 b2's sprocket.

### b8 (spool-fed line)

**Flat crown blades closed to a fixed stop** (b8 step 5; b6's whole-tip strip).
- **The budget.** The blade's height is set from the clamp, so the ligament
  left over the strands varies by:
  - the bundle's radius and offset: 0.345–0.43 mm from the conductor's
    centre;
  - the conductor centre's height in the clamp: ±0.05 mm [estimate].
- **The ligament** left over the strands [calc §8]:

  | Score depth (of the 0.49 mm wall) | Ligament left |
  |---:|---|
  | 70 % | +0.03 to +0.21 mm |
  | 80 % | −0.02 to +0.16 mm (a nick in the worst case) |
  | 60 % | +0.08 to +0.26 mm |
  | 50 % | +0.13 to +0.31 mm |

- **Consequence.** At 80 % a few outer strands are nicked on some ends; at
  70 % the worst case leaves 0.03 mm. The force monitor cannot see one strand
  [digest], so the backlit stub picture must catch it.
- **Repairs.**
  - Score 50–60 % to a stop. The tip pull then rises to ~4.7–13 N a conductor
    (borrowed geometry §3, 60 % row), still carried by the clamp.
  - Or run the blades on a shoe riding the jacket's top, so the centre-height
    error drops out. That is b7's centring point applied to a flat blade.

**The fold kink at the gang push.**
- **The kink.** Each conductor's root is bent back over the clamp face at
  R 1.5–2.5 mm about four times (b1's count), and copper keeps a set
  [digest].
- **What it costs.** A residual kink of 5°, 10° or 15° shortens that front by
  0.05, 0.18 or 0.41 mm at 12 mm free length [calc §10]. The angle differs
  conductor to conductor.
- **Against the window.** The 4P housing fan already uses 0.06 mm of the
  ~±0.3 mm gang window.
- **Repairs.**
  - A straightening pass: the converging comb run root to tip twice.
  - Or K1, where nothing folds.
- **Uncertain.** The real residual angle. Fold a split 4P end back and forward
  four times and photograph it.

---

## 3. Consistency

1. **The strip length belongs to the contact in the die, and b-files pair
   JST's length with a clone reel.**
   - **Where 2.4 mm is used:**
     - b1, b1b and b8 buy "the reel from the applicator vendor", which is
       probably a clone [b1 item 4];
     - b4 scores at 2.4 mm;
     - b6 stops at 2.4 mm;
     - b7's tip stop is at 2.4 mm;
     - b8 feeds 12 + 2.4 = 14.4 mm.
   - **The clone contact** has an estimated conductor barrel of 1.25–1.5 mm,
     a window of 0.6–1.0 mm and a neck of 0.4–0.6 mm [xh-facts §1, calc §3].
     On it, 2.4 mm gives:
     - **edge-steered:** a 0.40–0.85 mm brush past the barrel, which reaches
       the box over most of the range;
     - **tip-stopped at a 0.25 mm brush:** the insulation edge 0.65–0.90 mm
       behind the conductor barrel. That is at the rear of the window or
       inside the insulation barrel, so the 50/50 look fails.
   - **At the clone spec's 1.85–2.1 mm** both land in range.
   - **Which is right.** Neither number is universal. JST's 2.4 mm [xh-facts
     §1] fits JST's own, unpublished, barrel lengths, and the clone spec fits
     the clone. b7 lists the disagreement as open; the coupling to the reel is
     the point here. The strip length is a per-reel recipe value in every
     stripper, score line and needle offset.
2. **b2's "anvil channel (1.68–1.90 mm open)" is the contact's own open
   conductor-barrel width** from clone drawings [xh-facts §1], not a
   measurement of the SN-2549's nest. procedure's critique repeats it.
   - **If the nest passes an open barrel up to 1.90 +0.25 mm,** it is as wide
     as the 1.85–1.95 mm box. The box then passes, and the "shoulder stops
     against the die face" backup does not exist.
   - **If the nest's floor is the crimp width (~1.3–1.5 mm),** the box stops.
   - The number cited does not decide it. x1's open question ("is the box
     outside the jaw's front face?") is the same measurement.
3. **b1c's "~190 samples through compaction at a 40 s turn [p5 calc]"** comes
   from p5's eccentric, whose compaction spans 22°
   [procedure `cam_drive.out.txt` §4].
   - On b1b's 15 mm crank and 100 mm rod, the last 0.2 mm is 8.74° [borrowed
     presses §1].
   - That gives **~78 samples** at 80 Hz on a 40 s turn [calc §6]. b1b's own
     figures of 19 at 10 s and 39 at 20 s scale to the same.
4. **b1c's angles.** By the crank formula:
   - the crimpers clear the box (4 mm up) at 226°, not 220°;
   - the feed advances (15–20 mm up) at 274–293°, not 266–285° [calc §6].

   The cams are printed from these, and the jack test replaces both with
   measured angles.
5. **b1's lateral window** of ±0.4 mm holds for clone wings only [calc §4];
   see §2.
6. **b8's strip pull**, "~15–45 N for four conductors: 4–11 N each [calc
   geometry §3]", is borrowed geometry §3's 80 %-score row. At the 50–60 % a
   fixed-stop blade can hold (§2), the 60 % row gives 4.7–13 N each, or
   19–52 N for four. That is still under the clamp's reach and the 85–100 N
   conductor break [xh-facts §1].
7. **Prime status, against what the b-files still mark "Prime to be
   confirmed"** [Prime]:
   - **No Prime listing** for:
     - the 1.5–2 t press (b1's "Amazon listing … Prime to be confirmed");
     - the OTP side-feed applicator (b1, b1b, b3);
     - the OTP knife set (a2, a2d, K1);
     - XH reels;
     - the benchtop sensor stripper (b7's bought machine);
     - the Bambu laser module (b4).

     Every applicator route in b1, b1b, b1c, b3 and b8, and my a1, is eBay
     ($80–90 shipping) or Made-in-China (freight quoted).
   - **The 10:1 NEMA 23 planetary** (StepperOnline, $48) is rated 10 N·m
     permissible and 20 N·m momentary. b1b's 10.8 N·m at the crank is at that
     limit, and the 20:1 variant's rating was not read.
   - **Heavy disc springs are not on Prime.** Only a light stainless M3–M12
     Belleville assortment is, which cannot make b1b's ~4 kN stack.
     - DIN 2093 A25, A28 and A31.5 cannot reach a 4 kN preload.
     - One A35.5 preloaded to 4 kN has 0.15 mm left to 5.2 kN, at ~8 kN/mm.
     - **Two A35.5 in series** give 0.30 mm at ~4 kN/mm, which is b1b's
       "~4 kN, ~4 kN/mm" [calc §7].
     - The NEMA 23 + 10:1 stalls at 4 kN for any obstruction met above
       ~0.16 mm over bottom dead centre, so ~0.16 mm of stack travel is what is
       needed [calc §7]. The same stack serves my a1.
   - **Wiper motor.** The Prime wiper-type gearmotor (BEMONOC, 6 N·m rated) has
     no park switch. b1b's wiper branch relies on one, and on ≥12 N·m stall.
   - **Frames.**
     - The VEVOR AP-3 3-ton arbor press ($255.90) opens 310 mm with a 130 mm
       throat. It is the first Prime-confirmed frame that opens past an OTP
       applicator's 166–176 mm, for b1b's "arbor press with a motor on the
       pinion" and for my a1.
     - The VEVOR AP-1 (150 mm) takes a knife-set block only, as the Harbor
       Freight 1-ton (139.7 mm) does.
   - **SN-2549:** $22.29 [Prime], against b2's $20.99 at iCrimp; no conflict.

---

## 4. Transfers

### From the supply view into theirs

- **Cut the carrier before the wire exists, against a steel edge at the tab
  root.** The cut goes from above or by a drop, and its line is set from the
  contact's own rear edge as seen [wave2 §6]. It goes to:
  - b2's drop-shear (§2);
  - b2b stage 3;
  - b3's head shear, where the captive pinch across the barrels already holds
    the contact near the tab.
- **Look at the waiting contact alone, and reject it with no wire in it.**
  → b1b and b1c: K2, with the blow-off in the dwell. It is also the repair
  for b1c's trapped gate.
- **A stepper wedge under the applicator base.** The crank fixes bottom dead
  centre and the wedge raises the anvil by 35–52 µm per mm of travel. It is
  self-locking at 2–3° under 3 kN [wave2 §8].
  - It goes to b1b, b1c and b8.
  - The machine sweeps crimp height on the production die in 0.02 mm steps,
    finer than the dial's ~0.05 mm.
  - Genuine and clone contacts become two stored wedge positions, not two
    dial settings made by hand.
- **The post in the box as the pick tool** (a6, x1) → b2's tweezers and b2b's
  keyed flap. The contact type then stays the same across b2b's stages (K3).
- **Skip-pitch strip over a crown** → b8 (K1). It removes the fold, band,
  tines and fork swing.
- **The strip length as a per-reel recipe value** → b4, b6, b7 and b8 (§3
  item 1).
- **One-sided drop with the kink carried into scrap:** the hinge line 2–3 mm
  upstream of the station tab [wave2 §9] → b2's hinged drop section.
- **The tab-stub check on kit contacts** (a7) → b2b's decision at stage 3.
- **Tapered pins in a neighbouring pilot hole at the pick** (a2) → b2's and
  b3's feeders. The pick's position then does not depend on the feed drive's
  backlash or the carrier's pitch error.

### From theirs into the supply view

- **b1's pre-feed conflict applies to my a1 as written.** a1's stroke sequence
  ends "on the way up, the cam advances the strip one pitch" while the
  carriage still holds the crimped contact on the anvil.
  - a1's screw ram can dwell: stop with the ram ~4–6 mm up, where the
    crimpers have cleared the box. The carriage withdraws the crimp ≥7 mm and
    pulls it against a catch plate, then the ram finishes.
  - The stop has to come before the feed band, at 15–20 mm up [b1b].
  - a2 and a2d avoid it, because their ribbon is drawn back before every
    index.
- **b2's spring link applies to my a2c and x1.**
  - Their NEMA 17 on a Tr8×2 screw pushes 280–380 N at the handle. At a
    handle ratio of 20 that is up to 7.6 kN at the die once the ratchet has
    released at full closure, 2.5× the 3 kN design [borrowed presses §4].
  - a2c's "the ratchet guarantees full closure, so the actuator needs no
    position accuracy" is true of closure and silent on overload.
  - x1's pusher carries hand-tool-as-press a1's load cell, so a software stop
    at force exists there. a2c states none.
  - Repair: the spring link, preloaded to ~1.25× the handle need, which makes
    the cap mechanical. Or the driver's current set so that stall thrust is
    ~1.25× the handle need.
- **b1b's jack test is my a1's first-week bench,** and the place a7's
  genuine-or-clone question is answered (K4).
- **b1c's one shaft** → a2d's supply motions (K6).
- **b8's root-placing rip, whole-tip slug and through-spool continuity**
  → a2d (K1).
- **b2b's identity check through the far end** → the gates of a2d and a6. The
  anvil or crown block is the electrode, so continuity at the gate names
  conductor *k* and shows its strands touching the contact before the stroke.
- **b3's V-fork on the head's rear face** → a2d and a6.
  - A V closing on the insulation behind the carrier line gives the conductor
    its lateral position mechanically.
  - The picture is then needed only for the axial position, not for the
    0.7-of-the-error visual servo in both axes.
  - Open: whether a V fits between the carrier line and the ribbon's root.
- **b1's order for the proof pull** (punch lifted first, then pull on the box)
  → a2d and K1, made with a neck fork (§2, b1's catch plate).
- **b7's blade rule** (die-hole or a centred rotary blade, not V-blades) → any
  strip station feeding a2d or a6. A flat blade to a stop obeys the same
  budget (§2, b8).
- **The sourcing record** [Prime]:
  - no OTP part is on Prime;
  - the VEVOR AP-3 (310 mm) is a Prime frame for a1;
  - the VEVOR AP-1 (150 mm) is a Prime frame for a2, a2d and K1's knife-set
    block.
