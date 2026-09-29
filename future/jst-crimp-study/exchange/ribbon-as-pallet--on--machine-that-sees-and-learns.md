# ribbon-as-pallet on machine-that-sees-and-learns

Wave 2 exchange. The view doing the reading: *the ribbon is a precision part*
([`../explorers/ribbon-as-pallet/summary.md`](../explorers/ribbon-as-pallet/summary.md)).
The view being read: *the first stage of a cell is one software can move and
observe* ([`../explorers/machine-that-sees-and-learns/summary.md`](../explorers/machine-that-sees-and-learns/summary.md)).

What this view brings to theirs:
- **The ribbon's own register.** An under-width channel and a flush cut make
  every conductor's position and every tip line known before anything looks.
  A picture then checks rather than finds.
- **An electrical channel.** A pogo block on the far end's cut face, a grounded
  contact and isolated blades give a wire to every conductor. Touches, nicks
  and placement register the instant they happen, independent of the camera.
- **Copper's set, and its limit.** Strands yield below R ≈ 67 mm and keep a
  bend. Every handling bend persists in the product. Gentle curls are
  elastic under reversal and cannot be pressed out.
- **The carrier strip and the pallet as fixtures**, and the procedure's two
  ends: palleting and tails.

Citations:
- **[calc P §n]**: this exchange's numbers,
  [`../explorers/ribbon-as-pallet/calc/exchange_on_machine_that_sees.py`](../explorers/ribbon-as-pallet/calc/exchange_on_machine_that_sees.py),
  with output
  [`exchange_on_machine_that_sees.out.txt`](../explorers/ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt).
- **[calc R §n]**: my wave-1
  [`pallet_geometry.out.txt`](../explorers/ribbon-as-pallet/calc/pallet_geometry.out.txt).
- **[calc V file §n]**: their calcs in
  [`../explorers/machine-that-sees-and-learns/calc/`](../explorers/machine-that-sees-and-learns/calc/).
- Contact dimensions are clone-drawing readings from
  [`../context/xh-facts.md`](../context/xh-facts.md) §1 unless stated.

---

## v1 The watched nest

### Break v1-1: the neighbours in the fan comb stand in the side silhouette

**Conflict.**
- Camera 2 looks "straight across the nest at wing-tip height, with a small
  backlight on the far side". To show strands against wing tips it must look
  along X, across the wire.
- v1's pallet fans the conductors to 5–6 mm pitch *in one plane*. The stage
  lowers the whole pallet to lay in, so the neighbours sit at the active
  conductor's Y and Z, ±5–6 mm away in X: on the sight line.
- Every inner conductor has a neighbour on the camera side and one on the
  backlight side. The two end conductors have one, which still blocks either
  the camera or the light [calc P §1].

**Physical consequence.**
- **The gate loses its side view.** Two of its six conditions come from that
  view: "no strand rises above the wing tips", and the conductor's height in
  the U (their calc §5 gives ~0.3 mm of spare).
- **X is no longer measured.** Camera 1 at 30–45° puts X and Z on one image
  axis.
  - The conductor hovers ~3.4 mm above where it lands, clearing insulation
    wings up to 3.2 mm tall.
  - That drop shows as 1.96–3.40 mm of apparent X.
  - X is recoverable only if the drop is known to 0.49–0.85 mm [calc P §2].
  - Without camera 2, X comes from the commanded Z, which the design meant
    not to trust.
- **The after-crimp silhouette is blocked the same way.** The window sits
  beside the nest, and the crimped conductor arrives with its neighbours
  alongside. So crimp height, bellmouth and brush are unread.
- **The black shroud and the punch have no room.** They must fit in the
  ~3.3–4.3 mm between the active conductor and its neighbours, at the
  neighbours' height.

**A repair that does not work: tilt the sight line.**
- To pass above one neighbour and below the other with 0.2 mm clearance, the
  camera must rise 9.9–11.9° [calc P §1].
- At 11° the silhouette of a crimp H × W reads H cos t + W sin t. That is
  +0.29–0.35 mm of crimp width inside the "height".
- Width varies ±0.15 mm, which puts ±0.03 mm of noise into a ±0.05 mm
  tolerance. It no longer measures crimp height.

**Repair A: neighbours out of plane** (a transfer from my
[a1](../explorers/ribbon-as-pallet/ideas/a1-pallet-tour.md)).
- The fan block holds every waiting conductor with its axis 4.1–4.55 mm above
  the barrel floor: the insulation wing tips (2.75–3.2 mm), plus 0.5 mm, plus
  the jacket radius [calc P §1]. a1's h ≈ 5 mm clears it.
- Only the active conductor goes down.
- **What changes.**
  - Camera 2's line runs under the neighbours, so the gate gets its side view
    back, and with it X.
  - Camera 1 at 30–35° sees past the camera-side neighbour down to the barrel
    floor at 5–6 mm pitch. At 45° the lifted neighbour hides the lowest
    0.2–1.2 mm of the U [calc P §1], so the oblique angle drops to ~30–40°.
  - The shroud can rise to ~3.3 mm above the floor, level with the insulation
    wing tips, under the lifted neighbours.
  - The after-crimp window sees one crimp.
- **What stays uncertain.**
  - The punch body's width at h. Beside neighbours at 5 mm pitch it must be
    narrower than ~8 mm at 5 mm up. This matches borrowed-machines' crimper
    tongue limit in its exchange on my a1.
  - How the active conductor gets down. Repair B answers that.

**Repair B, a branch: piano-key fan block.**
- *The problem with a finger.* A point finger has only 1.2–3.5 mm of free
  conductor ahead of the block to make a 5 mm drop
  ([borrowed-machines on ribbon-as-pallet, Break a1-1](borrowed-machines--on--ribbon-as-pallet.md)).
- *The mechanism.* Each conductor rides in its own hinged key: a printed
  finger of the fan block with a groove on its underside and a TPU retaining
  lip.
  - The hinge line sits where the fan has opened to about 2.5 mm pitch, the
    narrowest a 1.7 mm groove with 0.4 mm walls allows.
  - A servo plunger at the station, which could be v1's hold-down servo,
    presses the key over the nest down 5 mm to a hard stop on the pallet body.
  - The conductor near the contact stays straight in its groove. The bend
    happens at the key root: 9.6–14.5° at R 24–60 mm, 20–30 mm behind the
    contact [calc P §9].
  - After the crimp the key's spring lifts the crimped contact back to h. No
    ramp drags it over the next contact.
- *What changes.*
  - The bend moves out of the insertion-critical 5 mm behind the contact and
    into the fan, which is already bent.
  - The key's groove is the hold-down, pressing the insulation down.
- *What stays uncertain.*
  - Key stiffness and the retaining lip's grip on silicone during lift-out.
  - Whether printed key walls of 0.3–0.4 mm survive at a 2.5 mm hinge pitch,
    or the hinge line moves out to ~3 mm pitch, which lengthens the fan.
  - Whether the key-root set (R 24–60 mm, plastic) shows in the finished loom.
    It is inside the parted length and reversed once.

**Repair C, a branch: fold back.** borrowed-machines' b1 fold-back parking
clears the sight line by folding the neighbours 180° back. It needs no h, but
each root takes an R ~2 mm set per reversal. That is kept as the other route,
with its own costs.

### What the X servo is steering inside

- **Lateral capture that needs no picture** [calc P §2]:
  - the 0.72 mm bundle in the 1.68–1.90 mm-wide open conductor barrel: ±0.48–0.59 mm;
  - the 1.7 mm jacket in the 2.46–3.00 mm insulation barrel: ±0.38–0.65 mm.
- **What the pallet delivers:**
  - ±0.1 mm at the comb face, since the ribbon's own pitch stack from a
    centred datum is 0.23 mm worst for a 5P [calc R §1];
  - ±0.2–0.3 mm of tip wander.
- **What that leaves the servo to do.** In X it converges inside a funnel the
  wings already provide. The picture's real work is:
  - **Y**, the insulation edge in a 0.5–1.0 mm window;
  - the **gate**.
- **With a flush cut in the pallet** (my a1, a5), every tip is on one line, so
  one tip reading per ribbon end sets Y for all its conductors. v1's per-tip
  reading stays as the check.
- **What changes.** One or two servo rounds, starting from the pallet's
  prediction, instead of 3–8 [calc V cycle_and_cost §1]. X no longer depends
  on camera 2.
- **What stays uncertain.** How ragged the torn insulation edge is. Window
  placement still depends on it. The flush-cut tip is a clean copper face and
  a steadier axial datum than that edge.

### Z curl from the spool: their measure-and-steer stands; pressing flat does not help

- **Residual curl.** Ribbon wound at R 25–50 mm on a spool keeps a residual
  curl anywhere from R ~44 mm to straight. Depending on strand yield
  (50–100 MPa [assumption]), a tip 7 mm proud is off by **0.0–0.55 mm in Z**
  [calc P §6].
  - The worst case is near the spool core, and it is comparable to v1's
    ~0.3 mm spare in Z.
- **Pressing flat does not help.** A reverse bend of a strand stays elastic
  over 2κ_y, so a flat press removes no curl gentler than R 23–47 mm
  [calc P §6]. It springs back.
- v1's "the servo measures where the tip actually is" is the answer that works.
- A mechanical alternative is a small over-bend, or three rollers (a wire
  straightener) on the ribbon as it enters the pallet.
- This correction lands on my own "copper keeps its shape" (see the last
  section).

### Break v1-2 (shared with v3 and v5): what sits behind the box, where the proof plate goes

**Conflict.**
- v1 step 10: "A slotted plate slides in behind the box", then the stage
  pulls ~20 N.
  v3 pulls to failure (~100 N) against the same plate. v5 drops the crimp into
  a slot from above.
- Three things share the space between the box's rear and the conductor
  barrel's front (the neck) [calc P §3]:
  1. **The retention lance.** It springs out of the floor side toward the
     rear. Its tip is 2.4–2.6 mm behind the front, 0.4–0.6 mm behind the
     2.0 mm box, and stands 0.6–0.9 mm below the floor. It crosses the plane of
     any plate set against the box's rear.
  2. **The brush.** It protrudes 0.2–0.5 mm past the conductor barrel into the
     neck.
  3. **The neck itself** is undimensioned. Clone lengths give −0.20 to
     +2.18 mm, so the free gap after the brush is −0.70 to +1.98 mm.

**Physical consequence.**
- **A slot open upward (v5) hits the lance.** Its plate has material under
  the floor strip, where the lance is.
- **The lance is loaded in its retention direction.** In the housing, the
  lance tip against a shoulder *is* the retention.
  - The clone retention minimum is 19.6 N, the same as the proof pull.
  - A 20 N proof on the lance tip loads it at its rating.
  - v3's pull to failure would fold it.
  - The crimp passes, and the contact later latches weakly or not at all.
- **The plate may not fit.** If the neck is short, no plate fits between box
  and brush.

**Repair A: a lance-notched plate.**
- The plate must be:
  - no thicker than the measured free gap less 0.2 mm;
  - slotted wider than the floor strip and the lance;
  - narrower than the box less its walls (~1.4 mm);
  - slotted deep enough (≥0.9 mm below the floor) that the lance sits in the
    slot.
- It bears on the side walls, and on the top wall too if the slot opens
  downward. Side walls alone give ~0.9 mm² of bearing: 23 MPa at 20 N and
  114 MPa at 100 N. Bronze is fine [calc P §3].
- **What changes.** The lance is never touched.
- **What stays uncertain.** Whether a gap exists at all. One kit contact
  under the caliper or the ELP settles it.

**A repair that does not work: a push sleeve on the insulation crimp's rear.**
- The insulation crimp is 1.7–1.9 × ≤2.05 mm over a 1.7 mm jacket. That leaves
  a radial step of 0.00–0.17 mm, nothing to bear on [calc P §3].

**Repair B, for strip contacts: react through the still-attached carrier tab.**
The pull runs 0.40–0.85 mm above the tab plane, so the tab sees eccentric
compression.
- **Without a hold-down** the tab bends at **4–12 N** of pull.
  - Their own exchange found this for
    [terminal-supply a2b](machine-that-sees-and-learns--on--terminal-supply.md).
  - It is true of my a2 too.
- **With a hold-down and a support.** A hold-down 3–5 mm ahead of the tab
  prevents pitch; a support sits under the tab.
  - The hold-down needs 0.08–0.28 × the pull: 1.6–5.7 N at 20 N, 8–28 N at
    100 N [calc P §3].
  - The tab is then in near-pure compression. It yields at 72–96 N
    [assumption: bronze yield 450–600 MPa].
- **What changes.**
  - The proof pull never touches the box or the lance.
  - A crimp that survives to tab yield is already 1.8× JST's 39.2 N, so tab
    yield is a pass, not a lost test.
  - v1 already cuts the tab at step 11, after the pull at step 10, so the
    order is right.
- **What stays uncertain.**
  - Tab width and temper. The $4.71 strip settles both.
  - Whether 17–28 N of hold-down on the box top dents it at v3's loads.
    Holding down on the conductor crimp instead is the alternative.

**Repair C, for the grip end: pull from a grip just behind the crimp, not
through the fan.**
- The stage pulling "the wire" through the fanned conductor straightens its
  S-bend at the copper's 0.36 N·mm plastic moment [calc R §4]. The tip then
  retracts by the arc-minus-chord, a few tenths of a millimetre, so the crimp's
  Y shifts and the fan's shape changes.
- A grooved TPU jaw at the comb face gripping at ≥20–40 N normal (my a6 clamp
  [calc R §4]) keeps the pull local.

### v1's contact supply: the strip as the singulator

v1 leaves supply open: strip, v4 or a person. The strip has two ways to feed
the nest.
1. **Keep the contact on the carrier through crimp and proof pull.** This is
   Repair B above.
   - The carrier's slots index the contact, and its Ø1.5 mm pilot hole on the
     contact's centreline is a fiducial the camera finds before the wire covers
     it.
   - *Conflict:* in side feed the next contact waits one pitch (~7 mm)
     upstream on the X line, at wing-tip height. It blocks camera 2's backlight
     side, exactly as the neighbour conductors do.
   - *Repair:* the camera goes on the downstream side, where only the empty
     carrier remains. That carrier sits behind the barrels' Y range, in the
     floor plane, off the line. The backlight becomes a thin side-lit diffuser
     standing in the ~4–4.5 mm between the active contact's wings and the next
     contact's.
2. **Shear the tab before lay-in, over the nest.** The contact drops into the
   nest always barrels-up, box forward, lance down. That is everything v4
   buys with a tray, taps and a nozzle, with no vision.
   - The proof pull then needs Repair A.
   - *What stays uncertain:* whether a sheared contact drops into the pocket
     without hopping, and the tab stub, which is now cut before the crimp.

Genuine SXH strip costs $0.047 each in 100s [digest]. The kit contacts on hand
are loose, which is v4's case.

### Transfer: the electrical channel beside every picture

A pogo block on the far end's cut face (my
[a6](../explorers/ribbon-as-pallet/ideas/a6-housing-as-last-comb.md)) needs
the far end unterminated, so the XH end is made first. That order is already
the digest's recovery advice.
- **Placement.** The contact is grounded through the nest. Each conductor
  reads continuous the instant its strands touch the barrel, before the
  stroke, independent of the silver-on-silver picture.
- **Nicks.** In v6's split and strip, blades are electrically isolated (their
  printed holders already are) and wired as a sense line.
  - A blade touching copper is an event logged with the conductor's number,
    at the moment it happens.
  - "Cut shallow, tear the rest" never touches copper by design, so any touch
    is a fault.
  - Their calc says a few cut strands are 1.7 % of the copper each, inside a
    force monitor's band, and the tip picture is the only guard
    [calc V campaign §3]. This is a second guard of a different kind: it says
    *where and when*, and the picture then looks there.
- **After insertion.** Pin map and shorts, and J2's cavity 3 open. v5's wafer
  board does the same from the housing end.
- **What stays uncertain.** Continuity cannot grade a crimp: 6–34 mΩ of loom
  against a 1–2 mΩ crimp [calc R §9]. A strand touched but not cut also
  flags, so the picture decides.

### Transfer: the pallet holds the crimp's roll for the in-line silhouette

This belongs with Break v5-1 below. In v1 the crimped contact is still on its
parted conductor, and the conductor is still webbed to the ribbon in the
pallet.
- The conductor's torsion is 0.33–0.58 N·mm/rad [calc P §5]. It holds the
  roll the nest gave it, if the crimp is set on the blade at 10–20 mN
  (0.3–1.1° of roll).
- So the stage should stop at first silhouette contact, not at a force.
- At 50 mN, 0.3 mm off the knife line, roll reaches 1.5–2.6° and uses most of
  the tolerance.

---

## v1b A printer's axes as the stage

- **This is my a1's stage, priced.** a1 needs X and Y past fixed stations and
  ~10–20 N for one-after-another insertion [calc R §8]. The $199 bed-slinger
  is a concrete answer, and the belt Y holds a 20 N proof pull against the
  carrier (Repair B).
- **The pallet mount.** "A lift-off magnetic mount with two dowels" is a
  kinematic seat only if the contacts are steel. See Break v2-1 for why
  printed flanks under a magnet creep.
- **The tail.** v1b's open problem is keeping 100–600 mm of loom clear of belts.
  - With the XH end first, the tail is an unterminated cut end.
  - It coils in a cup on the pallet, with its cut face in the pogo block that
    rides on the pallet (a1, a6).
  - The carriage carries one object with no hardware swinging.

---

## v2 The arm taught by hand

### Break v2-1: printed kinematic flanks under a magnet yield and creep

- **Conflict.** A cone-vee-flat printed in PETG, preloaded by a magnet.
- **Numbers.** A steel ball on a printed flank at 10–30 N of magnet preload
  (2.4–7.1 N per flank, 4–6 mm balls) peaks at **67–126 MPa**. PETG yields at
  ~50 MPa [calc P §7].
- **Consequence.** The flanks bed in over the first seatings and then creep
  under the standing preload. "Tens of microns over hundreds of seatings" rests
  on plastic under yield stress.
- **Repair** (my a1b and a2 seats): steel balls and hardened dowel-pin pairs
  pressed into printed bodies. Only steel touches steel (877–1658 MPa Hertz
  peak, fine for hardened pins).
- **What stays uncertain.** Repeatability of such a seat with printed bodies
  behind the pins [estimate: a few µm]. A dial indicator over 50 seatings
  settles it. This is the one test v2 already names.

### What the arm is for shrinks at both ends of the procedure

- **The tail job.** Their account makes managing a 600 mm loom with a
  terminated far end the arm's "whole job", after the Sogang system lost its
  cycles to the floppy cable.
  - Terminate the XH end first, and the tail is a bare cut end coiled on the
    pallet (v1b above).
  - With [a4](../explorers/ribbon-as-pallet/ideas/a4-spool-as-magazine.md),
    the ribbon is never cut before termination. The tail is the spool itself,
    fixed in a rack, and the cut that frees a loom squares the next end.
  - Either way the arm carries one rigid pallet.
- **The peel.** My a5 P3 has the clamp face as tear stop: the tear cannot run
  past where the clamp holds the web.
  - A learned peel then does not need to judge when to stop. It grips and
    pulls sideways, and the pallet sets the parted length.
  - The wrist camera's "watch the tear front" becomes a check.
  - Whether the web tears along its line at all is still repo Open item 5.
- **Passive pallets.** In a1 every pallet mechanism (lid, fan block, pitch
  change, piano keys) is moved by the stage pushing it against a fixed stop.
  The arm never operates a pallet, it only carries one, which is the task
  where 50 demonstrations are most likely to suffice.

### Combination: the arm carries backshells, not pallets (v2 × a3)

- My [a3](../explorers/ribbon-as-pallet/ideas/a3-backshell-that-ships.md)
  snaps a 1–2 g printed clip onto each ribbon end. It is the datum, the recipe
  code, the label and, in the product, the strain relief.
- **What v2 contributes.** The arm picks looms from a tray by their backshells
  and docks each backshell into station holders. Palleting, the person's
  10–30 min per unit, becomes snapping 14 clips on.
- **What a3 contributes.** A rigid, keyed handle the SO-101's gripper can
  close on at ±1–2 mm, with its datum faces seated by the dock, not the arm.
- **What stays uncertain.**
  - Whether a ~12 mm-long clip holds the ribbon against fan, strip and
    insertion loads: tens of newtons of grip on silicone, a3's own open
    question.
  - Whether stations can do fanning with the ribbon held only there.

---

## v3 The press that runs experiments

### Break v3-1: a 40 mm coupon cannot wrap a capstan, and the jacket may tear at the drum

- **Conflict.** The pull axis wraps the conductor three turns around a
  10–15 mm drum before a pin. The coupons are 40 mm, and the campaign counts
  1.2 m of 5P.
- **Numbers** [calc P §4]:
  - Three turns plus the lead and tail need a coupon of **~150–200 mm**, or
    290 mm on a 25 mm drum.
  - That is 4.5–6.0 m of 5P for 153 coupons, still cheap (a 50 ft spool is
    15 m).
  - At the drum entry, friction per millimetre is μT/R: 6–17 N/mm at 100 N
    on 10–15 mm drums. Across a 0.5–1 mm contact strip of jacket that is
    6–34 MPa of shear, against silicone's 8–11 MPa tensile.
- **Consequence.**
  - Short coupons cannot be gripped as described.
  - At pull-to-failure loads the jacket can tear at the capstan entry before
    the crimp gives. That is v3's own "wire break at the capstan (a bad test)"
    category, which may dominate near 100 N.
  - A long pad clamp on the jacket fares no better: passing 100 N from jacket
    to strands takes 1.5–4.7 MPa on a Shore 60A jacket.
- **Repair: pull on copper at the far end.**
  - Strip 10 mm of the coupon's far end and solder it into a slotted lug with
    the bench's Hakko. Solder shear over that length carries 500–750 N, above
    wire break.
  - Coupons stay ~60 mm.
  - A slotted fork hooks the lug.
- **What changes.** Coupon length and wire use return to v3's figures, and
  failures can only be at the crimp or in the wire.
- **What stays uncertain.**
  - Wire breaking at the lug's fillet, where solder-stiffened strands meet
    free ones. It is a third failure mode, above ~80 N, and outside the window
    the campaign is looking for.
  - The 20 N proof pull on production looms can still use a jacket grip:
    0.5–1 MPa over 25 mm.

### Break v3-2: the reaction at the contact

This is Break v1-2. For kit contacts use the lance-notched plate, once the neck
is measured. For genuine strip, the carrier tab with a box hold-down holds to
72–96 N.

### Transfer: coupons made the way production makes them (v3 × a1/a5 × a2)

- **The confound.** v3 names coupon stripping as a confound: "150 clean strips
  on silicone".
- **A ribbon-end coupon.** Make coupons as ribbon ends in a production pallet:
  - a 5P piece ~80 mm long;
  - flush-cut, and all five stripped as one whole-end slug while still webbed
    (a5 S1);
  - then parted 25 mm and fanned to strip pitch.
  - Its five conductors dock onto a 7-contact carrier segment
    ([a2](../explorers/ribbon-as-pallet/ideas/a2-two-pallets-meet.md)).
  - The press crimps them at one set point.
  - Each is pulled in turn against the carrier, with a box hold-down, to tab
    yield or failure.
- **What changes.**
  - Strip quality is the production's own, so the sweep measures what
    production will make.
  - Five replicates per level come from one docking. The height sweep loads
    16 pallets, not 80 coupons.
  - Far-end continuity confirms each conductor sits in its contact before the
    stroke.
- **What stays uncertain.**
  - Far-end grips for pulling each conductor. Each needs its own soldered lug,
    so the far end is parted too.
  - Carrier tab yield (72–96 N) caps the top of the range.
  - Strip pitch (~7 mm [estimate]) sets the parted length.

### Transfer: the settable stop as stop blocks and a shim stack (v3 × a2b)

- **The stop.** v3 needs "a settable, repeatable stop". My
  [a2b](../explorers/ribbon-as-pallet/ideas/a2b-gang-press-stop-die.md) sets
  crimp height with hardened stop blocks. A feeler-gauge shim stack under them
  gives the 0.02 mm steps: 16 levels are 16 stacks, and the idle 12 t press
  drives it by hand.
- **Contributions.** v3 contributes the window and the ground-truth pictures.
  a2b contributes a height that belongs to the tooling, so production needs no
  per-crimp control.
- **What stays uncertain.**
  - In a gang die the per-station heights differ die to die. v5's silhouette
    measures each station once, and v3 must not read that spread as the
    sweep's effect.
  - Shim stacks compress slightly under 5–13 kN [estimate]. The silhouette
    height, not the stack, is the result, as v3 already says of its stop.

---

## v4 Tap, look, pick; v4b Pocket plate

- **Barrels-up does not lie flat.** The lance stands 0.6–0.9 mm below the
  floor.
  - A contact barrels-up on a flat tray rests on its lance tip and one end,
    tilted ~11–17° [estimate: 0.75 mm over the 2.5–4 mm from the lance tip to
    either end].
  - The box top is then not level under the nozzle. Pressing down levels it by
    pushing the lance, elastically at nozzle forces under a newton.
  - Two things follow. The camera's "barrels-up" class includes this tilt. And
    a spring-limited nozzle keeps the pick from bending lances, which v4
    already worries about for tapping.
- **The strip as the other singulator.** See "v1's contact supply" above:
  shearing the tab over the nest delivers every contact in the nest's pose with
  no tray.

### Combination: the tap-filled plate is the crimp cassette (v4b × a2c)

- **The plates are nearly the same.** My
  [a2c](../explorers/ribbon-as-pallet/ideas/a2c-loose-contact-cassette.md)
  nest bar and v4b's pocket plate are the same object at different pitches:
  pockets with a one-sided lance relief, filled by shaking.
- **The combination.** A v4b plate with one row of N pockets at crimp pitch
  (4–5 mm, free for loose contacts):
  - it is tap-filled and every pocket is photographed (full and flat, tilted,
    empty);
  - then the ribbon pallet docks on it, and every conductor drops into every
    contact in one motion.
- **What v4b contributes.**
  - Fill by tapping, with the camera as the per-pocket check.
  - Pocket width tuned by printed coupons (1.90–2.10 mm) per contact lot.
- **What a2c contributes.**
  - No nozzle, no rotating axis, no vacuum on a stage that also carries a
    pallet: v4's open problem of fitting both.
  - Placement by docking.
  - Far-end continuity per conductor.
- **What stays uncertain.**
  - The crimp needs steel under each contact. Anvils rise through floor
    windows in the plate (a2b's pallet windows), or a walking head's lower jaw
    reaches in from the open front of each cradle.
  - Tapping may pop seated contacts out, v4b's own open item.
  - A pocket's rear shoulder as pull reaction meets the lance and brush as in
    Break v1-2. My a2c has this problem as drawn.

---

## v5 The inspection booth

### Break v5-1: a crimp on a knife edge has no roll reference, and roll reads as height

- **Conflict.**
  - The blade stands on edge along the channel, a line under the barrel
    centre.
  - The clamp 20 mm behind closes soft jaws on round insulation.
  - Nothing sets the crimp's roll about the wire axis. The booth's "seam-up or
    seam-down give the same height" covers 180°, not a few degrees.
- **Numbers.** Viewed along X, a crimp rolled by r shows H cos r + W sin r
  [calc P §5]:
  - rectangle bound: +0.028–0.033 mm per degree;
  - rounded-bottom bound: about half that.
  - Against ±0.05 mm, roll must be held to **~1–2°** (rectangle) or ~2–4°
    (rounded).
- **Consequence.**
  - The error is always positive: a rolled crimp reads tall. A good crimp can
    read as under-crimped, and an over-crimp can read as good.
  - A hand-dropped crimp lands at whatever roll its conductor's twist gives
    it. Scatter from roll is added to the crimp-height scatter the booth is
    meant to learn.
- **Repair A: a roll datum on the box.** A light spring presses the box's flat
  top, or its floor, onto a ground flat beside the blade. The square box, not
  the round insulation, then sets roll.
- **Repair B: measure the least of a small roll sweep.** A servo rolls the
  insulation clamp ±4° in steps and keeps the minimum height. Slowness makes
  this ~10 s.
- **Repair C: measure in the pallet.** See the combination below.
- **What stays uncertain.**
  - Where the box's flats are true to the crimp. Crimp twist relative to the
    box is a real defect, and the top view already looks for it.

### Break v5-2: the slotted plate

This is Break v1-2 in its sharpest form. v5's slot must open upward for a
dropped crimp, so its plate lies under the floor strip where the lance is. The
slot needs to run ≥0.9 mm below the floor, wider than the lance.

### Combination: the booth docks a whole pallet (v5 × a1b × a2d)

- **The booth takes a ribbon pallet, not a loose crimp.**
  - The pallet sits on a kinematic seat on the booth.
  - A detented X slide (a1b) or a small stage steps each crimp over the blade.
- **Hand crimps from a strip.** With [a2d](../explorers/ribbon-as-pallet/ideas/a2d-by-hand.md)
  (dock a strip segment, squeeze a guided hand tool at each contact), the
  crimps are still on the carrier:
  - the proof pull reacts through the tab (Break v1-2 Repair B);
  - the tabs are sheared after inspection.
- **What v5 contributes.** Its optics, silhouette crimp height, top view,
  proof pull and log.
- **What the pallet contributes.**
  - Roll held by the ribbon (≤1° at 10–20 mN [calc P §5]).
  - Crimp position known without a search.
  - One dock per ribbon end, 14 a unit, instead of 53 drop-ins at ~20 s
    (~18 min a unit) [v5].
- **What stays uncertain.** The a2d hand tool's own crimp quality on this wire
  (digest measurement 3).

---

## v6 The patient cell

### Break v6-1: inserting into a rear-face-up housing from a horizontal pallet on the same head

**Conflict.**
- The housing sits "rear-face-up, lit from beneath", so insertion is
  vertical.
- The ribbon pallet, the same one used for crimping, lies horizontal on the
  head.
- The servo tweezer is on the same head as the pallet.

**Physical consequences** [calc P §8]:
1. **A quarter-bend in every conductor.** Turning each contact box-down makes
   a 90° turn inside the 25–35 mm parted length, at R ≤16–22 mm. That is well
   below the ~67 mm yield radius, so every conductor keeps a quarter-bend near
   the housing.
2. **The tweezer cannot move a conductor relative to the pallet** without
   axes of its own. "Lift it out of the comb and bring the box over its cavity"
   moves the pallet too.
3. **The housing tethers the pallet after the first latch.** Every later head
   move to reach cavity k bends the inserted conductors 1..k−1 into arbitrary
   sets. The forces are tiny (the plastic moment is 0.36 N·mm [calc R §4]), but
   the shapes stay in the product.
4. **A 0.8 mm gap for the jaw.** Beside an inserted neighbour at 2.5 mm pitch
   the gap is 0.8 mm. The slide-along jaw's side toward the previous conductor
   must be under ~0.4 mm.

**Repair A: close the pitch in the pallet and insert along the wire axis** (my
[a6](../explorers/ribbon-as-pallet/ideas/a6-housing-as-last-comb.md)).
- The housing nest turns so its mating axis is Y.
- The fan block swaps for a 2.5 mm block, or a pitch changer closes.
- A grooved clamp grips every conductor within ~2 mm behind its insulation
  crimp.
- Contacts go in one after another: a staircase clamp face, or Sogang's
  lean-and-slide (18/20 against 3/20 for a straight push).
- **What changes.** No 90° bend. No tethered pallet. No tweezer inside a 0.8 mm
  gap.
- **What stays uncertain.** a6's own open items: how deep the crimp's rear
  seats, and the staircase overtravel.

**Repair A keeps v6's latch picture, through the mating face.**
- XH housings show a trapezoidal window below each post opening on the mating
  face [mfr S1, S2]. xh-facts reads it as the lance's catch and the XJ-06
  extraction access [assumption, from the drawing]. If so, there is a straight
  line of sight from the mating face to the lance tip.
- With the mating face toward +Y, a small first-surface mirror (already on
  v1's list) in front of the nest turns that view up to a camera.
  - A latched contact shows its lance tip in its window.
  - An unlatched one does not.
- This reads the latch itself. v6's bright square going dark reads that the
  cavity is occupied, and its pull-back needs a retention threshold nobody has.
  a6's HX711 "lance snap" is uncertain at slow speed.
- **What stays uncertain.** Whether the lance tip is visible through the
  window of a white PA 6 housing at the ELP's 45 px/mm. One kit housing under
  the camera settles it, together with which face the lance faces.

**Repair B: keep v6's per-conductor, recipe-driven insertion, horizontal.**
- The tweezer gets its own small X–Y slide on the head (two micro servos, or
  a v1b-style second carriage). The housing lies with its mating axis along Y.
- **What v6 keeps.** It can take any conductor to any cavity, including J4's
  2–3 and J7's 1–2 crossings (digest), which row insertion (a6) cannot do.
- **What stays uncertain.**
  - The crossing conductors cross each other in the parted length, which
    needs slack there.
  - The 0.8 mm jaw gap remains.

### Break v6-2: a spring-loaded scalpel on a free ribbon pushes the ribbon, not the web

- **Conflict.** "~40 mm of the end free of the clamp". The scalpel lowers
  "until its spring slide deflects slightly", then the ribbon is drawn back
  under it. No support under the ribbon is described.
- **Numbers.** A 5P cantilevered 40 mm has a tip stiffness about its thin axis
  of **~0.003 N/mm**. A 0.1 N blade preload would ask for ~30 mm of deflection
  [calc P §8]. The ribbon bends away (and yields) long before the slide
  deflects.
- **Second conflict, with a support.** On a flat table the web hangs between
  two conductors over the lower valley. The blade stretches it down into the
  valley, v6's own worry.
- **Repair: an under-width channel with anvil ribs in the lower valleys** (my
  a1 and a5; AMP US 4,230,008).
  - The channel is ~0.2 mm under nominal width. It squeezes the conductors
    into register over steel ribs, one per valley: razor backs or 0.3 mm shim
    edges stood in the channel floor.
  - The blade scores down onto the rib, as a knife cuts silicone on a mat.
  - The channel registers each valley to within 0.12–0.43 mm, worst case from
    a centred datum, 3 to 9 conductors [calc R §1]. The line laser becomes a check
    of the channel rather than the finder.
- **What stays uncertain.**
  - Web thickness and valley depth: repo Open item 5, and a cross-section
    under the ELP.
  - Whether a rib narrower than the valley stays under the web as the ribbon
    is drawn.

### Transfer: the flush cut makes "back out" cheap

- **v6's back-out.** It cuts the ribbon end off and starts again, and strip
  retries shorten one conductor. v1 notes a shortened conductor "skews the
  housing".
- **With a guillotine in the pallet** (a1), back-out is one stroke 6–10 mm
  further in. Every tip is again on one line, so there is no skew.
- The pallet starts with that restart allowance in its free length.
- Per-conductor re-strips stay for small corrections (+0.2 mm). Anything
  larger re-cuts the whole end.

### Transfer: who cuts, pallets and labels

v6 hands back to the person:
- cutting to length;
- palleting 14 ends (15–30 min);
- stocking;
- labelling.

My view can take three of these:
- **[a4](../explorers/ribbon-as-pallet/ideas/a4-spool-as-magazine.md)**
  terminates each loom's XH end on the spool, then feeds out and cuts. Ten
  units' 530 board-end crimps come from six threadings [a4]. The
  person threads spools rather than palleting ends.
- **[a3](../explorers/ribbon-as-pallet/ideas/a3-backshell-that-ships.md)**
  embosses the loom name (the J4/J7 guard) on the part that ships.
- **Housings from a gravity magazine** in the nest (a6).

### v6's twist pads

The worry that the pads spin the 60-strand bundle inside its jacket rather
than twisting the stub mostly goes away on numbers.
- Spinning the bundle through the whole parted length resists ~7× the twist
  (1.2–1.4 against 0.13–0.18 N·mm).
- Through only the 7 mm to the comb, it resists ~1.5× [calc P §10, estimates].
- A pinch on the jacket at the strip line during the twist makes it certain.

---

## Combinations

| # | Theirs | Mine | What each contributes | What stays uncertain |
|---|---|---|---|---|
| C1 **Watched pallet station** | v1 gate, cameras, silhouette window, log; v6 ask queue | a1 fan block with neighbours at h ≈ 5 mm; piano-key lay-in (Break v1-1 Repair B); flush-cut Y datum; far-end port; tab-reacted proof pull | Theirs: the look before the stroke, crimp height in line, the record, the queue. Mine: an unblocked side view, X from the funnel, Y from the cut, roll held by the ribbon, an electrical second channel | Punch width at h; key lip grip; strip pitch if strip-fed; neck gap if loose |
| C2 **Booth with a pallet dock** | v5 optics, pull and log | a1b seat and detents; a2d hand crimps on strip | Theirs: verify with no automated crimper yet. Mine: roll and position reference, 14 docks a unit instead of 53 drop-ins, pull against the carrier | Hand-tool crimp quality; box hold-down design |
| C3 **Campaign on docked ribbon coupons** | v3 sweep, supervisor, report, re-check routine | a1/a5 production-made coupons; a2 docking onto a carrier segment; a2b stop blocks and shim stacks | Theirs: the window nobody published, and labelled ground truth. Mine: five replicates per docking, strip quality as production's, a height that belongs to the tooling | Far-end lugs per conductor; tab yield caps at ~72–96 N; die-to-die spread |
| C4 **Tap-filled crimp cassette** | v4b pocket plate, tapping, per-pocket picture | a2c docking and far-end check; a2b floor windows for anvils | Theirs: loose kit contacts oriented without tweezers, and seen. Mine: no nozzle or vacuum, all contacts placed in one motion | Anvils through a printed plate; pop-out; the pocket's pull shoulder vs lance |
| C5 **Spool-fed patient cell** | v6 look-act-look at every station, the queue | a4 spool clamp as the fixed pallet; stations come to it; travelling C-frame head (digest convergence) | Theirs: judgement at every station. Mine: no cutting, palleting or tail; the cut that frees a loom squares the next end | Machine size (~0.6 m drop); no far-end port unless a slip ring on the spool |
| C6 **Arm carries backshells** | v2 arm, docks, teaching, dagger corrections | a3 backshell as handle, datum, label | Theirs: handling that is varied and floppy. Mine: the handle is the part that ships, so there are no pallets to load | Backshell grip on silicone; whether stations can work with the ribbon held only there |

---

## What their view has not yet seen

- **The ribbon is already a fixture.**
  - The web holds conductors in order at 1.7 ±0.1 mm.
  - An under-width channel registers them to tenths without looking.
  - A flush cut makes a common tip line.

  v1's servo, v6's line laser and v6's per-tip strip placement find what the
  pallet can make. The pictures remain valuable as checks and as the gate.
- **Every handling bend stays in the product.** The strands yield below
  R ≈ 67 mm. v6's tweezer lift, 90° insertion, tail hook and tethered moves
  each leave a set behind the housing.
- **The parted length stays in the product.** v1's 5–6 mm fan pitch needs the
  web parted ~20–35 mm back [calc R §2], and that parted conductor remains
  behind the housing. It is Derek's open question (digest), and v1 and v6
  inherit it.
- **The lance and brush share the neck** where every proof pull in this view
  reacts (Break v1-2).
- **Roll is part of the height measurement** (Break v5-1).
- **The order of the ends.** v2 and v6 assume the far end is already
  terminated, and so manage tails with hardware on them. Terminating the XH
  end first:
  - removes the swinging Faston;
  - makes the far end a test port;
  - keeps a bad crimp from scrapping a finished loom (digest).
- **Parts handed back to the person that my view could take:**
  - cutting to length (a4);
  - palleting (a4, or a3's snap-on clip);
  - the per-crimp contact load in v1 (strip, or the C4 cassette);
  - labelling (a3);
  - housing supply (a6 magazine);
  - v3's 150 coupons (C3's production-made ribbon coupons).

---

## Where their work changes my own ideas (for my revision)

1. **a1 gets in-line crimp height and a look before the stroke.**
   - a1 had "crimp height is not measured in line" and one frame after the
     crimp.
   - v1's silhouette window can sit at a1's station, with neighbours at h. The
     pallet holds roll if the crimp is set down at 10–20 mN.
   - v1's gate (side silhouette, strands above wing tips, insulation in the
     window) goes before a1's stroke.
2. **a1's lay-in becomes piano keys.**
   - The finger's 5 mm drop has no room (borrowed-machines' Break a1-1).
   - A ramp bend-back leaves 1–4° toward the kink, 0.09–0.38 mm at a box tip
     5 mm ahead, unless over-bent [calc P §6].
   - Hinged keys move the bend 20–30 mm back at R 24–60 mm, and the key lifts
     the crimp, so no ramp is needed.
3. **"Copper keeps its shape" has a floor.**
   - Gentle curls, from R ~23–47 mm up, are elastic under reversal. Pressing
     flat does not remove the spool's Z curl (0.0–0.55 mm at 7 mm proud)
     [calc P §6].
   - The pallet's claim to hold tips in Z needs either a small over-bend,
     three straightening rollers at the pallet entry, or v1's measured
     steering.
4. **a2's proof pull bends the tabs as written.**
   - The support comb has swung away and the pull line sits 0.40–0.85 mm above
     the tab. The tabs bend at 4–12 N (their exchange on terminal-supply a2b;
     my calc P §3).
   - a2 needs a hold-down bar over the boxes and a support under the tabs.
     Then the tab reacts in compression to 72–96 N.
5. **a2c's rear shoulder meets the lance and brush.** The pocket needs the
   lance relief to continue under the shoulder (≥0.9 mm deep), and the shoulder
   has to fit the measured neck gap.
6. **a6 gains a latch picture and crossings.**
   - Through the mating-face window, the lance tip is seen in place of the
     HX711 snap count.
   - v6's per-conductor, recipe-driven insertion is the way a6 can do J4's and
     J7's crossings. As a branch, a6 keeps row insertion for the five 4P looms
     (38 % of crimps) and per-conductor insertion for crossing looms.
7. **a2b's stop blocks get their number from v3.** a2b's gang die needs v5's
   per-station silhouette once, to separate die-to-die spread from set point.
8. **a2c loading is v4b.** Tap-filling a pocket bar with a per-pocket photo is
   a2c's coin-motor shaker, made observable. Pocket width is tuned per lot on
   printed coupons.
9. **The ask queue and the per-pin log** belong in a1 and a4. Neither has a
   path for a doubtful case except stopping. The queue parks the case with a
   photo and a proposal, and the machine moves on.
10. **v1b is a1's stage.** A $199 printer gives X and Z on the carriage, with
    the station on the bed.

---

## Measurements that settle most of the above

1. **One kit contact and one SXH strip contact** under the caliper and the
   ELP, side and top. They settle:
   - the neck gap between the box's rear and the conductor barrel's front;
   - the lance tip's position, width and proud height;
   - the tab's width and thickness.

   Break v1-2 and a2c's shoulder hang on these.
2. **One crimp rolled on a knife edge** under the ELP at 0°, 1°, 2° and 3°:
   the height-per-degree that decides v5's roll datum.
3. **Ribbon from near the spool core.** Lay 7 mm of free conductor over a
   straightedge on camera for the Z curl, then press it flat and release. This
   confirms or refutes the elastic springback in calc P §6.
4. **One kit housing, mating face under the ELP with a contact latched and one
   not.** It shows whether the lance tip reads through the trapezoidal window.
5. **One coupon soldered into a lug and pulled** against a luggage scale, and
   one wrapped three turns on a 15 mm dowel. Which fails first, and where.
