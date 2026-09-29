# procedure-is-the-machine on borrowed-machines

Wave 2 exchange. The reader's view: the sequence and the division of labor are
the design. The subject's view: somebody already mass-produces most of this, for
another purpose. The purpose is to make b1–b5 more useful: to break specific
variants, repair or branch them, bring transfers, and propose combinations.

Numbers are in
[`../explorers/procedure-is-the-machine/calc/exchange_borrowed.py`](../explorers/procedure-is-the-machine/calc/exchange_borrowed.py),
with output in
[`exchange_borrowed.out.txt`](../explorers/procedure-is-the-machine/calc/exchange_borrowed.out.txt).
They are cited as [calc §n]. Every input not taken from xh-facts, the digest or
the borrowed-machines calcs is an [estimate] or [assumption], and is printed
beside its result.

---

## Across the set

### A. Free space around a carrier-fed anvil

The digest's strip geometry settles more than it first appears to. The side-feed
carrier joins at the rear of the insulation barrel, in the contact's floor plane,
with pilot holes "on each contact's centreline, under the wire's path". So every
conductor lying in the row at the target's X also lies over the carrier strip.

That fixes the space around an applicator anvil while the strip is attached
[calc §1]:
- **Below the anvil level:** strip, track and shear. No neighbour can drop down
  there.
- **Above:** the punch.
- **Upstream** (feed-in side): the next contacts stand on the carrier with open
  wings, 3.2 mm tall, at the carrier pitch (~7.1 mm, Würth analog).
- **Downstream:** only empty carrier.

Consequences:
- **b1's fold-back parking** is the one in-row arrangement in the whole study
  that is compatible with a strip-fed applicator. The neighbours leave through
  the only open side, which is behind the tooling.
- **b3's fan works because b3 cuts the contact free first.** Fanned neighbours
  over an attached strip meet the waiting contacts. At 4.35 mm fan pitch and
  7.1 mm carrier pitch, the second and third upstream neighbours lie on the next
  contact's open wings.
- **b2 cuts the contact free as well**, so its die is surrounded only by the
  hand tool's jaw plates.
- **My p1 and p5 slotted presser**, which drops the neighbours ~7 mm, does not
  work over an attached strip. See *Where their work changes mine* below.

### B. The person's attended minutes, counted one way for every row

borrowed-machines counts person time as the busy seconds at its own stations.
Here the whole procedure is counted, with one task library (the one in my
`person_timeline.py`): cut, split, strip, load, crimp or present, insert,
label. The absolute minutes are high: the same library gives 46 min for XH work
alone, against the ledger's 45 min for every harness. Compare the rows with each
other [calc §5, estimates]:

| Row | Attended min/unit |
|---|---:|
| Today, by hand | 46 |
| b1: hand split/strip, 60 s fold per end, hand insertion | 52 |
| b1 + b4: 80 s per end at the laser | 54 |
| b1 + a fold-back lid, 5 s per end (below) | 39 |
| … + b1's insertion extension | 34 |
| … + in-pose score and peel, no flips, no comb (below) | 24 |
| b2 hand-presented: 30 s cycle, insertion afterwards | 60 |
| b2 hand-presented, inserting contact *k*−1 during cycle *k* (p4) | 53 |
| b2 + 15 mm/s actuator (20 s cycle) + p4 soft clamp + pipelined | 44 |

What the table says:
- As written, b1, b1 + b4 and b2 hand-presented **move the person's minutes
  rather than remove them**.
  - The crimp (~13 min by hand) is exchanged for folding (~14 min).
  - b4's laser session (~19 min) takes about as long as a hand peel and strip
    (~16 min).
  - A person-paced cycle longer than a hand crimp adds minutes.
- What they buy is consistency, a log, the contact out of the person's fingers
  and, for b4, a datum.
- Minutes fall when these leave the person:
  1. folding;
  2. splitting and stripping;
  3. insertion.

  Each has a mechanism below. This is the same finding as my p4, now shown on
  their arrangements.

### C. Cut-first means a redo costs loom length and a second trip

Every b-arrangement starts from cut ribbon ends in cassettes. A bad crimp can only
be redone as a whole end cut back ~6 mm [my calc recovery_length §1], so each
redo:
- shortens the loom;
- extends the split (8–15 mm, and b1's clamp edge must again land exactly on
  the root);
- with b4, sends the end back to the laser (a module swap if the batch is
  over).

With a 12 mm length reserve per loom, 0.4 (at a 2 % bad-crimp rate) to 35 (at
10 %) looms are scrapped over the program [my calc recovery_length §3]. The OTP
applicator's quality on 1.7 mm silicone is untested, so the rate is unknown.
Terminate-first, cut-last (my p3) makes a redo cost spool only. It fits b1's
press as well as it fits my own benches (Combination C4).

---

## b1: bought press and applicator, printer-axis shuttle

### Break 1 (sequence): the pre-feed runs while the fork, foot and crimped contact are still on the axis

- **The conflict.** b1 steps 5–7 run in this order:
  1. the relay fires, and the applicator crimps, shears and feeds;
  2. the foot lifts and the shuttle backs off 12 mm;
  3. the fork returns the conductor.

  A pre-feed applicator (the setting b1 needs, so that a contact waits at rest)
  advances the next contact **on the upstroke** [prior-art §3, TE 408-32162].
  It slides in Y into the X-range that the crimped contact and its conductor
  still occupy.
- **Why the conductor cannot move.** A hand-held wire is shoved aside. b1's
  fork is fixed on the applicator axis and the foot is still down, so the
  conductor cannot yield.
- **Consequence.** One of these, or a mix:
  - the feed finger jams or leaves its pilot hole (Mecal's rule: it "should
    never come out of the hole");
  - the incoming contact rides over the crimped one;
  - the fresh crimp is levered sideways against the fork.
- **Timing** [calc §2]:
  - The window between "punch and hold-down clear the box" (~4–6 mm up)
    and "feed finger starts" (~15–20 mm up, [assumption]) is 36–65° of
    crank.
  - On a ~0.5 s press cycle that is 50–90 ms.
  - Lifting the foot, opening the fork and withdrawing ≥7 mm takes ~0.6 s
    [estimate].
  - It does not fit.

**Repairs and branches:**
- **R1, dwell in the window (b1b only).** A stoppable crank stops anywhere from
  40° to 105° after BDC. Then:
  1. the foot lifts;
  2. the fork opens;
  3. the shuttle withdraws the crimped contact ≥7 mm, which is also where the
     20 N catch-plate pull fits;
  4. the crank finishes the turn and the feed runs with the anvil empty.

  This is a sequence repair that only a slow drive allows. The bought fast
  press cannot take it unless it has an inch or stop-at-top-of-crimp mode,
  which is unknown for the Sanao class.
- **R2, compliant fork.** Mount the fork on a flexure or spring slide that
  yields at least one carrier pitch in Y. The incoming contact then shoves the
  crimped conductor aside, as a hand-held wire moves, and the shuttle withdraws
  afterwards.
  - It keeps b1 on the bought press.
  - It gives up the fork's lateral reference only after the crimp.
  - Uncertain: the feed spring's push [unmeasured], and whether the crimped
    box snags the incoming wings.
- **R3, post-feed cam.**
  - **How it runs.** The contact slides in on the downstroke. The fork and foot
    must hold the conductor ~3.2 mm above the anvil, over the wing tips, and
    the punch's descent carries the conductor into the wings.
  - **What it changes.**
    - The before-image can no longer show "strands in the barrel".
    - The lateral reference at first die touch becomes the fork alone.
    - Whether the OTP punch or its wire guide pushes a held conductor down
      cleanly is unknown.

What stays uncertain in all three: what the OTP unit does with a crimped contact
still in place at the feed (it arrives with the part). Setting the cam to
pre-feed or post-feed and watching one slow jack stroke (the b1b jack test)
shows it.

### Break 2 (reference): trimmed straight at the datum, housed at 2.5 mm, the outer contacts land short

b1's tips are trimmed at the cassette datum with the split conductors straight at
ribbon pitch. At the housing they diverge to 2.5 mm, so each outer conductor's
path is a diagonal and its front lands short [calc §7]. For J1, the outermost
lands:

| Split length | Outermost front short by |
|---:|---:|
| 8 mm | 0.67 mm |
| 12 mm | 0.43 mm |
| 15 mm | 0.35 mm |

- J4 is 0.37 mm short at 8 mm.
- A single 4P or 5P is 0.05–0.16 mm short.
- Gang insertion wants fronts within ~±0.3 mm [into-the-housing, via digest].

With per-conductor insertion (b1's extension), the shortfall becomes tension,
which peels the web root a little further. That is probably harmless, but it
works against b1's own rule that the root sits exactly on the clamp edge.

- **Repair:** trim in the pose of the finished housing. For J1, J2 and J4 the
  cassette's trim slot is a per-loom curve, offset by these amounts.
- **Uncertain:** whether a curved slot and a flush cutter hold ±0.05 mm.

### Break 3 (person): the fold is the largest person step, and it rests on a parking fan nobody can load fast

- **The step.** b1's person folds each split conductor 180° into parking
  grooves that fan to ~4 mm pitch, so the fork's tines have room. That takes
  ~60 s per end, ~14 min per unit (B above).
- **Can a lid do it?** A grooved lid that fans the conductors as it closes
  catches a conductor in its own groove only if the local groove pitch is
  below:

  | Conductor, counted from the centre | Groove pitch must be under |
  |---|---:|
  | 1st | 3.40 mm |
  | 2nd | 2.27 mm |
  | 3rd | 2.04 mm |
  | 4th | 1.94 mm |

  [calc §12]. A one-shot lid into 4 mm grooves mis-sorts every conductor beyond
  the first neighbour.

Branches:
- **B3a, valley tines, no parking fan.** Split conductors touch only along a
  line and are free to shift sideways. Two blunt steel tines (0.2–0.3 mm shim)
  1.7 mm apart ride down the V-valleys either side of the target and wedge each
  neighbour aside by a tine thickness.
  - The parked group can then lie back as one flat band.
  - The lid needs no grooves: it folds the whole split end back over the clamp
    edge in one motion, which the person does in ~5 s or the shuttle does
    against a ramp.
  - Uncertain: whether blunt tines enter without notching the silicone, which
    tears from notches.
- **B3b, split on demand, edge first.** Leave the web joined by a thin ligament
  (a partial laser slit, b4, or a shallow valley blade). The fork peels only the
  edge conductor, at ~1–5 N [calc §9], and the clamp edge is where the peel
  stops, so it is the root by construction. The rest stays a ribbon, which
  folds back or up as a single flap. Details under Combination C3.

Either branch takes b1's person step from ~60 s to ~5 s per end: the 52 → 39 min
row in B.

### Insertion extension: crossings and trimmed conductors are an order problem

- **Crossing order.** J4 (3P's GND to cavity 2) and J7 (5P's GND to cavity 7,
  past CLO and CHI) are not in ribbon order [digest]. The extension indexes the
  housing 2.5 mm per cavity while the fork lays conductors forward by root.
  - The crossing conductor must lie over the others.
  - **Order rule:** insert the crossing conductor **last**. Every other
    conductor is then already tethered in the plane, and the last one the fork
    lays forward lands on top.
  - The recipe carries an insertion order separate from the crimp order.
- **Trimmed conductors.** J2's and J7's trimmed conductors are "conductors the
  fork never takes", so they stay parked at full length in the finished loom.
  A cutter at the clamp edge, run by the recipe, trims them at the root.
  Otherwise the person does it at loading, as in my p1 (with a printed blank in
  the key).

### What b1 contributes that this view had missed

- The fold-back park is the carrier-compatible neighbour strategy (A).
- The catch plate proof pull holds the contact by its box after the punch has
  lifted. That tests the crimp's grip.

---

## b1b: the OTP applicator in a slow crank press

### The dwell window: a property of b1b that its text does not use yet

b1b sells the slow crank on the force curve and stop-before-bottom. From the
sequence view, its larger gift is that **the ram can wait at any angle while
something else happens**:
- b1's pre-feed conflict is repaired by R1;
- the proof pull fits in the same dwell;
- a camera frame of the crimp can be taken with the punch clear and the contact
  still in place.

**The wiper-motor branch loses this.** Its park switch makes one uninterruptible
~1.2 s revolution, a window of ~0.12–0.22 s at 50 rpm. It therefore inherits
b1's conflict, and needs R2 or R3.

### Break (force): the stepper does not stall safely near bottom dead centre

- **The claim.** b1b tried "stepper stalls at bottom" and answered with a ~2×
  torque margin and step recovery.
- **The physics.** Near BDC a crank is a displacement source: ds/dθ → 0, so any
  obstruction met there is pushed through with whatever force the loop
  stiffness demands. Obstruction is the obstruction's own force; add the
  ~3 kN crimp [calc §3].
- **The numbers.** Crank r = 15 mm, rod 100 mm, 10.8 N·m (NEMA 23 + 10:1):

  | Obstruction height above normal BDC | Loop stiffness | What happens |
  |---:|---:|---|
  | 0.1 mm | 100 kN/mm | passes BDC at 10 kN |
  | 0.2 mm | 40 kN/mm | passes BDC at 8 kN |
  | 0.4 mm | 20–100 kN/mm | stalls early, at 3–4 kN |

  The shop press frame is probably near the stiff end [b1b estimate].
- **Reading it.** The drive stalls on tall obstructions, where the crank still
  has little mechanical advantage. It sails through short, stiff ones: a
  doubled contact (+0.2–0.4 mm of stock), a folded strand bundle or a carrier
  scrap. A 0.1–0.2 mm obstruction is met in the last 0.1–0.2 mm, where compaction
  happens anyway, so the force curve cannot flag it early enough to stop.

**Repair, from b1b's own ball-screw branch:** put a disc-spring stack in the
connecting rod, preloaded above the crimp peak (4 kN preload, ~4 kN/mm
[estimate]).
- Below 4 kN the stack does not move, so crimp height is untouched.
- Above it, force never exceeds 5.4 kN in any case computed [calc §3].
- A switch on the stack's travel is a genuine "stop at force" signal.

Uncertain: whether the OTP punches survive 5 kN on a doubled contact. They are
made for 15–20 kN presses [assumption].

### Transfer and combination: the one-shaft applicator press (b1b × p5)

See Combination C1. b1b's notebook names "printed cams on b1b's crankshaft" as a
loose end; my p5 is that machine, and the two fit.

### The jack test is a stage 0 for more than b1b

The shop press jack stroking the applicator is useful the week it is done, on
its own:
- real crimps on the real ribbon;
- sections;
- pull tests;
- feed timing and whether the feed pushes a crimped contact aside (Break 1).

Every applicator-based arrangement, and my p1 bench B, can start from it.

---

## b2: the hand crimper in a frame, fed from the strip

### Break 1 (force): a stalled actuator puts 5–7× a hand's force through a hand tool

- **The problem.** The 1,500 N actuator's "5–19× margin" becomes a load case
  once the dies bottom. The actuator keeps pushing until its motor stalls or its
  own end-of-travel switch trips. The switch does not sit at the tool's closed
  position.
- **The numbers** [calc §4]:

  | Handle-to-die ratio | A hand's ~300 N at the die | Actuator stalled at 1,500–2,000 N, at the die |
  |---:|---:|---:|
  | 8 | 2.4 kN | 12–16 kN |
  | 20 | 6.0 kN | 30–40 kN |

  The pivots and stamped frame are sized for the hand column.
- **Repair: a spring link** between the actuator clevis and the handle.
  - It is preloaded to ~1.25× the largest handle force the crimp needs: ~160 N
    at a ratio of 20, ~410 N at 8. That caps the die force near 3.2 kN.
  - A microswitch on the link's travel gives "tool closed" by force.
  - That replaces the ratchet's "no half crimps" guarantee when the pawl comes
    out, as b2 proposes for jams.
- **Uncertain, and tied to the digest's open question.** If the SN-2549's jaws
  do not bottom die-on-die, then a force-limited close makes crimp height
  follow force. That is the objection b2's own notebook raised against battery
  lug crimpers. Crimp height then has to come from the actuator's position. A
  0.5 mm handle resolution through a ratio of 8–20 is ±0.025–0.06 mm at the
  die: borderline against ±0.05. Holding the closed tool to a light settles
  which case applies.

### Break 2 (geometry): the contact cannot be lowered into the nest from above

- **The conflict.** With the tool on edge, the upper die sits directly over the
  lower nest in plan. A gripper that "swings down" to place the contact meets
  the upper die. The jaw opening is a few millimetres, and the open wings are
  3.2 mm tall.
- **What works.** The approach that works is the one a person uses: along the
  contact's axis, **from the box side**, barrels first, into the gap between the
  open dies. The gripper holding the box outside the front face fits that
  motion exactly.
- **The blade then has to move.** A fixed blade in the barrel-to-box gap blocks
  a barrels-first entry.
  - It drops in after the contact is placed, like WC-110's flap.
  - Or it is not needed: b2's own reasoning says the anvil channel
    (1.68–1.90 mm) is narrower than the box (1.85–1.95 mm). If so, the box's
    rear shoulder stops against the die's front face, which is an axial
    locator for free.
- **Uncertain.** Whether that shoulder position centres the barrels in the
  SN-2549's die sections. One contact, the tool and the ELP camera settle it.

### Break 3 (person): "10 s of attention per crimp" is 20–30 s of presence per crimp

b2 hand-presented has a 30 s machine cycle [borrowed cycle_and_arm]:
- 16 s to feed, cut, place and go captive;
- 7 s to close;
- 7 s to open.

The person must be there for every one of the 53 cycles, so the crimp phase is
~27 min attended, against ~13 min of hand crimping [both estimates]. With the
whole procedure counted, b2 hand-presented is 60 min against 46 today
[calc §5].

Repairs, from p4:
- **Pipelining.** Insert contact *k*−1 while the machine feeds and places for
  *k* (→ 53 min).
- **A faster actuator.** The force margin allows it: 500 N at ~15 mm/s is
  still 1.5–12× the handle need. Close and open take ~2.7 s each, for a ~20 s
  cycle.
- **p4's soft clamp.** TPU V-jaws close on the insulation once the strands are
  at the stop, so the person lets go before the close. Busy time falls to
  ~5 s present + 8 s insert.

Together: ~44 min. The minutes saved are small. The contact leaves the person's
fingers, which is what Derek asked for most. The division of labor is then
explicit: the person splays and pokes, and the machine feeds, places, crimps and
keeps the order.

### Transfer: make the blade an electrode, and the far end the identity check

This builds on hand-tool-as-press's far-end terminal block and ribbon-as-pallet
a6's pogo pins on the cut face.
- **Setup.**
  - The person clips the far end's cut face into a pogo comb.
  - The blade is insulated from the contact on its box-facing side (Kapton on
    the feeler leaf).
  - The blade is mounted in its printed bracket, insulated from the tool.
- **Two signals come free:**
  - far end → tool body means strands are touching the contact;
  - far end → blade means the strands have reached the stop.
- **What they give.** The second signal fires the close, so no pedal is needed.
  The channel that lit up says **which** conductor was poked, so:
  - J4's crossing is enforced (the station refuses 4P#2 when cavity 2 wants
    3P#1);
  - J2's skip is enforced;
  - an open after the crimp shows before the contact leaves the tool.
- **Uncertain.** Contact resistance of light strand-on-steel touches: ohms, not
  milliohms, which is fine for a 3.3 V input with a pull-up [estimate]. Also
  whether Kapton survives the box shoulder's pressure.

### Combination: the pedal-less hand station (b2 × p4)

See Combination C2.

---

## b3: a printer gantry carries a narrow crimp head to a fanned ribbon

### Break 1 (reference): crimping on the fan and trimming on a straight line makes the outer conductors too long in the housing

- **The mechanism.** b3's fixture fans the split conductors to 3.6–5.35 mm with
  their tips on one line. Each outer conductor carries its fan diagonal as extra
  length. Converged to 2.5 mm in the housing, that extra shows as a bow behind
  the housing, or as fronts that are not in line [calc §6, b3's 20 mm split,
  8 mm straight cantilever].
- **At 4.35 mm fan pitch:**

  | End | Outermost conductor too long by | Bow behind the housing |
  |---|---:|---:|
  | 4P | 0.54 mm | ~2 mm |
  | 5P | 1.06 mm | ~3 mm |
  | J4 (7) | 2.27 mm | ~4 mm |
  | J1 (9) | 3.80 mm | ~6 mm |

  At 3.6 mm the 4P is +0.26 mm and J1 +1.97 mm.
- **Consequence.**
  - b3's per-conductor insertion seats every contact and leaves the bows.
  - Gang insertion, which would avoid b3's lateral drag of 6–10 mm, is
    impossible for 5P and wider, because the fronts are 0.5–3.8 mm out of line
    against ±0.3.
- **Repair: a stepped trim edge** on the fan fixture. Each groove ends short of
  the common line by that conductor's excess, and the person, or a trim blade on
  the head, cuts each tip to its step.
  - After crimping, a converging comb slides forward from the root and brings
    the contacts to 2.5 mm with their fronts in line.
  - The housing then slides on all at once (my p1 bench C).
  - That removes the "piano key" clamp release, the drag and the second clamp
    bar for buckling.
- **What it leaves uncertain.**
  - Whether ±0.05 mm per step holds with hand trimming.
  - Whether the comb can converge crimped contacts, with boxes 1.95 mm at
    0.55 mm gaps, without snagging.

### Break 2 (reference): nothing in the head holds the captive contact axially

After the head's shear cuts the tab, the contact is held only by the punch's
captive pinch on its wing tips. The conductor slides in axially. If the strands
catch the conductor barrel's rear edge (b3's own open problem), the pinched
contact is pushed forward along the anvil and the brush and window are lost.
The camera sees it only after the fact.
- **Repair: b2's blade, in b3's head.** A thin leaf in the barrel-to-box gap,
  on the head, locates the contact axially and stops the strands. The captive
  pinch then only holds the contact down.
- **A second repair from this view:** a V-fork on the head's rear face that
  closes on the insulation ~3 mm behind the strip line as the bed advances. The
  8 mm cantilever's wander of 0.2–1 mm under a light touch [my calc
  selector_and_bow §4] is then replaced by the fork's own capture, and the
  camera map becomes a coarse guide.

### What b3 hands back that this view would take

- **Laying each end into fan grooves** (60–90 s per end). A still ribbon at a
  work clamp, fed from the spool (p3), removes it.
- **The J4/J7 crossings**, which the fixture does not address. With
  per-conductor insertion, b3 can make the crossing by order: insert the
  crossing conductor last, as in b1. With the converging comb, the crossing is
  made in the comb at loading (my p1 loft).

### Transfer to b3 from p2

p2 (still ribbon, tools come to it) and b3 are one arrangement reached from two
views. b3's contribution to p2 is concrete: a harvested-blade C-frame head that
picks from a **fixed** feeder, so p2's turret does not carry a reel. p2's
contribution to b3 is the per-conductor order (strip, crimp, look, insert, then
the next) and the idea that the housing drops below the row between insertions.

---

## b4: a laser slits the webs and scores the strip line

### Break 1 (geometry): the slot comb cannot enter at ribbon pitch

- **Why.** The comb's slots (1.0–1.2 mm) must straddle whatever is left at the
  score, and its teeth must pass between conductors. At 1.7 mm pitch the split
  conductors still touch flank to flank.
- **The ±45° flank passes do not reach the flank at that pitch.** A 45° beam
  reaches the 90° flank only if the pitch is above 2.05 mm; a 60° beam only
  above 2.55 mm [calc §8].
- **So at ribbon pitch** the flanks stay full wall, the neck at the score is
  1.7 mm wide, and there is no gap for a tooth.
- **With the conductors spread to 2.5 mm** and 45° passes, the neck is
  ~1.3–1.4 mm wide, the gap between necks 1.1–1.2 mm, and a comb with
  1.4–1.6 mm slots fits. The comb plate must then sit in a kerf, so the score
  has to be rastered ~0.6 mm wide and the plate be steel shim, not a print.

**Branches:**
- **B1a, pinch pull.** Leave the comb out. TPU pads close lightly on the slug,
  forward of the score, one conductor at a time (my p1 bench A, or p4's clamp
  pull).
  - With top and bottom scores only, b4's own figure is ~4–11 N per conductor
    and the tear goes to the score.
  - No flank passes, no tilt dock, one flip.
  - Uncertain: slug-to-strand friction under the pinch adds to the pull
    [estimate: a few newtons].
- **B1b, spread first.** Fan to 2.5 mm in the cassette, then score all round,
  then use the comb. The cost is that the conductors are free cantilevers when
  scored (next break), and the fan's trim geometry (b3 Break 1) returns if the
  spread exceeds housing pitch.

### Break 2 (order): the second slit frees the conductors before the second score

- **As written:** slit top, score top, flip, slit bottom, score bottom. The last
  score lands on conductors that the bottom slit has just freed. They are then
  10–20 mm cantilevers, which may splay as the ribbon relaxes, and the beam
  aims at the crown.
- **Reordered:** score top, slit top to mid-plane, flip, score bottom (the web's
  lower half still holds pitch and plane), slit last. Every precise line is
  then cut while the ribbon is still a pallet.
- **What it costs:** nothing. What it changes: flank access (Break 1) needs a
  spread, which conflicts with scoring while webbed. B1a resolves it by not
  scoring the flanks.

### Break 3 (person): 80 s per end at the laser is about the hand peel and strip it replaces

- **The minutes.** b4's person time (load 30 s, three flips 30 s, pull and brush
  20 s, per end) is ~19 min per unit. A hand peel and strip is ~16 min by my
  library [calc §5, estimates]. Its value is the **datum**: split root and
  insulation edge at known distances from the cassette. That is exactly what
  the crimpers' axial reference needs (below), but it does not save minutes.
- **Repair, the laser at the station.** Two small diode modules, one above and
  one below a stationary clamp (p1 bench A, or p3's work clamp at the spool),
  score both crowns with no flip. The H2C stays printing. The tear follows as
  pinch pull B1a.
- **Uncertain:**
  - diode scoring on this silicone (b4's own first open problem);
  - Class 4 enclosure and interlock at a bench station;
  - fume venting.

  Amazon modules go to my sourcing requests, Prime to be confirmed.

### Transfer: a partial slit makes "split on demand" possible

b4's slit can stop short of severing, leaving a 0.05–0.2 mm ligament:
- the ribbon stays a ribbon;
- one conductor peels off along its slit at ~1–5 N (tear strength 15–25 N/mm
  [Primasil via b4], [calc §9]);
- an unscored web of 0.4–0.6 mm [assumption] needs 6–15 N and tears where it
  chooses.

That turns splitting into a per-conductor step inside the crimp loop (C3), and
the clamp edge becomes the root by construction.

### The redo path

A crimp failed at b1, b1b or b2 means:
1. re-clamp 6 mm further out;
2. trim;
3. go back to the laser.

With the H2C module that is a module swap or a held batch. An in-pose laser at
the station, or p3's cut-last order, keeps a redo local.

---

## b5: a desktop arm as the operator

### Break: b5's 5 mm lead-ins are smaller than b5's own 6 mm RSS backlash

b5's calc gives 6.0 mm RSS (11.2 mm worst) of tool-tip wander from STS3215
backlash, and docks "with 5 mm lead-in" to absorb it.
- **Repair: approach every dock the same way**, descending with the same
  payload.
  - Gravity then loads each joint the same way.
  - Taught waypoints absorb the backlash.
  - What remains is repeatability: ~1.2 mm RSS, 2.2 mm worst, inside 5 mm
    [calc §13, from b5's numbers].
  - A flip reverses gravity on the wrist only, 0.15–1.2 mm.
- **Uncertain:** the tail's varying weight (≤15–20 g against a 50–150 g
  cassette [estimate]).

### What the arm is carrying, in procedure terms

- **Carrying is the one step that costs the person least.** The arm automates
  the carrying between steps. The person's largest steps in every
  b-arrangement are loading, folding and the fan fixture.
- **Each of the arm's own justifications has another route:**

  | Justification | Removed by |
  |---|---|
  | Flips | Two-sided scoring at a station (b4 Break 3) |
  | Racks | A magazine on one slide (my p1) |
  | The loose tail | The spool as carrier: no tail until the cut (p3) |

- **Where an arm could still earn its place** is the dexterous loading itself:
  laying a split end into a cassette, or folding it back. That is imitation
  learning on a deformable object: untested, and outside the precision path.

  This keeps b5's own judgement that precision lives in the docks, and moves
  the arm to where the minutes are.

---

## Combinations

**C1. The one-shaft applicator press** (b1b × p5)
- **b1b contributes:**
  - the OTP applicator in the shop-press frame;
  - the 15 mm crank at BDC as the crimp;
  - the strain-gauged rod.
- **p5 contributes:**
  - the timing diagram cut into printed cams on the same shaft: presser foot,
    fork swing, withdraw and catch pull in the 40–105° dwell before the feed;
  - the cassette's printed rack as the Y escapement;
  - the J2 skip bump.
- **The skip.** It pulls a pin between the rod and the T-slot block, so the
  applicator neither crimps nor feeds for that turn.
- **The stack.** The disc-spring stack sits in the same rod.
- **The drive.** One NEMA 23 turns everything. The self-locking worm of p5 is
  optional, since the crank does not need it.
- **What it settles:** b1's pre-feed conflict, by timing rather than by
  software.
- **What it leaves open:**
  - a 180° fork swing driven from a cam (rack and pinion on a follower);
  - the applicator's feed timing, which sets where the window is.

**C2. The pedal-less hand station** (b2 × p4 × far-end electrode)
- **b2 contributes:**
  - strip feed, tab shear and box gripper;
  - the captive click;
  - the die, which the bench already trusts.
- **p4 contributes:**
  - the person-machine split: the person splays and pokes, the machine keeps
    the order;
  - lit conductor and cavity;
  - the soft clamp that takes over so the person lets go;
  - the clamp's proof pull after the punch has lifted;
  - pipelined insertion.
- **The electrode blade** fires the close and checks identity.
- **What it removes:** the pedal, the person holding through the close, and
  wrong-conductor errors at J4, J7 and J2.
- **Open:**
  - axial entry into a captive contact (strand splay at the barrel's rear edge,
    shared with p4);
  - the SN-2549's crimp on this wire.

**C3. Split on demand, edge first** (b4 partial slit × p ordering × b1 fold-back)
- **b4 contributes:** a laser slit to 70–90 % of each web, and the crown
  scores, in one job with one flip.
- **This view contributes the order.** Per conductor, edge first:
  1. peel the edge conductor off the ribbon along its slit, up to the clamp
     edge (~1–5 N);
  2. lay it into the pre-fed contact;
  3. crimp;
  4. pinch-pull its slug if not already stripped (B1a);
  5. park it.
- **b1 contributes:** the remaining webbed ribbon folds back or up as a single
  flap, and the neighbours are always a ribbon, never loose conductors.
- **What it removes:** the parking fan, the tines and the person's fold.
- **Open:**
  - whether a peel along a laser slit stays in the web or wanders into the
    insulation;
  - whether a ribbon folded back at an 8–15 mm split root lies flat enough to
    clear the tooling.

**C4. Terminate at the spool through a borrowed press** (p3 × b1b)
- **p3 contributes:**
  - the spool as carrier;
  - trim by the cut that freed the last loom;
  - test through the slip ring;
  - cut last, so a redo costs spool.
- **b1b contributes:** the crimp head, a bought applicator whose strip already
  feeds itself.
- **The neighbour problem** is C3 at the work clamp.
- **What it removes:** cassette loading, the largest person step in every
  b-arrangement.
- **Open:** everything open in p3 (spool inner end, feeding floppy ribbon out
  to length), plus guarding a crank press at a spool.

**C5. Head to a still ribbon, then converge and gang** (b3 × p2 × p1 bench C)
- **b3 contributes:**
  - the Ender-class gantry;
  - the force closed inside a hand-sized C-frame;
  - the pick from a fixed feeder with its own shear.
- **This view contributes:**
  - the stepped trim (b3 Break 1);
  - b2's blade in the head;
  - a converging comb;
  - gang insertion in place of per-conductor insertion with drag.
- **Open:** harvesting and aligning applicator blades in a 1 kg head
  (b3's own), and the converging comb.

**C6. Stage 0 for any applicator bench** (b1b's jack test × my p1 build order)
- **What it is.** The applicator in the shop-press jack is a working crimper in
  its first week. It becomes bench B of my p1 before any shuttle, cassette
  motor or crank exists.
- **Stages.** The person folds or lifts by hand at a printed cassette on the
  bed. Then the crank replaces the jack (b1b), then the cams join (C1).

---

## What their view has not yet seen

- **The order inside one crimp cycle** (b1 Break 1): feed, withdraw, pull and
  look all compete for the same crank angles.
- **The person's attended minutes,** counted over the whole procedure (B).
  Busy seconds at one station understate a person-paced cycle (b2) and hide the
  fold (b1).
- **The length geometry between the crimp pose and the housing pose**:
  - a straight trim with a housing fan makes outer conductors short (b1);
  - a fan crimp with a straight trim makes them long (b3).

  Trim in the housing's pose, or step the trim line.
- **Crossings and trimmed conductors at insertion.** Insert the crossing
  conductor last; trim unused conductors at the root by recipe.
- **What is handed back that a machine can take:**

  | Handed back | Taken by |
  |---|---|
  | Folding | An ungrooved lid with valley tines, or split on demand |
  | The pedal | The electrode blade |
  | Holding through the close | p4's soft clamp |
  | The laser flips | Two-sided scoring |
  | Loading cassettes | The spool (p3) |
  | Crimp height per session | See below |

  Crimp height per session is the person with a micrometer in b1, b1b and b2.
  It could become a sacrificial first crimp of each session, taken by the
  machine for sectioning. Or b1b's force-curve band could be taught from that
  sample, so the machine flags a drift in shape between samples. Crimp height
  itself still needs the micrometer.
- **Cut-first costs** (C): a redo shortens the loom and, with b4, goes back to
  the laser.

## Where their work changes my own ideas (for revision)

1. **p1 and p5 slotted presser.** It fails with a strip-fed anvil (A). The
   carrier lies under the wire path, so neighbours cannot drop 7 mm there. The
   branches are:
   - cut the contact free and place it on a standalone 1.6 mm blade anvil,
     using b2's shear and box gripper or b3's pick-and-cut;
   - fold back, as b1 does, or split on demand (C3);
   - lift the target instead (p2's arrangement), with the tooling above the row
     by at least the strip track's depth.

   p1's "pawl pre-feeds the side-feed strip onto a 1.6 mm anvil blade" and "the
   presser drops the neighbours" cannot both stand.
2. **p4's proof pull at BDC tests the tool's grip, not the crimp's.** At BDC the
   punch is still pressing the barrel. Adopt b1's order: lift the punch, hold the
   contact by its box on a catch, then pull. p5's hook behind the box at 290°
   is already right.
3. **p5's over-travel hazard** gets the disc-spring stack from b1b's ball-screw
   branch in place of a shear pin: force is capped at ~4–5 kN and a switch
   comes free [calc §3].
   - With a NEMA 23 on p5, a 0.2 mm obstruction in a 40 kN/mm loop passes BDC
     at 8 kN without the stack.
   - A NEMA 17 on the small eccentric stalls earlier.
4. **The axial chain, my tightest number.** It falls from ±0.34–0.35 mm to
   ~±0.10 mm RSS if the insulation edge is a laser score placed relative to
   the cassette, and the split root is laser-defined [calc §10]. p1 bench A
   becomes:
   - b4's crown scores in the cassette;
   - a per-conductor pinch pull at the bench.
5. **My transfer table's "SO-101 class arm 1–3 mm" was optimistic.** Measured
   backlash gives ~6 mm RSS unless every dock is approached the same way, which
   leaves ~1.2 mm. The dowel and V-groove captures of ±1.5–3 mm hold only with
   the same-direction rule.
6. **Split length.** b1 needs 8–15 mm with fold-back, and my p1 presser ~30 mm.
   Derek's split-length question now has a mechanism attached to each answer.
7. **p4's "anvil shuttle brings the pre-fed contact"** becomes b2's cut, box grip
   and captive click, placed along the axis from the box side.
8. **p2's crimp head** need not carry a reel: b3's pick from a fixed feeder.

## Measurements that settle most of this

1. **One OTP applicator in the shop-press jack**, stroked slowly by hand. It
   settles:
   - the feed start height (sets C1's window and b1 Break 1);
   - whether the feed shoves a crimped contact aside;
   - the tooling half-width;
   - the tip-to-tooling-face depth;
   - the anvil's height above the strip track.
2. **The SN-2549 closed against a light** (do the jaws bottom?) and handle
   travel against die travel, for the ratio. These set b2's spring link.
3. **A metre of ribbon slit partway with a razor**, then peeled one conductor at
   a time. That settles the peel force and whether the tear stays in the web
   (C3).
4. **One contact placed into the SN-2549 nest** from the box side under the
   ELP camera: does the box shoulder stop at the die face with the barrels
   centred? (b2 Break 2)
5. **J1's two ribbons laid in a straight-trim cassette and pushed into an
   XHP-9 by hand**: how far short the outer contacts sit (b1 Break 2).
