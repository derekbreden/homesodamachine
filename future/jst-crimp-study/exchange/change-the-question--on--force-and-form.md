# change-the-question on force-and-form

change-the-question reads the five listed steps as one way to cut the problem:
the order can change, a step can be split or moved in time, the part or the
product can change. This file reads
[force-and-form](../explorers/force-and-form/summary.md)'s eight arrangements
that way: its idea files, its
[notebook](../explorers/force-and-form/notebook.md), its calc outputs and its
sketch labels.

Numbers marked **[calc off §n]** are in
[`../explorers/change-the-question/calc/on_force_and_form.py`](../explorers/change-the-question/calc/on_force_and_form.py),
with output in
[`on_force_and_form.out.txt`](../explorers/change-the-question/calc/on_force_and_form.out.txt).
Force-and-form's own numbers are cited as [f&f calc: file §n], and my wave-1
numbers as [ctq §n].

Force-and-form has settled the stroke itself: where force is needed, what sets
the bottom, what may be printed. The points below sit around the stroke:
- geometric conflicts in how a contact and a conductor reach the dies (f1, f3,
  f4);
- how often a machine calls the person back (f1);
- arrangements where reordering the procedure changes what the press must do
  (f5, f3b).

---

## f1 — the SN-2549 closed by an actuator

[f1](../explorers/force-and-form/ideas/f1-motorised-ratchet-crimper.md)

### Break 1: the machine calls the person back 53 times per unit

- **The conflict.** The keyed flap is loaded by hand once per crimp. At a 1–2
  minute cycle the person comes back every 1–2 minutes for one to two hours:
  14 ribbon loads plus 53 contact drops, **67 calls per unit** [calc off §7].
  As written, f1 is an attended station. It buys contact location and a logged
  curve, not the person's time. That is procedure-is-the-machine's p4 point,
  and here it applies to the step Derek most wants automated.
- **Repairs, each a branch.**
  - *Keyed stick magazine.* Extrude the flap's keyed profile (box plus lance
    notch) into a stick, loaded with 53 contacts at leisure; an escapement
    releases one per cycle into the flap in its loading position. That is 15
    calls. The 53 handlings remain, now in one sitting.
  - *Strip and a shear over the flap.* f4's dispenser shear cuts one contact
    off an SXH strip and drops it into the flap: 14 calls, a reel every ~150
    units. The slow cycle lets the dispenser and the ribbon carriage take turns
    over one opening. The shear has to leave a tab of at most one or two stock
    thicknesses, since JST lists both "no cut-off length" and "too much cut-off
    length" as faults [mfr S5].
  - *Tack first.* The carriage lowers a contact already fixed to its
    conductor. There is no feeder and no threading. This is Combination 2
    below.

### Break 2: a flap screwed under the jaws is filled through the nest

- **The conflict.** f1's flap is "screwed under the jaws" and the contact is
  "dropped into" it box down. With the tool flat, the box and its lance then
  have to pass down through the open XH nest, conductor section included.
  - Across the jaw-opening direction the box plus lance is ~2.8–3.25 mm (box
    2.2–2.35 mm, lance 0.6–0.9 mm proud [xh-facts §1]).
  - The box is 1.85–1.95 mm wide, wider than the ~1.5 mm conductor-crimper
    channel. So the box can only pass through the gap between the die faces,
    which must open 2.8–3.25 mm at the XH position [estimate].
  - Loading an open contact from the front face needs less: its open
    insulation wings (2.75–3.2 mm tall) sit in the insulation section, whose
    roof is ~1 mm higher.
- **The repair.** A hinged flap loaded outside the jaws, which swings in and
  carries the barrels up into the nest from the box face. This is how JST's
  own flap locator carries the contact [mfr S6, S7]. The magazine and the
  shear above then feed the flap in its swung-out position.
- **What it leaves.** The SN-2549's open gap at the XH nest is unmeasured, and
  a pin gauge settles it (Questions).

### Break 3: threading meets the insulation crimper

f1 lists this as open ("insulation clearance at capture"). Worked:

- **The numbers.** At capture the insulation wings sit inside the insulation
  crimper's 1.8–2.0 mm channel, so the clear width is 1.4–1.6 mm for a
  1.6–1.8 mm conductor.
  - That is 0–0.4 mm of interference and 10–41 % wall strain.
  - The push is roughly 0.2–6 N [calc off §1, estimate].
  - 6 N is the Euler load of a 5 mm free length [sibling calcs:
    ribbon-as-pallet pallet_geometry §4, into-the-housing insertion_geometry
    §1]. A guide within ~3 mm of the barrel mouth carries the worst case with
    about 2× margin.
- **The anchor.** The repo's hand procedure already does exactly this: close
  the SN-2549 one click so the contact is captive, then feed the wire
  [repo cable-assemblies.md]. So a capture height where the insulation passes
  exists, at least for a hand that wiggles.
- **The repair.**
  - Take the capture target from the tool: the jaw gap at the first ratchet
    click, measured with feeler or pin gauges. Do not take it from "the first
    force rise", which may lie deeper.
  - Give the carriage a wiggle: a small lateral or rotational oscillation
    during the push, like Sogang's housing "weaving" [prior-art, Start here].
- **What it leaves.**
  - Whether the first-click gap grips the contact hard enough to resist the
    push.
  - Whether the torn silicone front edge skives on the wing edges. The camera
    after the crimp shows the insulation edge in the window or not.

---

## f1b — the WC-110 in the cradle

[f1b](../explorers/force-and-form/ideas/f1b-wc110-in-the-cradle.md)

- **The WC-110 buys two separable things: JST's locator and JST's profile.**
  My view pulls them apart.
  - *Locator.* f1's keyed flap supplies it, or a contact already tacked to its
    wire.
  - *Profile.* It is testable before the $536 is spent. Crimp five on the
    ribbon with the SN-2549 and compare them with a genuine JST factory crimp
    (the $0.90 ASXHSXH22K305 lead, c2), corrected for copper area [calc off
    §6].

  If the SN-2549 lands within ±0.05 mm of the corrected height and passes
  39.2 N, what the WC-110 still adds is its wire stop.
- **The wire stop as a force rise.** The stop arrives during the last 1–2 mm of
  travel, while the insulation is squeezing through the captured insulation
  barrel at 0.2–6 N [calc off §1]. A force threshold alone cannot tell "tip at
  the stop" from "insulation snagged at the mouth". Position can: the carriage
  knows where the stop should be to ±0.2 mm. The rule becomes "a force rise
  inside a ±0.3 mm window at the expected depth".
- **What that leaves.** How much push a bare 2.4 mm tip takes against a stop
  before its strands spread.

---

## f2 — crank press for a bought applicator

[f2](../explorers/force-and-form/ideas/f2-crank-press-for-an-applicator.md)

Nothing in f2 breaks from where I stand. What changes is around it.

- **The fork at 1.7 mm pitch.** A split ribbon has its OD equal to its pitch
  (1.7 ±0.1 on 1.7), so neighbouring conductors touch: the gap is −0.1 to
  +0.1 mm.
  - A fork tine cannot come down between them near the root. It has to enter
    at the free tips and slide rootward, wedging them apart.
  - c1's interlaced split puts the ±1.7 mm neighbours into the other plane
    first. Within a plane the conductors sit at 3.4 mm with 1.7 mm gaps, and a
    fork with tines up to ~1.5 mm comes straight down between them.
  - The other plane, folded down and back under the clamp nose (c1 step 3),
    lies below the anvil and outside the ram's path.
  - This applies equally to the forks of f1, f3 and f4.
- **An output pallet: insertion taken off the person.**
  - f2 hands back insertion, with the crimped contacts dangling on split
    conductors in ribbon order. The carriage that laid conductor i into the
    applicator can, after the stroke, set its crimped contact into a pocket on
    one of two pallets at 5.0 mm pitch, one for the odd cavities and one for
    the even.
  - A pusher then drives each half-row straight into alternate cavities (c1
    steps 7–8), and the housing goes onto a real male XH wafer for the test.
  - A single-conductor station places one contact at a time, so it can deliver
    in *cavity* order rather than ribbon order. J7's one crossing and J4's two
    are then made by the order of delivery. No gang can do that.
  - J4's largest move is 6.3 mm sideways (IO26 and GND) over a 15–20 mm
    split, 17–23°. J7's is 4.2 mm, 12–16° [calc off §9].
- **Dialling the applicator.** On JST's MKS-L the conductor dial moves ~0.05 mm
  per graduation [mfr, via f2]. The copper-area correction between a genuine
  JST lead and this ribbon is 0.02–0.07 mm [calc off §6], about one
  graduation. So a reference crimp sets the dial only after the correction.
  Sectioning an OTP crimp beside the JST lead also answers f2's open question
  of which contact the OTP profile was cut for.
- **Spool-fed T4 runs (c5).**
  - At ~1 minute per crimp including carriage moves, a T4 end takes ~4–5
    minutes. A 15.2 m 4P spool makes 21 long or 38 short ends [ctq §9], which
    is ~1.5–3 hours, inside one printing day.
  - With the output pallet, the wafer test and a guillotine, f2 becomes the
    termination station c5 hosts (Combination 3).

**f2b** ([file](../explorers/force-and-form/ideas/f2b-arbor-press-with-a-hard-stop.md)):
every f2 transfer above applies unchanged. I have nothing to add to the frame.

---

## f3 — knee micro-press

[f3](../explorers/force-and-form/ideas/f3-knee-micropress.md)

### Break 1: the pilot pin stands in the threading path

- **The conflict.**
  - The lead contact's pilot hole is on its centreline, 2.2–2.65 mm behind the
    insulation barrel (tab 0.7–1.15 mm plus half of a 3.0 mm carrier) [calc
    off §2; carrier width from the Würth drawing, mfr].
  - The conductor slides along the carrier's top face, ±0.85 mm about the same
    line.
  - A pin dropped into that hole from above is in the way. Riding over
    0.3–0.5 mm of pin tilts the conductor 6.5–12.8° upward, into a captured
    insulation barrel that already has less clearance than the conductor's OD
    (Break 3 of f1).
  - borrowed-machines found the same hole under the same wire against
    ribbon-as-pallet a2 (their exchange, Break a2-2).
- **Repairs.**
  - *Pilot the upstream contact's hole,* one pitch back, where an applicator's
    feed finger works. The carrier is still attached, so it holds the lead
    contact against the threading push, with the tab in tension. This adds one
    pitch of strip tolerance to the location [estimate ±0.02–0.05 mm].
  - *No pin at the lead contact at all.* This is the MKS-L's practice (guide
    plates, pressure plate, and the anvil cradle centring as the crimper
    closes, per borrowed-machines' reading of the manual).
  - *Withdraw the pin after capture.* The capture alone then holds the contact
    axially against 0.2–6 N, which is unknown.

### Break 2: the order of cut, thread and pull, and a fork with nothing to bear on

- **The order.** The idea file cuts the tab last (step 8). The sketch cuts it
  at step 3. Each order moves a conflict:
  - *Cut last:* the proof-pull fork (step 7) has to fit in the 0.7–1.15 mm
    between the insulation barrel and the carrier, over the tab. Pulling the
    wire drives the contact toward the carrier, loading the tab in
    compression.
  - *Cut at capture (the sketch):* the carrier no longer reacts the threading
    push. A contact shoved 0.1 mm forward leaves the bellmouth window.
- **The fork's bearing face.** Behind the insulation barrel there is almost
  nothing to pull against [calc off §8].
  - The crimped insulation barrel is 1.8–2.0 mm wide and ~1.8 mm tall. It
    hides behind the uncrimped 1.7 mm wire's own outline.
  - A slot that lets the wire through leaves 0.03–0.18 mm of rim per side,
    none for a 1.8 mm wire in a 1.8 mm crimp, plus 0.2 mm of floor edge.
  - The fork bears on silicone. The proof pull then measures how hard the fork
    grips silicone, not the crimp.
  - This also reaches force-and-form's transfer to into-the-housing i2
    ("the slotted backstop behind the insulation barrel is the proof-pull
    fork").
- **The repair: a reorder, and a different face.**
  1. Pilot upstream.
  2. Capture.
  3. Thread, with the carrier in tension.
  4. Crimp.
  5. Re-touch.
  6. Cut the tab.
  7. Pull against a steel blade lowered from above into the space over the
     conductor crimp, bearing on the box's rear face.

  That face offers 1.3–1.7 × 1.9 mm [calc off §8]. The load path is then the
  one JST's pull test means: wire, conductor crimp, contact, box. The lance is
  on the floor side, clear of a blade from above.
- **What it leaves.** Whether the blade marks the box. The length of the space
  between box and insulation barrel, ~2–3 mm [estimate], which a kit contact
  settles.

### Branch f3-t: no strip, a keyed steel nest, contacts arrive already tacked

This comes from c1b.
- **What stays.** The knee, wedge, load cell and re-touch indicator.
- **What changes.**
  - The pilot pin and strip track become a steel nest with a box stop,
    ±0.02–0.05 mm [f&f calc: placement_budget], as good as the strip's
    ±0.03–0.06 mm.
  - The contact arrives on its conductor, so the carriage lays it in from
    above with the crimper open 5 mm, as an applicator does. There is no
    threading, no pilot pin and no tab.
  - The CQRobot kit's loose contacts become usable.
- **What it leaves.**
  - Whether c1b's tack holds the contact square while the carriage moves it.
  - Whether a loosely tacked insulation barrel re-forms cleanly in f3's
    insulation crimper.

---

## f3b — curl at a light station, coin at a stiff one

[f3b](../explorers/force-and-form/ideas/f3b-two-station-forming.md)

- **One station, three finishes.** Station A's product is a contact with its
  insulation crimped and its conductor wings curled onto the strands but not
  coined. That is c1b's tack made stronger, and it is c3's fold. It has three
  finishes:
  - coin at station B (f3b);
  - crimp by hand or in any single die (c1b);
  - solder (c3).

  Station A commits to none of them. The finish can differ per loom or change
  later.
- **What station A takes from c1b: gang placement.**
  - At 3.4 mm a half-row is laid by one presser-comb motion.
  - Station A's force per contact is the end of the curl plateau plus the
    insulation crimp, ~180–580 N [f&f calc: stroke_model §1; xh-facts §4].
  - A half-row of 2–5 then needs ~0.4–2.9 kN. That is past c1b's tack (under
    700 N), and past the ~450 N at which f3b calls a printed frame harmless.
  - So a gang station A wants a steel local stop. The alternative splits it
    again: gang the insulation tack only, and curl at a single die.
- **What c1b takes from station A.** c1b's first open problem, tack grip on
  silicone, shrinks. Wings curled round the strands hold a contact more
  firmly than an insulation tack does [estimate].
- **One experiment answers four ideas.** Section and pull ten crimps on the
  ribbon made each of four ways:
  - in one stroke;
  - insulation first, then conductor (c1b; the order JST's YC tools and the
    PA-09 use was not read);
  - curl, then coin (f3b);
  - fold, then solder (c3).

  f3's press makes all four. A non-ratchet PA-09 makes the first two. The JST
  reference lead gives the target for the first.

---

## f4 — the head goes to the wire

[f4](../explorers/force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md)

### Break: the head cannot leave the crimp, and its funnel cannot reach the pick

- **The release conflict.** The head carries its anvil under the contact and
  its crimper over it.
  - *"Drops away downward."* Moving the head down moves the opened crimper
    onto the contact. With the knee's 5 mm opening it closes on the contact
    after 3.3–3.5 mm and never frees it [calc off §3].
  - *"Back off" along the wire (the sketch).* This pulls the rear funnel over
    the crimped contact. The funnel exit is 2.0 mm; the crimped end view is
    1.95 × 2.4 mm, 3.09 mm on the diagonal.
  - A downward move would also take the closed funnel through the wire.
- **The pick conflict.** The carrier (3.0 mm wide) and tab (0.7–1.15 mm) lie
  directly behind the insulation barrel, which is exactly where the rear
  funnel has to sit.
- **Repairs.**
  - *Split funnel.* The upper half rides on the crimper side and the lower half
    on a small sprung or servo slide on the anvil side.
    - It opens with the knee, and the head retreats forward along the
      conductor, the dies sliding off past the box. That needs the crimper
      open only 1.8–2.0 mm above the crimp, and the knee gives 5 mm.
    - At the pick, the lower half stays back until the tab is cut and the head
      has cleared the carrier.
  - *No funnel on the head.* The comb holds each conductor's insulation to
    within ~3 mm of the stripped tip, and the captured barrel's flared mouth is
    the funnel.
    - The head camera aims a 1.4–1.6 mm mouth to about ±0.05 mm.
    - The push of 0.2–6 N [calc off §1] over a free length of 5 mm or less is
      within Euler: 6 N at 5 mm, ~17 N at 3 mm.
    - This leaves tip scatter past the comb, and how well the camera sees a tip
      standing out 3 mm.
- **Either way the exit is along the conductor, toward the box.** Sideways is
  closed by the ±5 mm neighbours, and downward by the crimper.

### Transfers into f4

- **A comb at 5.0 mm per plane.**
  - After c1's split, the upper plane goes into a 5.0 mm comb. Its conductors
    move 1.6 mm or less for rows of three or fewer [calc off §4]. The lower
    plane waits, folded back.
  - The head crimps a whole plane, and those contacts then already sit at
    twice the housing pitch. A housing brought to them takes the half-row in
    one straight push.
  - The board is already the fixed reference, and f4 already suggests it hold
    a housing.
  - The push has to bear on the box's rear face, not the insulation barrel
    [calc off §8], or grip the silicone within ~2 mm of the barrel.
- **The board at the spool's exit (c5).** The ribbon still never moves during
  crimping. The tail stays on the spool until a guillotine cuts it, which is
  f4's premise and c5's together.

---

## f5 — die cassette and the shop press

[f5](../explorers/force-and-form/ideas/f5-die-cassette-and-the-shop-press.md)

f5's own open item is the station pitch. At strip pitch a whole ribbon end fans
30–38 mm, and the person lays floppy stripped tips into it
[f&f calc: gang §1].

### Combination 1: a half-row cassette at 5.0 mm

- **The arrangement.**
  - f5's cassette: steel shoes, guide posts, stop blocks setting height, and
    any press to close it.
  - c1's half-rows: the stations sit at 5.0 mm, twice the housing pitch, and
    each stroke crimps one half-row, the odd cavities and then the even.
- **Numbers** [calc off §4].
  - *Spread.* Going from 3.4 to 5.0 mm moves the outer conductor 0.8 mm in a
    row of 2, 1.6 mm in a row of 3, 2.4 mm in a row of 4 and 3.2 mm in a row
    of 5.
  - *Comb capture.* A straight V-tooth comb captures any move under half a
    slot (2.5 mm). With ±0.2 mm of lay error the margins are +1.5, +0.7, −0.1
    and −0.9 mm.
  - *Coverage.* 36 of the 53 crimps per unit (68 %) sit in rows of three
    cavities or fewer: every T4, J2 and J6 row, and the 3-rows of J4 and J7.
    The 4-rows (J1 B, J4 A, J7 A) and J1's 5-row need a tilted or rolling
    comb.
  - *Force.* A row of 2 takes 1.6–4.9 kN and a row of 3 takes 2.3–7.3 kN. A
    1 t arbor press covers rows of up to three at the high estimate.
  - *Steel between stations.* 0.6–1.5 mm, for crimpers 3.5–4.4 mm wide
    [f&f calc: gang §1].
- **One 5-station cassette serves every row.** An unused station closes to the
  stop without a contact. Its crimper and anvil never touch, because crimp
  height is a positive gap. J2's empty cavity 3 is an empty middle pocket, so
  the load stays symmetric.
- **The lower shoe is already the insertion pallet.**
  - Its pockets at 5.0 mm face alternate cavities of a housing held at the
    shoe's front edge.
  - A gate in front of the boxes is the axial stop during the crimp. It lifts,
    and a pusher drives the half-row home. The pusher either bears on the
    boxes' rear faces [calc off §8] or grips the silicone within ~2 mm of the
    barrels. Whether a 0.4–0.6 mm tongue fits into the cavity above the
    insulation crimp is unmeasured, and one kit housing settles it.
  - The wafer test follows the second row.
- **What each side contributes.**
  - *f5:* the self-stopping steel cassette, any-press drive, inspection before
    force, and the summed force.
  - *c1:* the split into planes, the comb lay from 3.4 to 5.0 mm, crimping at
    insertion pitch, two straight pushes and the wafer test.
- **What it changes.**
  - The split is 12–20 mm long instead of 25–40 mm.
  - There is no convergence after the crimp.
  - For rows of three or fewer, c1's lift and cam plate are not needed.
- **What it costs, and what it leaves uncertain.**
  - Loose contacts in pockets, loaded per row: 30 calls per unit, against
    14–28 for f5 as written [calc off §7].
  - The J4 and J7 crossings are made at the lay: one on J7, two on J4, by hand
    or a crossover finger.
  - A multi-station crimper block with webs of 0.6–1.5 mm.
  - As in f5, the summed force cannot name a station, and the camera before
    the stroke is the per-station check.
- **Scope.** A T4-only version is two stations. The program's 1,200 T4 crimps
  become 600 two-station strokes.

### Branch f5-k: keep the strip as the pallet, crimp every k-th conductor

- **The arrangement.** Four conductors span 4 × 1.7 = 6.8 mm, 0.3 mm from
  Würth's 7.10 mm carrier pitch. For any pitch from 7.1 to 9.5 mm, some k of
  4, 5 or 6 sits within 0.7 mm [calc off §5].
  - A strip segment on pilot pins takes conductors {1, 5, 9 …}, then
    {2, 6 …}, and so on.
  - Each conductor moves 0.7 mm or less, instead of 12–15 mm.
- **The price.**
  - k strokes per ribbon end, with small gangs: 3P 1+1+1; 5P 2+1+1+1; J1 laid
    as nine, 3+2+2+2.
  - The conductors not in the row have to be lifted off the anvil plane:
    3–4 mm, 11–19° over a 12–20 mm split [ctq §4].
- **What decides it.** The $4.71 strip decides k.

### Smaller break: the loom map belongs in the force check

- J2's and J7's 3P ends each carry a trimmed conductor. In a strip cassette
  that station either crimps a contact with no wire or runs with a gap in the
  strip.
- The sum then falls by the same 8–20 % [f&f calc: gang §4] that f5 reads as
  "missing conductor".
- So the expected occupancy of each ribbon end has to set the band.

---

## Transfers from change-the-question

1. **Tack first, and one fold station with three finishes** (c1b, c3) into f1,
   f3 and f3b.
2. **The interlaced split into planes** (c1) into the forks of f1–f4 and the
   combs of f4 and f5. In-plane pitch is 3.4 mm with 1.7 mm gaps, where a
   fork or comb descends without wedging.
3. **Half-rows at twice the housing pitch** (c1) into f5's cassette, f4's comb,
   and an output pallet for f2 and f3. Crimp or collect at 5.0 mm, then insert
   straight.
4. **The real-wafer tester** (c1, c5), for the test every force-and-form idea
   hands back.
5. **The reference crimp with a copper correction** (c2).
   - The correction: H_ribbon ≈ H_ref − (A_ref − 0.302 mm²) / (1.5 mm ×
     0.8–0.9) [calc off §6]. It is 0.02–0.07 mm, the size of JST's ±0.05 mm
     tolerance. Count the lead's strands under the ELP camera to get A_ref.
   - Where it lands:
     - f1: is the SN-2549 profile close to JST's?
     - f1b: is the WC-110 needed?
     - f2: the dial.
     - f3: the wedge target.
6. **Ends as stock, T4 first, terminate at the spool** (c5):
   - f2 as the spool-run host;
   - f4's board at the spool exit;
   - a two-station T4 cassette for f5.
7. **The contact's form sets the call rate** [calc off §7]; c4's "choose the
   contact for the machine".
   - The strip-fed ideas (f2–f4) call the person once per ribbon end.
   - Loose-contact f1 and the half-row cassette call once per crimp or per row.
   - The kit's loose contacts are a convenience, not a constraint: strip costs
     $0.008–0.047 a contact [xh-facts §6].

## Combinations

- **C1 — half-row cassette (f5 × c1).** Above, under f5.
- **C2 — a tack station feeding a crimp station (c1b × f1 or f3-t).**
  - *c1b contributes* placement of a whole half-row in one motion. Each contact
    is pinned at its axial position and roll.
  - *The crimp station contributes* the heavy crimp, one contact at a time,
    with a steel or keyed locator and a logged curve.
  - *f1 as the host.* f1's keyed flap becomes the locator the SN-2549 lacks,
    which is c1b's third open problem. The flagged contact still has to enter
    the nest box first from the wire side, which needs the gap of f1 Break 2.
  - *f3-t as the host.* The crimper lifts 5 mm clear and the contact is laid
    in from above, with no gap condition.
  - *What goes:* the per-crimp contact drop and the threading.
  - *Calls:* 34 per unit, none paced by the crimp [calc off §7].
  - *What it leaves:* the tack's grip under the carriage's side loads, and
    tack-first crimp quality (the f3b experiment).
- **C3 — f2 with an output pallet, wafer tester and spool (f2 × c1 × c5).**
  - *What it makes:* T4 ends from start to finish, one spool run at a time.
  - *Who contributes what:*
    - f2 places, crimps and cuts;
    - c1 contributes the pallets, the push and the test;
    - c5 contributes the feed, the cut and the bins.
  - *What it leaves:*
    - whether the carriage sets crimped contacts reliably into 5.0 mm pockets
      (a rigid 1.95 mm box into a pocket of about 2.1 mm);
    - the pusher's face (box rear).
- **C4 — station A with three finishes (f3b × c1b × c3).** It comes with the
  one sectioning experiment (f3b above).

## What force-and-form's view has not yet seen

- **Everything before the fork.** All eight arrangements start from a split,
  stripped ribbon the person supplies. At 1.7 mm pitch the split conductors
  touch, so any fork at the root is a wedging operation from the tips. c1's
  interlaced jaws hand over planes at 3.4 mm with room between conductors.
- **Everything after the crimp.** All eight hand back insertion and the test.
  The output pallet at 5.0 mm, the straight push and the wafer tester take
  them.
- **The target height.** f3's re-touch reads crimp height to a micron, and
  f2's dial moves 0.05 mm. But the height to aim at is licence-gated. The
  $0.90 JST lead supplies it, once its copper is counted [calc off §6].
- **Push and pull faces.** Behind a crimped XH contact on this ribbon there is
  almost no metal [calc off §8]. The box's rear face is the bearing face for
  proof pulls and insertion pushes. Its top 0.4–0.6 mm stands clear of the
  insulation crimp, so a pusher bearing there withdraws straight back. Whether
  such a tongue also fits inside the housing cavity beside the insulation crimp
  is unmeasured.
- **The call rate.** The person's return rate is set more by the contact's
  form than by any mechanism [calc off §7].
- **Pin order.** A single-conductor station with an output pallet makes J4's
  and J7's crossings by delivery order. A gang has to make them at the lay.

## Where force-and-form's work changes my ideas

- **c1.**
  - The screw ram becomes a knee lift under the pallet [f&f calc: drives §B]:
    60–160 N from a NEMA 17, with the top of the lift at straight.
  - The hard stop moves into a short steel loop between the punch mount and
    the ram guide. A loop through a printed frame sits 0.2–0.85 mm open at
    peak and drifts [f&f calc: force_loop §1].
  - The punch and anvil become a harvested SN-2549 jaw pair ($9.99), used as a
    matched pair. They replace an SN crimper working over a separate HSS
    blank.
  - A re-touch indicator across punch and anvil gives crimp height on every
    crimp.
  - New branch: spread before the crimp to 5.0 mm for rows of three or fewer
    (68 % of crimps). For those rows it drops the lift and the post-crimp cam
    plate. The cam-plate version stays for J1 and the 4-rows [calc off §4].
  - My pusher comb "straddling each wire behind the insulation barrels" bears
    on 0.03–0.18 mm a side [calc off §8]. It becomes one of two things:
    - a blade on the top 0.4–0.6 mm band of each box's rear face;
    - a silicone grip within ~2 mm of the barrel.
- **c1b.**
  - f1's keyed flap with its lance notch becomes the heavy crimp's locator.
  - f3b's station A becomes a curl-tack branch, stronger on silicone, and it
    brings the gang-force caveat above.
- **c3.**
  - force-and-form's stroke model puts the end of the curl at 150–450 N,
    0.15–0.2 mm above bottom [f&f calc: stroke_model §1]. My "tens to ~300 N"
    moves up.
  - A printed folder frame opens ~0.16 mm at 450 N [f&f calc: force_loop §1].
    That is more than c3's ±0.1 mm fold-height tolerance. The fold needs a
    steel local stop, or to stop on the curve's shape as f3b does.
- **c2.** The copper correction becomes part of how the reference crimp is
  used.
- **c4 and c5.**
  - Carrier pitch now decides f5's fan, k in f5-k, and f3's upstream pilot
    distance. That puts more weight on the $4.71 strip.
  - f2 is a candidate host for c5's spool runs.

## Questions this exchange adds for Derek

- With the SN-2549 at its first ratchet click, what gap lies between the XH
  nest's jaw faces (feeler or pin gauges)? Does a ribbon conductor go into the
  captured contact without wiggling?
- With the handles fully open, what gap lies between the jaw faces at the XH
  nest? It decides whether a contact can be dropped through the nest into a
  flap below (f1) or needs a swinging flap.
- If JST ASXHSXH22K305 leads are bought: how many strands, and of what
  diameter, are in the lead's conductor? That sets the copper correction.
