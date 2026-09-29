# hand-tool-as-press on change-the-question (wave 3)

hand-tool-as-press reads the procedure as "the crimp tool is already the
machine": the SN-2549's own XH profile, ratchet and gain, closed by a foot or a
slow actuator, with the ribbon's far end as an electrode array. This file reads
[change-the-question](../explorers/change-the-question/summary.md)'s idea files,
especially the wave-2 ones:
- [c6](../explorers/change-the-question/ideas/c6-pre-form-the-contact.md), pre-form;
- [c6b](../explorers/change-the-question/ideas/c6b-by-hand-this-week.md), by hand this week;
- [c1c](../explorers/change-the-question/ideas/c1c-crimp-in-the-row.md), crimp in the row;
- the revised [c1](../explorers/change-the-question/ideas/c1-half-rows.md),
  [c1b](../explorers/change-the-question/ideas/c1b-tack-first.md),
  [c2](../explorers/change-the-question/ideas/c2-buy-the-crimp.md) and
  [c5](../explorers/change-the-question/ideas/c5-ends-as-stock.md);
- their calc ([w2 §n](../explorers/change-the-question/calc/wave2.out.txt),
  [ctq §n](../explorers/change-the-question/calc/ctq.out.txt)).

It leaves aside what
[terminal-supply's wave-2 critique](terminal-supply--on--change-the-question.md)
and change-the-question's own
[wave-3 file](change-the-question--on--into-the-housing-w3.md) already carry:
- the fixed C and the stepping slide;
- the box-face front stop;
- the lance groove;
- growth against a nose stop (their B4);
- the feed-length rule for two sequential pushes;
- the anvil blade behind the lance;
- steel as master in X.

My numbers for this file are **[htq §n]** in
[`../explorers/hand-tool-as-press/calc/exchange_ctq_w3.py`](../explorers/hand-tool-as-press/calc/exchange_ctq_w3.py),
output
[`exchange_ctq_w3.out.txt`](../explorers/hand-tool-as-press/calc/exchange_ctq_w3.out.txt).
Other calc cited here:
- **[ht w2 §n]** is my wave-2 calc ([wave2.out.txt](../explorers/hand-tool-as-press/calc/wave2.out.txt));
- **[ith ex §n]** is into-the-housing's
  [exchange_hand_tool_as_press.out.txt](../explorers/into-the-housing/calc/exchange_hand_tool_as_press.out.txt).

Prime rows are from [`../sourcing/amazon-prime.md`](../sourcing/amazon-prime.md),
observed 2026-09-28.

---

## 1. Combinations

### K1 — The bench's SN-2549 pre-forms its own contacts; the flags come back to the same die on a foot-closed bench (c6 / c6b × a1b / a6)

**What it combines.**
- c6's idea of narrowing every contact's insulation barrel before it meets a
  wire, so the conductor snaps in and the contact travels as a flag.
- c6b's snap block, loom-order sticks and box-keyed clip.
- My [a6](../explorers/hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md)
  jig bench: cradle, cord treadle, far-end block, pull jig and keyhole gauge.
- [a1b](../explorers/hand-tool-as-press/ideas/a1b-pawl-out.md)'s machine-set
  stop, as the way the bench grows.

The one new move is that **the pre-former is the crimp tool itself, stopped
early**. The number that allows it: a single-stroke tool touches the tall
insulation wings (2.75–3.20 mm open) before the short conductor wings
(1.50–1.60 mm). On an edge model of the die, the insulation wings are pushed
inside the die width over 0.65–1.7 mm of stroke before the conductor die
touches anything. That is 2–10 mm of grip travel, likely one or more ratchet
clicks [htq §3, estimate]. H1 below explains why this matters: c6's round
keyhole is a shape the die never makes and never re-forms.

**Picture it.**

*Where things start.*
- The ribbon end is cut, split and stripped at a6's end jig.
- Its far end sits in the far-end block, one Wago 221-415 per conductor
  (Prime row, $28 for 25), on ESP32 inputs.
- Kit contacts sit loose in a dish.
- There are two SN-2549s: the bench's, and a second one (Prime row, $22.29,
  532 ratings). Or the one tool is used in two passes.

*Station P, pre-form (no wire anywhere near).*
- The second SN-2549 lies in a1's cradle. a1's locator plate on the lower
  jaw's M4 screw keeps only its front stop; the neck blade is gone, because
  there is no wire.
- Derek drops a contact barrels-up into the XH nest, box against the stop, and
  squeezes to click *k*.
- Click *k* was chosen once per contact lot, under the ELP end-on. It is the
  deepest click at which the insulation wings are inside the die width and the
  conductor wings carry no mark.
- He presses the release lever. The jaws open, and a printed plunger pushes the
  contact forward, box first, into c6b's loom-order stick clipped at the jaw's
  front face.
- Moving forward, the lance (tip rearward) leaves the anvil's front face and
  cannot catch.
- What comes out [htq §3, estimate]:
  - the insulation barrel is narrowed to about the die width, 1.8–2.0 mm plus
    0.02–0.05 mm springback;
  - its tips curl inward high in the arches, ~2.3–3.0 mm tall;
  - the conductor barrel is open and untouched.
- This is the shape the final stroke passes through anyway. Contacts this
  narrow stack nose to tail without nesting: a 1.85–1.95 mm box cannot enter a
  U whose inside is 1.4–1.6 mm.
- About 8–12 s each, 7–11 min per unit, while a print runs [htq §8].

*Station S, snap.*
- c6b's snap block: a steel-lined box pocket with a lance groove and a front
  stop, a backlit window, and a tip stop.
- Here the tip stop is a **steel plate wired as an electrode**. The pocket
  lining is not wired.
- Derek lays one stripped conductor over the contact with its cut tip on the
  plate. The ESP32 names the conductor, and buzzes if it is the wrong one.
- His thumb tool's rear tine presses the jacket through the throat into the
  narrowed U, and the front tine lays the strands in the open conductor U.
- He lifts a flag.

*Station C, crimp.*
- The bench SN-2549 in a6's cradle, closed by the cord treadle. The treadle is
  **single-stage** now: there is no hold stage, because contact and conductor
  are already one part.
- The flag rides on two sprung supports at one height *h* above the anvil:
  - on the jaw's rear face, a printed U guide takes the jacket;
  - on the front face, c6b's clip carries an open-topped slot keyed to box and
    lance, on a sprung ledge.

  Both springs are 1–3 N, so the punch seats the contact on the anvil before
  the wings start to curl, which takes tens of N.
- *h* is 1.1–1.7 mm. That clears the lance on entry (lance + 0.2 = 0.8–1.1 mm)
  and gives the exit lift (1.0–1.7 mm [ith ex §2]).
- The front stop is a spring-steel leaf preloaded to 10–30 N, insulated from
  the tool and wired: **green** when the box face touches it.
  - Being a detent, it is change-the-question's own growth-safe repair
    ([their w3 B4](change-the-question--on--into-the-housing-w3.md)).
  - The tool's jaws are wired too: **amber** when the punch first touches the
    contact.
- Derek lays the jacket in the rear U and slides the flag forward, box first,
  **until green, and stops pushing**. The flag's grip on its jacket is only
  0.08–3.8 N (H2), so a harder push slides the contact back along the wire.
  Green is what tells him to stop.
- He presses the treadle:
  1. amber, the punch meets the wings;
  2. the contact is pushed down onto the anvil against the ledge springs;
  3. curl and coin;
  4. the ratchet completes the stroke.
- When the tool opens, the springs lift the crimp back to *h*, above the anvil
  face that would catch the lance. He draws it back out through the nest.
- The cord's S-type cell and the pulley's AS5600 (both Prime rows) log force
  against travel, as in a6.

*Then:* a6's pull jig and keyhole gauge, on every crimp or on samples, and
into-the-housing's i5 nest for insertion, on the same far-end block.

**What locates what.**

| Pair | Reference |
|---|---|
| Contact to the pre-forming die | Box face on the locator's front stop, in the same XH profile that later crimps it |
| Conductor tip to contact | Snap block's box stop and tip stop (electrode); afterwards the snap's grip |
| Flag to the crimp die, axially | Box face on the front-stop leaf (green) |
| Flag laterally and in roll | The keyed slot on box and lance; the rear U on the jacket |
| Flag vertically | Sprung supports at *h*, then the punch presses it onto the anvil |
| Crimp height | The SN-2549's dies and ratchet, as today |

**What drives the crimp.** The foot, through the cord and a 2:1 treadle:
55–122 N at the toe for 100–220 N at the grip [ht w2 §5]. The ratchet
guarantees full closure. Later, a1's NEMA 17 on a Tr8×2 screw replaces the foot.

**How it knows.**
- The stick's order and gaps are the build list.
- The tip electrode confirms identity and tip position before the snap.
- The backlit window shows stray strands before they are hidden.
- Green means the box is at its stop.
- Amber marks die touch. Amber before the foot moves means the flag is
  touching a jaw.
- The force–travel curve.
- The pull jig and the keyhole gauge.
- i5 pairs each conductor with its cavity.

**What the person does.** Every motion, by hand and foot:
- pre-form, away from any wire;
- snap;
- slide the flag to green, press the treadle, draw it back;
- pull and gauge, if sampled;
- insert and label.

Estimates [htq §8]:
- 22–34 s per contact, of which 14–22 s at the wire;
- 19–30 min per unit, 7–11 of them pre-forming while a print runs;
- against ~22 min today and ~31 min for a6 with pull and gauge.

What it buys is one part and one stop per act, and a check at each stop. It
does not buy minutes.

**What each side contributes, and what drops out of each.**
- *From change-the-question:* the flag (contact fixed to conductor before any
  crimp tool), the snap motion, loom-order sticks, and the box-keyed clip.
- *From hand-tool-as-press:*
  - the tool as its own pre-former;
  - the treadle;
  - electrode stops (tip, box, die touch);
  - the sprung two-level entry that keeps the lance off the anvil;
  - the cradle's force log, the pull jig and the keyhole gauge.
- *Dropped from mine:*
  - a1/a6's neck blade and its open question (whether a kit contact's neck
    leaves room for blade plus brush [ht w2 §1]);
  - the two-stage treadle's question of where the first ratchet tooth falls;
  - steering a floppy conductor into a captive contact.
- *Dropped from theirs:*
  - the steel keyhole jaws, the mandrel and the HSS blank to grind;
  - the round keyhole's re-forming problem (H1);
  - squeezing the tool by hand while holding a flag.

**What it leaves.**
- **Whether the window exists** on this SN-2549. On the pessimistic apex model
  it runs from −0.12 to +0.78 mm and can vanish [htq §3]. One slow close,
  click by click, on an empty contact under the ELP settles it.
- **What throat the chosen click leaves** after springback, and the snap's grip
  in a U rather than a round bore.
  - The walls are ~2.3–3.0 mm tall, ~12–33 N/mm against c6's ~80 N/mm curled
    wings [estimate, 3EI/L³ at 2.0–2.8 mm].
  - The silicone (2.5–5.5 MPa [w2 §4]) still yields before the wall does.
- **Whether the SN-2549 opens 3.6–4.9 mm at the nest** [htq §4]. Unmeasured.
- The far end must be stripped and in the block before the XH end is crimped
  (a6's open item).

**How it grows.**

| Hand piece | Its motorised or shared form |
|---|---|
| The click pre-former | a1b's pawl-out cradle stopping at a taught grip position. The force rise on the pre-form stroke then gives each contact's wing height, which sorts mixed-maker contacts in a kit bag |
| The snap block | c1c's pallet with a presser comb (K2) |
| The flag guide and stop | A head feeding flags along the guide (a2), where the side-entry jaw law still applies |
| The treadle | a1's pusher |

### K2 — c1c's windowed pallet under one SN-2549 nest cut to a tongue: the jaw law dissolves at 3.4 mm (c1c × a4 / a4b)

**What it combines.**
- c1c's layout: a fixed steel C, one X slide carrying the web clamp, two
  windowed pallets at 3.4 mm, sticks feeding pockets, snap, and crimp in the
  row.
- My [a4](../explorers/hand-tool-as-press/ideas/a4-dies-in-a-die-set.md):
  - SN jaws in a guided die set;
  - an eccentric drive;
  - a disc-spring cap on the peak force;
  - a button cell;
  - crimp height read by re-touch after each stroke.
- [a4b](../explorers/hand-tool-as-press/ideas/a4b-c-frame-one-nest-head.md)'s
  one-nest cut.

c1c names a4 as one of its presses. What the pairing adds is that **a
one-nest tongue at 3.4 mm pitch needs no stand-out**, so my side-entry jaw law
(8–14 mm of stand-out, strands set at 15–52 mm root radius [ht w2 §3]) stops
applying.

**Picture it.**
- **The C.** Its spine stands in front of the housing nest. Its arms reach back
  20–26 mm: the lower one under the housing nest and the working pallet, the
  upper one over them (H6 gives the reason).
  - A lower arm 12 mm thick and 15–25 mm wide deflects 11–41 µm [htq §7].
  - The height stop sits in the die block beside the anvil, so that deflection
    costs travel, not crimp height.
- **Ram.**
  - Guided on two 8 mm case-hardened rods (Prime row, $6.99).
  - Driven by a 2–2.5 mm eccentric on the bench NEMA 23, or the self-locking
    12 V worm gearmotor (Prime row, $26.99).
- **Punch.** One XH nest cut from a spare 2549 jaw. The iCrimp IWS-0723K set
  lists a 2549 die among five interchangeable dies (Prime row, $46.59,
  9 ratings). It is the only Prime route to a loose 2549 die found, and it
  comes in a frame.
  - The tongue is **≤4.45 mm wide** [htq §5], narrow for 2.1–2.3 mm above the
    anvil beside c6-keyhole neighbours, or 2.6–3.3 mm beside K1's tool-made
    ones.
  - That leaves walls of 1.43–1.48 mm either side of a 1.5–1.6 mm conductor
    arch.
- **Anvil.** A 3 × 3 mm HSS blank (Prime row) ground to **≤1.90 mm** so it
  passes the 2.0 mm pocket.
  - It sits on a stack of disc springs preloaded to ~3.5 kN, over a button
    cell.
    - The Hilitchi Belleville assortment (Prime row, $14.99) is light-duty
      stainless; a stack for 3–4 kN is not shown in it.
    - The 500 kg micro button cell (Prime row, $74.99) covers 3 kN. The
      Φ20 mm cell's Prime variant is 200 kg, which is under range.
  - The anvil is fixed. The pallet's swing arm lifts the pallet 1–2 mm to step
    past it and settles it back, with the pocket floor 0.1–0.2 mm under the
    anvil top (c1c's rule).
- **Crimp height** comes from the hard stop between ram holder and anvil block.
  - A 1.9 mm anvil gives the tongue's faces nothing to land on. So any
    face-to-face bottoming the SN jaws have in the hand tool is gone, and the
    stop alone sets height.
  - The disc stack caps the peak.
  - After each stroke the eccentric backs to a ~10 N re-touch, and a 0.001 mm
    indicator across ram and anvil block reads crimp height. The Clockwise
    DITR-0105, with an RS232 port, is a Prime row at $52.99; its DTCR-01
    cable has no Prime listing (consistency item 8).
- **Electrodes.** The anvil block and the punch are wired. The ribbon's far end
  is in a far-end block, or on c5 / procedure-is-the-machine p3's slip ring
  through the spool (6-circuit, Prime row, $9.99).
  - When the pallet settles carrier *k* onto the anvil, the conductor that
    answers must be the one the pin map puts there.
  - That catches a mis-laid J7 GND-over-CLO before any force.
- **The person** does what c1c says: keeps sticks and housings fed, lays each
  ribbon end in the clamp, makes J4's crossings.

**What each side contributes.**
- *c1c:* a pocket that holds each contact on its conductor from placement to
  crimp, 3.4 mm in-plane gaps, narrowed neighbours, and a press the work steps
  under.
- *Mine:*
  - the SN profile the bench already crimps with by hand, so hand crimps are
    references for the upper profile and replacement jaws cost $5–10 at
    icrimptools.com [source, wave 1];
  - height by stop, with a force cap and a height reading on every crimp;
  - conductor identity at the anvil.
- *What drops out:* the jaw law's stand-out and copper set, and a4b's
  6.3–9.9 mm lift with its arm cantilevered over the row [ht w2 §4]. The arm
  goes under the pallet instead.

**What it leaves.**
- Cutting a hardened jaw to a 4.45 mm tongue without cracking (a4b's problem,
  now tighter).
- The SN's lower XH cradle replaced by a flat HSS anvil. The crimp's underside
  then differs from the hand tool's [assumption: the SN's lower die shape is
  unrecorded].
- H4 to H6 below.
- Everything c1c already leaves.

### Others, briefly

- **K3 — c6's loom-order sticks as
  [a2b](../explorers/hand-tool-as-press/ideas/a2b-gravity-tool-flat.md)'s chute.**
  - Stood vertical over the flat tool's nest, a stick is the chute: pre-formed
    contacts neither tumble nor nest in a 2.1 × 2.6 mm channel, and an
    escapement at its foot replaces the revolver disc.
  - With c6's round keyhole the box governs the passage: 2.8–3.3 mm with the
    lance, against 3.35–4.10 mm for an open contact [ith ex §2].
  - c6's closed-ring sub-variant (ID 1.75–1.8 mm, flared rear) is then a2b's
    conductor guide: the hanging conductor threads axially into its own
    contact's ring.
  - The ring's metal (~2.2 mm) stands above the 1.80 mm closed height, so the
    die does re-form it, into an oval rather than a B. That is untested.
- **K4 — c5's T4 runs under
  [a3](../explorers/hand-tool-as-press/ideas/a3-tool-travels-to-ribbon.md) or
  [a2d](../explorers/hand-tool-as-press/ideas/a2d-batch-then-gang-push.md).**
  - One ribbon, one housing size, no crossings: a3's on-edge fixture and a2d's
    squaring comb need no configurability.
  - The unspooled remainder, on a slip ring, is my far-end electrode array
    before any loom is cut, so a2d's "feed until green" and a3's identity
    check work at the spool.
- **K5 — a1b as [c3](../explorers/change-the-question/ideas/c3-fold-and-solder.md)'s
  fold station.**
  - c3's steel arch curls both barrels at 0.1–0.3 kN and stops 0.2–0.3 mm
    above crimp height. That is the SN-2549's own stroke stopped short of die
    contact, which a1b's pusher does at any grip position: 3–20 N at the grip
    through a gain of 15–30.
  - No custom arch is needed, and the fold is in the profile the contact was
    designed around.
- **K6 — c2's JST lead as a1b's and a5's sweep target and H1's comparison.**
  The genuine crimp's insulation height and width are the target that the
  grip-position map is set to. Its insulation barrel, sectioned, is the "real
  B-crimp" against which a pre-formed and re-crimped barrel is judged.

---

## 2. What still breaks in their revised and new ideas

**H1. c6 (and c6b, and c1c's pre-formed host): the round keyhole is a shape the crimp die neither makes nor re-forms.**
- **The conflict** [htq §1].
  - A bore of 1.57–1.65 mm (mandrel plus springback) with a 1.3–1.5 mm throat
    puts the wing tips beside the bore's widest point, only 0.28–0.47 mm above
    its centre.
  - The highest metal is **1.28–1.66 mm** above the contact's underside. That
    is 0.14–0.52 mm below the 1.80 mm closed insulation height of the clone
    spec [digest].
  - **104–146° of the jacket's top is uncovered**.
  - The snapped jacket stands ~1.90 mm tall, 0.25–0.6 mm proud of the tips.
- **Physical consequence.**
  - A die closing to 1.80 mm meets the jacket first. It reaches the wing tips
    only if its profile dips below ~1.3–1.6 mm at x = ±0.65–0.75 mm.
  - A B-profile dips at x = 0, the cusp, where there is no metal, only jacket
    [assumption: the SN's insulation section is a B].
  - So the final stroke squeezes the sides to die width and indents the
    jacket through the throat. It does not turn the tips over the jacket.
  - The insulation grip in the finished loom is then c6's snap grip,
    0.08–3.8 N axially [htq §2], plus whatever the cusp's indent adds.
  - The jacket is open over 104–146° to a bend toward the throat. JST's
    criterion is an insulation crimp that "survives 60–90° bends several
    times" [xh-facts §5], near a compressor and pumps.
- **c6's own repair does not reach it.** "Take the keyhole from the tool: …
  stop at the first contact of the arch with the pin" [c6 tried 1].
  - A B-die's stroke pushes the tips inside its width, runs them up the arches
    toward the cusp, meets them there and drives them down. The wing roots stay
    near vertical until then [htq §1, kinematics].
  - Stopped early, it gives a narrowed U with tips high.
  - Stopped at the pin, the tips are closed over the pin with no throat.
  - At no point is it a round bore with an open 1.3–1.5 mm throat.
- **Repairs and branches, side by side.**
  - (a) **The tool-made pre-form** (K1): stop the real die inside its window.
    - The tips stay above the closed height, so the final stroke finishes the
      curl it started.
    - Outer width 1.8–2.05 mm keeps c6's pitch gains: 4.55–4.78 mm of tongue
      room at 3.4 mm, against 4.46–4.64 for the round keyhole [htq §5].
    - It is taller, 2.3–3.0 mm against 1.3–1.7. That costs passage height
      (H3) and tongue height (K2).
  - (b) **Keep the round keyhole and qualify it as the insulation crimp.**
    Measure pull along the wire, bends toward the throat and vibration, on the
    ribbon, against c2's JST lead. It is c6 as drawn, with its insulation
    crimp redefined.
  - (c) **A taller keyhole from a flat-sided blade mandrel** (1.5–1.6 mm wide,
    ~2.5 mm tall) in c6's own steel pre-former. The U's walls stay straight and
    the tips sit above the closed height.
    - It keeps the separate pre-former and loses the tool's own profile.
    - The walls are ~2.4–6 × softer than c6's curled wings [estimate], so the
      throat's snap margin is thinner.
- **What it leaves.** The SN-2549's XH insulation profile: B or not, and its
  closed height (assumed 1.8–2.1 mm). An ELP or Revopoint image of the die,
  or one crimp on a bare jacket sectioned, settles it.

**H2. c6, c6b and c1c: the flag's grip is quoted at the mandrel, not at the bore it leaves.**
- **The numbers** [htq §2]. With c6's own grip model, at the bore after
  0.02–0.05 mm springback (c6's go/no-go text uses that bore), the axial grip
  is **0.08–3.8 N**, not 0.2–4 N.
- **The jacket's OD.** The ribbon is 1.7 ±0.1 mm per conductor [xh-facts §7].
  At 1.60 mm, a 1.60 mandrel's bore grips **nothing**, and a 1.55 mandrel's
  grips 0–1.0 N.
- **Consequence.**
  - At the low end the flag slides in c6b's keyed slot (0.1–0.5 N) and on
    c1c's move from load position to press.
  - In c6b the person's push to the stop becomes the thing that moves the
    contact on its wire (K1's "green, stop pushing").
- **Repair.**
  - Choose the mandrel against the conductor's measured OD, not the ribbon
    pitch: bore ~0.08–0.12 mm under the jacket, so a squeeze of about 5–7 %.
  - Set the no-go pin 0.05–0.08 mm under that jacket OD, not at 1.70.
  - The Prime-confirmed Accusize gauge set stops at 1.52 mm, so neither pin is
    in it (Wave 3 request, in
    [my sourcing requests](../explorers/hand-tool-as-press/sourcing-requests.md)).
- **What it leaves.** The jacket's real OD. Caliper five conductors, split, not
  the pitch.

**H3. c6b (and c1b's option 1): a flag pushed box-first through the open SN-2549 drags its lance, and the lance wins.**
- **The conflict.**
  - Pushed box-first from the wire side on the anvil, the flag's lance (0.6–0.9
    mm proud, tip rearward) meets the lower jaw's rear edge. Its outer slope
    folds it up, as a cavity would, and it is dragged folded across the whole
    jaw thickness.
  - The fold force is 1–5 N [ith ex §3, estimate]. The flag's axial grip is
    0.08–3.8 N (H2).
- **Physical consequence.**
  - Across most of both ranges the contact stops and the jacket keeps moving.
    The strip-to-barrel position the snap block set is lost without any sign,
    and insulation can reach the window or the conductor barrel.
  - The "2.8–3.25 mm" c6b asks of the tool's opening is enough only for a flag
    carried clear of the anvil. c6b does not say what carries it.
- **Repair: K1's sprung two-level entry.**
  - A rear U on the jacket and a front ledge, both at *h* = 1.1–1.7 mm on
    1–3 N springs.
  - The flag travels level with its lance clear. The punch seats it on the
    anvil. The springs lift the crimp back to *h* for exit, which clears the
    1.0–1.7 mm lift a crimped lance needs before drawing back [ith ex §2].
  - The clip's keyed slot is open-topped.
  - It is a2b's chute tongue and into-the-housing's lift-before-draw, moved
    onto c6b's clip.
- **What it costs.** The jaw opening at the nest rises to **3.5–4.3 mm** with
  c6's round keyhole and **3.6–4.9 mm** with the tool-made pre-form
  [htq §4]. The SN-2549's full opening is unmeasured.
  - If it falls short, the fallback is dragging the flag with the jaws at full
    open (2.4–2.6 mm needed). The lance-fold force is then reacted by pushing
    on the box, not the wire: a printed pusher behind the box's rear shoulder
    (1.27 mm² at 16 MPa per 20 N [ht w2 §2]), which a person cannot do through
    a nest.

**H4. c1c: the cam plate under the pallet and the anvil blade rising through the carrier are in the same place.**
- **The conflict.**
  - c1 puts "a slotted cam plate under each pallet" for the 3.4 → 5.0 mm
    spread. c1c keeps it.
  - c1c also has "the anvil blade rises through each carrier's window and bears
    on the contact's floor directly".
  - Under carrier *k* both want the same few millimetres.
- **Consequence.** As drawn, the anvil hits the cam plate before it reaches the
  contact.
- **Repairs and branches.**
  - (a) A ≤1.9 mm window in the cam plate at every carrier position at the
    3.4 mm setting. The webs left are 1.5 mm, and they also carry the slanted
    slots.
  - (b) Move the cam plate to the carriers' rear, driving pins on the carrier
    tails, so the underside is clear.
  - (c) K2's fixed anvil, with the pallet settling onto it. The same window
    question remains for the plate.
- **Uncertain.** Whether a 1.5 mm printed web carries the spread's side loads.

**H5. c1c: carriers sprung forward against a fixed front stop meet it sideways when the slide steps, and nothing holds them against the rearward proof pull.**
- **Stepping.**
  - Each carrier is sprung forward (0.1–0.5 N) so its box presses on the
    hardened front stop.
  - At rest, then, every box sits forward of the stop face by the overtravel.
    A 3.4 mm X step brings the next box sideways into the stop's side edge.
  - Repairs:
    - side lead-in ramps on the stop: 30–45° pushes the box back 0.2–0.5 mm
      over 0.2–0.87 mm of the step [htq §6];
    - or retract the stop by more than the overtravel during each step. That
      fits change-the-question's own stop that backs off after capture.
  - Either way, the box front, a folded sheet edge, rides a steel ramp at under
    1 N. That looks harmless and is unmeasured.
- **Proof pull.**
  - c1c pulls ~20 N per contact "with each box held by its pocket's rear
    shoulder" by backing off the web clamp.
  - A row of 2–5 puts **40–100 N rearward** on carriers whose only rearward
    restraint is a 0.1–0.5 N spring [htq §6]. They travel back to wherever
    their tracks end.
  - The pressure on the shoulder is fine: 16 MPa on 1.27 mm² [ht w2 §2].
- **Repair.**
  - A rear latch per carrier, or the tracks' rear ends as a hard stop.
  - Then carry the row's 40–100 N into the slide directly, not through the
    swing-arm pivot, where it would be 0.8–4 N·m at a 20–40 mm arm
    [estimate].
  - Or pull row by row at a separate pull station: a6's slotted steel plate
    dropped over the row's necks.
- **Uncertain.** Whether a printed carrier with ~0.5 mm walls survives 20 N on
  its shoulder at every crimp.

**H6. c1c: a C "at the back" puts its spine where the ribbon's tail goes and its lower arm where pallet A parks.**
- **The conflict.**
  - c1c's order, front to back: housing nest, pallets, clamp nose, clamp, then
    the ribbon's tail (up to 600 mm, or c5's spool).
  - A C standing at the back reaches forward over and under the clamp. Its
    spine is in the tail's path.
  - Its lower arm runs under the clamp nose, which is exactly where pallet A,
    carrying its crimped row, "swings down and back under the clamp nose".
- **Repair: open the C backward.** Put the spine in front of the housing nest,
  with arms reaching back 20–26 mm over and under the nest to the working
  carrier.
  - A 12 mm-thick arm, 15–25 mm wide, deflects 11–41 µm at 3 kN, and the stop
    beside the anvil makes that travel only [htq §7].
  - The tail and the parked pallet lie behind, outside the C.
  - The housing stick feeds from the side when the slide has moved the nest
    clear of the upper arm.
- **What it leaves.** The rows' pushes into the housing happen between the C's
  arms, and the upper arm limits access from above.

**H7. c1c with hand-tool-as-press a4 as its press: a4's narrowing is too wide, and c1's anvil blank is too wide** [htq §5].
- c1c's punch estimate (1.75–1.9 mm half-width) is right for its geometry. a4's
  "one-nest die narrowed to 6–8 mm" is 1.5–3.5 mm too wide.
  - The tongue must be ≤4.45 mm.
  - It must stay narrow up to 2.1–2.3 mm above the anvil beside c6 keyholes
    with their jackets, and 2.6–3.3 mm beside tool-made pre-forms.
- c1's anvil, "a 3 × 3 mm HSS blank ground flat", has to lose ≥1.1 mm of width
  to pass a 2.0 mm pocket.
- The consequence of both is that crimp height comes only from the stop (K2).

---

## 3. Consistency

1. **c6's grip versus c6's bore.** The grip table (0.2–4 N) uses the mandrel's
   diameter. c6's go/no-go text says the bore is the mandrel plus
   0.02–0.05 mm.
   - Their own model at the stated bore gives 0.08–3.8 N at OD 1.70 [htq §2].
   - Neither figure uses the ±0.1 mm OD that xh-facts §7 records. At OD 1.60 a
     1.60 mandrel grips nothing.
   - Right: the bore after springback, against the measured jacket.
2. **c6's go/no-go pins (Ø1.50 go, Ø1.70 no-go)** admit bores up to 1.69 mm,
   which grip ~0 N on a 1.70 jacket.
   - The no-go belongs 0.05–0.08 mm under the measured OD.
   - The Prime-confirmed pin set stops at 1.52 mm [sourcing: Accusize row].
3. **c6's throat retention, "0.3–10 N (half to all of the push-in)".** Their
   push-in is 0.5–20 N at a 1.4 mm throat and 0.7–30 N at 1.3 mm [w2 §4], so
   half-to-all is 0.25–20 or 0.35–30 N. The 10 N ceiling is not derived.
   Minor: nothing downstream uses the top.
4. **c1's lance, "0.65–0.9 mm below the floor, tip 2.3–2.6 mm behind the box
   front [xh-facts §1]".**
   - xh-facts §1 gives 0.6–0.9 proud and ~2.4–2.6 behind the front.
     into-the-housing uses 2.24–2.64, which takes in S22's ±0.20.
   - 0.65 and 2.30 are the Würth drawing's lance, quoted in terminal-supply's
     critique, and change-the-question itself has since shown that part is not
     XH.
   - Right: xh-facts, or into-the-housing's wider range. No conclusion
     changes: c1's 1.1 mm groove covers both.
5. **"Box plus lance 2.8–3.25 mm"** (c1b, c6b, and terminal-supply's C4)
   against xh-facts' box 2.2–2.4 mm plus lance 0.6–0.9 mm = **2.8–3.3 mm**.
   Minor. More consequential is that this is the height a flag needs **dragged
   on the anvil with its lance folded**. Carried clear, it needs 3.5–4.9 mm
   (H3).
6. **c1b's "tack-first reverses JST's conductor-first order".** That is true
   against JST's two-step hand tools (force-and-form f9). Against a
   single-stroke tool it is not.
   - The SN-2549, and any single-stroke punch whose insulation section closes
     higher than its conductor section, touch the insulation wings first, by
     0.65–1.7 mm of stroke on the edge model [htq §3, estimate].
   - A tack looser than the stroke's own mid-point is the state a
     single-stroke crimp passes through.
   - So c1b's quality risk is confined to tacks tighter than that point. It is
     a matter of scope, not a contradiction.
7. **a4's narrowing (6–8 mm)** in my own file against c1c's punch estimate
   (1.75–1.9 mm half-width, 3.5–3.8 mm across including its legs). c1c's
   number is the one that fits c1c; the room there is ≤4.45 mm (H7). a4's
   6–8 mm stays right for strip feed and 5 mm shuttles.
8. **My a4's indicator price** ("a 0.001 mm indicator costs $451–668") is
   superseded by the Prime pass: Clockwise DITR-0105, 0.001 mm, RS232 port,
   $52.99, 67 ratings; the data cable is not on Prime [sourcing row]. It makes
   a4's and K2's re-touch height cheap.
9. **Agreements checked:**
   - pre-formed insulation envelope 1.96–2.14 mm = mandrel + springback + 2
     × stock [w2 §2];
   - the wing cantilever stiffness ~80 N/mm (3EI/L³, 0.2 × 1.2 × 1.5 mm);
   - open conductor barrel max 2.15 mm (1.90 + 0.25);
   - contact mass 0.043 g;
   - stick lengths [w2 §5];
   - T4's 38 % of crimps [ctq §1].

---

## 4. Transfers

### From hand-tool-as-press into change-the-question

- **The crimp tool as the pre-former.** A single-stroke tool shapes the
  insulation barrel before it touches the conductor barrel. Stopped inside
  that window, by a ratchet click or a1b's set grip, it makes c6's narrowing
  in the profile that will finish the crimp.
  - It repairs H1.
  - It replaces the steel keyhole jaws and mandrel.
  - With a1b, the pre-form stroke's force rise is a per-contact wing-height
    measurement, which sorts mixed-maker kit contacts before they reach a
    stick.
- **Electrode stops through the far end.**
  - c6b's tip stop, c6b's box stop and the tool's jaws: identity, "at the
    stop", and die touch as separate lamps.
  - c1c's anvil: the conductor on carrier *k* is named before any force, which
    checks J7's hand-laid crossing.
  - On c5's stock runs the far end is the unspooled remainder on a slip ring.
- **Green means stop pushing.** Any flag is held on its wire by 0.08–3.8 N, so
  the event that ends the push matters more than the stop that receives it.
- **The sprung two-level entry and lift-before-draw** (H3) for any flag going
  box-first through a side-entry die: c6b, c1b's option 1, force-and-form f9's
  station C.
- **The foot.** c6b's crimp needs one hand on the flag and none on the tool.
- **The keyhole fit gauge** downstream of c6b and c1c. Pre-formed barrels that
  the die squeezes only at the sides (H1) are exactly what a stencil-steel
  cavity section checks.
- **a1b stopped short of die contact is c3's fold station** (K5).
- **The hand as existence proof.** c6's pre-form (10–80 N) and c1b's tack
  (33–132 N per barrel) sit far below what a bench hand tool already delivers
  through its gain. A hand tool with a set stop can do either with no new
  drive.

### From change-the-question into hand-tool-as-press

- **Flags remove my two largest unknowns** for any arrangement that accepts a
  pre-form and a snap:
  - the axial reference moves from a 0.10 mm blade in a neck of unknown length
    to the box front on a stop;
  - conductor depth moves from strands-at-the-blade to the snap block's tip
    stop;
  - a1's hold at the first ratchet tooth is no longer needed.
- **The jaw law is a property of whole jaws.** c1's two-plane split gives
  3.4 mm in-plane gaps, and c6 narrows the neighbours. Together they let a
  one-nest SN tongue ≤4.45 mm wide crimp upright with no stand-out and no
  copper set (K2). a4b's lifted conductor and cantilevered arm become an arm
  under a windowed pallet.
- **Loom-order sticks** replace a2b's revolver disc and a2's stub magazine for
  loose contacts, once the contacts cannot nest (K3). J2's blank spacer makes
  the stick the build list.
- **Pre-formed contacts lower the passage** my a2 and a2b must open for. With
  the round keyhole the box governs: 2.8–3.3 mm, against 3.35–4.10 for an open
  contact. The tool-made pre-form gives most of that back (H3).
- **c5's T4 scope** gives a3 and a2d one configuration, and the spool as a far
  end before any loom exists (K4).
- **c2's JST lead** is the reference for a1b's grip-position map and a5's
  per-barrel sweep (K6).
- **c1b's "the insulation barrel is the forgiving one".** In
  [a5](../explorers/hand-tool-as-press/ideas/a5-two-squeeze-plier.md) the
  insulation squeeze's floor and ceiling are perhaps 0.1 mm apart. If the
  insulation barrel arrives pre-formed (K1's click in the SN-2549, or the
  PA-09's own 1.9 mm die closed part way before the conductor squeeze), a5's
  second squeeze only finishes a curl the die started, and that window may
  widen. That is untested.

---

## Questions this exchange adds for Derek

- **The window.** Close the SN-2549 one click at a time on an empty kit
  contact, releasing after each, and look end-on under the ELP.
  - At which click are the insulation wings inside the die width?
  - At which does the conductor barrel first show a mark?
  - Five minutes; it decides K1 and repair (a) of H1.
- **The insulation die.** An ELP or Revopoint image of the SN-2549's XH
  insulation section: is it a B (two arches and a cusp), and how tall is it
  closed? Or crimp one contact on a stripped-back jacket and cut it through.
- **The jacket.** Caliper the OD of five split conductors (not the ribbon
  pitch). It sets c6's bore and the no-go pin.
- **The opening.** How wide does the SN-2549 open at the XH nest, jaw to jaw,
  handles fully open? K1 and H3 need 3.5–4.9 mm.
- **A second SN-2549** ($22.29, Prime) as a dedicated pre-former, or one tool
  used in two passes?
