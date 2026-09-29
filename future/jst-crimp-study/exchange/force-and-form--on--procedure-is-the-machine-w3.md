# force-and-form on procedure-is-the-machine (wave 3)

- **The view doing the reading:** *a crimp is a small, slow sheet-metal forming
  operation* ([`../explorers/force-and-form/summary.md`](../explorers/force-and-form/summary.md)).
- **The view being read:** *the sequence and the division of labor are the
  design* ([`../explorers/procedure-is-the-machine/summary.md`](../explorers/procedure-is-the-machine/summary.md)).
  - All twelve idea files were read. The wave-2 additions are p1c, p4b, p5b, p6
    and p7; p1, p2, p3 and p5 carry wave-2 repairs.
  - Also read: their calc outputs, and the wave-2 critique
    [hand-tool-as-press on procedure-is-the-machine](hand-tool-as-press--on--procedure-is-the-machine.md).
    Its breaks (presser into strip hardware, presser set, fork on the shear
    line, proof pull through the dies, contact's own axial reference) are not
    repeated here.

**Citations**
- **[calc FP §n]:** this exchange's numbers,
  [`exchange_procedure_w3.py`](../explorers/force-and-form/calc/exchange_procedure_w3.py),
  output [`exchange_procedure_w3.out.txt`](../explorers/force-and-form/calc/exchange_procedure_w3.out.txt).
  Its §1 imports procedure-is-the-machine's own set model (their `wave2.py`
  §1) read-only, so the set figures below are theirs, run at new lifts.
- **[calc P name §n]:** procedure-is-the-machine's calcs.
- **[f&f wave2 §n]:** force-and-form's wave-2 calc.
- **[ith ex §n]:** into-the-housing's
  [`exchange_hand_tool_as_press.out.txt`](../explorers/into-the-housing/calc/exchange_hand_tool_as_press.out.txt).
- **[H §n]:** hand-tool-as-press's
  [`exchange_procedure.out.txt`](../explorers/hand-tool-as-press/calc/exchange_procedure.out.txt).
- **[Prime: …]:** a row of [`../sourcing/amazon-prime.md`](../sourcing/amazon-prime.md),
  observed 2026-09-28.

---

## 1. Combinations

### FP1: lift once, crimp upright, fin from below

Sketch: [`../explorers/force-and-form/sketches/fp1-lift-once-fin-from-below.svg`](../explorers/force-and-form/sketches/fp1-lift-once-fin-from-below.svg)
(schematic).

**The pairing.** It combines four things:
- procedure-is-the-machine's **p1c order**: lift conductor *k* once, and do
  everything to it in that pose;
- its **cassette** or **p6's spool clamp**, and its post-held contacts in key
  order;
- force-and-form's **steel C with a knee**, standing still at the station
  (f4's head, not travelling; f3's geometric bottom and re-touch gauge);
- a **fin anvil** that rises *from below* through *k*'s own empty slot between
  the unlifted neighbours (f7's ground stock on edge, f8's lance relief).

**What the pairing does that neither side does alone:**
- **p1c's tip-down SN-2549 makes every crimp rolled 90°** (Break B1 below) and
  depends on the unmeasured *t*.
- **f4 needs the ribbon split into planes and spread to a 5 mm comb.**
- **FP1 works on the ribbon at housing pitch, 2.5 mm, in one plane.**
  - It lifts *k* only 3.5 mm.
  - The crimp comes out upright, lance down, the way every housing cavity
    wants it.
  - Crimp height is a setting that is measured on every crimp, from steel
    Derek chooses (f7).

#### Picture it: J1 in its cassette (or the 4P end at p6's reel clamp)

**Where things start.**
- **The cassette is loaded as in p1:** keys 1–9 = cavities 1–9, crossings
  made in the loft, J2's key 3 blanked, far end in the pogo block.
- **The comb:** p1's comb of 0.635 mm music-wire pins [Prime: Music wire,
  0.025 in, K&S 5005, $7.24] holds the conductors 20–30 mm back.
- **A tip comb:** a second, short row of the same pins, also on the
  cassette, stands 4–6 mm behind the tip line. Its tops sit ~1 mm above the row
  axis.
- **A post bar rides the cassette's X carriage.**
  - It holds J1's nine contacts box-first on 0.64 mm posts (header pins
    [Prime: 2.54 mm male pin headers, $7.99]), one post per key, in key order.
  - The posts are in **two tiers**: odd keys at one Y, even keys ~8 mm
    further forward. Open contacts on one tier are then 5.0 mm apart, where
    open wings (2.46–3.0 mm) do not touch.
  - The posts sit at the lifted height, ahead of the tips.
  - The person fills it at leisure. It is the build list, as p1c's revolver is.
  - A kit contact and a strip stub cut to one pitch are both just "a contact
    on a post" (terminal-supply a4, x1).

**Fixed at the station (bench B's frame).**
- The X slide carries the cassette and its post bar.
- A lift-finger servo under the station line, ~10 mm behind the contacts.
- A trim blade and a strip head on a Y carriage (p1c), or none if p7 has
  stripped the end.
- The ELP camera looking **along X** at the lifted height, with a light pad
  [Prime: LED light pad, A5, $16.99] on the far side. Only *k* is at that
  height, so its silhouette stands alone.
- **The steel C.**
  - Its spine stands ~15–20 mm ahead of the tips. Its throat opens toward the
    cassette, and the row indexes through the throat in X.
  - The **upper arm** carries a knee driven by a NEMA 17 on a Tr8×2 screw
    [Prime: NEMA 17 with integrated T8×2 lead screw, $27.99] at 60–160 N. The
    knee drives a crimper on two ground guide pins, with a 0.001 mm indicator
    across the dies [Prime: Digital indicator, 0.001 mm, $52.99].
  - The **lower arm** lies entirely below the row. In a slot in it slides the
    fin. When the fin is up, a ground **gate block** slides under the fin's
    foot on a servo, and a button load cell sits under the gate [Prime:
    Button compression load cell, 500 kg, $74.99].

**One key, *k*** (about 60–90 s [estimate]):
1. **Index.** X brings key *k* to the station line. The fin is down (its top
   1 mm below the row's underside), and the crimper is open.
2. **Lift.** The finger raises *k* by **h = 3.5 mm**.
   - The neighbours stay in the row.
   - *k* lifts out from between its two tip-comb pins.
3. **Trim.** The trim blade is grounded. Cutting through copper, it touches
   *k*'s strands, so the far-end pogo block (or p6's hub socket) reads which
   conductor this is, and that no other conductor reads. **Identity is taken
   here, where copper is touched anyway.**
4. **Strip** in the pose (p1c), or already done by p7.
5. **Look.** The side silhouette gives the bare length, that is, where the
   insulation edge is, and whether the brush is whole.
6. **Place.**
   - The post bar's Y slide (MGN9 [Prime: MGN9 rail, $16.12] and a small
     stepper) moves contact *k* −Y. It slides onto *k*'s stripped end through
     fully open barrels: 0.72 mm of strands into a 1.5–1.9 mm U, and 1.7 mm of
     jacket into 2.46–3.0 mm wings.
   - It stops where the measured insulation edge lands mid-window. The
     contact's box-front-to-barrel offset was measured on its post (p1c's
     ±0.07 mm RSS row [calc P wave2 §3]), and nothing handles the contact
     between that measurement and the crimp.
   - The other contacts on the bar ride over their own unlifted conductors:
     h ≥ 2.8–3.1 mm keeps their lances clear [calc FP §1a].
7. **Fin up.**
   - The fin rises 4.3 mm through *k*'s empty slot, between *k*−1 and *k*+1,
     and the gate block slides under its foot.
   - The fin's top meets the contact's floor under the barrels. The box
     overhangs its front edge, so the fin stops behind the lance (f8's
     relief).
   - Clearance to the neighbours is 0.92 mm a side against an uncrimped
     jacket and 0.78 mm against a crimped, squared insulation barrel at the
     1.45 mm conductor step. At the 1.88 mm insulation step it is 0.70 and
     0.55 mm [calc FP §2].
8. **Crimp.**
   - The knee drives the crimper down to the knee's straight position: 0.2 mm
     short of straight is ~1 µm (f3).
   - At the end of the curl (~150–450 N, before compaction) the drive pauses.
     The wings' tips are then on the strands, so continuity through the post
     confirms identity a second time.
   - Then compaction. The load cell logs force against knee position.
9. **Height.** The crimper re-touches at ~10 N, and the indicator reads the
   unloaded crimp height (f3). Or the knee chases a measured target in two or
   three hits [f&f wave2 §10].
10. **Clear.** The knee opens. The gate block slides out and the fin drops 4.3
    mm, clearing the lance by far more than its 0.6–0.9 mm. The post bar backs
    +Y off the box.
11. **Pull.** A hook drops into the neck behind the box's rear face and pulls
    +Y 20 N through a spring, with a switch. Only the crimp carries it (the
    wave-2 critique's pull through the box). What must hold the other end is
    in B7.
12. **Lay back.** The finger lowers *k*. At h = 3.5 mm the residual rise is
    0.46–2.16 mm at 15 mm free, 0–0.77 at 20, 0–0.05 at 25 and none at 30
    [calc FP §1, their model]. p1c's squaring presser tidies what is left.
13. Next key. J1 takes ~9–14 minutes.

The unit's row is then upright, squared, fronts on one line and lances all
down: bench C's gang insertion (p1), or the person.

**What each side contributes**

| From procedure-is-the-machine | From force-and-form |
|---|---|
| p1's cassette: keys = cavities, loft crossings, blanks, far-end pogo block; or p6's reel clamp with the hub socket | f4's steel C standing at the station, spine ahead of the tips: the crimp force closes inside it |
| p1c's lift once: trim, strip, measure, place and crimp *k* in one pose | f3's knee at straight as the geometric bottom; re-touch height every crimp; chase-the-height branch |
| p1c's camera bare-length correction and post-measured contact offset (±0.07–0.09 mm) | the fin anvil from ground flat stock on edge (f7 route d), stepped for the two barrels |
| posts loaded in key order: the build list | f8's lance relief; the narrow crimper (≤ ~4 mm) that misses the posts either side |
| identity at every crimp through the far end | the rule that only the fin may enter the row plane, so the lift is set by die geometry, not by a hand tool's shape |
| squaring and bench C gang insertion | force curve on a load cell in the lower die stack |

**What locates what**

| Moment | Located | Against | Held to |
|---|---|---|---|
| Dock | cassette | bench B dowels | ±0.02–0.05 mm |
| Index | key *k* | X lead screw | ±0.02 |
| Lift | *k*'s height at the contact | lift finger | ±0.1 (the open U forgives ±0.3) |
| Neighbours at the fin | *k*±1 laterally | tip comb pins on the cassette | ±0.1–0.2 against 0.55–0.92 clearance |
| Place, axial | contact barrels vs insulation edge | post-bar Y slide, corrected by the silhouette and the on-post offset | ±0.07–0.09 RSS |
| Place, lateral | contact on the fin | the crimper's own entry flare centres it; the post bar is built laterally compliant so the steel wins | ±0.02 at first touch |
| Crimp height | crimper to fin | knee at straight + gate block thickness, all in the steel C; read by the indicator | ±0.01 (read), ±1.5–6 µm from force scatter at 100–200 kN/mm [calc FP §3] |

"Fixed" for position is bench B's frame. "Fixed" for crimp height is the steel
C alone.

**What drives the crimp and carries its force.**
- A NEMA 17 Tr8×2 pushes the knee joint at 60–160 N.
- The loop is crimper → knee links → upper arm → spine → lower arm → load
  cell → gate block → fin → contact.
- The cassette, the post bar, the lift finger and the X/Y slides carry
  positioning loads only.
- The post bar sees a few newtons, when the crimper's flare centres the
  contact.

**How it knows the crimp worked:**
- identity at the trim, and again at the end of the curl;
- the force curve against knee position;
- the re-touch height on every crimp;
- the side silhouette before and after: bare length and brush, then
  bellmouth and insulation edge in the window;
- the 20 N proof pull and its switch;
- the squaring presser's force.

**What it automates, and what the person does.**
- **Automated:** trim, strip in pose (or p7), measure, place the contact,
  crimp, measure height, proof pull, identity at every crimp, and square.
- **The person:**
  - cuts;
  - peels, or splits with p7;
  - lays the cassette, including J4 and J7's crossings in the loft;
  - loads the post bar in key order at leisure;
  - docks the cassette, or a magazine of them;
  - inserts at bench C or by hand;
  - labels.

  At p6's reel clamp the post bar rides the clamp's X slide (stage 2's
  revolver becomes this bar). The reel is the far end.

**Branches kept beside it.**
- **FP1-reel.** At p6's clamp or p3's work clamp:
  - The proof pull is reacted by the whole reel, which removes B7.
  - Identity goes through the hub socket, and a bad crimp costs 6 mm of reel.
- **FP1-SN-crimper.** A harvested SN XH crimper half (f7 route a) as the upper
  die over the fin.
  - At h ≥ 3.1 mm its bar clears the neighbours [calc FP §1a].
  - But it is 20–30 mm long in X and comes down on the posted contacts for
    *k*±2. So it needs a single shuttle post instead of the bar.
  - The fin must also be matched to the SN channel's width (pin gauges
    [Prime: Precision pin gauges, $45.58] read it).
- **FP1-laminated fin.** The fin can be laminated from Prime-confirmed 1095
  blue-tempered shim [Prime: Spring steel shim, 0.005–0.032 in, $53.39]:
  - 0.032 + 0.025 in = **1.448 mm** for the conductor step;
  - 0.032 + 0.032 + 0.010 in = **1.88 mm** for the insulation step.

  Clamped face to face, its top is lapped across the leaves. Spring temper
  (~Rc 45–50 [assumption]) against 400–900 MPa of mean die pressure is its
  open question. Ground O1 stock (my requests #22 and #28) is the harder
  route.
- **FP1-f6.** The crimper carries only the conductor step. f6's separate
  insulation blade, on its own small drive and wedge, forms the insulation
  barrel to its measured window on silicone.

**What it leaves uncertain.**
- **The steel.** The crimper profile comes from a knife set (price and profile
  unobserved) or wire EDM (±0.01 mm from a good shop; JLCCNC states ±0.05)
  [f&f wave2 §8]. This is all of f7's open list.
- **The transition *t*.** A fin that stops behind the lance and still
  carries the conductor barrel's front needs t ≥ 0.34–0.74 mm. The clone
  drawings' length budget gives 0.30–2.28 [f&f on_into_the_housing §1d].
- **Tip wander** near the tips against 0.55–0.92 mm of fin clearance. The tip
  comb is the repair, and it is unbuilt.
- **Set below 20 mm free.** At 15 mm free the rise is still 0.5–2.2 mm, so
  squaring stays.
- **The gate block and fin drop over ~3,200 cycles**, and whether a load cell
  in the lower stack costs height stability. It is read by the indicator
  anyway.
- **The post bar's lateral compliance** against its positioning.
- **The proof-pull reaction** at a cut loom (B7).

### FP2: the camshaft turns a knee, not an eccentric or a handle (p5/p5b × f3 × FP1)

- **The machine.** p5's one-motor, one-turn-per-conductor timing diagram,
  with FP1's station as its tooling.
  - The cams are: index pawl on the cassette's rack (p5), lift (p5b),
    post-bar Y, fin up and gate, a **knee lobe**, the hook pull with its
    spring and switch, and lower-and-square.
  - The knee sits in FP1's small steel C.
- **The knee lobe.**
  - It drives the knee *through* straight to a stop just past it. The dies'
    lowest point is at straight, so the lobe's printed profile error does not
    reach crimp height, as with a crank at bottom dead centre.
  - The printed cam frame carries only the knee's 60–160 N input. The C
    carries the crimp.
  - Shaft torque follows from the crimp's work, 0.13–0.44 J over a 40–60°
    lobe: 0.12–0.63 N·m average and ~0.25–1.9 N·m peak [calc FP §8; estimate
    of the profile factor]. p5b needs 2.1–3.2 N·m to squeeze an SN handle.
- **The motor.**
  - p5's NEMA 17 worm-gear stepper has no Prime listing [Prime: "NEMA 17
    worm-gear stepper, 30:1–50:1", none found].
  - A 12 V self-locking worm gearmotor at 40 kg·cm (3.9 N·m) and 10 rpm
    [Prime: Greartisan, $26.99, 40 ratings] covers FP2 directly, or through a
    3:1 belt to ~3 rpm.
  - An AS5600 on the shaft (my request #9) gives the angle.
- **What it drops from p5:** the eccentric, the stop blocks, the preloaded
  stack, the fin between dropped neighbours, and the presser. B4 below is why
  that matters.
- **What it keeps from p5b:** the fixed-depth axial chain. The Y dwell is cut
  in the cam, ±0.21 mm RSS [calc P wave2 §3]. A small stepper on the post bar
  alone buys back the camera correction, and that is the only departure from
  "one motor".

### FP3: p7 strips at the reel for f2c's applicator station (p7 × f2c × p6)

f2c's first open problem is splitting and stripping on the spool unattended.
p7's two straight blades, closing on steel stops across the whole webbed end at
the clamp, take the whole slug in one stroke: 43–59 N for a 4P at a 0.2 mm
ligament by the tension bound, less from the score lines [calc P wave2 §7].
- **One backlit frame** measures every insulation edge. f2c's carriage then
  sets each conductor's depth into the applicator individually, so the frame's
  per-conductor edges become per-conductor corrections.
- **The applicator's strip and anvil are grounded.** A conductor laid into
  the pre-fed contact reads through p6's hub socket or p3's slip ring, which
  gives identity before each stroke.
- **p6's puller** replaces f2c's push-out of 400/700 mm into the guillotine,
  and the housing is never the handle.
- **What it leaves:** p7's own open problems (B5), and the split into planes
  that f2c's two 5.0 mm pallets want (change-the-question c1).

### FP4: one strip line for a gang (p7 × f5b, f9)

- **What p7 gives a gang.** A half-row cassette (f5b) or a tack pallet (f9)
  lays every barrel of a row at one fixed Y. p7 puts every insulation edge on
  one line in one stroke.
- **The fan moves the outer edges back** by ~0.6 d²/L [calc FP §7]:

  | Half-row at 5.0 mm (from a 3.4 mm plane) | 12 mm split | 20 mm split |
  |---|---|---|
  | row of 2 | 0.03 mm | 0.02 mm |
  | row of 3 | 0.13 mm | 0.08 mm |
  | row of 4 | 0.29 mm | 0.17 mm |
  | row of 5 | 0.51 mm | 0.31 mm |

  - Rows of 2–3 carry 68 % of the unit's crimps [f&f wave2 §9]. They keep
    their edges inside ±0.13 mm.
  - Rows of 4–5 need their pockets staggered by the computed pattern (fixed
    per row length). The alternative is stripping after the spread, which
    gives up p7's webbed registration.

### FP5: the reel as the qualification rig (p6 stages 0–1 × f6, f7)

- **What runs there.** f6's 35-crimp insulation-window sweep and f7's
  comparison of four steel sources, run at p6's reel clamp on the real ribbon.
- **What the reel gives each sample:**
  - identity, and open or short, through the hub socket;
  - a proof pull reacted by the whole reel;
  - bend-and-look (f6);
  - a bad sample that costs 6 mm of reel.
- **What stage 1 then is.** The first motorised crimp (p6 stage 1) is where
  f3's knee cartridge, or an SN, is judged against the $0.90 JST reference
  lead with Derek watching. That is p6's "stage 1 measures for the next",
  pointed at the steel.

---

## 2. What still breaks in their new and revised ideas

### B1. p1c, p2 head T, p3 step 4 (C1), p3b, p5b, p6 stages 1–5: every crimp comes out rolled 90°

**Conflict.**
- p1c hangs the SN-2549 tip-down "with its jaws closing across the row", and
  lifts *k* by *t* + 1.85 mm so the neighbours pass under the jaw tip.
- An SN nest's axis is normal to the jaw plane. A jaw closing along X
  therefore puts the contact's floor normal along X.
  - Every barrel opens along the row.
  - Every lance points at a neighbour, not at the housing's window face.
- This is exactly the flat-fixture variant hand-tool-as-press a3 describes,
  and its own file sets aside for this reason: "every crimp is rolled 90°"
  ([a3](../explorers/hand-tool-as-press/ideas/a3-tool-travels-to-ribbon.md),
  [ith ex §8]).
- p2's head T, p3's C1 station, p3b, p5b and every stage of p6 from 1 on use
  the same module in the same pose.
- None of their files mentions the roll.

**Physical consequence.**
- No XHP can be slid onto the row. Bench C, p3's gang insertion from a tube,
  and p6 stage 4 all stop.
- The rolled row does not even lie flat. With every floor facing one way, the
  box's top side reaches +1.35 mm from the conductor axis and the floor side,
  with its lance, −1.65 to −1.95 mm. At 2.5 mm pitch, each lance overlaps the
  next box by 0.5–0.8 mm at the lance tip [calc FP §1b]. Where the
  neighbouring box ends, the overlap is ~0.3–0.6 mm [estimate, from the
  lance's taper].
  - into-the-housing's "0.1–0.3 mm gaps" leaves out the lance.
  - So p1c's squaring presser, pushing each crimp into a TPU slot bar
    "within ~0.5 mm of the row", pushes lances into boxes.
- **Twisting each conductor back 90°** over a 20–35 mm split takes the
  strands 2.3–4× past torsional yield, and the residual roll is unknown
  [ith ex §8]. p2's bow-and-push gripper could roll each contact as it
  inserts, but over its shorter bow length the strain is higher.
- **At p6 stage 1 the person inserts by hand**, so each contact can be turned
  as it goes in. Every conductor then carries a quarter-turn behind the
  housing.

**Repairs and branches.** Each changes something different.
- **(a) FP1.**
  - What goes: the SN module is replaced by a steel C with a fin rising from
    below. The lift falls to 3.5 mm, and the crimp is upright.
  - What stays: every p1c order rule, the camera correction, the posts and
    identity.
  - What is left uncertain: the die steel, *t* and tip wander (FP1 above).
- **(b) a3-e: the cassette, or p6's reel clamp, on edge.**
  - The ribbon plane stands vertical and the keys stack in Z. The tip-down
    tool then closes normal to the ribbon plane, and the crimp is upright.
  - The lift becomes a side-pull by the jaw half's depth plus ~2 mm: 8–14 mm
    for a = 6–12 mm [assumption, hand-tool-as-press a3].
  - Their own model at those pulls [calc FP §1]:

    | Free length | Pull 8 mm | Pull 11 mm | Pull 14 mm |
    |---|---|---|---|
    | 25 mm | 0.33–3.56 | 1.98–6.73 | 4.33–10.01 |
    | 30 mm | 0–1.70 | 0.31–4.46 | 1.60–7.49 |
    | 35 mm | 0–0.42 | 0–2.35 | 0.21–5.01 |

    (Residual rise at the tip, mm.)
  - So a3-e wants a 30–35 mm split and a squaring pass on every conductor.
  - At a reel, "on edge" means the reel lies flat on a vertical axle.
- **(c) The tool on its side, jaws pointing across the row, closing in Z.** The
  crimp is upright. The lower jaw half sits under *k*, so the lift is again
  a + ~2 mm, with (b)'s numbers. The row can stay flat.
- **(d) a3-t: twist and untwist.** A rotating lift finger turns *k*'s tip 90°
  before the crimp and back after. The residual roll is the question, and the
  cavity's lead-in squares only ±10–15° [ith ex §8, estimate].

**What stays uncertain.**
- *t* and *a*, both unmeasured.
- Which way the SN-2549's XH nest actually opens when the tool hangs
  tip-down. One crimp photographed end-on settles it (Measurements).

### B2. p1c, p4b, p5b, p6 stage 1+: capture at the first ratchet tooth, then an axial feed, meets a pinched bore

**Conflict.**
- In every SN head of theirs the contact is made captive at the first tooth,
  and the conductor is then fed axially into it.
- At capture the insulation wings' tips are pinched to the crimper channel,
  1.4–1.6 mm apart. The bore the jacket meets at its equator depends on the
  barrel floor's width [f&f wave2 §1]:

  | Floor width | Bore at the jacket's equator |
  |---|---|
  | 1.6–1.7 mm | 0.03–0.17 mm of interference with a 1.7 mm jacket |
  | 1.8 mm | ±0.05 mm |
  | 1.9 mm and wider | clear |

**Physical consequence.**
- The jacket's square-cut front edge meets a wing tip's rear edge.
- The feed is a lead screw (p1c, p6 stage 2+), p4b's clamp slide, or a fixed
  cam dwell (p5b). The conductor is supported ~10 mm back.
- It either rides in with the jacket's front edge rolled back under the
  wings, or it stalls. A free bare bundle 1.6–2.4 mm long buckles at 6–14 N [calc FP
  §5].

**Repairs.**
- **Row 4 of their own order table.** "Contact placed on the conductor first,
  tool closes around both."
  - The contact sits on its post with its barrels fully open. The conductor,
    or the post, slides in.
  - The tool closes around both, and its hold click then captures contact
    and conductor together.
  - FP1 does this with a fixed die. For an SN head it means the post brings
    the contact to the conductor, and the open jaws come to both.
- **Or keep the pusher short of the first tooth.** A lead screw can hold any
  position. The jaws then just locate the contact's box and barrels without
  pinching the wings, and the neck blade holds it axially.

**Uncertain:** the kit contact's floor width, which one end-on photograph
gives.

### B3. p1c, p4b, p6 stage 1: identity by strand touch on the neck blade and a camera-set depth are two stops on one axis

**Conflict.**
- p1c's step 7 reads identity when the strands touch the grounded flap blade.
  It sets depth from the camera: insulation edge mid-window.
- The two agree only if every bare length is exactly the window-to-blade
  distance. The strip scatter is ±0.2 mm, the largest term in their own chain
  [calc P wave2 §3].

**Physical consequence.**
- About half the conductors reach mid-window before touching, so no identity
  reads.
- The other half touch first, and are then fed 0–0.4 mm further into the
  blade against a bundle that buckles at 6–54 N [calc FP §5]. Strands fold
  back inside a captured barrel. That is a crimp defect force monitoring
  cannot see (one strand in 60 is ~1.7 % of force [digest]).

**Repair.**
- **Take identity where copper is touched anyway:**
  - the grounded trim blade, which cuts copper in the lifted pose;
  - or strands on the contact through a wired post at the end of the curl
    (FP1 steps 3 and 8).
- **Keep the tips off the neck blade by design.** The neck then has to hold
  box clearance, the blade, the scatter gap and a visible brush:
  0.05 + 0.3 + 0.25 + 0.1–0.3 = **t ≥ 0.70–0.90 mm** [calc FP §5]. The
  clone-drawing budget allows 0.30–2.28. p6 stage 1's touch-off-only depth
  (±0.22 mm RSS) is unaffected, because it has no camera to disagree with.

**Uncertain:** the kit contact's neck length. It is the same photograph as
f8's *t*, and as hand-tool-as-press's neck measurement.

### B4. p5: with stop blocks, the frame and the drive carry the margin, and the preloaded stack sets a floor under every stroke

**Conflict.**
- **To be sure of reaching the stops,** the eccentric must be able to push
  past them by a margin *m*. That margin covers frame creep, bearing play and
  shim error, 0.02–0.10 mm [assumption].
- **The margin costs k_loop × m of surplus force, on every stroke.**
  - On a stiff frame, 0.05–0.10 mm takes the loop to the stack's preload.
  - p5 sets the preload "above the crimp force (~3.5–4 kN)".
- **The frame's load at BDC** [calc FP §3; 'high' case, 2.43 kN crimp]:

  | Frame | m 0.02 | m 0.05 | m 0.10 |
  |---|---|---|---|
  | 40 kN/mm, stack 3.5 kN at 3 kN/mm | 3.23 kN | 3.57 (stack on) | 3.70 (stack on) |
  | 40 kN/mm, stack 4.0 kN at 10 kN/mm | 3.23 | 4.09 | 4.49 |
  | 20 kN/mm | 2.83 | 3.43 | 3.62–4.14 |
  | 10 kN/mm | 2.63 | 2.93 | 3.43 |
  | 5 kN/mm | 2.53 | 2.68 | 2.93 |

- **Consequence:** "A soft frame under ~3 kN cyclic load" understates what a
  stiff p5 frame carries. It is 1.5–2.1× the crimp force every stroke once the
  stack engages, and that goes through the printed parts, bearings and worm
  3,200 times.

**What it changes in their torque table.**
- p5's stiffness-versus-torque table (from [H §4]) says a NEMA 17 through
  30:1 wants a ~20 kN/mm frame. That table puts the whole 2.6 kN at the crank
  angle where the overtravel equals the frame's deflection plus the margin.
- In a compliant loop the stops touch when the eccentric is *m* above bottom
  dead centre, whatever the frame's stiffness.
  - The rigid stop height is δ0 = F/k + *m*.
  - The die is at the stops when z − δ0 + F/k = 0, which gives z = *m*.
  - Compaction happens earlier in the crank at lower force, while the frame
    winds up.
- **The peak shaft torque** comes to 1.0–2.3 N·m for frames of 2–40 kN/mm
  [calc FP §3]:

  | Frame | [H §4] | This model |
  |---|---|---|
  | 5 kN/mm | 4.28 N·m | 1.85 N·m |
  | 40 kN/mm | 2.32 N·m | 2.17 N·m |

- **Energy check.** Shaft work is the crimp's 0.13–0.44 J plus the frame's
  strain energy (0.17–1.7 J), and the frame returns its share after bottom
  dead centre.

**Repair: with stops, compliance is the design, not the defect.**
- **A deliberately compliant loop**, a plain unpreloaded spring in the rod or
  a springy printed frame at ~5–10 kN/mm:
  - keeps the surplus at 1.05–1.4× the crimp;
  - caps a doubled contact (a rigid +0.2 mm) at 3.9–5.4 kN by itself.

  A 40 kN/mm frame with no stack puts 14.4 kN into that doubled contact; the
  stack caps it at 4.3 kN.
- **Height stays on the stops.** This is force-and-form's "hard stop in a short
  steel local loop; the outer frame may be springy".
- **Or FP2.** A knee at straight in a small steel C (100–200 kN/mm) gives
  ±1.5–6 µm from force scatter, with no stops and no surplus at all.

**Where the load cell goes.**
- p5 puts it "under the anvil", and p1's B-drop "under the fin". If it sits
  between the fin and the fin holder, it is *inside* the stop loop.
- A 500 kg button cell's 0.05–0.1 mm of full-scale deflection (~50–100 kN/mm
  [estimate]) then moves crimp height by ±3–12 µm with ±300–600 N of force
  scatter. The stops cannot remove that.
- Under the whole lower die, holder and stops together, the cell is outside
  the loop and sees the stop contact as the sharp stiffness rise p5 already
  plans to read.

### B5. p5b: a spring link that caps force below the ratchet's release leaves a locked tool for the displacement cams to drag

**Conflict.**
- The link is preloaded to 275 N. The handle's need is 90–220 N by
  hand-tool-as-press's figures, and 40–250 N by force-and-form's [drives],
  both unmeasured.
- The digest quotes ~280 N at the grip as what a NEMA 17 Tr8×2 delivers to a
  hand tool.
- A ratcheting tool releases only at its end position. That release is itself
  a geometric bottom at the handle.
- If any crimp needs more than 275 N to reach the release, the lobe
  completes, the link compresses, and the pawl stays engaged.
  - The jaws stay clamped on the contact.
  - At 255–285° the Y cam's proof pull and at 300–335° the lift cam then drag
    a locked tool and the conductor it holds.
  - The switch cam's go/no-go at 335° comes after both.

**Repairs.**
- **Read ratchet release** (a microswitch on the pawl, or the jaws' opening)
  at ~255°. The shaft is turned by a stepper or a gearmotor that can stop
  there before the Y and lift cams act.
- **Or remove the pawl** (hand-tool-as-press a1b). The lobe then drives the
  handle by displacement through the link.
  - If the jaws bottom face to face, the jaws are the stop and the link
    caps the surplus: B4's compliant-rod design, inside a hand tool.
  - If they do not bottom, the tool's 10–40:1 handle-to-die ratio shrinks a
    printed lobe's ±0.1–0.2 mm profile error to ±0.005–0.02 mm at the dies
    [estimate]. The tool's internal compliance at crimp force stays.

**Consistency note (safe side).** p5b's lobe torque assumes 220–275 N constant
over the last 8 mm of grip: 1.8–2.2 J. The crimp takes 0.13–0.48 J [digest]. So
either the tool's linkage loses 75–90 %, or the constant-force assumption
overstates the lobe by 2–4×. Either way the motor sizing errs on the safe side.

### B6. p7: the push reaches the slug only through the cut caps

**Conflict.**
- The blades cut each crown to a chord at ±zs and then "push rather than
  grip".
- The only slug surface a blade face bears on is the end face of the cap it
  cut:

  | Ligament | Cap end face, per conductor (both blades) |
  |---|---|
  | 0.15 mm | 0.65 mm² |
  | 0.20 mm | 0.51 mm² |
  | 0.30 mm | 0.28 mm² |

  [calc FP §6]
- **The flanks and the web**, which must tear, are behind that face, joined to
  the cap by shear through the cap's underside.

**Physical consequence.**
- At the tension bound (10–15 N per conductor) the cap faces carry:
  - 15–29 MPa at 0.15–0.20 mm ligaments;
  - 36–54 MPa at 0.30 mm.
- That is 2–5× silicone's 8–11 MPa tensile strength, on a 0.19–0.34 mm lip
  that is free on top. A neo-Hookean E ~4 MPa jacket is at 66–79 % strain by
  then.
- **So the caps crush and can roll over the blade edges before the flanks
  tear.** The slug then stays on with its crowns shaved.
- At the low tear figure (3 N per conductor) it is 5–11 MPa, marginal.
- **The thicker, safer ligament makes it worse**, because the cap gets smaller.

**Repairs.**
- **A pad pair** (TPU or fine-toothed) closes on the slug's top and bottom
  ahead of the blades and travels with them.
  - It spreads the push over each cap's top, ~2.6–3.3 mm², so ~3–4 MPa of pad
    pressure at friction ~0.8 carries 15 N per conductor.
  - That is ~35–60 N of clamp per side on a 5P [estimate, from calc FP §6's
    cap areas].
- **The cut itself: slice while pressing.** Straight blades are indifferent to
  X, so each blade can be drawn 2–4 mm along its own edge as it closes.
  - The slicing literature shows the normal force to cut soft solids falls
    several-fold with a slice-to-push ratio near 1 [assumption, from Atkins et
    al. 2004 on cutting soft solids, not fetched this session].
  - Pressing straight in, a sharp edge indents silicone by the order of
    0.03–0.25 mm before it starts to cut [estimate: cutting toughness
    ~0.1–1 N/mm against E ~4 MPa]. That is comparable to the 0.2–0.3 mm
    ligament, so the real kerf may stop short of the steel stop.
- **The lower blade's slot.** The lower blade "rises through a 0.3 mm slot in
  the channel floor" and then travels +Y 3–4 mm with the carriage. The slot
  must be 3.3–4.3 mm long, which leaves the ribbon unsupported there.
  - Or the floor ahead of the strip line rides the carriage with the blades,
    as a split floor.

**Uncertain:** the tear path itself (their open problem). The hand-lever trial
p7 already asks Derek for should be run twice, with and without slug pads.

### B7. p1c, p5b, p1 (hook), p4b, p6 at a cut loom: the proof pull's reaction goes through the clamp's grip on silicone

**Conflict.**
- The pull on the box is reacted at the ribbon clamp: the cassette's TPU
  cam-clamp, or p4b's soft clamp.
- The clamp grips the jacket. The pull must pass from jacket to strands under
  the clamp.
- Strands slip inside a squeezed jacket at [calc FP §4, from f&f wave2 §5]:
  - 0.5–2.1 N per mm of length at 10 % squeeze;
  - 1.4–6.3 N/mm at 30 %.

**Physical consequence.**
- A light clamp lets the copper slide back inside the jacket. The hook's
  switch then sees the tool follow, which fails a good crimp.
- False passes are not the risk. Over 25 mm of split conductor the copper
  path is 1,413 N/mm and the jacket path 0.19–0.41 N/mm, so at a 0.5 mm pull
  threshold the jacket carries 0.1–0.2 N.

**Repair.**
- The clamp squeezes the jacket 15–30 % over 5–20 mm, depending on the
  silicone's stiffness: 3.2–6.4 mm at 30 % and E 5.5, 20–40 mm at 10 % and
  E 2.5.
- At a reel (p3, p6, FP1-reel) the whole reel anchors the copper, and the
  question disappears.
- p4b's clamp also carries the strip pull. A squeeze that holds 20 N holds
  the 3–15 N slug.

### B8. p1 B-drop and p5: a 1.6–1.9 mm fin under the conductor barrel is wider than the crimp

**Conflict.**
- The anvil sits inside the crimper's channel, so anvil width = crimp width
  − clearance (0.04–0.08).
- JST's analog SXA-01T-P0.6 at 22 AWG crimps **1.50 wide** × 0.80 high
  [mfr S14]. xh-facts estimates ~1.5 for SXH-001T-P0.6.

**Consequence** [calc FP §2, equal enclosed area, estimate]:

| Fin under the conductor barrel | Crimp |
|---|---|
| 1.6 mm | 1.66 wide × 0.75 high |
| 1.9 mm | 1.96 wide × 0.68 high |

That is a different profile from JST's.

**Repair.**
- A stepped fin: ~1.45 mm under the conductor barrel, 1.8–1.9 under the
  insulation barrel (FP1's laminated or ground-stock fin).
- At the JST width the B-drop fin keeps 5.0–6.2 kN of free-topped Euler load
  at 9–10 mm tall, against 6.7 at 1.6 mm. That is still above 3 kN, with less
  margin.

---

## 3. Consistency

1. **Rolled crimps.**
   - Hand-tool-as-press a3's own file and into-the-housing's calc [ith ex §8]
     say a tip-down SN closing along the row rolls every crimp. p1c, p2 head
     T, p3/p3b's C1 station, p5b and p6 stages 1–5 use that pose and are
     silent.
   - The geometry is unambiguous; the a3 file and ith are right.
   - ith §8's "0.1–0.3 mm gaps" between rolled boxes omits the lance. With
     it the rolled row overlaps by 0.5–0.8 mm [calc FP §1b].
2. **p6's stage table against its stored calc output.**
   - p6 and the summary give 51 / 61 / 40 / 33 / 24 / 15 attended minutes and
     +$100–170 / +$90–140 / +$20–60 for stages 1–3.
   - The stored [`wave2.out.txt`](../explorers/procedure-is-the-machine/calc/wave2.out.txt)
     §6 shows 54 / 65 / 43 / 36 / 27 / 18, +$70–110 / +$200–320 / +$40–90,
     and "gantry, post column" for stage 2.
   - Re-running their current `wave2.py` (to a scratch file, not their
     directory) reproduces the idea file's numbers exactly. The stored output
     is stale.
   - It also carries a duplicated fragment at the end of §7 ("ductors' fronts
     back …"), and its §1 pull-backs differ from a re-run by ≤0.02 mm.
3. **The fin width** (p1, p5, summary: "1.6–1.9 mm") against crimp width ~1.5
   (xh-facts table; [mfr S14]; [f&f wave2 §8]): see B8. The conductor step
   should be ~1.45.
4. **p5: "Hand tools bottom their jaws … Applicators do not; they set height on
   dials [xh-facts §2]."**
   - An applicator's crimp height is also a position: the press's crank bottom
     dead centre plus a wedge offset. JST's CDS applicator has "dial
     crimp-height adjustment" [xh-facts §2]. The OTP-standard KS-EM40R has a
     "CH/I.H wedge type height adjusting system with the precision of 0.02 mm"
     [f&f summary, source crimpapplicator.com].
   - What differs between stop blocks and a dial is not position against
     something else. It is a dead stop, which takes surplus force (B4),
     against a kinematic bottom, which takes none.
5. **p5's frame-stiffness torque table** (from [H §4]): 2.3–5.8 N·m against
   1.0–2.3 N·m from the stroke curve with frame wind-up [calc FP §3]; see B4.
   The table errs high on soft frames.
6. **p5b's lobe work** (220–275 N over 8 mm, ~2 J) against the crimp's
   0.13–0.48 J [digest]; see B5. Conservative.
7. **p1c: "~0.65 mm over the top of a squared crimp's box (2.4 mm tall)"**
   assumes an upright box. As the tool makes it, the box's 2.4 mm lies across
   the row (B1).
8. **Sourcing.**
   - p5 and p5b's NEMA 17 worm-gear stepper has no Prime listing [Prime:
     "none found"].
   - The Prime routes that do exist:
     - the Greartisan 12 V self-locking worm gearmotor, 3.9 N·m;
     - the StepperOnline NEMA 17 26.85:1 planetary, 3 N·m permissible and not
       self-locking [Prime rows].
   - The planetary covers p5 at 1.0–2.3 N·m but not p5b's 2.1–3.2 N·m with
     margin.
9. **No disagreement found** in their other figures checked against xh-facts
   and the digest:
   - strip 2.4 mm with the clone's 1.6–2.1 noted;
   - 60 × 0.08 mm strands;
   - 0.1–0.9 Ω through a 15.24 m reel (0.87 Ω by ρL/A);
   - 0.08 mm a side for a 1.7 mm conductor between 0.64 mm pins;
   - silicone 8–11 MPa;
   - ~190 HX711 samples through compaction;
   - the p7 fan pull-backs, which my S-bend estimate reproduces within
     0.01–0.10 mm [calc FP §7].

---

## 4. Transfers

### From force-and-form into procedure-is-the-machine

- **The jaw's closing direction is the contact's floor normal.** A head that
  closes along the row rolls the crimp. Any head working a flat row must close
  normal to it, and only the part of it under the conductor (the anvil) has to
  pass through the row plane. That sets the lift by die geometry, 3–3.5 mm
  with a fin, not by a hand tool's shape (B1, FP1).
- **With stops, a compliant loop is the design.**
  - Height comes from the stops.
  - The surplus force is k × *m*, so make k small.
  - A doubled contact is capped by the same spring.
  - The drive needs 1–2.3 N·m.
  - Or: a knee or crank bottom in a small steel C, with no stops. The load
    cell goes outside any stop loop (B4).
- **Capture pinches the insulation bore.** Feed the conductor into an open
  contact on a post, then let the tool close on both (B2). This is row 4 of
  their own order table, chosen for a physical reason.
- **Identity where copper is touched anyway:** the trim blade, or the wing
  tips at the end of the curl. The neck stays clear by design (B3).
- **On silicone the insulation crimp is set by position.** It grips the
  conductor at only 0.5–8 N, and its window runs between a cut floor and the
  2.4 mm cavity ceiling (f6).
  - Every SN head of theirs crimps the insulation at the SN's fixed step, and
    none of their files checks where that lands.
  - p6 stage 0 is where to look: bend-and-look over a 2 mm pin on five of
    today's crimps.
- **Proof-pull reaction needs a squeezing clamp**, or a reel (B7).
- **Push through a pad, not a cut face.** And slice while cutting (B6).
- **Ground flat stock stood on edge, or laminated Prime shim, is an anvil
  fin** whose width is its thickness (B8, FP1).
- **Precision is needed only at first die touch and at the bottom.** FP1's
  post bar is deliberately soft laterally, so the crimper's flare places the
  contact. That frees their cassette and post supports from sub-0.1 mm work.

### From procedure-is-the-machine into force-and-form

- **Lift once → f4 and f8 need no split into planes.**
  - With *k* alone lifted 3.5 mm and a fin from below, f4's steel C works on
    the ribbon at 2.5 mm pitch as a fixed station. The gantry, the 5 mm comb
    board and change-the-question's c1 split all drop out of f4's single-head
    form.
  - f8's narrow stepped crimper gets a second use away from the housing's
    mouth.
- **Camera bare length replaces my touch-off as the axial reference** in f1,
  f3 and f4. Touch-off finds the strand tips, the wrong end: ±0.22 against
  ±0.07–0.09 mm RSS [calc P wave2 §3]. My neck blade keeps the proof pull and
  loses the depth job.
- **Identity through the far end** (pogo block, hub socket, slip ring). It
  turns f3's touch-off circuit into an identity check, and it gives **f5b's
  gang cassette per-station identity**.
  - Insulate each station's anvil or pocket and read continuity to the far
    end before the stroke. f5's "summed force cannot name a station" is then
    answered for the one fault that matters most, a conductor in the wrong
    station.
  - It is not answered for strand loss.
- **Terminate at the reel, cut last, pull rather than push:**
  - f2c's feed-out becomes p6's puller;
  - f3's and f7's first builds become p6 stage-1 hardware at the reel;
  - every qualification crimp gets an open, short and identity check (FP5).
- **p7 gives every gang (f5, f5b, f9) its strip line in one stroke**, with the
  fan's pull-back as the stated cost (FP4). p7 is also what f2c lacked (FP3).
- **Posts loaded in key order as the build list:**
  - FP1's post bar;
  - f5b's keyed pockets could be loaded from a post bar in one push instead
    of by hand;
  - f9's tack pallet likewise.
- **p4b's accounting applies to f1.** f1 with hand-dropped contacts is a
  person-paced head (~67 calls a unit). It saves minutes only as one of two
  heads alternating. A single f1 buys consistency and a log.

---

## Measurements this exchange sharpens

1. **One crimp from the SN-2549 held tip-down,** jaws closing along a flat row
   of conductors, photographed end-on. Settles B1 by looking.
2. **One kit contact side-on under the ELP camera:**
   - the transition *t* (FP1's lance relief, B3's neck budget, f8);
   - end-on, the insulation barrel floor's inner width (B2).
3. **One crimped conductor in the cassette's TPU clamp, pulled at 20 N**
   through the box with a luggage scale. Does the copper creep back inside the
   jacket (B7)?
4. **p7's two-razor hand trial run twice, with and without pads on the
   slug.** Do the caps roll over the edges (B6)?
5. **The SN-2549's handle force at the moment the ratchet releases**, on a
   bathroom scale, against p5b's 275 N link (B5).
